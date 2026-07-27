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
t = t.replace(old, new, 1)
tie_old = 'one("           const nextTie = n.tie ?'
tie_new = 'one("          const nextTie = n.tie ?'
tie_repl_old = '    "           const nextTie = n.tieTo ?'
tie_repl_new = '    "          const nextTie = n.tieTo ?'
if tie_old not in t or tie_repl_old not in t:
    raise SystemExit('Could not find tie renderer guard indentation')
t = t.replace(tie_old, tie_new, 1).replace(tie_repl_old, tie_repl_new, 1)
p.write_text(t, encoding='utf-8')
