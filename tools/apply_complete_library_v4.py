from pathlib import Path

source = Path('tools/apply_complete_library.py').read_text(encoding='utf-8')

old = "replace_once(\"this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step,\", \"this.setState({ selId: n.id, scoreObjectId: null, selectedChordHead: null, staff: n.s, pos: n.p, step: n.step,\", 'ordinary note clears chord head')"
new = "ordinary_old = \"this.setState({ selId: n.id, scoreObjectId: null, staff: n.s, pos: n.p, step: n.step,\"\nordinary_new = \"this.setState({ selId: n.id, scoreObjectId: null, selectedChordHead: null, staff: n.s, pos: n.p, step: n.step,\"\nordinary_count = text.count(ordinary_old)\nif ordinary_count != 2:\n    raise SystemExit(f'ordinary note/rest selector reset: expected exactly 2 matches, found {ordinary_count}')\ntext = text.replace(ordinary_old, ordinary_new)"
if old not in source:
    raise SystemExit('note/rest selector guard not found')
source = source.replace(old, new, 1)

old = "replace_once(\"             acc: n.acc ? (n.acc === 'f' ? SM.flat : n.acc === 'sh' ? SM.sharp : n.acc) : '',\", \"             acc: n.accSmufl ? (n.acc || '') : (n.acc ? (n.acc === 'f' ? SM.flat : n.acc === 'sh' ? SM.sharp : n.acc) : ''),\", 'complete accidental rendering')"
new = "if \"            acc: n.acc || '',\" not in text or \"            accStyle: n.acc ? glyphAt(-28, 0, 48)\" not in text:\n    raise SystemExit('generic accidental renderer is missing')"
if old not in source:
    raise SystemExit('redundant accidental rewrite not found')
source = source.replace(old, new, 1)

scope = {'__name__': '__main__'}
exec(compile(source, 'tools/apply_complete_library.py', 'exec'), scope)

finishing = Path('tools/apply_complete_library_v2.py').read_text(encoding='utf-8')
marker = "path = Path('index.html')"
if marker not in finishing:
    raise SystemExit('finishing pass body not found')
exec(compile(finishing[finishing.index(marker):], 'tools/apply_complete_library_v2.py', 'exec'), {'__name__': '__main__', 'Path': Path})

# Human-authored trigger marker: run the complete guarded pipeline from this exact wrapper revision.
