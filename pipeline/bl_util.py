"""Utilidades de Blender compartidas: materiales cartoon, contornos, primitivas, keyframes."""
import math

import bmesh
import bpy

D = math.radians
INK = (0.03, 0.03, 0.05)

_MATS = {}


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
    k = (tuple(round(c, 3) for c in color[:3]), round(shadow, 2), flat)
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


def finish(obj, material, outline=0.025, outline_color=INK, smooth=True):
    obj.data.materials.clear()
    obj.data.materials.append(material)
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


def box(name, center, size, color, parent=None, outline=0.03, shadow=0.8, rot=(0, 0, 0)):
    o = prim("cube", name, None, size=1, location=center)
    o.scale = size
    apply_scale(o)
    o.rotation_euler = rot
    if parent:
        o.parent = parent
    return finish(o, mat(color, shadow), outline, smooth=False)


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
    data.energy = energy
    data.color = color
    data.angle = D(3)
    o = bpy.data.objects.new("sol", data)
    o.rotation_euler = tuple(D(a) for a in rot)
    return link(o)
