from pathlib import Path

# Apply all prior guarded passes.
source = Path('tools/apply_complete_library_v4.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/apply_complete_library_v4.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)


helper = r'''  patchSelectedScoreObject(patch, label) {
    const id = this.state.scoreObjectId;
    if (!id) return false;
    this.setState(s => ({
      scoreEvents: (s.scoreEvents || []).map(x => x.id === id ? Object.assign({}, x, typeof patch === 'function' ? patch(x) : patch) : x),
      scoreSpans: (s.scoreSpans || []).map(x => x.id === id ? Object.assign({}, x, typeof patch === 'function' ? patch(x) : patch) : x),
      spoken: label
    }));
    return true;
  }
  applyLegacyFallback(cat, name, glyph) {
    const s = this.state, note = this.selected(), object = this.scoreObjectById(s.scoreObjectId);
    if (cat === 'Layout') {
      if (/Nudge left/.test(name)) { if (object) this.moveScoreObject(-this.gridBeats(), 0); else if (note) this.editNote({ p: Math.max(0, note.p - this.gridBeats()) }, 'Note nudged left'); }
      else if (/Nudge right/.test(name)) { if (object) this.moveScoreObject(this.gridBeats(), 0); else if (note) this.editNote({ p: Math.min(s.bars * this.barCapacity() - .001, note.p + this.gridBeats()) }, 'Note nudged right'); }
      else if (/Nudge up/.test(name)) { if (object) this.patchSelectedScoreObject(x => ({ offsetY: (x.offsetY || 0) - 4 }), 'Notation nudged up'); else if (note) this.movePitch(1); }
      else if (/Nudge down/.test(name)) { if (object) this.patchSelectedScoreObject(x => ({ offsetY: (x.offsetY || 0) + 4 }), 'Notation nudged down'); else if (note) this.movePitch(-1); }
      else if (/More spacing/.test(name)) this.setState(p => ({ spacing: Math.min(180, p.spacing + 5), spoken: 'Score spacing expanded' }));
      else if (/Less spacing/.test(name)) this.setState(p => ({ spacing: Math.max(50, p.spacing - 5), spoken: 'Score spacing tightened' }));
      else if (/Scale up/.test(name)) { if (object) this.patchSelectedScoreObject(x => ({ scale: Math.min(2.5, (x.scale || 1) + .1) }), 'Notation scaled up'); else if (note) this.editNote(n => ({ scale: Math.min(2.5, (n.scale || 1) + .1) }), 'Note scaled up'); }
      else if (/Scale down/.test(name)) { if (object) this.patchSelectedScoreObject(x => ({ scale: Math.max(.35, (x.scale || 1) - .1) }), 'Notation scaled down'); else if (note) this.editNote(n => ({ scale: Math.max(.35, (n.scale || 1) - .1) }), 'Note scaled down'); }
      else if (/Hide item/.test(name)) { if (object) this.patchSelectedScoreObject({ hidden: true }, 'Notation hidden — still available in SELECT'); else if (note) this.editNote({ hidden: true }, 'Note hidden — still available in SELECT'); }
      else if (/Show item/.test(name)) { if (object) this.patchSelectedScoreObject({ hidden: false }, 'Notation shown'); else if (note) this.editNote({ hidden: false }, 'Note shown'); }
      else if (/Flip placement/.test(name)) { if (object) this.patchSelectedScoreObject(x => ({ flipped: !x.flipped }), 'Notation placement flipped'); else if (note) this.editNote(n => ({ flipped: !n.flipped }), 'Note attachment placement flipped'); }
      else if (/Reset position/.test(name)) { const reset = { offsetX: 0, offsetY: 0, scale: 1, flipped: false, hidden: false }; if (object) this.patchSelectedScoreObject(reset, 'Notation position reset'); else if (note) this.editNote(reset, 'Note position reset'); }
      else if (/Move to staff above/.test(name)) { if (object) this.moveScoreObject(0, -1); else if (note) this.editNote({ s: Math.max(0, note.s - 1) }, 'Note moved to staff above'); }
      else if (/Move to staff below/.test(name)) { if (object) this.moveScoreObject(0, 1); else if (note) this.editNote({ s: Math.min(s.players.length - 1, note.s + 1) }, 'Note moved to staff below'); }
      else if (/Show voice color/.test(name)) this.setState(p => ({ showVoiceColor: !p.showVoiceColor, spoken: p.showVoiceColor ? 'Voice colors hidden' : 'Voice colors shown' }));
      else this.placeScoreEvent('glyph', name, glyph, glyph, { system: false, text: glyph || name });
      return this.setState({ halo: false });
    }
    if (note && glyph) {
      this.editNote(n => ({ marks: (n.marks || []).concat([{ g: glyph, name: name, place: 'above' }]) }), name + ' placed on the selected note');
      return this.setState({ halo: false });
    }
    this.placeScoreEvent('glyph', name, glyph, glyph, { system: false, text: glyph || name });
  }
'''
replace_once('  haloApply() {', helper + '  haloApply() {', 'real legacy fallback helper')
replace_once(
"    this.setState({ halo: false, spoken: name + ' applied' });\n  }\n  commitWheel() {",
"    this.applyLegacyFallback(cat, name, glyph);\n  }\n  commitWheel() {",
    'remove fake final command fallback'
)

# Hidden and transformed notation remains saved and selector-reachable.
replace_once("          if (st.hidden) return {", "          if (st.hidden || n.hidden) return {", 'hidden note rendering')
replace_once(
"wrapStyle: 'position:absolute;left:' + noteX(n.p) + 'px;top:' + top + 'px;width:0;height:0;',",
"wrapStyle: 'position:absolute;left:' + (noteX(n.p) + (n.offsetX || 0)) + 'px;top:' + (top + (n.offsetY || 0)) + 'px;width:0;height:0;transform:scale(' + (n.scale || 1) + ');transform-origin:center;',",
    'note transform rendering'
)
replace_once(
"        return { text: text2, ptr: (ev.name || ev.type) + ' at the cursor', onSelect: (e) => { if (e && e.stopPropagation) e.stopPropagation(); this.selectScoreObject(ev.id); }, style: 'position:absolute;left:' + left + 'px;top:' + top + 'px;z-index:12;cursor:pointer;color:var(--ink);white-space:nowrap;font-family:' + family + ';font-size:' + size + 'px;line-height:1;' + extra + sel };",
"        return { text: text2, ptr: (ev.name || ev.type) + ' at the cursor', onSelect: (e) => { if (e && e.stopPropagation) e.stopPropagation(); this.selectScoreObject(ev.id); }, style: ev.hidden ? 'display:none;' : 'position:absolute;left:' + (left + (ev.offsetX || 0)) + 'px;top:' + (top + (ev.offsetY || 0)) + 'px;z-index:12;cursor:pointer;color:var(--ink);white-space:nowrap;font-family:' + family + ';font-size:' + size + 'px;line-height:1;transform:scale(' + (ev.scale || 1) + ')' + (ev.flipped ? ' scaleY(-1)' : '') + ';transform-origin:center;' + extra + sel };",
    'event transform rendering'
)
replace_once(
"wrapStyle: 'position:absolute;left:' + x1 + 'px;top:' + top + 'px;width:' + width + 'px;height:' + h + 'px;z-index:11;cursor:pointer;touch-action:manipulation;' + selectedStyle,",
"wrapStyle: sp.hidden ? 'display:none;' : 'position:absolute;left:' + (x1 + (sp.offsetX || 0)) + 'px;top:' + (top + (sp.offsetY || 0)) + 'px;width:' + width + 'px;height:' + h + 'px;z-index:11;cursor:pointer;touch-action:manipulation;transform:scale(' + (sp.scale || 1) + ')' + (sp.flipped ? ' scaleY(-1)' : '') + ';transform-origin:left center;' + selectedStyle,",
    'span transform rendering'
)

if "spoken: name + ' applied' });\n  }\n  commitWheel()" in text:
    raise SystemExit('Fake final command fallback remains')

path.write_text(text, encoding='utf-8')
print('Real legacy fallback and layout actions applied')
