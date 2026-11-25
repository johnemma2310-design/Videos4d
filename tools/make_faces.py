"""Genera las caras 2D de Sticky (PNG transparentes) en assets/faces/.

Cada cara es una imagen cuadrada que se proyecta sobre el frente de la cabeza
(esfera) en Blender. Uso:  python tools/make_faces.py
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "faces"
S = 2            # supersampling
N = 1024         # tamaño final
LW = 16          # grosor de línea
BLACK = (15, 15, 20, 255)
WHITE = (255, 255, 255, 255)
MOUTH = (120, 20, 35, 255)
TONGUE = (240, 110, 130, 255)
SWEAT = (120, 190, 255, 255)

EYE_L, EYE_R, EYE_Y = 380, 644, 420


def P(*v):
    return [x * S for x in v]


def eye(d, cx, cy, rx=96, ry=128, px=0, py=0, pr=(42, 56), lid=0.0, tiny=False):
    """Ojo ovalado blanco con pupila. lid = fracción tapada por el párpado (0-1)."""
    d.ellipse(P(cx - rx, cy - ry, cx + rx, cy + ry), fill=WHITE, outline=BLACK, width=LW * S)
    prx, pry = (14, 18) if tiny else pr
    x, y = cx + px, cy + py
    d.ellipse(P(x - prx, y - pry, x + prx, y + pry), fill=BLACK)
    if not tiny:
        d.ellipse(P(x - prx * 0.55, y - pry * 0.7, x - prx * 0.05, y - pry * 0.15), fill=WHITE)
    if lid > 0:
        top = cy - ry - 4
        bottom = cy - ry + 2 * ry * lid
        d.rectangle(P(cx - rx - 4, top - 10, cx + rx + 4, bottom), fill=(0, 0, 0, 0))
        # vuelve a cerrar el contorno: borde del párpado
        d.line(P(cx - rx + 6, bottom, cx + rx - 6, bottom), fill=BLACK, width=LW * S)
        d.arc(P(cx - rx, cy - ry, cx + rx, cy + ry), start=0, end=180, fill=BLACK, width=LW * S)


def brow(d, cx, cy, angle, length=120, side=1):
    a = math.radians(angle) * side
    dx, dy = math.cos(a) * length / 2, math.sin(a) * length / 2
    d.line(P(cx - dx, cy - dy, cx + dx, cy + dy), fill=BLACK, width=int(LW * 1.4) * S)


def smile(d, w=180, y=660, h=70):
    d.arc(P(512 - w, y - h, 512 + w, y + h), start=20, end=160, fill=BLACK, width=LW * S)


def frown(d, w=120, y=720, h=50):
    d.arc(P(512 - w, y, 512 + w, y + 2 * h), start=200, end=340, fill=BLACK, width=LW * S)


def big_open_smile(d, w=210, top=610, h=190):
    box = P(512 - w, top - h, 512 + w, top + h)
    d.chord(box, start=0, end=180, fill=MOUTH, outline=BLACK, width=LW * S)
    d.ellipse(P(512 - w * 0.5, top + h * 0.4, 512 + w * 0.5, top + h * 0.98), fill=TONGUE)
    d.chord(box, start=0, end=180, fill=None, outline=BLACK, width=LW * S)
    d.line(P(512 - w, top, 512 + w, top), fill=BLACK, width=LW * S)


def o_mouth(d, rx=60, ry=85, y=710):
    d.ellipse(P(512 - rx, y - ry, 512 + rx, y + ry), fill=MOUTH, outline=BLACK, width=LW * S)


def evil_grin(d):
    pts = [(300, 640), (512, 700), (724, 610), (690, 700), (512, 780), (340, 720)]
    d.polygon(P(*sum(pts, ())), fill=WHITE, outline=BLACK, width=LW * S)
    for x in (400, 512, 620):
        d.line(P(x, 650, x, 770), fill=BLACK, width=8 * S)


def wavy(d, y=720, w=170, amp=22, waves=3):
    pts = []
    for i in range(41):
        t = i / 40
        pts += [512 - w + 2 * w * t, y + amp * math.sin(t * waves * 2 * math.pi)]
    d.line(P(*pts), fill=BLACK, width=LW * S, joint="curve")


def spiral(d, cx, cy, r=80):
    pts = []
    for i in range(200):
        t = i / 199
        a = t * 3.2 * 2 * math.pi
        pts += [cx + math.cos(a) * r * t, cy + math.sin(a) * r * t]
    d.ellipse(P(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=WHITE, outline=BLACK, width=LW * S)
    d.line(P(*pts), fill=BLACK, width=10 * S)


def sweat(d, x=780, y=300):
    d.polygon(P(x, y - 60, x - 32, y + 10, x + 32, y + 10), fill=SWEAT)
    d.ellipse(P(x - 34, y - 20, x + 34, y + 45), fill=SWEAT, outline=BLACK, width=6 * S)


def tear(d, x, y):
    d.ellipse(P(x - 22, y, x + 22, y + 60), fill=SWEAT, outline=BLACK, width=5 * S)


FACES = {}


def face(name):
    def reg(fn):
        FACES[name] = fn
        return fn
    return reg


@face("neutral")
def _(d):
    eye(d, EYE_L, EYE_Y); eye(d, EYE_R, EYE_Y); smile(d, w=110, h=45, y=680)


@face("feliz")
def _(d):
    eye(d, EYE_L, EYE_Y, py=-8); eye(d, EYE_R, EYE_Y, py=-8); big_open_smile(d)


@face("shock")
def _(d):
    eye(d, EYE_L, EYE_Y, rx=110, ry=145, tiny=True); eye(d, EYE_R, EYE_Y, rx=110, ry=145, tiny=True)
    o_mouth(d)


@face("triste")
def _(d):
    eye(d, EYE_L, EYE_Y, py=30); eye(d, EYE_R, EYE_Y, py=30)
    brow(d, EYE_L, 290, -20, side=1); brow(d, EYE_R, 290, 20, side=1)
    frown(d); tear(d, EYE_L + 40, 545)


@face("enojado")
def _(d):
    eye(d, EYE_L, EYE_Y, lid=0.3, px=10); eye(d, EYE_R, EYE_Y, lid=0.3, px=-10)
    brow(d, EYE_L, 330, 25); brow(d, EYE_R, 330, -25)
    frown(d, w=100, h=35, y=720)


@face("malvado")
def _(d):
    eye(d, EYE_L, EYE_Y, lid=0.45, px=20); eye(d, EYE_R, EYE_Y, lid=0.45, px=20)
    brow(d, EYE_L, 345, 18); brow(d, EYE_R, 345, -18)
    evil_grin(d)


@face("aburrido")
def _(d):
    eye(d, EYE_L, EYE_Y, lid=0.55, py=25); eye(d, EYE_R, EYE_Y, lid=0.55, py=25)
    d.line(P(420, 710, 610, 700), fill=BLACK, width=LW * S)


@face("miedo")
def _(d):
    eye(d, EYE_L, EYE_Y, rx=105, ry=140, tiny=True, py=10); eye(d, EYE_R, EYE_Y, rx=105, ry=140, tiny=True, py=10)
    brow(d, EYE_L, 275, -22); brow(d, EYE_R, 275, 22)
    wavy(d); sweat(d)


@face("mareado")
def _(d):
    spiral(d, EYE_L, EYE_Y); spiral(d, EYE_R, EYE_Y); wavy(d, amp=15, waves=2)


@face("pensando")
def _(d):
    eye(d, EYE_L, EYE_Y, px=28, py=-45); eye(d, EYE_R, EYE_Y, px=28, py=-45)
    brow(d, EYE_R, 285, -12)
    d.line(P(450, 720, 590, 700), fill=BLACK, width=LW * S)


@face("dormido")
def _(d):
    for cx in (EYE_L, EYE_R):
        d.arc(P(cx - 75, EYE_Y - 40, cx + 75, EYE_Y + 60), start=10, end=170, fill=BLACK, width=LW * S)
    o_mouth(d, rx=30, ry=38, y=700)


@face("sonrisa")
def _(d):
    for cx in (EYE_L, EYE_R):  # ojitos felices ^ ^
        d.arc(P(cx - 75, EYE_Y - 40, cx + 75, EYE_Y + 80), start=200, end=340, fill=BLACK, width=LW * S)
    smile(d, w=170, h=80, y=640)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in FACES.items():
        img = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
        fn(ImageDraw.Draw(img))
        img.resize((N, N), Image.LANCZOS).save(OUT / f"{name}.png")
    # hoja de contacto para revisar rápido
    cols, cell = 4, 256
    rows = math.ceil(len(FACES) / cols)
    sheet = Image.new("RGBA", (cols * cell, rows * cell), (230, 240, 250, 255))
    for i, name in enumerate(FACES):
        head = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
        ImageDraw.Draw(head).ellipse((8, 8, cell - 8, cell - 8), fill=WHITE, outline=BLACK, width=6)
        f = Image.open(OUT / f"{name}.png").resize((int(cell * 0.82),) * 2, Image.LANCZOS)
        head.alpha_composite(f, (int(cell * 0.09),) * 2)
        sheet.alpha_composite(head, ((i % cols) * cell, (i // cols) * cell))
    sheet.save(OUT.parent / "faces_preview.png")
    print("caras:", ", ".join(FACES))


if __name__ == "__main__":
    main()
