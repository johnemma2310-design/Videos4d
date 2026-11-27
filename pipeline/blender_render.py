"""Renderiza las tomas de un episodio en Blender (modo consola).

Lo llama pipeline/build.py así:
    blender -b --factory-startup -P pipeline/blender_render.py -- out/timeline.json [tomas]

Por cada toma reconstruye la escena desde cero: escenario (escenarios.py), los
personajes (personajes_bl.py) con su pose (poses.py) y cara, y la cámara.
Escribe los fotogramas como PNG numerados globalmente en frames_dir.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import bl_util  # noqa: E402
from bl_util import empty, key, link  # noqa: E402
from escenarios import SETS  # noqa: E402
from personajes_bl import build  # noqa: E402
from poses import animar  # noqa: E402

# Dónde se paran los secundarios respecto al protagonista (x, y)
LUGARES = {
    "izquierda": (-1.8, 0.3), "derecha": (1.8, 0.3),
    "atras_izquierda": (-1.3, 2.2), "atras_derecha": (1.3, 2.2), "atras": (0, 2.6),
    "frente_izquierda": (-1.5, -1.0), "frente_derecha": (1.5, -1.0),
    "lejos_izquierda": (-3.5, 3.5), "lejos_derecha": (3.5, 3.5),
}

# ------------------------------------------------------------------- cámara

PLANOS = {
    #            distancia, altura, lente, apuntar (0=cabeza, 1=cuerpo)
    "general": (9.0, 0.9, 32, 0.25),
    "medio": (4.6, 0.5, 40, 0.45),
    "primer_plano": (2.5, 0.15, 50, 0.0),
    "arriba": (7.0, 0.0, 35, 0.6),
    "contrapicado": (3.2, -1.6, 32, 0.2),
    "lateral": (4.2, 0.4, 40, 0.4),
}


def actor_frame(p):
    root = p["root"]
    s = root.scale.z
    head = p["head"].matrix_world.translation.copy()
    up = (root.matrix_world.to_3x3().normalized() @ Vector((0, 0, 1))).normalized()
    fwd = (root.matrix_world.to_3x3().normalized() @ Vector((0, -1, 0))).normalized()
    return head, head - up * p["drop"] * s, fwd, s


def camera(plano, focus, actors, f0, f1, follow_root, golpes=(), mano=False, cortes=None, temblor=False):
    bpy.context.view_layer.update()
    head, center, fwd, s = actor_frame(focus)

    def place(name):
        if name == "grupo":
            pts = [actor_frame(a) for a in actors]
            heads = [h for h, _, _, _ in pts]
            tgt = sum((h.lerp(c, 0.45) for h, c, _, _ in pts), Vector()) / len(pts)
            spread = max((h - tgt).length for h in heads) if len(heads) > 1 else 1.0
            dist = max(5.0, spread * 3.2 + 2.5)
            return tgt + Vector((0, -dist, 0.6)), tgt, 35
        if name == "hombro":     # por encima del hombro de otro personaje, mirando al foco
            others = [a for a in actors if a is not focus]
            if others:
                oh, oc, _, _ = actor_frame(others[0])
                f = Vector((fwd.x, fwd.y, 0)).normalized()
                lat = Vector((-f.y, f.x, 0))
                rel = oh - head
                ahead = max(rel.dot(f), 0.6)       # qué tan adelante está el otro
                side = rel.dot(lat)                # y hacia qué lado
                # la cámara mira de frente al foco (se ve la cara) y queda justo detrás del otro,
                # un poco hacia afuera: su hombro enmarca el borde del cuadro
                pos = head + f * (ahead + 1.7) + lat * (side * 1.35) + Vector((0, 0, 0.35))
                return pos, head.lerp(center, 0.2), 40
            name = "espalda"
        if name == "espalda":    # detrás del personaje, viendo lo que él ve (mejor en exteriores)
            side = Vector((-fwd.y, fwd.x, 0)) * 0.9
            return (head - fwd * 3.0 * max(s, 0.6) + side + Vector((0, 0, 0.5)),
                    head + fwd * 2.5 - Vector((0, 0, 0.6)), 35)
        if name == "pies":       # detalle de los pies, cámara casi al ras del suelo
            feet = focus["root"].matrix_world.translation.copy() + Vector((0, 0, 0.5 * s))
            side = Vector((-fwd.y, fwd.x, 0)) * 0.6
            return feet + fwd * 3.0 * max(s, 0.6) + side + Vector((0, 0, 0.15)), feet, 35
        dist, h, lens, aim = PLANOS[name]
        if name == "primer_plano" and s > 1.3:
            h = -0.4              # gigantes: cámara un poco abajo (se ve la cara bajo el sombrero e impone)
        k = max(s, 0.55)          # personajes chicos: cámara más cerca
        dist *= k
        target = head.lerp(center, aim)
        if name == "arriba":
            pos = target + Vector((0, 0, dist)) + Vector((0, -1.5 * k, 0))
        else:
            f = fwd
            if name == "lateral":
                f = (fwd + Vector((fwd.y, -fwd.x, 0)) * 1.4).normalized()
            pos = target + f * dist + Vector((0, 0, h * k))
            if abs(f.z) > 0.7:        # acostado mirando arriba: evita la cámara cenital exacta
                pos += Vector((0, -dist * 0.35, 0))
        return pos, target, lens

    cam_data = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cam_data)
    link(cam)
    tgt = empty("cam_objetivo")
    tr = cam.constraints.new("TRACK_TO")
    tr.target = tgt
    tr.track_axis = "TRACK_NEGATIVE_Z"
    tr.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    root = focus["root"]
    root_start = root.location.copy()
    if follow_root:   # la cámara acompaña al personaje cuando camina/corre
        for o in (cam, tgt):
            c = o.constraints.new("COPY_LOCATION")
            c.target = root
            c.use_offset = True
            o.constraints.move(len(o.constraints) - 1, 0)

    def put(f, pos, target, lens):
        off = root_start if follow_root else Vector((0, 0, 0))
        key(cam, "location", f, tuple(pos - off))
        key(tgt, "location", f, tuple(target - off))
        cam_data.lens = lens
        cam_data.keyframe_insert("lens", frame=f)

    known = set(PLANOS) | {"grupo", "hombro", "espalda", "pies"}
    segs = cortes or [(f0, plano)]
    for si, (a0, pl) in enumerate(segs):           # cortes internos: un sub-plano por segmento
        a1 = segs[si + 1][0] - 1 if si + 1 < len(segs) else f1
        if pl == "zoom_in":
            a, b = place("medio"), place("primer_plano")
            put(a0, *a)
            put(a0 + max(2, int((a1 - a0) * 0.35)), *b)
            put(a1, b[0] + (b[1] - b[0]) * 0.05, b[1], b[2])
        elif pl == "zoom_out":
            a, b = place("primer_plano"), place("general")
            put(a0, *a)
            put(a0 + max(2, int((a1 - a0) * 0.4)), *b)
            put(a1, *b)
        else:
            pos, target, lens = place(pl if pl in known else "medio")
            put(a0, pos, target, lens)
            put(a1, pos + (target - pos) * 0.07, target, lens)   # acercamiento lento
            for g in golpes:        # "zoom golpe" en la palabra clave: el lente salta y se queda
                if a0 + 2 <= g <= a1 - 4:
                    for f, l in ((g, lens), (g + 3, lens * 1.22), (a1, lens * 1.22)):
                        cam_data.lens = l
                        cam_data.keyframe_insert("lens", frame=f)
    if len(segs) > 1:               # los cortes son secos: sin interpolar entre sub-planos
        for o in (cam, tgt):
            for fc in fcurves_de(o):
                for kp in fc.keyframe_points:
                    kp.interpolation = "LINEAR"
        for fc in fcurves_de(cam_data):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
    if mano:                         # cámara en mano: micro-temblor en el punto al que mira
        for fc in fcurves_de(tgt):
            if fc.data_path == "location":
                mod = fc.modifiers.new("NOISE")
                mod.strength = 0.05
                mod.scale = 28.0
                mod.phase = (f0 * 7.31 + fc.array_index * 13.7) % 100
    if temblor:                      # sacudida fuerte al inicio de la toma (golpe, aparición, grito)
        for o in (cam, tgt):
            for fc in fcurves_de(o):
                if fc.data_path == "location":
                    mod = fc.modifiers.new("NOISE")
                    mod.strength = 0.35 if o is cam else 0.2
                    mod.scale = 2.5
                    mod.phase = (f0 * 3.1 + fc.array_index * 7.7) % 100
                    mod.use_restricted_range = True
                    mod.frame_start, mod.frame_end = f0, f0 + 20
                    mod.blend_out = 12


def fcurves_de(obj):
    """F-curves de un objeto o node tree (compatible con las acciones por capas de Blender 4.4+/5)."""
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and len(act.fcurves):
        return list(act.fcurves)
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for cb in getattr(strip, "channelbags", []):
                out.extend(cb.fcurves)
    return out


# ------------------------------------------------------------------- render


def setup_render(tl, f0, f1):
    sc = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            pass
    try:
        sc.eevee.taa_render_samples = tl.get("muestras", 16)
    except AttributeError:
        pass
    sc.render.resolution_x, sc.render.resolution_y = tl["res"]
    sc.render.resolution_percentage = tl.get("calidad", 100)
    sc.render.fps = tl["fps"]
    if bl_util.suave():
        try:
            sc.eevee.use_raytracing = False         # la AO va en los materiales: ~3x más rápido que raytracing
        except AttributeError:
            pass
        try:
            sc.eevee.shadow_ray_count = 2
        except AttributeError:
            pass
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.view_settings.exposure = -0.15
    else:
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.filepath = str(Path(tl["frames_dir"]) / "######")
    sc.render.use_file_extension = True
    sc.frame_start, sc.frame_end = f0, f1


def place_actor(p, actor, main_pos, is_main):
    root = p["root"]
    root.scale = (actor.get("escala", 1.0),) * 3
    if is_main:
        root.location = main_pos
        return
    if "pos" in actor:
        dx, dy = actor["pos"]
    else:
        dx, dy = LUGARES.get(actor.get("lugar", "derecha"), LUGARES["derecha"])
    root.location = (main_pos[0] + dx, main_pos[1] + dy, main_pos[2])
    if actor.get("mirar", True):   # se gira un poco hacia el protagonista, sin perder la cara
        theta = math.atan2(-dx, dy)
        turn = max(-math.radians(25), min(math.radians(25), 0.4 * theta))
        root.rotation_euler = (0, 0, turn)


def animar_cara(p, actor):
    """Parpadeo y lip-sync: mezcla la cara normal con sus variantes (ojos cerrados / boca abierta)
    usando nodos 'Parpadeo' y 'Habla' con keyframes de paso. También 'brillo_ojos' (emisivo)."""
    head = p.get("head")
    if head is None or head.type != "MESH":
        return
    from bl_util import mix_node, socket
    capas = [(n, actor.get(f"face_{n.lower()}"), actor.get(k)) for n, k in
             (("Habla", "boca"), ("Parpadeo", "parpadeos"))]
    capas = [c for c in capas if c[1] and c[2]]
    if not capas and not actor.get("brillo_ojos"):
        return
    for m in {m for m in head.data.materials if m}:
        nt = m.node_tree
        tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE" and n.image
                    and Path(n.image.filepath).name == Path(actor["face"]).name), None)
        if tex is None:
            continue
        col_links = [l.to_socket for l in tex.outputs["Color"].links]
        alp_links = [l.to_socket for l in tex.outputs["Alpha"].links]
        vec = tex.inputs["Vector"].links[0].from_socket if tex.inputs["Vector"].links else None
        col, alp = tex.outputs["Color"], tex.outputs["Alpha"]
        for nombre, png, tramos in capas:
            t2 = nt.nodes.new("ShaderNodeTexImage")
            t2.image = bpy.data.images.load(png, check_existing=True)
            t2.extension, t2.interpolation = tex.extension, tex.interpolation
            if vec:
                nt.links.new(vec, t2.inputs["Vector"])
            val = nt.nodes.new("ShaderNodeValue")
            val.name = val.label = nombre
            sock = val.outputs[0]
            sock.default_value = 0.0
            sock.keyframe_insert("default_value", frame=1)
            for a, b in tramos:
                sock.default_value = 1.0
                sock.keyframe_insert("default_value", frame=a)
                sock.default_value = 0.0
                sock.keyframe_insert("default_value", frame=b + 1)
            mc = mix_node(nt)
            nt.links.new(sock, socket(mc.inputs, "Factor", "VALUE"))
            nt.links.new(col, socket(mc.inputs, "A", "RGBA"))
            nt.links.new(t2.outputs["Color"], socket(mc.inputs, "B", "RGBA"))
            ma = nt.nodes.new("ShaderNodeMix")
            ma.data_type = "FLOAT"
            nt.links.new(sock, ma.inputs[0])
            nt.links.new(alp, socket(ma.inputs, "A", "VALUE"))
            nt.links.new(t2.outputs["Alpha"], socket(ma.inputs, "B", "VALUE"))
            col, alp = socket(mc.outputs, "Result", "RGBA"), socket(ma.outputs, "Result", "VALUE")
        for s in col_links:
            nt.links.new(col, s)
        for s in alp_links:
            nt.links.new(alp, s)
        if actor.get("brillo_ojos"):
            bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf:
                em = nt.nodes.new("ShaderNodeMath")
                em.operation = "MULTIPLY"
                nt.links.new(alp, em.inputs[0])
                em.inputs[1].default_value = 6.0
                nt.links.new(col, bsdf.inputs["Emission Color"])
                nt.links.new(em.outputs[0], bsdf.inputs["Emission Strength"])
        for fc in fcurves_de(nt):        # cambios instantáneos (no se "derrite" la cara)
            if '"Habla"' in fc.data_path or '"Parpadeo"' in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"


def render_shot(tl, shot):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bl_util.reset_caches()
    bl_util.set_style(tl.get("estilo", "toon"))
    f0, f1 = shot["f0"], shot["f1"]
    setup_render(tl, f0, f1)
    main_pose = shot["actores"][0]["pose"]
    info = SETS.get(shot["escenario"], SETS["vacio"])({**shot, "pose": main_pose})
    parts, moving = [], False
    for i, actor in enumerate(shot["actores"]):
        p = build(actor["def"], Path(actor["face"]))
        place_actor(p, actor, info["standing"], i == 0)
        if actor.get("efecto"):
            from bloques_bl import aplicar_efecto
            prog = None
            if actor.get("efecto_progresivo"):
                prog = (f0 + int((f1 - f0) * 0.1), f0 + int((f1 - f0) * 0.85))
            aplicar_efecto(p, actor["efecto"], Path(actor["face"]), prog)
        animar_cara(p, actor)
        mv = animar(p, actor["pose"], f0, f1, tl["fps"])
        parts.append(p)
        if i == shot.get("foco", 0):
            moving = mv
    focus = parts[min(shot.get("foco", 0), len(parts) - 1)]
    camera(shot["plano"], focus, parts, f0, f1, follow_root=moving, golpes=shot.get("golpes", []),
           mano=bl_util.suave(), cortes=shot.get("cortes"), temblor=shot.get("temblor", False))
    if tl.get("guardar_blend"):
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(tl["frames_dir"]).parent / f"toma_{shot['i']:02d}.blend"))
    sc = bpy.context.scene
    if tl.get("solo_preview"):
        sc.frame_set((f0 + f1) // 2)
        sc.render.filepath = str(Path(tl["frames_dir"]).parent / f"preview_{shot['i']:02d}.png")
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    tl = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    only = {int(x) for x in argv[1].split(",")} if len(argv) > 1 and argv[1] else None
    for shot in tl["shots"]:
        if only is None or shot["i"] in only:
            quien = ", ".join(f"{a['def'].get('id')}:{a['pose']}/{a['cara']}" for a in shot["actores"])
            print(f"=== toma {shot['i']}: {shot['escenario']} / {shot['plano']} / {quien} "
                  f"(frames {shot['f0']}-{shot['f1']})", flush=True)
            render_shot(tl, shot)


if __name__ == "__main__":
    main()
