from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)


replace_once('20260727-complete-smufl-playback-1', '20260727-complete-smufl-playback-2', 'build and cache version')

replace_once(
"    if (meta.kind === 'hairpin') return meta.direction === 'down' ? 'hairpin-down' : 'hairpin-up';",
"    if (meta.kind === 'hairpin') return meta.direction === 'swell' ? 'hairpin-swell' : (meta.direction === 'down' ? 'hairpin-down' : 'hairpin-up');",
'catalog swell hairpin type')

replace_once(
"    if (meta.kind === 'dynamic' || meta.kind === 'hold') {\n      this.placeScoreEvent(meta.kind, name, glyph, glyph, { system: false, meta: playback });\n      return;\n    }",
"    if (meta.kind === 'dynamic' || meta.kind === 'hold') {\n      this.placeScoreEvent(meta.kind, name, glyph, glyph, { system: false, meta: playback });\n      return;\n    }\n    if (meta.kind === 'electronic') {\n      this.placeScoreEvent('electronic', name, glyph, meta.electronic || name, { system: true, text: glyph || name, meta: playback });\n      return;\n    }",
'electronic event placement')

replace_once(
"    if (meta.placement === 'note' || /^(notehead|accidental|articulation|ornament|tremolo|pitch-effect|technique|bowing|percussion)$/.test(meta.kind)) {",
"    if (meta.placement === 'note' || /^(notehead|accidental|articulation|ornament|grace|tremolo|pitch-effect|technique|bowing|percussion)$/.test(meta.kind)) {",
'grace note command routing')
replace_once(
"      else if (meta.kind === 'ornament') { patch.orn = glyph; patch.ornPlayback = playback; }\n      else if (meta.kind === 'tremolo')",
"      else if (meta.kind === 'ornament' || meta.kind === 'grace') { patch.orn = glyph; patch.ornPlayback = playback; }\n      else if (meta.kind === 'tremolo')",
'grace playback attachment')

replace_once(
"  noteMidi(note, state) {\n    const s = state || this.state, clef = this.clefAt(note.s, note.p, s), key = this.keyAt(note.p, s);\n    if (note.accCents != null && isFinite(Number(note.accCents))) {\n      return midiFor(note.step, clef === 'bass', '\\uE261', key, (s.clefOctaves || [])[note.s]) + Number(note.accCents) / 100;\n    }\n    return midiFor(note.step, clef === 'bass', note.acc, key, (s.clefOctaves || [])[note.s]);\n  }",
"  noteMidi(note, state) {\n    const s = state || this.state, clef = this.clefAt(note.s, note.p, s), key = this.keyAt(note.p, s);\n    const clefEvent = this.effectiveScoreEvent('clef', note.s, note.p, s);\n    const localOctave = clefEvent && clefEvent.playback ? Number(clefEvent.playback.semitones) || 0 : 0;\n    const base = note.accCents != null && isFinite(Number(note.accCents))\n      ? midiFor(note.step, clef === 'bass', '\\uE261', key, (s.clefOctaves || [])[note.s]) + Number(note.accCents) / 100\n      : midiFor(note.step, clef === 'bass', note.acc, key, (s.clefOctaves || [])[note.s]);\n    return base + localOctave;\n  }",
'position-aware octave clef playback')

insert = r'''  activeElectronic(pos, state) {
    const s = state || this.state;
    return (s.scoreEvents || []).filter(x => x.type === 'electronic' && x.p <= pos + .0005).sort((a,b) => b.p-a.p)[0] || null;
  }
  techniquePlaybackProfile(staff, pos, note, state) {
    const s = state || this.state, ev = this.activeTechnique(staff, pos, s);
    const p = (note && note.techniquePlayback) || (ev && ev.playback) || {};
    const tech = String(p.technique || '').toLowerCase();
    if (/pizz/.test(tech)) return { length: .55, gain: 1.05 };
    if (/sul-ponticello|behind-bridge|scrape/.test(tech)) return { length: .72, gain: .78 };
    if (/sul-tasto|air/.test(tech)) return { length: 1.08, gain: .66 };
    if (/col-legno|chop|click|snap|slap/.test(tech)) return { length: .34, gain: 1.12 };
    if (/muted/.test(tech)) return { length: .72, gain: .68 };
    if (/flutter|growl/.test(tech)) return { length: .82, gain: .9 };
    if (/harmonic/.test(tech)) return { length: .92, gain: .72 };
    return { length: 1, gain: 1 };
  }
'''
replace_once('  techniqueInstrument(staff, pos, note, state) {', insert + '  techniqueInstrument(staff, pos, note, state) {', 'electronic and technique profiles')

replace_once(
"    if (/muted/.test(tech) && /guitar/.test(base)) return 'electric_guitar_muted';\n    const percussion",
"    if (/muted/.test(tech) && /guitar/.test(base)) return 'electric_guitar_muted';\n    if (/col-legno|chop|click|snap|slap/.test(tech)) return 'woodblock';\n    if (/behind-bridge|scrape/.test(tech)) return 'reverse_cymbal';\n    if (/sul-ponticello/.test(tech) && /violin|viola|cello|contrabass|string|fiddle/.test(base)) return 'tremolo_strings';\n    if (/sul-tasto/.test(tech) && /violin|viola|cello|contrabass|string|fiddle/.test(base)) return 'string_ensemble_1';\n    if (/flutter|growl/.test(tech)) return 'muted_trumpet';\n    if (/air/.test(tech)) return 'pan_flute';\n    const percussion",
'extended technique sample routing')
replace_once(
"    if (/bell|triangle/.test(perc)) return 'tinkle_bell';\n    return base;",
"    if (/handbell|bell|triangle/.test(perc)) return 'tinkle_bell';\n    if (/siren|whistle/.test(perc)) return 'whistle';\n    if (/clap|click|snap|slap|stamp|tap|hop/.test(perc)) return 'woodblock';\n    if (/tambourine|shaker|maraca/.test(perc)) return 'agogo';\n    return base;",
'extended percussion sample routing')

replace_once(
"      const dynEv = this.effectiveScoreEvent('dynamic', n.s, n.p, s), dynGlyph = n.dyn || (dynEv && (dynEv.glyph || dynEv.value));\n      let vel = Math.round(dynEv && dynEv.playback && dynEv.playback.velocity != null ? dynEv.playback.velocity : (dynGlyph && dynMap[dynGlyph] ? dynMap[dynGlyph] : 40 + (s.vel / 100) * 87));",
"      const dynEv = this.effectiveScoreEvent('dynamic', n.s, n.p, s), dynGlyph = n.dyn || (dynEv && (dynEv.glyph || dynEv.value));\n      let vel = Math.round(dynEv && dynEv.playback && dynEv.playback.velocity != null ? dynEv.playback.velocity : (dynGlyph && dynMap[dynGlyph] ? dynMap[dynGlyph] : 40 + (s.vel / 100) * 87));\n      const electronic = this.activeElectronic(n.p, s);\n      if (electronic && electronic.playback) {\n        if (electronic.playback.electronic === 'mute') return;\n        if (electronic.playback.electronic === 'fade') vel = Math.round(vel * .58);\n      }",
'electronic playback effect')

replace_once(
"      const ap = this.articulationPlayback(n);\n      const originalInstrument = s.instruments[n.s], semanticInstrument = this.techniqueInstrument(n.s, n.p, n, s);",
"      const ap = this.articulationPlayback(n), tp = this.techniquePlaybackProfile(n.s, n.p, n, s);\n      const originalInstrument = s.instruments[n.s], semanticInstrument = this.techniqueInstrument(n.s, n.p, n, s);",
'technique playback profile use')
replace_once(
"      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : ap.length), n.s, (decorated ? vel * .8 : vel) * ap.gain, n.art);",
"      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : ap.length * tp.length), n.s, (decorated ? vel * .8 : vel) * ap.gain * tp.gain, n.art);",
'technique duration and gain')

replace_once(
"      else if (/trill|shake/.test(pattern)) trill(/shake/.test(pattern) ? upStep + 1 : upStep, tN, tStep);\n      else if (/tremolo/.test(pattern)",
"      else if (/trill|shake/.test(pattern)) trill(/shake/.test(pattern) ? upStep + 1 : upStep, tN, tStep);\n      else if (/acciaccatura/.test(pattern)) this.playTone(m + (semantic.direction === 'down' ? dnStep : upStep), Math.max(this.audio().currentTime + .002, when - .055), .065, staff, v * .82, null);\n      else if (/appoggiatura|grace/.test(pattern)) this.playTone(m + (semantic.direction === 'down' ? dnStep : upStep), when, Math.max(.08, dur * .38), staff, v * .88, null);\n      else if (/tremolo/.test(pattern)",
'grace-note playback patterns')

replace_once(
"        else if (ev.type === 'glyph' || ev.type === 'meter-glyph') { text2 = ev.glyph || ev.text || ev.name; family = 'Bravura,\\'Noto Music\\',serif'; size = ev.type === 'meter-glyph' ? 31 : 27; top = ev.type === 'meter-glyph' ? st.top + 3 : st.top - 28; extra = ''; }",
"        else if (ev.type === 'glyph' || ev.type === 'meter-glyph' || ev.type === 'electronic') { text2 = ev.glyph || ev.text || ev.name; family = 'Bravura,\\'Noto Music\\',serif'; size = ev.type === 'meter-glyph' ? 31 : 27; top = ev.type === 'meter-glyph' ? st.top + 3 : st.top - 28; extra = ''; }",
'electronic glyph rendering')

required = [
    '20260727-complete-smufl-playback-2',
    "meta.direction === 'swell' ? 'hairpin-swell'",
    "if (meta.kind === 'electronic')",
    "meta.kind === 'ornament' || meta.kind === 'grace'",
    'activeElectronic(pos, state)',
    'techniquePlaybackProfile(staff, pos, note, state)',
    "electronic.playback.electronic === 'mute'",
    '/acciaccatura/.test(pattern)',
    "button4: 'previous-zone', button5: 'next-zone'",
    'const BUMPER_COMBO_MS = 120;'
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing semantic playback marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Applied corrected SMuFL playback families and build 2')
