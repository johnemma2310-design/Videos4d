"""Capas extra de cara (bigote, barba, lentes, pestañas, hocicos...) en assets/faces/extras/.

Se combinan con las expresiones de assets/faces/ según cada personaje de
assets/personajes.json (lo hace pipeline/build.py). Mismo lienzo 1024x1024 que
make_faces.py. Uso:  python tools/make_face_extras.py
"""
from pathlib import Path
import math
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent.parent / "assets" / "faces" / "extras"
S, N = 2, 1024
BLACK = (15, 15, 20, 255)
EYE_L, EYE_R, EYE_Y, RX, RY = 380, 644, 420, 96, 128


def P(*v):
    return [x * S for x in v]


def poly(d, pts, fill, outline=BLACK, w=10):
    d.polygon(P(*sum(pts, ())), fill=fill, outline=outline, width=w * S)


def bigote(d, color=(45, 30, 25, 255)):
    # dos "alas" curvas bajo la nariz
    for sx in (-1, 1):
        pts = []
        for i in range(21):
            t = i / 20
            x = 512 + sx * (10 + 190 * t)
            y = 600 + 35 * math.sin(t * math.pi) - 55 * t * t
            pts.append((x, y))
        for i in range(20, -1, -1):
            t = i / 20
            x = 512 + sx * (10 + 190 * t)
            y = 600 + 70 * math.sin(t * math.pi) * (1 - 0.4 * t) - 40 * t * t + 20
            pts.append((x, y))
        poly(d, pts, color)


def bigote_blanco(d):
    bigote(d, (235, 235, 235, 255))


def barba(d, color=(60, 40, 30, 255)):
    """Barba en media luna alrededor de la barbilla (va debajo de la boca)."""
    outer = [(512 + 330 * math.cos(math.radians(a)), 470 + 330 * math.sin(math.radians(a)))
             for a in range(15, 166, 5)]
    inner = [(512 + 250 * math.cos(math.radians(a)), 450 + 250 * math.sin(math.radians(a)))
             for a in range(165, 14, -5)]
    pts = outer + inner
    d.polygon(P(*sum(pts, ())), fill=color, outline=BLACK, width=10 * S)


def barba_blanca(d):
    barba(d, (230, 230, 230, 255))


def pestanas(d):
    for cx, sx in ((EYE_L, -1), (EYE_R, 1)):
        for k in range(3):
            a = math.radians(-100 + sx * (35 + k * 22)) if sx > 0 else math.radians(-80 - (35 + k * 22))
            x0 = cx + math.cos(a) * RX * 0.98
            y0 = EYE_Y + math.sin(a) * RY * 0.98
            x1 = cx + math.cos(a) * (RX + 45)
            y1 = EYE_Y + math.sin(a) * (RY + 45)
            d.line(P(x0, y0, x1, y1), fill=BLACK, width=12 * S)


def labios(d):  # lunar coqueto + pintalabios suave en las comisuras
    d.ellipse(P(650, 610, 672, 632), fill=BLACK)


def chapitas(d):
    for cx in (EYE_L - 60, EYE_R + 60):
        d.ellipse(P(cx - 70, 580, cx + 70, 640), fill=(255, 130, 150, 150))


def pecas(d):
    for cx in (EYE_L - 40, EYE_R + 40):
        for dx, dy in ((-30, 0), (0, 22), (30, -6), (12, -28)):
            d.ellipse(P(cx + dx - 7, 590 + dy - 7, cx + dx + 7, 590 + dy + 7), fill=(170, 100, 60, 255))


def lentes(d):
    r = 140
    for cx in (EYE_L, EYE_R):
        d.ellipse(P(cx - r, EYE_Y - r, cx + r, EYE_Y + r), outline=BLACK, width=16 * S)
        d.ellipse(P(cx - r + 14, EYE_Y - r + 14, cx + r - 14, EYE_Y + r - 14), fill=(200, 230, 255, 50))
    d.arc(P(EYE_L + r - 30, EYE_Y - 60, EYE_R - r + 30, EYE_Y + 20), 200, 340, fill=BLACK, width=14 * S)
    d.line(P(EYE_L - r, EYE_Y - 20, 30, EYE_Y - 60), fill=BLACK, width=14 * S)
    d.line(P(EYE_R + r, EYE_Y - 20, 994, EYE_Y - 60), fill=BLACK, width=14 * S)


def lentes_lectura(d):
    """Gafas de lectura de media luna: borde recto arriba, curvo abajo, un poco bajas en la cara."""
    gold = (40, 35, 30, 255)
    for cx in (376, 648):
        box = P(cx - 92, 330, cx + 92, 500)
        d.chord(box, 0, 180, fill=(220, 235, 255, 70), outline=gold, width=13 * S)
    d.arc(P(462, 395, 562, 455), 200, 340, fill=gold, width=12 * S)
    d.line(P(284, 418, 40, 380), fill=gold, width=11 * S)
    d.line(P(740, 418, 984, 380), fill=gold, width=11 * S)


def lentes_sol(d):
    for cx in (EYE_L, EYE_R):
        d.rounded_rectangle(P(cx - 135, EYE_Y - 80, cx + 135, EYE_Y + 95), radius=60 * S,
                            fill=(20, 20, 30, 255), outline=BLACK, width=10 * S)
        d.line(P(cx - 80, EYE_Y - 40, cx - 30, EYE_Y - 55), fill=(255, 255, 255, 180), width=14 * S)
    d.line(P(EYE_L + 135, EYE_Y - 30, EYE_R - 135, EYE_Y - 30), fill=BLACK, width=16 * S)


def nariz_perro(d):
    d.ellipse(P(380, 530, 644, 720), fill=(255, 255, 255, 255), outline=BLACK, width=10 * S)  # hocico
    d.ellipse(P(455, 520, 569, 590), fill=BLACK)
    d.ellipse(P(478, 530, 510, 548), fill=(255, 255, 255, 200))
    d.line(P(512, 590, 512, 640), fill=BLACK, width=10 * S)


def nariz_gato(d):
    poly(d, [(482, 560), (542, 560), (512, 598)], (255, 140, 170, 255), w=6)
    for sy in (-1, 1):
        for k in range(3):
            y = 600 + k * 22
            d.line(P(430, y, 210, y - 30 + k * 30), fill=BLACK, width=7 * S)
            d.line(P(594, y, 814, y - 30 + k * 30), fill=BLACK, width=7 * S)
        break


def pico(d):
    poly(d, [(420, 560), (604, 560), (512, 690)], (255, 170, 30, 255), w=10)
    d.line(P(430, 585, 594, 585), fill=BLACK, width=7 * S)


def nariz_cerdo(d):
    d.ellipse(P(420, 520, 604, 640), fill=(255, 160, 180, 255), outline=BLACK, width=10 * S)
    for cx in (480, 544):
        d.ellipse(P(cx - 16, 565, cx + 16, 600), fill=(120, 40, 60, 255))


EXTRAS = dict(bigote=bigote, bigote_blanco=bigote_blanco, barba=barba, barba_blanca=barba_blanca,
              pestanas=pestanas, labios=labios, chapitas=chapitas, pecas=pecas, lentes=lentes,
              lentes_lectura=lentes_lectura,
              lentes_sol=lentes_sol, nariz_perro=nariz_perro, nariz_gato=nariz_gato, pico=pico,
              nariz_cerdo=nariz_cerdo)
# capas que van DEBAJO de la expresión (para que ojos y boca queden encima)
DEBAJO = {"barba", "barba_blanca", "chapitas", "pecas", "nariz_perro", "nariz_cerdo"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in EXTRAS.items():
        img = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
        fn(ImageDraw.Draw(img))
        img.resize((N, N), Image.LANCZOS).save(OUT / f"{name}.png")
    print("extras:", ", ".join(EXTRAS))


if __name__ == "__main__":
    main()
