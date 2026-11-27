# stick3DD: fábrica automática de videos de Sticky

> **Claude, lee esto primero.** Este repo se trabaja desde varios dispositivos y con varias sesiones de Claude.
> Este archivo es el contexto compartido: qué es el proyecto, cómo está armado y cómo hacer un video.
> El historial y los pendientes están en [docs/BITACORA.md](docs/BITACORA.md). **Al terminar una tarea,
> agrega una entrada ahí** (fecha, qué cambió, qué quedó pendiente) para que el próximo Claude sepa dónde vamos.

## Sincronización con GitHub (obligatorio)

Repo: https://github.com/johnemma2510-design/Videos4d (rama `main`). Se edita desde varios dispositivos
(nuevos personajes, escenarios, poses, guiones), así que el repo debe quedar siempre al día.

- **Al empezar una sesión:** ejecuta `git pull` para traer lo que hicieron en otros dispositivos.
  Si hay conflictos o cambios locales sin guardar, no los sobrescribas: avisa al usuario.
- **Al terminar cualquier cambio** (personaje, escenario, pose, cara, sonido, guion, código o docs):
  1. Agrega una entrada en `docs/BITACORA.md`.
  2. `git add` solo los archivos del cambio. Nunca `out/`, `.mp4`, `.blend` ni datos personales.
  3. `git commit` con mensaje claro en español y la línea `Co-Authored-By` del modelo que estés usando.
  4. `git push`, y verifica con `git status -sb` que quedó igual a `origin/main`.
- Si un push falla, no uses `--force`; explícale al usuario qué pasó.

## Qué es

Canal de YouTube **Curiosidades con Sticky** (@StickyElCurioso): videos "¿Qué pasaría si...?" en español,
Shorts verticales y videos largos. El dueño quiere **automatizar al máximo**: él da un tema y Claude escribe el guion
y elige escenario, planos, poses, caras, personajes secundarios y sonidos. El pipeline renderiza el MP4 sin tocar nada a mano.

**Sticky** = muñeco de palitos 3D, cabeza redonda blanca con contorno negro, caras 2D expresivas y **bufanda azul**.
Es el protagonista por defecto. Estilo visual: low-poly, colores planos, contornos negros y sombreado de 2 tonos (cartoon).

## Dos estilos de video (`"estilo"` en el guion)

| | `toon` (Sticky clásico) | `bloques` (formato principal desde 2026-11-26) |
|---|---|---|
| Look | muñecos de palitos, contornos negros, 2 tonos | muñecos de bloques de juguete, sin contornos, sombras suaves, bordes redondeados, texturas (adoquín, pasto, madera) |
| Reparto | `assets/personajes.json` | `assets/personajes_bloques.json` (mismos ids) |
| Caras | `assets/faces/` (ojos grandes) | `assets/faces_simple/` (ojitos negros y boca de línea, estilo juguete) |
| Sticky | palitos + bufanda azul | **elegante**: esmoquin, corbatín, gafas de lectura, calvo y bufanda azul (`sticky_casual` = la versión con camisa) |
| Formato | "¿Qué pasaría si…?" 20–60 s | **"Reglas del pueblo"**, 70–120 s (ver abajo) |

Referencia de formato: canales de historias en mundo de bloques con millones de vistas en Shorts.
**Nunca** copies sus personajes, títulos ni historias, y no uses logos, nombres ni assets de Roblox o Minecraft:
el estilo es "muñecos de bloques" genérico y los personajes son nuestros.

### Formato "Reglas del pueblo" (estilo bloques)
- **Título**: MAYÚSCULAS + "!!!" con una regla rara: `SI [algo], [consecuencia]!!!` o `EN ESTE PUEBLO, [regla]!!!`.
- **Escena 1**: la regla dicha completa ("En este pueblo, si…, te vuelves de *vidrio*") + `texto_pantalla` + `zoom_in`.
- **Escena 2**: la amenaza (qué pasa si se rompe la regla).
- **Narración en primera persona** (Sticky cuenta lo que le pasó). Fórmula recomendada (desde 2026-11-27):
  1. Gancho: la regla absurda + consecuencia (`musica: "misterio"`).
  2. Exageración del mundo: cómo vive el pueblo con la regla, con un detalle absurdo ("hasta los bebés…", `musica: "comico"`)
     y la leyenda de la entidad (personaje `sombra`, cara `brillante`, plano `contrapicado`, `temblor`, `musica: "tension"`).
  3. Llegada y detonante: "nos mudamos un lunes y nadie nos avisó" + alguien cercano sufre la regla.
  4. Investigación: el protagonista rompe la regla **a propósito** para saber la verdad (`musica: "silencio"` justo antes del susto).
  5. Giro emocional: la entidad era incomprendida (`flashback: true`, `musica: "triste"`) y el verdadero culpable era otro.
  6. Resolución cálida (`musica: "calido"`) + broma de miedo en el CTA ("a los que no dan like, todavía los visita") y suscripción.
  También sirve la versión "síntomas": rompe la regla sin querer, efecto progresivo, todos se alejan, ayuda inesperada, moraleja.
- 25–35 escenas de 1 frase. El pipeline corta solo cada ~2.5 s (plano + contraplano); usa diálogos con `habla`.
- Marca 1 palabra clave por escena con `*asteriscos*`: sale **amarilla** en el subtítulo (la voz no lee los asteriscos).
- Apto para niños: misterio y tensión sí, violencia o sustos fuertes no. Moraleja positiva (amistad, saludar, decir la verdad…).
- Ejemplos completos: `episodios/vigilante_noches/guion.json` (fórmula nueva) y `episodios/pueblo_vidrio/guion.json`.

## Motor nuevo: blocky-studio (Three.js + Remotion, desde 2026-11-27)

Segundo motor para el estilo de bloques, montado con la skill `blocky-3d-story-video` (`.claude/skills/`, viene del
paquete de la carpeta `Skills/` y del tutorial https://www.youtube.com/watch?v=w-wq3uCyCxE). Renderiza en el navegador:
**10 s de video en ~1.5 min** (Blender tarda horas). Sigue el paso a paso de la skill: títulos → guion → voz → reparto →
storyboard → sonido → render → puntaje → lecciones (`blocky-studio/lab/lessons.md`).
- Instalar en otro PC: `cd blocky-studio; npm install; npm rebuild esbuild; python -m venv .venv; .venv\Scripts\python -m pip install -r requirements.txt`.
- Voz en español: edge-tts y alinear con `ALIGN_LANG=es` (`scripts/align.py` acepta el idioma por esa variable).
- Sticky elegante está en `projects/sticky10/cast.json`: torso `varsity` negro con camisa blanca, `bald` y `extras`
  (`scarf` azul, `bowtie`, `glasses` de media luna), que agregamos al motor en `src/engine/avatar/build.ts` y `src/schema/cast.ts`.
- Ejemplo completo de 10 s: `blocky-studio/projects/sticky10/` (`make_story.py` genera `story.json`).
- Episodio completo de referencia: `blocky-studio/projects/vigilante/` (`make_story.py` con escenas, recetas de cámara,
  cortes automáticos `partir()`, whip-outs y música por actos). Copia sus helpers para el próximo video.
- Extensiones nuestras al motor: `scale` en actores, torso `tuxedo`, `extras` (bufanda, corbatín, gafas) y looks
  `NIGHT_GLOW`, `INTERIOR_DAY`, `INTERIOR_NIGHT`. Puntajes de cada video en `blocky-studio/lab/scores.csv`.

## Instalación en un dispositivo nuevo (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File tools/instalar.ps1
```
Instala Blender 5.3, FFmpeg y las dependencias de Python (`requirements.txt`). Blender se busca en
`C:\Program Files\Blender Foundation\*\blender.exe`; si está en otro lado, define la variable `BLENDER`.
En Mac/Linux: instala Blender y FFmpeg con tu gestor de paquetes y luego `pip install -r requirements.txt`.

## Cómo hacer un video ("haz un video sobre X")

1. Crea `episodios/<slug>/guion.json` (formato abajo). **Tú decides todo.** Reglas de estilo:
   - Gancho en la escena 1: pregunta + `texto_pantalla` grande + `plano: "zoom_in"`.
   - Una frase corta por escena (2–5 s de voz). Cambia de plano casi en cada escena; no repitas el mismo dos veces seguidas.
   - La cara refleja la emoción de la frase y cambia seguido: es lo que da vida.
   - Usa personajes secundarios (`extras`) para contar la historia: mamá, doña Rosa, el perro, el profe…
     Con 2 o más personajes, usa `plano: "grupo"` o pon `foco` en quien habla o reacciona.
   - Cambia de escenario cuando la historia avance; `noche: true` para momentos de miedo o calma.
   - 1–2 efectos de sonido por escena en los momentos clave; `palabra` = índice de la palabra donde suena.
   - Progresión "DÍA 1 → DÍA 10 → DÍA 100" con `texto_pantalla` cuando aplique.
   - Cierre: llamado a suscribirse (`saludar` o `celebrar`, cara `feliz`).
   - Shorts: 20–60 s (8–15 escenas). Videos largos: `"formato": "horizontal"`.
2. Vista previa (1 cuadro por toma, ~1 min). **Mira** las imágenes `out/preview_XX.png` y corrige lo que se vea mal:
   `python pipeline/build.py episodios/<slug>/guion.json --preview --calidad 30`
3. Render final: `python pipeline/build.py episodios/<slug>/guion.json --calidad 100` (para pruebas, `--calidad 50`).
   Para ver el avance: `python tools/monitor.py` y abrir http://localhost:8765 (barra, cuadros, velocidad, hora de fin,
   toma actual y último cuadro). En la app de Claude se abre con la configuración `monitor` de `.claude/launch.json`.
   Resultado: `episodios/<slug>/<slug>.mp4`. Para re-renderizar tomas sueltas usa `--tomas 2,5`, que vuelve a armar el video solo.
   Tarda aprox. 1–1.5 s por cuadro a calidad 50 (unos 15 min por cada 25 s de video): córrelo en segundo plano.

Ejemplos completos: `episodios/prueba_cama/guion.json` (solo Sticky) y `episodios/demo_reparto/guion.json` (varios personajes).

## Formato de guion.json

```json
{
  "titulo": "...", "estilo": "bloques", "formato": "vertical", "voz": "es-MX-JorgeNeural", "velocidad": "+8%",
  "musica": "opcional.mp3", "volumen_musica": 0.12,
  "escenas": [
    {
      "texto": "lo que narra la voz, con la *palabra* clave resaltada",
      "escenario": "cocina", "noche": false, "plano": "medio", "foco": 0,
      "personaje": "sticky", "pose": "de_pie", "cara": "feliz", "efecto": "vidrio",
      "extras": [
        {"personaje": "mama", "lugar": "derecha", "pose": "senalar", "cara": "enojado"},
        {"personaje": "perro", "lugar": "frente_izquierda", "pose": "saltar", "cara": "feliz"}
      ],
      "sfx": [{"sonido": "pop", "palabra": 0, "volumen": 0.55, "retraso": 0}],
      "texto_pantalla": "DÍA 1", "color_fondo": [0.98, 0.8, 0.25], "pausa": 0.35
    }
  ]
}
```
- `personaje`, `pose`, `cara`: el protagonista de la escena (por defecto `sticky`).
- `extras`: secundarios. `lugar` es relativo al protagonista; también se puede dar `"pos": [dx, dy]`.
  `"mirar": false` para que no giren hacia el protagonista. `"escala"` cambia el tamaño.
- `foco`: índice del personaje al que apunta la cámara (0 = protagonista, 1 = primer extra…).
- `color_fondo` solo aplica al escenario `vacio`.
- `efecto` (protagonista o extras): `piedra` (estatua gris) o `vidrio` (transparente celeste). La cara se mantiene.
  Con `"efecto_progresivo": true` (solo estilo bloques) el efecto sube de los pies a la cabeza durante la toma,
  con un borde brillante (rojo en piedra, celeste en vidrio): úsalo en la escena donde empieza la transformación.
- `*palabra*` en `texto`: palabra clave en amarillo en el subtítulo, y además la cámara hace un "zoom golpe" en ese instante.
- En estilo bloques la cámara tiene un temblor leve de cámara en mano (automático).
- **Ritmo (solo bloques, automático)**: voz `+12%` sin silencios al inicio/final, respiro de 0.12 s, corte de cámara
  cada ~2.5 s en el inicio de una palabra (plano → contraplano), whoosh suave en cada cambio de escena, parpadeo
  aleatorio y música de fondo (acto `misterio` si no dices otra). `"planos": ["general","primer_plano","medio"]` fija los
  sub-planos de una escena; `"sin_cortes": true` los desactiva; `"sin_transicion": true` quita el whoosh.
- `"habla": n`: el personaje n (0 = protagonista, 1 = primer extra…) dice la frase con **su voz** (`voz`/`tono`/`velocidad`
  en `personajes_bloques.json`) y **mueve la boca** (lip-sync). Sin `habla`, la frase es narración. `"voz"`/`"tono"` en la escena lo fuerzan.
- `"musica"` en una escena cambia el acto desde ahí: `misterio`, `tension`, `triste`, `calido`, `comico` o `silencio` (corte seco).
  Se cruzan solas y bajan cuando hay voz. Pistas en `assets/musica/` (`python tools/make_music.py`; puedes poner tus `.wav` con esos nombres).
- `"flashback": true`: tono sepia + viñeta en esa escena. `"temblor": true`: sacudida fuerte de cámara al inicio de la toma.
- `"brillo_ojos": true` en un actor (automático con cara `brillante`): la cara brilla en la oscuridad.
- `--preview` ahora también genera `out/audio.wav` y `out/subs.ass`, para escuchar el ritmo antes del render.

## Catálogo actual

Hay imágenes de todo en `docs/catalogo_personajes.png`, `docs/catalogo_escenarios.png` y sus versiones `_bloques`
(se regeneran con `python tools/catalogo.py` y `python tools/catalogo.py --bloques`).

- **escenario**: `pueblo` (plaza de adoquín, torre con reloj, estatua, casas, bancas: el principal del estilo bloques), `sala` (sofá, tele), `habitacion` (cama, ventana, lámpara), `cocina` (estufa, refri, mesa), `escuela` (pizarrón, pupitres),
  `exterior` (pasto, árboles), `parque` (banca, flores, farol), `ciudad` (edificios, calle, coche), `playa` (palmera, mar, sombrilla),
  `espacio` (luna, cohete, planeta), `bosque` (pinos, hongos, rocas), `vacio` (fondo de color). Todos aceptan `noche: true`.
- **plano**: `general`, `medio`, `primer_plano`, `arriba`, `contrapicado`, `lateral`, `zoom_in`, `zoom_out`, `grupo` (encuadra a todos),
  `hombro` (de frente al foco con el hombro de otro personaje en el borde; necesita un extra), `pies` (detalle de pies, ideal con `efecto`),
  `espalda` (detrás del personaje; solo en exteriores, en interiores no hay pared atrás)
- **lugar** (extras): `izquierda`, `derecha`, `atras`, `atras_izquierda`, `atras_derecha`, `frente_izquierda`, `frente_derecha`, `lejos_izquierda`, `lejos_derecha`
- **personajes** (`assets/personajes.json`): `sticky`, `nino`, `nina`, `senora` (Doña Rosa), `mama`, `senor_bigote` (Don Bigotes),
  `abuelo`, `chef`, `doctor` (Doctora), `profe`, `policia`, `rockero`, `vaquero`, `perro` (Firulais), `gato` (Michi), `pajaro` (Pío), `cerdo` (Chancho).
  En bloques existen además `vecino`, `amiga` y `sombra` (El Vigilante: entidad alta y misteriosa, escala 1.7) (`assets/personajes_bloques.json`, con colores `piel`, `camisa`, `pantalon`, `zapatos` y `manga_larga`).
- **accesorios bloques** (`pipeline/bloques_bl.py`): `pelo_corto`, `pelo_largo`, `chongo`, `coletas`, `calvo`, `pelo_punta`, `gorra`, `gorra_policia`,
  `sombrero`, `gorro_chef`, `lazo`, `bufanda`, `panuelo`, `corbata`, `corbatin`, `smoking`, `chaleco`, `mochila`, `falda`, `vestido`, `bata`,
  `delantal`, `collar`, `baston`
- **pose humanos**: `de_pie`, `saludar`, `pensar`, `caminar`, `correr`, `saltar`, `celebrar`, `temblar`, `mareado`, `triste`, `senalar`, `acostado` (solo en `habitacion`, queda en la cama)
- **pose animales**: `de_pie`, `caminar`, `correr`, `saltar`, `celebrar`, `temblar`, `triste`, `volar` (pájaro). Cualquier otra pose se convierte en `de_pie`.
- **cara** (`assets/faces/`): `neutral`, `feliz`, `sonrisa`, `shock`, `triste`, `enojado`, `malvado`, `aburrido`, `miedo`, `mareado`, `pensando`, `dormido`; en bloques además `terror` (pupilas diminutas), `llorando`, `furioso`, `sospecha`, `brillante` (ojos amarillos que brillan), `asombro`.
  Cada cara de `faces_simple` tiene variantes `__parpadeo` y `__habla` (las usa el pipeline solo)
- **cara_extra** (capas por personaje, `assets/faces/extras/`): `bigote`, `bigote_blanco`, `barba`, `barba_blanca`, `pestanas`, `labios`, `chapitas`, `pecas`, `lentes`, `lentes_lectura`, `lentes_sol`, `nariz_perro`, `nariz_gato`, `pico`, `nariz_cerdo`
- **accesorios**: pelo `pelo_corto`, `pelo_largo`, `chongo`, `coletas`, `calvo`, `pelo_punta`; cabeza `gorra`, `gorra_policia`, `sombrero`, `gorro_chef`, `lazo`;
  cuerpo `bufanda`, `corbata`, `falda`, `vestido`, `bata`, `delantal`, `collar`, `baston`
- **sfx** (`assets/sfx/`): `pop`, `whoosh`, `boom`, `ding`, `boing`, `golpe`, `sorpresa`, `tictac`, `ronquido`, `triste`, `tiza`, `lapiz`, `papel`, `borrador`, `puerta`, `portazo`, `clic`,
  `boom_grave`, `riser`, `latido`, `viento`, `pasos`, `campana`, `transicion`, `corte_seco`, `risa_eco` (`python tools/make_sfx.py`; un `.wav` tuyo con el mismo nombre los reemplaza)
- **voces** edge-tts: `es-MX-JorgeNeural`, `es-MX-DaliaNeural`, `es-ES-AlvaroNeural`, `es-CO-GonzaloNeural`…

## Cómo extender (y luego actualiza el catálogo de arriba)

| Quiero... | Dónde |
|---|---|
| Nuevo personaje (combinando lo que ya existe) | agregar una entrada en `assets/personajes.json`; no hace falta tocar código |
| Nuevo accesorio 3D | función `acc_<nombre>` en `pipeline/personajes_bl.py` (se registra sola) |
| Nueva expresión | `tools/make_faces.py` (decorador `@face`) y luego `python tools/make_faces.py` |
| Nueva capa de cara | `tools/make_face_extras.py` (`EXTRAS`; si va debajo de la boca, agregarla a `DEBAJO`) |
| Nuevo escenario | función en `pipeline/escenarios.py`, agregarla a `SETS`; debe devolver `{"standing": (x,y,z)}` |
| Nueva pose | `pipeline/poses.py` (`POSES` para humanos, `ANIMAL_POSES` para animales) |
| Nuevo animal | `build_cuadrupedo` / `build_pajaro` en `pipeline/personajes_bl.py` |
| Sonido | `tools/make_sfx.py` o un `.wav` propio en `assets/sfx/` con el nombre que quieras |

Después de agregar personajes o escenarios: `python tools/catalogo.py` y **revisa la imagen**.

## Arquitectura

```
guion.json ─▶ pipeline/build.py ─┬─▶ edge-tts (voz + tiempos por palabra)
                                 ├─▶ compone caras (expresión + capas del personaje) ─▶ out/caras/
                                 ├─▶ out/timeline.json ─▶ Blender (-b) pipeline/blender_render.py
                                 │        ├─ escenarios.py   (sets)
                                 │        ├─ personajes_bl.py (construye personajes desde personajes.json)
                                 │        ├─ poses.py        (animación por keyframes)
                                 │        └─ bl_util.py      (materiales cartoon, contornos, primitivas)
                                 ├─▶ mezcla audio (voz + sfx + música) ─▶ out/audio.wav
                                 ├─▶ subtítulos ASS (1–3 palabras, estilo Shorts) ─▶ out/subs.ass
                                 └─▶ FFmpeg ─▶ episodios/<slug>/<slug>.mp4
```
Detalles clave:
- Todo se construye **por código** cada toma (no hay .blend guardados). Blender arranca con `--factory-startup`.
- Las caras son PNG proyectados en el frente (-Y) de la cabeza esfera. Los personajes miran a -Y.
- Contorno = modificador Solidify con normales invertidas (inverted hull). Sombreado = Shader to RGB + rampa constante (EEVEE).
- Los materiales se cachean por color (`bl_util.mat`) para compilar menos shaders.
- `out/` y los `.mp4` no se suben a git (ver `.gitignore`).

## Convenciones

- Código y textos en español. Python 3.11+ (probado en 3.14) y Blender 5.3.
- No subas videos ni renders a git; sí sube los `guion.json` de cada episodio.
- Antes de un render largo, haz siempre la `--preview` y revísala.

## Música y efectos de sonido (biblioteca compartida)

Los 3 proyectos de videos de este PC (stick3DD, STICK 3D y animacion Stick) comparten la misma biblioteca de audio.
- **En este proyecto está en** `assets/musica/ y assets/sfx/ (catálogo: assets/CATALOGO_AUDIO.md)`. La lista con el ambiente, el origen y la licencia de cada archivo está en el `CATALOGO` de esa carpeta.
- **Copia maestra:** `C:\Users\cit\Audio-Compartido\` (ahí está también el catálogo original).
- **También hay `sfx_drive/`**: 37 efectos bajados de una carpeta de Google Drive (memes, golpes, transiciones). En el catálogo cada uno tiene su nivel de riesgo de copyright. Los 🔴 **no se usan** en videos monetizados, y los 🟡 solo de vez en cuando y en momentos cortos.
- **Antes de buscar o generar un sonido, mira el catálogo.** Si ya hay uno que sirve, úsalo.
- **Si agregas uno nuevo:** guárdalo en la carpeta de audio de este proyecto (minúsculas, sin espacios ni acentos) y ejecuta
  `powershell -ExecutionPolicy Bypass -File C:\Users\cit\Audio-Compartido\sincronizar_audio.ps1`. El script lo copia a los otros proyectos sin sobrescribir nada.
  Luego describe en `C:\Users\cit\Audio-Compartido\CATALOGO.md` para qué sirve, de dónde salió y su licencia, vuelve a ejecutar el script y haz commit y push de la carpeta de audio.
- **Dónde buscar audio nuevo:** genéralo con código (`tools/make_sfx.py` y `tools/make_music.py` de stick3DD), o usa YouTube Audio Library, Pixabay o Freesound (solo CC0). Incompetech es CC-BY y hay que dar crédito. **Nunca** uses música comercial ni sonidos "trending" de TikTok.