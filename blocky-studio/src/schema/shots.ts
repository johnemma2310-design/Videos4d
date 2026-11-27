// Data contract for a video's shots (shots.json). An agent authors this file; it never edits engine code.
// Frames inside a shot are local (0 = the shot's first frame). Camera keys may start before 0 so that a whip-in is
// already moving on the first frame.
import { z } from "zod";
import { castFile } from "./cast";

const v3 = z.tuple([z.number(), z.number(), z.number()]);
const camKey = z.object({ f: z.number(), pos: v3, target: v3, ease: z.string().optional() }).strict();
const shake = z.object({
  f0: z.number(), f1: z.number(), ampDeg: z.tuple([z.number(), z.number()]),
  mode: z.enum(["alt", "random"]).optional(), decay: z.number().optional(), bursts: z.number().optional(),
}).strict();

export const actorSpec = z.object({
  /** key in the cast file */
  character: z.string(),
  pos: z.tuple([z.number(), z.number()]), // x, z on the ground
  yaw: z.number().optional(), // degrees; 0 faces +Z
  /** clips layered in start order: a later clip overrides the channels it animates */
  clips: z.array(z.object({ clip: z.string(), at: z.number() }).strict()).optional(),
  /** face decal swaps: the expression shown from local frame f on */
  faces: z.array(z.object({ f: z.number(), v: z.string() }).strict()).optional(),
  /** travel across the ground: positions at local frames (linear in between). Walk and run clips step in time with the distance covered */
  path: z.array(z.object({ f: z.number(), pos: z.tuple([z.number(), z.number()]) }).strict()).optional(),
  /** local frame ranges in which this character is speaking: the mouth moves */
  talk: z.array(z.tuple([z.number(), z.number()])).optional(),
  /** where the eyes look, as an offset of the pupils (x: + = to the viewer's right, y: + = down; about -0.05..0.05) */
  look: z.tuple([z.number(), z.number()]).optional(),
  /** false = never blink (default: blinks every 2.5 to 4 seconds) */
  blink: z.boolean().optional(),
  contactShadow: z.number().min(0).max(1).optional(),
  /** item carried in the right hand */
  prop: z.enum(["spear"]).optional(),
  propColor: z.string().optional(),
}).strict();

export const shotSpec = z.object({
  id: z.string(),
  frames: z.number().int().positive(),
  set: z.string(),
  setParams: z.record(z.unknown()).optional(),
  look: z.string(),
  actors: z.array(actorSpec),
  camera: z.object({ fov: z.number().min(10).max(100).optional(), keys: z.array(camKey).min(1), shake: z.array(shake).optional(), roll: z.number().optional() }).strict(),
  /** where the sun's shadow box sits and how wide it is (studs). Default: around the first actor, 14 studs */
  shadow: z.object({ focus: v3, extent: z.number().positive() }).strict().optional(),
  /** effects: { type: "embers" | "flame" | "fireballs" | "rain" | "steam" | "water", ...parameters } */
  vfx: z.array(z.object({ type: z.string() }).passthrough()).optional(),
  crowds: z.array(z.object({
    palette: z.enum(["fire", "water"]), count: z.number().int().min(1).max(2000), area: z.tuple([z.number(), z.number(), z.number(), z.number()]),
    facing: z.number().optional(), cheer: z.number().min(0).max(1).optional(), spears: z.number().min(0).max(1).optional(), seed: z.number().optional(),
    mood: z.string().optional(), walk: z.number().min(0).max(1).optional(), walkDir: z.number().optional(), bothWays: z.boolean().optional(), speed: z.number().optional(), run: z.boolean().optional(),
  }).strict()).optional(),
  /** per-shot overrides of the look preset (merged per top-level key: sky, fog, lights, post) */
  lookOverrides: z.record(z.unknown()).optional(),
  /** "auto" (default) blurs frames where the camera turns or travels fast; "off"; or explicit local frame ranges */
  motionBlur: z.union([z.literal("auto"), z.literal("off"), z.array(z.tuple([z.number(), z.number()]))]).optional(),
  /** local frame shown on the shot's first frame (default 0). Storyboards use it to show one chosen frame per shot */
  startAt: z.number().optional(),
}).strict();

export const shotsFile = z.object({ fps: z.literal(30), width: z.number().int(), height: z.number().int(), shots: z.array(shotSpec).min(1),
  /** the characters of this video (same format as cast.json); optional */
  cast: castFile.optional() }).strict();
export type ShotSpec = z.infer<typeof shotSpec>;
export type ShotsFile = z.infer<typeof shotsFile>;
