import React from "react";
import { Composition } from "remotion";
import { CanvasHost } from "./remotion/CanvasHost";
import { Final, type FinalProps } from "./remotion/Final";

const frames = (file: { shots: { frames: number }[] }) => file.shots.reduce((n, s) => n + s.frames, 0);
// placeholder so the composition has something to show in the studio; real videos always pass --props
const SAMPLE = {
  shots: { fps: 30, width: 720, height: 960, shots: [{ id: "sample", frames: 30, set: "fireStreet", look: "DAY_SUN", actors: [{ character: "pip", pos: [0, 0] }], camera: { keys: [{ f: 0, pos: [0, 4, 12], target: [0, 3.6, 0] }] } }] },
  captions: [{ w: "sample", f: 0 }],
} as unknown as FinalProps;
const SHEETS: [string, string, number, number, number][] = [
  // id, program, frames, width, height
  ["CastSheet", "sheet.cast", 30, 1280, 720],
  ["FaceSheet", "sheet.faces", 1, 1280, 960],
  ["ClipSheet", "sheet.clips", 40, 1280, 720],
];

export const Root: React.FC = () => (
  <>
    {/* The finished video. Always render with --props=projects/<name>/final.json (written by scripts/build-video.ts). */}
    <Composition
      id="Final" component={Final} fps={30} width={720} height={960} durationInFrames={30} defaultProps={SAMPLE}
      calculateMetadata={({ props }) => {
        const s = props.shots as unknown as { shots: { frames: number }[]; width?: number; height?: number };
        return { durationInFrames: frames(s), width: s.width ?? 720, height: s.height ?? 960 };
      }}
    />
    {/* Preview sheets. --props=projects/<name>/sheet.json (from scripts/sheet-props.ts) shows your own cast. */}
    {SHEETS.map(([id, program, n, w, h]) => (
      <Composition key={id} id={id} component={CanvasHost} durationInFrames={n} fps={30} width={w} height={h} defaultProps={{ program }} />
    ))}
  </>
);
