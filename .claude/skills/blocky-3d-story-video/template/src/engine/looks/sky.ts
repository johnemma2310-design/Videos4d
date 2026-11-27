import * as THREE from "three";

export interface SkyParams {
  top: string;
  horizon: string;
  /** elevation (sin of angle, 0..1) at which the gradient reaches the top colour */
  gradientHeight: number;
  /** bright haze band hugging the horizon */
  haze: string;
  hazeHeight: number;
  cloudLight: string;
  cloudDark: string;
  /** 0 = clear, 1 = overcast */
  cloudCover: number;
  cloudScale: number;
  cloudSeed: number;
}

/** Procedural sky dome: vertical gradient + horizon haze + fBm clouds projected on a flat cloud layer. */
export function buildSky(p: SkyParams, radius = 9000): THREE.Mesh {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {
      uTop: { value: new THREE.Color(p.top) },
      uHorizon: { value: new THREE.Color(p.horizon) },
      uHaze: { value: new THREE.Color(p.haze) },
      uCloudLight: { value: new THREE.Color(p.cloudLight) },
      uCloudDark: { value: new THREE.Color(p.cloudDark) },
      uGradientHeight: { value: p.gradientHeight },
      uHazeHeight: { value: p.hazeHeight },
      uCover: { value: p.cloudCover },
      uScale: { value: p.cloudScale },
      uSeed: { value: p.cloudSeed },
    },
    vertexShader: /* glsl */ `
      varying vec3 vDir;
      void main() {
        vDir = position;
        vec4 mv = modelViewMatrix * vec4(position, 0.0);   // rotate only: the dome follows the camera
        gl_Position = projectionMatrix * vec4(mv.xyz, 1.0);
        gl_Position.z = gl_Position.w;                      // push to the far plane
      }`,
    fragmentShader: /* glsl */ `
      varying vec3 vDir;
      uniform vec3 uTop, uHorizon, uHaze, uCloudLight, uCloudDark;
      uniform float uGradientHeight, uHazeHeight, uCover, uScale, uSeed;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float noise(vec2 p) {
        vec2 i = floor(p), f = fract(p);
        vec2 u = f * f * (3.0 - 2.0 * f);
        return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
      }
      float fbm(vec2 p) {
        float a = 0.5, s = 0.0;
        for (int i = 0; i < 6; i++) { s += a * noise(p); p = p * 2.03 + 17.0; a *= 0.5; }
        return s;
      }
      void main() {
        vec3 d = normalize(vDir);
        float h = max(d.y, 0.0);
        vec3 col = mix(uHorizon, uTop, smoothstep(0.0, uGradientHeight, h));
        if (uCover > 0.0) {
          vec2 p = d.xz / (d.y + 0.12) * uScale + uSeed;
          float n = fbm(p);
          float edge = 1.0 - uCover;
          float c = smoothstep(edge - 0.12, edge + 0.18, n) * smoothstep(0.0, 0.05, d.y);
          float shade = smoothstep(0.2, 0.9, fbm(p * 2.3 + 5.0));
          col = mix(col, mix(uCloudDark, uCloudLight, shade), c);
        }
        col = mix(uHaze, col, smoothstep(0.0, uHazeHeight, h));
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 48, 24), mat);
  mesh.frustumCulled = false;
  mesh.renderOrder = -1000;
  return mesh;
}
