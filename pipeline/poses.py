"""Poses animadas. Cada pose recibe las partes de un personaje (ver personajes_bl.py)
y pone keyframes entre f0 y f1. Si la pose desplaza al personaje devuelve True
(la cámara lo sigue).
"""
import math
import random

from mathutils import Vector

from bl_util import D, key

# ================================================================= humanos


def rest(p, f):
    for s, sx in (("d", -1), ("i", 1)):
        key(p["arm_" + s], "rotation_euler", f, (0, D(-12) * sx, 0))
        key(p["leg_" + s], "rotation_euler", f, (0, D(-5) * sx, 0))
    key(p["body"], "location", f, (0, 0, 0))
    key(p["body"], "rotation_euler", f, (0, 0, 0))
    key(p["neck"], "rotation_euler", f, (0, 0, 0))


def arm(p, side, f, out_deg, fwd_deg=0):
    """out_deg: hacia afuera (0 = colgando, 180 = arriba). fwd_deg: hacia el frente."""
    sx = -1 if side == "d" else 1
    key(p["arm_" + side], "rotation_euler", f, (D(-fwd_deg), D(-out_deg) * sx, 0))


def leg(p, side, f, out_deg, fwd_deg=0):
    sx = -1 if side == "d" else 1
    key(p["leg_" + side], "rotation_euler", f, (D(-fwd_deg), D(-out_deg) * sx, 0))


def frames(f0, f1, step):
    f = f0
    while f < f1:
        yield f
        f += step
    yield f1


def pose_de_pie(p, f0, f1, fps):
    for f in frames(f0, f1, 8):
        t = (f - f0) / fps
        key(p["body"], "location", f, (0, 0, 0.02 * math.sin(t * 4)))
        arm(p, "d", f, 12 + 3 * math.sin(t * 4))
        arm(p, "i", f, 12 + 3 * math.sin(t * 4 + 1))
        key(p["neck"], "rotation_euler", f, (0, D(4 * math.sin(t * 2)), 0))


def pose_saludar(p, f0, f1, fps):
    pose_de_pie(p, f0, f1, fps)
    for f in frames(f0, f1, 4):
        t = (f - f0) / fps
        arm(p, "d", f, 110 + 18 * math.sin(t * 16))
    for f in frames(f0, f1, 10):
        t = (f - f0) / fps
        key(p["neck"], "rotation_euler", f, (0, D(-8 + 3 * math.sin(t * 3)), 0))


def pose_pensar(p, f0, f1, fps):
    pose_de_pie(p, f0, f1, fps)
    for f in frames(f0, f1, 10):
        t = (f - f0) / fps
        arm(p, "d", f, 25, 125 + 4 * math.sin(t * 3))
        arm(p, "i", f, 10, 30)
        key(p["neck"], "rotation_euler", f, (D(-6), D(10 + 3 * math.sin(t * 2)), D(8)))


def pose_caminar(p, f0, f1, fps, speed=1.1, cadence=4.0, lean=0, swing=32):
    root = p["root"]
    start = Vector(root.location)
    fwd = Vector((0, -1, 0))
    for f in frames(f0, f1, 2):
        t = (f - f0) / fps
        ph = math.sin(t * cadence * math.pi)
        leg(p, "d", f, 4, swing * ph)
        leg(p, "i", f, 4, -swing * ph)
        arm(p, "d", f, 12, -swing * 0.9 * ph)
        arm(p, "i", f, 12, swing * 0.9 * ph)
        key(p["body"], "location", f, (0, 0, 0.05 * abs(math.sin(t * cadence * math.pi))))
        key(p["body"], "rotation_euler", f, (D(lean), 0, 0))
        key(root, "location", f, tuple(start + fwd * speed * t))
    return speed


def pose_correr(p, f0, f1, fps):
    return pose_caminar(p, f0, f1, fps, speed=3.2, cadence=7, lean=14, swing=55)


def pose_saltar(p, f0, f1, fps):
    for f in frames(f0, f1, 2):
        t = (f - f0) / fps
        h = abs(math.sin(t * math.pi * 1.6))
        key(p["body"], "location", f, (0, 0, 0.9 * h))
        arm(p, "d", f, 50 + 70 * h)
        arm(p, "i", f, 50 + 70 * h)
        leg(p, "d", f, 5 + 15 * h)
        leg(p, "i", f, 5 + 15 * h)


def pose_celebrar(p, f0, f1, fps):
    for f in frames(f0, f1, 3):
        t = (f - f0) / fps
        b = abs(math.sin(t * math.pi * 2.4))
        key(p["body"], "location", f, (0, 0, 0.25 * b))
        arm(p, "d", f, 118 + 10 * math.sin(t * 12))
        arm(p, "i", f, 118 + 10 * math.sin(t * 12 + 2))
        leg(p, "d", f, 8)
        leg(p, "i", f, 8)


def pose_temblar(p, f0, f1, fps):
    import random
    rnd = random.Random(f0)
    for f in frames(f0, f1, 1):
        key(p["body"], "location", f, (rnd.uniform(-.025, .025), rnd.uniform(-.01, .01), 0))
        arm(p, "d", f, 4, 35 + rnd.uniform(-4, 4))
        arm(p, "i", f, 4, 35 + rnd.uniform(-4, 4))
        leg(p, "d", f, 1)
        leg(p, "i", f, 1)
        key(p["neck"], "rotation_euler", f, (D(-4), D(rnd.uniform(-2, 2)), 0))


def pose_mareado(p, f0, f1, fps):
    for f in frames(f0, f1, 3):
        t = (f - f0) / fps
        key(p["body"], "rotation_euler", f, (D(2 * math.cos(t * 5)), D(4 * math.sin(t * 5)), 0))
        key(p["neck"], "rotation_euler", f, (0, D(18 * math.sin(t * 5 + 0.8)), D(10 * math.sin(t * 3))))
        arm(p, "d", f, 50 + 20 * math.sin(t * 5))
        arm(p, "i", f, 50 - 20 * math.sin(t * 5))
        leg(p, "d", f, 10)
        leg(p, "i", f, 10)


def pose_triste(p, f0, f1, fps):
    for f in frames(f0, f1, 10):
        t = (f - f0) / fps
        key(p["neck"], "rotation_euler", f, (D(18 + 2 * math.sin(t * 2)), 0, 0))
        key(p["body"], "rotation_euler", f, (D(6), 0, 0))
        arm(p, "d", f, 4, 8)
        arm(p, "i", f, 4, 8)
        leg(p, "d", f, 3)
        leg(p, "i", f, 3)


def pose_senalar(p, f0, f1, fps):
    pose_de_pie(p, f0, f1, fps)
    for f in frames(f0, f1, 10):
        arm(p, "d", f, 92, 10)


def pose_acostado(p, f0, f1, fps):
    root = p["root"]
    root.rotation_euler = (D(-90), 0, 0)   # boca arriba, cabeza hacia el fondo (+Y)
    root.location = (-1.3, -0.68, 1.2)
    for f in frames(f0, f1, 12):
        t = (f - f0) / fps
        key(p["neck"], "rotation_euler", f, (0, D(6 * math.sin(t * 1.5)), 0))
        arm(p, "d", f, 8)
        arm(p, "i", f, 8)
        leg(p, "d", f, 2)
        leg(p, "i", f, 2)


POSES = {
    "de_pie": pose_de_pie, "saludar": pose_saludar, "pensar": pose_pensar,
    "caminar": pose_caminar, "correr": pose_correr, "saltar": pose_saltar,
    "celebrar": pose_celebrar, "temblar": pose_temblar, "mareado": pose_mareado,
    "triste": pose_triste, "senalar": pose_senalar, "acostado": pose_acostado,
}



# ================================================================ animales


def a_rest(p, f):
    for s in ("d", "i"):
        key(p["arm_" + s], "rotation_euler", f, (0, 0, 0))
        key(p["leg_" + s], "rotation_euler", f, (0, 0, 0))
    key(p["body"], "location", f, (0, 0, 0))
    key(p["body"], "rotation_euler", f, (0, 0, 0))
    key(p["neck"], "rotation_euler", f, (0, 0, 0))


def a_cola(p, f0, f1, fps, speed=9, amp=28, down=False):
    tail = p.get("tail")
    if not tail:
        return
    base = tail.rotation_euler.copy()
    for f in frames(f0, f1, 2):
        t = (f - f0) / fps
        bx = base.x + (D(50) if down else 0)
        key(tail, "rotation_euler", f, (bx, 0, base.z + D(amp * math.sin(t * speed))))


def a_quieto(p, f0, f1, fps):
    a_cola(p, f0, f1, fps)
    for f in frames(f0, f1, 8):
        t = (f - f0) / fps
        key(p["neck"], "rotation_euler", f, (D(3 * math.sin(t * 1.5)), D(8 * math.sin(t * 1.1)), 0))
        key(p["body"], "location", f, (0, 0, 0.015 * math.sin(t * 4)))
        if p["kind"] == "pajaro":
            out = 8 + 6 * math.sin(t * 6)
            key(p["arm_d"], "rotation_euler", f, (0, D(out), 0))
            key(p["arm_i"], "rotation_euler", f, (0, D(-out), 0))


def a_caminar(p, f0, f1, fps, speed=1.0, cadence=4.0, swing=30):
    a_cola(p, f0, f1, fps, speed=14)
    root = p["root"]
    start = Vector(root.location)
    for f in frames(f0, f1, 2):
        t = (f - f0) / fps
        ph = math.sin(t * cadence * math.pi)
        if p["kind"] == "pajaro":   # saltitos
            key(p["body"], "location", f, (0, 0, 0.12 * abs(ph)))
            for s, sx in (("d", 1), ("i", -1)):
                key(p["arm_" + s], "rotation_euler", f, (0, D(sx * 20 * abs(ph)), 0))
        else:
            key(p["arm_d"], "rotation_euler", f, (D(-swing * ph), 0, 0))
            key(p["leg_i"], "rotation_euler", f, (D(-swing * ph), 0, 0))
            key(p["arm_i"], "rotation_euler", f, (D(swing * ph), 0, 0))
            key(p["leg_d"], "rotation_euler", f, (D(swing * ph), 0, 0))
            key(p["body"], "location", f, (0, 0, 0.04 * abs(ph)))
        key(root, "location", f, tuple(start + Vector((0, -speed * t, 0))))
    return True


def a_correr(p, f0, f1, fps):
    return a_caminar(p, f0, f1, fps, speed=3.0, cadence=7, swing=50)


def a_saltar(p, f0, f1, fps):
    a_cola(p, f0, f1, fps, speed=16, amp=35)
    for f in frames(f0, f1, 2):
        t = (f - f0) / fps
        h = abs(math.sin(t * math.pi * 1.8))
        key(p["body"], "location", f, (0, 0, 0.6 * h))
        if p["kind"] == "pajaro":
            for s, sx in (("d", 1), ("i", -1)):
                key(p["arm_" + s], "rotation_euler", f, (0, D(sx * (20 + 70 * h)), 0))
        else:
            key(p["arm_d"], "rotation_euler", f, (D(-40 * h), 0, 0))
            key(p["arm_i"], "rotation_euler", f, (D(-40 * h), 0, 0))
            key(p["leg_d"], "rotation_euler", f, (D(40 * h), 0, 0))
            key(p["leg_i"], "rotation_euler", f, (D(40 * h), 0, 0))


def a_volar(p, f0, f1, fps):
    for f in frames(f0, f1, 2):
        t = (f - f0) / fps
        flap = 55 * math.sin(t * 22)
        key(p["body"], "location", f, (0, 0, 0.9 + 0.15 * math.sin(t * 4)))
        key(p["arm_d"], "rotation_euler", f, (0, D(30 + flap), 0))
        key(p["arm_i"], "rotation_euler", f, (0, D(-30 - flap), 0))
        key(p["leg_d"], "rotation_euler", f, (D(30), 0, 0))
        key(p["leg_i"], "rotation_euler", f, (D(30), 0, 0))


def a_temblar(p, f0, f1, fps):
    rnd = random.Random(f0)
    a_cola(p, f0, f1, fps, speed=30, amp=6, down=True)
    for f in frames(f0, f1, 1):
        key(p["body"], "location", f, (rnd.uniform(-.025, .025), rnd.uniform(-.01, .01), 0))


def a_triste(p, f0, f1, fps):
    a_cola(p, f0, f1, fps, speed=2, amp=5, down=True)
    for f in frames(f0, f1, 10):
        t = (f - f0) / fps
        key(p["neck"], "rotation_euler", f, (D(22 + 2 * math.sin(t * 2)), 0, 0))


ANIMAL_POSES = {"de_pie": a_quieto, "caminar": a_caminar, "correr": a_correr, "saltar": a_saltar,
                "celebrar": a_saltar, "volar": a_volar, "temblar": a_temblar, "triste": a_triste}


def animar(p, pose, f0, f1, fps):
    """Aplica la pose al personaje (humano o animal). Devuelve True si se desplaza."""
    if p["kind"] == "humano":
        rest(p, f0)
        fn = POSES.get(pose, pose_de_pie)
    else:
        a_rest(p, f0)
        fn = ANIMAL_POSES.get(pose, a_quieto)
    return bool(fn(p, f0, f1, fps))
