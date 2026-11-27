// The engine: owns one WebGLRenderer on a plain canvas and draws a frame as a pure function of the frame number.
// No React, no Remotion imports here.
//   Stage   = one scene + camera + optional post settings (one per shot).
//   Program = builds stages once and returns the per-frame update, which may switch the active stage.
// Frames may be fractional: motion blur renders several sub-frames per frame and the host averages them.
import * as THREE from "three";
import type { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { Registry } from "./core/registry";
import { applyToneMapping, makePipeline, type PostParams } from "./post/pipeline";

export type EngineInfo = { renderer: string; vendor: string; webgl2: boolean };
export type Stage = { scene: THREE.Scene; camera: THREE.PerspectiveCamera; post?: PostParams };
export type ProgramResult = ((frame: number) => void) | { update: (frame: number) => void; samples?: (frame: number) => number };
export type Program = (engine: Engine, props: Record<string, unknown>) => ProgramResult;
export const programs = new Registry<Program>("program");

export class Engine {
  readonly renderer: THREE.WebGLRenderer;
  readonly info: EngineInfo;
  /** the default stage; simple programs just fill these */
  readonly scene = new THREE.Scene();
  readonly camera: THREE.PerspectiveCamera;
  private stage: Stage;
  private composers = new Map<Stage, EffectComposer>();
  private update: (frame: number) => void;
  private sampleCount: (frame: number) => number;

  /** `scale` = supersampling factor: the GL canvas is scale x the output size and the host downsamples it */
  constructor(canvas: HTMLCanvasElement, readonly width: number, readonly height: number, program: string, props: Record<string, unknown> = {}, readonly scale = 1) {
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
    this.renderer.setPixelRatio(1);
    this.renderer.setSize(width * scale, height * scale, false);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    const gl = this.renderer.getContext();
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    this.info = {
      renderer: ext ? String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)) : "unknown",
      vendor: ext ? String(gl.getParameter(ext.UNMASKED_VENDOR_WEBGL)) : "unknown",
      webgl2: this.renderer.capabilities.isWebGL2,
    };
    this.camera = this.makeCamera();
    this.stage = { scene: this.scene, camera: this.camera };
    const r = programs.get(program)(this, props);
    this.update = typeof r === "function" ? r : r.update;
    this.sampleCount = typeof r === "function" || !r.samples ? () => 1 : r.samples;
  }

  makeCamera(fov = 47) { // 47 deg: measured default of the reference
    return new THREE.PerspectiveCamera(fov, this.width / this.height, 0.3, 30000);
  }

  /** post chain for the default stage */
  usePost(post: PostParams) {
    this.stage.post = post;
  }

  /** make another stage the one that gets drawn (multi-shot programs call this from update) */
  setStage(stage: Stage) {
    this.stage = stage;
  }

  /** how many sub-frames to average for this frame (1 = no motion blur) */
  samples(frame: number) {
    return Math.max(1, Math.round(this.sampleCount(frame)));
  }

  /** Draw the scene at time `frame` (may be fractional). Must depend on nothing but `frame`. */
  renderFrame(frame: number) {
    this.update(frame);
    const s = this.stage;
    if (s.post) {
      let c = this.composers.get(s);
      if (!c) this.composers.set(s, (c = makePipeline(this.renderer, s.scene, s.camera, this.width * this.scale, this.height * this.scale, s.post)));
      applyToneMapping(this.renderer, s.post);
      c.render();
    } else {
      this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
      this.renderer.toneMappingExposure = 1;
      this.renderer.render(s.scene, s.camera);
    }
    this.renderer.getContext().finish();
  }

  /** free a stage that will not be drawn again soon (long videos build one stage per shot; without this the GPU fills up) */
  release(stage: Stage) {
    const c = this.composers.get(stage);
    if (c) { c.dispose(); (c as any).renderTarget1?.dispose(); (c as any).renderTarget2?.dispose(); for (const pass of (c as any).passes ?? []) pass.dispose?.(); this.composers.delete(stage); }
    stage.scene.traverse((o: any) => {
      o.geometry?.dispose?.();
      for (const m of Array.isArray(o.material) ? o.material : o.material ? [o.material] : []) {
        for (const v of Object.values(m)) if (v && (v as any).isTexture) (v as any).dispose();
        for (const u of Object.values(m.uniforms ?? {})) if ((u as any)?.value?.isTexture) (u as any).value.dispose();
        m.dispose?.();
      }
      o.shadow?.dispose?.();
      o.dispose?.();
    });
  }

  dispose() {
    this.composers.forEach((c) => c.dispose());
    this.renderer.dispose();
  }
}

/** Plain daylight rig for the test sheets (real shots use look presets). */
export const dayRig = (scene: THREE.Scene, extent = 14) => {
  scene.background = new THREE.Color("#a9c0de");
  scene.add(new THREE.HemisphereLight("#cfdcf0", "#5a4a58", 1.0));
  const sun = new THREE.DirectionalLight("#fff4e0", 3.0);
  sun.position.set(9, 16, 12);
  sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096);
  Object.assign(sun.shadow.camera, { left: -extent, right: extent, top: extent, bottom: -extent, near: 1, far: 80 });
  sun.shadow.bias = -0.0004;
  sun.shadow.normalBias = 0.02;
  scene.add(sun);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: "#8f8a84", roughness: 0.95 }));
  ground.rotation.x = -Math.PI / 2;
  ground.receiveShadow = true;
  scene.add(ground);
  return sun;
};
