// The reel program: renders a list of shots (shots.json) back to back. Each shot gets its own stage (scene, camera,
// post chain), built the first time one of its frames is requested. Everything is a pure function of the frame.
import * as THREE from "three";
import cast from "../../../data/cast.json";
import { castFile } from "../../schema/cast";
import { shotsFile, type ShotSpec } from "../../schema/shots";
import { evalClip, clips, type Pose } from "../anim/clips";
import { Avatar } from "../avatar/build";
import { EXPRESSIONS } from "../avatar/faces";
import { cameraSpeed, evalCamera } from "../camera/eval";
import { evalStep } from "../core/ease";
import { programs, type Engine, type Stage } from "../Engine";
import { applyLook, contactShadow, looks } from "../looks";
import { sets } from "../sets";
import { buildCrowd } from "../avatar/crowd";
import { vfx } from "../vfx";
import { hash01 } from "../core/rng";
import type { Mouth } from "../avatar/faces";

const STRIDE: Record<string, number> = { walk: 4.6, runLeaning: 6.5 }; // studs covered by one loop of the clip
const TALK: Mouth[] = ["bigD", "smallD", "o", "smallD"];                 // mouth shapes cycled while a word is spoken, 3 frames each

const SAMPLES = 8; // the reference smears into about 8 discrete ghost copies
const BLUR_DEG = 0.45, BLUR_MOVE = 0.35; // per-frame camera turn (deg) / travel (studs) above which a frame is blurred

type Built = { stage: Stage; spec: ShotSpec; start: number; update: (local: number) => void; seed: number };

const buildShot = (e: Engine, spec: ShotSpec, start: number, index: number, CAST: ReturnType<typeof castFile.parse>): Built => {
  const scene = new THREE.Scene();
  const camera = e.makeCamera(spec.camera.fov ?? 47);
  const look = { ...looks.get(spec.look), ...(spec.lookOverrides as object | undefined) } as ReturnType<typeof looks.get>;
  const focus = spec.actors[0] ? new THREE.Vector3(spec.actors[0].pos[0], 2, spec.actors[0].pos[1]) : new THREE.Vector3(0, 2, 0);
  applyLook(scene, look, spec.shadow ? new THREE.Vector3(...spec.shadow.focus) : focus, spec.shadow?.extent ?? 14);
  const setFx = sets.get(spec.set)(scene, spec.setParams ?? {}, index * 7919 + 13) ?? [];
  const actors = spec.actors.map((a) => {
    const def = CAST[a.character];
    if (!def) throw new Error(`shot ${spec.id}: unknown character "${a.character}". Known: ${Object.keys(CAST).join(", ")}`);
    for (const c of a.clips ?? []) clips.get(c.clip); // fail early on unknown clips
    for (const f of a.faces ?? []) if (!EXPRESSIONS[f.v]) throw new Error(`shot ${spec.id}: unknown expression "${f.v}"`);
    const av = new Avatar(def, a.faces?.[0]?.v ?? "neutralTalk");
    av.root.position.set(a.pos[0], 0, a.pos[1]);
    av.root.rotation.y = THREE.MathUtils.degToRad(a.yaw ?? 0);
    scene.add(av.root);
    if (a.prop === "spear") {
      // a pole standing on the ground beside the hand, with a small square flag (the arm stays down in the reference)
      const hand = av.handAnchor("R"), g = new THREE.Group();
      const wood = new THREE.MeshStandardMaterial({ color: "#6a4a32", roughness: 0.8 });
      const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 9, 8), wood);
      pole.position.y = 2.5;
      const tip = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.9, 6), new THREE.MeshStandardMaterial({ color: "#2a2422", roughness: 0.5 }));
      tip.position.y = 7.45;
      const flag = new THREE.Mesh(new THREE.BoxGeometry(0.45, 1.2, 0.05), new THREE.MeshStandardMaterial({ color: a.propColor ?? "#c8201c", roughness: 0.8 }));
      flag.position.set(-0.38, 5.4, 0); // small narrow flag below the tip, as on f01779
      g.add(pole, tip, flag);
      g.position.set(-0.05, 0, 0.66); // measured on f01779: the pole stands 1.55 studs from the body centre, in front of the arm
      g.traverse((o) => { o.castShadow = true; });
      hand.add(g);
    }
    const blob = contactShadow(3.4, a.contactShadow ?? 0.7);
    blob.position.set(a.pos[0], 0.02, a.pos[1]);
    scene.add(blob);
    // where the actor is at local frame f, and how far they have travelled by then
    const path = a.path && a.path.length > 1 ? a.path : null;
    const at = (f: number): [number, number, number, number] => {   // x, z, distance so far, heading (radians)
      if (!path) return [a.pos[0], a.pos[1], 0, THREE.MathUtils.degToRad(a.yaw ?? 0)];
      let dist = 0, x = path[0].pos[0], z = path[0].pos[1], head = THREE.MathUtils.degToRad(a.yaw ?? 0);
      for (let i = 1; i < path.length; i++) {
        const p = path[i - 1], q = path[i], dx = q.pos[0] - p.pos[0], dz = q.pos[1] - p.pos[1], len = Math.hypot(dx, dz);
        const u = q.f === p.f ? 1 : Math.min(1, Math.max(0, (f - p.f) / (q.f - p.f)));
        if (len > 0.001 && (u > 0 || i === 1)) head = Math.atan2(dx, dz);
        x = p.pos[0] + dx * u; z = p.pos[1] + dz * u; dist += len * u;
        if (u < 1) break;
      }
      return [x, z, dist, a.yaw !== undefined ? THREE.MathUtils.degToRad(a.yaw) : head];
    };
    return { av, a, at, blob, path };
  });
  const seed = index * 7919 + 13;
  const fx = (spec.vfx ?? []).map((v, k) => {
    const built = vfx.get(v.type)(v as Record<string, any>, seed + k * 101);
    scene.add(built.object);
    const q = v as Record<string, any>;   // "follow": index of the actor this effect travels with, "lag": frames it trails behind
    return { ...built, follow: typeof q.follow === "number" ? (q.follow as number) : -1, lag: (q.lag as number) ?? 0 };
  });
  const crowds = (spec.crowds ?? []).map((c, k) => {
    const built = buildCrowd({ ...c, seed: c.seed ?? seed + k });
    scene.add(built.object);
    return built;
  });
  const update = (local: number) => {
    actors.forEach(({ av, a, at, blob, path }, ai) => {
      const [x, z, dist, heading] = at(local);
      av.root.position.set(x, 0, z); av.root.rotation.y = heading; blob.position.set(x, 0.02, z);
      const pose: Pose = {};
      for (const c of [...(a.clips ?? [])].sort((p, q) => p.at - q.at)) if (local >= c.at) {
        // a walker's steps follow the ground: the loop advances with the distance covered, not with time
        const t = path && STRIDE[c.clip] ? (dist / STRIDE[c.clip]) * (clips.get(c.clip).period ?? 20) : local - c.at;
        Object.assign(pose, evalClip(c.clip, t));
      }
      const k = Math.ceil(local);                                   // faces change on whole frames
      const word = (a.talk ?? []).find(([f0, f1]) => k >= f0 && k < f1);
      const mouth = word ? TALK[(Math.floor((k - word[0]) / 3) + (word[1] - word[0] > 9 ? 0 : 1)) % TALK.length] : undefined;
      if (word && k - word[0] < 3) pose.headPitch = (pose.headPitch ?? 0) + 4;   // a small nod on each word
      const period = 78 + Math.floor(hash01(ai * 17 + 3, seed) * 44), off = Math.floor(hash01(ai * 29 + 11, seed) * period);
      const blink = a.blink !== false && ((k + off) % period) < 3;
      av.setPose(pose);
      av.setExpression(a.faces?.length ? evalStep(a.faces, k) : "neutralTalk", mouth || blink || a.look ? { mouth, blink, look: a.look } : undefined);
    });
    evalCamera(camera, spec.camera, local, seed);
    for (const c of crowds) c.update(local);
    for (const v of fx) {
      if (v.follow >= 0 && actors[v.follow]) {
        const who = actors[v.follow], [x, z] = who.at(local - v.lag);
        v.object.position.set(x - who.a.pos[0], 0, z - who.a.pos[1]);
      }
      v.update(local, camera);
    }
    for (const v of setFx) v.update(local, camera);
  };
  return { stage: { scene, camera, post: look.post }, spec, start, update, seed };
};

programs.add("reel", (e, props) => {
  const file = shotsFile.parse(props);
  const CAST = castFile.parse(file.cast ?? cast); // a video brings its own characters; data/cast.json is only the fallback
  const starts: number[] = [];
  let total = 0;
  for (const s of file.shots) { starts.push(total); total += s.frames; }
  const built = new Map<number, Built>();
  // a time t in (n-1, n] belongs to whole frame n, so sub-frame samples never cross a cut
  const at = (t: number) => {
    const n = Math.min(total - 1, Math.max(0, Math.ceil(t)));
    let i = starts.length - 1;
    while (i > 0 && starts[i] > n) i--;
    let b = built.get(i);
    if (!b) {
      // keep at most two shots alive (the one being drawn and its neighbour); a 100-shot video would otherwise exhaust the GPU
      for (const [k, old] of built) if (built.size >= 2 && k !== i) { e.release(old.stage); built.delete(k); }
      built.set(i, (b = buildShot(e, file.shots[i], starts[i], i, CAST)));
    }
    return b;
  };
  return {
    update: (t) => {
      const b = at(t);
      b.update(t - b.start + (b.spec.startAt ?? 0));
      e.setStage(b.stage);
    },
    samples: (frame) => {
      const b = at(frame), mb = b.spec.motionBlur ?? "auto", local = frame - b.start + (b.spec.startAt ?? 0);
      if (mb === "off") return 1;
      if (Array.isArray(mb)) return mb.some(([a, z]) => local >= a && local <= z) ? SAMPLES : 1;
      const sp = cameraSpeed(b.stage.camera, b.spec.camera, local, b.seed);
      return sp.deg > BLUR_DEG || sp.move > BLUR_MOVE ? SAMPLES : 1;
    },
  };
});
