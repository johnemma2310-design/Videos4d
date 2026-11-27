// npx tsx scripts/validate.ts data/cast.json  -> exits 1 and prints JSON paths on any schema error
import fs from "node:fs";
import { castFile } from "../src/schema/cast";
const file = process.argv[2];
const r = castFile.safeParse(JSON.parse(fs.readFileSync(file, "utf8")));
if (!r.success) {
  for (const i of r.error.issues) console.error(`${file}: ${i.path.join(".") || "(root)"}: ${i.message}`);
  process.exit(1);
}
console.log(`${file}: ok (${Object.keys(r.data).length} characters)`);
