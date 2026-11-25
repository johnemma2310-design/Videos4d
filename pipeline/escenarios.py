"""Escenarios low-poly estilo cartoon. Cada función recibe la escena (cfg) y devuelve
{"standing": (x, y, z)} = dónde se para el protagonista. Los personajes miran a -Y
y la cámara suele estar del lado -Y, así que el decorado va hacia +Y (fondo) y a los lados.

cfg["noche"] = true oscurece cualquier escenario (luna y estrellas en los exteriores).
"""
import math
import random

from bl_util import D, ball, box, cone, cyl, mat, prim, finish, sun, world

DAY_SKY = (0.52, 0.8, 1.0)
NIGHT_SKY = (0.06, 0.08, 0.22)


def ambiente(cfg, sky=DAY_SKY, exterior=True):
    """Cielo + sol, o versión nocturna."""
    if cfg.get("noche"):
        world(NIGHT_SKY if exterior else tuple(c * 0.35 for c in sky), 0.25, (0.5, 0.6, 1.0))
        sun(2.2, (0.65, 0.75, 1.0), (55, 0, -35))
        if exterior:
            ball("luna", (-9, 40, 16), 2.2, (1, 0.97, 0.8), outline=0, shadow=1.0)
            rnd = random.Random(11)
            for i in range(60):
                x, z = rnd.uniform(-40, 40), rnd.uniform(5, 30)
                b = ball(f"estrella{i}", (x, 60, z), rnd.uniform(0.08, 0.2), (1, 1, 0.9), outline=0, seg=6)
                b.data.materials[0] = mat((1, 1, 0.9), flat=True)
    else:
        world(sky)
        sun()


def flat(o, color):
    """Pone un material plano (emisivo, sin sombra): ventanas encendidas, estrellas, sol."""
    o.data.materials[0] = mat(color, flat=True)
    return o


def arbol(name, x, y, s=1.0, top=(0.2, 0.62, 0.3), pino=True):
    cyl(f"{name}_tronco", (x, y, 0.7 * s), 0.18 * s, 1.4 * s, (0.5, 0.32, 0.2), outline=0.03,
        vertices=8, smooth=False)
    if pino:
        for k in range(3):
            cone(f"{name}_copa{k}", (x, y, (1.6 + k * 0.8) * s), (1.2 - k * 0.3) * s, 0, 1.6 * s, top,
                 outline=0.04, vertices=8, shadow=0.75)
    else:
        ball(f"{name}_copa", (x, y, 2.3 * s), 1.1 * s, top, outline=0.04, shadow=0.75, seg=12)


def nubes(rnd, n=5, y=25):
    for i in range(n):
        x, z = rnd.uniform(-14, 14), rnd.uniform(6, 10)
        for j in range(3):
            ball(f"nube{i}_{j}", (x + j * 1.1, y, z + (j % 2) * 0.4), rnd.uniform(0.9, 1.4), (1, 1, 1),
                 outline=0, shadow=0.92, seg=16)


# ------------------------------------------------------------ interiores

def habitacion(cfg):
    ambiente(cfg, (0.55, 0.78, 0.95), exterior=False)
    box("piso", (0, 0, -0.05), (16, 16, 0.1), (0.86, 0.66, 0.46), outline=0)
    box("pared", (0, 3.2, 3), (16, 0.2, 6), (0.62, 0.82, 0.97))
    box("pared_izq", (-5.5, 0, 3), (0.2, 16, 6), (0.55, 0.76, 0.93))
    box("zocalo", (0, 3.05, 0.15), (16, 0.12, 0.3), (0.95, 0.95, 0.95), outline=0.02)
    cielo_ventana = NIGHT_SKY if cfg.get("noche") else (0.45, 0.75, 1.0)
    box("ventana_marco", (2.6, 3.05, 3.4), (2.2, 0.1, 1.8), (0.97, 0.97, 0.97))
    flat(box("ventana_cielo", (2.6, 2.98, 3.4), (1.9, 0.05, 1.5), cielo_ventana, outline=0.015), cielo_ventana)
    box("ventana_cruz_v", (2.6, 2.94, 3.4), (0.08, 0.04, 1.5), (0.97, 0.97, 0.97), outline=0)
    box("ventana_cruz_h", (2.6, 2.94, 3.4), (1.9, 0.04, 0.08), (0.97, 0.97, 0.97), outline=0)
    box("cuadro", (-2.4, 3.05, 3.6), (1.0, 0.08, 1.2), (0.98, 0.82, 0.3))
    box("cuadro_in", (-2.4, 2.99, 3.6), (0.75, 0.04, 0.95), (0.95, 0.5, 0.4), outline=0.01)
    bx = -1.3
    box("cama_base", (bx, 0.6, 0.35), (1.9, 3.6, 0.5), (0.55, 0.35, 0.22))
    box("cabecera", (bx, 2.45, 0.9), (1.9, 0.15, 1.6), (0.55, 0.35, 0.22))
    box("colchon", (bx, 0.55, 0.7), (1.8, 3.4, 0.25), (0.97, 0.97, 0.97))
    box("almohada", (bx, 1.85, 0.9), (1.2, 0.7, 0.22), (1, 1, 1), outline=0.02)
    if cfg.get("pose") == "acostado":
        box("cobija", (bx, -0.1, 1.05), (1.95, 2.3, 0.62), (0.95, 0.42, 0.45))
        box("cobija_borde", (bx, 1.07, 1.05), (1.97, 0.12, 0.64), (1, 0.97, 0.9), outline=0.02)
    else:
        box("cobija", (bx, 0.2, 0.86), (1.95, 2.6, 0.12), (0.95, 0.42, 0.45))
    # mesita + lámpara
    box("mesita", (0.35, 2.3, 0.4), (0.7, 0.6, 0.8), (0.62, 0.4, 0.25))
    cyl("lampara_pie", (0.35, 2.3, 1.05), 0.05, 0.5, (0.3, 0.3, 0.35), outline=0.015, vertices=8)
    cone("lampara", (0.35, 2.3, 1.4), 0.3, 0.18, 0.35, (1, 0.9, 0.55), outline=0.02, vertices=16)
    rug = prim("cylinder", "alfombra", vertices=48, radius=1.4, depth=0.03, location=(1.3, -1.8, 0.02))
    finish(rug, mat((0.98, 0.83, 0.35)), 0, smooth=False)
    return {"standing": (1.3, -1.8, 0)}


def cocina(cfg):
    ambiente(cfg, (0.98, 0.93, 0.8), exterior=False)
    a, b = (0.95, 0.95, 0.95), (0.35, 0.6, 0.85)
    for i in range(-6, 6):
        for j in range(-11, 4):
            box(f"loseta{i}_{j}", (i + 0.5, j + 0.5, -0.05), (1, 1, 0.1), a if (i + j) % 2 else b, outline=0)
    box("pared", (0, 3.6, 3), (12, 0.2, 6), (0.98, 0.92, 0.75))
    box("pared_izq", (-5, 0, 3), (0.2, 12, 6), (0.95, 0.88, 0.7))
    # mueble bajo + cubierta
    box("muebles", (0.5, 3.05, 0.45), (7, 0.9, 0.9), (0.4, 0.65, 0.55))
    box("cubierta", (0.5, 3.0, 0.95), (7.1, 1.0, 0.1), (0.92, 0.92, 0.95), outline=0.02)
    for k in range(6):
        box(f"puerta{k}", (-2.4 + k * 1.15, 2.58, 0.45), (1.0, 0.04, 0.75), (0.45, 0.72, 0.62), outline=0.015)
        cyl(f"jaladera{k}", (-2.4 + k * 1.15 + 0.35, 2.54, 0.65), 0.03, 0.06, (0.8, 0.8, 0.8),
            outline=0, vertices=8, rot=(D(90), 0, 0))
    # estufa
    box("estufa", (2.2, 3.0, 1.02), (1.6, 0.9, 0.06), (0.15, 0.15, 0.18), outline=0.015)
    for k, (x, y) in enumerate([(1.8, 2.8), (2.6, 2.8), (1.8, 3.2), (2.6, 3.2)]):
        cyl(f"hornilla{k}", (x, y, 1.07), 0.17, 0.03, (0.35, 0.35, 0.38), outline=0.01, vertices=16)
    cyl("olla", (1.8, 2.8, 1.35), 0.32, 0.5, (0.85, 0.3, 0.25), outline=0.025, vertices=24)
    cyl("olla_tapa", (1.8, 2.8, 1.62), 0.34, 0.05, (0.75, 0.75, 0.78), outline=0.02, vertices=24)
    cyl("sarten", (2.6, 3.2, 1.12), 0.28, 0.08, (0.2, 0.2, 0.22), outline=0.02, vertices=24)
    # alacenas
    box("alacena", (-0.5, 3.3, 3.4), (4.5, 0.6, 1.3), (0.4, 0.65, 0.55))
    for k in range(4):
        box(f"alacena_p{k}", (-2.2 + k * 1.12, 2.98, 3.4), (1.0, 0.04, 1.1), (0.45, 0.72, 0.62), outline=0.015)
    # refri
    box("refri", (-4.0, 2.7, 1.5), (1.4, 1.2, 3.0), (0.92, 0.95, 1.0))
    box("refri_linea", (-4.0, 2.08, 2.1), (1.42, 0.04, 0.05), (0.6, 0.65, 0.7), outline=0)
    box("refri_mango", (-3.45, 2.05, 1.5), (0.06, 0.06, 0.8), (0.6, 0.65, 0.7), outline=0.01)
    # ventana sobre el fregadero
    cielo = NIGHT_SKY if cfg.get("noche") else (0.5, 0.8, 1.0)
    box("ventana_marco", (3.6, 3.48, 2.6), (1.8, 0.1, 1.4), (1, 1, 1))
    flat(box("ventana_cielo", (3.6, 3.42, 2.6), (1.5, 0.05, 1.1), cielo, outline=0.01), cielo)
    # mesa con frutero
    box("mesa", (2.5, -0.2, 0.85), (1.8, 1.2, 0.1), (0.75, 0.5, 0.3))
    for k, (x, y) in enumerate([(1.75, -0.7), (3.25, -0.7), (1.75, 0.3), (3.25, 0.3)]):
        cyl(f"mesa_pata{k}", (x, y, 0.4), 0.05, 0.8, (0.6, 0.38, 0.22), outline=0.015, vertices=8)
    cyl("frutero", (2.5, -0.2, 1.0), 0.35, 0.15, (1, 1, 1), outline=0.015, vertices=20)
    for k, (dx, c) in enumerate([(-0.15, (0.95, 0.2, 0.2)), (0.12, (1, 0.8, 0.1)), (0, (0.3, 0.8, 0.3))]):
        ball(f"fruta{k}", (2.5 + dx, -0.2 + (k - 1) * 0.1, 1.17), 0.13, c, outline=0.015, seg=12)
    return {"standing": (0, -0.6, 0)}


def escuela(cfg):
    ambiente(cfg, (0.9, 0.95, 0.85), exterior=False)
    box("piso", (0, 0, -0.05), (16, 16, 0.1), (0.78, 0.62, 0.45), outline=0)
    box("pared", (0, 3.4, 3), (16, 0.2, 6), (0.85, 0.93, 0.8))
    box("pared_izq", (-6, 0, 3), (0.2, 16, 6), (0.8, 0.9, 0.75))
    box("pizarron_marco", (0, 3.25, 2.6), (5.4, 0.1, 2.4), (0.6, 0.4, 0.22))
    box("pizarron", (0, 3.18, 2.6), (5.0, 0.06, 2.0), (0.15, 0.38, 0.28), outline=0.01)
    rnd = random.Random(5)
    for k in range(7):   # garabatos de gis
        w = rnd.uniform(0.6, 1.6)
        box(f"gis{k}", (rnd.uniform(-2, 2), 3.13, rnd.uniform(1.9, 3.3)), (w, 0.01, 0.05), (0.95, 0.95, 0.95),
            outline=0, rot=(0, D(rnd.uniform(-8, 8)), 0))
    box("charola", (0, 3.1, 1.55), (5.0, 0.2, 0.06), (0.6, 0.4, 0.22), outline=0.01)
    reloj = cyl("reloj", (3.9, 3.28, 4.2), 0.42, 0.08, (1, 1, 1), outline=0.03, vertices=32, rot=(D(90), 0, 0))
    box("aguja1", (3.9, 3.2, 4.33), (0.04, 0.02, 0.26), (0.1, 0.1, 0.1), outline=0)
    box("aguja2", (3.98, 3.2, 4.2), (0.2, 0.02, 0.04), (0.1, 0.1, 0.1), outline=0)
    # escritorio del profe
    box("escritorio", (-3.2, 1.6, 0.85), (2.2, 1.0, 0.12), (0.62, 0.4, 0.25))
    box("escritorio_frente", (-3.2, 1.12, 0.45), (2.2, 0.06, 0.8), (0.55, 0.35, 0.22))
    ball("manzana", (-2.7, 1.6, 1.02), 0.12, (0.95, 0.2, 0.2), outline=0.015, seg=12)
    box("libros", (-3.7, 1.6, 1.0), (0.4, 0.3, 0.2), (0.3, 0.45, 0.9), outline=0.015)
    # pupitres a los lados
    for k, (x, y) in enumerate([(2.6, 0.8), (4.4, 0.8), (2.6, -1.4), (-4.0, -1.0), (4.4, -1.4)]):
        box(f"pupitre{k}", (x, y, 0.75), (1.1, 0.7, 0.08), (0.95, 0.75, 0.4))
        cyl(f"pupitre_pata{k}", (x, y, 0.37), 0.05, 0.75, (0.4, 0.4, 0.45), outline=0.015, vertices=8)
        box(f"silla{k}", (x, y + 0.6, 0.45), (0.6, 0.5, 0.06), (0.3, 0.55, 0.85))
        box(f"silla_resp{k}", (x, y + 0.85, 0.8), (0.6, 0.06, 0.6), (0.3, 0.55, 0.85))
    return {"standing": (0, 0.8, 0)}


# ------------------------------------------------------------ exteriores

def exterior(cfg):
    ambiente(cfg)
    box("pasto", (0, 0, -0.05), (60, 60, 0.1), (0.42, 0.78, 0.35), outline=0)
    rnd = random.Random(3)
    for i in range(9):
        arbol(f"arbol{i}", rnd.uniform(-12, 12), rnd.uniform(5, 18), rnd.uniform(0.8, 1.4), pino=False)
    if not cfg.get("noche"):
        nubes(rnd)
    return {"standing": (0, 0, 0)}


def parque(cfg):
    ambiente(cfg)
    box("pasto", (0, 0, -0.05), (60, 60, 0.1), (0.45, 0.8, 0.38), outline=0)
    box("camino", (0, 2, 0.0), (60, 2.2, 0.04), (0.9, 0.8, 0.6), outline=0)
    rnd = random.Random(8)
    for i in range(10):
        arbol(f"arbol{i}", rnd.uniform(-15, 15), rnd.uniform(6, 20), rnd.uniform(0.9, 1.5), pino=i % 3 == 0)
    # banca
    box("banca_asiento", (-2.6, 1.0, 0.55), (2.0, 0.6, 0.1), (0.6, 0.38, 0.2))
    box("banca_resp", (-2.6, 1.28, 0.95), (2.0, 0.08, 0.6), (0.6, 0.38, 0.2))
    for sx in (-1, 1):
        box(f"banca_pata{sx}", (-2.6 + sx * 0.85, 1.0, 0.27), (0.1, 0.55, 0.55), (0.25, 0.25, 0.28))
    # flores
    for i in range(16):
        x, y = rnd.uniform(-6, 6), rnd.uniform(3.4, 6)
        cyl(f"tallo{i}", (x, y, 0.2), 0.02, 0.4, (0.2, 0.6, 0.2), outline=0, vertices=6)
        ball(f"flor{i}", (x, y, 0.42), 0.1, rnd.choice([(1, 0.3, 0.4), (1, 0.85, 0.2), (0.8, 0.5, 1)]),
             outline=0.012, seg=10)
    # farol
    cyl("farol", (2.8, 1.0, 1.5), 0.06, 3.0, (0.2, 0.2, 0.25), outline=0.015, vertices=8)
    lamp = ball("farol_luz", (2.8, 1.0, 3.1), 0.22, (1, 0.95, 0.6), outline=0.02, seg=12)
    if cfg.get("noche"):
        flat(lamp, (1, 0.95, 0.6))
    if not cfg.get("noche"):
        nubes(rnd)
    return {"standing": (0, 0, 0)}


def ciudad(cfg):
    ambiente(cfg, (0.6, 0.82, 1.0))
    box("banqueta", (0, -10, -0.02), (60, 26, 0.14), (0.78, 0.78, 0.8), outline=0)
    box("cordon", (0, 3.0, 0.02), (60, 0.25, 0.2), (0.6, 0.6, 0.62), outline=0.015)
    box("calle", (0, 7.0, -0.06), (60, 8, 0.1), (0.28, 0.28, 0.32), outline=0)
    for k in range(-8, 9):
        box(f"raya{k}", (k * 3.0, 7.0, 0.0), (1.4, 0.18, 0.02), (1, 0.9, 0.3), outline=0)
    box("banqueta_fondo", (0, 12.5, -0.02), (60, 3, 0.14), (0.78, 0.78, 0.8), outline=0)
    rnd = random.Random(21)
    x = -22.0
    k = 0
    noche = cfg.get("noche")
    while x < 22:
        w, h = rnd.uniform(3, 5.5), rnd.uniform(6, 16)
        col = rnd.choice([(0.95, 0.6, 0.45), (0.6, 0.7, 0.9), (0.95, 0.85, 0.55), (0.7, 0.85, 0.7),
                          (0.85, 0.65, 0.8)])
        box(f"edificio{k}", (x + w / 2, 16, h / 2), (w - 0.2, 4, h), col, outline=0.05)
        for fy in range(int(h // 1.6)):
            for fx in range(int((w - 0.6) // 1.0)):
                lit = noche and rnd.random() < 0.55
                c = (1, 0.9, 0.5) if lit else ((0.15, 0.2, 0.35) if noche else (0.6, 0.85, 1.0))
                win = box(f"ven{k}_{fx}_{fy}", (x + 0.7 + fx * 1.0, 13.98, 1.0 + fy * 1.6), (0.6, 0.05, 0.9),
                          c, outline=0.012)
                if lit:
                    flat(win, c)
        x += w
        k += 1
    for i, fx in enumerate((-6, 0, 6)):
        cyl(f"farola{i}", (fx + 3, 2.6, 1.6), 0.07, 3.2, (0.25, 0.25, 0.3), outline=0.015, vertices=8)
        luz = box(f"farola_luz{i}", (fx + 3, 2.4, 3.2), (0.4, 0.5, 0.15), (1, 0.95, 0.65), outline=0.015)
        if noche:
            flat(luz, (1, 0.95, 0.65))
    # coche
    cx = -3.5
    box("coche", (cx, 6.0, 0.75), (3.2, 1.5, 0.8), (0.9, 0.2, 0.2))
    box("coche_techo", (cx - 0.2, 6.0, 1.4), (1.8, 1.4, 0.6), (0.9, 0.2, 0.2))
    box("coche_vidrio", (cx - 0.2, 5.28, 1.4), (1.5, 0.04, 0.45), (0.6, 0.85, 1.0), outline=0.01)
    for sx in (-1, 1):
        cyl(f"llanta{sx}", (cx + sx * 1.0, 5.22, 0.38), 0.38, 0.25, (0.1, 0.1, 0.12), outline=0.015,
            vertices=16, rot=(D(90), 0, 0))
    return {"standing": (0, 0, 0)}


def playa(cfg):
    ambiente(cfg, (0.45, 0.8, 1.0))
    box("arena", (0, 0, -0.05), (60, 16, 0.1), (0.98, 0.88, 0.6), outline=0)
    box("mar", (0, 30, -0.08), (120, 44, 0.1), (0.15, 0.55, 0.85), outline=0)
    box("orilla", (0, 8.2, -0.04), (60, 0.6, 0.06), (1, 1, 1), outline=0)
    rnd = random.Random(4)
    for i in range(14):
        box(f"ola{i}", (rnd.uniform(-20, 20), rnd.uniform(10, 30), -0.01), (rnd.uniform(1, 3), 0.12, 0.02),
            (0.6, 0.85, 1.0), outline=0)
    if not cfg.get("noche"):
        flat(ball("sol_disco", (12, 80, 22), 5, (1, 0.9, 0.4), outline=0, seg=24), (1, 0.9, 0.4))
        nubes(rnd, 4, 60)
    # palmera
    px, py = -3.2, 3.0
    for k in range(7):
        cyl(f"palma{k}", (px + k * 0.12, py, 0.3 + k * 0.6), 0.2 - k * 0.015, 0.62, (0.65, 0.45, 0.25),
            outline=0.025, vertices=10, rot=(0, D(10), 0), smooth=False)
    top = (px + 0.85, py, 4.4)
    for k in range(7):
        a = k / 7 * 2 * math.pi
        leaf = ball(f"hoja{k}", (top[0] + math.cos(a) * 1.1, top[1] + math.sin(a) * 1.1, top[2] - 0.3), 1.0,
                    (0.25, 0.7, 0.3), outline=0.025, scale=(1.3, 0.35, 0.12), shadow=0.75, seg=12)
        leaf.rotation_euler = (0, D(20), a)
    for k in range(3):
        ball(f"coco{k}", (top[0] + (k - 1) * 0.22, top[1] - 0.15, top[2] - 0.35), 0.16, (0.45, 0.3, 0.15),
             outline=0.015, seg=10)
    # sombrilla y toalla
    cyl("sombrilla_palo", (2.8, 1.5, 1.2), 0.04, 2.4, (0.9, 0.9, 0.9), outline=0.015, vertices=8)
    cone("sombrilla", (2.8, 1.5, 2.45), 1.4, 0.05, 0.6, (1, 0.35, 0.35), outline=0.03, vertices=12)
    box("toalla", (2.6, 0.6, 0.0), (1.0, 2.0, 0.03), (0.3, 0.6, 1.0), outline=0.012)
    # castillo de arena
    box("castillo", (-1.5, -1.2, 0.25), (0.8, 0.8, 0.5), (0.95, 0.8, 0.5))
    for k, (dx, dy) in enumerate([(-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)]):
        cyl(f"torre{k}", (-1.5 + dx, -1.2 + dy, 0.4), 0.15, 0.8, (0.95, 0.8, 0.5), outline=0.015, vertices=10)
    return {"standing": (0, 0, 0)}


def espacio(cfg):
    world((0.05, 0.03, 0.15), 0.3, (0.7, 0.7, 1.0))
    sun(3.5, (1, 0.97, 0.9), (40, 0, -40))
    box("suelo_lunar", (0, 0, -0.05), (80, 80, 0.1), (0.72, 0.72, 0.76), outline=0)
    rnd = random.Random(9)
    for i in range(12):
        x, y = rnd.uniform(-10, 10), rnd.uniform(-2, 14)
        if abs(x) < 1.5 and y < 2:
            continue
        r = rnd.uniform(0.4, 1.3)
        cyl(f"crater{i}", (x, y, 0.0), r, 0.08, (0.6, 0.6, 0.65), outline=0.02, vertices=20)
        cyl(f"crater_in{i}", (x, y, 0.03), r * 0.75, 0.06, (0.5, 0.5, 0.56), outline=0, vertices=20)
    for i in range(90):
        b = ball(f"estrella{i}", (rnd.uniform(-50, 50), 70, rnd.uniform(-5, 40)), rnd.uniform(0.08, 0.25),
                 (1, 1, 1), outline=0, seg=6)
        flat(b, (1, 1, 0.95))
    ball("planeta", (14, 60, 18), 6, (0.95, 0.55, 0.3), outline=0.15, shadow=0.6)
    ring = prim("torus", "anillo", major_radius=9, minor_radius=0.5, major_segments=48, minor_segments=6,
                location=(14, 60, 18), rotation=(D(70), D(15), 0))
    ring.scale = (1, 1, 0.15)
    finish(ring, mat((0.98, 0.85, 0.55), 0.7), 0.08)
    ball("tierra", (-16, 70, 26), 3.5, (0.25, 0.55, 0.95), outline=0.1, shadow=0.6)
    # cohete
    rx, ry = 3.5, 4.0
    cyl("cohete", (rx, ry, 2.0), 0.7, 3.0, (0.95, 0.95, 0.97), outline=0.035, vertices=24)
    cone("cohete_punta", (rx, ry, 4.1), 0.7, 0, 1.2, (0.9, 0.2, 0.2), outline=0.035, vertices=24)
    cyl("ventanilla", (rx, ry - 0.68, 2.8), 0.25, 0.08, (0.5, 0.8, 1.0), outline=0.025, vertices=20,
        rot=(D(90), 0, 0))
    for k in range(3):
        a = k / 3 * 2 * math.pi
        box(f"aleta{k}", (rx + math.cos(a) * 0.8, ry + math.sin(a) * 0.8, 0.8), (0.12, 0.6, 1.0),
            (0.9, 0.2, 0.2), rot=(0, 0, a + D(90)))
    return {"standing": (0, 0, 0)}


def bosque(cfg):
    ambiente(cfg, (0.6, 0.85, 0.95))
    box("suelo", (0, 0, -0.05), (60, 60, 0.1), (0.3, 0.6, 0.28), outline=0)
    rnd = random.Random(13)
    for i in range(22):
        x, y = rnd.uniform(-14, 14), rnd.uniform(2.5, 20)
        if abs(x) < 2 and y < 5:
            x += 4 * (1 if x >= 0 else -1)
        tone = rnd.choice([(0.15, 0.5, 0.25), (0.2, 0.58, 0.3), (0.12, 0.42, 0.22)])
        arbol(f"arbol{i}", x, y, rnd.uniform(0.9, 1.7), tone, pino=rnd.random() < 0.65)
    for i in range(6):
        x, y = rnd.choice([-1, 1]) * rnd.uniform(1.5, 4), rnd.uniform(-1, 3)
        cyl(f"hongo_pie{i}", (x, y, 0.15), 0.07, 0.3, (1, 0.97, 0.9), outline=0.012, vertices=10)
        cap = ball(f"hongo{i}", (x, y, 0.32), 0.2, (0.9, 0.15, 0.15), outline=0.015, scale=(1, 1, 0.6), seg=14)
        for k in range(3):
            ball(f"punto{i}_{k}", (x + (k - 1) * 0.1, y - 0.12, 0.38), 0.035, (1, 1, 1), outline=0, seg=6)
    for i in range(5):
        x, y = rnd.uniform(-6, 6), rnd.uniform(1, 6)
        if abs(x) < 1.2:
            continue
        r = ball(f"roca{i}", (x, y, 0.15), rnd.uniform(0.3, 0.6), (0.55, 0.55, 0.6), outline=0.025,
                 scale=(1.3, 1, 0.7), seg=8)
        for poly in r.data.polygons:
            poly.use_smooth = False
    cyl("tronco_caido", (-2.6, 1.5, 0.3), 0.3, 2.4, (0.5, 0.32, 0.2), outline=0.025, vertices=12,
        rot=(0, D(90), D(20)))
    return {"standing": (0, 0, 0)}


def vacio(cfg):
    col = tuple(cfg.get("color_fondo") or (0.98, 0.8, 0.25))
    world(col)
    sun()
    floor = box("piso", (0, 0, -0.05), (40, 40, 0.1), tuple(c * 0.9 for c in col), outline=0)
    floor.visible_shadow = False
    return {"standing": (0, 0, 0)}


SETS = {f.__name__: f for f in (habitacion, cocina, escuela, exterior, parque, ciudad, playa, espacio,
                                bosque, vacio)}
