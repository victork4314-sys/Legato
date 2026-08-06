from pathlib import Path

source = Path('tools/apply_semantic_playback_corrections.py').read_text(encoding='utf-8')
old = "replace_once('20260727-complete-smufl-playback-1', '20260727-complete-smufl-playback-2', 'build and cache version')"
new = "old_build = '20260727-complete-smufl-playback-1'\nnew_build = '20260727-complete-smufl-playback-2'\nbuild_count = text.count(old_build)\nif build_count != 4:\n    raise SystemExit(f'build and cache version: expected exactly 4 matches, found {build_count}')\ntext = text.replace(old_build, new_build)"
if source.count(old) != 1:
    raise SystemExit('Could not locate the original build-tag guard')
source = source.replace(old, new, 1)
exec(compile(source, 'tools/apply_semantic_playback_corrections.py', 'exec'), {'__name__': '__main__', 'Path': Path})
