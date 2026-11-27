// Preview sheets for authoring a video: they work with any cast (pass { cast } as props, or the default cast is used).
//   sheet.cast  — every character in a row, turning 12 degrees per frame
//   sheet.faces — every expression on the first character
//   sheet.clips — every clip on the first character, all starting at frame 0
import * as THREE from "three";
import defaultCast from "../../../data/cast.json";
import { castFile } from "../../schema/cast";
import { clips, evalClip } from "../anim/clips";
import { Avatar } from "../avatar/build";
import { EXPRESSIONS } from "../avatar/faces";
import { dayRig, programs, type Engine } from "../Engine";

const castOf = (props: Record<string, unknown>) => castFile.parse(props.cast ?? defaultCast);
/** lay items out in rows facing the camera and frame them all */
const grid = (e: Engine, n: number, perRow: number, dx: number, dz: number, place: (i: number, x: number, z: number) => void) => {
  const rows = Math.ceil(n / perRow);
  for (let i = 0; i < n; i++) place(i, ((i % perRow) - (Math.min(n, perRow) - 1) / 2) * dx, -Math.floor(i / perRow) * dz);
  const w = Math.min(n, perRow) * dx, depth = rows * dz;
  const dist = Math.max(w / (2 * Math.tan((47 * Math.PI) / 360) * (e.width / e.height)), 12) + depth * 0.6;
  e.camera.position.set(0, 6 + rows * 2.2, dist);
  e.camera.lookAt(0, 2.2, -depth * 0.4);
};

programs.add("sheet.cast", (e, props) => {
  dayRig(e.scene, 30);
  const cast = castOf(props), ids = Object.keys(cast);
  const avatars: Avatar[] = [];
  grid(e, ids.length, 5, 4.4, 6.5, (i, x, z) => {
    const a = new Avatar(cast[ids[i]], "neutralTalk");
    a.root.position.set(x, 0, z);
    e.scene.add(a.root);
    avatars.push(a);
  });
  return (frame) => avatars.forEach((a) => (a.root.rotation.y = THREE.MathUtils.degToRad(frame * 12)));
});

programs.add("sheet.faces", (e, props) => {
  dayRig(e.scene, 30);
  const cast = castOf(props), def = cast[Object.keys(cast)[0]], names = Object.keys(EXPRESSIONS);
  // heads only, close enough to read every drawing; order matches Object.keys(EXPRESSIONS): left to right, top to bottom
  names.forEach((n, i) => {
    const a = new Avatar(def, n);
    a.showOnlyHead();
    a.root.position.set(((i % 6) - 2.5) * 1.9, -Math.floor(i / 6) * 1.9, 0);
    e.scene.add(a.root);
  });
  const rows = Math.ceil(names.length / 6), cy = 4.55 - ((rows - 1) * 1.9) / 2;
  e.camera.fov = 30;
  e.camera.updateProjectionMatrix();
  e.camera.position.set(0, cy, 17.5);
  e.camera.lookAt(0, cy, 0);
  return () => {};
});

programs.add("sheet.clips", (e, props) => {
  dayRig(e.scene, 30);
  const cast = castOf(props), def = cast[Object.keys(cast)[0]], ids = clips.ids().filter((c) => c !== "rest");
  const avatars: { a: Avatar; clip: string }[] = [];
  grid(e, ids.length, 4, 5.2, 7.5, (i, x, z) => {
    const a = new Avatar(def, "neutralTalk");
    a.root.position.set(x, 0, z);
    a.root.rotation.y = 0.35;
    e.scene.add(a.root);
    avatars.push({ a, clip: ids[i] });
  });
  return (frame) => avatars.forEach(({ a, clip }) => a.setPose(evalClip(clip, frame)));
});
