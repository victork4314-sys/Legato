"use strict";
(() => {
  const VERSION="20260728-catalog-hotfix-bridge-1";
  function install(){
    const root=typeof window.__dcRootName==="function"?window.__dcRootName():null;
    const entry=window.__dcRegistry&&root&&window.__dcRegistry[root];
    const p=entry&&entry.Logic&&entry.Logic.prototype;
    if(!p||(!p.__catalogRenderAudioPatch&&!p.__catalogPlacementPatch))return false;
    if(!p.__legatoCatalogRouting)Object.defineProperty(p,"__legatoCatalogRouting",{value:VERSION,configurable:true});
    return true;
  }
  if(!install()){let n=0,t=setInterval(()=>{if(install()||++n>240)clearInterval(t);},50);}
})();
