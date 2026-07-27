from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    text = text.replace(old, new, 1)


# Add the requested top controls immediately before the existing menu control.
top_anchor = '''      <div onClick="{{ openHubBtn }}" data-ptr="Open the menu" style="{{ modeBadgeStyle }}">'''
top_controls = '''      <div onClick="{{ toggleSidebarsBtn }}" data-ptr="{{ sidebarsPtrLabel }}" style="{{ sidebarsToggleStyle }}" style-hover="border-color:#74a12e">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #b6bfba; letter-spacing: .05em;">{{ sidebarsLabel }}</div>
      </div>
      <div onClick="{{ toggleAutoScanBtn }}" data-ptr="{{ autoScanPtrLabel }}" style="{{ autoScanToggleStyle }}" style-hover="border-color:#74a12e">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #b6bfba; letter-spacing: .05em;">{{ autoScanLabel }}</div>
      </div>
''' + top_anchor
replace_once(top_anchor, top_controls, "top controls insertion")

# Make the workspace switch cleanly between three columns and score-only view.
replace_once(
    '''  <div style="display: grid; grid-template-columns: 224px minmax(0, 1fr) 296px; min-height: 0; overflow: hidden;">''',
    '''  <div style="{{ workspaceStyle }}">''',
    "workspace style binding",
)

# Remove only the final face-button controls strip below the note/play toolbar.
controls_strip = '''      <div style="display: flex; align-items: center; gap: 6px; padding: 5px 10px; min-width: 0; overflow-x: auto; background: #101413; border-bottom: 1px solid #232927;">
        <sc-for list="{{ faceButtons }}" as="fb" hint-placeholder-count="5">
          <div onClick="{{ fb.onSelect }}" data-ptr="{{ fb.label }}" style="display: flex; align-items: center; gap: 6px; padding: 5px 11px 5px 5px; border-radius: 5px; cursor: pointer; border: 1px solid #262d2b; background: #151a18; flex-shrink: 0;" style-hover="border-color:#3c4441">
            <div style="{{ fb.chipStyle }}">{{ fb.btn }}</div>
            <div style="font-size: 12px; color: #c3ccc7; white-space: nowrap;">{{ fb.label }}</div>
          </div>
        </sc-for>
        <div style="flex: 1; min-width: 6px;"></div>
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #6f7a75; letter-spacing: .05em; white-space: nowrap;">D-PAD MOVES · LB/RB CHANGES PANEL</div>
      </div>

'''
replace_once(controls_strip, "", "final controls strip removal")

# UI-only state; score data and document serialization remain untouched.
replace_once(
    '''focusRepeat: true, padLost: false, padEver: false
  };''',
    '''focusRepeat: true, padLost: false, padEver: false, sidebarsHidden: false, autoScan: false
  };''',
    "sidebar and scan state",
)

replace_once(
    '''  componentWillUnmount() { window.removeEventListener('keydown', this._keys); window.removeEventListener('keyup', this._keyup); window.__legatoKeys = null; cancelAnimationFrame(this._raf); if (this._ac) this._ac.close(); }''',
    '''  componentWillUnmount() { window.removeEventListener('keydown', this._keys); window.removeEventListener('keyup', this._keyup); window.__legatoKeys = null; cancelAnimationFrame(this._raf); if (this._autoScanTimer) clearInterval(this._autoScanTimer); if (this._ac) this._ac.close(); }''',
    "auto scan cleanup",
)

focus_anchor = '''  focusList() {
    const s = this.state;'''
methods = '''  visibleZones() {
    return this.state.sidebarsHidden ? [0, 2, 3] : [0, 1, 2, 3, 4];
  }
  cycleVisibleZone(d) {
    const zones = this.visibleZones();
    this.setState(s => {
      let i = zones.indexOf(s.zone);
      if (i < 0) i = 0;
      const zone = zones[(i + d + zones.length) % zones.length];
      return { zone: zone, focus: 0, spoken: ['Modes', 'Players', 'Toolbar', 'Score', 'Properties'][zone] };
    });
  }
  toggleSidebars() {
    this.setState(s => {
      const hidden = !s.sidebarsHidden;
      return {
        sidebarsHidden: hidden,
        zone: hidden && (s.zone === 1 || s.zone === 4) ? 3 : s.zone,
        focus: 0,
        spoken: hidden ? 'Sidebars hidden — scanning visible controls only' : 'Sidebars shown — all controls included'
      };
    });
  }
  restartAutoScan() {
    if (this._autoScanTimer) clearInterval(this._autoScanTimer);
    this._autoScanTimer = null;
    if (!this.state.autoScan) return;
    this._autoScanTimer = setInterval(() => this.advanceAutoScan(), 1200);
  }
  toggleAutoScan() {
    this.setState(s => ({
      autoScan: !s.autoScan,
      focus: 0,
      spoken: s.autoScan ? 'Auto scan off' : 'Auto scan on — visible controls only'
    }), () => this.restartAutoScan());
  }
  advanceAutoScan() {
    if (!this.state.autoScan || this.anyOverlay() || this.state.ptrOn) return;
    const list = this.focusList();
    if (list.length && this.state.focus < list.length - 1) return this.moveFocus(1);
    this.cycleVisibleZone(1);
  }

''' + focus_anchor
replace_once(focus_anchor, methods, "sidebar and auto scan methods")

replace_once(
    '''  focusList() {
    const s = this.state;
    if (s.zone === 0) return ['Setup', 'Write', 'Engrave', 'Play', 'Print', 'Controller'].map((n, i) => ({ t: 'mode', i: i, label: n + ' mode' }));''',
    '''  focusList() {
    const s = this.state;
    if (s.sidebarsHidden && (s.zone === 1 || s.zone === 4)) return [];
    if (s.zone === 0) return ['Setup', 'Write', 'Engrave', 'Play', 'Print', 'Controller'].map((n, i) => ({ t: 'mode', i: i, label: n + ' mode' }))
      .concat([{ t: 'top', i: 0, label: s.sidebarsHidden ? 'Show sidebars' : 'Hide sidebars' }, { t: 'top', i: 1, label: s.autoScan ? 'Stop auto scan' : 'Start auto scan' }]);''',
    "visible focus list",
)

replace_once(
    '''      case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleZone(-1); break;
      case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleZone(1); break;''',
    '''      case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;
      case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;''',
    "visible zone cycling",
)

replace_once(
    '''    else if (it.t === 'mode') this.setState({ mode: it.i, spoken: ['Setup', 'Write', 'Engrave', 'Play', 'Print', 'Controller'][it.i] + ' mode' });''',
    '''    else if (it.t === 'top') { if (it.i === 0) this.toggleSidebars(); else this.toggleAutoScan(); }
    else if (it.t === 'mode') this.setState({ mode: it.i, spoken: ['Setup', 'Write', 'Engrave', 'Play', 'Print', 'Controller'][it.i] + ' mode' });''',
    "top control activation",
)

replace_once(
    '''      toggleOneHanded: () => this.setState(p => ({ oneHanded: !p.oneHanded, spoken: p.oneHanded ? 'Two-handed profile' : 'One-handed profile — bumpers and triggers now navigate' })),''',
    '''      sidebarsLabel: s.sidebarsHidden ? 'SHOW SIDEBARS' : 'HIDE SIDEBARS',
      sidebarsPtrLabel: s.sidebarsHidden ? 'Show sidebars' : 'Hide sidebars',
      toggleSidebarsBtn: () => this.toggleSidebars(),
      sidebarsToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.sidebarsHidden ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.sidebarsHidden ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 0),
      autoScanLabel: s.autoScan ? 'AUTO SCAN ON' : 'AUTO SCAN',
      autoScanPtrLabel: s.autoScan ? 'Stop auto scan' : 'Start auto scan',
      toggleAutoScanBtn: () => this.toggleAutoScan(),
      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 1),
      toggleOneHanded: () => this.setState(p => ({ oneHanded: !p.oneHanded, spoken: p.oneHanded ? 'Two-handed profile' : 'One-handed profile — bumpers and triggers now navigate' })),''',
    "top control render bindings",
)

replace_once(
    '''      leftZoneStyle: this.zoneBox(1),
      centerZoneStyle: this.zoneBox(3),
      rightZoneStyle: this.zoneBox(4),''',
    '''      workspaceStyle: 'display:grid;grid-template-columns:' + (s.sidebarsHidden ? 'minmax(0,1fr)' : '224px minmax(0,1fr) 296px') + ';min-height:0;overflow:hidden;',
      leftZoneStyle: s.sidebarsHidden ? 'display:none;' : this.zoneBox(1),
      centerZoneStyle: this.zoneBox(3),
      rightZoneStyle: s.sidebarsHidden ? 'display:none;' : this.zoneBox(4),''',
    "sidebar render styles",
)

required = [
    "{{ toggleSidebarsBtn }}",
    "{{ toggleAutoScanBtn }}",
    "{{ workspaceStyle }}",
    "sidebarsHidden: false",
    "autoScan: false",
    "cycleVisibleZone(d)",
    "s.sidebarsHidden ? [0, 2, 3] : [0, 1, 2, 3, 4]",
]
for item in required:
    if item not in text:
        raise SystemExit(f"validation failed: missing {item}")

forbidden = [
    'list="{{ faceButtons }}" as="fb"',
    "D-PAD MOVES · LB/RB CHANGES PANEL",
]
for item in forbidden:
    if item in text:
        raise SystemExit(f"validation failed: old controls strip remains: {item}")

path.write_text(text, encoding="utf-8")
