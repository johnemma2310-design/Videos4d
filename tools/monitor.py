"""Monitor de render: página web local que muestra cuánto falta para cada episodio.

    python tools/monitor.py            # abre http://localhost:8765
    python tools/monitor.py --puerto 9000

Lee episodios/*/out/ (timeline.json, estado.json y los cuadros PNG). No toca nada:
se puede dejar abierto mientras build.py renderiza, incluso desde otra terminal.
"""
import argparse
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
EPIS = ROOT / "episodios"


def leer_json(p, default=None):
    try:
        return json.loads(p.read_text("utf-8"))
    except (OSError, ValueError):
        return default


def cuadros(frames_dir):
    """[(numero, mtime)] de los PNG renderizados, ordenados por número."""
    out = []
    try:
        with os.scandir(frames_dir) as it:
            for e in it:
                if e.name.endswith(".png") and e.name[:-4].isdigit():
                    out.append((int(e.name[:-4]), e.stat().st_mtime))
    except OSError:
        pass
    out.sort()
    return out


def info_episodio(ep):
    out = ep / "out"
    guion = leer_json(ep / "guion.json", {})
    tl = leer_json(out / "timeline.json", {})
    est = leer_json(out / "estado.json", {})
    shots = tl.get("shots", [])
    total = shots[-1]["f1"] if shots else est.get("total", 0)
    now = time.time()
    fr = cuadros(out / "frames")
    hechos = len(fr)
    ultimo = max((m for _, m in fr), default=0)
    # velocidad con los últimos 40 cuadros (por hora de escritura)
    por_tiempo = sorted(m for _, m in fr)[-40:]
    vel = (por_tiempo[-1] - por_tiempo[0]) / (len(por_tiempo) - 1) if len(por_tiempo) > 5 else None
    etapa = est.get("etapa", "sin iniciar")
    if est.get("preview"):
        etapa = "vista previa" if etapa != "listo" else "vista previa lista"
    activo = (etapa == "render" and now - ultimo < 120) or \
             (etapa in ("voz", "audio", "video") and now - est.get("cambio", 0) < 600)
    faltan = max(total - hechos, 0)
    eta = faltan * vel if (vel and etapa == "render") else None
    if etapa in ("audio", "video"):
        eta = 20
    num_ultimo = max((n for n, m in fr if m == ultimo), default=0)
    toma_actual = next((s["i"] for s in shots if s["f0"] <= num_ultimo + 1 <= s["f1"]), None)
    tomas = []
    hechos_set = {n for n, _ in fr}
    for s in shots:
        n = s["f1"] - s["f0"] + 1
        d = sum(1 for k in range(s["f0"], s["f1"] + 1) if k in hechos_set)
        tomas.append({"i": s["i"], "escenario": s.get("escenario"), "plano": s.get("plano"),
                      "pct": round(100 * d / n) if n else 0})
    mp4 = ep / f"{ep.name}.mp4"
    video_listo = mp4.exists() and mp4.stat().st_mtime >= est.get("inicio", 0)
    return {
        "id": ep.name, "titulo": guion.get("titulo", ep.name), "estilo": guion.get("estilo", "toon"),
        "etapa": "listo" if (etapa == "listo" and video_listo) else etapa, "activo": activo,
        "total": total, "hechos": hechos, "pct": round(100 * hechos / total, 1) if total else 0,
        "vel": round(vel, 2) if vel else None, "eta": round(eta) if eta else None,
        "fin": time.strftime("%H:%M", time.localtime(now + eta)) if eta else None,
        "transcurrido": round(now - est["inicio"]) if est.get("inicio") else None,
        "duracion_video": est.get("segundos") or (round(total / tl.get("fps", 30), 1) if total else None),
        "calidad": tl.get("calidad"), "toma_actual": toma_actual, "tomas": tomas,
        "video": str(mp4.relative_to(ROOT)) if video_listo else None,
        "hay_cuadro": hechos > 0, "ultimo": ultimo,
    }


def estado_general():
    eps = [info_episodio(e) for e in sorted(EPIS.iterdir()) if (e / "guion.json").exists()]
    eps.sort(key=lambda e: (not e["activo"], -e["ultimo"]))
    return {"ahora": time.strftime("%H:%M:%S"), "episodios": eps}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api":
            return self._send(200, json.dumps(estado_general(), ensure_ascii=False).encode(), "application/json")
        if u.path == "/cuadro":
            ep = parse_qs(u.query).get("ep", [""])[0]
            d = (EPIS / ep / "out" / "frames").resolve()
            if EPIS.resolve() not in d.parents:
                return self._send(404, b"", "text/plain")
            fr = cuadros(d)
            if not fr:
                return self._send(404, b"", "text/plain")
            n = max(fr, key=lambda x: x[1])[0]
            return self._send(200, (d / f"{n:06d}.png").read_bytes(), "image/png")
        return self._send(200, PAGE.encode(), "text/html; charset=utf-8")


PAGE = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Monitor de render</title>
<style>
:root{--bg:#f4f6fb;--card:#fff;--ink:#1c2030;--mut:#6b7285;--line:#e3e7ef;--acc:#2f7cf6;--ok:#1fa45a;--warn:#e8a317}
@media (prefers-color-scheme:dark){:root{--bg:#12141b;--card:#1b1e28;--ink:#eef1f7;--mut:#9aa1b4;--line:#2a2f3d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,Segoe UI,sans-serif;padding:16px}
h1{font-size:20px;margin:0 0 4px}.sub{color:var(--mut);margin-bottom:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;margin-bottom:14px;display:flex;gap:16px}
.img{width:120px;flex:none;aspect-ratio:9/16;border-radius:10px;background:var(--line) center/cover no-repeat}
.body{flex:1;min-width:0}.tt{font-weight:700;font-size:16px;margin-bottom:2px;overflow-wrap:anywhere}
.tag{display:inline-block;font-size:12px;padding:2px 8px;border-radius:99px;background:var(--line);color:var(--mut);margin-right:6px}
.tag.on{background:var(--acc);color:#fff}.tag.ok{background:var(--ok);color:#fff}
.bar{height:12px;background:var(--line);border-radius:99px;overflow:hidden;margin:12px 0 8px}
.fill{height:100%;background:var(--acc);border-radius:99px;transition:width .6s}
.fill.ok{background:var(--ok)}
.big{font-size:26px;font-weight:800}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;margin-top:8px}
.k{color:var(--mut);font-size:12px}.v{font-weight:700}
.tomas{display:flex;gap:2px;margin-top:10px}.t{flex:1;height:8px;border-radius:2px;background:var(--line);position:relative;overflow:hidden}
.t i{position:absolute;inset:0;background:var(--ok);transform-origin:left}.t.cur{outline:2px solid var(--warn)}
@media (max-width:520px){.card{flex-direction:column}.img{width:100%;max-width:180px}}
</style></head><body>
<h1>🎬 Monitor de render</h1><div class="sub" id="sub">cargando…</div><div id="list"></div>
<script>
const fmt=s=>{if(s==null)return'—';s=Math.round(s);const h=Math.floor(s/3600),m=Math.floor(s%3600/60),x=s%60;
 return h?`${h} h ${m} min`:m?`${m} min ${x} s`:`${x} s`};
const ETAPA={"voz":"Generando voz","render":"Renderizando","audio":"Mezclando audio","video":"Armando el video",
 "listo":"¡Listo!","vista previa":"Vista previa","vista previa lista":"Vista previa lista","sin iniciar":"Sin iniciar"};
async function tick(){
 try{const r=await fetch('/api');const d=await r.json();
  document.getElementById('sub').textContent=`Actualizado ${d.ahora} · se refresca cada 3 s`;
  document.getElementById('list').innerHTML=d.episodios.map(e=>{
   const ok=e.etapa==='listo';const tag=ok?'ok':(e.activo?'on':'');
   const img=e.hay_cuadro?`style="background-image:url('/cuadro?ep=${encodeURIComponent(e.id)}&t=${e.ultimo}')"`:'';
   const main=ok?`<div class="big">✅ Video listo</div><div class="k">${e.video}</div>`:
     e.eta!=null&&e.activo?`<div class="big">Faltan ${fmt(e.eta)}</div><div class="k">termina aprox. a las ${e.fin}</div>`:
     `<div class="big">${e.activo?ETAPA[e.etapa]||e.etapa:'En pausa'}</div>`;
   return `<div class="card"><div class="img" ${img}></div><div class="body">
    <div class="tt">${e.titulo}</div>
    <span class="tag ${tag}">${ETAPA[e.etapa]||e.etapa}${e.activo&&!ok?' ●':''}</span><span class="tag">${e.estilo}</span>
    ${e.calidad?`<span class="tag">calidad ${e.calidad}%</span>`:''}
    <div class="bar"><div class="fill ${ok?'ok':''}" style="width:${ok?100:e.pct}%"></div></div>
    ${main}
    <div class="grid">
     <div><div class="k">Cuadros</div><div class="v">${e.hechos} / ${e.total} (${e.pct}%)</div></div>
     <div><div class="k">Velocidad</div><div class="v">${e.vel?e.vel+' s/cuadro':'—'}</div></div>
     <div><div class="k">Lleva</div><div class="v">${fmt(e.transcurrido)}</div></div>
     <div><div class="k">Video final</div><div class="v">${e.duracion_video?e.duracion_video+' s':'—'}</div></div>
     <div><div class="k">Toma actual</div><div class="v">${e.toma_actual!=null?(e.toma_actual+1)+' de '+e.tomas.length:'—'}</div></div>
    </div>
    <div class="tomas">${e.tomas.map(t=>`<div class="t ${t.i===e.toma_actual&&e.activo?'cur':''}" title="Toma ${t.i+1}: ${t.escenario} / ${t.plano} (${t.pct}%)"><i style="transform:scaleX(${t.pct/100})"></i></div>`).join('')}</div>
   </div></div>`}).join('')||'<div class="card">No hay episodios todavía.</div>';
 }catch(err){document.getElementById('sub').textContent='Sin conexión con el monitor…'}
}
tick();setInterval(tick,3000);
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--puerto", type=int, default=8765)
    a = ap.parse_args()
    print(f"Monitor en http://localhost:{a.puerto}  (Ctrl+C para cerrar)")
    ThreadingHTTPServer(("127.0.0.1", a.puerto), Handler).serve_forever()


if __name__ == "__main__":
    main()
