"use strict";
const assert = require("assert");
global.LegatoVoiceLanguage = require("../legato-voice-language.js");
global.LegatoVoiceControl = require("../legato-voice-control.js");
const F = require("../legato-voice-dictation-fallback.js");

function ownerMock() {
  return {
    state: { staff: 0, pos: 0, bars: 4, players: [{}] },
    barCapacity() { return 4; },
    pitchName(step) { return ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"][step] || ""; }
  };
}

const tests = [];
function test(name, fn) { tests.push({ name, fn }); }

test("detects classic iPad user agent", () => assert.strictEqual(F.isIPadLike({ userAgent: "Mozilla iPad", maxTouchPoints: 5 }), true));
test("detects desktop-style iPad user agent", () => assert.strictEqual(F.isIPadLike({ userAgent: "Mozilla Macintosh", maxTouchPoints: 5 }), true));
test("does not label a Mac as iPad", () => assert.strictEqual(F.isIPadLike({ userAgent: "Mozilla Macintosh", maxTouchPoints: 0 }), false));
test("detects service-not-allowed", () => assert.strictEqual(F.isServiceRefusal("Voice recognition stopped: service-not-allowed."), true));
test("shows fallback for iPad", () => assert.strictEqual(F.shouldShowFallback("Voice control is ready", { userAgent: "iPad", maxTouchPoints: 5 }), true));
test("builds a valid dictated note plan", () => {
  const plan = F.buildDictationPlan("add c4 quarter note", ownerMock(), { glyphs: [] }, {});
  assert.strictEqual(plan.valid, true);
  assert.strictEqual(plan.commands[0].preparedPitches[0].step, 0);
});
test("blocks unknown dictated text", () => {
  const plan = F.buildDictationPlan("purple dinosaur", ownerMock(), { glyphs: [] }, {});
  assert.strictEqual(plan.valid, false);
});
test("requires explicit run button after dictated run phrase", () => {
  const plan = F.buildDictationPlan("run commands", ownerMock(), { glyphs: [] }, {});
  assert.strictEqual(plan.valid, false);
  assert.ok(plan.errors[0].includes("Run commands"));
});
test("applies plan to existing voice state", () => {
  const state = {};
  const plan = { valid: true, commands: [{ label: "Undo" }], errors: [] };
  F.applyPlanToState(state, plan, "undo");
  assert.strictEqual(state.pending, plan);
  assert.strictEqual(state.transcript, "undo");
  assert.ok(state.status.includes("Review"));
});
test("empty dictation is blocked", () => {
  const plan = F.buildDictationPlan("", ownerMock(), { glyphs: [] }, {});
  assert.strictEqual(plan.valid, false);
});

let failures = 0;
for (const item of tests) {
  try { item.fn(); console.log("ok - " + item.name); }
  catch (error) { failures++; console.error("not ok - " + item.name); console.error(error.stack || error); }
}
console.log(`\n${tests.length - failures}/${tests.length} dictation-fallback tests passed`);
if (failures) process.exit(1);
