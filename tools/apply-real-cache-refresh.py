from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
old = '<script src="./support.js?v=20260727-rests-ties-focus-fonts-1"></script>'
new = '''<meta name="legato-build" content="20260727-real-cache-refresh-1">
<script src="./cache-refresh.js?v=20260727-real-cache-refresh-1"></script>
<script src="./support.js?v=20260727-real-cache-refresh-1"></script>'''

if new in text:
    print('Real cache refresh already wired')
    raise SystemExit(0)

count = text.count(old)
if count != 1:
    raise SystemExit(f'Expected exactly one current runtime tag, found {count}')

text = text.replace(old, new, 1)
path.write_text(text, encoding='utf-8')

for required in [
    'meta name="legato-build" content="20260727-real-cache-refresh-1"',
    'cache-refresh.js?v=20260727-real-cache-refresh-1',
    'support.js?v=20260727-real-cache-refresh-1'
]:
    if required not in text:
        raise SystemExit('Missing cache-refresh marker: ' + required)

if text.count('cache-refresh.js?v=') != 1:
    raise SystemExit('Cache watcher must be loaded exactly once')

print('Real cache refresh wired successfully')
