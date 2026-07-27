"use strict";
(() => {
  const VERSION="20260728-theory-playback-1";
  const text=(m,n)=>[m&&m.id,m&&m.label,m&&m.kind,m&&m.range,m&&m.sound,m&&m.pattern,m&&m.effect,m&&m.technique,n].filter(Boolean).join(" ").toLowerCase();
  const percussion=t=>/timpani/.test(t)?"timpani":/wood.?block|clave/.test(t)?"woodblock":/agogo|cowbell/.test(t)?"agogo":/steel drum/.test(t)?"steel_drums":/taiko|bass drum/.test(t)?"taiko_drum":/tom/.test(t)?"melodic_tom":/cymbal|gong/.test(t)?"reverse_cymbal":/bell|triangle/.test(t)?"tinkle_bell":null;
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
      const marks=n&&n.catalogMarks||[],graces=marks.filter(x=>x.audioRoute==="ornament"&&/grace|appoggiatura|acciaccatura/.test(text(x.playback,x.name)));
      const clean=graces.length?Object.assign({},n,{catalogMarks:marks.filter(x=>graces.indexOf(x)<0)}):n;
      const result=baseRealise.call(this,clean,m,when,dur,vel);
      graces.forEach(mark=>{
        const t=text(mark.playback,mark.name);
        if(/after/.test(t)){this.playTone(m+2,when+Math.max(.03,dur*.82),Math.max(.055,Math.min(.11,dur*.16)),n.s,vel*.72,null);return;}
        const q=Object.assign({},n,{catalogMarks:[],orn:/appoggiatura/.test(t)&&!/acciaccatura|slash/.test(t)?"\uE562":"\uE560",ornPlayback:null,tremoloPlayback:null,pitchPlayback:null,chord:[],tie:true});
        baseRealise.call(this,q,m,when,dur,vel*.82);
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
    window.__LEGATO_THEORY_AUDIO_AUDIT__={version:VERSION,graceNotes:"separate grace gesture",noteheads:"dead harmonic cluster and audible optional noteheads",percussion:"catalog family to sampled percussion voice",microtones:"cent offsets through noteMidi",ok:true};
    return true;
  }
  if(!install()){let n=0,t=setInterval(()=>{if(install()||++n>240)clearInterval(t);},50);}
})();
