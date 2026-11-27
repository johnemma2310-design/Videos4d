// Animation clips as keyframe data (degrees, frames at 30 fps) and a seekable evaluator.
// Conventions: shoulderPitch 0 = arm down, 90 = forward, 180 = up; shoulderRoll 0 = against body, 90 = straight out;
// hipPitch + = leg forward; headYaw + = to the left of the character; headPitch + = down; torsoPitch + = lean forward.
// Timings measured on the reference (reconstruction report D, section 8); rig-space angles are estimates.
import { evalTrack, Key } from "../core/ease";
import { Registry } from "../core/registry";

export type Pose = Record<string, number>;
export type Clip = { loop?: boolean; period?: number; tracks: Record<string, Key[]> };

export const clips = new Registry<Clip>("clip");
const both = (name: string, keys: Key[]) => ({ ["L." + name]: keys, ["R." + name]: keys });

clips.add("rest", { tracks: {} });
clips.add("shrugOut", { tracks: both("shoulderRoll", [{ f: 0, v: 0 }, { f: 2, v: 40, ease: "backOut" }, { f: 3, v: 42 }, { f: 15, v: 35, ease: "settle" }]) });
clips.add("wave", {
  tracks: {
    "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 3, v: 165, ease: "snap" }, { f: 26, v: 165 }, { f: 28, v: 0, ease: "snap" }],
    "R.shoulderRoll": [{ f: 0, v: 0 }, { f: 3, v: 72, ease: "snap" }, { f: 8.75, v: 24, ease: "sine" }, { f: 14.5, v: 72, ease: "sine" }, { f: 20.25, v: 24, ease: "sine" }, { f: 26, v: 72, ease: "sine" }, { f: 28, v: 0, ease: "snap" }],
  },
});
clips.add("handUpQuick", { tracks: { "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 2, v: 120, ease: "snap" }], "R.shoulderRoll": [{ f: 0, v: 0 }, { f: 2, v: 15, ease: "snap" }] } });
clips.add("pointUp", {
  tracks: {
    "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 2, v: 135, ease: "snap" }, { f: 3, v: 145, ease: "backOut" }, { f: 5, v: 140 }, { f: 18, v: 140 }, { f: 20, v: 0, ease: "snap" }],
    "R.shoulderRoll": [{ f: 0, v: 0 }, { f: 3, v: 20, ease: "snap" }, { f: 18, v: 20 }, { f: 20, v: 0, ease: "snap" }],
  },
});
clips.add("armsUp", { tracks: { ...both("shoulderPitch", [{ f: 0, v: 0 }, { f: 2, v: 160, ease: "backOut" }]), ...both("shoulderRoll", [{ f: 0, v: 0 }, { f: 2, v: 20, ease: "snap" }]) } });
clips.add("castForward", { tracks: { "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 7, v: 95, ease: "snap" }, { f: 9, v: 90 }], torsoPitch: [{ f: 0, v: 0 }, { f: 9, v: 0 }, { f: 11, v: -10, ease: "snap" }] } });
clips.add("castUpBoth", { tracks: { ...both("shoulderPitch", [{ f: 0, v: 0 }, { f: 4, v: 150, ease: "snap" }]), ...both("shoulderRoll", [{ f: 0, v: 0 }, { f: 4, v: 25, ease: "snap" }]) } });
clips.add("reachForward", { tracks: { "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 3, v: 62, ease: "snap" }] } }); // arm held forward and down, as in S24
clips.add("presentPlate", { tracks: { "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 14, v: 80, ease: "smooth" }] } });
clips.add("cheerLoop", {
  loop: true, period: 12,
  tracks: {
    "L.shoulderPitch": [{ f: 0, v: 150 }, { f: 6, v: 175, ease: "sine" }, { f: 12, v: 150, ease: "sine" }],
    "R.shoulderPitch": [{ f: 0, v: 175 }, { f: 6, v: 150, ease: "sine" }, { f: 12, v: 175, ease: "sine" }],
    ...both("shoulderRoll", [{ f: 0, v: 20 }]),
    rootY: [{ f: 0, v: 0 }, { f: 3, v: 0.15, ease: "sine" }, { f: 6, v: 0, ease: "sine" }, { f: 9, v: 0.15, ease: "sine" }, { f: 12, v: 0, ease: "sine" }],
  },
});
clips.add("walk", {
  loop: true, period: 20,
  tracks: {
    "L.shoulderPitch": [{ f: 0, v: -30 }, { f: 10, v: 30, ease: "sine" }, { f: 20, v: -30, ease: "sine" }],
    "R.shoulderPitch": [{ f: 0, v: 30 }, { f: 10, v: -30, ease: "sine" }, { f: 20, v: 30, ease: "sine" }],
    "L.hipPitch": [{ f: 0, v: 35 }, { f: 10, v: -35, ease: "sine" }, { f: 20, v: 35, ease: "sine" }],
    "R.hipPitch": [{ f: 0, v: -35 }, { f: 10, v: 35, ease: "sine" }, { f: 20, v: -35, ease: "sine" }],
  },
});
clips.add("runLeaning", {
  loop: true, period: 14,
  tracks: {
    torsoPitch: [{ f: 0, v: 28 }], ...both("shoulderPitch", [{ f: 0, v: -40 }]), headPitch: [{ f: 0, v: -25 }],
    "L.hipPitch": [{ f: 0, v: 55 }, { f: 7, v: -55, ease: "sine" }, { f: 14, v: 55, ease: "sine" }],
    "R.hipPitch": [{ f: 0, v: -55 }, { f: 7, v: 55, ease: "sine" }, { f: 14, v: -55, ease: "sine" }],
  },
});

/** pose of a clip at local frame f (frames since the clip started). Pure and seekable. */
export const evalClip = (id: string, f: number): Pose => {
  const c = clips.get(id);
  const lf = c.loop && c.period ? ((f % c.period) + c.period) % c.period : f;
  const pose: Pose = {};
  for (const [name, keys] of Object.entries(c.tracks)) pose[name] = evalTrack(keys, lf);
  return pose;
};
