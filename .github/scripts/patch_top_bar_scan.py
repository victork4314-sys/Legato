from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)


def append_ring_to_style(name, index):
    global text
    needle = name + ':'
    pos = text.find(needle)
    if pos < 0:
        raise SystemExit(f'{name} binding not found')
    line_end = text.find('\n', pos)
    line = text[pos:line_end]
    ring = f"this.ring('top', {index})"
    if ring in line:
        return
    if not line.rstrip().endswith(','):
        raise SystemExit(f'unexpected {name} line shape')
    updated = line.rstrip()[:-1] + f' + {ring},'
    text = text[:pos] + updated + text[line_end:]

replace_once(
'''      <div onClick="{{ openMenu }}" data-ptr="File menu" style="display: flex; align-items: center; gap: 7px; padding: 4px 10px; border: 1px solid #2b3230; border-radius: 5px; background: #121615; cursor: pointer;" style-hover="border-color:#3c4441">''',
'''      <div onClick="{{ openMenu }}" data-ptr="File menu" style="{{ fileMenuStyle }}" style-hover="border-color:#3c4441">''',
'file menu style binding')

replace_once(
'''    if (s.zone === 0) return ['Setup', 'Write', 'Engrave', 'Play', 'Print', 'Controller'].map((n, i) => ({ t: 'mode', i: i, label: n + ' mode' }))
      .concat([{ t: 'top', i: 0, label: s.sidebarsHidden ? 'Show sidebars' : 'Hide sidebars' }, { t: 'top', i: 1, label: s.autoScan ? 'Stop auto scan' : 'Start auto scan' }]);''',
'''    if (s.zone === 0) return [
      { t: 'top', i: 0, label: s.ptrOn ? 'Turn pointer off' : 'Turn pointer on' },
      { t: 'top', i: 1, label: s.sidebarsHidden ? 'Show sidebars' : 'Hide sidebars' },
      { t: 'top', i: 2, label: s.autoScan ? 'Stop auto scan' : 'Start auto scan' },
      { t: 'top', i: 3, label: 'Open the menu' },
      { t: 'top', i: 4, label: 'Open the file menu' }
    ].concat(['Setup', 'Write', 'Engrave', 'Play', 'Print', 'Controller'].map((n, i) => ({ t: 'mode', i: i, label: n + ' mode' })));''',
'top bar focus list')

replace_once(
'''    else if (it.t === 'top') { if (it.i === 0) this.toggleSidebars(); else this.toggleAutoScan(); }''',
'''    else if (it.t === 'top') {
      if (it.i === 0) this.togglePointer();
      else if (it.i === 1) this.toggleSidebars();
      else if (it.i === 2) this.toggleAutoScan();
      else if (it.i === 3) this.openHub();
      else if (it.i === 4) this.setState({ menu: true, menuIdx: 0, spoken: 'File menu' });
    }''',
'top bar activation')

replace_once(
'''      sidebarsToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.sidebarsHidden ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.sidebarsHidden ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 0),''',
'''      sidebarsToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.sidebarsHidden ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.sidebarsHidden ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 1),''',
'sidebars ring index')

replace_once(
'''      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 1),''',
'''      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 2),''',
'auto scan ring index')

append_ring_to_style('ptrChipStyle', 0)
append_ring_to_style('modeBadgeStyle', 3)

marker = "      autoScanToggleStyle: 'display:flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid ' + (s.autoScan ? accent : '#2b3230') + ';border-radius:5px;background:' + (s.autoScan ? 'rgba(116,161,46,.12)' : '#121615') + ';cursor:pointer;' + this.ring('top', 2),\n"
if text.count(marker) != 1:
    raise SystemExit('file style insertion marker mismatch')
text = text.replace(marker, marker + "      fileMenuStyle: 'display:flex;align-items:center;gap:7px;padding:4px 10px;border:1px solid #2b3230;border-radius:5px;background:#121615;cursor:pointer;' + this.ring('top', 4),\n", 1)

required = [
    "{ t: 'top', i: 0, label: s.ptrOn ? 'Turn pointer off' : 'Turn pointer on' }",
    "{ t: 'top', i: 4, label: 'Open the file menu' }",
    "this.ring('top', 0)",
    "this.ring('top', 3)",
    "this.ring('top', 4)",
    'style="{{ fileMenuStyle }}"'
]
for item in required:
    if item not in text:
        raise SystemExit(f'validation failed: missing {item}')

path.write_text(text, encoding='utf-8')
print('top bar scan patch applied')
