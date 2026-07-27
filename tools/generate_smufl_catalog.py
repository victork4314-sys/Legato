from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

GLYPHS_URL = 'https://raw.githubusercontent.com/w3c-cg/smufl/gh-pages/metadata/glyphnames.json'
RANGES_URL = 'https://raw.githubusercontent.com/w3c-cg/smufl/gh-pages/metadata/ranges.json'
BRAVURA_URL = 'https://raw.githubusercontent.com/steinbergmedia/bravura/master/redist/bravura_metadata.json'

POPULAR_NAMES = {
    'noteheadWhole','noteheadHalf','noteheadBlack','restWhole','restHalf','restQuarter','rest8th','rest16th','rest32nd',
    'accidentalFlat','accidentalNatural','accidentalSharp','accidentalDoubleFlat','accidentalDoubleSharp',
    'articStaccatoAbove','articStaccatissimoAbove','articTenutoAbove','articAccentAbove','articMarcatoAbove',
    'fermataAbove','breathMarkComma','caesura','ornamentTrill','ornamentMordent','ornamentTurn','ornamentTurnInverted',
    'dynamicP','dynamicMP','dynamicMF','dynamicF','dynamicPP','dynamicFF','dynamicSFZ',
    'gClef','fClef','cClef','unpitchedPercussionClef1','timeSigCommon','timeSigCutCommon',
    'barlineSingle','barlineDouble','barlineFinal','repeatLeft','repeatRight','segno','coda',
    'keyboardPedalPed','keyboardPedalUp','stringsUpBow','stringsDownBow','stringsHarmonic','stringsSnapPizzicatoAbove',
    'brassMuteClosed','brassMuteOpen','wiggleTrillFastest','tremolo1','tremolo2','tremolo3'
}

GROUP_ORDER = [
    'Popular', 'Notes & rests', 'Accidentals & microtones', 'Articulations & dynamics',
    'Ornaments & tremolos', 'Lines, spans & pedals', 'Clefs, staff & meters',
    'Repeats, barlines & structure', 'Text, analysis & fingering', 'Strings',
    'Winds & brass', 'Keyboard, harp & accordion', 'Guitar & tablature', 'Percussion',
    'Vocal, solfège & hand signs', 'Historical, chant & mensural',
    'Electronic, conducting & handbells', 'Specialist & optional'
]

SPECIALIST_RE = re.compile(
    r'chant|mensural|medieval|renaissance|daseian|kievan|byzantine|white mensural|black mensural|'
    r'plainchant|isorhythmic|figured bass supplement|kodály|kodaly|simplified music notation|'
    r'are[l-]?ezgi|sagittal|wilson|hewm|johnston|stockhausen|turkish folk|persian|'
    r'solfège|solfege|handbell|electronic|conducting|analytics', re.I
)


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={'User-Agent': 'Legato catalog generator'})
    with urllib.request.urlopen(req, timeout=90) as response:
        return json.load(response)


def humanize(name: str) -> str:
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    text = text.replace('_', ' ').replace('  ', ' ').strip()
    return text[:1].upper() + text[1:]


def codepoint_char(value: str | None) -> str:
    if not value:
        return ''
    try:
        return chr(int(value.replace('U+', ''), 16))
    except Exception:
        return ''


def group_for(range_desc: str, name: str, desc: str, optional: bool) -> str:
    t = f'{range_desc} {name} {desc}'.lower()
    if optional:
        return 'Specialist & optional'
    if SPECIALIST_RE.search(t):
        return 'Historical, chant & mensural' if re.search(r'chant|mensural|medieval|renaissance|daseian|kievan|byzantine|plainchant', t) else 'Specialist & optional'
    if re.search(r'notehead|note name|notes and rests|rests|stem|flag|beam|augmentation dot', t):
        return 'Notes & rests'
    if re.search(r'accidental|microtonal|quarter-tone|quarter tone|comma|enharmonic', t):
        return 'Accidentals & microtones'
    if re.search(r'articulation|fermata|breath|caesura|dynamic|expressive', t):
        return 'Articulations & dynamics'
    if re.search(r'ornament|tremolo|wiggle|arpeggi', t):
        return 'Ornaments & tremolos'
    if re.search(r'multi-segment|line|pedal|octave|tuplet|gliss|portamento|hairpin', t):
        return 'Lines, spans & pedals'
    if re.search(r'clef|staff|time signature|meter|individual notes|standard accidentals', t):
        return 'Clefs, staff & meters'
    if re.search(r'barline|repeat|navigation|system divider|repeat ending|rehearsal', t):
        return 'Repeats, barlines & structure'
    if re.search(r'text|fingering|figured bass|analytics|scale degree|function theory|roman numeral', t):
        return 'Text, analysis & fingering'
    if re.search(r'string|bow|pizzicato|harmonic', t):
        return 'Strings'
    if re.search(r'wind|brass|mute|horn|woodwind', t):
        return 'Winds & brass'
    if re.search(r'keyboard|harp|accordion|harpsichord|organ', t):
        return 'Keyboard, harp & accordion'
    if re.search(r'guitar|tablature|fret|lute', t):
        return 'Guitar & tablature'
    if re.search(r'percussion|drum|mallet|beater|pictogram', t):
        return 'Percussion'
    if re.search(r'vocal|vowel|solf|hand sign|lyrics', t):
        return 'Vocal, solfège & hand signs'
    if re.search(r'electronic|conducting|handbell', t):
        return 'Electronic, conducting & handbells'
    return 'Specialist & optional'


def accidental_cents(name: str, desc: str) -> float | None:
    t = f'{name} {desc}'.lower()
    if 'natural' in t and not any(k in t for k in ('sharp', 'flat', 'up', 'down')):
        return 0
    direction = -1 if re.search(r'flat|down|lower', t) else (1 if re.search(r'sharp|up|raise', t) else 0)
    if not direction:
        return None
    if 'triple' in t: return 300 * direction
    if 'double' in t: return 200 * direction
    if re.search(r'three.?quarter|three quarters', t): return 150 * direction
    if re.search(r'quarter.?tone|quarter tone|half sharp|half flat|koron|sori', t): return 50 * direction
    if re.search(r'five.?sixth', t): return (500/3) * direction
    if re.search(r'five.?twelfth', t): return (250/3) * direction
    if re.search(r'one.?third|third.?tone', t): return (200/3) * direction
    if re.search(r'one.?sixth|sixth.?tone', t): return (100/3) * direction
    if re.search(r'one.?twelfth|twelfth.?tone', t): return (50/3) * direction
    if re.search(r'one.?ninth|ninth.?tone', t): return (200/9) * direction
    if 'comma' in t:
        nums = re.findall(r'(?<![a-z])(\d+)', t)
        commas = int(nums[0]) if nums else 1
        return 21.506 * commas * direction
    if 'sharp' in t or 'flat' in t:
        return 100 * direction
    return None


def dynamic_velocity(name: str, desc: str) -> int | None:
    t = f'{name} {desc}'.lower()
    table = [
        ('pppppp', 8), ('ffffff', 127), ('ppppp', 12), ('fffff', 126), ('pppp', 18), ('ffff', 124),
        ('ppp', 28), ('fff', 116), ('pp', 40), ('ff', 104), ('mp', 64), ('mf', 80), ('sfz', 122),
        ('sffz', 126), ('rfz', 118), ('fp', 92), ('fz', 114), ('niente', 5)
    ]
    for token, value in table:
        if token in t: return value
    if re.search(r'(^|\W)p($|\W)', t): return 52
    if re.search(r'(^|\W)f($|\W)', t): return 94
    return None


def infer_semantics(name: str, desc: str, range_desc: str) -> dict:
    t = f'{name} {desc} {range_desc}'.lower()
    sem: dict = {'placement': 'event', 'kind': 'glyph', 'audible': False}

    if 'notehead' in t:
        sem.update(placement='note', kind='notehead')
        if re.search(r'harmonic|diamond', t): sem.update(audible=True, sound='harmonic')
        elif re.search(r'cross|x notehead|slash|dead', t): sem.update(audible=True, sound='muted')
        return sem
    if 'rest' in t and 'breath' not in t:
        sem.update(placement='note', kind='rest')
        return sem
    if 'accidental' in t or re.search(r'quarter.?tone|comma', t):
        cents = accidental_cents(name, desc)
        sem.update(placement='note', kind='accidental', audible=cents is not None, sound='pitch', cents=cents)
        return sem
    if re.search(r'clef', t):
        sem.update(placement='event', kind='clef')
        return sem
    if re.search(r'time sig|time signature|meter', t):
        sem.update(placement='event', kind='meter')
        return sem
    if re.search(r'barline|repeat|segno|coda|fine|dal segno|da capo|ending', t):
        sem.update(placement='structure', kind='structure', audible=True, sound='play-order')
        return sem
    if re.search(r'dynamic', t):
        vel = dynamic_velocity(name, desc)
        sem.update(placement='event', kind='dynamic', audible=vel is not None, sound='dynamic', velocity=vel)
        return sem
    if re.search(r'hairpin|crescendo|diminuendo', t):
        direction = 'down' if re.search(r'diminuendo|decrescendo', t) else 'up'
        sem.update(placement='span', kind='hairpin', audible=True, sound='hairpin', direction=direction)
        return sem
    if re.search(r'fermata', t):
        hold = 1.5 if 'short' in t else (3.0 if ('long' in t or 'very long' in t) else 2.0)
        sem.update(placement='event', kind='hold', audible=True, sound='fermata', factor=hold)
        return sem
    if re.search(r'breath mark', t):
        sem.update(placement='event', kind='hold', audible=True, sound='breath', seconds=.18)
        return sem
    if re.search(r'caesura', t):
        sem.update(placement='event', kind='hold', audible=True, sound='caesura', seconds=.45)
        return sem
    if re.search(r'artic', t) or any(x in t for x in ('staccato','tenuto','marcato','accent','portato','stress','unstress')):
        profile = 'normal'
        if 'staccatissimo' in t: profile = 'staccatissimo'
        elif 'staccato' in t: profile = 'staccato'
        elif 'tenuto' in t: profile = 'tenuto'
        elif 'marcato' in t: profile = 'marcato'
        elif 'accent' in t: profile = 'accent'
        elif 'portato' in t: profile = 'portato'
        elif 'unstress' in t: profile = 'unstress'
        elif 'stress' in t: profile = 'stress'
        sem.update(placement='note', kind='articulation', audible=profile != 'normal', sound='articulation', profile=profile)
        return sem
    if re.search(r'ornament|trill|mordent|turn|shake|cadence|tremblement', t):
        pattern = 'trill'
        if 'mordent' in t: pattern = 'mordent-down' if re.search(r'lower|inverted', t) else 'mordent-up'
        elif 'inverted turn' in t: pattern = 'turn-inverted'
        elif 'turn' in t: pattern = 'turn'
        elif 'shake' in t: pattern = 'shake'
        sem.update(placement='note', kind='ornament', audible=True, sound='ornament', pattern=pattern)
        return sem
    if re.search(r'tremolo', t):
        strokes = 3 if re.search(r'3|three|third', t) else (2 if re.search(r'2|two|second', t) else 1)
        sem.update(placement='note', kind='tremolo', audible=True, sound='tremolo', strokes=strokes)
        return sem
    if re.search(r'gliss|portamento|slide|scoop|fall|doit|plop|rip|smear|bend|flip', t):
        effect = next((x for x in ('glissando','portamento','scoop','fall','doit','plop','rip','smear','bend','flip','slide') if x in t), 'slide')
        placement = 'span' if effect in ('glissando','portamento') or 'line' in t else 'note'
        sem.update(placement=placement, kind='pitch-effect', audible=True, sound='pitch-effect', effect=effect)
        return sem
    if re.search(r'pedal', t):
        sem.update(placement='span' if re.search(r'line|pedal ped|sustain', t) else 'event', kind='pedal', audible=True, sound='pedal')
        return sem
    if re.search(r'ottava|octave|8va|8vb|15ma|15mb', t):
        shift = -24 if '15mb' in t else (24 if '15ma' in t else (-12 if re.search(r'8vb|bassa|down', t) else 12))
        sem.update(placement='span', kind='octave-line', audible=True, sound='octave', semitones=shift)
        return sem
    if re.search(r'pizzicato|pizz\.|snap pizz', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='pizzicato')
        return sem
    if re.search(r'arco', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='arco')
        return sem
    if re.search(r'harmonic', t):
        sem.update(placement='note', kind='technique', audible=True, sound='harmonic')
        return sem
    if re.search(r'mute closed|muted|con sord|sordino|stopped', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='muted')
        return sem
    if re.search(r'mute open|senza sord|open', t) and re.search(r'mute|brass|string', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='open')
        return sem
    if re.search(r'sul pont|ponticello', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='sul-ponticello')
        return sem
    if re.search(r'sul tasto|flautando', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='sul-tasto')
        return sem
    if re.search(r'col legno', t):
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique='col-legno')
        return sem
    if re.search(r'flutter|growl|slap tongue|tongue ram|air sound|breath noise', t):
        technique = 'flutter' if 'flutter' in t else ('growl' if 'growl' in t else ('slap' if 'slap' in t else 'air'))
        sem.update(placement='event', kind='technique', audible=True, sound='technique', technique=technique)
        return sem
    if re.search(r'up bow|down bow|bowed', t):
        sem.update(placement='note', kind='bowing', audible=True, sound='bowing', direction='up' if 'up bow' in t else 'down')
        return sem
    if re.search(r'let ring|l\.v\.', t):
        sem.update(placement='span', kind='let-ring', audible=True, sound='let-ring')
        return sem
    if re.search(r'vibrato', t):
        sem.update(placement='span', kind='vibrato', audible=True, sound='vibrato')
        return sem
    if re.search(r'ritard|rallent|accelerando|tempo', t):
        sem.update(placement='span' if re.search(r'ritard|rallent|accelerando', t) else 'event', kind='tempo', audible=True, sound='tempo', direction='up' if 'accelerando' in t else 'down')
        return sem
    if re.search(r'percussion|drum|mallet|beater|cymbal|gong|tambourine|triangle', t):
        sem.update(placement='note', kind='percussion', audible=True, sound='percussion', instrument=humanize(name))
        return sem
    if re.search(r'fingering|figured bass|analytics|roman|scale degree|lyrics|text', t):
        sem.update(placement='event', kind='text')
        return sem
    if re.search(r'line|bracket|tie|slur|phrase', t):
        kind = 'slur' if 'slur' in t else ('tie' if 'tie' in t else 'line')
        sem.update(placement='span', kind=kind, audible=kind in ('slur','tie'), sound=kind if kind in ('slur','tie') else None)
        return sem
    return sem


def main() -> None:
    out_path = Path('smufl-catalog.js')
    glyphs = fetch_json(GLYPHS_URL)
    ranges = fetch_json(RANGES_URL)
    bravura = fetch_json(BRAVURA_URL)

    range_for: dict[str, tuple[str, str]] = {}
    for rid, data in ranges.items():
        desc = data.get('description', humanize(rid))
        for name in data.get('glyphs', []):
            range_for[name] = (rid, desc)

    entries: list[dict] = []
    seen: set[str] = set()
    for name, data in glyphs.items():
        seen.add(name)
        rid, rdesc = range_for.get(name, ('unclassified', 'Unclassified SMuFL'))
        desc = data.get('description') or humanize(name)
        glyph = codepoint_char(data.get('codepoint'))
        sem = infer_semantics(name, desc, rdesc)
        group = group_for(rdesc, name, desc, False)
        tier = 'popular' if name in POPULAR_NAMES else ('specialist' if SPECIALIST_RE.search(rdesc + ' ' + name) else 'expanded')
        entries.append({
            'id': name, 'label': desc, 'glyph': glyph, 'codepoint': data.get('codepoint',''),
            'range': rdesc, 'rangeId': rid, 'group': group, 'tier': tier,
            **sem
        })

    optional = bravura.get('optionalGlyphs', {}) or {}
    for name, data in optional.items():
        if name in seen:
            continue
        desc = humanize(name)
        glyph = codepoint_char(data.get('codepoint'))
        sem = infer_semantics(name, desc, 'Bravura optional glyphs')
        entries.append({
            'id': name, 'label': desc, 'glyph': glyph, 'codepoint': data.get('codepoint',''),
            'range': 'Bravura optional glyphs', 'rangeId': 'bravuraOptional',
            'group': group_for('Bravura optional glyphs', name, desc, True), 'tier': 'specialist',
            'optional': True, **sem
        })

    entries.sort(key=lambda e: (GROUP_ORDER.index(e['group']) if e['group'] in GROUP_ORDER else 999, e['range'], e['label']))
    payload = {
        'specification': 'SMuFL metadata gh-pages plus Bravura optional glyphs',
        'glyphCount': len(entries), 'rangeCount': len(ranges),
        'groups': GROUP_ORDER, 'glyphs': entries,
    }
    text = 'window.LEGATO_SMUFL_CATALOG=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n'
    out_path.write_text(text, encoding='utf-8')
    print(f'Wrote {out_path} with {len(entries)} glyphs across {len(ranges)} SMuFL ranges')


if __name__ == '__main__':
    main()
