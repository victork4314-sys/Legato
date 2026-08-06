"use strict";
const assert=require("assert");
global.LegatoLocalSpeechEngine={isIPadLike:n=>/iPad/.test(n.userAgent||"")||(/Macintosh/.test(n.userAgent||"")&&n.maxTouchPoints>1),hasNativeSpeechRecognition:s=>!!(s.SpeechRecognition||s.webkitSpeechRecognition)};
global.LegatoVoiceLanguage={
 normalize:v=>String(v||"").toLowerCase().trim(),
 bestCatalogMatch(q,g){const x=g.find(v=>v.label.toLowerCase().startsWith(q.toLowerCase()));return{match:x||null,ambiguous:false,score:x?1:0};},
 parsePlan(text){
  const t=String(text).toLowerCase().trim();
  if(t==="undo")return{valid:true,errors:[],commands:[{type:"action",action:"undo",count:1,label:"Undo"}]};
  if(t==="tempo 120 then undo")return{valid:true,errors:[],commands:[{type:"tempo",bpm:120,label:"Set tempo to 120"},{type:"action",action:"undo",count:1,label:"Undo"}]};
  if(t==="place fermata")return{valid:true,errors:[],commands:[{type:"catalog",query:"fermata",label:"Place fermata",confidence:.9}]};
  if(t==="run commands")return{valid:true,errors:[],commands:[{type:"voice-run",label:"Run"}]};
  return{valid:false,errors:["No Legato command was recognized."],commands:[{type:"unknown",label:"Unknown"}]};
 }
};
const R=require("../legato-voice-control.js");
function owner(){const calls=[];return{state:{staff:0,pos:0,bars:4,players:[{}]},calls,setState(p,cb){Object.assign(this.state,p);calls.push(["setState",p]);if(cb)cb();},dispatch(a,p){calls.push(["dispatch",a,p]);},setDur(i){calls.push(["dur",i]);},setAcc(a){calls.push(["acc",a]);},barCapacity(){return 4;},pitchName(){return"C4";},enterNote(){calls.push(["note"]);},applyCatalogCommand(g){calls.push(["catalog",g.id]);},saveProject(){},newProject(){}};}
const tests=[];function test(n,f){tests.push({n,f});}
test("valid phrase executes immediately",async()=>{const o=owner();const r=await R.processTranscript(o,"undo",{});assert.strictEqual(r.executed,true);assert.ok(o.calls.some(c=>c[0]==="dispatch"&&c[1]==="undo"));});
test("unknown phrase changes nothing",async()=>{const o=owner();const r=await R.processTranscript(o,"purple",{});assert.strictEqual(r.executed,false);assert.strictEqual(o.calls.length,0);});
test("ordered phrase executes in order",async()=>{const o=owner();const r=await R.processTranscript(o,"tempo 120 then undo",{});assert.strictEqual(r.executed,true);assert.strictEqual(o.state.tempo,120);assert.deepStrictEqual(o.calls.map(c=>c[0]),["setState","dispatch"]);});
test("catalog uses existing placement",async()=>{const o=owner();const r=await R.processTranscript(o,"place fermata",{catalog:{glyphs:[{id:"fermataAbove",label:"Fermata above",glyph:"x"}]}});assert.strictEqual(r.executed,true);assert.ok(o.calls.some(c=>c[0]==="catalog"&&c[1]==="fermataAbove"));});
test("old run command is blocked",async()=>{const o=owner();const r=await R.processTranscript(o,"run commands",{});assert.strictEqual(r.executed,false);assert.strictEqual(o.calls.length,0);});
test("service refusal detection",()=>assert.strictEqual(R.isServiceRefusalError({error:"service-not-allowed"}),true));
test("iPad selects local engine",()=>assert.strictEqual(R.shouldUseLocalEngine({navigator:{userAgent:"iPad",maxTouchPoints:5},webkitSpeechRecognition:function(){}}),true));
test("Mac selects native recognizer",()=>assert.strictEqual(R.shouldUseLocalEngine({navigator:{userAgent:"Macintosh",maxTouchPoints:0},webkitSpeechRecognition:function(){}}),false));
test("runtime has no pending preview state",()=>assert.strictEqual(Object.prototype.hasOwnProperty.call(R.state,"pending"),false));
(async()=>{let fail=0;for(const t of tests){try{await t.f();console.log("ok - "+t.n);}catch(e){fail++;console.error("not ok - "+t.n);console.error(e.stack||e);}}console.log(`\n${tests.length-fail}/${tests.length} immediate-voice tests passed`);if(fail)process.exit(1);})();
