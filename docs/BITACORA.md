# Bitácora del proyecto

Historial compartido entre dispositivos y sesiones de Claude. **Agrega una entrada al terminar cada tarea**
(la más nueva arriba): fecha, dispositivo/sesión si se sabe, qué se hizo, decisiones tomadas y pendientes.

---

## 2026-11-26: look más cercano a la referencia, Sticky elegante y monitor de render
- Caras simples estilo juguete en `assets/faces_simple/` (`tools/make_faces_simple.py`), usadas automáticamente en el estilo bloques.
- Cabeza de bloques más chica y redondeada (HEAD 0.76, bisel 24 %), brazos pegados al cuerpo y colores vivos (vista Standard).
- **Sticky elegante** (decisión del dueño): esmoquin negro con solapas de satín, camisa blanca, corbatín, pañuelo en el bolsillo,
  gafas de lectura de media luna (`lentes_lectura`), calvo y bufanda azul. La versión anterior quedó como `sticky_casual`.
- `tools/monitor.py`: página local (http://localhost:8765) con el progreso de cada render. `build.py` escribe `out/estado.json` por etapa.
- Velocidad medida sin raytracing: ~1.7 s por cuadro a calidad 50 (antes ~4 s con raytracing).


## 2026-11-26: mejoras sugeridas por Gemini (revisadas y aplicadas)
- Se consultó a Gemini (en el navegador del usuario) cómo se hacen los videos de referencia. Coincide con nuestro enfoque:
  Blender EEVEE, caras 2D sobre la cabeza, voces IA, cortes rápidos y palabra clave en color. Su sugerencia de importar
  avatares de Roblox (Rbx2Blender) **se descartó** por derechos: seguimos con muñecos propios.
- `efecto_progresivo`: barrido animado de vidrio o piedra de los pies a la cabeza, con borde brillante (nodo "Progreso" en `bloques_bl._barrido`).
  Usa transparencia DITHERED (BLENDED producía cabezas fantasma).
- Render más rápido: raytracing apagado y nodo Ambient Occlusion en cada material del estilo bloques.
- Cámara en mano (modificador NOISE en el objetivo de la cámara) y "zoom golpe" automático en cada `*palabra clave*`.
- Subtítulos subidos al 30 % desde abajo (zona segura de la interfaz de Shorts).

**Pendientes sugeridos por Gemini que aún no se hacen**
- Parpadeo automático y boca 2D sincronizada con el volumen de la voz (necesita variantes de cara con boca abierta).
- Romper personajes en pedazos (bisect con bmesh + cuerpos rígidos) para escenas de "se rompe".
- Quitar silencios de la voz con el filtro `silenceremove` de FFmpeg.
- Voces distintas por personaje cuando hablan (no solo el narrador).


## 2026-11-26: estilo "bloques" y formato "Reglas del pueblo"
- Análisis de un canal de referencia de Shorts con muñecos de bloques (1–21 M de vistas): historias de 100–130 s
  con una regla rara ("Si…", "En este pueblo…"), narración en primera persona, giro final, cámara muy cercana,
  cortes cada 2–3 s y la palabra clave del subtítulo en color. Solo se usó como referencia de formato: personajes, historias y escenarios son nuestros.
- Se evaluó generar con IA de video (vidIQ): ~780 créditos por video y la cuenta tiene 0 (plan de 150/mes). Por eso se usa Blender.
- Nuevo estilo `"estilo": "bloques"`: materiales suaves (Principled), sin contornos, bordes biselados, sombras suaves,
  raytracing de EEVEE y texturas procedurales (`bl_util.mat_textura`: adoquín, ladrillo, pasto, madera, piedra).
- `pipeline/bloques_bl.py`: humanos de bloques (ropa por partes, pelo de bloques, 22 accesorios) y animales de bloques,
  además de los efectos `piedra` y `vidrio`. Reparto en `assets/personajes_bloques.json` (19 personajes, mismos ids + `vecino` y `amiga`).
- Escenarios nuevos: `pueblo` (plaza, torre con reloj, estatua, casas) y `sala`. Las paredes interiores ahora miden 12 de alto.
- Planos nuevos: `hombro`, `pies` y `espalda`. Subtítulos: `*palabra*` sale en amarillo.
- Episodio demo: `episodios/pueblo_vidrio/` ("EN ESTE PUEBLO, SI NADIE TE SALUDA, TE VUELVES DE VIDRIO!!!"), 22 escenas, 80 s.

**Pendientes**
- Render lento para 80–120 s (estimado: más de 1 h a calidad 50). Ideas: menos muestras, 24 fps, renderizar tomas en paralelo.
- `espalda` mira hacia -Y: en interiores no hay pared atrás.
- Faltan escenarios de bloques: casa por fuera con jardín, tienda, hospital, salón de clases blanco.
- Falta animar la boca al hablar y hacer que los efectos aparezcan poco a poco (ahora la toma entera ya es de vidrio o de piedra).


## 2026-11-25: regla de sincronización con GitHub
- `CLAUDE.md` ahora exige `git pull` al empezar y commit + push al terminar cada cambio, para que todos los dispositivos estén al día.
- Repo remoto: https://github.com/johnemma2510-design/Videos4d (rama `main`).

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
