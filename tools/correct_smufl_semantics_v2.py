from pathlib import Path

source = Path('tools/correct_smufl_semantics.py').read_text(encoding='utf-8')

anchor = """    if ident.startswith(('control','text')):
        set_sem(g, 'event', 'glyph', False)
        continue
    if re.search(r'combining|component|separator|parenthes|bracket (start|end)|stem (up|down|left|right)|for stem', low) and not re.search(r'actual|notehead', low):
"""
replacement = """    if ident.startswith(('control','text')):
        set_sem(g, 'event', 'glyph', False)
        continue
    if ident.startswith('graceNoteSlash'):
        set_sem(g, 'event', 'glyph', False)
        continue
    if re.search(r'gracenote|grace note|acciaccatura|appoggiatura', low):
        pattern = 'acciaccatura' if re.search(r'acciacc', low) else 'appoggiatura'
        direction = 'down' if re.search(r'below|stem down', low) else 'up'
        set_sem(g, 'note', 'grace', True, 'grace', pattern=pattern, direction=direction)
        continue
    if re.search(r'combining|component|separator|parenthes|bracket (start|end)|stem (up|down|left|right)|for stem', low) and not re.search(r'actual|notehead', low):
"""
if source.count(anchor) != 1:
    raise SystemExit('Could not locate the control/component priority anchor')
source = source.replace(anchor, replacement, 1)

later_grace = """    if re.search(r'gracenote|grace note|acciaccatura|appoggiatura', low):
        pattern = 'acciaccatura' if re.search(r'acciacc|slash', low) else 'appoggiatura'
        direction = 'down' if re.search(r'below|down', low) else 'up'
        set_sem(g, 'note', 'grace', True, 'grace', pattern=pattern, direction=direction)
        continue

"""
if source.count(later_grace) != 1:
    raise SystemExit('Could not locate the old grace priority block')
source = source.replace(later_grace, '', 1)

tech_anchor = """def technique_name(text):
    low = text.lower()
    pairs = [
"""
tech_replacement = """def technique_name(text):
    low = text.lower()
    if 'harmon mute' in low and re.search(r'stem open|stem out', low):
        return 'harmon-open'
    if 'harmon mute' in low and re.search(r'stem closed|stem in', low):
        return 'harmon-closed'
    if re.search(r'mute open|open mute|senza sord', low):
        return 'open'
    pairs = [
"""
if source.count(tech_anchor) != 1:
    raise SystemExit('Could not locate the technique classifier')
source = source.replace(tech_anchor, tech_replacement, 1)

source = source.replace("'graceNoteAcciaccaturaStemUp': lambda g: g.get('kind') == 'grace' and g.get('pattern') == 'acciaccatura',", "'graceNoteAcciaccaturaStemUp': lambda g: g.get('kind') == 'grace' and g.get('pattern') == 'acciaccatura',\n    'graceNoteSlashStemUp': lambda g: not g.get('audible') and g.get('kind') == 'glyph',")

exec(compile(source, 'tools/correct_smufl_semantics.py', 'exec'), {'__name__': '__main__', 'Path': Path, 're': __import__('re'), 'json': __import__('json')})
