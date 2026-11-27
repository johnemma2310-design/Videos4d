// Set library: a set builds static scenery into a scene from a params object (defaults merged with per-shot overrides).
import type * as THREE from "three";
import plazaDefaults from "../../../params/plaza_defaults.json";
import { Registry } from "../core/registry";
import { buildTabletPlaza, type TabletPlazaParams } from "./tabletPlaza";
import aerialDefaults from "../../../params/aerial_defaults.json";
import { buildAerialKingdoms, type AerialParams } from "./aerialKingdoms";
import { buildTownStreet, FIRE_STREET, WATER_STREET, type TownStreetParams } from "./townStreet";
import { vfx, type Vfx } from "../vfx";
import { buildCourtyard, FIRE_COURTYARD, WATER_COURTYARD, type CourtyardParams } from "./courtyard";
import { buildVolcano, VOLCANO_DEFAULTS, type VolcanoParams } from "./volcano";
import { buildKitchen, KITCHEN_DEFAULTS, type KitchenParams } from "./kitchen";
import { buildNightField, NIGHT_FIELD_DEFAULTS, type NightFieldParams } from "./nightField";

/** a set may return effects it placed itself (e.g. flames on its fire bowls); the shot updates them every frame */
export type SetBuilder = (scene: THREE.Scene, params: Record<string, unknown>, seed: number) => void | Vfx[];
export const sets = new Registry<SetBuilder>("set");

sets.add("tabletPlaza", (scene, p) => buildTabletPlaza(scene, { ...(plazaDefaults as unknown as TabletPlazaParams), ...p }));
sets.add("nightField", (scene, p) => {
  const q = p as Partial<NightFieldParams>;
  buildNightField(scene, { ground: { ...NIGHT_FIELD_DEFAULTS.ground, ...q.ground }, houses: { ...NIGHT_FIELD_DEFAULTS.houses, ...q.houses }, canal: q.canal });
});
sets.add("aerialKingdoms", (scene, p) => buildAerialKingdoms(scene, { ...(aerialDefaults as unknown as AerialParams), ...p }));

const street = (base: TownStreetParams): SetBuilder => (scene, p, seed) => {
  const q = p as Partial<TownStreetParams> & { flames?: boolean };
  const params: TownStreetParams = {
    seed: q.seed ?? base.seed, ground: { ...base.ground, ...q.ground }, houses: { ...base.houses, ...q.houses },
    kerb: q.kerb === null ? null : base.kerb ? { ...base.kerb, ...q.kerb } : q.kerb ?? null,
    bowls: q.bowls === null ? null : base.bowls ? { ...base.bowls, ...q.bowls } : q.bowls ?? null,
  };
  const { bowlSpots } = buildTownStreet(scene, params);
  if (q.flames === false) return;
  return bowlSpots.map((pos, i) => {
    const f = vfx.get("flame")({ pos, size: 1.5 * (params.bowls?.scale ?? 1), light: i < 3 ? 9 : 0 }, seed + i * 17); // only the nearest bowls carry a light
    scene.add(f.object);
    return f;
  });
};
sets.add("fireStreet", street(FIRE_STREET));
sets.add("waterStreet", street(WATER_STREET));
sets.add("kitchen", (scene, p) => {
  const q = p as Partial<KitchenParams>;
  buildKitchen(scene, { ...KITCHEN_DEFAULTS, ...q, window: { ...KITCHEN_DEFAULTS.window, ...q.window }, table: q.table === null ? null : { ...KITCHEN_DEFAULTS.table!, ...q.table } });
});
sets.add("fireCourtyard", (scene, p, seed) => buildCourtyard(scene, { ...FIRE_COURTYARD, ...(p as Partial<CourtyardParams>) }, seed));
sets.add("waterCourtyard", (scene, p, seed) => buildCourtyard(scene, { ...WATER_COURTYARD, ...(p as Partial<CourtyardParams>) }, seed));
sets.add("volcano", (scene, p, seed) => {
  const q = p as Partial<VolcanoParams>;
  return buildVolcano(scene, { ...VOLCANO_DEFAULTS, ...q, houses: q.houses === null ? null : { ...VOLCANO_DEFAULTS.houses!, ...q.houses } }, seed);
});
