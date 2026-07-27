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
        if label == 'tie drawing endpoint' and count == 0:
            candidates = [line for line in text.splitlines(True) if line.rstrip('\\r\\n').lstrip() == old.lstrip()]
            if len(candidates) == 1:
                line = candidates[0]
                ending = '\\r\\n' if line.endswith('\\r\\n') else ('\\n' if line.endswith('\\n') else '')
                body = line[:-len(ending)] if ending else line
                indent = body[:len(body) - len(body.lstrip())]
                text = text.replace(line, indent + new.lstrip() + ending, 1)
                return
        raise SystemExit(f'{label}: expected {expected} match(es), found {count}')
    text = text.replace(old, new, expected)
"""
if old not in t:
    raise SystemExit('Could not find guarded replacement helper')
t = t.replace(old, new, 1)
p.write_text(t, encoding='utf-8')
