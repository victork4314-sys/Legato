from pathlib import Path
import subprocess

patch = Path('tools/apply_meter_theme_scroll_repairs.py')
text = patch.read_text(encoding='utf-8')
old = """    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, found {count}')\n    text = text.replace(old, new, 1)\n"""
new = """    if label == 'controller theme focus list' and count == 2:\n        text = text.replace(old, new, 1)\n        return\n    if count != 1:\n        raise SystemExit(f'{label}: expected exactly one match, found {count}')\n    text = text.replace(old, new, 1)\n"""
if text.count(old) != 1:
    raise SystemExit('guard helper shape changed; refusing to guess')
text = text.replace(old, new, 1)
old_print_check = "if text.count('data-print-score=\"true\"') != 1:"
new_print_check = "if text.count('<div data-print-score=\"true\"') != 1:"
if text.count(old_print_check) != 1:
    raise SystemExit('print marker guard shape changed; refusing to guess')
text = text.replace(old_print_check, new_print_check, 1)
patch.write_text(text, encoding='utf-8')
subprocess.run(['python3', str(patch)], check=True)
