// Flat hand-drawn face decals. Coordinates are (u, v) in the head's front bounding square (0..1, origin top-left),
// measured on the reference: eye centres (0.33, 0.44) / (0.67, 0.44), eye radius 0.115, mouth centre (0.5, 0.85),
// line width 0.022. A face is a combination of eyes + brows + mouth; expressions are named combinations.
export type Eyes = "open" | "closedWavy" | "arcs" | "hollow" | "halfLid" | "chevron" | "dots" | "lines";
export type Brows = "none" | "angry" | "worried" | "oneArch";
export type Mouth = "smallD" | "bigD" | "frown" | "dash" | "smirk" | "grit" | "teethGrid" | "zigzag" | "smileU" | "wideU" | "o" | "scream" | "wavy";
export type FaceSpec = { eyes: Eyes; brows?: Brows; mouth: Mouth; look?: [number, number]; cheeks?: boolean };
/** per-frame changes laid over an expression: a talking mouth, a blink, where the eyes look */
export type FaceOpts = { mouth?: Mouth; blink?: boolean; look?: [number, number] };
const LOCKED_MOUTHS: Mouth[] = ["scream", "grit", "teethGrid", "zigzag"]; // too specific to be replaced by a talking mouth
const BLINKABLE: Eyes[] = ["open", "halfLid", "hollow", "dots"];
export const faceKey = (name: string, o?: FaceOpts) => name + (o?.mouth ?? "") + (o?.blink ? "b" : "") + (o?.look ? o.look.join(",") : "");

export const EXPRESSIONS: Record<string, FaceSpec> = {
  neutralTalk: { eyes: "open", mouth: "smallD" }, // E01
  laugh: { eyes: "closedWavy", mouth: "bigD" }, // E02
  bigHappy: { eyes: "open", mouth: "bigD" }, // E03
  angryTalk: { eyes: "open", brows: "angry", mouth: "smallD" }, // E04
  angryFrown: { eyes: "open", brows: "angry", mouth: "frown" }, // E05
  smug: { eyes: "halfLid", brows: "oneArch", mouth: "smirk" }, // E06
  hollowShock: { eyes: "hollow", mouth: "grit" }, // E07
  deadpan: { eyes: "lines", mouth: "wavy" }, // E08
  blank: { eyes: "open", mouth: "dash" }, // E09
  worried: { eyes: "open", brows: "worried", mouth: "frown", look: [0.03, 0] }, // E10
  disgust: { eyes: "chevron", mouth: "o", cheeks: true }, // E11
  scream: { eyes: "open", mouth: "scream" }, // E12
  nervous: { eyes: "open", brows: "worried", mouth: "zigzag" }, // E13
  grittedAngry: { eyes: "open", brows: "angry", mouth: "teethGrid" }, // E14
  happyArcs: { eyes: "arcs", mouth: "smileU" }, // E15
  dotSmile: { eyes: "dots", mouth: "wideU" }, // E16
  eyesClosedTalk: { eyes: "lines", mouth: "smallD" },
  mouthSmall: { eyes: "open", mouth: "o" },
};

const INK = "#0b0b0b";

/** draw a face on a square canvas of side S (transparent background) */
export const drawFace = (g: CanvasRenderingContext2D, S: number, base: FaceSpec, opts: FaceOpts = {}) => {
  const spec: FaceSpec = { ...base };
  if (opts.mouth && !LOCKED_MOUTHS.includes(spec.mouth)) spec.mouth = opts.mouth;
  if (opts.blink && BLINKABLE.includes(spec.eyes)) spec.eyes = "lines";
  if (opts.look) spec.look = opts.look;
  const P = (u: number) => u * S;
  // soft depth under the drawing: blush on the cheeks and a small nose shadow (round 3: faces read flat without them)
  for (const cx of [0.2, 0.8]) { const bl = g.createRadialGradient(P(cx), P(0.68), 0, P(cx), P(0.68), P(0.12)); bl.addColorStop(0, "rgba(232,96,96,0.30)"); bl.addColorStop(1, "rgba(232,96,96,0)"); g.fillStyle = bl; g.fillRect(P(cx - 0.13), P(0.55), P(0.26), P(0.26)); }
  g.strokeStyle = "rgba(90,45,30,0.45)"; g.lineWidth = 0.02 * S; g.lineCap = "round"; g.beginPath(); g.moveTo(P(0.47), P(0.645)); g.quadraticCurveTo(P(0.5), P(0.67), P(0.53), P(0.645)); g.stroke();
  const lw = 0.03 * S; // bolder than the 0.022 first measured: thin lines vanished in medium and wide shots
  g.lineCap = "round"; g.lineJoin = "round"; g.lineWidth = lw; g.strokeStyle = INK; g.fillStyle = INK;
  const ex = [0.33, 0.67], ey = 0.44, er = 0.128;
  const [lx, ly] = spec.look ?? [0, 0];
  const line = (pts: [number, number][]) => { g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(P(x), P(y)) : g.moveTo(P(x), P(y)))); g.stroke(); };

  ex.forEach((cx, i) => {
    const side = i === 0 ? -1 : 1; // -1 = viewer's left eye
    switch (spec.eyes) {
      case "open":
        g.fillStyle = "#fff"; g.beginPath(); g.arc(P(cx), P(ey), P(er), 0, Math.PI * 2); g.fill(); g.stroke();
        g.fillStyle = INK; g.beginPath(); g.arc(P(cx + lx), P(ey + ly), P(0.046), 0, Math.PI * 2); g.fill();
        g.fillStyle = "#fff"; g.beginPath(); g.arc(P(cx + lx - 0.016), P(ey + ly - 0.018), P(0.015), 0, Math.PI * 2); g.fill(); g.fillStyle = INK; // highlight
        break;
      case "hollow":
        g.fillStyle = INK; g.beginPath(); g.arc(P(cx), P(ey), P(0.16), 0, Math.PI * 2); g.fill();
        g.fillStyle = "#fff"; g.beginPath(); g.arc(P(cx + 0.02), P(ey - 0.02), P(0.025), 0, Math.PI * 2); g.fill(); g.fillStyle = INK;
        break;
      case "halfLid":
        g.fillStyle = "#fff"; g.beginPath(); g.arc(P(cx), P(ey), P(er), -0.05 * Math.PI, 1.05 * Math.PI); g.closePath(); g.fill(); g.stroke();
        g.fillStyle = INK; g.beginPath(); g.arc(P(cx + lx), P(ey + 0.04), P(0.042), 0, Math.PI * 2); g.fill();
        break;
      case "closedWavy":
        g.beginPath(); g.moveTo(P(cx - 0.1), P(ey)); g.quadraticCurveTo(P(cx - 0.04), P(ey - 0.05), P(cx), P(ey - 0.015));
        g.quadraticCurveTo(P(cx + 0.05), P(ey + 0.02), P(cx + 0.1), P(ey + 0.02 * -side)); g.stroke();
        break;
      case "lines":
        g.beginPath(); g.moveTo(P(cx - 0.08), P(ey)); g.quadraticCurveTo(P(cx), P(ey + 0.012), P(cx + 0.08), P(ey - 0.004)); g.stroke();
        break;
      case "arcs":
        g.beginPath(); g.moveTo(P(cx - 0.1), P(ey + 0.03)); g.quadraticCurveTo(P(cx), P(ey - 0.1), P(cx + 0.1), P(ey + 0.03)); g.stroke();
        break;
      case "chevron": // viewer's left eye is "<", right eye is ">"  (points outward)
        g.strokeStyle = "#3a1f14";
        line([[cx - side * 0.08, ey - 0.07], [cx + side * 0.09, ey], [cx - side * 0.08, ey + 0.07]]);
        g.strokeStyle = INK;
        break;
      case "dots":
        g.beginPath(); g.ellipse(P(cx), P(ey), P(0.034), P(0.052), 0, 0, Math.PI * 2); g.fill();
        g.fillStyle = "#fff"; g.beginPath(); g.arc(P(cx - 0.01), P(ey - 0.02), P(0.011), 0, Math.PI * 2); g.fill(); g.fillStyle = INK;
        break;
    }
    g.lineWidth = lw * 1.35;
    switch (spec.brows) {
      case "angry": line([[cx + side * 0.12, ey - er - 0.07], [cx - side * 0.09, ey - er + 0.035]]); break;
      case "worried": line([[cx + side * 0.11, ey - er - 0.005], [cx - side * 0.07, ey - er - 0.07]]); break;
      case "oneArch":
        if (i === 1) { g.beginPath(); g.moveTo(P(cx - 0.09), P(ey - er - 0.05)); g.quadraticCurveTo(P(cx), P(ey - er - 0.13), P(cx + 0.09), P(ey - er - 0.06)); g.stroke(); }
        break;
    }
    g.lineWidth = lw;
  });

  const mx = 0.5, my = 0.85;
  const openD = (w: number, h: number) => {
    g.fillStyle = INK; g.beginPath(); g.moveTo(P(mx - w / 2), P(my - h / 2));
    g.lineTo(P(mx + w / 2), P(my - h / 2));
    g.quadraticCurveTo(P(mx + w / 2), P(my + h * 0.75), P(mx), P(my + h * 0.62));
    g.quadraticCurveTo(P(mx - w / 2), P(my + h * 0.75), P(mx - w / 2), P(my - h / 2)); g.closePath(); g.fill(); g.stroke();
    g.save(); g.clip();
    g.fillStyle = "#fff"; g.fillRect(P(mx - w / 2), P(my - h / 2), P(w), P(h * 0.33));
    g.fillStyle = "#e88aa0"; g.beginPath(); g.ellipse(P(mx), P(my + h * 0.62), P(w * 0.3), P(h * 0.3), 0, 0, Math.PI * 2); g.fill();
    g.restore(); g.fillStyle = INK;
  };
  switch (spec.mouth) {
    case "smallD": openD(0.24, 0.14); break;
    case "bigD": openD(0.38, 0.22); break;
    case "frown": g.beginPath(); g.moveTo(P(mx - 0.08), P(my + 0.03)); g.quadraticCurveTo(P(mx), P(my - 0.05), P(mx + 0.08), P(my + 0.03)); g.stroke(); break;
    case "dash": line([[mx - 0.05, my], [mx + 0.05, my]]); break;
    case "wavy": g.beginPath(); g.moveTo(P(mx), P(my)); g.quadraticCurveTo(P(mx + 0.03), P(my - 0.02), P(mx + 0.05), P(my)); g.quadraticCurveTo(P(mx + 0.08), P(my + 0.02), P(mx + 0.1), P(my)); g.stroke(); break;
    case "smirk": g.beginPath(); g.moveTo(P(mx - 0.07), P(my + 0.01)); g.quadraticCurveTo(P(mx + 0.02), P(my + 0.04), P(mx + 0.09), P(my - 0.035)); g.stroke(); break;
    case "grit":
      g.fillStyle = "#fff"; g.beginPath(); g.roundRect(P(mx - 0.07), P(my - 0.035), P(0.14), P(0.07), P(0.02)); g.fill(); g.stroke();
      g.beginPath(); g.moveTo(P(mx - 0.06), P(my)); g.quadraticCurveTo(P(mx - 0.02), P(my - 0.015), P(mx + 0.02), P(my + 0.005)); g.quadraticCurveTo(P(mx + 0.045), P(my + 0.012), P(mx + 0.06), P(my)); g.stroke();
      g.fillStyle = INK; break;
    case "teethGrid":
      g.fillStyle = "#fff"; g.beginPath(); g.roundRect(P(mx - 0.1), P(my - 0.05), P(0.2), P(0.1), P(0.025)); g.fill(); g.stroke();
      line([[mx - 0.1, my], [mx + 0.1, my]]);
      for (let k = -1.5; k <= 1.5; k++) line([[mx + k * 0.04, my - 0.05], [mx + k * 0.04, my + 0.05]]);
      g.fillStyle = INK; break;
    case "zigzag": line([[mx - 0.06, my], [mx - 0.03, my - 0.025], [mx, my + 0.015], [mx + 0.03, my - 0.025], [mx + 0.06, my]]); break;
    case "smileU": g.beginPath(); g.moveTo(P(mx - 0.07), P(my - 0.02)); g.quadraticCurveTo(P(mx), P(my + 0.06), P(mx + 0.07), P(my - 0.02)); g.stroke(); break;
    case "wideU": g.beginPath(); g.moveTo(P(mx - 0.12), P(my - 0.03)); g.quadraticCurveTo(P(mx), P(my + 0.09), P(mx + 0.12), P(my - 0.03)); g.stroke(); break;
    case "o": g.beginPath(); g.ellipse(P(mx), P(my), P(0.045), P(0.055), 0, 0, Math.PI * 2); g.fill(); g.fillStyle = "#e88aa0"; g.beginPath(); g.ellipse(P(mx), P(my + 0.02), P(0.025), P(0.022), 0, 0, Math.PI * 2); g.fill(); g.fillStyle = INK; break;
    case "scream": {
      const w = 0.5, h = 0.42, y0 = my - 0.22;
      g.fillStyle = INK; g.beginPath(); g.moveTo(P(mx - w * 0.36), P(y0)); g.lineTo(P(mx + w * 0.36), P(y0));
      g.quadraticCurveTo(P(mx + w * 0.56), P(y0 + h * 0.5), P(mx + w / 2), P(y0 + h)); g.lineTo(P(mx - w / 2), P(y0 + h));
      g.quadraticCurveTo(P(mx - w * 0.56), P(y0 + h * 0.5), P(mx - w * 0.36), P(y0)); g.closePath(); g.fill(); g.stroke();
      g.fillStyle = "#e88aa0"; g.beginPath(); g.ellipse(P(mx), P(y0 + h * 0.86), P(w * 0.24), P(h * 0.16), 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = "#fff";
      for (let k = -2; k <= 2; k++) {
        g.fillRect(P(mx + k * 0.062 - 0.026), P(y0 + 0.012), P(0.052), P(0.06));
        g.fillRect(P(mx + k * 0.078 - 0.03), P(y0 + h - 0.062), P(0.06), P(0.05));
      }
      g.fillStyle = INK; break;
    }
  }
  if (spec.cheeks) {
    g.beginPath(); g.arc(P(0.3), P(0.8), P(0.035), Math.PI * 0.6, Math.PI * 1.4); g.stroke();
    g.beginPath(); g.arc(P(0.7), P(0.8), P(0.035), -Math.PI * 0.4, Math.PI * 0.4); g.stroke();
  }
};
