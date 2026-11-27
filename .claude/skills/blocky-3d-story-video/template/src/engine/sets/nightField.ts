// SET S — night battlefield: bare straw-littered soil, a row of dark houses with a few lit windows on the horizon,
// an optional canal strip. Dimensions and colours are parameters so the comparison loop can tune them.
import * as THREE from "three";
import { rng } from "../core/rng";
import { makeRng } from "../tex/pocRng";
import { noiseCanvas, scatterStrokes, toTexture } from "../tex/textures";
import { groundRelief } from "../tex/relief";

export type NightFieldParams = {
  ground: { dark: string; light: string; straw: string; strawCount: number; repeat: number };
  houses: { z: number; count: number; spanX: number; wall: string; roof: string; window: string; windowGain: number; lit: number; seed: number; height: [number, number] };
  canal?: { x: number; width: number };
};
export const NIGHT_FIELD_DEFAULTS: NightFieldParams = {
  ground: { dark: "#1c0c08", light: "#5a3020", straw: "#8a5a3a", strawCount: 900, repeat: 40 },
  houses: { z: -150, count: 22, spanX: 320, wall: "#3a2a24", roof: "#24382c", window: "#ffd9a0", windowGain: 2.2, lit: 0.35, seed: 5, height: [9, 16] },
};

export const buildNightField = (scene: THREE.Scene, p: NightFieldParams) => {
  const c = noiseCanvas({ size: 1024, seed: 21, dark: p.ground.dark, light: p.ground.light, baseCells: 24, octaves: 5, contrast: 1.5, grain: 0.35 });
  scatterStrokes(c, makeRng(9), p.ground.strawCount, p.ground.straw, [30, 110], [1, 2.4], [0.3, 0.8]);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(900, 900), groundRelief(c, 22, { repeat: [p.ground.repeat, p.ground.repeat], strength: 2.2, roughness: 0.95, cells: 64 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const h = p.houses, r = rng(h.seed);
  const wall = new THREE.MeshStandardMaterial({ color: h.wall, roughness: 0.95 }), roof = new THREE.MeshStandardMaterial({ color: h.roof, roughness: 0.85 });
  const lit = new THREE.MeshBasicMaterial({ color: new THREE.Color(h.window).multiplyScalar(h.windowGain) }), dark = new THREE.MeshStandardMaterial({ color: "#120a08" });
  const pyramid = new THREE.ConeGeometry(Math.SQRT1_2, 1, 4);
  for (let i = 0; i < h.count; i++) {
    const w = 10 + r() * 8, d = 9 + r() * 5, hh = h.height[0] + r() * (h.height[1] - h.height[0]);
    const x = ((i + 0.5) / h.count - 0.5) * h.spanX + (r() - 0.5) * 6, z = h.z + (r() - 0.5) * 30;
    const body = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), wall);
    body.position.set(x, hh / 2, z);
    const rf = new THREE.Mesh(pyramid, roof);
    rf.rotation.y = Math.PI / 4;
    const holder = new THREE.Group();
    holder.add(rf);
    holder.scale.set(w * 1.08, hh * 0.45, d * 1.08);
    holder.position.set(x, hh + hh * 0.225, z);
    scene.add(body, holder);
    const cols = Math.max(2, Math.round(w / 4)), rows = Math.max(1, Math.round(hh / 5));
    for (let a = 0; a < cols; a++)
      for (let b = 0; b < rows; b++) {
        const win = new THREE.Mesh(new THREE.PlaneGeometry(1.3, 1.9), r() < h.lit ? lit : dark);
        win.position.set(x + ((a + 0.5) / cols - 0.5) * w * 0.8, ((b + 0.6) / rows) * hh * 0.85, z + d / 2 + 0.05);
        scene.add(win);
      }
  }
};
