# Lessons

Read this file before every stage of every video and apply what it says. After each finished video, add at most five
new lessons at the top of "Open" (newest first). A lesson must name the thing to change (a file, a field, a number)
and the evidence. When a lesson has been built into the engine or a preset default, move it to "Built in".
Remove a lesson that turned out to be wrong, and say so in the report.

## Open

From "vigilante" (2026-11-27, measured 67.3, visual 55, Spanish, edge-tts voices per line):
- **Camera is the weakest category (21):** 24 % nearly still frames. Close-ups with push 5-8 % and long two-shots read as still.
  Give every shot at least 15 % push or a sideways drift, and add a slow orbit on dialogue shots over 2 s.
- **Cut more (pacing 66):** mean shot 2.03 s vs 1.46. Split every line longer than ~1.6 s at a clause start.
- **Dark characters vanish at night indoors:** the Vigilante with skin #4a4658 had no readable face; skin #a29cb6 and a
  brighter night interior (hemi 1.35) fixed it. Keep faces of night characters light.
- **Over-the-shoulder with a giant (scale 1.6):** aim the target at y ~6.6 and raise the camera to ~6 or the head is cut.
- **Arc:** the story ends in day light (CTA), which flattens the arc score; end the CTA at dusk or night.

From the user's sound pack (2026-11-21):
- **Use the user's 18 labelled sounds in every video**, as `sfx/usage.md` says: pops and clicks on appearances and changes,
  whooshes on whips, risers ending on reveals (`lead` = the riser's length), `transition` on changes of place or time,
  `riser_fear` before the disaster, `money` on money. They are added to the rain, fire and crowd layers, not instead of them.

From the user's frame-by-frame review and round 3 (2026-11-21, final 75.3: measured 83.5, visual 56):
- **Faces must be alive in every shot** (the user). Nobody holds one expression: the speaker's mouth follows the words
  (`talk` on the actor), everyone blinks (automatic), expressions change on the meaningful word, eyes look at things
  (`look`). The generator adds a second expression to any actor left on one.
- **Walking and running must really travel** (the user). Give the actor `to` or `path`; attach what belongs to them
  with `follow` on the effect; move the camera with them. Keep crowds out of the walker's lane.
- **Crowds have faces and move** (the user): set `mood` to fit the beat and `walk` above 0 in street scenes.
- **Never put a table or prop between two characters and the camera side-on** (the user). Use over-the-shoulder,
  then a close-up, then a front two-shot with furniture low in the frame.
- **Day scenes need haze as well as a blue sky.** Keep fog density near 0.004 with a pale blue fog colour, and add
  bloom 0.3: a clean sky without haze reads flatter than the target.
- **Caption on the face:** in any close-up, keep the chin above 62 % of the frame height (the mop shot and Grandma's
  close-up failed). Check the last frame of each close-up.
- **Reviewer scores vary by about 4 points** between runs on similar pictures. Do not read a 2-point change as real;
  compare item by item.
- **Check a patch script saved its file.** An assertion half-way through a patch aborted before writing, and a
  20-minute render started on the old shots. Verify one changed line after every patch.

From "rain-liars" round 2 (2026-11-21, final 76.6: measured 84.1, visual 59):
- **A push-in on a close-up ends on a torso.** For close-ups use a push of 8 % at most (or a sideways drift only),
  so the last frame still holds the whole head. Check the LAST frame of each close-up, not the middle one.
- **The day act is the weak act.** `DAY_SUN` and `DAY_COOL` skies read as flat grey: give day scenes a blue sky with
  cumulus (`sky.top` bluer, `cloudCover` 0.35, brighter `cloudLight`), a warm key with visible shadows, and haze.
- **One street, one square, one kitchen is too few places for 2 minutes.** Plan at least six distinct locations and
  open each with a wide or high establishing shot; use one low angle for the threat.
- **The hero's saturated top looks pasted in at night.** Lower its saturation a step, or tint characters with the
  scene (lower hemisphere light, stronger coloured key) so they take the firelight.
- **White-outs:** cap bloom on shots with many flames (`post.bloom.strength` 0.35) and keep the lightning frame's
  exposure at 1.1.

From "rain-liars" (2026-11-20, final 74.4: measured 82.7, visual 55):
- **Too few sound effects** (the user, 2026-11-21: "very less sfx"). Hit and whoosh are not enough. Every video gets
  recorded sounds for what is on screen: fetch them with `scripts/sfx_fetch.py` and place them with `sfx` on the
  shots (rain-liars went from 17 sounds to 120: rain under every cloud, fire, pops, drips, thunder, crowd).
- **Close-ups show too much torso and crop the head.** Use camera target y 4.6-4.8 and distance 7.5-8.5 for a
  close-up, so the face sits in the upper-middle and the torso takes under half the frame.
- **Night flames blow out to white discs.** Keep `flame` size at 3 or less at night, or lower its burst and halo
  gain in `src/engine/vfx/index.ts`; add a `steam` puff above each as smoke.
- **Crowds stand in one flat row; sets are bare.** Use two or three crowd bands at different depths and at least two
  props in every shot longer than 1.5 s (kitchen and street especially).
- **Day and dusk scenes are flatly lit and skies are flat.** `DUSK_MAGENTA` needs cloud cover and a key from the
  camera side; always add the street fog override to `DAY_SUN`.
- **A resolved story ends in daylight, which flattens the arc score.** Grade the coda as late afternoon (lower
  exposure, warmer key) instead of full day.
- **A long video must be rendered with `--timeout=180000`**, and storyboards in batches of about 17 frames
  (`--frames=a-b`, then rename to three-digit numbers); frame files from short ranges get two-digit names.

Earlier:
- **Scenes are too still.** Both test videos measured a frame-to-frame change of 1.3–1.7 against the target's 9.6
  (QA category "camera", 48–49 of 100). In `story.json`: push in 15–25 % on every shot instead of 8–15 %; use more
  whip-ins on new subjects; put a crowd, a moving effect (embers, flames, fireballs, rain) or a second gesture in
  every shot longer than 1.5 s.
- **Frames are too empty.** Edge density 6–9 % against the target's 13.6 % (category "detail", 50–56). Stage shots with
  crowds, props and textured walls behind the subject; avoid framings that are mostly plain ground or sky.
- **Night shots run too warm.** Warmth in the last third was 2.8–3.0 times the first third; the target's is 1.7
  (category "arc", 51–66). For night shots add `lookOverrides` with a less saturated key light
  (`"color": "#ffd8c0"`) or a lower `post.grade.gain` red, and check the storyboard's colour score.
- **Cut more often.** By this tool's detector the target has 40 cuts per minute and a mean shot of 1.46 s. One shot
  per sentence is the minimum; add cuts on clause starts and punchline words.
- **Pauses.** The stand-in voice left a median pause of 0.56–0.58 s; the target's is 0.36 s. Ask the narrator to keep
  the gaps between sentences short.

## Built in

- **Scenes are too still / frames too empty** (first two tests): push-ins of 15-25 %, crowds and effects in every shot. Camera rose from 48 to 78 and detail from 50-56 to 75 on rain-liars. Now the default in the story helpers (`projects/rain-liars/make_story.py`).
- **Pauses too long:** `scripts/tighten_pauses.py` shortens them in the recording.
