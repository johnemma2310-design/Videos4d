"""Caras simples estilo juguete de bloques (para "estilo": "bloques") en assets/faces_simple/.

Ojitos negros ovalados con brillo, cejas gruesas cortas y boca de línea: legibles en
planos lejanos y en celular. Mismos nombres que assets/faces/ para que los guiones no cambien.
Uso:  python tools/make_faces_simple.py
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "faces_simple"
S, N = 2, 1024
INK = (20, 20, 24, 255)
WHITE = (255, 255, 255, 255)
MOUTH = (110, 25, 35, 255)
TONGUE = (235, 105, 120, 255)
TEAR = (120, 195, 255, 255)
EL, ER, EY = 410, 614, 445      # centros de los ojos
LW = 22                         # grosor de líneas
ZOOM = 1.35                     # escala final de los rasgos


def P(*v):
    return [x * S for x in v]


def ojo(d, cx, cy=EY, rx=38, ry=56, dx=0, dy=0, brillo=True):
    x, y = cx + dx, cy + dy
    d.ellipse(P(x - rx, y - ry, x + rx, y + ry), fill=INK)
    if brillo:
        d.ellipse(P(x - rx * 0.45, y - ry * 0.6, x - rx * 0.02, y - ry * 0.18), fill=WHITE)


def ojo_cerrado(d, cx, feliz=True):
    if feliz:   # ^
        d.arc(P(cx - 50, EY - 30, cx + 50, EY + 60), 200, 340, fill=INK, width=LW * S)
    else:       # -
        d.line(P(cx - 45, EY + 10, cx + 45, EY + 10), fill=INK, width=LW * S)


def ceja(d, cx, ang, dy=0, largo=95):
    a = math.radians(ang)
    y = EY - 105 + dy
    ddx, ddy = math.cos(a) * largo / 2, math.sin(a) * largo / 2
    d.line(P(cx - ddx, y - ddy, cx + ddx, y + ddy), fill=INK, width=int(LW * 1.2) * S)


def sonrisa(d, w=120, y=600, h=70):
    d.arc(P(512 - w, y - h, 512 + w, y + h), 25, 155, fill=INK, width=LW * S)


def boca_abierta(d, w=125, top=600, h=120):
    box = P(512 - w, top - h, 512 + w, top + h)
    d.chord(box, 0, 180, fill=MOUTH, outline=INK, width=LW * S)
    d.ellipse(P(512 - w * 0.5, top + h * 0.4, 512 + w * 0.5, top + h * 0.98), fill=TONGUE)
    d.chord(box, 0, 180, fill=None, outline=INK, width=LW * S)
    d.line(P(512 - w, top, 512 + w, top), fill=INK, width=LW * S)


def boca_o(d, rx=42, ry=55, y=650):
    d.ellipse(P(512 - rx, y - ry, 512 + rx, y + ry), fill=MOUTH, outline=INK, width=LW * S)


def linea(d, y=650, w=70, tilt=0):
    d.line(P(512 - w, y + tilt, 512 + w, y - tilt), fill=INK, width=LW * S)


def triste_boca(d, w=85, y=665, h=45):
    d.arc(P(512 - w, y, 512 + w, y + 2 * h), 205, 335, fill=INK, width=LW * S)


def ondulada(d, y=655, w=95, amp=16):
    pts = []
    for i in range(31):
        t = i / 30
        pts += [512 - w + 2 * w * t, y + amp * math.sin(t * 3 * 2 * math.pi)]
    d.line(P(*pts), fill=INK, width=LW * S, joint="curve")


def sonrisa_malvada(d):
    d.arc(P(392, 520, 652, 690), 15, 165, fill=INK, width=LW * S)
    d.line(P(392, 590, 372, 570), fill=INK, width=LW * S)
    d.line(P(632, 590, 662, 560), fill=INK, width=LW * S)


def espiral(d, cx):
    pts = []
    for i in range(160):
        t = i / 159
        a = t * 3 * 2 * math.pi
        pts += [cx + math.cos(a) * 55 * t, EY + math.sin(a) * 55 * t]
    d.line(P(*pts), fill=INK, width=12 * S)


FACES = {
    "neutral":  lambda d: (ojo(d, EL), ojo(d, ER), sonrisa(d, 80, 610, 45)),
    "feliz":    lambda d: (ojo(d, EL), ojo(d, ER), boca_abierta(d)),
    "sonrisa":  lambda d: (ojo_cerrado(d, EL), ojo_cerrado(d, ER), sonrisa(d, 120, 590, 75)),
    "shock":    lambda d: (ojo(d, EL, rx=44, ry=66), ojo(d, ER, rx=44, ry=66), ceja(d, EL, -8, -25),
                           ceja(d, ER, 8, -25), boca_o(d)),
    "triste":   lambda d: (ojo(d, EL, dy=10), ojo(d, ER, dy=10), ceja(d, EL, -22, 5), ceja(d, ER, 22, 5),
                           triste_boca(d)),
    "enojado":  lambda d: (ojo(d, EL, ry=46), ojo(d, ER, ry=46), ceja(d, EL, 25, 25), ceja(d, ER, -25, 25),
                           triste_boca(d, 70, 675, 30)),
    "malvado":  lambda d: (ojo(d, EL, ry=40, dy=8), ojo(d, ER, ry=40, dy=8), ceja(d, EL, 22, 25),
                           ceja(d, ER, -22, 25), sonrisa_malvada(d)),
    "aburrido": lambda d: (ojo_cerrado(d, EL, False), ojo_cerrado(d, ER, False), linea(d, 655, 55)),
    "miedo":    lambda d: (ojo(d, EL, rx=40, ry=60, dy=6), ojo(d, ER, rx=40, ry=60, dy=6), ceja(d, EL, -20, -15),
                           ceja(d, ER, 20, -15), ondulada(d),
                           d.ellipse(P(700, 300, 750, 370), fill=TEAR, outline=INK, width=6 * S)),
    "mareado":  lambda d: (espiral(d, EL), espiral(d, ER), ondulada(d, amp=12)),
    "pensando": lambda d: (ojo(d, EL, dx=12, dy=-18), ojo(d, ER, dx=12, dy=-18), ceja(d, ER, -12, -10),
                           linea(d, 655, 50, tilt=10)),
    "dormido":  lambda d: (ojo_cerrado(d, EL, False), ojo_cerrado(d, ER, False), boca_o(d, 24, 30, 655)),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FACES.items():
        img = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
        fn(ImageDraw.Draw(img))
        big = int(N * ZOOM)   # rasgos más grandes, centrados (se leen mejor en el celular)
        img = img.resize((big, big), Image.LANCZOS)
        off = (big - N) // 2
        img.crop((off, off + 30, off + N, off + N + 30)).save(OUT / f"{name}.png")
    cols, cell = 6, 200
    rows = math.ceil(len(FACES) / cols)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (210, 225, 240, 255))
    for i, name in enumerate(FACES):
        tile = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
        ImageDraw.Draw(tile).rounded_rectangle((12, 12, cell - 12, cell - 12), radius=40,
                                               fill=(255, 225, 190, 255), outline=(60, 60, 60, 255), width=3)
        f = Image.open(OUT / f"{name}.png").resize((cell - 24, cell - 24), Image.LANCZOS)
        tile.alpha_composite(f, (12, 12))
        sheet.alpha_composite(tile, ((i % cols) * cell, (i // cols) * cell))
    sheet.save(OUT.parent / "faces_simple_preview.png")
    print("caras simples:", ", ".join(FACES))


if __name__ == "__main__":
    main()
