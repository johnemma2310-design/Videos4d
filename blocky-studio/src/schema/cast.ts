// Data contract for characters (cast.json). Shared by the browser engine and the Node validator.
import { z } from "zod";

const hex = z.string().regex(/^#[0-9a-fA-F]{6}$/, "expected a #rrggbb colour");
export const HAIR_STYLES = ["sidePart", "bob", "long", "ponytail", "tufts", "bun", "curly", "spikyTop", "bald", "beanie", "rainHat"] as const;

const torso = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("plain"), color: hex }).strict(),
  z.object({ kind: z.literal("varsity"), color: hex, strip: hex, trim: hex.optional() }).strict(),
  z.object({ kind: z.literal("stripes"), color: hex, color2: hex, bands: z.number().int().min(2).max(12).optional() }).strict(),
  z.object({ kind: z.literal("plaid"), color: hex, color2: hex }).strict(),
  z.object({ kind: z.literal("coat"), color: hex, trim: hex }).strict(),
]);

export const characterDef = z.object({
  skin: hex,
  hair: z.object({ style: z.enum(HAIR_STYLES), color: hex }).strict(),
  outfit: z.object({
    torso,
    sleeves: z.object({ color: hex, length: z.number().min(0).max(1).optional(), cuff: hex.optional() }).strict().optional(),
    legs: z.object({ color: hex, length: z.number().min(0).max(1).optional(), shoes: hex.optional() }).strict(),
  }).strict(),
  // stick3DD: accesorios de Sticky (bufanda, corbatín, gafas de lectura de media luna)
  extras: z.object({ scarf: hex.optional(), bowtie: hex.optional(), glasses: hex.optional() }).strict().optional(),
}).strict();

export const castFile = z.record(z.string().regex(/^[a-z][a-zA-Z0-9_]*$/), characterDef);
export type CharacterDef = z.infer<typeof characterDef>;
export type CastFile = z.infer<typeof castFile>;
