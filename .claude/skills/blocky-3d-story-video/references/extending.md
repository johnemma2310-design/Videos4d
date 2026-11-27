# Extending the engine

Only do this when the story truly needs something the catalogue lacks. Prefer staging the story in what exists.

## The one rule that cannot be broken
Every frame must be a pure function of its frame number. Frames are rendered out of order in several browser tabs, and motion blur draws the same frame at fractional times.
- No `Math.random`, `Date`, `performance.now` or anything that remembers the previous frame. Use `rng(seed)` and `hash01(n, seed)` from `src/engine/core/rng.ts`.
- Particles are computed from (frame, seed) in closed form; nothing is integrated step by step.
- If you use a library pass that calls `Math.random` when it is created, seed it (see how `post/pipeline.ts` handles the occlusion pass).

After any engine change, confirm it: render the same short range with `--concurrency=1` and `--concurrency=4` into two folders and compare the frames; they must be identical.

## Where things go
| To add | File | How |
|---|---|---|
| A gesture | `src/engine/anim/clips.ts` | `clips.add("name", { tracks: { "R.shoulderPitch": [{ f: 0, v: 0 }, { f: 3, v: 90, ease: "snap" }] } })`. Channels: `L.`/`R.` + `shoulderPitch` (0 down, 90 forward, 180 up), `shoulderRoll` (0 against the body, 90 straight out), `hipPitch`; `headYaw`, `headPitch`, `headRoll`, `torsoPitch`, `rootY`. Eases: `snap`, `backOut` (overshoots), `settle`, `sine`, `step`, `smooth`. Keep the style: 2 to 4 frames to reach a pose, then hold |
| An expression | `src/engine/avatar/faces.ts` | add an entry to `EXPRESSIONS` from the existing eye, brow and mouth parts, or add a new part to `drawFace` |
| A hair style or outfit pattern | `src/engine/avatar/hair.ts`, `outfits.ts`, and the lists in `src/schema/cast.ts` | hair is a few simple meshes on a head of radius 0.6 and height 1.2 |
| A look | `src/engine/looks/index.ts` | `looks.add("NAME", { sky, fog, lights, post })`. Tune it on a real shot before relying on it |
| A set | new file in `src/engine/sets/`, registered in `sets/index.ts` | a function `(scene, params, seed)` that adds static scenery; it may return effects it placed. Take sizes and colours from a params object with defaults. For stone, brick and ground use `rubbleMaterial`, `reliefMaterial` and `groundRelief` from `src/engine/tex/relief.ts` |
| An effect | `src/engine/vfx/index.ts` | `vfx.add("name", (params, seed) => ({ object, update(frame, camera) }))` |
| A prop | `src/engine/programs/reel.ts` (see the spear) and the `prop` list in `src/schema/shots.ts` | attach to `avatar.handAnchor("R")` |

## Scale and proportions (do not change)
Avatar: legs 1 x 2 x 1, torso 2 x 2 x 1, arms 1 x 2 x 1 hanging from the torso's top corners, head a rounded cylinder of radius 0.6 and height 1.2 with no neck; total 5.16 studs. Box edges are hard. No hands, elbows or knees. These were measured and are what makes the characters read correctly.

## Style facts worth keeping when you add things
- Characters do not move between poses: no breathing, swaying or bobbing.
- The camera is almost never still: a slow push-in on nearly every shot.
- No depth of field, vignette, film grain or lens flare.
- Glow only on things that are actually fire or very bright; ordinary lit windows do not glow.
- Motion blur is several sharp copies averaged, not a smooth smear.
