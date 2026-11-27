// Turns a story file + word timestamps into the render input for the Final composition.
//   npx tsx scripts/build-video.ts projects/<name>
// Reads   projects/<name>/story.json  (shots with word cues instead of frame counts)
//         projects/<name>/words.json  (from scripts/align.py)
//         projects/<name>/cast.json   (the characters; optional)
// Writes  projects/<name>/final.json  { shots, captions, audio }   -> render input
//         projects/<name>/sounds.json [{ t, type }]                 -> for scripts/mix_audio.py --sounds
//
// Timing rules measured on the reference:
//   - a caption switches on the frame of its word's onset and holds until the next word;
//   - a shot starts on the frame of its cue word's onset (cuts and caption switches share a frame);
//   - the audio stops dead at the end of speech and the picture holds silently for about a second.
// In story.json a shot gives `cue` (index of its first word). Inside a shot, times may be written relative to it:
//   camera key { "u": 0..1 }      -> fraction of the shot's length   (or "f": local frames, also negative for a whip-in)
//   clip       { "word": index }  -> starts on that word            (or "at": local frames)
//   face       { "word": index }  -> swaps on that word             (or "f": local frames)
// Sound:
//   shot  "sound": "hit" | "whoosh"                -> a sound on the shot's first frame
//   story "soundWords": [{ "afterWord": i, "text": "WHOOSH", "sound": "whoosh" }]
//         -> a caption that is shown but not spoken, placed in the pause after word i, with its sound.
//            A shot may start on it with "cueSound": k (index into soundWords) instead of "cue".
import fs from "node:fs";
import path from "node:path";
import { shotsFile } from "../src/schema/shots";

const dir = process.argv[2];
if (!dir) { console.error("usage: npx tsx scripts/build-video.ts projects/<name>"); process.exit(1); }
const story = JSON.parse(fs.readFileSync(path.join(dir, "story.json"), "utf8"));
const { words, speech_end } = JSON.parse(fs.readFileSync(path.join(dir, "words.json"), "utf8")) as { speech_end: number; words: { w: string; t: number; end: number }[] };
const FPS = 30, HOLD = story.endHoldFrames ?? 32; // 1.08 s of silent picture, as on the reference
const SOUNDS = ["hit", "whoosh"];
const checkWord = (i: number) => { if (!Number.isInteger(i) || i < 0 || i >= words.length) throw new Error(`word index ${i} out of range (0..${words.length - 1})`); };
const frameOf = (i: number) => { checkWord(i); return Math.round(words[i].t * FPS); };
const total = Math.round(speech_end * FPS) + HOLD;

const names: string[] = story.names ?? [], caps: string[] = story.sfx ?? [];
const captionText = (spoken: string) => {
  const bare = spoken.replace(/[^\p{L}\p{N}'’-]/gu, "").replace(/’/g, "'"), low = bare.toLowerCase();
  if (caps.some((x) => x.toLowerCase() === low)) return bare.toUpperCase();
  const name = names.find((x) => x.toLowerCase() === low);
  if (name) return name;
  if (low === "i" || low.startsWith("i'")) return "I" + low.slice(1);
  return low;
};
const captions = words.map((w, i) => ({ w: captionText(w.w), f: frameOf(i) })).filter((c) => c.w);
if (captions.length && captions[0].f > 0) captions[0].f = Math.min(captions[0].f, 2); // nothing blank at the start

// caption-only sound words sit in the pause after a spoken word
const sounds: { t: number; type: string; dur?: number; gain?: number }[] = [];
const soundFrames: number[] = (story.soundWords ?? []).map((s: { afterWord: number; text: string; sound?: string }, k: number) => {
  checkWord(s.afterWord);
  const next = s.afterWord + 1 < words.length ? words[s.afterWord + 1].t : speech_end, gap = next - words[s.afterWord].end;
  if (gap < 0.5) console.warn(`soundWords[${k}] "${s.text}": the pause after word ${s.afterWord} is only ${gap.toFixed(2)} s; the reference left about 1 s. Ask the narrator for a longer pause there.`);
  const t = words[s.afterWord].end + Math.min(0.15, Math.max(0, gap * 0.25)), f = Math.round(t * FPS);
  captions.push({ w: s.text.toUpperCase(), f });
  if (s.sound) { if (!SOUNDS.includes(s.sound)) throw new Error(`soundWords[${k}]: unknown sound "${s.sound}". Known: ${SOUNDS.join(", ")}`); sounds.push({ t: f / FPS, type: s.sound }); }
  return f;
});
captions.sort((a, b) => a.f - b.f);

const starts: number[] = story.shots.map((s: { id: string; cue?: number; cueSound?: number }, i: number) => {
  if (i === 0) return 0;
  if (s.cueSound !== undefined) { if (soundFrames[s.cueSound] === undefined) throw new Error(`shot ${s.id}: cueSound ${s.cueSound} is not in soundWords`); return soundFrames[s.cueSound]; }
  if (s.cue === undefined) throw new Error(`shot ${s.id}: needs "cue" (a word index) or "cueSound"`);
  return frameOf(s.cue);
});
starts.forEach((f, i) => { if (i && f <= starts[i - 1]) throw new Error(`shot ${story.shots[i].id}: starts at frame ${f}, not after the previous shot (frame ${starts[i - 1]}). Cues must increase.`); });

const shots = story.shots.map((s: any, i: number) => {
  const start = starts[i], frames = (i + 1 < starts.length ? starts[i + 1] : total) - start;
  if (frames < 3) throw new Error(`shot ${s.id}: only ${frames} frames long`);
  const local = (w: number) => frameOf(w) - start;
  const { cue, cueSound, sound, ...rest } = s;
  if (sound) { if (!SOUNDS.includes(sound)) throw new Error(`shot ${s.id}: unknown sound "${sound}". Known: ${SOUNDS.join(", ")}`); sounds.push({ t: start / FPS, type: sound }); }
  // recorded sounds: "sfx": [{ type, word | at (local frames), dur: seconds | "shot" (a looped background layer), gain: dB, lead: seconds }]
  // lead = start that many seconds BEFORE the named frame (a riser as long as its lead ends exactly on the cut)
  for (const x of (rest.sfx ?? []) as any[]) {
    if (!SOUNDS.includes(x.type) && !fs.existsSync(path.join("sfx", `${x.type}.wav`))) throw new Error(`shot ${s.id}: sound "${x.type}" is not built in and sfx/${x.type}.wav does not exist (run scripts/sfx_fetch.py)`);
    const f0 = Math.max(0, x.word !== undefined ? local(x.word) : (x.at ?? 0));
    const dur = x.dur === "shot" ? (frames - f0) / FPS : x.dur;
    sounds.push({ t: Math.max(0, (start + f0) / FPS - (x.lead ?? 0)), type: x.type, ...(dur ? { dur } : {}), ...(x.gain ? { gain: x.gain } : {}) });
  }
  delete rest.sfx;
  return {
    ...rest, frames,
    actors: (s.actors ?? []).map((a0: any) => {
      const { to, talk, path, ...a } = a0;
      // "talk": true = every word of the shot, or [firstWord, lastWord]; the mouth moves from each word's start to its end
      let talkOut: number[][] | undefined;
      if (talk) {
        const w0 = Array.isArray(talk) ? talk[0] : 0, w1 = Array.isArray(talk) ? talk[1] : words.length - 1;
        talkOut = [];
        for (let w = Math.max(0, w0); w <= Math.min(words.length - 1, w1); w++) {
          const f0 = frameOf(w) - start, f1 = Math.round(words[w].end * FPS) - start;
          if (f1 > 0 && f0 < frames) talkOut.push([Math.max(0, f0), Math.min(frames, Math.max(f0 + 3, f1))]);
        }
      }
      // "to": [x, z] = walk there over the whole shot; "path": [{ u | f | word, pos }] for anything else
      const pathOut = path ? path.map((k: any) => ({ f: k.word !== undefined ? local(k.word) : k.u !== undefined ? Math.round(k.u * (frames - 1)) : k.f, pos: k.pos }))
        : to ? [{ f: 0, pos: a.pos }, { f: frames - 1, pos: to }] : undefined;
      return {
      ...a, ...(talkOut?.length ? { talk: talkOut } : {}), ...(pathOut ? { path: pathOut } : {}),
      clips: a.clips?.map((c: any) => ({ clip: c.clip, at: c.word !== undefined ? local(c.word) : c.at })),
      faces: a.faces?.map((f: any) => ({ v: f.v, f: f.word !== undefined ? local(f.word) : f.f })),
    }; }),
    camera: { ...s.camera, keys: s.camera.keys.map((k: any) => { const { u, ...r } = k; return u !== undefined ? { ...r, f: Math.round(u * (frames - 1)) } : k; }) },
  };
});
const castPath = path.join(dir, "cast.json");
const cast = fs.existsSync(castPath) ? JSON.parse(fs.readFileSync(castPath, "utf8")) : undefined;
const file = shotsFile.parse({ fps: FPS, width: story.width ?? 720, height: story.height ?? 960, shots, cast });
for (const s of file.shots) for (const a of s.actors) if (cast && !cast[a.character]) throw new Error(`shot ${s.id}: character "${a.character}" is not in cast.json (${Object.keys(cast).join(", ")})`);
fs.writeFileSync(path.join(dir, "final.json"), JSON.stringify({ shots: file, captions, audio: story.audio }, null, 1));
sounds.sort((a, b) => a.t - b.t);
fs.writeFileSync(path.join(dir, "sounds.json"), JSON.stringify(sounds, null, 1));
const lens = shots.map((s: any) => s.frames / FPS);
console.log(`${shots.length} shots, ${captions.length} captions, ${sounds.length} sounds, ${total} frames (${(total / FPS).toFixed(2)} s); shot lengths ${lens.map((x: number) => x.toFixed(2)).join(", ")} s; mean ${(lens.reduce((a: number, b: number) => a + b, 0) / lens.length).toFixed(2)} s`);
