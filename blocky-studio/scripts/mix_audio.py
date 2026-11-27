"""Voice + music bed + sound effects, mixed to one file that stops dead at the end of speech.

usage: python mix_audio.py <narration.wav> <words.json> <out.wav> [--music music.wav] [--sounds sounds.json] [--bed-db 7] [--sfx-dir sfx]

- words.json comes from align.py (it holds the end of speech); sounds.json comes from build-video.ts.
- Without --music, a plain pad (slow chords of sine partials) is synthesised as a stand-in.
- Sounds are synthesised here: "hit" = a short low thump (the reference has one on about a third of its cuts),
  "whoosh" = a filtered-noise sweep. Any other type is a recording: <sfx dir>/<type>.wav (see sfx_fetch.py).
  A sound with "dur" is a background layer (rain, fire): the file is looped for that long, in step with the
  video's clock so it runs on unbroken across cuts. "gain" is in dB (0 = default level for its kind).
Measured on the reference: bed about 6-8 dB under the voice, no detectable tempo, effectively mono, hard stop."""
import argparse, json, subprocess, wave
import numpy as np, imageio_ffmpeg

SR = 48000
ap = argparse.ArgumentParser()
ap.add_argument("narration"); ap.add_argument("words"); ap.add_argument("out")
ap.add_argument("--music"); ap.add_argument("--sounds"); ap.add_argument("--bed-db", type=float, default=7.0); ap.add_argument("--sfx-dir", default="sfx")
a = ap.parse_args()

def load(path):
    raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0

end = json.load(open(a.words, encoding="utf-8"))["speech_end"]
n = int(end * SR)
voice = load(a.narration)[:n]; voice = np.pad(voice, (0, n - len(voice)))
if a.music:
    bed = np.resize(load(a.music), n)
else:
    t = np.arange(n) / SR; bed = np.zeros(n, np.float32)
    chords = [(146.83, 220.0, 293.66, 349.23), (130.81, 196.0, 261.63, 329.63), (116.54, 174.61, 233.08, 293.66), (130.81, 196.0, 246.94, 329.63)]
    for ci, ch in enumerate(chords):
        env = np.clip(1 - np.abs(((t / 5.0 - ci + 0.5) % len(chords)) - 0.5), 0, 1) ** 1.5  # slow cross-fades, no beat
        for f in ch:
            bed += env * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t + 0.3) + 0.15 * np.sin(2 * np.pi * 3 * f * t))
    bed *= 1 + 0.05 * np.sin(2 * np.pi * 0.2 * t)
rms = lambda x: float(np.sqrt((x[np.abs(x) > 1e-4] ** 2).mean() + 1e-12))
voice *= 0.25 / rms(voice)                      # voice to about -12 dBFS RMS while speaking
bed *= (0.25 / rms(bed)) * 10 ** (-a.bed_db / 20)
bed[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))   # no click at the start; the END is a hard stop on purpose

def hit():
    d = int(0.45 * SR); t = np.arange(d) / SR
    f = 46 + 60 * np.exp(-t / 0.05)                                  # pitch drops from about 105 Hz to 46 Hz
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    click = np.random.default_rng(1).standard_normal(d) * np.exp(-t / 0.006) * 0.25
    click = np.convolve(click, np.ones(24) / 24, mode="same")        # dull the click
    return (body + click) * 0.28

def whoosh():
    d = int(0.8 * SR); t = np.arange(d) / SR
    noise = np.random.default_rng(2).standard_normal(d)
    dark = np.convolve(noise, np.ones(90) / 90, mode="same") * 6; bright = np.convolve(noise, np.ones(10) / 10, mode="same") * 2
    sweep = np.sin(np.pi * t / 0.8) ** 2                             # opens up, then closes
    return (dark * (1 - sweep) + bright * sweep) * np.sin(np.pi * t / 0.8) ** 1.5 * 0.30

fx = np.zeros(n, np.float32); count = 0
if a.sounds:
    import os
    make = {"hit": hit, "whoosh": whoosh}; files = {}
    def clip(kind):
        if kind not in files:
            path = os.path.join(a.sfx_dir, kind + ".wav")
            if not os.path.exists(path): raise SystemExit(f"sound '{kind}': no such built-in sound and no file {path}")
            files[kind] = load(path)
        return files[kind]
    ONE_SHOT_PEAK, LAYER_RMS = 0.30, 0.25 * 10 ** (-16 / 20)        # one-shots peak a little under the voice; layers sit 16 dB under it
    for s in json.load(open(a.sounds, encoding="utf-8")):
        i0 = int(s["t"] * SR); g = 10 ** (s.get("gain", 0) / 20)
        if i0 >= n: continue                                         # nothing sounds after the dead stop
        if s["type"] in make: w = make[s["type"]]() * g
        elif s.get("dur"):                                           # background layer, looped in step with the clock
            c = clip(s["type"]); d = int(s["dur"] * SR); idx = (i0 + np.arange(d)) % len(c)
            w = c[idx] * (LAYER_RMS / rms(c)) * g
            f = min(d // 2, int(0.04 * SR)); w[:f] *= np.linspace(0, 1, f); w[-f:] *= np.linspace(1, 0, f)
        else:
            c = clip(s["type"]); w = c * (ONE_SHOT_PEAK / max(1e-6, np.abs(c).max())) * g
        w = w[: n - i0]; fx[i0:i0 + len(w)] += w; count += 1
fx = np.tanh(fx / 0.45) * 0.45                       # loud effects are squashed instead of pulling the whole mix down
mix = voice + bed + fx
over = np.abs(mix) > 0.7                              # untouched below 0.7; only the rare peaks above it are rounded off, so the voice keeps its level
mix[over] = np.sign(mix[over]) * (0.7 + 0.27 * np.tanh((np.abs(mix[over]) - 0.7) / 0.27))
with wave.open(a.out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print(f"wrote {a.out}: {n / SR:.2f} s, bed {a.bed_db} dB under the voice, {count} sounds, {'music file' if a.music else 'synthesised pad'}")
