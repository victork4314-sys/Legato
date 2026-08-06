from pathlib import Path
import json, re

source = Path('tools/correct_smufl_semantics_v3.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/correct_smufl_semantics_v3.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('smufl-catalog.js')
raw = path.read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
data = json.loads(raw[len(prefix):].strip()[:-1])

for g in data['glyphs']:
    low = (g.get('id','') + ' ' + g.get('label','')).lower()
    if 'laissezvibrer' in low or 'laissez vibrer' in low:
        g.update(placement='span', kind='let-ring', audible=True, sound='let-ring')
    elif g.get('id') in ('chantAugmentum','chantEpisema'):
        g.update(placement='note', kind='articulation', audible=True, sound='articulation', profile='tenuto')
    elif g.get('id','').startswith('chantIctus'):
        g.update(placement='note', kind='articulation', audible=True, sound='articulation', profile='accent')
    elif re.match(r'chant(Semi)?Circulus', g.get('id','')):
        g.update(placement='note', kind='articulation', audible=True, sound='articulation', profile='chant')

sound_defaults = {
    'dynamic': ('dynamic', {'velocity': 78}),
    'hold': ('fermata', {'factor': 2}),
    'grace': ('grace', {'pattern': 'appoggiatura', 'direction': 'up'}),
    'ornament': ('ornament', {'pattern': 'trill'}),
    'tremolo': ('tremolo', {'strokes': 1}),
    'pitch-effect': ('pitch-effect', {'effect': 'slide'}),
    'articulation': ('articulation', {'profile': 'generic'}),
    'technique': ('technique', {'technique': 'generic-technique'}),
    'bowing': ('bowing', {'technique': 'bow-change'}),
    'percussion': ('percussion', {'instrument': 'percussion'}),
    'electronic': ('electronic', {'electronic': 'level'}),
    'hairpin': ('hairpin', {'direction': 'up'}),
    'let-ring': ('let-ring', {}),
    'pedal': ('pedal', {'state': 'on'}),
    'octave-line': ('octave', {'semitones': 12}),
    'tempo': ('tempo', {'direction': 'down'}),
    'tie': ('tie', {}),
    'slur': ('slur', {}),
    'vibrato': ('vibrato', {})
}
for g in data['glyphs']:
    kind = g.get('kind')
    if kind in sound_defaults and not g.get('audible'):
        sound, extras = sound_defaults[kind]
        g['audible'] = True
        g['sound'] = sound
        for key, value in extras.items():
            g.setdefault(key, value)

contradictions = [g['id'] for g in data['glyphs'] if g.get('kind') in sound_defaults and not g.get('audible')]
if contradictions:
    raise SystemExit('Sound-bearing semantic contradictions remain: ' + repr(contradictions[:20]))

path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print('Normalized every sound-bearing semantic family')
