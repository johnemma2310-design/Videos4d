"""Construye personajes en Blender a partir de assets/personajes.json.

Todos devuelven el mismo diccionario de partes para que las poses funcionen igual:
root, body, neck, head, arm_d, arm_i, leg_d, leg_i (+ tail en animales).
En animales: arm_* = patas delanteras (alas en el pájaro), leg_* = patas traseras.
El frente de todos los personajes mira hacia -Y.
"""
import bpy

from bl_util import (D, ball, box, cone, cyl, empty, finish, mat, mix_node, prim, socket, sphere_cap,
                     toon_material)

WHITE = (1, 1, 1)
R_HUMAN = 0.62


# ---------------------------------------------------------------- cabeza

def head_material(face_png, radius, base=WHITE):
    m, nt, emit = toon_material("cabeza", base, shadow=0.86)
    ramp_out = emit.inputs["Color"].links[0].from_socket
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    W = 2 * radius * 0.98

    def math_node(op, a, b):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs[0]

    u = math_node("ADD", math_node("DIVIDE", sep.outputs["X"], W), 0.5)
    v = math_node("ADD", math_node("DIVIDE", sep.outputs["Z"], W), 0.5)
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(u, comb.inputs["X"])
    nt.links.new(v, comb.inputs["Y"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(face_png), check_existing=True)
    tex.extension = "CLIP"
    tex.interpolation = "Cubic"
    nt.links.new(comb.outputs[0], tex.inputs["Vector"])
    front = math_node("LESS_THAN", sep.outputs["Y"], -0.05 * radius / 0.62)
    fac = math_node("MULTIPLY", tex.outputs["Alpha"], front)
    mix = mix_node(nt)
    nt.links.new(fac, socket(mix.inputs, "Factor", "VALUE"))
    nt.links.new(ramp_out, socket(mix.inputs, "A", "RGBA"))
    nt.links.new(tex.outputs["Color"], socket(mix.inputs, "B", "RGBA"))
    nt.links.new(socket(mix.outputs, "Result", "RGBA"), emit.inputs["Color"])
    return m


def make_head(name, parent, loc, radius, face_png, base=WHITE, outline=0.035):
    h = prim("uv_sphere", name, parent, segments=48, ring_count=24, radius=radius)
    h.location = loc
    finish(h, head_material(face_png, radius, base), outline)
    return h


def limb(name, pivot, length, color=WHITE, radius=0.05, end_radius=0.075, outline=0.022):
    stick = prim("cylinder", name, pivot, vertices=12, radius=radius, depth=length)
    stick.location = (0, 0, -length / 2)
    finish(stick, mat(color, 0.85), outline)
    tip = prim("uv_sphere", name + "_punta", pivot, segments=16, ring_count=8, radius=end_radius)
    tip.location = (0, 0, -length)
    finish(tip, mat(color, 0.85), outline)
    return stick


# ------------------------------------------------------------ accesorios
# Cada accesorio recibe (partes, color). Las coordenadas de pelo/sombreros son
# locales a la cabeza (centro de la esfera); las de ropa, locales al cuerpo.

R = R_HUMAN
HAIR = (0.25, 0.17, 0.12)


def _hairline(r, front=0.6, side=0.15, back=-0.25):
    def keep(x, y, z):
        yn = y / r
        lim = side + (front - side) * max(-yn, 0) + (back - side) * max(yn, 0)
        return z > r * lim
    return keep


def acc_pelo_corto(p, c):
    sphere_cap("pelo", R * 1.06, _hairline(R * 1.06), c or HAIR, p["head"])


def acc_pelo_largo(p, c):
    c = c or HAIR
    sphere_cap("pelo", R * 1.06, _hairline(R * 1.06, front=0.55, side=-0.1, back=-0.6), c, p["head"])
    ball("pelo_atras", (0, R * 0.3, -R * 0.45), R, c, p["head"], 0.03, scale=(0.98, 0.6, 1.15))


def acc_chongo(p, c):
    c = c or (0.6, 0.6, 0.64)
    sphere_cap("pelo", R * 1.05, _hairline(R * 1.05, front=0.5, side=0.05), c, p["head"])
    ball("chongo", (0, R * 0.35, R * 1.0), R * 0.38, c, p["head"], 0.03)


def acc_coletas(p, c):
    c = c or HAIR
    sphere_cap("pelo", R * 1.06, _hairline(R * 1.06, front=0.55), c, p["head"])
    for sx in (-1, 1):
        ball(f"coleta{sx}", (sx * R * 1.08, R * 0.15, 0), R * 0.3, c, p["head"], 0.03, scale=(0.9, 0.9, 1.5))


def acc_lazo(p, c):
    c = c or (1, 0.4, 0.65)
    for sx in (-1, 1):
        ball(f"lazo{sx}", (R * 0.35 + sx * R * 0.2, -R * 0.1, R * 0.95), R * 0.17, c, p["head"], 0.02,
             scale=(1.3, 0.6, 0.9))
    ball("lazo_c", (R * 0.35, -R * 0.12, R * 0.95), R * 0.08, c, p["head"], 0.02)


def acc_calvo(p, c):
    c = c or (0.85, 0.85, 0.88)
    for sx in (-1, 1):
        ball(f"pelo_lado{sx}", (sx * R * 0.93, R * 0.2, R * 0.05), R * 0.3, c, p["head"], 0.025,
             scale=(0.55, 1, 0.9))


def acc_pelo_punta(p, c):
    c = c or (0.95, 0.3, 0.15)
    sphere_cap("pelo", R * 1.06, _hairline(R * 1.06), c, p["head"])
    for i, (x, y, rx, ry) in enumerate([(0, 0, 0, 0), (-0.45, 0.1, 0, -35), (0.45, 0.1, 0, 35),
                                         (-0.2, 0.45, 30, -15), (0.2, 0.45, 30, 15)]):
        cone(f"punta{i}", (x * R, y * R, R * 1.05), R * 0.28, 0, R * 0.7, c, p["head"], 0.025,
             vertices=8, rot=(D(rx), D(ry), 0))


def acc_gorra(p, c):
    c = c or (0.9, 0.2, 0.2)
    sphere_cap("gorra", R * 1.07, lambda x, y, z: z > R * 0.25, c, p["head"])
    v = cyl("visera", (0, -R * 0.95, R * 0.4), R * 0.6, 0.06, c, p["head"], 0.025, vertices=24,
            rot=(D(28), 0, 0))
    v.scale = (1, 0.75, 1)


def acc_gorra_policia(p, c):
    c = c or (0.12, 0.18, 0.4)
    cyl("gorra_copa", (0, 0, R * 0.8), R * 0.95, R * 0.5, c, p["head"], 0.03, vertices=32)
    cyl("gorra_banda", (0, 0, R * 0.62), R * 0.92, R * 0.14, (0.08, 0.08, 0.1), p["head"], 0.02, vertices=32)
    v = cyl("visera", (0, -R * 0.75, R * 0.55), R * 0.55, 0.05, (0.08, 0.08, 0.1), p["head"], 0.02,
            vertices=24, rot=(D(-15), 0, 0))
    v.scale = (1, 0.7, 1)
    ball("placa", (0, -R * 0.93, R * 0.8), R * 0.1, (1, 0.85, 0.2), p["head"], 0.015, scale=(1, 0.3, 1.2))


def acc_sombrero(p, c):
    c = c or (0.6, 0.38, 0.18)
    cyl("ala", (0, 0, R * 0.6), R * 1.65, 0.06, c, p["head"], 0.03, vertices=32)
    cyl("copa", (0, 0, R * 0.95), R * 0.78, R * 0.75, c, p["head"], 0.03, vertices=32)
    cyl("cinta", (0, 0, R * 0.7), R * 0.8, R * 0.15, (0.15, 0.1, 0.08), p["head"], 0.0, vertices=32)


def acc_gorro_chef(p, c):
    c = c or WHITE
    cyl("gorro", (0, 0, R * 1.05), R * 0.75, R * 0.85, c, p["head"], 0.03, vertices=32)
    for i, (x, y) in enumerate([(-0.4, 0), (0.4, 0), (0, -0.35), (0, 0.35), (0, 0)]):
        ball(f"gorro_bola{i}", (x * R, y * R, R * 1.55), R * 0.42, c, p["head"], 0.03)


def acc_bufanda(p, c):
    c = c or (0.13, 0.48, 0.95)
    t = prim("torus", "bufanda", p["body"], major_radius=0.2, minor_radius=0.085,
             major_segments=32, minor_segments=12)
    t.location = (0, 0, 1.86)
    t.scale = (1, 1, 0.9)
    finish(t, mat(c, 0.72), 0.025)
    box("bufanda_cola", (-0.12, -0.17, 1.62), (0.13, 0.05, 0.42), c, p["body"], 0.022, 0.72,
        rot=(D(8), 0, D(-12)))


def acc_corbata(p, c):
    c = c or (0.85, 0.15, 0.2)
    box("corbata_nudo", (0, -0.075, 1.8), (0.1, 0.05, 0.08), c, p["body"], 0.015)
    cone("corbata", (0, -0.075, 1.55), 0.09, 0.03, 0.45, c, p["body"], 0.015, vertices=4,
         rot=(D(180), 0, D(45))).scale = (1, 0.35, 1)


def acc_falda(p, c):
    cone("falda", (0, 0, 1.1), 0.42, 0.1, 0.42, c or (0.95, 0.45, 0.35), p["body"], 0.025, vertices=24)


def acc_vestido(p, c):
    cone("vestido", (0, 0, 1.33), 0.45, 0.1, 0.95, c or (1, 0.55, 0.75), p["body"], 0.025, vertices=24)


def acc_bata(p, c):
    cone("bata", (0, 0, 1.2), 0.42, 0.14, 1.25, c or WHITE, p["body"], 0.025, vertices=24)
    box("bata_bolsillo", (0.16, -0.27, 1.05), (0.12, 0.02, 0.1), (0.85, 0.9, 1), p["body"], 0.012)


def acc_delantal(p, c):
    box("delantal", (0, -0.08, 1.3), (0.5, 0.03, 0.7), c or WHITE, p["body"], 0.02)


def acc_collar(p, c):
    t = prim("torus", "collar", p["body"], major_radius=0.17, minor_radius=0.035,
             major_segments=24, minor_segments=8)
    t.location = (0, -0.02, 1.8)
    t.rotation_euler = (D(20), 0, 0)
    finish(t, mat(c or WHITE, 0.85), 0.012)


def acc_baston(p, c):
    c = c or (0.45, 0.28, 0.15)
    cyl("baston", (-0.3, -0.12, 0.5), 0.035, 1.0, c, p["body"], 0.015, vertices=10)
    t = prim("torus", "baston_mango", p["body"], major_radius=0.1, minor_radius=0.035,
             major_segments=16, minor_segments=8)
    t.location = (-0.2, -0.12, 1.0)
    t.rotation_euler = (D(90), 0, 0)
    finish(t, mat(c, 0.8), 0.015)


ACCESORIOS = {k[4:]: v for k, v in globals().items() if k.startswith("acc_")}


# --------------------------------------------------------------- humanos

def build_humano(d, face_png):
    root = empty(d.get("id", "personaje"))
    body = empty("cuerpo", parent=root)
    skin = tuple(d.get("color_piel", WHITE))
    t = prim("cylinder", "torso", body, vertices=12, radius=0.055, depth=0.9)
    t.location = (0, 0, 1.45)
    finish(t, mat(skin, 0.85), 0.022)
    neck = empty("cuello", (0, 0, 1.88), body)
    head = make_head("cabeza", neck, (0, 0, R - 0.06), R, face_png, skin)
    p = {"root": root, "body": body, "neck": neck, "head": head, "kind": "humano",
         "drop": 1.45}
    for side, sx in (("d", -1), ("i", 1)):
        a = empty(f"brazo_{side}", (0.04 * sx, 0, 1.78), body)
        limb(f"brazo_{side}_palo", a, 0.85, skin)
        lg = empty(f"pierna_{side}", (0.03 * sx, 0, 1.0), body)
        limb(f"pierna_{side}_palo", lg, 1.0, skin, end_radius=0.08)
        p["arm_" + side], p["leg_" + side] = a, lg
    colors = d.get("colores", {})
    hair_color = colors.get("pelo")
    for name in d.get("accesorios", []):
        fn = ACCESORIOS.get(name)
        if not fn:
            print(f"[aviso] accesorio '{name}' no existe")
            continue
        fn(p, tuple(colors[name]) if name in colors else (tuple(hair_color) if hair_color and
                                                          name.startswith(("pelo", "chongo", "coletas", "calvo")) else None))
    return p


# --------------------------------------------------------------- animales

def build_cuadrupedo(d, face_png, kind):
    colors = d.get("colores", {})
    body_c = tuple(colors.get("cuerpo", (0.86, 0.6, 0.35)))
    ear_c = tuple(colors.get("orejas", body_c))
    root = empty(d.get("id", kind))
    body = empty("cuerpo", parent=root)
    ball("torso", (0, 0.05, 0.85), 0.5, body_c, body, 0.03, scale=(0.72, 1.3, 0.66))
    neck = empty("cuello", (0, -0.5, 1.0), body)
    hr = 0.5
    head = make_head("cabeza", neck, (0, -0.12, 0.32), hr, face_png, body_c)
    p = {"root": root, "body": body, "neck": neck, "head": head, "kind": kind, "drop": 0.75}
    if kind == "perro":
        for sx in (-1, 1):
            o = ball(f"oreja{sx}", (sx * hr * 0.92, hr * 0.1, hr * 0.15), hr * 0.42, ear_c, head, 0.025,
                     scale=(0.4, 0.6, 1.2))
            o.rotation_euler = (0, D(-sx * 15), 0)
    elif kind == "gato":
        for sx in (-1, 1):
            cone(f"oreja{sx}", (sx * hr * 0.55, 0, hr * 0.85), hr * 0.32, 0, hr * 0.55, ear_c, head, 0.025,
                 vertices=4, rot=(0, D(sx * 20), D(45)))
    elif kind == "cerdo":
        for sx in (-1, 1):
            cone(f"oreja{sx}", (sx * hr * 0.6, 0, hr * 0.8), hr * 0.28, 0, hr * 0.4, ear_c, head, 0.025,
                 vertices=3, rot=(D(-25), D(sx * 35), 0))
    for side, sx in (("d", -1), ("i", 1)):
        a = empty(f"pata_del_{side}", (0.22 * sx, -0.45, 0.62), body)
        limb(f"pata_del_{side}_palo", a, 0.6, body_c, radius=0.07, end_radius=0.1)
        lg = empty(f"pata_tras_{side}", (0.22 * sx, 0.55, 0.62), body)
        limb(f"pata_tras_{side}_palo", lg, 0.6, body_c, radius=0.07, end_radius=0.1)
        p["arm_" + side], p["leg_" + side] = a, lg
    tail = empty("cola", (0, 0.95, 1.0), body)
    if kind == "cerdo":
        t = prim("torus", "cola_rizo", tail, major_radius=0.1, minor_radius=0.03, major_segments=16,
                 minor_segments=6)
        t.rotation_euler = (0, D(90), 0)
        finish(t, mat(ear_c, 0.8), 0.015)
    else:
        length = 0.75 if kind == "gato" else 0.5
        c = cyl("cola_palo", (0, 0, length / 2), 0.06 if kind == "perro" else 0.05, length, body_c, tail,
                0.02, vertices=10)
        tail.rotation_euler = (D(-35 if kind == "perro" else -15), 0, 0)
    p["tail"] = tail
    return p


def build_pajaro(d, face_png):
    colors = d.get("colores", {})
    body_c = tuple(colors.get("cuerpo", (0.35, 0.75, 1.0)))
    wing_c = tuple(colors.get("alas", body_c))
    root = empty(d.get("id", "pajaro"))
    body = empty("cuerpo", parent=root)
    neck = empty("cuello", (0, 0, 0.45), body)
    r = 0.55
    head = make_head("cabeza", neck, (0, 0, r), r, face_png, body_c)
    p = {"root": root, "body": body, "neck": neck, "head": head, "kind": "pajaro", "drop": 0.45}
    for i, rz in enumerate((-20, 0, 20)):
        cone(f"cresta{i}", (0, 0.05, r * 1.0), 0.09, 0, 0.3, wing_c, head, 0.015, vertices=6,
             rot=(0, D(rz), 0))
    for side, sx in (("d", -1), ("i", 1)):
        a = empty(f"ala_{side}", (sx * r * 0.92, 0.05, 1.05), body)
        ball(f"ala_{side}_m", (0, 0, -0.25), 0.3, wing_c, a, 0.025, scale=(0.3, 0.7, 1.0))
        lg = empty(f"pata_{side}", (sx * 0.15, 0, 0.5), body)
        limb(f"pata_{side}_palo", lg, 0.5, (1, 0.6, 0.15), radius=0.03, end_radius=0.06, outline=0.015)
        p["arm_" + side], p["leg_" + side] = a, lg
    tail = empty("cola", (0, r * 0.9, 0.85), body)
    cone("cola_plumas", (0, 0.15, 0), 0.18, 0.02, 0.35, wing_c, tail, 0.02, vertices=4,
         rot=(D(-70), 0, 0))
    p["tail"] = tail
    return p


def build(d, face_png):
    kind = d.get("tipo", "humano")
    if kind == "humano":
        return build_humano(d, face_png)
    if kind == "pajaro":
        return build_pajaro(d, face_png)
    return build_cuadrupedo(d, face_png, kind)
