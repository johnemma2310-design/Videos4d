// One-word captions, to the spec measured on the reference (report: editing, captions and audio):
//   white #FCFCFC fill, 4 px black outline, hard black shadow at (+2, +2) with no blur, x-height 36 px, cap height 44 px,
//   baseline at y = 680 of 960 as measured by the analysis; 682 here after matching glyph boxes on two reference frames, centred, never wraps, hard switch on the word's first frame, never blank
//   once speech has started, holds through pauses. All pixel values scale with the frame height.
// Captions are drawn in the DOM above the 3D canvas, so they are never shaken or motion-blurred.
import React, { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export type Caption = { w: string; f: number }; // text as displayed, first frame

const FONT = "CaptionFont";
// Poppins metrics (units per em 1000): ascender 1050, x-height 548
const EM_PER_XHEIGHT = 1 / 0.548, ASCENT = 1.05;
export const CAPTION_TUNE = { xHeight: 36, baseline: 682, outline: 4, shadow: 2 }; // at 960 px frame height

export const useCaptionFont = () => {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const h = delayRender("caption font");
    const face = new FontFace(FONT, `url(${staticFile("fonts/Poppins-Bold.ttf")})`);
    face.load().then((f) => {
      (document.fonts as unknown as { add: (f: FontFace) => void }).add(f);
      setReady(true);
      continueRender(h);
    });
  }, []);
  return ready;
};

export const Captions: React.FC<{ captions: Caption[] }> = ({ captions }) => {
  const frame = useCurrentFrame();
  const { height, width } = useVideoConfig();
  const ready = useCaptionFont();
  let word: string | null = null;
  for (const c of captions) if (c.f <= frame) word = c.w; else break;
  if (!ready || word === null) return null;
  const k = height / 960, size = CAPTION_TUNE.xHeight * EM_PER_XHEIGHT * k;
  const base: React.CSSProperties = {
    position: "absolute", left: 0, width, textAlign: "center", whiteSpace: "nowrap",
    top: CAPTION_TUNE.baseline * k - ASCENT * size, fontFamily: FONT, fontSize: size, lineHeight: 1.4, fontWeight: 700,
    WebkitTextStroke: `${CAPTION_TUNE.outline * 2 * k}px #000`, paintOrder: "stroke fill", letterSpacing: 0,
  };
  const s = CAPTION_TUNE.shadow * k;
  return (
    <>
      <div style={{ ...base, color: "#000", transform: `translate(${s}px, ${s}px)` }}>{word}</div>
      <div style={{ ...base, color: "#FCFCFC" }}>{word}</div>
    </>
  );
};

/** Caption text rules measured on the reference: lowercase (also at sentence starts), no punctuation except
 *  apostrophes, capitals only for "I" and listed names, sound-effect words in ALL CAPS. */
export const captionText = (spoken: string, names: string[] = [], sfx: string[] = []) => {
  const bare = spoken.replace(/[^\p{L}\p{N}'’-]/gu, "").replace(/’/g, "'");
  const low = bare.toLowerCase();
  if (sfx.some((x) => x.toLowerCase() === low)) return bare.toUpperCase();
  const name = names.find((x) => x.toLowerCase() === low);
  if (name) return name;
  if (low === "i" || low.startsWith("i'")) return "I" + low.slice(1);
  return low;
};
