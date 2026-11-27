// Easing functions and the keyframe-track evaluator. Everything is a pure function of its inputs (seekable).
export type EaseName = string;

const bezier = (x1: number, y1: number, x2: number, y2: number) => (x: number) => {
  // solve bezier x(t) = x by bisection, return y(t); y may leave [0,1] (overshoot)
  let lo = 0, hi = 1, t = x;
  for (let i = 0; i < 24; i++) {
    t = (lo + hi) / 2;
    const cx = 3 * (1 - t) * (1 - t) * t * x1 + 3 * (1 - t) * t * t * x2 + t * t * t;
    if (cx < x) lo = t; else hi = t;
  }
  return 3 * (1 - t) * (1 - t) * t * y1 + 3 * (1 - t) * t * t * y2 + t * t * t;
};

export const EASE: Record<string, (t: number) => number> = {
  linear: (t) => t,
  easeInQuad: (t) => t * t,
  easeOutQuad: (t) => 1 - (1 - t) ** 2,
  easeInOutQuad: (t) => (t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2),
  easeInCubic: (t) => t ** 3,
  easeOutCubic: (t) => 1 - (1 - t) ** 3,
  easeInQuart: (t) => t ** 4,
  easeOutQuart: (t) => 1 - (1 - t) ** 4,
  easeInSine: (t) => 1 - Math.cos((t * Math.PI) / 2),
  easeOutSine: (t) => Math.sin((t * Math.PI) / 2),
  easeInOutSine: (t) => -(Math.cos(Math.PI * t) - 1) / 2,
  sine: (t) => 0.5 - 0.5 * Math.cos(Math.PI * t),
  // measured character-animation curves (reconstruction report D)
  snap: bezier(0.2, 0.9, 0.3, 1.0),
  backOut: bezier(0.3, 1.5, 0.5, 1.0),
  smooth: bezier(0.4, 0, 0.2, 1),
};

export const ease = (name: EaseName | undefined, t: number) => {
  const f = EASE[name ?? "linear"];
  if (!f) throw new Error(`unknown easing "${name}"`);
  if (t <= 0) return 0;
  if (t >= 1) return 1; // exact endpoints (the bezier solver is approximate)
  return f(t);
};

export type Key<T = number> = { f: number; v: T; ease?: EaseName };

/** numeric track; `settle` = exponential approach with tau 4 frames; `step` = hold previous value */
export const evalTrack = (keys: Key[], f: number): number => {
  if (f <= keys[0].f) return keys[0].v;
  for (let i = 1; i < keys.length; i++) {
    if (f <= keys[i].f) {
      const a = keys[i - 1], b = keys[i];
      const e = b.ease ?? "snap";
      if (e === "step") return a.v;
      if (e === "settle") return b.v + (a.v - b.v) * Math.exp(-(f - a.f) / 4);
      return a.v + (b.v - a.v) * ease(e, (f - a.f) / (b.f - a.f));
    }
  }
  return keys[keys.length - 1].v;
};

/** step track for discrete values (face decals): the value of the last key at or before f */
export const evalStep = <T,>(keys: Key<T>[], f: number): T => {
  let v = keys[0].v;
  for (const k of keys) if (k.f <= f) v = k.v;
  return v;
};
