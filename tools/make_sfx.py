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


# ----------------------------------------------- efectos "cinematográficos"

def ruido_banda(n, a_lo, a_hi):
    """Ruido pasabanda: lowpass(a_hi) - lowpass(a_lo)."""
    r = rng.standard_normal(n)
    return lowpass(r, a_hi) - lowpass(r, a_lo)


def tiza():      # tiza / arañazo en pizarrón
    n = int(SR * 0.9)
    x = np.arange(n) / SR
    s = ruido_banda(n, 0.05, 0.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * x) ** 2)
    s += 0.25 * np.sin(2 * np.pi * (2400 + 300 * np.sin(2 * np.pi * 5 * x)) * x)
    return s * np.clip(x / 0.02, 0, 1) * np.clip((0.9 - x) / 0.1, 0, 1)


def lapiz():     # lápiz escribiendo rápido
    n = int(SR * 1.2)
    x = np.arange(n) / SR
    trazos = (np.sin(2 * np.pi * 6.5 * x + np.sin(2 * np.pi * 1.3 * x) * 2) > -0.2).astype(float)
    return ruido_banda(n, 0.08, 0.7) * lowpass(trazos, 0.01) * 0.8


def papel():     # papel arrugándose
    n = int(SR * 0.8)
    s = np.zeros(n)
    for _ in range(90):
        i = rng.integers(0, n - 800)
        k = rng.integers(80, 700)
        s[i:i + k] += ruido_banda(k, 0.1, 0.8) * np.exp(-np.arange(k) / (k / 3)) * rng.uniform(0.3, 1)
    return s


def borrador():
    n = int(SR * 0.7)
    x = np.arange(n) / SR
    vaiven = np.abs(np.sin(2 * np.pi * 4.5 * x))
    return lowpass(rng.standard_normal(n), 0.12) * vaiven * 1.4


def puerta():    # puerta que rechina
    x = t(1.3)
    f = 520 + 260 * np.sin(2 * np.pi * 0.7 * x) + 60 * np.sin(2 * np.pi * 23 * x)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25
    s = lowpass(s, 0.25) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 3 * x)))
    return s * np.clip(x / 0.05, 0, 1) * np.clip((1.3 - x) / 0.2, 0, 1)


def portazo():
    n = int(SR * 0.9)
    s = lowpass(rng.standard_normal(n), 0.05) * 3 + sweep(90, 45, 0.9)
    return np.tanh(s * env(n, 0.001, 0.12) * 3)


def clic():      # interruptor / bombilla
    c = np.sin(2 * np.pi * 3200 * t(0.012)) * env(int(SR * 0.012), 0.0003, 0.003)
    c2 = np.sin(2 * np.pi * 1800 * t(0.02)) * env(int(SR * 0.02), 0.0003, 0.005) * 0.6
    out = np.zeros(int(SR * 0.12)); out[:len(c)] += c; out[int(SR * 0.05):int(SR * 0.05) + len(c2)] += c2
    return out


def boom_grave():  # impacto de cine
    x = t(2.5)
    s = np.sin(2 * np.pi * np.cumsum(np.geomspace(70, 28, len(x))) / SR) * 1.5
    s += lowpass(rng.standard_normal(len(x)), 0.01) * 3
    return np.tanh(s * env(len(x), 0.002, 0.7) * 2)


def riser():     # sube la tensión (1.8 s) y corta
    x = t(1.8)
    s = ruido_banda(len(x), 0.02, 0.5) * (x / 1.8) ** 2 * 1.5
    s += 0.35 * np.sin(2 * np.pi * np.cumsum(np.geomspace(200, 1600, len(x))) / SR) * (x / 1.8) ** 3
    return s


def latido():
    out = np.zeros(int(SR * 1.0))
    for at, v in ((0.0, 1.0), (0.22, 0.7)):
        x = t(0.18)
        b = np.sin(2 * np.pi * np.cumsum(np.geomspace(70, 40, len(x))) / SR) * env(len(x), 0.002, 0.05) * v
        i = int(at * SR); out[i:i + len(b)] += b
    return out


def viento():
    n = int(SR * 3.0)
    x = np.arange(n) / SR
    s = lowpass(rng.standard_normal(n), 0.03) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.4 * x))
    return s * np.sin(np.linspace(0, np.pi, n))


def pasos():
    out = np.zeros(int(SR * 1.6))
    for k in range(4):
        n = int(SR * 0.1)
        st = lowpass(rng.standard_normal(n), 0.2) * env(n, 0.001, 0.02) + sweep(140, 70, 0.1) * env(n, 0.001, 0.03)
        i = int(k * 0.4 * SR); out[i:i + n] += st * (1 if k % 2 else 0.8)
    return out


def campana():
    x = t(2.5)
    s = sum(np.sin(2 * np.pi * f * x) * a * np.exp(-x / d)
            for f, a, d in ((523, 1, 1.2), (1046, .5, .8), (1568, .35, .5), (2093, .2, .3), (1244, .15, .6)))
    return s * env(len(x), 0.002)


def transicion():  # whoosh corto y suave para los cortes de escena
    n = int(SR * 0.28)
    sh = np.sin(np.linspace(0, np.pi, n)) ** 3
    return ruido_banda(n, 0.02, 0.25) * sh * 2


def corte_seco():  # "sound drop": golpe sordo que corta el sonido antes de un susto
    n = int(SR * 0.4)
    return np.tanh(sweep(120, 30, 0.4) * env(n, 0.001, 0.08) * 3)


def risa_eco():    # "jajaja" sintético con eco (flashbacks)
    out = np.zeros(int(SR * 2.2))
    for k in range(5):
        x = t(0.13)
        f = 260 - k * 12
        s = np.sign(np.sin(2 * np.pi * f * x)) * 0.3 * np.sin(np.linspace(0, np.pi, len(x)))
        s = lowpass(s, 0.2)
        i = int(k * 0.18 * SR); out[i:i + len(s)] += s
    eco = out.copy()
    for d, g in ((0.25, 0.5), (0.5, 0.3), (0.75, 0.15)):
        j = int(d * SR); out[j:] += eco[:-j] * g
    return out


SFX = dict(pop=pop, whoosh=whoosh, boom=boom, ding=ding, boing=boing, golpe=golpe,
           sorpresa=sorpresa, tictac=tictac, ronquido=ronquido, triste=triste,
           tiza=tiza, lapiz=lapiz, papel=papel, borrador=borrador, puerta=puerta, portazo=portazo,
           clic=clic, boom_grave=boom_grave, riser=riser, latido=latido, viento=viento, pasos=pasos,
           campana=campana, transicion=transicion, corte_seco=corte_seco, risa_eco=risa_eco)


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
