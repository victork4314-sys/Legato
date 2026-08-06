from pathlib import Path

source = Path('tools/apply_semantic_playback_corrections_v3.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/apply_semantic_playback_corrections_v3.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

legacy = """const LEGACY_REALISED_GLYPHS = {};
['\\uE566','\\uEAA4','\\uE566\\uE262','\\uE566\\uE260','\\uE566\\uE261','\\uE56C','\\uE56D','\\uE56E','\\uE567','\\uE568','\\uE569','\\uE56A','\\uE56F','\\uE585','\\uE5B8','\\uE5B2','\\uE5B3','\\uE5B6','\\uE5B4','\\uE5B5','\\uE5B7','\\uE5BB','\\uE5BD','\\uE5C8','\\uE5C0','\\uE5C1','\\uE5B0','\\uE5B1','\\uE560','\\uE562','\\uE5E8','\\uE5E4','\\uE5D1','\\uE5D6','\\uE5D3','\\uE5D0','\\uE5D5','\\uE5D4','\\uE5E2','\\uE5E1','\\uE5E3','\\uE5E5','\\uE634','\\uE635','\\uE220','\\uE221','\\uE222'].forEach(g => { LEGACY_REALISED_GLYPHS[g] = 1; });
"""
replace_once("// standard rest decomposition: largest value that fits and does not cross a stronger beat\n", legacy + "// standard rest decomposition: largest value that fits and does not cross a stronger beat\n", 'legacy realization lookup')
replace_once("    if (semantic) {\n      const pattern = String(semantic.pattern || semantic.effect || semantic.sound || '').toLowerCase();", "    if (semantic && !LEGACY_REALISED_GLYPHS[g]) {\n      const pattern = String(semantic.pattern || semantic.effect || semantic.sound || '').toLowerCase();", 'skip duplicate semantic realization')

if 'LEGACY_REALISED_GLYPHS' not in text or 'semantic && !LEGACY_REALISED_GLYPHS[g]' not in text:
    raise SystemExit('Legacy realization de-duplication is missing')
path.write_text(text, encoding='utf-8')
print('Prevented duplicate legacy and catalog semantic realization')
