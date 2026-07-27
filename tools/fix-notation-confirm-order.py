from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')

marker = "if (s.scoreObjectId && action === 'delete') return this.deleteScoreObject();"
if marker in t and "if (s.scoreObjectId && action === 'confirm') return this.editSelectedScoreObject();" in t:
    print('Exclusive notation controller priority already repaired')
    raise SystemExit(0)

release = "    if (phase === 'release') { if (action === 'select-modifier') this._mod = false; return; }\n"
early = release + """    if (s.spanDraft && action === 'confirm') return this.finishScoreSpan();
    if (s.tieFrom && action === 'confirm') {
      const target = this.selected();
      if (target && target.id !== s.tieFrom) return this.finishTie(target);
      return this.setState({ spoken: 'Tie point two is waiting for A — move to the immediately following note of the same pitch' });
    }
    if (s.scoreObjectId && action === 'confirm') return this.editSelectedScoreObject();
    if (s.tieFrom && action === 'delete') return this.setState({ tieFrom: null, spoken: 'Tie cancelled' });
    if (s.spanDraft && action === 'delete') return this.cancelScoreSpan();
    if (s.scoreObjectId && action === 'delete') return this.deleteScoreObject();
"""
if t.count(release) != 1:
    raise SystemExit(f'dispatch release marker: expected 1 match, found {t.count(release)}')
t = t.replace(release, early, 1)

old_confirm = """      case 'confirm':
        if (P) { this.clickPointer(); break; }
        if (s.spanDraft) { this.finishScoreSpan(); break; }
        if (s.scoreObjectId) { this.editSelectedScoreObject(); break; }
        if (s.tieFrom) {
          const target = this.selected();
          if (target && target.id !== s.tieFrom) this.finishTie(target);
          else this.setState({ spoken: 'Tie point two is waiting for A — move to the immediately following note of the same pitch' });
          break;
        }
        this.enterNote(); break;
"""
reordered_confirm = """      case 'confirm':
        if (s.spanDraft) { this.finishScoreSpan(); break; }
        if (s.tieFrom) {
          const target = this.selected();
          if (target && target.id !== s.tieFrom) this.finishTie(target);
          else this.setState({ spoken: 'Tie point two is waiting for A — move to the immediately following note of the same pitch' });
          break;
        }
        if (P) { this.clickPointer(); break; }
        if (s.scoreObjectId) { this.editSelectedScoreObject(); break; }
        this.enterNote(); break;
"""
clean_confirm = """      case 'confirm':
        if (P) { this.clickPointer(); break; }
        this.enterNote(); break;
"""
if old_confirm in t:
    t = t.replace(old_confirm, clean_confirm, 1)
elif reordered_confirm in t:
    t = t.replace(reordered_confirm, clean_confirm, 1)
else:
    raise SystemExit('confirm switch block not found')

old_begin = """    this.setState({ spanDraft: { object: 'span', id: editing || this.scoreId('s'), editing: editing || null, type: type, name: name, glyph: glyph || '', s1: start.s, p1: start.p, step1: start.step, system: type === 'ending' || type.indexOf('tempo-') === 0 }, scoreObjectId: null, halo: false, panel: null, selId: null,
      staff: start.s, pos: start.p, step: start.step, spoken: name + ' point one set — move to point two and press A' });
"""
new_begin = """    this.setState({ spanDraft: { object: 'span', id: editing || this.scoreId('s'), editing: editing || null, type: type, name: name, glyph: glyph || '', s1: start.s, p1: start.p, step1: start.step, system: type === 'ending' || type.indexOf('tempo-') === 0 }, scoreObjectId: null, halo: false, panel: null, menu: false, hub: false, kb: null, radial: false, picker: false, remapFor: null, captureFor: null, recovery: null, selId: null,
      staff: start.s, pos: start.p, step: start.step, spoken: name + ' point one set — move to point two and press A' });
"""
if t.count(old_begin) != 1:
    raise SystemExit(f'beginScoreSpan overlay reset: expected 1 match, found {t.count(old_begin)}')
t = t.replace(old_begin, new_begin, 1)

p.write_text(t, encoding='utf-8')
print('Exclusive notation controller priority repaired')
