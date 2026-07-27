from pathlib import Path
p = Path('tools/apply-interaction-fix.py')
t = p.read_text(encoding='utf-8')
old = """    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)
"""
new = """    count = text.count(old)
    expected = 2 if label == 'font stylesheet' else 1
    if count != expected:
        raise SystemExit(f'{label}: expected {expected} match(es), found {count}')
    text = text.replace(old, new, expected)
"""
if old not in t:
    raise SystemExit('Could not find guarded replacement helper')
p.write_text(t.replace(old, new, 1), encoding='utf-8')
