"""Shortens the pauses in a voice-over without touching speech.
usage: python tighten_pauses.py <in.wav> <words.json> <out.wav> [--target 0.36]
For every gap between words it finds the truly silent stretch (by level), and removes part of it from the middle so
the typical pause matches the target. At least 70 ms of silence is kept on each side of a cut, and cuts are
cross-faded over 8 ms. Run align.py again on the result."""
import sys, json, subprocess, wave
import numpy as np, imageio_ffmpeg

args = sys.argv[1:]; target = 0.36
if "--target" in args: i = args.index("--target"); target = float(args[i + 1]); del args[i:i + 2]
src, wj, out = args
sr = 48000
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
words = json.load(open(wj, encoding="utf-8"))["words"]
gaps = [(words[i]["end"], words[i + 1]["t"]) for i in range(len(words) - 1)]
med = float(np.median([b - c for c, b in gaps if b - c >= 0.15]))
scale = min(1.0, target / med)
hop = sr // 200   # 5 ms
n = len(a) // hop; db = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(axis=1)) + 1e-9)
quiet = db < -50
cuts, margin, fade = [], int(0.07 * sr), int(0.008 * sr)
for end, start in gaps:
    if start - end < 0.15: continue
    lo, hi = max(0, int((end - 0.15) * 200)), min(n, int((start + 0.15) * 200))
    best, run = (0, 0), None           # longest silent run around the gap
    for k in range(lo, hi + 1):
        q = k < hi and quiet[k]
        if q and run is None: run = k
        if not q and run is not None:
            if k - run > best[1] - best[0]: best = (run, k)
            run = None
    s0, s1 = best[0] * hop, best[1] * hop; sil = (s1 - s0) / sr
    remove = min(sil * (1 - scale), sil - 2 * margin / sr)
    if remove < 0.03: continue
    mid = (s0 + s1) // 2; r = int(remove * sr)
    cuts.append((mid - r // 2, mid - r // 2 + r))
pieces, pos = [], 0
for c0, c1 in cuts:
    seg = a[pos:c0].copy(); seg[-fade:] *= np.linspace(1, 0, fade); pieces.append(seg)
    pos = c1
    a[pos:pos + fade] *= np.linspace(0, 1, fade)
pieces.append(a[pos:])
o = np.concatenate(pieces)
w = wave.open(out, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(o, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print(f"typical pause was {med:.2f} s, scaled by {scale:.2f}; {len(cuts)} pauses shortened, {sum(c1 - c0 for c0, c1 in cuts) / sr:.1f} s removed; {len(a) / sr:.1f} s -> {len(o) / sr:.1f} s")
print(f"loudest sample inside any removed stretch: {max(20 * np.log10(np.abs(a[c0:c1]).max() + 1e-9) for c0, c1 in cuts):.1f} dBFS (speech is about -20)")
