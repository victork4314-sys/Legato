"use strict";
// Verification-only branch: this comment triggers the same exhaustive audit without changing runtime code.
// The workflow now preserves the exact assertion output as a downloadable artifact.
const assert = require("assert");
global.window = global;
require("../smufl-catalog.js");
require("../notation-catalog-core.js");

const audit = global.__LEGATO_CATALOG_AUDIT__;
const core = global.__LEGATO_CATALOG_CORE__;
const glyphs = global.LEGATO_SMUFL_CATALOG.glyphs;
const byId = new Map(audit.rows.map(row => [row.id, row]));
const allowedPlacements = new Set(["note", "event", "span", "structure"]);
const allowedAudio = new Set([
  "silent-notation", "pitch", "hold", "dynamic", "hairpin", "glissando",
  "pedal", "octave", "tempo", "slur", "ornament", "tremolo",
  "pitch-effect", "technique", "articulation", "continuous-line",
  "audible-mark", "audible-event"
]);

assert(audit, "catalog audit did not run");
assert(core, "catalog core did not load");
assert.strictEqual(glyphs.length, 3451, "catalog source must contain all 3451 entries");
assert.strictEqual(audit.checked, 3451, "every SMuFL entry must be checked");
assert.strictEqual(audit.expected, 3451);
assert.strictEqual(audit.failures.length, 0, "no entry may lack placement, role, kind, or audible routing");
assert.strictEqual(new Set(glyphs.map(x => x.id)).size, 3451, "every catalog ID must be unique");
assert.strictEqual(byId.size, 3451, "every source entry must have exactly one audit row");
assert.deepStrictEqual(core.NORWEGIAN_KEYS.filter(x => ["æ", "ø", "å"].includes(x)), ["æ", "ø", "å"], "Norwegian letters must be on the keyboard");

for (const source of glyphs) {
  const row = byId.get(source.id);
  assert(row, source.id + " is missing from the audit");
  assert(allowedPlacements.has(row.placement), source.id + " has an unsupported placement");
  assert(row.kind && row.role && row.band, source.id + " lacks a complete engraving profile");
  assert(allowedAudio.has(row.audioRoute), source.id + " has an unsupported audio route");
  assert(!row.audible || row.audioRoute !== "silent-notation", source.id + " is marked audible but has no playback route");

  const sid = String(source.id || "");
  const declared = String(source.placement || "").toLowerCase();
  const isBeamControl = /control(?:Begin|End)Beam/i.test(sid);
  const isTieControl = /control(?:Begin|End)Tie/i.test(sid);
  if (declared === "structure") assert.strictEqual(row.placement, "structure", sid + " must remain structural");
  if (declared === "note") assert.strictEqual(row.placement, "note", sid + " must remain note-attached");
  if (declared === "span" && !isBeamControl && !isTieControl) assert.strictEqual(row.placement, "span", sid + " must remain a span");
  if (/slur|phrase/i.test(sid) && !isBeamControl) assert.strictEqual(row.placement, "span", sid + " must be a span");
  if (isBeamControl) {
    assert.strictEqual(row.placement, "note", sid + " must attach to a note");
    assert.strictEqual(row.kind, "beam-control", sid + " must not become a slur");
  }
  if (String(source.kind).toLowerCase() === "accidental") {
    assert.strictEqual(row.placement, "note", sid + " accidental must attach to a note");
    if (source.audible) assert.strictEqual(row.audioRoute, "pitch", sid + " audible accidental must alter pitch");
  }
  if (row.placement === "structure") assert.strictEqual(row.kind, "structure", sid + " structural entry needs structural semantics");
  if (row.placement === "span") assert.strictEqual(row.role, "span", sid + " span needs two-point semantics");
}

for (const token of ["coda", "segno", "controlBeginSlur", "controlEndSlur", "controlBeginBeam", "controlEndBeam"]) {
  assert(audit.rows.some(x => String(x.id).toLowerCase().includes(token.toLowerCase())), token + " must exist in the audited catalog");
}
const coda = audit.rows.find(x => String(x.id).toLowerCase().includes("coda") && x.kind === "structure");
assert(coda && coda.placement === "structure", "Coda must use structural placement");
assert.strictEqual(audit.rows.filter(x => x.audible).length, audit.audibleChecked, "every audible entry must be counted");

console.log(JSON.stringify({
  checked: audit.checked,
  audibleChecked: audit.audibleChecked,
  failures: audit.failures.length,
  uniqueIds: byId.size,
  norwegianKeys: core.NORWEGIAN_KEYS.filter(x => ["æ", "ø", "å"].includes(x)),
  byPlacement: audit.byPlacement
}, null, 2));
