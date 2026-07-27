from __future__ import annotations

from pathlib import Path

# Amend the first guarded pass without weakening any unrelated replacement.
source = Path('tools/apply_complete_library.py').read_text(encoding='utf-8')
old_call = '''replace_once("this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step,", "this.setState({ selId: n.id, scoreObjectId: null, selectedChordHead: null, staff: n.s, pos: n.p, step: n.step,", 'ordinary note clears chord head')'''
new_call = '''ordinary_old = "this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step,"
ordinary_new = "this.setState({ selId: n.id, scoreObjectId: null, selectedChordHead: null, staff: n.s, pos: n.p, step: n.step,"
ordinary_count = text.count(ordinary_old)
if ordinary_count != 2:
    raise SystemExit(f'ordinary note/rest selector reset: expected exactly 2 matches, found {ordinary_count}')
text = text.replace(ordinary_old, ordinary_new)'''
if old_call not in source:
    raise SystemExit('Could not locate the note/rest selector reset guard')
source = source.replace(old_call, new_call, 1)
exec(compile(source, 'tools/apply_complete_library.py', 'exec'), {'__name__': '__main__'})

# Run the finishing pass after its original first-pass bootstrap.
finishing = Path('tools/apply_complete_library_v2.py').read_text(encoding='utf-8')
marker = "path = Path('index.html')"
if marker not in finishing:
    raise SystemExit('Could not locate finishing-pass body')
finishing = finishing[finishing.index(marker):]
exec(compile(finishing, 'tools/apply_complete_library_v2.py', 'exec'), {'__name__': '__main__', 'Path': Path})
