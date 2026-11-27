# story.json format

`scripts/build-video.ts` turns `story.json` + `words.json` into `final.json`. It validates everything and names the bad field when something is wrong.

## Top level
```json
{
  "audio": "audio/<name>.wav",
  "names": ["Nana"],
  "sfx": [],
  "endHoldFrames": 32,
  "shots": [ ... ]
}
```
- `audio`: path under `public/`, the file `mix_audio.py` wrote.
- `names`: words to capitalise in captions. `sfx`: spoken words to show in ALL CAPS.
- `soundWords`: captions that are shown but not spoken, each with a sound: `[{ "afterWord": 20, "text": "WHOOSH", "sound": "whoosh" }]`. The word appears in the pause after word 20. It needs a pause of about a second there, so write one into the script (a full stop and a new paragraph) and ask the narrator to leave it; the build warns if the pause is under half a second.
- `endHoldFrames`: silent picture after the last word (default 32 = 1.07 s).
- Frame size is 720 x 960 at 30 fps unless you add `"width"` and `"height"`.

## Words and cues
Count the script's words from 0, ignoring punctuation. `words.json` (from `align.py`) lists them in order with their times, so check your indices against it. A shot's `cue` is the index of its first word. The first shot must have `cue: 0`; cues must increase.

## A shot
```json
{
  "id": "3_nana",
  "cue": 9,
  "set": "kitchen",
  "setParams": { "chairs": [] },
  "look": "INTERIOR_NEUTRAL",
  "lookOverrides": { "fog": { "color": "#c4d2ec", "density": 0.003 } },
  "shadow": { "focus": [-4, 3, -3], "extent": 26 },
  "actors": [ ... ],
  "crowds": [ ... ],
  "vfx": [ ... ],
  "camera": { ... },
  "motionBlur": "auto"
}
```
| Field | Meaning |
|---|---|
| `cue` | index of the shot's first word. Or `cueSound: k` to start on the k-th entry of `soundWords` |
| `sound` | `"hit"` or `"whoosh"`: a sound effect on the shot's first frame |
| `sfx` | recorded sounds: a list of `{ "type", "word" or "at" (local frame), "dur": seconds or "shot" (makes it a looped background layer), "gain": dB, "lead": seconds }`. `lead` starts the sound that long before the named frame (risers). `type` is a file in `sfx/` (see the catalogue, section 7) |
| `set`, `setParams` | a set id and optional overrides of its defaults (see the catalogue) |
| `look`, `lookOverrides` | a look id; overrides replace whole top-level groups: `sky`, `fog`, `lights`, `post` |
| `shadow` | where the sun's shadow box sits (`focus` x, y, z) and its half-width in studs. Default: 14 studs around the first actor. Use a larger `extent` for wide shots (40 to 90) |
| `motionBlur` | `"auto"` (default: blurs frames where the camera moves fast), `"off"`, or frame ranges `[[0, 4]]` |

Units are **studs**: an avatar is 5.2 tall, 2 wide (4 with arms). Ground is y = 0. +X is screen-right when the camera looks along -Z.

## Actors
```json
{ "character": "pip", "pos": [-3.5, -2], "yaw": 25,
  "clips": [ { "clip": "pointUp", "word": 11 } ],
  "faces": [ { "f": 0, "v": "neutralTalk" }, { "word": 14, "v": "angryTalk" } ],
  "prop": "spear", "contactShadow": 0.7 }
```
- `character`: a key of `cast.json`. `pos`: [x, z] on the ground. `yaw`: degrees; 0 faces +Z (toward a camera that looks along -Z), 90 faces +X.
- `clips`: gestures. Start each on a `word` (index) or at a local frame `at` (may be negative to start before the shot, so the pose is already held). A later clip overrides the joints it moves.
- `faces`: expression swaps, on a `word` or at local frame `f`. Always give one at `f: 0`.
- `talk`: `true` or `[firstWord, lastWord]`: the mouth follows the spoken words. `look`: `[x, y]` pupil offset. `blink`: `false` to stop the automatic blinking.
- `to`: `[x, z]`: travel there over the whole shot; or `path`: `[{ "u" | "f" | "word", "pos": [x, z] }]`. Omit `yaw` to face the direction of travel. Use with a `walk` or `runLeaning` clip started before the shot (`"at": -100`).
- `prop`: `"spear"` (a pole with a small flag in the right hand; `propColor` sets the flag).

## Crowds
```json
{ "palette": "fire", "count": 60, "area": [-16, -80, -10, 6], "facing": 90, "cheer": 0.2, "spears": 0.3, "seed": 3 }
```
Every crowd member has a drawn face and blinks. Optional: `"mood"`: `calm` (default), `worried`, `panic`, `cheer`, `stunned`; `"walk"`: fraction that walk (0 to 1) along `"walkDir"` (degrees, default = `facing`), both ways with `"bothWays": true`, turning round at the ends of the rectangle; `"run": true`; `"speed"` in studs per frame.

`area` is a ground rectangle [x0, z0, x1, z1]. `palette`: `"fire"` (reds, yellows, black) or `"water"` (teals, blues, white, purple). `cheer` and `spears` are fractions of the crowd. Most members stand still; that is correct for the style.

## Camera
```json
{ "fov": 47,
  "keys": [ { "u": 0, "pos": [1.5, 4.2, 11], "target": [-3.2, 3.8, -2] },
            { "u": 1, "pos": [1.2, 4.2, 9.6], "target": [-3.2, 3.8, -2], "ease": "linear" } ],
  "shake": [ { "f0": 12, "f1": 60, "ampDeg": [0.04, 0.5], "mode": "alt", "bursts": 2 } ] }
```
- A key has a position and a look-at target. Time is `u` (0 to 1 = fraction of the shot) or `f` (local frames; negative values are allowed so a whip is already under way on the first frame).
- `ease` applies to the move that **ends** at that key: `linear`, `easeOutQuad`, `easeOutCubic`, `easeOutQuart`, `easeInQuad`, `easeInCubic`, `easeInQuart`, `easeInSine`, `easeOutSine`, `easeInOutSine`, `easeInOutQuad`.
- `fov`: 47 by default. Use 40 for calm interior shots.
- `shake`: local frames `f0` to `f1`, amplitude in degrees [horizontal, vertical]. `mode`: `"alt"` (flips every frame) or `"random"`. `decay` (0.72 to 0.75 per frame) for an impact; `bursts` for repeated pulses.
- Recipes for every move the style uses are in the catalogue.

## Effects
```json
{ "type": "embers", "count": 300, "box": [60, 30, 60], "centre": [0, 12, -14], "size": 0.16 }
```
Types and parameters are in the catalogue.

## Long stories
A 2-minute story is about 100 shots, too many to write by hand as JSON. Write `projects/<name>/make_story.py` that builds `story.json`:
- a dictionary of **scenes** (set, setParams, look, lookOverrides, shadow) so each place is defined once;
- helpers for **actors** (`A(character, x, z, yaw, face, faces, clips)`), **camera recipes** (`med`, `close`, `wide`, each with a push-in of 15 to 25 %, optional whip and shake) and **effects**;
- one line per shot: id, cue word, scene, actors, camera, effects, crowds, sound.
Effects take local frames, not word indices; convert with `round(words[i].t * 30) - round(words[cue].t * 30)`.
Run it, then `build-video.ts`. Fix staging by editing the script, never the generated JSON.

## Complete example
`projects/example/story.json` is a working six-shot story using two sets, three looks, gestures, face swaps, a whip pan and a shake.
