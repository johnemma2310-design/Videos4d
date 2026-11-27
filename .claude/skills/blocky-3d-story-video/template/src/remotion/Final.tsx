// The finished video: 3D reel + captions + audio. Layer order as measured: render (with shake and motion blur) →
// captions on top → encode. The audio is one pre-mixed file (voice + music bed), which stops dead where the mix ends.
import React from "react";
import { AbsoluteFill, Audio, staticFile } from "remotion";
import { CanvasHost } from "./CanvasHost";
import { Captions, type Caption } from "./Captions";

export type FinalProps = { shots: Record<string, unknown>; captions: Caption[]; audio?: string; scale?: number };

export const Final: React.FC<FinalProps> = ({ shots, captions, audio, scale }) => (
  <AbsoluteFill style={{ background: "#000" }}>
    <CanvasHost program="reel" props={shots} scale={scale} />
    <Captions captions={captions} />
    {audio ? <Audio src={staticFile(audio)} /> : null}
  </AbsoluteFill>
);

/** a single caption over a plain frame or a still: used to check the caption style against the reference */
export const CaptionTest: React.FC<{ word: string; background?: string }> = ({ word, background }) => (
  <AbsoluteFill style={{ background: "#5a5560" }}>
    {background ? <img src={staticFile(background)} style={{ position: "absolute", width: "100%", height: "100%" }} /> : null}
    <Captions captions={[{ w: word, f: 0 }]} />
  </AbsoluteFill>
);
