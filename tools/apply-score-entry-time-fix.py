from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text

OLD_BUILD = '20260727-real-cache-refresh-1'
NEW_BUILD = '20260727-score-entry-time-1'


def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)


if NEW_BUILD in text:
    print('Score entry and time signature repair already applied')
    raise SystemExit(0)

build_count = text.count(OLD_BUILD)
if build_count != 3:
    raise SystemExit(f'build marker: expected 3 matches, found {build_count}')
text = text.replace(OLD_BUILD, NEW_BUILD)

one(
'''  [data-score-edit="true"]:hover { background: rgba(var(--accent-rgb),.12); box-shadow: 0 0 0 1px rgba(var(--accent-rgb),.34); }
''',
'''  [data-score-edit="true"]:hover { background: rgba(var(--accent-rgb),.12); box-shadow: 0 0 0 1px rgba(var(--accent-rgb),.34); }
  [data-score-editor-shell="true"] { position: relative; transition: box-shadow .12s ease, outline-color .12s ease; }
  [data-score-editor-shell="true"][data-score-active="true"] {
    box-shadow: inset 0 0 0 3px var(--accent), inset 0 0 0 6px rgba(var(--accent-rgb),.18);
  }
  [data-score-editor-shell="true"][data-scan-selected="true"] {
    outline: 3px solid var(--accent) !important;
    outline-offset: -5px !important;
    box-shadow: inset 0 0 0 6px rgba(var(--accent-rgb),.2) !important;
  }
  [data-score-editor-shell="true"][data-scan-selected="true"]::after {
    content: 'SCORE EDITOR SELECTED · PRESS A';
    position: absolute; left: 14px; top: 10px; z-index: 60; pointer-events: none;
    padding: 7px 10px; border-radius: 5px; background: var(--accent); color: var(--bg);
    font-family: 'IBM Plex Mono', monospace; font-size: 10px; font-weight: 700; letter-spacing: .05em;
  }
''',
'editor selection css')

one(
'''      <div onClick="{{ toggleAutoScanBtn }}" data-ptr="{{ autoScanPtrLabel }}" style="{{ autoScanToggleStyle }}" style-hover="border-color:var(--accent)">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--text-2); letter-spacing: .05em;">{{ autoScanLabel }}</div>
      </div>
      <div onClick="{{ openHubBtn }}" data-ptr="Open the menu" style="{{ modeBadgeStyle }}">
''',
'''      <div onClick="{{ toggleAutoScanBtn }}" data-ptr="{{ autoScanPtrLabel }}" style="{{ autoScanToggleStyle }}" style-hover="border-color:var(--accent)">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--text-2); letter-spacing: .05em;">{{ autoScanLabel }}</div>
      </div>
      <div onClick="{{ returnToScore }}" data-ptr="{{ returnToScorePtr }}" data-score-return="true" style="{{ returnToScoreStyle }}" style-hover="filter:brightness(1.08)">
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 10px; font-weight: 700; letter-spacing: .06em;">SCORE</div>
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 8px; letter-spacing: .04em; opacity: .78;">{{ returnToScoreHint }}</div>
      </div>
      <div onClick="{{ openHubBtn }}" data-ptr="Open the menu" style="{{ modeBadgeStyle }}">
''',
'top score control')

one(
'''      <div data-scroll="score" data-ptr="Score editor" data-score-editor-shell="true" onClick="{{ enterScoreEditor }}" style="flex: 1; min-height: 0; overflow: auto; padding: 12px 0 18px; background: radial-gradient(1200px 500px at 50% -5%, var(--raised), var(--bg) 70%);">
        <div data-print-score="true" style="{{ paperStyle }}">
''',
'''      <div data-scroll="score" data-ptr="Score editor" data-score-editor-shell="true" data-score-active="{{ scoreEditorActive }}" onClick="{{ enterScoreEditor }}" style="{{ scoreEditorStyle }}">
        <div aria-hidden="true" style="{{ scoreEditorBadgeStyle }}">SCORE EDITOR ACTIVE · ARROWS MOVE CURSOR</div>
        <div data-print-score="true" style="{{ paperStyle }}">
''',
'score shell state')

one(
'''  enterScoreEditor() {
    document.querySelectorAll('[data-scan-selected="true"]').forEach(el => el.removeAttribute('data-scan-selected'));
    this.rumble('tick');
    this.setState({ zone: 3, focus: 0, spoken: 'Score editor — arrows move through the score; use normal zone navigation to leave' });
  }
''',
'''  enterScoreEditor() {
    document.querySelectorAll('[data-scan-selected="true"]').forEach(el => el.removeAttribute('data-scan-selected'));
    this.rumble('tick');
    this.setState({ zone: 3, focus: 0, spoken: 'Score editor active — arrows move the cursor; the SCORE control stays lit while you are inside' });
  }
''',
'enter score feedback')

one(
'''      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : 'var(--border-strong)') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(var(--accent-rgb),.12)' : 'var(--raised)') + ';cursor:pointer;' + this.ring('top', 2),
      fileMenuStyle: 'display:flex;align-items:center;gap:7px;padding:4px 10px;border:1px solid var(--border-strong);border-radius:5px;background:var(--raised);cursor:pointer;' + this.ring('top', 4),
''',
'''      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : 'var(--border-strong)') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(var(--accent-rgb),.12)' : 'var(--raised)') + ';cursor:pointer;' + this.ring('top', 2),
      returnToScore: () => this.enterScoreEditor(),
      returnToScorePtr: s.zone === 3 ? 'Score editor active' : 'Return to score editor — press A',
      returnToScoreHint: s.zone === 3 ? 'ACTIVE' : 'A ENTER',
      returnToScoreStyle: 'display:flex;flex-direction:column;align-items:center;justify-content:center;min-width:58px;padding:3px 9px;border-radius:5px;cursor:pointer;line-height:1.05;border:1px solid ' + accent + ';background:' + (s.zone === 3 ? accent : 'rgba(var(--accent-rgb),.14)') + ';color:' + (s.zone === 3 ? 'var(--bg)' : 'var(--text-strong)') + ';box-shadow:' + (s.zone === 3 ? '0 0 0 2px rgba(var(--accent-rgb),.22)' : 'none') + ';',
      scoreEditorActive: s.zone === 3 ? 'true' : 'false',
      scoreEditorStyle: 'flex:1;min-height:0;overflow:auto;padding:12px 0 18px;background:radial-gradient(1200px 500px at 50% -5%,var(--raised),var(--bg) 70%);position:relative;',
      scoreEditorBadgeStyle: s.zone === 3 ? 'position:sticky;top:8px;left:12px;z-index:55;width:max-content;margin:0 0 -27px 12px;padding:6px 9px;border-radius:5px;background:var(--accent);color:var(--bg);font-family:\'IBM Plex Mono\',monospace;font-size:9px;font-weight:700;letter-spacing:.05em;pointer-events:none;' : 'display:none;',
      fileMenuStyle: 'display:flex;align-items:center;gap:7px;padding:4px 10px;border:1px solid var(--border-strong);border-radius:5px;background:var(--raised);cursor:pointer;' + this.ring('top', 4),
''',
'score control render state')

one(
'''        const timeWidth = Math.max(String(met[0]).length, String(met[1]).length) * 17 + 6;
''',
'''        const timeWidth = Math.max(String(met[0]).length, String(met[1]).length) * 21 + 8;
''',
'time signature width')

one(
'''          timeTopStyle: 'position:absolute;left:' + timeX + 'px;top:0;width:' + timeWidth + 'px;height:24px;display:flex;align-items:center;justify-content:center;' + BR + 'font-size:32px;line-height:24px;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',
          timeBotStyle: 'position:absolute;left:' + timeX + 'px;top:24px;width:' + timeWidth + 'px;height:24px;display:flex;align-items:center;justify-content:center;' + BR + 'font-size:32px;line-height:24px;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',
          timeHitStyle: 'position:absolute;left:' + (timeX - 3) + 'px;top:0;width:' + (timeWidth + 6) + 'px;height:48px;cursor:pointer;z-index:4;',
''',
'''          timeTopStyle: 'position:absolute;left:' + timeX + 'px;top:-1px;width:' + timeWidth + 'px;height:25px;display:grid;place-items:center;' + BR + 'font-size:40px;line-height:1;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',
          timeBotStyle: 'position:absolute;left:' + timeX + 'px;top:23px;width:' + timeWidth + 'px;height:25px;display:grid;place-items:center;' + BR + 'font-size:40px;line-height:1;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',
          timeHitStyle: 'position:absolute;left:' + (timeX - 4) + 'px;top:-2px;width:' + (timeWidth + 8) + 'px;height:52px;cursor:pointer;z-index:4;',
''',
'larger centered time signature')

# Explicitly protect the requested untouched controller behavior.
for marker in [
    "const DEFAULT_BINDINGS = { button0: 'confirm', button1: 'delete'",
    "case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;",
    "case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;"
]:
    if marker not in text:
        raise SystemExit('Protected controller behavior missing: ' + marker)

required = [
    NEW_BUILD,
    'data-score-return="true"',
    'SCORE EDITOR SELECTED · PRESS A',
    'SCORE EDITOR ACTIVE · ARROWS MOVE CURSOR',
    "returnToScoreHint: s.zone === 3 ? 'ACTIVE' : 'A ENTER'",
    "font-size:40px;line-height:1",
    "data-score-active=\"{{ scoreEditorActive }}\""
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing result marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Score entry and time signature repair applied')
