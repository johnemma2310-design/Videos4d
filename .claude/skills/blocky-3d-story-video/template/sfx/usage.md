# Sound library: what each sound is for

Read this before placing sounds. The first table is the user's own pack with the user's own instructions; follow them.
The second table is the public-domain set fetched for the story world (rain, fire, crowds). Use both: the pack gives the
edit its punctuation (pops, whooshes, risers), the second gives the world its sound.

## The user's pack (their labels)
| Sound | Length | What it is | Where to use it |
|---|---|---|---|
| `whoosh_air` | 0.97 s | whoosh (the click at the end removed) | camera whips and fast moves |
| `bell_pop` | 0.86 s | pop in / pop out with a bell-like ring | something popping in or out of the picture |
| `loading_soft` | 1.03 s | soft loading sound | when something is loading, filling or getting ready |
| `pop_soft_in` | 0.17 s | soft pop-in | a gentle appearance; a good default pop |
| `camera_shutter` | 0.64 s | camera shutter | a snapshot, a freeze, a reveal held like a photo |
| `riser` | 1.84 s | riser | building up to a cut or a reveal |
| `riser_fear` | 7.15 s | fear riser (long) | dread building: the threat approaches, before the disaster |
| `whoosh_quick` | 0.23 s | soft quick whoosh | small fast moves: a gesture, a quick pan, an object passing |
| `clock_tick` | 2.98 s | ticking clock | time passing, waiting, a countdown |
| `pop_soft` | 0.12 s | soft pop | small appearances and face changes |
| `loading_anim` | 3.81 s | soft loading for animation | under something being built, drawn or assembled on screen |
| `money` | 0.83 s | money sound | money, prices, treasure, a reward |
| `pop_b` | 0.76 s | pop | appearances; alternate with the other pops |
| `click` | 0.19 s | click | a switch, a decision, a small precise action |
| `whoosh_short` | 0.15 s | whoosh | camera whips and fast cuts; alternate with whoosh_air |
| `riser_burst` | 2.31 s | soft riser that starts slow and then bursts | a build that ends in an impact or a big reveal |
| `pop_c` | 0.23 s | pop | appearances; alternate with the other pops |
| `transition` | 0.77 s | transition sound | transitions and cuts to a new place or time |

How to place them:
- **Pops and clicks** go on the frame something appears, changes or is pointed at. Vary them: do not use the same pop twice in a row.
- **Whooshes** go on camera whips and fast moves, starting on the first frame of the move.
- **Risers must END on the cut or the reveal.** Give the sound a `lead` equal to its length (in seconds) so it starts early and peaks on the frame you name.
- **`transition`** goes on a hard change of place or time, on the first frame of the new shot.
- **`clock_tick`, `loading_soft`, `loading_anim`** run under waiting, counting or building moments; keep them a few dB down (`gain` -4).
- Keep the rain, fire and crowd layers as they are; these sounds are added on top, never instead.

## The story-world set
| Sound | Length | Kind | Source title |
|---|---|---|---|
| `pop` | 0.5 s | single event | cartoon poppyup appearances -0003.aiff |
| `drip` | 0.47 s | single event | Water_drop_9.wav |
| `thunder` | 4.0 s | single event | Thunder Clap |
| `splash` | 2.0 s | single event | Water splash, emptying a bucket 1 |
| `rain_light` | 30.0 s | background layer (give it `dur`) | Light rain falling at night in Hawaii |
| `rain_heavy` | 30.0 s | background layer (give it `dur`) | Heavy rain_clear recording |
| `fire` | 30.0 s | background layer (give it `dur`) | fire crackles |
| `crowd_panic` | 11.73 s | background layer (give it `dur`) | Crowd Screaming |
| `crowd_cheer` | 5.13 s | background layer (give it `dur`) | Short Crowd Cheer 2.flac |
| `hiss` | 3.0 s | single event | Steam.wav |
