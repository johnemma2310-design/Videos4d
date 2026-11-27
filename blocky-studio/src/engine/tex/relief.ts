// Surface relief. The reference's stone, brick and rock read as deep, lit geometry; flat colour textures do not.
// Everything here starts from a height field (0 = deepest joint, 1 = proudest stone face) and derives from it:
//   - a tangent-space normal map (so the sun and sky pick out every stone edge),
//   - cavity shading baked into the colour (joints stay dark even in flat light),
//   - a roughness map (joints rough, faces a little smoother).
// All generators are seeded and tile seamlessly.
import * as THREE from "three";
import { hash01, rng } from "../core/rng";

export type Field = { data: Float32Array; size: number };

const smooth = (a: number, b: number, x: number) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** tileable value noise, several octaves, 0..1 */
export const noiseField = (size: number, seed: number, cells: number, octaves = 4): Field => {
  const data = new Float32Array(size * size);
  let amp = 1, total = 0;
  for (let o = 0; o < octaves; o++) {
    const n = cells << o, g = new Float32Array(n * n), r = rng(seed + o * 101);
    for (let i = 0; i < g.length; i++) g[i] = r();
    for (let y = 0; y < size; y++) {
      const fy = (y / size) * n, y0 = Math.floor(fy), ty = fy - y0, sy = ty * ty * (3 - 2 * ty);
      for (let x = 0; x < size; x++) {
        const fx = (x / size) * n, x0 = Math.floor(fx), tx = fx - x0, sx = tx * tx * (3 - 2 * tx);
        const a = g[(y0 % n) * n + (x0 % n)], b = g[(y0 % n) * n + ((x0 + 1) % n)], c = g[((y0 + 1) % n) * n + (x0 % n)], d = g[((y0 + 1) % n) * n + ((x0 + 1) % n)];
        data[y * size + x] += amp * lerp(lerp(a, b, sx), lerp(c, d, sx), sy);
      }
    }
    total += amp; amp *= 0.5;
  }
  for (let i = 0; i < data.length; i++) data[i] /= total;
  return { data, size };
};

/**
 * Rubble / cobble cells: irregular stones separated by joints. Returns the height field and, per pixel, the id of the
 * stone it belongs to (for per-stone colour). `aspect` > 1 stretches stones horizontally (coursed masonry).
 */
export const stoneCells = (size: number, seed: number, cells: number, o: { aspect?: number; joint?: number; dome?: number; jitter?: number } = {}) => {
  const aspect = o.aspect ?? 1, joint = o.joint ?? 0.14, dome = o.dome ?? 0.35, jit = o.jitter ?? 0.85;
  const gx = Math.max(2, Math.round(cells / aspect)), gy = cells;
  const px = new Float32Array(gx * gy), py = new Float32Array(gx * gy), r = rng(seed);
  for (let i = 0; i < gx * gy; i++) { px[i] = 0.5 + (r() - 0.5) * jit; py[i] = 0.5 + (r() - 0.5) * jit; }
  const height = new Float32Array(size * size), id = new Int32Array(size * size);
  for (let y = 0; y < size; y++) {
    const fy = (y / size) * gy, cy = Math.floor(fy);
    for (let x = 0; x < size; x++) {
      const fx = (x / size) * gx, cx = Math.floor(fx);
      let d1 = 9, d2 = 9, best = 0;
      for (let j = -1; j <= 1; j++)
        for (let i = -1; i <= 1; i++) {
          const ix = (cx + i + gx) % gx, iy = (cy + j + gy) % gy, k = iy * gx + ix;
          // distance measured in a space where stones are `aspect` times wider than tall
          const dx = (cx + i + px[k] - fx) * aspect, dy = cy + j + py[k] - fy, d = Math.sqrt(dx * dx + dy * dy);
          if (d < d1) { d2 = d1; d1 = d; best = k; } else if (d < d2) d2 = d;
        }
      const edge = d2 - d1; // 0 on a joint, grows toward the stone centre
      height[y * size + x] = smooth(0, joint, edge) * (1 - dome + dome * smooth(0, 0.6, edge));
      id[y * size + x] = best;
    }
  }
  return { height: { data: height, size } as Field, id, count: gx * gy };
};

/** luminance of a canvas as a height field (dark = low) */
export const fieldFromCanvas = (c: HTMLCanvasElement): Field => {
  const s = c.width, d = c.getContext("2d")!.getImageData(0, 0, s, s).data, data = new Float32Array(s * s);
  for (let i = 0; i < s * s; i++) data[i] = (d[i * 4] * 0.299 + d[i * 4 + 1] * 0.587 + d[i * 4 + 2] * 0.114) / 255;
  return { data, size: s };
};

/** tangent-space normal map from a height field (wraps at the edges). `strength` = how steep the relief reads. */
export const normalCanvas = (f: Field, strength: number) => {
  const s = f.size, c = document.createElement("canvas");
  c.width = c.height = s;
  const g = c.getContext("2d")!, img = g.createImageData(s, s), h = f.data;
  for (let y = 0; y < s; y++) {
    const ym = ((y - 1 + s) % s) * s, yp = ((y + 1) % s) * s, y0 = y * s;
    for (let x = 0; x < s; x++) {
      const xm = (x - 1 + s) % s, xp = (x + 1) % s;
      // Sobel
      const dx = (h[ym + xp] + 2 * h[y0 + xp] + h[yp + xp] - h[ym + xm] - 2 * h[y0 + xm] - h[yp + xm]) * strength;
      const dy = (h[yp + xm] + 2 * h[yp + x] + h[yp + xp] - h[ym + xm] - 2 * h[ym + x] - h[ym + xp]) * strength;
      const inv = 1 / Math.sqrt(dx * dx + dy * dy + 1), i = (y0 + x) * 4;
      img.data[i] = (-dx * inv * 0.5 + 0.5) * 255;
      img.data[i + 1] = (dy * inv * 0.5 + 0.5) * 255; // canvas rows run downward, texture v runs upward
      img.data[i + 2] = (inv * 0.5 + 0.5) * 255;
      img.data[i + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  return c;
};

const tex = (c: HTMLCanvasElement, repeat: [number, number], srgb: boolean) => {
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(...repeat);
  t.anisotropy = 8;
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  return t;
};

export type ReliefOpts = { repeat: [number, number]; strength?: number; cavity?: number; roughness?: number; jointRoughness?: number };

/** build a lit material from a colour canvas and its height field */
export const reliefMaterial = (albedo: HTMLCanvasElement, height: Field, o: ReliefOpts) => {
  const s = height.size, cavity = o.cavity ?? 0.45;
  // bake cavity darkening into the colour, and write roughness (green channel, as three expects)
  const g = albedo.getContext("2d")!, img = g.getImageData(0, 0, s, s);
  const rc = document.createElement("canvas");
  rc.width = rc.height = s;
  const rg = rc.getContext("2d")!, rimg = rg.createImageData(s, s), face = o.roughness ?? 0.8, jr = o.jointRoughness ?? 1;
  for (let i = 0; i < s * s; i++) {
    const h = height.data[i], k = 1 - cavity * (1 - smooth(0, 0.55, h));
    img.data[i * 4] *= k; img.data[i * 4 + 1] *= k; img.data[i * 4 + 2] *= k;
    const ro = lerp(jr, face, smooth(0.1, 0.6, h)) * 255;
    rimg.data[i * 4] = 255; rimg.data[i * 4 + 1] = ro; rimg.data[i * 4 + 2] = 0; rimg.data[i * 4 + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  rg.putImageData(rimg, 0, 0);
  return new THREE.MeshStandardMaterial({
    map: tex(albedo, o.repeat, true), normalMap: tex(normalCanvas(height, o.strength ?? 3), o.repeat, false),
    roughnessMap: tex(rc, o.repeat, false), roughness: 1, metalness: 0,
  });
};

export type Courses = {
  /** number of horizontal courses in one tile */
  rows: number;
  /** stone length as a multiple of its course height: [min, max]. [1, 3] = coursed rubble, [4, 12] = thin rock strata */
  width: [number, number];
  /** how much course heights vary (0 = all equal, 0.5 = from half to one-and-a-half) */
  rowVar?: number;
  /** joint width and corner rounding, as fractions of the course height */
  joint?: number; round?: number;
  /** how far stone outlines wander from straight lines, as a fraction of the course height */
  wobble?: number;
};

/**
 * Stones laid in horizontal courses: each course has its own height, each stone its own length, outlines wander a
 * little. This is how the reference's walls are built (and, with long thin stones, how its rock faces are layered).
 */
export const coursedStones = (size: number, seed: number, c: Courses) => {
  const r = rng(seed), rowVar = c.rowVar ?? 0.35, joint = c.joint ?? 0.16, round = c.round ?? 0.3, wob = c.wobble ?? 0.18;
  // course heights that sum exactly to the tile, so it wraps vertically
  const hs = Array.from({ length: c.rows }, () => 1 + (r() - 0.5) * 2 * rowVar), sum = hs.reduce((a, b) => a + b, 0);
  const height = new Float32Array(size * size), id = new Int32Array(size * size);
  const warpX = noiseField(size, seed + 21, 10, 3), warpY = noiseField(size, seed + 22, 10, 3);
  let y0 = 0, stone = 0;
  const rowsPx: { y0: number; y1: number; xs: number[]; first: number }[] = [];
  for (let k = 0; k < c.rows; k++) {
    const y1 = k === c.rows - 1 ? size : y0 + (hs[k] / sum) * size, rh = y1 - y0;
    // stone boundaries along the course; the last stone ends exactly at the tile edge so it wraps horizontally
    const xs = [r() * rh * c.width[0]];
    while (xs[xs.length - 1] < size + xs[0] - rh * c.width[0] * 0.6) xs.push(xs[xs.length - 1] + rh * (c.width[0] + r() * (c.width[1] - c.width[0])));
    xs[xs.length - 1] = size + xs[0];
    rowsPx.push({ y0, y1, xs, first: stone });
    stone += xs.length - 1;
    y0 = y1;
  }
  let row = 0;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      // look the pixel up at a slightly warped position, so edges are not ruler-straight
      const i = y * size + x, rh0 = size / c.rows;
      const wx = x + (warpX.data[i] - 0.5) * 2 * wob * rh0, wy = (((y + (warpY.data[i] - 0.5) * 2 * wob * rh0) % size) + size) % size;
      while (row < rowsPx.length - 1 && wy >= rowsPx[row].y1) row++;
      while (row > 0 && wy < rowsPx[row].y0) row--;
      const R = rowsPx[row], rh = R.y1 - R.y0;
      let px = wx;
      while (px < R.xs[0]) px += size;
      while (px >= R.xs[R.xs.length - 1]) px -= size;
      let s = 0;
      while (px >= R.xs[s + 1]) s++;
      const dx = Math.min(px - R.xs[s], R.xs[s + 1] - px), dy = Math.min(wy - R.y0, R.y1 - wy), rad = round * rh;
      let e = Math.min(dx, dy);
      if (dx < rad && dy < rad) e = rad - Math.hypot(rad - dx, rad - dy); // rounded corners
      const j = joint * rh * 0.5;
      height[i] = smooth(0, 1, (e - j) / (rh * 0.22)) * (0.8 + 0.2 * smooth(0, 1, e / (rh * 0.5)));
      id[i] = R.first + s;
    }
  }
  return { height: { data: height, size } as Field, id, count: stone };
};

export type RubbleOpts = ReliefOpts & {
  seed: number; size?: number; cells?: number; aspect?: number; joint?: number; light: string; dark: string; mortar: string; grain?: number; variation?: number;
  /** lay the stones in courses instead of as irregular cells */
  courses?: Courses;
};

/** rubble masonry / rock face / setts: stones each with their own shade, grainy faces, dark recessed joints */
export const rubbleMaterial = (o: RubbleOpts) => {
  const S = o.size ?? 1024;
  const { height, id } = o.courses ? coursedStones(S, o.seed, o.courses) : stoneCells(S, o.seed, o.cells ?? 12, { aspect: o.aspect, joint: o.joint });
  const grain = noiseField(S, o.seed + 7, 48, 3), big = noiseField(S, o.seed + 13, 6, 3);
  const a = new THREE.Color(o.dark), b = new THREE.Color(o.light), m = new THREE.Color(o.mortar);
  const c = document.createElement("canvas");
  c.width = c.height = S;
  const g = c.getContext("2d")!, img = g.createImageData(S, S), gr = o.grain ?? 0.25, vr = o.variation ?? 1;
  for (let i = 0; i < S * S; i++) {
    const h = height.data[i];
    // stone faces are not flat: add grain and a slow swell to the height as well
    height.data[i] = Math.min(1, h * (0.78 + 0.22 * big.data[i]) + (grain.data[i] - 0.5) * 0.16 * h);
    const t = Math.min(1, Math.max(0, 0.5 + (hash01(id[i], o.seed) - 0.5) * vr + (grain.data[i] - 0.5) * gr * 2 + (big.data[i] - 0.5) * 0.3));
    const face = smooth(0.05, 0.3, h);
    img.data[i * 4] = lerp(m.r, lerp(a.r, b.r, t), face) * 255;
    img.data[i * 4 + 1] = lerp(m.g, lerp(a.g, b.g, t), face) * 255;
    img.data[i * 4 + 2] = lerp(m.b, lerp(a.b, b.b, t), face) * 255;
    img.data[i * 4 + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  return { material: reliefMaterial(c, height, o), albedo: c, height };
};

/** loose ground (gravel, soil, concrete): relief from layered noise only */
export const groundRelief = (albedo: HTMLCanvasElement, seed: number, o: ReliefOpts & { cells?: number }) => {
  const S = albedo.width, n = noiseField(S, seed, o.cells ?? 40, 4), l = fieldFromCanvas(albedo);
  for (let i = 0; i < S * S; i++) n.data[i] = n.data[i] * 0.6 + l.data[i] * 0.4;
  return reliefMaterial(albedo, n, { cavity: 0.25, ...o });
};
