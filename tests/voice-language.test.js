"use strict";
const assert = require("assert");
const V = require("../legato-voice-language.js");

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }
function one(text, options) {
  const plan = V.parsePlan(text, options);
  assert.strictEqual(plan.commands.length, 1, text);
  return plan.commands[0];
}

test("normalizes music symbols", () => assert.strictEqual(V.normalize("C♯5, B♭3"), "c sharp 5, b flat 3"));
test("converts number words", () => assert.strictEqual(V.replaceNumberWords("tempo one hundred twenty"), "tempo 120"));
test("whole number parser", () => assert.strictEqual(V.wordsToNumber("twenty five"), 25));
test("alias exact replacement", () => assert.strictEqual(V.applyAliases("staccato", { staccato: "place staccato" }), "place staccato"));
test("splits ordered phrases", () => assert.deepStrictEqual(V.splitSegments("undo then play; move right"), ["undo", "play", "move right"]));

[
  ["undo", "undo"], ["redo", "redo"], ["play", "play-toggle"], ["stop playback", "play-toggle"],
  ["delete selection", "delete"], ["open symbols", "command-halo"], ["open menu", "project-menu"],
  ["toggle pointer", "toggle-pointer"], ["copy selection", "copy"], ["paste", "paste"],
  ["next staff", "next-staff"], ["previous staff", "previous-staff"], ["move left", "move-left"],
  ["move right", "move-right"], ["move up", "move-up"], ["move down", "move-down"]
].forEach(([phrase, action]) => test("action " + phrase, () => assert.strictEqual(one(phrase).action, action)));

test("repeated action", () => { const c = one("move right 5 times"); assert.strictEqual(c.count, 5); assert.strictEqual(c.action, "move-right"); });
test("blocks excessive repeat", () => assert.strictEqual(V.parsePlan("move right 17 times").valid, false));
test("tempo", () => assert.strictEqual(one("set tempo to 120").bpm, 120));
test("spoken tempo number", () => assert.strictEqual(one("tempo one hundred twenty").bpm, 120));
test("tempo lower bound", () => assert.strictEqual(V.parsePlan("tempo 10").valid, false));
test("tempo upper bound", () => assert.strictEqual(V.parsePlan("tempo 401").valid, false));
test("write mode", () => assert.strictEqual(one("write mode").mode, 1));
test("engrave mode", () => assert.strictEqual(one("engrave").mode, 2));
test("go to bar and beat", () => { const c = one("go to bar 3 beat 2"); assert.strictEqual(c.bar, 3); assert.strictEqual(c.beat, 2); });
test("select staff", () => assert.strictEqual(one("select staff 4").staff, 4));
test("save project", () => assert.strictEqual(one("save score").operation, "save"));
test("new project", () => assert.strictEqual(one("new score").operation, "new"));
test("open project", () => assert.strictEqual(one("open project").operation, "open"));

test("quarter duration", () => assert.strictEqual(one("select quarter").durationIndex, 2));
test("eighth duration", () => assert.strictEqual(one("use eighth note").durationIndex, 3));
test("32nd duration", () => assert.strictEqual(one("select thirty second").durationIndex, 5));
test("sharp accidental", () => assert.strictEqual(one("select sharp").accidental, "sh"));
test("flat accidental", () => assert.strictEqual(one("flat accidental").accidental, "f"));
test("natural accidental", () => assert.strictEqual(one("use natural").accidental, "n"));

test("quarter rest", () => { const c = one("add quarter rest"); assert.strictEqual(c.type, "rest"); assert.strictEqual(c.durationIndex, 2); });
test("single note", () => { const c = one("add quarter note c sharp 5"); assert.strictEqual(c.type, "note"); assert.strictEqual(c.pitches[0].label, "C♯5"); });
test("note default duration", () => { const c = one("enter d 4"); assert.strictEqual(c.durationIndex, 2); });
test("middle c", () => assert.strictEqual(one("add middle c note").pitches[0].label, "C4"));
test("flat note", () => assert.strictEqual(one("write b flat 3 half note").pitches[0].label, "B♭3"));
test("chord", () => { const c = one("add c 4 e 4 g 4 chord"); assert.strictEqual(c.type, "chord"); assert.strictEqual(c.pitches.length, 3); });
test("chord duration", () => assert.strictEqual(one("add c4 e4 g4 eighth note chord").durationIndex, 3));

test("catalog command", () => { const c = one("place staccato"); assert.strictEqual(c.type, "catalog"); assert.strictEqual(c.query, "staccato"); });
test("catalog command with article", () => assert.strictEqual(one("add a fermata").query, "fermata"));
test("run preview", () => assert.strictEqual(one("run commands").type, "voice-run"));
test("clear preview", () => assert.strictEqual(one("cancel voice plan").type, "voice-clear"));
test("run must be alone", () => assert.strictEqual(V.parsePlan("undo then run commands").valid, false));
test("unknown blocks plan", () => assert.strictEqual(V.parsePlan("undo then purple dinosaur").valid, false));
test("maximum eight commands", () => assert.strictEqual(V.parsePlan(Array(9).fill("undo").join(" then ")).valid, false));
test("eight commands allowed", () => assert.strictEqual(V.parsePlan(Array(8).fill("undo").join(" then ")).valid, true));
test("ordered command plan", () => { const p = V.parsePlan("quarter note then add c 5 then place staccato"); assert.strictEqual(p.commands.length, 3); assert.strictEqual(p.valid, true); });
test("polite wording", () => assert.strictEqual(one("please could you undo that").action, "undo"));
test("pronunciation alias", () => assert.strictEqual(one("stack auto", { aliases: { "stack auto": "place staccato" } }).query, "staccato"));

const glyphs = [
  { id: "articStaccatoAbove", label: "Staccato above", tier: "popular" },
  { id: "articStaccatoBelow", label: "Staccato below", tier: "popular" },
  { id: "articStaccatissimoAbove", label: "Staccatissimo above", tier: "popular" },
  { id: "fermataAbove", label: "Fermata above", tier: "popular" },
  { id: "fermataBelow", label: "Fermata below", tier: "popular" },
  { id: "dynamicForte", label: "Forte", tier: "popular" }
];
test("catalog exact label", () => assert.strictEqual(V.bestCatalogMatch("forte", glyphs).match.id, "dynamicForte"));
test("catalog contained label", () => assert.strictEqual(V.bestCatalogMatch("fermata", glyphs).match.id, "fermataAbove"));
test("catalog chooses default above variant", () => assert.strictEqual(V.bestCatalogMatch("staccato", glyphs).match.id, "articStaccatoAbove"));
test("catalog typo", () => assert.strictEqual(V.bestCatalogMatch("stacatto above", glyphs).match.id, "articStaccatoAbove"));
test("catalog no match", () => assert.strictEqual(V.bestCatalogMatch("purple dinosaur", glyphs).match, null));
test("levenshtein", () => assert.strictEqual(V.levenshtein("staccato", "stacatto"), 2));

let failures = 0;
for (const t of tests) {
  try { t.fn(); console.log("ok - " + t.name); }
  catch (error) { failures++; console.error("not ok - " + t.name); console.error(error.stack || error); }
}
console.log("\n" + (tests.length - failures) + "/" + tests.length + " voice-language tests passed");
if (failures) process.exit(1);
