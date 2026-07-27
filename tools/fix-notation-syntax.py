from pathlib import Path
p = Path('index.html')
t = p.read_text(encoding='utf-8')
bad = "border-top:1.5px solid  + accent2 + ';transform:rotate("
good = "border-top:1.5px solid ' + accent2 + ';transform:rotate("
count = t.count(bad)
if count != 1:
    raise SystemExit(f'glissando syntax: expected 1 match, found {count}')
p.write_text(t.replace(bad, good, 1), encoding='utf-8')
print('Glissando syntax repaired')
