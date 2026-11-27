// SET P — home kitchen interior: small-brick sandstone walls with a band of blue-grey tiles and a low stone band,
// a concrete floor and ceiling, a window in the left wall, a plank table and white plastic chairs.
// The room is open toward +Z and +X (where the camera stands). Furniture positions are parameters.
import * as THREE from "three";
import { rng } from "../core/rng";
import { makeCanvas, noiseCanvas, toTexture } from "../tex/textures";
import { fieldFromCanvas, reliefMaterial, rubbleMaterial } from "../tex/relief";

export type KitchenParams = {
  width: number; depth: number; height: number;
  wall: string; wallDark: string; mortar: string; brickRows: number; brickRepeat: number;
  tile: string; tileDark: string; tileBand: [number, number];
  /** low band of rough stone on the back wall: [y0, y1], or null */
  stoneBand: [number, number] | null; stone: string; stoneDark: string;
  floor: string; floorDark: string; ceiling: string;
  window: { z: number; width: number; y0: number; y1: number; glow: number; sky: string };
  table: { x: number; z: number; yaw: number; length: number; width: number; height: number; color: string } | null;
  chairs: { x: number; z: number; yaw: number }[];
  chair: string;
};
export const KITCHEN_DEFAULTS: KitchenParams = {
  width: 30, depth: 22, height: 11.5,
  wall: "#c4ae9a", wallDark: "#a8927e", mortar: "#9a8672", brickRows: 20, brickRepeat: 4.5,
  tile: "#7d8fae", tileDark: "#62728e", tileBand: [6.6, 8.8],
  stoneBand: [2.2, 4.2], stone: "#8a94a6", stoneDark: "#5c6474",
  floor: "#e6e4e0", floorDark: "#c4c2be", ceiling: "#b4b0aa",
  window: { z: -5.5, width: 5, y0: 6.0, y1: 9.8, glow: 0.98, sky: "#dfeaf8" },
  table: { x: -6.4, z: -3.0, yaw: 90, length: 15, width: 2.6, height: 3.0, color: "#c8a468" },
  chairs: [{ x: 2.0, z: 2.9, yaw: 215 }, { x: 1.0, z: -5.3, yaw: 290 }],
  chair: "#f0ede6",
};

const brickCanvas = (p: KitchenParams, seed: number) => {
  const S = 1024, { canvas, ctx } = makeCanvas(S), r = rng(seed);
  ctx.fillStyle = p.mortar; ctx.fillRect(0, 0, S, S);
  const a = new THREE.Color(p.wallDark), b = new THREE.Color(p.wall), c = new THREE.Color();
  const rows = p.brickRows, h = S / rows, w = S / 7;
  for (let row = 0; row < rows; row++)
    for (let col = -1; col < 8; col++) {
      c.copy(a).lerp(b, r());
      ctx.fillStyle = "#" + c.getHexString();
      ctx.fillRect(col * w + (row % 2) * w * 0.5 + 3, row * h + 3, w - 6, h - 6);
    }
  const n = noiseCanvas({ size: S, seed: seed + 1, dark: "#000000", light: "#ffffff", baseCells: 40, octaves: 4, contrast: 1.2, grain: 0.5 });
  ctx.globalAlpha = 0.14; ctx.globalCompositeOperation = "overlay"; ctx.drawImage(n, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = "source-over";
  return canvas;
};
const tileCanvas = (p: KitchenParams, seed: number) => {
  const { canvas, ctx } = makeCanvas(512, 128), r = rng(seed);
  ctx.fillStyle = "#3a4250"; ctx.fillRect(0, 0, 512, 128);
  const a = new THREE.Color(p.tileDark), b = new THREE.Color(p.tile), c = new THREE.Color();
  for (let i = 0; i < 4; i++) { c.copy(a).lerp(b, r()); ctx.fillStyle = "#" + c.getHexString(); ctx.fillRect(i * 128 + 3, 3, 122, 122); }
  return canvas;
};

export const buildKitchen = (scene: THREE.Scene, p: KitchenParams) => {
  const W = p.width, D = p.depth, H = p.height, R = p.brickRepeat;
  const brick = brickCanvas(p, 3);
  // bricks: relief from the drawing itself (mortar is the dark, low part)
  const brickHeight = fieldFromCanvas(brick);
  const wallMat = (len: number, hh: number) => {
    const c = document.createElement("canvas"); c.width = c.height = brick.width; c.getContext("2d")!.drawImage(brick, 0, 0);
    return reliefMaterial(c, brickHeight, { repeat: [len / R, hh / R], strength: 2.5, cavity: 0.2, roughness: 0.9 });
  };
  const concrete = (dark: string, light: string, rep: number, seed: number) => {
    const c = noiseCanvas({ size: 512, seed, dark, light, baseCells: 18, octaves: 5, contrast: 1.4, grain: 0.4 });
    return new THREE.MeshStandardMaterial({ map: toTexture(c, [rep, rep]), bumpMap: toTexture(c, [rep, rep]), bumpScale: 1, roughness: 0.85 });
  };
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(W * 3, D * 3), concrete(p.floorDark, p.floor, 8, 8));
  floor.rotation.x = -Math.PI / 2; floor.position.z = D * 0.5; floor.receiveShadow = true;
  scene.add(floor);
  const ceilMat = concrete("#8a8680", p.ceiling, 6, 9);
  ceilMat.emissive = new THREE.Color(p.ceiling); ceilMat.emissiveIntensity = 0.3; // a ceiling gets no direct light; this stands in for bounce
  const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(W * 3, D * 3), ceilMat);
  ceiling.rotation.x = Math.PI / 2; ceiling.position.set(0, H, D * 0.5);
  scene.add(ceiling);
  const back = new THREE.Mesh(new THREE.BoxGeometry(W, H, 0.6), wallMat(W, H));
  back.position.set(0, H / 2, -D / 2); back.receiveShadow = true;
  scene.add(back);
  const [b0, b1] = p.tileBand;
  const backBand = new THREE.Mesh(new THREE.BoxGeometry(W, b1 - b0, 0.25), new THREE.MeshStandardMaterial({ map: toTexture(tileCanvas(p, 5), [W / (4 * (b1 - b0)), 1]), roughness: 0.4 }));
  backBand.position.set(0, (b0 + b1) / 2, -D / 2 + 0.4);
  scene.add(backBand);
  if (p.stoneBand) {
    const [s0, s1] = p.stoneBand;
    const stone = rubbleMaterial({ seed: 12, size: 512, courses: { rows: 8, width: [1.2, 3], rowVar: 0.35, joint: 0.2, round: 0.35, wobble: 0.2 }, light: p.stone, dark: p.stoneDark, mortar: "#2c3038", repeat: [W * 0.62 / 6, (s1 - s0) / 6], strength: 4, variation: 1.2 }).material;
    const m = new THREE.Mesh(new THREE.BoxGeometry(W * 0.62, s1 - s0, 0.5), stone);
    m.position.set(W * 0.19, (s0 + s1) / 2, -D / 2 + 0.5);
    scene.add(m);
  }
  // left wall with a window opening (four pieces around the hole) and the sky seen through it
  const { z: wz, width: ww, y0: wy0, y1: wy1 } = p.window, mat = wallMat(D, H);
  const piece = (z0: number, z1: number, y0: number, y1: number) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.6, y1 - y0, z1 - z0), mat);
    m.position.set(-W / 2, (y0 + y1) / 2, (z0 + z1) / 2); m.castShadow = true; m.receiveShadow = true;
    scene.add(m);
  };
  piece(-D / 2, wz - ww / 2, 0, H); piece(wz + ww / 2, D * 1.2, 0, H); piece(wz - ww / 2, wz + ww / 2, 0, wy0); piece(wz - ww / 2, wz + ww / 2, wy1, H);
  const sky = makeCanvas(64, 128);
  const grd = sky.ctx.createLinearGradient(0, 0, 0, 128);
  grd.addColorStop(0, "#8fb4e6"); grd.addColorStop(0.6, p.window.sky); grd.addColorStop(0.62, "#d8c8b0"); grd.addColorStop(1, "#c8b89e"); // sky over a pale horizon
  sky.ctx.fillStyle = grd; sky.ctx.fillRect(0, 0, 64, 128);
  const pane = new THREE.Mesh(new THREE.PlaneGeometry(ww, wy1 - wy0), new THREE.MeshBasicMaterial({ map: toTexture(sky.canvas), color: new THREE.Color().setScalar(p.window.glow), fog: false }));
  pane.rotation.y = Math.PI / 2; pane.position.set(-W / 2 - 0.5, (wy0 + wy1) / 2, wz);
  scene.add(pane);
  const frame = new THREE.MeshStandardMaterial({ color: "#d8d2c8", roughness: 0.7 });
  for (const [sy, sz] of [[wy1 - wy0, 0.28], [0.28, ww]] as const) {
    const bar = new THREE.Mesh(new THREE.BoxGeometry(0.35, sy, sz), frame);
    bar.position.set(-W / 2 + 0.1, (wy0 + wy1) / 2, wz);
    scene.add(bar);
  }
  const furniture: THREE.Group[] = [];
  if (p.table) {
    const t = p.table, wood = new THREE.MeshStandardMaterial({ map: toTexture(noiseCanvas({ size: 256, seed: 4, dark: "#8a6a3c", light: t.color, baseCells: 3, octaves: 5, contrast: 1.6, grain: 0.3 }), [3, 1]), roughness: 0.55 });
    const g = new THREE.Group();
    const top = new THREE.Mesh(new THREE.BoxGeometry(t.length, 0.28, t.width), wood); top.position.y = t.height; g.add(top);
    for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.4, t.height, 0.4), wood);
      leg.position.set(x * (t.length / 2 - 0.5), t.height / 2, z * (t.width / 2 - 0.4)); g.add(leg);
    }
    g.position.set(t.x, 0, t.z); g.rotation.y = THREE.MathUtils.degToRad(t.yaw);
    furniture.push(g);
  }
  // plastic garden chair, simplified: seat, slatted back, arms, four legs
  const pl = new THREE.MeshStandardMaterial({ color: p.chair, roughness: 0.4 });
  for (const c of p.chairs) {
    const chair = new THREE.Group();
    const add = (g: THREE.BufferGeometry, x: number, y: number, z: number, rx = 0) => { const m = new THREE.Mesh(g, pl); m.position.set(x, y, z); m.rotation.x = rx; chair.add(m); };
    add(new THREE.BoxGeometry(2.6, 0.2, 2.5), 0, 2.1, 0);
    for (const sx of [-0.9, -0.3, 0.3, 0.9]) add(new THREE.BoxGeometry(0.4, 2.4, 0.16), sx, 3.5, -1.3, -0.14);
    add(new THREE.BoxGeometry(2.6, 0.5, 0.2), 0, 4.75, -1.47, -0.14);
    for (const sx of [-1, 1]) { add(new THREE.BoxGeometry(0.28, 0.2, 2.4), sx * 1.35, 3.1, 0); add(new THREE.BoxGeometry(0.25, 1.0, 0.25), sx * 1.35, 2.6, 1.05); }
    for (const [x, z] of [[-1.2, -1.1], [1.2, -1.1], [-1.2, 1.1], [1.2, 1.1]]) add(new THREE.BoxGeometry(0.24, 2.1, 0.24), x, 1.05, z);
    chair.position.set(c.x, 0, c.z); chair.rotation.y = THREE.MathUtils.degToRad(c.yaw);
    furniture.push(chair);
  }
  for (const g of furniture) { g.traverse((o) => { o.castShadow = true; o.receiveShadow = true; }); scene.add(g); }
};
