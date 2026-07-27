from pathlib import Path

source_path = Path('.github/scripts/patch_real_dom_scan.py')
source = source_path.read_text(encoding='utf-8')
old = '''# Reset the DOM index whenever auto scan starts so it begins at the first actual rendered control.
a, b = method_span(text, 'toggleAutoScan')
segment = text[a:b]
anchor = "this._autoScanTimer = setInterval(() => this.advanceAutoScan(), 850);"
if anchor not in segment:
    raise SystemExit('toggleAutoScan interval anchor not found')
segment = segment.replace(anchor, "this._domScanIndex = -1;\\n      " + anchor, 1)
text = text[:a] + segment + text[b:]
'''
new = '''# Reset the DOM index whenever the real scan timer starts.
anchor = "this._autoScanTimer = setInterval(() => this.advanceAutoScan(), 1200);"
if text.count(anchor) != 1:
    raise SystemExit(f'auto scan timer anchor mismatch: {text.count(anchor)}')
text = text.replace(anchor, "this._domScanIndex = -1;\\n    " + anchor, 1)
'''
if old not in source:
    raise SystemExit('patch-runner correction anchor not found')
source = source.replace(old, new, 1)
exec(compile(source, str(source_path), 'exec'))
