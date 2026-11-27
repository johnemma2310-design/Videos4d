"""Renderiza el catálogo visual (sin voz): una foto por personaje y una por escenario.

    python tools/catalogo.py                 # todo
    python tools/catalogo.py personajes      # solo reparto
    python tools/catalogo.py escenarios      # solo escenarios
    python tools/catalogo.py escenarios --noche

Resultado: docs/catalogo_personajes.png y docs/catalogo_escenarios[_noche].png
"""
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
from build import actores, cargar_reparto, find_blender  # noqa: E402

ESCENARIOS = ["pueblo", "sala", "habitacion", "cocina", "escuela", "exterior", "parque", "ciudad", "playa",
              "espacio", "bosque", "vacio"]
CARAS_DEMO = ["feliz", "sonrisa", "pensando", "shock", "malvado", "enojado", "miedo", "triste", "neutral"]


def render(shots, work, estilo="toon"):
    tl = {"fps": 30, "res": [1080, 1920], "calidad": 30, "frames_dir": str(work / "frames"),
          "shots": shots, "solo_preview": True, "estilo": estilo, "muestras": 24}
    (work / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False), "utf-8")
    subprocess.run([find_blender(), "-b", "--factory-startup", "-P", str(ROOT / "pipeline" / "blender_render.py"),
                    "--", str(work / "timeline.json")], check=True)


def hoja(work, labels, dst, cols):
    ims = [Image.open(work / f"preview_{i:02d}.png").convert("RGB") for i in range(len(labels))]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 40)), (25, 25, 30))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arialbd.ttf", 26)
    except OSError:
        font = ImageFont.load_default()
    for i, (im, lab) in enumerate(zip(ims, labels)):
        x, y = (i % cols) * w, (i // cols) * (h + 40)
        sheet.paste(im, (x, y))
        d.text((x + 10, y + h + 6), lab, fill=(255, 255, 255), font=font)
    dst.parent.mkdir(exist_ok=True)
    sheet.save(dst)
    print("[catálogo]", dst)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "todo"
    noche = "--noche" in sys.argv
    estilo = "bloques" if "--bloques" in sys.argv else "toon"
    suf = "_bloques" if estilo == "bloques" else ""
    reparto = cargar_reparto(estilo)
    if what in ("todo", "personajes"):
        work = ROOT / "docs" / f"_render_personajes{suf}"
        work.mkdir(parents=True, exist_ok=True)
        shots = []
        for i, pid in enumerate(reparto):
            sc = {"personaje": pid, "cara": CARAS_DEMO[i % len(CARAS_DEMO)], "pose": "de_pie"}
            shots.append({"i": i, "f0": 1, "f1": 30, "escenario": "vacio", "plano": "medio",
                          "color_fondo": [0.62, 0.84, 0.98], "actores": actores(sc, reparto, work, estilo)})
        render(shots, work, estilo)
        hoja(work, [f"{pid} ({d.get('nombre', '')})" for pid, d in reparto.items()],
             ROOT / "docs" / f"catalogo_personajes{suf}.png", 6)
    if what in ("todo", "escenarios"):
        work = ROOT / "docs" / f"_render_escenarios{suf}"
        work.mkdir(parents=True, exist_ok=True)
        shots = []
        for i, esc in enumerate(ESCENARIOS):
            sc = {"personaje": "sticky", "cara": "feliz", "pose": "saludar",
                  "extras": [{"personaje": "perro", "lugar": "derecha", "cara": "feliz"}] if i % 2 else []}
            shots.append({"i": i, "f0": 1, "f1": 30, "escenario": esc, "plano": "general", "noche": noche,
                          "actores": actores(sc, reparto, work, estilo)})
        render(shots, work, estilo)
        hoja(work, ESCENARIOS, ROOT / "docs" / f"catalogo_escenarios{suf}{'_noche' if noche else ''}.png", 5)


if __name__ == "__main__":
    main()
