# Bitácora del proyecto

Historial compartido entre dispositivos y sesiones de Claude. **Agrega una entrada al terminar cada tarea**
(la más nueva arriba): fecha, dispositivo/sesión si se sabe, qué se hizo, decisiones tomadas y pendientes.

---

## 2026-11-25: reparto, escenarios y preparación para GitHub
- Se reorganizó el render en módulos: `bl_util.py`, `personajes_bl.py`, `escenarios.py`, `poses.py` y `blender_render.py`.
- **Reparto** en `assets/personajes.json`: 17 personajes (13 humanos y 4 animales: perro, gato, pájaro, cerdo).
  Los humanos se arman con accesorios 3D (pelo, gorras, sombreros, ropa, bastón) y capas de cara (bigote, barba, lentes, pestañas…).
- **Escenarios**: de 3 se pasó a 10 (cocina, escuela, parque, ciudad, playa, espacio, bosque, además de los anteriores), todos con modo `noche`.
- El guion acepta varios personajes por escena (`extras`, `lugar`, `foco`) y un plano nuevo, `grupo`.
- `tools/catalogo.py` genera `docs/catalogo_personajes.png` y `docs/catalogo_escenarios.png`.
- Episodio de ejemplo con reparto: `episodios/demo_reparto/` (6 escenas, 22 s).
- Archivos para GitHub: README, `.gitignore`, `requirements.txt`, `tools/instalar.ps1`.

**Pendientes / ideas**
- Render lento (~1.3 s/cuadro a calidad 50). Ideas: bajar muestras EEVEE a 8, renderizar tomas en paralelo, usar la GPU.
- La voz edge-tts es gratis pero algo robótica; se puede probar ElevenLabs (necesita API key).
- Música de fondo: falta poner pistas libres de derechos en `assets/musica/`.
- Los sonidos son sintéticos; reemplazarlos por `.wav` reales libres de derechos.
- Faltan poses: sentarse, comer, dormir de pie, hablar (boca animada), y que los personajes caminen hacia un lugar.
- Faltan: miniaturas automáticas (estilo "DÍA 1 vs DÍA 100"), subida a YouTube y formato horizontal para videos largos (no se ha probado).
- En la toma "mareado" en primer plano la cabeza puede salirse un poco del cuadro.
- La visera de la `gorra` (niño) casi no se ve de frente.
- De noche, los interiores se ven algo grises; falta una luz cálida de lámpara.

## 2026-11-25: primera versión del pipeline
- Análisis de un canal de referencia (Shorts de stickman 3D): narración en primera persona, caras 2D sobre una cabeza 3D,
  cortes cada 2–4 s y subtítulos palabra por palabra. Se usó solo como referencia de estilo, sin copiar personajes.
- Se eligió **Blender 5.3 + Python** (todo por script) + **edge-tts** + **FFmpeg**.
- Sticky en 3D (cabeza blanca, bufanda azul), 12 expresiones, 10 sonidos sintéticos, 12 poses y 8 planos.
- Primer video: `episodios/prueba_cama/` ("¿Qué pasaría si no te levantas de la cama en 100 días?").
