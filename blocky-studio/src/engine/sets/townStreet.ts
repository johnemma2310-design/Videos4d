// SET B/C — a town street: cobbled ground, a row of houses down one or both sides (stone walls with window grids,
// gable roofs, chimneys), a kerb, and optional fire bowls along it. One builder serves both kingdoms through its
// palette. The street runs along -Z; x < 0 is the left side. Units are studs; ground is y = 0.
import * as THREE from "three";
import { rng } from "../core/rng";
import { makeCanvas, noiseCanvas, toTexture } from "../tex/textures";
import { coursedStones, fieldFromCanvas, reliefMaterial, rubbleMaterial, noiseField, type Courses, type Field } from "../tex/relief";

/** house walls: rubble in courses about 0.6 studs tall, stones 1 to 3 times as long as they are tall */
const HOUSE_COURSES: Courses = { rows: 26, width: [1.2, 3.5], rowVar: 0.4, joint: 0.2, round: 0.35, wobble: 0.2 };
import { hash01 } from "../core/rng";

export type TownStreetParams = {
  seed: number;
  ground: { stone: string; stoneDark: string; gap: string; repeat: number; sett: number };
  houses: {
    sides: ("left" | "right")[];
    /** distance of the facades from the street centre, first and last house position along the street, spacing */
    x: number; z0: number; z1: number; gap: number;
    /** the right-hand row may stand further out and start further away than the left one */
    rightX?: number; rightZ0?: number;
    width: [number, number]; depth: number; height: [number, number]; roof: [number, number];
    wall: string; wallDark: string; roofColor: string; roofDark: string; window: string; windowLit: string; lit: number; trim: string;
  };
  kerb: { x: number; height: number; color: string } | null;
  bowls: { x: number; z0: number; z1: number; step: number; pedestal: string; bowl: string; scale?: number } | null;
};

export const FIRE_STREET: TownStreetParams = {
  seed: 11,
  ground: { stone: "#d9b890", stoneDark: "#b08e6c", gap: "#7a5e48", repeat: 20, sett: 16 },
  // values from the comparison rounds on reference frame f00088
  houses: { sides: ["left"], x: 17, z0: 6, z1: -330, gap: 5, width: [18, 24], depth: 18, height: [11, 16], roof: [6, 8.5],
            wall: "#8a90a0", wallDark: "#565b6a", roofColor: "#9a4a40", roofDark: "#70322c", window: "#2a2a34", windowLit: "#d8b488", lit: 0.45, trim: "#d8d2c8" },
  kerb: { x: 9.5, height: 0.5, color: "#8a8078" },
  bowls: { x: 7.6, z0: -4, z1: -130, step: 16, pedestal: "#5a524c", bowl: "#1a1614", scale: 1.2 },
};
export const WATER_STREET: TownStreetParams = {
  ...FIRE_STREET, seed: 23,
  ground: { stone: "#c9c4c0", stoneDark: "#a39e9c", gap: "#6a6668", repeat: 20, sett: 16 },
  houses: { ...FIRE_STREET.houses, wall: "#dcdad6", wallDark: "#b8b6b4", roofColor: "#4a6a7a", roofDark: "#34505e", window: "#3a4048", trim: "#f4f2ee" },
  bowls: null,
};

/** rows of rounded setts with dark joints; also used as the bump map */
const cobbleCanvas = (g: TownStreetParams["ground"], seed: number) => {
  const S = 1024, { canvas, ctx } = makeCanvas(S), r = rng(seed), n = g.sett, h = S / n;
  ctx.fillStyle = g.gap; ctx.fillRect(0, 0, S, S);
  const a = new THREE.Color(g.stoneDark), b = new THREE.Color(g.stone), c = new THREE.Color();
  for (let row = 0; row < n; row++) {
    let x = -r() * h * 1.4;
    while (x < S) {
      const w = h * (1.0 + r() * 0.9);
      c.copy(a).lerp(b, r());
      const grd = ctx.createLinearGradient(0, row * h, 0, row * h + h);
      grd.addColorStop(0, "#" + c.clone().multiplyScalar(1.12).getHexString()); grd.addColorStop(1, "#" + c.clone().multiplyScalar(0.82).getHexString());
      ctx.fillStyle = grd;
      ctx.beginPath(); ctx.roundRect(x + 4, row * h + 4, w - 8, h - 8, h * 0.22); ctx.fill();
      if (x + w > S) { ctx.beginPath(); ctx.roundRect(x - S + 4, row * h + 4, w - 8, h - 8, h * 0.22); ctx.fill(); } // wrap
      x += w;
    }
  }
  return canvas;
};

/** Gable-roof prism with unit footprint and unit height, ridge along Z */
const gable = (() => {
  let g: THREE.BufferGeometry | null = null;
  return () => {
    if (g) return g;
    const v = [-0.5, 0, 0.5, 0.5, 0, 0.5, 0, 1, 0.5, -0.5, 0, -0.5, 0.5, 0, -0.5, 0, 1, -0.5];
    g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(v, 3));
    g.setIndex([0, 1, 2, 4, 3, 5, 0, 2, 5, 0, 5, 3, 1, 4, 5, 1, 5, 2]);
    g = g.toNonIndexed();
    g.computeVertexNormals();
    return g;
  };
})();

/** shared rubble pattern for all facades of one street (computed once), then windows are cut into a copy per house */
const wallStone = (h: TownStreetParams["houses"], seed: number) => {
  const S = 512, { height, id } = coursedStones(S, seed, HOUSE_COURSES), grain = noiseField(S, seed + 3, 40, 3);
  const a = new THREE.Color(h.wallDark), b = new THREE.Color(h.wall), m = new THREE.Color(h.wallDark).multiplyScalar(0.6);
  const rgb = new Uint8ClampedArray(S * S * 4);
  for (let k = 0; k < S * S; k++) {
    const hh = height.data[k], tt = Math.min(1, Math.max(0, 0.5 + (hash01(id[k], seed) - 0.5) * 1.3 + (grain.data[k] - 0.5) * 0.5)), face = Math.min(1, hh / 0.3);
    rgb[k * 4] = (m.r + (a.r + (b.r - a.r) * tt - m.r) * face) * 255; rgb[k * 4 + 1] = (m.g + (a.g + (b.g - a.g) * tt - m.g) * face) * 255;
    rgb[k * 4 + 2] = (m.b + (a.b + (b.b - a.b) * tt - m.b) * face) * 255; rgb[k * 4 + 3] = 255;
    height.data[k] = Math.min(1, hh * 0.85 + (grain.data[k] - 0.5) * 0.18 * hh);
  }
  return { S, rgb, height };
};
const facade = (h: TownStreetParams["houses"], stone: ReturnType<typeof wallStone>, cols: number, rows: number, seed: number, repeat: [number, number]) => {
  const S = stone.S, { canvas, ctx } = makeCanvas(S), r = rng(seed * 3 + 1);
  ctx.putImageData(new ImageData(new Uint8ClampedArray(stone.rgb), S, S), 0, 0);
  const height: Field = { data: new Float32Array(stone.height.data), size: S };
  const flat = (x: number, y: number, w: number, hh: number, v: number) => {
    for (let yy = Math.max(0, Math.floor(y)); yy < Math.min(S, y + hh); yy++) for (let xx = Math.max(0, Math.floor(x)); xx < Math.min(S, x + w); xx++) height.data[yy * S + xx] = v;
  };
  for (let a = 0; a < cols; a++)
    for (let b = 0; b < rows; b++) {
      // small deep-set windows without bright frames, as on the reference
      const w = S / cols, hh = S / rows, ww = w * 0.24, wh = hh * 0.34, x = a * w + (w - ww) / 2, y = b * hh + hh * 0.3;
      ctx.fillStyle = "rgba(0,0,0,0.35)"; ctx.fillRect(x - 4, y - 4, ww + 8, wh + 8);
      ctx.fillStyle = r() < h.lit ? h.windowLit : h.window; ctx.fillRect(x, y, ww, wh);
      flat(x - 4, y - 4, ww + 8, wh + 8, 0.2); // the opening sits back in the wall
    }
  return reliefMaterial(canvas, height, { repeat, strength: 3, cavity: 0.3, roughness: 0.85 });
};

export const buildTownStreet = (scene: THREE.Scene, p: TownStreetParams) => {
  const r = rng(p.seed);
  // setts: regular rows of rounded stones (as on the reference); relief comes from the same drawing, dark joints = low
  const cob = cobbleCanvas(p.ground, p.seed), rep = p.ground.repeat * 8;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(1600, 1600), reliefMaterial(cob, fieldFromCanvas(cob), { repeat: [rep, rep], strength: 1.4, cavity: 0.05, roughness: 0.62 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const h = p.houses;
  const roofMat = new THREE.MeshStandardMaterial({ map: toTexture(noiseCanvas({ size: 256, seed: 5, dark: h.roofDark, light: h.roofColor, baseCells: 24, octaves: 3, contrast: 1.4, grain: 0.3 }), [3, 2]), roughness: 0.85 });
  const stone = wallStone(h, p.seed + 40);
  const side = rubbleMaterial({ seed: p.seed + 41, size: 512, courses: HOUSE_COURSES, light: h.wall, dark: h.wallDark, mortar: "#" + new THREE.Color(h.wallDark).multiplyScalar(0.45).getHexString(), repeat: [2, 2], strength: 3, variation: 1.3 }).material;
  const chimney = new THREE.MeshStandardMaterial({ color: h.wallDark, roughness: 0.95 });
  for (const s of h.sides) {
    const sx = s === "left" ? -1 : 1, hx = s === "right" ? h.rightX ?? h.x : h.x;
    let z = s === "right" ? h.rightZ0 ?? h.z0 : h.z0, i = s === "right" ? 100 : 0;
    while (z > h.z1) {
      const w = h.width[0] + r() * (h.width[1] - h.width[0]), hh = h.height[0] + r() * (h.height[1] - h.height[0]), rf = h.roof[0] + r() * (h.roof[1] - h.roof[0]);
      const cols = Math.max(2, Math.round(w / 6)), rows = Math.max(2, Math.round(hh / 6));
      const front = facade(h, stone, cols, rows, p.seed + i, [1, 1]);
      const g = new THREE.Group();
      // the facade faces the street: +x for the left row, -x for the right row
      const body = new THREE.Mesh(new THREE.BoxGeometry(h.depth, hh, w), sx < 0 ? [front, side, side, side, side, side] : [side, front, side, side, side, side]);
      body.position.y = hh / 2;
      const roof = new THREE.Mesh(gable(), roofMat);
      roof.scale.set(h.depth * 1.08, rf, w * 1.04);
      roof.position.y = hh;
      const ch = new THREE.Mesh(new THREE.BoxGeometry(1.6, 3.2, 1.6), chimney);
      ch.position.set((r() - 0.5) * h.depth * 0.4, hh + rf * 0.75, (r() - 0.5) * w * 0.5);
      g.add(body, roof, ch);
      g.traverse((o) => { o.castShadow = true; o.receiveShadow = true; });
      g.position.set(sx * (hx + h.depth / 2 + r() * 2.5), 0, z - w / 2); // separate buildings, slightly staggered
      scene.add(g);
      z -= w + h.gap; i++;
    }
  }

  if (p.kerb) {
    // a raised pavement from the kerb edge back to the houses; crowds stand on it
    const wPav = Math.max(1.2, h.x + 4 - p.kerb.x);
    const k = new THREE.Mesh(new THREE.BoxGeometry(wPav, p.kerb.height, 1600), new THREE.MeshStandardMaterial({ color: p.kerb.color, roughness: 0.9 }));
    k.position.set(-p.kerb.x - wPav / 2, p.kerb.height / 2, -600);
    k.castShadow = true; k.receiveShadow = true;
    scene.add(k);
  }
  /** positions where fire bowls stand; the caller adds "flame" effects on top (y = 2.3) */
  const bowlSpots: [number, number, number][] = [];
  if (p.bowls) {
    const ped = new THREE.MeshStandardMaterial({ color: p.bowls.pedestal, roughness: 0.95 }), iron = new THREE.MeshStandardMaterial({ color: p.bowls.bowl, roughness: 0.55, metalness: 0.5 });
    for (let z = p.bowls.z0; z > p.bowls.z1; z -= p.bowls.step) {
      const g = new THREE.Group();
      const base = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 1.0, 1.5, 7), ped);
      base.position.y = 0.75;
      const bowl = new THREE.Mesh(new THREE.SphereGeometry(1.15, 12, 6, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), iron);
      bowl.scale.y = 0.6; bowl.position.y = 2.25;
      g.add(base, bowl);
      for (let k = 0; k < 6; k++) { // the spiked rim
        const sp = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.6, 4), iron);
        sp.position.set(Math.cos(k * 1.047) * 1.1, 2.4, Math.sin(k * 1.047) * 1.1);
        g.add(sp);
      }
      g.traverse((o) => { o.castShadow = true; });
      const sc = p.bowls.scale ?? 1;
      g.scale.setScalar(sc);
      g.position.set(-p.bowls.x, 0, z);
      scene.add(g);
      bowlSpots.push([-p.bowls.x, 2.2 * sc, z]);
    }
  }
  return { bowlSpots };
};
