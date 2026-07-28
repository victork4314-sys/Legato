"use strict";
(() => {
  const VERSION="20260728-theory-playback-2";
  const text=(m,n)=>[m&&m.id,m&&m.label,m&&m.kind,m&&m.range,m&&m.sound,m&&m.pattern,m&&m.effect,m&&m.technique,n].filter(Boolean).join(" ").toLowerCase();
  const percussion=t=>/timpani/.test(t)?"timpani":/wood.?block|clave/.test(t)?"woodblock":/agogo|cowbell/.test(t)?"agogo":/steel drum/.test(t)?"steel_drums":/taiko|bass drum/.test(t)?"taiko_drum":/tom/.test(t)?"melodic_tom":/cymbal|gong/.test(t)?"reverse_cymbal":/bell|triangle/.test(t)?"tinkle_bell":null;
  const intervalSteps=t=>{const m=String(t||"").match(/(?:ascending|descending|asc|desc)[^0-9]*(2nd|3rd|4th|5th|6th|7th|8th)/);if(!m)return 1;return Math.max(1,parseInt(m[1],10)-1);};
  function install(){
    const root=typeof window.__dcRootName==="function"?window.__dcRootName():null,entry=window.__dcRegistry&&root&&window.__dcRegistry[root],p=entry&&entry.Logic&&entry.Logic.prototype;
    if(!p||!p.__catalogRenderAudioPatch)return false;
    if(p.__legatoTheoryPlayback===VERSION)return true;
    const baseArt=p.articulationPlayback;
    p.articulationPlayback=function(n){
      const out=baseArt.call(this,n),t=text(n&&n.noteheadPlayback,n&&n.noteheadPlayback&&n.noteheadPlayback.label);
      if(/dead|muted|cross|slash/.test(t)){out.length=Math.min(out.length,.34);out.gain=Math.min(out.gain,.62);}
      else if(/harmonic|diamond/.test(t)){out.length=Math.max(out.length,1.08);out.gain=Math.min(out.gain,.82);}
      return out;
    };
    const baseTech=p.techniqueInstrument;
    p.techniqueInstrument=function(staff,pos,n,state){
      const s=state||this.state,base=baseTech.call(this,staff,pos,n,s),source=(s.instruments||[])[staff]||base;
      const t=[text(n&&n.noteheadPlayback,n&&n.noteheadPlayback&&n.noteheadPlayback.label),text(n&&n.percussionPlayback,n&&n.percussionPlayback&&n.percussionPlayback.label)].concat((n&&n.catalogMarks||[]).map(x=>text(x.playback,x.name))).join(" ");
      const perc=percussion(t);if(perc)return perc;
      if(/pizz/.test(t)&&/violin|viola|cello|contrabass|string|fiddle/.test(source))return"pizzicato_strings";
      if(/tremolo/.test(t)&&/violin|viola|cello|contrabass|string|fiddle/.test(source))return"tremolo_strings";
      if(/mute|muted|closed|dead/.test(t)&&/trumpet|trombone|horn|brass/.test(source))return"muted_trumpet";
      if(/harmonic|diamond/.test(t)&&/guitar/.test(source))return"guitar_harmonics";
      if(/mute|muted|dead/.test(t)&&/guitar/.test(source))return"electric_guitar_muted";
      return base;
    };
    const baseRealise=p.realise;
    p.realise=function(n,m,when,dur,vel){
      const marks=n&&n.catalogMarks||[],graces=marks.filter(x=>x.audioRoute==="ornament"&&/grace|appoggiatura|acciaccatura/.test(text(x.playback,x.name))),orders=marks.filter(x=>x.audioRoute==="play-order");
      const arp=this.activeScoreSpan&&this.activeScoreSpan("arpeggio-line",n.s,n.p),aeolian=orders.find(x=>/aeolian chord/.test(text(x.playback,x.name))),spread=(arp||aeolian)&&n&&n.chord&&n.chord.length;
      let clean=graces.length?Object.assign({},n,{catalogMarks:marks.filter(x=>graces.indexOf(x)<0)}):n;
      if(spread)clean=Object.assign({},clean,{chord:[]});
      const result=baseRealise.call(this,clean,m,when,dur,vel);
      graces.forEach(mark=>{
        const t=text(mark.playback,mark.name);
        if(/after/.test(t)){this.playTone(m+2,when+Math.max(.03,dur*.82),Math.max(.055,Math.min(.11,dur*.16)),n.s,vel*.72,null);return;}
        const q=Object.assign({},n,{catalogMarks:[],orn:/appoggiatura/.test(t)&&!/acciaccatura|slash/.test(t)?"\uE562":"\uE560",ornPlayback:null,tremoloPlayback:null,pitchPlayback:null,chord:[],tie:true});
        baseRealise.call(this,q,m,when,dur,vel*.82);
      });
      if(spread){
        const source=arp&&arp.playback||aeolian&&aeolian.playback||{},label=arp&&arp.name||aeolian&&aeolian.name||"",t=text(source,label),down=/down|descending|desc\b/.test(t),gap=.052;
        let pitches=(n.chord||[]).map(off=>this.noteMidi(Object.assign({},n,{step:n.step+off,chord:[]}),this.state)).sort((a,b)=>a-b);
        if(down){pitches=pitches.reverse();pitches.forEach((pitch,i)=>this.playTone(pitch,Math.max(this.audio().currentTime+.004,when-(pitches.length-i)*gap),Math.max(.1,dur*.9),n.s,vel*.9,null));}
        else pitches.forEach((pitch,i)=>this.playTone(pitch,when+(i+1)*gap,Math.max(.1,dur*.9),n.s,vel*.9,null));
      }
      orders.filter(x=>x!==aeolian).forEach(mark=>{
        const t=text(mark.playback,mark.name),down=/down|descending|desc\b/.test(t),up=/up|ascending|asc\b/.test(t),steps=intervalSteps(t),targetStep=n.step+(down?-steps:steps),target=this.noteMidi(Object.assign({},n,{step:targetStep,chord:[]}),this.state);
        if(/descending slide/.test(t)){this.playTone(target,Math.max(this.audio().currentTime+.004,when-.075),.09,n.s,vel*.76,null);return;}
        if(/ascending slide/.test(t)){this.playTone(target,Math.max(this.audio().currentTime+.004,when-.075),.09,n.s,vel*.76,null);return;}
        if(down||up)this.playTone(target,when+.055,Math.max(.08,dur*.62),n.s,vel*.78,null);
        else this.playTone(m,when+.055,Math.max(.08,dur*.42),n.s,vel*.62,null);
      });
      const nh=n&&n.noteheadPlayback,t=text(nh,nh&&nh.label);
      if(nh&&nh.audible){
        if(/cluster/.test(t)){[-1,1,2].forEach((x,i)=>this.playTone(m+x,when+i*.008,Math.max(.12,dur*.72),n.s,vel*.58,null));}
        else if(/harmonic|diamond/.test(t))this.playTone(m+12,when+.008,Math.max(.12,dur*.8),n.s,vel*.44,null);
        else if(!/dead|muted|cross|slash/.test(t))this.playTone(m+12,when+.012,Math.min(.16,Math.max(.07,dur*.24)),n.s,vel*.3,null);
      }
      return result;
    };
    Object.defineProperty(p,"__legatoTheoryPlayback",{value:VERSION,configurable:true});
    window.__LEGATO_THEORY_AUDIO_AUDIT__={version:VERSION,graceNotes:"separate grace gesture",noteheads:"dead harmonic cluster and audible optional noteheads",percussion:"catalog family to sampled percussion voice",microtones:"cent offsets through noteMidi",playOrder:"ornament harp chant mensural interval order and arpeggio spans",ok:true};
    return true;
  }
  if(!install()){let n=0,t=setInterval(()=>{if(install()||++n>240)clearInterval(t);},50);}
})();
