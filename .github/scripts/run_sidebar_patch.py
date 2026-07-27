from pathlib import Path

script_path = Path('.github/scripts/patch_sidebar_scan.py')
source = script_path.read_text(encoding='utf-8')
old = '    "s.sidebarsHidden ? [0, 2, 3] : [0, 1, 2, 3, 4]",\n'
new = '    "return this.state.sidebarsHidden ? [0, 2, 3] : [0, 1, 2, 3, 4];",\n'
if source.count(old) != 1:
    raise SystemExit(f'validation runner expected one guard to correct, found {source.count(old)}')
source = source.replace(old, new, 1)
exec(compile(source, str(script_path), 'exec'))
