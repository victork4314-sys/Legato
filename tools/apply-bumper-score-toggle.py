from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

OLD_BUILD = '20260727-score-entry-time-1'
NEW_BUILD = '20260727-bumper-score-toggle-1'


def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)


if NEW_BUILD in text:
    print('Bumper score toggle already applied')
    raise SystemExit(0)

if text.count(OLD_BUILD) != 3:
    raise SystemExit(f'build marker: expected 3 matches, found {text.count(OLD_BUILD)}')
text = text.replace(OLD_BUILD, NEW_BUILD)

one(
"const DEFAULT_BINDINGS = { button0: 'confirm', button1: 'delete', button2: 'cycle-articulation', button3: 'command-halo', button4: 'previous-zone', button5: 'next-zone', button6: 'select-modifier', button7: 'duration-wheel', button8: 'undo', button9: 'project-menu', button10: 'play-toggle', button11: 'toggle-pointer', button12: 'move-up', button13: 'move-down', button14: 'move-left', button15: 'move-right' };\n",
"const DEFAULT_BINDINGS = { button0: 'confirm', button1: 'delete', button2: 'cycle-articulation', button3: 'command-halo', button4: 'previous-zone', button5: 'next-zone', button6: 'select-modifier', button7: 'duration-wheel', button8: 'undo', button9: 'project-menu', button10: 'play-toggle', button11: 'toggle-pointer', button12: 'move-up', button13: 'move-down', button14: 'move-left', button15: 'move-right' };\nconst BUMPER_COMBO_MS = 120;\n",
'define bumper combo window')

one(
"    tour: false, tourIdx: 0,\n",
"    tour: false, tourIdx: 0, scoreHint: false,\n",
'score hint state')

one(
"  componentWillUnmount() { window.removeEventListener('keydown', this._keys); window.removeEventListener('keyup', this._keyup); window.__legatoKeys = null; cancelAnimationFrame(this._raf); if (this._autoScanTimer) clearInterval(this._autoScanTimer); if (this._ac) this._ac.close(); }\n",
"  componentWillUnmount() { window.removeEventListener('keydown', this._keys); window.removeEventListener('keyup', this._keyup); window.__legatoKeys = null; cancelAnimationFrame(this._raf); if (this._autoScanTimer) clearInterval(this._autoScanTimer); if (this._scoreHintTimer) clearTimeout(this._scoreHintTimer); if (this._ac) this._ac.close(); }\n",
'clear score hint timer')

one(
"""  enterScoreEditor() {
    document.querySelectorAll('[data-scan-selected=\"true\"]').forEach(el => el.removeAttribute('data-scan-selected'));
    this.rumble('tick');
    this.setState({ zone: 3, focus: 0, spoken: 'Score editor active — arrows move the cursor; the SCORE control stays lit while you are inside' });
  }
""",
"""  rememberScoreReturn() {
    const selected = document.querySelector('[data-scan-selected=\"true\"]');
    if (!selected || selected.getAttribute('data-score-editor-shell') === 'true') return;
    const zone = this.scanZoneForElement(selected), list = this.zoneScanItems(zone);
    this._scoreReturn = { zone: zone, focus: Math.max(0, list.indexOf(selected)) };
  }
  enterScoreEditor() {
    if (this.state.zone !== 3) this.rememberScoreReturn();
    document.querySelectorAll('[data-scan-selected=\"true\"]').forEach(el => el.removeAttribute('data-scan-selected'));
    if (this._scoreHintTimer) clearTimeout(this._scoreHintTimer);
    this.rumble('tick');
    this.setState({ zone: 3, focus: 0, scoreHint: true, spoken: 'Score editor active — arrows move the cursor; press LB and RB together to leave' }, () => {
      this._scoreHintTimer = setTimeout(() => this.setState({ scoreHint: false }), 1500);
    });
  }
  leaveScoreEditor() {
    const back = this._scoreReturn || { zone: 2, focus: 0 };
    if (this._scoreHintTimer) clearTimeout(this._scoreHintTimer);
    this.rumble('tick');
    this.setState({ zone: back.zone, focus: back.focus, scoreHint: false, spoken: 'Left the score editor — press LB and RB together to return' }, () => {
      requestAnimationFrame(() => this.syncGlobalSelection());
    });
  }
  toggleScoreEditor() {
    if (this.state.zone === 3) this.leaveScoreEditor();
    else this.enterScoreEditor();
  }
""",
'score editor toggle methods')

one(
"      returnToScore: () => this.enterScoreEditor(),\n      returnToScorePtr: s.zone === 3 ? 'Score editor active' : 'Return to score editor — press A',\n      returnToScoreHint: s.zone === 3 ? 'ACTIVE' : 'A ENTER',\n",
"      returnToScore: () => this.toggleScoreEditor(),\n      returnToScorePtr: s.zone === 3 ? 'Leave score editor — press A' : 'Return to score editor — press A',\n      returnToScoreHint: s.zone === 3 ? 'A LEAVE' : 'A ENTER',\n",
'top score toggle')

one(
"      scoreEditorBadgeStyle: s.zone === 3 ? 'position:sticky;top:8px;left:12px;z-index:55;width:max-content;margin:0 0 -27px 12px;padding:6px 9px;border-radius:5px;background:var(--accent);color:var(--bg);font-family:var(--ui-font);font-size:9px;font-weight:700;letter-spacing:.05em;pointer-events:none;' : 'display:none;',\n",
"      scoreEditorBadgeStyle: s.zone === 3 && s.scoreHint ? 'position:sticky;top:8px;left:12px;z-index:55;width:max-content;margin:0 0 -27px 12px;padding:6px 9px;border-radius:5px;background:var(--accent);color:var(--bg);font-family:var(--ui-font);font-size:9px;font-weight:700;letter-spacing:.05em;pointer-events:none;' : 'display:none;',\n",
'fade active score banner')

one(
"<span>LB / RB · ZONE</span>",
"<span>LB/RB · ACCIDENTAL · BOTH · SCORE</span>",
'bumper help text')

old_poll = """      for (let i = 0; i < b.length; i++) {
        const action = this.bindings['button' + i];
        if (!action) continue;
        const on = b[i].pressed, was = !!prev[i];
        if (on && !was) { this._hold = this._hold || {}; this._hold[i] = t; this._rep = this._rep || {}; this._rep[i] = t + s.repeatDelay; this.dispatch(action, 'press'); }
        else if (on && was && /^move-|^extend|^octave/.test(action)) {
          if (this._rep && t >= this._rep[i]) { this._rep[i] = t + s.repeatRate; this.dispatch(action, 'repeat'); }
        } else if (!on && was) this.dispatch(action, 'release');
      }
"""
new_poll = """      this._bumperPending = this._bumperPending || {};
      const lbOn = !!(b[4] && b[4].pressed), rbOn = !!(b[5] && b[5].pressed);
      const bumpersTogether = lbOn && rbOn;
      if (bumpersTogether && !this._bumperCombo) {
        delete this._bumperPending[4];
        delete this._bumperPending[5];
        this._bumperCombo = true;
        this.toggleScoreEditor();
      }
      if (this._bumperCombo && !lbOn && !rbOn) this._bumperCombo = false;
      [4, 5].forEach(i => {
        const on = !!(b[i] && b[i].pressed), was = !!prev[i];
        const action = this.bindings['button' + i];
        if (!action) return;
        if (this._bumperCombo) {
          if (!on) delete this._bumperPending[i];
          return;
        }
        if (on && !was) {
          this._bumperPending[i] = { action: action, at: t, fired: false };
          this._rep = this._rep || {};
          this._rep[i] = t + s.repeatDelay;
        }
        const pending = this._bumperPending[i];
        if (on && pending && !pending.fired && t - pending.at >= BUMPER_COMBO_MS) {
          pending.fired = true;
          this.dispatch(pending.action, 'press');
        } else if (on && was && pending && pending.fired && /^move-|^extend|^octave/.test(pending.action)) {
          if (this._rep && t >= this._rep[i]) { this._rep[i] = t + s.repeatRate; this.dispatch(pending.action, 'repeat'); }
        } else if (!on && was && pending) {
          if (!pending.fired) this.dispatch(pending.action, 'press');
          this.dispatch(pending.action, 'release');
          delete this._bumperPending[i];
          if (this._rep) delete this._rep[i];
        }
      });
      for (let i = 0; i < b.length; i++) {
        if (i === 4 || i === 5) continue;
        const action = this.bindings['button' + i];
        if (!action) continue;
        const on = b[i].pressed, was = !!prev[i];
        if (on && !was) { this._hold = this._hold || {}; this._hold[i] = t; this._rep = this._rep || {}; this._rep[i] = t + s.repeatDelay; this.dispatch(action, 'press'); }
        else if (on && was && /^move-|^extend|^octave/.test(action)) {
          if (this._rep && t >= this._rep[i]) { this._rep[i] = t + s.repeatRate; this.dispatch(action, 'repeat'); }
        } else if (!on && was) this.dispatch(action, 'release');
      }
"""
one(old_poll, new_poll, 'bumper polling')

for marker in [
    "const DEFAULT_BINDINGS = { button0: 'confirm', button1: 'delete'",
    "button4: 'previous-zone', button5: 'next-zone'",
    "case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;",
    "case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;"
]:
    if marker not in text:
        raise SystemExit('Protected individual bumper behavior missing: ' + marker)

required = [
    NEW_BUILD,
    'const BUMPER_COMBO_MS = 120;',
    'this.toggleScoreEditor();',
    'if (i === 4 || i === 5) continue;',
    "returnToScoreHint: s.zone === 3 ? 'A LEAVE' : 'A ENTER'",
    's.zone === 3 && s.scoreHint',
    'setTimeout(() => this.setState({ scoreHint: false }), 1500)',
    'LB/RB · ACCIDENTAL · BOTH · SCORE'
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing result marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Bumper score toggle applied')
