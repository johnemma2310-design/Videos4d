"""Lays the storyboard frames out as one labelled sheet.
usage: python board_sheet.py projects/<name> <folder of rendered frames> <out.jpg>
Each tile shows the frame with its shot number, start time, length, look and the words it covers."""
import sys, os, json, glob
import numpy as np, cv2

proj, frames_dir, out = sys.argv[1:4]
labels = json.load(open(os.path.join(proj, "board_labels.json"), encoding="utf-8"))
files = sorted(glob.glob(os.path.join(frames_dir, "*.jpeg")) + glob.glob(os.path.join(frames_dir, "*.jpg")) + glob.glob(os.path.join(frames_dir, "*.png")))
if len(files) != len(labels):
    sys.exit(f"{len(files)} frames in {frames_dir} but {len(labels)} shots in the storyboard: render storyboard.json again")
TW, TH, BAR = 300, 400, 64
tiles = []
for f, L in zip(files, labels):
    im = cv2.resize(cv2.imread(f), (TW, TH), interpolation=cv2.INTER_AREA)
    bar = np.full((BAR, TW, 3), 28, np.uint8)
    cv2.putText(bar, f"{L['n']}  {L['t']:.2f}s +{L['dur']:.2f}s  {L['look']}", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (120, 220, 255), 1, cv2.LINE_AA)
    cv2.putText(bar, L["camera"][:44], (6, 37), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(bar, L["line"][:44], (6, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    tiles.append(np.vstack([im, bar]))
cols = 6 if len(tiles) > 10 else 5 if len(tiles) > 4 else len(tiles)
while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]), [cv2.IMWRITE_JPEG_QUALITY, 90])
print(f"storyboard sheet: {len(labels)} shots -> {out}")
