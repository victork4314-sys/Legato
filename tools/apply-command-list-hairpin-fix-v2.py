from pathlib import Path

source_path = Path('tools/apply-command-list-hairpin-fix.py')
source = source_path.read_text(encoding='utf-8')
old = '''replace_once('<div onClick="{{ h.onSelect }}" data-ptr="{{ h.name }}" style="{{ h.style }}" style-hover="border-color:var(--border-hover)">', '<div onClick="{{ h.onSelect }}" data-ptr="{{ h.name }}" data-halo-item="{{ h.index }}" style="{{ h.style }}" style-hover="border-color:var(--border-hover)">', 'halo item DOM marker')'''
new = '''replace_once("""              <sc-for list="{{ haloItems }}" as="h" hint-placeholder-count="16">
                <div onClick="{{ h.onSelect }}" data-ptr="{{ h.name }}" style="{{ h.style }}" style-hover="border-color:var(--border-hover)">""", """              <sc-for list="{{ haloItems }}" as="h" hint-placeholder-count="16">
                <div onClick="{{ h.onSelect }}" data-ptr="{{ h.name }}" data-halo-item="{{ h.index }}" style="{{ h.style }}" style-hover="border-color:var(--border-hover)">""", 'halo item DOM marker')'''
if old not in source:
    if new not in source:
        raise SystemExit('Could not anchor the Y command tile guard')
else:
    source = source.replace(old, new, 1)
exec(compile(source, str(source_path), 'exec'), {'__name__': '__main__'})
