from pathlib import Path
import json, re

raw = Path('smufl-catalog.js').read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
data = json.loads(raw[len(prefix):].strip()[:-1])
glyphs = data['glyphs']
by_id = {g['id']: g for g in glyphs}


def check(name, condition, detail=''):
    if not condition:
        raise SystemExit('AUDIT FAILED: ' + name + (': ' + detail if detail else ''))
    print('PASS:', name)

check('glyph count', data['glyphCount'] == 3451, str(data['glyphCount']))
check('range count', data['rangeCount'] == 131, str(data['rangeCount']))
check('catalog length', len(glyphs) == data['glyphCount'], str(len(glyphs)))
controls = [g['id'] for g in glyphs if g.get('audible') and g['id'].startswith(('control','text'))]
check('control and text glyphs silent', not controls, repr(controls[:10]))
grace_trills = [g['id'] for g in glyphs if g.get('kind') == 'grace' and re.search(r'trill|shake', str(g.get('pattern','')))]
check('grace notes are not trills', not grace_trills, repr(grace_trills[:10]))
clusters = [g['id'] for g in glyphs if 'cluster' in (g['id'] + ' ' + g['label']).lower() and g.get('sound') == 'harmonic']
check('cluster noteheads are not harmonics', not clusters, repr(clusters[:10]))
audible_kinds = {'dynamic','hold','grace','ornament','tremolo','pitch-effect','articulation','technique','bowing','percussion','electronic','hairpin'}
silent = [g['id'] for g in glyphs if g.get('kind') in audible_kinds and not g.get('audible')]
check('performance semantic kinds audible', not silent, repr(silent[:10]))
check('controlBeginBeam silent', by_id['controlBeginBeam']['audible'] is False, repr(by_id['controlBeginBeam']))
check('acciaccatura classification', by_id['graceNoteAcciaccaturaStemUp'].get('kind') == 'grace' and by_id['graceNoteAcciaccaturaStemUp'].get('pattern') == 'acciaccatura', repr(by_id['graceNoteAcciaccaturaStemUp']))
check('grace slash component silent', by_id['graceNoteSlashStemUp'].get('audible') is False, repr(by_id['graceNoteSlashStemUp']))
check('breath comma hold', by_id['breathMarkComma'].get('sound') == 'breath', repr(by_id['breathMarkComma']))
check('forte velocity', by_id['dynamicForte'].get('velocity') == 94, repr(by_id['dynamicForte']))
check('piano velocity', by_id['dynamicPiano'].get('velocity') == 52, repr(by_id['dynamicPiano']))
check('Harmon open', by_id['brassHarmonMuteStemOpen'].get('technique') == 'harmon-open', repr(by_id['brassHarmonMuteStemOpen']))
check('Harmon closed', by_id['brassHarmonMuteStemClosed'].get('technique') == 'harmon-closed', repr(by_id['brassHarmonMuteStemClosed']))
pedal_on = [g['id'] for g in glyphs if g.get('kind') == 'pedal' and g.get('placement') == 'event' and g.get('state') == 'on']
pedal_off = [g['id'] for g in glyphs if g.get('kind') == 'pedal' and g.get('placement') == 'event' and g.get('state') == 'off']
check('standalone pedal on exists', bool(pedal_on), repr(pedal_on[:10]))
check('standalone pedal off exists', bool(pedal_off), repr(pedal_off[:10]))
elec_mute = [g['id'] for g in glyphs if g.get('kind') == 'electronic' and g.get('electronic') == 'mute']
elec_unmute = [g['id'] for g in glyphs if g.get('kind') == 'electronic' and g.get('electronic') == 'unmute']
check('electronic mute exists', bool(elec_mute), repr(elec_mute[:10]))
check('electronic unmute exists', bool(elec_unmute), repr(elec_unmute[:10]))
print('Corrected catalog named audit passed')
