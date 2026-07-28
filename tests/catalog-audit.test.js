"use strict";
// Verification-only diagnostic: list the exact structure split produced by current main.
global.window = global;
require("../smufl-catalog.js");
require("../notation-catalog-core.js");
const glyphs = global.LEGATO_SMUFL_CATALOG.glyphs;
const core = global.__LEGATO_CATALOG_CORE__;
const sourceStructures = glyphs.filter(x => String(x.kind).toLowerCase() === "structure" && String(x.placement).toLowerCase() === "structure");
const score = sourceStructures.filter(x => core.isScoreStructure(x, x.label));
const composite = sourceStructures.filter(x => core.isCompositePlayOrder(x, x.label));
console.error("STRUCTURE_SPLIT " + JSON.stringify({
  total: sourceStructures.length,
  score: score.map(x => ({id:x.id,label:x.label,group:x.group,range:x.range})),
  composite: composite.map(x => ({id:x.id,label:x.label,group:x.group,range:x.range}))
}, null, 2));
process.exit(1);
