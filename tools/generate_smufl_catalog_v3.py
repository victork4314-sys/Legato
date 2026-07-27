from pathlib import Path
import json

# Generate the complete official catalog first.
source = Path('tools/generate_smufl_catalog_v2.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/generate_smufl_catalog_v2.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('smufl-catalog.js')
raw = path.read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
if not raw.startswith(prefix) or not raw.rstrip().endswith(';'):
    raise SystemExit('Generated catalog wrapper is invalid')
data = json.loads(raw[len(prefix):].strip()[:-1])

# Hairpins, slurs, ties and similar drawn notation are semantic engraving objects,
# not reliably represented as standalone SMuFL glyph records. Keep them in the
# same complete command registry rather than pretending they are ordinary glyphs.
semantic_spans = [
    {
        'id': 'legatoSemanticCrescendoHairpin',
        'label': 'Crescendo hairpin',
        'description': 'Gradually increase loudness from point one to point two',
        'codepoint': 'U+E53E',
        'glyph': '\ue53e',
        'range': 'Semantic performance spans',
        'group': 'Popular',
        'tier': 'popular',
        'optional': False,
        'placement': 'span',
        'kind': 'hairpin',
        'audible': True,
        'sound': 'hairpin',
        'direction': 'up'
    },
    {
        'id': 'legatoSemanticDiminuendoHairpin',
        'label': 'Diminuendo hairpin',
        'description': 'Gradually decrease loudness from point one to point two',
        'codepoint': 'U+E53F',
        'glyph': '\ue53f',
        'range': 'Semantic performance spans',
        'group': 'Popular',
        'tier': 'popular',
        'optional': False,
        'placement': 'span',
        'kind': 'hairpin',
        'audible': True,
        'sound': 'hairpin',
        'direction': 'down'
    }
]
existing = {g.get('id') for g in data.get('glyphs', [])}
for item in semantic_spans:
    if item['id'] not in existing:
        data['glyphs'].append(item)

data['glyphCount'] = len(data['glyphs'])
if 'Popular' not in data.get('groups', []):
    data.setdefault('groups', []).insert(0, 'Popular')

path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print('Added semantic performance spans:', ', '.join(x['label'] for x in semantic_spans))
