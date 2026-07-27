from pathlib import Path
import re

p = Path('index.html')
t = p.read_text(encoding='utf-8')


def one(old, new, label):
    global t
    count = t.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    t = t.replace(old, new, 1)


def sub(pattern, replacement, label):
    global t
    t2, count = re.subn(pattern, lambda _m: replacement, t, count=1, flags=re.M)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    t = t2

if '20260727-notation-objects-2' in t:
    print('Notation lifecycle follow-up already applied')
    raise SystemExit(0)

if t.count('20260727-notation-objects-1') != 3:
    raise SystemExit('Expected three notation-objects-1 build markers')
t = t.replace('20260727-notation-objects-1', '20260727-notation-objects-2')

one("kb: 'scoreObjectText', kbIdx: 0, scoreText:", "kb: 'scoreText', kbIdx: 0, scoreText:", 'text editor field')
one("if (s.kb === 'scoreObjectText') return this.finishScoreObjectText();", "if (s.kb === 'scoreText') return this.finishScoreObjectText();", 'text editor done action')

one(
"      this.setState(Object.assign({}, snap.doc, {\n        selId: null, recovery: null,",
"      this.setState(Object.assign({ scoreEvents: [], scoreSpans: [] }, snap.doc, {\n        selId: null, scoreObjectId: null, spanDraft: null, recovery: null,",
'legacy recovery defaults')
one(
"        this.setState(Object.assign({}, data.doc, { selId: null, spoken: 'Opened ' + file.name }), () => { this._prevDocStr = JSON.stringify(this.doc()); this._restoring = false; });",
"        this.setState(Object.assign({ scoreEvents: [], scoreSpans: [] }, data.doc, { selId: null, scoreObjectId: null, spanDraft: null, spoken: 'Opened ' + file.name }), () => { this._prevDocStr = JSON.stringify(this.doc()); this._restoring = false; });",
'legacy project defaults')
one(
"      notes: [], selId: null, title: 'Untitled score', composer: '', keyIdx: 0, meter: 0, tempo: 100,",
"      notes: [], scoreEvents: [], scoreSpans: [], selId: null, scoreObjectId: null, spanDraft: null, title: 'Untitled score', composer: '', keyIdx: 0, meter: 0, tempo: 100,",
'new project notation reset')

one(
"        const keep = s.notes.filter(n => n.p < (s.bars - 1) * this.barCapacity());\n        return { bars: s.bars - 1, notes: keep, selId: null, spoken: 'Last measure removed' };",
"        const end = (s.bars - 1) * this.barCapacity();\n        const keep = s.notes.filter(n => n.p < end);\n        return { bars: s.bars - 1, notes: keep, scoreEvents: (s.scoreEvents || []).filter(x => x.p < end), scoreSpans: (s.scoreSpans || []).filter(x => Math.min(x.p1, x.p2) < end).map(x => Object.assign({}, x, { p1: Math.min(x.p1, end - .001), p2: Math.min(x.p2, end - .001) })), selId: null, scoreObjectId: null, spanDraft: null, spoken: 'Last measure removed' };",
'remove measure notation cleanup')

sub(
 r"  removePlayer\(i\) \{[\s\S]*?\n  \}\n  addToGrandStaff\(i\) \{",
 r'''  removePlayer(i) {
    this.setState(s => {
      if (s.players.length <= 1) return { spoken: 'A score needs at least one player' };
      const players = s.players.filter((p, j) => j !== i);
      syncStaves(players);
      const shift = x => x > i ? x - 1 : x;
      return {
        players: players,
        clefs: s.clefs.filter((c, j) => j !== i),
        clefOctaves: (s.clefOctaves || s.clefs.map(() => 0)).filter((c, j) => j !== i),
        instruments: s.instruments.filter((c, j) => j !== i),
        mix: s.mix.filter((c, j) => j !== i),
        notes: s.notes.filter(n => n.s !== i).map(n => n.s > i ? Object.assign({}, n, { s: n.s - 1 }) : n),
        scoreEvents: (s.scoreEvents || []).filter(x => x.system || x.s !== i).map(x => x.system ? x : Object.assign({}, x, { s: shift(x.s) })),
        scoreSpans: (s.scoreSpans || []).filter(x => x.system || (x.s1 !== i && x.s2 !== i)).map(x => x.system ? x : Object.assign({}, x, { s1: shift(x.s1), s2: shift(x.s2) })),
        staff: Math.max(0, Math.min(players.length - 1, s.staff > i ? s.staff - 1 : s.staff)),
        selId: null, scoreObjectId: null, spanDraft: null,
        spoken: (s.players[i] ? s.players[i].name : 'Player') + ' removed'
      };
    });
    this.rumble('firm');
  }
  addToGrandStaff(i) {''',
'remove player notation cleanup')

one(
"        notes: s.notes.map(n => n.s > i ? Object.assign({}, n, { s: n.s + 1 }) : n),\n        spoken: 'Second staff added to ' + src.name",
"        notes: s.notes.map(n => n.s > i ? Object.assign({}, n, { s: n.s + 1 }) : n),\n        scoreEvents: (s.scoreEvents || []).map(x => !x.system && x.s > i ? Object.assign({}, x, { s: x.s + 1 }) : x),\n        scoreSpans: (s.scoreSpans || []).map(x => x.system ? x : Object.assign({}, x, { s1: x.s1 > i ? x.s1 + 1 : x.s1, s2: x.s2 > i ? x.s2 + 1 : x.s2 })),\n        spoken: 'Second staff added to ' + src.name",
'grand staff notation shift')

# MIDI tempo map and position-aware pitches/octave spans.
sub(
 r"  exportMidi\(\) \{[\s\S]*?\n  \}\n  runOp\(name\) \{",
 r'''  exportMidi() {
    const s = this.state, PPQ = 480;
    const vlq = n => { const bytes = [n & 127]; n >>= 7; while (n > 0) { bytes.unshift((n & 127) | 128); n >>= 7; } return bytes; };
    const str = t => t.split('').map(c => c.charCodeAt(0) & 127);
    const chunk = (id, data) => str(id).concat([(data.length >> 24) & 255, (data.length >> 16) & 255, (data.length >> 8) & 255, data.length & 255], data);
    const tracks = [];
    const tempoEvents = [{ p: 0, value: s.tempo }].concat((s.scoreEvents || []).filter(x => x.type === 'tempo')).sort((a, b) => a.p - b.p);
    let tempoData = [], tempoLast = 0;
    tempoEvents.forEach(ev => {
      const tick = Math.max(0, Math.round(ev.p * PPQ)), us = Math.round(60000000 / Math.max(20, Number(ev.value) || s.tempo));
      tempoData = tempoData.concat(vlq(tick - tempoLast), [255, 81, 3, (us >> 16) & 255, (us >> 8) & 255, us & 255]); tempoLast = tick;
    });
    tempoData = tempoData.concat(vlq(0), [255, 47, 0]);
    tracks.push(chunk('MTrk', tempoData));
    STAVES.forEach((st, i) => {
      const events = [];
      s.notes.filter(n => n.s === i && !n.rest).forEach(n => {
        const beats = noteBeats(n), on = Math.round(n.p * PPQ), off = Math.round((n.p + beats * .96) * PPQ);
        const clef = this.clefAt(i, n.p, s), key = this.keyAt(n.p, s), oct = this.activeScoreSpan(['octave-up', 'octave-down', 'octave-up-2', 'octave-down-2'], i, n.p, s);
        let midi = midiFor(n.step, clef === 'bass', n.acc, key, (s.clefOctaves || [])[i]);
        if (oct) midi += oct.type === 'octave-up' ? 12 : oct.type === 'octave-down' ? -12 : oct.type === 'octave-up-2' ? 24 : -24;
        events.push({ t: on, d: [144 + Math.min(15, i), Math.max(0, Math.min(127, midi)), n.art === '\uE4A0' ? 108 : 88] });
        events.push({ t: off, d: [128 + Math.min(15, i), Math.max(0, Math.min(127, midi)), 0] });
      });
      events.sort((a, b) => a.t - b.t);
      let last = 0, data = vlq(0).concat([255, 3, st.name.length], str(st.name));
      events.forEach(ev => { data = data.concat(vlq(ev.t - last), ev.d); last = ev.t; });
      data = data.concat(vlq(0), [255, 47, 0]);
      tracks.push(chunk('MTrk', data));
    });
    const header = chunk('MThd', [0, 1, 0, tracks.length, (PPQ >> 8) & 255, PPQ & 255]);
    let all = header; tracks.forEach(track => { all = all.concat(track); });
    this.download(this.fileBase() + '.mid', 'audio/midi', new Uint8Array(all));
    this.setState({ spoken: 'MIDI exported — tempo changes and position-aware pitches included' });
  }
  runOp(name) {''',
'position-aware MIDI export')

# Use the active key for realised ornaments.
one(
"    const K = KEYS[this.state.keyIdx] || KEYS[0];",
"    const K = this.keyAt(n.p == null ? this.state.pos : n.p) || KEYS[0];",
'ornament active key')

# A glissando must use a valid CSS line style.
one("border-top:1.5px ' + (sp.type === 'gliss' ? 'wavy' : 'solid') + ' '", "border-top:1.5px solid ", 'glissando line CSS')

for marker in [
    '20260727-notation-objects-2',
    "kb: 'scoreText'",
    'scoreEvents: [], scoreSpans: []',
    'tempo changes and position-aware pitches included',
    'scoreEvents: (s.scoreEvents || []).filter(x => x.p < end)',
    'scoreSpans: (s.scoreSpans || []).filter(x => x.system || (x.s1 !== i && x.s2 !== i))'
]:
    if marker not in t:
        raise SystemExit('Missing follow-up marker: ' + marker)

p.write_text(t, encoding='utf-8')
print('Notation lifecycle follow-up applied')
