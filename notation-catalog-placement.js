"use strict";
(() => {
  const C = window.__LEGATO_CATALOG_CORE__;
  if (!C) return console.error("[Legato catalog] core missing");
  const { VERSION, NORWEGIAN_KEYS, textOf, canonicalStructure, classify, spanType } = C;

  function noteAtCursor(o) {
    const s=o.state||{};
    return (s.notes||[]).filter(n=>n&&n.s===s.staff&&Math.abs(Number(n.p)-Number(s.pos))<.021).sort((a,b)=>Number(a.rest)-Number(b.rest))[0] || (typeof o.selected==="function"?o.selected():null);
  }
  function noteMark(meta,name,glyph){return{id:(meta.id||"mark")+"-"+Math.random().toString(36).slice(2,8),semanticId:meta.id||name,name:name||meta.label||meta.id||"Symbol",glyph:glyph||meta.glyph||"",kind:meta.kind,band:meta.auditBand,audible:!!meta.audible,playback:Object.assign({},meta),audioRoute:meta.audioRoute};}
  function appendMark(n,m){return(Array.isArray(n.catalogMarks)?n.catalogMarks:[]).concat([m]);}

  function applyNote(o,meta,name,glyph){
    const target=noteAtCursor(o),mark=noteMark(meta,name,glyph);
    const patch=n=>{
      if(meta.auditRole==="replacement"&&meta.kind==="notehead")return{noteheadGlyph:glyph,noteheadSmufl:meta.id,noteheadPlayback:meta};
      if(meta.auditRole==="replacement"&&meta.kind==="percussion")return{noteheadGlyph:glyph,percussionPlayback:meta};
      if(meta.auditRole==="replacement"&&meta.kind==="accidental")return{acc:glyph,accSmufl:meta.id,accCents:meta.cents==null?null:Number(meta.cents)};
      if(meta.kind==="beam-control")return{beam:meta.auditRole==="beam-join"?"join":"break"};
      if(meta.kind==="stem-direction")return{stem:meta.auditRole==="stem-up"?"up":meta.auditRole==="stem-down"?"down":null};
      return{catalogMarks:appendMark(n,mark)};
    };
    if(!target)return o.setState(s=>{const armed=Object.assign({},s.armed||{});
      if(meta.auditRole==="replacement"&&meta.kind==="notehead")Object.assign(armed,{noteheadGlyph:glyph,noteheadSmufl:meta.id,noteheadPlayback:meta});
      else if(meta.auditRole==="replacement"&&meta.kind==="percussion")Object.assign(armed,{noteheadGlyph:glyph,percussionPlayback:meta});
      else if(meta.auditRole==="replacement"&&meta.kind==="accidental")Object.assign(armed,{acc:glyph,accSmufl:meta.id,accCents:meta.cents==null?null:Number(meta.cents)});
      else if(meta.kind==="beam-control")armed.beam=meta.auditRole==="beam-join"?"join":"break";
      else if(meta.kind==="stem-direction")armed.stem=meta.auditRole==="stem-up"?"up":meta.auditRole==="stem-down"?"down":null;
      else armed.catalogMarks=(armed.catalogMarks||[]).concat([mark]);
      return{armed,halo:false,scoreObjectId:null,spoken:mark.name+" armed — the next note gets it"};});
    if(!target.id)target.id="n"+Math.random().toString(36).slice(2,9);
    o.setState(s=>({notes:(s.notes||[]).map(n=>n===target||n.id===target.id?Object.assign({},n,patch(n)):n),halo:false,scoreObjectId:null,selId:target.id,spoken:mark.name+" placed on the note"}),()=>{
      if(meta.audible&&!target.rest&&typeof o.audition==="function"){const changed=(o.state.notes||[]).find(n=>n.id===target.id)||target;try{o.audition(changed.step,changed.s,changed.acc,changed.art,changed);}catch(_){}}
    });
  }

  function placeEvent(o,meta,name,glyph){
    const a=o.scoreAnchor(),type=meta.kind==="dynamic"?"dynamic":meta.kind==="hold"?"hold":meta.kind==="technique"?"technique":meta.kind==="text"?"text":"glyph";
    const ev={id:typeof o.scoreId==="function"?o.scoreId("e"):"e"+Math.random().toString(36).slice(2,9),object:"event",type,name:name||meta.label||meta.id||"Symbol",text:glyph||name||meta.label||meta.id,glyph:glyph||meta.glyph||"",value:glyph||name,s:a.s,p:a.p,step:a.step,system:meta.auditBand==="system",semanticKey:meta.id||name,placement:meta.placement,auditBand:meta.auditBand,offsetY:meta.auditBand==="below"&&type==="glyph"?92:meta.auditBand==="staff"?28:0,smufl:meta.id||null,range:meta.range||null,playback:Object.assign({},meta)};
    o.setState(s=>({scoreEvents:(s.scoreEvents||[]).concat([ev]).sort((x,y)=>x.p-y.p),halo:false,scoreObjectId:ev.id,selId:null,spoken:ev.name+" placed"}));
  }

  function playbackMarkNames(name){return name==="End repeat + Start repeat"?["End repeat","Start repeat"]:[name];}
  function placeStructure(o,meta,name,glyph){
    const a=o.scoreAnchor(),cap=o.barCapacity(),bar=Math.max(0,Math.floor(a.p/cap)),p=bar*cap,nm=canonicalStructure(meta,name);
    const ev={id:typeof o.scoreId==="function"?o.scoreId("e"):"e"+Math.random().toString(36).slice(2,9),object:"event",type:"structure",name:nm,text:glyph||nm,glyph:glyph||meta.glyph||nm,value:nm,s:0,p,step:6,system:true,semanticKey:meta.id||nm,placement:"structure",auditBand:meta.auditBand||"system",smufl:meta.id||null,range:meta.range||null,playback:Object.assign({},meta)};
    o.setState(s=>{const mm=Object.assign({},s.measureMarks||{}),marks=(mm[bar]||[]).slice();playbackMarkNames(nm).forEach((playName,i)=>marks.push({g:i?"":ev.glyph,name:playName,smufl:meta.id||null,eventId:ev.id,hiddenVisual:true}));mm[bar]=marks;return{scoreEvents:(s.scoreEvents||[]).concat([ev]).sort((x,y)=>x.p-y.p),measureMarks:mm,halo:false,scoreObjectId:ev.id,selId:null,spoken:nm+" placed at bar "+(bar+1)};});
  }
  function syncMarks(o){const cap=o.barCapacity(),mm={};(o.state.scoreEvents||[]).filter(e=>e.type==="structure").forEach(e=>{const b=Math.max(0,Math.floor(Number(e.p)/cap));playbackMarkNames(e.name).forEach((playName,i)=>(mm[b]=mm[b]||[]).push({g:i?"":e.glyph||e.text||e.name,name:playName,smufl:e.smufl||null,eventId:e.id,hiddenVisual:true}));});o.setState({measureMarks:mm});}
  function autoCurve(o,d){if(d.curveDirection&&d.curveDirection!=="auto")return d.curveDirection;const n=(o.state.notes||[]).find(n=>!n.rest&&n.s===d.s1&&Math.abs(n.p-d.p1)<.021);if(!n)return"up";const stemUp=n.stem?n.stem==="up":!((n.voice||1)===2||(n.voice||1)===4||n.step>=8);return stemUp?"down":"up";}

  function install(){
    const root=typeof window.__dcRootName==="function"?window.__dcRootName():null,ent=window.__dcRegistry&&root&&window.__dcRegistry[root],p=ent&&ent.Logic&&ent.Logic.prototype;
    if(!p)return false;if(p.__catalogPlacementPatch===VERSION)return true;
    const baseApply=p.applyCatalogCommand,baseMove=p.moveScoreObject,baseDelete=p.deleteScoreObject,baseEdit=p.editSelectedScoreObject,baseFinish=p.finishScoreSpan,baseSelectable=p.scoreSelectableObjects,baseSelectLogical=p.selectLogicalScoreObject,baseDispatch=p.dispatch,baseDeleteSelection=p.deleteSelection,baseSelectNote=p.selectNote,baseSelectObject=p.selectScoreObject;

    p.scoreSelectableObjects=function(state){const s=state||this.state,out=typeof baseSelectable==="function"?baseSelectable.call(this,s):[];(s.notes||[]).forEach(n=>(n.catalogMarks||[]).forEach((m,i)=>out.push({kind:"catalog-note-mark",id:n.id+":catalog:"+m.id,noteId:n.id,catalogMarkId:m.id,staff:n.s,pos:n.p,step:n.step,label:m.name+" · attached symbol "+(i+1)})));return out.sort((a,b)=>a.pos-b.pos||a.staff-b.staff||a.label.localeCompare(b.label));};
    p.selectLogicalScoreObject=function(item){if(item&&item.kind==="catalog-note-mark"){const n=(this.state.notes||[]).find(x=>x.id===item.noteId);if(n&&typeof baseSelectNote==="function")baseSelectNote.call(this,n);return this.setState({panel:null,scoreObjectId:null,selectedChordHead:null,selectedCatalogMark:{noteId:item.noteId,markId:item.catalogMarkId},staff:item.staff,pos:item.pos,step:item.step,spoken:item.label+" selected individually — arrows move it, A flips above or below, B removes it"});}return baseSelectLogical.call(this,item);};
    const patchMark=(o,fn,spoken)=>{const pick=o.state&&o.state.selectedCatalogMark;if(!pick)return false;o.setState(s=>({notes:(s.notes||[]).map(n=>n.id!==pick.noteId?n:Object.assign({},n,{catalogMarks:(n.catalogMarks||[]).map(m=>m.id===pick.markId?Object.assign({},m,fn(m)):m)})),spoken}));return true;};
    const deleteMark=o=>{const pick=o.state&&o.state.selectedCatalogMark;if(!pick)return false;let label="Symbol";o.setState(s=>({notes:(s.notes||[]).map(n=>{if(n.id!==pick.noteId)return n;const found=(n.catalogMarks||[]).find(m=>m.id===pick.markId);if(found)label=found.name;return Object.assign({},n,{catalogMarks:(n.catalogMarks||[]).filter(m=>m.id!==pick.markId)});}),selectedCatalogMark:null,spoken:label+" removed"}));return true;};
    p.dispatch=function(action,phase){if(this.state&&this.state.selectedCatalogMark&&phase!=="release"){if(action==="move-up")return patchMark(this,m=>({offsetY:(m.offsetY||0)-6}),"Attached symbol moved up");if(action==="move-down")return patchMark(this,m=>({offsetY:(m.offsetY||0)+6}),"Attached symbol moved down");if(action==="move-left")return patchMark(this,m=>({offsetX:(m.offsetX||0)-4}),"Attached symbol moved left");if(action==="move-right")return patchMark(this,m=>({offsetX:(m.offsetX||0)+4}),"Attached symbol moved right");if(action==="confirm")return patchMark(this,m=>({band:m.band==="below"?"above":"below",offsetX:0,offsetY:0}),"Attached symbol flipped above or below");if(action==="delete")return deleteMark(this);}return baseDispatch.call(this,action,phase);};
    p.deleteSelection=function(){if(this.state&&this.state.selectedCatalogMark)return deleteMark(this);return baseDeleteSelection.call(this);};
    p.selectNote=function(n){if(this.state&&this.state.selectedCatalogMark)this.setState({selectedCatalogMark:null});return baseSelectNote.call(this,n);};
    p.selectScoreObject=function(id){if(this.state&&this.state.selectedCatalogMark)this.setState({selectedCatalogMark:null});return baseSelectObject.call(this,id);};

    p.applyCatalogCommand=function(meta,name,glyph){const m=classify(meta,name,glyph),t=textOf(m,name);
      if(!m.catalog&&m.legacy&&!/coda|segno|fine|start repeat|end repeat|barline|slur|phrase/.test(t))return baseApply.call(this,m,name,glyph);
      if(m.kind==="key"&&/key signature change/.test(t)&&typeof this.openScoreEventPanel==="function")return this.openScoreEventPanel("key",name||"Key signature",glyph||"");
      if(/^(clef|meter|rest|key)$/.test(m.kind))return baseApply.call(this,m,name,glyph);
      if(m.kind==="tie"&&m.placement!=="span"){if(typeof this.toggleTie==="function")this.toggleTie();return this.setState({halo:false,scoreObjectId:null});}
      if(m.kind==="structure"||m.placement==="structure")return placeStructure(this,m,name,glyph);
      if(m.placement==="span")return this.beginScoreSpan(spanType(m,name),name||m.label||m.id,glyph||m.glyph||"",null,m);
      if(m.placement==="note")return applyNote(this,m,name,glyph);
      return placeEvent(this,m,name,glyph);
    };
    p.finishScoreSpan=function(anchor){const d=this.state&&this.state.spanDraft;if(d&&/^(slur|phrase|tie)$/.test(d.type))d.curveDirection=autoCurve(this,d);return baseFinish.call(this,anchor);};
    p.editSelectedScoreObject=function(){const obj=this.scoreObjectById&&this.scoreObjectById(this.state.scoreObjectId);if(obj&&(obj.object==="span"||obj.p1!=null)&&/^(slur|phrase|tie)$/.test(obj.type)){const next=obj.curveDirection==="down"?"up":"down";this.setState(s=>({scoreSpans:(s.scoreSpans||[]).map(x=>x.id===obj.id?Object.assign({},x,{curveDirection:next}):x),spoken:obj.name+" curved "+(next==="down"?"downwards":"upwards")}));return true;}return baseEdit.call(this);};
    p.moveScoreObject=function(dp,ds){const id=this.state&&this.state.scoreObjectId,obj=id&&this.scoreObjectById&&this.scoreObjectById(id),r=baseMove.call(this,dp,ds);if(obj&&obj.type==="structure"&&Math.abs(dp)>.00001)setTimeout(()=>syncMarks(this),0);return r;};
    p.deleteScoreObject=function(){const id=this.state&&this.state.scoreObjectId,obj=id&&this.scoreObjectById&&this.scoreObjectById(id),r=baseDelete.call(this);if(obj&&obj.type==="structure")setTimeout(()=>syncMarks(this),0);return r;};
    p.kbMove=function(d){this.setState(s=>{const i=Math.max(0,Math.min(NORWEGIAN_KEYS.length-1,s.kbIdx+d));return{kbIdx:i,spoken:NORWEGIAN_KEYS[i]};});};
    p.kbType=function(){const s=this.state,k=NORWEGIAN_KEYS[Math.max(0,Math.min(NORWEGIAN_KEYS.length-1,s.kbIdx))];if(k==="DONE"){if(s.kb==="scoreText")return this.finishScoreObjectText();return this.setState({kb:null,spoken:s.kb+" saved"});}if(k==="DEL")return this.setState(q=>Object.assign({spoken:"Deleted"},{[q.kb]:String(q[q.kb]||"").slice(0,-1)}));const ch=k==="SPACE"?" ":s.kbShift?k.toUpperCase():k;this.setState(q=>Object.assign({spoken:ch===" "?"Space":ch,kbShift:false},{[q.kb]:String(q[q.kb]||"")+ch}));};
    Object.defineProperty(p,"__catalogPlacementPatch",{value:VERSION,configurable:true});return true;
  }
  if(!install()){let n=0,t=setInterval(()=>{if(install()||++n>240)clearInterval(t);},50);}
  window.__LEGATO_CATALOG_PLACEMENT__={version:VERSION,install};
})();
