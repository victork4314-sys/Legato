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

repairs = [
    (
        '<div style="width: min(1000px, 94vw); max-height: 84vh; display: grid; grid-template-columns: 216px 1fr; border: 1px solid var(--border-strong); border-radius: 6px; background: var(--panel); box-shadow: 0 40px 110px rgba(0,0,0,.7); overflow: hidden; animation: ringIn .1s ease-out;">',
        '<div style="width: min(1000px, 94vw); height: min(760px, 84vh); max-height: 84vh; display: grid; grid-template-columns: 216px 1fr; border: 1px solid var(--border-strong); border-radius: 6px; background: var(--panel); box-shadow: 0 40px 110px rgba(0,0,0,.7); overflow: hidden; animation: ringIn .1s ease-out;">',
        'Y modal fixed height'
    ),
    (
        '<div data-scroll="halocats" style="border-right: 1px solid var(--border); background: var(--raised); padding: 12px 10px; overflow: auto;">',
        '<div data-scroll="halocats" style="border-right: 1px solid var(--border); background: var(--raised); padding: 12px 10px; min-height: 0; overflow: auto;">',
        'Y category scrolling'
    ),
    (
        '''        </div>
        <div style="display: flex; flex-direction: column; min-width: 0;">
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 13px 16px; border-bottom: 1px solid var(--border);">''',
        '''        </div>
        <div style="display: flex; flex-direction: column; min-width: 0; min-height: 0;">
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 13px 16px; border-bottom: 1px solid var(--border);">''',
        'Y content flex shrink'
    ),
    (
        '<div data-scroll="halo" style="flex: 1; overflow: auto; padding: 12px 14px 16px;">',
        '<div data-scroll="halo" style="flex: 1; min-height: 0; overflow: auto; padding: 12px 14px 16px;">',
        'Y command pane scrolling'
    )
]
marker = "path.write_text(text, encoding='utf-8')"
if marker not in source:
    raise SystemExit('Could not insert Y modal layout repairs')
injection = '\n'.join(f"replace_once({before!r}, {after!r}, {label!r})" for before, after, label in repairs)
source = source.replace(marker, injection + '\n\n' + marker, 1)
exec(compile(source, str(source_path), 'exec'), {'__name__': '__main__'})
