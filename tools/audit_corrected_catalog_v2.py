from pathlib import Path

source = Path('tools/audit_corrected_catalog.py').read_text(encoding='utf-8')
old = "audible_kinds = {'dynamic','hold','grace','ornament','tremolo','pitch-effect','articulation','technique','bowing','percussion','electronic','hairpin'}"
new = "audible_kinds = {'dynamic','hold','grace','ornament','tremolo','pitch-effect','articulation','technique','bowing','percussion','electronic','hairpin','let-ring','pedal','octave-line','tempo','tie','slur','vibrato'}"
if source.count(old) != 1:
    raise SystemExit('Could not expand the audible-kind audit')
source = source.replace(old, new, 1)
anchor = "print('Corrected catalog named audit passed')"
extra = """check('laissez vibrer audible', by_id['articLaissezVibrerAbove'].get('kind') == 'let-ring' and by_id['articLaissezVibrerAbove'].get('audible'), repr(by_id['articLaissezVibrerAbove']))
check('chant augmentum lengthens', by_id['chantAugmentum'].get('profile') == 'tenuto' and by_id['chantAugmentum'].get('audible'), repr(by_id['chantAugmentum']))
check('chant ictus emphasizes', by_id['chantIctusAbove'].get('profile') == 'accent' and by_id['chantIctusAbove'].get('audible'), repr(by_id['chantIctusAbove']))
check('chant circulus audible', by_id['chantCirculusAbove'].get('audible') is True, repr(by_id['chantCirculusAbove']))
"""
if source.count(anchor) != 1:
    raise SystemExit('Could not extend the named audit')
source = source.replace(anchor, extra + anchor, 1)
exec(compile(source, 'tools/audit_corrected_catalog.py', 'exec'), {'__name__': '__main__', 'Path': Path, 'json': __import__('json'), 're': __import__('re')})
