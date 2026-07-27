from pathlib import Path

source = Path('tools/apply_semantic_playback_corrections_v2.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/apply_semantic_playback_corrections_v2.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once(
"    if (meta.kind === 'electronic') {\n      this.placeScoreEvent('electronic', name, glyph, meta.electronic || name, { system: true, text: glyph || name, meta: playback });\n      return;\n    }",
"    if (meta.kind === 'electronic') {\n      this.placeScoreEvent('electronic', name, glyph, meta.electronic || name, { system: true, text: glyph || name, meta: playback });\n      return;\n    }\n    if (meta.kind === 'pedal' && meta.placement === 'event') {\n      this.placeScoreEvent('pedal-event', name, glyph, meta.state || name, { system: false, text: glyph || name, meta: playback });\n      return;\n    }",
'standalone pedal placement')

replace_once(
"    return base + localOctave;\n  }",
"    const harmonicShift = note.noteheadPlayback && note.noteheadPlayback.sound === 'harmonic' ? 12 : 0;\n    return base + localOctave + harmonicShift;\n  }",
'harmonic notehead pitch')

replace_once(
"    const p = (note && note.techniquePlayback) || (ev && ev.playback) || {};",
"    const p = (note && (note.techniquePlayback || note.noteheadPlayback)) || (ev && ev.playback) || {};",
'notehead playback profile source')
replace_once(
"    if (/harmonic/.test(tech)) return { length: .92, gain: .72 };\n    return { length: 1, gain: 1 };",
"    if (/harmonic/.test(tech)) return { length: .92, gain: .72 };\n    if (p.audible && /^(technique|bowing)$/.test(String(p.kind || ''))) return { length: .86, gain: .88 };\n    return { length: 1, gain: 1 };",
'generic audible technique profile')
replace_once(
"    const ev = this.activeTechnique(staff, pos, s), p = (note && note.techniquePlayback) || (ev && ev.playback) || {}, tech = String(p.technique || p.sound || '').toLowerCase();",
"    const ev = this.activeTechnique(staff, pos, s), p = (note && (note.techniquePlayback || note.noteheadPlayback)) || (ev && ev.playback) || {}, tech = String(p.technique || p.sound || '').toLowerCase();",
'notehead technique sample source')
replace_once(
"    if (/muted/.test(tech) && /trumpet|trombone|horn|brass/.test(base)) return 'muted_trumpet';",
"    if (/harmon-open|harmon-closed/.test(tech)) return 'muted_trumpet';\n    if (/muted/.test(tech) && /trumpet|trombone|horn|brass/.test(base)) return 'muted_trumpet';",
'harmon mute sample routing')
replace_once(
"    if (/muted/.test(tech)) return { length: .72, gain: .68 };",
"    if (/harmon-open/.test(tech)) return { length: .9, gain: .78 };\n    if (/harmon-closed/.test(tech)) return { length: .68, gain: .58 };\n    if (/muted/.test(tech)) return { length: .72, gain: .68 };",
'harmon mute playback profiles')

insert = r'''  activePedalEvent(staff, pos, state) {
    const s = state || this.state;
    return (s.scoreEvents || []).filter(x => x.type === 'pedal-event' && x.s === staff && x.p <= pos + .0005).sort((a,b) => b.p-a.p)[0] || null;
  }
  nextPedalRelease(staff, pos, state) {
    const s = state || this.state;
    const next = (s.scoreEvents || []).filter(x => x.type === 'pedal-event' && x.s === staff && x.p > pos + .0005 && x.playback && x.playback.state === 'off').sort((a,b) => a.p-b.p)[0];
    return next ? next.p : null;
  }
'''
replace_once('  activeElectronic(pos, state) {', insert + '  activeElectronic(pos, state) {', 'pedal event helpers')

replace_once(
"      const slur = this.activeScoreSpan(['slur', 'phrase', 'let-ring'], n.s, n.p, s), pedal = this.activeScoreSpan('pedal', n.s, n.p, s);\n      let duration = this.secondsBetween(n.p, n.p + beats, s);\n      if (pedal) duration = Math.max(duration, this.secondsBetween(n.p, Math.max(n.p + beats, Math.max(pedal.p1, pedal.p2)), s));\n      else if (slur) duration *= 1.08;",
"      const slur = this.activeScoreSpan(['slur', 'phrase', 'let-ring'], n.s, n.p, s), pedalSpan = this.activeScoreSpan('pedal', n.s, n.p, s), pedalEvent = this.activePedalEvent(n.s, n.p, s);\n      const pedalOn = pedalEvent && pedalEvent.playback && pedalEvent.playback.state !== 'off';\n      let duration = this.secondsBetween(n.p, n.p + beats, s);\n      if (pedalSpan) duration = Math.max(duration, this.secondsBetween(n.p, Math.max(n.p + beats, Math.max(pedalSpan.p1, pedalSpan.p2)), s));\n      else if (pedalOn) { const release = this.nextPedalRelease(n.s, n.p, s); duration = Math.max(duration, this.secondsBetween(n.p, release == null ? Math.min(s.bars * this.barCapacity(), n.p + this.barCapacity()) : release, s)); }\n      else if (slur) duration *= 1.08;",
'standalone pedal sustain')

replace_once(
"        else if (ev.type === 'glyph' || ev.type === 'meter-glyph' || ev.type === 'electronic') {",
"        else if (ev.type === 'glyph' || ev.type === 'meter-glyph' || ev.type === 'electronic' || ev.type === 'pedal-event') {",
'pedal event glyph rendering')

required = [
    "if (meta.kind === 'pedal' && meta.placement === 'event')",
    'harmonicShift',
    'activePedalEvent(staff, pos, state)',
    'nextPedalRelease(staff, pos, state)',
    'pedalOn',
    '/harmon-open|harmon-closed/.test(tech)',
    "button4: 'previous-zone', button5: 'next-zone'",
    'const BUMPER_COMBO_MS = 120;'
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing final semantic playback marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Applied harmonic notehead, mute-variant, and standalone pedal playback')
