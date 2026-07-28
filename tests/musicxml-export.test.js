"use strict";
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

class Logic {
  constructor(state) { this.state = state; }
  barCapacity() { return 4; }
  clefAt(staff) { return (this.state.clefs || [])[staff] || "treble"; }
  keyAt() { return { type: null, n: 0 }; }
  meterAt() { return "4/4"; }
  noteMidi(note) {
    const bass = this.clefAt(note.s) === "bass";
    const tab = bass ? [0, 2, 4, 5, 7, 9, 10] : [0, 1, 3, 5, 7, 8, 10];
    const base = bass ? 43 : 64;
    const index = ((note.step % 7) + 7) % 7;
    let midi = base + Math.floor(note.step / 7) * 12 + tab[index];
    const accidental = { "\uE260": -1, "\uE261": 0, "\uE262": 1, "\uE263": 2, "\uE264": -2 }[note.acc];
    if (accidental != null) midi += accidental;
    if (note.accCents != null) midi += Number(note.accCents) / 100;
    return midi;
  }
}

global.window = {
  __dcRootName: () => "Root",
  __dcRegistry: { Root: { Logic } }
};
global.setInterval = setInterval;
global.clearInterval = clearInterval;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "..", "musicxml-export-fix.js"), "utf8"),
  { filename: "musicxml-export-fix.js" }
);

const state = {
  title: "Export test",
  composer: "Tester",
  tempo: 100,
  bars: 2,
  players: [{ name: "Flute", short: "Fl." }],
  instruments: ["flute"],
  clefs: ["treble"],
  clefOctaves: [0],
  notes: [
    { id: "n1", s: 0, p: 0, d: "q", dots: 1, step: 6, voice: 1 },
    { id: "n2", s: 0, p: 1.5, d: "e", step: 7, chord: [2, 4], voice: 1, art: "\uE4A2" },
    { id: "n3", s: 0, p: 3, d: "q", step: 8, voice: 1, rest: true },
    { id: "n4", s: 0, p: 0, d: "h", step: 2, voice: 2 },
    { id: "n5", s: 0, p: 4, d: "e", dots: 1, tup: 3, step: 9, voice: 1 }
  ],
  scoreEvents: [
    { type: "dynamic", name: "mf", p: 1.5, s: 0 },
    { type: "text", text: "4/4 (q,1+1+1+1)", p: 2, s: 0 },
    { type: "glyph", text: "\uE050", p: 2.5, s: 0 },
    { type: "text", text: "dolce", p: 5, s: 0 }
  ],
  scoreSpans: [],
  measureMarks: {},
  chords: []
};

const doc = new Logic(state).buildMusicXML();
assert(doc.includes("<divisions>10080</divisions>"));
assert(doc.includes("<duration>15120</duration>"), "dotted quarter must advance exactly 1.5 beats");
assert(doc.includes("<duration>5040</duration>"), "dotted eighth triplet must equal half a beat");
assert.strictEqual((doc.match(/<chord\/>/g) || []).length, 2, "three-note chord must have two chord-member tags");
assert(doc.includes("<backup><duration>40320</duration></backup>"), "second voice must restart at the measure beginning");
assert(!doc.includes("4/4 (q,1+1+1+1)"), "debug grouping label must be stripped");
assert(!/[\uE000-\uF8FF]/.test(doc), "SMuFL private-use glyphs must never be exported as words");
assert(!doc.includes("<image") && !doc.includes("<credit"), "no non-musical graphics or comments may be exported");
assert(doc.includes("<words>dolce</words>"), "real musical expression text should remain");
assert.strictEqual((doc.match(/<time>/g) || []).length, 1, "unchanged time signature must not repeat every bar");
assert.strictEqual((doc.match(/<key>/g) || []).length, 1, "unchanged key signature must not repeat every bar");
assert.strictEqual((doc.match(/<rest\/>/g) || []).length, 1, "only the explicit rest may be visible");
assert((doc.match(/<forward>/g) || []).length > 0, "implicit gaps must use invisible forward movement instead of fake rests");
assert(window.__LEGATO_MUSICXML_AUDIT__.ok === true);
console.log("MusicXML export audit passed");
