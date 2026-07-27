from pathlib import Path
import re
import subprocess
import tempfile

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text


def once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)


def regex_once(pattern, replacement, label, flags=0):
    global text
    text2, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    text = text2


# Cache refresh: the HTML itself is not allowed to sit stale, and the external runtime gets a new URL.
once(
    '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<script src="./support.js?v=20260727-console-focus-1"></script>',
    '<meta charset="utf-8">\n<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">\n<meta http-equiv="Pragma" content="no-cache">\n<meta http-equiv="Expires" content="0">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<script src="./support.js?v=20260727-meter-themes-scroll-2"></script>',
    'cache headers and runtime version'
)

# The whole app inherits a complete palette from this root.
once(
    '<div style="width: 100%; height: 100vh; background: #111315; display: grid; grid-template-rows: 46px 30px minmax(0, 1fr); grid-template-columns: minmax(0, 1fr); overflow: hidden;">',
    '<div data-legato-root="true" style="{{ rootStyle }}">',
    'theme root'
)

# Print only the actual score DOM, and give cursor following a stable target.
once('<div style="{{ paperStyle }}">', '<div data-print-score="true" style="{{ paperStyle }}">', 'print score marker')
once('<div style="{{ caretStyle }}"></div>', '<div data-score-caret="true" style="{{ caretStyle }}"></div>', 'score caret marker')

# Every long overlay must own its own scroll surface.
once('<div style="padding: 14px 15px 16px;">\n          <div style="min-height: 46px;', '<div data-scroll="keyboard" style="max-height: 70vh; overflow: auto; padding: 14px 15px 16px;">\n          <div style="min-height: 46px;', 'keyboard scrolling')
once('<div style="padding: 22px 22px 18px;">\n          <div style="display: flex; align-items: center; gap: 14px;', '<div data-scroll="tour" style="max-height: 62vh; overflow: auto; padding: 22px 22px 18px;">\n          <div style="display: flex; align-items: center; gap: 14px;', 'tour scrolling')

# Add the visual theme picker under Setup, without moving any existing setup controls.
setup_close = '''              <div onClick="{{ doSave }}" data-ptr="Save project" style="padding: 9px 11px; border-radius: 6px; cursor: pointer; text-align: center; border: 1px solid #3a424a; color: #cbd1d6; font-size: 12.5px;">Save .legato</div>
            </div>
          </div>
        </sc-if>'''
setup_new = '''              <div onClick="{{ doSave }}" data-ptr="Save project" style="padding: 9px 11px; border-radius: 6px; cursor: pointer; text-align: center; border: 1px solid #3a424a; color: #cbd1d6; font-size: 12.5px;">Save .legato</div>
            </div>
          </div>
          <div style="border: 1px solid #343a42; border-radius: 6px; background: #20242a; padding: 10px 11px 12px; margin-bottom: 10px;">
            <div style="font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; color: #9fa7b2; letter-spacing: .02em; padding-bottom: 3px;">Theme</div>
            <div style="font-size: 11px; color: #858f9a; padding-bottom: 9px;">Complete interface palettes — the score stays clean and readable.</div>
            <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px;">
              <sc-for list="{{ themeRows }}" as="th" hint-placeholder-count="12">
                <div onClick="{{ th.onSelect }}" data-ptr="Theme {{ th.name }}" style="{{ th.style }}" style-hover="filter:brightness(1.08)">
                  <div style="display:flex;gap:3px;align-items:center;">
                    <span style="{{ th.bgSwatch }}"></span><span style="{{ th.panelSwatch }}"></span><span style="{{ th.accentSwatch }}"></span>
                  </div>
                  <span style="min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{{ th.name }}</span>
                </div>
              </sc-for>
            </div>
          </div>
        </sc-if>'''
once(setup_close, setup_new, 'setup theme picker')
once('hint-placeholder-count="5">\n              <div onClick="{{ r.onSelect }}" data-ptr="{{ r.k }}"', 'hint-placeholder-count="6">\n              <div onClick="{{ r.onSelect }}" data-ptr="{{ r.k }}"', 'setup row count')

# State and persistence for themes.
once(
    "const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks'];\nconst STORE = 'legato.recovery.v1';",
    "const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks'];\nconst STORE = 'legato.recovery.v1';\nconst THEME_STORE = 'legato.theme.v1';",
    'theme storage key'
)
once(
    "sidebarsHidden: false, autoScan: false\n  };",
    "sidebarsHidden: false, autoScan: false, theme: 'verdant'\n  };",
    'theme state'
)
once(
    "    this.loadRecovery();\n    try { if (!localStorage.getItem(TOUR_SEEN))",
    "    try { const savedTheme = localStorage.getItem(THEME_STORE); if (savedTheme && THEMES.some(t => t.id === savedTheme)) this.setState({ theme: savedTheme }); } catch (e) {}\n    this.loadRecovery();\n    try { if (!localStorage.getItem(TOUR_SEEN))",
    'theme restore'
)

# Theme setter and an immediate audible clef-octave preview.
once(
    "  setTempo(d) { this.setState(s => ({ tempo: Math.max(30, Math.min(240, s.tempo + d * 2)), spoken: (s.tempo + d * 2) + ' beats per minute' })); }",
    "  setTheme(id) {\n    const theme = themeById(id);\n    try { localStorage.setItem(THEME_STORE, theme.id); } catch (e) {}\n    this.setState({ theme: theme.id, spoken: theme.name + ' theme' });\n  }\n  setTempo(d) { this.setState(s => ({ tempo: Math.max(30, Math.min(240, s.tempo + d * 2)), spoken: (s.tempo + d * 2) + ' beats per minute' })); }",
    'theme setter'
)
regex_once(
    r"  setClefOctave\(value\) \{\n    this\.setState\(s => \{\n      const octaves = \(s\.clefOctaves \|\| s\.clefs\.map\(\(\) => 0\)\)\.slice\(\);\n      octaves\[s\.staff\] = value;\n      const label = value === 0 \? 'normal pitch' : \(Math\.abs\(value\) === 1 \? '8' : '15'\) \+ \(value > 0 \? ' above' : ' below'\);\n      return \{ clefOctaves: octaves, panel: null, spoken: 'Clef octave set to ' \+ label \+ ' for ' \+ STAVES\[s\.staff\]\.name \};\n    \}\);\n  \}",
    "  setClefOctave(value) {\n    this.setState(s => {\n      const octaves = (s.clefOctaves || s.clefs.map(() => 0)).slice();\n      octaves[s.staff] = value;\n      const label = value === 0 ? 'normal pitch' : (Math.abs(value) === 1 ? '8' : '15') + (value > 0 ? ' above' : ' below');\n      return { clefOctaves: octaves, panel: null, spoken: 'Clef octave set to ' + label + ' for ' + STAVES[s.staff].name };\n    }, () => {\n      this.warmScore(this.state.staff);\n      const selected = this.selected();\n      const step = selected ? selected.step : this.state.step;\n      const acc = selected ? selected.acc : null;\n      this.audition(step, this.state.staff, acc, selected ? selected.art : null, selected || null);\n    });\n  }",
    'clef octave preview'
)

# Clicking the little number goes straight to its own choices, rather than a generic clef menu.
once("    if (s.panel === 'clef') {", "    if (s.panel === 'clefOctave') {\n      const currentOctave = (s.clefOctaves || [])[s.staff] || 0;\n      return [\n        { label: 'Normal clef pitch', value: currentOctave === 0 ? 'IN USE' : '', act: () => this.setClefOctave(0) },\n        { label: '8 above the clef', value: currentOctave === 1 ? 'IN USE' : '', act: () => this.setClefOctave(1) },\n        { label: '8 below the clef', value: currentOctave === -1 ? 'IN USE' : '', act: () => this.setClefOctave(-1) },\n        { label: '15 above the clef', value: currentOctave === 2 ? 'IN USE' : '', act: () => this.setClefOctave(2) },\n        { label: '15 below the clef', value: currentOctave === -2 ? 'IN USE' : '', act: () => this.setClefOctave(-2) }\n      ];\n    }\n    if (s.panel === 'clef') {", 'clef octave panel')
once("          openClefOctave: () => this.openScoreEditor('clef', i),", "          openClefOctave: () => this.openScoreEditor('clefOctave', i),", 'octave number click')
once("panelTitle: s.panel ? (this.hubTiles().find(t => t.id === s.panel) || {}).name : '',", "panelTitle: s.panel ? ((this.hubTiles().find(t => t.id === s.panel) || {}).name || (s.panel === 'clefOctave' ? 'Clef octave' : 'Edit')) : '',", 'clef octave panel title')

# Meter-aware beaming. Four-four is grouped in two clear half-bar groups; compound metres use dotted beats.
old_pattern = """        const beamPattern = {
          '4/4': [1, 1, 1, 1],
          '3/4': [1, 1, 1],
          '2/2': [2, 2],
          '6/8': [1.5, 1.5],
          '5/4': [3, 2],
          '12/8': [1.5, 1.5, 1.5, 1.5],
          '7/8': [1, 1, 1.5]
        }[meterName] || [1];"""
new_pattern = """        const beamPattern = {
          '4/4': [2, 2],
          '3/4': [1, 1, 1],
          '2/2': [2, 2],
          '6/8': [1.5, 1.5],
          '5/4': [3, 2],
          '12/8': [1.5, 1.5, 1.5, 1.5],
          '7/8': [1, 1, 1.5]
        }[meterName] || [capBar];"""
once(old_pattern, new_pattern, 'meter beam pattern')

# Replace rotated rectangles with one polygon for each continuous beam segment. This removes anti-alias seams.
regex_once(
    r"              const bar = \(lo, hi, lv\) => \{.*?              \};\n              const hook = \(i, lv, forward\) => \{.*?              \};",
    """              const beamShape = (xa, xb, ya, yb) => {
                const topA = defaultUp ? ya : ya - thick;
                const topB = defaultUp ? yb : yb - thick;
                const botA = topA + thick, botB = topB + thick;
                const left = Math.min(xa, xb) - 1.5;
                const top = Math.min(topA, topB) - 1.5;
                const width = Math.abs(xb - xa) + 3;
                const height = Math.max(botA, botB) - top + 1.5;
                const pts = [
                  (xa - left).toFixed(2) + 'px ' + (topA - top).toFixed(2) + 'px',
                  (xb - left).toFixed(2) + 'px ' + (topB - top).toFixed(2) + 'px',
                  (xb - left).toFixed(2) + 'px ' + (botB - top).toFixed(2) + 'px',
                  (xa - left).toFixed(2) + 'px ' + (botA - top).toFixed(2) + 'px'
                ].join(',');
                beams.push({ style: 'position:absolute;left:' + left + 'px;top:' + top + 'px;width:' + width + 'px;height:' + height + 'px;background:#1b1a17;clip-path:polygon(' + pts + ');z-index:2;' });
              };
              const bar = (lo, hi, lv) => {
                const xa = xs[lo], xb = xs[hi];
                const ya = at(xa) - beamDir * lv * gap, yb = at(xb) - beamDir * lv * gap;
                beamShape(xa, xb, ya, yb);
              };
              const hook = (i, lv, forward) => {
                const xa = xs[i], width = Math.min(14, Math.max(9, XS * .22));
                const ya = at(xa) - beamDir * lv * gap;
                const xb = forward ? xa + width : xa - width;
                const yb = at(xb) - beamDir * lv * gap;
                beamShape(xa, xb, ya, yb);
              };""",
    'continuous beam polygons',
    flags=re.S
)

# A run of sixteenths/thirty-seconds stays continuous; only an actual lower-flag note creates a break.
old_secondary = """                const has = group.map(g => (FLAG[g.n.d] || 1) > lv);
                const levelUnit = Math.max(.125, 1 / Math.pow(2, lv));
                let i = 0;
                while (i < group.length) {
                  if (!has[i]) { i += 1; continue; }
                  let j = i;
                  while (j + 1 < group.length && has[j + 1]
                    && Math.floor((group[j + 1].n.p % capBar) / levelUnit + .0005) === Math.floor((group[i].n.p % capBar) / levelUnit + .0005)) j += 1;
                  if (j > i) bar(i, j, lv);
                  else {
                    const local = (group[i].n.p % capBar) / levelUnit;
                    const atStart = Math.abs(local - Math.floor(local + .0005)) < .0005;
                    hook(i, lv, atStart || i === 0);
                  }
                  i = j + 1;
                }"""
new_secondary = """                const has = group.map(g => (FLAG[g.n.d] || 1) > lv);
                let i = 0;
                while (i < group.length) {
                  if (!has[i]) { i += 1; continue; }
                  let j = i;
                  while (j + 1 < group.length && has[j + 1]) j += 1;
                  if (j > i) bar(i, j, lv);
                  else hook(i, lv, i === 0 || (i < group.length - 1 && !has[i - 1]));
                  i = j + 1;
                }"""
once(old_secondary, new_secondary, 'secondary beam continuity')

# Proper multi-digit, visually centred time signatures.
once(
    "        const met = METERS[s.meter].split('/');\n        const octave = (s.clefOctaves || [])[i] || 0;\n        const keyX = 52, timeX = 70 + (K.n || 0) * 12;",
    "        const met = METERS[s.meter].split('/');\n        const timeGlyphs = value => String(value).split('').map(d => String.fromCharCode(0xE080 + Number(d))).join('');\n        const timeWidth = Math.max(String(met[0]).length, String(met[1]).length) * 20 + 8;\n        const octave = (s.clefOctaves || [])[i] || 0;\n        const keyX = 52, timeX = 70 + (K.n || 0) * 12;",
    'time signature helpers'
)
once(
    "          timeTop: String.fromCharCode(0xE080 + Number(met[0]) % 10),\n          timeBot: String.fromCharCode(0xE080 + Number(met[1]) % 10),\n          timeTopStyle: glyphAt(timeX, 20, 48) + 'cursor:pointer;z-index:5;',\n          timeBotStyle: glyphAt(timeX, 44, 48) + 'cursor:pointer;z-index:5;',\n          timeHitStyle: 'position:absolute;left:' + (timeX - 3) + 'px;top:-6px;width:31px;height:60px;cursor:pointer;z-index:4;',",
    "          timeTop: timeGlyphs(met[0]),\n          timeBot: timeGlyphs(met[1]),\n          timeTopStyle: 'position:absolute;left:' + timeX + 'px;top:-3px;width:' + timeWidth + 'px;height:27px;display:grid;place-items:center;' + BR + 'font-size:43px;line-height:1;color:#1b1a17;white-space:nowrap;cursor:pointer;z-index:5;',\n          timeBotStyle: 'position:absolute;left:' + timeX + 'px;top:21px;width:' + timeWidth + 'px;height:27px;display:grid;place-items:center;' + BR + 'font-size:43px;line-height:1;color:#1b1a17;white-space:nowrap;cursor:pointer;z-index:5;',\n          timeHitStyle: 'position:absolute;left:' + (timeX - 3) + 'px;top:-6px;width:' + (timeWidth + 6) + 'px;height:60px;cursor:pointer;z-index:4;',",
    'centred time signature styles'
)

# Every measure-based calculation must follow the active meter, not an old hard-coded four beats.
once("const met = METERS[s.meter].split('/');\n    let xml", "const met = METERS[s.meter].split('/');\n    const capXml = Number(met[0]) * (4 / Number(met[1]));\n    let xml", 'MusicXML bar capacity')
text = text.replace("n.p >= b * 4 && n.p < (b + 1) * 4", "n.p >= b * capXml && n.p < (b + 1) * capXml")
text = text.replace("let cursor = b * 4;", "let cursor = b * capXml;")
text = text.replace("if ((b + 1) * 4 - cursor > .001) xml += '<note><rest/><duration>' + Math.round(((b + 1) * 4 - cursor) * DIV)", "if ((b + 1) * capXml - cursor > .001) xml += '<note><rest/><duration>' + Math.round(((b + 1) * capXml - cursor) * DIV)")
text = text.replace("noteX(bar * 4)", "noteX(bar * this.barCapacity())")
text = text.replace("p.bars * 4 - .001", "p.bars * this.barCapacity() - .001")
text = text.replace("(n.p % 4 + 1).toFixed(2)", "(n.p % this.barCapacity() + 1).toFixed(2)")
text = text.replace("(p.pos % 4 + 1).toFixed(2)", "(p.pos % this.barCapacity() + 1).toFixed(2)")

# Score-only printing: clone the engraved paper into a clean print document.
once(
    "  printScore() { this.setState({ spoken: 'Opening the print view' }); setTimeout(() => window.print(), 250); }",
    """  printScore() {
    const paper = document.querySelector('[data-print-score=\"true\"]');
    if (!paper) return this.setState({ spoken: 'The score is not ready to print yet' });
    const win = window.open('', '_blank', 'width=980,height=1100');
    if (!win) return this.setState({ spoken: 'The print window was blocked — allow pop-ups for Legato and try again' });
    const clone = paper.cloneNode(true);
    clone.style.transform = 'none';
    clone.style.transformOrigin = 'top left';
    clone.style.margin = '0 auto';
    clone.style.boxShadow = 'none';
    clone.style.borderRadius = '0';
    clone.querySelectorAll('[data-ptr]').forEach(el => el.removeAttribute('data-ptr'));
    const embedded = Array.from(document.querySelectorAll('style')).map(el => el.textContent || '').join('\\n');
    const pageName = this.state.paper === 'A4' ? 'A4' : (this.state.paper === 'Tabloid' ? '11in 17in' : 'letter');
    const orientation = String(this.state.orientation || 'Portrait').toLowerCase();
    const vars = themeCss(themeById(this.state.theme));
    win.document.open();
    win.document.write('<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>' + this.esc(this.state.title || 'Legato score') + '</title><link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Source+Serif+4:wght@500;600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=Noto+Music&amp;display=swap\" rel=\"stylesheet\"><style>:root{' + vars + '}' + embedded + '@page{size:' + pageName + ' ' + orientation + ';margin:10mm}html,body{margin:0!important;padding:0!important;background:var(--paper)!important;color:var(--ink)!important}body{display:block!important;overflow:visible!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}[data-print-score]{width:100%!important;max-width:none!important;min-height:0!important;box-shadow:none!important}</style></head><body>' + clone.outerHTML + '</body></html>');
    win.document.close();
    this.setState({ spoken: 'Score-only print view opened' });
    const printNow = () => setTimeout(() => { win.focus(); win.print(); }, 120);
    if (win.document.fonts && win.document.fonts.ready) win.document.fonts.ready.then(printNow).catch(printNow); else printNow();
  }""",
    'score-only print'
)

# Overlay scroll priority and cursor following. Playback must never drag the editor viewport around.
old_scroller = """  scroller() {
    const s = this.state;
    const pick = name => document.querySelector('[data-scroll="' + name + '"]');
    if (s.panel) return pick('panel');
    if (s.hub) return pick('hub');
    if (s.picker) return pick('picker');
    if (s.halo) return pick('halo');
    if (s.menu) return pick('menu');
    if (s.zone === 1) return pick('players');
    if (s.zone === 2) return pick('toolbar');
    if (s.zone === 4) return pick('props');
    return pick('score');
  }"""
new_scroller = """  scroller() {
    const s = this.state;
    const pick = name => document.querySelector('[data-scroll="' + name + '"]');
    if (s.tour) return pick('tour');
    if (s.captureFor) return pick('capture');
    if (s.remapFor) return pick('remap');
    if (s.kb) return pick('keyboard');
    if (s.panel) return pick('panel');
    if (s.hub) return pick('hub');
    if (s.picker) return pick('picker');
    if (s.halo) return pick('halo');
    if (s.menu) return pick('menu');
    if (s.zone === 1) return pick('players');
    if (s.zone === 2) return pick('toolbar');
    if (s.zone === 4) return pick('props');
    return pick('score');
  }"""
once(old_scroller, new_scroller, 'overlay scroll priority')
regex_once(
    r"    if \(s\.zone === 3 && !s\.halo && !s\.picker && !s\.menu && !s\.kb\) \{\n      const caret = \[\]\.slice\.call\(document\.querySelectorAll\('\[data-scroll=\"score\"\] div'\)\)\n        \.find\(d => \(d\.style && d\.style\.animationName === 'caretPulse'\) \|\| \(d\.getAttribute\('style'\) \|\| ''\)\.indexOf\('caretPulse'\) >= 0\);\n      return this\.reveal\(caret\);\n    \}",
    "    if (s.zone === 3 && !s.halo && !s.picker && !s.menu && !s.kb && !s.playing) {\n      const caret = document.querySelector('[data-score-caret=\"true\"]');\n      if (caret) this.reveal(caret);\n      return;\n    }",
    'cursor follow without playback'
)

# Theme hooks in render.
once(
    "    const accent = this.props.accentColor || '#7f9e90';",
    "    const theme = themeById(s.theme);\n    const accent = theme.accent;",
    'render theme selection'
)
once(
    "    return {\n      padStatus: s.padStatus,",
    "    return {\n      rootStyle: 'width:100%;height:100vh;background:var(--bg);color:var(--text);display:grid;grid-template-rows:46px 30px minmax(0,1fr);grid-template-columns:minmax(0,1fr);overflow:hidden;' + themeCss(theme),\n      themeRows: THEMES.map(t => ({\n        name: t.name,\n        onSelect: () => this.setTheme(t.id),\n        style: 'display:flex;align-items:center;gap:8px;min-width:0;padding:8px 9px;border-radius:6px;cursor:pointer;font-size:11.5px;font-weight:600;border:1px solid ' + (t.id === theme.id ? accent : 'var(--border)') + ';background:' + (t.id === theme.id ? 'rgba(var(--accent-rgb),.16)' : 'var(--control)') + ';color:var(--text);',\n        bgSwatch: 'width:12px;height:12px;border-radius:3px;background:' + t.bg + ';border:1px solid ' + t.borderStrong + ';',\n        panelSwatch: 'width:12px;height:12px;border-radius:3px;background:' + t.panel + ';border:1px solid ' + t.borderStrong + ';',\n        accentSwatch: 'width:12px;height:12px;border-radius:3px;background:' + t.accent + ';border:1px solid ' + t.accentSoft + ';'\n      })),\n      padStatus: s.padStatus,",
    'theme render values'
)
once(
    "        { k: 'TEMPO', v: s.tempo + ' BPM', t: 'tempo', act: () => this.setTempo(1) }",
    "        { k: 'TEMPO', v: s.tempo + ' BPM', t: 'tempo', act: () => this.setTempo(1) },\n        { k: 'THEME', v: theme.name, t: 'theme', act: () => this.setTheme(THEMES[(THEMES.findIndex(t => t.id === theme.id) + 1) % THEMES.length].id) }",
    'theme setup row'
)

# Older controller focus path also knows themes.
once(
    "      .concat([{ t: 'title', i: 0, label: 'Title' }, { t: 'composer', i: 0, label: 'Composer' }, { t: 'key', i: 0, label: 'Key signature' }, { t: 'meter', i: 0, label: 'Time signature' }, { t: 'tempo', i: 0, label: 'Tempo' }])\n      .concat(CLEFS.map((c, i) => ({ t: 'clef', i: i, label: c.name + ' clef' })));",
    "      .concat([{ t: 'title', i: 0, label: 'Title' }, { t: 'composer', i: 0, label: 'Composer' }, { t: 'key', i: 0, label: 'Key signature' }, { t: 'meter', i: 0, label: 'Time signature' }, { t: 'tempo', i: 0, label: 'Tempo' }])\n      .concat(THEMES.map((t, i) => ({ t: 'theme', i: i, label: t.name + ' theme' })))\n      .concat(CLEFS.map((c, i) => ({ t: 'clef', i: i, label: c.name + ' clef' })));",
    'controller theme focus list'
)
once(
    "    else if (it.t === 'proj') [() => this.newProject(), () => { const el = document.getElementById('legato-open'); if (el) el.click(); }, () => this.saveProject()][it.i]();",
    "    else if (it.t === 'proj') [() => this.newProject(), () => { const el = document.getElementById('legato-open'); if (el) el.click(); }, () => this.saveProject()][it.i]();\n    else if (it.t === 'theme') this.setTheme(THEMES[it.i].id);",
    'controller theme activation'
)

# Protect metadata that requires literal colours before replacing the visual palette with CSS variables.
props_match = re.search(r'<script type="text/x-dc" data-dc-script data-props="[^"]*">', text)
if not props_match:
    raise SystemExit('component props tag not found')
props_tag = props_match.group(0).replace('#7f9e90', '#42e69a')
text = text.replace(props_match.group(0), '__LEGATO_PROPS_TAG__', 1)
thumb_match = re.search(r'<template id="__bundler_thumbnail".*?</template>', text, flags=re.S)
if not thumb_match:
    raise SystemExit('thumbnail template not found')
thumbnail = thumb_match.group(0).replace('#181b1f', '#111b17').replace('#7f9e90', '#42e69a').replace('#111315', '#07100c')
text = text.replace(thumb_match.group(0), '__LEGATO_THUMBNAIL__', 1)

# Existing interface colours become theme variables. Special-purpose warning/error colours remain unchanged.
colour_map = {
    '#111315': 'var(--bg)', '#181b1f': 'var(--panel)', '#20242a': 'var(--raised)', '#24292f': 'var(--control)',
    '#343a42': 'var(--border)', '#3a424a': 'var(--border-strong)', '#454e57': 'var(--border-strong)', '#414953': 'var(--border-strong)',
    '#56616c': 'var(--border-hover)', '#2b3138': 'var(--hover)', '#1b1f24': 'var(--panel-low)', '#141917': 'var(--panel-low)',
    '#1f2523': 'var(--track)', '#090c0b': 'var(--input-bg)', '#4a535d': 'var(--toggle-off)', '#2a3230': 'var(--control)',
    '#f1f3f4': 'var(--text)', '#e4e8eb': 'var(--text-strong)', '#cbd1d6': 'var(--text-2)', '#c2c8ce': 'var(--text-2)',
    '#b3bbc3': 'var(--muted-text)', '#a7afb8': 'var(--muted)', '#9fa7b2': 'var(--muted)', '#858f9a': 'var(--muted-2)',
    '#707985': 'var(--muted-3)', '#97a19c': 'var(--muted)', '#7b847f': 'var(--muted-2)',
    '#7f9e90': 'var(--accent)', '#9ab5a8': 'var(--accent-soft)', '#54786a': 'var(--score-accent)',
    '#f8f7f4': 'var(--paper)', '#1b1a17': 'var(--ink)', '#26241f': 'var(--staff-ink)', '#3d3a34': 'var(--ink-soft)',
    '#6b6760': 'var(--paper-muted)', '#8e8a80': 'var(--paper-muted)', '#a09b90': 'var(--paper-muted)'
}
for old, new in colour_map.items():
    text = text.replace(old, new)
text = text.replace('rgba(127,158,144,', 'rgba(var(--accent-rgb),')
text = text.replace('__LEGATO_PROPS_TAG__', props_tag, 1)
text = text.replace('__LEGATO_THUMBNAIL__', thumbnail, 1)

# Default variables, self-contained scrolling and the full theme catalogue are inserted after colour conversion.
once(
    '<style>\n  [data-ptr][data-scan-selected="true"] {',
    '''<style>
  :root {
    --bg:#07100c;--panel:#111b17;--raised:#17241f;--control:#1d2c26;--panel-low:#0d1713;
    --border:#2f4b3f;--border-strong:#426657;--border-hover:#5b8d77;--hover:#22362e;--track:#13221c;--input-bg:#060c09;--toggle-off:#466056;
    --text:#f5fff9;--text-strong:#ecfff4;--text-2:#d0e9dc;--muted-text:#b3cdbf;--muted:#91ad9e;--muted-2:#718b7e;--muted-3:#587064;
    --accent:#42e69a;--accent-soft:#88f4bf;--accent-rgb:66,230,154;--score-accent:#167b4f;
    --paper:#fffdf7;--ink:#151813;--staff-ink:#20241d;--ink-soft:#3d4439;--paper-muted:#77756d;
  }
  [data-scroll] { overscroll-behavior: contain; scrollbar-gutter: stable; touch-action: pan-x pan-y; }
  [data-ptr][data-scan-selected="true"] {''',
    'default theme variables and scroll containment'
)

# Insert theme definitions directly after the meter list.
theme_code = r'''
const THEME_DARK = {
  bg:'#07100c',panel:'#111b17',raised:'#17241f',control:'#1d2c26',panelLow:'#0d1713',border:'#2f4b3f',borderStrong:'#426657',borderHover:'#5b8d77',hover:'#22362e',track:'#13221c',inputBg:'#060c09',toggleOff:'#466056',
  text:'#f5fff9',textStrong:'#ecfff4',text2:'#d0e9dc',mutedText:'#b3cdbf',muted:'#91ad9e',muted2:'#718b7e',muted3:'#587064',paper:'#fffdf7',ink:'#151813',staffInk:'#20241d',inkSoft:'#3d4439',paperMuted:'#77756d',scoreAccent:'#167b4f'
};
const THEME_LIGHT = {
  bg:'#e8edf2',panel:'#f8fafc',raised:'#ffffff',control:'#eef2f6',panelLow:'#dde4eb',border:'#c3ced9',borderStrong:'#9fadb9',borderHover:'#718394',hover:'#e1e8ef',track:'#d4dde5',inputBg:'#ffffff',toggleOff:'#9aa8b4',
  text:'#17212a',textStrong:'#0d151c',text2:'#33414d',mutedText:'#4f606e',muted:'#617483',muted2:'#758692',muted3:'#87949e',paper:'#fffdf7',ink:'#151813',staffInk:'#20241d',inkSoft:'#3d4439',paperMuted:'#77756d',scoreAccent:'#145b9e'
};
function makeTheme(id, name, accent, accentSoft, accentRgb, base, extra) {
  return Object.assign({}, base, extra || {}, { id:id, name:name, accent:accent, accentSoft:accentSoft, accentRgb:accentRgb });
}
const THEMES = [
  makeTheme('verdant','Verdant Studio','#42e69a','#88f4bf','66,230,154',THEME_DARK,{}),
  makeTheme('ocean','Ocean Blueprint','#43d9ff','#91ebff','67,217,255',THEME_DARK,{bg:'#061117',panel:'#0d1b24',raised:'#132735',control:'#183241',panelLow:'#091721',border:'#284b5e',borderStrong:'#376a82',borderHover:'#4d91af',hover:'#1e3c4d',track:'#102633',inputBg:'#040c11',toggleOff:'#3d6171',scoreAccent:'#087da0'}),
  makeTheme('cobalt','Cobalt Stage','#6f9cff','#a8c2ff','111,156,255',THEME_DARK,{bg:'#080d18',panel:'#11192a',raised:'#18233a',control:'#1e2b46',panelLow:'#0c1423',border:'#31456c',borderStrong:'#486293',borderHover:'#6685bd',hover:'#263754',track:'#14213a',inputBg:'#060a12',toggleOff:'#4b5f82',scoreAccent:'#315eb8'}),
  makeTheme('plum','Plum Nocturne','#ca8cff','#e2b8ff','202,140,255',THEME_DARK,{bg:'#100914',panel:'#1c1123',raised:'#291831',control:'#34203e',panelLow:'#170d1c',border:'#573566',borderStrong:'#754b86',borderHover:'#9b68ad',hover:'#40264b',track:'#291630',inputBg:'#0b060e',toggleOff:'#6b5173',scoreAccent:'#8b42b3'}),
  makeTheme('ruby','Ruby Concert','#ff7186','#ffacb8','255,113,134',THEME_DARK,{bg:'#15090c',panel:'#241116',raised:'#31171d',control:'#3d1d25',panelLow:'#1d0d11',border:'#68313d',borderStrong:'#8d4655',borderHover:'#bd6475',hover:'#4b252e',track:'#30151b',inputBg:'#0d0507',toggleOff:'#79505a',scoreAccent:'#b52f48'}),
  makeTheme('amber','Amber Manuscript','#ffc857','#ffe09a','255,200,87',THEME_DARK,{bg:'#151007',panel:'#241b0e',raised:'#312514',control:'#3d2e18',panelLow:'#1d160b',border:'#654b26',borderStrong:'#896638',borderHover:'#b4884c',hover:'#4a381f',track:'#2e2211',inputBg:'#0d0904',toggleOff:'#715f42',scoreAccent:'#a96d00'}),
  makeTheme('coral','Coral Workshop','#ff8b6f','#ffb8a6','255,139,111',THEME_DARK,{bg:'#140c09',panel:'#221713',raised:'#302019',control:'#3a281f',panelLow:'#1b120e',border:'#634335',borderStrong:'#865c49',borderHover:'#b47a63',hover:'#493127',track:'#2d1e17',inputBg:'#0c0705',toggleOff:'#735a50',scoreAccent:'#b94d32'}),
  makeTheme('teal','Midnight Teal','#39dccb','#8bece2','57,220,203',THEME_DARK,{bg:'#051211',panel:'#0c1e1c',raised:'#122a27',control:'#183632',panelLow:'#081916',border:'#28534d',borderStrong:'#39736b',borderHover:'#4e9b91',hover:'#1e423d',track:'#0f2925',inputBg:'#030b0a',toggleOff:'#3e6b65',scoreAccent:'#087f73'}),
  makeTheme('contrast','High Contrast','#f4ff4f','#fbff9e','244,255,79',THEME_DARK,{bg:'#000000',panel:'#090909',raised:'#111111',control:'#1b1b1b',panelLow:'#050505',border:'#5f5f5f',borderStrong:'#8b8b8b',borderHover:'#d4d4d4',hover:'#262626',track:'#202020',inputBg:'#000000',toggleOff:'#777777',text:'#ffffff',textStrong:'#ffffff',text2:'#f4f4f4',mutedText:'#dedede',muted:'#c7c7c7',muted2:'#a8a8a8',muted3:'#888888',scoreAccent:'#5f6900'}),
  makeTheme('arctic','Arctic Light','#1677df','#65a9ef','22,119,223',THEME_LIGHT,{}),
  makeTheme('paper','Paper & Ink','#a45f2a','#cf9366','164,95,42',THEME_LIGHT,{bg:'#e9e1d4',panel:'#fbf7ef',raised:'#fffdf8',control:'#f2eadf',panelLow:'#ded4c5',border:'#cbbba7',borderStrong:'#a99780',borderHover:'#7f6d59',hover:'#e8ddcf',track:'#d8ccbc',inputBg:'#fffdf9',toggleOff:'#a99b8a',text:'#28231d',textStrong:'#191510',text2:'#4a4036',mutedText:'#62564a',muted:'#76695d',muted2:'#887b6f',muted3:'#9b9086',paper:'#fffaf0',scoreAccent:'#8b451b'}),
  makeTheme('lavender','Lavender Light','#7657dc','#aa95ee','118,87,220',THEME_LIGHT,{bg:'#e9e6f2',panel:'#faf9fd',raised:'#ffffff',control:'#f0edf7',panelLow:'#ddd8ea',border:'#c8c0dc',borderStrong:'#a69bbb',borderHover:'#7c6d99',hover:'#e6e1f0',track:'#d8d2e6',inputBg:'#ffffff',toggleOff:'#a49ab5',text:'#211c2c',textStrong:'#15111d',text2:'#423850',mutedText:'#5a4e68',muted:'#6d617a',muted2:'#80758b',muted3:'#958c9d',scoreAccent:'#5637af'})
];
function themeById(id) { return THEMES.find(t => t.id === id) || THEMES[0]; }
function themeCss(t) {
  return '--bg:' + t.bg + ';--panel:' + t.panel + ';--raised:' + t.raised + ';--control:' + t.control + ';--panel-low:' + t.panelLow + ';--border:' + t.border + ';--border-strong:' + t.borderStrong + ';--border-hover:' + t.borderHover + ';--hover:' + t.hover + ';--track:' + t.track + ';--input-bg:' + t.inputBg + ';--toggle-off:' + t.toggleOff + ';--text:' + t.text + ';--text-strong:' + t.textStrong + ';--text-2:' + t.text2 + ';--muted-text:' + t.mutedText + ';--muted:' + t.muted + ';--muted-2:' + t.muted2 + ';--muted-3:' + t.muted3 + ';--accent:' + t.accent + ';--accent-soft:' + t.accentSoft + ';--accent-rgb:' + t.accentRgb + ';--score-accent:' + t.scoreAccent + ';--paper:' + t.paper + ';--ink:' + t.ink + ';--staff-ink:' + t.staffInk + ';--ink-soft:' + t.inkSoft + ';--paper-muted:' + t.paperMuted + ';';
}
'''
once("const METERS = ['4/4', '3/4', '2/2', '6/8', '5/4', '12/8', '7/8'];", "const METERS = ['4/4', '3/4', '2/2', '6/8', '5/4', '12/8', '7/8'];\n" + theme_code, 'theme catalogue')

# The print button description now reflects what it actually does.
text = text.replace("['Print / PDF', 'Browser print of the engraved pages']", "['Print / PDF', 'Print only the engraved score or save it as PDF']")

# Static regression checks before writing anything.
checks = {
    'cache bust': 'support.js?v=20260727-meter-themes-scroll-2',
    'theme count': "makeTheme('lavender'",
    'theme picker': 'list="{{ themeRows }}"',
    'continuous polygon': 'clip-path:polygon(',
    'secondary continuity': 'while (j + 1 < group.length && has[j + 1]) j += 1;',
    'meter 4/4 grouping': "'4/4': [2, 2]",
    'multi-digit time': 'timeGlyphs(met[0])',
    'score only print': "document.querySelector('[data-print-score=\"true\"]')",
    'octave panel': "s.panel === 'clefOctave'",
    'octave preview': 'this.warmScore(this.state.staff);',
    'cursor marker': 'data-score-caret="true"',
    'no playback follow': '&& !s.playing) {',
    'modal scroll priority': "if (s.kb) return pick('keyboard');"
}
for label, needle in checks.items():
    if needle not in text:
        raise SystemExit(f'regression check failed: {label}')
if text == original:
    raise SystemExit('patch made no changes')
if text.count('const THEMES = [') != 1:
    raise SystemExit('theme catalogue duplicated')
if text.count('data-print-score="true"') != 1:
    raise SystemExit('print score marker duplicated or missing')
if 'levelUnit = Math.max(.125' in text:
    raise SystemExit('old secondary beam splitting survived')
if 'window.print(), 250' in text:
    raise SystemExit('old page screenshot print survived')

# Parse the embedded JavaScript with Node before replacing the file.
script_match = re.search(r'<script type="text/x-dc"[^>]*>\n(.*?)\n</script>', text, flags=re.S)
if not script_match:
    raise SystemExit('embedded application script not found')
with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as tmp:
    tmp.write(script_match.group(1))
    temp_name = tmp.name
result = subprocess.run(['node', '--check', temp_name], text=True, capture_output=True)
if result.returncode:
    raise SystemExit('JavaScript syntax check failed:\n' + result.stdout + result.stderr)

path.write_text(text, encoding='utf-8')
print('Applied guarded meter/theme/print/scroll repairs successfully.')
