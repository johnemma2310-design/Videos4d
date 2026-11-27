// Look presets: sky + fog + light rig + post chain. One look per shot. Values are tuned by the comparison loop.
import * as THREE from "three";
import { Registry } from "../core/registry";
import type { PostParams } from "../post/pipeline";
import { buildSky, type SkyParams } from "./sky";

export type LookPreset = {
  sky: SkyParams;
  fog: { color: string; density: number };
  lights: {
    hemi: { sky: string; ground: string; intensity: number };
    /** direction the key light comes FROM */
    key: { color: string; intensity: number; from: [number, number, number]; shadow?: boolean };
  };
  post: PostParams;
};
export const looks = new Registry<LookPreset>("look");

/** DAY_COOL as calibrated on reference frame f00490 (overcast-cool variant: soft key, strong sky fill). */
looks.add("DAY_COOL", {
  sky: { top: "#cfdef7", horizon: "#c2d2ec", gradientHeight: 0.35, haze: "#c2d2ec", hazeHeight: 0.02, cloudLight: "#ffffff", cloudDark: "#c0c8d8", cloudCover: 0, cloudScale: 1, cloudSeed: 0 },
  fog: { color: "#c0cae4", density: 0.0045 },
  lights: { hemi: { sky: "#f1eef6", ground: "#9a959e", intensity: 1.42 }, key: { color: "#ffffff", intensity: 0.86, from: [-0.3, 1, 0.8], shadow: true } },
  post: { toneMapping: "none", exposure: 1, bloom: { strength: 0.25, radius: 0.6, threshold: 0.9 }, grade: { saturation: 1, contrast: 1, lift: [0, 0, 0], gain: [1, 1, 1], gamma: 1, vignette: 0 } },
});

/** NIGHT_EMBER as calibrated on reference frame f01779 (62.5 composite): warm key from the camera side, maroon sky, no tone curve. */
looks.add("NIGHT_EMBER", {"sky": {"top": "#241312", "horizon": "#6a372c", "gradientHeight": 0.5, "haze": "#70392c", "hazeHeight": 0.03, "cloudLight": "#6a372c", "cloudDark": "#2a1614", "cloudCover": 0.2, "cloudScale": 1, "cloudSeed": 3}, "fog": {"color": "#5a2a1e", "density": 0.004}, "lights": {"hemi": {"sky": "#8a5a50", "ground": "#2a1410", "intensity": 1.1}, "key": {"color": "#ffc49a", "intensity": 3.3, "from": [-0.35, 0.6, 0.8], "shadow": true}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.6, "radius": 0.85, "threshold": 0.9}, "ao": {"radius": 1.5, "intensity": 1}, "grade": {"saturation": 1.05, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.05, 0.97, 0.9], "gamma": 1, "vignette": 0}}});

/** DAY_SUN: hard-sun daylight as calibrated on the aerial reference frame f00050 (strong key, very thin haze). */
looks.add("DAY_SUN", {"sky": {"top": "#9a9db4", "horizon": "#a7afc9", "gradientHeight": 0.25, "haze": "#d5dff1", "hazeHeight": 0.035, "cloudLight": "#c4c8d6", "cloudDark": "#8c8fa6", "cloudCover": 0.55, "cloudScale": 1.2, "cloudSeed": 3}, "fog": {"color": "#c5cee0", "density": 8e-05}, "lights": {"hemi": {"sky": "#dfe6ff", "ground": "#9a948c", "intensity": 0.9}, "key": {"color": "#fff4e6", "intensity": 3, "from": [-0.8, 0.75, 0.35], "shadow": true}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.15, "radius": 0.6, "threshold": 0.95}, "grade": {"saturation": 1, "contrast": 1, "lift": [0, 0, 0], "gain": [1, 1, 1], "gamma": 1, "vignette": 0}}});

/** Starting values taken from the measured look data (reconstruction/data/lighting/looks.json). NOT yet calibrated
 *  against a reference frame: the two looks that were calibrated both needed large corrections from such values. */
looks.add("RAIN_OVERCAST", {"sky": {"top": "#868fa0", "horizon": "#9aa1b3", "gradientHeight": 0.5, "haze": "#9aa1b3", "hazeHeight": 0.03, "cloudLight": "#ffffff", "cloudDark": "#9aa1b3", "cloudCover": 0.0, "cloudScale": 1, "cloudSeed": 2}, "fog": {"color": "#8a93a4", "density": 0.02}, "lights": {"hemi": {"sky": "#aab4c6", "ground": "#70757f", "intensity": 1.6}, "key": {"color": "#dfe6f2", "intensity": 0.6, "from": [0.2, 1, 0.5], "shadow": false}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.1, "radius": 0.5, "threshold": 1.0}, "ao": {"radius": 1.0, "intensity": 0.8}, "grade": {"saturation": 0.85, "contrast": 0.8, "lift": [0, 0, 0], "gain": [1, 1, 1], "gamma": 1, "vignette": 0}}});
looks.add("FIRE_WARM", {"sky": {"top": "#e8a590", "horizon": "#f2c8a8", "gradientHeight": 0.5, "haze": "#f2c8a8", "hazeHeight": 0.03, "cloudLight": "#ffffff", "cloudDark": "#f2c8a8", "cloudCover": 0.2, "cloudScale": 1, "cloudSeed": 2}, "fog": {"color": "#c98a78", "density": 0.004}, "lights": {"hemi": {"sky": "#e8a590", "ground": "#5a2a26", "intensity": 0.55}, "key": {"color": "#ffd9b8", "intensity": 1.7, "from": [0.4, 0.77, 0.5], "shadow": true}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.45, "radius": 0.7, "threshold": 0.9}, "ao": {"radius": 1.5, "intensity": 1}, "grade": {"saturation": 1.15, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.12, 1.0, 0.88], "gamma": 1, "vignette": 0}}});
looks.add("PEACH_HIGHKEY", {"sky": {"top": "#f4c2a2", "horizon": "#fdeedd", "gradientHeight": 0.5, "haze": "#fdeedd", "hazeHeight": 0.03, "cloudLight": "#ffffff", "cloudDark": "#fbe2c5", "cloudCover": 0.15, "cloudScale": 1, "cloudSeed": 2}, "fog": {"color": "#f8dcc8", "density": 0.003}, "lights": {"hemi": {"sky": "#fff2e6", "ground": "#b89a8c", "intensity": 2.2}, "key": {"color": "#ffe2c4", "intensity": 3.0, "from": [-0.6, 0.5, 0.5], "shadow": true}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.4, "radius": 0.9, "threshold": 0.92}, "ao": {"radius": 1.5, "intensity": 1}, "grade": {"saturation": 0.92, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.04, 1.0, 0.95], "gamma": 1, "vignette": 0}}});
looks.add("DUSK_MAGENTA", {"sky": {"top": "#b784a3", "horizon": "#cd91aa", "gradientHeight": 0.5, "haze": "#cd91aa", "hazeHeight": 0.03, "cloudLight": "#ffffff", "cloudDark": "#cd91aa", "cloudCover": 0.15, "cloudScale": 1, "cloudSeed": 2}, "fog": {"color": "#b88aa2", "density": 0.003}, "lights": {"hemi": {"sky": "#b98aa8", "ground": "#3a1c22", "intensity": 0.8}, "key": {"color": "#ffb49a", "intensity": 1.2, "from": [0.6, 0.21, 0.6], "shadow": true}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.3, "radius": 0.6, "threshold": 1.0}, "ao": {"radius": 1.5, "intensity": 1}, "grade": {"saturation": 1.1, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.0, 0.95, 0.98], "gamma": 1, "vignette": 0}}});
looks.add("INTERIOR_NEUTRAL", {"sky": {"top": "#cfd9e6", "horizon": "#e6ecf2", "gradientHeight": 0.5, "haze": "#e6ecf2", "hazeHeight": 0.03, "cloudLight": "#ffffff", "cloudDark": "#e6ecf2", "cloudCover": 0.0, "cloudScale": 1, "cloudSeed": 2}, "fog": {"color": "#d8d0c8", "density": 0.0005}, "lights": {"hemi": {"sky": "#cfc6bc", "ground": "#6b5a4c", "intensity": 0.9}, "key": {"color": "#fff0dc", "intensity": 2.5, "from": [-0.8, 0.64, 0.25], "shadow": true}}, "post": {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.25, "radius": 0.6, "threshold": 1.0}, "ao": {"radius": 1.2, "intensity": 1.2}, "grade": {"saturation": 1.0, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.05, 1.0, 0.92], "gamma": 1, "vignette": 0}}});

/** add sky, fog and lights to a scene. The shadow box is fitted once around `focus` (never per frame). */
export const applyLook = (scene: THREE.Scene, look: LookPreset, focus = new THREE.Vector3(0, 2, 0), shadowExtent = 14) => {
  scene.add(buildSky(look.sky));
  scene.fog = new THREE.FogExp2(look.fog.color, look.fog.density);
  const l = look.lights;
  scene.add(new THREE.HemisphereLight(l.hemi.sky, l.hemi.ground, l.hemi.intensity));
  const key = new THREE.DirectionalLight(l.key.color, l.key.intensity);
  key.position.copy(focus).addScaledVector(new THREE.Vector3(...l.key.from).normalize(), shadowExtent * 3);
  key.target.position.copy(focus);
  if (l.key.shadow !== false) {
    key.castShadow = true;
    key.shadow.mapSize.set(4096, 4096);
    Object.assign(key.shadow.camera, { left: -shadowExtent, right: shadowExtent, top: shadowExtent, bottom: -shadowExtent, near: 1, far: shadowExtent * 6 });
    key.shadow.bias = -0.0005;
    key.shadow.normalBias = shadowExtent * 0.002;
    key.shadow.radius = 4;
  }
  scene.add(key, key.target);
  return key;
};

/** soft dark blob under a character: the reference shows ground at luma ~9 directly under the feet */
export const contactShadow = (size = 3.2, opacity = 0.75) => {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const grd = g.createRadialGradient(64, 64, 4, 64, 64, 64);
  grd.addColorStop(0, `rgba(0,0,0,${opacity})`);
  grd.addColorStop(0.55, `rgba(0,0,0,${opacity * 0.45})`);
  grd.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 128, 128);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size * 0.62), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2;
  m.position.y = 0.02;
  m.renderOrder = 1;
  return m;
};
