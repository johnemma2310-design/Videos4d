// Writes the props file for a preview sheet of a project's own cast.
//   npx tsx scripts/sheet-props.ts projects/<name> <sheet.cast | sheet.faces | sheet.clips>
// then:  npx remotion still src/index.ts CastSheet out/cast.png --props=projects/<name>/sheet.json --gl=angle
import fs from "node:fs";
import path from "node:path";
import { castFile } from "../src/schema/cast";

const [dir, program = "sheet.cast"] = process.argv.slice(2);
if (!dir) { console.error("usage: npx tsx scripts/sheet-props.ts projects/<name> [sheet.cast|sheet.faces|sheet.clips]"); process.exit(1); }
const r = castFile.safeParse(JSON.parse(fs.readFileSync(path.join(dir, "cast.json"), "utf8")));
if (!r.success) {
  for (const i of r.error.issues) console.error(`cast.json: ${i.path.join(".") || "(root)"}: ${i.message}`);
  process.exit(1);
}
fs.writeFileSync(path.join(dir, "sheet.json"), JSON.stringify({ program, props: { cast: r.data } }));
console.log(`wrote ${path.join(dir, "sheet.json")} (${Object.keys(r.data).length} characters, ${program})`);
