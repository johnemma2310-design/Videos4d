// SET H — tablet plaza on the fire bank: gravel ground with straw, dark border wall, the water town beyond the canal,
// the rule sign and a brazier on the wall. Ported from the calibration test (reconstruction/poc, target f00490).
// Parameters are data (params/*.json) so the comparison loop can tune them without code changes.
import * as THREE from "three";
import { makeRng, range } from "../tex/pocRng";
import { makeCanvas, noiseCanvas, scatterStrokes, softDiscTexture, toTexture } from "../tex/textures";
import { groundRelief, rubbleMaterial } from "../tex/relief";

// World: the subject stands at the origin facing +Z, the camera looks along -Z, ground is y = 0.
export interface BuildingParams {
  x: number;
  z: number;
  w: number;
  d: number;
  /** wall height and roof height (studs) */
  h: number;
  roof: number;
  yaw?: number;
}

export interface DomeParams {
  x: number;
  z: number;
  /** tower radius / height, dome radius */
  r: number;
  h: number;
  dome: number;
}

export interface TabletPlazaParams {
  ground: { dark: string; light: string; straw: string; strawCount: number; repeat: number; roughness: number };
  wall: { z: number; height: number; depth: number; dark: string; light: string; cap: string; repeat: number };
  town: { wall: string; wallDark: string; roof: string; window: string; dome: string; buildings: BuildingParams[]; domes: DomeParams[] };
  sign: { x: number; y: number; z: number; w: number; h: number; panel: string; trim: string; glyph: string; yaw: number };
  brazier: { x: number; z: number; radius: number; metal: string; flame: string; flameIntensity: number; flameSize: number };
  /** soft ground-level mist sprites in front of the far wall: [x, y, z, size, opacity] */
  mist: { color: string; puffs: [number, number, number, number, number][] };
  /** small props lying on the ground: [x, z, width, height, depth, yawDeg, colour] */
  debris: [number, number, number, number, number, number, string][];
  /** false = the old flat textures (kept for comparison) */
  relief?: boolean;
  reliefStrength?: { wall?: number; ground?: number };
}
type CharacterSceneParams = TabletPlazaParams;

function groundCanvas(p: CharacterSceneParams["ground"]): HTMLCanvasElement {
  const c = noiseCanvas({ size: 1024, seed: 11, dark: p.dark, light: p.light, baseCells: 32, octaves: 5, contrast: 1.5, grain: 0.35 });
  const rng = makeRng(42);
  // pebbles: small darker / lighter blobs
  const ctx = c.getContext("2d")!;
  for (let i = 0; i < 2600; i++) {
    ctx.globalAlpha = range(rng, 0.15, 0.5);
    ctx.fillStyle = rng() < 0.5 ? p.dark : p.light;
    ctx.beginPath();
    ctx.ellipse(rng() * 1024, rng() * 1024, range(rng, 1.5, 5), range(rng, 1.5, 4), rng() * 3, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
  scatterStrokes(c, rng, p.strawCount, p.straw, [30, 110], [1, 2.4], [0.35, 0.9]);
  return c;
}

function wallTexture(p: CharacterSceneParams["wall"]): THREE.Texture {
  const c = noiseCanvas({ size: 1024, seed: 5, dark: p.dark, light: p.light, baseCells: 6, octaves: 6, contrast: 1.6, grain: 0.15 });
  const ctx = c.getContext("2d")!;
  const rng = makeRng(77);
  // rough horizontal strata: long, slightly wavy dark cracks and lighter ledges
  for (let i = 0; i < 70; i++) {
    const y = rng() * 1024;
    ctx.globalAlpha = range(rng, 0.2, 0.6);
    ctx.strokeStyle = rng() < 0.6 ? "#0d0c12" : p.light;
    ctx.lineWidth = range(rng, 1, 5);
    ctx.beginPath();
    let x = rng() * 1024;
    ctx.moveTo(x, y);
    const len = range(rng, 80, 420);
    for (let s = 0; s < len; s += 20) ctx.lineTo((x += 20), y + range(rng, -5, 5));
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
  return toTexture(c, [p.repeat, Math.max(1, Math.round((p.repeat * p.height) / 600))]);
}

/** Plaster wall with a regular grid of dark windows. One texture tile = one window bay. */
function facadeTexture(wall: string, wallDark: string, windowColor: string): THREE.Texture {
  const c = noiseCanvas({ size: 256, seed: 3, dark: wallDark, light: wall, baseCells: 8, octaves: 4, contrast: 1.2, grain: 0.1 });
  const ctx = c.getContext("2d")!;
  ctx.fillStyle = windowColor;
  ctx.fillRect(96, 70, 64, 110);
  ctx.fillStyle = wall;
  ctx.fillRect(126, 70, 4, 110);
  return toTexture(c);
}

function buildTown(p: CharacterSceneParams["town"]): THREE.Group {
  const g = new THREE.Group();
  const facade = facadeTexture(p.wall, p.wallDark, p.window);
  const roofMat = new THREE.MeshStandardMaterial({ color: p.roof, roughness: 0.9 });
  const domeMat = new THREE.MeshStandardMaterial({ color: p.dome, roughness: 0.6 });
  const towerMat = new THREE.MeshStandardMaterial({ color: p.wall, roughness: 0.95 });
  for (const b of p.buildings) {
    const grp = new THREE.Group();
    const bay = 5; // studs per window bay
    const mk = (len: number) => {
      const t = facade.clone();
      t.repeat.set(Math.max(1, Math.round(len / bay)), Math.max(1, Math.round(b.h / 6)));
      t.needsUpdate = true;
      return new THREE.MeshStandardMaterial({ map: t, roughness: 0.95 });
    };
    const mx = mk(b.d);
    const mz = mk(b.w);
    const body = new THREE.Mesh(new THREE.BoxGeometry(b.w, b.h, b.d), [mx, mx, roofMat, roofMat, mz, mz]);
    body.position.y = b.h / 2;
    // hip roof: 4-sided pyramid stretched to the footprint (slight overhang)
    const roof = new THREE.Mesh(new THREE.ConeGeometry(Math.SQRT1_2, 1, 4, 1), roofMat);
    roof.rotation.y = Math.PI / 4;
    const holder = new THREE.Group();
    holder.add(roof);
    holder.scale.set(b.w * 1.06, b.roof, b.d * 1.06);
    holder.position.y = b.h + b.roof / 2;
    grp.add(body, holder);
    grp.position.set(b.x, 0, b.z);
    grp.rotation.y = THREE.MathUtils.degToRad(b.yaw ?? 0);
    g.add(grp);
  }
  for (const d of p.domes) {
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(d.r, d.r, d.h, 20), towerMat);
    tower.position.set(d.x, d.h / 2, d.z);
    const dome = new THREE.Mesh(new THREE.SphereGeometry(d.dome, 24, 16), domeMat);
    dome.scale.y = 1.15;
    dome.position.set(d.x, d.h + d.dome * 0.75, d.z);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(d.dome * 0.45, d.dome * 1.3, 16), domeMat);
    tip.position.set(d.x, d.h + d.dome * 2.2, d.z);
    g.add(tower, dome, tip);
  }
  return g;
}

function buildSign(p: CharacterSceneParams["sign"]): THREE.Mesh {
  const { canvas, ctx } = makeCanvas(256, 512);
  ctx.fillStyle = p.trim;
  ctx.fillRect(0, 0, 256, 512);
  ctx.fillStyle = p.panel;
  ctx.fillRect(14, 14, 228, 484);
  ctx.strokeStyle = p.glyph;
  ctx.lineWidth = 3;
  ctx.strokeRect(26, 26, 204, 460);
  // abstract gold lettering (unreadable at this crop; only its presence matters)
  ctx.fillStyle = p.glyph;
  ctx.font = "bold 150px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText("A", 128, 190);
  ctx.fillText("S", 128, 400);
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(p.w, p.h, 0.3),
    new THREE.MeshStandardMaterial({ map: toTexture(canvas), roughness: 0.6, metalness: 0.1 }),
  );
  m.position.set(p.x, p.y, p.z);
  m.rotation.y = THREE.MathUtils.degToRad(p.yaw);
  return m;
}

function buildBrazier(p: CharacterSceneParams["brazier"], wallTop: number): THREE.Group {
  const g = new THREE.Group();
  const metal = new THREE.MeshStandardMaterial({ color: p.metal, roughness: 0.5, metalness: 0.6 });
  const bowl = new THREE.Mesh(new THREE.SphereGeometry(p.radius, 24, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), metal);
  bowl.scale.y = 0.75;
  bowl.position.y = p.radius * 0.95;
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(p.radius * 0.15, p.radius * 0.3, p.radius * 0.4, 12), metal);
  stem.position.y = p.radius * 0.2;
  g.add(bowl, stem);
  // flame: HDR additive billboards so the bloom pass picks it up
  const tex = softDiscTexture(128, 0.1);
  const flameColor = new THREE.Color(p.flame).multiplyScalar(p.flameIntensity);
  for (const [dx, dy, s] of [[0, 0.45, 1.0], [-0.2, 0.25, 0.7], [0.22, 0.3, 0.65], [0.02, 0.85, 0.6]]) {
    const sp = new THREE.Sprite(
      new THREE.SpriteMaterial({ map: tex, color: flameColor, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }),
    );
    sp.scale.setScalar(p.radius * p.flameSize * s);
    sp.position.set(dx * p.radius * p.flameSize, p.radius * (0.95 + dy * p.flameSize), 0);
    g.add(sp);
  }
  g.position.set(p.x, wallTop, p.z);
  return g;
}


export function buildTabletPlaza(scene: THREE.Scene, p: TabletPlazaParams): void {
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(600, 600),
    p.relief === false ? new THREE.MeshStandardMaterial({ map: toTexture(groundCanvas(p.ground), [p.ground.repeat, p.ground.repeat]), roughness: p.ground.roughness })
      : groundRelief(groundCanvas(p.ground), 31, { repeat: [p.ground.repeat, p.ground.repeat], strength: p.reliefStrength?.ground ?? 2.2, roughness: p.ground.roughness, cells: 64 }),
  );
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);

  const wallTex = wallTexture(p.wall);
  // rock face in rough horizontal courses: wide, flat stones with deep dark joints
  const wallMat = p.relief === false ? new THREE.MeshStandardMaterial({ map: wallTex, roughness: 0.95 })
    : rubbleMaterial({ seed: 5, light: p.wall.light, dark: p.wall.dark, mortar: "#08070c", repeat: [600 / 12, p.wall.height / 12], strength: p.reliefStrength?.wall ?? 6, variation: 1.6, grain: 0.5,
        courses: { rows: 30, width: [4, 12], rowVar: 0.6, joint: 0.14, round: 0.15, wobble: 0.35 } }).material; // thin strata: about 0.4 studs tall, 2 to 5 long
  const capMat = new THREE.MeshStandardMaterial({ color: p.wall.cap, roughness: 0.9 });
  const wall = new THREE.Mesh(new THREE.BoxGeometry(600, p.wall.height, p.wall.depth), [wallMat, wallMat, capMat, capMat, wallMat, wallMat]);
  wall.position.set(0, p.wall.height / 2, p.wall.z - p.wall.depth / 2);
  wall.receiveShadow = true;
  scene.add(wall);

  scene.add(buildTown(p.town));
  scene.add(buildSign(p.sign));
  scene.add(buildBrazier(p.brazier, p.wall.height));

  const mistTex = softDiscTexture(128, 0);
  for (const [x, y, z, size, opacity] of p.mist.puffs) {
    const sp = new THREE.Sprite(
      new THREE.SpriteMaterial({ map: mistTex, color: p.mist.color, opacity, transparent: true, depthWrite: false, fog: false }),
    );
    sp.position.set(x, y, z);
    sp.scale.setScalar(size);
    scene.add(sp);
  }

  for (const [x, z, w, h, d, yaw, color] of p.debris) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshStandardMaterial({ color, roughness: 1 }));
    m.position.set(x, h / 2, z);
    m.rotation.y = THREE.MathUtils.degToRad(yaw);
    m.castShadow = true;
    scene.add(m);
  }
}
