// The blocky avatar: six rigid parts, measured on the reference (reconstruction report B, section 1).
// Units are studs. Feet at y = 0, facing +Z. "L" = the left of the character = +X.
//   legs 1x2x1 (y 0..2), torso 2x2x1 (y 2..4), arms 1x2x1 hanging from the torso top corners,
//   head = rounded cylinder r 0.6, 1.2 tall, sitting on the torso with no neck. Box edges are hard (no bevel).
import * as THREE from "three";
import type { CharacterDef } from "../../schema/cast";
import type { Pose } from "../anim/clips";
import { faceKey, type FaceOpts } from "./faces";
import { buildHair } from "./hair";
import { armSide, headTexture, legSide, torsoFront, torsoSide } from "./outfits";

const HEAD_PROFILE: [number, number][] = [[0, 0], [0.36, 0], [0.52, 0.06], [0.59, 0.18], [0.6, 0.3], [0.6, 0.92], [0.57, 1.06], [0.48, 1.16], [0.32, 1.2], [0, 1.2]];
let HEAD: THREE.BufferGeometry | null = null;
export const headGeometry = () => {
  if (HEAD) return HEAD;
  // phiStart = -PI puts u = 0.5 at the front (+Z); v is remapped to be linear in height
  HEAD = new THREE.LatheGeometry(HEAD_PROFILE.map(([r, y]) => new THREE.Vector2(r, y)), 40, -Math.PI, Math.PI * 2);
  const pos = HEAD.getAttribute("position"), uv = HEAD.getAttribute("uv");
  for (let i = 0; i < uv.count; i++) uv.setY(i, pos.getY(i) / 1.2);
  HEAD.computeVertexNormals();
  return HEAD;
};
const LIMB = new THREE.BoxGeometry(1, 2, 1);
const LEG = new THREE.BoxGeometry(0.975, 2, 1); // the two legs touch; a hairline gap reads as the seam
const TORSO = new THREE.BoxGeometry(2, 2, 1);
const ROUGH = 0.85; // avatars are matte: no visible specular in the reference
const mat = (o: THREE.MeshStandardMaterialParameters) => new THREE.MeshStandardMaterial({ roughness: ROUGH, metalness: 0, ...o });
const d2r = Math.PI / 180;

export class Avatar {
  readonly root = new THREE.Group(); // place and yaw this
  private lean = new THREE.Group(); // torsoPitch + rootY
  private head = new THREE.Group();
  private shoulder: Record<"L" | "R", THREE.Group> = { L: new THREE.Group(), R: new THREE.Group() };
  private hip: Record<"L" | "R", THREE.Group> = { L: new THREE.Group(), R: new THREE.Group() };
  private headMat: THREE.MeshStandardMaterial;
  private expression = "";

  constructor(readonly def: CharacterDef, expression = "neutralTalk") {
    const { skin, outfit } = def;
    this.root.add(this.lean);
    const shadow = (m: THREE.Mesh) => { m.castShadow = true; m.receiveShadow = true; return m; };

    // torso material order: +x, -x, +y, -y, +z (front), -z
    const side = mat({ map: torsoSide(outfit.torso) }), top = mat({ color: outfit.torso.color });
    const torso = shadow(new THREE.Mesh(TORSO, [side, side, top, top, mat({ map: torsoFront(outfit.torso) }), side]));
    torso.position.y = 3;
    this.lean.add(torso);

    const armM = mat({ map: armSide(outfit, skin) }), armTop = mat({ color: outfit.sleeves?.color ?? outfit.torso.color }), hand = mat({ color: skin });
    const legM = mat({ map: legSide(outfit, skin) }), legTop = mat({ color: outfit.legs.color }), sole = mat({ color: outfit.legs.shoes ?? "#0c0a0e" });
    for (const s of ["L", "R"] as const) {
      const sx = s === "L" ? 1 : -1;
      // shoulder pivot at the top corner of the torso; the arm box hangs outside it
      this.shoulder[s].position.set(sx * 1, 4, 0);
      this.shoulder[s].rotation.order = "ZXY";
      const arm = shadow(new THREE.Mesh(LIMB, [armM, armM, armTop, hand, armM, armM]));
      arm.position.set(sx * 0.5, -1, 0);
      this.shoulder[s].add(arm);
      this.lean.add(this.shoulder[s]);
      this.hip[s].position.set(sx * 0.5, 2, 0);
      const leg = shadow(new THREE.Mesh(LEG, [legM, legM, legTop, sole, legM, legM]));
      leg.position.y = -1;
      this.hip[s].add(leg);
      this.lean.add(this.hip[s]);
    }

    this.head.position.set(0, 3.96, 0);
    this.headMat = mat({ roughness: 0.7 });
    this.head.add(shadow(new THREE.Mesh(headGeometry(), this.headMat)));
    this.head.add(buildHair(def.hair.style, def.hair.color));
    this.lean.add(this.head);
    this.setExpression(expression);
  }

  /** hide everything but the head (used by the expression sheet) */
  showOnlyHead() {
    for (const c of this.lean.children) c.visible = c === this.head;
  }

  /** swap the whole face decal (instant, as in the reference) */
  setExpression(name: string, opts?: FaceOpts) {
    const key = faceKey(name, opts);
    if (key === this.expression) return;
    this.expression = key;
    this.headMat.map = headTexture(this.def.skin, name, opts);
    this.headMat.needsUpdate = true;
  }

  /** apply a pose (degrees). Missing channels are 0 = rest. */
  setPose(p: Pose) {
    const v = (k: string) => p[k] ?? 0;
    for (const s of ["L", "R"] as const) {
      const sx = s === "L" ? 1 : -1;
      const pitch = v(`${s}.shoulderPitch`), roll = v(`${s}.shoulderRoll`);
      // roll always opens the arm outward, whether it hangs down or points up
      this.shoulder[s].rotation.set(-pitch * d2r, 0, sx * roll * d2r * (Math.cos(pitch * d2r) >= 0 ? 1 : -1));
      this.hip[s].rotation.set(-v(`${s}.hipPitch`) * d2r, 0, 0);
    }
    this.head.rotation.set(v("headPitch") * d2r, v("headYaw") * d2r, v("headRoll") * d2r, "YXZ");
    this.lean.rotation.x = v("torsoPitch") * d2r;
    this.lean.position.y = v("rootY");
  }

  /** attachment point at the end of an arm (for held props and hand VFX) */
  handAnchor(s: "L" | "R") {
    const a = new THREE.Object3D();
    a.position.set((s === "L" ? 1 : -1) * 0.5, -2, 0);
    this.shoulder[s].add(a);
    return a;
  }
}
