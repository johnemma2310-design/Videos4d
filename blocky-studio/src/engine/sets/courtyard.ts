// A castle courtyard, open to the sky: flagstone floor, a high wall with an arched gate and battlements, two round
// towers with cone roofs, banners, a carpet running from the gate toward the camera, and torches on the wall.
// The subject stands near the origin; the wall is behind them at -Z. One builder, two palettes.
import * as THREE from "three";
import { rubbleMaterial } from "../tex/relief";
import { vfx, type Vfx } from "../vfx";

export type CourtyardParams = {
  stone: string; stoneDark: string; mortar: string; floor: string; floorDark: string;
  carpet: string | null; carpetTrim: string; banner: string; emblem: string; roof: string;
  wallZ: number; wallHeight: number; width: number; torches: boolean;
};
export const FIRE_COURTYARD: CourtyardParams = {
  stone: "#8a5a50", stoneDark: "#5a3430", mortar: "#2a1614", floor: "#9a7a6a", floorDark: "#6e5448",
  carpet: "#b01c1c", carpetTrim: "#e8b040", banner: "#b01c1c", emblem: "#f2e2c0", roof: "#6a2622",
  wallZ: -22, wallHeight: 20, width: 70, torches: true,
};
export const WATER_COURTYARD: CourtyardParams = {
  ...FIRE_COURTYARD, stone: "#d8d2cc", stoneDark: "#aaa49e", mortar: "#6e6a68", floor: "#d0ccc6", floorDark: "#a8a49e",
  carpet: "#1f8a80", carpetTrim: "#f2f0e6", banner: "#1f7a70", emblem: "#f2f0e6", roof: "#4a6a7a", torches: false,
};

export const buildCourtyard = (scene: THREE.Scene, p: CourtyardParams, seed: number): Vfx[] => {
  const W = p.width, H = p.wallHeight, z = p.wallZ;
  const shadow = (m: THREE.Object3D) => { m.traverse((o) => { o.castShadow = true; o.receiveShadow = true; }); return m; };
  // floor: large flat flagstones
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), rubbleMaterial({
    seed: seed + 1, light: p.floor, dark: p.floorDark, mortar: p.mortar, repeat: [400 / 24, 400 / 24], strength: 2, cavity: 0.2, roughness: 0.7, variation: 0.8,
    courses: { rows: 9, width: [1, 2.2], rowVar: 0.15, joint: 0.06, round: 0.08, wobble: 0.04 } }).material);
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true;
  scene.add(floor);
  // walls: coursed rubble, one material per face size so stones keep their scale
  const wallMat = (len: number, hh: number) => rubbleMaterial({ seed: seed + 2, light: p.stone, dark: p.stoneDark, mortar: p.mortar, repeat: [len / 14, hh / 14], strength: 3.5, variation: 1.3,
    courses: { rows: 22, width: [1.2, 3.5], rowVar: 0.4, joint: 0.2, round: 0.35, wobble: 0.2 } }).material;
  const back = wallMat(W, H);
  // the back wall in three pieces around a gate 9 wide and 12 high
  const gw = 9, gh = 12;
  for (const [x0, x1, y0, y1] of [[-W / 2, -gw / 2, 0, H], [gw / 2, W / 2, 0, H], [-gw / 2, gw / 2, gh, H]]) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, 3), back);
    m.position.set((x0 + x1) / 2, (y0 + y1) / 2, z - 1.5);
    scene.add(shadow(m));
  }
  // arch top: a half disc of dark opening above the gate's square part, and the dark passage behind
  const dark = new THREE.MeshBasicMaterial({ color: "#0a0606" });
  const passage = new THREE.Mesh(new THREE.PlaneGeometry(gw, gh), dark);
  passage.position.set(0, gh / 2, z - 2.9);
  scene.add(passage);
  const bars = new THREE.MeshStandardMaterial({ color: "#1a1614", roughness: 0.5, metalness: 0.6 });
  for (let k = -3; k <= 3; k++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.25, gh, 0.25), bars); b.position.set(k * 1.25, gh / 2, z - 1.2); scene.add(b); }
  for (let k = 1; k <= 4; k++) { const b = new THREE.Mesh(new THREE.BoxGeometry(gw, 0.25, 0.25), bars); b.position.set(0, k * 2.4, z - 1.2); scene.add(b); }
  // battlements
  const merlon = new THREE.BoxGeometry(2.4, 2.2, 3.4);
  for (let x = -W / 2 + 1.5; x < W / 2; x += 4.8) { const m = new THREE.Mesh(merlon, back); m.position.set(x, H + 1.1, z - 1.5); scene.add(shadow(m)); }
  // side walls running toward the camera
  const side = wallMat(60, H);
  for (const sx of [-1, 1]) { const m = new THREE.Mesh(new THREE.BoxGeometry(3, H, 60), side); m.position.set(sx * (W / 2 + 1.5), H / 2, z + 30); scene.add(shadow(m)); }
  // towers at the back corners
  const towerMat = wallMat(38, H * 1.5), roofMat = new THREE.MeshStandardMaterial({ color: p.roof, roughness: 0.8 });
  for (const sx of [-1, 1]) {
    const t = new THREE.Mesh(new THREE.CylinderGeometry(6, 6.4, H * 1.5, 20), towerMat);
    t.position.set(sx * (W / 2 - 4), H * 0.75, z - 3);
    const r = new THREE.Mesh(new THREE.ConeGeometry(7.4, 11, 20), roofMat);
    r.position.set(sx * (W / 2 - 4), H * 1.5 + 5.5, z - 3);
    scene.add(shadow(t), shadow(r));
  }
  // carpet from the gate toward the camera
  if (p.carpet) {
    const c = document.createElement("canvas"); c.width = 128; c.height = 512;
    const g = c.getContext("2d")!;
    g.fillStyle = p.carpetTrim; g.fillRect(0, 0, 128, 512);
    g.fillStyle = p.carpet; g.fillRect(10, 0, 108, 512);
    g.strokeStyle = p.carpetTrim; g.lineWidth = 3;
    for (let k = 0; k < 8; k++) { g.beginPath(); g.moveTo(64, k * 64 + 8); g.lineTo(100, k * 64 + 32); g.lineTo(64, k * 64 + 56); g.lineTo(28, k * 64 + 32); g.closePath(); g.stroke(); }
    const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace; tx.wrapT = THREE.RepeatWrapping; tx.repeat.set(1, 6);
    const m = new THREE.Mesh(new THREE.PlaneGeometry(8, 90), new THREE.MeshStandardMaterial({ map: tx, roughness: 0.9 }));
    m.rotation.x = -Math.PI / 2; m.position.set(0, 0.04, z + 45); m.receiveShadow = true;
    scene.add(m);
  }
  // banners on the back wall: a swallow-tailed cloth with a round emblem
  const bc = document.createElement("canvas"); bc.width = 128; bc.height = 320;
  const bg = bc.getContext("2d")!;
  bg.fillStyle = p.banner; bg.beginPath(); bg.moveTo(0, 0); bg.lineTo(128, 0); bg.lineTo(128, 320); bg.lineTo(64, 270); bg.lineTo(0, 320); bg.closePath(); bg.fill();
  bg.fillStyle = p.emblem; bg.beginPath(); bg.arc(64, 110, 30, 0, Math.PI * 2); bg.fill();
  bg.fillStyle = p.banner; bg.beginPath(); bg.arc(64, 110, 17, 0, Math.PI * 2); bg.fill();
  const bt = new THREE.CanvasTexture(bc); bt.colorSpace = THREE.SRGBColorSpace;
  const bm = new THREE.MeshStandardMaterial({ map: bt, transparent: true, alphaTest: 0.5, roughness: 0.9, side: THREE.DoubleSide });
  for (const x of [-22, -11, 11, 22]) { const m = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 8.5), bm); m.position.set(x, H - 6.5, z + 0.1); scene.add(m); }
  // torches on the wall either side of the gate
  if (!p.torches) return [];
  return [-7.5, 7.5, -16.5, 16.5].map((x, i) => {
    const bracket = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.12, 1.6, 6), bars);
    bracket.position.set(x, 7.2, z + 0.6); bracket.rotation.x = -0.5;
    scene.add(bracket);
    const f = vfx.get("flame")({ pos: [x, 7.9, z + 1.0], size: 1.3, light: i < 2 ? 9 : 0 }, seed + i * 13);
    scene.add(f.object);
    return f;
  });
};
