"use strict";
const assert = require("assert");
global.LegatoVoiceLanguage = require("../legato-voice-language.js");
const R = require("../legato-voice-control.js");
const V = global.LegatoVoiceLanguage;

function ownerMock() {
  const calls = [];
  const o = {
    state: { staff: 0, pos: 0, bars: 8, players: [{}, {}], dur: 2, acc: "n", entry: "note" },
    calls,
    setState(patch, cb) { Object.assign(this.state, typeof patch === "function" ? patch(this.state) : patch); calls.push(["setState", patch]); if (cb) cb(); },
    dispatch(action, phase) { calls.push(["dispatch", action, phase]); },
    setDur(index) { this.state.dur = index; calls.push(["setDur", index]); },
    setAcc(value) { this.state.acc = value; calls.push(["setAcc", value]); },
    barCapacity() { return 4; },
    pitchName(step) { return ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"][step] || ""; },
    enterNote() { calls.push(["enterNote", this.state.step, this.state.pos, this.state.dur, this.state.acc, this.state.entry]); this.state.pos += [4,2,1,.5,.25,.125][this.state.dur] || 1; },
    applyCatalogCommand(meta, name, glyph) { calls.push(["catalog", meta.id, name, glyph]); },
    saveProject() { calls.push(["save"]); },
    newProject() { calls.push(["new"]); }
  };
  return o;
}

const tests=[]; function test(name, fn){tests.push({name,fn});}

test("pitch base strips accidental",()=>assert.strictEqual(R.pitchBase("C♯5"),"C5"));
test("finds pitch step",()=>assert.strictEqual(R.pitchStep(ownerMock(),{letter:"E",octave:4},0,0),2));
test("resolves catalog",()=>{const r=R.resolveCatalogCommand({type:"catalog",query:"fermata",label:"Place fermata",confidence:.9},[{id:"fermataAbove",label:"Fermata above",glyph:"x"}]);assert.strictEqual(r.command.glyph.id,"fermataAbove");});
test("unknown catalog blocks plan",()=>{const o=ownerMock();const p=R.preparePlan(o,V.parsePlan("place purple dinosaur"),{glyphs:[]});assert.strictEqual(p.valid,false);});
test("prepares note pitch",()=>{const o=ownerMock();const p=R.preparePlan(o,V.parsePlan("add e4 quarter note"),{glyphs:[]});assert.strictEqual(p.valid,true);assert.strictEqual(p.commands[0].preparedPitches[0].step,2);});
test("prepares ordered staff context",()=>{const o=ownerMock();const p=R.preparePlan(o,V.parsePlan("staff 2 then add c4"),{glyphs:[]});assert.strictEqual(p.valid,true);assert.strictEqual(p.commands[1].preparedPitches[0].step,0);});
test("executes repeated action",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"action",action:"move-right",count:3});assert.strictEqual(o.calls.filter(c=>c[0]==="dispatch").length,3);});
test("executes duration",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"duration",durationIndex:4});assert.strictEqual(o.state.dur,4);});
test("executes accidental",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"accidental",accidental:"sh"});assert.strictEqual(o.state.acc,"sh");});
test("executes tempo",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"tempo",bpm:140,label:"Tempo"});assert.strictEqual(o.state.tempo,140);});
test("executes goto",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"goto",bar:3,beat:2,label:"Go"});assert.strictEqual(o.state.pos,9);});
test("executes staff bounded",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"staff",staff:9});assert.strictEqual(o.state.staff,1);});
test("executes rest",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"rest",durationIndex:1});const call=o.calls.find(c=>c[0]==="enterNote");assert.strictEqual(call[5],"rest");});
test("executes note",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"note",durationIndex:2,preparedPitches:[{letter:"E",octave:4,accidental:"natural",label:"E4",step:2}]});const call=o.calls.find(c=>c[0]==="enterNote");assert.strictEqual(call[1],2);});
test("executes chord at one position",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"chord",durationIndex:2,preparedPitches:[{label:"C4",step:0,accidental:"natural"},{label:"E4",step:2,accidental:"natural"},{label:"G4",step:4,accidental:"natural"}]});const calls=o.calls.filter(c=>c[0]==="enterNote");assert.deepStrictEqual(calls.map(c=>c[2]),[0,0,0]);assert.strictEqual(o.state.pos,1);});
test("executes catalog",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"catalog",glyph:{id:"fermataAbove",label:"Fermata above",glyph:"x"}});assert.strictEqual(o.calls.find(c=>c[0]==="catalog")[1],"fermataAbove");});
test("executes project save",async()=>{const o=ownerMock();await R.executeCommand(o,{type:"project",operation:"save"});assert.ok(o.calls.some(c=>c[0]==="save"));});
test("rejects invalid plan",async()=>{let threw=false;try{await R.executePlan(ownerMock(),{valid:false,errors:["blocked"],commands:[]});}catch(e){threw=true;}assert.ok(threw);});
test("executes complete plan in order",async()=>{const o=ownerMock();const p=R.preparePlan(o,V.parsePlan("tempo 120 then move right 2 times"),{glyphs:[]});assert.strictEqual(p.valid,true);await R.executePlan(o,p);assert.strictEqual(o.state.tempo,120);assert.strictEqual(o.calls.filter(c=>c[0]==="dispatch").length,2);});

(async()=>{let fail=0;for(const t of tests){try{await t.fn();console.log("ok - "+t.name);}catch(e){fail++;console.error("not ok - "+t.name);console.error(e.stack||e);}}console.log(`\n${tests.length-fail}/${tests.length} voice-runtime tests passed`);if(fail)process.exit(1);})();
