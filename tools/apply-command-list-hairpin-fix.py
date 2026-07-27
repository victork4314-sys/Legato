from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)


replace_once('<meta name="legato-build" content="20260727-notation-objects-2">', '<meta name="legato-build" content="20260727-command-list-hairpins-1">', 'build meta')
replace_once('<script src="./cache-refresh.js?v=20260727-notation-objects-2"></script>', '<script src="./cache-refresh.js?v=20260727-command-list-hairpins-1"></script>', 'cache refresh version')
replace_once('<script src="./support.js?v=20260727-notation-objects-2"></script>', '<script src="./support.js?v=20260727-command-list-hairpins-1"></script>', 'support version')

replace_once("['Tempo text','Allegro']", "['Tempo change','♩ = 120']", 'tempo command label')
replace_once("['Key signature','\\uE262\\uE260']", "['Key signature change','\\uE262\\uE260']", 'key command label')
replace_once("['Time signature','\\uE09E']", "['Time signature change','\\uE09E']", 'meter command label')
replace_once("['Accelerando','accel.']]]", "['Accelerando','accel.'],['Horizontal line','—']]]", 'horizontal line command')
replace_once("if (/Tempo text/.test(name)) { this.openScoreEventPanel('tempo', 'Tempo', glyph); return; }", "if (/Tempo (?:text|change)/.test(name)) { this.openScoreEventPanel('tempo', 'Tempo', glyph); return; }", 'tempo handler')

replace_once('data-ptr="{{ c.name }}" style="{{ c.style }}"', 'data-ptr="{{ c.name }}" data-halo-category="{{ c.index }}" style="{{ c.style }}"', 'halo category DOM marker')
replace_once('data-ptr="{{ h.name }}" style="{{ h.style }}"', 'data-ptr="{{ h.name }}" data-halo-item="{{ h.index }}" style="{{ h.style }}"', 'halo item DOM marker')

replace_once("""  haloMove(dx, dy) {
    this.setState(s => {
      const list = CAT[s.haloCat][1], cols = 4;
      let i = s.haloIdx + dx + dy * cols;
      i = Math.max(0, Math.min(list.length - 1, i));
      return { haloIdx: i, spoken: list[i][0] + ' — ' + CAT[s.haloCat][0] };
    });
  }
  haloCategory(d) {
    this.setState(s => {
      const c = (s.haloCat + d + CAT.length) % CAT.length;
      return { haloCat: c, haloIdx: 0, spoken: CAT[c][0] + ', ' + CAT[c][1].length + ' commands' };
    });
  }
""", """  revealHaloSelection() {
    requestAnimationFrame(() => {
      const item = document.querySelector('[data-halo-item="' + this.state.haloIdx + '"]');
      const category = document.querySelector('[data-halo-category="' + this.state.haloCat + '"]');
      if (item && item.scrollIntoView) item.scrollIntoView({ block: 'nearest', inline: 'nearest' });
      if (category && category.scrollIntoView) category.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    });
  }
  haloMove(dx, dy) {
    this.setState(s => {
      const list = CAT[s.haloCat][1], cols = 4;
      let i = s.haloIdx + dx + dy * cols;
      i = Math.max(0, Math.min(list.length - 1, i));
      return { haloIdx: i, spoken: list[i][0] + ' — ' + CAT[s.haloCat][0] };
    }, () => this.revealHaloSelection());
  }
  haloCategory(d) {
    this.setState(s => {
      const c = (s.haloCat + d + CAT.length) % CAT.length;
      return { haloCat: c, haloIdx: 0, spoken: CAT[c][0] + ', ' + CAT[c][1].length + ' commands' };
    }, () => this.revealHaloSelection());
  }
""", 'controller command scrolling')

replace_once("""      haloCats: CAT.map((c, i) => ({
        name: c[0], count: c[1].length,
        onSelect: () => this.setState({ haloCat: i, haloIdx: 0, spoken: c[0] }),
        style: 'display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 11px;border-radius:5px;cursor:pointer;font-size:13px;border:1px solid ' + (s.haloCat === i ? accent : 'transparent') + ';background:' + (s.haloCat === i ? 'rgba(var(--accent-rgb),.1)' : 'transparent') + ';color:' + (s.haloCat === i ? 'var(--text)' : 'var(--muted)') + ';'
      })),
      haloItems: CAT[s.haloCat][1].map((c, i) => ({
        name: c[0], glyph: c[1],
        onSelect: () => { this.setState({ haloIdx: i }); this.haloApply(); },
        style: 'display:flex;align-items:center;gap:10px;padding:9px 11px;border-radius:6px;cursor:pointer;min-height:52px;border:1px solid ' + (s.haloIdx === i ? accent : 'var(--border)') + ';background:' + (s.haloIdx === i ? 'rgba(var(--accent-rgb),.13)' : 'var(--raised)') + ';',
""", """      haloCats: CAT.map((c, i) => ({
        index: i, name: c[0], count: c[1].length,
        onSelect: () => this.setState({ haloCat: i, haloIdx: 0, spoken: c[0] }, () => this.revealHaloSelection()),
        style: 'display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 11px;border-radius:5px;cursor:pointer;font-size:13px;border:1px solid ' + (s.haloCat === i ? accent : 'transparent') + ';background:' + (s.haloCat === i ? 'rgba(var(--accent-rgb),.1)' : 'transparent') + ';color:' + (s.haloCat === i ? 'var(--text)' : 'var(--muted)') + ';'
      })),
      haloItems: CAT[s.haloCat][1].map((c, i) => ({
        index: i, name: c[0], glyph: c[1],
        onSelect: () => this.setState({ haloIdx: i }, () => this.haloApply()),
        style: 'display:flex;align-items:center;gap:10px;padding:9px 11px;border-radius:6px;cursor:pointer;min-height:52px;border:1px solid ' + (s.haloIdx === i ? accent : 'var(--border)') + ';background:' + (s.haloIdx === i ? 'rgba(var(--accent-rgb),.13)' : 'var(--raised)') + ';',
""", 'halo render focus and click ordering')

replace_once("return { text: text2, ptr: (ev.name || ev.type) + ' at the cursor', onSelect: () => this.selectScoreObject(ev.id), style:", "return { text: text2, ptr: (ev.name || ev.type) + ' at the cursor', onSelect: (e) => { if (e && e.stopPropagation) e.stopPropagation(); this.selectScoreObject(ev.id); }, style:", 'point-event selection')

replace_once("""          else if (sp.type.indexOf('hairpin') === 0) { top = st1.top + 65; h = 22; const up = sp.type !== 'hairpin-down'; const swell = sp.type === 'hairpin-swell'; line1 = base + 'top:10px;width:' + (swell ? width / 2 : width) + 'px;height:1.5px;background:' + accent2 + ';transform:rotate(' + (up ? -7 : 7) + 'deg);'; line2 = base + 'top:10px;width:' + (swell ? width / 2 : width) + 'px;height:1.5px;background:' + accent2 + ';transform:rotate(' + (up ? 7 : -7) + 'deg);' + (swell ? 'left:' + width / 2 + 'px;' : ''); }
""", """          else if (sp.type.indexOf('hairpin') === 0) {
            top = st1.top + 62; h = 30;
            const swell = sp.type === 'hairpin-swell';
            const outer = swell ? 'polygon(0 50%,50% 0,100% 50%,50% 100%)' : (sp.type === 'hairpin-down' ? 'polygon(0 0,100% 50%,0 100%)' : 'polygon(0 50%,100% 0,100% 100%)');
            const inner = swell ? 'polygon(0 50%,50% 20%,100% 50%,50% 80%)' : (sp.type === 'hairpin-down' ? 'polygon(0 20%,100% 50%,0 80%)' : 'polygon(0 50%,100% 20%,100% 80%)');
            line1 = base + 'top:7px;width:' + width + 'px;height:16px;background:' + accent2 + ';clip-path:' + outer + ';pointer-events:none;';
            line2 = base + 'top:7px;width:' + width + 'px;height:16px;background:var(--paper);clip-path:' + inner + ';pointer-events:none;';
          }
""", 'fixed-opening hairpin geometry')

replace_once("""          return { ptr: (sp.name || sp.type) + (sp.preview ? ' point two preview' : ' from point one to point two'), onSelect: () => { if (!sp.preview) this.selectScoreObject(sp.id); }, wrapStyle: 'position:absolute;left:' + x1 + 'px;top:' + top + 'px;width:' + width + 'px;height:' + h + 'px;z-index:11;cursor:pointer;' + selectedStyle, line1Style: line1 || 'display:none;', line2Style: line2 || 'display:none;', label: label, end: end, labelStyle: label ? 'position:absolute;left:0;top:0;font-family:var(--ui-font);font-size:13px;font-style:italic;font-weight:600;color:' + accent2 + ';white-space:nowrap;' : 'display:none;', endStyle: end ? 'position:absolute;right:-2px;top:2px;font-family:var(--ui-font);font-size:15px;color:' + accent2 + ';' : 'display:none;' };
""", """          return { ptr: (sp.name || sp.type) + (sp.preview ? ' point two preview' : ' from point one to point two'), onSelect: (e) => { if (e && e.stopPropagation) e.stopPropagation(); if (!sp.preview) this.selectScoreObject(sp.id); }, wrapStyle: 'position:absolute;left:' + x1 + 'px;top:' + top + 'px;width:' + width + 'px;height:' + h + 'px;z-index:11;cursor:pointer;touch-action:manipulation;' + selectedStyle, line1Style: line1 || 'display:none;', line2Style: line2 || 'display:none;', label: label, end: end, labelStyle: label ? 'position:absolute;left:0;top:0;font-family:var(--ui-font);font-size:13px;font-style:italic;font-weight:600;color:' + accent2 + ';white-space:nowrap;pointer-events:none;' : 'display:none;', endStyle: end ? 'position:absolute;right:-2px;top:2px;font-family:var(--ui-font);font-size:15px;color:' + accent2 + ';pointer-events:none;' : 'display:none;' };
""", 'saved span selection hit area')

path.write_text(text, encoding='utf-8')
print('Command-list, scrolling, hairpin and selection repairs applied')
