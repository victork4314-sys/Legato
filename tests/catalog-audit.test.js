"use strict";
const assert = require("assert");
global.window = global;
require("../smufl-catalog.js");
require("../notation-catalog-core.js");
const audit = global.__LEGATO_CATALOG_AUDIT__;
assert(audit, "catalog audit did not run");
assert.strictEqual(audit.checked, 3451, "every SMuFL entry must be checked");
assert.strictEqual(audit.expected, 3451);
assert.strictEqual(audit.failures.length, 0, "no entry may lack placement, role, kind, or audible routing");
assert.strictEqual(audit.rows.filter(x => x.audible).length, audit.audibleChecked);
assert(audit.rows.every(x => ["note", "event", "span", "structure"].includes(x.placement)), "every entry must use a supported placement path");
assert(audit.rows.every(x => !x.audible || (x.audioRoute && x.audioRoute !== "silent-notation")), "every audible entry must have a playback route");
for (const id of ["coda", "segno", "controlBeginSlur", "controlEndSlur", "controlBeginBeam", "controlEndBeam"]) {
  assert(audit.rows.some(x => String(x.id).toLowerCase().includes(id.toLowerCase())), id + " must exist in the audited catalog");
}
const coda = audit.rows.find(x => String(x.id).toLowerCase().includes("coda") && x.kind === "structure");
assert(coda && coda.placement === "structure", "Coda must use structural placement");
const beams = audit.rows.filter(x => /control(?:Begin|End)Beam/i.test(x.id));
assert(beams.length >= 2 && beams.every(x => x.placement === "note" && x.kind === "beam-control"), "beam controls must attach to notes, not become slurs");
console.log(JSON.stringify({ checked: audit.checked, audibleChecked: audit.audibleChecked, failures: audit.failures.length, byPlacement: audit.byPlacement }, null, 2));
