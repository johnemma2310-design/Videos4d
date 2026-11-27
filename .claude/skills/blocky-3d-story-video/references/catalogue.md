# Catalogue: what the engine has

Contents: 1. Characters · 2. Expressions · 3. Gestures (clips) · 4. Sets · 5. Looks · 6. Effects · 7. Sound · 8. Camera recipes

Units are studs (an avatar is 5.2 tall). Colours are `#rrggbb`.

## 1. Characters (`cast.json`)
```json
{
  "pip": { "skin": "#d9a27a",
           "hair": { "style": "bun", "color": "#2a6f6a" },
           "outfit": { "torso": { "kind": "plain", "color": "#f2c230" },
                       "sleeves": { "color": "#f2c230", "length": 1, "cuff": "#2b3a67" },
                       "legs": { "color": "#2b3a67", "length": 1, "shoes": "#141826" } } }
}
```
Keys are lowercase names you choose; shots refer to them.

| Part | Options |
|---|---|
| `hair.style` | `sidePart`, `bob`, `long`, `ponytail`, `tufts`, `bun`, `curly`, `spikyTop`, `bald`, `beanie`, `rainHat` (a domed hat with a wide brim) (`color` is the hair or hat colour) |
| `torso.kind` | `plain` {color} · `stripes` {color, color2, bands} · `plaid` {color, color2} · `varsity` {color, strip, trim}: an open jacket over a shirt, `strip` is the shirt colour · `coat` {color, trim}: a buttoned, belted coat with collar and pockets, `trim` = buttons and buckle |
| `sleeves` | `color`; `length` 0 to 1 (0.4 = short sleeves, rest is skin); `cuff` = a striped cuff colour. Omit for sleeves matching the torso |
| `legs` | `color`; `length` below 1 = shorts; `shoes` |

Design notes: avatars are flat-coloured and matte, with no hands, neck, elbows or knees. Identity comes from outfit colour and hair shape, because the faces are too simple to tell people apart. Give the main character a colour nobody else wears, and check it against both the day and night looks (warm night light turns yellow to orange).

## 2. Expressions (`faces`)
Faces are flat drawings that swap instantly, with soft shading on the head (under the hair, at the sides, under the chin), blush and an eye highlight. Swap on the word that motivates the change.

On top of the expression, per actor:
- `"talk": true` (every word of the shot) or `[firstWord, lastWord]`: the mouth opens and closes with each spoken word, with a small nod. Give it to whoever is saying the line on screen. It leaves screaming and gritted mouths alone.
- blinking is automatic (three frames every 2.5 to 4 seconds, each character on their own rhythm); `"blink": false` turns it off.
- `"look": [x, y]`: where the pupils point, about -0.05 to 0.05 (`[0, -0.05]` = up, `[-0.05, 0]` = to the viewer's left).
No actor should keep one expression for more than about a second: add a second `faces` entry half-way through any longer shot.

| Name | Looks like | Use for |
|---|---|---|
| `neutralTalk` | round eyes, small open mouth | default while narrating |
| `bigHappy` | round eyes, big open grin | delight |
| `laugh` | eyes shut in wavy lines, big grin | laughing |
| `happyArcs` | eyes as upward arcs, small smile | content, background characters |
| `dotSmile` | small dot eyes, wide smile | gentle, parental |
| `smug` | half-closed eyes, one raised brow, smirk | "here's the weird part", self-aware jokes |
| `angryTalk` | slanted brows, open mouth | stating a rule |
| `angryFrown` | slanted brows, frown | disapproval |
| `grittedAngry` | slanted brows, bared teeth | rage |
| `hollowShock` | solid black eyes with a white dot, tight mouth | dread, the bad news |
| `scream` | huge open mouth with teeth | panic |
| `worried` | brows up in the middle, small frown, eyes aside | unease |
| `nervous` | worried brows, zig-zag mouth | the cliffhanger |
| `disgust` | eyes as outward chevrons, tiny mouth | "gross" |
| `deadpan` | eyes as flat lines, small wavy mouth | flat punchline |
| `blank` | round eyes, tiny dash mouth | stunned |
| `eyesClosedTalk`, `mouthSmall` | in-between talking faces | alternate with `neutralTalk` every 3 to 4 frames for a talking effect |

Preview: `npx tsx scripts/sheet-props.ts projects/<name> sheet.faces` then render `FaceSheet`.

## 3. Gestures (`clips`)
Poses snap into place in 2 to 4 frames and then hold. Start one on a word.

| Clip | What it does |
|---|---|
| `rest` | arms down |
| `shrugOut` | both arms out to the sides with a small overshoot, then held |
| `handUpQuick` | right arm snaps up and forward |
| `pointUp` | right arm up high for about 15 frames, then down |
| `armsUp` | both arms up, held (panic, cheering) |
| `wave` | right arm up and waving for two cycles, then down |
| `reachForward` | right arm held forward and down |
| `presentPlate` | right arm lifts slowly to horizontal |
| `castForward` | right arm swings forward, body leans back slightly (throwing an effect) |
| `castUpBoth` | both arms up and slightly out |
| `cheerLoop` | looping arms-up cheer with a small bounce |
| `walk` | looping walk in place (leg angles are estimates) |
| `runLeaning` | looping run in place, body leaning forward, arms back |

`walk` and `runLeaning` are leg and arm cycles. To make the character really travel, give the actor `"to": [x, z]` (walk there over the whole shot) or `"path": [{ "u" | "f" | "word", "pos": [x, z] }]`. The steps then follow the distance covered (natural speeds: walk about 0.23 studs per frame, run about 0.46), and the character faces the way they go unless `yaw` is given. Move the camera with them (same change of position and target), and keep crowds out of their lane. Preview all clips: render `ClipSheet`.

## 4. Sets
| Set id | What it is | Good for | Looks it has been tuned with |
|---|---|---|---|
| `tabletPlaza` | gravel yard in front of a long dark rock wall; a pale town with domes beyond; a tall sign board and a fire bowl on the wall | talking shots, the "rule" moment | `DAY_COOL` |
| `fireStreet` | cobbled street, a row of slate-stone houses with red roofs on the left, raised pavement, flaming fire bowls along the kerb | town life, crowds, dusk and night | `DAY_SUN` |
| `waterStreet` | the same street in pale plaster with blue-grey roofs, no fire bowls | the rival town | untuned |
| `kitchen` | brick room with a tile band, window, plank table and plastic chairs; open toward the camera | home, family scenes | `INTERIOR_NEUTRAL` with brighter fill (see below) |
| `nightField` | bare straw-strewn ground with a row of houses on the horizon | the big event, battles, crowds at night | `NIGHT_EMBER` |
| `aerialKingdoms` | bird's-eye map: a canal between a blue-roofed town (left) and a red-roofed town (right), plains, landmarks, smoke | the opening establishing shot | `DAY_SUN` |
| `fireCourtyard` | castle courtyard in dark red stone: high wall with a barred gate and battlements, corner towers, red carpet, red banners, torches | ceremonies, crowds, announcements | seen under `FIRE_WARM` only; not scored |
| `waterCourtyard` | the same courtyard in pale stone with teal carpet and banners, no torches | the rival town's ceremonies | seen under `PEACH_HIGHKEY` only; not scored |
| `volcano` | a huge ridged cone with glowing cracks over a plain, small houses at its foot; can erupt | the looming threat, the final image | seen under `DAY_SUN` and `NIGHT_EMBER`; not scored |

Useful `setParams`:
- `fireStreet` / `waterStreet`: `{ "flames": false }` puts the bowls out; `houses`: `{ "lit": 0 to 1 }` fraction of lit windows, `"sides": ["left", "right"]`, `"rightX"`, `"rightZ0"` for a far row, `"height"`, `"wall"`, `"roofColor"`; `ground`: `{ "stone", "stoneDark", "gap" }`; `"bowls": null` removes them. The kerb is at x = -9.5, houses start at x = -17, bowls stand at x = -7.6 every 16 studs from z = -4. The open street is x > -9.5.
- `kitchen`: `"chairs": []` (or a list of `{x, z, yaw}`), `"table": null` or `{x, z, yaw, length, width, height}`, `window`: `{z, width, y0, y1}`, wall and floor colours. Room: x from -15 to 15, back wall at z = -11, window in the left wall. Stand actors around (-4, -3) and put the camera near (9, 4.5, 2.5).
- `nightField`: `houses`: `{ "z", "count", "lit", "wall", "roof", "height" }`, `ground`: `{ "dark", "light" }`.
- `tabletPlaza`: the wall is at z = -29; stand actors near the origin and put the camera on +Z.
- `fireCourtyard` / `waterCourtyard`: the wall is at z = -22 (`wallZ`), 20 high, 70 wide; the carpet runs along x = 0 toward the camera. Stand actors near the origin, crowds either side of the carpet. `"carpet": null` removes it; `"torches": false`; colours: `stone`, `stoneDark`, `floor`, `banner`, `emblem`, `roof`. Use `"shadow": { "focus": [0, 0, -8], "extent": 50 }`.
- `volcano`: the cone's base centre is 260 studs away (`distance`), 170 high. `"erupt": true` adds a fire column, flying embers, lava bombs and dark smoke; `"lavaGlow"` (1.6; use 3 at night) brightens the cracks; `"houses": null` removes the houses or `{ "lit": 0 to 1 }` lights their windows. Put the camera near the origin looking up at about [0, 60, -240]; an actor at the origin with `yaw: 180` is seen from behind, looking at it. Use `"shadow": { "focus": [0, 0, -200], "extent": 260 }` by day.
- `aerialKingdoms`: camera about 180 studs up looking down the canal (-Z); use `"shadow": { "focus": [0, 0, -600], "extent": 700 }`. No actors (they would be invisible at that height).

## 5. Looks
| Look | Mood | Status |
|---|---|---|
| `DAY_COOL` | soft cool daylight, pale sky, light haze | calibrated |
| `DAY_SUN` | hard warm sun, blue sky with clouds, thin haze | calibrated (add `"fog": {"color": "#c4d2ec", "density": 0.0028}` for street-level haze) |
| `NIGHT_EMBER` | maroon night sky, warm light from the camera side, strong glow on fire | calibrated |
| `DUSK_MAGENTA` | pink-violet dusk | starting values; reads about right |
| `RAIN_OVERCAST` | grey, shadowless, dense fog; add the `rain` effect | starting values; reads about right |
| `FIRE_WARM` | warm orange day | starting values; too bright |
| `PEACH_HIGHKEY` | pale warm daylight, soft | retuned once; colour balance matches the reference, still darker than it |
| `INTERIOR_NEUTRAL` | indoor daylight | starting values; too dark as is. Use this override: `"lookOverrides": { "lights": { "hemi": { "sky": "#e6ddd2", "ground": "#8a7a6a", "intensity": 1.9 }, "key": { "color": "#fff0dc", "intensity": 1.8, "from": [0.5, 0.8, 0.7], "shadow": true } } }` |

The arc that suits this style: bright day for the set-up, dusk for the turn, night for the big event.
A `lookOverrides` group replaces the whole group. `lights` = `{ hemi: {sky, ground, intensity}, key: {color, intensity, from: [x, y, z], shadow} }` where `from` is the direction the light comes from; put it on the camera's side or faces go dark. `fog` = `{color, density}`. `post.bloom` = `{strength, radius, threshold}`.

## 6. Effects (`vfx`)
All positions are in studs.

| Type | Main parameters (defaults) | Notes |
|---|---|---|
| `embers` | `count` (450), `box` [w, h, d] (60, 30, 60), `centre` [x, y, z], `size` (0.34), `gain` (2.2), `rise`, `wind` | rising sparks. Use `size` 0.15 when they are far from the camera, 0.34 when some drift close to the lens |
| `flame` | `pos`, `size` (1.2), `light` (9) | a fire: torch, bowl, hand |
| `jet` | `from`, `dir`, `length` (10), `start` (local frame it ignites) | flame thrown from a hand; pair with the `castForward` clip and start it about 10 frames after the clip |
| `fireballs` | `count` (6), `from`, `velocity` per frame, `spread`, `size` (3.2), `every` (frames between launches) | glowing balls with trails crossing the sky; keep them 40+ studs from the camera |
| `rain` | `count` (3200), `box`, `centre`, `length`, `opacity` | streaks, different every frame; keep the box a few studs in front of the camera, not around it |
| `steam` | `pos`, `count`, `spread`, `rise`, `size`, `color`, `opacity` | slow rising puffs (also smoke) |
| `cloud` | `pos` [x, y, z], `size` (3.0 = pillow over one head at y 7.3; 15 = barn-sized at y 11.5), `dark` 0 to 1, `rain` (0 = none, 0.5, 1.2 = heavy), `appear`, `pour`, `vanish` (local frames), `glow` (0.22 at night) | a personal rain cloud: pops in at `appear`, rains under itself, pours hard from `pour`, shrinks away from `vanish`. To show it with a face clear of the caption: camera target y 4.1, distance 12.5 |
| any effect | `"follow": <index of an actor in the shot>`, `"lag": frames`: the effect travels with that actor, trailing by `lag` frames (a cloud over a walker: lag 6 to 8) |
| `props` | `items`: list of `{ shape: "box" or "cyl", pos (centre), size [w, h, d] or [radius, height], color, rotX, rotY, rotZ, glow }` | plain matte blocks for things the sets lack: a well, a boat, a cart, a dish on a table, something held out. They read as toys; keep them small in frame or in the background |
| `water` | `pos`, `size` [w, length], `deep`, `light`, `line`, `lineAmount`, `foam`, `glint`, `glintGain` | a flat water surface with drifting ripple lines. Day defaults are milky turquoise; night: `"deep": "#0f4a34", "light": "#2f8a58", "line": "#9fe0b8", "lineAmount": 0.38` |

## 7. Sound
| What | How |
|---|---|
| A low hit on a cut | `"sound": "hit"` on the shot. Use on reveals and impacts, about one cut in three |
| A whoosh on a cut | `"sound": "whoosh"` on the shot |
| A sound word (shown, not spoken) | `soundWords` at the top of `story.json`; a shot can start on it with `cueSound` |

| A recorded sound on an event | `"sfx": [{ "type": "pop", "word": 11 }]` on the shot (or `"at"`: local frame). The file is `sfx/pop.wav` |
| A background layer for a shot | `"sfx": [{ "type": "rain_light", "dur": "shot", "gain": -9 }]`: looped for the shot, in step with the video's clock so it runs on unbroken across cuts |

| A riser that ends on a cut | `"sfx": [{ "type": "riser", "at": 0, "lead": 1.84 }]` on the shot AFTER the build: `lead` starts the sound that many seconds early, so a riser as long as its lead peaks on the cut |

**`sfx/usage.md` is the guide to the library**: every sound, its length, what it is and where the user wants it. The user's own pack: `pop_soft_in`, `pop_soft`, `pop_b`, `pop_c`, `bell_pop`, `click`, `whoosh_air`, `whoosh_quick`, `whoosh_short`, `riser` (1.84 s), `riser_burst` (2.31 s), `riser_fear` (7.15 s), `transition`, `camera_shutter`, `clock_tick`, `loading_soft`, `loading_anim`, `money`. Alternate the pops and the whooshes; never the same one twice running.

The hit and whoosh are synthesised. Recordings come from `scripts/sfx_fetch.py` (public-domain clips found through the Openverse API; each one is listed in `sfx/credits.json`). The library in `sfx/` is shared by all videos in the studio, so fetch a sound once. Useful set: `pop`, `drip`, `splash`, `thunder`, `hiss`, `rain_light`, `rain_heavy`, `fire`, `crowd_panic`, `crowd_cheer`. Default levels: events peak a little under the voice; layers sit 16 dB under it; `gain` shifts that in dB. Everything stops with the voice at the last spoken word.

## 8. Camera recipes
Every recipe is two or three keys. `H` = the subject's head position, about [x, 4.3, z] for a standing avatar.

| Move | Keys | Use for |
|---|---|---|
| Creep-in (the default) | same target; position moves 8 to 15 % closer over the shot, `linear` | almost every shot |
| Medium shot | camera 10 to 13 studs from the subject, height 4 to 4.5, target at chest (y 3.6 to 4) | narrator |
| Close-up | camera 5 to 7 studs away, target at y 4.3 | reactions, punchlines |
| Wide | camera 25 to 35 studs away, height 7 to 10 | groups, places |
| Pull-back reveal | start close, end 3 to 7 times further and higher at `u` 0.45 with `easeOutQuad`, then a slow drift to `u` 1 | revealing a place or a crowd |
| Whip-in | first key at `f: -1` with the target 6 to 10 studs to one side; second key at `f: 4` on the subject with `easeOutCubic`; then a creep to `u: 1` | arriving on a new subject fast |
| Whip-out | add a key at `u: 0.93` holding the framing, then a last key at `u: 1.07` with the target swung 8 to 10 studs sideways, `easeInQuart` (the shot ends mid-swing) | leaving fast (pair with a whip-in on the next shot) |
| Orbit | same target, position rotated 15 to 25 degrees around it, `easeInQuad` | interior dialogue |
| Impact shake | `{ "f0": N, "f1": N+10, "ampDeg": [0.5, 0.5], "mode": "alt", "decay": 0.75 }` | something hits |
| Rumble | `{ "f0": N, "f1": N+50, "ampDeg": [0.04, 0.5], "mode": "alt", "bursts": 2 }` | explosions overhead |
| Dread tremble | `{ "f0": N, "f1": N+25, "ampDeg": [0.25, 0.35], "mode": "random" }` | the last shot |

Measured framings that work: a **close-up** needs target y 4.6 to 4.8 and distance 7.5 to 8.5 (closer or lower fills the frame with torso and crops the head); a **medium** is target y 3.9 to 4.1 at 11.5 to 12.5. Keep night `flame` sizes at 3 or less, or they bloom into white discs.

Framing rule: the caption baseline is at 71 % of the frame height. Aim the camera so faces sit between 30 % and 45 % from the top; in two-person shots keep the centre clear.
