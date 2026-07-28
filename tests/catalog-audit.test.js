"use strict";
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
  "play-order", "audible-mark", "audible-event"
]);
const sourceById = id => glyphs.find(x => x.id === id);
const rowById = id => byId.get(id);

assert(audit, "catalog audit did not run");
assert(core, "catalog core did not load");
assert.strictEqual(glyphs.length, 3451, "catalog source must contain all 3451 entries");
assert.strictEqual(audit.checked, 3451, "every SMuFL entry must be checked");
assert.strictEqual(audit.expected, 3451);
assert.strictEqual(audit.failures.length, 0, "no entry may lack placement, role, kind, or audible routing");
assert.strictEqual(new Set(glyphs.map(x => x.id)).size, 3451, "every catalog ID must be unique");
assert.strictEqual(byId.size, 3451, "every source entry must have exactly one audit row");
assert.deepStrictEqual(core.NORWEGIAN_KEYS.filter(x => ["æ", "ø", "å"].includes(x)), ["æ", "ø", "å"], "Norwegian letters must be on the keyboard");

const sourceStructures = glyphs.filter(x => String(x.kind).toLowerCase() === "structure" && String(x.placement).toLowerCase() === "structure");
const scoreStructures = sourceStructures.filter(x => core.isScoreStructure(x, x.label));
const compositeStructures = sourceStructures.filter(x => core.isCompositePlayOrder(x, x.label));
const structureNoteMarks = sourceStructures.filter(x => core.isStructureNoteMark(x, x.label));
assert.strictEqual(sourceStructures.length, 93, "all source structure records must be accounted for");
assert.strictEqual(scoreStructures.length, 36, "all genuine score-position structures must be identified");
assert.strictEqual(compositeStructures.length, 56, "all note-level play-order structures must be identified");
assert.strictEqual(structureNoteMarks.length, 1, "the lyric repeat symbol must be separated from score playback");
assert.strictEqual(scoreStructures.length + compositeStructures.length + structureNoteMarks.length, sourceStructures.length, "no structure record may be ambiguous");

for (const source of glyphs) {
  const row = byId.get(source.id);
  const sid = String(source.id || "");
  const declared = String(source.placement || "").toLowerCase();
  const beamControl = /control(?:Begin|End)Beam/i.test(sid);
  const tieControl = /control(?:Begin|End)Tie/i.test(sid);
  const explicitlyNoSlur = /no.?slur|without.?slur/i.test(sid);
  const composite = core.isCompositePlayOrder(source, source.label);
  const score = core.isScoreStructure(source, source.label) && String(source.kind).toLowerCase() === "structure";
  const structureMark = core.isStructureNoteMark(source, source.label);

  assert(row, sid + " is missing from the audit");
  assert(allowedPlacements.has(row.placement), sid + " has an unsupported placement");
  assert(row.kind && row.role && row.band, sid + " lacks a complete engraving profile");
  assert(allowedAudio.has(row.audioRoute), sid + " has an unsupported audio route");
  assert(!row.audible || row.audioRoute !== "silent-notation", sid + " is marked audible but has no playback route");

  if (structureMark) {
    assert.strictEqual(row.placement, "note", sid + " lyric repeat must attach below a note");
    assert.strictEqual(row.kind, "note-mark", sid + " lyric repeat must use note-mark semantics");
    assert.strictEqual(row.band, "below", sid + " lyric repeat must sit below the staff");
    assert.strictEqual(row.audible, false, sid + " lyric repeat is engraving, not repeated music");
  } else if (composite) {
    assert.strictEqual(row.placement, "note", sid + " composite structure must attach to a note");
    assert.strictEqual(row.kind, "play-order", sid + " composite structure must use play-order semantics");
    assert.strictEqual(row.audioRoute, "play-order", sid + " composite structure must be audible in sequence");
  } else if (score) {
    assert.strictEqual(row.placement, "structure", sid + " score structure must remain structural");
    assert.strictEqual(row.kind, "structure", sid + " score structure needs score-structure semantics");
    if (core.isAudibleScoreStructure(source, source.label)) {
      assert.strictEqual(row.audible, true, sid + " complete navigation structure must affect playback");
      assert.strictEqual(row.audioRoute, "play-order", sid + " navigation structure must route playback order");
    } else {
      assert.strictEqual(row.audible, false, sid + " visual barline component must remain silent");
      assert.strictEqual(row.audioRoute, "silent-notation", sid + " visual barline component must not fake sound");
    }
  } else {
    if (declared === "note") assert.strictEqual(row.placement, "note", sid + " must remain note-attached");
    if (declared === "span" && !beamControl && !tieControl) assert.strictEqual(row.placement, "span", sid + " must remain a span");
    if (declared === "event") assert.strictEqual(row.placement, "event", sid + " must remain an event");
  }

  if (/slur|phrase/i.test(sid) && !explicitlyNoSlur && !beamControl && !tieControl) assert.strictEqual(row.placement, "span", sid + " must be a span");
  if (beamControl) {
    assert.strictEqual(row.placement, "note", sid + " must attach to a note");
    assert.strictEqual(row.kind, "beam-control", sid + " must not become a slur");
    assert.strictEqual(row.audible, false, sid + " is an engraving control, not a performed sound");
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
assert(coda && coda.placement === "structure" && coda.audioRoute === "play-order", "Coda must use audible structural placement");
assert.strictEqual(core.canonicalStructure({id:"repeatRightLeftThick",label:"Repeat Right Left Thick"}, "Repeat Right Left Thick"), "End repeat + Start repeat", "combined repeats must build both playback boundaries");
assert.strictEqual(core.canonicalStructure({id:"repeat2Bars",label:"Repeat last two bars"}, "Repeat last two bars"), "Repeat previous 2 bars", "two-bar repeat must have block playback semantics");
assert.strictEqual(audit.rows.filter(x => x.kind === "play-order").length, 56, "all composite play-order symbols must be routed");
assert.strictEqual(audit.rows.filter(x => x.audible).length, audit.audibleChecked, "every audible entry must be counted");

const noSlurRip = rowById("tripleTongueAboveNoSlur");
assert(noSlurRip, "tripleTongueAboveNoSlur must exist in the audit");
assert.strictEqual(noSlurRip.placement, "note", "No Slur triple tonguing must remain note-attached");
assert.strictEqual(noSlurRip.kind, "pitch-effect", "No Slur triple tonguing must keep its Bravura rip effect");
assert.strictEqual(noSlurRip.audioRoute, "pitch-effect", "No Slur triple tonguing must sound as a rip, not as legato");
const printableTie = rowById("textTie");
assert(printableTie, "textTie must exist in the audit");
assert.strictEqual(printableTie.placement, "event", "Printable text tie must remain an event");
assert.strictEqual(printableTie.kind, "text", "Printable text tie must remain text");
assert.strictEqual(printableTie.audioRoute, "silent-notation", "Printable text tie must remain silent engraving");

const organTieSource = sourceById("organGermanTie");
const tieControlSource = sourceById("controlBeginTie");
assert(organTieSource, "organGermanTie must exist in the catalog");
assert(tieControlSource, "controlBeginTie must exist in the catalog");
const organTie = core.classify(organTieSource, organTieSource.label, organTieSource.glyph);
const tieControl = core.classify(tieControlSource, tieControlSource.label, tieControlSource.glyph);
assert.strictEqual(organTie.kind, "tie", "organ German tie must keep tie semantics");
assert.strictEqual(organTie.placement, "span", "organ German tie must remain a full two-point span");
assert.strictEqual(core.spanType(organTie, organTie.label), "tie", "organ German tie must build a tie curve");
assert.strictEqual(tieControl.kind, "tie", "Begin Tie control must use tie semantics");
assert.strictEqual(tieControl.placement, "note", "Begin Tie control must stay a note-entry command");

class PlacementHarness {
  constructor() {
    this.state = { notes: [], players: [{}], staff: 0, pos: 0, step: 6, bars: 4, measureMarks: {}, scoreEvents: [], scoreSpans: [], armed: {} };
    this.spanCalls = [];
    this.tieCalls = 0;
  }
  setState(update, callback) { const patch = typeof update === "function" ? update(this.state) : update; this.state = Object.assign({}, this.state, patch || {}); if (callback) callback(); }
  selected() { return null; }
  scoreAnchor() { return { s: 0, p: 0, step: 6 }; }
  scoreId(prefix) { return (prefix || "x") + "1"; }
  barCapacity() { return 4; }
  beginScoreSpan() { this.spanCalls.push(Array.from(arguments)); return true; }
  toggleTie() { this.tieCalls += 1; }
  applyCatalogCommand() { this.baseApplyCalled = true; }
  scoreSelectableObjects() { return []; }
  selectLogicalScoreObject() {}
  dispatch() {}
  deleteSelection() {}
  selectNote() {}
  selectScoreObject() {}
  moveScoreObject() {}
  deleteScoreObject() {}
  editSelectedScoreObject() {}
  finishScoreSpan() { return true; }
}
global.__dcRootName = () => "catalog-test";
global.__dcRegistry = { "catalog-test": { Logic: PlacementHarness } };
require("../notation-catalog-placement.js");
const fullTieHarness = new PlacementHarness();
fullTieHarness.applyCatalogCommand(organTieSource, organTieSource.label, organTieSource.glyph);
assert.strictEqual(fullTieHarness.tieCalls, 0, "full tie glyph must not invoke note tie entry");
assert.strictEqual(fullTieHarness.spanCalls.length, 1, "full tie glyph must start one span");
assert.strictEqual(fullTieHarness.spanCalls[0][0], "tie", "full tie glyph must start a tie span");
const controlTieHarness = new PlacementHarness();
controlTieHarness.applyCatalogCommand(tieControlSource, tieControlSource.label, tieControlSource.glyph);
assert.strictEqual(controlTieHarness.tieCalls, 1, "Begin Tie control must invoke note tie entry once");
assert.strictEqual(controlTieHarness.spanCalls.length, 0, "Begin Tie control must not create a free span");

console.log(JSON.stringify({
  checked: audit.checked,
  audibleChecked: audit.audibleChecked,
  failures: audit.failures.length,
  uniqueIds: byId.size,
  scoreStructures: scoreStructures.length,
  compositePlayOrder: compositeStructures.length,
  structureNoteMarks: structureNoteMarks.length,
  norwegianKeys: core.NORWEGIAN_KEYS.filter(x => ["æ", "ø", "å"].includes(x)),
  noSlurRip: noSlurRip.audioRoute,
  tieRouting: { fullSpan: fullTieHarness.spanCalls.length, entryControl: controlTieHarness.tieCalls },
  byPlacement: audit.byPlacement
}, null, 2));
