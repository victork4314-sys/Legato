from pathlib import Path
import json, re

source = Path('tools/correct_smufl_semantics_v2.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/correct_smufl_semantics_v2.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('smufl-catalog.js')
raw = path.read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
data = json.loads(raw[len(prefix):].strip()[:-1])

tech_ranges = re.compile(r'(string techniques|wind techniques|brass techniques|guitar techniques|vocal techniques|handbells|percussion playing technique|beater pictograms)', re.I)
visual_component = re.compile(r'(component|combining|stem$|left$|right$|up$|down$|parenthes|bracket|placeholder|control)', re.I)
for g in data['glyphs']:
    text = f"{g.get('id','')} {g.get('label','')}"
    low = text.lower()
    if g.get('kind') == 'pedal' and g.get('placement') == 'event':
        state = 'off' if re.search(r'up|release|lift|off|cancel', low) else 'on'
        g.update(audible=True, sound='pedal', state=state)
    if re.search(r'bow direction|up bow|down bow', low):
        direction = 'up' if 'up bow' in low else ('down' if 'down bow' in low else 'change')
        g.update(placement='note', kind='bowing', audible=True, sound='bowing', technique=direction + '-bow')
    if tech_ranges.search(g.get('range','')) and not g.get('audible') and not visual_component.search(text):
        if 'handbell' in g.get('range','').lower():
            g.update(placement='note', kind='percussion', audible=True, sound='percussion', instrument='handbell', technique=g.get('label'))
        elif 'percussion' in g.get('range','').lower() or 'beater' in g.get('range','').lower():
            g.update(placement='note', kind='percussion', audible=True, sound='percussion', instrument=g.get('label'))
        else:
            g.update(placement='event', kind='technique', audible=True, sound='technique', technique=re.sub(r'[^a-z0-9]+', '-', g.get('label','technique').lower()).strip('-'))

by_id = {g['id']: g for g in data['glyphs']}
for ident in ('brassHarmonMuteStemOpen','brassHarmonMuteStemClosed'):
    if ident in by_id and not by_id[ident].get('audible'):
        raise SystemExit(ident + ' must be audible')
if 'stringsChangeBowDirectionImposed' in by_id and not by_id['stringsChangeBowDirectionImposed'].get('audible'):
    raise SystemExit('String bow-direction changes must be audible')

path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print('Extended semantics across all dedicated performance-technique ranges')
