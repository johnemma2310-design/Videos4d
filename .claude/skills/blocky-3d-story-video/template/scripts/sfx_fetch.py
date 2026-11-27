"""Finds and downloads public-domain (CC0) sound effects through the Openverse API, checks them by measurement and
keeps the best candidate for each sound.
usage: python sfx_fetch.py <wanted.json> <sfx dir> [--redo name,name]

wanted.json: [{ "name": "rain_light", "query": "light rain loop", "kind": "loop" | "oneshot", "min": 8, "max": 120 }]
  kind "loop"    = a steady background (rain, fire): the steadiest candidate wins; the middle is kept.
  kind "oneshot" = a single event (pop, thunder): the candidate with the clearest single attack wins; trimmed to it.
Writes <sfx dir>/<name>.wav (mono, 48 kHz) and <sfx dir>/credits.json (title, creator, licence, page for every clip).
Only CC0 results are requested: free for any use, no credit required. Nothing about the user is sent; the only
request data is the search words. You cannot hear the result: the user must listen to the first mix."""
import sys, os, json, time, subprocess, urllib.request, urllib.parse, wave
import numpy as np, imageio_ffmpeg

args = sys.argv[1:]; redo = []
if "--redo" in args: i = args.index("--redo"); redo = args[i + 1].split(","); del args[i:i + 2]
wanted_path, out = args
os.makedirs(out, exist_ok=True); tmp = os.path.join(out, "_candidates"); os.makedirs(tmp, exist_ok=True)
cred_path = os.path.join(out, "credits.json")
credits = json.load(open(cred_path, encoding="utf-8")) if os.path.exists(cred_path) else {}
SR = 48000; UA = {"User-Agent": "sfx-fetch/1.0"}
FF = imageio_ffmpeg.get_ffmpeg_exe()

def get(url, binary=False):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        b = r.read(); return b if binary else json.loads(b)
def decode(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
def rms_windows(a, sec=0.25):
    w = int(sec * SR); n = len(a) // w
    return np.sqrt((a[:n * w].reshape(n, w) ** 2).mean(axis=1) + 1e-12) if n else np.array([1e-6])
def save(path, a):
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

for want in json.load(open(wanted_path, encoding="utf-8")):
    name, kind = want["name"], want.get("kind", "oneshot"); dst = os.path.join(out, name + ".wav")
    if os.path.exists(dst) and name not in redo: print(f"{name}: already in the library"); continue
    q = urllib.parse.urlencode({"q": want["query"], "license": "cc0", "page_size": 20})
    try: res = get("https://api.openverse.org/v1/audio/?" + q).get("results", [])
    except Exception as e: print(f"{name}: search failed ({e})"); continue
    time.sleep(1.2)
    lo, hi = want.get("min", 0.1), want.get("max", 30)
    fake = ("mouth", "voice", "vocal", "beatbox", "synth", "8bit", "8-bit", "imitation") + tuple(want.get("avoid", []))   # imitations, not the real thing
    cands = [r for r in res if r.get("url") and lo <= (r.get("duration") or 0) / 1000 <= hi and r.get("license") == "cc0" and not any(x in (r.get("title") or "").lower() for x in fake)][:5]
    best = None
    for k, r in enumerate(cands):
        f = os.path.join(tmp, f"{name}_{k}.{(r.get('filetype') or 'mp3')[:4]}")
        try: open(f, "wb").write(get(r["url"], True)); a = decode(f)
        except Exception as e: print(f"  {name} candidate {k}: download failed ({e})"); continue
        time.sleep(0.6)
        if len(a) < SR * 0.05 or np.abs(a).max() < 0.02: continue
        if kind == "loop":
            w = rms_windows(a); mid = w[len(w) // 6: len(w) * 5 // 6] if len(w) > 12 else w
            steadiness = float(np.std(20 * np.log10(mid)))                  # dB spread of loudness: lower = steadier
            score = -steadiness - (4 if np.abs(a).max() > 0.999 else 0)
            s0 = len(a) // 6; clip = a[s0: s0 + min(len(a) * 2 // 3, 30 * SR)]  # the middle, at most 30 s
            note = f"loudness spread {steadiness:.1f} dB"
        else:
            env = rms_windows(a, 0.01); pk = int(np.argmax(env)); floor = float(np.percentile(env, 20)) + 1e-6
            snr = 20 * np.log10(env[pk] / floor)
            start = pk
            while start > 0 and env[start - 1] > env[pk] * 0.05: start -= 1
            s0 = max(0, start * SR // 100 - int(0.01 * SR)); length = min(len(a) - s0, int(want.get("keep", 2.5) * SR))
            clip = a[s0: s0 + length].copy(); tail = min(len(clip), int(0.15 * SR)); clip[-tail:] *= np.linspace(1, 0, tail)
            score = snr - 8 * (start / 100 > 5)                              # a clear event, not buried late in a long take
            note = f"event stands {snr:.0f} dB above the quiet parts, at {start / 100:.2f} s"
        print(f"  {name} candidate {k}: {r['title'][:44]!r} {len(a) / SR:.1f} s, {note}")
        if best is None or score > best[0]: best = (score, clip, r, note)
    if best is None: print(f"{name}: NO usable CC0 result for '{want['query']}'"); continue
    _, clip, r, note = best
    clip = clip / max(1e-6, np.abs(clip).max()) * 0.9
    save(dst, clip)
    credits[name] = {"title": r.get("title"), "creator": r.get("creator"), "licence": "CC0 1.0 (public domain)", "page": r.get("foreign_landing_url"), "source": r.get("source"), "query": want["query"], "kind": kind, "seconds": round(len(clip) / SR, 2), "check": note}
    json.dump(credits, open(cred_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{name}: kept {r['title'][:50]!r} by {r.get('creator')} ({len(clip) / SR:.1f} s)")
print(f"library: {len([f for f in os.listdir(out) if f.endswith('.wav')])} clips in {out}; credits in {cred_path}")
