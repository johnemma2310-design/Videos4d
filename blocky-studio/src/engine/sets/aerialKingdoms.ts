// SET A — aerial map of the two kingdoms: a canal between the water town (x < 0, blue roofs) and the fire town
// (x > 0, red roofs), plains, landmarks, an island and smoke columns. Ported from the calibration test
// (reconstruction/poc, target f00050). The canal runs along -Z around x = 0; ground is y = 0; units are studs.
import * as THREE from "three";
import { makeRng, range, type Rng } from "../tex/pocRng";
import { noiseCanvas, softDiscTexture, toTexture } from "../tex/textures";

export interface TownParams {
  /** inner / outer edge measured outward from the water edge, near / far Z (positive numbers = distance ahead) */
  xInner: number;
  xOuter: number;
  zNear: number;
  zFar: number;
  ground: string;
  wall: string;
  roofs: string[];
  /** house footprint (w along X, d along Z), wall height, roof height */
  house: { w: number; d: number; h: number; roof: number };
  /** houses per block along X and Z, gap between houses, street width between blocks */
  block: { nx: number; nz: number; gap: number; street: number };
  /** fraction of house slots left empty */
  vacancy: number;
  jitter: number;
  /** rectangular clearings (plazas): [xCentre, zCentre, w, d] with x measured outward from the water edge */
  clearings: [number, number, number, number][];
  /** streets / side channels running across the town, perpendicular to the canal */
  crossStreets: { dist: number; width: number; color: string }[];
}

export interface LandmarkParams {
  /** signed world x, distance ahead (z = -dist) */
  x: number;
  dist: number;
  w: number;
  d: number;
  h: number;
  body: string;
  roof: string;
  /** number of corner / roof towers and their dome radius (0 = spires instead of domes) */
  towers: number;
  dome: number;
}

export interface AerialParams {
  /** seed for every procedural placement (houses, bushes, smoke puffs) */
  seed?: number;
  plain: { left: string; right: string; leftDark: string; rightDark: string; bushes: string; bushCount: number };
  canal: {
    halfWidth: number;
    /** the canal widens towards the camera: halfWidth * (1 + flare * exp(-dist / flareDist)) */
    flare: number;
    flareDist: number;
    /** centre line: x = amp * sin((dist - phase) / wavelength * 2pi) + drift * dist */
    curveAmp: number;
    curveWavelength: number;
    curvePhase: number;
    drift: number;
    waterDark: string;
    waterLight: string;
    foam: number;
    bankLeft: string;
    bankRight: string;
    bankWidth: number;
    grassStrip: string;
    length: number;
  };
  left: TownParams;
  right: TownParams;
  landmarks: LandmarkParams[];
  island: { dist: number; radius: number; color: string };
  smoke: { x: number; dist: number; height: number; radius: number; color: string; opacity: number; lean: number }[];
}

/** Gable-roof prism with unit footprint (x, z in -0.5..0.5) and unit height, ridge along Z. */
function gableGeometry(): THREE.BufferGeometry {
  const g = new THREE.BufferGeometry();
  // prettier-ignore
  const v = [
    // left slope
    -0.5, 0, 0.5, 0, 1, 0.5, 0, 1, -0.5, -0.5, 0, 0.5, 0, 1, -0.5, -0.5, 0, -0.5,
    // right slope
    0.5, 0, 0.5, 0.5, 0, -0.5, 0, 1, -0.5, 0.5, 0, 0.5, 0, 1, -0.5, 0, 1, 0.5,
    // front and back gables
    -0.5, 0, 0.5, 0.5, 0, 0.5, 0, 1, 0.5, 0.5, 0, -0.5, -0.5, 0, -0.5, 0, 1, -0.5,
  ];
  g.setAttribute("position", new THREE.Float32BufferAttribute(v, 3));
  g.computeVertexNormals();
  return g;
}

function canalCentre(c: AerialParams["canal"], dist: number): number {
  return c.curveAmp * Math.sin(((dist - c.curvePhase) / c.curveWavelength) * Math.PI * 2) + c.drift * dist;
}

/** Half width of the water at a given distance ahead. */
function canalHalfWidth(c: AerialParams["canal"], dist: number): number {
  return c.halfWidth * (1 + c.flare * Math.exp(-Math.max(dist, 0) / c.flareDist));
}

/**
 * Flat ribbon following the canal between two lateral offsets measured outward from the water edge
 * (side = -1 left, +1 right, 0 = the water itself spanning both edges). UV: u across, v along.
 */
function ribbon(c: AerialParams["canal"], side: -1 | 0 | 1, off0: number, off1: number, y: number, vScale: number, z0 = -200, z1 = c.length): THREE.BufferGeometry {
  const pos: number[] = [];
  const uv: number[] = [];
  const idx: number[] = [];
  const steps = 240;
  for (let i = 0; i <= steps; i++) {
    const dist = z0 + ((z1 - z0) * i) / steps;
    const cx = canalCentre(c, dist);
    const hw = canalHalfWidth(c, dist);
    const xa = side === 0 ? -hw : side * (hw + off0);
    const xb = side === 0 ? hw : side * (hw + off1);
    pos.push(cx + xa, y, -dist, cx + xb, y, -dist);
    uv.push(0, dist / vScale, 1, dist / vScale);
    if (i < steps) {
      const a = i * 2;
      idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

function buildTown(t: TownParams, side: -1 | 1, canal: AerialParams["canal"], rng: Rng): THREE.Group {
  const g = new THREE.Group();
  // town floor (streets / paving)
  const floorTex = toTexture(
    noiseCanvas({ size: 512, seed: side + 20, dark: new THREE.Color(t.ground).multiplyScalar(0.8).getStyle(), light: t.ground, baseCells: 16, contrast: 1.2, grain: 0.2 }),
    [20, 40],
  );
  const floor = new THREE.Mesh(
    ribbon(canal, side, t.xInner, t.xOuter, 0.2, 400, t.zNear - 60, t.zFar + 8),
    new THREE.MeshStandardMaterial({ map: floorTex, roughness: 1, side: THREE.DoubleSide }),
  );
  floor.receiveShadow = true;
  g.add(floor);

  const cellX = t.house.w + t.block.gap;
  const cellZ = t.house.d + t.block.gap;
  const blockX = t.block.nx * cellX + t.block.street;
  const blockZ = t.block.nz * cellZ + t.block.street;
  const slots: { x: number; z: number; yaw: number; s: number }[] = [];
  for (let bz = t.zNear; bz < t.zFar; bz += blockZ) {
    for (let bx = t.xInner; bx < t.xOuter; bx += blockX) {
      for (let iz = 0; iz < t.block.nz; iz++) {
        for (let ix = 0; ix < t.block.nx; ix++) {
          if (rng() < t.vacancy) continue;
          const dist = bz + iz * cellZ + cellZ / 2 + range(rng, -t.jitter, t.jitter);
          const off = bx + ix * cellX + cellX / 2 + range(rng, -t.jitter, t.jitter);
          if (off > t.xOuter || dist > t.zFar) continue;
          if (t.crossStreets.some((c) => Math.abs(dist - c.dist) < c.width / 2 + t.house.d / 2)) continue;
          if (t.clearings.some(([cx, cz, w, d]) => Math.abs(off - cx) < w / 2 && Math.abs(dist - cz) < d / 2)) continue;
          slots.push({ x: canalCentre(canal, dist) + side * (canalHalfWidth(canal, dist) + off), z: -dist, yaw: rng() < 0.5 ? 0 : Math.PI / 2, s: range(rng, 0.85, 1.15) });
        }
      }
    }
  }
  for (const cs of t.crossStreets) {
    const strip = new THREE.Mesh(
      ribbon(canal, side, t.xInner, t.xOuter, 0.35, 400, cs.dist - cs.width / 2, cs.dist + cs.width / 2),
      new THREE.MeshStandardMaterial({ color: cs.color, roughness: 0.8, side: THREE.DoubleSide }),
    );
    strip.receiveShadow = true;
    g.add(strip);
  }
  const wallMat = new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: 0.95 });
  const roofMat = new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: 0.8 });
  const bodies = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), wallMat, slots.length);
  const roofs = new THREE.InstancedMesh(gableGeometry(), roofMat, slots.length);
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const up = new THREE.Vector3(0, 1, 0);
  const wallColor = new THREE.Color(t.wall);
  const col = new THREE.Color();
  slots.forEach((s, i) => {
    q.setFromAxisAngle(up, s.yaw);
    const h = t.house.h * s.s;
    m.compose(new THREE.Vector3(s.x, h / 2, s.z), q, new THREE.Vector3(t.house.w, h, t.house.d));
    bodies.setMatrixAt(i, m);
    m.compose(new THREE.Vector3(s.x, h, s.z), q, new THREE.Vector3(t.house.w * 1.12, t.house.roof * s.s, t.house.d * 1.12));
    roofs.setMatrixAt(i, m);
    bodies.setColorAt(i, col.copy(wallColor).multiplyScalar(range(rng, 0.85, 1.05)));
    roofs.setColorAt(i, col.set(t.roofs[Math.floor(rng() * t.roofs.length)]).multiplyScalar(range(rng, 0.8, 1.15)));
  });
  for (const im of [bodies, roofs]) {
    im.castShadow = true;
    im.receiveShadow = true;
    im.instanceMatrix.needsUpdate = true;
    if (im.instanceColor) im.instanceColor.needsUpdate = true;
    im.frustumCulled = false;
    g.add(im);
  }
  return g;
}

function buildLandmark(l: LandmarkParams): THREE.Group {
  const g = new THREE.Group();
  const body = new THREE.MeshStandardMaterial({ color: l.body, roughness: 0.9 });
  const roof = new THREE.MeshStandardMaterial({ color: l.roof, roughness: 0.6 });
  const keep = new THREE.Mesh(new THREE.BoxGeometry(l.w, l.h, l.d), body);
  keep.position.y = l.h / 2;
  g.add(keep);
  const r = Math.min(l.w, l.d) * 0.11;
  for (let i = 0; i < l.towers; i++) {
    // towers on a ring: corners first, then interior
    const a = (i / l.towers) * Math.PI * 2 + Math.PI / 4;
    const ring = i < 4 ? 1 : 0.45;
    const x = Math.cos(a) * l.w * 0.5 * ring;
    const z = Math.sin(a) * l.d * 0.5 * ring;
    const th = l.h * (i < 4 ? 1.25 : 1.6);
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(r, r, th, 12), body);
    tower.position.set(x, th / 2, z);
    g.add(tower);
    const top = l.dome > 0
      ? new THREE.Mesh(new THREE.SphereGeometry(l.dome, 16, 12), roof)
      : new THREE.Mesh(new THREE.ConeGeometry(r * 1.2, l.h * 0.6, 8), roof);
    top.position.set(x, th + (l.dome > 0 ? l.dome * 0.6 : l.h * 0.3), z);
    g.add(top);
  }
  g.traverse((o) => {
    o.castShadow = true;
  });
  g.position.set(l.x, 0, -l.dist);
  return g;
}

function buildSmoke(s: AerialParams["smoke"][number], rng: Rng): THREE.Group {
  const g = new THREE.Group();
  const tex = softDiscTexture(128, 0.25);
  const n = 90;
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const sp = new THREE.Sprite(
      new THREE.SpriteMaterial({ map: tex, color: s.color, opacity: s.opacity * (1 - 0.8 * t * t), transparent: true, depthWrite: false }),
    );
    // column: narrow at the base, widest at ~60 % height, thinning into wisps at the top
    const rad = s.radius * (0.4 + 0.6 * Math.sin(Math.PI * Math.min(1, t * 0.85 + 0.1)));
    sp.position.set(s.x + s.lean * t * t * s.height + range(rng, -0.3, 0.3) * rad, t * s.height, -s.dist + range(rng, -0.3, 0.3) * rad);
    sp.scale.setScalar(rad * 2 * range(rng, 0.8, 1.2));
    g.add(sp);
  }
  return g;
}

export function buildAerialKingdoms(scene: THREE.Scene, p: AerialParams): void {
  const rng = makeRng(p.seed ?? 2024);
  // open plains: two half-planes meeting under the canal
  const farZ = 12000;
  for (const side of [-1, 1] as const) {
    const base = side < 0 ? p.plain.left : p.plain.right;
    const dark = side < 0 ? p.plain.leftDark : p.plain.rightDark;
    const tex = toTexture(noiseCanvas({ size: 512, seed: 30 + side, dark, light: base, baseCells: 8, contrast: 1.3, grain: 0.08 }), [24, 24]);
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(farZ, farZ * 2), new THREE.MeshStandardMaterial({ map: tex, roughness: 1 }));
    plane.rotation.x = -Math.PI / 2;
    plane.position.set((side * farZ) / 2 + p.canal.drift * 600, 0, -farZ + 400);
    plane.receiveShadow = true;
    scene.add(plane);
  }

  // scattered bushes on the left plain beyond the town
  const bushes = new THREE.InstancedMesh(
    new THREE.IcosahedronGeometry(1, 1),
    new THREE.MeshStandardMaterial({ color: p.plain.bushes, roughness: 1 }),
    p.plain.bushCount,
  );
  const m = new THREE.Matrix4();
  for (let i = 0; i < p.plain.bushCount; i++) {
    const dist = range(rng, p.left.zFar + 40, p.left.zFar + 2600);
    const off = range(rng, p.left.xInner, 2200);
    const s = range(rng, 4, 9);
    m.compose(new THREE.Vector3(canalCentre(p.canal, dist) - off, s * 0.4, -dist), new THREE.Quaternion(), new THREE.Vector3(s, s * 0.7, s));
    bushes.setMatrixAt(i, m);
  }
  bushes.castShadow = true;
  scene.add(bushes);

  // water + banks
  const c = p.canal;
  const waterCanvas = noiseCanvas({ size: 512, seed: 9, dark: c.waterDark, light: c.waterLight, baseCells: 8, octaves: 6, contrast: 1.6, grain: 0.1 });
  const wctx = waterCanvas.getContext("2d")!;
  const wr = makeRng(3);
  wctx.fillStyle = "#ffffff";
  for (let i = 0; i < 900 * c.foam; i++) {
    wctx.globalAlpha = range(wr, 0.15, 0.6);
    wctx.fillRect(wr() * 512, wr() * 512, range(wr, 2, 10), range(wr, 1, 3));
  }
  const water = new THREE.Mesh(
    ribbon(c, 0, 0, 0, 0.6, 160),
    new THREE.MeshStandardMaterial({ map: toTexture(waterCanvas, [2, 1]), roughness: 0.35, metalness: 0 }),
  );
  water.receiveShadow = true;
  scene.add(water);
  const bankMat = (hex: string) => new THREE.MeshStandardMaterial({ color: hex, roughness: 1, side: THREE.DoubleSide });
  scene.add(new THREE.Mesh(ribbon(c, -1, 0, c.bankWidth, 0.4, 100), bankMat(c.bankLeft)));
  scene.add(new THREE.Mesh(ribbon(c, 1, 0, c.bankWidth, 0.4, 100), bankMat(c.bankRight)));
  scene.add(new THREE.Mesh(ribbon(c, -1, c.bankWidth * 0.45, c.bankWidth * 0.75, 0.5, 100), bankMat(c.grassStrip)));
  // quay walls: thin light kerbs along both water edges
  for (const s of [-1, 1]) {
    scene.add(new THREE.Mesh(ribbon(c, s as -1 | 1, 0, 3, 1.2, 100), bankMat("#d8dcdc")));
  }

  scene.add(buildTown(p.left, -1, c, rng));
  scene.add(buildTown(p.right, 1, c, rng));
  for (const l of p.landmarks) scene.add(buildLandmark(l));

  const island = new THREE.Mesh(
    new THREE.CylinderGeometry(p.island.radius, p.island.radius * 1.15, 2.5, 14),
    new THREE.MeshStandardMaterial({ color: p.island.color, roughness: 1 }),
  );
  island.position.set(canalCentre(c, p.island.dist), 1.2, -p.island.dist);
  scene.add(island);

  for (const s of p.smoke) scene.add(buildSmoke(s, rng));
}
