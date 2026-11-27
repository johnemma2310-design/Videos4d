"""Checks a voice-over before it is accepted. Run after align.py.
usage: python voice_check.py <narration.wav> <words.json>
Reports pace, pauses, level, clipping and noise, each against the target measured on the reference
(188 words per minute including pauses; pauses median 0.36 s; no long gaps except deliberate ones)."""
import sys, json, subprocess
import numpy as np, imageio_ffmpeg

wav, wj = sys.argv[1:3]
d = json.load(open(wj, encoding="utf-8")); words, end = d["words"], d["speech_end"]
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
start = words[0]["t"]; dur = end - start
wpm = len(words) / dur * 60
gaps = [(words[i + 1]["t"] - words[i]["end"], i) for i in range(len(words) - 1)]
pauses = [g for g in gaps if g[0] >= 0.15]
med = float(np.median([g[0] for g in pauses])) if pauses else 0.0
long = [(round(g, 2), words[i]["w"], words[i + 1]["w"]) for g, i in gaps if g > 0.9]
win = 1600; n = len(a) // win; rms = np.sqrt((a[:n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12); db = 20 * np.log10(rms)
speech = db[db > -40]; noise = np.percentile(db, 5)
peak = float(np.abs(a).max()); clipped = float((np.abs(a) > 0.985).mean() * 100)
issues = []
def line(name, value, ok, note=""):
    print(f"  {'ok  ' if ok else 'WARN'} {name:26s} {value}{('   ' + note) if note and not ok else ''}")
    if not ok: issues.append(name)
print(f"voice-over: {len(words)} words, speech {start:.2f} to {end:.2f} s ({dur:.1f} s)")
line("pace", f"{wpm:.0f} words/min (target 188)", 160 <= wpm <= 215, "re-record faster" if wpm < 160 else "re-record a little slower")
line("pauses (median)", f"{med:.2f} s over {len(pauses)} pauses (target 0.36)", 0.15 <= med <= 0.6 or not pauses)
line("long gaps (> 0.9 s)", f"{len(long)}: {long[:4]}", True)
line("silence before first word", f"{start:.2f} s", start < 0.6, "trim the start of the file")
line("speech level", f"{np.median(speech):.1f} dBFS median", np.median(speech) > -35, "recorded very quietly")
line("peak / clipping", f"peak {20 * np.log10(max(peak, 1e-6)):.1f} dBFS, {clipped:.3f} % clipped samples", clipped < 0.05, "the recording clips; lower the input gain")
line("background noise", f"{noise:.1f} dBFS (speech is {np.median(speech) - noise:.0f} dB above it)", np.median(speech) - noise > 25, "noisy room or microphone")
print("long gaps are fine where a sound word (shown, not spoken) is planned; otherwise they slow the video down.")
print("RESULT:", "no problems found" if not issues else "check: " + ", ".join(issues))
