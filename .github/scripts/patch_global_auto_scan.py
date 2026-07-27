from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old = '''  advanceAutoScan() {
    if (!this.state.autoScan || this.anyOverlay() || this.state.ptrOn) return;
    const list = this.focusList();
    if (list.length && this.state.focus < list.length - 1) return this.moveFocus(1);
    this.cycleVisibleZone(1);
  }
'''
new = '''  autoScanTargets() {
    const s = this.state;
    const targets = [];
    const add = (zone, mode) => {
      const previousZone = s.zone, previousMode = s.mode;
      s.zone = zone;
      if (mode != null) s.mode = mode;
      this.focusList().forEach((item, focus) => targets.push({ zone: zone, mode: mode == null ? s.mode : mode, focus: focus, label: item.label }));
      s.zone = previousZone;
      s.mode = previousMode;
    };
    add(0, s.mode);
    if (!s.sidebarsHidden) add(1, s.mode);
    add(2, s.mode);
    for (let mode = 0; mode < 6; mode++) if (!s.sidebarsHidden) add(4, mode);
    return targets;
  }
  advanceAutoScan() {
    if (!this.state.autoScan || this.anyOverlay() || this.state.ptrOn) return;
    const targets = this.autoScanTargets();
    if (!targets.length) return;
    const s = this.state;
    let index = targets.findIndex(t => t.zone === s.zone && t.mode === s.mode && t.focus === s.focus);
    index = (index + 1 + targets.length) % targets.length;
    const next = targets[index];
    this.setState({ zone: next.zone, mode: next.mode, focus: next.focus, spoken: next.label });
  }
'''
if text.count(old) != 1:
    raise SystemExit(f'advanceAutoScan block mismatch: {text.count(old)}')
text = text.replace(old, new, 1)
for required in ['autoScanTargets()', 'for (let mode = 0; mode < 6; mode++)', 'spoken: next.label']:
    if required not in text:
        raise SystemExit('missing ' + required)
path.write_text(text, encoding='utf-8')
print('global auto scan patch applied')
