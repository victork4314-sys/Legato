from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

OLD_BUILD = '20260727-bumper-score-toggle-1'
NEW_BUILD = '20260727-notation-objects-1'


def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)


def sub_once(pattern, repl, label, flags=0):
    global text
    text2, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text2


if NEW_BUILD in text:
    print('Notation object system already applied')
    raise SystemExit(0)

if text.count(OLD_BUILD) != 3:
    raise SystemExit(f'build marker: expected 3 matches, found {text.count(OLD_BUILD)}')
text = text.replace(OLD_BUILD, NEW_BUILD)

one(
"const DOC_KEYS = ['notes', 'chords', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks', 'fontPack'];",
"const DOC_KEYS = ['notes', 'chords', 'scoreEvents', 'scoreSpans', 'divisi', 'condense', 'players', 'clefs', 'clefOctaves', 'instruments', 'title', 'composer', 'keyIdx', 'meter', 'tempo', 'bars', 'measureMarks', 'fontPack'];",
'document keys')

one(
"    armed: {}, grid: 0, playerName: '', entry: 'note', voice: 1, range: null, measureMarks: {},\n",
"    armed: {}, grid: 0, playerName: '', entry: 'note', voice: 1, range: null, measureMarks: {},\n    scoreEvents: [], scoreSpans: [], spanDraft: null, scoreObjectId: null, scoreEventDraft: null, scoreText: '', editingScoreObject: null,\n",
'notation state')

# Add a direct, controller-selectable route into all notation at the cursor.
one(
'''          <sc-for list="{{ staffTabs }}" as="t" hint-placeholder-count="4">
            <div onClick="{{ t.onSelect }}" data-ptr="{{ t.name }} staff" style="{{ t.style }}" style-hover="border-color:var(--accent)">{{ t.name }}</div>
          </sc-for>
''',
'''          <sc-for list="{{ staffTabs }}" as="t" hint-placeholder-count="4">
            <div onClick="{{ t.onSelect }}" data-ptr="{{ t.name }} staff" style="{{ t.style }}" style-hover="border-color:var(--accent)">{{ t.name }}</div>
          </sc-for>
          <div onClick="{{ openNotation }}" data-ptr="Add musical notation at the cursor" style="{{ notationButtonStyle }}" style-hover="border-color:var(--accent)">
            <span style="font-size:15px;line-height:1;">＋</span><span>MUSIC</span>
          </div>
''',
'toolbar notation button')

# Render real point events and start/end spans as their own selectable score layers.
one(
'''            <sc-for list="{{ chordSymbols }}" as="cs" hint-placeholder-count="0">
              <div style="{{ cs.style }}">{{ cs.text }}</div>
            </sc-for>
            <sc-for list="{{ tuplets }}" as="tp" hint-placeholder-count="0">
''',
'''            <sc-for list="{{ chordSymbols }}" as="cs" hint-placeholder-count="0">
              <div style="{{ cs.style }}">{{ cs.text }}</div>
            </sc-for>
            <sc-for list="{{ scoreEvents }}" as="ev" hint-placeholder-count="0">
              <div onClick="{{ ev.onSelect }}" data-ptr="{{ ev.ptr }}" data-score-object="true" style="{{ ev.style }}">{{ ev.text }}</div>
            </sc-for>
            <sc-for list="{{ scoreSpans }}" as="sp" hint-placeholder-count="0">
              <div onClick="{{ sp.onSelect }}" data-ptr="{{ sp.ptr }}" data-score-object="true" style="{{ sp.wrapStyle }}">
                <div style="{{ sp.line1Style }}"></div><div style="{{ sp.line2Style }}"></div>
                <div style="{{ sp.labelStyle }}">{{ sp.label }}</div><div style="{{ sp.endStyle }}">{{ sp.end }}</div>
              </div>
            </sc-for>
            <sc-for list="{{ tuplets }}" as="tp" hint-placeholder-count="0">
''',
'notation render layers')

# Add gradual tempo commands to the existing full catalog.
one(
"['Let ring','l.v.'],['Vibrato','\\uEAB0']]],",
"['Let ring','l.v.'],['Vibrato','\\uEAB0'],['Ritardando','rit.'],['Rallentando','rall.'],['Accelerando','accel.']]],",
'gradual tempo commands')

methods = r'''  scoreId(prefix) {
    return (prefix || 'o') + Math.random().toString(36).slice(2, 9);
  }
  scoreAnchor() {
    const n = this.selected(), s = this.state;
    return n ? { s: n.s, p: n.p, step: n.step } : { s: s.staff, p: s.pos, step: s.step };
  }
  scoreObjectById(id, state) {
    const s = state || this.state;
    return (s.scoreEvents || []).find(x => x.id === id) || (s.scoreSpans || []).find(x => x.id === id) || null;
  }
  scoreObjectAt(staff, pos, state) {
    const s = state || this.state, eps = .011;
    const ev = (s.scoreEvents || []).filter(x => (x.system || x.s === staff) && Math.abs(x.p - pos) < eps).sort((a, b) => b.p - a.p)[0];
    if (ev) return ev;
    return (s.scoreSpans || []).find(x => (x.s1 === staff || x.s2 === staff) && (Math.abs(x.p1 - pos) < eps || Math.abs(x.p2 - pos) < eps)) || null;
  }
  effectiveScoreEvent(type, staff, pos, state) {
    const s = state || this.state;
    return (s.scoreEvents || []).filter(x => x.type === type && x.p <= pos + .0005 && (x.system || x.s === staff)).sort((a, b) => b.p - a.p)[0] || null;
  }
  pointTempoAt(pos, state) {
    const s = state || this.state, ev = this.effectiveScoreEvent('tempo', 0, pos, s);
    return Math.max(20, Math.min(400, Number(ev ? ev.value : s.tempo) || 92));
  }
  clefAt(staff, pos, state) {
    const s = state || this.state, ev = this.effectiveScoreEvent('clef', staff, pos, s);
    return ev ? ev.value : (s.clefs[staff] || 'treble');
  }
  keyAt(pos, state) {
    const s = state || this.state, ev = this.effectiveScoreEvent('key', 0, pos, s);
    return KEYS[Math.max(0, Math.min(KEYS.length - 1, Number(ev ? ev.value : s.keyIdx) || 0))] || KEYS[0];
  }
  meterAt(pos, state) {
    const s = state || this.state, ev = this.effectiveScoreEvent('meter', 0, pos, s);
    return ev ? String(ev.value) : METERS[s.meter];
  }
  activeScoreSpan(types, staff, pos, state) {
    const s = state || this.state, wanted = Array.isArray(types) ? types : [types];
    return (s.scoreSpans || []).filter(x => wanted.indexOf(x.type) >= 0 && (x.system || x.s1 === staff || x.s2 === staff) && Math.min(x.p1, x.p2) <= pos + .0005 && Math.max(x.p1, x.p2) >= pos - .0005).sort((a, b) => Math.max(b.p1, b.p2) - Math.max(a.p1, a.p2))[0] || null;
  }
  tempoAt(pos, state) {
    const s = state || this.state, base = this.pointTempoAt(pos, s);
    const span = this.activeScoreSpan(['tempo-down', 'tempo-up'], 0, pos, s);
    if (!span) return base;
    const lo = Math.min(span.p1, span.p2), hi = Math.max(span.p1, span.p2), length = Math.max(.001, hi - lo);
    const start = this.pointTempoAt(lo, s), target = Number(span.target) || start * (span.type === 'tempo-up' ? 1.28 : .74);
    const t = Math.max(0, Math.min(1, (pos - lo) / length));
    return start + (target - start) * t;
  }
  secondsBetween(start, end, state) {
    const s = state || this.state;
    if (end <= start) return 0;
    const breaks = [start, end];
    (s.scoreEvents || []).filter(x => x.type === 'tempo' && x.p > start && x.p < end).forEach(x => breaks.push(x.p));
    (s.scoreSpans || []).filter(x => x.type === 'tempo-down' || x.type === 'tempo-up').forEach(x => {
      const a = Math.min(x.p1, x.p2), b = Math.max(x.p1, x.p2);
      if (a > start && a < end) breaks.push(a);
      if (b > start && b < end) breaks.push(b);
    });
    breaks.sort((a, b) => a - b);
    const clean = breaks.filter((x, i) => !i || Math.abs(x - breaks[i - 1]) > .0001);
    let seconds = 0;
    for (let i = 0; i < clean.length - 1; i++) {
      const a = clean[i], b = clean[i + 1], mid = (a + b) / 2;
      const span = this.activeScoreSpan(['tempo-down', 'tempo-up'], 0, mid, s);
      if (!span) { seconds += (b - a) * 60 / this.pointTempoAt(mid, s); continue; }
      const lo = Math.min(span.p1, span.p2), hi = Math.max(span.p1, span.p2), len = Math.max(.001, hi - lo);
      const b0 = this.pointTempoAt(lo, s), b1 = Number(span.target) || b0 * (span.type === 'tempo-up' ? 1.28 : .74);
      const slope = (b1 - b0) / len;
      const bpmA = Math.max(1, b0 + slope * (a - lo)), bpmB = Math.max(1, b0 + slope * (b - lo));
      seconds += Math.abs(slope) < .000001 ? (b - a) * 60 / bpmA : 60 / slope * Math.log(bpmB / bpmA);
    }
    return seconds;
  }
  beatAtElapsed(start, seconds, state) {
    const s = state || this.state, limit = Math.max(start + 1, s.bars * this.barCapacity());
    let lo = start, hi = limit;
    for (let i = 0; i < 24; i++) {
      const mid = (lo + hi) / 2;
      if (this.secondsBetween(start, mid, s) < seconds) lo = mid; else hi = mid;
    }
    return (lo + hi) / 2;
  }
  placeScoreEvent(type, name, glyph, value, options) {
    const opts = options || {}, anchor = opts.anchor || this.scoreAnchor(), system = opts.system != null ? !!opts.system : /^(key|meter|tempo|rehearsal|structure|system-text)$/.test(type);
    this.rumble('soft');
    this.setState(s => {
      const draft = s.scoreEventDraft || {}, editing = opts.editing || draft.editing || null;
      const ev = { id: editing || this.scoreId('e'), object: 'event', type: type, name: name, text: opts.text || name, glyph: glyph || '', value: value, s: anchor.s, p: anchor.p, step: anchor.step, system: system };
      let list = (s.scoreEvents || []).filter(x => x.id !== editing && !(x.type === type && x.system === system && (system || x.s === anchor.s) && Math.abs(x.p - anchor.p) < .002));
      list = list.concat([ev]).sort((a, b) => a.p - b.p);
      return { scoreEvents: list, scoreObjectId: ev.id, scoreEventDraft: null, editingScoreObject: null, panel: null, halo: false, selId: null,
        spoken: name + ' placed at bar ' + (Math.floor(anchor.p / this.barCapacity()) + 1) + ' beat ' + (anchor.p % this.barCapacity() + 1).toFixed(2) };
    });
  }
  openScoreEventPanel(type, name, glyph, editing) {
    this.rumble('tick');
    this.setState({ panel: 'score-' + type, panelIdx: 0, hub: false, halo: false, menu: false, scoreEventDraft: { type: type, name: name, glyph: glyph || '', editing: editing || null }, spoken: 'Choose ' + name + ' for the cursor position' });
  }
  placeScoreEventChoice(type, value, label, glyph, system) {
    const d = this.state.scoreEventDraft || {};
    this.placeScoreEvent(type, label || d.name || type, glyph || d.glyph || '', value, { system: system, editing: d.editing || null });
  }
  beginScoreSpan(type, name, glyph, editing) {
    const anchor = editing ? null : this.scoreAnchor();
    const old = editing ? this.scoreObjectById(editing) : null;
    const start = old ? { s: old.s1, p: old.p1, step: old.step1 } : anchor;
    this.rumble('soft');
    this.setState({ spanDraft: { object: 'span', id: editing || this.scoreId('s'), editing: editing || null, type: type, name: name, glyph: glyph || '', s1: start.s, p1: start.p, step1: start.step, system: type === 'ending' || type.indexOf('tempo-') === 0 }, scoreObjectId: null, halo: false, panel: null, selId: null,
      staff: start.s, pos: start.p, step: start.step, spoken: name + ' point one set — move to point two and press A' });
  }
  finishScoreSpan(anchor) {
    const d = this.state.spanDraft;
    if (!d) return false;
    const end0 = anchor || this.scoreAnchor(), same = Math.abs(end0.p - d.p1) < .002 && end0.s === d.s1;
    const end = same ? { s: end0.s, p: Math.min(this.state.bars * this.barCapacity() - .001, end0.p + this.gridBeats()), step: end0.step } : end0;
    const span = Object.assign({}, d, { object: 'span', editing: undefined, s2: end.s, p2: end.p, step2: end.step });
    this.rumble('soft');
    this.setState(s => ({ scoreSpans: (s.scoreSpans || []).filter(x => x.id !== d.editing && x.id !== d.id).concat([span]).sort((a, b) => Math.min(a.p1, a.p2) - Math.min(b.p1, b.p2)), spanDraft: null, scoreObjectId: span.id, selId: null,
      spoken: span.name + ' finished from point one to point two' }));
    return true;
  }
  cancelScoreSpan() {
    if (!this.state.spanDraft) return false;
    this.setState({ spanDraft: null, spoken: 'Point one cancelled' });
    return true;
  }
  selectScoreObject(id) {
    const obj = this.scoreObjectById(id);
    if (!obj) return;
    const isSpan = obj.object === 'span' || obj.p1 != null;
    const p = isSpan ? obj.p1 : obj.p, staff = isSpan ? obj.s1 : obj.s;
    this.rumble('tick');
    this.setState({ zone: 3, scoreObjectId: id, selId: null, range: null, staff: staff || 0, pos: p || 0, step: isSpan ? (obj.step1 || 6) : (obj.step || 6), spoken: obj.name + ' selected — arrows move it, A edits, B deletes' });
  }
  deleteScoreObject() {
    const id = this.state.scoreObjectId;
    if (!id) return false;
    const obj = this.scoreObjectById(id), label = obj ? obj.name : 'Notation';
    this.rumble('firm');
    this.setState(s => ({ scoreEvents: (s.scoreEvents || []).filter(x => x.id !== id), scoreSpans: (s.scoreSpans || []).filter(x => x.id !== id), scoreObjectId: null, spoken: label + ' deleted' }));
    return true;
  }
  moveScoreObject(dp, ds) {
    const id = this.state.scoreObjectId;
    if (!id) return false;
    this.setState(s => {
      const max = s.bars * this.barCapacity() - .001, maxStaff = Math.max(0, s.players.length - 1);
      const events = (s.scoreEvents || []).map(x => x.id !== id ? x : Object.assign({}, x, { p: Math.max(0, Math.min(max, x.p + dp)), s: x.system ? x.s : Math.max(0, Math.min(maxStaff, x.s + ds)) }));
      const spans = (s.scoreSpans || []).map(x => x.id !== id ? x : Object.assign({}, x, { p1: Math.max(0, Math.min(max, x.p1 + dp)), p2: Math.max(0, Math.min(max, x.p2 + dp)), s1: x.system ? x.s1 : Math.max(0, Math.min(maxStaff, x.s1 + ds)), s2: x.system ? x.s2 : Math.max(0, Math.min(maxStaff, x.s2 + ds)) }));
      const obj = events.find(x => x.id === id) || spans.find(x => x.id === id);
      return { scoreEvents: events, scoreSpans: spans, staff: obj ? (obj.s != null ? obj.s : obj.s1) : s.staff, pos: obj ? (obj.p != null ? obj.p : obj.p1) : s.pos, spoken: (obj ? obj.name : 'Notation') + ' moved' };
    });
    return true;
  }
  editSelectedScoreObject() {
    const obj = this.scoreObjectById(this.state.scoreObjectId);
    if (!obj) return false;
    if (obj.object === 'span' || obj.p1 != null) { this.beginScoreSpan(obj.type, obj.name, obj.glyph, obj.id); return true; }
    if (/^(clef|key|meter|tempo)$/.test(obj.type)) { this.openScoreEventPanel(obj.type, obj.name, obj.glyph, obj.id); return true; }
    if (/^(text|staff-text|system-text|technique|rehearsal)$/.test(obj.type)) {
      this.setState({ kb: 'scoreObjectText', kbIdx: 0, scoreText: obj.text || obj.name || '', editingScoreObject: obj.id, spoken: 'Edit ' + obj.name + ' text' });
      return true;
    }
    this.setState({ spoken: obj.name + ' selected — arrows move it, B deletes' });
    return true;
  }
  finishScoreObjectText() {
    const id = this.state.editingScoreObject, value = this.state.scoreText || 'text';
    this.setState(s => ({ scoreEvents: (s.scoreEvents || []).map(x => x.id === id ? Object.assign({}, x, { text: value, name: value }) : x), kb: null, editingScoreObject: null, spoken: value + ' saved' }));
  }
'''

one('  haloApply() {\n', methods + '  haloApply() {\n', 'notation methods')

# Replace the command application behavior while retaining note-specific commands.
pattern = r"  haloApply\(\) \{[\s\S]*?\n  \}\n  commitWheel\(\) \{"
new_halo = r'''  haloApply() {
    const s = this.state, cat = CAT[s.haloCat][0], cmd = CAT[s.haloCat][1][s.haloIdx], name = cmd[0], glyph = cmd[1];
    const lower = name.toLowerCase();
    const sel = this.selected();
    if (cat === 'Lines') {
      if (/^Tie/.test(name)) { this.toggleTie(); return this.setState({ halo: false }); }
      if (/Pedal change|Una corda|Tre corde/.test(name)) { this.placeScoreEvent('technique', name, glyph, name, { system: false, text: name }); return; }
      let type = 'line';
      if (/^Slur/.test(name)) type = 'slur'; else if (/^Phrase/.test(name)) type = 'phrase';
      else if (/Glissando/.test(name)) type = 'gliss'; else if (/Portamento/.test(name)) type = 'portamento';
      else if (/Trill extension/.test(name)) type = 'trill-line'; else if (/Sustain pedal/.test(name)) type = 'pedal';
      else if (/^8va/.test(name)) type = 'octave-up'; else if (/^8vb/.test(name)) type = 'octave-down';
      else if (/^15ma/.test(name)) type = 'octave-up-2'; else if (/^15mb/.test(name)) type = 'octave-down-2';
      else if (/Ritardando|Rallentando/.test(name)) type = 'tempo-down'; else if (/Accelerando/.test(name)) type = 'tempo-up';
      else if (/Let ring/.test(name)) type = 'let-ring'; else if (/Vibrato/.test(name)) type = 'vibrato';
      this.beginScoreSpan(type, name, glyph); return;
    }
    if (cat === 'Dynamics') {
      if (/Crescendo|Diminuendo|Swell|Niente/.test(name)) {
        const type = /Diminuendo|Niente dim/.test(name) ? 'hairpin-down' : /Swell/.test(name) ? 'hairpin-swell' : 'hairpin-up';
        this.beginScoreSpan(type, name, glyph); return;
      }
      this.placeScoreEvent('dynamic', name, glyph, glyph, { system: false }); return;
    }
    if (cat === 'Articulations' && /Fermata|Breath mark|Caesura/.test(name)) {
      this.placeScoreEvent('hold', name, glyph, glyph, { system: false }); return;
    }
    if (cat === 'Text') {
      if (/Lyrics|Figured bass|Fingering/.test(name)) {
        if (!sel) return this.setState({ halo: false, spoken: name + ' needs a selected note' });
        this.editNote(n => ({ marks: (n.marks || []).concat([{ g: name === 'Lyrics' ? 'la' : glyph, place: 'below', text: true }]) }), name + ' added');
        return this.setState({ halo: false });
      }
      if (/Chord symbol/.test(name)) { this.addChordSymbol('C7'); return this.setState({ halo: false }); }
      if (/Tempo text/.test(name)) { this.openScoreEventPanel('tempo', 'Tempo', glyph); return; }
      if (/Rehearsal mark/.test(name)) { this.placeScoreEvent('rehearsal', name, glyph, glyph, { system: true, text: glyph || 'A' }); return; }
      if (/Playing technique/.test(name)) { this.placeScoreEvent('technique', name, glyph, glyph, { system: false, text: glyph || 'pizz.' }); return; }
      const type = /System text|Copyright|Subtitle|Composer/.test(name) ? 'system-text' : /Staff text/.test(name) ? 'staff-text' : 'text';
      this.placeScoreEvent(type, name, glyph, glyph, { system: type === 'system-text', text: glyph || name }); return;
    }
    if (cat === 'Structure') {
      const cl = CLEFS.find(c => lower.indexOf(c.name.toLowerCase()) === 0);
      if (cl) { this.placeScoreEvent('clef', cl.name + ' clef', cl.glyph, cl.id, { system: false }); return; }
      if (/key signature/i.test(name)) { this.openScoreEventPanel('key', 'Key signature', glyph); return; }
      if (/time signature|open meter/i.test(name)) { this.openScoreEventPanel('meter', 'Time signature', glyph); return; }
      if (/First ending|Second ending/.test(name)) { this.beginScoreSpan('ending', name, glyph); return; }
      this.placeScoreEvent('structure', name, glyph, name, { system: true, text: glyph || name }); return;
    }
    if (cat === 'Notes') {
      if (/^Remove (top|bottom) note/.test(name)) { this.removeChordNote(); return this.setState({ halo: false }); }
      if (/^Add (third|fifth|octave)/.test(name)) { this.addInterval(/third/.test(name) ? 3 : /fifth/.test(name) ? 7 : 12, name.replace('Add ', '')); return this.setState({ halo: false }); }
      const di = DURS.findIndex(d => lower.indexOf(d.name.toLowerCase()) === 0);
      if (di >= 0) this.setDur(di);
      return this.setState({ halo: false, spoken: name + ' selected' });
    }
    if (cat === 'Rests') {
      const di = DURS.findIndex(d => lower.indexOf(d.name.toLowerCase()) === 0);
      this.setState({ entry: 'rest', halo: false, spoken: name + ' armed — A enters it' });
      if (di >= 0) this.setDur(di);
      return;
    }
    if (cat === 'Accidentals') {
      if (sel) this.editNote({ acc: /natural/i.test(name) ? null : glyph }, name + ' applied to the note');
      else this.setState({ acc: /flat/i.test(name) ? 'f' : /sharp/i.test(name) ? 'sh' : 'n', spoken: name + ' armed for the next note' });
      return this.setState({ halo: false });
    }
    if (cat === 'Ornaments') { this.applyOrn(glyph, name); return this.setState({ halo: false }); }
    if (cat === 'Articulations') {
      this.setState({ artic: name });
      if (sel) this.editNote({ art: glyph }, name + ' applied to the note');
      return this.setState({ halo: false, spoken: sel ? name + ' applied' : name + ' armed for the next note' });
    }
    if (cat === 'Rhythm') {
      if (/^Voice/.test(name)) this.setVoice(parseInt(name.replace(/\D/g, ''), 10));
      else if (/Triplet/.test(name)) this.toggleTuplet(3); else if (/Quintuplet/.test(name)) this.toggleTuplet(5);
      else if (/Sextuplet/.test(name)) this.toggleTuplet(6); else if (/Septuplet/.test(name)) this.toggleTuplet(7); else if (/Nonuplet/.test(name)) this.toggleTuplet(9);
      else if (/Beam together/.test(name)) this.editNote({ beam: 'join' }, 'Beam together'); else if (/Break beam/.test(name)) this.editNote({ beam: 'break' }, 'Beam break');
      else if (/Stem up/.test(name)) this.editNote({ stem: 'up' }, 'Stem up'); else if (/Stem down/.test(name)) this.editNote({ stem: 'down' }, 'Stem down'); else if (/Automatic stem/.test(name)) this.editNote({ stem: null }, 'Automatic stem');
      return this.setState({ halo: false, spoken: name + ' applied' });
    }
    this.setState({ halo: false, spoken: name + ' applied' });
  }
  commitWheel() {'''
sub_once(pattern, new_halo, 'halo behavior', flags=re.M)

# Add score-event choice panels before the rest of the Menu panels.
one(
"  panelRows() {\n    const s = this.state;\n",
"  panelRows() {\n    const s = this.state;\n    if (s.panel === 'score-clef') return CLEFS.map(c => ({ label: c.name + ' clef at the cursor', value: this.clefAt(s.staff, s.pos) === c.id ? 'ACTIVE HERE' : '', act: () => this.placeScoreEventChoice('clef', c.id, c.name + ' clef', c.glyph, false) }));\n    if (s.panel === 'score-key') return KEYS.map((k, i) => ({ label: k.name + ' at the cursor', value: this.keyAt(s.pos).name === k.name ? 'ACTIVE HERE' : '', act: () => this.placeScoreEventChoice('key', i, k.name + ' key signature', '', true) }));\n    if (s.panel === 'score-meter') return METERS.concat(['9/8', '10/8', '11/8', '13/8', '3/2', '4/2']).map(m => ({ label: m + ' at the cursor', value: this.meterAt(s.pos) === m ? 'ACTIVE HERE' : '', act: () => this.placeScoreEventChoice('meter', m, m + ' time signature', '', true) }));\n    if (s.panel === 'score-tempo') return [30, 36, 40, 44, 48, 52, 56, 60, 66, 72, 76, 80, 84, 92, 100, 108, 112, 120, 132, 144, 160, 176, 192, 208, 224, 240].map(t => ({ label: t + ' BPM at the cursor', value: Math.round(this.tempoAt(s.pos)) === t ? 'ACTIVE HERE' : '', act: () => this.placeScoreEventChoice('tempo', t, t + ' BPM', '', true) }));\n",
'score event panels')

# Make the main Menu key/meter/tempo entries place changes at the cursor.
one(
"      commands: () => this.setState({ hub: false, halo: true, spoken: 'All commands' }),\n      file: () => this.setState({ hub: false, menu: true, menuIdx: 0, spoken: 'File menu' }),",
"      commands: () => this.setState({ hub: false, halo: true, spoken: 'All commands' }),\n      key: () => this.openScoreEventPanel('key', 'Key signature', ''),\n      meter: () => this.openScoreEventPanel('meter', 'Time signature', ''),\n      tempo: () => this.openScoreEventPanel('tempo', 'Tempo', ''),\n      file: () => this.setState({ hub: false, menu: true, menuIdx: 0, spoken: 'File menu' }),",
'hub notation panels')

# Commit edited score-object text from the on-screen keyboard.
one(
"    if (k === 'DONE') return this.setState({ kb: null, spoken: s.kb + ' saved' });\n",
"    if (k === 'DONE') { if (s.kb === 'scoreObjectText') return this.finishScoreObjectText(); return this.setState({ kb: null, spoken: s.kb + ' saved' }); }\n",
'score text keyboard')

# Cancel/delete notation drafts and objects before note deletion.
one(
"    if (s.tieFrom && action === 'delete') return this.setState({ tieFrom: null, spoken: 'Tie cancelled' });\n",
"    if (s.tieFrom && action === 'delete') return this.setState({ tieFrom: null, spoken: 'Tie cancelled' });\n    if (s.spanDraft && action === 'delete') return this.cancelScoreSpan();\n    if (s.scoreObjectId && action === 'delete') return this.deleteScoreObject();\n",
'notation delete dispatch')

one(
"      case 'move-up': P ? this.movePointer(0, -22) : this.movePitch(1); break;\n      case 'move-down': P ? this.movePointer(0, 22) : this.movePitch(-1); break;\n      case 'move-left': P ? this.movePointer(-22, 0) : this.movePos(-1); break;\n      case 'move-right': P ? this.movePointer(22, 0) : this.movePos(1); break;\n      case 'confirm':\n        if (P) { this.clickPointer(); break; }\n",
"      case 'move-up': if (s.scoreObjectId) { this.moveScoreObject(0, -1); break; } P ? this.movePointer(0, -22) : this.movePitch(1); break;\n      case 'move-down': if (s.scoreObjectId) { this.moveScoreObject(0, 1); break; } P ? this.movePointer(0, 22) : this.movePitch(-1); break;\n      case 'move-left': if (s.scoreObjectId) { this.moveScoreObject(-this.gridBeats(), 0); break; } P ? this.movePointer(-22, 0) : this.movePos(-1); break;\n      case 'move-right': if (s.scoreObjectId) { this.moveScoreObject(this.gridBeats(), 0); break; } P ? this.movePointer(22, 0) : this.movePos(1); break;\n      case 'confirm':\n        if (P) { this.clickPointer(); break; }\n        if (s.spanDraft) { this.finishScoreSpan(); break; }\n        if (s.scoreObjectId) { this.editSelectedScoreObject(); break; }\n",
'notation movement and confirm')

# Delete selected score objects even through direct deleteSelection calls.
one(
"  deleteSelection() {\n    const s = this.state;\n",
"  deleteSelection() {\n    const s = this.state;\n    if (s.spanDraft) return this.cancelScoreSpan();\n    if (s.scoreObjectId) return this.deleteScoreObject();\n",
'notation delete selection')

# Notes and staff clicks leave object selection cleanly.
one(
"    this.setState({ selId: n.id, staff: n.s, pos: n.p, step: n.step, spoken: this.describe(n) + ' selected — up and down transpose it' });\n",
"    this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step, spoken: this.describe(n) + ' selected — up and down transpose it' });\n",
'note clears object selection')
one(
"      this.setState({ selId: n.id, staff: n.s, pos: n.p, step: n.step,\n",
"      this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step,\n",
'rest clears object selection')

# Pitch naming now follows the clef and key active at that exact position.
sub_once(
 r"  pitchName\(step, s, acc\) \{[\s\S]*?\n  \}\n  setClef\(id\)",
 r'''  pitchName(step, s, acc, pos) {
    const at = pos == null ? this.state.pos : pos;
    const bass = this.clefAt(s, at) === 'bass';
    const key = this.keyAt(at);
    const base = (bass ? BASS : NAMES)[Math.max(0, Math.min(16, step))] || '';
    const alter = acc === '\uE262' ? ' sharp' : acc === '\uE260' ? ' flat' : acc === '\uE261' ? ' natural'
      : (keyAlter(step, bass, key) === -1 ? ' flat' : keyAlter(step, bass, key) === 1 ? ' sharp' : '');
    return base.replace(/(\D+)(-?\d)/, '$1' + alter.replace(' ', '') + '$2').replace('sharp', '♯').replace('flat', '♭').replace('natural', '♮');
  }
  setClef(id)''',
 'position-aware pitch name', flags=re.M)

# Moving the cursor selects an event/span endpoint when it lands there.
one(
"      const hit = s.notes.find(n => n.s === s.staff && Math.abs(n.p - pos) < .01);\n      if (hit && !hit.id) hit.id = 'n' + Math.random().toString(36).slice(2, 8);\n      const grew = bars > s.bars;\n      return {\n        bars: bars, pos: pos, selId: hit ? hit.id : null, step: hit ? hit.step : s.step,\n        spoken: hit ? this.describe(hit) + ' selected'\n          : 'Bar ' + (Math.floor(pos / cap) + 1) + ', beat ' + (pos % cap + 1).toFixed(2) + ', empty' + (grew ? ' — bar ' + bars + ' added' : '')\n      };\n",
"      const hit = s.notes.find(n => n.s === s.staff && Math.abs(n.p - pos) < .01);\n      if (hit && !hit.id) hit.id = 'n' + Math.random().toString(36).slice(2, 8);\n      const obj = s.spanDraft ? null : this.scoreObjectAt(s.staff, pos, s);\n      const grew = bars > s.bars;\n      return {\n        bars: bars, pos: pos, selId: hit ? hit.id : null, scoreObjectId: hit ? null : (obj ? obj.id : null), step: hit ? hit.step : s.step,\n        spoken: hit ? this.describe(hit) + ' selected' : obj ? obj.name + ' selected — A edits, B deletes'\n          : 'Bar ' + (Math.floor(pos / cap) + 1) + ', beat ' + (pos % cap + 1).toFixed(2) + ', empty' + (grew ? ' — bar ' + bars + ' added' : '')\n      };\n",
'cursor notation selection')

# Staff clicks clear any previous score-object selection.
one(
"          this.setState({ zone: 3, staff: i, pos: beat, step: step, selId: null,\n",
"          this.setState({ zone: 3, staff: i, pos: beat, step: step, selId: null, scoreObjectId: null,\n",
'staff click object clear')
one(
"          this.setState({ zone: 3, staff: i, pos: beat, step: step, selId: null }, () => this.enterNote());\n",
"          this.setState({ zone: 3, staff: i, pos: beat, step: step, selId: null, scoreObjectId: null }, () => this.enterNote());\n",
'staff double click object clear')

# Position-aware audition and sample warming.
one(
"      const m = midiFor(n.step, s.clefs[n.s] === 'bass', n.acc, KEYS[s.keyIdx], (s.clefOctaves || [])[n.s]), k = n.s + ':' + m;\n",
"      const m = midiFor(n.step, this.clefAt(n.s, n.p, s) === 'bass', n.acc, this.keyAt(n.p, s), (s.clefOctaves || [])[n.s]), k = n.s + ':' + m;\n",
'warm score events')
one(
"    this.rumbleTone(midiFor(step, this.state.clefs[staff] === 'bass', acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[staff]));\n",
"    this.rumbleTone(midiFor(step, this.clefAt(staff, note ? note.p : this.state.pos) === 'bass', acc, this.keyAt(note ? note.p : this.state.pos), (this.state.clefOctaves || [])[staff]));\n",
'audition rumble events')
one(
"    const ac = this.audio(), midi = midiFor(step, this.state.clefs[staff] === 'bass', acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[staff]);\n",
"    const at = note ? note.p : this.state.pos;\n    const ac = this.audio(), midi = midiFor(step, this.clefAt(staff, at) === 'bass', acc, this.keyAt(at), (this.state.clefOctaves || [])[staff]);\n",
'audition audio events')

# Playback walks real tempo changes and reads active clef/key/dynamic/spans per note.
sub_once(
 r"  startPlayback\(\) \{[\s\S]*?\n  \}\n  stopPlayback\(\) \{",
 r'''  startPlayback() {
    this.rumble('soft');
    const ac = this.audio();
    const capL = this.barCapacity();
    this._b0 = this.state.loop ? Math.floor(this.state.pos / capL) * capL : 0;
    const spb0 = 60 / this.tempoAt(this._b0);
    this._t0 = ac.currentTime + .06 + (this.state.countIn ? spb0 * 4 : 0);
    if (this.state.countIn) for (let k = 0; k < 4; k++) this.click(ac.currentTime + .06 + k * spb0, k === 0);
    this._clicked = {};
    this._fired = {};
    this._order = this.playOrder();
    this._orderIdx = 0;
    this.setState({ playing: true, playPos: this._b0, spoken: this.state.loop ? 'Looping bar ' + (this._b0 / capL + 1) : 'Playing from bar 1' });
  }
  stopPlayback() {''',
 'tempo-aware playback start', flags=re.M)

sub_once(
 r"  schedule\(\) \{[\s\S]*?\n  \}\n  scroller\(\) \{",
 r'''  schedule() {
    const ac = this._ac;
    if (!ac) return;
    if (this._t0 == null || !this._fired) return this.startPlayback();
    const s = this.state, elapsed = Math.max(0, ac.currentTime - this._t0);
    const beat = this.beatAtElapsed(this._b0, elapsed, s);
    if (!isFinite(beat)) { this._t0 = ac.currentTime; return; }
    const capP = this.barCapacity(), order = this._order && this._order.length ? this._order : null;
    const loopEnd = s.loop ? this._b0 + capP : (order ? order.length * capP : s.bars * capP);
    if (beat >= loopEnd) {
      if (s.loop) { this._t0 = ac.currentTime; this._fired = {}; this.setState({ playPos: this._b0 }); return; }
      return this.setState({ playing: false, playPos: 0, spoken: 'Playback finished — ' + s.bars + ' bars' });
    }
    const ahead = this.beatAtElapsed(this._b0, elapsed + .38, s);
    s.notes.forEach((n, i) => {
      if (n.rest || n.cue) return;
      if (order) {
        const slot = Math.floor((beat + .0001) / capP), src = order[Math.min(order.length - 1, slot)], nBar = Math.floor(n.p / capP + .0001);
        if (nBar !== src && nBar !== order[Math.min(order.length - 1, slot + 1)]) return;
      } else if (!(n.p >= this._b0) || n.p > loopEnd) return;
      if (this._fired[i] || !(n.p <= ahead)) return;
      this._fired[i] = 1;
      let playAt = n.p;
      if (order) {
        const nBar = Math.floor(n.p / capP + .0001), slot = order.indexOf(nBar, Math.max(0, Math.floor((beat + .0001) / capP) - 1));
        if (slot < 0) return;
        playAt = slot * capP + (n.p - nBar * capP);
        const fk = 'o' + slot + ':' + i;
        if (this._fired[fk]) return;
        this._fired[fk] = 1;
      }
      const when = this._t0 + this.secondsBetween(this._b0, playAt, s);
      let beats = noteBeats(n), chain = n, guard = 0;
      while (chain && (chain.tie || chain.tieTo) && guard++ < 32) {
        const nxt = chain.tieTo ? s.notes.find(x => x.id === chain.tieTo) : s.notes.filter(x => x.s === n.s && (x.voice || 1) === (n.voice || 1) && !x.rest && x.step === chain.step && Math.abs(x.p - (chain.p + noteBeats(chain))) < .002)[0];
        if (!nxt) break;
        beats += noteBeats(nxt); this._fired['tied' + s.notes.indexOf(nxt)] = 1; chain = nxt;
      }
      if (this._fired['tied' + i]) return;
      const clef = this.clefAt(n.s, n.p, s), key = this.keyAt(n.p, s);
      let m = midiFor(n.step, clef === 'bass', n.acc, key, (s.clefOctaves || [])[n.s]);
      const dynMap = { '\uE529': 20, '\uE52A': 30, '\uE52B': 42, '\uE520': 54, '\uE52C': 66, '\uE52D': 78, '\uE522': 92, '\uE52F': 104, '\uE530': 116, '\uE531': 124, '\uE539': 122, '\uE53B': 126, '\uE534': 96, '\uE53C': 118, '\uE526': 14 };
      const dynEv = this.effectiveScoreEvent('dynamic', n.s, n.p, s), dynGlyph = n.dyn || (dynEv && (dynEv.glyph || dynEv.value));
      let vel = Math.round(dynGlyph && dynMap[dynGlyph] ? dynMap[dynGlyph] : 40 + (s.vel / 100) * 87);
      const hair = this.activeScoreSpan(['hairpin-up', 'hairpin-down', 'hairpin-swell'], n.s, n.p, s);
      if (hair) {
        const lo = Math.min(hair.p1, hair.p2), hi = Math.max(hair.p1, hair.p2), t = Math.max(0, Math.min(1, (n.p - lo) / Math.max(.001, hi - lo)));
        const target = hair.type === 'hairpin-down' ? 28 : hair.type === 'hairpin-swell' ? (t < .5 ? 118 : 34) : 118;
        const tt = hair.type === 'hairpin-swell' ? (t < .5 ? t * 2 : (t - .5) * 2) : t;
        vel = Math.round(vel + (target - vel) * tt);
      }
      const oct = this.activeScoreSpan(['octave-up', 'octave-down', 'octave-up-2', 'octave-down-2'], n.s, n.p, s);
      if (oct) m += (oct.type === 'octave-up' ? 12 : oct.type === 'octave-down' ? -12 : oct.type === 'octave-up-2' ? 24 : -24);
      const slur = this.activeScoreSpan(['slur', 'phrase', 'let-ring'], n.s, n.p, s), pedal = this.activeScoreSpan('pedal', n.s, n.p, s);
      let duration = this.secondsBetween(n.p, n.p + beats, s);
      if (pedal) duration = Math.max(duration, this.secondsBetween(n.p, Math.max(n.p + beats, Math.max(pedal.p1, pedal.p2)), s));
      else if (slur) duration *= 1.08;
      const decorated = ORN_REPLACES[n.orn];
      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : .96), n.s, decorated ? vel * .8 : vel, n.art);
      this.realise(n, m, when, duration, vel);
    });
    (s.chords || []).forEach((c, ci) => {
      if (c.p < this._b0 || c.p > loopEnd) return;
      const k = 'c' + ci;
      if (this._fired[k] || c.p > ahead) return;
      this._fired[k] = 1;
      const pitches = this.chordPitches(c.text); if (!pitches) return;
      const when = this._t0 + this.secondsBetween(this._b0, c.p, s), dur = this.secondsBetween(c.p, c.p + 1.6, s);
      pitches.forEach((m2, j) => this.playTone(m2, Math.max(ac.currentTime, when) + j * .012, dur, 0, 62, null));
    });
    if (s.metronome) {
      const first = Math.floor(beat), last = Math.floor(ahead);
      for (let b = first; b <= last; b++) {
        if (b < this._b0 || this._clicked[b]) continue;
        this._clicked[b] = 1;
        const meter = this.meterAt(b, s).split('/'), cap = Number(meter[0]) * (4 / Number(meter[1]));
        this.click(this._t0 + this.secondsBetween(this._b0, b, s), Math.abs(b % cap) < .001);
      }
    }
    if (Math.abs(beat - s.playPos) > .02) this.setState({ playPos: beat });
  }
  scroller() {''',
 'position-aware schedule', flags=re.M)

# A visible direct button and more informative selection readout.
one(
"      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : 'var(--border-strong)') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(var(--accent-rgb),.12)' : 'var(--raised)') + ';cursor:pointer;' + this.ring('top', 2),\n",
"      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : 'var(--border-strong)') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(var(--accent-rgb),.12)' : 'var(--raised)') + ';cursor:pointer;' + this.ring('top', 2),\n      openNotation: () => this.setState({ halo: true, haloCat: 5, haloIdx: 0, spoken: 'Add music at the cursor — choose a category and press A' }),\n      notationButtonStyle: 'display:flex;align-items:center;justify-content:center;gap:5px;flex:0 0 auto;min-height:38px;padding:3px 10px;border-radius:4px;cursor:pointer;font-family:\\'IBM Plex Mono\\',monospace;font-size:9.5px;font-weight:700;letter-spacing:.05em;border:1px solid var(--border-strong);background:var(--control);color:var(--text);',\n",
'toolbar notation render values')
one(
"      tempo: s.tempo,\n",
"      tempo: Math.round(this.tempoAt(s.pos, s)),\n",
'cursor tempo display')
one(
"      selectionCount: s.tieFrom ? 'CHOOSE TIE END' : (s.selId ? 'NOTE SELECTED' : 'CURSOR'),\n",
"      selectionCount: s.spanDraft ? 'CHOOSE POINT TWO' : s.tieFrom ? 'CHOOSE TIE END' : (s.scoreObjectId ? 'MUSIC OBJECT SELECTED' : s.selId ? 'NOTE SELECTED' : 'CURSOR'),\n",
'notation selection readout')

# Insert point-event and span rendering after chord symbols in renderVals.
one(
'''      chordSymbols: (s.chords || []).map((c, i) => {
        const topStaff = STAVES.find(st => !st.hidden) || STAVES[0];
        return {
          text: c.text,
          style: 'position:absolute;left:' + (noteX(c.p) - 8) + 'px;top:' + (topStaff.top - 44) + 'px;font-family:var(--ui-font);font-size:17px;font-weight:600;color:var(--ink);white-space:nowrap;'
            + (s.chordIdx === i ? 'background:rgba(var(--accent-rgb),.22);border-radius:3px;padding:0 3px;' : '')
        };
      }),
''',
'''      chordSymbols: (s.chords || []).map((c, i) => {
        const topStaff = STAVES.find(st => !st.hidden) || STAVES[0];
        return {
          text: c.text,
          style: 'position:absolute;left:' + (noteX(c.p) - 8) + 'px;top:' + (topStaff.top - 44) + 'px;font-family:var(--ui-font);font-size:17px;font-weight:600;color:var(--ink);white-space:nowrap;'
            + (s.chordIdx === i ? 'background:rgba(var(--accent-rgb),.22);border-radius:3px;padding:0 3px;' : '')
        };
      }),
      scoreEvents: (s.scoreEvents || []).map(ev => {
        const st = STAVES[ev.s] || STAVES[0], topStaff = STAVES.find(x => !x.hidden) || STAVES[0], x = noteX(ev.p), selected = s.scoreObjectId === ev.id;
        let text2 = ev.text || ev.name || '', top = st.top - 30, family = 'var(--ui-font)', size = 13, extra = 'font-style:italic;', left = x - 6;
        if (ev.type === 'clef') { const c = CLEFS.find(z => z.id === ev.value) || CLEFS[0]; text2 = c.glyph; family = 'Bravura,\\'Noto Music\\',serif'; size = 42; top = st.top - 5; left = x - 14; extra = ''; }
        else if (ev.type === 'key') { const k = KEYS[Number(ev.value)] || KEYS[0]; text2 = Array(k.n || 0).fill(k.type === 'flat' ? SM.flat : SM.sharp).join('') || '♮'; family = 'Bravura,\\'Noto Music\\',serif'; size = 27; top = st.top + 5; extra = ''; }
        else if (ev.type === 'meter') { const parts = String(ev.value).split('/'); text2 = parts[0] + '\\n' + parts[1]; family = 'var(--ui-font)'; size = 18; top = st.top - 1; extra = 'font-weight:800;line-height:.72;text-align:center;white-space:pre-line;'; }
        else if (ev.type === 'tempo') { text2 = '♩ = ' + ev.value; top = topStaff.top - 48; size = 14; extra = 'font-weight:700;'; }
        else if (ev.type === 'dynamic') { text2 = ev.glyph || ev.value || ev.name; family = 'Bravura,\\'Noto Music\\',serif'; size = 32; top = st.top + 58; extra = ''; }
        else if (ev.type === 'hold') { text2 = ev.glyph || ev.name; family = 'Bravura,\\'Noto Music\\',serif'; size = 30; top = st.top - 34; extra = ''; }
        else if (ev.type === 'rehearsal') { text2 = ev.text || ev.glyph || 'A'; top = topStaff.top - 64; size = 14; extra = 'font-weight:800;border:1.5px solid var(--ink);padding:2px 6px;border-radius:2px;'; }
        else if (ev.type === 'structure' || ev.type === 'system-text') { top = topStaff.top - 42; extra = ev.type === 'system-text' ? 'font-weight:600;' : ''; }
        else if (ev.type === 'technique') { top = st.top + 63; extra = 'font-style:italic;font-weight:600;'; }
        const sel = selected ? 'outline:2px solid var(--score-accent);outline-offset:3px;background:rgba(var(--accent-rgb),.12);border-radius:2px;' : '';
        return { text: text2, ptr: (ev.name || ev.type) + ' at the cursor', onSelect: () => this.selectScoreObject(ev.id), style: 'position:absolute;left:' + left + 'px;top:' + top + 'px;z-index:12;cursor:pointer;color:var(--ink);white-space:nowrap;font-family:' + family + ';font-size:' + size + 'px;line-height:1;' + extra + sel };
      }),
      scoreSpans: (() => {
        const list = (s.scoreSpans || []).slice();
        if (s.spanDraft) list.push(Object.assign({}, s.spanDraft, { p2: s.pos, s2: s.staff, step2: s.step, preview: true }));
        return list.map(sp => {
          const st1 = STAVES[sp.s1] || STAVES[0], st2 = STAVES[sp.s2 == null ? sp.s1 : sp.s2] || st1;
          const x1 = noteX(Math.min(sp.p1, sp.p2)), x2 = noteX(Math.max(sp.p1, sp.p2)), width = Math.max(22, x2 - x1);
          const selected = s.scoreObjectId === sp.id || sp.preview, accent2 = selected ? 'var(--score-accent)' : 'var(--ink)';
          let top = Math.min(st1.top, st2.top) - 24, h = Math.abs(st2.top - st1.top) + 90, label = '', end = '', line1 = '', line2 = '';
          const base = 'position:absolute;left:0;transform-origin:left center;border-color:' + accent2 + ';';
          if (sp.type === 'slur' || sp.type === 'phrase') { top = Math.min(st1.top, st2.top) - (sp.type === 'phrase' ? 40 : 27); h = 28; line1 = base + 'top:9px;width:' + width + 'px;height:14px;border:2px solid ' + accent2 + ';border-color:' + accent2 + ' transparent transparent transparent;border-radius:50% 50% 0 0;'; }
          else if (sp.type.indexOf('hairpin') === 0) { top = st1.top + 65; h = 22; const up = sp.type !== 'hairpin-down'; const swell = sp.type === 'hairpin-swell'; line1 = base + 'top:10px;width:' + (swell ? width / 2 : width) + 'px;height:1.5px;background:' + accent2 + ';transform:rotate(' + (up ? -7 : 7) + 'deg);'; line2 = base + 'top:10px;width:' + (swell ? width / 2 : width) + 'px;height:1.5px;background:' + accent2 + ';transform:rotate(' + (up ? 7 : -7) + 'deg);' + (swell ? 'left:' + width / 2 + 'px;' : ''); }
          else if (sp.type === 'pedal') { top = st1.top + 72; h = 22; label = 'Ped.'; end = '✱'; line1 = base + 'left:28px;top:10px;width:' + Math.max(8, width - 38) + 'px;border-top:1.5px solid ' + accent2 + ';'; }
          else if (sp.type.indexOf('octave-') === 0) { top = st1.top - 45; h = 25; label = sp.type === 'octave-up' ? '8va' : sp.type === 'octave-down' ? '8vb' : sp.type === 'octave-up-2' ? '15ma' : '15mb'; line1 = base + 'left:30px;top:10px;width:' + Math.max(8, width - 30) + 'px;border-top:1.5px dashed ' + accent2 + ';'; end = '⌟'; }
          else if (sp.type === 'gliss' || sp.type === 'portamento') { const y1 = st1.top + 48 - (sp.step1 || 6) * 6, y2 = st2.top + 48 - (sp.step2 || 6) * 6, dy = y2 - y1; top = Math.min(y1, y2) - 6; h = Math.abs(dy) + 16; const angle = Math.atan2(dy, width) * 180 / Math.PI; label = sp.type === 'gliss' ? 'gliss.' : 'port.'; line1 = base + 'top:' + (y1 - top) + 'px;width:' + width + 'px;border-top:1.5px ' + (sp.type === 'gliss' ? 'wavy' : 'solid') + ' ' + accent2 + ';transform:rotate(' + angle + 'deg);'; }
          else if (sp.type === 'trill-line') { top = st1.top - 40; h = 24; label = 'tr'; line1 = base + 'left:20px;top:10px;width:' + Math.max(8, width - 20) + 'px;border-top:2px wavy ' + accent2 + ';'; }
          else if (sp.type === 'tempo-down' || sp.type === 'tempo-up') { const first = STAVES.find(x => !x.hidden) || STAVES[0]; top = first.top - 58; h = 26; label = sp.name || (sp.type === 'tempo-up' ? 'accel.' : 'rit.'); line1 = base + 'left:34px;top:12px;width:' + Math.max(8, width - 34) + 'px;border-top:1.5px dashed ' + accent2 + ';'; }
          else if (sp.type === 'ending') { const first = STAVES.find(x => !x.hidden) || STAVES[0]; top = first.top - 72; h = 24; label = /^Second/.test(sp.name) ? '2.' : '1.'; line1 = base + 'top:8px;width:' + width + 'px;border-top:1.5px solid ' + accent2 + ';border-left:1.5px solid ' + accent2 + ';height:12px;'; }
          else { top = st1.top + 66; h = 20; label = sp.name || ''; line1 = base + 'top:10px;width:' + width + 'px;border-top:1.5px solid ' + accent2 + ';'; }
          const selectedStyle = selected ? 'background:rgba(var(--accent-rgb),.08);outline:1px dashed ' + accent2 + ';outline-offset:2px;' : '';
          return { ptr: (sp.name || sp.type) + (sp.preview ? ' point two preview' : ' from point one to point two'), onSelect: () => { if (!sp.preview) this.selectScoreObject(sp.id); }, wrapStyle: 'position:absolute;left:' + x1 + 'px;top:' + top + 'px;width:' + width + 'px;height:' + h + 'px;z-index:11;cursor:pointer;' + selectedStyle, line1Style: line1 || 'display:none;', line2Style: line2 || 'display:none;', label: label, end: end, labelStyle: label ? 'position:absolute;left:0;top:0;font-family:var(--ui-font);font-size:13px;font-style:italic;font-weight:600;color:' + accent2 + ';white-space:nowrap;' : 'display:none;', endStyle: end ? 'position:absolute;right:-2px;top:2px;font-family:var(--ui-font);font-size:15px;color:' + accent2 + ';' : 'display:none;' };
        });
      })(),
''',
'notation render values')

# Keep the existing bumper shortcut and accidental bindings protected.
for marker in [
    "button4: 'previous-zone', button5: 'next-zone'",
    'const BUMPER_COMBO_MS = 120;',
    'this.toggleScoreEditor();',
    "case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;",
    "case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;"
]:
    if marker not in text:
        raise SystemExit('Protected controller behavior missing: ' + marker)

required = [
    NEW_BUILD,
    "'scoreEvents', 'scoreSpans'",
    'beginScoreSpan(type, name, glyph, editing)',
    'finishScoreSpan(anchor)',
    'placeScoreEvent(type, name, glyph, value, options)',
    'clefAt(staff, pos, state)',
    'tempoAt(pos, state)',
    'secondsBetween(start, end, state)',
    'scoreEvents: (s.scoreEvents || []).map',
    'scoreSpans: (() =>',
    'CHOOSE POINT TWO',
    'Add musical notation at the cursor'
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing notation marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Notation object system applied')
