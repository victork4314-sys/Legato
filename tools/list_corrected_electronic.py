from pathlib import Path
import json
raw = Path('smufl-catalog.js').read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
data = json.loads(raw[len(prefix):].strip()[:-1])
items = [g for g in data['glyphs'] if g.get('id','').startswith('elec') or 'electronic' in g.get('range','').lower()]
for g in items:
    print(json.dumps({k:g.get(k) for k in ('id','label','range','placement','kind','audible','sound','electronic')}, ensure_ascii=False))
print('COUNT', len(items))
