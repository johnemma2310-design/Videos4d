# Describing the voice

Use this when the user wants to design a similar narrator voice in a text-to-speech service. You cannot hear audio:
describe the voice from measurements and from how the scripts are written, and say which parts are guesses.

## The target narrator, measured
| Measure | Value |
|---|---|
| Pitch, typical | 174 Hz; most of the time 130 to 220 Hz |
| Pitch movement | about an octave between low and high words |
| Pace including pauses | 188 words per minute |
| Pace while speaking | 243 words per minute |
| Pauses | typically 0.36 s, longest about 1 s |

174 Hz is too low for a small child and high for a man: a teenage boy or a young man with a light voice. Accent,
tone colour and whether the original is human or synthetic are not known. `scripts/voice_profile.py <video or wav>
<words.json>` measures the same things on any recording.

## A description to start from
> A teenage boy, around 14 to 16, with a light, clear, slightly high voice. Fast, energetic storytelling pace, like a
> kid excitedly telling a friend an unbelievable story. Deadpan and matter-of-fact on ordinary lines, then suddenly
> dramatic on big moments. Crisp, punchy delivery with very short pauses between sentences. Bright, clean,
> close-microphone studio sound with no echo and no background noise. Not a cartoon voice and not a small child.

Add the accent the user wants. Suggested settings: the fastest speed, low-to-middle stability so the pitch moves,
middle-to-high expressiveness. Tell the user to preview with their own script's first paragraph.

## What usually comes back
The first generated voice-over for this studio spoke at the right speed (239 words per minute while speaking) but
paused too long (0.52 s), giving 168 words per minute overall. `scripts/tighten_pauses.py` fixed that (181, 0.40 s)
without touching speech. Expect to do the same.
