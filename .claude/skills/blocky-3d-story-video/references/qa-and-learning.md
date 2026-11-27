# Quality assurance and the self-improving loop

The goal the user set: every video should come out closer to the target video. When a video's final score reaches
**85 or more, remind the user**, because they then want to switch this loop off and simply use the skill.

Everything here lives in the studio's `lab/` folder, which persists between videos:

| File | What it holds |
|---|---|
| `lab/target/profile.json` | the target video's measured style (statistics only; shipped with the skill) |
| `lab/target/target_sheet.jpg` | the target's frames, two per second. Built locally (see below); never shipped or published |
| `lab/lessons.md` | what to do differently, from earlier videos. Read it before every stage |
| `lab/scores.csv` | one row per finished video |
| `lab/reports/<name>.md` | the QA report for each video |
| `lab/config.json` | `{ "target_video": "<path>", "self_improve": true }` |

## Once per studio: the target sheet
Ask the user for the path of the target video on this computer, save it in `lab/config.json`, then:
```
.venv/Scripts/python scripts/qa_score.py profile "<target video>" lab/target
```
This re-measures the profile and writes `target_sheet.jpg` for side-by-side viewing. The target's frames are for
private comparison only. If the user has no target video file, skip the sheet: the shipped profile still gives the
measured score, and you say plainly that the visual comparisons were made from memory of the style rules only.

## The three comparison points

### 1. Character sheet (before approval)
Render `CastSheet` and `FaceSheet`, then look at them next to `lab/target/target_sheet.jpg`. Check:
- flat single-colour clothing with printed details only; no gradients, no realistic fabric;
- each main character has one strong colour that separates them from the others and from the sets they appear in;
- hair is a simple solid shape; skin tones are plain;
- the palette sits in the same family as the target's characters (saturated primaries and off-whites against a
  duller world), and the hero's colour survives the night look (render one still under `NIGHT_EMBER` if unsure).
Proportions and face style are fixed by the engine and always match.

### 2. Storyboard (before approval)
```
.venv/Scripts/python scripts/qa_score.py frames out/<name>_board lab/target/profile.json
```
gives colour and detail scores for the storyboard frames. Then open `out/<name>_storyboard.jpg` next to the target
sheet and judge each shot:
- is the subject framed like the target frames its subjects (medium shots from chest height, close-ups for
  punchlines, wide shots for places and crowds)?
- is the face in the upper 45 % and clear of the caption?
- is the frame full (crowd, props, textured background), not a figure on empty ground?
- does the light come from the camera's side, and does the look match the story beat (day → dusk → night)?
Fix `story.json` and re-run until both the numbers and the sheet hold up. Do not ask for approval on a storyboard
you would not approve yourself.

### 3. Finished video (the QA review)
```
.venv/Scripts/python scripts/verify_final.py out/<name>.mp4 projects/<name> out/<name>_check.jpg
.venv/Scripts/python scripts/qa_score.py score out/<name>.mp4 lab/target/profile.json out/<name>_qa
```
`verify_final.py` checks timing (captions, cuts, sound ending, sync). `qa_score.py score` writes `report.json`,
`report.md` and `video_sheet.jpg`, and prints the measured score with the weakest categories first.

Then run the **visual review with fresh eyes**. If you can start a sub-agent, give it this brief and nothing about
what you expect it to find: the paths of `out/<name>_qa/video_sheet.jpg`, `lab/target/target_sheet.jpg`,
`out/<name>_storyboard.jpg`, and the rubric below; ask for a score per item with one sentence of evidence each, and
the three changes that would bring the video closest to the target. If you cannot start one, do the review yourself
and say so in the report.

Visual rubric (each 0–10; visual score = the sum):
1. Character style: blocky, flat-coloured, drawn faces, readable silhouettes
2. World style: textured, hazy, lit surfaces against the plain characters
3. Framing and shot sizes: the same mix of medium, close and wide as the target
4. Camera angles and height: eye level for people, high for maps and crowds, low only for threats
5. Camera movement: the constant push-in, whips on reveals, shake only on impacts
6. Staging: frames filled with crowd, props and background; subject clear
7. Lighting and colour per scene: believable, light on the subject, looks matching the beat
8. Effects: fire, embers, water, rain read correctly and are not blown out
9. Captions and faces: caption never over a face; expressions change with the words
10. Overall: would this pass as the same series as the target?

Record the result:
```
.venv/Scripts/python scripts/qa_score.py log out/<name>_qa/report.json lab --name <name> --visual <visual score>
```
Final score = 70 % measured + 30 % visual. The command prints it, the history, and **"GOAL REACHED"** when it is 85 or
more. When you see that line, tell the user at the top of your message, and offer to set `"self_improve": false`.

## After every video (while `self_improve` is true)
1. Write `lab/reports/<name>.md`: the final score, the measured table, the visual rubric scores with evidence, and a
   section "What to change next time" with at most five concrete items.
2. Update `lab/lessons.md` with those items (newest first). Each names a file, field or number.
3. If an item is a wrong default (a look preset, a set default, a caption value, a clip), fix it in the studio's
   engine now, re-render the affected storyboard frame to confirm it helped, and move the lesson to "Built in".
   Keep the engine's rule: every frame is a pure function of its frame number (`references/extending.md`).
4. Tell the user the score, how it compares with the previous videos, and the top three changes.

## What the scores mean, honestly
- The measured score compares statistics: the spread of brightness, saturation and hue; edge density; shot lengths;
  how much the picture changes from frame to frame; caption placement; the dead stop; narration pace; and the
  bright-to-dark arc. The target scores 100 against itself.
- A new story should not match the target shot for shot, so 100 is not the aim; the user's bar is 85.
- Narration pace and pauses count for 10 points and depend on the recording, not on you. Say so when they cost points.
- A high measured score with a poor visual score means the numbers are being gamed. Trust the sheet.
