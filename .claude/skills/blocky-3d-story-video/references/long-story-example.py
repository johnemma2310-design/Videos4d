"""Writes story.json for 'The Rain Only Falls On Liars'. Shots are listed in order with the word index they start on.
usage: python projects/rain-liars/make_story.py   (run from the studio folder)"""
import json, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(os.path.join(HERE, "words.json"), encoding="utf-8"))["words"]
fr = lambda i: round(W[i]["t"] * 30)
shots = []

# ---------------------------------------------------------------- scenes
BLUE_SKY = {"top": "#4f86d8", "horizon": "#b4d2f4", "gradientHeight": 0.5, "haze": "#e2edf9", "hazeHeight": 0.06, "cloudLight": "#ffffff", "cloudDark": "#aebcd8", "cloudCover": 0.36, "cloudScale": 1.3, "cloudSeed": 5}
FOG = {"sky": BLUE_SKY, "fog": {"color": "#cfdcf2", "density": 0.0026},
       "lights": {"hemi": {"sky": "#dfe6ff", "ground": "#9a948c", "intensity": 0.95}, "key": {"color": "#fff0d8", "intensity": 3.2, "from": [0.55, 0.62, 0.6], "shadow": True}}}
DUSK = {"sky": {"top": "#7f5f96", "horizon": "#e8a0a0", "gradientHeight": 0.55, "haze": "#eab0a8", "hazeHeight": 0.06, "cloudLight": "#f6c8c0", "cloudDark": "#8f6488", "cloudCover": 0.5, "cloudScale": 1.2, "cloudSeed": 4},
        "lights": {"hemi": {"sky": "#c79ab4", "ground": "#4a2a30", "intensity": 1.0}, "key": {"color": "#ffc4a4", "intensity": 2.2, "from": [0.4, 0.5, 0.8], "shadow": True}}}
LATE_POST = {"toneMapping": "none", "exposure": 0.8, "bloom": {"strength": 0.25, "radius": 0.6, "threshold": 0.95}, "ao": {"radius": 1.2, "intensity": 1.0}, "grade": {"saturation": 1.05, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.03, 0.99, 0.94], "gamma": 1, "vignette": 0}}
LATE = {"lights": {"hemi": {"sky": "#e8cdb8", "ground": "#8a6a58", "intensity": 0.75}, "key": {"color": "#ffe2c0", "intensity": 2.3, "from": [0.5, 0.42, 0.7], "shadow": True}}, "post": LATE_POST}
LATE_IN = {"lights": {"hemi": {"sky": "#e6cfb8", "ground": "#8a6a54", "intensity": 1.45}, "key": {"color": "#ffe2c4", "intensity": 1.7, "from": [0.5, 0.6, 0.7], "shadow": True}}, "post": LATE_POST}
NIGHT_POST = {"toneMapping": "none", "exposure": 1, "bloom": {"strength": 0.36, "radius": 0.8, "threshold": 0.92}, "ao": {"radius": 1.5, "intensity": 1}, "grade": {"saturation": 1.05, "contrast": 1.0, "lift": [0, 0, 0], "gain": [1.05, 0.97, 0.9], "gamma": 1, "vignette": 0}}
NIGHT_L = {"post": NIGHT_POST, "lights": {"hemi": {"sky": "#9a6a60", "ground": "#3a2018", "intensity": 1.5}, "key": {"color": "#ffe8dc", "intensity": 2.8, "from": [0.35, 0.6, 0.8], "shadow": True}}}
KITCH_L = {"lights": {"hemi": {"sky": "#e6ddd2", "ground": "#8a7a6a", "intensity": 1.55}, "key": {"color": "#ffe6c0", "intensity": 2.5, "from": [-0.55, 0.6, 0.6], "shadow": True}}}   # warm light from the window side
SIGN_AWAY = {"sign": {"x": -9.55, "y": -80, "z": -18, "w": 4, "h": 7, "panel": "#786a92", "trim": "#847690", "glyph": "#8f8068", "yaw": 0}}
SCENES = {
    "street":  dict(set="fireStreet", setParams={"bowls": None}, look="DAY_SUN", lookOverrides=FOG, shadow={"focus": [0, 0, -8], "extent": 44}),
    "dusk":    dict(set="fireStreet", setParams={"houses": {"lit": 0.5}}, look="DUSK_MAGENTA", lookOverrides=DUSK, shadow={"focus": [0, 0, -8], "extent": 44}),
    "night":   dict(set="fireStreet", setParams={"houses": {"lit": 0.75}, "flames": False}, look="NIGHT_EMBER", lookOverrides=NIGHT_L, shadow={"focus": [0, 0, -8], "extent": 44}),
    "plaza":   dict(set="tabletPlaza", setParams=SIGN_AWAY, look="DAY_COOL", lookOverrides={"sky": BLUE_SKY, "lights": {"hemi": {"sky": "#dfe6ff", "ground": "#9a948c", "intensity": 1.0}, "key": {"color": "#fff0d8", "intensity": 2.8, "from": [0.5, 0.62, 0.62], "shadow": True}}}, shadow={"focus": [0, 0, -4], "extent": 30}),
    "plazaN":  dict(set="tabletPlaza", setParams=SIGN_AWAY, look="NIGHT_EMBER", lookOverrides=NIGHT_L, shadow={"focus": [0, 0, -4], "extent": 30}),
    "kitchen": dict(set="kitchen", setParams={"chairs": [], "table": None}, look="INTERIOR_NEUTRAL", lookOverrides=KITCH_L, shadow={"focus": [-4, 3, -3], "extent": 26}),
    "river":   dict(set="waterStreet", setParams={"ground": {"stone": "#cdb98e", "stoneDark": "#a8946c", "gap": "#8a7858"}}, look="DAY_SUN", lookOverrides=FOG, shadow={"focus": [6, 0, -14], "extent": 50}),
}

# ---------------------------------------------------------------- helpers
def A(ch, x, z, yaw=0, face="neutralTalk", faces=(), clips=(), **kw):
    a = {"character": ch, "pos": [x, z], **({} if yaw is None else {"yaw": yaw}), "faces": [{"f": 0, "v": face}] + [{"word": w, "v": v} for w, v in faces]}
    if clips: a["clips"] = [({"clip": c, "word": w} if isinstance(w, int) and w >= 0 else {"clip": c, "at": -w - 1000}) for c, w in clips]
    a.update(kw); return a
TALKERS = {"neutralTalk", "bigHappy", "smug", "angryTalk", "dotSmile", "worried", "deadpan", "happyArcs", "angryFrown", "nervous", "laugh", "eyesClosedTalk"}
PAIR = {"neutralTalk": "eyesClosedTalk", "bigHappy": "laugh", "laugh": "bigHappy", "worried": "nervous", "nervous": "worried", "blank": "worried", "deadpan": "blank", "smug": "happyArcs",
        "dotSmile": "happyArcs", "happyArcs": "dotSmile", "angryFrown": "angryTalk", "angryTalk": "angryFrown", "hollowShock": "blank", "scream": "hollowShock", "grittedAngry": "angryTalk", "disgust": "deadpan"}
HELD = lambda clip: (clip, -990)          # pose already held when the shot starts (at = -10)

def cam(target, frm, push=0.2, whip=None, out=None, shake=None, fov=47, rise=0, pan=None, to=None):
    t = list(target); p0 = list(frm)
    near = math.dist(p0, t) < 9.5                      # a close-up: barely push, or the head leaves the frame
    p1 = list(to) if to else [p0[i] + (t[i] - p0[i]) * (min(push, 0.05) if near else push * 1.3) for i in range(3)]; p1[1] += rise
    if not to: p1[0] += 0.9 * (1 if p0[0] >= t[0] else -1) * (-1 if len(shots) % 2 else 1)   # drift sideways, alternating
    keys = []
    if whip: keys += [{"f": -1, "pos": p0, "target": [t[0] + whip, t[1], t[2]]}, {"f": 4, "pos": p0, "target": t, "ease": "easeOutCubic"}]
    else: keys += [{"u": 0, "pos": p0, "target": t}]
    t1 = pan if pan else t
    if out:
        keys += [{"u": 0.9, "pos": p1, "target": t1, "ease": "linear"}, {"u": 1.07, "pos": p1, "target": [t1[0] + out, t1[1], t1[2]], "ease": "easeInQuart"}]
    else: keys += [{"u": 1, "pos": p1, "target": t1, "ease": "linear"}]
    c = {"fov": fov, "keys": keys}
    if shake: c["shake"] = shake
    return c
def med(x, z, side=3.0, dist=11.5, h=4.4, ty=3.9, **kw): return cam([x, ty, z], [x + side, h, z + dist], **kw)
def close(x, z, side=1.6, dist=8.0, h=4.8, ty=4.7, **kw): return cam([x, ty, z], [x + side, h, z + dist], **kw)
def wide(x, z, side=7, dist=30, h=8, ty=5, **kw): return cam([x, ty, z], [x + side, h, z + dist], **kw)
def track(target, frm, delta, push=0.0, shake=None):
    """the camera travels with a walker: position and target both move by delta (x, y, z)"""
    t1 = [target[i] + delta[i] for i in range(3)]; p1 = [frm[i] + delta[i] + (t1[i] - frm[i] - delta[i]) * push for i in range(3)]
    c = {"fov": 47, "keys": [{"u": 0, "pos": list(frm), "target": list(target)}, {"u": 1, "pos": p1, "target": t1, "ease": "linear"}]}
    if shake: c["shake"] = shake
    return c
IMPACT = lambda f=0: [{"f0": f, "f1": f + 10, "ampDeg": [0.5, 0.5], "mode": "alt", "decay": 0.75}]
RUMBLE = lambda f=0, n=50: [{"f0": f, "f1": f + n, "ampDeg": [0.04, 0.5], "mode": "alt", "bursts": 2}]

CUE = [0]; NIGHT = [False]
def cloud(x, z, kind="pillow", cue=None, appear=None, pour=None, vanish=None, **kw):
    base = {"pillow": dict(pos=[x, 7.3, z], size=3.0, dark=0.3), "barn": dict(pos=[x, 11.5, z - 1], size=15, dark=0.5, rain=0.6), "mid": dict(pos=[x, 9.5, z], size=7, dark=0.45)}[kind]
    v = {"type": "cloud", **base, **kw}
    if NIGHT[0]: v.setdefault("glow", 0.22)
    for k, w in (("appear", appear), ("pour", pour), ("vanish", vanish)):
        if w is not None: v[k] = fr(w) - fr(CUE[0])
    return v
SMOKE = "#2e2624"
def flames(spots, size=5.0, light=0):
    sz = min(size, 5.0) * 0.8
    return [{"type": "flame", "pos": list(s), "size": sz, "light": light} for s in spots] + \
           [{"type": "steam", "pos": [s[0], s[1] + sz * 1.6, s[2]], "count": 7, "spread": 3, "rise": 14, "size": 6, "color": SMOKE, "opacity": 0.42} for s in list(spots)[:4]]
EMBERS = lambda c=(0, 12, -14), n=320, size=0.16: {"type": "embers", "count": n, "box": [60, 30, 60], "centre": list(c), "size": size}
RAIN = lambda c=(0, 13, -4), n=2600: {"type": "rain", "count": n, "box": [44, 30, 34], "centre": list(c)}
STEAM = lambda pos, n=14, size=7, color="#e6e2de", op=0.35: {"type": "steam", "pos": list(pos), "count": n, "spread": 8, "rise": 9, "size": size, "color": color, "opacity": op}
def props(*items): return {"type": "props", "items": [dict(i) for i in items]}
def crowd(area, n, pal="water", facing=0, cheer=0.0, seed=1, **kw): return {"palette": pal, "count": n, "area": list(area), "facing": facing, "cheer": cheer, "seed": seed, **kw}
def TOWN(seed=1, cheer=0.0, z0=-70, z1=-14, mood="calm", walk=0.4, run=False):
    """the town behind the subject: a busy band where people walk both ways, a far band, a few bystanders at the side"""
    w = dict(mood=mood, walk=walk, walkDir=0, bothWays=True, run=run)
    return [crowd([-8, z0, 12, z1], 34, "water", 0, cheer, seed, **w), crowd([-8, z0, 12, z1], 26, "fire", 0, cheer, seed + 7, **w),
            crowd([-8, z0 - 70, 14, z0 - 4], 26, "water", 0, cheer, seed + 3, **w), crowd([7, z1 + 1, 13, z1 + 9], 5, "fire", -40, cheer, seed + 5, mood=mood)]
def SIDES(seed=1, mood="calm", walk=0.5, run=False, z0=-80, z1=-4):
    """people on both sides of a clear lane down the middle (x 0 to 4), for shots where someone travels along the street"""
    w = dict(mood=mood, walk=walk, walkDir=0, bothWays=True, run=run)
    return [crowd([-8, z0, -2.5, z1], 22, "water", 60, 0, seed, **w), crowd([6.5, z0, 13, z1], 22, "fire", -60, 0, seed + 4, **w)]
ROOFS = [(-15, 15, -6), (-15, 16, -30), (-14, 15, -52), (-15, 17, -78), (-14, 16, -104)]
WELL = lambda x, z: [dict(shape="cyl", pos=[x, 0.9, z], size=[1.9, 1.8], color="#8c8a92"), dict(shape="cyl", pos=[x, 1.82, z], size=[1.55, 0.06], color="#15131a"),
                     dict(shape="box", pos=[x - 1.8, 2.6, z], size=[0.3, 5.2, 0.3], color="#6a4a32"), dict(shape="box", pos=[x + 1.8, 2.6, z], size=[0.3, 5.2, 0.3], color="#6a4a32"),
                     dict(shape="box", pos=[x, 5.2, z], size=[4.4, 0.35, 0.5], color="#6a4a32"), dict(shape="box", pos=[x, 5.7, z], size=[5, 0.3, 2.4], color="#9a4a40", rotZ=0)]
OLD_BOAT = lambda x, z, y=0.9, tilt=14: [dict(shape="box", pos=[x, y, z], size=[3.4, 1.6, 9], color="#7a4a2e", rotZ=tilt, rotY=20), dict(shape="box", pos=[x, y + 0.9, z], size=[3.8, 0.3, 9.4], color="#c8a070", rotZ=tilt, rotY=20),
                                    dict(shape="cyl", pos=[x + 0.6, y + 4.2, z], size=[0.16, 7], color="#5a3a26", rotZ=tilt), dict(shape="box", pos=[x + 1.2, y + 5.2, z], size=[0.1, 3.4, 2.6], color="#f0ece0", rotZ=tilt, rotY=20)]
def BOAT(x, z, y=0.8, tilt=18, yaw=25):
    """a small sailing boat: hull with a pointed bow, pale deck, keel, mast and a slack sail. tilt = lying on its side"""
    r = dict(rotZ=tilt, rotY=yaw); s, c = math.sin(math.radians(yaw)), math.cos(math.radians(yaw))
    f = lambda d: [x + s * d, y, z + c * d]
    return [dict(shape="box", pos=f(0), size=[3.2, 1.5, 7], color="#7a4a2e", **r), dict(shape="box", pos=f(3.6), size=[2.26, 1.5, 2.26], color="#7a4a2e", rotZ=tilt, rotY=yaw + 45),
            dict(shape="box", pos=[x + s * -3.3, y + 0.2, z + c * -3.3], size=[3.0, 1.9, 0.5], color="#5e3822", **r), dict(shape="box", pos=[x, y + 0.78, z], size=[2.8, 0.14, 6.6], color="#d8b888", **r),
            dict(shape="box", pos=[x, y - 0.85, z], size=[0.4, 0.4, 7.4], color="#3a2418", **r), dict(shape="cyl", pos=[x + math.sin(math.radians(tilt)) * -3.2, y + 3.6, z], size=[0.17, 5.6], color="#4a3222", rotZ=tilt),
            dict(shape="box", pos=[x + math.sin(math.radians(tilt)) * -3.6 + 0.9, y + 4.4, z + 0.4], size=[0.08, 3.0, 2.2], color="#efe8d8", rotZ=tilt + 6, rotY=yaw + 8),
            dict(shape="box", pos=[x + 0.4, y + 0.95, z - 1.2], size=[1.2, 0.5, 1.0], color="#9a6a40", **r)]
def RIVERBED(water=False):
    """what makes the street read as a river bed: stone banks, a bridge, mooring posts, and cracked mud (or water)"""
    it = [dict(shape="box", pos=[-9.0, 1.3, -180], size=[1.4, 2.6, 400], color="#8a8c96"), dict(shape="box", pos=[20.5, 1.6, -180], size=[2.0, 3.2, 400], color="#8a8c96"), dict(shape="box", pos=[24.5, 1.5, -180], size=[6, 3.0, 400], color="#b8a888"),
          dict(shape="box", pos=[5.7, 8.2, -64], size=[31, 1.3, 5.5], color="#9a9ca6"), dict(shape="box", pos=[5.7, 9.4, -61.4], size=[31, 1.1, 0.5], color="#7c7e88"), dict(shape="box", pos=[5.7, 9.4, -66.6], size=[31, 1.1, 0.5], color="#7c7e88"),
          dict(shape="box", pos=[-2.5, 3.8, -64], size=[2.4, 7.6, 5], color="#8a8c96"), dict(shape="box", pos=[13.5, 3.8, -64], size=[2.4, 7.6, 5], color="#8a8c96")]
    for k, z in enumerate((-6, -20, -36)): it += [dict(shape="cyl", pos=[-7.6, 1.6, z], size=[0.3, 3.2], color="#5a4030"), dict(shape="cyl", pos=[-7.6, 2.7, z], size=[0.38, 0.3], color="#c8b48a")]
    if not water:
        for k in range(16): it.append(dict(shape="box", pos=[-5 + (k * 7.3) % 23, 0.03, -4 - k * 5.1], size=[0.22, 0.05, 3.2 + (k % 3)], color="#7a6a4c", rotY=(k * 53) % 180))
        it += [dict(shape="cyl", pos=[2.5, 0.35, -9], size=[0.9, 0.7, 0.7], color="#6a4a30", rotZ=90), dict(shape="box", pos=[14, 0.3, -18], size=[2.2, 0.6, 1.4], color="#8a6a48", rotY=30)]
    return it
WAGON = lambda x, z: [dict(shape="box", pos=[x, 2.0, z], size=[7, 2.4, 3.4], color="#b02a22"), dict(shape="cyl", pos=[x - 1.2, 4.2, z], size=[1.1, 2.2], color="#d8b03a"),
                      dict(shape="cyl", pos=[x - 2.4, 0.9, z + 1.8], size=[0.9, 0.4], color="#2a2422", rotX=90), dict(shape="cyl", pos=[x + 2.4, 0.9, z + 1.8], size=[0.9, 0.4], color="#2a2422", rotX=90),
                      dict(shape="cyl", pos=[x + 3.2, 3.6, z + 0.6], size=[0.22, 3.2], color="#d8b03a", rotZ=-60)]

def stall(x, z, col, rot=0):
    return [dict(shape="box", pos=[x, 1.3, z], size=[4.2, 2.6, 2.2], color="#7a5a3c", rotY=rot), dict(shape="box", pos=[x, 2.75, z], size=[4.4, 0.3, 2.4], color="#c9a878", rotY=rot),
            dict(shape="box", pos=[x - 2, 3.6, z - 1], size=[0.25, 7.2, 0.25], color="#5a4030"), dict(shape="box", pos=[x + 2, 3.6, z - 1], size=[0.25, 7.2, 0.25], color="#5a4030"),
            dict(shape="box", pos=[x, 7.3, z - 0.2], size=[5.2, 0.35, 3.4], color=col, rotX=14, rotY=rot), dict(shape="box", pos=[x - 1, 3.2, z], size=[0.9, 0.7, 0.9], color="#d84a3a"), dict(shape="box", pos=[x + 0.6, 3.2, z], size=[1.1, 0.6, 0.9], color="#e8b83a")]
def barrel(x, z): return [dict(shape="cyl", pos=[x, 0.9, z], size=[0.75, 1.8, 0.65], color="#6a4a30"), dict(shape="cyl", pos=[x, 1.5, z], size=[0.78, 0.14], color="#2a2420")]
def banner(x, z, col): return [dict(shape="cyl", pos=[x, 5, z], size=[0.14, 10], color="#4a3a30"), dict(shape="box", pos=[x + 0.9, 8.2, z], size=[1.7, 3.2, 0.08], color=col)]
STREET_DRESS = stall(-6.6, -24, "#c8382c", 8) + stall(7.5, -32, "#2f8f83", -10) + stall(-6.2, -52, "#e8b83a", 5) + barrel(-8.4, -3) + barrel(-7.2, -3.6) + barrel(9, -15) + banner(-8.8, -12, "#c8382c") + banner(-8.8, -40, "#2f8f83") + banner(11, -24, "#e8b83a") + \
               [dict(shape="box", pos=[-7.8, 0.7, -9], size=[1.4, 1.4, 1.4], color="#8a6a48", rotY=20), dict(shape="box", pos=[-7.6, 1.9, -9.1], size=[1.0, 1.0, 1.0], color="#9a7a54", rotY=-15)]
PLAZA_DRESS = stall(-10.5, -16, "#c8382c", 20) + stall(11, -18, "#2f8f83", -20) + barrel(-6.5, -22) + barrel(-5.2, -23) + barrel(8, -24) + banner(-13.5, -24, "#e8b83a") + banner(13.5, -24, "#c8382c") + \
              [dict(shape="box", pos=[13, 0.8, -10], size=[1.6, 1.6, 1.6], color="#8a6a48", rotY=25), dict(shape="box", pos=[13.2, 2.2, -10.2], size=[1.1, 1.1, 1.1], color="#9a7a54")]
KITCHEN_DRESS = [dict(shape="box", pos=[-10.5, 3.2, -10], size=[5, 6.4, 1.4], color="#8a5a3a"), dict(shape="box", pos=[-10.5, 4.3, -9.25], size=[4.6, 0.15, 0.2], color="#5a3a26"), dict(shape="box", pos=[-10.5, 2.1, -9.25], size=[4.6, 0.15, 0.2], color="#5a3a26"),
                 dict(shape="box", pos=[3, 1.6, -9.8], size=[3.4, 3.2, 2], color="#3a3a40"), dict(shape="cyl", pos=[2.4, 3.55, -9.8], size=[0.6, 0.7], color="#b0b4ba"), dict(shape="cyl", pos=[3.8, 3.45, -9.8], size=[0.45, 0.5], color="#c8502a"),
                 dict(shape="box", pos=[-3, 7.2, -10.8], size=[2.6, 2, 0.15], color="#e8d8a8"), dict(shape="box", pos=[-3, 7.2, -10.72], size=[2.0, 1.4, 0.1], color="#5a8ab0"),
                 dict(shape="cyl", pos=[8, 0.9, -9.6], size=[0.8, 1.8, 0.7], color="#6a4a30"), dict(shape="box", pos=[10.5, 1.0, -9.6], size=[2, 2, 2], color="#9a7a54", rotY=12)]
def DINNER(x, z, dish=True):
    it = [dict(shape="box", pos=[x, 2.75, z], size=[9, 0.3, 3], color="#a87a48"), dict(shape="box", pos=[x, 2.92, z], size=[8.4, 0.05, 2.4], color="#e8e0d0")]
    for sx in (-4, 4):
        for sz in (-1.2, 1.2): it.append(dict(shape="box", pos=[x + sx, 1.3, z + sz], size=[0.35, 2.6, 0.35], color="#7a5632"))
    for sx in (-2.4, 2.4): it += [dict(shape="cyl", pos=[x + sx, 3.0, z + 0.3], size=[0.75, 0.08], color="#f6f2ea"), dict(shape="box", pos=[x + sx + 1.1, 3.0, z + 0.3], size=[0.1, 0.05, 0.9], color="#b8bcc4")]
    it += [dict(shape="cyl", pos=[x, 3.35, z - 0.5], size=[0.12, 0.8], color="#f4ecd8"), dict(shape="cyl", pos=[x, 3.82, z - 0.5], size=[0.07, 0.16], color="#ffd060", glow=1.6)]
    if dish: it += CASSEROLE(x, 3.02, z + 0.4)
    return it
def CASSEROLE(x, y, z): return [dict(shape="box", pos=[x, y + 0.3, z], size=[1.9, 0.6, 1.3], color="#b0401e"), dict(shape="box", pos=[x, y + 0.64, z], size=[1.7, 0.12, 1.1], color="#e8b040"),
                                dict(shape="box", pos=[x - 1.1, y + 0.42, z], size=[0.35, 0.14, 0.5], color="#8a2e16"), dict(shape="box", pos=[x + 1.1, y + 0.42, z], size=[0.35, 0.14, 0.5], color="#8a2e16")]
KITCHEN_DRESS += [dict(shape="box", pos=[-2, 0.03, -4], size=[11, 0.06, 7], color="#9a3a34"), dict(shape="box", pos=[-2, 0.045, -4], size=[9.6, 0.06, 5.6], color="#c8a46a"),
                  dict(shape="box", pos=[-14.6, 8, -2.4], size=[0.25, 4.6, 1.3], color="#c0443a"), dict(shape="box", pos=[-14.6, 8, -8.6], size=[0.25, 4.6, 1.3], color="#c0443a"), dict(shape="box", pos=[-14.6, 10.3, -5.5], size=[0.3, 0.35, 7.6], color="#6a4a30"),
                  dict(shape="cyl", pos=[-2, 10.6, -5], size=[0.05, 2.6], color="#2a2420"), dict(shape="cyl", pos=[-2, 9.1, -5], size=[0.35, 0.7, 1.0], color="#e8b83a", glow=0.5),
                  dict(shape="box", pos=[8.5, 4.6, -10.6], size=[4.2, 0.2, 0.9], color="#6a4a30"), dict(shape="cyl", pos=[7.4, 5.1, -10.6], size=[0.4, 0.8], color="#4a7a9a"), dict(shape="cyl", pos=[8.6, 5.0, -10.6], size=[0.35, 0.6], color="#d8d0c0"), dict(shape="cyl", pos=[9.7, 5.15, -10.6], size=[0.3, 0.9], color="#5a8a4a")]
DRESS = {"street": STREET_DRESS, "dusk": STREET_DRESS, "night": STREET_DRESS, "plaza": PLAZA_DRESS, "plazaN": PLAZA_DRESS, "kitchen": KITCHEN_DRESS}

def S(id, cue, scene, actors, camera, vfx=(), crowds=(), sound=None, **over):
    dress = over.pop('dress', True)
    vfx = list(vfx) + ([props(*DRESS[scene])] if scene in DRESS and dress else [])
    for i, a in enumerate(actors):
        if a.get('talk') is False: del a['talk']
        elif 'talk' not in a and i == 0 and a['faces'][0]['v'] in TALKERS: a['talk'] = True   # the first actor mouths the narrator's words
    NIGHT[0] = False
    s = {"id": f"{len(shots) + 1:02d}_{id}", "cue": cue, **json.loads(json.dumps(SCENES[scene])), "actors": actors, "camera": camera}
    if vfx: s["vfx"] = list(vfx)
    if crowds: s["crowds"] = list(crowds)
    if sound: s["sound"] = sound
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(s.get(k), dict): s[k] = {**s[k], **v}
        else: s[k] = v
    # ---- sounds that follow from what is on screen (recordings in sfx/, see scripts/sfx_fetch.py)
    sfx, layers = list(MANUAL_SFX.get(cue, [])), {}
    def layer(kind, gain, at_=0): layers[kind] = max(layers.get(kind, (-99, 0))[0], gain), min(layers.get(kind, (0, at_))[1], at_)
    for v in vfx:
        if v["type"] == "cloud":
            big = v.get("size", 3) >= 10
            if "appear" in v: sfx.append({"type": "pop", "at": max(0, v["appear"])})
            if "pour" in v:
                if big: layer("rain_heavy", 4, max(0, v["pour"]))
                else: sfx.append({"type": "splash", "at": max(0, v["pour"])})
            elif v.get("rain", 0.5) > 0 and "vanish" not in v:
                layer("rain_light", (0 if big else -9) + (4 if v.get("rain", 0.5) > 0.9 else 0))
        elif v["type"] == "rain": layer("rain_heavy" if v.get("count", 3000) >= 1000 else "rain_light", 0)
        elif v["type"] == "flame": layer("fire", 0 if sum(1 for q in vfx if q["type"] == "flame") >= 3 else -5)
        elif v["type"] == "steam" and v.get("color", "#e6e2de") in ("#e6e2de", "#f2efe9") and not any(x["type"] == "hiss" for x in sfx): sfx.append({"type": "hiss", "at": 0, "gain": -4})
    sfx += [{"type": k, "at": at_, "dur": "shot", "gain": g} for k, (g, at_) in layers.items()]
    sfx = [x for x in sfx if os.path.exists(os.path.join(HERE, "..", "..", "sfx", x["type"] + ".wav"))]
    if sfx: s["sfx"] = sfx
    shots.append(s)
MANUAL_SFX = {   # by the shot's cue word: sounds the picture does not imply
    328: [{"type": "drip", "at": 0}], 342: [{"type": "drip", "at": 0}], 343: [{"type": "drip", "at": 0}], 344: [{"type": "drip", "at": 0}],
    347: [{"type": "thunder", "at": 0, "gain": 3}],
    221: [{"type": "crowd_panic", "at": 0, "dur": "shot", "gain": 2}], 237: [{"type": "crowd_panic", "at": 0, "dur": "shot", "gain": -3}], 274: [{"type": "crowd_panic", "at": 0, "dur": "shot", "gain": 3}],
    399: [{"type": "crowd_cheer", "at": 0, "dur": "shot", "gain": 3}],
}
def at(cue, night=False): CUE[0] = cue; NIGHT[0] = night; return cue

# ================================================================ A. the law (0-36)
S("world", at(0), "street", [A("mrsHobb", -3, -10, 20, "happyArcs"), A("teacher", 3, -14, -15, "dotSmile"), A("hobb", 7, -8, -30, "happyArcs")],
  wide(0, -12, side=9, dist=34, h=11, whip=-9, push=0.25), crowds=TOWN(1), sound="whoosh")
S("lie", at(3), "street", [A("mayor", 0, -6, 12, "bigHappy", clips=[("handUpQuick", 5)])], med(0, -6, push=0.22), crowds=TOWN(2))
S("pop", at(8), "street", [A("mayor", 0, -6, 12, "bigHappy", faces=[(11, "hollowShock")], clips=[HELD("handUpQuick")])],
  cam([0, 4.3, -6], [2.4, 3.6, 6.5], push=0.15, shake=IMPACT(fr(11) - fr(8))), vfx=[cloud(0, -6, appear=11)], crowds=TOWN(2), sound="hit")
S("small", at(16), "street", [A("mayor", 0, -6, 12, "worried")], cam([0, 7.4, -6], [1.5, 6.6, 1.5], push=0.2), vfx=[cloud(0, -6)], crowds=TOWN(2))
S("pillow", at(22), "street", [A("mayor", 0, -6, 12, "deadpan")], med(0, -6, side=-3, ty=4.1, h=4.6, dist=12.5, push=0.2), vfx=[cloud(0, -6)], crowds=TOWN(2))
S("follows", at(28), "street", [A("mayor", 2, -40, None, "worried", faces=[(31, "nervous")], look=[0, -0.05], clips=[("walk", -1000)], to=[2, -30.5], talk=False)],
  track([2, 4.9, -40], [5.2, 4.2, -27], [0, 0, 9.5]), vfx=[cloud(2, -40, follow=0, lag=7)], crowds=SIDES(3))
S("ownup", at(33), "street", [A("mayor", 0, -6, 12, "nervous", look=[0, -0.05])], close(0, -6, dist=7.5, push=0.25), vfx=[cloud(0, -6)], crowds=TOWN(2))

# ================================================================ B. Mr. Hobb (37-67)
TABLE = props(dict(shape="box", pos=[-4, 3.25, -4.2], size=[2.2, 0.8, 1.6], color="#c9772e"), dict(shape="box", pos=[-4, 3.7, -4.2], size=[1.9, 0.25, 1.3], color="#e8c060"))
S("hobbs", at(37), "kitchen", [A("hobb", -4, -6, 12, "dotSmile", faces=[(39, "neutralTalk"), (41, "worried")], look=[0.03, 0.03]), A("mrsHobb", -0.2, -1.6, 216, "bigHappy", clips=[("presentPlate", -990)])],
  cam([-3.6, 4.2, -6], [1.0, 5.4, 2.6], push=0.1), vfx=[props(*CASSEROLE(-1.5, 2.9, -3.2)), STEAM((-1.5, 3.8, -3.2), 5, 1.2, "#ffffff", 0.3)])
S("loved", at(42), "kitchen", [A("hobb", -4, -6, 8, "worried", faces=[(43, "bigHappy"), (45, "hollowShock")], look=[0, 0.04])],
  cam([-4, 4.7, -6], [-3.0, 4.8, 2.2], push=0.05, shake=IMPACT(fr(45) - fr(42) + 4)), vfx=[cloud(-4, -6, appear=45, pos=[-4, 7.1, -6], size=2.6)], sound="hit")
S("raincoat", at(46), "kitchen", [A("hobb", -2.3, -6, 0, "deadpan", faces=[(49, "blank"), (51, "deadpan")], look=[0, -0.05], talk=False), A("mrsHobb", 2.3, -6, 0, "angryFrown", faces=[(50, "deadpan")], look=[-0.05, 0])],
  cam([0, 4.3, -6], [0.6, 4.7, 8.2], push=0.14), vfx=[props(*DINNER(0, -3.4)), cloud(-2.3, -6, pos=[-2.3, 7.2, -6], size=2.6), STEAM((0, 4.0, -3.0), 5, 1.4, "#ffffff", 0.3)])
S("years", at(52), "kitchen", [A("mrsHobb", 2.3, -6, 0, "deadpan", faces=[(53, "eyesClosedTalk"), (54, "deadpan")], look=[-0.05, 0])],
  cam([2.3, 4.7, -6], [3.4, 4.8, 2.0], push=0.05), vfx=[props(*DINNER(0, -3.4))])
S("truth", at(55), "street", [A("mayor", 0, -6, 12, "worried", faces=[(57, "scream")], clips=[("armsUp", 56)])], med(0, -6, ty=4.1, h=4.6, dist=12.5, push=0.2), vfx=[cloud(0, -6)], crowds=TOWN(2))
S("splash", at(58), "street", [A("mayor", 0, -6, 12, "scream", faces=[(63, "blank")], clips=[HELD("armsUp"), ("rest", 64)])],
  wide(0, -6, side=4, dist=15, h=5, ty=4.2, push=0.25, shake=IMPACT(fr(61) - fr(58))), vfx=[cloud(0, -6, pour=61, vanish=64)], crowds=TOWN(2), sound="hit")

# ================================================================ C. the weird part (68-96)
S("weird", at(68), "plaza", [A("drizzle", 0, 0, 10, "smug", clips=[("shrugOut", 69)])], med(0, 0, whip=9, push=0.22), vfx=[cloud(0, 0, "barn")], sound="whoosh")
S("norain", at(73), "street", [A("teacher", -2, -8, 0, "worried", look=[0, -0.05]), A("grandma", 3, -9, 0, "worried", faces=[(76, "blank")], look=[0, -0.05]), A("hobb", 7, -7, 0, "blank", look=[0, -0.05])],
  cam([1, 4.6, -9], [3, 3.2, 5.5], push=0.1, pan=[1, 8, -20]), crowds=TOWN(4, mood="worried"))
S("sixty", at(79), "street", [], track([2, 0, -24], [2, 27, -9], [0, 0, -13]),
  crowds=[crowd([-8, -90, 12, 0], 46, "water", 0, 0, 21, mood="worried", walk=0.85, walkDir=0, bothWays=True), crowd([-8, -90, 12, 0], 30, "fire", 0, 0, 22, mood="worried", walk=0.85, walkDir=0, bothWays=True)],
  vfx=[props(dict(shape="cyl", pos=[1.5, 0.5, -28], size=[0.55, 1.0, 0.4], color="#8a6a4a"), dict(shape="cyl", pos=[-3, 0.5, -40], size=[0.55, 1.0, 0.4], color="#8a6a4a"), dict(shape="cyl", pos=[6, 0.35, -34], size=[0.55, 0.9, 0.4], color="#8a6a4a", rotZ=90))])
S("road", at(82), "river", [A("mrsHobb", 4.5, -6, None, "happyArcs", clips=[("walk", -1000)], to=[5, -15], talk=False), A("mayor", 9.5, -13, None, "dotSmile", clips=[("walk", -1000)], to=[8.5, -23], talk=False)],
  {"fov": 47, "keys": [{"u": 0, "pos": [13.5, 3.4, 9.5], "target": [9.5, 2.4, -8]}, {"u": 0.3, "pos": [13.5, 3.4, 9.5], "target": [9.5, 2.4, -8], "ease": "linear"}, {"u": 1, "pos": [13, 7.5, 7], "target": [6, 5.5, -44], "ease": "easeInOutSine"}]},
  vfx=[props(*BOAT(11.5, -9)), props(*RIVERBED())], crowds=[crowd([-6, -110, 18, -30], 26, "water", 0, 0, 5, walk=0.9, walkDir=0, bothWays=True), crowd([-6, -110, 18, -30], 12, "fire", 0, 0, 6, walk=0.9, walkDir=0, bothWays=True)], dress=False)
S("wells", at(88), "plaza", [A("grandma", -3.4, -3, 70, "worried"), A("teacher", 3.4, -3, -70, "worried"), A("odo", 0, -6.4, 0, "blank")],
  cam([0, 2.5, -3], [3, 7, 9], push=0.2), vfx=[props(*WELL(0, -3))])
S("lower", at(91), "plaza", [A("grandma", -3.4, -3, 70, "hollowShock"), A("teacher", 3.4, -3, -70, "hollowShock")], cam([0, 1.8, -3], [0.4, 9, 1.5], push=0.35), vfx=[props(*WELL(0, -3))])

# ================================================================ D. the narrator (97-158)
S("me", at(97), "street", [A("drizzle", 0, -6, 10, "deadpan")], med(0, -6, side=-3, push=0.22), vfx=[cloud(0, -6, "barn")], crowds=TOWN(5))
S("cloud", at(99), "street", [A("drizzle", 0, -6, 10, "deadpan")], cam([0, 7, -7], [3, 4.4, 6], to=[7, 4.5, 24]), vfx=[cloud(0, -6, "barn")], crowds=TOWN(5))
S("barn", at(110), "street", [A("drizzle", 0, -6, 10, "blank")], cam([0, 8, -7], [7, 3.5, 24], push=0.15, shake=IMPACT(0)), vfx=[cloud(0, -6, "barn")], crowds=TOWN(5), sound="hit")
S("socks", at(115), "street", [A("drizzle", 0, -6, 10, "deadpan")], cam([0, 0.9, -6], [1.6, 1.3, 0.5], push=0.25),
  vfx=[cloud(0, -6, "barn"), {"type": "water", "pos": [0, 0.04, -6], "size": [5, 5], "deep": "#6f8fa8", "light": "#a8c2d6"}])
S("lunch", at(121), "plaza", [A("drizzle", -6, -2, 20, "deadpan", clips=[("presentPlate", -990)])], wide(-4.5, -2, side=5, dist=17, h=6, ty=4.5, push=0.2),
  vfx=[cloud(-6, -2, "barn")], crowds=[crowd([2, -9, 13, -1], 16, "water", -70, 0.1, 6)])
S("soggy", at(125), "plaza", [A("drizzle", -6, -2, 20, "deadpan", faces=[(128, "disgust")], clips=[("presentPlate", -990)])], close(-6, -2, dist=7.5, ty=3.6, h=4.2, push=0.25),
  vfx=[cloud(-6, -2, "barn"), props(dict(shape="box", pos=[-5.0, 2.75, -0.2], size=[0.9, 0.3, 0.9], color="#b89a5a"))])
S("never", at(130), "plaza", [A("drizzle", 0, 0, 10, "neutralTalk", clips=[("shrugOut", 132)])], med(0, 0, side=-3, push=0.22), vfx=[cloud(0, 0, "barn")])
S("notone", at(136), "plaza", [A("drizzle", 0, 0, 10, "deadpan")], close(0, 0, push=0.25), vfx=[cloud(0, 0, "barn")])
S("teacher", at(138), "plaza", [A("teacher", 0, 0, -10, "bigHappy", clips=[("wave", 138)])], med(0, 0, push=0.22, whip=8))
S("mop", at(142), "plaza", [A("teacher", 0, 0, -10, "bigHappy", faces=[(146, "hollowShock")])], cam([0, 5.0, 0], [1.2, 6.4, 5.2], push=0.3, shake=IMPACT(fr(147) - fr(142))), sound="hit")
S("kids", at(148), "plaza", [A("odo", -3, -1, 25, "laugh", clips=[("handUpQuick", 149)]), A("mrsHobb", 3.2, -2, -25, "laugh", clips=[("pointUp", 150)]), A("hobb", 0.2, -4, 0, "bigHappy")],
  med(0, -1.5, side=0.5, dist=13, push=0.22), crowds=[crowd([-12, -16, 12, -7], 18, "fire", 0, 0.5, 8)])
S("dontmind", at(152), "plaza", [A("drizzle", 0, 0, 10, "dotSmile")], close(0, 0, push=0.25), vfx=[cloud(0, 0, "barn")])
S("everytime", at(157), "plaza", [A("drizzle", 0, 0, 10, "deadpan")], cam([0, 4.7, 0], [0.8, 4.8, 6.5], push=0.2), vfx=[cloud(0, 0, "barn", rain=1.0)])

# ================================================================ E. Odo and Grandma (159-203)
S("odo", at(159), "dusk", [A("odo", 0, -6, 10, "smug")], med(0, -6, push=0.22, whip=9), crowds=TOWN(9), sound="whoosh")
S("lies", at(162), "dusk", [A("odo", -1, -6, 40, "bigHappy", clips=[("pointUp", 163)]), A("teacher", 4, -5, -60, "blank")],
  med(1.5, -5.5, side=1, dist=12.5, ty=4.1, h=4.6, push=0.2), vfx=[cloud(-1, -6, appear=164)], crowds=TOWN(9))
S("ownsup", at(166), "dusk", [A("odo", -1, -6, 15, "smug", clips=[("shrugOut", 167)])], med(-1, -6, side=-2.5, dist=12, ty=4.1, h=4.6, push=0.22), vfx=[cloud(-1, -6, vanish=169, rain=0)], crowds=TOWN(9))
S("firstdrop", at(171), "dusk", [A("odo", -1, -6, 15, "happyArcs")], close(-1, -6, push=0.25), crowds=TOWN(9))
GCLOUD = dict(pos=[-5, 7.0, -4], size=2.4)
S("grandma", at(174), "kitchen", [A("grandma", -5, -4, 60, "dotSmile")], cam([-5, 4.6, -4], [6, 4.6, 5], push=0.22), vfx=[cloud(-5, -4, **GCLOUD)])
S("little", at(179), "kitchen", [A("grandma", -5, -4, 60, "worried")], cam([-5, 6.2, -4], [0, 5, 2.5], push=0.2), vfx=[cloud(-5, -4, **GCLOUD)])
S("grandpa", at(182), "kitchen", [A("grandma", -5, -4, 60, "worried")], cam([-5, 4.0, -4], [7, 4.4, 4], push=0.12, pan=[1.5, 2.5, -5.5]), vfx=[cloud(-5, -4, **GCLOUD)],
  setParams={"chairs": [{"x": 1.5, "z": -5.5, "yaw": -30}]})
S("saying", at(186), "kitchen", [A("grandma", -5, -4, 60, "neutralTalk", faces=[(189, "eyesClosedTalk"), (191, "neutralTalk")], clips=[("pointUp", 187)])],
  cam([-5, 4.7, -4], [1.6, 4.8, 1.6], push=0.28), vfx=[cloud(-5, -4, **GCLOUD)])
S("tellsme", at(194), "kitchen", [A("grandma", -6.5, -4, 80, "dotSmile"), A("drizzle", -1, -3.5, -40, "deadpan")], cam([-3.8, 4.4, -4], [8, 4.8, 6], push=0.2),
  vfx=[cloud(-6.5, -4, pos=[-6.5, 7.0, -4], size=2.4), cloud(-1, -3.5, "mid", pos=[-1, 8.4, -3.5], size=6)])
S("meant", at(198), "kitchen", [A("drizzle", -1, -3.5, 50, "smug")], cam([-1, 4.7, -3.5], [5.2, 4.8, 2.2], push=0.25), vfx=[cloud(-1, -3.5, "mid", pos=[-1, 8.4, -3.5], size=6)])

# ================================================================ F. the fire (204-275)
S("night", at(204, True), "night", [], wide(0, -30, side=10, dist=40, h=12, push=0.15), crowds=TOWN(11, z0=-90, z1=-30))
S("chimney", at(207, True), "night", [], cam([-14, 17, -30], [3, 1.6, -13], push=0.25, shake=IMPACT(fr(210) - fr(207))), vfx=flames([ROOFS[1]], 6, 12) + [EMBERS((-10, 20, -30), 180)], sound="hit")
S("oneroof", at(212, True), "night", [], cam([-14, 16, -30], [2, 9, -14], push=0.25), vfx=flames([ROOFS[1]], 7, 12) + [EMBERS((-10, 20, -30), 220)])
S("five", at(214, True), "night", [], cam([-12, 14, -50], [8, 7, 4], push=0.22), vfx=flames(ROOFS, 8, 6) + [EMBERS((-6, 18, -40), 380)])
S("street", at(216, True), "night", [], cam([-10, 12, -70], [12, 16, 16], push=0.25, shake=RUMBLE(4, 40)),
  vfx=flames(ROOFS + [(-15, 15, -130), (-14, 16, -160), (-9, 3, -20), (-9, 3, -62)], 9, 5) + [EMBERS((0, 16, -40), 520, 0.2)], crowds=TOWN(12, 0.2, mood="panic", walk=0.7, run=True))
S("whoosh", at(220, True), "night", [A("teacher", 3, -8, 20, "scream", clips=[HELD("armsUp")])], med(3, -8, push=0.3, whip=-10, shake=RUMBLE(0, 24)),
  vfx=flames(ROOFS[:3], 9, 6) + [{"type": "jet", "from": [-9, 6, -10], "dir": [1, 0.15, 0.2], "length": 16, "start": 0}, EMBERS((0, 10, -8), 420, 0.3)], crowds=TOWN(12, 0.2, mood="panic", walk=0.7, run=True), sound="whoosh")
S("ran", at(221, True), "night", [A("hobb", -7, -6, None, "scream", clips=[("runLeaning", -1000)], to=[9, -6]), A("mrsHobb", -10, -8.5, None, "scream", clips=[("runLeaning", -1000)], to=[6, -8.5]), A("mayor", -4, -4.5, None, "hollowShock", clips=[("runLeaning", -1000)], to=[12, -4.5])],
  track([-4, 3.9, -6], [-3, 4.2, 9], [15, 0, 0]), vfx=flames(ROOFS[:3], 9, 6) + [EMBERS((0, 10, -8), 420, 0.3)],
  crowds=[crowd([-8, -60, 14, -12], 30, "water", 90, 0, 31, mood="panic", walk=0.9, walkDir=90, run=True), crowd([-8, -60, 14, -12], 22, "fire", 90, 0, 32, mood="panic", walk=0.9, walkDir=90, run=True)], dress=False)
S("buckets", at(226, True), "plazaN", [A("grandma", -3.4, -3, 70, "hollowShock"), A("teacher", 3.4, -3, -70, "worried")], cam([0, 2.2, -3], [2.5, 8, 6], push=0.3),
  vfx=[props(*WELL(0, -3), dict(shape="cyl", pos=[2.9, 0.5, -0.6], size=[0.5, 1.0, 0.38], color="#8a6a4a")), EMBERS((0, 10, -10), 200)])
S("wagon", at(231, True), "night", [A("mayor", 5.5, -7, -30, "angryTalk", clips=[("castForward", 234)])], med(2, -8, side=4, dist=14, push=0.2),
  vfx=[props(*WAGON(0, -9)), STEAM((-5, 4.5, -9), 10, 3.2, "#b89a78", 0.5)] + flames(ROOFS[:2], 9, 6) + [EMBERS((0, 10, -8), 300, 0.3)])
S("lying", at(237, True), "plazaN", [A("mayor", 0, -2, 0, "worried"), A("odo", -5, -3, 15, "worried"), A("teacher", 5, -3, -15, "worried")], wide(0, -6, side=5, dist=26, h=9, push=0.22),
  vfx=flames([(-14, 9, -29), (12, 9, -29)], 6, 4) + [EMBERS((0, 12, -14), 360)], crowds=[crowd([-16, -22, 16, -6], 46, "water", 0, 0.4, 13, mood="panic"), crowd([-16, -22, 16, -6], 30, "fire", 0, 0.4, 14, mood="panic")])
S("mondays", at(243, True), "plazaN", [A("mayor", 0, -2, 5, "bigHappy", clips=[HELD("armsUp")])], close(0, -2, dist=7, push=0.3), vfx=[EMBERS((0, 8, -6), 260, 0.3)])
S("yelled", at(246, True), "plazaN", [A("mayor", 0, -2, 5, "bigHappy", clips=[HELD("armsUp")])], med(0, -2, ty=4.1, h=4.6, dist=12.5, push=0.2),
  vfx=[EMBERS((0, 10, -10), 300)], crowds=[crowd([-14, -20, 14, -7], 30, "water", 0, 0.3, 13, mood="worried")])
S("pop2", at(249, True), "plazaN", [A("mayor", 0, -2, 5, "blank", clips=[("rest", -1000)])], cam([0, 4.3, -2], [2.2, 3.8, 9.5], push=0.15, shake=IMPACT(3)), vfx=[cloud(0, -2, appear=249), EMBERS((0, 10, -10), 240)], sound="hit")
S("drizzle", at(250, True), "plazaN", [A("mayor", 0, -2, 5, "deadpan")], med(0, -2, side=-3, ty=4.1, h=4.6, dist=12.5, push=0.2), vfx=[cloud(0, -2), EMBERS((0, 10, -10), 300)] + flames([(-6, 0, -5)], 4, 8))
S("screamed", at(252, True), "plazaN", [A("odo", 0, -2, -5, "scream", clips=[("armsUp", 252)])], med(0, -2, push=0.25, whip=8), vfx=[EMBERS((0, 10, -10), 300)])
S("moon", at(254, True), "plazaN", [A("odo", 0, -2, -5, "scream", clips=[HELD("armsUp"), ("pointUp", 256)])], cam([0, 4.6, -2], [1.4, 3.2, 4.5], push=0.3), vfx=[EMBERS((0, 8, -6), 260, 0.3)])
S("nothing", at(260, True), "plazaN", [A("odo", 0, -2, -5, "blank")], cam([0, 4.8, -2], [1.6, 3.6, 6.5], push=0.15), vfx=[EMBERS((0, 12, -10), 200)])
S("meanit", at(261, True), "plazaN", [A("grandma", 0, -2, 10, "worried")], close(0, -2, push=0.25), vfx=[cloud(0, -2, pos=[0, 7.0, -2], size=2.4), EMBERS((0, 10, -10), 260)],
  crowds=[crowd([-14, -20, 14, -7], 30, "water", 0, 0.0, 13, mood="worried")])
S("reached", at(269, True), "plazaN", [], wide(0, -14, side=6, dist=30, h=9, push=0.25, shake=RUMBLE(2, 34)),
  vfx=flames([(-16, 9, -29), (-6, 9, -29), (5, 9, -29), (15, 9, -29), (-12, 0, -16), (10, 0, -18)], 7, 5) + [EMBERS((0, 12, -14), 520, 0.2)], sound="hit")
S("everyoneran", at(274, True), "plazaN", [A("odo", -9, -2, None, "scream", clips=[("runLeaning", -1000)], to=[5, -2]), A("teacher", -6, -4.5, None, "scream", clips=[("runLeaning", -1000)], to=[8, -4.5]), A("mayor", -2, -1, None, "scream", clips=[("runLeaning", -1000)], to=[12, -1])],
  track([-5, 3.9, -2.5], [-4, 4.2, 10], [13, 0, 0]), vfx=flames([(-12, 0, -14), (6, 9, -29)], 7, 6) + [EMBERS((0, 10, -8), 420, 0.3)],
  crowds=[crowd([-16, -20, 16, -7], 34, "water", 90, 0, 33, mood="panic", walk=0.9, walkDir=90, run=True)])

# ================================================================ G. the reframe (276-314)
FIRE_SQ = flames([(-16, 9, -29), (-6, 9, -29), (5, 9, -29), (15, 9, -29), (-12, 0, -14), (11, 0, -16)], 7, 5)
S("except", at(276, True), "plazaN", [A("drizzle", 0, 0, 10, "blank")], med(0, 0, push=0.22, whip=-10), vfx=FIRE_SQ + [cloud(0, 0, "barn"), EMBERS()])
S("lookup", at(279, True), "plazaN", [A("drizzle", 0, 0, 10, "worried")], cam([0, 4.5, 0], [1.5, 6.2, 6], push=0.25), vfx=[cloud(0, 0, "barn"), EMBERS()])
S("nine", at(285, True), "plazaN", [A("drizzle", 0, 0, 10, "blank")], cam([0, 9, -1], [7, 4.5, 28], push=0.15), vfx=FIRE_SQ + [cloud(0, 0, "barn"), EMBERS()], sound="hit")
S("echo", at(289), "kitchen", [A("grandma", -5, -4, 60, "neutralTalk", faces=[(292, "eyesClosedTalk"), (294, "neutralTalk")], clips=[HELD("pointUp")])],
  cam([-5, 4.7, -4], [0.8, 4.8, 0.8], push=0.3), vfx=[cloud(-5, -4, **GCLOUD)])
S("understood", at(297, True), "plazaN", [A("drizzle", 0, 0, 5, "hollowShock")], cam([0, 4.7, 0], [0.8, 4.8, 6.5], push=0.3), vfx=[cloud(0, 0, "barn"), EMBERS((0, 8, -6), 260, 0.3)], sound="hit")
S("alie", at(301, True), "plazaN", [A("drizzle", 0, 0, 5, "worried")], med(0, 0, side=-3, push=0.22), vfx=FIRE_SQ + [cloud(0, 0, "barn"), EMBERS()])
S("justone", at(306), "plaza", [A("drizzle", 0, 0, 10, "dotSmile")], close(0, 0, push=0.25), vfx=[cloud(0, 0, "barn")])
S("toldit", at(308), "plaza", [A("drizzle", -6, -2, 20, "dotSmile", clips=[("presentPlate", -990)])], med(-6, -2, push=0.22), vfx=[cloud(-6, -2, "barn")],
  crowds=[crowd([6, -14, 20, -4], 16, "water", -70, 0.1, 6)])
S("everyday", at(312), "dusk", [A("drizzle", 0, -6, 10, "dotSmile")], med(0, -6, side=-3, push=0.22), vfx=[cloud(0, -6, "barn")], crowds=TOWN(9))

# ================================================================ H. the act (315-379)
S("walked", at(315, True), "plazaN", [A("drizzle", 0, -13, None, "angryFrown", clips=[("walk", -1000)], to=[0, -1], talk=False)], cam([0, 4.4, -6], [1.5, 7.5, 20], push=0.3), vfx=FIRE_SQ + [cloud(0, -13, "barn", follow=0, lag=6), EMBERS((0, 12, -8), 420, 0.2)])
S("domind", at(323, True), "plazaN", [A("drizzle", 0, 0, 5, "angryTalk")], close(0, 0, push=0.28), vfx=[cloud(0, 0, "barn"), EMBERS((0, 8, -6), 260, 0.3)])
S("isaid", at(326, True), "plazaN", [A("drizzle", 0, 0, 5, "angryFrown")], med(0, 0, push=0.2), vfx=FIRE_SQ + [cloud(0, 0, "barn"), EMBERS()])
S("drip", at(328, True), "plazaN", [A("drizzle", 0, 0, 5, "blank")], cam([0, 4.8, 0], [4, 3.6, 12], push=0.2), vfx=FIRE_SQ + [cloud(0, 0, "barn", rain=0.15), EMBERS()])
S("socks2", at(329, True), "plazaN", [A("drizzle", 0, 0, 5, "angryTalk", clips=[("handUpQuick", 330)])], cam([0, 4.2, 0], [2, 2.6, 7.5], push=0.25), vfx=FIRE_SQ + [cloud(0, 0, "barn"), EMBERS()])
S("alone", at(333, True), "plazaN", [A("drizzle", 0, 0, 5, "grittedAngry", clips=[("shrugOut", 334)])], med(0, 0, side=-2.5, dist=9, push=0.25), vfx=FIRE_SQ + [cloud(0, 0, "barn"), EMBERS()])
S("called", at(337, True), "plazaN", [A("drizzle", 0, 0, 5, "angryTalk", faces=[(341, "scream")], clips=[("armsUp", 340)])], close(0, 0, dist=7.5, push=0.3), vfx=[cloud(0, 0, "barn"), EMBERS((0, 8, -6), 260, 0.3)])
S("drip1", at(342, True), "plazaN", [A("drizzle", 0, 0, 5, "blank", clips=[HELD("armsUp")])], cam([0, 7, 0], [5, 3.4, 17], push=0.2), vfx=[cloud(0, 0, "barn", rain=0.3), EMBERS()])
S("drip2", at(343, True), "plazaN", [A("drizzle", 0, 0, 5, "worried", clips=[HELD("armsUp")])], cam([0, 5.5, 0], [-3, 3.6, 11], push=0.2), vfx=[cloud(0, 0, "barn", rain=0.7), EMBERS()])
S("drip3", at(344, True), "plazaN", [A("drizzle", 0, 0, 5, "hollowShock", clips=[HELD("armsUp")])], cam([0, 4.7, 0], [1.2, 4.8, 7.0], push=0.25), vfx=[cloud(0, 0, "barn", rain=1.2), EMBERS()])
S("imind", at(345, True), "plazaN", [A("drizzle", 0, 0, 5, "scream", clips=[HELD("armsUp")])], cam([0, 4.7, 0], [0.6, 4.8, 6.0], push=0.3), vfx=[cloud(0, 0, "barn"), EMBERS((0, 8, -6), 260, 0.3)])
BRIGHT = {"post": {"toneMapping": "none", "exposure": 1.1, "bloom": {"strength": 0.55, "radius": 0.9, "threshold": 0.85}, "grade": {"saturation": 0.9, "contrast": 1.0, "lift": [0.05, 0.05, 0.08], "gain": [1.1, 1.1, 1.2], "gamma": 1, "vignette": 0}}}
S("crack", at(347, True), "plazaN", [A("drizzle", 0, 0, 5, "scream", clips=[HELD("armsUp")])], cam([0, 10, -1], [9, 2, 24], push=0.25, shake=IMPACT(0)),
  vfx=FIRE_SQ + [cloud(0, 0, "barn", pour=347), EMBERS()], sound="hit", lookOverrides={**NIGHT_L, **BRIGHT})
S("letgo", at(348, True), "plazaN", [A("drizzle", 0, 0, 5, "scream", clips=[HELD("armsUp")])], cam([0, 8, -1], [8, 3, 22], push=0.25, shake=RUMBLE(0, 40)),
  vfx=FIRE_SQ + [cloud(0, 0, "barn", pour=348), RAIN((0, 13, -4), 1800), EMBERS()])
S("nineyears", at(355, True), "plazaN", [A("drizzle", 0, 0, 5, "laugh", clips=[HELD("armsUp")])], close(0, 0, dist=8, ty=4.6, push=0.28), vfx=[RAIN((0, 12, -4), 1100), EMBERS((0, 8, -6), 120, 0.3)])
S("roofs", at(359, True), "night", [], cam([-12, 14, -50], [10, 9, 6], push=0.22, shake=RUMBLE(0, 40)), vfx=flames(ROOFS, 8, 6) + [RAIN((0, 14, -10), 3200), STEAM((-14, 16, -30), 16, 9)])
S("river2", at(365, True), "night", [], cam([-10, 10, -70], [12, 18, 18], push=0.2), vfx=flames(ROOFS, 6, 4) + [RAIN((4, 16, 0), 3200), STEAM((-14, 16, -30), 18, 10), STEAM((-14, 16, -78), 18, 10)], crowds=TOWN(12, 0.1, mood="panic", walk=0.6, run=True))
S("hissed", at(371, True), "night", [], cam([-14, 16, -30], [2, 10, -14], push=0.25), vfx=flames([ROOFS[1]], 3, 3) + [RAIN((-6, 14, -22), 2600), STEAM((-14, 15, -30), 22, 8, "#f2efe9", 0.5)])
S("streetby", at(377, True), "night", [], wide(0, -30, side=10, dist=40, h=12, push=0.18), vfx=[RAIN((6, 14, 0), 2600), STEAM((-14, 16, -30), 14, 10), STEAM((-14, 16, -78), 14, 10), STEAM((-14, 16, -6), 14, 10)], crowds=TOWN(12, mood="stunned", walk=0.0))

# ================================================================ I. aftermath (380-403)
WET = [crowd([-16, -22, 16, -7], 46, "water", 0, 0, 13, mood="stunned"), crowd([-16, -22, 16, -7], 30, "fire", 0, 0, 14, mood="stunned")]
S("stood", at(380, True), "plazaN", [A("mayor", -4, -4, 5, "blank"), A("teacher", 4, -4, -5, "blank"), A("grandma", 0, -3, 0, "dotSmile")], wide(0, -8, side=5, dist=26, h=8, push=0.22), vfx=[RAIN((0, 13, -4), 500)], crowds=WET)
S("soaked", at(385, True), "plazaN", [A("mayor", 0, -2, 5, "deadpan")], close(0, -2, push=0.25), vfx=[RAIN((0, 10, -2), 300)], crowds=WET)
S("staring", at(386, True), "plazaN", [A("drizzle", 0, 0, 5, "blank")], med(0, 0, push=0.25))
S("odowalk", at(389, True), "plazaN", [A("odo", 0, -12, None, "worried", faces=[(392, "dotSmile")], clips=[("walk", -1000)], to=[0, -3.5], talk=False)], cam([0, 4.2, -6], [1.6, 4.5, 9], push=0.1), crowds=[crowd([-16, -26, -4, -7], 24, "water", 20, 0, 13, mood="stunned"), crowd([4, -26, 16, -7], 24, "fire", -20, 0, 14, mood="stunned")])
S("jacket", at(393, True), "plazaN", [A("odoShirt", -2.8, 0, 50, "dotSmile", clips=[("reachForward", 394)]), A("drizzle", 2.8, 0, -45, "blank", faces=[(397, "bigHappy")])],
  med(0, 0, side=0.5, dist=12, push=0.22), vfx=[props(dict(shape="box", pos=[-0.7, 2.9, 1.2], size=[1.7, 1.9, 0.45], color="#2356c8", rotY=50))])
S("nobody", at(399, True), "plazaN", [A("drizzle", 0, 0, 5, "bigHappy", clips=[("armsUp", 400)]), A("odoShirt", -4.5, -1.5, 20, "laugh", clips=[HELD("cheerLoop")]), A("teacher", 4.5, -1.5, -20, "bigHappy", clips=[HELD("cheerLoop")])],
  med(0, -0.5, side=1, dist=14, push=0.22), crowds=[crowd([-16, -22, 16, -6], 46, "water", 0, 0.8, 13), crowd([-16, -22, 16, -6], 30, "fire", 0, 0.8, 14)])

# ================================================================ J. coda (404-434)
S("river3", at(404), "river", [A("mrsHobb", -8.6, -8, 60, "bigHappy", clips=[("wave", 406)], talk=False)],
  {"fov": 47, "keys": [{"u": 0, "pos": [13.5, 4.5, 8.5], "target": [7, 3.4, -10]}, {"u": 1, "pos": [13, 7.5, 7], "target": [6, 5.5, -44], "ease": "easeInOutSine"}]},
  vfx=[{"type": "water", "pos": [5.7, 1.1, -180], "size": [28.4, 400]}, props(*BOAT(9, -16, 1.9, 3, 12)), props(*RIVERBED(True))], crowds=[crowd([-9, 2.6, -8.4, -90], 1, "water", 90, 0.5, 5)], sound="whoosh", lookOverrides=LATE, dress=False)
S("gone", at(410), "kitchen", [A("grandma", -5, -4, 60, "happyArcs", clips=[("wave", 412)])], cam([-5, 4.4, -4], [4, 4.6, 3.5], push=0.25), lookOverrides=LATE_IN)
S("sunburn", at(416), "street", [A("drizzleSun", 0, -6, 10, "bigHappy", faces=[(421, "worried")])], med(0, -6, push=0.22, whip=8), crowds=TOWN(15), lookOverrides=LATE)
S("burn", at(421), "street", [A("drizzleSun", 0, -6, 10, "nervous")], close(0, -6, push=0.28), crowds=TOWN(15), lookOverrides=LATE)
S("told", at(423), "kitchen", [A("grandma", -6.5, -4, 80, "worried"), A("drizzleSun", -1, -3.5, -40, "smug", clips=[("shrugOut", 426)])], cam([-3.8, 4.4, -4], [8, 4.8, 6], push=0.2), lookOverrides=LATE_IN)
S("pop3", at(429), "kitchen", [A("drizzleSun", -1, -3.5, 50, "smug", faces=[(429, "hollowShock")])], cam([-1, 4.5, -3.5], [5.5, 4.4, 3.2], push=0.15, shake=IMPACT(2)),
  vfx=[cloud(-1, -3.5, appear=429, pos=[-1, 7.0, -3.5], size=2.4)], sound="hit", lookOverrides=LATE_IN)
S("okay", at(430), "kitchen", [A("drizzleSun", -1, -3.5, 50, "deadpan", faces=[(432, "nervous")])], cam([-1, 4.7, -3.5], [4.6, 4.8, 2.2], push=0.25),
  vfx=[cloud(-1, -3.5, pos=[-1, 7.0, -3.5], size=2.4)], lookOverrides=LATE_IN)

# every face must stay alive: an actor left on one expression gets a second one half-way through the shot
for i, s in enumerate(shots):
    nxt = shots[i + 1]["cue"] if i + 1 < len(shots) else len(W) - 1
    if fr(nxt) - fr(s["cue"]) < 34 or nxt - s["cue"] < 2: continue
    for a in s["actors"]:
        if len(a["faces"]) == 1 and a["faces"][0]["v"] in PAIR:
            a["faces"].append({"word": s["cue"] + (nxt - s["cue"] + 1) // 2, "v": PAIR[a["faces"][0]["v"]]})
            if nxt - s["cue"] >= 6: a["faces"].append({"word": nxt - 1, "v": a["faces"][0]["v"]})

story = {"audio": "audio/rain-liars.wav", "names": ["Hobb", "Drizzle", "Odo", "Grandma", "Grandma's", "Grandpa", "Mondays", "Mr"], "sfx": ["Whoosh", "Pop", "Drip", "Crack"], "endHoldFrames": 32, "shots": shots}
json.dump(story, open(os.path.join(HERE, "story.json"), "w", encoding="utf-8"), indent=1)
print(f"{len(shots)} shots -> story.json; mean shot {W[-1]['end'] / len(shots):.2f} s")
