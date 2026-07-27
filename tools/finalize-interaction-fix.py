from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')


def one(old, new, label):
    global t
    count = t.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    t = t.replace(old, new, 1)

if 'Tie point two is waiting for A' not in t:
    one("      case 'confirm': P ? this.clickPointer() : this.enterNote(); break;",
        "      case 'confirm':\n        if (P) { this.clickPointer(); break; }\n        if (s.tieFrom) {\n          const target = this.selected();\n          if (target && target.id !== s.tieFrom) this.finishTie(target);\n          else this.setState({ spoken: 'Tie point two is waiting for A — move to the immediately following note of the same pitch' });\n          break;\n        }\n        this.enterNote(); break;",
        'controller tie confirmation')
    one("    if (s.zone !== 3 && !s.ptrOn) {",
        "    if (s.tieFrom && action === 'delete') return this.setState({ tieFrom: null, spoken: 'Tie cancelled' });\n    if (s.zone !== 3 && !s.ptrOn) {",
        'tie cancellation')
    one("      if (zone === 0) return !el.closest('[data-scroll=\"players\"],[data-scroll=\"toolbar\"],[data-scroll=\"props\"]') && el.getBoundingClientRect().top < 125;",
        "      if (zone === 0) return el.getAttribute('data-score-editor-shell') === 'true' || (!el.closest('[data-scroll=\"players\"],[data-scroll=\"toolbar\"],[data-scroll=\"props\"]') && el.getBoundingClientRect().top < 125);",
        'score gateway scan order')
    one("      titleStyle: 'font-family:\\'Source Serif 4\\',Georgia,serif;font-size:22px;font-weight:600;color:var(--ink);letter-spacing:.005em;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;cursor:pointer;padding:2px 8px;',",
        "      titleStyle: 'font-family:var(--score-font);font-size:22px;font-weight:600;color:var(--ink);letter-spacing:.005em;line-height:1.15;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;cursor:pointer;padding:2px 8px;',",
        'score title font')
    one("      selectionCount: s.selId ? 'NOTE SELECTED' : 'CURSOR',",
        "      selectionCount: s.tieFrom ? 'CHOOSE TIE END' : (s.selId ? 'NOTE SELECTED' : 'CURSOR'),",
        'tie status')

# Prove the clarified untouched behavior is still exact.
for marker in [
  "case 'previous-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(-1); break; } this.cycleVisibleZone(-1); break;",
  "case 'next-zone': if (s.zone === 3 && s.selId) { this.nudgeAccidental(1); break; } this.cycleVisibleZone(1); break;",
  "button4: 'previous-zone', button5: 'next-zone'"
]:
    if marker not in t:
        raise SystemExit('Untouched accidental/bumper behavior changed: ' + marker)

p.write_text(t, encoding='utf-8')
print('Final interaction edge cases applied')
