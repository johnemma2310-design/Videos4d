# Troubleshooting

## First-time setup (once per studio)
Run from the studio folder:
```
npm install
npm install-scripts approve esbuild        # only if npm reports esbuild's install script was not run
npm rebuild esbuild
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt     # on macOS/Linux: .venv/bin/python
```
- The first render downloads a headless browser (about 130 MB) and the first alignment downloads a speech model. Let both finish.
- Ask the user for the path of the target video on this computer and build the comparison sheet (`references/qa-and-learning.md`, "Once per studio").
- The style of the user's 10 sample titles and scripts is already in `references/title-script-style.md`, and `lab/samples_ngrams.json` holds the fingerprints for the copy check. Only ask for samples if the user wants to add new ones.
- Check the install by making the example: run stages 5 to 8 of the pipeline on `projects/example` with a test voice (`scripts/tts_test.ps1 -Script projects/example/script.txt -Out projects/example/audio/narration.wav` on Windows). Tell the user it is a robotic stand-in.

## Setup and rendering
| Symptom | Cause and fix |
|---|---|
| `npm install` warns that esbuild's install script was not run, then renders fail to bundle | `npm install-scripts approve esbuild` then `npm rebuild esbuild` |
| First render seems to hang | it is downloading the headless browser (about 130 MB). Let it finish; do not cut its output short |
| A warning about the zod version | harmless; the build uses zod 3 |
| Render fails with a path error | the project path has spaces: use relative paths for `--props` and the output |
| Blank or black frames | always pass `--gl=angle`. Check the log for "SOFTWARE RENDERER": that means no GPU is being used |
| Renders suddenly take 3 to 4 times longer | leftover `chrome-headless-shell` processes from an interrupted render. End them and try again |
| Python cannot import `cv2` or `faster_whisper` | run the scripts with the project's `.venv` python, after `pip install -r requirements.txt` |
| `align.py` is slow the first time | it downloads the speech model once |

## Long videos and storyboards
| Symptom | Cause and fix |
|---|---|
| A storyboard or render stops with `TimeoutError: waiting for the page to render` | A frame took longer than the time limit to build its scene. Add `--timeout=180000`. For storyboards also use `--concurrency=1` and render in batches of about 17 frames with `--frames=a-b`, each batch in its own command |
| Storyboard frames appear in the wrong order on the sheet | Batches whose frame numbers are below 100 are saved as `element-38.jpeg`, later ones as `element-086.jpeg`. Rename all to three digits before running `board_sheet.py` |
| The `reel` composition ignores `--props` | Stills and renders of a project use the `Final` composition with `final.json` or `storyboard.json`; in these files camera keys use `f` (frames), not `u` |

## Sound effects
| Symptom | Cause and fix |
|---|---|
| `sound "x" is not built in and sfx/x.wav does not exist` | Fetch it with `sfx_fetch.py`, or fix the name |
| `NO usable CC0 result` | Shorten the query to two plain words ("steam hiss"), or widen `min`/`max` seconds |
| A kept clip is an imitation or the wrong thing (its title says mouth, voice, synth) | Add words to `"avoid"` in the wanted file and run again with `--redo name` |
| The voice got quieter after adding sounds | It should not: loud effects are squashed, not the mix. Check the `gain` values; keep layers at 0 or below |
| `sfx_fetch.py` is slow | Some source files are long. It downloads up to five candidates per sound; let it finish, the library is reused afterwards |

## Build errors (`build-video.ts`)
| Message | Fix |
|---|---|
| `unknown set / look / clip / vfx "x". Known: ...` | use one of the listed ids (see the catalogue) |
| `unknown expression "x"` | use a name from the expressions table |
| `character "x" is not in cast.json` | add the character or fix the name |
| `word index N out of range` | the script has fewer words than you counted; check `words.json` |
| `cue N must come after the previous shot's cue` | cues must increase |
| `only N frames long` | two cues are on words spoken almost together; merge the shots or move a cue |

## The picture looks wrong (check the contact sheet)
| Fault | Fix |
|---|---|
| Something stands between camera and character (chair, table, fire bowl, wall) | move the actor or camera, or remove the prop with `setParams` (kitchen: `"chairs": []`, `"table": null`) |
| Character dark or silhouetted | the key light is behind them. In `lookOverrides.lights.key.from`, point the light from the camera's side |
| Character tiny or cut off | recompute the camera: a medium shot is 10 to 13 studs from the subject with the target at chest height |
| Face hidden by the caption | the face is too low in frame; raise the target's y or lower the camera |
| Window, sky or fire blows out to white | lower `post.bloom.strength`, raise `post.bloom.threshold`, or lower the effect's `gain` |
| Embers look like big blobs | `size` 0.15 for distant embers |
| Whole frame smeared | a camera key jumps too far in one frame. Smear is intended only on whip pans and shakes; set `"motionBlur": "off"` to check |
| Shadows missing or cut off in a wide shot | add `"shadow": { "focus": [x, 0, z], "extent": 60 }` around the action |
| A running character looks fallen over | `runLeaning` leans the body 28 degrees; seen from the side with a strong yaw it reads badly. Use `walk`, or face the runner more toward or away from the camera |
| Yellow outfit turns orange at night | expected under warm light. Pick the hero colour with that in mind, or lower the key light's warmth |

## Timing
| Fault | Fix |
|---|---|
| Captions drift from the voice | re-run `align.py`; check its list of words it could not hear |
| `verify_final.py` reports a cut 1 to 2 frames late | normal for a shot that opens inside a whip pan |
| No sound effects in the video | run `build-video.ts` before `mix_audio.py`, and pass `--sounds projects/<name>/sounds.json` |
| The build warns that a pause is too short for a sound word | the narrator needs to leave about a second of silence there; re-record, or drop the sound word |
