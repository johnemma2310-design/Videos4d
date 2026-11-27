// Effects library. Every effect is stateless: what it shows at frame f is computed from f and a seed only, so frames
// can be rendered in any order and sub-frame samples (motion blur) just work. Sizes are studs, times are frames at 30 fps.
// Looks and timings follow the measurements in reconstruction report D, section 5, and were tuned by eye against
// reference frames on the effects sheet (data/fx_tests.json, scripts/fxsheet.sh).
import * as THREE from "three";
import { Registry } from "../core/registry";
import { hash01, rng } from "../core/rng";
import { softDiscTexture } from "../tex/textures";

export type Vfx = { object: THREE.Object3D; update: (f: number, camera: THREE.PerspectiveCamera) => void };
export type VfxBuilder = (params: Record<string, any>, seed: number) => Vfx;
export const vfx = new Registry<VfxBuilder>("vfx");

const hdr = (hex: string, k: number) => new THREE.Color(hex).multiplyScalar(k);
let DISC: THREE.Texture | null = null;
const disc = () => (DISC ??= softDiscTexture(128, 0.05));

/** irregular starburst: a soft core with uneven rays (the reference fireballs and hand fire read as spiky stars) */
const starTextures: THREE.Texture[] = [];
const star = (variant: number) => {
  const v = variant % 4;
  if (starTextures[v]) return starTextures[v];
  const S = 256, c = document.createElement("canvas");
  c.width = c.height = S;
  const g = c.getContext("2d")!, r = rng(1234 + v * 17);
  const core = g.createRadialGradient(S / 2, S / 2, 0, S / 2, S / 2, S * 0.3);
  core.addColorStop(0, "rgba(255,255,255,1)"); core.addColorStop(0.45, "rgba(255,255,255,0.75)"); core.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = core; g.fillRect(0, 0, S, S);
  g.translate(S / 2, S / 2);
  const rays = 11 + Math.floor(r() * 5);
  for (let i = 0; i < rays; i++) {
    const a = (i / rays) * Math.PI * 2 + (r() - 0.5) * 0.5, len = S * (0.26 + r() * 0.22), w = S * (0.035 + r() * 0.04);
    const grd = g.createLinearGradient(0, 0, Math.cos(a) * len, Math.sin(a) * len);
    grd.addColorStop(0, "rgba(255,255,255,0.9)"); grd.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = grd;
    g.beginPath(); g.moveTo(Math.cos(a + 1.57) * w, Math.sin(a + 1.57) * w); g.lineTo(Math.cos(a) * len, Math.sin(a) * len); g.lineTo(Math.cos(a - 1.57) * w, Math.sin(a - 1.57) * w); g.closePath(); g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  return (starTextures[v] = t);
};
const additive = (map: THREE.Texture, color: THREE.Color) => new THREE.SpriteMaterial({ map, color, blending: THREE.AdditiveBlending, depthWrite: false, fog: false, transparent: true });

// ---------------------------------------------------------------- embers
// Rising sparks in a box that wraps around its centre: an endless field with no state. On the reference they are
// bright yellow teardrops, 4-14 px far away and soft ovals up to ~100 px close to the lens.
vfx.add("embers", (p, seed) => {
  const n = p.count ?? 450, box: [number, number, number] = p.box ?? [60, 30, 60], centre: [number, number, number] = p.centre ?? [0, 12, 0];
  const r = rng(seed), base = new Float32Array(n * 3), rnd = new Float32Array(n * 4);
  for (let i = 0; i < n; i++) {
    base.set([r(), r(), r()], i * 3);
    rnd.set([r(), r(), r(), r()], i * 4);
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(base, 3));
  geo.setAttribute("aRnd", new THREE.BufferAttribute(rnd, 4));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false,
    uniforms: {
      uT: { value: 0 }, uBox: { value: new THREE.Vector3(...box) }, uCentre: { value: new THREE.Vector3(...centre) },
      uRise: { value: p.rise ?? 2.6 }, uWind: { value: new THREE.Vector2(...(p.wind ?? [1.2, 0.3])) },
      uSize: { value: p.size ?? 0.34 }, uPx: { value: 1920 }, uHot: { value: hdr(p.hot ?? "#fff3b4", p.gain ?? 2.2) }, uCool: { value: hdr(p.cool ?? "#f08a2c", p.gain ?? 2.2) },
    },
    vertexShader: /* glsl */ `
      attribute vec4 aRnd; uniform float uT, uRise, uSize, uPx; uniform vec3 uBox, uCentre; uniform vec2 uWind;
      varying float vK; varying float vNear;
      void main() {
        float sp = 0.6 + aRnd.x * 0.9;
        vec3 q = position;
        q.y = fract(q.y + uT * uRise * sp / uBox.y);
        q.x = fract(q.x + uT * uWind.x * sp / uBox.x + sin(uT * (0.6 + aRnd.y) + aRnd.z * 6.28) * 0.5 / uBox.x);
        q.z = fract(q.z + uT * uWind.y * sp / uBox.z + cos(uT * (0.5 + aRnd.z) + aRnd.w * 6.28) * 0.5 / uBox.z);
        vec4 mv = modelViewMatrix * vec4(uCentre + (q - 0.5) * uBox, 1.0);
        gl_Position = projectionMatrix * mv;
        float d = max(0.5, -mv.z);
        vNear = smoothstep(12.0, 3.0, d);
        gl_PointSize = min(220.0, uPx * 0.5 * uSize * (0.5 + aRnd.w) * (1.0 + vNear * 1.5) * projectionMatrix[1][1] / d);
        vK = (0.55 + 0.45 * aRnd.y) * (0.8 + 0.2 * sin(uT * 9.0 + aRnd.x * 40.0)) * smoothstep(0.0, 0.08, q.y) * smoothstep(1.0, 0.85, q.y);
      }`,
    fragmentShader: /* glsl */ `
      uniform vec3 uHot, uCool; varying float vK; varying float vNear;
      void main() {
        vec2 c = gl_PointCoord - 0.5;
        c.x *= 1.7;                              // taller than wide
        c.y += 0.12 * (1.0 - 4.0 * c.x * c.x);   // pointed top, round bottom: a teardrop
        float r = length(c) * 2.0;
        float a = smoothstep(1.0, mix(0.55, 0.25, vNear), r);
        gl_FragColor = vec4(mix(uCool, uHot, smoothstep(0.85, 0.2, r)) * a * vK, 1.0);
      }`,
  });
  const pts = new THREE.Points(geo, mat);
  pts.frustumCulled = false;
  return { object: pts, update: (f) => { mat.uniforms.uT.value = f / 30; } };
});

// ---------------------------------------------------------------- flame (braziers, torches, hand fire)
// A camera-facing teardrop of scrolling noise with a hot core, plus a small starburst and a modest halo and light.
const FLAME_FRAG = /* glsl */ `
  uniform float uT, uSeed; uniform vec3 uCore, uMid, uTip; varying vec2 vUv;
  float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float n(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
  void main() {
    vec2 u = vUv; float y = u.y;
    float x = (u.x - 0.5) * 2.0;
    float wob = (n(vec2(u.x * 3.0 + uSeed, y * 2.5 - uT * 3.7)) - 0.5) * 0.7 * y;
    float w = mix(0.85, 0.0, pow(y, 0.7)) * (0.9 + 0.2 * sin(uT * 23.5 + uSeed));
    float d = abs(x + wob) / max(w, 0.001);
    float body = smoothstep(1.0, 0.25, d) * smoothstep(0.0, 0.08, y);
    float fl = n(vec2(u.x * 5.0 + uSeed * 3.0, y * 4.0 - uT * 6.0));
    body *= 0.75 + 0.5 * fl;
    vec3 col = mix(uTip, uMid, smoothstep(0.95, 0.35, y + d * 0.3));
    col = mix(col, uCore, smoothstep(0.75, 0.1, d + y * 0.9));
    gl_FragColor = vec4(col * body, 1.0);
  }`;
const QUAD_VERT = /* glsl */ `varying vec2 vUv; void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
vfx.add("flame", (p, seed) => {
  const size = p.size ?? 1.2, gain = p.gain ?? 1.5;
  const g = new THREE.Group();
  g.position.set(...((p.pos ?? [0, 0, 0]) as [number, number, number]));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false, side: THREE.DoubleSide,
    uniforms: { uT: { value: 0 }, uSeed: { value: (seed % 97) * 0.37 }, uCore: { value: hdr("#fefea2", gain / Math.sqrt(Math.max(1, size / 1.6))) }, uMid: { value: hdr("#f08a3c", gain * 0.8) }, uTip: { value: hdr("#c04848", gain * 0.5) } },
    vertexShader: QUAD_VERT, fragmentShader: FLAME_FRAG,
  });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(size, size * 1.7), mat);
  quad.position.y = size * 0.8;
  const big = Math.max(1, size / 1.6); // large flames: smaller, dimmer starburst and halo, so the flame shape survives the bloom
  const burst = new THREE.Sprite(additive(star(seed), hdr("#ffe9a0", (gain * 0.55) / big)));
  burst.scale.setScalar((size * 1.5) / Math.sqrt(big));
  burst.position.y = size * 0.45;
  const halo = new THREE.Sprite(additive(disc(), hdr("#ff9a3c", 0.16 / big)));
  halo.scale.setScalar(size * 3);
  halo.position.y = size * 0.6;
  const light = new THREE.PointLight("#ff9a3c", p.light ?? 9, p.reach ?? 14, 2);
  light.position.y = size * 0.8;
  g.add(quad, burst, halo, light);
  const base = light.intensity;
  return {
    object: g,
    update: (f, cam) => {
      mat.uniforms.uT.value = f / 30;
      quad.quaternion.copy(cam.quaternion);
      const k = 0.85 + 0.15 * Math.sin((f / 8) * Math.PI * 2 + seed) * Math.sin(f * 0.37 + seed * 1.7); // ~8-frame flicker
      light.intensity = base * k;
      burst.material.rotation = Math.floor(f / 2) * 1.3 + seed; // the rays re-arrange every other frame
      burst.scale.setScalar(((size * 1.5) / Math.sqrt(big)) * (0.85 + 0.3 * k));
    },
  };
});

// ---------------------------------------------------------------- flame jet (flamethrower from a hand)
// Measured: grows from 57 to 557 px in 15 frames, pale-yellow core, orange edge, red tip. A row of additive puffs
// along the direction, widening with distance and re-jittered every frame.
vfx.add("jet", (p, seed) => {
  const from: [number, number, number] = p.from ?? [0, 3, 0], dir = new THREE.Vector3(...((p.dir ?? [-1, 0, 0]) as [number, number, number])).normalize();
  const length = p.length ?? 10, start = p.start ?? 0, N = 26, g = new THREE.Group();
  const puffs = Array.from({ length: N }, (_, i) => { const s = new THREE.Sprite(additive(i % 3 ? disc() : star(i), new THREE.Color())); g.add(s); return s; });
  const core = new THREE.Color("#fffbd0"), mid = new THREE.Color("#f6a040"), tip = new THREE.Color("#c04848"), c = new THREE.Color();
  const light = new THREE.PointLight("#ffb347", 0, 26, 2);
  g.add(light);
  return {
    object: g,
    update: (f) => {
      const grow = Math.min(1, Math.max(0, (f - start) / 15)), reach = length * (0.1 + 0.9 * grow), k = Math.floor(f);
      light.intensity = f >= start ? 30 * grow : 0;
      light.position.set(from[0] + dir.x * reach * 0.4, from[1] + 1, from[2] + dir.z * reach * 0.4);
      puffs.forEach((s, i) => {
        const u = (i + hash01(i + k * 31, seed)) / N;
        s.visible = f >= start;
        const w = 0.9 + u * 3.6;
        s.position.set(from[0] + dir.x * reach * u, from[1] + dir.y * reach * u + (hash01(i * 3 + k * 17, seed) - 0.5) * w * 0.7, from[2] + dir.z * reach * u + (hash01(i * 5 + k * 13, seed) - 0.5) * w * 0.7);
        s.scale.setScalar(w * (0.8 + 0.5 * hash01(i + k * 7, seed)));
        if (u < 0.45) c.copy(core).lerp(mid, u / 0.45); else c.copy(mid).lerp(tip, (u - 0.45) / 0.55);
        s.material.color.copy(c).multiplyScalar(1.25 * (1 - u * 0.6));
        s.material.rotation = hash01(i + k, seed) * 6.28;
      });
    },
  };
});

// ---------------------------------------------------------------- fireballs with trails
// Each ball flies a straight line on a seeded launch schedule; its trail is the same path sampled at earlier frames.
// Measured look: saturated pale-yellow core, spiky rays, orange halo to about twice the core, grainy orange trail.
vfx.add("fireballs", (p, seed) => {
  const count = p.count ?? 6, from: [number, number, number] = p.from ?? [60, 26, -40], vel: [number, number, number] = p.velocity ?? [-1.6, -0.12, 0.25];
  const every = p.every ?? 14, spread: [number, number, number] = p.spread ?? [10, 10, 30], size = p.size ?? 3.2, life = p.life ?? 90, TRAIL = 22;
  const g = new THREE.Group();
  const balls = Array.from({ length: count }, (_, i) => {
    const core = new THREE.Sprite(additive(disc(), hdr("#ffe89a", 1.5)));
    core.scale.setScalar(size * 1.15);
    const rays = new THREE.Sprite(additive(star(i), hdr("#ffd27a", 1.1)));
    const halo = new THREE.Sprite(additive(disc(), hdr("#f7882c", 0.55)));
    halo.scale.setScalar(size * 3.4);
    const trail = Array.from({ length: TRAIL }, () => {
      const s = new THREE.Sprite(additive(disc(), new THREE.Color()));
      g.add(s);
      return s;
    });
    const light = new THREE.PointLight("#ffb347", 25, 34, 2);
    g.add(halo, rays, core, light);
    return { core, rays, halo, trail, light, i };
  });
  const hot = new THREE.Color("#ffd27a"), mid = new THREE.Color("#e0723b"), end = new THREE.Color("#3a1a12");
  const posAt = (i: number, f: number, out: THREE.Vector3) => {
    // launch k of ball i happens at frame k * every * count + i * every (+ jitter); position restarts at each launch
    const cycle = every * count, t0 = i * every + hash01(i, seed) * every * 0.6;
    const k = Math.floor((f - t0) / cycle), age = f - t0 - k * cycle;
    const j = (a: number) => (hash01(i * 31 + k * 7 + a, seed) - 0.5) * 2;
    out.set(from[0] + j(1) * spread[0] + vel[0] * age, from[1] + j(2) * spread[1] + vel[1] * age, from[2] + j(3) * spread[2] + vel[2] * age);
    return age;
  };
  const v = new THREE.Vector3(), c = new THREE.Color();
  return {
    object: g,
    update: (f) => {
      for (const b of balls) {
        const age = posAt(b.i, f, v);
        const alive = age >= 0 && age < life;
        b.core.visible = b.rays.visible = b.halo.visible = alive;
        b.light.intensity = alive ? 25 : 0;
        for (const o of [b.core, b.rays, b.halo, b.light]) o.position.copy(v);
        const fl = 0.85 + 0.3 * hash01(Math.floor(f) + b.i * 13, seed);
        b.rays.scale.setScalar(size * 2.3 * fl);
        b.rays.material.rotation = Math.floor(f / 2) * 0.9 + b.i;
        b.trail.forEach((s, n) => {
          const u = (n + 1) / TRAIL, back = (n + 1) * 1.4, a2 = posAt(b.i, f - back, v);
          s.visible = alive && a2 >= 0;
          s.position.copy(v);
          // grainy: each puff is offset and sized by a hash, and drifts up as it ages
          s.position.y += u * u * 1.5 + (hash01(n * 7 + b.i * 50, seed) - 0.5) * size * 0.5 * (0.3 + u);
          s.position.z += (hash01(n * 11 + b.i * 50, seed) - 0.5) * size * 0.4;
          s.scale.setScalar(size * (0.45 + u * 0.9) * (0.7 + 0.6 * hash01(n + b.i * 91, seed)));
          if (u < 0.35) c.copy(hot).lerp(mid, u / 0.35); else c.copy(mid).lerp(end, (u - 0.35) / 0.65);
          s.material.color.copy(c).multiplyScalar(0.5 * (1 - u));
        });
      }
    },
  };
});

// ---------------------------------------------------------------- rain
// Dense long streaks in a box in front of the camera, re-randomised every whole frame (the reference streaks have no
// frame-to-frame correspondence). Thin camera-facing quads, so they keep their width under supersampling.
vfx.add("rain", (p, seed) => {
  const n = p.count ?? 3200, box: [number, number, number] = p.box ?? [44, 30, 34], centre: [number, number, number] = p.centre ?? [0, 13, -2], len = p.length ?? 5.5, w = p.width ?? 0.03;
  const pos = new Float32Array(n * 12), alpha = new Float32Array(n * 4), idx = new Uint32Array(n * 6), geo = new THREE.BufferGeometry();
  for (let i = 0; i < n; i++) idx.set([i * 4, i * 4 + 1, i * 4 + 2, i * 4 + 2, i * 4 + 1, i * 4 + 3], i * 6);
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("aA", new THREE.BufferAttribute(alpha, 1));
  geo.setIndex(new THREE.BufferAttribute(idx, 1));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, fog: false, side: THREE.DoubleSide,
    uniforms: { uColor: { value: new THREE.Color(p.color ?? "#f2f6fb") }, uOpacity: { value: p.opacity ?? 0.6 } },
    vertexShader: /* glsl */ `attribute float aA; varying float vA; void main() { vA = aA; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: /* glsl */ `uniform vec3 uColor; uniform float uOpacity; varying float vA; void main() { gl_FragColor = vec4(uColor, uOpacity * vA); }`,
  });
  const mesh = new THREE.Mesh(geo, mat);
  mesh.frustumCulled = false;
  let last = NaN;
  const right = new THREE.Vector3();
  return {
    object: mesh,
    update: (f, cam) => {
      const k = Math.ceil(f);
      if (k === last) return;
      last = k;
      right.setFromMatrixColumn(cam.matrixWorld, 0);
      for (let i = 0; i < n; i++) {
        const h = (a: number) => hash01(i * 4 + a + k * 7919, seed);
        const x = centre[0] + (h(0) - 0.5) * box[0], y = centre[1] + (h(1) - 0.5) * box[1], z = centre[2] + (h(2) - 0.5) * box[2];
        const l = len * (0.5 + h(3)), lean = (hash01(i, seed) - 0.5) * 0.12 * l, ww = w * (0.6 + hash01(i + 5, seed) * 0.9);
        const rx = right.x * ww, rz = right.z * ww;
        pos.set([x - rx, y, z - rz, x + rx, y, z + rz, x + lean - rx, y - l, z - rz, x + lean + rx, y - l, z + rz], i * 12);
        const a = 0.35 + 0.65 * hash01(i + 9, seed);
        alpha.set([a * 0.2, a * 0.2, a, a], i * 4); // fades toward its tail (the top)
      }
      geo.attributes.position.needsUpdate = true;
      geo.attributes.aA.needsUpdate = true;
    },
  };
});

// ---------------------------------------------------------------- steam / smoke puffs
vfx.add("steam", (p, seed) => {
  const n = p.count ?? 12, at: [number, number, number] = p.pos ?? [0, 0, 0], spread = p.spread ?? 4, rise = p.rise ?? 6, size = p.size ?? 6, period = p.period ?? 120;
  const g = new THREE.Group(), r = rng(seed);
  const puffs = Array.from({ length: n }, () => {
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: disc(), color: p.color ?? "#e6e2de", transparent: true, depthWrite: false, opacity: 0 }));
    g.add(s);
    return { s, x: (r() - 0.5) * spread, z: (r() - 0.5) * spread, ph: r(), k: 0.7 + r() * 0.6 };
  });
  return {
    object: g,
    update: (f) => {
      for (const q of puffs) {
        const u = (((f / period) * q.k + q.ph) % 1 + 1) % 1;
        q.s.position.set(at[0] + q.x * (1 + u), at[1] + u * rise, at[2] + q.z * (1 + u));
        q.s.scale.setScalar(size * (0.5 + u));
        q.s.material.opacity = (p.opacity ?? 0.3) * Math.sin(Math.PI * u);
      }
    },
  };
});

// ---------------------------------------------------------------- water surface
// Stylised near-opaque water. The reference shows a bright lattice of ripple lines drifting over a flat colour
// (milky turquoise by day, dark green at night), with foam patches. The lattice is the edge pattern of two moving
// cell-noise layers.
vfx.add("water", (p) => {
  const size: [number, number] = p.size ?? [40, 400];
  const mat = new THREE.ShaderMaterial({
    fog: true,
    uniforms: THREE.UniformsUtils.merge([THREE.UniformsLib.fog, {
      uT: { value: 0 }, uDeep: { value: new THREE.Color(p.deep ?? "#58bcc6") }, uLight: { value: new THREE.Color(p.light ?? "#8fd6da") },
      uLine: { value: new THREE.Color(p.line ?? "#eafcff") }, uLineAmt: { value: p.lineAmount ?? 0.75 },
      uFoam: { value: new THREE.Color(p.foam ?? "#f2fbfc") }, uFoamAmt: { value: p.foamAmount ?? 0.12 },
      uGlint: { value: hdr(p.glint ?? "#ffffff", p.glintGain ?? 0) }, uScale: { value: p.scale ?? 0.42 }, uFlow: { value: p.flow ?? 0.5 },
    }]),
    vertexShader: /* glsl */ `
      #include <fog_pars_vertex>
      varying vec3 vW;
      void main() { vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; vec4 mvPosition = viewMatrix * w; gl_Position = projectionMatrix * mvPosition;
        #include <fog_vertex>
      }`,
    fragmentShader: /* glsl */ `
      #include <fog_pars_fragment>
      uniform float uT, uScale, uFlow, uLineAmt, uFoamAmt; uniform vec3 uDeep, uLight, uLine, uFoam, uGlint; varying vec3 vW;
      vec2 h2(vec2 p) { return fract(sin(vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)))) * 43758.5453); }
      float h(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float n(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
        return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
      // distance to the nearest cell edge: thin where two cells meet
      float cells(vec2 p, float t) {
        vec2 i = floor(p), f = fract(p); float d1 = 8.0, d2 = 8.0;
        for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) {
          vec2 g = vec2(float(x), float(y)), o = h2(i + g);
          o = 0.5 + 0.42 * sin(t + 6.2831 * o);
          float d = length(g + o - f);
          if (d < d1) { d2 = d1; d1 = d; } else if (d < d2) d2 = d;
        }
        return d2 - d1;
      }
      void main() {
        vec2 q = vW.xz * uScale;
        // warp the lattice so the cells read as wavy ripples, not straight-edged polygons
        q += 0.35 * vec2(n(q * 1.7 + vec2(uT * 0.4, 0.0)), n(q * 1.7 + vec2(5.2, uT * 0.5))) ;
        float t = uT * 1.6;
        float e1 = cells(q * vec2(1.0, 0.7) + vec2(0.0, uT * uFlow), t);
        float e2 = cells(q * vec2(1.7, 1.2) + vec2(3.1, -uT * uFlow * 0.7), t * 1.3 + 2.0);
        float lines = smoothstep(0.09, 0.0, e1) * 0.8 + smoothstep(0.07, 0.0, e2) * 0.45;
        float tone = n(q * 0.6 + vec2(uT * 0.1, uT * uFlow * 0.4));
        vec3 col = mix(uDeep, uLight, tone);
        col = mix(col, uLine, clamp(lines, 0.0, 1.0) * uLineAmt);
        float foam = smoothstep(1.0 - uFoamAmt, 1.0, n(q * 1.3 + vec2(-uT * 0.15, uT * uFlow)) * 0.6 + lines * 0.5);
        col = mix(col, uFoam, foam);
        float g = smoothstep(0.985, 1.0, n(q * 7.0 + vec2(uT * 1.3, -uT * 2.1))) * lines;
        gl_FragColor = vec4(col + uGlint * g, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
        #include <fog_fragment>
      }`,
  });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size[0], size[1]), mat);
  m.rotation.x = -Math.PI / 2;
  m.position.set(...((p.pos ?? [0, 0, 0]) as [number, number, number]));
  return { object: m, update: (f) => { mat.uniforms.uT.value = f / 30; } };
});

// ---------------------------------------------------------------- cloud (a personal rain cloud)
// A matte lump of merged blobs that hangs over a spot, pops in, rains under itself and can pour itself out and vanish.
// size = width in studs (3.2 = pillow, 26 = barn). dark 0..1 goes from white to storm grey.
// appear: frame it pops in (default: already there). pour: frame the heavy rain starts. vanish: frame it starts to shrink away.
vfx.add("cloud", (p, seed) => {
  const at: [number, number, number] = p.pos ?? [0, 8, 0], size = p.size ?? 3.2, dark = p.dark ?? 0.25;
  const appear = p.appear ?? -1000, pour = p.pour ?? Infinity, vanish = p.vanish ?? Infinity, rainAmt = p.rain ?? 0.5;
  const g = new THREE.Group(), body = new THREE.Group(), r = rng(seed + 5);
  const top = new THREE.Color("#f4f6fa").lerp(new THREE.Color("#5b606c"), dark), under = new THREE.Color("#c9d0dc").lerp(new THREE.Color("#2c2f38"), dark);
  const glow = p.glow ?? 0; // a little self-light so the cloud still reads at night
  const mat = new THREE.MeshStandardMaterial({ color: top, roughness: 1, metalness: 0, emissive: top, emissiveIntensity: glow });
  const matUnder = new THREE.MeshStandardMaterial({ color: under, roughness: 1, emissive: under, emissiveIntensity: glow });
  const blobs = Math.round(7 + Math.min(14, size * 0.6)), depth = p.depth ?? size * 0.55, h = p.height ?? size * 0.34;
  for (let i = 0; i < blobs; i++) {
    const u = blobs === 1 ? 0.5 : i / (blobs - 1), edge = 1 - Math.abs(u - 0.5) * 1.3;
    const rad = h * (0.55 + 0.6 * edge) * (0.8 + 0.4 * r());
    const m = new THREE.Mesh(new THREE.IcosahedronGeometry(rad, 2), mat);
    m.position.set((u - 0.5) * size * 0.8 + (r() - 0.5) * size * 0.08, rad * 0.35 + (r() - 0.5) * h * 0.2, (r() - 0.5) * depth * 0.75);
    m.scale.set(1.25, 0.85, 1.1);
    m.castShadow = true;
    body.add(m);
  }
  const base = new THREE.Mesh(new THREE.SphereGeometry(0.5, 20, 12), matUnder); // flat dark belly
  base.scale.set(size * 0.92, h * 0.5, depth * 0.95);
  base.position.y = -h * 0.12;
  base.castShadow = true;
  body.add(base);
  g.add(body);
  g.position.set(...at);
  const fall = at[1] - h * 0.2, k = size / 3.2;
  const mk = (count: number, len: number, op: number, s: number) => {
    const v = vfx.get("rain")({ count, box: [size * 0.8, fall, depth * 0.8], centre: [at[0], fall / 2, at[2]], length: len, width: 0.02 + 0.002 * Math.min(6, k), opacity: op, color: p.rainColor ?? "#dfeaf6" }, s);
    return v;
  };
  const drizzle = rainAmt > 0 ? mk(Math.round(Math.min(420, 22 * rainAmt * k * k) + 6), Math.min(2.6, 0.7 + 0.22 * k), 0.6, seed + 1) : null;
  const heavy = Number.isFinite(pour) ? mk(Math.round(Math.min(1500, 160 * k * k)), Math.min(5, 1.6 + 0.5 * k), 0.55, seed + 2) : null;
  const holder = new THREE.Group();
  holder.add(g);
  if (drizzle) holder.add(drizzle.object);
  if (heavy) holder.add(heavy.object);
  return {
    object: holder,
    update: (f, cam) => {
      const a = Math.min(1, Math.max(0, (f - appear) / 5)), pop = a <= 0 ? 0 : 1 + 0.35 * Math.sin(a * Math.PI) * (1 - a) + (a - 1) * (a - 1) * -1 + 0; // overshoot then settle
      const v = Number.isFinite(vanish) ? Math.min(1, Math.max(0, (f - vanish) / 14)) : 0;
      const s = Math.max(0, (a <= 0 ? 0 : Math.min(1.12, a * 1.25) - Math.max(0, a - 0.8) * 0.6) * (1 - v));
      void pop;
      body.scale.setScalar(Math.max(0.0001, s));
      body.visible = s > 0.001;
      body.position.y = Math.sin(f * 0.07 + seed) * 0.06 * Math.sqrt(size);
      if (drizzle) { drizzle.object.visible = a >= 1 && f < pour && v <= 0; if (drizzle.object.visible) drizzle.update(f, cam); }
      if (heavy) { heavy.object.visible = f >= pour && v < 0.9; if (heavy.object.visible) heavy.update(f, cam); }
    },
  };
});

// ---------------------------------------------------------------- props (simple matte primitives)
// items: [{ shape: "box" | "cyl", pos: [x, y, z] (centre), size: [w, h, d] or [radius, height], color, rotY, rotZ, glow }]
vfx.add("props", (p) => {
  const g = new THREE.Group();
  for (const it of (p.items ?? []) as any[]) {
    const s = it.size ?? [1, 1, 1];
    const geo = it.shape === "cyl" ? new THREE.CylinderGeometry(s[0], s[2] ?? s[0], s[1], 20) : new THREE.BoxGeometry(s[0], s[1], s[2]);
    const mat = new THREE.MeshStandardMaterial({ color: it.color ?? "#8a7a6a", roughness: 0.9, emissive: it.glow ? new THREE.Color(it.color ?? "#ffffff") : new THREE.Color(0), emissiveIntensity: it.glow ?? 0 });
    const m = new THREE.Mesh(geo, mat);
    m.position.set(...((it.pos ?? [0, 0, 0]) as [number, number, number]));
    m.rotation.set(THREE.MathUtils.degToRad(it.rotX ?? 0), THREE.MathUtils.degToRad(it.rotY ?? 0), THREE.MathUtils.degToRad(it.rotZ ?? 0));
    m.castShadow = m.receiveShadow = true;
    g.add(m);
  }
  return { object: g, update: () => {} };
});
