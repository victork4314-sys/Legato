"use strict";
const assert = require("assert");
const { webcrypto } = require("crypto");
const E = require("../legato-local-speech-engine.js");

const tests=[]; function test(name,fn){tests.push({name,fn});}

test("detects classic iPad",()=>assert.strictEqual(E.isIPadLike({userAgent:"Mozilla iPad",maxTouchPoints:5}),true));
test("detects desktop user agent on touch iPad",()=>assert.strictEqual(E.isIPadLike({userAgent:"Mozilla Macintosh",maxTouchPoints:5}),true));
test("does not detect Mac",()=>assert.strictEqual(E.isIPadLike({userAgent:"Mozilla Macintosh",maxTouchPoints:0}),false));
test("detects native recognizer",()=>assert.strictEqual(E.hasNativeSpeechRecognition({webkitSpeechRecognition:function(){}}),true));
test("downsamples 48k to 16k",()=>{const input=new Float32Array(480);for(let i=0;i<input.length;i++)input[i]=i;const out=E.downsampleTo16k(input,48000);assert.strictEqual(out.length,160);assert.ok(out[0]>0&&out[0]<3);});
test("copies 16k audio",()=>{const input=new Float32Array([1,2]);const out=E.downsampleTo16k(input,16000);assert.deepStrictEqual(Array.from(out),[1,2]);assert.notStrictEqual(out,input);});
test("rolling audio is bounded",()=>{const a=new Float32Array([1,2,3]);const b=new Float32Array([4,5,6]);assert.deepStrictEqual(Array.from(E.appendRollingAudio(a,b,4)),[3,4,5,6]);});
test("transcript waits for stability",()=>{const g=new E.TranscriptGate({stableMs:500,dedupeMs:2000});assert.strictEqual(g.observe("undo",0),null);assert.strictEqual(g.observe("undo",499),null);assert.strictEqual(g.observe("undo",500),"undo");});
test("transcript dedupes",()=>{const g=new E.TranscriptGate({stableMs:1,dedupeMs:2000});g.observe("undo",0);assert.strictEqual(g.observe("undo",1),"undo");g.observe("undo",100);assert.strictEqual(g.observe("undo",101),null);});
test("sha verification",async()=>{const buffer=new TextEncoder().encode("Legato").buffer;const hash=await E.sha256Hex(buffer,webcrypto);assert.strictEqual(hash.length,64);await E.verifySHA256(buffer,hash,webcrypto);});
test("sha mismatch rejects",async()=>{let threw=false;try{await E.verifySHA256(new Uint8Array([1]).buffer,"0".repeat(64),webcrypto);}catch(_){threw=true;}assert.ok(threw);});
test("engine lifecycle stops tracks and audio",async()=>{
  let stopped=0,closed=0,disconnected=0;
  const intervals=new Map();let id=0;
  const scope={crossOriginIsolated:true,setInterval(fn){const n=++id;intervals.set(n,fn);return n;},clearInterval(n){intervals.delete(n);},setTimeout,clearTimeout,crypto:webcrypto};
  const module={FS_unlink(){},FS_createDataFile(){},init(){return 1;},set_audio(){},get_transcribed(){return "";}};
  const node=()=>({connect(){},disconnect(){disconnected++;}});
  const processor=Object.assign(node(),{onaudioprocess:null});
  const context={sampleRate:48000,state:"running",destination:{},createMediaStreamSource:node,createScriptProcessor(){return processor;},createGain(){return {gain:{value:1},connect(){},disconnect(){disconnected++;}};},async close(){closed++;}};
  const stream={getTracks(){return[{stop(){stopped++;}}];}};
  const engine=new E.LocalWhisperEngine({scope,navigator:{mediaDevices:{}},module,modelLoader:async()=>new Uint8Array([1,2]).buffer,getUserMedia:async()=>stream,audioContextFactory:()=>context});
  await engine.start();assert.strictEqual(engine.running,true);assert.strictEqual(intervals.size,2);
  await engine.stop();assert.strictEqual(engine.running,false);assert.strictEqual(stopped,1);assert.strictEqual(closed,1);assert.strictEqual(intervals.size,0);assert.ok(disconnected>=2);
});

(async()=>{let fail=0;for(const t of tests){try{await t.fn();console.log("ok - "+t.name);}catch(e){fail++;console.error("not ok - "+t.name);console.error(e.stack||e);}}console.log(`\n${tests.length-fail}/${tests.length} local-speech tests passed`);if(fail)process.exit(1);})();
