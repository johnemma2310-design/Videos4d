// Post chain: scene (HDR, linear, MSAA x4) -> selective bloom -> tone map + sRGB -> display-space grade.
// No vignette, grain, chromatic aberration or depth of field: the reference has none.
import * as THREE from "three";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/examples/jsm/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/examples/jsm/postprocessing/OutputPass.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { GTAOPass } from "three/examples/jsm/postprocessing/GTAOPass.js";
export interface PostParams {
  /** "none" | "aces" | "agx" | "neutral" | "reinhard" */
  toneMapping: string;
  exposure: number;
  bloom: { strength: number; radius: number; threshold: number };
  /** ambient occlusion (contact darkening in creases and under feet). radius in studs; omit or intensity 0 = off */
  ao?: { radius: number; intensity: number };
  /** Display-space grade applied after tone mapping + sRGB encoding (like a video grade). */
  grade: {
    saturation: number;
    contrast: number;
    /** screen-blended into RGB (0..1 display units): lifts blacks / tints shadows */
    lift: [number, number, number];
    /** multiplies RGB: tints highlights */
    gain: [number, number, number];
    gamma: number;
    vignette: number;
  };
}

const TONE: Record<string, THREE.ToneMapping> = {
  none: THREE.NoToneMapping,
  aces: THREE.ACESFilmicToneMapping,
  agx: THREE.AgXToneMapping,
  neutral: THREE.NeutralToneMapping,
  reinhard: THREE.ReinhardToneMapping,
};

/** Final display-space grade: gain -> lift -> gamma -> contrast -> saturation -> vignette. */
const GradeShader = {
  uniforms: {
    tDiffuse: { value: null },
    uSaturation: { value: 1 },
    uContrast: { value: 1 },
    uLift: { value: new THREE.Vector3() },
    uGain: { value: new THREE.Vector3(1, 1, 1) },
    uGamma: { value: 1 },
    uVignette: { value: 0 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uSaturation, uContrast, uGamma, uVignette;
    uniform vec3 uLift, uGain;
    varying vec2 vUv;
    void main() {
      vec3 c = texture2D(tDiffuse, vUv).rgb;
      c = c * uGain + uLift * (1.0 - c);
      c = pow(max(c, 0.0), vec3(1.0 / uGamma));
      c = (c - 0.5) * uContrast + 0.5;
      float y = dot(c, vec3(0.2126, 0.7152, 0.0722));
      c = mix(vec3(y), c, uSaturation);
      vec2 d = vUv - 0.5;
      c *= 1.0 - uVignette * dot(d, d) * 2.0;
      gl_FragColor = vec4(clamp(c, 0.0, 1.0), 1.0);
    }`,
};

/** tone mapping lives on the renderer, so it is re-applied whenever the active shot changes */
export function applyToneMapping(gl: THREE.WebGLRenderer, post: PostParams): void {
  gl.setPixelRatio(1);
  gl.outputColorSpace = THREE.SRGBColorSpace;
  gl.toneMapping = TONE[post.toneMapping] ?? THREE.NoToneMapping;
  gl.toneMappingExposure = post.exposure;
  gl.shadowMap.enabled = true;
  gl.shadowMap.type = THREE.PCFSoftShadowMap;
}

/**
 * Scene (HDR, linear, MSAA x4) -> bloom -> tone map + sRGB -> grade.
 * Returns a composer; call composer.render() once per frame.
 */
export function makePipeline(
  gl: THREE.WebGLRenderer,
  scene: THREE.Scene,
  camera: THREE.Camera,
  width: number,
  height: number,
  post: PostParams,
): EffectComposer {
  applyToneMapping(gl, post);

  const target = new THREE.WebGLRenderTarget(width, height, { type: THREE.HalfFloatType, samples: 4 });
  const composer = new EffectComposer(gl, target);
  composer.setPixelRatio(1);
  composer.setSize(width, height);
  composer.addPass(new RenderPass(scene, camera));
  if (post.ao && post.ao.intensity > 0) {
    // The pass builds its sampling-noise texture from Math.random, which differs in every render tab. Feed it a
    // seeded generator while it is constructed so every tab gets the same texture.
    const realRandom = Math.random;
    let s = 0x2f6e2b1;
    Math.random = () => {
      s = (s + 0x6d2b79f5) | 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    const ao = new GTAOPass(scene, camera, width, height);
    Math.random = realRandom;
    // The pass re-renders the scene with a normal material. Sprites, transparent objects and anything that does not
    // write depth (sky dome, glows, mist) must sit that out, or they occlude like solid walls.
    const hidden: THREE.Object3D[] = [];
    const pass = ao as unknown as { _overrideVisibility: () => void; _restoreVisibility: () => void };
    pass._overrideVisibility = () => {
      scene.traverse((o) => {
        const m = (o as THREE.Mesh).material as THREE.Material | THREE.Material[] | undefined;
        const mats = m ? (Array.isArray(m) ? m : [m]) : [];
        const skip = (o as THREE.Sprite).isSprite || (o as THREE.Points).isPoints || (o as THREE.Line).isLine || mats.some((x) => x.transparent || !x.depthWrite);
        if (skip && o.visible) { o.visible = false; hidden.push(o); }
      });
    };
    pass._restoreVisibility = () => { hidden.forEach((o) => (o.visible = true)); hidden.length = 0; };
    ao.updateGtaoMaterial({ radius: post.ao.radius, distanceExponent: 1, thickness: 1, scale: 1, samples: 16 });
    ao.blendIntensity = post.ao.intensity;
    composer.addPass(ao);
  }
  if (post.bloom.strength > 0) {
    composer.addPass(
      new UnrealBloomPass(new THREE.Vector2(width, height), post.bloom.strength, post.bloom.radius, post.bloom.threshold),
    );
  }
  composer.addPass(new OutputPass());
  const grade = new ShaderPass(GradeShader);
  grade.uniforms.uSaturation.value = post.grade.saturation;
  grade.uniforms.uContrast.value = post.grade.contrast;
  grade.uniforms.uLift.value.set(...post.grade.lift);
  grade.uniforms.uGain.value.set(...post.grade.gain);
  grade.uniforms.uGamma.value = post.grade.gamma;
  grade.uniforms.uVignette.value = post.grade.vignette;
  composer.addPass(grade);
  return composer;
}
