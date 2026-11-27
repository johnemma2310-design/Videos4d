"""Word timestamps for a narration, aligned to the written script. Runs locally (faster-whisper).
usage: python align.py <narration.wav> <script.txt> <words.json>
Output: [{"w": <word as written in the script>, "t": start seconds, "end": seconds}], one entry per script word.
Whisper's words are matched to the script's words; script words it missed get interpolated times and are reported."""
import sys, json, re, subprocess, difflib
import numpy as np, imageio_ffmpeg
from faster_whisper import WhisperModel

wav, script_path, out = sys.argv[1:4]
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
import os  # stick3DD: idioma con ALIGN_LANG (es para los videos en español)
segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, word_timestamps=True, vad_filter=False, language=os.environ.get("ALIGN_LANG", "en"))
heard = [w for s in segs for w in s.words]
norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("’", "'"))
script = [w for w in open(script_path, encoding="utf-8").read().split() if norm(w)]
a, b = [norm(w) for w in script], [norm(w.word) for w in heard]
times = [None] * len(script)
for tag, i0, i1, j0, j1 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if tag == "equal":
        for k in range(i1 - i0): times[i0 + k] = (heard[j0 + k].start, heard[j0 + k].end)
    elif tag == "replace" and i1 - i0 == j1 - j0:  # misheard words, same count: keep their timing
        for k in range(i1 - i0): times[i0 + k] = (heard[j0 + k].start, heard[j0 + k].end)
missing = [i for i, t in enumerate(times) if t is None]
for i in missing:  # spread unmatched words evenly between their matched neighbours
    p = next((k for k in range(i - 1, -1, -1) if times[k]), None); n = next((k for k in range(i + 1, len(times)) if times[k] and k not in missing), None)
    t0 = times[p][1] if p is not None else 0.0; t1 = times[n][0] if n is not None else len(audio) / 16000
    run = [k for k in missing if (p is None or k > p) and (n is None or k < n)]
    j = run.index(i); step = (t1 - t0) / len(run)
    times[i] = (t0 + j * step, t0 + (j + 1) * step)
# end of speech = last window above -40 dBFS (trailing silence in the file must not delay the dead stop)
win = 320; n = len(audio) // win
rms = np.sqrt((audio[:n * win].reshape(n, win) ** 2).mean(axis=1) + 1e-12)
loud = np.nonzero(20 * np.log10(rms) > -40)[0]
speech_end = float((loud[-1] + 1) * win / 16000) if len(loud) else len(audio) / 16000
json.dump({"speech_end": round(speech_end, 3), "words": [{"w": w, "t": round(t[0], 3), "end": round(t[1], 3)} for w, t in zip(script, times)]}, open(out, "w", encoding="utf-8"), indent=1)
print(f"{len(script)} script words, {len(heard)} heard, {len(missing)} interpolated{': ' + ', '.join(script[i] for i in missing) if missing else ''}; speech ends at {speech_end:.2f} s")
