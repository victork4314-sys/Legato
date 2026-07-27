from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')
original = text

if '20260727-rests-ties-focus-fonts-1' in text:
    print('Interaction repair already applied')
    raise SystemExit(0)


def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)


def sub(pattern, replacement, label, flags=0):
    global text
    found = list(re.finditer(pattern, text, flags))
    if len(found) != 1:
        raise SystemExit(f'{label}: expected 1 match, found {len(found)}')
    text = re.sub(pattern, lambda _: replacement, text, count=1, flags=flags)


# Fresh build and selectable fonts.
one('<script src="./support.js?v=20260727-meter-themes-scroll-2"></script>',
    '<script src="./support.js?v=20260727-rests-ties-focus-fonts-1"></script>', 'cache marker')
one("<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Source+Serif+4:wght@500;600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=Noto+Music&amp;display=swap\" rel=\"stylesheet\">",
    "<link href=\"https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&amp;family=EB+Garamond:wght@500;600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=IBM+Plex+Sans:wght@400;500;600;700&amp;family=IBM+Plex+Serif:wght@500;600&amp;family=Inter:wght@400;500;600;700&amp;family=Libre+Baskerville:wght@400;700&amp;family=Noto+Music&amp;family=Noto+Sans:wght@400;500;600;700&amp;family=Noto+Serif:wght@500;600&amp;family=Source+Sans+3:wght@400;500;600;700&amp;family=Source+Serif+4:wght@500;600&amp;display=swap\" rel=\"stylesheet\">",
    'font stylesheet')
one('    --paper:#fffdf7;--ink:#151813;--staff-ink:#20241d;--ink-soft:#3d4439;--paper-muted:#77756d;\n',
    '    --paper:#fffdf7;--ink:#151813;--staff-ink:#20241d;--ink-soft:#3d4439;--paper-muted:#77756d;\n    --ui-font:\'Inter\',sans-serif;--score-font:\'Source Serif 4\',serif;\n',
    'font css defaults')

font_catalogue = """const FONT_PACKS = [
  { id:'studio', name:'Studio', ui:"'Inter',sans-serif", score:"'Source Serif 4',serif" },
  { id:'accessible', name:'Accessible', ui:"'Atkinson Hyperlegible',sans-serif", score:"'Noto Serif',serif" },
  { id:'humanist', name:'Humanist', ui:"'Source Sans 3',sans-serif", score:"'EB Garamond',serif" },
  { id:'plex', name:'Plex', ui:"'IBM Plex Sans',sans-serif", score:"'IBM Plex Serif',serif" },
  { id:'classical', name:'Classical', ui:"'Noto Sans',sans-serif", score:"'Libre Baskerville',serif" },
  { id:'clean', name:'Clean', ui:"'Noto Sans',sans-serif", score:"'Source Serif 4',serif" }
];
function fontById(id) { return FONT_PACKS.find(f => f.id === id) || FONT_PACKS[0]; }
function fontCss(f) { return '--ui-font:' + f.ui + ';--score-font:' + f.score + ';'; }

"""
one("const KB_KEYS = ('abcdefghijklmnopqrstuvwxyz0123456789').split('').concat(['É', 'é', '♭', '♯', '.', ',', '-', \"'\", 'SPACE', 'DEL', 'DONE']);",
    font_catalogue + "const KB_KEYS = ('abcdefghijklmnopqrstuvwxyz0123456789').split('').concat(['É', 'é', '♭', '♯', '.', ',', '-', \"'\", 'SPACE', 'DEL', 'DONE']);",
    'font catalogue')
one("const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks'];",
    "const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks', 'fontPack'];",
    'document fonts')
one("const THEME_STORE = 'legato.theme.v1';", "const THEME_STORE = 'legato.theme.v1';\nconst FONT_STORE = 'legato.fonts.v1';", 'font storage')
one("    kb: null, kbIdx: 0, kbShift: false, selId: null,",
    "    kb: null, kbIdx: 0, kbShift: false, selId: null, tieFrom: null,", 'tie state')
one("sidebarsHidden: false, autoScan: false, theme: 'verdant'",
    "sidebarsHidden: false, autoScan: false, theme: 'verdant', fontPack: 'studio'", 'font state')
one("    try { const savedTheme = localStorage.getItem(THEME_STORE); if (savedTheme && THEMES.some(t => t.id === savedTheme)) this.setState({ theme: savedTheme }); } catch (e) {}",
    "    try { const savedTheme = localStorage.getItem(THEME_STORE); if (savedTheme && THEMES.some(t => t.id === savedTheme)) this.setState({ theme: savedTheme }); } catch (e) {}\n    try { const savedFont = localStorage.getItem(FONT_STORE); if (savedFont && FONT_PACKS.some(f => f.id === savedFont)) this.setState({ fontPack: savedFont }); } catch (e) {}",
    'load font choice')

# The editor is one normal selectable destination. Nested score items stay out of global scan.
one('      if (el.offsetParent === null || el.closest(\'[data-scroll="score"]\')) return false;',
    "      const scoreShell = el.getAttribute('data-score-editor-shell') === 'true';\n      if (el.offsetParent === null || (el.closest('[data-scroll=\"score\"]') && !scoreShell)) return false;",
    'score scan inclusion')
one("  scanZoneForElement(el) {\n    if (el.closest('[data-scroll=\"players\"]')) return 1;",
    "  scanZoneForElement(el) {\n    if (el.getAttribute('data-score-editor-shell') === 'true') return 0;\n    if (el.closest('[data-scroll=\"players\"]')) return 1;",
    'score gateway zone')
one("  visibleScanItems() {",
    "  enterScoreEditor() {\n    document.querySelectorAll('[data-scan-selected=\"true\"]').forEach(el => el.removeAttribute('data-scan-selected'));\n    this.rumble('tick');\n    this.setState({ zone: 3, focus: 0, spoken: 'Score editor — arrows move through the score; use normal zone navigation to leave' });\n  }\n  visibleScanItems() {",
    'enter score method')
one("    const liveTarget = document.querySelector('[data-scan-selected=\"true\"]');\n    if (liveTarget && this.state.zone !== 3) { liveTarget.click(); return; }",
    "    const liveTarget = document.querySelector('[data-scan-selected=\"true\"]');\n    if (liveTarget && liveTarget.getAttribute('data-score-editor-shell') === 'true') { liveTarget.click(); return; }\n    if (liveTarget && this.state.zone !== 3) { liveTarget.click(); return; }",
    'activate score gateway')
one('<div data-scroll="score" style="flex: 1; min-height: 0; overflow: auto; padding: 12px 0 18px; background: radial-gradient(1200px 500px at 50% -5%, var(--raised), var(--bg) 70%);">',
    '<div data-scroll="score" data-ptr="Score editor" data-score-editor-shell="true" onClick="{{ enterScoreEditor }}" style="flex: 1; min-height: 0; overflow: auto; padding: 12px 0 18px; background: radial-gradient(1200px 500px at 50% -5%, var(--raised), var(--bg) 70%);">',
    'score gateway template')
one("      openPicker: () => this.openPicker(),",
    "      openPicker: () => this.openPicker(),\n      enterScoreEditor: () => this.enterScoreEditor(),",
    'score gateway binding')

# Deleted notes leave rhythmic space, not stored fake rest objects. Entering a note also replaces any old overlapping rest object.
one("        const rests = list.filter(n => !n.rest).map(n => ({ id: 'n' + Math.random().toString(36).slice(2, 8), s: n.s, p: n.p, d: n.d, step: 4, voice: n.voice || 1, rest: true }));\n        return { notes: p.notes.filter(n => ids.indexOf(n.id) < 0).concat(rests), range: null, selId: null, spoken: list.length + ' items deleted — rests inserted' };",
    "        return { notes: p.notes.filter(n => ids.indexOf(n.id) < 0), range: null, selId: null, spoken: list.length + ' items deleted' };",
    'range deletion rests')
one("      const rest = stack.length > 1 ? [] : [{ id: 'n' + Math.random().toString(36).slice(2, 8), s: sel.s, p: sel.p, d: sel.d, step: 4, voice: sel.voice || 1, rest: true }];\n      const others = stack.filter(n => n.id !== sel.id);",
    "      const others = stack.filter(n => n.id !== sel.id);",
    'single deletion rest')
one("        notes: p.notes.filter(n => n.id !== sel.id).concat(rest),",
    "        notes: p.notes.filter(n => n.id !== sel.id),", 'single deletion result')
one("          : 'Note deleted — rest inserted'",
    "          : 'Note deleted'", 'single deletion message')
one("      const usedArmed = Object.keys(s.armed || {}).some(k => s.armed[k]);\n      const cap2 = this.barCapacity();",
    "      const usedArmed = Object.keys(s.armed || {}).some(k => s.armed[k]);\n      const nEnd = s.pos + noteBeats(n);\n      const kept = s.notes.filter(x => !(x.rest && x.s === s.staff && (x.voice || 1) === (s.voice || 1) && x.p < nEnd - .0005 && x.p + noteBeats(x) > s.pos + .0005));\n      const cap2 = this.barCapacity();",
    'replace overlapping rests')
one("        notes: s.notes.concat([n]),", "        notes: kept.concat([n]),", 'enter note rest replacement')

# A tie is a two-point operation between adjacent notes of the same sounding pitch, staff and voice.
sub(r"  toggleTie\(\) \{\n    if \(!this\.editNote\(n => \(\{ tie: !n\.tie \}\), 'Tie toggled'\)\) this\.setState\(\{ spoken: 'Select a note to tie it' \}\);\n  \}",
"""  toggleTie() {
    const sel = this.selected();
    if (!sel || sel.rest) return this.setState({ tieFrom: null, spoken: 'Select the first note of the tie' });
    if (sel.tie || sel.tieTo) {
      return this.editNote({ tie: false, tieTo: null }, 'Tie removed');
    }
    this.setState({ tieFrom: sel.id, spoken: 'Tie start selected — choose the adjacent note of the same pitch and press A' });
  }
  finishTie(target) {
    const start = this.state.notes.find(n => n.id === this.state.tieFrom);
    if (!start) return this.setState({ tieFrom: null, spoken: 'The tie start no longer exists' });
    if (!target || target.rest) return this.setState({ spoken: 'A tie must end on a note' });
    if (!target.id) target.id = 'n' + Math.random().toString(36).slice(2, 8);
    const sameStaff = target.s === start.s;
    const sameVoice = (target.voice || 1) === (start.voice || 1);
    const startMidi = midiFor(start.step, this.state.clefs[start.s] === 'bass', start.acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[start.s]);
    const targetMidi = midiFor(target.step, this.state.clefs[target.s] === 'bass', target.acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[target.s]);
    const adjacent = Math.abs(target.p - (start.p + noteBeats(start))) < .01;
    if (!sameStaff || !sameVoice || startMidi !== targetMidi || !adjacent) {
      return this.setState({ spoken: 'That cannot be tied — choose the immediately following note of the same pitch, voice and staff' });
    }
    this.setState(s => ({
      notes: s.notes.map(n => n.id === start.id ? Object.assign({}, n, { tie: true, tieTo: target.id }) : n),
      tieFrom: null, selId: target.id, staff: target.s, pos: target.p, step: target.step,
      spoken: 'Tie completed from point one to point two'
    }));
  }""", 'two point tie')

# Tie selection happens before ordinary note selection.
one("  selectNote(n) {\n    if (this.state.zone !== 3) this.setState({ zone: 3 });\n    if (n.rest) {",
    "  selectNote(n) {\n    if (!n) return this.setState({ selId: null });\n    if (!n.id) n.id = 'n' + Math.random().toString(36).slice(2, 8);\n    if (this.state.tieFrom && n.id !== this.state.tieFrom) return this.finishTie(n);\n    if (this.state.zone !== 3) this.setState({ zone: 3 });\n    if (n.rest) {",
    'tie target selection')
one("    if (!n) return this.setState({ selId: null });\n    if (!n.id) n.id = 'n' + Math.random().toString(36).slice(2, 8);\n    this.audition(n.step, n.s, n.acc, n.art, n);",
    "    this.audition(n.step, n.s, n.acc, n.art, n);", 'remove duplicate note guard')
one("    else this.setState({ spoken: 'Tie applied from this note' });",
    "    else this.toggleTie();", 'duration wheel tie')
one("        if (/^Tie|^Slur|^Phrase/.test(name)) { this.editNote({ tie: true }, name + ' started'); }\n        else this.editNote(n => ({ line: glyph, marks: (n.marks || []).concat([{ g: glyph, place: 'below' }]) }), name + ' started from this note');",
    "        if (/^Tie/.test(name)) { this.toggleTie(); }\n        else if (/^Slur|^Phrase/.test(name)) { this.editNote({ line: glyph }, name + ' started'); }\n        else this.editNote(n => ({ line: glyph, marks: (n.marks || []).concat([{ g: glyph, place: 'below' }]) }), name + ' started from this note');",
    'line tie command')
one("      else if (/^Tie/.test(name)) {\n       this.toggleTie(); msg = 'Tie toggled';\n     }",
    "      else if (/^Tie/.test(name)) {\n       this.toggleTie(); msg = 'Tie selection started';\n     }",
    'secondary tie wording') if "      else if (/^Tie/.test(name)) {\n       this.toggleTie(); msg = 'Tie toggled';\n     }" in text else None

# Playback and drawing follow the chosen endpoint; old Boolean ties still migrate to the next matching adjacent pitch.
one("      while (chain && chain.tie && guard++ < 32) {\n        const nxt = s.notes.filter(x => x.s === n.s && (x.voice || 1) === (n.voice || 1) && !x.rest && Math.abs(x.p - (chain.p + noteBeats(chain))) < .002)[0];",
    "      while (chain && (chain.tie || chain.tieTo) && guard++ < 32) {\n        const nxt = chain.tieTo\n          ? s.notes.find(x => x.id === chain.tieTo)\n          : s.notes.filter(x => x.s === n.s && (x.voice || 1) === (n.voice || 1) && !x.rest && x.step === chain.step && Math.abs(x.p - (chain.p + noteBeats(chain))) < .002)[0];",
    'tie playback endpoint')
one("           const nextTie = n.tie ? s.notes.filter(m => m.s === n.s && m.p > n.p).sort((a, b) => a.p - b.p)[0] : null;",
    "           const nextTie = n.tieTo ? s.notes.find(m => m.id === n.tieTo) : (n.tie ? s.notes.filter(m => !m.rest && m.s === n.s && (m.voice || 1) === (n.voice || 1) && m.step === n.step && Math.abs(m.p - (n.p + noteBeats(n))) < .01).sort((a, b) => a.p - b.p)[0] : null);",
    'tie drawing endpoint')

# Time signature: two equal 24px cells exactly centered on the 48px staff, with a clearer gap after the key.
one("        const timeWidth = Math.max(String(met[0]).length, String(met[1]).length) * 20 + 8;",
    "        const timeWidth = Math.max(String(met[0]).length, String(met[1]).length) * 17 + 6;", 'time width')
one("        const keyX = 52, timeX = 70 + (K.n || 0) * 12;",
    "        const keyX = 52, timeX = 76 + (K.n || 0) * 12;", 'time horizontal position')
one("          timeTopStyle: 'position:absolute;left:' + timeX + 'px;top:-3px;width:' + timeWidth + 'px;height:27px;display:grid;place-items:center;' + BR + 'font-size:43px;line-height:1;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',\n          timeBotStyle: 'position:absolute;left:' + timeX + 'px;top:21px;width:' + timeWidth + 'px;height:27px;display:grid;place-items:center;' + BR + 'font-size:43px;line-height:1;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',\n          timeHitStyle: 'position:absolute;left:' + (timeX - 3) + 'px;top:-6px;width:' + (timeWidth + 6) + 'px;height:60px;cursor:pointer;z-index:4;',",
    "          timeTopStyle: 'position:absolute;left:' + timeX + 'px;top:0;width:' + timeWidth + 'px;height:24px;display:flex;align-items:center;justify-content:center;' + BR + 'font-size:32px;line-height:24px;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',\n          timeBotStyle: 'position:absolute;left:' + timeX + 'px;top:24px;width:' + timeWidth + 'px;height:24px;display:flex;align-items:center;justify-content:center;' + BR + 'font-size:32px;line-height:24px;color:var(--ink);white-space:nowrap;cursor:pointer;z-index:5;',\n          timeHitStyle: 'position:absolute;left:' + (timeX - 3) + 'px;top:0;width:' + (timeWidth + 6) + 'px;height:48px;cursor:pointer;z-index:4;',",
    'center time signature')

# Staff lines remain instantly clickable even where generated rests are visible.
one("        style: 'position:absolute;left:' + (X0 - 16) + 'px;top:' + (st.top - 16) + 'px;width:' + (s.bars * this.barCapacity() * XS + 20) + 'px;height:80px;cursor:crosshair;',",
    "        style: 'position:absolute;left:' + (X0 - 16) + 'px;top:' + (st.top - 16) + 'px;width:' + (s.bars * this.barCapacity() * XS + 20) + 'px;height:80px;cursor:crosshair;z-index:1;',",
    'staff hit priority')
one("            style: glyphAt(noteX(r.p) - 7, y, 48, 'rgba(27,26,23,.42)')",
    "            style: glyphAt(noteX(r.p) - 7, y, 48, 'rgba(27,26,23,.42)') + 'pointer-events:none;'",
    'generated rest pointer pass through')

# Font pack UI and persistence.
sub(r"\n  setTheme\(id\) \{", "\n  setFontPack(id) {\n    const f = fontById(id);\n    try { localStorage.setItem(FONT_STORE, f.id); } catch (e) {}\n    this.setState({ fontPack: f.id, spoken: f.name + ' font set' });\n  }\n  setTheme(id) {", 'font setter')
one("    const theme = themeById(s.theme);\n    const accent = theme.accent;",
    "    const theme = themeById(s.theme);\n    const font = fontById(s.fontPack);\n    const accent = theme.accent;", 'active font')
one("      rootStyle: 'width:100%;height:100vh;background:var(--bg);color:var(--text);display:grid;grid-template-rows:46px 30px minmax(0,1fr);grid-template-columns:minmax(0,1fr);overflow:hidden;' + themeCss(theme),",
    "      rootStyle: 'width:100%;height:100vh;background:var(--bg);color:var(--text);font-family:var(--ui-font);display:grid;grid-template-rows:46px 30px minmax(0,1fr);grid-template-columns:minmax(0,1fr);overflow:hidden;' + themeCss(theme) + fontCss(font),",
    'root font css')
one("      themeRows: THEMES.map(t => ({",
    "      fontRows: FONT_PACKS.map(f => ({\n        name: f.name,\n        sample: 'Legato · Étude',\n        onSelect: () => this.setFontPack(f.id),\n        style: 'display:flex;flex-direction:column;gap:4px;padding:9px;border-radius:6px;cursor:pointer;border:1px solid ' + (f.id === font.id ? accent : 'var(--border)') + ';background:' + (f.id === font.id ? 'rgba(var(--accent-rgb),.16)' : 'var(--control)') + ';font-family:' + f.ui + ';',\n        sampleStyle: 'font-family:' + f.score + ';font-size:15px;color:var(--text);'\n      })),\n      themeRows: THEMES.map(t => ({",
    'font render rows')
one("      .concat(THEMES.map((t, i) => ({ t: 'theme', i: i, label: t.name + ' theme' })))\n      .concat(CLEFS.map((c, i) => ({ t: 'clef', i: i, label: c.name + ' clef' })));",
    "      .concat(THEMES.map((t, i) => ({ t: 'theme', i: i, label: t.name + ' theme' })))\n      .concat(FONT_PACKS.map((f, i) => ({ t: 'font', i: i, label: f.name + ' font' })))\n      .concat(CLEFS.map((c, i) => ({ t: 'clef', i: i, label: c.name + ' clef' })));",
    'font scan items')
one("    else if (it.t === 'theme') this.setTheme(THEMES[it.i].id);",
    "    else if (it.t === 'theme') this.setTheme(THEMES[it.i].id);\n    else if (it.t === 'font') this.setFontPack(FONT_PACKS[it.i].id);",
    'font activation')

font_panel = """          <div style="border: 1px solid var(--border); border-radius: 6px; background: var(--raised); padding: 10px 11px 12px; margin-bottom: 10px;">
            <div style="font-family: var(--ui-font); font-size: 11.5px; font-weight: 600; color: var(--muted); letter-spacing: .02em; padding-bottom: 3px;">Fonts</div>
            <div style="font-size: 11px; color: var(--muted-2); padding-bottom: 9px;">Choose the interface and score-heading type together. Music symbols remain Bravura.</div>
            <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px;">
              <sc-for list="{{ fontRows }}" as="ft" hint-placeholder-count="6">
                <div onClick="{{ ft.onSelect }}" data-ptr="Font {{ ft.name }}" style="{{ ft.style }}" style-hover="filter:brightness(1.08)">
                  <span style="font-size:10px;color:var(--muted);">{{ ft.name }}</span>
                  <span style="{{ ft.sampleStyle }}">{{ ft.sample }}</span>
                </div>
              </sc-for>
            </div>
          </div>
"""
one("          </div>\n        </sc-if>\n\n\n        <div style=\"border: 1px solid var(--border); border-radius: 6px; background: var(--raised); padding: 10px 11px 12px; margin-bottom: 10px;\">\n          <div style=\"font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; color: var(--muted); letter-spacing: .02em; padding-bottom: 9px;\">SCORE SETUP — A EDITS, LEFT/RIGHT CHANGES</div>",
    "          </div>\n" + font_panel + "        </sc-if>\n\n\n        <div style=\"border: 1px solid var(--border); border-radius: 6px; background: var(--raised); padding: 10px 11px 12px; margin-bottom: 10px;\">\n          <div style=\"font-family: 'Inter', sans-serif; font-size: 11.5px; font-weight: 600; color: var(--muted); letter-spacing: .02em; padding-bottom: 9px;\">SCORE SETUP — A EDITS, LEFT/RIGHT CHANGES</div>",
    'font setup panel')

# Let the selected font affect all ordinary UI and score headings without touching notation or monospace readouts.
text = text.replace("font-family: 'Inter', sans-serif", "font-family: var(--ui-font)")
text = text.replace("font-family:\\'Inter\\',sans-serif", "font-family:var(--ui-font)")
text = text.replace("font-family: 'Source Serif 4', serif", "font-family: var(--score-font)")
text = text.replace("font-family:\\'Source Serif 4\\',serif", "font-family:var(--score-font)")
one("    const vars = themeCss(themeById(this.state.theme));",
    "    const vars = themeCss(themeById(this.state.theme)) + fontCss(fontById(this.state.fontPack));",
    'print font variables')

# Strong proof that the clarified request did not alter accidental or bumper behavior.
required_untouched = [
  "case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;",
  "case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;",
  "button4: 'previous-zone', button5: 'next-zone'"
]
for marker in required_untouched:
    if marker not in text:
        raise SystemExit('Clarified untouched control changed: ' + marker)

if text == original:
    raise SystemExit('No repair was applied')
path.write_text(text, encoding='utf-8')
print('Applied rests, two-point ties, selectable score editor, staff clicking, time placement and font choices')
