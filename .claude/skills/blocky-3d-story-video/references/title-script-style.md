# Title and script style (measured on the 10 samples)

The user supplied 10 titles and scripts from videos with 3.5 to 26 million views. This page is the analysis of them.
New titles and scripts must fit these shapes and numbers while using a world, people and wording of their own.
`scripts/script_check.py` tests a draft against the numbers and against copied wording.

Contents: 1 Two families · 2 Titles · 3 World story: numbers · 4 World story: the 12 parts · 5 Voice and devices ·
6 What makes them work · 7 Time-travel comedy · 8 Never reuse

## 1. Two families
| | World story (8 of 10) | Time-travel comedy (2 of 10) |
|---|---|---|
| Views | 3.5 to 26 M (the four biggest are all this family) | 7.2 and 14 M |
| Title | Title Case, 3 to 6 words, one emoji at the end | ALL CAPS, 5 to 7 words, ends with `...` |
| Opens | "In this world, …" | "I" + past tense: what happened to me |
| Narrator | a kid with the worst power or the oddest habit | a clueless modern person in a famous moment of history |
| Length | 370 to 435 words (about 2 min at 188 words/min) | 225 to 246 words (about 75 s) |
| Ending | fully resolved, then a "Now …" coda with a callback joke | breaks off mid-sentence, where the title would finish it |

Default to the world story. Offer a time-travel title only as one or two of the ten, or when the user asks.

## 2. Titles
**World-story titles** (all 8):
- 3 to 6 words, 20 to 33 characters, every word capitalised, **one emoji at the very end** that pictures the central
  thing (wave, ghost, star, radio, horse, a cross for "don't").
- Present tense. The title states **the law of the world as a plain fact, or a warning**. It never mentions the
  narrator, never says "I", never asks a question, never hints at the twist.
- Three shapes:
  | Shape | Count | Pattern |
  |---|---|---|
  | The law as a fact | 4 | *subject + present verb + object*: what this world does ("The Ocean Pulls Back", "Powers Come From Stars") |
  | A warning | 3 | *Don't + verb + the + thing* ("Don't Cross The Blue Line"), or *X And Y Don't Mix* |
  | A place and a time | 1 | *time word + place* ("Midnight Radio Tower") |
- Everyday nouns a seven-year-old knows: ocean, fire, water, pets, ghosts, stars, stone, horse, line, tower.
- The title makes the viewer ask "what happens if…?" The first sentence of the script answers "what is this world?",
  and the story answers the rest.

**Time-travel titles** (both): `I` + past-tense verb + where/what, all capitals, trailing `...`
("I BECAME A ROMAN SOLDIER..."). The script's last, unfinished sentence leads back into the title.

## 3. World story: numbers
Measured on the 8 world samples (range, typical):
| Measure | Range | Typical |
|---|---|---|
| Words | 370 to 435 | 395 |
| Sentences | 49 to 68 | 54 |
| Median sentence | 5 to 7 words | 6 |
| Longest sentence | 16 to 25 words | about 19, and only one or two that long |
| Sentences of 4 words or fewer | 22 to 41 % | 25 % |
| Sentences starting "And" | 4 to 13 % | 9 % |
| Quoted lines of speech | 0 to 9 | 3 |
| Spoken length at 188 words/min | 118 to 139 s | about 2 min 5 s |

The target video file is the first 61 s (188 words) of sample 1; the full script runs about 2 min 7 s and resolves.
**A cut-off ending is not part of the world-story style.**

## 4. World story: the 12 parts
Position is how far through the words each part starts. All eight samples follow this order.

| # | Part | Starts at | What it does | How the samples say it |
|---|---|---|---|---|
| 1 | Premise | 0 % | One sentence: the magic law of this world, often with a trigger in time ("once every…", "every Halloween", "on your first day of school") | "In this world, …" (8 of 8) |
| 2 | How it works | 2 to 6 % | Two or three tiny, concrete, funny examples of ordinary life under the law, in parallel sentences | "You see, …" (8 of 8). Example groups: X kids do this. Y kids do that. |
| 3 | Rule or limit | 3 to 17 % | The one law, the danger, or the limit that will matter later. Short enough for a sign. | "And there's only one rule." (3 of 8), or a plain limit / "Nobody knows why." |
| 4 | The odd detail | 16 to 21 % | Something slightly wrong that nobody explains: the seed of the twist | "But here's the weird part." (2 of 8); in others the oddity is a personal clue |
| 5 | The narrator | 12 to 27 % | A kid who got the worst version: the lamest power, the dullest hobby, no power, the unlucky one. Three small specifics, **one of which is the thing that will save everyone** | "My name is …" (2), "The stone gave me …", "My ghost is …", "And me, I'm …" |
| 6 | The cost | 27 to 39 % | How other kids treat them. A mocking nickname (4 of 8), teasing (6 of 8). Sometimes a rival with the best power, who is later the one rescued (2 of 8). | "He calls me X. Now everyone calls me X." |
| 7 | The keepsake | 17 to 40 % (or held back for the reveal) | A parent's or grandparent's saying, or an object they left (7 of 8). Stated once, plainly, not understood yet. | "Dad always tells me …", "Grandma always says one thing." |
| 8 | The turn | **34 to 43 %** | One short sentence starts the event. From here the story is past tense and continuous. | "Then came …", "Until our class trip …", "Then one night …", "This Halloween …" |
| 9 | Everyone else fails | 45 to 62 % | The disaster. The strong ones try, one after another, and each fails for a stated reason (usually three tries). | "A did X. It failed. B did Y. It failed." |
| 10 | The reframe | 58 to 73 % | The narrator sees what the premise really meant: the thing everybody feared or mocked was something else all along. Often with the keepsake line said again word for word. | "That's when I understood." / "Anyone except me." / "I knew that voice." |
| 11 | The act | 62 to 90 % | Short physical beats. A first try that falls short, then harder. Sound words, a triple ("Up, up, up"). A silent crowd afterwards, then one small gesture. | "The whole class was standing in the rain, staring." |
| 12 | Coda | last 4 to 8 % | Present tense again: the new normal in two or three sentences. **The last line is a callback joke of 4 to 14 words** that turns an early detail upside down. | "Nobody called me X again." (2), "Now …" (6 of 8) |

The reframe (part 10) is the heart of every sample. Each one turns the premise inside out: the war itself fed the
danger; the sea was only drawing breath; the monsters were trying to reach a cure; the chaser only wanted what the
narrator was carrying; the kid without a star was one. Design the reframe first, then plant its clues in parts 4, 5
and 7.

## 5. Voice and devices
- **First person, a kid, deadpan.** States impossible things as plain facts, then undercuts them with something
  small and domestic (a treasure chest that holds only sand, and its finder still pleased with it).
- **Tense:** the world in present tense (parts 1 to 7), the event in past tense (8 to 11), the coda in present.
- **Words:** everyday and short. The longest words are things like "marshmallows", "shipwrecks", "nightlight".
  No adverb piles, no abstract nouns, no moral stated out loud.
- **Parallel sets of two or three** carry the world-building and the failures.
- **Numbers are round and big** ("300 years", "100 ft", "3 miles", "thousands of them") and repeat.
- **Fragments for speed:** one-, two- and three-word sentences at the peaks ("Mud. Miles of it.").
- **Sound words** as their own sentence (5 of 8 use sound words or a triple beat): one per big impact.
- **Speech is rare and short.** At most a few lines; one of them is often a single word that lands as a joke or as
  the emotional beat.
- **Family is the emotional anchor** (7 of 8): a mother, father or grandparent is lost, doubted or proved right.
- **Nobody is punished.** The bully is rescued and becomes the friend; enemies end up sharing something.
- **Names:** short first names for other kids and pets (one or two syllables); the narrator is often unnamed.
- **Plant and pay off, everything.** Every odd detail in the first third returns in the last third. If a detail does
  not come back, cut it.

## 6. What makes them work (use as a checklist when judging an idea)
1. The premise is a rule a child would wish for or fear, in one sentence, with a picture in it.
2. The narrator's flaw is funny and concrete, and is the exact tool the ending needs.
3. Conditions that make the flaw useful are stated early as a throwaway ("when it's wet, I stick even harder").
4. The stakes reach the whole community or one named person the narrator has a reason not to help.
5. The strongest characters visibly fail first.
6. The twist re-explains the premise instead of adding new magic.
7. The last line makes the viewer smile, not gasp.

## 7. Time-travel comedy (2 samples)
- 225 to 246 words, 21 to 29 sentences, median sentence 8 to 11 words: longer, comma-chained sentences that pile
  action on action.
- Sentence 1 states the whole situation: "I" + travelled/woke up + a famous place and time.
- The narrator is a coward or a nuisance who acts on modern knowledge or panic. Every action backfires into the next:
  a chain of accidents (sample 5) or a warning nobody believes (sample 8).
- Signature words: "accidentally", "somehow", "immediately", "So, naturally," "Then," "Suddenly".
- Quick back-and-forth speech in very short lines is allowed (up to 8).
- The high point is an authority figure misreading the narrator ("This man knows no fear").
- **Ends on an unfinished sentence** ("…and that's how I became…") that loops back to the title. This is the only
  family where the audio stops mid-sentence.

## 8. Never reuse
New work must not use the samples' worlds, premises, people or sentences:
- Worlds/premises taken: fire and water kingdoms with a volcano; a sea that withdraws once a century; an undersea
  kingdom behind a line; a stone that hands out animal powers; ghost pets; zombies walking to a radio tower; powers
  from birth stars; a headless horseman on Halloween; a Roman battle; the Titanic.
- Names taken: Sens, Leo, Rex, Duke, Mia, Kai, Zara, Bubbles, Tank, Finch.
- Powers/flaws taken: mud, shells, gills, snail, goldfish ghost, climbing, no star, the pumpkin bucket.
- No run of five words in a row may match a sample, except the house phrases the samples share among themselves
  ("In this world,", "You see,", "And there's only one rule.", "But here's the weird part.",
  "… always says one thing.", "Now everyone calls me …", "Nobody called me … again.").
  `script_check.py` enforces this with fingerprints (`lab/samples_ngrams.json`); it does not need the sample texts.
