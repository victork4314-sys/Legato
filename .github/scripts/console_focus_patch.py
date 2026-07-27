from pathlib import Path
p=Path('index.html'); s=p.read_text()
def span(name):
 m='\n  '+name+'('; a=s.find(m)
 if a<0: raise SystemExit('missing '+name)
 b=s.find('{',a); d=0; q=None; esc=False; i=b
 while i<len(s):
  c=s[i]
  if q:
   if esc: esc=False
   elif c=='\\': esc=True
   elif c==q: q=None
  else:
   if c in "'\"`": q=c
   elif c=='{': d+=1
   elif c=='}':
    d-=1
    if d==0:return a+1,i+1
  i+=1
 raise SystemExit('unclosed '+name)
def repl(name,new):
 global s
 a,b=span(name); s=s[:a]+new+s[b:]
repl('visibleScanItems',"""  visibleScanItems() {
    const all = Array.from(document.querySelectorAll('[data-ptr]')).filter(el => {
      if (el.offsetParent === null || el.closest('[data-scroll=\"score\"]')) return false;
      if (el.getAttribute('aria-hidden') === 'true' || el.getAttribute('aria-disabled') === 'true') return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
    return all.filter(el => !all.some(other => other !== el && el.contains(other)));
  }""")
repl('zoneScanItems',"""  zoneScanItems(zone) {
    return this.visibleScanItems().filter(el => {
      if (zone === 1) return !!el.closest('[data-scroll=\"players\"]');
      if (zone === 2) return !!el.closest('[data-scroll=\"toolbar\"]');
      if (zone === 4) return !!el.closest('[data-scroll=\"props\"]');
      if (zone === 0) return !el.closest('[data-scroll=\"players\"],[data-scroll=\"toolbar\"],[data-scroll=\"props\"]') && el.getBoundingClientRect().top < 125;
      return false;
    });
  }""")
extra="""  scanZoneForElement(el) {
    if (el.closest('[data-scroll=\"players\"]')) return 1;
    if (el.closest('[data-scroll=\"toolbar\"]')) return 2;
    if (el.closest('[data-scroll=\"props\"]')) return 4;
    return 0;
  }
  consoleScanOrder() {
    const zones = this.state.sidebarsHidden ? [0,2] : [0,1,2,4];
    return zones.reduce((out,z)=>out.concat(this.zoneScanItems(z)),[]);
  }
  focusDomItem(el) {
    if (!el) return;
    document.querySelectorAll('[data-scan-selected=\"true\"]').forEach(x=>x.removeAttribute('data-scan-selected'));
    el.setAttribute('data-scan-selected','true');
    const zone=this.scanZoneForElement(el), list=this.zoneScanItems(zone), focus=Math.max(0,list.indexOf(el));
    this._domScanIndex=Math.max(0,this.consoleScanOrder().indexOf(el));
    this.reveal(el);
    const spoken=el.getAttribute('data-ptr')||el.getAttribute('aria-label')||(el.textContent||'').trim()||'Item';
    this.setState({zone,focus,spoken});
  }
  moveConsoleFocus(dx,dy) {
    const items=this.visibleScanItems(); if(!items.length)return;
    let cur=document.querySelector('[data-scan-selected=\"true\"]');
    if(!cur||items.indexOf(cur)<0)cur=this.zoneScanItems(this.state.zone)[this.state.focus]||items[0];
    const r=cur.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;
    const cand=items.filter(x=>x!==cur).map(el=>{const a=el.getBoundingClientRect(),x=a.left+a.width/2,y=a.top+a.height/2,px=x-cx,py=y-cy;const ok=dx?(dx>0?px>4:px<-4):(dy>0?py>4:py<-4);if(!ok)return null;const pri=dx?Math.abs(px):Math.abs(py),sec=dx?Math.abs(py):Math.abs(px);return{el,score:pri+sec*2.4};}).filter(Boolean).sort((a,b)=>a.score-b.score);
    if(cand.length)this.focusDomItem(cand[0].el);
  }\n"""
a,b=span('syncGlobalSelection')
s=s[:a]+extra+"""  syncGlobalSelection() {
    const selected=document.querySelector('[data-scan-selected=\"true\"]'), visible=this.visibleScanItems();
    if(selected&&visible.indexOf(selected)>=0)return;
    document.querySelectorAll('[data-scan-selected=\"true\"]').forEach(el=>el.removeAttribute('data-scan-selected'));
    if(this.state.zone===3)return;
    const list=this.zoneScanItems(this.state.zone); if(!list.length)return;
    const el=list[Math.max(0,Math.min(list.length-1,this.state.focus))]; el.setAttribute('data-scan-selected','true'); this.reveal(el);
  }"""+s[b:]
repl('advanceAutoScan',"""  advanceAutoScan() {
    if (!this.state.autoScan || this.anyOverlay() || this.state.ptrOn) return;
    const items=this.consoleScanOrder(); if(!items.length)return;
    let i=(this._domScanIndex==null?-1:this._domScanIndex)+1;
    if(i>=items.length){this._domScanIndex=-1;return this.setState({mode:(this.state.mode+1)%6,zone:0,focus:0},()=>requestAnimationFrame(()=>this.advanceAutoScan()));}
    this._domScanIndex=i; this.focusDomItem(items[i]);
  }""")
repl('moveFocus',"""  moveFocus(d) { this.moveConsoleFocus(0,d); }""")
repl('adjustFocus',"""  adjustFocus(d) { this.moveConsoleFocus(d,0); }""")
a,b=span('activateFocus'); seg=s[a:b]
if 'data-scan-selected' not in seg:
 brace=s.find('{',a,b); ins="\n    const liveTarget=document.querySelector('[data-scan-selected=\"true\"]');\n    if(liveTarget&&this.state.zone!==3){liveTarget.click();return;}"
 s=s[:brace+1]+ins+s[brace+1:]
old='./support.js?v=20260727-real-dom-scan-1'; new='./support.js?v=20260727-console-focus-1'
if s.count(old)!=1: raise SystemExit('cache anchor')
s=s.replace(old,new,1)
for x in ['moveConsoleFocus(dx,dy)','data-scroll=\"props\"','console-focus-1']:
 if x not in s: raise SystemExit('missing '+x)
p.write_text(s)
