"""Checks a draft script against the measured shape of the sample scripts, and for wording copied from them.
usage: python script_check.py <script.txt> [--family world|timetravel] [--samples <dir>] [--ngrams <file.json>]
       python script_check.py --build-ngrams <samples dir> <out.json>      (studio owner only; makes the fingerprint file)

The ranges are the min and max measured over the samples (see references/title-script-style.md).
The copy check compares five-word runs. The fingerprint file holds only hashes, not the samples' text.
Runs that two or more samples share ("and there's only one rule") are house phrases and are allowed."""
import sys, os, re, json, glob, hashlib, statistics as st

WORD = r"[A-Za-z0-9'-]+"
def norm(t): return t.replace("’", "'").replace("‘", "'")
def words_of(t): return re.findall(WORD, norm(t).lower())
def sentences(t): return [s.strip() for s in re.split(r"(?<=[.!?…])[”\"]?\s+", t) if re.search(r"[A-Za-z]", s)]
def grams(t, n=5):   # runs inside one sentence; a run that crosses a full stop is not a copied sentence
    out = []
    for s in sentences(norm(t)):
        w = words_of(s); out += [" ".join(w[i:i + n]) for i in range(len(w) - n + 1)]
    return out
def h(g): return hashlib.sha1(g.encode()).hexdigest()[:12]
def body_of(path):
    t = open(path, encoding="utf-8").read()
    if path.endswith(".md"): t = "\n".join(t.split("\n")[3:])
    return re.sub(r"\(the captions end here\)", "", t).strip()

if len(sys.argv) > 1 and sys.argv[1] == "--build-ngrams":
    count = {}
    for f in sorted(glob.glob(os.path.join(sys.argv[2], "*.md"))):
        for g in set(grams(body_of(f))): count[h(g)] = count.get(h(g), 0) + 1
    json.dump({"n": 5, "hashes": count}, open(sys.argv[3], "w"))
    print(f"{len(count)} five-word runs fingerprinted ({sum(1 for v in count.values() if v > 1)} shared house phrases) -> {sys.argv[3]}"); sys.exit()

args = sys.argv[1:]
def opt(name, default=None):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
    return default
family, sdir, ngf = opt("--family"), opt("--samples"), opt("--ngrams")
if not args: sys.exit(__doc__)
text = norm(open(args[0], encoding="utf-8").read().strip())
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ngf = ngf or os.path.join(here, "lab", "samples_ngrams.json"); sdir = sdir or os.path.join(here, "lab", "samples")
w = words_of(text); sents = sentences(text); lens = [len(words_of(s)) for s in sents]; low = text.lower()
if family is None: family = "world" if low.startswith("in this world") else ("timetravel" if low.startswith("i ") else "world")

RANGES = {   # (sample min, sample max) per family
    "world":      {"words": (370, 435), "sentences": (49, 68), "median sentence": (5, 7), "longest sentence": (16, 25), "sentences of 4 words or fewer %": (22, 41), "sentences starting And %": (4, 13), "quoted lines": (0, 9)},
    "timetravel": {"words": (225, 246), "sentences": (21, 29), "median sentence": (8, 11), "longest sentence": (20, 20), "sentences of 4 words or fewer %": (14, 28), "sentences starting And %": (0, 7), "quoted lines": (2, 8)},
}[family]
SLACK = {"words": 15, "sentences": 5, "median sentence": 0.5, "longest sentence": 3, "sentences of 4 words or fewer %": 5, "sentences starting And %": 4, "quoted lines": 2}
first_words = [words_of(s)[0] for s in sents if words_of(s)]
got = {"words": len(w), "sentences": len(sents), "median sentence": st.median(lens), "longest sentence": max(lens),
       "sentences of 4 words or fewer %": round(sum(1 for x in lens if x <= 4) / len(lens) * 100),
       "sentences starting And %": round(first_words.count("and") / len(first_words) * 100), "quoted lines": (text.count("“") + text.count('"')) // 2 if "“" not in text else text.count("“")}
issues = []
def row(name, value, ok, note=""):
    print(f"  {'ok   ' if ok else 'CHECK'} {name:34s} {value}{('   <- ' + note) if note and not ok else ''}")
    if not ok: issues.append(name)
def where(i): return round(sum(lens[:i]) / len(w) * 100)

print(f"script check ({family} family): {args[0]}")
print(f"  length at 188 words/min: {len(w) / 188 * 60:.0f} s")
for k, (lo, hi) in RANGES.items():
    row(k, f"{got[k]}  (samples {lo} to {hi})", lo - SLACK[k] <= got[k] <= hi + SLACK[k])

print("structure")
if family == "world":
    row("opens 'In this world,'", sents[0][:60], low.startswith("in this world,"))
    ys = next((i for i, s in enumerate(sents) if s.lower().startswith("you see,")), None)
    row("'You see,' in the first 8 %", "absent" if ys is None else f"at {where(ys)} %", ys is not None and where(ys) <= 8)
    turn = next((i for i, s in enumerate(sents) if 32 <= where(i) <= 48 and re.match(r"(then|until|this|so the next|at (sunrise|noon|dawn|midnight|sunset)|one (day|night|morning))\b", s.lower()) and not s.lower().startswith("then there")), None)
    row("the turn at 34 to 43 %", "not found" if turn is None else f"at {where(turn)} %: {sents[turn][:50]}", turn is not None, "start the big event with Then / Until / This <day> / At sunrise")
    intro = next((i for i, s in enumerate(sents) if where(i) >= 8 and re.search(r"\b(my name is|and me,|gave me|my \w+ is|i always|i'm|i am)", s.lower())), None)
    print(f"  info  narrator first speaks of themself  {'not found' if intro is None else f'at {where(intro)} %: {sents[intro][:50]}'}   (samples 12 to 27 %)")
    coda = next((i for i in range(len(sents) - 5, len(sents)) if i >= 0 and re.match(r"(and )?now\b|and every|he still|she still", sents[i].lower())), None)
    row("'Now ...' coda in the last lines", "not found" if coda is None else f"at {where(coda)} %: {sents[coda][:50]}", coda is not None, "close in the present tense with the new normal")
    row("short, finished last line", f"{lens[-1]} words (samples 4 to 14): {sents[-1][:60]}", lens[-1] <= 14 and not sents[-1].endswith(("…", "...")), "the world family resolves; no cut-off ending")
    seen = {}
    for i, s in enumerate(sents):
        key = " ".join(words_of(s))
        if len(words_of(s)) >= 3: seen.setdefault(key, []).append(i)
    rep = [(k, v) for k, v in seen.items() if len(v) > 1 and where(v[-1]) - where(v[0]) >= 15]
    print(f"  info  planted line repeated later       {('yes: ' + rep[0][0][:50]) if rep else 'none (2 of 8 samples repeat the mentor line word for word; the rest pay off an object or a detail)'}")
    tri = re.findall(r"\b(\w+), \1, \1\b", low); snd = re.findall(r"(?:^|[.!?] )(\w+)!", text)
    print(f"  info  triple beats / sound words        {tri or '-'} / {snd or '-'}   (samples: 5 of 8 use one or both)")
    nick = re.search(r"nobody called me .{1,20} again|everyone calls me|calls? me|called me", low)
    print(f"  info  nickname                           {'yes' if nick else 'none (4 of 8 samples give the narrator a mocking nickname; 6 of 8 have them teased)'}")
else:
    row("opens with 'I' + past tense", sents[0][:60], low.startswith("i "))
    row("ends on an unfinished sentence", sents[-1][-40:], text.rstrip().endswith(("…", "...")), "the last sentence breaks off where the title would complete it")
    acc = len(re.findall(r"\b(accidentally|somehow|immediately|naturally|suddenly)\b", low))
    row("accident words (samples 4 to 6)", acc, acc >= 3)

print("uniqueness")
allowed, bad = 0, []
if os.path.exists(ngf):
    table = json.load(open(ngf))["hashes"]
    for g in grams(text):
        c = table.get(h(g))
        if c is None: continue
        if c > 1: allowed += 1
        else: bad.append(g)
elif os.path.isdir(sdir) and glob.glob(os.path.join(sdir, "*.md")):
    count = {}
    for f in glob.glob(os.path.join(sdir, "*.md")):
        for g in set(grams(body_of(f))): count[g] = count.get(g, 0) + 1
    for g in grams(text):
        if g in count: (bad.append(g) if count[g] == 1 else None); allowed += count[g] > 1
else:
    print("  CHECK no sample fingerprints found (lab/samples_ngrams.json); copy check skipped"); issues.append("copy check")
row("five-word runs shared with a sample", f"{len(bad)}{(': ' + '; '.join(bad[:6])) if bad else ''}  ({allowed} house phrases allowed)", not bad, "reword these")
USED = ["sens", "leo", "rex", "duke", "mia", "kai", "zara", "bubbles", "tank", "finch"]
hit = [n for n in USED if re.search(rf"\b{n}\b", low)]
row("names already used by the samples", hit or "none", not hit, "pick new names")
print("RESULT:", "inside the sample ranges, nothing copied" if not issues else f"{len(issues)} to look at: " + ", ".join(issues))
