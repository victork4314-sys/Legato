from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

def once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    text = text.replace(old, new, 1)

once(
"""<style>\n  @font-face {""",
"""<style>\n  [data-ptr][data-scan-selected=\"true\"] {\n    outline: 2px solid #74a12e !important;\n    outline-offset: 1px;\n    box-shadow: 0 0 0 1px rgba(116,161,46,.35), 0 0 12px rgba(116,161,46,.22) !important;\n    position: relative;\n    z-index: 2;\n  }\n  @font-face {""",
'global selection css')

once(
"""  componentWillUnmount() { window.removeEventListener('keydown', this._keys); window.removeEventListener('keyup', this._keyup); window.__legatoKeys = null; cancelAnimationFrame(this._raf); if (this._autoScanTimer) clearInterval(this._autoScanTimer); if (this._ac) this._ac.close(); }\n""",
"""  componentWillUnmount() { window.removeEventListener('keydown', this._keys); window.removeEventListener('keyup', this._keyup); window.__legatoKeys = null; cancelAnimationFrame(this._raf); if (this._autoScanTimer) clearInterval(this._autoScanTimer); if (this._ac) this._ac.close(); }\n  componentDidUpdate() {\n    requestAnimationFrame(() => this.syncGlobalSelection());\n  }\n  syncGlobalSelection() {\n    const nodes = Array.from(document.querySelectorAll('[data-ptr]'));\n    nodes.forEach(el => el.removeAttribute('data-scan-selected'));\n    if (this.state.zone === 3) return;\n    const list = this.focusList(), item = list[this.state.focus];\n    if (!item || !item.label) return;\n    const norm = value => String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim().replace(/\\s+/g, ' ');\n    const stop = new Set(['a','an','the','to','of','on','or','and','this','that','with','as','you','move','set']);\n    const tokens = value => norm(value).split(' ').filter(x => x && !stop.has(x));\n    const wanted = norm(item.label), wantedTokens = tokens(item.label);\n    const visible = nodes.filter(el => el.offsetParent !== null);\n    let target = visible.find(el => norm(el.getAttribute('data-ptr')) === wanted)\n      || visible.find(el => { const label = norm(el.getAttribute('data-ptr')); return label && (label.includes(wanted) || wanted.includes(label)); });\n    if (!target) {\n      let best = null, bestScore = -1;\n      visible.forEach(el => {\n        const labelTokens = tokens(el.getAttribute('data-ptr'));\n        const overlap = wantedTokens.filter(x => labelTokens.includes(x)).length;\n        const score = overlap * 10 - Math.abs(labelTokens.length - wantedTokens.length);\n        if (overlap && score > bestScore) { best = el; bestScore = score; }\n      });\n      target = best;\n    }\n    if (!target) {\n      const region = visible.filter(el => {\n        const r = el.getBoundingClientRect();\n        if (this.state.zone === 0) return r.top < 115;\n        if (this.state.zone === 1) return r.right < 360;\n        if (this.state.zone === 2) return r.top >= 70 && r.top < 230;\n        if (this.state.zone === 4) return r.left > window.innerWidth - 420;\n        return false;\n      });\n      target = region[this.state.focus % Math.max(1, region.length)] || null;\n    }\n    if (target) target.setAttribute('data-scan-selected', 'true');\n  }\n""",
'global selection lifecycle')

once(
"""  zoneBox(i) {\n    const s = this.state;\n    const on = s.zone === i || (i === 3 && s.zone === 2);\n    return 'display:flex;flex-direction:column;height:100%;min-height:0;min-width:0;overflow:hidden;background:#0e1211;'\n      + (i === 3 ? '' : (i === 1 ? 'border-right:1px solid #232927;' : 'border-left:1px solid #232927;'))\n      + (on ? 'box-shadow:inset 0 0 0 2px #74a12e, inset 0 0 26px rgba(116,161,46,.07);' : '');\n  }""",
"""  zoneBox(i) {\n    return 'display:flex;flex-direction:column;height:100%;min-height:0;min-width:0;overflow:hidden;background:#0e1211;'\n      + (i === 3 ? '' : (i === 1 ? 'border-right:1px solid #232927;' : 'border-left:1px solid #232927;'));\n  }""",
'remove whole-zone highlight')

once(
"""  ring(type, i) {\n    const list = this.focusList(), it = list[this.state.focus];\n    return it && it.t === type && it.i === i ? 'box-shadow:0 0 0 2px ' + (this.props.accentColor || '#74a12e') + ';' : '';\n  }""",
"""  ring(type, i) {\n    return '';\n  }""",
'disable mixed local rings')

once(
"""      modeStripStyle: 'display:flex;align-items:stretch;gap:0;min-width:0;overflow:hidden;background:#0e1211;border-bottom:1px solid #232927;padding:0 10px;'\n        + (s.zone === 0 ? 'box-shadow:inset 0 0 0 2px ' + accent + ';' : ''),""",
"""      modeStripStyle: 'display:flex;align-items:stretch;gap:0;min-width:0;overflow:hidden;background:#0e1211;border-bottom:1px solid #232927;padding:0 10px;',""",
'remove whole mode bar highlight')

old_toolbar = """      toolbarStyle: 'display:flex;align-items:center;gap:5px;min-height:46px;padding:4px 10px;flex:1 1 320px;min-width:260px;overflow-x:auto;overflow-y:hidden;'\n        + (s.zone === 2 ? 'box-shadow:inset 0 0 0 2px ' + accent + ';' : ''),"""
new_toolbar = """      toolbarStyle: 'display:flex;align-items:center;gap:5px;min-height:46px;padding:4px 10px;flex:1 1 320px;min-width:260px;overflow-x:auto;overflow-y:hidden;',"""
once(old_toolbar, new_toolbar, 'remove whole toolbar highlight')

for required in ['syncGlobalSelection()', 'data-scan-selected', "ring(type, i) {\n    return '';", "outline: 2px solid #74a12e", 'bestScore']:
    if required not in text:
        raise SystemExit('missing ' + required)

path.write_text(text, encoding='utf-8')
print('global item selection patch applied')
