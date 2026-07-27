from pathlib import Path
import json, re

source = Path('tools/correct_smufl_semantics_v4.py').read_text(encoding='utf-8')
exec(compile(source, 'tools/correct_smufl_semantics_v4.py', 'exec'), {'__name__': '__main__', 'Path': Path})

path = Path('smufl-catalog.js')
raw = path.read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
data = json.loads(raw[len(prefix):].strip()[:-1])

for g in data['glyphs']:
    ident = g.get('id','')
    if ident in ('elecMute','elecMicrophoneMute'):
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='mute')
    elif ident in ('elecUnmute','elecMicrophoneUnmute'):
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='unmute')
    elif ident.startswith(('elecVolumeLevel','elecMIDIController')):
        match = re.search(r'(0|20|40|60|80|100)$', ident)
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='level', level=int(match.group(1)) if match else 100)
    elif ident == 'elecPlay':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='play')
    elif ident == 'elecStop':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='stop')
    elif ident == 'elecPause':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='pause', seconds=1.0)
    elif ident == 'elecFastForward':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='fast-forward')
    elif ident == 'elecRewind':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='rewind')
    elif ident == 'elecReplay':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='replay')
    elif ident == 'elecLoop':
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='loop')
    elif ident in ('elecSkipBackwards','elecSkipForwards'):
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='skip-backward' if 'Backwards' in ident else 'skip-forward')
    elif ident in ('elecAudioMono','elecAudioStereo') or ident.startswith('elecAudioChannels'):
        nums = {'One':1,'Two':2,'Three':3,'ThreeFrontal':3,'ThreeSurround':3,'Four':4,'Five':5,'Six':6,'Seven':7,'Eight':8}
        channels = 1 if ident == 'elecAudioMono' else (2 if ident == 'elecAudioStereo' else next((v for k,v in nums.items() if ident.endswith(k)), 2))
        g.update(placement='event', kind='electronic', audible=True, sound='electronic', electronic='channels', channels=channels)

by_id = {g['id']: g for g in data['glyphs']}
for ident, effect in (('elecMute','mute'),('elecUnmute','unmute'),('elecVolumeLevel40','level'),('elecPlay','play'),('elecStop','stop')):
    if by_id[ident].get('electronic') != effect:
        raise SystemExit('Electronic correction failed for ' + ident)

path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print('Prioritized official electronic control semantics')
