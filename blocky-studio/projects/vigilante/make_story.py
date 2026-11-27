"""Director del episodio "El Vigilante" (motor blocky-studio): genera story.json y la pista de música por actos.

Uso (desde blocky-studio):  python projects/vigilante/make_story.py
Cada línea del guion (script.txt) da 1-2 tomas. Las tomas se escriben con helpers: escenas (set + look),
actores (A), cámara por receta (cam) y sonidos automáticos (whoosh en whips, pop en cambios de cara,
transition al cambiar de lugar).
"""
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
W = json.loads((HERE / "words.json").read_text(encoding="utf-8"))["words"]
L = json.loads((HERE / "line_starts.json").read_text())
FPS = 30
GIANT = 1.6   # escala del Vigilante


def wi(line, k=0):
    """índice global de la palabra k de la línea"""
    return L[line] + k


def lf(word, cue):
    return round(W[word]["t"] * FPS) - round(W[cue]["t"] * FPS)


# ------------------------------------------------------------------ escenas
INTERIOR = {"lights": {"hemi": {"sky": "#e6ddd2", "ground": "#8a7a6a", "intensity": 1.9},
                       "key": {"color": "#fff0dc", "intensity": 1.8, "from": [0.5, 0.8, 0.7], "shadow": True}}}
NOCHE_DENTRO = {"lights": {"hemi": {"sky": "#6a7aaa", "ground": "#2a2a3a", "intensity": 1.35},
                           "key": {"color": "#a8bcff", "intensity": 1.15, "from": [0.6, 0.7, 0.8], "shadow": True}}}
HAZE = {"fog": {"color": "#c4d2ec", "density": 0.0035}}

CUARTO_PROPS = {"type": "props", "items": [
    {"shape": "box", "pos": [-9, 0.6, -6], "size": [4.5, 1.2, 7], "color": "#6a4a32"},      # cama
    {"shape": "box", "pos": [-9, 1.45, -6], "size": [4.2, 0.5, 6.6], "color": "#eeeae2"},   # colchón
    {"shape": "box", "pos": [-9, 1.75, -4.4], "size": [4.3, 0.25, 3.6], "color": "#2a5ab0"},# cobija
    {"shape": "box", "pos": [-9, 1.9, -8.6], "size": [3.2, 0.6, 1.2], "color": "#f6f4ee"},  # almohada
    {"shape": "box", "pos": [-5.5, 1.0, -9.5], "size": [1.6, 2.0, 1.6], "color": "#5a3e2a"},# buró
    {"shape": "cyl", "pos": [-5.5, 2.4, -9.5], "size": [0.35, 0.8], "color": "#d8c8a0"},    # lámpara
    {"shape": "cyl", "pos": [-5.5, 3.0, -9.5], "size": [0.6, 0.6], "color": "#ffe8a0", "glow": 1.2},
    {"shape": "box", "pos": [6, 3.0, -10.4], "size": [5, 6, 1.2], "color": "#7a5236"},      # ropero
    {"shape": "box", "pos": [6, 3.0, -9.75], "size": [0.12, 5.4, 0.1], "color": "#3a2618"},
    {"shape": "box", "pos": [1, 0.03, -3], "size": [8, 0.06, 6], "color": "#8a3a4a"},       # tapete
]}
COCINA_PROPS = {"type": "props", "items": [
    {"shape": "cyl", "pos": [-1.5, 2.85, -6.5], "size": [0.35, 0.5], "color": "#e8e4dc"},    # taza
    {"shape": "box", "pos": [0.5, 2.7, -6.2], "size": [1.4, 0.15, 1.0], "color": "#d8b080"}, # pan
    {"shape": "box", "pos": [9, 2.5, -10.3], "size": [6, 5, 1.0], "color": "#c8d4dc"},       # alacena
    {"shape": "cyl", "pos": [2.5, 2.9, -6.8], "size": [0.3, 0.6], "color": "#e05a3a"},
]}

ESC = {
    "calle_dia": dict(set="fireStreet", look="DAY_SUN", lookOverrides=HAZE,
                      shadow={"focus": [-3, 0, -8], "extent": 40}, setParams={"houses": {"lit": 0.1}}),
    "calle_noche": dict(set="fireStreet", look="NIGHT_EMBER", shadow={"focus": [-3, 0, -8], "extent": 40},
                        setParams={"houses": {"lit": 0.7}}),
    "plaza": dict(set="tabletPlaza", look="DAY_COOL", shadow={"focus": [0, 0, -4], "extent": 30}),
    "campo_noche": dict(set="nightField", look="NIGHT_EMBER", shadow={"focus": [0, 0, -6], "extent": 40}),
    "cocina": dict(set="kitchen", look="INTERIOR_NEUTRAL", lookOverrides=INTERIOR,
                   shadow={"focus": [-4, 3, -3], "extent": 26}, setParams={"chairs": []}, props=COCINA_PROPS),
    "cuarto": dict(set="kitchen", look="INTERIOR_NEUTRAL", lookOverrides=NOCHE_DENTRO,
                   shadow={"focus": [-4, 3, -3], "extent": 26}, setParams={"chairs": [], "table": None},
                   props=CUARTO_PROPS),
    "recuerdo": dict(set="waterStreet", look="PEACH_HIGHKEY", shadow={"focus": [-3, 0, -8], "extent": 40}),
    "recuerdo_tarde": dict(set="waterStreet", look="DUSK_MAGENTA", shadow={"focus": [-3, 0, -8], "extent": 40}),
}

# dónde se para el protagonista y desde qué ángulo mira bien la cámara en cada lugar
SPOT = {"calle_dia": ((-3, -2), 15), "calle_noche": ((-3, -2), 15), "plaza": ((0, 0), 0),
        "campo_noche": ((0, -6), 0), "cocina": ((-4, -3), 65), "cuarto": ((-3, -3), 60),
        "recuerdo": ((-3, -2), 15), "recuerdo_tarde": ((-3, -2), 15)}


# ------------------------------------------------------------------ helpers
def A(ch, pos, yaw, faces, clips=None, talk=None, look=None, scale=None, path=None):
    a = {"character": ch, "pos": list(pos), "faces": faces}
    if yaw is not None:
        a["yaw"] = yaw
    if clips:
        a["clips"] = clips
    if talk is not None:
        a["talk"] = talk
    if look:
        a["look"] = look
    if scale:
        a["scale"] = scale
    if path:
        a["path"] = path
    return a


def F(*pares):
    """caras: F("worried", (word, "hollowShock"), ...)"""
    out = [{"f": 0, "v": pares[0]}]
    for w, v in pares[1:]:
        out.append({"word": w, "v": v})
    return out


def cam(subj, kind, ang, s=1.0, push=None, whip=0, shake=None, ty=None, dist=None, cy=None, fov=None):
    x, z = subj
    rec = {   # distancia, altura cámara, altura objetivo, fov, push por defecto
        "close": (8.0, 4.7, 4.0, 45, 0.08), "med": (12.0, 4.5, 3.9, 47, 0.18),
        "wide": (26.0, 9.0, 3.4, 47, 0.22), "low": (9.0, 1.2, 4.6, 52, 0.2),
        "high": (15.0, 15.0, 2.0, 47, 0.2),
    }[kind]
    d = (dist or rec[0]) * (s if kind in ("close", "low") else 1)
    tgt = [x, (ty if ty is not None else rec[2] * (s if kind in ("close", "low") else 1)), z]
    a = math.radians(ang)
    pos = [x + math.sin(a) * d, cy if cy is not None else rec[1] * (s if kind == "close" else 1), z + math.cos(a) * d]
    k = push if push is not None else rec[4]
    p1 = [round(p + (t - p) * k, 2) for p, t in zip(pos, tgt)]
    keys = []
    if whip:
        keys.append({"f": -1, "pos": pos, "target": [tgt[0] + whip * math.cos(a), tgt[1], tgt[2] - whip * math.sin(a)]})
        keys.append({"f": 4, "pos": pos, "target": tgt, "ease": "easeOutCubic"})
    else:
        keys.append({"u": 0, "pos": [round(v, 2) for v in pos], "target": tgt})
    keys.append({"u": 1, "pos": p1, "target": tgt, "ease": "linear"})
    c = {"fov": fov or rec[3], "keys": keys}
    if shake:
        c["shake"] = shake
    return c


def impacto(f):
    return {"f0": max(0, f), "f1": max(0, f) + 10, "ampDeg": [0.5, 0.5], "mode": "alt", "decay": 0.75}


def miedo(f, n=25):
    return {"f0": max(0, f), "f1": max(0, f) + n, "ampDeg": [0.25, 0.35], "mode": "random"}


WHOOSH = ["whoosh_quick", "whoosh_air", "whoosh_short"]
POPS = ["pop_soft", "pop_b", "pop_c", "pop_soft_in"]
shots, cnt = [], {"w": 0, "p": 0}
ultimo = {"esc": None}


def S(id_, cue, esc, actors, camera, sfx=None, crowds=None, vfx=None, sound=None):
    sc = json.loads(json.dumps(ESC[esc]))
    props = sc.pop("props", None)
    s = {"id": id_, "cue": cue, **sc, "actors": actors, "camera": camera}
    fx = list(sfx or [])
    if ultimo["esc"] is not None and ultimo["esc"] != esc:
        fx.append({"type": "transition", "at": 0, "gain": -3})
    elif any(k.get("f") == -1 for k in camera["keys"]):
        fx.append({"type": WHOOSH[cnt["w"] % 3], "at": 0}); cnt["w"] += 1
    for a in actors:                         # pop en cada cambio de cara (máx. 1 por toma)
        cambios = [f["word"] for f in a["faces"] if "word" in f]
        if cambios:
            fx.append({"type": POPS[cnt["p"] % 4], "word": cambios[0], "gain": -4}); cnt["p"] += 1
            break
    if esc == "calle_noche":
        fx.append({"type": "fire", "at": 0, "dur": "shot", "gain": -8})
    ultimo["esc"] = esc
    s["sfx"] = fx
    v = list(vfx or [])
    if props:
        v.append(props)
    if v:
        s["vfx"] = v
    if crowds:
        s["crowds"] = crowds
    if sound:
        s["sound"] = sound
    shots.append(s)


def gente(palette="water", n=24, mood="calm", walk=0.5, area=(-9, -45, 6, -14), seed=3, cheer=0):
    c = {"palette": palette, "count": n, "area": list(area), "facing": 0, "walk": walk, "bothWays": True,
         "mood": mood, "seed": seed}
    if cheer:
        c["cheer"] = cheer
    return c


EMBERS = {"type": "embers", "count": 160, "box": [40, 20, 40], "centre": [0, 9, -14], "size": 0.16, "gain": 1.2}

# ------------------------------------------------------------------ tomas
st = SPOT["calle_dia"][0]
# 0 "En este pueblo, si no das las buenas noches, | el Vigilante se lleva tu voz."
c = wi(0)
S("00a_pueblo", c, "calle_dia", [A("sticky", st, 15, F("neutralTalk", (wi(0, 3), "smug")), talk=True)],
  cam(st, "wide", 15), crowds=[gente(n=30)])
c = wi(0, 9)
S("00b_vigilante", c, "campo_noche",
  [A("vigilante", (0, -6), 0, F("blank", (wi(0, 12), "grittedAngry")), scale=GIANT, look=[0, -0.02],
     clips=[{"clip": "reachForward", "word": wi(0, 12)}])],
  cam((0, -6), "low", 8, s=GIANT, shake=[impacto(0), miedo(lf(wi(0, 14), c))]),
  vfx=[EMBERS], sound="hit", sfx=[{"type": "riser_burst", "at": 0, "lead": 2.31}])
# 1 "Aquí todos se despiden antes de dormir. | Todos."
c = wi(1)
S("01a_todos", c, "calle_dia",
  [A("senora", (-4.5, -3), 20, F("happyArcs"), clips=[{"clip": "wave", "word": wi(1, 2)}]),
   A("vecino", (-1.0, -4), -10, F("dotSmile"), clips=[{"clip": "wave", "word": wi(1, 3)}]),
   A("sticky", (-2.8, -0.5), 10, F("neutralTalk", (wi(1, 4), "smug")), talk=True)],
  cam((-2.6, -2.5), "med", 10, whip=8), crowds=[gente(n=30, mood="calm", walk=0.3)])
c = wi(1, 7)
S("01b_todos2", c, "calle_dia", [A("senora", (-4.5, -3), 25, F("bigHappy"), clips=[{"clip": "wave", "at": 0}], talk=True)],
  cam((-4.5, -3), "close", 25))
# 2 "Hasta los bebés dicen buenas noches | antes de aprender a decir mamá."
ck = SPOT["cocina"][0]
c = wi(2)
S("02a_bebe", c, "cocina",
  [A("mama", ck, 60, F("dotSmile", (wi(2, 4), "bigHappy"))),
   A("bebe", (-2.2, -1.4), 70, F("happyArcs", (wi(2, 3), "neutralTalk")), scale=0.5, talk=[wi(2, 3), wi(2, 5)],
     clips=[{"clip": "wave", "word": wi(2, 3)}])],
  cam((-3.2, -2.2), "med", 65))
c = wi(2, 6)
S("02b_bebe2", c, "cocina",
  [A("bebe", (-2.2, -1.4), 70, F("bigHappy", (wi(2, 10), "laugh")), scale=0.5, talk=True)],
  cam((-2.2, -1.4), "close", 70, s=0.5, dist=17, whip=-6), sfx=[{"type": "bell_pop", "word": wi(2, 11)}])
# 3 "Porque dicen que el Vigilante mide tres metros..."
c = wi(3)
S("03_mide", c, "campo_noche",
  [A("vigilante", (0, -6), 10, F("blank", (wi(3, 5), "hollowShock")), scale=GIANT)],
  cam((0, -6), "low", -10, s=GIANT, push=0.25, shake=[miedo(lf(wi(3, 6), c), 30)]),
  vfx=[EMBERS], sound="hit", sfx=[{"type": "thunder", "word": wi(3, 5), "gain": -6}])
# 4 "y que sus ojos brillan en la oscuridad."
c = wi(4)
S("04_ojos", c, "campo_noche",
  [A("vigilante", (0, -6), 5, F("hollowShock", (wi(4, 4), "grittedAngry")), scale=GIANT, look=[0, 0])],
  cam((0, -6), "close", 5, s=GIANT, whip=7), vfx=[EMBERS],
  sfx=[{"type": "riser_fear", "at": 0, "dur": 2.2, "gain": -4}])
# 5 "Nos mudamos un lunes, | y nadie nos avisó."
c = wi(5)
S("05a_mudanza", c, "calle_dia",
  [A("sticky", (-2, 6), None, F("bigHappy", (wi(5, 3), "neutralTalk")), clips=[{"clip": "walk", "at": -100}],
     path=[{"u": 0, "pos": [-2, 6]}, {"u": 1, "pos": [-2.5, 0]}], talk=True),
   A("mama", (0.2, 6.5), None, F("happyArcs"), clips=[{"clip": "walk", "at": -100}],
     path=[{"u": 0, "pos": [0.2, 6.5]}, {"u": 1, "pos": [-0.3, 0.5]}]),
   ],
  cam((-1, 1), "med", 20, dist=16, push=0.3), crowds=[gente(n=26, walk=0.6)],
  vfx=[{"type": "props", "items": [{"shape": "box", "pos": [2.2, 0.9, 1.5], "size": [1.8, 1.8, 1.8], "color": "#c8a070"},
                                   {"shape": "box", "pos": [2.4, 2.3, 1.4], "size": [1.4, 1.0, 1.4], "color": "#b89060"}]}])
c = wi(5, 4)
S("05b_nadie", c, "calle_dia", [A("sticky", (-2.5, 0), 20, F("smug", (wi(5, 6), "worried")), talk=True, look=[0.04, 0])],
  cam((-2.5, 0), "close", 20, whip=-7))
# 6 "Esa noche, mi mamá se durmió sin despedirse."
cq = SPOT["cuarto"][0]
c = wi(6)
S("06_durmio", c, "cuarto",
  [A("mama", (-6.2, -6), 70, F("happyArcs", (wi(6, 4), "deadpan")), clips=[{"clip": "shrugOut", "word": wi(6, 4)}])],
  cam((-6.2, -6), "med", 60, dist=11), sfx=[{"type": "click", "word": wi(6, 5), "gain": 2}])
# 7 "A la mañana siguiente... | no podía decir ni una palabra."
c = wi(7)
S("07a_manana", c, "cocina", [A("mama", ck, 60, F("neutralTalk", (wi(7, 3), "nervous")))],
  cam(ck, "close", 60, whip=6), sfx=[{"type": "clock_tick", "at": 0, "dur": "shot", "gain": -8}])
c = wi(7, 4)
S("07b_sinvoz", c, "cocina",
  [A("mama", ck, 75, F("hollowShock")), A("sticky", (-0.6, -2.6), 280, F("worried", (wi(7, 8), "hollowShock")))],
  cam((-2.6, -1.8), "med", 35, shake=[impacto(lf(wi(7, 9), c))]), sound="hit")
# 8 "¡Mamá! ¿Qué te pasa?"
c = wi(8)
S("08_mama", c, "cocina", [A("sticky", (-1.2, -0.6), 40, F("scream"), clips=[{"clip": "armsUp", "at": 0}])],
  cam((-1.2, -0.6), "close", 55, whip=-6, shake=[impacto(0)]))
# 9 "Corrí a la plaza a pedir ayuda."
c = wi(9)
S("09_corri", c, "calle_dia",
  [A("sticky", (-2, 8), None, F("worried", (wi(9, 5), "nervous")), clips=[{"clip": "runLeaning", "at": -100}],
     path=[{"u": 0, "pos": [-2, 8]}, {"u": 1, "pos": [-2, -14]}])],
  {"fov": 47, "keys": [{"u": 0, "pos": [4, 5, 18], "target": [-2, 3.5, 6]},
                       {"u": 1, "pos": [4, 5, -4], "target": [-2, 3.5, -16], "ease": "linear"}]},
  crowds=[gente(n=30, walk=0.5, area=(-9, -60, 6, -20))], sfx=[{"type": "whoosh_air", "at": 0}])
# 10 "Don Bigotes, el alcalde, | me miró muy serio."
c = wi(10)
S("10a_bigotes", c, "plaza",
  [A("bigotes", (0, 0), 0, F("smug", (wi(10, 2), "angryFrown")), clips=[{"clip": "handUpQuick", "word": wi(10, 2)}])],
  cam((0, 0), "med", 0, whip=8), crowds=[gente("fire", n=16, walk=0.2, area=(-14, -24, 14, -10))])
c = wi(10, 4)
S("10b_serio", c, "plaza",
  [A("bigotes", (0, 0), 0, F("angryFrown"), look=[0, 0]), A("sticky", (-2.2, 4.6), 160, F("nervous"))],
  {"fov": 42, "keys": [{"u": 0, "pos": [-1.0, 5.4, 9.5], "target": [0.3, 4.2, 0]},
                       {"u": 1, "pos": [-0.9, 5.4, 8.3], "target": [0.3, 4.2, 0], "ease": "linear"}]})
# 11 "Es la regla, muchacho. | Nadie rompe la regla."   (habla Don Bigotes)
c = wi(11)
S("11a_regla", c, "plaza",
  [A("bigotes", (0, 0), 5, F("angryTalk"), talk=True, clips=[{"clip": "pointUp", "word": wi(11, 1)}])],
  cam((0, 0), "close", 5, whip=-7))
c = wi(11, 4)
S("11b_nadie", c, "plaza", [A("bigotes", (0, 0), 0, F("grittedAngry"), talk=True, clips=[{"clip": "reachForward", "at": 0}])],
  cam((0, 0), "low", 0, push=0.25, shake=[impacto(lf(wi(11, 5), c))]), sound="hit")
# 12 "Pero yo quería saber la verdad."
c = wi(12)
S("12_verdad", c, "cuarto", [A("sticky", cq, 55, F("angryFrown", (wi(12, 5), "smug")), talk=True)],
  cam(cq, "close", 55), sfx=[{"type": "riser", "at": 0, "lead": 0.3, "gain": -6}])
# 13 "Así que esa noche, apagué la luz... | sin decir buenas noches."
c = wi(13)
S("13a_luz", c, "cuarto",
  [A("sticky", cq, 50, F("smug", (wi(13, 5), "deadpan")), clips=[{"clip": "reachForward", "word": wi(13, 4)}], talk=True)],
  cam(cq, "med", 50, whip=7), sfx=[{"type": "click", "word": wi(13, 4), "gain": 3}])
c = wi(13, 7)
S("13b_silencio", c, "cuarto", [A("sticky", cq, 45, F("deadpan", (wi(13, 9), "worried")), talk=True)],
  cam(cq, "close", 45, push=0.05), sfx=[{"type": "clock_tick", "at": 0, "dur": "shot", "gain": -6}])
# 14 "Y entonces, la puerta se abrió."
c = wi(14)
S("14_puerta", c, "cuarto",
  [A("sticky", (-3.5, -2), 40, F("worried", (wi(14, 5), "scream")), clips=[{"clip": "armsUp", "word": wi(14, 5)}]),
   A("vigilante", (3.5, -8), -40, F("blank"), scale=GIANT)],
  cam((0, -5), "wide", 55, dist=17, shake=[impacto(lf(wi(14, 5), c)), miedo(lf(wi(14, 5), c) + 10)]),
  sound="hit", sfx=[{"type": "knock", "word": wi(14, 3), "gain": 2}, {"type": "riser_fear", "at": 0, "dur": 1.8, "gain": -6}])
# 15 "Era enorme."
c = wi(15)
S("15_enorme", c, "cuarto", [A("vigilante", (3.5, -8), -30, F("blank", (wi(15, 1), "hollowShock")), scale=GIANT)],
  cam((3.5, -8), "low", -10, s=GIANT, push=0.3, shake=[miedo(0, 40)]), sfx=[{"type": "thunder", "at": 0, "gain": -8}])
# 16 "Me miró, | y con una voz muy grave me dijo..."
c = wi(16)
S("16a_miro", c, "cuarto", [A("sticky", (-3.5, -2), 50, F("hollowShock"), look=[0.05, -0.03])],
  cam((-3.5, -2), "close", 55, whip=-6))
c = wi(16, 2)
S("16b_grave", c, "cuarto",
  [A("sticky", (-3.5, -2), 135, F("nervous")), A("vigilante", (1.5, -7), -40, F("blank"), scale=GIANT)],
  {"fov": 44, "keys": [{"u": 0, "pos": [-7.5, 6.2, 3.5], "target": [1.5, 6.6, -7]},
                       {"u": 1, "pos": [-6.8, 6.2, 2.5], "target": [1.5, 6.7, -7], "ease": "linear"}]})
# 17 "¿Por qué nadie me dice buenas noches a mí?"  (habla el Vigilante)
c = wi(17)
S("17_pregunta", c, "cuarto", [A("vigilante", (1.5, -7), -20, F("worried"), scale=GIANT, talk=True)],
  cam((1.5, -7), "close", 20, s=GIANT, dist=8.5))
# 18 "Hace muchos años, él cuidaba el pueblo cada noche."  (recuerdo)
c = wi(18)
S("18_antes", c, "recuerdo",
  [A("vigilante", (-2, 6), None, F("dotSmile", (wi(18, 4), "happyArcs")), scale=GIANT, clips=[{"clip": "walk", "at": -100}],
     path=[{"u": 0, "pos": [-2, 6]}, {"u": 1, "pos": [-2.5, -3]}])],
  cam((-2.2, 1), "wide", 20, dist=24, push=0.25), crowds=[gente(n=20, walk=0.3, mood="calm")],
  sfx=[{"type": "transition", "at": 0}])
# 19 "Pero los niños se burlaban | de lo alto que era."
c = wi(19)
S("19a_burla", c, "recuerdo",
  [A("vigilante", (-3, -4), 20, F("blank", (wi(19, 3), "worried")), scale=GIANT),
   A("nino", (1.5, 1), -40, F("laugh"), scale=0.65, clips=[{"clip": "handUpQuick", "word": wi(19, 3)}]),
   A("amiga", (3.2, 0), -30, F("laugh"), scale=0.65, clips=[{"clip": "cheerLoop", "at": 0}])],
  cam((-0.2, -1.5), "med", 15, dist=15, whip=7), sfx=[{"type": "crowd_cheer", "word": wi(19, 3), "gain": -8}])
c = wi(19, 5)
S("19b_alto", c, "recuerdo", [A("nino", (1.5, 1), -20, F("laugh", (wi(19, 8), "bigHappy")), scale=0.65, talk=True,
                               clips=[{"clip": "pointUp", "at": 0}])],
  cam((1.5, 1), "close", 0, s=0.65, dist=13.5, whip=-6))
# 20 "Y nadie, nunca, le dio las buenas noches."
c = wi(20)
S("20_solo", c, "recuerdo_tarde",
  [A("vigilante", (-2.5, -1), 200, F("worried"), scale=GIANT, clips=[{"clip": "walk", "at": -100}],
     path=[{"u": 0, "pos": [-2.5, -1]}, {"u": 1, "pos": [-3, -12]}])],
  cam((-2.6, -4), "med", 10, dist=16, push=0.1), sfx=[{"type": "rain_light", "at": 0, "dur": "shot", "gain": -14}])
# 21 "Él no robaba voces. | Las guardaba, para no estar solo."
c = wi(21)
S("21a_noroba", c, "cuarto",
  [A("sticky", (-3.5, -1.5), 120, F("worried", (wi(21, 2), "blank"))),
   A("vigilante", (1.5, -6), -50, F("worried"), scale=GIANT)],
  cam((-1, -4), "med", 55, dist=17), sfx=[{"type": "transition", "at": 0, "gain": -3}])
c = wi(21, 4)
S("21b_solo", c, "cuarto", [A("vigilante", (1.5, -6), -25, F("worried", (wi(21, 8), "deadpan")), scale=GIANT)],
  cam((1.5, -6), "close", 25, s=GIANT, dist=8.5, whip=6))
# 22 "¿Y la regla? La inventó Don Bigotes, | para que todos le tuvieran miedo."
c = wi(22)
S("22a_invento", c, "plaza", [A("bigotes", (0, 0), -10, F("smug"), clips=[{"clip": "shrugOut", "word": wi(22, 3)}])],
  cam((0, 0), "med", -10, whip=-8), crowds=[gente("fire", n=16, walk=0.2, area=(-14, -24, 14, -10), seed=8)],
  sound="hit")
c = wi(22, 7)
S("22b_miedo", c, "plaza", [A("bigotes", (0, 0), 0, F("smug", (wi(22, 11), "laugh")), clips=[{"clip": "castUpBoth", "word": wi(22, 11)}])],
  cam((0, 0), "low", 0, push=0.25), sfx=[{"type": "riser", "at": 0, "lead": 0.2, "gain": -6}])
# 23 "Así que hice algo que nadie había hecho."
c = wi(23)
S("23_hice", c, "cuarto", [A("sticky", (-3.5, -1.5), 45, F("smug", (wi(23, 3), "bigHappy")), talk=True)],
  cam((-3.5, -1.5), "close", 45, whip=7))
# 24 "Buenas noches, Vigilante."
c = wi(24)
S("24_buenas", c, "cuarto",
  [A("sticky", (-3.5, -1.5), 100, F("bigHappy"), talk=True, clips=[{"clip": "wave", "at": 0}]),
   A("vigilante", (1.5, -6), -50, F("blank", (wi(24, 2), "worried")), scale=GIANT)],
  cam((-1, -4), "med", 65, dist=16), sfx=[{"type": "bell_pop", "word": wi(24, 2)}])
# 25 "Por primera vez en cien años, sonrió."
c = wi(25)
S("25_sonrio", c, "cuarto",
  [A("vigilante", (1.5, -6), -30, F("worried", (wi(25, 6), "bigHappy")), scale=GIANT,
     clips=[{"clip": "castUpBoth", "word": wi(25, 6)}])],
  cam((1.5, -6), "close", 30, s=GIANT, dist=8.5, push=0.1), sfx=[{"type": "riser_burst", "word": wi(25, 6), "lead": 2.31, "gain": -4}])
# 26 "A la mañana siguiente, mi mamá volvió a hablar."
c = wi(26)
S("26_habla", c, "cocina",
  [A("mama", ck, 60, F("bigHappy", (wi(26, 6), "laugh")), talk=[wi(26, 6), wi(26, 8)],
     clips=[{"clip": "armsUp", "word": wi(26, 6)}]),
   A("sticky", (-0.6, -2.6), 280, F("laugh"), clips=[{"clip": "cheerLoop", "word": wi(26, 6)}])],
  cam((-2.6, -1.8), "med", 35, whip=-7), sfx=[{"type": "crowd_cheer", "word": wi(26, 7), "gain": -10}])
# 27 "Y ahora, todo el pueblo | le da las buenas noches al Vigilante."
c = wi(27)
S("27a_pueblo", c, "calle_noche",
  [A("vigilante", (-3, -6), 15, F("bigHappy"), scale=GIANT, clips=[{"clip": "wave", "word": wi(27, 3)}]),
   A("sticky", (0.5, -1), -20, F("laugh"), clips=[{"clip": "wave", "at": 0}])],
  cam((-1.5, -4), "med", 15, dist=18), crowds=[gente("fire", n=40, mood="cheer", walk=0, cheer=0.5,
                                                    area=(-9, -30, 7, -10), seed=5)])
c = wi(27, 5)
S("27b_todos", c, "calle_noche",
  [A("vigilante", (-3, -6), 15, F("laugh"), scale=GIANT, clips=[{"clip": "cheerLoop", "at": 0}])],
  {"fov": 47, "keys": [{"u": 0, "pos": [-1, 6, 8], "target": [-3, 6, -6]},
                       {"u": 0.5, "pos": [6, 16, 30], "target": [-3, 4, -16], "ease": "easeOutQuad"},
                       {"u": 1, "pos": [6.3, 16.3, 31], "target": [-3, 4, -16], "ease": "linear"}]},
  crowds=[gente("fire", n=70, mood="cheer", walk=0, cheer=0.6, area=(-9, -40, 8, -10), seed=6)],
  sfx=[{"type": "crowd_cheer", "at": 0, "gain": -6}])
# 28 "Bueno... a los que no le dan like, | todavía los visita."
c = wi(28)
S("28a_like", c, "campo_noche",
  [A("vigilante", (0, -6), 0, F("happyArcs", (wi(28, 1), "smug")), scale=GIANT, look=[0, 0])],
  cam((0, -6), "close", 0, s=GIANT, whip=8), vfx=[EMBERS], sfx=[{"type": "riser_fear", "at": 0, "dur": 2.5, "gain": -5}])
c = wi(28, 8)
S("28b_visita", c, "campo_noche",
  [A("vigilante", (0, -6), 0, F("grittedAngry"), scale=GIANT, clips=[{"clip": "reachForward", "at": 0}])],
  cam((0, -6), "low", 0, s=GIANT, push=0.3, shake=[impacto(0), miedo(10, 30)]), vfx=[EMBERS], sound="hit",
  sfx=[{"type": "thunder", "at": 0, "gain": -4}])
# 29 "¡Suscríbete y no olvides decir buenas noches!"
c = wi(29)
S("29_suscribete", c, "calle_dia",
  [A("sticky", st, 15, F("bigHappy", (wi(29, 4), "laugh")), talk=True, clips=[{"clip": "wave", "at": 0}])],
  cam(st, "close", 15, whip=-7), crowds=[gente(n=24)], sfx=[{"type": "bell_pop", "at": 0}])

story = {"audio": "audio/vigilante.wav", "names": ["Vigilante", "Don", "Bigotes"], "sfx": [], "endHoldFrames": 30,
         "shots": shots}
(HERE / "story.json").write_text(json.dumps(story, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(shots), "tomas")

# ------------------------------------------------------------- música por actos
ACTOS = [(0, "misterio"), (2, "comico"), (3, "tension"), (5, "misterio"), (7, "tension"), (13, "silencio"),
         (14, "tension"), (17, "triste"), (22, "tension"), (23, "calido"), (28, "tension"), (29, "calido")]
SR = 48000
MUS = HERE.parents[2] / "assets" / "musica"


def dec(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").astype(np.float32) / 32768


total = W[-1]["end"] + 2.0
mus = np.zeros(int(total * SR), np.float32)
for k, (line, acto) in enumerate(ACTOS):
    a = W[L[line]]["t"] - (0.3 if k else 0)
    b = (W[L[ACTOS[k + 1][0]]]["t"] if k + 1 < len(ACTOS) else total)
    if acto == "silencio":
        continue
    m = dec(MUS / f"{acto}.wav")
    n = int((b - a + 0.5) * SR)
    seg = np.tile(m, n // len(m) + 1)[:n].copy()
    fi = int(0.3 * SR)
    seg[:fi] *= np.linspace(0, 1, fi); seg[-fi:] *= np.linspace(1, 0, fi)
    i = int(a * SR)
    mus[i:i + len(seg)] += seg[: len(mus) - i]
with wave.open(str(HERE / "audio" / "music.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mus, -1, 1) * 32767).astype("<i2").tobytes())
print("música por actos:", ", ".join(a for _, a in ACTOS))
