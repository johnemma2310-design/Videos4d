"""Utilidades de Blender compartidas: materiales cartoon, contornos, primitivas, keyframes."""
import math

import bmesh
import bpy

D = math.radians
INK = (0.03, 0.03, 0.05)

_MATS = {}

# Estilo global de la toma: "toon" (Sticky clásico: contornos negros, 2 tonos) o
# "bloques" (muñecos de bloques: sin contornos, sombreado suave, bordes redondeados, texturas).
STYLE = {"name": "toon"}


def set_style(name):
    STYLE["name"] = name or "toon"


def suave():
    return STYLE["name"] == "bloques"


def reset_caches():
    _MATS.clear()


def socket(sockets, name, type_=None):
    for s in sockets:
        if s.name == name and (type_ is None or s.type == type_) and s.enabled:
            return s
    for s in sockets:
        if s.name == name:
            return s
    raise KeyError(name)


def mix_node(nt, data_type="RGBA"):
    n = nt.nodes.new("ShaderNodeMix")
    n.data_type = data_type
    return n


def toon_material(name, color, shadow=0.78, flat=False):
    """Material cartoon nuevo: 2 tonos (luz/sombra), sin brillos."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(emit.outputs[0], out.inputs["Surface"])
    c = (*color[:3], 1)
    if flat:
        emit.inputs["Color"].default_value = c
        return m, nt, emit
    if suave():   # sombreado suave tipo juego de bloques
        nt.nodes.remove(emit)
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        rgb = nt.nodes.new("ShaderNodeRGB")
        rgb.outputs[0].default_value = c
        nt.links.new(rgb.outputs[0], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.62
        nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
        return m, nt, bsdf
    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*[v * shadow for v in color[:3]], 1)
    ramp.color_ramp.elements[1].position = 0.10
    ramp.color_ramp.elements[1].color = c
    nt.links.new(diff.outputs[0], s2r.inputs[0])
    nt.links.new(s2r.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], emit.inputs["Color"])
    return m, nt, emit


def mat(color, shadow=0.8, flat=False):
    """Material cartoon compartido (cacheado por color): menos shaders = render más rápido."""
    k = (tuple(round(c, 3) for c in color[:3]), round(shadow, 2), flat, STYLE["name"])
    if k not in _MATS:
        m, _, _ = toon_material(f"m{len(_MATS)}", color, shadow, flat)
        if flat == "outline":
            m.use_backface_culling = True
        _MATS[k] = m
    return _MATS[k]


def outline_mat(color=INK):
    k = ("outline", tuple(color))
    if k not in _MATS:
        m, _, _ = toon_material(f"contorno{len(_MATS)}", color, flat=True)
        m.use_backface_culling = True
        _MATS[k] = m
    return _MATS[k]


def mat_textura(kind, c1, c2, scale=1.0):
    """Material con textura procedural (solo estilo bloques): adoquin, ladrillo, pasto, madera, piedra."""
    k = ("tex", kind, tuple(c1), tuple(c2), scale, STYLE["name"])
    if k in _MATS:
        return _MATS[k]
    m, nt, bsdf = toon_material(f"tex_{kind}{len(_MATS)}", c1)
    if not suave():
        _MATS[k] = m
        return m
    rgb = bsdf.inputs["Base Color"].links[0].from_node
    nt.nodes.remove(rgb)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if kind in ("adoquin", "ladrillo"):
        t = nt.nodes.new("ShaderNodeTexBrick")
        t.inputs["Color1"].default_value = (*c1, 1)
        t.inputs["Color2"].default_value = (*c2, 1)
        t.inputs["Mortar"].default_value = (*[v * 0.72 for v in c1], 1)
        t.inputs["Scale"].default_value = (1.2 if kind == "adoquin" else 2.5) * scale
        t.inputs["Mortar Size"].default_value = 0.015
        nt.links.new(tc.outputs["Object" if kind == "ladrillo" else "Generated"], t.inputs["Vector"])
        if kind == "adoquin":
            mp = nt.nodes.new("ShaderNodeMapping")
            mp.inputs["Scale"].default_value = (20 * scale, 20 * scale, 1)
            nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
            nt.links.new(mp.outputs[0], t.inputs["Vector"])
        nt.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        n = nt.nodes.new("ShaderNodeTexNoise" if kind != "piedra" else "ShaderNodeTexVoronoi")
        n.inputs["Scale"].default_value = {"pasto": 18, "madera": 6, "piedra": 9}.get(kind, 10) * scale
        mx = mix_node(nt)
        nt.links.new(n.outputs[0] if kind != "piedra" else n.outputs["Distance"], socket(mx.inputs, "Factor", "VALUE"))
        socket(mx.inputs, "A", "RGBA").default_value = (*c1, 1)
        socket(mx.inputs, "B", "RGBA").default_value = (*c2, 1)
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
        nt.links.new(socket(mx.outputs, "Result", "RGBA"), bsdf.inputs["Base Color"])
    _MATS[k] = m
    return m


def finish(obj, material, outline=0.025, outline_color=INK, smooth=True):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    if suave():
        outline = 0          # en estilo bloques no hay contornos negros
    if smooth and hasattr(obj.data, "polygons"):
        for p in obj.data.polygons:
            p.use_smooth = True
    if outline:
        obj.data.materials.append(outline_mat(outline_color))
        mod = obj.modifiers.new("contorno", "SOLIDIFY")
        mod.thickness = outline
        mod.offset = 1.0
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.material_offset = 1
    return obj


def link(obj, parent=None):
    if obj.name not in bpy.context.scene.collection.objects:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        bpy.context.scene.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    return obj


def empty(name, loc=(0, 0, 0), parent=None):
    e = bpy.data.objects.new(name, None)
    e.location = loc
    e.empty_display_size = 0.1
    return link(e, parent)


def prim(kind, name, parent=None, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(**kw)
    o = bpy.context.active_object
    o.name = name
    return link(o, parent)


def apply_scale(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def bevel(o, width=0.04, segments=3):
    """Bordes redondeados (look de juguete/bloques)."""
    mod = o.modifiers.new("bisel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    o.data.shade_smooth() if hasattr(o.data, "shade_smooth") else None
    try:
        mod.harden_normals = True
    except AttributeError:
        pass
    return o


def box(name, center, size, color, parent=None, outline=0.03, shadow=0.8, rot=(0, 0, 0), material=None,
        round_=None):
    o = prim("cube", name, None, size=1, location=center)
    o.scale = size
    apply_scale(o)
    o.rotation_euler = rot
    if parent:
        o.parent = parent
    finish(o, material or mat(color, shadow), outline, smooth=False)
    if suave():
        r = round_ if round_ is not None else min(0.06, min(size) * 0.18)
        if r > 0.004:
            bevel(o, r)
    return o


def cyl(name, center, radius, depth, color, parent=None, outline=0.025, vertices=16, rot=(0, 0, 0),
        shadow=0.8, smooth=True):
    o = prim("cylinder", name, None, vertices=vertices, radius=radius, depth=depth, location=center,
             rotation=rot)
    if parent:
        o.parent = parent
    return finish(o, mat(color, shadow), outline, smooth=smooth)


def ball(name, center, radius, color, parent=None, outline=0.025, scale=(1, 1, 1), shadow=0.8, seg=24):
    o = prim("uv_sphere", name, None, segments=seg, ring_count=max(8, seg // 2), radius=radius,
             location=center)
    o.scale = scale
    if parent:
        o.parent = parent
    return finish(o, mat(color, shadow), outline)


def cone(name, center, r1, r2, depth, color, parent=None, outline=0.025, vertices=16, rot=(0, 0, 0),
         shadow=0.8, smooth=False):
    o = prim("cone", name, None, vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=center,
             rotation=rot)
    if parent:
        o.parent = parent
    return finish(o, mat(color, shadow), outline, smooth=smooth)


def sphere_cap(name, radius, keep, color, parent=None, loc=(0, 0, 0), outline=0.03, shadow=0.8):
    """Media esfera recortada: conserva los vértices donde keep(x, y, z) es True (pelo, gorras)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=radius)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not keep(v.co.x, v.co.y, v.co.z)], context="VERTS")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = loc
    link(o, parent)
    return finish(o, mat(color, shadow), outline)


def key(obj, path, frame, value):
    setattr(obj, path, value)
    obj.keyframe_insert(data_path=path, frame=frame)


def world(color, light_strength=0.35, light_color=(1, 1, 1)):
    w = bpy.data.worlds.new("mundo")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    if suave():   # la cámara ve el cielo con su color real; la luz ambiental es más tenue
        cam_bg = nt.nodes.new("ShaderNodeBackground")
        cam_bg.inputs["Color"].default_value = (*color[:3], 1)
        cam_bg.inputs["Strength"].default_value = 1.15
        amb = nt.nodes.new("ShaderNodeBackground")
        amb.inputs["Color"].default_value = (*color[:3], 1)
        amb.inputs["Strength"].default_value = 0.7 if light_strength >= 0.3 else 0.3
        lp = nt.nodes.new("ShaderNodeLightPath")
        mix = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
        nt.links.new(amb.outputs[0], mix.inputs[1])
        nt.links.new(cam_bg.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs["Surface"])
        return
    bg_cam = nt.nodes.new("ShaderNodeBackground")
    bg_cam.inputs["Color"].default_value = (*color[:3], 1)
    bg_light = nt.nodes.new("ShaderNodeBackground")
    bg_light.inputs["Color"].default_value = (*light_color, 1)
    bg_light.inputs["Strength"].default_value = light_strength
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg_light.outputs[0], mix.inputs[1])
    nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


def sun(energy=4.0, color=(1, 1, 1), rot=(48, 0, -28)):
    data = bpy.data.lights.new("sol", "SUN")
    data.energy = energy * (0.75 if suave() else 1.0)
    data.color = color
    data.angle = D(6 if suave() else 3)   # sombras más suaves en estilo bloques
    o = bpy.data.objects.new("sol", data)
    o.rotation_euler = tuple(D(a) for a in rot)
    return link(o)
