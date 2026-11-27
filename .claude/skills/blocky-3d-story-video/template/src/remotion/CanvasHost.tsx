// Hosts the engine inside a Remotion composition.
//   - a hidden GL canvas (supersampled) that the engine draws into;
//   - a visible 2D canvas at output size that receives the result.
// Motion blur: the engine is drawn at N sub-frame times and the 2D canvas keeps their running average, which gives
// the stepped multi-sample smear measured on the reference. Supersampling: the 2D copy downsamples the GL canvas.
import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, useCurrentFrame, useVideoConfig } from "remotion";
import { Engine } from "../engine/Engine";
import "../engine/programs";

export const CanvasHost: React.FC<{ program: string; props?: Record<string, unknown>; scale?: number }> = ({ program, props, scale = 2 }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const glCanvas = useRef<HTMLCanvasElement | null>(null);
  const out = useRef<HTMLCanvasElement>(null);
  const engine = useRef<Engine | null>(null);
  const [info, setInfo] = useState("");

  useEffect(() => {
    const c = document.createElement("canvas");
    glCanvas.current = c;
    const e = new Engine(c, width, height, program, props ?? {}, scale);
    engine.current = e;
    const s = `GL renderer: ${e.info.renderer} | webgl2: ${e.info.webgl2}`;
    console.log("[engine] " + s);
    if (/swiftshader|llvmpipe|software/i.test(e.info.renderer)) console.error("[engine] SOFTWARE RENDERER in use");
    setInfo(s);
    return () => { e.dispose(); engine.current = null; };
  }, [width, height, program, scale]);

  useLayoutEffect(() => {
    const e = engine.current, g = out.current?.getContext("2d");
    if (!e || !g || !glCanvas.current) return;
    const h = delayRender(`frame ${frame}`);
    const n = e.samples(frame);
    g.imageSmoothingEnabled = true;
    g.imageSmoothingQuality = "high";
    for (let j = 0; j < n; j++) {
      // exposure covers the interval that ends at this frame: (frame - 1, frame]
      e.renderFrame(n === 1 ? frame : frame - 1 + (j + 1) / n);
      g.globalAlpha = 1 / (j + 1); // running average of the samples
      g.drawImage(glCanvas.current, 0, 0, width, height);
    }
    g.globalAlpha = 1;
    continueRender(h);
  }, [frame, info]);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <canvas ref={out} width={width} height={height} style={{ width, height }} data-gl={info} />
    </AbsoluteFill>
  );
};
