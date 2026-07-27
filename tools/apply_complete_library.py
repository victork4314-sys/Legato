from __future__ import annotations

from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

OLD_BUILD = '20260727-command-list-hairpins-1'
NEW_BUILD = '20260727-complete-smufl-playback-1'


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)


def insert_before(anchor: str, addition: str, label: str) -> None:
    replace_once(anchor, addition + anchor, label)


# Build and cache identity, plus generated catalog before the app runtime.
replace_once(f'<meta name="legato-build" content="{OLD_BUILD}">', f'<meta name="legato-build" content="{NEW_BUILD}">', 'build meta')
replace_once(
    f'<script src="./cache-refresh.js?v={OLD_BUILD}"></script>\n<script src="./support.js?v={OLD_BUILD}"></script>',
    f'<script src="./cache-refresh.js?v={NEW_BUILD}"></script>\n<script src="./smufl-catalog.js?v={NEW_BUILD}"></script>\n<script src="./support.js?v={NEW_BUILD}"></script>',
    'catalog and cache scripts'
)

# Add a dedicated logical selector beside the placement library.
replace_once(
'''          <div onClick="{{ openNotation }}" data-ptr="Add musical notation at the cursor" style="{{ notationButtonStyle }}" style-hover="border-color:var(--accent)">
            <span style="font-size:15px;line-height:1;">＋</span><span>MUSIC</span>
          </div>''',
'''          <div onClick="{{ openNotation }}" data-ptr="Add musical notation at the cursor" style="{{ notationButtonStyle }}" style-hover="border-color:var(--accent)">
            <span style="font-size:15px;line-height:1;">＋</span><span>MUSIC</span>
          </div>
          <div onClick="{{ openScoreSelector }}" data-ptr="Select any object in the score" style="{{ scoreSelectorButtonStyle }}" style-hover="border-color:var(--accent)">
            <span style="font-size:13px;line-height:1;">◎</span><span>SELECT</span>
          </div>''',
    'score selector button'
)

# Turn the old curated list into one input source, then build the complete library from official metadata.
replace_once('const CAT = [', 'const LEGACY_CAT = [', 'rename curated catalog')
replace_once(
'''];
const PROJECT_OPS = [''',
'''];

const SMUFL_CATALOG = window.LEGATO_SMUFL_CATALOG || { glyphs: [], groups: [], glyphCount: 0, rangeCount: 0 };
const LEGATO_POPULAR = {
  Notes: ['Whole note','Half note','Quarter note','Eighth note','16th note','Grace note','Add third','Add fifth','Add octave'],
  Rests: ['Whole rest','Half rest','Quarter rest','Eighth rest','16th rest'],
  Accidentals: ['Double flat','Flat','Natural','Sharp','Double sharp'],
  Articulations: ['Staccato','Staccatissimo','Tenuto','Accent','Marcato','Fermata','Breath mark','Caesura','Up bow','Down bow','Natural harmonic','Snap pizzicato'],
  Ornaments: ['Trill','Upper mordent','Lower mordent','Turn','Inverted turn','Acciaccatura','Appoggiatura','Arpeggio up','Arpeggio down','Fall','Scoop','Doit','Bend'],
  Dynamics: ['pp','p','mp','mf','f','ff','sfz','Crescendo','Diminuendo','Swell'],
  Lines: ['Tie','Slur','Phrase mark','Sustain pedal','8va','8vb','Glissando line','Portamento line','Let ring','Ritardando','Accelerando'],
  Rhythm: ['Triplet','Quintuplet','Beam together','Break beam','Stem up','Stem down','Automatic stem'],
  Text: ['Lyrics','Chord symbol','Playing technique','Tempo change','Rehearsal mark','Expression text'],
  Structure: ['Treble clef','Bass clef','Alto clef','Tenor clef','Percussion clef','Key signature change','Time signature change','Normal barline','Double barline','Final barline','Start repeat','End repeat','First ending','Second ending','Segno','Coda','Fine']
};
function legacyTuple(category, item) {
  return [item[0], item[1], { legacy: true, legacyCategory: category }];
}
function catalogTuple(item) {
  return [item.label, item.glyph || '□', Object.assign({ catalog: true }, item)];
}
function buildCompleteCatalog() {
  const out = [], popular = [], seenPopular = {};
  Object.keys(LEGATO_POPULAR).forEach(category => {
    const source = LEGACY_CAT.find(c => c[0] === category);
    if (!source) return;
    LEGATO_POPULAR[category].forEach(label => {
      const item = source[1].find(x => x[0] === label);
      if (item && !seenPopular[label]) { seenPopular[label] = 1; popular.push(legacyTuple(category, item)); }
    });
  });
  (SMUFL_CATALOG.glyphs || []).filter(g => g.tier === 'popular').forEach(g => {
    if (!seenPopular[g.label]) { seenPopular[g.label] = 1; popular.push(catalogTuple(g)); }
  });
  out.push(['Popular', popular]);
  LEGACY_CAT.forEach(category => out.push([category[0], category[1].map(item => legacyTuple(category[0], item))]));
  const byGroupRange = {};
  (SMUFL_CATALOG.glyphs || []).forEach(g => {
    const key = g.group + '\u0000' + g.range;
    (byGroupRange[key] = byGroupRange[key] || []).push(catalogTuple(g));
  });
  (SMUFL_CATALOG.groups || []).forEach(group => {
    Object.keys(byGroupRange).filter(key => key.split('\u0000')[0] === group).sort((a,b) => a.localeCompare(b)).forEach(key => {
      const range = key.split('\u0000')[1];
      out.push([group + ' · ' + range, byGroupRange[key]]);
    });
  });
  return out;
}
const CAT = buildCompleteCatalog();

const PROJECT_OPS = [''',
    'dynamic complete catalog'
)

# State for exact chord-head selection.
replace_once(
"    scoreEvents: [], scoreSpans: [], spanDraft: null, scoreObjectId: null, scoreEventDraft: null, scoreText: '', editingScoreObject: null,",
"    scoreEvents: [], scoreSpans: [], spanDraft: null, scoreObjectId: null, scoreEventDraft: null, scoreText: '', editingScoreObject: null, selectedChordHead: null,",
    'selector state'
)

# Add catalog placement, complete logical selection, chord-head editing, and semantic playback helpers.
methods = r'''  durationFromCatalog(id, label) {
    const t = ((id || '') + ' ' + (label || '')).toLowerCase();
    if (/1024/.test(t)) return 't';
    if (/512|256|128|64|32nd/.test(t)) return 't';
    if (/16th/.test(t)) return 's';
    if (/8th|eighth/.test(t)) return 'e';
    if (/half/.test(t)) return 'h';
    if (/whole|breve|longa|maxima/.test(t)) return 'w';
    return 'q';
  }
  catalogClefValue(meta) {
    const t = ((meta.id || '') + ' ' + (meta.label || '')).toLowerCase();
    if (/fclef|bass/.test(t)) return 'bass';
    if (/unpitched|percussion|neutral clef/.test(t)) return 'percussion';
    if (/tenor/.test(t)) return 'tenor';
    if (/cclef|alto/.test(t)) return 'alto';
    return 'treble';
  }
  catalogSpanType(meta) {
    if (meta.kind === 'hairpin') return meta.direction === 'down' ? 'hairpin-down' : 'hairpin-up';
    if (meta.kind === 'octave-line') return Number(meta.semitones) === -24 ? 'octave-down-2' : Number(meta.semitones) === 24 ? 'octave-up-2' : Number(meta.semitones) < 0 ? 'octave-down' : 'octave-up';
    if (meta.kind === 'pedal') return 'pedal';
    if (meta.kind === 'slur') return 'slur';
    if (meta.kind === 'tie') return 'tie';
    if (meta.kind === 'let-ring') return 'let-ring';
    if (meta.kind === 'vibrato') return 'vibrato';
    if (meta.kind === 'tempo') return meta.direction === 'up' ? 'tempo-up' : 'tempo-down';
    if (meta.kind === 'pitch-effect') return meta.effect === 'portamento' ? 'portamento' : 'gliss';
    return 'line';
  }
  applyCatalogCommand(meta, name, glyph) {
    const sel = this.selected(), playback = Object.assign({}, meta);
    if (meta.kind === 'tie') { this.toggleTie(); return this.setState({ halo: false }); }
    if (meta.placement === 'span') { this.beginScoreSpan(this.catalogSpanType(meta), name, glyph, null, playback); return; }
    if (meta.placement === 'structure') {
      const bar = Math.floor(this.state.pos / this.barCapacity());
      this.setState(s => {
        const mm = Object.assign({}, s.measureMarks || {});
        mm[bar] = (mm[bar] || []).concat([{ g: glyph, name: name, smufl: meta.id }]);
        return { measureMarks: mm };
      });
      this.placeScoreEvent('structure', name, glyph, name, { system: true, text: glyph || name, meta: playback });
      return;
    }
    if (meta.kind === 'clef') {
      this.placeScoreEvent('clef', name, glyph, this.catalogClefValue(meta), { system: false, meta: playback });
      return;
    }
    if (meta.kind === 'meter') {
      this.placeScoreEvent('meter-glyph', name, glyph, glyph, { system: true, text: glyph, meta: playback });
      return;
    }
    if (meta.kind === 'dynamic' || meta.kind === 'hold') {
      this.placeScoreEvent(meta.kind, name, glyph, glyph, { system: false, meta: playback });
      return;
    }
    if (meta.kind === 'text') {
      this.placeScoreEvent('text', name, glyph, glyph, { system: false, text: glyph || name, meta: playback });
      return;
    }
    if (meta.kind === 'rest') {
      const dur = this.durationFromCatalog(meta.id, name), di = DURS.findIndex(d => d.id === dur);
      this.setState({ entry: 'rest', halo: false, armed: Object.assign({}, this.state.armed, { restGlyph: glyph, restSmufl: meta.id }), spoken: name + ' armed — A enters it' });
      if (di >= 0) this.setDur(di);
      return;
    }
    if (meta.placement === 'note' || /^(notehead|accidental|articulation|ornament|tremolo|pitch-effect|technique|bowing|percussion)$/.test(meta.kind)) {
      const patch = {};
      if (meta.kind === 'notehead') { patch.noteheadGlyph = glyph; patch.noteheadSmufl = meta.id; patch.noteheadPlayback = playback; }
      else if (meta.kind === 'accidental') { patch.acc = glyph; patch.accCents = meta.cents == null ? null : Number(meta.cents); patch.accSmufl = meta.id; }
      else if (meta.kind === 'articulation') { patch.art = glyph; patch.artPlayback = playback; }
      else if (meta.kind === 'ornament') { patch.orn = glyph; patch.ornPlayback = playback; }
      else if (meta.kind === 'tremolo') { patch.orn = glyph; patch.tremoloPlayback = playback; }
      else if (meta.kind === 'pitch-effect') { patch.orn = glyph; patch.pitchPlayback = playback; }
      else if (meta.kind === 'percussion') { patch.noteheadGlyph = glyph; patch.percussionPlayback = playback; }
      else { patch.techniqueGlyph = glyph; patch.techniquePlayback = playback; }
      if (sel) {
        this.editNote(patch, name + ' applied to the selected note');
        this.setState({ halo: false }, () => this.audition(sel.step, sel.s, patch.acc || sel.acc, patch.art || sel.art, Object.assign({}, sel, patch)));
      } else {
        this.setState(s => ({ armed: Object.assign({}, s.armed, patch), halo: false, spoken: name + ' armed — the next note gets it' }));
      }
      return;
    }
    this.placeScoreEvent('glyph', name, glyph, glyph, { system: false, text: glyph || name, meta: playback });
  }
  scoreSelectableObjects(state) {
    const s = state || this.state, out = [];
    (s.notes || []).forEach(n => {
      const baseLabel = n.rest ? 'Rest' : this.pitchName(n.step, n.s, n.acc, n.p);
      out.push({ kind: n.rest ? 'rest' : 'note', id: n.id, noteId: n.id, staff: n.s, pos: n.p, step: n.step, label: baseLabel + ' · bar ' + (Math.floor(n.p / this.barCapacity()) + 1) });
      if (!n.rest) {
        const heads = [n.step].concat(n.chord || [] .map ? (n.chord || []).map(x => n.step + x) : []);
        heads.forEach((step, index) => out.push({ kind: 'chord-head', id: n.id + ':head:' + index, noteId: n.id, headIndex: index, staff: n.s, pos: n.p, step: step, label: 'Chord note ' + this.pitchName(step, n.s, n.acc, n.p) }));
      }
      (n.marks || []).forEach((mark, index) => out.push({ kind: 'note-mark', id: n.id + ':mark:' + index, noteId: n.id, markIndex: index, staff: n.s, pos: n.p, step: n.step, label: 'Attached mark ' + (mark.name || mark.g || index + 1) }));
    });
    (s.chords || []).forEach((c, index) => out.push({ kind: 'chord-symbol', id: 'chord:' + index, chordIndex: index, staff: 0, pos: c.p, step: 10, label: 'Chord symbol ' + c.text }));
    (s.scoreEvents || []).forEach(ev => out.push({ kind: 'score-event', id: ev.id, scoreObjectId: ev.id, staff: ev.s || 0, pos: ev.p, step: ev.step || 6, label: ev.name || ev.type }));
    (s.scoreSpans || []).forEach(sp => {
      out.push({ kind: 'score-span', id: sp.id, scoreObjectId: sp.id, staff: sp.s1 || 0, pos: sp.p1, step: sp.step1 || 6, label: (sp.name || sp.type) + ' · whole span' });
      out.push({ kind: 'span-start', id: sp.id + ':start', scoreObjectId: sp.id, staff: sp.s1 || 0, pos: sp.p1, step: sp.step1 || 6, handle: 'start', label: (sp.name || sp.type) + ' · start handle' });
      out.push({ kind: 'span-end', id: sp.id + ':end', scoreObjectId: sp.id, staff: sp.s2 == null ? sp.s1 : sp.s2, pos: sp.p2, step: sp.step2 || 6, handle: 'end', label: (sp.name || sp.type) + ' · end handle' });
    });
    Object.keys(s.measureMarks || {}).forEach(bar => (s.measureMarks[bar] || []).forEach((mark, index) => out.push({ kind: 'measure-mark', id: 'measure:' + bar + ':' + index, bar: Number(bar), markIndex: index, staff: 0, pos: Number(bar) * this.barCapacity(), step: 10, label: mark.name || 'Measure mark' })));
    return out.sort((a,b) => a.pos - b.pos || a.staff - b.staff || a.label.localeCompare(b.label));
  }
  openScoreObjectSelector() {
    const objects = this.scoreSelectableObjects();
    this.rumble('tick');
    this.setState({ panel: 'score-object-selector', panelIdx: 0, halo: false, hub: false, menu: false, spoken: objects.length ? 'Score object selector — ' + objects.length + ' selectable objects' : 'Score object selector — the score is empty' });
  }
  selectLogicalScoreObject(item) {
    if (!item) return;
    if (item.kind === 'score-event' || item.kind === 'score-span' || item.kind === 'span-start' || item.kind === 'span-end') {
      this.selectScoreObject(item.scoreObjectId);
      return this.setState({ panel: null, selectedChordHead: null, spoken: item.label + ' selected — arrows move it, A edits, B deletes' });
    }
    if (item.kind === 'chord-head') {
      const n = this.state.notes.find(x => x.id === item.noteId);
      if (n) this.selectNote(n);
      return this.setState({ panel: null, selectedChordHead: { noteId: item.noteId, index: item.headIndex }, step: item.step, spoken: item.label + ' selected individually — up and down move it, B removes it' });
    }
    if (item.kind === 'note' || item.kind === 'rest' || item.kind === 'note-mark') {
      const n = this.state.notes.find(x => x.id === item.noteId);
      if (n) this.selectNote(n);
      return this.setState({ panel: null, selectedChordHead: null, spoken: item.label + ' selected' });
    }
    if (item.kind === 'chord-symbol') return this.setState({ panel: 'chordsym', panelIdx: 0, chordIdx: item.chordIndex, pos: item.pos, spoken: item.label + ' selected' });
    if (item.kind === 'measure-mark') return this.setState({ panel: null, staff: 0, pos: item.pos, selectedChordHead: null, spoken: item.label + ' selected at bar ' + (item.bar + 1) });
  }
  chordHeadSteps(note) { return [note.step].concat((note.chord || []).map(x => note.step + x)).sort((a,b) => a-b); }
  rewriteChordHeads(noteId, steps, selectedStep) {
    const uniq = Array.from(new Set(steps)).sort((a,b) => a-b);
    if (!uniq.length) return this.setState(s => ({ notes: s.notes.filter(n => n.id !== noteId), selId: null, selectedChordHead: null, spoken: 'Chord deleted' }));
    const base = uniq[0], offsets = uniq.slice(1).map(x => x - base), idx = Math.max(0, uniq.indexOf(selectedStep));
    this.setState(s => ({ notes: s.notes.map(n => n.id === noteId ? Object.assign({}, n, { step: base, chord: offsets }) : n), step: selectedStep, selectedChordHead: { noteId: noteId, index: idx }, spoken: this.pitchName(selectedStep, (s.notes.find(n => n.id === noteId) || {}).s || 0) + ' chord note selected' }));
  }
  moveSelectedChordHead(delta) {
    const pick = this.state.selectedChordHead;
    if (!pick) return false;
    const note = this.state.notes.find(n => n.id === pick.noteId);
    if (!note) return false;
    const steps = this.chordHeadSteps(note), old = steps[Math.max(0, Math.min(steps.length - 1, pick.index))], moved = Math.max(-6, Math.min(22, old + delta));
    steps[pick.index] = moved;
    this.rewriteChordHeads(note.id, steps, moved);
    this.audition(moved, note.s, note.acc, note.art, note);
    return true;
  }
  deleteSelectedChordHead() {
    const pick = this.state.selectedChordHead;
    if (!pick) return false;
    const note = this.state.notes.find(n => n.id === pick.noteId);
    if (!note) return false;
    const steps = this.chordHeadSteps(note);
    if (steps.length === 1) { this.deleteNote(); this.setState({ selectedChordHead: null }); return true; }
    const removed = steps.splice(Math.max(0, Math.min(steps.length - 1, pick.index)), 1)[0];
    this.rewriteChordHeads(note.id, steps, steps[Math.max(0, Math.min(steps.length - 1, pick.index - 1))]);
    this.setState({ spoken: this.pitchName(removed, note.s) + ' removed from the chord' });
    return true;
  }
  noteMidi(note, state) {
    const s = state || this.state, clef = this.clefAt(note.s, note.p, s), key = this.keyAt(note.p, s);
    if (note.accCents != null && isFinite(Number(note.accCents))) {
      return midiFor(note.step, clef === 'bass', '\uE261', key, (s.clefOctaves || [])[note.s]) + Number(note.accCents) / 100;
    }
    return midiFor(note.step, clef === 'bass', note.acc, key, (s.clefOctaves || [])[note.s]);
  }
  articulationPlayback(note) {
    const p = note && note.artPlayback, name = ((p && (p.profile || p.label || p.id)) || '').toLowerCase();
    const glyph = note && note.art;
    if (/staccatissimo/.test(name)) return { length: .28, gain: .95, attack: .65 };
    if (/staccato/.test(name) || glyph === '\uE4A2') return { length: .48, gain: 1, attack: .8 };
    if (/tenuto/.test(name) || glyph === '\uE4A4') return { length: 1.04, gain: 1.02, attack: .9 };
    if (/marcato/.test(name)) return { length: .82, gain: 1.38, attack: 1.35 };
    if (/accent|stress/.test(name) || glyph === '\uE4A0') return { length: .9, gain: 1.25, attack: 1.22 };
    if (/portato/.test(name)) return { length: .72, gain: 1.06, attack: .95 };
    if (/unstress/.test(name)) return { length: .92, gain: .78, attack: .72 };
    return { length: .96, gain: 1, attack: 1 };
  }
  activeTechnique(staff, pos, state) {
    const s = state || this.state;
    return (s.scoreEvents || []).filter(x => x.p <= pos + .0005 && !x.system && x.s === staff && (x.type === 'technique' || (x.playback && x.playback.kind === 'technique'))).sort((a,b) => b.p-a.p)[0] || null;
  }
  techniqueInstrument(staff, pos, note, state) {
    const s = state || this.state, base = s.instruments[staff] || 'acoustic_grand_piano';
    const ev = this.activeTechnique(staff, pos, s), p = (note && note.techniquePlayback) || (ev && ev.playback) || {}, tech = String(p.technique || p.sound || '').toLowerCase();
    if (/pizz/.test(tech) && /violin|viola|cello|contrabass|string|fiddle/.test(base)) return 'pizzicato_strings';
    if (/tremolo/.test(tech) && /violin|viola|cello|contrabass|string|fiddle/.test(base)) return 'tremolo_strings';
    if (/muted/.test(tech) && /trumpet|trombone|horn|brass/.test(base)) return 'muted_trumpet';
    if (/harmonic/.test(tech) && /guitar/.test(base)) return 'guitar_harmonics';
    if (/muted/.test(tech) && /guitar/.test(base)) return 'electric_guitar_muted';
    return base;
  }
'''
insert_before('  haloApply() {', methods, 'catalog and selector methods')

# Preserve semantic metadata in events/spans.
replace_once(
"      const ev = { id: editing || this.scoreId('e'), object: 'event', type: type, name: name, text: opts.text || name, glyph: glyph || '', value: value, s: anchor.s, p: anchor.p, step: anchor.step, system: system };",
"      const ev = Object.assign({ id: editing || this.scoreId('e'), object: 'event', type: type, name: name, text: opts.text || name, glyph: glyph || '', value: value, s: anchor.s, p: anchor.p, step: anchor.step, system: system }, opts.meta ? { smufl: opts.meta.id || null, range: opts.meta.range || null, playback: opts.meta } : {});",
    'event semantic metadata'
)
replace_once('  beginScoreSpan(type, name, glyph, editing) {', '  beginScoreSpan(type, name, glyph, editing, meta) {', 'span metadata signature')
replace_once(
"    this.setState({ spanDraft: { object: 'span', id: editing || this.scoreId('s'), editing: editing || null, type: type, name: name, glyph: glyph || '', s1: start.s, p1: start.p, step1: start.step, system: type === 'ending' || type.indexOf('tempo-') === 0 },",
"    this.setState({ spanDraft: Object.assign({ object: 'span', id: editing || this.scoreId('s'), editing: editing || null, type: type, name: name, glyph: glyph || '', s1: start.s, p1: start.p, step1: start.step, system: type === 'ending' || type.indexOf('tempo-') === 0 }, meta ? { smufl: meta.id || null, range: meta.range || null, playback: meta } : {}),",
    'span semantic metadata'
)

# Route generated entries through semantics while preserving all existing curated behavior.
replace_once(
"    const s = this.state, cat = CAT[s.haloCat][0], cmd = CAT[s.haloCat][1][s.haloIdx], name = cmd[0], glyph = cmd[1];\n    const lower = name.toLowerCase();",
"    const s = this.state, shownCat = CAT[s.haloCat][0], cmd = CAT[s.haloCat][1][s.haloIdx], name = cmd[0], glyph = cmd[1], meta = cmd[2] || {}, cat = meta.legacyCategory || shownCat;\n    if (meta.catalog) return this.applyCatalogCommand(meta, name, glyph);\n    const lower = name.toLowerCase();",
    'catalog command dispatch'
)

# Logical selector rows use the existing fully controller-accessible panel.
insert_before(
"    if (s.panel === 'score-clef')",
"    if (s.panel === 'score-object-selector') return this.scoreSelectableObjects(s).map(item => ({ label: item.label, value: item.kind.replace(/-/g, ' ').toUpperCase(), act: () => this.selectLogicalScoreObject(item) }));\n",
    'selector panel rows'
)

# Dedicated selector rendering actions.
replace_once(
"      openNotation: () => this.setState({ halo: true, haloCat: 5, haloIdx: 0, spoken: 'Add music at the cursor — choose a category and press A' }),\n      notationButtonStyle:",
"      openNotation: () => this.setState({ halo: true, haloCat: 0, haloIdx: 0, spoken: 'Add music — Popular first, then every SMuFL and Bravura range' }),\n      openScoreSelector: () => this.openScoreObjectSelector(),\n      scoreSelectorButtonStyle: 'display:flex;align-items:center;justify-content:center;gap:5px;flex:0 0 auto;min-height:38px;padding:3px 10px;border-radius:4px;cursor:pointer;font-family:\\'IBM Plex Mono\\',monospace;font-size:9.5px;font-weight:700;letter-spacing:.05em;border:1px solid var(--border-strong);background:var(--control);color:var(--text);',\n      notationButtonStyle:",
    'selector render props'
)
replace_once("hint: 'Every notation symbol, 11 categories'", "hint: 'Popular first, then every official SMuFL and Bravura range'", 'hub complete library label')

# Apply selector behavior before normal note movement/deletion.
replace_once(
"    if (s.spanDraft && action === 'confirm') return this.finishScoreSpan();",
"    if (s.selectedChordHead && action === 'move-up') return this.moveSelectedChordHead(1);\n    if (s.selectedChordHead && action === 'move-down') return this.moveSelectedChordHead(-1);\n    if (s.selectedChordHead && action === 'delete') return this.deleteSelectedChordHead();\n    if (s.spanDraft && action === 'confirm') return this.finishScoreSpan();",
    'chord head controller priority'
)

# Clear exact chord-head state whenever ordinary note/object selection changes.
replace_once("this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step,", "this.setState({ selId: n.id, scoreObjectId: null, selectedChordHead: null, staff: n.s, pos: n.p, step: n.step,", 'ordinary note clears chord head')
replace_once("this.setState({ zone: 3, scoreObjectId: id, selId: null, range: null,", "this.setState({ zone: 3, scoreObjectId: id, selId: null, selectedChordHead: null, range: null,", 'object clears chord head')

# New notes inherit all semantic properties armed by the complete library.
replace_once(
"      const n = Object.assign({}, s.armed, { id: 'n' + Math.random().toString(36).slice(2, 8), s: s.staff, p: s.pos, d: DURS[s.dur].id, step: s.step, voice: s.voice, rest: s.entry === 'rest', dots: s.dots, acc: s.acc === 'n' ? null : (s.acc === 'f' ? SM.flat : SM.sharp) });",
"      const n = Object.assign({ id: 'n' + Math.random().toString(36).slice(2, 8), s: s.staff, p: s.pos, d: DURS[s.dur].id, step: s.step, voice: s.voice, rest: s.entry === 'rest', dots: s.dots, acc: s.acc === 'n' ? null : (s.acc === 'f' ? SM.flat : SM.sharp) }, s.armed || {});",
    'semantic note entry'
)

# Render complete notehead and accidental glyphs.
replace_once("          const headGlyph = HEAD_GLYPH[n.d] || '\\uE0A4';", "          const headGlyph = n.noteheadGlyph || HEAD_GLYPH[n.d] || '\\uE0A4';", 'custom notehead rendering')
replace_once("             acc: n.acc ? (n.acc === 'f' ? SM.flat : n.acc === 'sh' ? SM.sharp : n.acc) : '',", "             acc: n.accSmufl ? (n.acc || '') : (n.acc ? (n.acc === 'f' ? SM.flat : n.acc === 'sh' ? SM.sharp : n.acc) : ''),", 'complete accidental rendering')

# Render generic catalog events as their glyphs in Bravura rather than plain text.
replace_once(
"        else if (ev.type === 'technique') { top = st.top + 63; extra = 'font-style:italic;font-weight:600;'; }",
"        else if (ev.type === 'technique') { top = st.top + 63; extra = 'font-style:italic;font-weight:600;'; }\n        else if (ev.type === 'glyph' || ev.type === 'meter-glyph') { text2 = ev.glyph || ev.text || ev.name; family = 'Bravura,\\'Noto Music\\',serif'; size = ev.type === 'meter-glyph' ? 31 : 27; top = ev.type === 'meter-glyph' ? st.top + 3 : st.top - 28; extra = ''; }",
    'generic catalog glyph rendering'
)

# Fractional pitch and technique-aware audition/playback.
replace_once(
"    const ac = this.audio(), midi = midiFor(step, this.clefAt(staff, at) === 'bass', acc, this.keyAt(at), (this.state.clefOctaves || [])[staff]);",
"    const ac = this.audio(), midi = note ? this.noteMidi(Object.assign({}, note, { step: step, acc: acc }), this.state) : midiFor(step, this.clefAt(staff, at) === 'bass', acc, this.keyAt(at), (this.state.clefOctaves || [])[staff]);",
    'fractional audition pitch'
)
replace_once(
"      const clef = this.clefAt(n.s, n.p, s), key = this.keyAt(n.p, s);\n      let m = midiFor(n.step, clef === 'bass', n.acc, key, (s.clefOctaves || [])[n.s]);",
"      const clef = this.clefAt(n.s, n.p, s), key = this.keyAt(n.p, s);\n      let m = this.noteMidi(n, s);",
    'fractional playback pitch'
)
replace_once(
"      const decorated = ORN_REPLACES[n.orn];\n      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : .96), n.s, decorated ? vel * .8 : vel, n.art);",
"      const decorated = ORN_REPLACES[n.orn] || n.ornPlayback || n.tremoloPlayback || n.pitchPlayback;\n      const ap = this.articulationPlayback(n);\n      const originalInstrument = s.instruments[n.s], semanticInstrument = this.techniqueInstrument(n.s, n.p, n, s);\n      if (semanticInstrument !== originalInstrument) s.instruments[n.s] = semanticInstrument;\n      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : ap.length), n.s, (decorated ? vel * .8 : vel) * ap.gain, n.art);\n      if (semanticInstrument !== originalInstrument) s.instruments[n.s] = originalInstrument;",
    'semantic articulation and technique playback'
)

# Generic ornament/tremolo/pitch-effect playback when a glyph is not in the old switch.
insert_before(
"    if (n.tie) return;",
r'''    const semantic = n.ornPlayback || n.tremoloPlayback || n.pitchPlayback || n.techniquePlayback;
    if (semantic) {
      const pattern = String(semantic.pattern || semantic.effect || semantic.sound || '').toLowerCase();
      if (/mordent-down/.test(pattern)) rep([dnStep, 0], .07);
      else if (/mordent/.test(pattern)) rep([upStep, 0], .07);
      else if (/turn-inverted/.test(pattern)) rep([dnStep, 0, upStep, 0], .07);
      else if (/turn/.test(pattern)) rep([upStep, 0, dnStep, 0], .07);
      else if (/trill|shake/.test(pattern)) trill(/shake/.test(pattern) ? upStep + 1 : upStep, tN, tStep);
      else if (/tremolo/.test(pattern) || semantic.kind === 'tremolo') {
        const strokes = Math.max(1, Number(semantic.strokes) || 1), step = strokes >= 3 ? .055 : strokes === 2 ? .085 : .13;
        for (let k = 1; k * step < dur; k++) this.playTone(m, when + k * step, step * 1.15, staff, v * .82, null);
      } else if (/scoop|plop/.test(pattern)) run(/scoop/.test(pattern) ? -4 : 4, /scoop/.test(pattern) ? 0 : 0, when - .12, .03, .65);
      else if (/fall|rip/.test(pattern)) run(-1, /rip/.test(pattern) ? -10 : -5, when + dur * .5, .03, .65);
      else if (/doit|lift/.test(pattern)) run(1, 6, when + dur * .5, .03, .68);
      else if (/bend|smear|flip|slide/.test(pattern)) [0,1,2,1,0].forEach((p,i) => this.playTone(m+p, when+i*(dur/5), dur/4, staff, v*.85, null));
    }
''',
    'generic semantic ornament playback'
)

# Hairpins and explicit dynamic events can use generated velocity metadata.
replace_once(
"      const dynEv = this.effectiveScoreEvent('dynamic', n.s, n.p, s), dynGlyph = n.dyn || (dynEv && (dynEv.glyph || dynEv.value));\n      let vel = Math.round(dynGlyph && dynMap[dynGlyph] ? dynMap[dynGlyph] : 40 + (s.vel / 100) * 87);",
"      const dynEv = this.effectiveScoreEvent('dynamic', n.s, n.p, s), dynGlyph = n.dyn || (dynEv && (dynEv.glyph || dynEv.value));\n      let vel = Math.round(dynEv && dynEv.playback && dynEv.playback.velocity != null ? dynEv.playback.velocity : (dynGlyph && dynMap[dynGlyph] ? dynMap[dynGlyph] : 40 + (s.vel / 100) * 87));",
    'generated dynamic playback'
)

# Holds alter real timing, not only appearance.
insert_before(
"      const decorated = ORN_REPLACES[n.orn] || n.ornPlayback || n.tremoloPlayback || n.pitchPlayback;",
r'''      const hold = (s.scoreEvents || []).filter(ev => ev.type === 'hold' && !ev.system && ev.s === n.s && Math.abs(ev.p - n.p) < .011).sort((a,b) => b.p-a.p)[0];
      if (hold && hold.playback) {
        if (hold.playback.sound === 'fermata') duration *= Math.max(1, Number(hold.playback.factor) || 2);
        else duration += Math.max(0, Number(hold.playback.seconds) || 0);
      }
''',
    'hold playback timing'
)

# Tie validation must compare fractional semantic pitch.
replace_once(
"    const startMidi = midiFor(start.step, this.state.clefs[start.s] === 'bass', start.acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[start.s]);\n    const targetMidi = midiFor(target.step, this.state.clefs[target.s] === 'bass', target.acc, KEYS[this.state.keyIdx], (this.state.clefOctaves || [])[target.s]);",
"    const startMidi = this.noteMidi(start, this.state);\n    const targetMidi = this.noteMidi(target, this.state);",
    'semantic tie pitch'
)

# MIDI cannot encode arbitrary per-note pitch without bends in this compact writer; round only at export while live playback stays microtonal.
replace_once(
"        let midi = midiFor(n.step, clef === 'bass', n.acc, key, (s.clefOctaves || [])[i]);",
"        let midi = this.noteMidi(n, s);",
    'semantic MIDI source pitch'
)

# Selection/status copy and recovery state.
replace_once(
"selectionCount: s.spanDraft ? 'CHOOSE POINT TWO' : s.tieFrom ? 'CHOOSE TIE END' : (s.scoreObjectId ? 'MUSIC OBJECT SELECTED' : s.selId ? 'NOTE SELECTED' : 'CURSOR'),",
"selectionCount: s.spanDraft ? 'CHOOSE POINT TWO' : s.tieFrom ? 'CHOOSE TIE END' : (s.selectedChordHead ? 'CHORD NOTE SELECTED' : s.scoreObjectId ? 'MUSIC OBJECT SELECTED' : s.selId ? 'NOTE SELECTED' : 'CURSOR'),",
    'selector status'
)
replace_once("notes: [], scoreEvents: [], scoreSpans: [], selId: null, scoreObjectId: null, spanDraft: null,", "notes: [], scoreEvents: [], scoreSpans: [], selId: null, scoreObjectId: null, selectedChordHead: null, spanDraft: null,", 'new project selector reset')

# Guard protected controls and exact complete-library markers.
required = [
    "button4: 'previous-zone', button5: 'next-zone'",
    'const BUMPER_COMBO_MS = 120;',
    "case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;",
    "case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;",
    'window.LEGATO_SMUFL_CATALOG',
    'scoreSelectableObjects(state)',
    'applyCatalogCommand(meta, name, glyph)',
    'noteMidi(note, state)',
    NEW_BUILD,
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing guarded marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Complete SMuFL catalog, semantic placement, playback, and selector integration applied')
