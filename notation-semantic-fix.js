"use strict";
(() => {
  const VERSION = "20260728-semantic-audio-drag-1";
  const HOLD_MS = 360;
  const canon = (m, n) => {
    const t = [m && m.id, m && m.label, n].filter(Boolean).join(" ").toLowerCase();
    if (/da.?capo|d\.c\./.test(t)) return /coda/.test(t) ? "D.C. al Coda" : /fine/.test(t) ? "D.C. al Fine" : "D.C.";
    if (/dal.?segno|d\.s\./.test(t)) return /coda/.test(t) ? "D.S. al Coda" : /fine/.test(t) ? "D.S. al Fine" : "D.S.";
    if (/to.?coda/.test(t)) return "To Coda";
    if (/coda/.test(t)) return "Coda";
    if (/fine/.test(t)) return "Fine";
    if (/segno/.test(t)) return "Segno";
    if (/start.*repeat|repeat.*start|left repeat/.test(t)) return "Start repeat";
    if (/end.*repeat|repeat.*end|right repeat/.test(t)) return "End repeat";
    return n || (m && m.label) || "Structure";
  };
  const words = (m, n) => [m && m.id, m && m.label, m && m.kind, m && m.sound, m && m.pattern, m && m.effect, m && m.technique, n].filter(Boolean).join(" ").toLowerCase();
  const enrich = (m, n, g) => {
    const x = Object.assign({}, m || {}), t = words(x, n) + " " + (g || "");
    if (/sforz|sfz|rinforz|rfz/.test(t)) { x.kind = "dynamic"; x.velocity = 118; x.sound = "dynamic"; }
    else if (/fortississimo|ffff/.test(t)) { x.kind = "dynamic"; x.velocity = 126; }
    else if (/fff/.test(t)) { x.kind = "dynamic"; x.velocity = 120; }
    else if (/ff/.test(t)) { x.kind = "dynamic"; x.velocity = 110; }
    else if (/\bmf\b/.test(t)) { x.kind = "dynamic"; x.velocity = 68; }
    else if (/\bmp\b/.test(t)) { x.kind = "dynamic"; x.velocity = 46; }
    else if (/ppp/.test(t)) { x.kind = "dynamic"; x.velocity = 20; }
    else if (/pp/.test(t)) { x.kind = "dynamic"; x.velocity = 30; }
    if (/fermata/.test(t)) { x.kind = "hold"; x.sound = "fermata"; x.factor = Number(x.factor) || 2; }
    else if (/caesura/.test(t)) { x.kind = "hold"; x.sound = "hold"; x.seconds = Number(x.seconds) || .6; }
    else if (/breath mark/.test(t)) { x.kind = "hold"; x.sound = "hold"; x.seconds = Number(x.seconds) || .25; }
    if (x.audible && (!x.kind || x.kind === "glyph")) {
      if (/ornament|trill|mordent|turn|grace/.test(t)) x.kind = "ornament";
      else if (/tremolo/.test(t)) x.kind = "tremolo";
      else if (/fall|doit|scoop|bend|smear|slide|pitch/.test(t)) x.kind = "pitch-effect";
      else if (/pizz|mute|harmonic|bow|technique/.test(t)) x.kind = "technique";
      else if (/accent|staccat|tenuto|marcato/.test(t)) x.kind = "articulation";
    }
    return x;
  };
  const noteHere = o => {
    const s = o.state || {};
    return (s.notes || []).filter(n => n.s === s.staff && Math.abs(n.p - s.pos) < .021).sort((a,b) => Number(a.rest)-Number(b.rest))[0] || null;
  };
  const anchorFromPoint = (o, x, y) => {
    const paper = document.querySelector('[data-print-score="true"]');
    if (!paper) return null;
    const r = paper.getBoundingClientRect();
    if (x < r.left || x > r.right || y < r.top || y > r.bottom) return null;
    const sx = paper.offsetWidth && r.width ? paper.offsetWidth / r.width : 1;
    const sy = paper.offsetHeight && r.height ? paper.offsetHeight / r.height : 1;
    const lx = (x-r.left)*sx, ly = (y-r.top)*sy, grid = o.gridBeats(), cap = o.barCapacity();
    const pos = Math.max(0, Math.min(o.state.bars*cap-.001, Math.round(((lx-108)/54)/grid)*grid));
    let staff = Math.max(0, Math.min((o.state.players||[]).length-1, Math.round((ly-136)/88)));
    const top = 112 + staff*88, step = Math.max(-6, Math.min(22, Math.round((48-(ly-top))/6)));
    return {s:staff,p:pos,step};
  };
  const entryAt = (o, cat, idx) => {
    try { return CAT[cat][1][idx]; } catch (_) { return null; }
  };
  const applyAt = (o, e, a) => {
    if (!e || !a) return;
    o.__semanticAnchor = a;
    o.setState({staff:a.s,pos:a.p,step:a.step,selId:null,scoreObjectId:null}, () => {
      try { o.applyCatalogCommand(e[2]||{},e[0],e[1]); } finally { o.__semanticAnchor = null; }
    });
  };
  function installLogic() {
    const root = typeof window.__dcRootName === "function" ? window.__dcRootName() : null;
    const ent = window.__dcRegistry && root && window.__dcRegistry[root];
    const p = ent && ent.Logic && ent.Logic.prototype;
    if (!p) return false;
    if (p.__semanticAudioDrag === VERSION) return true;
    const baseApply = p.applyCatalogCommand, baseAnchor = p.scoreAnchor, baseRender = p.renderVals, baseMove = p.moveScoreObject, baseDispatch = p.dispatch, baseStart = p.startPlayback, baseSchedule = p.schedule;
    p.scoreAnchor = function(){ return this.__semanticAnchor || baseAnchor.call(this); };
    p.applyCatalogCommand = function(meta,name,glyph){
      meta = enrich(meta,name,glyph);
      const placement = String(meta.placement||"").toLowerCase(), kind = String(meta.kind||"").toLowerCase(), t = words(meta,name);
      if (placement === "structure" || /segno|coda|fine|da.?capo|dal.?segno|repeat|barline/.test(t)) {
        const a = this.__semanticAnchor || this.scoreAnchor(), bar = Math.max(0,Math.floor(a.p/this.barCapacity())), nm = canon(meta,name);
        return this.setState(s => { const mm=Object.assign({},s.measureMarks||{}), list=(mm[bar]||[]).filter(x=>String(x.smufl||x.name)!==String(meta.id||nm)); mm[bar]=list.concat([{g:glyph||nm,name:nm,smufl:meta.id,label:name||nm}]); return {measureMarks:mm,halo:false,scoreObjectId:null,selId:null,spoken:nm+" placed at bar "+(bar+1)}; });
      }
      if (placement === "note" && /^(pitch-effect|technique)$/.test(kind)) {
        const n = noteHere(this);
        if (!n) return this.setState(s=>({armed:Object.assign({},s.armed||{},kind==="pitch-effect"?{orn:glyph,pitchPlayback:meta}:{techniqueGlyph:glyph,techniquePlayback:meta}),halo:false,spoken:name+" armed — the next note gets it"}));
        if (!n.id) n.id="n"+Math.random().toString(36).slice(2,8);
        const patch = kind==="pitch-effect"?{orn:glyph,pitchPlayback:meta}:{techniqueGlyph:glyph,techniquePlayback:meta};
        return this.setState({selId:n.id},()=>{this.editNote(patch,name+" applied");this.setState({halo:false,scoreObjectId:null,selId:null});this.audition(n.step,n.s,n.acc,n.art,Object.assign({},n,patch));});
      }
      return baseApply.call(this,meta,name,glyph);
    };
    p.renderVals = function(){
      const v = baseRender.call(this)||{};
      if (Array.isArray(v.scoreEvents)) v.scoreEvents.forEach((x,i)=>{ const e=(this.state.scoreEvents||[])[i]; if(e&&(e.system||/^(structure|system-text|rehearsal|tempo)$/.test(e.type))&&x&&typeof x.style==="string") x.style=x.style.replace(/top:-?\d+(?:\.\d+)?px;/,"top:"+Math.max(8,64+(e.offsetY||0))+"px;"); });
      return v;
    };
    p.moveScoreObject = function(dp,ds){
      const id=this.state.scoreObjectId;
      if(id&&ds&&Math.abs(dp)<.00001){this.setState(s=>({scoreEvents:(s.scoreEvents||[]).map(x=>x.id===id?Object.assign({},x,{offsetY:(x.offsetY||0)+ds*6}):x),scoreSpans:(s.scoreSpans||[]).map(x=>x.id===id?Object.assign({},x,{offsetY:(x.offsetY||0)+ds*6}):x),spoken:((this.scoreObjectById(id,s)||{}).name||"Notation")+" moved"}));return true;}
      return baseMove.call(this,dp,ds);
    };
    p.dispatch = function(action,phase){
      if(this.__heldCatalog && action==="confirm"&&phase==="press"){const e=this.__heldCatalog;this.__heldCatalog=null;applyAt(this,e,{s:this.state.staff,p:this.state.pos,step:this.state.step});return;}
      if(this.state.halo&&action==="confirm"){
        if(phase==="press"){const pads=navigator.getGamepads?Array.from(navigator.getGamepads()).filter(Boolean):[];if(!pads.length)return this.haloApply();clearTimeout(this.__holdTimer);this.__holdReady=false;this.__holdTimer=setTimeout(()=>{this.__holdReady=true;const e=entryAt(this,this.state.haloCat,this.state.haloIdx);this.__heldCatalog=e;this.setState({halo:false,spoken:"Move to any position and press A to place "+(e?e[0]:"the symbol")});},HOLD_MS);return;}
        if(phase==="release"){clearTimeout(this.__holdTimer);if(!this.__holdReady){this.__holdReady=false;return this.haloApply();}this.__holdReady=false;return;}
        return;
      }
      return baseDispatch.call(this,action,phase);
    };
    p.startPlayback = function(){this.__lastPlaySlot=-1;return baseStart.call(this);};
    p.schedule = function(){
      if(this._order&&this._order.length&&this._ac&&this._t0!=null&&this._fired){const beat=this.beatAtElapsed(this._b0,Math.max(0,this._ac.currentTime-this._t0),this.state),slot=Math.floor((beat+.0001)/this.barCapacity());if(slot!==this.__lastPlaySlot){this.__lastPlaySlot=slot;this._fired={};}}
      return baseSchedule.call(this);
    };
    Object.defineProperty(p,"__semanticAudioDrag",{value:VERSION,configurable:true});
    return true;
  }
  function installPointer(){
    if(window.__semanticPointerHold) return; window.__semanticPointerHold=true; let a=null;
    document.addEventListener("pointerdown",e=>{const el=e.target&&e.target.closest&&e.target.closest("[data-halo-item]");const o=window.__legatoOwner;if(!el||!o||!o.state.halo)return;const cat=o.state.haloCat,idx=Number(el.getAttribute("data-halo-item")),entry=entryAt(o,cat,idx);a={o,el,id:e.pointerId,entry,held:false,t:setTimeout(()=>{if(a){a.held=true;o.setState({spoken:"Drag onto the score and release to place "+(entry?entry[0]:"the symbol")});}},HOLD_MS)};},true);
    document.addEventListener("pointermove",e=>{if(a&&a.id===e.pointerId&&a.held)e.preventDefault();},true);
    document.addEventListener("pointerup",e=>{if(!a||a.id!==e.pointerId)return;clearTimeout(a.t);const x=a;a=null;if(!x.held)return;e.preventDefault();e.stopImmediatePropagation();const at=anchorFromPoint(x.o,e.clientX,e.clientY);if(!at)return x.o.setState({spoken:"Release over the score to place the symbol"});x.o.__skipHaloClick=true;applyAt(x.o,x.entry,at);setTimeout(()=>x.o.__skipHaloClick=false,400);},true);
    document.addEventListener("pointercancel",()=>{if(a)clearTimeout(a.t);a=null;},true);
    document.addEventListener("click",e=>{const o=window.__legatoOwner;if(o&&o.__skipHaloClick&&e.target&&e.target.closest&&e.target.closest("[data-halo-item]")){e.preventDefault();e.stopImmediatePropagation();o.__skipHaloClick=false;}},true);
  }
  if(!installLogic()){let n=0,t=setInterval(()=>{if(installLogic()||++n>240)clearInterval(t);},50);} installPointer();
  window.__LEGATO_SEMANTIC_PATCH__={version:VERSION,install:installLogic};
})();
