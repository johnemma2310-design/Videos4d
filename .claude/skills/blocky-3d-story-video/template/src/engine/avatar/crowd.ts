// Instanced crowds: hundreds of simplified avatars (two legs, torso, two arms, head with a drawn face, hair cap) in a
// few draw calls. Members stand, cheer, walk or run; walkers really travel across the ground and wrap around inside
// the crowd's rectangle. Every member has a face (grouped by skin and expression) and blinks.
// Everything is a function of (frame, seed).
import * as THREE from "three";
import { hash01, rng } from "../core/rng";
import { headGeometry } from "./build";
import { headTexture } from "./outfits";

export const PALETTES: Record<string, { shirts: string[]; legs: string[]; flag: string }> = {
  fire: { shirts: ["#b3262a", "#f2d31c", "#1c1a1a", "#7a1218", "#8e1622", "#efe9e2", "#c0502a"], legs: ["#2b2726", "#5a3a22", "#3a3d44", "#7a3d22"], flag: "#c8201c" },
  water: { shirts: ["#35b890", "#178a86", "#7ad0e0", "#f2f2f2", "#6a3f9c", "#a8c9a8", "#2a6aa8"], legs: ["#2b2726", "#0a359c", "#577586", "#6c6768"], flag: "#1f7a70" },
};
const SKINS = ["#e8c6a2", "#d7a07c", "#c98f66", "#8a5a3a", "#f0d2b4", "#4a2c22"];
const HAIRS = ["#17120f", "#3a2418", "#7a3a22", "#c9a878", "#e3cf7a", "#c4201a", "#6a6e74"];
/** the faces a crowd wears, by mood */
export const MOODS: Record<string, string[]> = {
  calm: ["happyArcs", "neutralTalk", "dotSmile", "blank", "bigHappy"],
  worried: ["worried", "blank", "nervous", "neutralTalk"],
  panic: ["scream", "worried", "hollowShock", "nervous", "scream"],
  cheer: ["bigHappy", "laugh", "happyArcs", "bigHappy"],
  stunned: ["blank", "hollowShock", "blank", "worried"],
};

export type CrowdSpec = {
  palette: "fire" | "water";
  count: number;
  /** ground rectangle [x0, z0, x1, z1] */
  area: [number, number, number, number];
  /** degrees; 0 faces +Z */
  facing?: number;
  /** fraction that cheer (arms-up loop), and fraction carrying spears */
  cheer?: number;
  spears?: number;
  seed?: number;
  /** which faces the members wear (default calm; cheer > 0.4 defaults to cheer) */
  mood?: string;
  /** fraction that walk (0..1); they travel along walkDir (degrees, default = facing), half of them the other way if bothWays */
  walk?: number;
  walkDir?: number;
  bothWays?: boolean;
  /** studs per frame (walk 0.2, run 0.42) and running pose */
  speed?: number;
  run?: boolean;
};

export const buildCrowd = (spec: CrowdSpec) => {
  const n = spec.count, seed = spec.seed ?? 1, r = rng(seed), pal = PALETTES[spec.palette];
  const g = new THREE.Group();
  const m = (roughness = 0.85) => new THREE.MeshStandardMaterial({ roughness });
  const mk = (geo: THREE.BufferGeometry, count = n) => {
    const im = new THREE.InstancedMesh(geo, m(), count);
    im.castShadow = true; im.receiveShadow = true; im.frustumCulled = false;
    g.add(im);
    return im;
  };
  const leg = () => new THREE.BoxGeometry(0.975, 2, 1).translate(0, -1, 0); // pivot at the hip
  const legL = mk(leg()), legR = mk(leg()), torso = mk(new THREE.BoxGeometry(2, 2, 1));
  const armL = mk(new THREE.BoxGeometry(1, 2, 1).translate(0.5, -1, 0)), armR = mk(new THREE.BoxGeometry(1, 2, 1).translate(-0.5, -1, 0));
  const hair = mk(new THREE.SphereGeometry(0.68, 10, 5, 0, Math.PI * 2, 0, Math.PI / 2).scale(1, 0.75, 1));
  const [x0, z0, x1, z1] = spec.area, W = Math.max(0.01, x1 - x0), D = Math.max(0.01, z1 - z0);
  const faces = MOODS[spec.mood ?? ((spec.cheer ?? 0) > 0.4 ? "cheer" : "calm")] ?? MOODS.calm;
  const baseYaw = ((spec.facing ?? 0) * Math.PI) / 180, walkYaw = ((spec.walkDir ?? spec.facing ?? 0) * Math.PI) / 180;
  const speed = spec.speed ?? (spec.run ? 0.42 : 0.2), stride = spec.run ? 6.5 : 4.6;
  const who = Array.from({ length: n }, (_, i) => {
    const walking = r() < (spec.walk ?? 0), back = !!spec.bothWays && r() < 0.5;
    return {
      x: x0 + r() * W, z: z0 + r() * D, yaw: baseYaw + (r() - 0.5) * 0.5, walking, travel: walkYaw + (back ? Math.PI : 0),
      cheer: !walking && r() < (spec.cheer ?? 0.15), spear: r() < (spec.spears ?? 0), phase: r() * 12, rate: 0.8 + r() * 0.45, i,
      skin: Math.floor(r() * SKINS.length), face: Math.floor(r() * faces.length), slot: 0,
    };
  });
  const c = new THREE.Color();
  who.forEach((w, i) => {
    const shirt = pal.shirts[Math.floor(r() * pal.shirts.length)], legc = pal.legs[Math.floor(r() * pal.legs.length)];
    torso.setColorAt(i, c.set(shirt)); armL.setColorAt(i, c.set(shirt)); armR.setColorAt(i, c.set(shirt));
    legL.setColorAt(i, c.set(legc)); legR.setColorAt(i, c.set(legc));
    hair.setColorAt(i, c.set(HAIRS[Math.floor(r() * HAIRS.length)]));
  });
  // heads: one instanced mesh per (skin, face), so every member has a drawn face and the group can blink
  const groups = new Map<string, { im: THREE.InstancedMesh; mat: THREE.MeshStandardMaterial; skin: string; face: string; k: number }>();
  const tally = new Map<string, number>();
  for (const w of who) { const key = w.skin + ":" + w.face; w.slot = tally.get(key) ?? 0; tally.set(key, w.slot + 1); }
  let gi = 0;
  for (const [key, count] of tally) {
    const [s, f] = key.split(":").map(Number), mat = new THREE.MeshStandardMaterial({ roughness: 0.7, map: headTexture(SKINS[s], faces[f]) });
    const im = new THREE.InstancedMesh(headGeometry(), mat, count);
    im.castShadow = true; im.frustumCulled = false; g.add(im);
    groups.set(key, { im, mat, skin: SKINS[s], face: faces[f], k: gi++ });
  }
  // spears: pole + square flag, standing beside the carrier
  const carriers = who.filter((w) => w.spear && !w.walking);
  if (carriers.length) {
    const poles = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.09, 0.09, 8.5, 6).translate(0, 4.25, 0), new THREE.MeshStandardMaterial({ color: "#6a4a32", roughness: 0.8 }), carriers.length);
    const flags = new THREE.InstancedMesh(new THREE.BoxGeometry(1.3, 0.9, 0.05).translate(0.7, 7.7, 0), new THREE.MeshStandardMaterial({ color: pal.flag, roughness: 0.8 }), carriers.length);
    const tips = new THREE.InstancedMesh(new THREE.ConeGeometry(0.2, 0.8, 5).translate(0, 8.9, 0), new THREE.MeshStandardMaterial({ color: "#2a2422", roughness: 0.5 }), carriers.length);
    const M = new THREE.Matrix4();
    carriers.forEach((w, k) => {
      M.makeRotationY(w.yaw).setPosition(w.x + Math.cos(w.yaw) * 1.6, 0, w.z - Math.sin(w.yaw) * 1.6);
      poles.setMatrixAt(k, M); flags.setMatrixAt(k, M); tips.setMatrixAt(k, M);
    });
    for (const im of [poles, flags, tips]) { im.castShadow = true; im.frustumCulled = false; g.add(im); }
  }

  const base = new THREE.Matrix4(), local = new THREE.Matrix4(), rot = new THREE.Matrix4(), out = new THREE.Matrix4(), tilt = new THREE.Matrix4();
  const put = (im: THREE.InstancedMesh, i: number, x: number, y: number, z: number, rx = 0) => {
    local.makeTranslation(x, y, z);
    if (rx) local.multiply(rot.makeRotationX(rx));
    im.setMatrixAt(i, out.multiplyMatrices(base, local));
  };
  const wrap = (v: number, lo: number, span: number) => lo + ((((v - lo) % span) + span) % span);
  const update = (f: number) => {
    for (const w of who) {
      let up = 0, upR = 0, bob = 0, swing = 0, x = w.x, z = w.z, yaw = w.yaw;
      if (w.walking) {
        const dist = speed * w.rate * f + w.phase * 3;
        // walk to the end of the rectangle, turn round, walk back (no popping from one end to the other)
        const alongX = Math.abs(Math.sin(w.travel)) > Math.abs(Math.cos(w.travel)), L = alongX ? W : D, sign = (alongX ? Math.sin(w.travel) : Math.cos(w.travel)) >= 0 ? 1 : -1;
        const s0 = alongX ? w.x - x0 : w.z - z0, u = wrap(s0 + sign * dist, 0, 2 * L), fwd = u < L, s = fwd ? u : 2 * L - u;
        if (alongX) x = x0 + s; else z = z0 + s;
        yaw = alongX ? (fwd ? Math.PI / 2 : -Math.PI / 2) : fwd ? 0 : Math.PI;
        const ph = (dist / stride) * Math.PI * 2;
        swing = Math.sin(ph) * (spec.run ? 0.96 : 0.61); bob = 0.08 * Math.abs(Math.sin(ph));
        up = spec.run ? -0.7 : -swing * 0.85; upR = spec.run ? -0.7 : swing * 0.85;
      } else if (w.cheer) {
        const t = ((f * w.rate + w.phase) / 12) * Math.PI * 2;
        up = (162 + 12 * Math.sin(t)) * (Math.PI / 180); upR = up * 0.93;
        bob = 0.15 * Math.abs(Math.sin(t));
      } else if (hash01(w.i, seed) < 0.25) up = upR = 0.1; // a few hold their arms slightly forward
      base.makeRotationY(yaw).setPosition(x, bob, z);
      if (w.walking && spec.run) base.multiply(tilt.makeRotationX(0.42)); // lean into the run
      put(legL, w.i, 0.5, 2, 0, -swing); put(legR, w.i, -0.5, 2, 0, swing);
      put(torso, w.i, 0, 3, 0); put(hair, w.i, 0, 4.72, 0);
      put(armL, w.i, 1, 4, 0, -up); put(armR, w.i, -1, 4, 0, -upR);
      const grp = groups.get(w.skin + ":" + w.face)!;
      put(grp.im, w.slot, 0, 3.96, 0);
    }
    for (const im of [legL, legR, torso, armL, armR, hair]) im.instanceMatrix.needsUpdate = true;
    const k = Math.ceil(f);
    for (const grp of groups.values()) {
      grp.im.instanceMatrix.needsUpdate = true;
      // each face group blinks on its own schedule: 3 frames shut about every 2.5 to 4 seconds
      const period = 75 + Math.floor(hash01(grp.k * 13 + 5, seed) * 45), off = Math.floor(hash01(grp.k * 7 + 1, seed) * period);
      const blink = ((k + off) % period) < 3;
      const map = headTexture(grp.skin, grp.face, blink ? { blink: true } : undefined);
      if (grp.mat.map !== map) { grp.mat.map = map; grp.mat.needsUpdate = true; }
    }
  };
  update(0);
  return { object: g, update };
};
