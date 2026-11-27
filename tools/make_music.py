"""Música de fondo por actos, sintetizada con numpy (libre de derechos) en assets/musica/.

Cada pista es un loop de ~16-20 s que build.py repite y cruza con la siguiente:
  misterio  -> gancho y reglas (pizzicato en menor + pad suave + celesta)
  tension   -> aparición / miedo (drone grave, ostinato de cuerdas, latidos)
  triste    -> flashback / giro emocional (piano lento en menor)
  calido    -> resolución (acordes mayores luminosos + campanitas)
  comico    -> momentos graciosos (bajo saltarín + pizzicato mayor)
Puedes reemplazar cualquiera por un .wav tuyo con el mismo nombre.
Uso:  python tools/make_music.py   (--forzar para regenerar)
"""
from pathlib import Path
import sys
import wave
import numpy as np

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "assets" / "musica"
rng = np.random.default_rng(11)


def hz(n):           # nota MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(x, a):
    """Filtro de un polo vectorizado por bloques (suficiente para suavizar)."""
    k = int(max(1, round(1 / a)))
    ker = np.exp(-np.arange(k * 5) / k)
    ker /= ker.sum()
    return np.convolve(x, ker)[: len(x)]


def nota(f, dur, kind="pluck", vel=1.0):
    n = int(SR * dur)
    x = np.arange(n) / SR
    if kind == "pluck":        # pizzicato
        s = sum(np.sin(2 * np.pi * f * h * x) / h ** 1.6 for h in (1, 2, 3, 4))
        e = np.exp(-x / 0.16) * np.clip(x / 0.003, 0, 1)
    elif kind == "piano":
        s = sum(np.sin(2 * np.pi * f * h * x * (1 + 0.0004 * h)) * a for h, a in ((1, 1), (2, .45), (3, .25), (4, .12), (5, .06)))
        e = np.exp(-x / 0.9) * np.clip(x / 0.004, 0, 1)
    elif kind == "celesta":
        s = np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * f * 4 * x) * np.exp(-x / 0.08)
        e = np.exp(-x / 0.5) * np.clip(x / 0.002, 0, 1)
    elif kind == "pad":
        s = sum(np.sin(2 * np.pi * f * (1 + d) * x) for d in (-0.004, 0, 0.004)) / 3
        s += 0.3 * np.sin(2 * np.pi * f * 2 * x)
        a = min(0.6, dur / 3)
        e = np.clip(x / a, 0, 1) * np.clip((dur - x) / a, 0, 1)
    elif kind == "cuerda":     # cuerda grave áspera (diente de sierra filtrado)
        s = 2 * ((f * x) % 1) - 1
        s = lowpass(s, 0.08)
        e = np.clip(x / 0.01, 0, 1) * np.exp(-x / 0.25)
    elif kind == "bajo":
        s = np.sin(2 * np.pi * f * x) + 0.3 * np.sin(2 * np.pi * 2 * f * x)
        e = np.exp(-x / 0.22) * np.clip(x / 0.004, 0, 1)
    else:
        raise ValueError(kind)
    return s * e * vel


class Pista:
    def __init__(self, bpm, compases, tiempos=4):
        self.beat = 60 / bpm
        self.dur = self.beat * tiempos * compases
        self.x = np.zeros(int(SR * self.dur) + SR * 3)

    def add(self, beat, f, dur_beats, kind, vel=1.0):
        s = nota(f, dur_beats * self.beat if kind != "pluck" else 0.9, kind, vel)
        i = int(beat * self.beat * SR)
        self.x[i:i + len(s)] += s[: max(0, len(self.x) - i)]

    def ruido(self, beat, dur, vel, a=0.3):
        n = int(dur * SR)
        s = lowpass(rng.standard_normal(n), a) * np.exp(-np.arange(n) / (SR * dur / 4)) * vel
        i = int(beat * self.beat * SR)
        self.x[i:i + n] += s[: max(0, len(self.x) - i)]

    def fin(self):
        """Dobla la cola del final sobre el inicio para que el loop no tenga corte."""
        n = int(SR * self.dur)
        y = self.x[:n].copy()
        cola = self.x[n:]
        y[: len(cola)] += cola
        return y


ACORDES = {  # nota raíz MIDI y tipo
    "m": (0, 3, 7), "M": (0, 4, 7), "dis": (0, 3, 6),
}


def acorde(root, tipo, octava=0):
    return [root + 12 * octava + i for i in ACORDES[tipo]]


def misterio():
    p = Pista(96, 8)
    prog = [(50, "m"), (46, "M"), (43, "m"), (45, "M")] * 2          # Dm Bb Gm A
    for c, (r, t) in enumerate(prog):
        b0 = c * 4
        ch = acorde(r, t, 1)
        for k, n in enumerate([ch[0], ch[1], ch[2], ch[1], ch[0] + 12, ch[2], ch[1], ch[2]]):
            p.add(b0 + k * 0.5, hz(n), 0.5, "pluck", 0.55 if k % 2 else 0.8)
        for n in acorde(r, t, 0):
            p.add(b0, hz(n), 4, "pad", 0.12)
        p.add(b0, hz(r - 12), 4, "bajo", 0.5)
        if c % 2 == 1:
            p.add(b0 + 2.5, hz(ch[2] + 24), 1, "celesta", 0.18)
            p.add(b0 + 3.0, hz(ch[1] + 24), 1, "celesta", 0.14)
        for k in range(4):
            p.ruido(b0 + k + 0.5, 0.03, 0.05, 0.6)                    # hi-hat suave
    return p.fin()


def tension():
    p = Pista(118, 8)
    for c in range(8):
        b0 = c * 4
        root = 38 if c < 6 else 39                                     # D -> Eb (semitono inquietante)
        for k in range(16):
            n = root + (12 if k % 4 == 2 else 0) + (1 if k % 8 == 7 else 0)
            p.add(b0 + k * 0.25, hz(n + 12), 0.25, "cuerda", 0.45 if k % 4 == 0 else 0.28)
        p.add(b0, hz(root), 4, "pad", 0.35)
        p.add(b0, hz(root + 6), 4, "pad", 0.07)                        # tritono de fondo
        p.add(b0, hz(26), 0.5, "bajo", 0.9)                            # latido
        p.add(b0 + 0.4, hz(26), 0.5, "bajo", 0.6)
        if c >= 4:
            p.add(b0 + 2, hz(74 + c), 2, "pad", 0.05 * (c - 3))         # cuerda aguda que sube
    return p.fin()


def triste():
    p = Pista(68, 8)
    prog = [(57, "m"), (53, "M"), (48, "M"), (55, "M")] * 2            # Am F C G
    mel = [76, 74, 72, 71, 72, 74, 76, 79, 77, 76, 74, 72, 71, 72, 69, 69]
    for c, (r, t) in enumerate(prog):
        b0 = c * 4
        ch = acorde(r, t, 0)
        p.add(b0, hz(r - 12), 4, "piano", 0.5)
        for k, n in enumerate([ch[0], ch[1], ch[2], ch[1]]):
            p.add(b0 + k, hz(n), 1.5, "piano", 0.32)
        for k in range(2):
            p.add(b0 + k * 2 + 0.02, hz(mel[(c * 2 + k) % len(mel)]), 2, "piano", 0.42)
        for n in ch:
            p.add(b0, hz(n), 4, "pad", 0.05)
    return p.fin()


def calido():
    p = Pista(100, 8)
    prog = [(48, "M"), (55, "M"), (57, "m"), (53, "M")] * 2            # C G Am F
    for c, (r, t) in enumerate(prog):
        b0 = c * 4
        ch = acorde(r, t, 1)
        for n in acorde(r, t, 0):
            p.add(b0, hz(n), 4, "pad", 0.16)
        p.add(b0, hz(r - 12), 2, "bajo", 0.55)
        p.add(b0 + 2, hz(r - 5), 2, "bajo", 0.4)
        for k, n in enumerate([ch[0], ch[2], ch[1], ch[2]] * 2):
            p.add(b0 + k * 0.5, hz(n), 0.5, "pluck", 0.5)
        p.add(b0 + 3, hz(ch[2] + 24), 1, "celesta", 0.2)
        for k in range(4):
            p.ruido(b0 + k + 0.5, 0.03, 0.06, 0.6)
    return p.fin()


def comico():
    p = Pista(124, 8)
    prog = [(48, "M"), (53, "M"), (55, "M"), (48, "M")] * 2
    for c, (r, t) in enumerate(prog):
        b0 = c * 4
        for k in range(4):
            p.add(b0 + k, hz(r - 12 + (7 if k % 2 else 0)), 0.5, "bajo", 0.7)
        ch = acorde(r, t, 1)
        for k in (0.5, 1.5, 2.5, 3.5):
            for n in ch:
                p.add(b0 + k, hz(n), 0.3, "pluck", 0.25)
        if c % 2:
            p.add(b0 + 3, hz(ch[2] + 12), 0.5, "celesta", 0.25)
            p.add(b0 + 3.5, hz(ch[0] + 24), 0.5, "celesta", 0.25)
    return p.fin()


MUSICA = dict(misterio=misterio, tension=tension, triste=triste, calido=calido, comico=comico)


def save(name, s):
    s = np.tanh(s / (np.max(np.abs(s)) + 1e-9) * 1.2) * 0.85
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((s * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    forzar = "--forzar" in sys.argv
    for k, fn in MUSICA.items():
        if forzar or not (OUT / f"{k}.wav").exists():
            save(k, fn())
    print("musica:", ", ".join(MUSICA))
