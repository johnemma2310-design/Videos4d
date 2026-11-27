"""Quality assurance against the target video's measured style.

  python qa_score.py profile <target video> <lab/target>                 measure the target once (profile.json + contact sheets)
  python qa_score.py frames  <folder of frames> <lab/target/profile.json>  storyboard stage: colour and detail only
  python qa_score.py score   <video> <lab/target/profile.json> <out dir>   finished video: all categories -> report.json, report.md, sheet
  python qa_score.py log     <report.json> <lab dir> --name <video> --visual <0-100>
                                                                         combine with the reviewer's visual score, record it, check the 85 % goal

The measured score says how close the video's STATISTICS are to the target's: colour, surface detail, pacing, camera
motion, captions, sound ending, narration pace and the bright-to-dark arc. A new story is not meant to copy the
target shot for shot, so this is a style distance, not a verdict. The reviewer's visual score covers what numbers
cannot see (staging, camera angles, character style). Final = 70 % measured + 30 % visual."""
import sys, os, json, csv, glob, subprocess, datetime
import numpy as np, cv2, imageio_ffmpeg

W, H = 360, 480
BAND = (int(H * 0.62), int(H * 0.76))          # caption band, excluded from picture statistics
WEIGHTS = {"colour": 25, "detail": 10, "pacing": 15, "camera": 15, "captions": 10, "sound": 5, "narration": 10, "arc": 10}

def norm(h):
    h = np.asarray(h, np.float64); s = h.sum(); return (h / s if s else h).tolist()
def hist_sim(p, q): return float(1 - 0.5 * np.abs(np.asarray(p) - np.asarray(q)).sum())
def close(x, target, tol): return float(max(0.0, 1 - abs(x - target) / tol)) if tol else 0.0

def picture_stats(small):
    """colour + detail histograms of one frame (caption band blanked out)"""
    m = np.ones((H, W), bool); m[BAND[0]:BAND[1]] = False
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV); g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    luma = np.histogram(g[m], 32, (0, 256))[0]; sat = np.histogram(hsv[..., 1][m], 16, (0, 256))[0]
    hue = np.histogram(hsv[..., 0][m], 18, (0, 180), weights=hsv[..., 1][m].astype(np.float64))[0]
    edges = cv2.Canny(g, 40, 100); density = float(edges[m].mean() / 255)
    b, _, r = [float(small[..., i][m].mean()) for i in range(3)]
    return luma, sat, hue, density, float(g[m].mean()), r / max(b, 1)

def caption_box(frame):
    """bounding box of near-white glyphs in the caption band, at full resolution; None if no caption"""
    h, w = frame.shape[:2]; y0, y1 = int(h * 0.60), int(h * 0.80)
    white = (frame[y0:y1].min(axis=2) > 235).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(white)
    keep = [i for i in range(1, n) if st[i, 4] > 40 and 12 < st[i, 3] < h * 0.09 and st[i, 2] < w * 0.25]
    if not keep: return None
    x0 = min(st[i, 0] for i in keep); x1 = max(st[i, 0] + st[i, 2] for i in keep)
    ya = min(st[i, 1] for i in keep) + y0; yb = max(st[i, 1] + st[i, 3] for i in keep) + y0
    # signature = number of letters and the word's width in 8 px steps: stable against compression noise
    return (x0 + x1) / 2 / w, yb / h, (yb - ya) / h, (len(keep), int(round((x1 - x0) / 8)))

def read_frames(src):
    if os.path.isdir(src):
        for f in sorted(glob.glob(os.path.join(src, "*.jp*g")) + glob.glob(os.path.join(src, "*.png"))): yield cv2.imread(f)
    else:
        cap = cv2.VideoCapture(src)
        while True:
            ok, f = cap.read()
            if not ok: break
            yield f

def analyse(src, with_audio=True, transcribe=True):
    fps = cv2.VideoCapture(src).get(cv2.CAP_PROP_FPS) if not os.path.isdir(src) else 30.0
    L = np.zeros(32); S = np.zeros(16); Hh = np.zeros(18); dens, lum, warm, motion, cuts, caps, sig = [], [], [], [], [0], [], []
    prev = prev_h = None; tiles = []
    for i, f in enumerate(read_frames(src)):
        small = cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA)
        l, s, hh, d, mean_l, rb = picture_stats(small)
        L += l; S += s; Hh += hh; dens.append(d); lum.append(mean_l); warm.append(rb)
        hsv = cv2.cvtColor(cv2.resize(small, (90, 120)), cv2.COLOR_BGR2HSV)
        hd = cv2.normalize(cv2.calcHist([hsv], [0, 1, 2], None, [16, 8, 8], [0, 180, 0, 256, 0, 256]), None).flatten()
        g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32); g[BAND[0]:BAND[1]] = 0
        if prev is not None:
            dh = cv2.compareHist(prev_h, hd, cv2.HISTCMP_BHATTACHARYYA); dp = float(np.abs(g - prev).mean())
            if (dh > 0.38 or (dh > 0.25 and dp > 28)) and i - cuts[-1] >= 6: cuts.append(i)
            else: motion.append(dp)
        prev, prev_h = g, hd
        c = caption_box(f); caps.append(c); sig.append(c[3] if c else None)
        if i % max(1, int(fps // 2)) == 0: tiles.append(cv2.resize(f, (150, 200)))
    n = len(lum)
    out = {"frames": n, "fps": fps, "duration": n / fps, "luma_hist": norm(L), "sat_hist": norm(S), "hue_hist": norm(Hh),
           "edge_hist": norm(np.histogram(dens, 10, (0, 0.3))[0]), "edge_mean": float(np.mean(dens)), "luma_mean": float(np.mean(lum)), "warmth_mean": float(np.mean(warm))}
    if os.path.isdir(src): return out, tiles
    lens = np.diff(cuts + [n]) / fps
    out.update({"shots": len(lens), "shot_mean": float(lens.mean()), "shot_median": float(np.median(lens)), "cuts_per_min": float((len(lens) - 1) / (n / fps) * 60),
                "shot_hist": norm(np.histogram(lens, [0, 0.5, 1, 1.5, 2, 3, 99])[0]),
                "motion_hist": norm(np.histogram(motion, [0, 0.3, 0.6, 1, 1.5, 2.5, 4, 7, 12, 999])[0]), "static_fraction": float(np.mean(np.asarray(motion) < 0.6)), "motion_median": float(np.median(motion))})
    have = [c for c in caps if c]
    first = next((i for i, c in enumerate(caps) if c), 0)
    changes = sum(1 for i in range(1, n) if sig[i] is not None and sig[i] != sig[i - 1])
    out.update({"caption_x": float(np.median([c[0] for c in have])) if have else 0, "caption_bottom": float(np.percentile([c[1] for c in have], 20)) if have else 0,  # the baseline: words without descenders
               
                "caption_height": float(np.percentile([c[2] for c in have], 90)) if have else 0, "caption_coverage": float(np.mean([c is not None for c in caps[first:]])) if have else 0,
                "caption_changes_per_s": changes / (n / fps)})
    third = n // 3
    out.update({"arc_luma": float(np.mean(lum[-third:]) / max(np.mean(lum[:third]), 1)), "arc_warmth": float(np.mean(warm[-third:]) / max(np.mean(warm[:third]), 0.01))})
    if with_audio:
        raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        if len(a) > 1600:
            win = 160; m = len(a) // win; rms = np.sqrt((a[:m * win].reshape(m, win) ** 2).mean(axis=1) + 1e-12); db = 20 * np.log10(rms)
            loud = np.nonzero(db > -50)[0]; end = (loud[-1] + 1) * win / 16000 if len(loud) else 0
            out.update({"sound_end": float(end), "silent_hold": float(n / fps - end), "level_before_stop": float(db[max(0, loud[-1] - 9):loud[-1] + 1].mean()) if len(loud) else -99})
            if transcribe:
                try:
                    from faster_whisper import WhisperModel
                    segs, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(a, word_timestamps=True, language="en")
                    ws = [w for s in segs for w in s.words]
                    if len(ws) > 3:
                        gaps = [ws[i + 1].start - ws[i].end for i in range(len(ws) - 1)]; p = [g for g in gaps if g >= 0.15]
                        out.update({"words": len(ws), "wpm": float(len(ws) / (ws[-1].end - ws[0].start) * 60), "pause_median": float(np.median(p)) if p else 0.0})
                except Exception as e: out["narration_note"] = f"not measured: {e}"
    return out, tiles

def sheet(tiles, path, cols=12):
    if not tiles: return
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(path, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 88])

def compare(m, t):
    """per-category scores 0..1 with the numbers behind them"""
    r = {}
    r["colour"] = (np.mean([hist_sim(m["luma_hist"], t["luma_hist"]), hist_sim(m["sat_hist"], t["sat_hist"]), hist_sim(m["hue_hist"], t["hue_hist"])]),
                   f"brightness {hist_sim(m['luma_hist'], t['luma_hist']):.2f}, saturation {hist_sim(m['sat_hist'], t['sat_hist']):.2f}, hue {hist_sim(m['hue_hist'], t['hue_hist']):.2f} (1 = same spread); mean luma {m['luma_mean']:.0f} vs {t['luma_mean']:.0f}, warmth {m['warmth_mean']:.2f} vs {t['warmth_mean']:.2f}")
    r["detail"] = (hist_sim(m["edge_hist"], t["edge_hist"]), f"edge density {m['edge_mean'] * 100:.1f} % vs {t['edge_mean'] * 100:.1f} %")
    if "shot_mean" not in m: return r
    r["pacing"] = (0.5 * hist_sim(m["shot_hist"], t["shot_hist"]) + 0.25 * close(m["shot_mean"], t["shot_mean"], t["shot_mean"]) + 0.25 * close(m["cuts_per_min"], t["cuts_per_min"], t["cuts_per_min"]),
                   f"shot length mean {m['shot_mean']:.2f} s vs {t['shot_mean']:.2f}, median {m['shot_median']:.2f} vs {t['shot_median']:.2f}; {m['cuts_per_min']:.0f} cuts/min vs {t['cuts_per_min']:.0f}")
    r["camera"] = (0.6 * hist_sim(m["motion_hist"], t["motion_hist"]) + 0.4 * close(m["static_fraction"], t["static_fraction"], 0.3),
                   f"frame-to-frame change median {m['motion_median']:.2f} vs {t['motion_median']:.2f}; nearly still frames {m['static_fraction'] * 100:.0f} % vs {t['static_fraction'] * 100:.0f} %")
    r["captions"] = (np.mean([close(m["caption_x"], t["caption_x"], 0.03), close(m["caption_bottom"], t["caption_bottom"], 0.015), close(m["caption_height"], t["caption_height"], 0.012),
                              close(m["caption_coverage"], t["caption_coverage"], 0.2), close(m["caption_changes_per_s"], t["caption_changes_per_s"], t["caption_changes_per_s"])]),
                     f"centre x {m['caption_x']:.3f} vs {t['caption_x']:.3f}, baseline {m['caption_bottom']:.3f} vs {t['caption_bottom']:.3f}, height {m['caption_height']:.3f} vs {t['caption_height']:.3f}, on screen {m['caption_coverage'] * 100:.0f} % vs {t['caption_coverage'] * 100:.0f} %, {m['caption_changes_per_s']:.1f} word changes/s vs {t['caption_changes_per_s']:.1f}")
    if "silent_hold" in m and "silent_hold" in t:
        r["sound"] = (0.5 * close(m["silent_hold"], t["silent_hold"], 0.6) + 0.5 * (1.0 if m["level_before_stop"] > -40 else 0.0), f"silent hold {m['silent_hold']:.2f} s vs {t['silent_hold']:.2f}; level just before the stop {m['level_before_stop']:.0f} dBFS (a hard stop is above -40)")
    if "wpm" in m and "wpm" in t:
        r["narration"] = (0.6 * close(m["wpm"], t["wpm"], 60) + 0.4 * close(m["pause_median"], t["pause_median"], 0.3), f"{m['wpm']:.0f} words/min vs {t['wpm']:.0f}; pause median {m['pause_median']:.2f} s vs {t['pause_median']:.2f}")
    r["arc"] = (0.5 * close(m["arc_luma"], t["arc_luma"], 0.5) + 0.5 * close(m["arc_warmth"], t["arc_warmth"], max(t["arc_warmth"], 0.5)),
                f"last third vs first third: brightness x{m['arc_luma']:.2f} (target x{t['arc_luma']:.2f}), warmth x{m['arc_warmth']:.2f} (target x{t['arc_warmth']:.2f})")
    return r

HINTS = {
    "colour": "Compare the storyboard with the target sheet look by look. Adjust the looks used (lookOverrides or the preset): exposure and fill for brightness, grade saturation, sky and fog colour for hue.",
    "detail": "Too little edge density = surfaces too plain or shots too wide and empty: add crowds, props, relief materials. Too much = textures too contrasty.",
    "pacing": "Change where shots start: one per sentence, extra cuts on clause starts and punchline words; long shots only in the big event.",
    "camera": "Too many still frames = shots without a push-in: give every shot a creep-in. Too much motion = moves too fast or shake too long.",
    "captions": "Check Captions.tsx tuning (baseline, size) and that no frame after the first word is without a caption.",
    "sound": "The mix must stop dead at the last word with about one second of silent picture (endHoldFrames 32).",
    "narration": "Ask the narrator for the target pace (about 188 words per minute) with short pauses.",
    "arc": "The target goes from bright and cool to dark and warm. Order the looks that way: day, then dusk, then night.",
}

def main():
    cmd = sys.argv[1]
    if cmd == "profile":
        video, out = sys.argv[2:4]; os.makedirs(out, exist_ok=True)
        m, tiles = analyse(video)
        json.dump(m, open(os.path.join(out, "profile.json"), "w"), indent=1); sheet(tiles, os.path.join(out, "target_sheet.jpg"))
        print(f"target profile: {m['shots']} shots, mean {m['shot_mean']:.2f} s, {m['cuts_per_min']:.0f} cuts/min, luma {m['luma_mean']:.0f}, {m.get('wpm', 0):.0f} wpm -> {out}")
    elif cmd == "frames":
        m, _ = analyse(sys.argv[2]); t = json.load(open(sys.argv[3])); r = compare(m, t)
        for k, (s, why) in r.items(): print(f"  {k:8s} {s * 100:5.1f} / 100   {why}")
        print("storyboard style check (colour and detail only; a storyboard has one frame per shot, so long shots count the same as short ones)")
    elif cmd == "score":
        video, prof, out = sys.argv[2:5]; os.makedirs(out, exist_ok=True)
        m, tiles = analyse(video); t = json.load(open(prof)); r = compare(m, t)
        used = {k: WEIGHTS[k] for k in r}; total = sum(r[k][0] * used[k] for k in r) / sum(used.values()) * 100
        missing = [k for k in WEIGHTS if k not in r]
        rep = {"video": video, "measured_score": round(total, 1), "categories": {k: {"score": round(r[k][0] * 100, 1), "weight": WEIGHTS[k], "numbers": r[k][1]} for k in r}, "not_measured": missing, "metrics": m}
        json.dump(rep, open(os.path.join(out, "report.json"), "w"), indent=1); sheet(tiles, os.path.join(out, "video_sheet.jpg"))
        lines = [f"# QA report — {os.path.basename(video)}", "", f"Measured style score: **{total:.1f} / 100** (statistics only; the visual review is added separately).", "",
                 "| Category | Score | Weight | This video vs target |", "|---|---|---|---|"]
        for k in sorted(r, key=lambda k: r[k][0]): lines.append(f"| {k} | {r[k][0] * 100:.0f} | {WEIGHTS[k]} | {r[k][1]} |")
        if missing: lines += ["", "Not measured: " + ", ".join(missing) + "."]
        lines += ["", "## Where to improve (weakest first)", ""]
        for k in sorted(r, key=lambda k: r[k][0]):
            if r[k][0] < 0.85: lines.append(f"- **{k}** ({r[k][0] * 100:.0f}): {HINTS[k]}")
        open(os.path.join(out, "report.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
        print("\n".join(lines[2:]))
    elif cmd == "log":
        rep = json.load(open(sys.argv[2])); lab = sys.argv[3]; args = sys.argv[4:]
        name = args[args.index("--name") + 1]; visual = float(args[args.index("--visual") + 1])
        final = 0.7 * rep["measured_score"] + 0.3 * visual
        path = os.path.join(lab, "scores.csv"); new = not os.path.exists(path)
        with open(path, "a", newline="") as fh:
            w = csv.writer(fh)
            if new: w.writerow(["date", "video", "measured", "visual", "final"] + list(WEIGHTS))
            w.writerow([datetime.date.today().isoformat(), name, rep["measured_score"], visual, round(final, 1)] + [rep["categories"].get(k, {}).get("score", "") for k in WEIGHTS])
        rows = list(csv.DictReader(open(path)))
        print(f"final score {final:.1f} / 100  (measured {rep['measured_score']} x 0.7 + visual {visual:.0f} x 0.3); video {len(rows)} in the log")
        if len(rows) > 1: print("history:", ", ".join(f"{r['video']} {r['final']}" for r in rows[-6:]))
        if final >= 85: print("GOAL REACHED: the final score is 85 or more. Tell the user now: they asked to be reminded so the self-improving loop can be switched off.")
        else: print(f"{85 - final:.1f} points below the 85 goal: keep the self-improving loop on.")

if __name__ == "__main__":
    main()
