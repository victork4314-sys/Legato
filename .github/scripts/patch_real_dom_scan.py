from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def method_span(source, name):
    marker = '\n  ' + name + '('
    start = source.find(marker)
    if start < 0:
        raise SystemExit(f'method not found: {name}')
    brace = source.find('{', start)
    if brace < 0:
        raise SystemExit(f'opening brace not found: {name}')
    depth = 0
    quote = None
    escape = False
    line_comment = False
    block_comment = False
    i = brace
    while i < len(source):
        c = source[i]
        n = source[i + 1] if i + 1 < len(source) else ''
        if line_comment:
            if c == '\n':
                line_comment = False
        elif block_comment:
            if c == '*' and n == '/':
                block_comment = False
                i += 1
        elif quote:
            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == quote:
                quote = None
        else:
            if c == '/' and n == '/':
                line_comment = True
                i += 1
            elif c == '/' and n == '*':
                block_comment = True
                i += 1
            elif c in "'\"`":
                quote = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return start + 1, i + 1
        i += 1
    raise SystemExit(f'unclosed method: {name}')


def replace_method(name, replacement):
    global text
    a, b = method_span(text, name)
    text = text[:a] + replacement + text[b:]


replace_method('syncGlobalSelection', r'''  visibleScanItems() {
    return Array.from(document.querySelectorAll('[data-ptr]')).filter(el => {
      if (el.offsetParent === null) return false;
      if (el.closest('[data-scroll="score"]')) return false;
      if (el.getAttribute('aria-hidden') === 'true' || el.getAttribute('aria-disabled') === 'true') return false;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    });
  }
  zoneScanItems(zone) {
    const all = this.visibleScanItems();
    return all.filter(el => {
      const r = el.getBoundingClientRect();
      if (zone === 0) return r.top < 120;
      if (zone === 1) return r.right <= 360 && r.top >= 70;
      if (zone === 2) return r.top >= 70 && r.top < 235;
      if (zone === 4) return r.left >= window.innerWidth - 430 && r.top >= 70;
      return false;
    });
  }
  syncGlobalSelection() {
    document.querySelectorAll('[data-scan-selected="true"]').forEach(el => el.removeAttribute('data-scan-selected'));
    if (this.state.zone === 3) return;
    const items = this.state.autoScan ? this.visibleScanItems() : this.zoneScanItems(this.state.zone);
    if (!items.length) return;
    const raw = this.state.autoScan ? (this._domScanIndex == null ? 0 : this._domScanIndex) : this.state.focus;
    const index = ((raw % items.length) + items.length) % items.length;
    const target = items[index];
    target.setAttribute('data-scan-selected', 'true');
    this.reveal(target);
  }''')

replace_method('advanceAutoScan', r'''  advanceAutoScan() {
    if (!this.state.autoScan) return;
    const items = this.visibleScanItems();
    if (!items.length) return;
    let next = (this._domScanIndex == null ? -1 : this._domScanIndex) + 1;
    if (next >= items.length) {
      const nextMode = (this.state.mode + 1) % 6;
      this._domScanIndex = -1;
      return this.setState({ mode: nextMode, zone: 2, focus: 0 }, () => requestAnimationFrame(() => this.advanceAutoScan()));
    }
    this._domScanIndex = next;
    const target = items[next];
    document.querySelectorAll('[data-scan-selected="true"]').forEach(el => el.removeAttribute('data-scan-selected'));
    target.setAttribute('data-scan-selected', 'true');
    this.reveal(target);
    const label = target.getAttribute('data-ptr') || target.getAttribute('aria-label') || target.textContent.trim() || 'Item';
    this.setState({ spoken: label });
  }''')

# Make A/Enter activate the real outlined item before falling back to the old hand-written focus list.
a, b = method_span(text, 'activateFocus')
brace = text.find('{', a, b)
insert = "\n    const liveTarget = document.querySelector('[data-scan-selected=\"true\"]');\n    if (liveTarget && this.state.zone !== 3) { liveTarget.click(); return; }"
text = text[:brace + 1] + insert + text[brace + 1:]

# Reset the DOM index whenever auto scan starts so it begins at the first actual rendered control.
a, b = method_span(text, 'toggleAutoScan')
segment = text[a:b]
anchor = "this._autoScanTimer = setInterval(() => this.advanceAutoScan(), 850);"
if anchor not in segment:
    raise SystemExit('toggleAutoScan interval anchor not found')
segment = segment.replace(anchor, "this._domScanIndex = -1;\n      " + anchor, 1)
text = text[:a] + segment + text[b:]

# Bump the deployed asset URL for this exact upgrade.
old_version = './support.js?v=20260727-selection-live-2'
new_version = './support.js?v=20260727-real-dom-scan-1'
if text.count(old_version) != 1:
    raise SystemExit(f'cache version anchor mismatch: {text.count(old_version)}')
text = text.replace(old_version, new_version, 1)

required = [
    'visibleScanItems()',
    "document.querySelector('[data-scan-selected=\"true\"]')",
    'support.js?v=20260727-real-dom-scan-1',
    "el.closest('[data-scroll=\"score\"]')",
]
for item in required:
    if item not in text:
        raise SystemExit('missing required patch text: ' + item)

path.write_text(text, encoding='utf-8')
print('real DOM scan patch applied')
