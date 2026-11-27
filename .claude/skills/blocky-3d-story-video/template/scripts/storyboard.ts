// Storyboard + beat table for a project, before the full render.
//   npx tsx scripts/storyboard.ts projects/<name>
// Reads   projects/<name>/final.json (from build-video.ts) and words.json
// Writes  projects/<name>/storyboard.json   render input: ONE frame per shot (its middle frame, captions included)
//         projects/<name>/board_labels.json what each storyboard frame shows
//         projects/<name>/beats.md          the beat table: time, words, set, look, who does what, camera, sound
// Then:   npx remotion render src/index.ts Final out/<name>_board --props=projects/<name>/storyboard.json --sequence --image-format=jpeg --gl=angle
//         python scripts/board_sheet.py projects/<name> out/<name>_board out/<name>_storyboard.jpg
import fs from "node:fs";
import path from "node:path";

const dir = process.argv[2];
if (!dir) { console.error("usage: npx tsx scripts/storyboard.ts projects/<name>"); process.exit(1); }
const fin = JSON.parse(fs.readFileSync(path.join(dir, "final.json"), "utf8"));
const { words } = JSON.parse(fs.readFileSync(path.join(dir, "words.json"), "utf8")) as { words: { w: string; t: number }[] };
const sounds: { t: number; type: string }[] = fs.existsSync(path.join(dir, "sounds.json")) ? JSON.parse(fs.readFileSync(path.join(dir, "sounds.json"), "utf8")) : [];
const FPS = 30, shots: any[] = fin.shots.shots;

let start = 0;
const rows: string[] = [], labels: any[] = [], boardShots: any[] = [], boardCaps: any[] = [];
const dist = (a: number[], b: number[]) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
const describeCamera = (s: any) => {
  const k = s.camera.keys, a = k[0], z = k[k.length - 1];
  const d0 = dist(a.pos, a.target), d1 = dist(z.pos, z.target), turn = dist(a.target, z.target);
  const size = Math.min(d0, d1) < 8 ? "close-up" : Math.min(d0, d1) < 16 ? "medium" : Math.min(d0, d1) < 40 ? "wide" : "very wide";
  const parts = [size];
  if (a.f < 0) parts.push("whip-in");
  if (d1 < d0 * 0.97) parts.push(`push-in ${Math.round((1 - d1 / d0) * 100)} %`); else if (d1 > d0 * 1.2) parts.push(`pull-back x${(d1 / d0).toFixed(1)}`);
  if (turn > 4 && a.f >= 0) parts.push("pan/whip");
  if (z.pos[1] - a.pos[1] > 3) parts.push("rising");
  if (s.camera.shake?.length) parts.push("shake");
  return parts.join(", ");
};
shots.forEach((s, i) => {
  const end = start + s.frames, mid = Math.floor(s.frames / 2);
  const line = words.filter((w) => { const f = Math.round(w.t * FPS); return f >= start && f < end; }).map((w) => w.w).join(" ");
  const who = (s.actors ?? []).map((a: any) => {
    const faces = (a.faces ?? []).map((f: any) => f.v).join(" → "), clips = (a.clips ?? []).map((c: any) => c.clip).join(", ");
    return `${a.character}${faces ? ` [${faces}]` : ""}${clips ? ` (${clips})` : ""}`;
  }).join("; ") || "—";
  const extras = [...(s.crowds ?? []).map((c: any) => `${c.count} ${c.palette} crowd`), ...(s.vfx ?? []).map((v: any) => v.type)].join(", ");
  const snd = sounds.filter((x) => Math.round(x.t * FPS) === start).map((x) => x.type).join(", ");
  rows.push(`| ${i + 1} | ${(start / FPS).toFixed(2)} | ${(s.frames / FPS).toFixed(2)} | ${line || "(silent)"} | ${s.set} | ${s.look} | ${who} | ${extras || "—"} | ${describeCamera(s)} | ${snd || "—"} |`);
  // the storyboard frame: this shot reduced to one frame, showing its middle
  const { frames, ...rest } = s;
  boardShots.push({ ...rest, frames: 1, startAt: mid, motionBlur: "off" });
  let cap = "";
  for (const c of fin.captions) if (c.f <= start + mid) cap = c.w; else break;
  boardCaps.push({ w: cap, f: i });
  labels.push({ n: i + 1, id: s.id, t: +(start / FPS).toFixed(2), dur: +(s.frames / FPS).toFixed(2), line, look: s.look, set: s.set, camera: describeCamera(s) });
  start = end;
});
const lens = shots.map((s) => s.frames / FPS), mean = lens.reduce((a, b) => a + b, 0) / lens.length, sorted = [...lens].sort((a, b) => a - b);
const md = [
  `# Beat table — ${path.basename(dir)}`, "",
  `${shots.length} shots, ${(start / FPS).toFixed(2)} s, ${words.length} words. Shot length: mean ${mean.toFixed(2)} s, median ${sorted[Math.floor(sorted.length / 2)].toFixed(2)} s, ` +
  `range ${sorted[0].toFixed(2)}–${sorted[sorted.length - 1].toFixed(2)} s; ${(((shots.length - 1) / (start / FPS)) * 60).toFixed(0)} cuts per minute. (Target: mean 1.65 s, median 1.43 s, about 35 cuts per minute.)`, "",
  "| # | Start (s) | Length (s) | Words | Set | Look | Who (faces) (gestures) | Crowd / effects | Camera | Sound |", "|---|---|---|---|---|---|---|---|---|---|", ...rows, "",
].join("\n");
fs.writeFileSync(path.join(dir, "beats.md"), md);
fs.writeFileSync(path.join(dir, "board_labels.json"), JSON.stringify(labels, null, 1));
fs.writeFileSync(path.join(dir, "storyboard.json"), JSON.stringify({ shots: { ...fin.shots, shots: boardShots }, captions: boardCaps }));
console.log(`${shots.length} storyboard frames -> ${path.join(dir, "storyboard.json")}; beat table -> ${path.join(dir, "beats.md")}`);
