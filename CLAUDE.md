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
- **Narración en primera persona** (Sticky cuenta lo que le pasó): mudanza o llegada, nadie le avisó, rompe la regla sin querer,
  empiezan los síntomas (detalle de pies o manos con `efecto`), pide ayuda, todos se alejan, momento más oscuro (`noche`),
  ayuda inesperada (un perrito, una abuelita…), giro final ("lo que nadie te cuenta es que…"), moraleja y cierre con suscripción.
- 18–30 escenas de 1 frase (2–4 s cada una). Cambia de plano siempre; usa mucho `primer_plano`, `hombro`, `pies` y `grupo`.
- Marca 1 palabra clave por escena con `*asteriscos*`: sale **amarilla** en el subtítulo (la voz no lee los asteriscos).
- Apto para niños: misterio y tensión sí, violencia o sustos fuertes no. Moraleja positiva (amistad, saludar, decir la verdad…).
- Ejemplo completo: `episodios/pueblo_vidrio/guion.json`.

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
  En bloques existen además `vecino` y `amiga` (`assets/personajes_bloques.json`, con colores `piel`, `camisa`, `pantalon`, `zapatos` y `manga_larga`).
- **accesorios bloques** (`pipeline/bloques_bl.py`): `pelo_corto`, `pelo_largo`, `chongo`, `coletas`, `calvo`, `pelo_punta`, `gorra`, `gorra_policia`,
  `sombrero`, `gorro_chef`, `lazo`, `bufanda`, `panuelo`, `corbata`, `corbatin`, `smoking`, `chaleco`, `mochila`, `falda`, `vestido`, `bata`,
  `delantal`, `collar`, `baston`
- **pose humanos**: `de_pie`, `saludar`, `pensar`, `caminar`, `correr`, `saltar`, `celebrar`, `temblar`, `mareado`, `triste`, `senalar`, `acostado` (solo en `habitacion`, queda en la cama)
- **pose animales**: `de_pie`, `caminar`, `correr`, `saltar`, `celebrar`, `temblar`, `triste`, `volar` (pájaro). Cualquier otra pose se convierte en `de_pie`.
- **cara** (`assets/faces/`): `neutral`, `feliz`, `sonrisa`, `shock`, `triste`, `enojado`, `malvado`, `aburrido`, `miedo`, `mareado`, `pensando`, `dormido`
- **cara_extra** (capas por personaje, `assets/faces/extras/`): `bigote`, `bigote_blanco`, `barba`, `barba_blanca`, `pestanas`, `labios`, `chapitas`, `pecas`, `lentes`, `lentes_lectura`, `lentes_sol`, `nariz_perro`, `nariz_gato`, `pico`, `nariz_cerdo`
- **accesorios**: pelo `pelo_corto`, `pelo_largo`, `chongo`, `coletas`, `calvo`, `pelo_punta`; cabeza `gorra`, `gorra_policia`, `sombrero`, `gorro_chef`, `lazo`;
  cuerpo `bufanda`, `corbata`, `falda`, `vestido`, `bata`, `delantal`, `collar`, `baston`
- **sfx** (`assets/sfx/`): `pop`, `whoosh`, `boom`, `ding`, `boing`, `golpe`, `sorpresa`, `tictac`, `ronquido`, `triste`
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
