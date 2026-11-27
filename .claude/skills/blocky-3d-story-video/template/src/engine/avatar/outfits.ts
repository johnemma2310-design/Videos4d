// Clothing is flat print on the boxes: canvas textures for the torso front, torso sides/back, sleeves and legs.
import * as THREE from "three";
import { drawFace, EXPRESSIONS, faceKey, type FaceOpts } from "./faces";

export type TorsoPrint =
  | { kind: "plain"; color: string }
  | { kind: "varsity"; color: string; strip: string; trim?: string } // open jacket over a tee: strip = tee colour
  | { kind: "stripes"; color: string; color2: string; bands?: number }
  | { kind: "plaid"; color: string; color2: string }
  | { kind: "coat"; color: string; trim: string }; // buttoned, belted coat with a collar and pockets: trim = buttons, belt, seams

export type Outfit = {
  torso: TorsoPrint;
  sleeves?: { color: string; length?: number; cuff?: string }; // length 0..1 of the arm covered (default 1); cuff = varsity-style striped cuff colour
  legs: { color: string; length?: number; shoes?: string }; // length < 1 = shorts (rest is skin)
};

const cache = new Map<string, THREE.Texture>();
const tex = (key: string, w: number, h: number, draw: (g: CanvasRenderingContext2D) => void) => {
  let t = cache.get(key);
  if (!t) {
    const c = document.createElement("canvas");
    c.width = w; c.height = h;
    draw(c.getContext("2d")!);
    t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    cache.set(key, t);
  }
  return t;
};

const hem = (g: CanvasRenderingContext2D, S: number, trim: string, u0 = 0, u1 = 1) => {
  g.fillStyle = trim;
  g.fillRect(u0 * S, 0.935 * S, (u1 - u0) * S, 0.012 * S);
  g.fillRect(u0 * S, 0.968 * S, (u1 - u0) * S, 0.012 * S);
};

const body = (g: CanvasRenderingContext2D, S: number, p: TorsoPrint) => {
  g.fillStyle = p.color; g.fillRect(0, 0, S, S);
  if (p.kind === "stripes") {
    const n = p.bands ?? 7; g.fillStyle = p.color2;
    for (let i = 0; i < n; i++) g.fillRect(0, ((i * 2 + 1) / (n * 2)) * S, S, S / (n * 2));
  }
  if (p.kind === "plaid") {
    g.fillStyle = p.color2; g.globalAlpha = 0.55;
    for (let i = 0; i < 4; i++) { g.fillRect(((i * 2 + 1) / 8) * S, 0, S / 8, S); g.fillRect(0, ((i * 2 + 1) / 8) * S, S, S / 8); }
    g.globalAlpha = 1;
  }
};

/** torso front (2x2 studs). Varsity layout measured on the reference hero (report B 1.6). */
export const torsoFront = (p: TorsoPrint) =>
  tex("tf" + JSON.stringify(p), 512, 512, (g) => {
    const S = 512;
    body(g, S, p);
    if (p.kind === "varsity") {
      const trim = p.trim ?? "#f2efec";
      g.fillStyle = p.strip; g.fillRect(0.38 * S, 0, 0.205 * S, S);
      g.fillStyle = trim;
      for (const v of [0.09, 0.27, 0.45, 0.62, 0.79, 0.96]) { g.beginPath(); g.arc(0.36 * S, v * S, 0.015 * S, 0, Math.PI * 2); g.fill(); }
      for (const [u, lean] of [[0.17, 1], [0.87, -1]] as const) {
        g.save(); g.translate(u * S, 0.72 * S); g.rotate((lean * 6 * Math.PI) / 180); g.fillRect(-0.01 * S, -0.15 * S, 0.02 * S, 0.3 * S); g.restore();
      }
      hem(g, S, trim, 0, 0.33); hem(g, S, trim, 0.64, 1);
    }
    if (p.kind === "coat") {
      const dark = "rgba(0,0,0,0.28)", light = "rgba(255,255,255,0.16)";
      g.fillStyle = light; g.beginPath(); g.moveTo(0.5 * S, 0.3 * S); g.lineTo(0.2 * S, 0); g.lineTo(0.5 * S, 0); g.closePath(); g.fill();        // collar, two lapels
      g.beginPath(); g.moveTo(0.5 * S, 0.3 * S); g.lineTo(0.8 * S, 0); g.lineTo(0.5 * S, 0); g.closePath(); g.fill();
      g.strokeStyle = dark; g.lineWidth = 0.014 * S; g.beginPath(); g.moveTo(0.2 * S, 0); g.lineTo(0.5 * S, 0.3 * S); g.lineTo(0.8 * S, 0); g.stroke();
      g.beginPath(); g.moveTo(0.5 * S, 0.3 * S); g.lineTo(0.5 * S, S); g.stroke();                                                                   // front seam
      g.fillStyle = p.trim; for (const v of [0.4, 0.52, 0.76, 0.88]) { g.beginPath(); g.arc(0.56 * S, v * S, 0.024 * S, 0, Math.PI * 2); g.fill(); } // buttons
      g.fillStyle = dark; g.fillRect(0, 0.6 * S, S, 0.085 * S);                                                                                       // belt
      g.fillStyle = p.trim; g.fillRect(0.44 * S, 0.59 * S, 0.12 * S, 0.105 * S); g.fillStyle = p.color; g.fillRect(0.465 * S, 0.615 * S, 0.07 * S, 0.055 * S);
      g.strokeStyle = dark; for (const u of [0.1, 0.68]) g.strokeRect(u * S, 0.76 * S, 0.22 * S, 0.16 * S);                                           // pockets
      g.fillStyle = light; for (const u of [0.1, 0.68]) g.fillRect(u * S, 0.76 * S, 0.22 * S, 0.045 * S);
    }
  });

export const torsoSide = (p: TorsoPrint) =>
  tex("ts" + JSON.stringify(p), 256, 256, (g) => {
    body(g, 256, p);
    if (p.kind === "varsity") hem(g, 256, p.trim ?? "#f2efec");
    if (p.kind === "coat") { g.fillStyle = "rgba(0,0,0,0.28)"; g.fillRect(0, 0.6 * 256, 256, 0.085 * 256); }
  });

/** one arm side face (1x2 studs, v = 0 at the shoulder) */
export const armSide = (o: Outfit, skin: string) => {
  const s = o.sleeves ?? { color: o.torso.color };
  return tex("as" + JSON.stringify(s) + skin, 128, 256, (g) => {
    const len = s.length ?? 1;
    g.fillStyle = skin; g.fillRect(0, 0, 128, 256);
    g.fillStyle = s.color; g.fillRect(0, 0, 128, 256 * len);
    if (s.cuff) {
      g.fillStyle = s.cuff; g.fillRect(0, 256 * 0.87, 128, 256 * 0.13);
      g.fillStyle = s.color; g.fillRect(0, 256 * 0.905, 128, 4); g.fillRect(0, 256 * 0.95, 128, 4);
    }
  });
};

/** one leg side face (1x2 studs, v = 0 at the hip) */
export const legSide = (o: Outfit, skin: string) =>
  tex("ls" + JSON.stringify(o.legs) + skin, 128, 256, (g) => {
    const len = o.legs.length ?? 1;
    g.fillStyle = skin; g.fillRect(0, 0, 128, 256);
    g.fillStyle = o.legs.color; g.fillRect(0, 0, 128, 256 * len);
    g.fillStyle = o.legs.shoes ?? "#0c0a0e"; g.fillRect(0, 256 * 0.9, 128, 256 * 0.1);
  });

/**
 * Head texture: wraps the full 360 degrees (u = 0.5 is the front), skin colour with the face decal projected onto the
 * front half so that it looks like the flat drawing when seen from the front (x_projected = sin(angle)).
 */
export const headTexture = (skin: string, expression: string, opts?: FaceOpts) =>
  tex("hd" + skin + faceKey(expression, opts), 1024, 512, (g) => {
    const spec = EXPRESSIONS[expression];
    if (!spec) throw new Error(`unknown expression "${expression}". Known: ${Object.keys(EXPRESSIONS).join(", ")}`);
    g.fillStyle = skin; g.fillRect(0, 0, 1024, 512);
    // depth painted into the skin: darker toward the sides and back, a shadow under the hairline and under the chin
    for (let x = 0; x < 1024; x += 4) { const ang = Math.abs((x / 1024 - 0.5) * Math.PI * 2), k = Math.min(1, Math.max(0, (ang - 0.75) / 1.3)); g.fillStyle = `rgba(70,30,22,${(0.3 * k * k).toFixed(3)})`; g.fillRect(x, 0, 4, 512); }
    const top = g.createLinearGradient(0, 0, 0, 150); top.addColorStop(0, "rgba(60,25,18,0.34)"); top.addColorStop(1, "rgba(60,25,18,0)"); g.fillStyle = top; g.fillRect(0, 0, 1024, 150);
    const chin = g.createLinearGradient(0, 430, 0, 512); chin.addColorStop(0, "rgba(60,25,18,0)"); chin.addColorStop(1, "rgba(60,25,18,0.36)"); g.fillStyle = chin; g.fillRect(0, 430, 1024, 82);
    const F = 512, face = document.createElement("canvas");
    face.width = face.height = F;
    drawFace(face.getContext("2d")!, F, spec, opts);
    // columns covering angles -80..80 degrees around the front
    for (let x = 0; x < 1024; x++) {
      const ang = (x / 1024 - 0.5) * Math.PI * 2;
      if (Math.abs(ang) > 1.4) continue;
      const sx = (0.5 + Math.sin(ang) / 2) * F;
      g.drawImage(face, sx, 0, 1, F, x, 0, 1, 512);
    }
  });
