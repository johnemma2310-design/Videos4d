"""Adds clips the user chose from a split recording (sfx_split.py) to the sound library under proper names.
usage: python sfx_adopt.py <pack dir> <sfx dir> <picks.json>
picks.json: [{ "n": 1, "name": "whoosh_air", "what": "...", "where": "...", "trim_end": 0.97 (optional, seconds kept) }]
Copies <pack>/<n>.wav to <sfx>/<name>.wav (trimmed, short fades, peak-normalised), records each in <sfx>/credits.json
and rewrites <sfx>/usage.md: the guide to which sound goes where (the user's own instructions)."""
import sys, os, json, wave
import numpy as np

pack, out, picks_path = sys.argv[1:4]
picks = json.load(open(picks_path, encoding="utf-8"))
cred_path = os.path.join(out, "credits.json"); credits = json.load(open(cred_path, encoding="utf-8")) if os.path.exists(cred_path) else {}
for p in picks:
    w = wave.open(os.path.join(pack, f"{p['n']:03d}.wav")); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
    if p.get("trim_end"): a = a[: int(p["trim_end"] * sr)]
    f = min(len(a) // 2, int(0.006 * sr)); a = a.copy(); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    a = a / max(1e-6, np.abs(a).max()) * 0.9
    o = wave.open(os.path.join(out, p["name"] + ".wav"), "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes((a * 32767).astype(np.int16).tobytes()); o.close()
    credits[p["name"]] = {"title": f"clip {p['n']} of {os.path.basename(os.path.normpath(pack))}", "creator": "supplied by the user", "licence": "the user's own sound pack", "kind": p.get("kind", "oneshot"),
                          "seconds": round(len(a) / sr, 2), "what": p["what"], "where": p["where"]}
    print(f"  {p['name']:16s} {len(a) / sr:5.2f} s  <- clip {p['n']}")
json.dump(credits, open(cred_path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

rows_user = [f"| `{k}` | {v['seconds']} s | {v['what']} | {v['where']} |" for k, v in credits.items() if v.get("creator") == "supplied by the user"]
rows_lib = [f"| `{k}` | {v.get('seconds', '')} s | {'background layer (give it `dur`)' if v.get('kind') == 'loop' else 'single event'} | {v.get('title', '')} |" for k, v in credits.items() if v.get("creator") != "supplied by the user"]
open(os.path.join(out, "usage.md"), "w", encoding="utf-8").write(
"# Sound library: what each sound is for\n\n"
"Read this before placing sounds. The first table is the user's own pack with the user's own instructions; follow them.\n"
"The second table is the public-domain set fetched for the story world (rain, fire, crowds). Use both: the pack gives the\n"
"edit its punctuation (pops, whooshes, risers), the second gives the world its sound.\n\n"
"## The user's pack (their labels)\n| Sound | Length | What it is | Where to use it |\n|---|---|---|---|\n" + "\n".join(rows_user) + "\n\n"
"How to place them:\n"
"- **Pops and clicks** go on the frame something appears, changes or is pointed at. Vary them: do not use the same pop twice in a row.\n"
"- **Whooshes** go on camera whips and fast moves, starting on the first frame of the move.\n"
"- **Risers must END on the cut or the reveal.** Give the sound a `lead` equal to its length (in seconds) so it starts early and peaks on the frame you name.\n"
"- **`transition`** goes on a hard change of place or time, on the first frame of the new shot.\n"
"- **`clock_tick`, `loading_soft`, `loading_anim`** run under waiting, counting or building moments; keep them a few dB down (`gain` -4).\n"
"- Keep the rain, fire and crowd layers as they are; these sounds are added on top, never instead.\n\n"
"## The story-world set\n| Sound | Length | Kind | Source title |\n|---|---|---|---|\n" + "\n".join(rows_lib) + "\n")
print(f"library: {len(credits)} sounds; guide -> {os.path.join(out, 'usage.md')}")
