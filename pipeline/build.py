"""Construye un video de Sticky a partir de un guion.json.

    python pipeline/build.py episodios/prueba_cama/guion.json [--calidad 50] [--preview]

Pasos:
 1. Voz: edge-tts narra cada escena (con tiempos por palabra).
 2. Línea de tiempo: cada escena dura lo que dura su voz + un respiro.
 3. Blender renderiza las tomas (pipeline/blender_render.py).
 4. Audio: voz + efectos (en la palabra elegida) + música opcional.
 5. Subtítulos estilo Shorts (1-3 palabras) + textos grandes de pantalla.
 6. FFmpeg junta todo en out/<episodio>.mp4
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 44100
PAD_END = 0.35          # respiro al final de cada escena (s)


def find_blender():
    env = os.environ.get("BLENDER")
    if env and Path(env).exists():
        return env
    if shutil.which("blender"):
        return shutil.which("blender")
    for base in (Path(r"C:\Program Files\Blender Foundation"),):
        if base.exists():
            exes = sorted(base.glob("*/blender.exe"), reverse=True)
            if exes:
                return str(exes[0])
    sys.exit("No encuentro Blender. Instálalo o define la variable BLENDER con la ruta a blender.exe")


# ------------------------------------------------------------------- 1. voz

def recortar(audio, words, umbral=0.012, margen=0.03):
    """Quita el silencio del inicio y del final de una frase (voz ágil, sin pausas muertas).

    Corre los tiempos de las palabras para que sigan sincronizados."""
    idx = np.flatnonzero(np.abs(audio) > umbral)
    if not len(idx):
        return audio, words
    a = max(0, idx[0] - int(margen * SR))
    b = min(len(audio), idx[-1] + int(margen * 2 * SR))
    dt = a / SR
    return audio[a:b], [{**w, "t": max(0.0, w["t"] - dt)} for w in words]


async def tts(text, voice, rate, mp3_path, pitch="+0Hz"):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    words = []
    with open(mp3_path, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
    return words


def decode(path):
    """Cualquier audio -> numpy float32 mono 44.1 kHz (vía ffmpeg)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").astype(np.float32) / 32768


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


# ------------------------------------------------------------- subtítulos

def ass_time(t):
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_escape(s):
    return s.replace("{", "(").replace("}", ")").replace("\n", " ")


# color de la palabra clave en los subtítulos (ASS usa &HBBGGRR&): amarillo intenso
HL = r"{\c&H00D7FF&}"


def golpes(sc, f0, fps):
    """Cuadros (absolutos) donde suena cada *palabra clave*: ahí la cámara hace zoom golpe."""
    toks, words = sc["texto"].split(), sc["words"]
    if len(toks) != len(words):
        return []
    return [f0 + round(w["t"] * fps) for w, tok in zip(words, toks) if "*" in tok]


def limpio(texto):
    """Texto para la voz: sin los * de las palabras resaltadas."""
    return texto.replace("*", "")


def build_ass(scenes, W, H, path):
    fs_sub = int(H * 0.048)
    fs_big = int(H * 0.068)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Arial Black,{fs_sub},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{int(fs_sub*0.14)},{int(fs_sub*0.06)},2,60,60,{int(H*0.30)},1
Style: Big,Arial Black,{fs_big},&H0022DDFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,-2,1,{int(fs_big*0.13)},{int(fs_big*0.07)},8,50,50,{int(H*0.09)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for sc in scenes:
        t0, words = sc["t0"], [dict(w) for w in sc["words"]]
        toks = sc["texto"].split()
        if len(toks) == len(words):          # recupera la puntuación del texto original
            for w, tok in zip(words, toks):
                w["hl"] = "*" in tok           # *palabra* = palabra clave resaltada
                w["w"] = tok.replace("*", "")
        # grupos de 1-3 palabras; corta en puntuación
        groups, cur = [], []
        for w in words:
            cur.append(w)
            if len(cur) == 3 or w["w"][-1:] in ",.!?¡¿:;" or len(" ".join(x["w"] for x in cur)) > 16:
                groups.append(cur); cur = []
        if cur:
            groups.append(cur)
        for gi, g in enumerate(groups):
            start = t0 + g[0]["t"]
            end = t0 + (groups[gi + 1][0]["t"] if gi + 1 < len(groups) else sc["dur"] - 0.05)
            txt = " ".join((HL + ass_escape(x["w"]) + r"{\c&HFFFFFF&}") if x.get("hl") else ass_escape(x["w"])
                           for x in g)
            pop = r"{\fscx70\fscy70\t(0,90,\fscx108\fscy108)\t(90,160,\fscx100\fscy100)}"
            lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Sub,,0,0,0,,{pop}{txt}")
        if sc.get("texto_pantalla"):
            big = ass_escape(sc["texto_pantalla"])
            pop = r"{\fscx40\fscy40\t(0,120,\fscx112\fscy112)\t(120,220,\fscx100\fscy100)\frz-3}"
            lines.append(f"Dialogue: 2,{ass_time(t0)},{ass_time(t0 + sc['dur'] - 0.02)},Big,,0,0,0,,{pop}{big}")
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------- personajes y caras

ESTILOS = {"toon": "personajes.json", "bloques": "personajes_bloques.json"}


def cargar_reparto(estilo="toon"):
    data = json.loads((ROOT / "assets" / ESTILOS.get(estilo, "personajes.json")).read_text(encoding="utf-8"))
    return {k: {**v, "id": k} for k, v in data.items() if not k.startswith("_")}


def caras_animadas(pid, cara, extras, out, estilo="toon"):
    """Cara normal + variantes para parpadeo y lip-sync (solo existen en faces_simple).

    Devuelve {"face": png, "face_parpadeo": png|None, "face_habla": png|None}."""
    res = {"face": str(componer_cara(pid, cara, extras, out, estilo))}
    for v in ("parpadeo", "habla"):
        ok = estilo == "bloques" and (ROOT / "assets" / "faces_simple" / f"{cara}__{v}.png").exists()
        res[f"face_{v}"] = str(componer_cara(pid, f"{cara}__{v}", extras, out, estilo)) if ok else None
    return res


def componer_cara(pid, cara, extras, out, estilo="toon"):
    """Expresión + capas del personaje (bigote, lentes...) -> un PNG por (personaje, cara)."""
    from PIL import Image
    faces = ROOT / "assets" / "faces"
    ex_dir = faces / "extras"
    if estilo == "bloques" and (ROOT / "assets" / "faces_simple").exists():
        faces = ROOT / "assets" / "faces_simple"    # ojitos y boca de línea, estilo juguete
    base = faces / f"{cara}.png"
    if not base.exists():
        print(f"[aviso] cara '{cara}' no existe, uso neutral")
        cara, base = "neutral", faces / "neutral.png"
    if not base.exists():
        base = ROOT / "assets" / "faces" / f"{cara}.png"
    if not extras:
        return base
    if any(not (ex_dir / f"{e}.png").exists() for e in extras):
        subprocess.run([sys.executable, str(ROOT / "tools" / "make_face_extras.py")], check=True)
    sys.path.insert(0, str(ROOT / "tools"))
    from make_face_extras import DEBAJO
    dst = out / "caras" / f"{estilo}__{pid}__{cara}.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    for e in [e for e in extras if e in DEBAJO]:
        img.alpha_composite(Image.open(ex_dir / f"{e}.png").convert("RGBA"))
    img.alpha_composite(Image.open(base).convert("RGBA"))
    for e in [e for e in extras if e not in DEBAJO]:
        if (ex_dir / f"{e}.png").exists():
            img.alpha_composite(Image.open(ex_dir / f"{e}.png").convert("RGBA"))
    img.save(dst)
    return dst


def actores(sc, reparto, out, estilo="toon"):
    """Protagonista (campos personaje/pose/cara de la escena) + secundarios (lista "extras")."""
    lista = [{"personaje": sc.get("personaje", "sticky"), "pose": sc.get("pose", "de_pie"),
              "cara": sc.get("cara", "neutral"), "efecto": sc.get("efecto"),
              "efecto_progresivo": sc.get("efecto_progresivo", False)}] + list(sc.get("extras", []))
    res = []
    for a in lista:
        pid = a.get("personaje", "sticky")
        if pid not in reparto:
            print(f"[aviso] personaje '{pid}' no está en assets/personajes.json, uso sticky")
            pid = "sticky"
        d = reparto[pid]
        cara = a.get("cara", "neutral")
        res.append({**a, "personaje": pid, "def": d, "cara": cara, "pose": a.get("pose", "de_pie"),
                    "escala": a.get("escala", d.get("escala", 1.0)),
                    "brillo_ojos": a.get("brillo_ojos", cara == "brillante"),
                    **caras_animadas(pid, cara, d.get("cara_extra", []), out, estilo)})
    return res


# ------------------------------------------------- vida: parpadeo y lip-sync

def parpadeos(f0, f1, fps, semilla):
    """Cuadros donde el personaje parpadea (cada 2-4.5 s, 4 cuadros cerrado)."""
    import random
    rnd = random.Random(semilla)
    out, f = [], f0 + int(rnd.uniform(0.4, 2.0) * fps)
    while f + 4 < f1:
        out.append([f, f + 3])
        f += int(rnd.uniform(2.0, 4.5) * fps)
    return out


def boca(words, f0, fps):
    """Intervalos [a, b] de cuadros con la boca abierta: abre y cierra ~cada 3 cuadros por sílaba."""
    out = []
    for w in words:
        a = f0 + round(w["t"] * fps)
        b = f0 + round((w["t"] + max(w["d"], 0.12)) * fps)
        f = a
        while f < b:
            out.append([f, min(f + 2, b)])
            f += 4
    return out


# cada plano y su contraplano para los cortes internos (cambiar de ángulo cada ~2 s)
CONTRA = {"medio": "primer_plano", "primer_plano": "medio", "general": "medio", "grupo": "primer_plano",
          "hombro": "primer_plano", "pies": "primer_plano", "contrapicado": "primer_plano",
          "lateral": "primer_plano", "arriba": "medio", "espalda": "primer_plano"}


def cortes(sc, f0, nframes, fps, max_seg=2.6):
    """Divide la toma en sub-planos de <= max_seg s, cortando al inicio de una palabra.

    Devuelve [(cuadro_inicio, plano), ...]. Respeta "planos" del guion si viene la lista."""
    plano = sc.get("plano", "medio")
    if plano in ("zoom_in", "zoom_out") or sc.get("sin_cortes"):
        return [(f0, plano)]
    lista = sc.get("planos") or [plano, CONTRA.get(plano, "primer_plano")]
    dur = nframes / fps
    n = max(1, round(dur / max_seg + 0.25)) if not sc.get("planos") else len(lista)
    if n == 1:
        return [(f0, lista[0])]
    inicios = [w["t"] for w in sc["words"]] or [0]
    res = [(f0, lista[0])]
    for k in range(1, n):
        ideal = dur * k / n
        t = min(inicios, key=lambda x: abs(x - ideal))
        f = f0 + round(t * fps)
        if f - res[-1][0] >= fps * 0.9 and f0 + nframes - f >= fps * 0.9:
            res.append((f, lista[k % len(lista)]))
    return res


# ------------------------------------------------------------------ audio

def sonido(nombre):
    wav = ROOT / "assets" / "sfx" / f"{nombre}.wav"
    if not wav.exists():
        subprocess.run([sys.executable, str(ROOT / "tools" / "make_sfx.py")], check=True)
    return decode(wav) if wav.exists() else None


def pegar(mix, s, at):
    j = int(max(at, 0) * SR)
    seg = s[: max(0, len(mix) - j)]
    mix[j:j + len(seg)] += seg


def mezclar_audio(g, scenes, t, out, agil):
    """Voz + efectos + música por actos (con cruces y 'ducking' bajo la voz) -> out/audio.wav.

    Música: "musica" en cada escena cambia el acto (misterio, tension, triste, calido, comico o
    "silencio" para un corte seco antes del susto); se mantiene hasta que otra escena lo cambie.
    "musica" global = acto inicial (o un .mp3/.wav propio en assets/musica/)."""
    n = int((t + 0.5) * SR)
    voz = np.zeros(n, np.float32)
    fx_mix = np.zeros(n, np.float32)
    for k, sc in enumerate(scenes):
        pegar(voz, sc["audio"], sc["t0"])
        if agil and k > 0 and not sc.get("sin_transicion"):
            s = sonido("transicion")
            if s is not None:
                pegar(fx_mix, s * 0.22, sc["t0"] - 0.1)
        for fx in sc.get("sfx", []):
            s = sonido(fx["sonido"])
            if s is None:
                print(f"[aviso] sonido {fx['sonido']} no existe"); continue
            w_idx = fx.get("palabra", 0)
            at = sc["t0"] + (sc["words"][min(w_idx, len(sc["words"]) - 1)]["t"] if sc["words"] else 0)
            pegar(fx_mix, s * fx.get("volumen", 0.55), at + fx.get("retraso", 0))

    # música por actos
    music_dir = ROOT / "assets" / "musica"
    if agil and not any((music_dir / f"{a}.wav").exists() for a in ("misterio", "tension")):
        subprocess.run([sys.executable, str(ROOT / "tools" / "make_music.py")], check=True)
    acto = g.get("musica", "misterio" if agil else None)
    tramos = []                                  # (acto, t_inicio, t_fin)
    for sc in scenes:
        acto = sc.get("musica", acto)
        if tramos and tramos[-1][0] == acto:
            tramos[-1][2] = sc["t0"] + sc["dur"]
        else:
            tramos.append([acto, sc["t0"], sc["t0"] + sc["dur"]])
    musica = np.zeros(n, np.float32)
    cache = {}
    for acto, a, b in tramos:
        if not acto or acto == "silencio":
            continue
        f = music_dir / (acto if Path(acto).suffix else f"{acto}.wav")
        if not f.exists():
            print(f"[aviso] música {f.name} no existe"); continue
        m = cache.setdefault(acto, decode(f))
        cola = 0.6                                # se cruza con el tramo siguiente
        largo = int((b - a + cola) * SR)
        seg = np.tile(m, largo // len(m) + 1)[:largo].copy()
        fi, fo = int(0.25 * SR), int(cola * SR)
        seg[:fi] *= np.linspace(0, 1, fi)
        seg[-fo:] *= np.linspace(1, 0, fo)
        pegar(musica, seg, a)
    # ducking: la música baja cuando hay voz (envolvente suavizada)
    env = np.abs(voz)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = np.clip(env / (np.percentile(env[env > 1e-4], 60) if np.any(env > 1e-4) else 1), 0, 1)
    vol = g.get("volumen_musica", 0.2 if agil else 0.12)
    mix = voz + fx_mix + musica * vol * (1 - 0.5 * env)
    peak = np.max(np.abs(mix)) or 1
    mix = mix / max(peak, 1.0) * 0.95
    write_wav(out / "audio.wav", mix)


# ------------------------------------------------------------------ main

def estado(out, etapa, **extra):
    """Deja la etapa actual en out/estado.json (lo lee tools/monitor.py)."""
    import time
    f = out / "estado.json"
    data = json.loads(f.read_text("utf-8")) if f.exists() else {}
    if etapa == "voz":
        data = {"inicio": time.time()}
    data.update(etapa=etapa, cambio=time.time(), **extra)
    f.write_text(json.dumps(data, ensure_ascii=False), "utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--calidad", type=int, default=None, help="%% de resolución (50 = rápido)")
    ap.add_argument("--preview", action="store_true", help="solo un cuadro por toma (rapidísimo)")
    ap.add_argument("--tomas", default=None, help="re-renderizar solo estas tomas, ej. 2,4")
    ap.add_argument("--sin-render", action="store_true", help="reusar los cuadros ya renderizados")
    args = ap.parse_args()

    guion_path = Path(args.guion).resolve()
    g = json.loads(guion_path.read_text(encoding="utf-8"))
    ep = guion_path.parent
    out = ep / "out"
    (out / "voz").mkdir(parents=True, exist_ok=True)
    fps = g.get("fps", 30)
    W, H = (1080, 1920) if g.get("formato", "vertical") == "vertical" else (1920, 1080)
    calidad = args.calidad or g.get("calidad", 100)

    # 1. voz ---------------------------------------------------------------
    estado(out, "voz", preview=bool(args.preview))
    estilo = g.get("estilo", "toon")
    reparto = cargar_reparto(estilo)
    agil = estilo == "bloques"            # ritmo de Shorts: voz más rápida y sin silencios
    voice = g.get("voz", "es-MX-JorgeNeural")
    rate = g.get("velocidad", "+12%" if agil else "+0%")
    pad = g.get("pausa", 0.12 if agil else PAD_END)
    scenes = []
    for i, sc in enumerate(g["escenas"]):
        mp3 = out / "voz" / f"{i:02d}.mp3"
        meta = out / "voz" / f"{i:02d}.json"
        # ¿quién habla? (diálogo): usa la voz y el tono de ese personaje
        v, pitch, r = voice, "+0Hz", rate
        if "habla" in sc:
            lista = [sc.get("personaje", "sticky")] + [e.get("personaje") for e in sc.get("extras", [])]
            quien = reparto.get(lista[min(sc["habla"], len(lista) - 1)], {})
            v, pitch, r = quien.get("voz", voice), quien.get("tono", "+0Hz"), quien.get("velocidad", rate)
        v, pitch, r = sc.get("voz", v), sc.get("tono", pitch), sc.get("velocidad", r)
        cache_key = {"texto": sc["texto"], "voz": v, "vel": r, "tono": pitch}
        if meta.exists() and json.loads(meta.read_text("utf-8")).get("key") == cache_key:
            words = json.loads(meta.read_text("utf-8"))["words"]
        else:
            print(f"[voz] {i} ({v} {pitch}): {limpio(sc['texto'])}")
            words = asyncio.run(tts(limpio(sc["texto"]), v, r, mp3, pitch))
            meta.write_text(json.dumps({"key": cache_key, "words": words}, ensure_ascii=False), "utf-8")
        audio = decode(mp3)
        if agil:
            audio, words = recortar(audio, words)
        scenes.append({**sc, "i": i, "words": words, "audio": audio,
                       "dur": len(audio) / SR + sc.get("pausa", pad)})

    # 2. línea de tiempo ----------------------------------------------------
    t, f = 0.0, 1
    shots = []
    for sc in scenes:
        sc["t0"] = t
        nframes = max(6, round(sc["dur"] * fps))
        sc["dur"] = nframes / fps
        acts = actores(sc, reparto, out, estilo)
        for k, a in enumerate(acts):
            if a.get("face_parpadeo"):
                a["parpadeos"] = parpadeos(f, f + nframes - 1, fps, sc["i"] * 31 + k)
            if a.get("face_habla") and sc.get("habla") == k:
                a["boca"] = boca(sc["words"], f, fps)
        shots.append({"i": sc["i"], "f0": f, "f1": f + nframes - 1, "escenario": sc.get("escenario", "vacio"),
                      "plano": sc.get("plano", "medio"), "actores": acts,
                      "cortes": cortes(sc, f, nframes, fps) if agil else [(f, sc.get("plano", "medio"))],
                      "temblor": sc.get("temblor", False),
                      "foco": sc.get("foco", 0), "noche": sc.get("noche", False),
                      "golpes": golpes(sc, f, fps),
                      "color_fondo": sc.get("color_fondo")})
        f += nframes
        t += sc["dur"]
    total_frames = f - 1
    frames_dir = out / "frames"
    timeline = {"fps": fps, "res": [W, H], "calidad": calidad, "frames_dir": str(frames_dir),
                "shots": shots, "solo_preview": args.preview, "estilo": estilo,
                "muestras": 24 if estilo == "bloques" else 16}
    (out / "timeline.json").write_text(json.dumps(timeline, indent=1, ensure_ascii=False), "utf-8")
    print(f"[tiempo] {len(shots)} tomas, {t:.1f} s, {total_frames} cuadros")

    # 3. render -------------------------------------------------------------
    estado(out, "render", total=total_frames, segundos=round(t, 1))
    if not args.sin_render:
        if not args.tomas and not args.preview and frames_dir.exists():
            shutil.rmtree(frames_dir)
        frames_dir.mkdir(exist_ok=True)
        cmd = [find_blender(), "-b", "--factory-startup", "-P", str(ROOT / "pipeline" / "blender_render.py"),
               "--", str(out / "timeline.json")]
        if args.tomas:
            cmd.append(args.tomas)
        print("[blender]", " ".join(cmd))
        subprocess.run(cmd, check=True)
    # 4. audio (también en preview, para escuchar el ritmo) ------------------
    estado(out, "audio")
    mezclar_audio(g, scenes, t, out, agil)
    build_ass(scenes, W, H, out / "subs.ass")
    if args.preview:
        estado(out, "listo", preview=True)
        print("[preview] listo:", out, "(escucha out/audio.wav)")
        return

    # 5. video final --------------------------------------------------------
    estado(out, "video")
    final = ep / f"{ep.name}.mp4"
    subs = str(out / "subs.ass").replace("\\", "/").replace(":", "\\:")
    vf = f"scale={W}:{H}:flags=lanczos"
    flash = [(sc["t0"], sc["t0"] + sc["dur"]) for sc in scenes if sc.get("flashback")]
    if flash:   # recuerdos: tono sepia cálido + viñeta
        en = "+".join(f"between(t,{a:.3f},{b:.3f})" for a, b in flash)
        vf += (f",colorchannelmixer=.45:.70:.18:0:.38:.64:.16:0:.28:.50:.13:0:enable='{en}'"
               f",vignette=PI/4:enable='{en}'")
    vf += f",ass='{subs}'"
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-framerate", str(fps), "-i", str(frames_dir / "%06d.png"),
           "-i", str(out / "audio.wav"), "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
           "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)]
    subprocess.run(cmd, check=True)
    estado(out, "listo", video=str(final))
    print("[listo]", final)


if __name__ == "__main__":
    main()
