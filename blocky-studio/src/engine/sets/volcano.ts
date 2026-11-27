// A volcano above a plain: a huge ridged cone with glowing cracks, a row of small houses at its foot for scale, and,
// optionally, an eruption (crater glow, a fire column, flying embers, a dark smoke plume).
// The camera stands near the origin looking toward -Z; the cone's base centre is at [0, 0, -distance].
import * as THREE from "three";
import { hash01, rng } from "../core/rng";
import { groundRelief } from "../tex/relief";
import { noiseCanvas } from "../tex/textures";
import { vfx, type Vfx } from "../vfx";

export type VolcanoParams = {
  distance: number; radius: number; height: number;
  rock: string; rockDark: string; lava: string; lavaGlow: number; cracks: number;
  ground: string; groundDark: string;
  houses: { count: number; wall: string; roof: string; lit: number } | null;
  erupt: boolean; smoke: boolean;
};
export const VOLCANO_DEFAULTS: VolcanoParams = {
  distance: 260, radius: 150, height: 170, rock: "#4a4046", rockDark: "#1c1618", lava: "#ff6a1c", lavaGlow: 1.6, cracks: 70,
  ground: "#8a8a6a", groundDark: "#5e6048", houses: { count: 26, wall: "#cfc8bc", roof: "#8a3a30", lit: 0.2 }, erupt: false, smoke: true,
};

export const buildVolcano = (scene: THREE.Scene, p: VolcanoParams, seed: number): Vfx[] => {
  const gc = noiseCanvas({ size: 512, seed: seed + 3, dark: p.groundDark, light: p.ground, baseCells: 14, octaves: 5, contrast: 1.4, grain: 0.3 });
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), groundRelief(gc, seed + 4, { repeat: [60, 60], strength: 1.5, roughness: 0.95 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true;
  scene.add(ground);

  // the cone: gullies run down the slope (radius varies with the angle), the rim is ragged, the top is cut off
  const SEG = 96, RINGS = 28, top = 0.13; // crater radius as a fraction of the base radius
  const geo = new THREE.CylinderGeometry(p.radius * top, p.radius, p.height, SEG, RINGS, true);
  const pos = geo.getAttribute("position");
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), zz = pos.getZ(i), ang = Math.atan2(zz, x), t = (y + p.height / 2) / p.height; // 0 base .. 1 rim
    const gully = 0.07 * Math.sin(ang * 23 + Math.sin(ang * 5) * 2) + 0.05 * Math.sin(ang * 9 + 1.3) + 0.03 * Math.sin(ang * 51);
    const k = 1 + gully * (0.35 + 0.65 * (1 - t)) + 0.12 * (1 - t) * Math.sin(ang * 3 + 0.7);
    pos.setX(i, x * k); pos.setZ(i, zz * k);
    pos.setY(i, y + (t > 0.98 ? (hash01(Math.round((ang + 4) * 14), seed) - 0.5) * p.height * 0.05 : 0));
  }
  geo.computeVertexNormals();
  // rock colour + glowing cracks that run downhill from the rim (drawn in the cone's unwrapped texture)
  const S = 1024, rock = noiseCanvas({ size: S, seed: seed + 5, dark: p.rockDark, light: p.rock, baseCells: 20, octaves: 5, contrast: 1.6, grain: 0.35 });
  const ec = document.createElement("canvas"); ec.width = ec.height = S;
  const eg = ec.getContext("2d")!, r = rng(seed + 6);
  eg.fillStyle = "#000"; eg.fillRect(0, 0, S, S);
  eg.strokeStyle = p.lava; eg.lineCap = "round";
  for (let k = 0; k < p.cracks; k++) {
    let x = r() * S, y = r() * S * 0.25; // v = 0 is the rim in this unwrap
    eg.lineWidth = 1.5 + r() * 3; eg.globalAlpha = 0.5 + r() * 0.5;
    eg.beginPath(); eg.moveTo(x, y);
    const len = 5 + Math.floor(r() * 14);
    for (let s = 0; s < len; s++) { x += (r() - 0.5) * 26; y += 14 + r() * 30; eg.lineTo(x, y); eg.lineWidth *= 0.95; }
    eg.stroke();
  }
  const map = new THREE.CanvasTexture(rock), emap = new THREE.CanvasTexture(ec);
  for (const t of [map, emap]) { t.wrapS = THREE.RepeatWrapping; t.repeat.set(3, 1); t.colorSpace = THREE.SRGBColorSpace; }
  const cone = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ map, bumpMap: map, bumpScale: 8, roughness: 0.95, emissive: new THREE.Color("#ffffff"), emissiveMap: emap, emissiveIntensity: p.lavaGlow, flatShading: false }));
  cone.position.set(0, p.height / 2 - 2, -p.distance);
  cone.castShadow = true; cone.receiveShadow = true;
  scene.add(cone);

  // houses at the foot, for scale
  if (p.houses) {
    const h = p.houses, hr = rng(seed + 7);
    const wall = new THREE.MeshStandardMaterial({ color: h.wall, roughness: 0.9 }), roof = new THREE.MeshStandardMaterial({ color: h.roof, roughness: 0.8 });
    const lit = new THREE.MeshBasicMaterial({ color: new THREE.Color("#ffd9a0").multiplyScalar(1.6) }), unlit = new THREE.MeshStandardMaterial({ color: "#2a2a30" });
    const pyramid = new THREE.ConeGeometry(Math.SQRT1_2, 1, 4);
    for (let i = 0; i < h.count; i++) {
      const w = 9 + hr() * 6, hh = 7 + hr() * 6, x = ((i + 0.5) / h.count - 0.5) * p.radius * 2.6 + (hr() - 0.5) * 8, z = -p.distance + p.radius * 1.02 + hr() * 30;
      const body = new THREE.Mesh(new THREE.BoxGeometry(w, hh, 9), wall); body.position.set(x, hh / 2, z);
      const rf = new THREE.Mesh(pyramid, roof); rf.rotation.y = Math.PI / 4;
      const holder = new THREE.Group(); holder.add(rf); holder.scale.set(w * 1.1, hh * 0.5, 10); holder.position.set(x, hh * 1.25, z);
      const win = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.9), hr() < h.lit ? lit : unlit); win.position.set(x, hh * 0.55, z + 4.55);
      body.castShadow = true;
      scene.add(body, holder, win);
    }
  }

  const fx: Vfx[] = [];
  const add = (type: string, params: Record<string, unknown>, k: number) => { const v = vfx.get(type)(params, seed + k * 31); scene.add(v.object); fx.push(v); };
  const rim: [number, number, number] = [0, p.height - 4, -p.distance];
  if (p.smoke) add("steam", { pos: [rim[0] + 10, rim[1], rim[2]], count: 16, spread: p.radius * 0.3, rise: p.height * 0.9, size: p.radius * 0.5, color: p.erupt ? "#3a2420" : "#5a5456", opacity: 0.55, period: 260 }, 1);
  if (p.erupt) {
    add("flame", { pos: [rim[0], rim[1] - 6, rim[2]], size: p.radius * 0.2, gain: 2.2, light: 0 }, 2);
    add("embers", { count: 500, box: [p.radius * 1.6, p.height * 0.9, p.radius], centre: [rim[0], rim[1] + p.height * 0.25, rim[2]], size: p.radius * 0.014, gain: 2.4, rise: p.height * 0.25, wind: [4, 0] }, 3);
    add("fireballs", { count: 5, from: [rim[0], rim[1], rim[2] + 10], velocity: [1.8, 1.1, 0.4], spread: [p.radius * 0.5, 4, 20], size: p.radius * 0.035, every: 11, life: 70 }, 4);
  }
  return fx;
};
