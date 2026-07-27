from pathlib import Path

source = Path('tools/generate_smufl_catalog.py').read_text(encoding='utf-8')
old = '''    if re.search(r'dynamic', t):
        vel = dynamic_velocity(name, desc)
        sem.update(placement='event', kind='dynamic', audible=vel is not None, sound='dynamic', velocity=vel)
        return sem
    if re.search(r'hairpin|crescendo|diminuendo', t):
        direction = 'down' if re.search(r'diminuendo|decrescendo', t) else 'up'
        sem.update(placement='span', kind='hairpin', audible=True, sound='hairpin', direction=direction)
        return sem
'''
new = '''    if re.search(r'hairpin|crescendo|diminuendo', t):
        direction = 'down' if re.search(r'diminuendo|decrescendo', t) else 'up'
        sem.update(placement='span', kind='hairpin', audible=True, sound='hairpin', direction=direction)
        return sem
    if re.search(r'dynamic', t):
        vel = dynamic_velocity(name, desc)
        sem.update(placement='event', kind='dynamic', audible=vel is not None, sound='dynamic', velocity=vel)
        return sem
'''
if source.count(old) != 1:
    raise SystemExit('Could not locate dynamic/hairpin inference order')
source = source.replace(old, new, 1)
exec(compile(source, 'tools/generate_smufl_catalog.py', 'exec'), {'__name__': '__main__'})
