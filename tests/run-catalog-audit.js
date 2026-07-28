"use strict";
// Verification-only diagnostic for the exact no-slur tonguing source record.
global.window = global;
require("../smufl-catalog.js");
require("../notation-catalog-core.js");
require("../notation-catalog-metadata-corrections.js");
const id = "tripleTongueAboveNoSlur";
const source = global.LEGATO_SMUFL_CATALOG.glyphs.find(x => x.id === id);
const classified = global.__LEGATO_CATALOG_CORE__.classify(source, source && source.label, source && source.glyph);
console.error("NO_SLUR_METADATA " + JSON.stringify({ source, classified }, null, 2));
process.exit(1);
