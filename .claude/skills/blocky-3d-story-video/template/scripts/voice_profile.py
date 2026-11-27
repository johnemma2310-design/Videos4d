"""Measures the narrator's pitch and pace in a video or recording (to describe a voice, not to copy one).
usage: python voice_profile.py <video or wav> <words.json: {"words":[{"w","t","end"}]} or a list>"""
import sys, json, subprocess
import numpy as np, imageio_ffmpeg

src, wj = sys.argv[1:3]
d = json.load(open(wj, encoding="utf-8")); words = d["words"] if isinstance(d, dict) else d
key = lambda w, a, b: w.get(a, w.get(b))
sr = 16000
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
win, hop = 640, 160   # 40 ms, 10 ms
f0s, per_word = [], []
for w in words:
    t0, t1 = key(w, "t", "start"), key(w, "end", "e")
    if t0 is None or t1 is None: continue
    vals = []
    for s in range(int(t0 * sr), int(t1 * sr) - win, hop):
        x = a[s:s + win] * np.hanning(win); x = x - x.mean()
        if np.sqrt((x ** 2).mean()) < 0.02: continue
        ac = np.correlate(x, x, "full")[win - 1:]; ac /= ac[0] + 1e-9
        lo, hi = sr // 450, sr // 70
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.55: vals.append(sr / k)
    if vals: per_word.append((w.get("w", w.get("word", "")), float(np.median(vals)))); f0s += vals
f = np.array(f0s)
print(f"voiced frames: {len(f)}")
print(f"pitch median {np.median(f):.0f} Hz; middle 80 % {np.percentile(f, 10):.0f} to {np.percentile(f, 90):.0f} Hz; range {12 * np.log2(np.percentile(f, 90) / np.percentile(f, 10)):.1f} semitones")
hist, edges = np.histogram(f, bins=[70, 100, 130, 160, 190, 220, 250, 280, 310, 350, 450])
for h, e0, e1 in zip(hist, edges[:-1], edges[1:]): print(f"  {e0:3.0f}-{e1:3.0f} Hz {h / len(f) * 100:5.1f} % {'#' * int(h / len(f) * 60)}")
pw = np.array([p for _, p in per_word])
n = len(pw) // 3
print(f"per-word pitch: first third {np.median(pw[:n]):.0f} Hz, middle {np.median(pw[n:2 * n]):.0f}, last third {np.median(pw[2 * n:]):.0f}")
hi = sorted(per_word, key=lambda x: -x[1])[:10]; print("highest-pitched words:", ", ".join(f"{w} {p:.0f}" for w, p in hi))
durs = [key(w, "end", "e") - key(w, "t", "start") for w in words if key(w, "end", "e")]
t0, t1 = key(words[0], "t", "start"), key(words[-1], "end", "e")
gaps = [key(words[i + 1], "t", "start") - key(words[i], "end", "e") for i in range(len(words) - 1)]
print(f"pace {len(words) / (t1 - t0) * 60:.0f} words/min overall; {len(words) / sum(durs) * 60:.0f} words/min while speaking; pauses over 0.15 s: {sum(1 for g in gaps if g > 0.15)}, median {np.median([g for g in gaps if g > 0.15]):.2f} s, longest {max(gaps):.2f} s")
