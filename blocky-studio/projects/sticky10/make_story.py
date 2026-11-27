"""Genera story.json de la prueba de 10 s (Sticky elegante, "el Vigilante se lleva tu voz").
Uso: python projects/sticky10/make_story.py   (desde blocky-studio)"""
import json
from pathlib import Path

HERE = Path(__file__).parent
W = json.loads((HERE / "words.json").read_text(encoding="utf-8"))["words"]
FPS = 30


def lf(word, cue):
    """cuadro local de una palabra dentro de la toma que empieza en 'cue'"""
    return round(W[word]["t"] * FPS) - round(W[cue]["t"] * FPS)


INTERIOR = {"lights": {"hemi": {"sky": "#e6ddd2", "ground": "#8a7a6a", "intensity": 1.9},
                       "key": {"color": "#fff0dc", "intensity": 1.8, "from": [0.5, 0.8, 0.7], "shadow": True}}}
NOCHE_DENTRO = {"lights": {"hemi": {"sky": "#4a5a8a", "ground": "#1a1a2a", "intensity": 0.9},
                           "key": {"color": "#9fb4ff", "intensity": 1.1, "from": [0.6, 0.7, 0.8], "shadow": True}}}
HAZE = {"fog": {"color": "#c4d2ec", "density": 0.0035}}

ESC = {
    "calle_dia": dict(set="fireStreet", look="DAY_SUN", lookOverrides=HAZE,
                      shadow={"focus": [-3, 0, -8], "extent": 40}, setParams={"houses": {"lit": 0.1}}),
    "calle_tarde": dict(set="fireStreet", look="DUSK_MAGENTA", shadow={"focus": [-3, 0, -8], "extent": 40},
                        setParams={"houses": {"lit": 0.5}}),
    "campo_noche": dict(set="nightField", look="NIGHT_EMBER", shadow={"focus": [0, 0, -6], "extent": 40}),
    "cocina_noche": dict(set="kitchen", look="INTERIOR_NEUTRAL", lookOverrides=NOCHE_DENTRO,
                         shadow={"focus": [-4, 3, -3], "extent": 26}, setParams={"chairs": []}),
}


def A(ch, x, z, yaw, faces, clips=None, talk=None, look=None, **kw):
    a = {"character": ch, "pos": [x, z], "faces": faces}
    if yaw is not None:
        a["yaw"] = yaw
    if clips:
        a["clips"] = clips
    if talk is not None:
        a["talk"] = talk
    if look:
        a["look"] = look
    a.update(kw)
    return a


def cam(p0, p1, target, fov=47, ease="linear", shake=None, whip=None):
    keys = []
    if whip:   # whip-in: arranca mirando a un lado y llega al sujeto en 4 cuadros
        keys.append({"f": -1, "pos": p0, "target": [target[0] + whip, target[1], target[2]]})
        keys.append({"f": 4, "pos": p0, "target": target, "ease": "easeOutCubic"})
    else:
        keys.append({"u": 0, "pos": p0, "target": target})
    keys.append({"u": 1, "pos": p1, "target": target, "ease": ease})
    c = {"fov": fov, "keys": keys}
    if shake:
        c["shake"] = shake
    return c


def push(pos, target, k):
    """acerca la cámara un k (0.2 = 20 %) hacia el objetivo"""
    return [round(p + (t - p) * k, 2) for p, t in zip(pos, target)]


shots = []


def S(id_, cue, esc, actors, camera, sfx=None, crowds=None, vfx=None, sound=None):
    s = {"id": id_, "cue": cue, **json.loads(json.dumps(ESC[esc])), "actors": actors, "camera": camera}
    if sfx:
        s["sfx"] = sfx
    if crowds:
        s["crowds"] = crowds
    if vfx:
        s["vfx"] = vfx
    if sound:
        s["sound"] = sound
    shots.append(s)


# 1. "En este pueblo," — plano general de la calle con gente caminando
p = [6, 7.5, 22]; t = [-3.5, 3.6, -4]
S("1_pueblo", 0, "calle_dia",
  [A("sticky", -3.5, -2, 15, [{"f": 0, "v": "neutralTalk"}, {"word": 2, "v": "smug"}], talk=True)],
  cam(p, push(p, t, 0.25), t),
  crowds=[{"palette": "water", "count": 26, "area": [-9, -40, 4, -12], "facing": 0, "walk": 0.6,
           "bothWays": True, "mood": "calm", "seed": 4}],
  sfx=[{"type": "transition", "at": 0}, {"type": "pop_soft_in", "word": 2}])

# 2. "si no das las buenas noches," — primer plano, Sticky explica la regla
c = 3; t = [-0.5, 4.0, 1]; p = [3.0, 4.7, 8.5]
S("2_regla", c, "calle_dia",
  [A("sticky", -0.5, 1, 15, [{"f": 0, "v": "angryTalk"}, {"word": 7, "v": "smug"}],
     talk=True)],
  cam(p, push(p, t, 0.08), t, whip=8),
  sfx=[{"type": "whoosh_quick", "at": 0}, {"type": "click", "word": 5}])

# 3. "el Vigilante se lleva tu voz." — contrapicado al Vigilante de noche, ojos y temblor
c = 9; t = [0, 4.8, -6]; p = [1.2, 1.2, 3.5]
S("3_vigilante", c, "campo_noche",
  [A("vigilante", 0, -6, 0, [{"f": 0, "v": "blank"}, {"word": 12, "v": "grittedAngry"}],
     clips=[{"clip": "reachForward", "word": 12}], talk=[12, 14], look=[0, -0.02])],
  cam(p, push(p, t, 0.22), t, fov=50,
      shake=[{"f0": 0, "f1": 10, "ampDeg": [0.5, 0.5], "mode": "alt", "decay": 0.75},
             {"f0": lf(14, c), "f1": lf(14, c) + 20, "ampDeg": [0.25, 0.35], "mode": "random"}]),
  vfx=[{"type": "embers", "count": 160, "box": [40, 20, 40], "centre": [0, 9, -14], "size": 0.16, "gain": 1.2}],
  sound="hit", sfx=[{"type": "riser_burst", "at": 0, "lead": 2.31}, {"type": "pop_b", "word": 14}])

# 4. "Nadie me avisó." — en la calle al atardecer: mamá y Don Bigotes pasan sin mirarlo
c = 15; t = [-1.0, 3.9, -4.5]; p = [4.5, 4.6, 10]
S("4_nadie", c, "calle_tarde",
  [A("sticky", -3.5, -2, 20, [{"f": 0, "v": "worried"}, {"word": 17, "v": "blank"}],
     clips=[{"clip": "handUpQuick", "word": 17}], talk=True, look=[0.04, 0]),
   A("mama", 0.5, -5, None, [{"f": 0, "v": "happyArcs"}], clips=[{"clip": "walk", "at": -100}],
     path=[{"u": 0, "pos": [3.5, -6]}, {"u": 1, "pos": [0.5, -7]}]),
   A("bigotes", 3.5, -8, None, [{"f": 0, "v": "deadpan"}], clips=[{"clip": "walk", "at": -100}],
     path=[{"u": 0, "pos": [6.0, -9.5]}, {"u": 1, "pos": [3.0, -10.5]}])],
  cam(p, push(p, t, 0.15), t),
  crowds=[{"palette": "fire", "count": 18, "area": [-9, -45, 6, -16], "facing": 0, "walk": 0.5, "mood": "calm", "seed": 9}],
  sfx=[{"type": "whoosh_air", "at": 0}, {"type": "pop_c", "word": 17}])

# 5. "Esa noche apagué la luz" — cocina de noche, primer plano, clic en "apagué"
c = 18; t = [-4, 4.0, -3]; p = [1.8, 4.7, 2.4]
S("5_luz", c, "cocina_noche",
  [A("sticky", -4, -3, 45, [{"f": 0, "v": "smug"}, {"word": 20, "v": "neutralTalk"}],
     clips=[{"clip": "reachForward", "word": 20}], talk=True, look=[0.03, -0.01])],
  cam(p, push(p, t, 0.08), t, fov=42),
  sfx=[{"type": "transition", "at": 0}, {"type": "click", "word": 20, "gain": 3}])

# 6. "sin decir nada." — plano medio, la cocina a oscuras
c = 23; t = [-4, 3.9, -3]; p = [8.5, 4.5, 3]
S("6_nada", c, "cocina_noche",
  [A("sticky", -4, -3, 50, [{"f": 0, "v": "deadpan"}, {"word": 25, "v": "worried"}], talk=True)],
  cam(p, push(p, t, 0.2), t, fov=42, whip=6),
  sfx=[{"type": "whoosh_short", "at": 0}, {"type": "clock_tick", "at": 0, "dur": "shot", "gain": -6}])

# 7. "Y entonces," — primer plano con temblor de miedo
c = 26; t = [-4, 4.0, -3]; p = [-0.6, 4.7, 4.6]
S("7_entonces", c, "cocina_noche",
  [A("sticky", -4, -3, 30, [{"f": 0, "v": "worried"}, {"word": 27, "v": "hollowShock"}], talk=True)],
  cam(p, push(p, t, 0.08), t, fov=42,
      shake=[{"f0": 0, "f1": 25, "ampDeg": [0.25, 0.35], "mode": "random"}]),
  sfx=[{"type": "riser_fear", "at": 0, "dur": 1.6, "gain": -3}])

# 8. "alguien tocó la puerta." — el Vigilante aparece en la cocina; Sticky grita
c = 28; t = [-1.8, 3.8, -5.0]; p = [9.5, 4.8, 8.5]
S("8_puerta", c, "cocina_noche",
  [A("sticky", -4.2, -2.8, 70, [{"f": 0, "v": "nervous"}, {"word": 29, "v": "scream"}],
     clips=[{"clip": "armsUp", "word": 29}]),
   A("vigilante", 0.3, -7.2, -35, [{"f": 0, "v": "blank"}, {"word": 31, "v": "grittedAngry"}], look=[-0.04, 0])],
  cam(p, push(p, t, 0.22), t, fov=44,
      shake=[{"f0": lf(29, c), "f1": lf(29, c) + 10, "ampDeg": [0.5, 0.5], "mode": "alt", "decay": 0.75},
             {"f0": lf(31, c), "f1": lf(31, c) + 30, "ampDeg": [0.25, 0.35], "mode": "random"}]),
  sound="hit", sfx=[{"type": "knock", "word": 29, "gain": 2}, {"type": "knock", "word": 30, "gain": 2},
                    {"type": "pop_soft", "word": 31}])

story = {"audio": "audio/sticky10.wav", "names": ["Vigilante"], "sfx": [], "endHoldFrames": 24, "shots": shots}
(HERE / "story.json").write_text(json.dumps(story, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(shots), "tomas")
