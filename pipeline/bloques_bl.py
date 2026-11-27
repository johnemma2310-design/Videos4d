"""Personajes estilo bloques (muñecos de juguete cuadrados) para el estilo "bloques".

Mismas partes que personajes_bl.py (root, body, neck, head, arm_*, leg_*, tail) para que
todas las poses de poses.py funcionen igual. El frente mira a -Y.

Proporciones (unidades de Blender): piernas 0–1.15, torso 1.15–2.3, cabeza cúbica encima.
Colores por parte en "colores": piel, camisa, pantalon, zapatos, pelo y uno por accesorio.
"""
import bpy

from bl_util import D, ball, bevel, box, cone, cyl, empty, finish, mat, prim
from personajes_bl import head_material

SKIN = (1.0, 0.86, 0.72)
SHIRT = (0.25, 0.55, 0.95)
PANTS = (0.2, 0.25, 0.4)
SHOES = (0.15, 0.13, 0.12)
HAIR = (0.3, 0.2, 0.12)

HEAD = 0.76            # lado de la cabeza (≈ 0.65 del ancho del torso, como un juguete de bloques)
NECK_Z = 2.3
H = HEAD / 2


def block_head(name, parent, loc, size, face_png, base):
    h = prim("cube", name, parent, size=size)
    h.location = loc
    finish(h, head_material(face_png, size / 2, base), 0, smooth=False)
    bevel(h, size * 0.24, 5)
    return h


def _part(name, parent, center, size, color, r=None):
    return box(name, center, size, color, parent, outline=0, round_=r)


# ------------------------------------------------------------- accesorios
# coordenadas de cabeza: locales al centro del cubo de la cabeza (lado HEAD)

def acc_pelo(p, c, largo=False):
    c = c or HAIR
    _part("pelo_arriba", p["head"], (0, 0.03, H + 0.06), (HEAD + 0.08, HEAD + 0.06, 0.2), c, 0.07)
    _part("pelo_atras", p["head"], (0, H + 0.04, 0.05), (HEAD + 0.08, 0.14, HEAD * 0.75), c, 0.05)
    _part("fleco", p["head"], (0.0, -H - 0.02, H - 0.06), (HEAD + 0.06, 0.12, 0.16), c, 0.05)
    for sx in (-1, 1):
        _part(f"patilla{sx}", p["head"], (sx * (H + 0.03), 0.05, 0.1), (0.1, HEAD * 0.9, HEAD * 0.55), c, 0.04)
    if largo:
        _part("pelo_largo", p["head"], (0, H + 0.06, -0.45), (HEAD + 0.1, 0.18, 1.0), c, 0.06)
        for sx in (-1, 1):
            _part(f"mecha{sx}", p["head"], (sx * (H + 0.04), -0.1, -0.35), (0.12, 0.5, 0.75), c, 0.04)


def acc_pelo_corto(p, c):
    acc_pelo(p, c)


def acc_pelo_largo(p, c):
    acc_pelo(p, c, largo=True)


def acc_chongo(p, c):
    c = c or (0.62, 0.62, 0.66)
    acc_pelo(p, c)
    _part("chongo", p["head"], (0, H * 0.4, H + 0.32), (0.42, 0.42, 0.36), c, 0.12)


def acc_coletas(p, c):
    c = c or HAIR
    acc_pelo(p, c)
    for sx in (-1, 1):
        _part(f"coleta{sx}", p["head"], (sx * (H + 0.2), 0.12, -0.05), (0.26, 0.3, 0.6), c, 0.1)


def acc_calvo(p, c):
    c = c or (0.85, 0.85, 0.88)
    for sx in (-1, 1):
        _part(f"pelo_lado{sx}", p["head"], (sx * (H + 0.03), 0.12, 0.0), (0.1, HEAD * 0.75, 0.32), c, 0.04)
    _part("pelo_nuca", p["head"], (0, H + 0.03, 0.0), (HEAD * 0.9, 0.1, 0.32), c, 0.04)


def acc_pelo_punta(p, c):
    c = c or (0.95, 0.3, 0.15)
    acc_pelo(p, c)
    for i, (x, y, rx, ry) in enumerate([(0, 0, 0, 0), (-0.25, 0.05, 0, -30), (0.25, 0.05, 0, 30),
                                         (-0.12, 0.25, 25, -10), (0.12, 0.25, 25, 10)]):
        cone(f"punta{i}", (x, y, H + 0.3), 0.15, 0, 0.42, c, p["head"], 0, vertices=4,
             rot=(D(rx), D(ry), D(45)))


def acc_gorra(p, c):
    c = c or (0.9, 0.2, 0.2)
    _part("gorra", p["head"], (0, 0.02, H + 0.08), (HEAD + 0.08, HEAD + 0.08, 0.26), c, 0.1)
    _part("visera", p["head"], (0, -H - 0.2, H - 0.02), (HEAD * 0.75, 0.42, 0.06), c, 0.03)


def acc_gorra_policia(p, c):
    c = c or (0.12, 0.18, 0.4)
    cyl("gorra_copa", (0, 0, H + 0.2), H * 1.15, 0.36, c, p["head"], 0, vertices=32)
    cyl("gorra_banda", (0, 0, H + 0.03), H * 1.08, 0.12, (0.08, 0.08, 0.1), p["head"], 0, vertices=32)
    _part("visera", p["head"], (0, -H - 0.15, H - 0.02), (HEAD * 0.7, 0.35, 0.06), (0.08, 0.08, 0.1), 0.03)
    _part("placa", p["head"], (0, -H * 1.12, H + 0.2), (0.14, 0.04, 0.16), (1, 0.85, 0.2), 0.02)


def acc_sombrero(p, c):
    c = c or (0.85, 0.72, 0.42)
    cyl("ala", (0, 0, H + 0.05), HEAD * 1.05, 0.06, c, p["head"], 0, vertices=32)
    cyl("copa", (0, 0, H + 0.28), H * 0.95, 0.45, c, p["head"], 0, vertices=32)
    cyl("cinta", (0, 0, H + 0.12), H * 0.97, 0.1, (0.55, 0.2, 0.12), p["head"], 0, vertices=32)


def acc_gorro_chef(p, c):
    c = c or (1, 1, 1)
    cyl("gorro", (0, 0, H + 0.3), H * 1.0, 0.6, c, p["head"], 0, vertices=32)
    for i, (x, y) in enumerate([(-0.2, 0), (0.2, 0), (0, -0.18), (0, 0.18), (0, 0)]):
        ball(f"gorro_bola{i}", (x, y, H + 0.68), 0.26, c, p["head"], 0)


def acc_lazo(p, c):
    c = c or (1, 0.4, 0.65)
    for sx in (-1, 1):
        _part(f"lazo{sx}", p["head"], (0.22 + sx * 0.12, -0.05, H + 0.2), (0.18, 0.08, 0.16), c, 0.05)
    _part("lazo_c", p["head"], (0.22, -0.06, H + 0.2), (0.08, 0.1, 0.08), c, 0.02)


def acc_bufanda(p, c):
    c = c or (0.13, 0.48, 0.95)
    t = prim("torus", "bufanda", p["body"], major_radius=0.42, minor_radius=0.13,
             major_segments=32, minor_segments=12)
    t.location = (0, 0, NECK_Z + 0.02)
    t.scale = (1.35, 0.85, 0.9)
    finish(t, mat(c, 0.72), 0)
    _part("bufanda_cola", p["body"], (-0.3, -0.36, 1.95), (0.26, 0.1, 0.62), c, 0.04).rotation_euler = (0, D(-6), 0)


def acc_panuelo(p, c):
    c = c or (0.95, 0.5, 0.15)
    cone("panuelo", (0, -0.31, NECK_Z - 0.12), 0.26, 0, 0.04, c, p["body"], 0, vertices=3,
         rot=(D(90), D(90), 0))
    t = prim("torus", "panuelo_aro", p["body"], major_radius=0.34, minor_radius=0.06,
             major_segments=24, minor_segments=8)
    t.location = (0, 0, NECK_Z + 0.01)
    t.scale = (1.2, 0.8, 1)
    finish(t, mat(c, 0.75), 0)


def acc_corbata(p, c):
    c = c or (0.85, 0.15, 0.2)
    _part("corbata_nudo", p["body"], (0, -0.31, NECK_Z - 0.08), (0.14, 0.06, 0.12), c, 0.02)
    _part("corbata", p["body"], (0, -0.31, NECK_Z - 0.45), (0.16, 0.04, 0.62), c, 0.02)


def acc_chaleco(p, c):
    c = c or (0.55, 0.36, 0.2)
    for sx in (-1, 1):
        _part(f"chaleco{sx}", p["body"], (sx * 0.36, -0.01, 1.73), (0.46, 0.62, 1.17), c, 0.04)


def acc_mochila(p, c):
    c = c or (0.55, 0.3, 0.75)
    _part("mochila", p["body"], (0, 0.44, 1.75), (0.85, 0.32, 0.85), c, 0.1)
    for sx in (-1, 1):
        _part(f"correa{sx}", p["body"], (sx * 0.3, -0.3, 1.95), (0.1, 0.04, 0.55), _darker(c), 0.02)


def acc_falda(p, c):
    cone("falda", (0, 0, 1.0), 0.86, 0.72, 0.42, c or (0.95, 0.45, 0.35), p["body"], 0, vertices=4,
         rot=(0, 0, D(45)))


def acc_vestido(p, c):
    c = c or (1, 0.55, 0.75)
    p["_torso"].data.materials[0] = mat(c)
    for side in ("d", "i"):
        p["_manga_" + side].data.materials[0] = mat(c)
    cone("vestido_falda", (0, 0, 0.8), 0.95, 0.74, 0.75, c, p["body"], 0, vertices=4, rot=(0, 0, D(45)))


def acc_bata(p, c):
    c = c or (1, 1, 1)
    _part("bata", p["body"], (0, 0, 1.6), (1.24, 0.66, 1.45), c, 0.05)
    for side in ("d", "i"):
        p["_manga_" + side].data.materials[0] = mat(c)
        p["_mano_" + side].data.materials[0] = mat(c)
    _part("bata_bolsillo", p["body"], (0.3, -0.34, 1.35), (0.24, 0.02, 0.2), (0.85, 0.9, 1), 0.02)


def acc_delantal(p, c):
    _part("delantal", p["body"], (0, -0.31, 1.45), (0.9, 0.04, 1.15), c or (1, 1, 1), 0.03)


def acc_collar(p, c):
    t = prim("torus", "collar", p["body"], major_radius=0.32, minor_radius=0.05,
             major_segments=24, minor_segments=8)
    t.location = (0, -0.05, NECK_Z - 0.02)
    t.scale = (1.3, 1, 1)
    finish(t, mat(c or (1, 1, 1), 0.85), 0)


def acc_baston(p, c):
    c = c or (0.45, 0.28, 0.15)
    cyl("baston", (0, -0.25, -0.7), 0.05, 1.3, c, p["arm_d"], 0, vertices=10)


def acc_smoking(p, c):
    """Saco de esmoquin con solapas de satín y pañuelo en el bolsillo (camisa blanca al centro)."""
    c = c or (0.06, 0.06, 0.08)
    satin = (0.16, 0.16, 0.19)
    _part("saco_atras", p["body"], (0, 0.26, 1.69), (1.22, 0.12, 1.26), c, 0.04)
    for sx in (-1, 1):
        _part(f"saco{sx}", p["body"], (sx * 0.385, -0.005, 1.69), (0.43, 0.64, 1.26), c, 0.04)
        _part(f"solapa{sx}", p["body"], (sx * 0.205, -0.325, 1.98), (0.1, 0.03, 0.62), satin, 0.015).rotation_euler = (
            0, D(11 * sx), 0)
    _part("boton_saco", p["body"], (0.19, -0.33, 1.42), (0.06, 0.03, 0.06), satin, 0.02)
    _part("panuelo_bolsillo", p["body"], (0.4, -0.33, 2.0), (0.15, 0.03, 0.08), (1, 1, 1), 0.015)
    for side in ("d", "i"):
        p["_manga_" + side].data.materials[0] = mat(c)


def acc_corbatin(p, c):
    c = c or (0.05, 0.05, 0.06)
    for sx in (-1, 1):
        cone(f"corbatin{sx}", (sx * 0.08, -0.32, 2.14), 0.08, 0.025, 0.14, c, p["body"], 0, vertices=4,
             rot=(0, D(-90 * sx), D(45)))
    _part("corbatin_nudo", p["body"], (0, -0.33, 2.14), (0.06, 0.05, 0.07), c, 0.02)


def _darker(c, k=0.75):
    return tuple(v * k for v in c[:3])


ACCESORIOS = {k[4:]: v for k, v in globals().items() if k.startswith("acc_")}


# ----------------------------------------------------------------- humanos

def build_bloque(d, face_png):
    colors = d.get("colores", {})
    col = lambda k, default: tuple(colors.get(k, default))  # noqa: E731
    skin, shirt = col("piel", SKIN), col("camisa", SHIRT)
    pants, shoes = col("pantalon", PANTS), col("zapatos", SHOES)
    manga_larga = d.get("manga_larga", False)

    root = empty(d.get("id", "personaje"))
    body = empty("cuerpo", parent=root)
    torso = _part("torso", body, (0, 0, 1.72), (1.16, 0.58, 1.15), shirt, 0.06)
    _part("cadera", body, (0, 0, 1.2), (1.16, 0.58, 0.14), pants, 0.03)
    neck = empty("cuello", (0, 0, NECK_Z), body)
    head = block_head("cabeza", neck, (0, 0, H + 0.02), HEAD, face_png, skin)
    p = {"root": root, "body": body, "neck": neck, "head": head, "kind": "humano", "drop": 1.27,
         "_torso": torso, "head_r": H, "bloque": True}
    for side, sx in (("d", -1), ("i", 1)):
        a = empty(f"brazo_{side}", (0.87 * sx, 0, 2.18), body)
        sleeve_len = 1.08 if manga_larga else 0.62
        p["_manga_" + side] = _part(f"manga_{side}", a, (0, 0, 0.12 - sleeve_len / 2), (0.56, 0.56, sleeve_len),
                                    shirt, 0.06)
        p["_mano_" + side] = _part(f"mano_{side}", a, (0, 0, 0.12 - sleeve_len - (1.12 - sleeve_len) / 2 + 0.02),
                                   (0.54, 0.54, 1.12 - sleeve_len + 0.04), skin, 0.06)
        lg = empty(f"pierna_{side}", (0.29 * sx, 0, 1.15), body)
        _part(f"pierna_{side}_b", lg, (0, 0, -0.52), (0.57, 0.58, 1.0), pants, 0.05)
        _part(f"zapato_{side}", lg, (0, -0.04, -1.06), (0.58, 0.68, 0.18), shoes, 0.06)
        p["arm_" + side], p["leg_" + side] = a, lg
    hair_color = colors.get("pelo")
    for name in d.get("accesorios", []):
        fn = ACCESORIOS.get(name)
        if not fn:
            print(f"[aviso] accesorio de bloques '{name}' no existe")
            continue
        c = colors.get(name) or (hair_color if name.startswith(("pelo", "chongo", "coletas", "calvo")) else None)
        fn(p, tuple(c) if c else None)
    return p


# ---------------------------------------------------------------- animales

def build_animal_bloque(d, face_png):
    kind = d.get("tipo_animal", "perro")
    colors = d.get("colores", {})
    body_c = tuple(colors.get("cuerpo", (0.86, 0.6, 0.35)))
    ear_c = tuple(colors.get("orejas", body_c))
    root = empty(d.get("id", kind))
    body = empty("cuerpo", parent=root)
    p = {"root": root, "body": body, "kind": "pajaro" if kind == "pajaro" else kind}
    if kind == "pajaro":
        neck = empty("cuello", (0, 0, 0.5), body)
        head = block_head("cabeza", neck, (0, 0, 0.55), 1.0, face_png, body_c)
        p.update(neck=neck, head=head, drop=0.5, head_r=0.5)
        wing_c = tuple(colors.get("alas", body_c))
        for side, sx in (("d", -1), ("i", 1)):
            a = empty(f"ala_{side}", (sx * 0.55, 0.05, 1.15), body)
            _part(f"ala_{side}_m", a, (0, 0.05, -0.3), (0.12, 0.6, 0.6), wing_c, 0.04)
            lg = empty(f"pata_{side}", (sx * 0.2, 0, 0.5), body)
            _part(f"pata_{side}_m", lg, (0, 0, -0.25), (0.08, 0.08, 0.5), (1, 0.6, 0.15), 0.02)
            _part(f"pie_{side}", lg, (0, -0.08, -0.5), (0.2, 0.3, 0.05), (1, 0.6, 0.15), 0.02)
            p["arm_" + side], p["leg_" + side] = a, lg
        tail = empty("cola", (0, 0.5, 0.9), body)
        _part("cola_plumas", tail, (0, 0.15, 0.1), (0.4, 0.3, 0.08), wing_c, 0.03).rotation_euler = (D(-30), 0, 0)
        p["tail"] = tail
        return p
    _part("torso", body, (0, 0.1, 0.95), (0.85, 1.5, 0.75), body_c, 0.12)
    neck = empty("cuello", (0, -0.6, 1.15), body)
    hs = 0.95
    head = block_head("cabeza", neck, (0, -0.15, 0.3), hs, face_png, body_c)
    p.update(neck=neck, head=head, drop=0.75, head_r=hs / 2)
    if kind == "perro":
        for sx in (-1, 1):
            _part(f"oreja{sx}", head, (sx * (hs / 2 + 0.05), 0.05, 0.05), (0.12, 0.35, 0.55), ear_c, 0.05)
    elif kind == "gato":
        for sx in (-1, 1):
            cone(f"oreja{sx}", (sx * 0.27, 0.05, hs / 2 + 0.15), 0.2, 0, 0.32, ear_c, head, 0, vertices=4,
                 rot=(0, 0, D(45)))
    elif kind == "cerdo":
        for sx in (-1, 1):
            _part(f"oreja{sx}", head, (sx * 0.3, 0.05, hs / 2 + 0.06), (0.22, 0.08, 0.2), ear_c, 0.03)
    for side, sx in (("d", -1), ("i", 1)):
        a = empty(f"pata_del_{side}", (0.25 * sx, -0.45, 0.65), body)
        _part(f"pata_del_{side}_m", a, (0, 0, -0.32), (0.26, 0.26, 0.66), body_c, 0.05)
        lg = empty(f"pata_tras_{side}", (0.25 * sx, 0.65, 0.65), body)
        _part(f"pata_tras_{side}_m", lg, (0, 0, -0.32), (0.26, 0.26, 0.66), body_c, 0.05)
        p["arm_" + side], p["leg_" + side] = a, lg
    tail = empty("cola", (0, 0.85, 1.15), body)
    if kind == "cerdo":
        t = prim("torus", "cola_rizo", tail, major_radius=0.1, minor_radius=0.035, major_segments=16,
                 minor_segments=6)
        t.rotation_euler = (0, D(90), 0)
        finish(t, mat(ear_c), 0)
    else:
        length = 0.75 if kind == "gato" else 0.5
        _part("cola_m", tail, (0, 0, length / 2), (0.14, 0.14, length), body_c, 0.04)
        tail.rotation_euler = (D(-35 if kind == "perro" else -15), 0, 0)
    p["tail"] = tail
    return p


# ------------------------------------------------------------------ efectos

EFECTOS = {
    #          color del efecto,      brillo del borde,     alpha
    "piedra": ((0.6, 0.6, 0.62), (1.0, 0.18, 0.05), 1.0),
    "vidrio": ((0.75, 0.92, 1.0), (0.55, 0.9, 1.0), 0.45),
}


def aplicar_efecto(p, efecto, face_png, progresivo=None):
    """'piedra' = estatua (gris con grietas), 'vidrio' = transparente celeste. Mantiene la cara.

    progresivo=(f0, f1): en estilo bloques el efecto sube de los pies a la cabeza entre esos cuadros,
    con un borde brillante (rojo en piedra, celeste en vidrio). Sin progresivo, el personaje ya está
    transformado desde el primer cuadro.
    """
    from bl_util import mat_textura, suave
    if efecto not in EFECTOS:
        return
    if progresivo and suave():
        bpy.context.view_layer.update()
        s = p["root"].matrix_world.to_scale().z
        z0 = p["root"].matrix_world.translation.z
        z1 = p["head"].matrix_world.translation.z + p.get("head_r", 0.43) * s * 1.3
        f0, f1 = progresivo
        done = {}
        for o in p["root"].children_recursive:
            if o.type != "MESH":
                continue
            for i, m0 in enumerate(o.data.materials):
                if m0 is None:
                    continue
                k = (m0.name, o == p["head"])
                if k not in done:
                    done[k] = _barrido(m0, efecto, z0, z1, f0, f1, cabeza=(o == p["head"]))
                o.data.materials[i] = done[k]
        return
    if efecto == "piedra":
        m_body = mat_textura("piedra", (0.62, 0.62, 0.64), (0.45, 0.45, 0.48))
        base = (0.6, 0.6, 0.62)
    else:
        m_body = _vidrio()
        base = (0.75, 0.9, 1.0)
    for o in p["root"].children_recursive:
        if o.type != "MESH":
            continue
        if o == p["head"]:
            o.data.materials[0] = head_material(face_png, p.get("head_r", 0.43), base)
            if efecto == "vidrio":
                o.data.materials[0].surface_render_method = "BLENDED"
        else:
            for i in range(len(o.data.materials)):
                o.data.materials[i] = m_body


def _barrido(m0, efecto, z0, z1, f0, f1, cabeza=False):
    """Copia del material con un barrido vertical animado (nodo 'Progreso') hacia el efecto."""
    from bl_util import mix_node, socket
    color, glow, alpha = EFECTOS[efecto]
    m = m0.copy()
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return m0
    base_in = bsdf.inputs["Base Color"]
    src = base_in.links[0].from_socket if base_in.links else None

    def math(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for idx, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[idx].default_value = v
            else:
                nt.links.new(v, n.inputs[idx])
        return n.outputs[0]

    def map_range(v, a, b, c, d):
        n = nt.nodes.new("ShaderNodeMapRange")
        n.clamp = True
        n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = a, b
        n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = c, d
        nt.links.new(v, n.inputs["Value"])
        return n.outputs["Result"]

    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    nt.links.new(geo.outputs["Position"], noise.inputs["Vector"])
    z = math("ADD", sep.outputs["Z"], math("MULTIPLY", noise.outputs["Fac"], 0.3))
    prog = nt.nodes.new("ShaderNodeValue")
    prog.name = prog.label = "Progreso"
    d = math("SUBTRACT", prog.outputs[0], z)          # > 0: ya transformado
    mask = map_range(d, -0.04, 0.04, 0.0, 1.0)
    band = map_range(math("ABSOLUTE", d), 0.0, 0.07, 1.0, 0.0)

    target = mix_node(nt)
    if cabeza:   # la cara se conserva: se tiñe el color en vez de reemplazarlo
        target.blend_type = "MULTIPLY"
        socket(target.inputs, "Factor", "VALUE").default_value = 1.0
        if src:
            nt.links.new(src, socket(target.inputs, "A", "RGBA"))
        socket(target.inputs, "B", "RGBA").default_value = (*[min(1, c * 1.15) for c in color], 1)
    else:
        socket(target.inputs, "Factor", "VALUE").default_value = 1.0
        socket(target.inputs, "B", "RGBA").default_value = (*color, 1)
    mx = mix_node(nt)
    nt.links.new(mask, socket(mx.inputs, "Factor", "VALUE"))
    if src:
        nt.links.new(src, socket(mx.inputs, "A", "RGBA"))
    else:
        socket(mx.inputs, "A", "RGBA").default_value = base_in.default_value
    nt.links.new(socket(target.outputs, "Result", "RGBA"), socket(mx.inputs, "B", "RGBA"))
    nt.links.new(socket(mx.outputs, "Result", "RGBA"), base_in)

    bsdf.inputs["Emission Color"].default_value = (*glow, 1)
    nt.links.new(math("MULTIPLY", band, 5.0), bsdf.inputs["Emission Strength"])
    if alpha < 1:
        nt.links.new(map_range(mask, 0.0, 1.0, 1.0, alpha), bsdf.inputs["Alpha"])
        nt.links.new(map_range(mask, 0.0, 1.0, 0.62, 0.05), bsdf.inputs["Roughness"])
        try:   # "dithered" respeta la profundidad: sin cabezas fantasma ni caras grises (BLENDED sí falla aquí)
            m.surface_render_method = "DITHERED"
        except AttributeError:
            m.blend_method = "HASHED"

    sock = prog.outputs[0]
    sock.default_value = z0 - 0.4
    sock.keyframe_insert("default_value", frame=f0)
    sock.default_value = z1 + 0.4
    sock.keyframe_insert("default_value", frame=f1)
    return m


def _vidrio():
    m = bpy.data.materials.new("vidrio")
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (0.7, 0.9, 1.0, 1)
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Alpha"].default_value = 0.45
    try:
        m.surface_render_method = "BLENDED"
    except AttributeError:
        m.blend_method = "BLEND"
    return m
