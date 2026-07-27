from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')

old = """      case 'confirm':
        if (P) { this.clickPointer(); break; }
        if (s.spanDraft) { this.finishScoreSpan(); break; }
        if (s.scoreObjectId) { this.editSelectedScoreObject(); break; }
        if (s.tieFrom) {
          const target = this.selected();
          if (target && target.id !== s.tieFrom) this.finishTie(target);
          else this.setState({ spoken: 'Tie point two is waiting for A — move to the immediately following note of the same pitch' });
          break;
        }
        this.enterNote(); break;
"""

new = """      case 'confirm':
        if (s.spanDraft) { this.finishScoreSpan(); break; }
        if (s.tieFrom) {
          const target = this.selected();
          if (target && target.id !== s.tieFrom) this.finishTie(target);
          else this.setState({ spoken: 'Tie point two is waiting for A — move to the immediately following note of the same pitch' });
          break;
        }
        if (P) { this.clickPointer(); break; }
        if (s.scoreObjectId) { this.editSelectedScoreObject(); break; }
        this.enterNote(); break;
"""

if new in t:
    print('Notation confirm priority already repaired')
    raise SystemExit(0)

count = t.count(old)
if count != 1:
    raise SystemExit(f'notation confirm priority: expected 1 match, found {count}')

p.write_text(t.replace(old, new, 1), encoding='utf-8')
print('Notation confirm priority repaired')
