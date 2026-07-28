"use strict";
// Verification-only diagnostic: inspect every source record classified as structure.
global.window = global;
require("../smufl-catalog.js");
const glyphs = global.LEGATO_SMUFL_CATALOG.glyphs;
const structures = glyphs.filter(x => String(x.kind).toLowerCase() === "structure" || String(x.placement).toLowerCase() === "structure");
const counts = {};
for (const x of structures) {
  const key = [x.group, x.range, x.sound || "silent"].join(" | ");
  counts[key] = (counts[key] || 0) + 1;
}
const outsideScoreStructure = structures.filter(x => !/repeats|barlines|structure|clefs|staff|meters/i.test([x.group, x.range].join(" ")));
console.error("STRUCTURE_FAMILY_DIAGNOSTIC " + JSON.stringify({
  total: structures.length,
  counts,
  outsideScoreStructure
}, null, 2));
process.exit(1);
