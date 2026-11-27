// Hair and hats: separate faceted low-poly meshes sitting on the head (head: radius 0.6, height 1.2, origin at the chin).
import * as THREE from "three";

export type HairStyle = "sidePart" | "bob" | "long" | "ponytail" | "tufts" | "bun" | "curly" | "spikyTop" | "bald" | "beanie" | "rainHat";

const cap = (r: number, h: number, seg = 9) => {
  // faceted dome covering the top of the head
  const g = new THREE.SphereGeometry(r, seg, 4, 0, Math.PI * 2, 0, Math.PI / 2);
  g.scale(1, h / r, 1);
  return g;
};
const add = (grp: THREE.Group, geo: THREE.BufferGeometry, mat: THREE.Material, p: [number, number, number], rot: [number, number, number] = [0, 0, 0], s: [number, number, number] = [1, 1, 1]) => {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(...p); m.rotation.set(...rot); m.scale.set(...s);
  m.castShadow = true;
  grp.add(m);
  return m;
};

export const buildHair = (style: HairStyle, color: string) => {
  const grp = new THREE.Group();
  if (style === "bald") return grp;
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.75, flatShading: true });
  const R = 0.66;
  const spike = new THREE.ConeGeometry(0.16, 0.42, 4);
  const box = new THREE.BoxGeometry(1, 1, 1);
  switch (style) {
    case "sidePart": { // H01: smooth swept cap sitting low on the forehead, lower on one side, short pointed sideburns
      const smooth = new THREE.MeshStandardMaterial({ color, roughness: 0.75 });
      // hairline: high over the forehead (tilted back), lower at the back; tilted sideways so one side sits lower
      const dome = new THREE.SphereGeometry(0.71, 16, 8, 0, Math.PI * 2, 0, Math.PI * 0.5);
      add(grp, dome, smooth, [0, 0.8, -0.05], [-0.3, 0, -0.14], [1, 0.86, 1.03]);
      add(grp, new THREE.SphereGeometry(0.3, 10, 6), smooth, [0.22, 1.0, 0.34], [0, 0, -0.3], [1.25, 0.5, 1]); // the swept fringe bulge
      for (const sx of [-1, 1]) add(grp, spike, smooth, [sx * 0.59, 0.72, 0.1], [Math.PI, 0, 0], [0.3, 0.6, 0.8]);
      break;
    }
    case "bob": // H02: shoulder-length straight bob with a straight fringe
      add(grp, cap(R, 0.4), mat, [0, 0.9, 0]);
      add(grp, box, mat, [0, 0.42, -0.34], [0, 0, 0], [1.34, 1.05, 0.66]);
      for (const sx of [-1, 1]) add(grp, box, mat, [sx * 0.6, 0.45, 0], [0, 0, 0], [0.16, 1.0, 0.9]);
      add(grp, box, mat, [0, 0.98, 0.52], [0, 0, 0], [1.1, 0.2, 0.16]);
      break;
    case "long": // H03: long layered hair, one thick lock in front of the shoulder
      add(grp, cap(R + 0.04, 0.48), mat, [0, 0.9, 0]);
      add(grp, box, mat, [0, 0.1, -0.4], [0.08, 0, 0], [1.4, 1.9, 0.6]);
      add(grp, box, mat, [0.62, 0.0, 0.2], [0, 0, 0.08], [0.34, 1.8, 0.4]);
      add(grp, box, mat, [-0.62, 0.45, 0.05], [0, 0, 0], [0.18, 1.0, 0.8]);
      add(grp, spike, mat, [0.2, 0.98, 0.5], [1.75, 0, 0.9], [1.1, 1.1, 0.6]);
      break;
    case "ponytail": // H04
      add(grp, cap(R + 0.02, 0.46), mat, [0, 0.9, 0]);
      add(grp, box, mat, [0, 0.65, -0.3], [0, 0, 0], [1.3, 0.6, 0.7]);
      add(grp, box, mat, [0.5, -0.1, -0.2], [0, 0, 0.12], [0.36, 1.7, 0.36]);
      break;
    case "tufts": // H05
      add(grp, cap(R, 0.36), mat, [0, 0.92, 0]);
      for (let i = 0; i < 6; i++) add(grp, spike, mat, [Math.cos(i * 1.05) * 0.36, 1.2, Math.sin(i * 1.05) * 0.36], [Math.sin(i) * 0.5, 0, Math.cos(i * 2) * 0.5], [0.8, 0.7, 0.8]);
      break;
    case "bun": // H06
      add(grp, cap(R, 0.4), mat, [0, 0.9, 0]);
      add(grp, new THREE.IcosahedronGeometry(0.26, 0), mat, [0, 1.42, -0.1]);
      break;
    case "curly": // H07
      for (let i = 0; i < 9; i++) add(grp, new THREE.IcosahedronGeometry(0.3, 0), mat, [Math.cos(i * 0.7) * 0.42 * (i < 8 ? 1 : 0), 0.95 + (i % 3) * 0.13, Math.sin(i * 0.7) * 0.42 * (i < 8 ? 1 : 0) - 0.05]);
      break;
    case "spikyTop": // H08
      add(grp, cap(R, 0.3), mat, [0, 0.92, 0]);
      for (let i = 0; i < 7; i++) add(grp, spike, mat, [Math.cos(i * 0.9) * 0.3, 1.32, Math.sin(i * 0.9) * 0.3], [0, i, 0], [0.9, 1.3, 0.9]);
      break;
    case "rainHat": // a domed hat with a wide brim, lower at the back
      mat.flatShading = false;
      add(grp, cap(R + 0.04, 0.6, 20), mat, [0, 0.8, 0]);
      add(grp, new THREE.CylinderGeometry(R + 0.42, R + 0.5, 0.09, 24), mat, [0, 0.82, -0.06], [-0.12, 0, 0]);
      break;
    case "beanie": // H11
      mat.flatShading = false;
      add(grp, cap(R + 0.03, 0.62, 20), mat, [0, 0.78, 0]);
      add(grp, new THREE.CylinderGeometry(R + 0.06, R + 0.06, 0.2, 20), mat, [0, 0.82, 0]);
      break;
  }
  return grp;
};
