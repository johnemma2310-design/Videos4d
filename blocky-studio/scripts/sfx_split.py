"""Splits one long recording of many sound effects into numbered clips at the silences, measures each clip, and writes
a page where the user can play and label them.
usage: python sfx_split.py <recording> <out dir> [--gap 0.25] [--floor -48] [--min 0.04]
  --gap    seconds of quiet that separate two sounds          --floor  level (dBFS) under which it counts as quiet
Writes <out dir>/001.wav ..., clips.json (measurements), labels.csv (for the user to fill in), index.html (players).
The descriptions are from measurement only (length, pitch, brightness, attack): nobody has listened to the clips."""
import sys, os, json, subprocess, wave, html
import numpy as np, imageio_ffmpeg

args = sys.argv[1:]
def opt(name, default):
    if name in args: i = args.index(name); v = float(args[i + 1]); del args[i:i + 2]; return v
    return default
gap, floor, minlen = opt("--gap", 0.25), opt("--floor", -48.0), opt("--min", 0.04)
src, out = args; os.makedirs(out, exist_ok=True)
SR = 48000
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", src, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop = SR // 200                                             # 5 ms
n = len(a) // hop; env = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12); db = 20 * np.log10(env)
loud = db > floor
segs, start, quiet = [], None, 0
for i, l in enumerate(loud):
    if l:
        if start is None: start = i
        quiet = 0
    elif start is not None:
        quiet += 1
        if quiet * 0.005 >= gap: segs.append((start, i - quiet + 1)); start = None
if start is not None: segs.append((start, n))
segs = [(s, e) for s, e in segs if (e - s) * 0.005 >= minlen]
print(f"{len(a) / SR:.1f} s recording, peak {20 * np.log10(np.abs(a).max() + 1e-9):.1f} dBFS -> {len(segs)} sounds")

def describe(c):
    d = len(c) / SR; e = np.sqrt((c[: len(c) // 240 * 240].reshape(-1, 240) ** 2).mean(axis=1) + 1e-12); pk = int(np.argmax(e))
    attack = pk * 0.005; spec = np.abs(np.fft.rfft(c * np.hanning(len(c)))) ** 2; f = np.fft.rfftfreq(len(c), 1 / SR)
    centroid = float((spec * f).sum() / (spec.sum() + 1e-12)); low = float(spec[f < 200].sum() / (spec.sum() + 1e-12))
    flat = float(np.exp(np.log(spec[1:] + 1e-12).mean()) / (spec[1:].mean() + 1e-12))       # 0 = pure tone, toward 1 = noise
    top = float(f[int(np.argmax(spec[1:])) + 1])
    words = ["very short" if d < 0.25 else "short" if d < 0.8 else "medium" if d < 2.5 else "long"]
    words.append("sharp start" if attack < 0.03 else "soft start" if attack > 0.15 else "quick start")
    words.append("low / boomy" if low > 0.5 or centroid < 500 else "bright / hissy" if centroid > 4000 else "mid-range")
    if len(e) > 8 and d > 0.5 and e[-max(2, len(e) // 6):].mean() / e.max() > 0.5: words.append("stays loud to the end")
    return {"seconds": round(d, 2), "attack_s": round(attack, 3), "brightness_hz": round(centroid), "strongest_hz": round(top), "low_share": round(low, 2), "noisiness": round(flat, 3),
            "peak_db": round(float(20 * np.log10(np.abs(c).max() + 1e-9)), 1), "guess": ", ".join(words)}

clips, pad = [], int(0.02 * SR)
for k, (s, e) in enumerate(segs, 1):
    c = a[max(0, s * hop - pad): min(len(a), e * hop + pad)].copy()
    f = min(len(c) // 2, int(0.004 * SR)); c[:f] *= np.linspace(0, 1, f); c[-f:] *= np.linspace(1, 0, f)
    name = f"{k:03d}.wav"
    w = wave.open(os.path.join(out, name), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(c, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    clips.append({"n": k, "file": name, "at": round(s * 0.005, 2), **describe(c)})
json.dump({"source": os.path.basename(src), "clips": clips}, open(os.path.join(out, "clips.json"), "w"), indent=1)
with open(os.path.join(out, "labels.csv"), "w", encoding="utf-8") as fh:
    fh.write("number,use (yes/no),name,what it is,where to use it\n")
    for c in clips: fh.write(f"{c['n']},,,,\n")
rows = "\n".join(f'<tr><td class="n">{c["n"]}</td><td><audio controls preload="none" src="{c["file"]}"></audio></td><td>{c["seconds"]} s</td><td>{html.escape(c["guess"])}</td><td class="at">at {int(c["at"] // 60)}:{c["at"] % 60:05.2f}</td></tr>' for c in clips)
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(f"""<!doctype html><meta charset="utf-8"><title>Sound clips from {html.escape(os.path.basename(src))}</title>
<style>body{{font:15px system-ui,sans-serif;margin:24px;background:#16171a;color:#e8e8ea}}table{{border-collapse:collapse}}td{{padding:6px 12px;border-bottom:1px solid #2c2e34;vertical-align:middle}}
.n{{font-weight:700;font-size:18px;width:40px}}.at{{color:#888}}audio{{height:32px;width:260px}}h1{{font-size:20px}}p{{color:#aaa;max-width:760px}}</style>
<h1>{len(clips)} sounds from {html.escape(os.path.basename(src))}</h1>
<p>Play each one and note its number. The description is a guess from measurement only (length, pitch, attack); nobody has listened to these.</p>
<table>{rows}</table>""")
for c in clips: print(f"  {c['n']:3d}  {c['seconds']:6.2f} s  at {c['at']:7.2f} s  {c['guess']}")
