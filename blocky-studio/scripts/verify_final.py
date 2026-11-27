"""Checks a finished video against its final.json and words.json.
usage: python verify_final.py <video.mp4> <project dir> <contact sheet out.jpg>
 - caption switches: the frame where the caption band changes vs the frame the word should start on
 - cuts: the frame where the picture changes most vs each shot's start frame
 - audio: where sound ends vs end of speech, and the length of the silent hold
 - re-transcribes the mixed audio and compares word onsets with the caption frames"""
import sys, json, subprocess, os
import numpy as np, cv2, imageio_ffmpeg
video, proj, sheet = sys.argv[1:4]
fin = json.load(open(os.path.join(proj, "final.json"))); words = json.load(open(os.path.join(proj, "words.json")))
cap = cv2.VideoCapture(video); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
n = len(frames); H, W = frames[0].shape[:2]
print(f"video: {W}x{H}, {fps:.0f} fps, {n} frames ({n / fps:.2f} s)")
# caption glyph mask per frame: near-white pixels in the caption band
band = lambda f: (f[int(H * 0.655):int(H * 0.735), int(W * 0.1):int(W * 0.9)].min(axis=2) > 236)
masks = [band(f) for f in frames]
blank = [i for i, m in enumerate(masks) if m.sum() < 150 and i >= fin["captions"][0]["f"]]
change = [i for i in range(1, n) if (masks[i] ^ masks[i - 1]).sum() > 0.25 * max(masks[i].sum(), masks[i - 1].sum(), 1)]
exp = [c["f"] for c in fin["captions"] if c["f"] > 0]
off = [min(change, key=lambda x: abs(x - e)) - e for e in exp]
print(f"captions: {len(exp)} expected switches, {len(change)} detected; offsets (frames) min {min(off)} max {max(off)}; exact {sum(o == 0 for o in off)}/{len(off)}; frames with no caption after the first word: {len(blank)}")
# cuts
starts = np.cumsum([0] + [s["frames"] for s in fin["shots"]["shots"]])[1:-1]
diff = [float(np.abs(frames[i].astype(int) - frames[i - 1].astype(int)).mean()) for i in range(1, n)]
for s in starts:
    k = max(range(max(1, s - 3), min(n, s + 4)), key=lambda i: diff[i - 1])
    print(f"  cut expected at frame {s}: biggest picture change at {k} (offset {k - s})")
# audio
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
win = 160; m = len(a) // win; rms = np.sqrt((a[:m * win].reshape(m, win) ** 2).mean(axis=1) + 1e-12)
loud = np.nonzero(20 * np.log10(rms) > -50)[0]; end = (loud[-1] + 1) * win / 16000
print(f"audio: {len(a) / 16000:.2f} s; last sound at {end:.2f} s (speech ends {words['speech_end']:.2f} s); silent hold {n / fps - end:.2f} s; level in the last 0.1 s of sound {20 * np.log10(rms[loud[-1] - 9:loud[-1] + 1].mean()):.1f} dBFS")
try:
    from faster_whisper import WhisperModel
    segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(a, word_timestamps=True, language="en")
    heard = [w for s in segs for w in s.words]
    if len(heard) == len(fin["captions"]):
        d = [c["f"] / fps - w.start for c, w in zip(fin["captions"], heard)]
        print(f"sync: caption start minus spoken onset in the finished file: median {np.median(d) * 1000:+.0f} ms, worst {max(d, key=abs) * 1000:+.0f} ms")
    else: print(f"sync: re-transcription heard {len(heard)} words vs {len(fin['captions'])} captions; not compared")
except Exception as e: print("sync: skipped:", e)
tiles = []
for s in [0] + list(starts):
    for k in (s, s + 8):
        t = cv2.resize(frames[min(n - 1, k)], (180, 240)); cv2.putText(t, str(k), (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1); tiles.append(t)
tiles.append(cv2.resize(frames[n - 1], (180, 240)))
while len(tiles) % 9: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(sheet, np.vstack([np.hstack(tiles[i:i + 9]) for i in range(0, len(tiles), 9)]))
