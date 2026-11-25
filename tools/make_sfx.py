"""Sintetiza efectos de sonido libres de derechos en assets/sfx/ (WAV 44.1 kHz mono).

Son placeholders hechos con matemáticas: puedes reemplazar cualquier archivo por
uno tuyo con el mismo nombre. Uso:  python tools/make_sfx.py
"""
from pathlib import Path
import wave
import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"
rng = np.random.default_rng(7)


def t(sec):
    return np.linspace(0, sec, int(SR * sec), endpoint=False)


def env(n, attack=0.005, decay=None):
    x = np.arange(n) / SR
    a = np.clip(x / attack, 0, 1)
    d = np.exp(-x / decay) if decay else 1.0
    return a * d


def sweep(f0, f1, sec, shape="sine"):
    x = t(sec)
    f = np.geomspace(f0, f1, len(x))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if shape == "sine" else np.sign(np.sin(ph)) * 0.6


def lowpass(x, alpha):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += alpha * (v - acc); y[i] = acc
    return y


def pop():
    s = sweep(900, 250, 0.09) * env(int(SR * 0.09), 0.002, 0.03)
    return s


def whoosh():
    n = int(SR * 0.45)
    noise = rng.standard_normal(n)
    sh = np.sin(np.linspace(0, np.pi, n)) ** 2
    return lowpass(noise, 0.08) * sh * 2.5


def boom():
    x = t(1.4)
    s = np.sin(2 * np.pi * np.cumsum(np.geomspace(110, 35, len(x))) / SR)
    s += lowpass(rng.standard_normal(len(x)), 0.02) * 2
    return np.tanh(s * env(len(x), 0.003, 0.35) * 2.5)


def ding():
    x = t(1.2)
    s = sum(np.sin(2 * np.pi * f * x) * a for f, a in [(1320, 1), (2640, .4), (3960, .2)])
    return s * env(len(x), 0.002, 0.3) * 0.6


def boing():
    x = t(0.6)
    f = 220 + 140 * np.sin(2 * np.pi * 9 * x) * np.exp(-x * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), 0.004, 0.25)


def golpe():
    n = int(SR * 0.25)
    s = lowpass(rng.standard_normal(n), 0.15) * 3 + sweep(160, 60, 0.25)
    return np.tanh(s * env(n, 0.001, 0.05) * 2)


def sorpresa():  # "stinger" ascendente
    return sweep(200, 1400, 0.5, "square") * env(int(SR * 0.5), 0.01, 0.4) * 0.5


def tictac():
    out = np.zeros(int(SR * 1.0))
    for k, f in enumerate([2200, 1600, 2200, 1600]):
        c = np.sin(2 * np.pi * f * t(0.02)) * env(int(SR * 0.02), 0.0005, 0.005)
        i = int(k * 0.25 * SR); out[i:i + len(c)] += c
    return out


def ronquido():
    x = t(1.6)
    s = lowpass(rng.standard_normal(len(x)), 0.05) * (0.5 + 0.5 * np.sin(2 * np.pi * 35 * x))
    return s * np.sin(np.linspace(0, np.pi, len(x))) * 2


def triste():  # trombón triste: wah wah wah waaah
    out = []
    for f, d in [(392, .35), (370, .35), (349, .35), (330, 1.0)]:
        x = t(d)
        vib = 1 + (0.02 * np.sin(2 * np.pi * 6 * x) if d > .5 else 0)
        s = np.sign(np.sin(2 * np.pi * f * vib * x)) * 0.3
        out.append(lowpass(s, 0.15) * env(len(x), 0.03, d))
    return np.concatenate(out) * 2


SFX = dict(pop=pop, whoosh=whoosh, boom=boom, ding=ding, boing=boing, golpe=golpe,
           sorpresa=sorpresa, tictac=tictac, ronquido=ronquido, triste=triste)


def save(name, s):
    s = s / (np.max(np.abs(s)) + 1e-9) * 0.9
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for k, fn in SFX.items():
        if not (OUT / f"{k}.wav").exists():   # no pisa sonidos que pusiste tú
            save(k, fn())
    print("sfx:", ", ".join(SFX))
