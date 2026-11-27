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


def ojo_terror(d, cx):
    """Ojo blanco grande con pupila diminuta (pupilas contraídas de miedo)."""
    d.ellipse(P(cx - 52, EY - 70, cx + 52, EY + 70), fill=WHITE, outline=INK, width=LW * S)
    d.ellipse(P(cx - 13, EY - 13, cx + 13, EY + 13), fill=INK)


def ojo_brillante(d, cx):
    """Ojos amarillos (en Blender brillan en la oscuridad con 'brillo_ojos')."""
    d.ellipse(P(cx - 46, EY - 40, cx + 46, EY + 40), fill=(255, 225, 60, 255))
    d.ellipse(P(cx - 10, EY - 30, cx + 10, EY + 30), fill=(255, 250, 200, 255))


def lagrimas(d):
    for cx in (EL, ER):
        d.rounded_rectangle(P(cx - 16, EY + 20, cx + 16, EY + 240), radius=16 * S, fill=TEAR)


def dientes(d, y=650, w=110, h=40):
    d.rounded_rectangle(P(512 - w, y - h, 512 + w, y + h), radius=18 * S, fill=WHITE, outline=INK, width=LW * S)
    for k in (-1, 0, 1):
        x = 512 + k * w / 2
        d.line(P(x, y - h, x, y + h), fill=INK, width=8 * S)
    d.line(P(512 - w, y, 512 + w, y), fill=INK, width=8 * S)


def gota_sudor(d):
    d.ellipse(P(700, 300, 750, 370), fill=TEAR, outline=INK, width=6 * S)


# Cada cara: ojos, cejas, boca y "habla" (boca abierta para el lip-sync). cerrados=True: sin parpadeo.
O = lambda **kw: (lambda d: (ojo(d, EL, **kw), ojo(d, ER, **kw)))  # noqa: E731
CEJAS = lambda a, dy: (lambda d: (ceja(d, EL, a, dy), ceja(d, ER, -a, dy)))  # noqa: E731
NADA = lambda d: None  # noqa: E731
HABLA = lambda d: boca_o(d, 48, 50, 640)  # noqa: E731
HABLA_GRANDE = lambda d: boca_abierta(d, 105, 605, 95)  # noqa: E731

FACES = {
    "neutral":  dict(ojos=O(), boca=lambda d: sonrisa(d, 80, 610, 45), habla=HABLA),
    "feliz":    dict(ojos=O(), boca=boca_abierta, habla=lambda d: boca_abierta(d, 110, 600, 70)),
    "sonrisa":  dict(ojos=lambda d: (ojo_cerrado(d, EL), ojo_cerrado(d, ER)), cerrados=True,
                     boca=lambda d: sonrisa(d, 120, 590, 75), habla=HABLA_GRANDE),
    "shock":    dict(ojos=O(rx=44, ry=66), cejas=CEJAS(-8, -25), boca=boca_o,
                     habla=lambda d: boca_o(d, 55, 75, 650)),
    "triste":   dict(ojos=O(dy=10), cejas=CEJAS(-22, 5), boca=triste_boca, habla=lambda d: boca_o(d, 38, 40, 665)),
    "enojado":  dict(ojos=O(ry=46), cejas=CEJAS(25, 25), boca=lambda d: triste_boca(d, 70, 675, 30),
                     habla=lambda d: dientes(d, 660, 90, 34)),
    "malvado":  dict(ojos=O(ry=40, dy=8), cejas=CEJAS(22, 25), boca=sonrisa_malvada, habla=HABLA_GRANDE),
    "aburrido": dict(ojos=lambda d: (ojo_cerrado(d, EL, False), ojo_cerrado(d, ER, False)), cerrados=True,
                     boca=lambda d: linea(d, 655, 55), habla=lambda d: boca_o(d, 30, 30, 655)),
    "miedo":    dict(ojos=O(rx=40, ry=60, dy=6), cejas=CEJAS(-20, -15), boca=ondulada, extra=gota_sudor,
                     habla=lambda d: boca_o(d, 40, 55, 655)),
    "mareado":  dict(ojos=lambda d: (espiral(d, EL), espiral(d, ER)), cerrados=True,
                     boca=lambda d: ondulada(d, amp=12), habla=HABLA),
    "pensando": dict(ojos=O(dx=12, dy=-18), cejas=lambda d: ceja(d, ER, -12, -10),
                     boca=lambda d: linea(d, 655, 50, tilt=10), habla=lambda d: boca_o(d, 34, 36, 650)),
    "dormido":  dict(ojos=lambda d: (ojo_cerrado(d, EL, False), ojo_cerrado(d, ER, False)), cerrados=True,
                     boca=lambda d: boca_o(d, 24, 30, 655), habla=lambda d: boca_o(d, 30, 40, 655)),
    # nuevas (formato de misterio)
    "terror":   dict(ojos=lambda d: (ojo_terror(d, EL), ojo_terror(d, ER)), cejas=CEJAS(-25, -35),
                     boca=lambda d: boca_abierta(d, 80, 640, 90), extra=gota_sudor,
                     habla=lambda d: boca_abierta(d, 95, 630, 115)),
    "llorando": dict(ojos=lambda d: (ojo_cerrado(d, EL, False), ojo_cerrado(d, ER, False)), cerrados=True,
                     cejas=CEJAS(-25, 0), boca=lambda d: triste_boca(d, 95, 660, 55), extra=lagrimas,
                     habla=lambda d: boca_o(d, 50, 45, 670)),
    "furioso":  dict(ojos=O(rx=36, ry=36, dy=10), cejas=CEJAS(32, 35), boca=dientes,
                     habla=lambda d: dientes(d, 655, 115, 55)),
    "sospecha": dict(ojos=lambda d: (ojo(d, EL, ry=24, dy=14, dx=18), ojo(d, ER, ry=24, dy=14, dx=18)),
                     cejas=lambda d: (ceja(d, EL, 10, 20), ceja(d, ER, -5, -5)),
                     boca=lambda d: linea(d, 655, 50, tilt=-12), habla=lambda d: boca_o(d, 32, 34, 655)),
    "brillante": dict(ojos=lambda d: (ojo_brillante(d, EL), ojo_brillante(d, ER)), cejas=CEJAS(18, 15),
                      boca=NADA, habla=lambda d: boca_o(d, 40, 50, 650)),
    "asombro":  dict(ojos=O(rx=46, ry=62), cejas=CEJAS(-10, -30), boca=lambda d: boca_abierta(d, 95, 610, 100),
                     habla=lambda d: boca_abierta(d, 100, 610, 115)),
}


def dibujar(spec, variante):
    """variante: '' (normal), 'parpadeo' (ojos cerrados) o 'habla' (boca abierta)."""
    img = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if variante == "parpadeo" and not spec.get("cerrados"):
        ojo_cerrado(d, EL, False)
        ojo_cerrado(d, ER, False)
    else:
        spec["ojos"](d)
    if spec.get("cejas"):
        spec["cejas"](d)
    (spec["habla"] if variante == "habla" else spec["boca"])(d)
    if spec.get("extra"):
        spec["extra"](d)
    big = int(N * ZOOM)   # rasgos más grandes, centrados (se leen mejor en el celular)
    img = img.resize((big, big), Image.LANCZOS)
    off = (big - N) // 2
    return img.crop((off, off + 30, off + N, off + N + 30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in FACES.items():
        dibujar(spec, "").save(OUT / f"{name}.png")
        dibujar(spec, "parpadeo").save(OUT / f"{name}__parpadeo.png")
        dibujar(spec, "habla").save(OUT / f"{name}__habla.png")
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
