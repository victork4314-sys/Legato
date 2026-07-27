from __future__ import annotations

from pathlib import Path

# First apply the architecture patch exactly as guarded there.
source = Path('tools/apply_complete_library.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/apply_complete_library.py', 'exec'), {'__name__': '__main__'})

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)


# Fix the logical chord-head enumeration expression before JavaScript parsing.
replace_once(
    "const heads = [n.step].concat(n.chord || [] .map ? (n.chord || []).map(x => n.step + x) : []);",
    "const heads = [n.step].concat((n.chord || []).map(x => n.step + x));",
    'logical chord head expression'
)

# Technique changes are position-aware events; bowings and note-specific effects remain note attachments.
replace_once(
"    if (meta.kind === 'dynamic' || meta.kind === 'hold') {\n      this.placeScoreEvent(meta.kind, name, glyph, glyph, { system: false, meta: playback });\n      return;\n    }",
"    if (meta.kind === 'dynamic' || meta.kind === 'hold') {\n      this.placeScoreEvent(meta.kind, name, glyph, glyph, { system: false, meta: playback });\n      return;\n    }\n    if (meta.kind === 'tempo' && meta.placement !== 'span') {\n      this.openScoreEventPanel('tempo', name, glyph);\n      return;\n    }\n    if (meta.kind === 'technique' && meta.placement === 'event') {\n      this.placeScoreEvent('technique', name, glyph, name, { system: false, text: name, meta: playback });\n      return;\n    }",
    'tempo and technique event semantics'
)

# Common/cut time symbols get real meter semantics; other component glyphs still place visibly.
replace_once(
"    if (meta.kind === 'meter') {\n      this.placeScoreEvent('meter-glyph', name, glyph, glyph, { system: true, text: glyph, meta: playback });\n      return;\n    }",
"    if (meta.kind === 'meter') {\n      if (/timeSigCommon/i.test(meta.id || '')) { this.placeScoreEvent('meter', name, glyph, '4/4', { system: true, meta: playback }); return; }\n      if (/timeSigCutCommon/i.test(meta.id || '')) { this.placeScoreEvent('meter', name, glyph, '2/2', { system: true, meta: playback }); return; }\n      this.placeScoreEvent('meter-glyph', name, glyph, glyph, { system: true, text: glyph, meta: playback });\n      return;\n    }",
    'meter symbol semantics'
)

# Complete rest glyphs render as chosen instead of collapsing to six built-in rests.
replace_once(
"glyph: n.rest ? (REST_GLYPHS[n.d] || REST_GLYPHS.q) : (!renderHeads ? '' : (stemless ? headGlyph : NOTE_GLYPHS[n.d][up ? 0 : 1])),",
"glyph: n.rest ? (n.restGlyph || REST_GLYPHS[n.d] || REST_GLYPHS.q) : (!renderHeads ? '' : (stemless ? headGlyph : NOTE_GLYPHS[n.d][up ? 0 : 1])),",
    'complete rest rendering'
)

# Active specialist techniques map to a genuinely different available sample where possible.
replace_once(
"    if (/muted/.test(tech) && /guitar/.test(base)) return 'electric_guitar_muted';\n    return base;",
"    if (/muted/.test(tech) && /guitar/.test(base)) return 'electric_guitar_muted';\n    const percussion = (note && note.percussionPlayback) || {};\n    const perc = String(percussion.instrument || percussion.label || '').toLowerCase();\n    if (/timpani/.test(perc)) return 'timpani';\n    if (/wood|block|clave/.test(perc)) return 'woodblock';\n    if (/agogo|cowbell/.test(perc)) return 'agogo';\n    if (/steel drum/.test(perc)) return 'steel_drums';\n    if (/taiko|bass drum/.test(perc)) return 'taiko_drum';\n    if (/tom/.test(perc)) return 'melodic_tom';\n    if (/cymbal|gong/.test(perc)) return 'reverse_cymbal';\n    if (/bell|triangle/.test(perc)) return 'tinkle_bell';\n    return base;",
    'percussion sample routing'
)

# Breath marks, caesuras and fermatas also shift everything that follows.
replace_once(
"    return seconds;\n  }\n  beatAtElapsed(start, seconds, state) {",
"    (s.scoreEvents || []).filter(ev => ev.type === 'hold' && ev.p >= start - .0005 && ev.p < end - .0005 && ev.playback).forEach(ev => {\n      if (ev.playback.sound === 'fermata') seconds += Math.max(0, (Number(ev.playback.factor) || 2) - 1) * 60 / this.pointTempoAt(ev.p, s);\n      else seconds += Math.max(0, Number(ev.playback.seconds) || 0);\n    });\n    return seconds;\n  }\n  beatAtElapsed(start, seconds, state) {",
    'hold timeline playback'
)

# Glissando/portamento and vibrato spans are heard, not merely drawn.
replace_once(
"      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : ap.length), n.s, (decorated ? vel * .8 : vel) * ap.gain, n.art);\n      if (semanticInstrument !== originalInstrument) s.instruments[n.s] = originalInstrument;\n      this.realise(n, m, when, duration, vel);",
"      this.playTone(m, Math.max(ac.currentTime, when), duration * (decorated ? .18 : ap.length), n.s, (decorated ? vel * .8 : vel) * ap.gain, n.art);\n      const glide = this.activeScoreSpan(['gliss','portamento'], n.s, n.p, s);\n      if (glide && Math.abs(n.p - Math.min(glide.p1, glide.p2)) < .011) {\n        const endPos = Math.max(glide.p1, glide.p2), target = s.notes.filter(q => !q.rest && q.s === n.s && Math.abs(q.p - endPos) < .011).sort((a,b) => Math.abs(a.step - n.step) - Math.abs(b.step - n.step))[0];\n        if (target) {\n          const targetMidi = this.noteMidi(target, s), count = Math.max(3, Math.min(24, Math.round(Math.abs(targetMidi - m) * 2))), segment = Math.max(.025, duration / count);\n          for (let gi = 1; gi < count; gi++) this.playTone(m + (targetMidi - m) * gi / count, when + segment * gi, segment * 1.15, n.s, vel * .72, null);\n        }\n      }\n      const vibrato = this.activeScoreSpan('vibrato', n.s, n.p, s);\n      if (vibrato) {\n        const stepV = .075, countV = Math.min(32, Math.floor(duration / stepV));\n        for (let vi = 1; vi < countV; vi++) this.playTone(m + Math.sin(vi * 1.7) * .22, when + vi * stepV, stepV * 1.08, n.s, vel * .36, null);\n      }\n      if (semanticInstrument !== originalInstrument) s.instruments[n.s] = originalInstrument;\n      this.realise(n, m, when, duration, vel);",
    'glissando portamento and vibrato playback'
)

# The score selector should not list an empty duplicate base chord head for rests or missing IDs.
replace_once(
"      out.push({ kind: n.rest ? 'rest' : 'note', id: n.id, noteId: n.id, staff: n.s, pos: n.p, step: n.step, label: baseLabel + ' · bar ' + (Math.floor(n.p / this.barCapacity()) + 1) });",
"      if (!n.id) n.id = 'n' + Math.random().toString(36).slice(2, 8);\n      out.push({ kind: n.rest ? 'rest' : 'note', id: n.id, noteId: n.id, staff: n.s, pos: n.p, step: n.step, label: baseLabel + ' · bar ' + (Math.floor(n.p / this.barCapacity()) + 1) });",
    'selector stable note ids'
)

# Generated catalog presence and protected controller paths remain mandatory.
required = [
    '20260727-complete-smufl-playback-1',
    '<script src="./smufl-catalog.js?v=20260727-complete-smufl-playback-1"></script>',
    "button4: 'previous-zone', button5: 'next-zone'",
    'const BUMPER_COMBO_MS = 120;',
    'score-object-selector',
    'SMUFL_CATALOG.glyphs',
    'accCents',
    'articulationPlayback(note)',
    "this.activeScoreSpan(['gliss','portamento']",
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing finishing-pass marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Complete library finishing pass applied')
