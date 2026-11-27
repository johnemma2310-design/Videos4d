# Script, pacing and caption rules

Shot, caption and sound numbers were measured on the reference short (the first 61 s of sample 1: 188 words, 37 shots).
Story shape and sentence numbers come from the 10 sample scripts; the full account is in `references/title-script-style.md`.

## Voice and sentences
- First person, a kid narrator: matter-of-fact, dry, then suddenly high stakes.
- Short declarative sentences: median 5 to 7 words, a quarter of them 4 words or fewer, one or two long ones (up to 25).
- About 188 words per minute including pauses, so plan about **3 words per second** of finished video. Pauses between sentences are short (median 0.36 s).
- Build with parallel sets of two or three ("A does this. B does that."), sentences starting with And / But / Then, and one plain rule stated in a few words.
- Plant details early and pay every one of them off; the last line calls back to the first third.
- **World stories resolve.** They end with a short present-tense coda and a callback joke. Only the time-travel comedy family ends on an unfinished sentence.

## Shape of a world story (370 to 435 words, about 2 minutes)
| Part | Starts at | Job |
|---|---|---|
| Premise | 0 % | "In this world, ...": the law in one line |
| How it works | 2 to 6 % | "You see, ...": two or three quick examples |
| Rule or limit | 3 to 17 % | the one law, short enough to fit a sign |
| Odd detail | 16 to 21 % | the unexplained thing that seeds the twist |
| Narrator | 12 to 27 % | who is telling this, and their "worst" trait |
| Cost and keepsake | 27 to 40 % | how others treat them; a parent's saying or object |
| Turn | 34 to 43 % | "Then came ...": the event starts, past tense from here |
| Everyone fails | 45 to 62 % | the strong ones try and fail, one by one |
| Reframe | 58 to 73 % | what the law really meant; the trait is the tool |
| The act | 62 to 90 % | short physical beats, first try falls short, then success |
| Coda | last 4 to 8 % | present tense, the new normal, the callback joke |

## Shots
- About 35 cuts per minute. Shot length: mean 1.65 s, median 1.43 s, range 0.4 to 3.1 s. A 2-minute world story is therefore about 70 to 80 shots; plan the beat table in the 11 story parts and reuse sets across them.
- A new shot starts on the first word of nearly every sentence. Extra cuts land on a clause start or on a punchline word.
- Fast sections (the rule, reveals): 0.4 to 1 s per shot. The big event: 2 to 3 s per shot, with the energy coming from effects and camera shake inside the shot.
- Only two kinds of transition exist: a hard cut, and a whip pan (the camera is already swinging as the new shot starts). No fades or dissolves.

## Captions (applied automatically; write the script normally)
- One word on screen at a time, switching on the frame the word is spoken, held through pauses.
- Shown lowercase, even at sentence starts, with punctuation removed except apostrophes.
- Capitals only for "I" and for names. List names in `story.json` under `"names"`.
- Write numbers the way they should be read aloud; if you want digits on screen, write digits in the script and make sure the narrator reads them as one word.

## Sound
- Voice on top, a sustained drumless music bed about 7 dB under it, no beat for the cuts to follow.
- Voice and music stop dead at the last word, and the picture holds silently for about one second. The build does this for you. In a world story the last word ends a finished sentence; in a time-travel comedy it is mid-sentence.
