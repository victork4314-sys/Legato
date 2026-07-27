from pathlib import Path
import subprocess

patch = Path('tools/apply_meter_theme_scroll_repairs.py')
text = patch.read_text(encoding='utf-8')
old = """    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, found {count}')\n    text = text.replace(old, new, 1)\n"""
new = """    if label == 'controller theme focus list' and count == 2:\n        text = text.replace(old, new, 1)\n        return\n    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, found {count}')\n    text = text.replace(old, new, 1)\n"""
if text.count(old) != 1:
    raise SystemExit('guard helper shape changed; refusing to guess')
patch.write_text(text.replace(old, new, 1), encoding='utf-8')
subprocess.run(['python3', str(patch)], check=True)
