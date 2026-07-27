from pathlib import Path
import re

path = Path("index.html")
text = path.read_text(encoding="utf-8")
original = text

def once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 exact match, found {count}")
    text = text.replace(old, new, 1)

def regex_once(pattern, replacement, label, flags=0):
    global text
    text2, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 regex match, found {count}")
    text = text2

# Professional typography and a muted graphite/sage palette.
once(
    '<link href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@400;500;600;700&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=Noto+Music&amp;display=swap" rel="stylesheet">',
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&amp;family=Source+Serif+4:wght@500;600&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=Noto+Music&amp;display=swap" rel="stylesheet">',
    "font import"
)

palette = {
    "'Barlow Semi Condensed'": "'Inter'",
    "Barlow Semi Condensed": "Inter",
    "#74a12e": "#7f9e90",
    "#9dc95e": "#9ab5a8",
    "rgba(116,161,46": "rgba(127,158,144",
    "#0a0c0b": "#111315",
    "#0e1211": "#181b1f",
    "#0c100f": "#181b1f",
    "#0d1110": "#181b1f",
    "#101413": "#1b1f24",
    "#111514": "#181b1f",
    "#121615": "#20242a",
    "#131817": "#20242a",
    "#141a18": "#20242a",
    "#151a18": "#20242a",
    "#161a19": "#20242a",
    "#171c1a": "#24292f",
    "#1b201e": "#2b3138",
    "#232927": "#343a42",
    "#262d2b": "#343a42",
    "#2b3230": "#3a424a",
    "#2f3634": "#414953",
    "#333b38": "#454e57",
    "#39413e": "#4a535d",
    "#3c4441": "#56616c",
    "#e9ece9": "#f1f3f4",
    "#dfe6e2": "#e4e8eb",
    "#c3ccc7": "#cbd1d6",
    "#b6bfba": "#c2c8ce",
    "#a9b3ae": "#b3bbc3",
    "#9aa5a0": "#a7afb8",
    "#98a29d": "#a7afb8",
    "#8d9792": "#9fa7b2",
    "#8b948f": "#9fa7b2",
    "#79847f": "#858f9a",
    "#7d8782": "#858f9a",
    "#6f7a75": "#707985",
    "#5f6a65": "#707985",
    "#4a524f": "#66717c",
    "#07130c": "#111315"
}
for old, new in palette.items():
    text = text.replace(old, new)

once(
    "  @keyframes ringIn { from { opacity: 0; transform: scale(.92) } to { opacity: 1; transform: scale(1) } }\n",
    """  @keyframes ringIn { from { opacity: 0; transform: scale(.96) } to { opacity: 1; transform: scale(1) } }
  [data-score-edit="true"] { border-radius: 4px; transition: background .1s ease, box-shadow .1s ease; }
  [data-score-edit="true"]:hover { background: rgba(127,158,144,.12); box-shadow: 0 0 0 1px rgba(127,158,144,.34); }
""",
    "professional score edit styling"
)

# Direct editing from the score header.
once(
    """          <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 0 48px 12px;">
            <div style="flex: 0 0 auto; white-space: nowrap; font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; color: #8e8a80; letter-spacing: .12em;">FLOW 01</div>
            <div style="flex: 1 1 auto; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 2px;">
              <div style="font-size: 19px; font-weight: 600; color: #1b1a17; letter-spacing: .01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">{{ title }}</div>
              <div style="font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; color: #6b6760; letter-spacing: .08em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">{{ composer }} · {{ keyName }} · {{ meterName }}</div>
            </div>
            <div style="flex: 0 0 auto; white-space: nowrap; font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; color: #8e8a80; letter-spacing: .12em;">{{ layoutLabel }} · {{ measureRange }}</div>
          </div>
""",
    """          <div style="display: flex; align-items: baseline; justify-content: space-between; padding: 0 48px 18px;">
            <div style="flex: 0 0 auto; white-space: nowrap; font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; color: #8e8a80; letter-spacing: .08em;">Flow 01</div>
            <div style="flex: 1 1 auto; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 3px;">
              <div onClick="{{ editTitle }}" data-ptr="Edit score title" data-score-edit="true" style="{{ titleStyle }}">{{ title }}</div>
              <div style="font-family: 'Inter', sans-serif; font-size: 10px; color: #6b6760; letter-spacing: .025em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;">
                <span onClick="{{ editComposer }}" data-ptr="Edit composer" data-score-edit="true" style="cursor: pointer; padding: 1px 3px;">{{ composer }}</span>
                <span> · </span>
                <span onClick="{{ editKey }}" data-ptr="Edit key signature" data-score-edit="true" style="cursor: pointer; padding: 1px 3px;">{{ keyName }}</span>
                <span> · </span>
                <span onClick="{{ editMeter }}" data-ptr="Edit time signature" data-score-edit="true" style="cursor: pointer; padding: 1px 3px;">{{ meterName }}</span>
              </div>
            </div>
            <div style="flex: 0 0 auto; white-space: nowrap; font-family: 'IBM Plex Mono', monospace; font-size: 9.5px; color: #8e8a80; letter-spacing: .08em;">{{ layoutLabel }} · {{ measureRange }}</div>
          </div>
""",
    "score header direct editing"
)

# Score-object hit targets: clef, octave indicator, key, time and instrument label.
once(
    """                <div style="{{ s.clefStyle }}">{{ s.clef }}</div>
                <sc-for list="{{ s.keyAccs }}" as="ka" hint-placeholder-count="1">
                  <div style="{{ ka.style }}">{{ ka.glyph }}</div>
                </sc-for>
                <div style="{{ s.timeTopStyle }}">{{ s.timeTop }}</div>
                <div style="{{ s.timeBotStyle }}">{{ s.timeBot }}</div>
""",
    """                <div onClick="{{ s.openClef }}" data-ptr="{{ s.clefPtr }}" data-score-edit="true" style="{{ s.clefStyle }}">{{ s.clef }}</div>
                <div onClick="{{ s.openClefOctave }}" data-ptr="{{ s.octavePtr }}" data-score-edit="true" style="{{ s.octaveStyle }}">{{ s.octaveText }}</div>
                <div onClick="{{ s.openKey }}" data-ptr="Edit key signature" data-score-edit="true" style="{{ s.keyHitStyle }}"></div>
                <sc-for list="{{ s.keyAccs }}" as="ka" hint-placeholder-count="1">
                  <div onClick="{{ ka.onSelect }}" data-ptr="Edit key signature" data-score-edit="true" style="{{ ka.style }}">{{ ka.glyph }}</div>
                </sc-for>
                <div onClick="{{ s.openMeter }}" data-ptr="Edit time signature" data-score-edit="true" style="{{ s.timeHitStyle }}"></div>
                <div onClick="{{ s.openMeter }}" data-ptr="Edit time signature" data-score-edit="true" style="{{ s.timeTopStyle }}">{{ s.timeTop }}</div>
                <div onClick="{{ s.openMeter }}" data-ptr="Edit time signature" data-score-edit="true" style="{{ s.timeBotStyle }}">{{ s.timeBot }}</div>
""",
    "direct notation object editing"
)
once(
    """            <sc-for list="{{ staffLabels }}" as="lb" hint-placeholder-count="3">
              <div style="{{ lb.style }}">{{ lb.name }}</div>
            </sc-for>
""",
    """            <sc-for list="{{ staffLabels }}" as="lb" hint-placeholder-count="3">
              <div onClick="{{ lb.onSelect }}" data-ptr="{{ lb.ptr }}" data-score-edit="true" style="{{ lb.style }}">{{ lb.name }}</div>
            </sc-for>
""",
    "instrument label direct editing"
)

# Draw stems behind noteheads. This prevents stems from visually cutting through heads.
once(
    """                <div style="{{ n.glyphStyle }}">{{ n.glyph }}</div>
                <sc-for list="{{ n.chordHeads }}" as="ch" hint-placeholder-count="0">
                  <div style="{{ ch.style }}">{{ ch.glyph }}</div>
                </sc-for>
                <div style="{{ n.stemStyle }}"></div>
""",
    """                <div style="{{ n.stemStyle }}"></div>
                <div style="{{ n.glyphStyle }}">{{ n.glyph }}</div>
                <sc-for list="{{ n.chordHeads }}" as="ch" hint-placeholder-count="0">
                  <div style="{{ ch.style }}">{{ ch.glyph }}</div>
                </sc-for>
""",
    "stem/head render order"
)

# Persistent document state for octave clefs.
once(
    "const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks'];",
    "const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks'];",
    "document octave state"
)
once(
    "const HEAD_GLYPH = { w: '\\uE0A2', h: '\\uE0A3' };",
    "const HEAD_GLYPH = { w: '\\uE0A2', h: '\\uE0A3', q: '\\uE0A4', e: '\\uE0A4', s: '\\uE0A4', t: '\\uE0A4' };",
    "complete notehead map"
)
once("  let y = 8, gi = -1, lastGroup = null;", "  let y = 112, gi = -1, lastGroup = null;", "title-safe system top")
once(
    "    clefs: DEFAULT_PLAYERS.map(p => p.clef),\n    instruments: DEFAULT_PLAYERS.map(p => p.instrument),",
    "    clefs: DEFAULT_PLAYERS.map(p => p.clef),\n    clefOctaves: DEFAULT_PLAYERS.map(() => 0),\n    instruments: DEFAULT_PLAYERS.map(p => p.instrument),",
    "initial octave clef state"
)
once(
    "      notes: [], selId: null, title: 'Untitled score', composer: '', keyIdx: 0, meter: 0, tempo: 100,",
    "      notes: [], selId: null, title: 'Untitled score', composer: '', keyIdx: 0, meter: 0, tempo: 100,\n      clefOctaves: (this.state.players || DEFAULT_PLAYERS).map(() => 0),",
    "new project octave reset"
)
once(
    "        clefs: s.clefs.concat([clef || 'treble']),\n        instruments: s.instruments.concat([instrument || 'acoustic_grand_piano']),",
    "        clefs: s.clefs.concat([clef || 'treble']),\n        clefOctaves: (s.clefOctaves || s.clefs.map(() => 0)).concat([0]),\n        instruments: s.instruments.concat([instrument || 'acoustic_grand_piano']),",
    "add player octave state"
)
once(
    "        clefs: s.clefs.filter((c, j) => j !== i),\n        instruments: s.instruments.filter((c, j) => j !== i),",
    "        clefs: s.clefs.filter((c, j) => j !== i),\n        clefOctaves: (s.clefOctaves || s.clefs.map(() => 0)).filter((c, j) => j !== i),\n        instruments: s.instruments.filter((c, j) => j !== i),",
    "remove player octave state"
)
once(
    "        clefs: s.clefs.slice(0, i + 1).concat(['bass'], s.clefs.slice(i + 1)),\n        instruments: s.instruments.slice(0, i + 1).concat([s.instruments[i]], s.instruments.slice(i + 1)),",
    "        clefs: s.clefs.slice(0, i + 1).concat(['bass'], s.clefs.slice(i + 1)),\n        clefOctaves: (s.clefOctaves || s.clefs.map(() => 0)).slice(0, i + 1).concat([0], (s.clefOctaves || s.clefs.map(() => 0)).slice(i + 1)),\n        instruments: s.instruments.slice(0, i + 1).concat([s.instruments[i]], s.instruments.slice(i + 1)),",
    "grand staff octave state"
)

# Octave-clef playback and export.
once(
    """function midiFor(step, bass, acc, key) {
  const oct = Math.floor(step / 7), i = ((step % 7) + 7) % 7;
  const base = bass ? 43 : 64, tab = bass ? BASS_SEMI : TREBLE_SEMI;
  let m = base + 12 * oct + tab[i];
  if (acc === '\\uE262') m += 1;
  else if (acc === '\\uE260') m -= 1;
  else if (acc === '\\uE263') m += 2;
  else if (acc === '\\uE264') m -= 2;
  else if (acc === '\\uE261') return m;            // explicit natural cancels the key
  else m += keyAlter(step, bass, key);
  return m;
}
""",
    """function midiFor(step, bass, acc, key, clefOctave) {
  const oct = Math.floor(step / 7), i = ((step % 7) + 7) % 7;
  const base = bass ? 43 : 64, tab = bass ? BASS_SEMI : TREBLE_SEMI;
  let m = base + 12 * oct + tab[i];
  if (acc === '\\uE262') m += 1;
  else if (acc === '\\uE260') m -= 1;
  else if (acc === '\\uE263') m += 2;
  else if (acc === '\\uE264') m -= 2;
  else if (acc !== '\\uE261') m += keyAlter(step, bass, key);
  return m + (Number(clefOctave) || 0) * 12;
}
""",
    "octave-aware MIDI"
)
midi_replacements = {
    "midiFor(sel.step, s.clefs[sel.s] === 'bass', sel.acc, KEYS[s.keyIdx])":
        "midiFor(sel.step, s.clefs[sel.s] === 'bass', sel.acc, KEYS[s.keyIdx], (s.clefOctaves || [])[sel.s])",
    "midiFor(sel.step, this.state.clefs[sel.s] === 'bass', sel.acc, KEYS[this.state.keyIdx])":
        "midiFor(sel.step, this.state.clefs[sel.s] === 'bass', sel.acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[sel.s])",
    "midiFor(n.step, s.clefs[n.s] === 'bass', n.acc, KEYS[s.keyIdx])":
        "midiFor(n.step, s.clefs[n.s] === 'bass', n.acc, KEYS[s.keyIdx], (s.clefOctaves || [])[n.s])",
    "midiFor(step, this.state.clefs[staff] === 'bass', acc, KEYS[this.state.keyIdx])":
        "midiFor(step, this.state.clefs[staff] === 'bass', acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[staff])",
    "midiFor(n.step, bass, n.acc)":
        "midiFor(n.step, bass, n.acc, KEYS[s.keyIdx], (s.clefOctaves || [])[n.s])",
    "midiFor(n.step, s.clefs[i] === 'bass', n.acc, KEYS[s.keyIdx])":
        "midiFor(n.step, s.clefs[i] === 'bass', n.acc, KEYS[s.keyIdx], (s.clefOctaves || [])[i])"
}
for old, new in midi_replacements.items():
    if old not in text:
        raise SystemExit(f"missing MIDI call: {old}")
    text = text.replace(old, new)

once(
    """            + '<time><beats>' + met[0] + '</beats><beat-type>' + met[1] + '</beat-type></time>'
            + '<clef><sign>' + (s.clefs[i] === 'bass' ? 'F' : s.clefs[i] === 'percussion' ? 'percussion' : 'G') + '</sign><line>' + (s.clefs[i] === 'bass' ? 4 : 2) + '</line></clef></attributes>\\n';
""",
    """            + '<time><beats>' + met[0] + '</beats><beat-type>' + met[1] + '</beat-type></time>'
            + '<clef><sign>' + (s.clefs[i] === 'bass' ? 'F' : s.clefs[i] === 'percussion' ? 'percussion' : 'G') + '</sign><line>' + (s.clefs[i] === 'bass' ? 4 : 2) + '</line>'
            + (((s.clefOctaves || [])[i] || 0) ? '<clef-octave-change>' + ((s.clefOctaves || [])[i] || 0) + '</clef-octave-change>' : '')
            + '</clef></attributes>\\n';
""",
    "MusicXML octave clef"
)

# Direct score editor helpers and octave-clef controls.
once(
    """  cycleMeter(d) {
    this.setState(s => {
      const i = (s.meter + d + METERS.length) % METERS.length;
      return { meter: i, spoken: METERS[i] + ' time signature' };
    });
  }
""",
    """  cycleMeter(d) {
    this.setState(s => {
      const i = (s.meter + d + METERS.length) % METERS.length;
      return { meter: i, spoken: METERS[i] + ' time signature' };
    });
  }
  setClefOctave(value) {
    this.setState(s => {
      const octaves = (s.clefOctaves || s.clefs.map(() => 0)).slice();
      octaves[s.staff] = value;
      const label = value === 0 ? 'normal pitch' : (Math.abs(value) === 1 ? '8' : '15') + (value > 0 ? ' above' : ' below');
      return { clefOctaves: octaves, panel: null, spoken: 'Clef octave set to ' + label + ' for ' + STAVES[s.staff].name };
    });
  }
  openScoreEditor(kind, staff) {
    const i = Math.max(0, Math.min(this.state.players.length - 1, staff == null ? this.state.staff : staff));
    this.rumble('tick');
    if (kind === 'instrument') return this.setState({ staff: i }, () => this.openPicker());
    if (kind === 'title' || kind === 'composer') return this.setState({ staff: i }, () => this.openKeyboard(kind));
    this.setState({ staff: i, panel: kind, panelIdx: 0, hub: false, halo: false, menu: false, spoken: 'Edit ' + kind + ' for ' + STAVES[i].name });
  }
""",
    "direct editor methods"
)
once(
    """    if (s.panel === 'key') return KEYS.map((k, i) => ({ label: k.name, value: i === s.keyIdx ? 'IN USE' : '', act: () => this.setState({ keyIdx: i, spoken: k.name + ' set' }) }));
""",
    """    if (s.panel === 'clef') {
      const currentOctave = (s.clefOctaves || [])[s.staff] || 0;
      return CLEFS.map((c, i) => ({ label: c.name + ' clef', value: s.clefs[s.staff] === c.id ? 'IN USE' : '', act: () => this.setClef(c.id) })).concat([
        { label: 'Normal clef pitch', value: currentOctave === 0 ? 'IN USE' : '', act: () => this.setClefOctave(0) },
        { label: '8 above the clef', value: currentOctave === 1 ? 'IN USE' : '', act: () => this.setClefOctave(1) },
        { label: '8 below the clef', value: currentOctave === -1 ? 'IN USE' : '', act: () => this.setClefOctave(-1) },
        { label: '15 above the clef', value: currentOctave === 2 ? 'IN USE' : '', act: () => this.setClefOctave(2) },
        { label: '15 below the clef', value: currentOctave === -2 ? 'IN USE' : '', act: () => this.setClefOctave(-2) }
      ]);
    }
    if (s.panel === 'key') return KEYS.map((k, i) => ({ label: k.name, value: i === s.keyIdx ? 'IN USE' : '', act: () => this.setState({ keyIdx: i, panel: null, spoken: k.name + ' set' }) }));
""",
    "clef contextual editor"
)
text = text.replace(
    "if (s.panel === 'meter') return METERS.map((m, i) => ({ label: m, value: i === s.meter ? 'IN USE' : '', act: () => this.setState({ meter: i, spoken: m + ' set' }) }));",
    "if (s.panel === 'meter') return METERS.map((m, i) => ({ label: m, value: i === s.meter ? 'IN USE' : '', act: () => this.setState({ meter: i, panel: null, spoken: m + ' set' }) }));"
)

# Manual beam, stem and cross-staff commands now have real state.
once(
    """      else if (/Stem up/.test(name)) { this.editNote({ stem: 'up' }, 'Stem up'); msg = 'Stem up'; }
      else if (/Stem down/.test(name)) { this.editNote({ stem: 'down' }, 'Stem down'); msg = 'Stem down'; }
""",
    """      else if (/Beam together/.test(name)) { this.editNote({ beam: 'join' }, 'Beam joins across the next normal boundary'); msg = 'Beam together'; }
      else if (/Break beam/.test(name)) { this.editNote({ beam: 'break' }, 'Beam breaks before this note'); msg = 'Beam break'; }
      else if (/Stem up/.test(name)) { this.editNote({ stem: 'up' }, 'Stem up'); msg = 'Stem up'; }
      else if (/Stem down/.test(name)) { this.editNote({ stem: 'down' }, 'Stem down'); msg = 'Stem down'; }
      else if (/Automatic stem/.test(name)) { this.editNote({ stem: null }, 'Automatic stem'); msg = 'Automatic stem'; }
      else if (/Cross-staff note/.test(name)) {
        const current = this.selected();
        if (current) {
          const next = current.crossStaff ? 0 : (current.s < s.players.length - 1 ? 1 : -1);
          this.editNote({ crossStaff: next }, next ? 'Note moved across the staff with its beam relationship kept' : 'Note returned to its own staff');
          msg = next ? 'Cross-staff note' : 'Cross-staff cleared';
        }
      }
""",
    "rhythm command implementation"
)
once(
    "      else if (/Septuplet/.test(name)) { this.toggleTuplet(7); msg = 'Septuplet applied'; }",
    "      else if (/Septuplet/.test(name)) { this.toggleTuplet(7); msg = 'Septuplet applied'; }\n      else if (/Nonuplet/.test(name)) { this.toggleTuplet(9); msg = 'Nonuplet applied'; }",
    "nonuplet implementation"
)

# Density-aware horizontal spacing, signature clearance and title-safe layout.
once(
    """    const accent = this.props.accentColor || '#7f9e90';
    const XS = XSTEP * (s.spacing / 100);
    const systemBottom = STAVES[STAVES.length - 1].top + 48;
    const noteX = p => X0 + p * XS;
""",
    """    const accent = this.props.accentColor || '#7f9e90';
    const shortest = Math.min.apply(null, s.notes.filter(n => !n.rest).map(noteBeats).concat([1]));
    const densityScale = shortest <= .126 ? 2.55 : (shortest <= .251 ? 1.7 : (shortest <= .501 ? 1.14 : 1));
    const chordLoad = Math.max.apply(null, s.notes.map(n => 1 + (n.chord || []).length).concat([1]));
    const chordScale = chordLoad >= 8 ? 1.34 : (chordLoad >= 5 ? 1.2 : 1);
    const XS = XSTEP * (s.spacing / 100) * Math.max(densityScale, chordScale);
    const signatureExtra = (KEYS[s.keyIdx].n || 0) * 12;
    const noteStart = X0 + signatureExtra + 24;
    const systemBottom = STAVES[STAVES.length - 1].top + 48;
    const noteX = p => noteStart + p * XS;
""",
    "density-aware spacing"
)
text = text.replace(
    "Math.max(1120, Math.round(X0 + s.bars * this.barCapacity() * XS + 150))",
    "Math.max(1120, Math.round(noteStart + s.bars * this.barCapacity() * XS + 150))"
)
text = text.replace(
    "min-width: ' + Math.round(s.bars * this.barCapacity() * XS + 60) + 'px;",
    "min-width: ' + Math.round(noteStart + s.bars * this.barCapacity() * XS + 60) + 'px;"
)

# Correctly spaced and centered clef/key/time geometry plus direct actions.
regex_once(
    r"""      staves: STAVES\.map\(\(st, i\) => \{\n.*?\n      \}\),\n      measureRange:""",
    """      staves: STAVES.map((st, i) => {
        const cl = CLEFS.find(c => c.id === s.clefs[i]) || CLEFS[0];
        const K = KEYS[s.keyIdx], shift = cl.id === 'bass' ? -2 : (cl.id === 'tenor' ? -1 : 0);
        const steps = K.type === 'flat' ? FLAT_STEPS : SHARP_STEPS;
        const met = METERS[s.meter].split('/');
        const octave = (s.clefOctaves || [])[i] || 0;
        const keyX = 52, timeX = 70 + (K.n || 0) * 12;
        const octaveName = octave === 0 ? 'normal' : (Math.abs(octave) === 1 ? '8' : '15') + (octave > 0 ? ' above' : ' below');
        return {
          label: st.label, clef: cl.glyph,
          keyAccs: (K.type ? steps.slice(0, K.n) : []).map((st2, j) => ({
            glyph: K.type === 'flat' ? SM.flat : SM.sharp,
            onSelect: () => this.openScoreEditor('key', i),
            style: glyphAt(keyX + j * 12, 48 - (st2 + shift) * 6, 48) + 'cursor:pointer;z-index:5;'
          })),
          timeTop: String.fromCharCode(0xE080 + Number(met[0]) % 10),
          timeBot: String.fromCharCode(0xE080 + Number(met[1]) % 10),
          timeTopStyle: glyphAt(timeX, 20, 48) + 'cursor:pointer;z-index:5;',
          timeBotStyle: glyphAt(timeX, 44, 48) + 'cursor:pointer;z-index:5;',
          timeHitStyle: 'position:absolute;left:' + (timeX - 3) + 'px;top:-6px;width:31px;height:60px;cursor:pointer;z-index:4;',
          keyHitStyle: 'position:absolute;left:' + (keyX - 4) + 'px;top:-6px;width:' + Math.max(18, (K.n || 0) * 12 + 8) + 'px;height:60px;cursor:pointer;z-index:4;',
          octaveText: octave ? (Math.abs(octave) === 1 ? '8' : '15') : '',
          octaveStyle: octave
            ? 'position:absolute;left:24px;top:' + (octave > 0 ? '-17px' : '40px') + ';min-width:18px;text-align:center;font-family:\'Inter\',sans-serif;font-size:11px;font-weight:700;line-height:1;color:#1b1a17;cursor:pointer;z-index:7;padding:2px;'
            : 'display:none;',
          octavePtr: 'Edit octave clef — ' + octaveName,
          clefPtr: 'Edit ' + cl.name + ' clef',
          openClef: () => this.openScoreEditor('clef', i),
          openClefOctave: () => this.openScoreEditor('clef', i),
          openKey: () => this.openScoreEditor('key', i),
          openMeter: () => this.openScoreEditor('meter', i),
          wrapStyle: 'position:absolute;left:0;right:0;top:' + st.top + 'px;height:48px;',
          clefStyle: glyphAt(8, cl.line, cl.size) + 'cursor:pointer;z-index:6;'
        };
      }),
      measureRange:""",
    "signature geometry",
    flags=re.S
)

# Header actions and professional title typography.
once(
    """      title: s.title,
      composer: s.composer,
      keyName: KEYS[s.keyIdx].name,
      meterName: METERS[s.meter],
""",
    """      title: s.title,
      titleStyle: 'font-family:\'Source Serif 4\',Georgia,serif;font-size:22px;font-weight:600;color:#1b1a17;letter-spacing:.005em;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;cursor:pointer;padding:2px 8px;',
      composer: s.composer,
      keyName: KEYS[s.keyIdx].name,
      meterName: METERS[s.meter],
      editTitle: () => this.openScoreEditor('title', s.staff),
      editComposer: () => this.openScoreEditor('composer', s.staff),
      editKey: () => this.openScoreEditor('key', s.staff),
      editMeter: () => this.openScoreEditor('meter', s.staff),
""",
    "header actions"
)

# Staff/instrument labels are direct instrument editors.
regex_once(
    r"""      staffLabels: GROUPS\.map\(grp => \{\n.*?\n      \}\),\n      systemBracket:""",
    """      staffLabels: GROUPS.map(grp => {
        const first = STAVES[grp[0]], last = STAVES[grp[grp.length - 1]];
        const mid = (first.top + last.top + 48) / 2;
        const name = grp.length > 1 ? 'Piano' : first.name;
        const staffIndex = grp[0];
        return {
          name: name,
          ptr: 'Edit instrument for ' + name,
          onSelect: () => this.openScoreEditor('instrument', staffIndex),
          style: 'position:absolute;left:-108px;top:' + (mid - 8) + 'px;width:64px;text-align:right;'
            + 'font-family:\'Inter\',sans-serif;font-size:13px;color:#3d3a34;letter-spacing:.005em;line-height:1.1;cursor:pointer;padding:2px 3px;'
        };
      }),
      systemBracket:""",
    "direct instrument labels",
    flags=re.S
)

# Ledger lines are deduplicated across chord members and follow cross-staff display.
regex_once(
    r"""      ledgers: \(\(\) => \{\n.*?\n      \}\)\(\),\n      staffLabels:""",
    """      ledgers: (() => {
        const out = [], seen = {};
        s.notes.forEach(n => {
          if (n.rest) return;
          const target = Math.max(0, Math.min(STAVES.length - 1, n.s + (n.crossStaff || 0)));
          const host = this._vis && this._vis.map ? this._vis.map[target] : target;
          const st = STAVES[host] || STAVES[target] || STAVES[n.s];
          if (!st || st.hidden) return;
          const steps = [n.step].concat((n.chord || []).map(o => n.step + o));
          steps.forEach(sp => {
            for (let k = 10; k <= sp; k += 2) {
              const key = host + ':' + n.p.toFixed(4) + ':a' + k;
              if (!seen[key]) { seen[key] = 1; out.push({ x: noteX(n.p), y: st.top + 48 - k * 6 }); }
            }
            for (let k = -2; k >= sp; k -= 2) {
              const key = host + ':' + n.p.toFixed(4) + ':b' + k;
              if (!seen[key]) { seen[key] = 1; out.push({ x: noteX(n.p), y: st.top + 48 - k * 6 }); }
            }
          });
        });
        const ext = (s.eng && s.eng.ledgerExt) || 12;
        return out.map(l => ({ style: 'position:absolute;left:' + (l.x - ext) + 'px;top:' + l.y + 'px;width:' + (ext * 2) + 'px;height:1.6px;background:#26241f;z-index:1;' }));
      })(),
      staffLabels:""",
    "ledger deduplication",
    flags=re.S
)

# Tuplets must not read stale beam information from the previous render.
text = text.replace(
    """            const bm = this._beams ? null : null;
            const infos = run.map(r => (this._beamInfo || {})[r.i]);
            const beamed = infos.length > 1 && infos.every(Boolean);
""",
    """            const beamed = run.length > 1 && run.every(r => /^(e|s|t)$/.test(r.n.d));
"""
)

# Replace the entire beam/chord/stem pipeline atomically so all geometry shares one source of truth.
new_notes_block = r"""      notes: (() => {
        const FLAG = { e: 1, s: 2, t: 3 }, beamInfo = {}, beams = [];
        const meterName = METERS[s.meter];
        const met = meterName.split('/');
        const capBar = Number(met[0]) * (4 / Number(met[1]));
        const beamPattern = {
          '4/4': [1, 1, 1, 1],
          '3/4': [1, 1, 1],
          '2/2': [2, 2],
          '6/8': [1.5, 1.5],
          '5/4': [3, 2],
          '12/8': [1.5, 1.5, 1.5, 1.5],
          '7/8': [1, 1, 1.5]
        }[meterName] || [1];
        const groupId = p => {
          const bar = Math.floor((p + .0005) / capBar);
          const local = p - bar * capBar;
          let edge = 0;
          for (let i = 0; i < beamPattern.length; i++) {
            edge += beamPattern[i];
            if (local < edge - .0005) return bar + ':' + i;
          }
          return bar + ':' + (beamPattern.length - 1);
        };
        const displayStaff = n => {
          const target = Math.max(0, Math.min(STAVES.length - 1, n.s + (n.crossStaff || 0)));
          return this._vis && this._vis.map ? this._vis.map[target] : target;
        };
        const layoutHeads = (steps, up) => {
          const left = {};
          let run = 0;
          steps.forEach((step, i) => {
            run = i && step - steps[i - 1] <= 1 ? run + 1 : 0;
            const displaced = run % 2 === 1;
            left[step] = -7 + (displaced ? (up ? -7 : 7) : 0);
          });
          const stemX = up
            ? Math.max.apply(null, steps.map(step => left[step] + 12))
            : Math.min.apply(null, steps.map(step => left[step]));
          return { left: left, stemX: stemX };
        };

        // Simultaneous notes in one staff/voice/onset are one chord engraving unit.
        const chordOf = {};
        s.notes.forEach((n, i) => {
          if (n.rest) return;
          const key = n.s + ':' + (n.voice || 1) + ':' + n.p.toFixed(4);
          (chordOf[key] = chordOf[key] || []).push({ n: n, i: i });
        });
        const chordKey = n => n.s + ':' + (n.voice || 1) + ':' + n.p.toFixed(4);
        const chordInfo = {};
        Object.keys(chordOf).forEach(key => {
          const members = chordOf[key];
          const all = [];
          members.forEach(m => {
            all.push(m.n.step);
            (m.n.chord || []).forEach(o => all.push(m.n.step + o));
          });
          const steps = Array.from(new Set(all)).sort((a, b) => a - b);
          const avg = steps.reduce((a, b) => a + b, 0) / steps.length;
          const voice = members[0].n.voice || 1;
          const forced = members.find(m => m.n.stem);
          const up = forced ? forced.n.stem === 'up' : (voice === 2 || voice === 4 ? false : avg < 8);
          let owner = members[0];
          members.forEach(m => {
            if (up ? m.n.step < owner.n.step : m.n.step > owner.n.step) owner = m;
          });
          const upLayout = layoutHeads(steps, true), downLayout = layoutHeads(steps, false);
          chordInfo[key] = {
            up: up, low: steps[0], high: steps[steps.length - 1],
            ownerIdx: owner.i, steps: steps,
            headLeftUp: upLayout.left, headLeftDown: downLayout.left,
            stemXUp: upLayout.stemX, stemXDown: downLayout.stemX
          };
        });

        // Build one ordered rhythmic stream per original staff and voice.
        const byStaff = {};
        Object.keys(chordOf).forEach(key => {
          const members = chordOf[key], ci = chordInfo[key];
          const lead = members.find(m => m.i === ci.ownerIdx) || members[0];
          const stream = lead.n.s + ':' + (lead.n.voice || 1);
          (byStaff[stream] = byStaff[stream] || []).push({ n: lead.n, i: lead.i, key: key });
        });
        s.notes.forEach((n, i) => {
          if (!n.rest) return;
          const stream = n.s + ':' + (n.voice || 1);
          (byStaff[stream] = byStaff[stream] || []).push({ n: n, i: i, rest: true });
        });
        Object.keys(byStaff).forEach(k => byStaff[k].sort((a, b) => a.n.p - b.n.p));

        Object.keys(byStaff).forEach(k => {
          const list = byStaff[k], group = [];
          const flush = () => {
            if (group.length > 1) {
              const voice = group[0].n.voice || 1;
              const defaultUp = group[0].key && chordInfo[group[0].key] ? chordInfo[group[0].key].up
                : (voice === 2 || voice === 4 ? false : group.reduce((a, g) => a + g.n.step, 0) / group.length < 8);
              const staffIds = group.map(g => displayStaff(g.n));
              const spansStaff = new Set(staffIds).size > 1;
              let beamGuide = null;
              if (spansStaff) {
                const centers = staffIds.map(si => (STAVES[si] || STAVES[group[0].n.s]).top + 24);
                beamGuide = (Math.min.apply(null, centers) + Math.max.apply(null, centers)) / 2;
              }
              const directions = group.map((g, i) => spansStaff
                ? ((STAVES[staffIds[i]] || STAVES[g.n.s]).top + 24 > beamGuide)
                : defaultUp);
              const xs = group.map((g, i) => {
                const ci = g.key ? chordInfo[g.key] : null;
                const stemX = ci ? (directions[i] ? ci.stemXUp : ci.stemXDown) : (directions[i] ? 5.7 : -7);
                return noteX(g.n.p) + stemX;
              });
              const ys = group.map((g, i) => {
                const ci = g.key ? chordInfo[g.key] : null;
                const step = ci ? (directions[i] ? ci.high : ci.low) : g.n.step;
                const st = STAVES[staffIds[i]] || STAVES[g.n.s];
                return st.top + 48 - step * 6;
              });
              const EG = s.eng || {}, SPACE = 12;
              const IDEAL = EG.stemLen || 42, MIN = 2.5 * SPACE;
              let y1, y2;
              if (spansStaff) {
                y1 = beamGuide;
                y2 = beamGuide;
              } else {
                const dir = defaultUp ? -1 : 1;
                const outer = (ys[ys.length - 1] - ys[0]) / 6;
                const mag = Math.abs(outer);
                const quant = mag === 0 ? 0 : (mag <= 1 ? .25 : mag <= 2 ? .5 : mag <= 4 ? 1 : mag <= 7 ? 1.5 : 2);
                const slant = Math.sign(outer) * quant * SPACE;
                const extremeIdx = ys.reduce((best, y, i) => (defaultUp ? y < ys[best] : y > ys[best]) ? i : best, 0);
                const spanX = (xs[xs.length - 1] - xs[0]) || 1;
                const tAt = i => (xs[i] - xs[0]) / spanX;
                y1 = ys[extremeIdx] + dir * IDEAL - slant * tAt(extremeIdx);
                y2 = y1 + slant;
                group.forEach((g, i) => {
                  const beamAt = y1 + (y2 - y1) * tAt(i);
                  const len = defaultUp ? ys[i] - beamAt : beamAt - ys[i];
                  if (len < MIN) {
                    const push = dir * (MIN - len);
                    y1 += push;
                    y2 += push;
                  }
                });
              }
              const beamSlant = y2 - y1;
              const span = (xs[xs.length - 1] - xs[0]) || 1;
              const at = x => y1 + beamSlant * ((x - xs[0]) / span);
              const thick = EG.beamThick || 5.5, gap = thick + 3.5;
              const beamDir = defaultUp ? -1 : 1;
              const maxLv = Math.max.apply(null, group.map(g => FLAG[g.n.d] || 1));
              const bar = (lo, hi, lv) => {
                const xa = xs[lo], xb = xs[hi];
                const ya = at(xa) - beamDir * lv * gap, yb = at(xb) - beamDir * lv * gap;
                const len = Math.hypot(xb - xa, yb - ya);
                const ang = Math.atan2(yb - ya, xb - xa) * 180 / Math.PI;
                beams.push({ style: 'position:absolute;left:' + (xa - .8) + 'px;top:' + (ya - (defaultUp ? 0 : thick)) + 'px;width:' + (len + 1.6) + 'px;height:' + thick + 'px;background:#1b1a17;transform:rotate(' + ang.toFixed(2) + 'deg);transform-origin:0 ' + (defaultUp ? '0' : '100%') + ';z-index:2;' });
              };
              const hook = (i, lv, forward) => {
                const xa = xs[i], width = Math.min(14, Math.max(9, XS * .22));
                const ya = at(xa) - beamDir * lv * gap;
                const xb = forward ? xa + width : xa - width;
                const yb = at(xb) - beamDir * lv * gap;
                const len = Math.hypot(xb - xa, yb - ya);
                const ang = Math.atan2(yb - ya, xb - xa) * 180 / Math.PI;
                beams.push({ style: 'position:absolute;left:' + (xa - .8) + 'px;top:' + (ya - (defaultUp ? 0 : thick)) + 'px;width:' + (len + 1) + 'px;height:' + thick + 'px;background:#1b1a17;transform:rotate(' + ang.toFixed(2) + 'deg);transform-origin:0 ' + (defaultUp ? '0' : '100%') + ';z-index:2;' });
              };
              bar(0, group.length - 1, 0);
              for (let lv = 1; lv < maxLv; lv++) {
                const has = group.map(g => (FLAG[g.n.d] || 1) > lv);
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
                }
              }
              group.forEach((g, i) => {
                const up = directions[i], ci = g.key ? chordInfo[g.key] : null;
                const stemX = ci ? (up ? ci.stemXUp : ci.stemXDown) : (up ? 5.7 : -7);
                const edge = at(xs[i]) + (up ? thick : -thick);
                beamInfo[g.i] = { up: up, beamY: edge, stemX: stemX };
                if (g.key) (chordOf[g.key] || []).forEach(m => { beamInfo[m.i] = { up: up, beamY: edge, stemX: stemX }; });
              });
            }
            group.length = 0;
          };
          list.forEach(item => {
            if (item.n.rest || !FLAG[item.n.d]) { flush(); return; }
            if (group.length) {
              const prev = group[group.length - 1].n;
              const contiguous = Math.abs(prev.p + noteBeats(prev) - item.n.p) < .002;
              const sameBar = Math.floor((prev.p + .0005) / capBar) === Math.floor((item.n.p + .0005) / capBar);
              const manualJoin = prev.beam === 'join' || item.n.beam === 'join';
              const manualBreak = item.n.beam === 'break' || prev.beam === 'break';
              const sameMetricGroup = groupId(prev.p) === groupId(item.n.p);
              if (!contiguous || !sameBar || manualBreak || (!manualJoin && !sameMetricGroup)) flush();
            }
            group.push(item);
          });
          flush();
        });

        this._beams = beams;
        this._beamInfo = beamInfo;
        return s.notes.map((n, i) => {
          const target = Math.max(0, Math.min(STAVES.length - 1, n.s + (n.crossStaff || 0)));
          const rsi = this._vis && this._vis.map ? this._vis.map[target] : target;
          const st = STAVES[rsi] || STAVES[target] || STAVES[n.s];
          const top = st.top + 48 - n.step * 6, bi = beamInfo[i];
          if (st.hidden) return { wrapStyle: 'display:none;', glyphStyle: 'display:none;', chordHeads: [], marks: [], glyph: '', flag: '', flagStyle: 'display:none;', stemStyle: 'display:none;', dotStyle: 'display:none;', dotGlyph: '', tupStyle: 'display:none;', tup: '', tieStyle: 'display:none;', selStyle: 'display:none;', acc: '', accStyle: 'display:none;', art: '', artStyle: 'display:none;', orn: '', ornStyle: 'display:none;', dyn: '', dynStyle: 'display:none;', hitStyle: 'display:none;', ptr: '', onSelect: () => {} };
          const ck = n.rest ? null : chordKey(n), ci = ck ? chordInfo[ck] : null;
          const ownsStem = !ci || ci.ownerIdx === i;
          const up = bi ? bi.up : (n.stem ? n.stem === 'up' : (ci ? ci.up : (n.voice === 2 || n.voice === 4 ? false : n.step < 8)));
          const sourceHeads = ci ? ci.steps : [n.step].concat((n.chord || []).map(o => n.step + o)).sort((a, b) => a - b);
          const isChord = sourceHeads.length > 1;
          const stemless = !!bi || isChord;
          const headGlyph = HEAD_GLYPH[n.d] || '\uE0A4';
          const headColor = n.id && n.id === s.selId ? '#54786a' : (n.voice === 2 ? '#3b3a52' : n.voice === 3 ? '#4b3a2a' : '#1b1a17');
          const layout = ci
            ? { left: up ? ci.headLeftUp : ci.headLeftDown, stemX: up ? ci.stemXUp : ci.stemXDown }
            : layoutHeads(sourceHeads, up);
          const lowStep = ci ? ci.low : sourceHeads[0], highStep = ci ? ci.high : sourceHeads[sourceHeads.length - 1];
          const lowY = st.top + 48 - lowStep * 6, highY = st.top + 48 - highStep * 6;
          const stemX = bi && bi.stemX != null ? bi.stemX : layout.stemX;
          const stemEnd = bi ? bi.beamY : (up ? highY - ((s.eng && s.eng.stemLen) || 42) : lowY + ((s.eng && s.eng.stemLen) || 42));
          const stemFrom = up ? lowY : highY;
          const hasStem = n.d !== 'w' && !n.rest && ownsStem && stemless;
          const flagGlyph = (!bi && ownsStem && stemless && FLAG_GLYPH[n.d]) ? FLAG_GLYPH[n.d][up ? 0 : 1] : '';
          const renderHeads = !ci || ownsStem;
          const anchor = n.step;
          const nextTie = n.tie ? s.notes.filter(m => m.s === n.s && m.p > n.p).sort((a, b) => a.p - b.p)[0] : null;
          return {
            wrapStyle: 'position:absolute;left:' + noteX(n.p) + 'px;top:' + top + 'px;width:0;height:0;',
            onSelect: () => this.selectNote(n),
            hitStyle: 'position:absolute;left:-15px;top:-17px;width:30px;height:34px;cursor:pointer;z-index:8;',
            ptr: (n.rest ? 'Rest' : this.pitchName(n.step, n.s)) + ' at bar ' + (Math.floor(n.p / capBar) + 1),
            glyph: n.rest ? (REST_GLYPHS[n.d] || REST_GLYPHS.q) : (!renderHeads ? '' : (stemless ? headGlyph : NOTE_GLYPHS[n.d][up ? 0 : 1])),
            glyphStyle: n.rest
              ? glyphAt(-7, st.top + 24 - top, n.cue ? 34 : 48, n.id && n.id === s.selId ? '#54786a' : '#1b1a17') + 'z-index:3;'
              : (!renderHeads ? 'display:none;' : glyphAt(stemless ? layout.left[anchor] : -7, 0, n.cue ? 34 : 48, headColor) + 'z-index:3;'),
            cueLabel: n.cue && n.cueFrom ? n.cueFrom : '',
            cueLabelStyle: n.cue && n.cueFrom
              ? 'position:absolute;left:-6px;top:' + (up ? -46 : 34) + 'px;font-family:\'Inter\',sans-serif;font-size:11px;font-style:italic;color:#5c5850;white-space:nowrap;'
              : 'display:none;',
            chordHeads: renderHeads && stemless ? sourceHeads.filter(step => step !== anchor).map(step => ({
              style: glyphAt(layout.left[step], -(step - anchor) * 6, 48, headColor) + 'z-index:3;',
              glyph: headGlyph
            })) : [],
            flag: flagGlyph,
            flagStyle: flagGlyph ? glyphAt(stemX, stemEnd - top, 48, headColor) + 'z-index:2;' : 'display:none;',
            dotStyle: n.dots ? glyphAt(12, n.step % 2 === 0 ? -6 : 0, 48) + 'z-index:4;' : 'display:none;',
            dotGlyph: n.dots ? '\uE1E7' : '',
            tupStyle: 'display:none;',
            tup: '',
            marks: (n.marks || []).map((mk, mi) => ({
              g: mk.g,
              style: mk.text
                ? 'position:absolute;left:-6px;top:' + (mk.place === 'below' ? 40 + mi * 13 : -34 - mi * 13) + 'px;font-family:\'Inter\',sans-serif;font-size:12px;font-style:italic;color:#1b1a17;white-space:nowrap;'
                : glyphAt(-7, mk.place === 'below' ? 52 + mi * 15 : -40 - mi * 15, 40)
            })),
            tieStyle: nextTie ? 'position:absolute;left:4px;top:' + (up ? 8 : -14) + 'px;width:' + Math.max(14, (nextTie.p - n.p) * XS - 12) + 'px;height:11px;border:2px solid #1b1a17;border-color:' + (up ? 'transparent transparent #1b1a17 transparent' : '#1b1a17 transparent transparent transparent') + ';border-radius:' + (up ? '0 0 50% 50%' : '50% 50% 0 0') + ';' : 'display:none;',
            selStyle: n.id && n.id === s.selId ? 'position:absolute;left:-14px;top:-12px;width:28px;height:24px;border-radius:12px;background:rgba(127,158,144,.24);border:1px solid #54786a;z-index:1;' : 'display:none;',
            stemStyle: hasStem
              ? 'position:absolute;left:' + stemX + 'px;top:' + (Math.min(stemEnd, stemFrom) - top) + 'px;width:1.6px;height:' + Math.max(1.6, Math.abs(stemEnd - stemFrom)) + 'px;background:' + headColor + ';z-index:2;'
              : 'display:none;',
            acc: n.acc || '',
            accStyle: n.acc ? glyphAt(-28, 0, 48) + 'z-index:4;' : 'display:none;',
            art: n.art || '',
            artStyle: n.art ? glyphAt(-7, up ? 22 : -20, 40) : 'display:none;',
            orn: n.orn || '',
            ornStyle: n.orn ? glyphAt(-8, -30, 40) : 'display:none;',
            dyn: n.dyn || '',
            dynStyle: n.dyn ? glyphAt(-10, (st.top + 82) - top, 40) : 'display:none;'
          };
        });
      })(),
"""
regex_once(
    r"""      notes: \(\(\) => \{\n.*?\n      \}\)\(\),\n      beams:""",
    new_notes_block + "      beams:",
    "atomic beam/stem/chord pipeline",
    flags=re.S
)

# Ensure the score surface itself is warm and editorial; no change to layout/function.
text = text.replace("background: #f4f2ec;", "background: #f8f7f4;")
text = text.replace("background:#f4f2ec;", "background:#f8f7f4;")

if text == original:
    raise SystemExit("patch made no changes")
path.write_text(text, encoding="utf-8")
print(f"Patched index.html: {len(original)} -> {len(text)} bytes")
