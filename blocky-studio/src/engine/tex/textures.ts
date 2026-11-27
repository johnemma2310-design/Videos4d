import * as THREE from "three";
import { makeRng, range, type Rng } from "./pocRng";

/** All textures are generated in code on a 2D canvas (no image files). */

export function makeCanvas(w: number, h = w): { canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D } {
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  return { canvas, ctx: canvas.getContext("2d")! };
}

export function toTexture(canvas: HTMLCanvasElement, repeat: [number, number] = [1, 1]): THREE.CanvasTexture {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(...repeat);
  t.anisotropy = 8;
  t.generateMipmaps = true;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  return t;
}

/** Tileable value-noise fBm in 0..1, row-major Float32Array of size*size. */
export function fbmField(size: number, seed: number, baseCells = 4, octaves = 5, gain = 0.5): Float32Array {
  const out = new Float32Array(size * size);
  let amp = 1;
  let total = 0;
  for (let o = 0; o < octaves; o++) {
    const cells = baseCells << o;
    const rng = makeRng(seed * 131 + o * 17 + 1);
    const lat = new Float32Array(cells * cells);
    for (let i = 0; i < lat.length; i++) lat[i] = rng();
    const s = cells / size;
    for (let y = 0; y < size; y++) {
      const fy = y * s;
      const y0 = Math.floor(fy);
      const ty = fy - y0;
      const sy = ty * ty * (3 - 2 * ty);
      const ya = (y0 % cells) * cells;
      const yb = ((y0 + 1) % cells) * cells;
      for (let x = 0; x < size; x++) {
        const fx = x * s;
        const x0 = Math.floor(fx);
        const tx = fx - x0;
        const sx = tx * tx * (3 - 2 * tx);
        const xa = x0 % cells;
        const xb = (x0 + 1) % cells;
        const top = lat[ya + xa] + (lat[ya + xb] - lat[ya + xa]) * sx;
        const bot = lat[yb + xa] + (lat[yb + xb] - lat[yb + xa]) * sx;
        out[y * size + x] += (top + (bot - top) * sy) * amp;
      }
    }
    total += amp;
    amp *= gain;
  }
  for (let i = 0; i < out.length; i++) out[i] /= total;
  return out;
}

export interface NoiseTexOpts {
  size?: number;
  seed?: number;
  /** dark and light ends of the ramp (sRGB hex) */
  dark: string;
  light: string;
  baseCells?: number;
  octaves?: number;
  /** >1 pushes values towards the two ends */
  contrast?: number;
  /** 0..1 per-pixel white-noise grain */
  grain?: number;
}

/** Two-colour fBm canvas: base for stone, gravel, plaster, roofs, water. Returns the canvas for further drawing. */
export function noiseCanvas(o: NoiseTexOpts): HTMLCanvasElement {
  const size = o.size ?? 512;
  const { canvas, ctx } = makeCanvas(size);
  const f = fbmField(size, o.seed ?? 1, o.baseCells ?? 4, o.octaves ?? 5);
  const a = new THREE.Color(o.dark);
  const b = new THREE.Color(o.light);
  // interpolate in display (sRGB) space so the hex values are what you see
  const ar = a.getHex(THREE.SRGBColorSpace);
  const br = b.getHex(THREE.SRGBColorSpace);
  const A = [(ar >> 16) & 255, (ar >> 8) & 255, ar & 255];
  const B = [(br >> 16) & 255, (br >> 8) & 255, br & 255];
  const img = ctx.createImageData(size, size);
  const rng = makeRng((o.seed ?? 1) + 999);
  const contrast = o.contrast ?? 1;
  const grain = o.grain ?? 0;
  for (let i = 0; i < f.length; i++) {
    let v = (f[i] - 0.5) * contrast * 2 + 0.5 + (rng() - 0.5) * grain;
    v = Math.min(1, Math.max(0, v));
    img.data[i * 4] = A[0] + (B[0] - A[0]) * v;
    img.data[i * 4 + 1] = A[1] + (B[1] - A[1]) * v;
    img.data[i * 4 + 2] = A[2] + (B[2] - A[2]) * v;
    img.data[i * 4 + 3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  return canvas;
}

/** Scatter short strokes (straw, cracks, scratches) over an existing canvas. */
export function scatterStrokes(
  canvas: HTMLCanvasElement,
  rng: Rng,
  count: number,
  color: string,
  length: [number, number],
  width: [number, number],
  alpha: [number, number] = [0.5, 1],
): void {
  const ctx = canvas.getContext("2d")!;
  ctx.strokeStyle = color;
  ctx.lineCap = "round";
  for (let i = 0; i < count; i++) {
    const x = rng() * canvas.width;
    const y = rng() * canvas.height;
    const ang = rng() * Math.PI * 2;
    const len = range(rng, length[0], length[1]);
    ctx.globalAlpha = range(rng, alpha[0], alpha[1]);
    ctx.lineWidth = range(rng, width[0], width[1]);
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.quadraticCurveTo(
      x + Math.cos(ang) * len * 0.5 + range(rng, -4, 4),
      y + Math.sin(ang) * len * 0.5 + range(rng, -4, 4),
      x + Math.cos(ang) * len,
      y + Math.sin(ang) * len,
    );
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
}

/** Soft round sprite (white, radial alpha falloff) for smoke, glow and flame billboards. */
export function softDiscTexture(size = 128, hardness = 0.0): THREE.CanvasTexture {
  const { canvas, ctx } = makeCanvas(size);
  const g = ctx.createRadialGradient(size / 2, size / 2, size * 0.5 * hardness, size / 2, size / 2, size / 2);
  g.addColorStop(0, "rgba(255,255,255,1)");
  g.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
