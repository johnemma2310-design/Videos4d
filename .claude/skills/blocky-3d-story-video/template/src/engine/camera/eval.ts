// Camera evaluation: keyframed position + target with per-segment easing, spherical interpolation around the target
// (so arcs keep their radius and a linear ease on distance gives the constant %-per-frame creep measured on the
// reference), plus additive shake. Pure function of the (possibly fractional) local frame.
import * as THREE from "three";
import { ease } from "../core/ease";
import { hash01 } from "../core/rng";

export type V3 = [number, number, number];
export type CamKey = { f: number; pos: V3; target: V3; ease?: string };
/** alt = sign flips every frame (15 Hz, as measured); random = redrawn every frame from a hash */
export type Shake = { f0: number; f1: number; ampDeg: [number, number]; mode?: "alt" | "random"; decay?: number; bursts?: number };
export type CameraSpec = { fov?: number; keys: CamKey[]; shake?: Shake[]; roll?: number };

const d2r = Math.PI / 180;
const va = new THREE.Vector3(), vb = new THREE.Vector3(), tgt = new THREE.Vector3();
const sa = new THREE.Spherical(), sb = new THREE.Spherical(), s = new THREE.Spherical();

export const evalCamera = (cam: THREE.PerspectiveCamera, spec: CameraSpec, f: number, seed = 0) => {
  const k = spec.keys;
  let i = 1;
  while (i < k.length - 1 && f > k[i].f) i++;
  const a = k[Math.max(0, i - 1)], b = k[Math.min(i, k.length - 1)];
  const e = a === b ? 0 : ease(b.ease ?? "linear", (f - a.f) / (b.f - a.f));
  tgt.fromArray(a.target).lerp(vb.fromArray(b.target), e);
  sa.setFromVector3(va.fromArray(a.pos).sub(vb.fromArray(a.target)));
  sb.setFromVector3(va.fromArray(b.pos).sub(vb.fromArray(b.target)));
  let dTheta = sb.theta - sa.theta;
  dTheta = Math.atan2(Math.sin(dTheta), Math.cos(dTheta));
  s.set(sa.radius * Math.pow(sb.radius / sa.radius, e), sa.phi + (sb.phi - sa.phi) * e, sa.theta + dTheta * e);
  cam.position.setFromSpherical(s).add(tgt);
  cam.up.set(0, 1, 0);
  cam.lookAt(tgt);

  // shake: an offset drawn for every whole frame; sub-frame samples slide between consecutive offsets, so shaken
  // frames smear (the reference shows motion blur along the shake direction)
  const n1 = Math.ceil(f), frac = f - (n1 - 1);
  let yaw = 0, pitch = 0;
  for (const sh of spec.shake ?? []) {
    const off = (n0: number): [number, number] => {
      if (n0 < sh.f0 || n0 > sh.f1) return [0, 0];
      const n = n0 - sh.f0, len = sh.f1 - sh.f0 + 1;
      let env = sh.decay ? Math.pow(sh.decay, n) : 1;
      if (sh.bursts) env *= Math.abs(Math.sin((Math.PI * sh.bursts * n) / len));
      const alt = (sh.mode ?? "alt") === "alt";
      const sx = alt ? (n % 2 ? -1 : 1) : hash01(n0 * 2 + 1, seed) * 2 - 1;
      const sy = alt ? (n % 2 ? 1 : -1) : hash01(n0 * 2 + 2, seed) * 2 - 1;
      return [sh.ampDeg[0] * env * sx, sh.ampDeg[1] * env * sy];
    };
    const p = off(n1 - 1), q = off(n1);
    yaw += p[0] + (q[0] - p[0]) * frac;
    pitch += p[1] + (q[1] - p[1]) * frac;
  }
  if (yaw || pitch) { cam.rotateY(yaw * d2r); cam.rotateX(pitch * d2r); }
  if (spec.roll) cam.rotateZ(spec.roll * d2r);
  cam.updateMatrixWorld();
};

/** angle in degrees between the view directions at two times, plus relative distance change: drives auto motion blur */
export const cameraSpeed = (cam: THREE.PerspectiveCamera, spec: CameraSpec, f: number, seed = 0) => {
  evalCamera(cam, spec, f - 1, seed);
  const d0 = cam.getWorldDirection(new THREE.Vector3()), p0 = cam.position.clone();
  evalCamera(cam, spec, f, seed);
  const d1 = cam.getWorldDirection(new THREE.Vector3());
  return { deg: (Math.acos(Math.min(1, d0.dot(d1))) * 180) / Math.PI, move: p0.distanceTo(cam.position) };
};
