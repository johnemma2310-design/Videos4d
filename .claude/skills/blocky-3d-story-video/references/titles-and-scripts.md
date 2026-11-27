# Titles and scripts

Titles and scripts must match the user's 10 sample videos in shape and quality while being new. The analysis of
those samples is in `references/title-script-style.md`. **Read it in full before writing a title or a script.**

## What is where
- `references/title-script-style.md`: the measured style: two families, title shapes, script numbers, the 12 story
  parts, devices, and the list of worlds, names and phrases already used.
- `scripts/script_check.py`: tests a draft against the sample numbers and structure, and for copied wording.
- `lab/samples_ngrams.json`: fingerprints of the samples' wording (hashes only) used by the copy check.
- `lab/samples/`: the samples' full text, if the user keeps it in this studio. Not required. If the user gives more
  samples later, save them here (title on line 1, `views: N` on line 2, script from line 4), rebuild the fingerprints
  with `script_check.py --build-ngrams lab/samples lab/samples_ngrams.json`, and add what is new to the style page.
- `lab/scores.csv`: videos already made in this studio. Their premises are also off limits.

## Stage 1: ten titles
1. Think of premises first, titles second. For each idea write the four things the style page calls the core:
   the law of the world, the narrator's "worst" trait, the disaster, and the reframe (what the law really meant).
   Drop any idea without a real reframe, or whose trait is not the tool the ending needs.
2. Reject anything close to a world, power or name in section 8 of the style page or in `lab/scores.csv`.
3. Check each idea can be staged with the sets and effects that exist (`references/catalogue.md`). If an idea needs a
   new set, say so next to it: it costs engine work (`references/extending.md`).
4. Write the title in one of the measured shapes. For a world story: 3 to 6 words, Title Case, present tense, the law
   or a warning, no narrator, no twist, one emoji at the end.
5. Offer 10: by default 8 or 9 world stories spread over the three title shapes, and 1 or 2 time-travel comedies.

Present them like this and wait for the user's pick:
```
3. The Clocks Stop At Noon ⏰          (law as a fact)
   World: one line.  Narrator: the trait, in a few words.  Sets: tabletPlaza, fireStreet.
```
Do not reveal the reframe in the list unless the user asks; they may want to read the script fresh.

## Stage 2: the script
1. Plan before writing. Fill the 12 parts from the style page in one line each, and list every plant with its
   pay-off. Every plant must pay off; the last line must call back to something in the first third.
2. Write to the family's length unless the user asks otherwise: **world story 370 to 435 words** (about 2 minutes),
   time-travel 225 to 246 words. For a shorter video keep all 12 parts and shrink each; never drop the coda.
3. Save the draft as `projects/<name>/script.txt` and run:
   ```
   .venv/Scripts/python scripts/script_check.py projects/<name>/script.txt
   ```
   Fix every `CHECK` line and run it again. The `info` lines are devices some samples use; choose deliberately.
4. Read the draft aloud in your head against section 5 of the style page: deadpan kid, present-past-present tense,
   everyday words, no stated moral, nobody punished.
5. Show the user the script, then the checker's table (draft value next to the sample range), then one line on what
   makes this story new. Wait for approval. After any edit, run the checker again.

Write sound words as their own sentence ("Crack!"). Write numbers as digits when they should appear as digits.

## Uniqueness
The copy check must report 0 five-word runs shared with a sample and no reused names. Beyond what the tool can see:
the world, the law, the narrator's trait, the disaster and the reframe must each differ from every sample and from
every earlier video. Borrow the skeleton, never the story.
