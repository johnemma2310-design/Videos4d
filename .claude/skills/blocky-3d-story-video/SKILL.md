---
name: blocky-3d-story-video
description: Full production pipeline for narrated, captioned story shorts with blocky toy avatars in a lit 3D world, rendered entirely in code (Three.js + Remotion, no AI image or video generators). Runs in approved stages - titles, script, voice-over, character sheets, beat table and storyboard, render, then a quality review scored against the target video, with lessons carried into the next video. Use this whenever the user wants title ideas, a script, character sheets, a storyboard or a finished MP4 for a blocky-avatar or Roblox-style story video, says "make a video", "next video", "new titles" in this studio, uploads a voice-over for one, or asks for a quality check or score of a rendered video, even if they don't name the style.
---

# Blocky 3D story video — production pipeline

Makes a portrait story short in a specific, measured style: rigid block characters with flat drawn faces, a textured hazy 3D town, one white word on screen at a time, a new shot on almost every sentence, and a story built on the measured shape of the user's 10 sample scripts. A code engine renders everything; you author **data files**, not code.

Make **original** stories, characters and worlds in this style. Never re-create the target video's or the samples' story, characters or designs.

## The studio
One persistent working folder holds the engine, every video's project and the lessons learned. Find it before anything else:
- If the user has a studio (a folder with `lab/lessons.md` and `projects/`), use it. **Never copy the template over an existing studio**: it holds tuned presets and lessons.
- If not, create one: copy `template/` to a folder the user names (default `blocky-studio` in the working directory), then run the setup in `references/troubleshooting.md` ("First-time setup").

At the start of every session in the studio, read `lab/lessons.md`. It overrides the defaults in this skill where they differ.

## The pipeline
Nine stages. **Stop at every gate marked ✋ and wait for the user's approval.** Do not run ahead: each later stage depends on what was approved. If the user changes something after a gate, redo the stages after it.

| # | Stage | You produce | Gate |
|---|---|---|---|
| 1 | Titles | 10 titles with premises | ✋ user picks one |
| 2 | Script | the script, checked against the samples | ✋ approve |
| 3 | Voice-over | a checked recording | ✋ approve |
| 4 | Characters | cast and character sheets, compared with the target | ✋ approve |
| 5 | Beats and storyboard | beat table and storyboard, compared with the target | ✋ approve |
| 6 | Project file | the render-ready project | ✋ user says "render" |
| 7 | Render | the MP4 | — |
| 8 | Quality review | score and report | — |
| 9 | Learn | lessons for the next video | — |

### 1. Titles ✋
Read `references/title-script-style.md` (the analysis of the user's 10 sample videos) and `references/titles-and-scripts.md`. Offer 10 numbered titles in the measured title shapes, each with its one-line world, the narrator's trait and the sets it would use. None may reuse a sample's world, power or names. Wait for the choice.

### 2. Script ✋
Create the project by copying `projects/example/`. Plan the 12 story parts and every plant and pay-off, then write the script to the sample length (world story 370 to 435 words, about 2 minutes, unless the user asks for another length) into `projects/<name>/script.txt`. Run `.venv/Scripts/python scripts/script_check.py projects/<name>/script.txt` and fix every `CHECK` line: it compares the draft with the samples' numbers and structure and fails on any five-word run copied from them. Show the script, the checker's table and one line on what makes the story new.

### 3. Voice-over ✋
Ask the user to record the approved script and give you the file. Save it as `projects/<name>/audio/narration.wav`, then:
```
.venv/Scripts/python scripts/align.py projects/<name>/audio/narration.wav projects/<name>/script.txt projects/<name>/words.json
.venv/Scripts/python scripts/voice_check.py projects/<name>/audio/narration.wav projects/<name>/words.json
```
Report the result in plain words: pace against the 188 words per minute target, pauses, any words the aligner could not hear, clipping or noise. The user decides whether to re-record. Never substitute a synthetic voice unless the user asks for a test.

- **Pauses too long** (median well over 0.36 s) is the usual fault of generated voices. Offer to shorten them: keep the original, run `scripts/tighten_pauses.py <in.wav> words.json <out.wav>` (it removes only silence), run `align.py` and `voice_check.py` again, and send the new file for the user to hear before approval.
- **If the user asks for a voice description** to design a similar voice in a text-to-speech service, read `references/voice.md`. Do not generate the voice yourself unless asked; it costs the user credits.

### 4. Characters ✋
Re-read the approved script and list every character and crowd it needs, with what each must show (who is the narrator, who belongs to which side, who appears at night). Write `projects/<name>/cast.json` (options in `references/catalogue.md`), then render the sheets:
```
npx tsx scripts/sheet-props.ts projects/<name> sheet.cast
npx remotion still src/index.ts CastSheet out/<name>_cast.png --props=projects/<name>/sheet.json --gl=angle
npx tsx scripts/sheet-props.ts projects/<name> sheet.faces
npx remotion still src/index.ts FaceSheet out/<name>_faces.png --props=projects/<name>/sheet.json --gl=angle
```
The cast sheet shows about five characters in a row; with more, write two `sheet.json` files (main cast, supporting cast) and render two sheets, or the back row is hidden. Before showing them, compare them with the target's characters using the checklist in `references/qa-and-learning.md` (section 1) and fix what fails: in particular, no character may wear the target hero's outfit (red jacket, white sleeves, brown trousers), and no two characters may share a colour once the warm night light is on them (yellow turns orange). Show the user the sheets with one line per character.

Also list what the script needs that the engine does not have (a prop, an effect, a set). Small things are data: the `props` effect makes boxes and cylinders, and `cloud` makes a personal rain cloud (`references/catalogue.md`). Anything bigger is engine work (`references/extending.md`): say so before the storyboard, not after.

### 5. Beats and storyboard ✋
Three rules the user set after watching the first video; they apply to every shot:
- **Faces are alive.** Nobody holds one frozen expression: the speaker's mouth follows the words (`talk`), everyone blinks (automatic), expressions change on the word that motivates them, eyes look at things (`look`), and crowds have faces with a `mood` that fits the beat.
- **Movement is real.** Anyone who walks or runs travels across the ground (`to` / `path`), what belongs to them travels with them (`follow` on the effect), and the camera moves with them. Street crowds walk (`walk`).
- **No flat side-on staging with furniture between characters.** Use an over-the-shoulder shot, then a close-up, then a front two-shot with the table low in the frame.

A storyboard shows one frame per shot, so it cannot show any of this. For every shot with travel, a tracking camera or a restaged scene, also render stills at about 15 % and 85 % of the shot from `final.json` and check both.

Write `projects/<name>/story.json` (`references/story-format.md`, `references/catalogue.md`), applying every open lesson. Then:
```
npx tsx scripts/build-video.ts projects/<name>
npx tsx scripts/storyboard.ts projects/<name>
npx remotion render src/index.ts Final out/<name>_board --props=projects/<name>/storyboard.json --sequence --image-format=jpeg --gl=angle --concurrency=1 --timeout=180000
.venv/Scripts/python scripts/board_sheet.py projects/<name> out/<name>_board out/<name>_storyboard.jpg
.venv/Scripts/python scripts/qa_score.py frames out/<name>_board lab/target/profile.json
```
For a story of more than about 30 shots, write the shots with a small generator script (helpers for scenes, camera recipes and actors; see `references/story-format.md`, "Long stories") and render the storyboard in batches of about 17 frames (`--frames=0-16`, `--frames=17-33`, ...), then rename the files to three-digit numbers before building the sheet (`references/troubleshooting.md`).

This gives the beat table (`projects/<name>/beats.md`), a storyboard sheet with one frame per shot, and colour and detail scores for it. Compare the sheet with the target as described in `references/qa-and-learning.md` (section 2). Fix `story.json` and repeat until you would approve it yourself. Then show the user the storyboard sheet, the beat table and the scores, and say what you changed after comparing.

### 6. Project file ✋
**Sound effects first.** The hit and whoosh alone are too few. Read `sfx/usage.md`: it lists every sound in the studio's library and where the user wants each one used. Two kinds work together:
- **the user's pack** (pops, clicks, whooshes, risers, a transition, a shutter, ticking, loading, money): the punctuation of the edit. Use them through the whole video, following the user's own instructions in that file;
- **story-world sounds** (rain, fire, thunder, crowds and whatever this story shows): if the library lacks one, list it in `projects/<name>/sfx_wanted.json` (start from `sfx/wanted_world.json`) and, **after the user agrees to the download**, fetch public-domain recordings:
```
.venv/Scripts/python scripts/sfx_fetch.py projects/<name>/sfx_wanted.json sfx
```
Read the names it kept: reject imitations and wrong sounds and fetch again with a better query (`--redo name`). Place the sounds with each shot's `sfx` list (`references/story-format.md`), preferably by rule from what is on screen (rain effect → rain layer, flames → fire layer, something appearing → its sound), then run `build-video.ts` again and mix:
```
.venv/Scripts/python scripts/mix_audio.py projects/<name>/audio/narration.wav projects/<name>/words.json public/audio/<name>.wav --sounds projects/<name>/sounds.json --sfx-dir sfx [--music music.wav]
```
**Music.** If the user gives a music file, pass it with `--music`; if they give a video, take only its audio first (`ffmpeg -i <video> -vn -ac 1 -ar 48000 projects/<name>/audio/music.wav`). It is looped or cut to length and placed 7 dB under the voice. Tell the user that the right to use the track in a published video is theirs to check. Without a file, a plain synthesised pad is used.

If the user gives a recording that holds many sounds, split it into numbered clips with `scripts/sfx_split.py <file> sfx/<pack>`, build them a page to play (the page must embed the audio; the app's file viewer does not play sound, so open it in their browser), and ask them to label the ones worth keeping. You cannot hear them: never guess what a sound is. Add their picks with `scripts/sfx_adopt.py`, which also rewrites `sfx/usage.md`.

You cannot hear the mix. Tell the user which sounds are where and ask them to listen. To change only the sound of a finished video, re-mix and attach it without re-rendering: `ffmpeg -i out/<name>.mp4 -i public/audio/<name>.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k out/<name>_sfx.mp4`.
The project is now render-ready (`projects/<name>/final.json` + the mixed audio). Tell the user it is ready, how long the render will take (about 10 seconds of start-up plus roughly 0.15 seconds per frame), and **ask them to tell you to render on this computer**. Give them the command too, in case they want to run it themselves:
```
npx remotion render src/index.ts Final out/<name>.mp4 --props=projects/<name>/final.json --gl=angle --crf=16 --concurrency=2 --timeout=180000
```

### 7. Render
Run the command when the user says so. Use relative paths and always `--gl=angle`.

### 8. Quality review
Follow `references/qa-and-learning.md` (section 3): timing check, measured score against the target profile, then a visual review with fresh eyes (a sub-agent if you can start one), then `qa_score.py log`. Report to the user: the final score, the previous videos' scores, the weakest categories with their numbers, and the frames you looked at. If the log prints **GOAL REACHED** (85 or more), say so first: the user asked to be reminded so the self-improving loop can be switched off.

### 9. Learn
While `lab/config.json` has `"self_improve": true`: write `lab/reports/<name>.md`, update `lab/lessons.md`, and build wrong defaults into the studio's engine as described in `references/qa-and-learning.md`. Tell the user what will be done differently next time.

## Rules that hold at every stage
- Characters hold still between gestures; the camera supplies the life with a push-in on nearly every shot.
- Faces swap on the word that motivates them; gestures start on a word.
- The caption baseline is at 71 % of the frame height: keep faces in the upper 45 %.
- Only two transitions exist: a hard cut and a whip pan.
- Every claim you make to the user about quality comes from a file you rendered and looked at, or a number a script printed. If a check was skipped, say so.

## What this skill cannot do
- 9 sets and 8 lighting looks exist (`references/catalogue.md`); a story has to be staged in those or the engine extended (`references/extending.md`).
- Three looks are calibrated against the target; the others may need per-shot `lookOverrides`.
- The narration is recorded by the user. Sound effects are two synthesised sounds (a low hit and a whoosh).
- The score measures style statistics plus a visual review. It is evidence, not proof of likeness.

## Reference files
| File | Read it when |
|---|---|
| `references/title-script-style.md` | stages 1 and 2: the measured style of the 10 samples |
| `references/titles-and-scripts.md` | stages 1 and 2: procedure |
| `references/script-rules.md` | stage 2 |
| `references/voice.md` | stage 3, when the user wants a voice description |
| `references/long-story-example.py` | stage 5: a complete generator for a 102-shot story (scenes, camera helpers, live faces, walking, crowds, sounds). Copy its helpers, not its story |
| `references/catalogue.md` | stages 4 and 5: characters, expressions, gestures, sets, looks, effects, sound, camera recipes |
| `references/story-format.md` | stage 5 |
| `references/qa-and-learning.md` | stages 4, 5, 8 and 9 |
| `references/troubleshooting.md` | first-time setup; a command fails; a shot looks wrong |
| `references/extending.md` | the story needs something the engine lacks; building a lesson into the engine |
