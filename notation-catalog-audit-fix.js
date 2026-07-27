"use strict";
(() => {
  const VERSION = "20260728-catalog-theory-audio-1";
  const KEYS = ("abcdefghijklmnopqrstuvwxyzæøå0123456789").split("").concat(["É","é","♭","♯",".",",","-","'","SPACE","DEL","DONE"]);
  const EPS = .021;
  const words = (m,n) => [m&&m.id,m&&m.label,m&&m.kind,m&&m.range,m&&m.rangeId,m&&m.group,m&&m.sound,m&&m.pattern,m&&m.effect,m&&m.technique,n].filter(Boolean).join(" ").toLowerCase();
  const here = o => {
    const s=o.state||{};
    return (s.notes||[]).filter(n=>n&&n.s===s.staff&&Math.abs(+n.p-+s.pos)<=EPS).sort((a,b)=>Math.abs(+a.p-+s.pos)-Math.abs(+b.p-+s.pos)||+a.rest-+b.rest)[0]||null;
  };
  const id = p => (p||"m")+Math.random().toString(36).slice(2,10);
  const structural = (m,n) => {
    const t=words(m,n), k=String(m&&m.kind||"").toLowerCase(), p=String(m&&m.placement||"").toLowerCase();
    if(k==="structure"||p==="structure") return true;
    if(/repeat (note|beat|measure)|repeat previous|tremolo repeat/.test(t)) return false;
    return /barline|segno|coda|fine|da\s*capo|dal\s*segno|volta|ending/.test(t);
  };
  const structureName = (m,n) => {
    const t=words(m,n);
    if(/da\s*capo|d\.?\s*c\.?/.test(t)) return /coda/.test(t)?"D.C. al Coda":/fine/.test(t)?"D.C. al Fine":"D.C.";
    if(/dal\s*segno|d\.?\s*s\.?/.test(t)) return /coda/.test(t)?"D.S. al Coda":/fine/.test(t)?"D.S. al Fine":"D.S.";
    if(/to\s*coda/.test(t)) return "To Coda";
    if(/coda/.test(t)) return "Coda";
    if(/segno/.test(t)) return "Segno";
    if(/fine/.test(t)) return "Fine";
    if(/start.*repeat|repeat.*start|left repeat/.test(t)) return "Start repeat";
    if(/end.*repeat|repeat.*end|right repeat/.test(t)) return "End repeat";
    if(/first ending|volta.*1|ending.*1/.test(t)) return "First ending";
    if(/second ending|volta.*2|ending.*2/.test(t)) return "Second ending";
    return n||(m&&m.label)||"Structure";
  };
  const kind = (m,n) => {
    const d=String(m&&m.kind||"").toLowerCase(), t=words(m,n);
    if(structural(m,n)) return "structure";
    if(/begin beam|end beam/.test(t)) return "beam-control";
    if(/phrase/.test(t)) return "phrase";
    if(/\btie\b/.test(t)) return "tie";
    if(/slur/.test(t)) return "slur";
    if(d==="percussion") return /notehead/.test(t)?"notehead":"percussion-mark";
    if(d&&d!=="glyph"&&d!=="text") return d;
    if(/\brest\b/.test(t)&&!/breath/.test(t)) return "rest";
    if(/notehead/.test(t)) return "notehead";
    if(/accidental|sharp|flat|natural|sagittal|helmholtz|comma/.test(t)) return "accidental";
    if(/fermata|breath mark|caesura/.test(t)) return "hold";
    if(/sforz|rinforz|forte|piano|mezzo|dynamic|niente/.test(t)) return "dynamic";
    if(/clef/.test(t)) return "clef";
    if(/time signature|timesig|meter/.test(t)) return "meter";
    if(/hairpin|crescendo|diminuendo|decrescendo|swell/.test(t)) return "hairpin";
    if(/pedal|una corda|tre corde/.test(t)) return "pedal";
    if(/8va|8vb|15ma|15mb|octave line|ottava/.test(t)) return "octave-line";
    if(/gliss/.test(t)) return "gliss";
    if(/portamento/.test(t)) return "portamento";
    if(/let ring/.test(t)) return "let-ring";
    if(/vibrato/.test(t)) return "vibrato";
    if(/ritard|rallent|accelerando|tempo line/.test(t)) return "tempo-span";
    if(/tremolo/.test(t)) return "tremolo";
    if(/ornament|trill|mordent|turn|grace note|appoggiatura|acciaccatura|arpeggio/.test(t)) return "ornament";
    if(/fall|doit|scoop|plop|rip|smear|bend|slide|pitch effect/.test(t)) return "pitch-effect";
    if(/staccat|tenuto|accent|marcato|articulation|stress|unstress/.test(t)) return "articulation";
    if(/up bow|down bow|bowing/.test(t)) return "bowing";
    if(/fingering|finger number/.test(t)) return "fingering";
    if(/lyric|syllable/.test(t)) return "lyrics";
    if(/string number|fret|hand sign|solf[eè]ge/.test(t)) return "note-mark";
    if(/percussion|drum|cymbal|gong|woodblock|mallet/.test(t)) return "percussion-mark";
    if(/playing technique|technique|pizz|mute|harmonic|open string|stopped/.test(t)) return "technique";
    return d||"glyph";
  };
  const spanKind = k => /^(slur|phrase|tie|hairpin|pedal|octave-line|let-ring|vibrato|tempo-span|gliss|portamento)$/.test(k);
  const noteKind = k => /^(notehead|accidental|articulation|ornament|tremolo|pitch-effect|bowing|fingering|lyrics|note-mark|percussion-mark)$/.test(k);
  const placement = (m,k) => {
    const d=String(m&&m.placement||"").toLowerCase();
    if(k==="structure") return "structure";
    if(spanKind(k)||d==="span") return "span";
    if(d==="note"||noteKind(k)) return "note";
    return d||"event";
  };
  const spanType = (o,m,n) => {
    const k=kind(m,n), t=words(m,n);
    if(k==="hairpin") return /down|diminuendo|decrescendo/.test(t)?"hairpin-down":/swell/.test(t)?"hairpin-swell":"hairpin-up";
    if(k==="phrase") return "phrase";
    if(k==="slur") return "slur";
    if(k==="tie") return "tie";
    if(k==="pedal") return "pedal";
    if(k==="portamento") return "portamento";
    if(k==="gliss") return "gliss";
    if(k==="octave-line") return /15mb/.test(t)||+m.semitones===-24?"octave-down-2":/15ma/.test(t)||+m.semitones===24?"octave-up-2":/8vb/.test(t)||+m.semitones<0?"octave-down":"octave-up";
    if(k==="tempo-span") return /accelerando|up/.test(t)?"tempo-up":"tempo-down";
    if(k==="let-ring") return "let-ring";
    if(k==="vibrato") return "vibrato";
    try { return o.catalogSpanType(m); } catch(_) { return "line"; }
  };
  const stemUp = n => n&&n.stem?n.stem==="up":!(n&&(n.voice===2||n.voice===4||+n.step>=8));
  const markPlace = (m,k,note) => {
    const t=words(m,m&&m.label), p=String(m&&(m.position||m.side||m.direction)||"").toLowerCase();
    if(/below/.test(p)||/placement below|below staff/.test(t)) return "below";
    if(/above/.test(p)||/placement above|above staff/.test(t)) return "above";
    if(k==="lyrics") return "below";
    if(k==="articulation") return stemUp(note)?"below":"above";
    if(k==="fingering") return note&&(note.voice===2||note.voice===4)?"below":"above";
    return "above";
  };
  const mark = (m,n,g,k,note) => ({id:id("m"),g:g||n||"□",name:n||(m&&m.label)||"Notation",kind:k,place:markPlace(m,k,note),smufl:m&&m.id||null,playback:Object.assign({},m||{},{kind:k}),offsetX:0,offsetY:0,scale:1,flipped:false,hidden:false});
  const attach = (o,m,n,g,k) => {
    const target=here(o)||(typeof o.selected==="function"?o.selected():null), mk=mark(m,n,g,k,target);
    if(target){
      if(!target.id) target.id=id("n");
      o.editNote(x=>({marks:(x.marks||[]).concat([mk]),artPlayback:k==="articulation"?mk.playback:x.artPlayback,ornPlayback:k==="ornament"?mk.playback:x.ornPlayback,tremoloPlayback:k==="tremolo"?mk.playback:x.tremoloPlayback,pitchPlayback:k==="pitch-effect"?mk.playback:x.pitchPlayback,techniquePlayback:/^(technique|bowing)$/.test(k)?mk.playback:x.techniquePlayback,percussionPlayback:k==="percussion-mark"?mk.playback:x.percussionPlayback}),mk.name+" placed on the note");
      o.setState({halo:false,scoreObjectId:null,selectedNoteMark:{noteId:target.id,markId:mk.id},spoken:mk.name+" placed separately on the note"});
      if(!target.rest&&typeof o.audition==="function") try{const q=Object.assign({},target,{marks:(target.marks||[]).concat([mk])});if(k==="articulation")q.artPlayback=mk.playback;else if(k==="ornament")q.ornPlayback=mk.playback;else if(k==="tremolo")q.tremoloPlayback=mk.playback;else if(k==="pitch-effect")q.pitchPlayback=mk.playback;else if(/^(technique|bowing)$/.test(k))q.techniquePlayback=mk.playback;else if(k==="percussion-mark")q.percussionPlayback=mk.playback;o.audition(target.step,target.s,target.acc,target.art,q);}catch(_){}
    }else o.setState(s=>({armed:Object.assign({},s.armed||{},{marks:((s.armed&&s.armed.marks)||[]).concat([mk])}),halo:false,scoreObjectId:null,spoken:mk.name+" armed separately — the next note gets it"}));
  };
  const structure = (o,m,n,g) => {
    const name=structureName(m,n), bar=Math.floor(o.state.pos/o.barCapacity()), key=(m&&m.id)||name, glyph=g||name;
    o.setState(s=>{const mm=Object.assign({},s.measureMarks||{}), row=(mm[bar]||[]).filter(x=>String(x.smufl||x.name)!==String(key));row.push({g:glyph,name,smufl:key});mm[bar]=row;return{measureMarks:mm};},()=>o.placeScoreEvent("structure",name,glyph,name,{system:true,text:glyph,meta:Object.assign({},m||{},{id:key,kind:"structure",placement:"structure"})}));
  };
  const syncStructures = o => {
    const cap=o.barCapacity(), events=(o.state.scoreEvents||[]), missing=[];
    Object.keys(o.state.measureMarks||{}).forEach(b=>(o.state.measureMarks[b]||[]).forEach((mk,i)=>{const key=String(mk.smufl||mk.name||("mark"+i));if(!events.some(e=>e.type==="structure"&&String(e.smufl||e.name)===key&&Math.floor(+e.p/cap)===+b)) missing.push({id:"mm"+b+"_"+i,object:"event",type:"structure",name:mk.name||"Structure",text:mk.g||mk.name,glyph:mk.g||"",value:mk.name,s:0,p:+b*cap,step:10,system:true,smufl:key,playback:{kind:"structure"}});}));
    if(missing.length)o.setState(s=>({scoreEvents:(s.scoreEvents||[]).concat(missing).sort((a,b)=>+a.p-+b.p)}));
  };
  const audit = () => {
    const list=window.LEGATO_SMUFL_CATALOG&&window.LEGATO_SMUFL_CATALOG.glyphs||[], routes={structure:0,span:0,note:0,event:0}, audible=0;
    list.forEach(m=>{const k=kind(m,m.label),p=placement(m,k);routes[p in routes?p:"event"]++;if(m.audible)audible++;});
    window.__legatoCatalogAudit={version:VERSION,total:list.length,routed:list.length,unrouted:0,audible,routes};
  };
  function install(){
    const root=typeof window.__dcRootName==="function"?window.__dcRootName():null, entry=window.__dcRegistry&&root&&window.__dcRegistry[root], proto=entry&&entry.Logic&&entry.Logic.prototype;
    if(!proto||!proto.__legatoTotalPlacement)return false;
    if(proto.__legatoCatalogAudit===VERSION)return true;
    const apply=proto.applyCatalogCommand;
    proto.applyCatalogCommand=function(m,n,g){
      m=Object.assign({},m||{});const k=kind(m,n),p=placement(m,k);m.kind=k;m.placement=p;
      if(k==="structure")return structure(this,m,n,g);
      if(k==="beam-control"){const target=here(this)||(typeof this.selected==="function"?this.selected():null);if(!target)return this.setState({halo:false,spoken:(n||m.label)+" needs a note at the cursor"});this.editNote({beam:/begin beam/.test(words(m,n))?"join":"break"},(n||m.label)+" applied");return this.setState({halo:false});}
      if(p==="span")return this.beginScoreSpan(spanType(this,m,n),n||m.label,g||m.glyph,null,m);
      if(k==="notehead"||k==="accidental"){
        const target=here(this)||(typeof this.selected==="function"?this.selected():null), patch=k==="notehead"?{noteheadGlyph:g,noteheadSmufl:m.id,noteheadPlayback:m}:{acc:g,accCents:m.cents==null?null:+m.cents,accSmufl:m.id};
        if(target){this.editNote(patch,(n||m.label)+" applied to the note");this.setState({halo:false});if(!target.rest)try{this.audition(target.step,target.s,patch.acc||target.acc,target.art,Object.assign({},target,patch));}catch(_){}}
        else this.setState(s=>({armed:Object.assign({},s.armed||{},patch),halo:false,spoken:(n||m.label)+" armed — the next note gets it"}));
        return;
      }
      if(p==="note"||noteKind(k)||(m.audible&&p==="event"&&!/^(dynamic|hold|tempo|clef|meter|technique)$/.test(k)))return attach(this,m,n,g,k);
      return apply.call(this,m,n,g);
    };
    const halo=proto.haloApply;
    proto.haloApply=function(){const r=halo.apply(this,arguments);setTimeout(()=>syncStructures(this),0);return r;};
    const begin=proto.beginScoreSpan;
    proto.beginScoreSpan=function(type,name,glyph,editing,meta){
      const r=begin.call(this,type,name,glyph,editing,meta);
      if(/^(slur|phrase)$/.test(type)&&this.state.spanDraft){const start=(this.state.notes||[]).find(n=>n.s===this.state.spanDraft.s1&&Math.abs(+n.p-+this.state.spanDraft.p1)<EPS);const forced=/down|below/.test(words(meta,name))?"down":/up|above/.test(words(meta,name))?"up":stemUp(start)?"down":"up";this.setState(s=>({spanDraft:Object.assign({},s.spanDraft,{direction:forced})}));}
      return r;
    };
    const legacy=proto.applyLegacyFallback;
    proto.applyLegacyFallback=function(cat,name,glyph){
      const obj=this.scoreObjectById&&this.scoreObjectById(this.state.scoreObjectId);
      if(cat==="Layout"&&/Flip placement/.test(name)&&obj&&/^(slur|phrase)$/.test(obj.type)){this.patchSelectedScoreObject(x=>({direction:x.direction==="down"?"up":"down",flipped:false}),"Slur direction changed");return this.setState({halo:false});}
      return legacy.apply(this,arguments);
    };
    const selectNote=proto.selectNote;
    proto.selectNote=function(n){if(!this.state.selectedNoteMark||!n||this.state.selectedNoteMark.noteId!==n.id)this.setState({selectedNoteMark:null});return selectNote.apply(this,arguments);};
    const selectObject=proto.selectScoreObject;
    proto.selectScoreObject=function(){this.setState({selectedNoteMark:null});return selectObject.apply(this,arguments);};
    const selectable=proto.scoreSelectableObjects;
    proto.scoreSelectableObjects=function(state){
      const out=selectable.call(this,state),s=state||this.state;
      (s.notes||[]).forEach(n=>(n.marks||[]).forEach((mk,i)=>{const mid=mk.id||(mk.id=id("m"));const old=out.find(x=>x.kind==="note-mark"&&x.noteId===n.id&&x.markIndex===i);if(old){old.markId=mid;old.id=n.id+":mark:"+mid;old.label="Attached symbol "+(mk.name||mk.g||i+1);}else out.push({kind:"note-mark",id:n.id+":mark:"+mid,noteId:n.id,markId:mid,markIndex:i,staff:n.s,pos:n.p,step:n.step,label:"Attached symbol "+(mk.name||mk.g||i+1)});}));
      return out;
    };
    const logical=proto.selectLogicalScoreObject;
    proto.selectLogicalScoreObject=function(item){
      if(item&&item.kind==="note-mark"){const n=(this.state.notes||[]).find(x=>x.id===item.noteId);if(n)selectNote.call(this,n);return this.setState({panel:null,selectedChordHead:null,selectedNoteMark:{noteId:item.noteId,markId:item.markId},spoken:item.label+" selected individually — arrows move it, A flips above or below, B deletes it"});}
      return logical.apply(this,arguments);
    };
    const dispatch=proto.dispatch;
    proto.dispatch=function(action,phase){
      const pick=this.state.selectedNoteMark;
      if(pick&&phase!=="release"){
        const edit=fn=>this.setState(s=>({notes:(s.notes||[]).map(n=>n.id!==pick.noteId?n:Object.assign({},n,{marks:(n.marks||[]).map(m=>m.id!==pick.markId?m:Object.assign({},m,fn(m)))}))}));
        if(action==="move-up")return edit(m=>({offsetY:(m.offsetY||0)-4}));
        if(action==="move-down")return edit(m=>({offsetY:(m.offsetY||0)+4}));
        if(action==="move-left")return edit(m=>({offsetX:(m.offsetX||0)-4}));
        if(action==="move-right")return edit(m=>({offsetX:(m.offsetX||0)+4}));
        if(action==="confirm")return edit(m=>({place:m.place==="below"?"above":"below",flipped:false}));
        if(action==="delete")return this.setState(s=>({notes:(s.notes||[]).map(n=>n.id!==pick.noteId?n:Object.assign({},n,{marks:(n.marks||[]).filter(m=>m.id!==pick.markId)})),selectedNoteMark:null,spoken:"Attached symbol deleted"}));
      }
      return dispatch.apply(this,arguments);
    };
    proto.kbMove=function(d){this.setState(s=>{const i=Math.max(0,Math.min(KEYS.length-1,(s.kbIdx||0)+d));return{kbIdx:i,spoken:KEYS[i]};});};
    proto.kbType=function(){const s=this.state,k=KEYS[s.kbIdx]||KEYS[0];if(k==="DONE"){if(s.kb==="scoreText"&&this.finishScoreObjectText)return this.finishScoreObjectText();return this.setState({kb:null,spoken:(s.kb||"Text")+" saved"});}if(k==="DEL")return this.setState(p=>Object.assign({spoken:"Deleted"},{[p.kb]:(p[p.kb]||"").slice(0,-1)}));const ch=k==="SPACE"?" ":(s.kbShift?k.toUpperCase():k);this.setState(p=>Object.assign({spoken:ch===" "?"Space":ch,kbShift:false},{[p.kb]:(p[p.kb]||"")+ch}));};
    const render=proto.render;
    proto.render=function(){
      const out=render.apply(this,arguments),s=this.state||{};
      if(out&&out.kbKeys)out.kbKeys=KEYS.map((k,i)=>({label:k==="SPACE"?"␣":k==="DEL"?"⌫":(s.kbShift&&k.length===1?k.toUpperCase():k),onSelect:()=>{this.setState({kbIdx:i});this.kbType();},style:"display:grid;place-items:center;min-height:38px;padding:4px 6px;border-radius:5px;cursor:pointer;font-size:"+(k.length>2?10:14)+"px;letter-spacing:.04em;grid-column:"+(k.length>2?"span 2":"span 1")+";border:1px solid "+(s.kbIdx===i?"var(--accent)":"var(--border)")+";background:"+(s.kbIdx===i?"rgba(var(--accent-rgb),.16)":"var(--raised)")+";color:"+(s.kbIdx===i?"var(--text)":"var(--text-2)")+";"}));
      if(out&&out.notes)(s.notes||[]).forEach((n,i)=>{if(!out.notes[i])return;let a=0,b=0;out.notes[i].marks=(n.marks||[]).filter(m=>!m.hidden).map(m=>{const below=(m.flipped?m.place!=="below":m.place==="below"),row=below?b++:a++,top=(below?40+row*15:-34-row*15)+(m.offsetY||0),left=-7+(m.offsetX||0),txt=/^[A-Za-z0-9 .,'’\-]+$/.test(String(m.g||""));return{g:m.g||m.name,style:"position:absolute;left:"+left+"px;top:"+top+"px;z-index:7;white-space:nowrap;color:var(--ink);transform:scale("+(m.scale||1)+");transform-origin:center;font-family:"+(txt?"var(--ui-font)":"Bravura,'Noto Music',serif")+";font-size:"+(txt?12:27)+"px;font-style:"+(txt?"italic":"normal")+";"};});});
      if(out&&out.measureMarks)out.measureMarks=[];
      if(out&&out.scoreEvents)(s.scoreEvents||[]).forEach((ev,i)=>{if(!out.scoreEvents[i]||ev.type!=="structure")return;let st=String(out.scoreEvents[i].style).replace(/font-family:[^;]+;/,"font-family:Bravura,'Noto Music',serif;").replace(/font-size:[^;]+;/,"font-size:30px;");if(/repeat|barline/.test(String(ev.name||"").toLowerCase()))st=st.replace(/top:([\-\d.]+)px/,(_,v)=>"top:"+(+v+42)+"px").replace(/font-size:[^;]+;/,"font-size:48px;");out.scoreEvents[i].style=st;});
      if(out&&out.scoreSpans)(s.scoreSpans||[]).forEach((sp,i)=>{if(!out.scoreSpans[i]||!/^(slur|phrase)$/.test(sp.type))return;const down=sp.direction==="down";if(down){out.scoreSpans[i].wrapStyle=String(out.scoreSpans[i].wrapStyle).replace(/top:([\-\d.]+)px/,(_,v)=>"top:"+(+v+82)+"px");out.scoreSpans[i].line1Style=String(out.scoreSpans[i].line1Style).replace(/border-color:[^;]+;/,"border-color:transparent transparent var(--ink) transparent;").replace(/border-radius:[^;]+;/,"border-radius:0 0 50% 50%;");}});
      return out;
    };
    const articulation=proto.articulationPlayback;
    proto.articulationPlayback=function(n){const base=articulation.call(this,n),marks=(n&&n.marks||[]).filter(x=>x.kind==="articulation"&&x.playback);marks.forEach(x=>{const t=words(x.playback,x.name);if(/staccatissimo/.test(t))base.length=Math.min(base.length,.28);else if(/staccato/.test(t))base.length=Math.min(base.length,.48);if(/marcato/.test(t))base.gain=Math.max(base.gain,1.38);else if(/accent|stress/.test(t))base.gain=Math.max(base.gain,1.25);if(/tenuto/.test(t))base.length=Math.max(base.length,1.04);});return base;};
    const realise=proto.realise;
    proto.realise=function(n,m,w,d,v){
      const r=realise.apply(this,arguments), active=[n&&n.ornPlayback&&n.ornPlayback.id,n&&n.tremoloPlayback&&n.tremoloPlayback.id,n&&n.pitchPlayback&&n.pitchPlayback.id];
      (n&&n.marks||[]).filter(x=>x.playback&&x.playback.audible&&!/^(articulation|technique|bowing|percussion-mark)$/.test(x.kind)&&active.indexOf(x.playback.id)<0).forEach(x=>{if(/^(ornament|tremolo|pitch-effect)$/.test(x.kind)){const q=Object.assign({},n,{orn:null,ornPlayback:null,tremoloPlayback:null,pitchPlayback:null,chord:[],tie:true});if(x.kind==="ornament")q.ornPlayback=x.playback;else if(x.kind==="tremolo")q.tremoloPlayback=x.playback;else q.pitchPlayback=x.playback;realise.call(this,q,m,w,d,v*.78);}else this.playTone(m,w+.035,Math.min(.14,d*.24),n.s,v*.55,null);});
      return r;
    };
    const mounted=proto.componentDidMount;
    proto.componentDidMount=function(){const r=mounted&&mounted.apply(this,arguments);setTimeout(()=>syncStructures(this),0);return r;};
    Object.defineProperty(proto,"__legatoCatalogAudit",{value:VERSION,configurable:true});
    audit();
    return true;
  }
  if(!install()){let n=0,t=setInterval(()=>{if(install()||++n>240)clearInterval(t);},50);}
})();
