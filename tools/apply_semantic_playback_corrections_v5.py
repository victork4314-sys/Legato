from pathlib import Path

source = Path('tools/apply_semantic_playback_corrections_v4.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/apply_semantic_playback_corrections_v4.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, found {count}')
    text = text.replace(old, new, 1)

replace_once(
"      if (electronic && electronic.playback) {\n        if (electronic.playback.electronic === 'mute') return;\n        if (electronic.playback.electronic === 'fade') vel = Math.round(vel * .58);\n      }",
"      if (electronic && electronic.playback) {\n        const effect = electronic.playback.electronic;\n        if (effect === 'mute' || effect === 'stop') return;\n        if (effect === 'fade') vel = Math.round(vel * .58);\n        if (effect === 'level' && electronic.playback.level != null) vel = Math.round(vel * Math.max(0, Math.min(100, Number(electronic.playback.level))) / 100);\n      }",
'electronic mute stop and level playback')

replace_once(
"    (s.scoreEvents || []).filter(ev => ev.type === 'hold' && ev.p >= start - .0005 && ev.p < end - .0005 && ev.playback).forEach(ev => {",
"    (s.scoreEvents || []).filter(ev => ev.type === 'electronic' && ev.p >= start - .0005 && ev.p < end - .0005 && ev.playback && ev.playback.electronic === 'pause').forEach(ev => { seconds += Math.max(0, Number(ev.playback.seconds) || 60 / this.pointTempoAt(ev.p, s)); });\n    (s.scoreEvents || []).filter(ev => ev.type === 'hold' && ev.p >= start - .0005 && ev.p < end - .0005 && ev.playback).forEach(ev => {",
'electronic pause timing')

required = [
    "effect === 'mute' || effect === 'stop'",
    "effect === 'level' && electronic.playback.level != null",
    "ev.playback.electronic === 'pause'",
    "button4: 'previous-zone', button5: 'next-zone'",
    'const BUMPER_COMBO_MS = 120;'
]
for marker in required:
    if marker not in text:
        raise SystemExit('Missing electronic playback marker: ' + marker)

path.write_text(text, encoding='utf-8')
print('Enforced official electronic mute, stop, level, and pause controls')
