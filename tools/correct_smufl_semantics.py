from pathlib import Path
import json, re

path = Path('smufl-catalog.js')
raw = path.read_text(encoding='utf-8')
prefix = 'window.LEGATO_SMUFL_CATALOG='
data = json.loads(raw[len(prefix):].strip()[:-1])

semantic_keys = {
    'placement','kind','audible','sound','cents','velocity','profile','pattern','strokes','effect',
    'technique','direction','factor','seconds','semitones','instrument','electronic','needsChoice'
}

def set_sem(g, placement, kind, audible=False, sound=None, **extra):
    for key in semantic_keys:
        g.pop(key, None)
    g.update(placement=placement, kind=kind, audible=bool(audible))
    if sound is not None:
        g['sound'] = sound
    g.update({k:v for k,v in extra.items() if v is not None})


def dynamic_semantics(g, text):
    ident = g['id']
    clean = re.sub(r'Small$', '', ident)
    low = text.lower()
    if re.search(r'hairpin|crescendo|diminuendo|decrescendo', low):
        direction = 'down' if re.search(r'diminuendo|decrescendo', low) else 'up'
        set_sem(g, 'span', 'hairpin', True, 'hairpin', direction=direction)
        return
    if 'messadivoce' in clean.lower() or 'messa di voce' in low:
        set_sem(g, 'span', 'hairpin', True, 'hairpin', direction='swell')
        return
    if re.search(r'combinedseparator|parenthes|hyphen|slash|colon|space', low) or clean in {'dynamicZ','dynamicM','dynamicR','dynamicS'}:
        set_sem(g, 'event', 'glyph', False)
        return
    direct = {
        'dynamicP':52,'dynamicPP':40,'dynamicPPP':28,'dynamicPPPP':18,'dynamicPPPPP':12,'dynamicPPPPPP':8,
        'dynamicF':94,'dynamicFF':104,'dynamicFFF':116,'dynamicFFFF':124,'dynamicFFFFF':126,'dynamicFFFFFF':127,
        'dynamicMP':64,'dynamicMF':80,'dynamicFP':94,'dynamicPF':64,'dynamicFZ':114,'dynamicSF':118,
        'dynamicSFZ':122,'dynamicSFFZ':126,'dynamicSFP':116,'dynamicSFPP':108,'dynamicRF':112,'dynamicRFZ':118,
        'dynamicNiente':5
    }
    if clean in direct:
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=direct[clean], profile=clean[7:].lower())
        return
    if re.search(r'sforz|sforzat|forzando|rinforz|rinforzat', low):
        vel = 118
        if 'pianissimo' in low: vel = 92
        elif 'piano' in low: vel = 104
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=vel, profile='force')
        return
    if 'forte-piano' in low or 'fortepiano' in low:
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=96, profile='fp')
        return
    if 'mezzo-forte' in low or ('mezzo' in low and 'forte' in low):
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=80, profile='mf')
        return
    if 'mezzo-piano' in low or ('mezzo' in low and 'piano' in low):
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=64, profile='mp')
        return
    if 'forte' in low:
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=94, profile='f')
        return
    if 'piano' in low:
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=52, profile='p')
        return
    if 'mezzo' in low:
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=70, profile='mezzo')
        return
    if 'niente' in low:
        set_sem(g, 'event', 'dynamic', True, 'dynamic', velocity=5, profile='niente')
        return
    set_sem(g, 'event', 'glyph', False)


def technique_name(text):
    low = text.lower()
    pairs = [
        ('pizz', 'pizzicato'), ('arco', 'arco'), ('sul pont', 'sul-ponticello'), ('ponticello', 'sul-ponticello'),
        ('sul tasto', 'sul-tasto'), ('flautando', 'sul-tasto'), ('col legno', 'col-legno'),
        ('behind bridge', 'behind-bridge'), ('scrape', 'scrape'), ('chop', 'chop'),
        ('flutter', 'flutter'), ('growl', 'growl'), ('slap', 'slap'), ('tongue ram', 'slap'),
        ('air sound', 'air'), ('breath noise', 'air'), ('key click', 'click'), ('tongue click', 'click'),
        ('finger click', 'click'), ('snap', 'snap'), ('harmonic', 'harmonic'), ('stopped', 'muted'),
        ('mute', 'muted'), ('sord', 'muted'), ('open', 'open')
    ]
    for token, value in pairs:
        if token in low:
            return value
    return None

for g in data['glyphs']:
    ident = g.get('id','')
    label = g.get('label','')
    range_name = g.get('range','')
    text = f'{ident} {label}'
    low = text.lower()
    range_low = range_name.lower()

    if ident.startswith(('control','text')):
        set_sem(g, 'event', 'glyph', False)
        continue
    if re.search(r'combining|component|separator|parenthes|bracket (start|end)|stem (up|down|left|right)|for stem', low) and not re.search(r'actual|notehead', low):
        set_sem(g, 'event', 'glyph', False)
        continue

    if ident.startswith('breathMark') or 'breath mark' in low:
        set_sem(g, 'event', 'hold', True, 'breath', seconds=.18)
        continue
    if ident.startswith('caesura') or 'caesura' in low:
        set_sem(g, 'event', 'hold', True, 'caesura', seconds=.45)
        continue
    if ident.startswith('fermata') or 'fermata' in low:
        factor = 1.5 if 'short' in low else (3.0 if 'long' in low or 'very long' in low else 2.0)
        set_sem(g, 'event', 'hold', True, 'fermata', factor=factor)
        continue

    if re.search(r'gracenote|grace note|acciaccatura|appoggiatura', low):
        pattern = 'acciaccatura' if re.search(r'acciacc|slash', low) else 'appoggiatura'
        direction = 'down' if re.search(r'below|down', low) else 'up'
        set_sem(g, 'note', 'grace', True, 'grace', pattern=pattern, direction=direction)
        continue

    if ident.startswith('dynamic') or range_low == 'dynamics':
        dynamic_semantics(g, text)
        continue

    if 'clef' in low:
        semitones = -24 if re.search(r'15mb|quindicesima bassa', low) else (24 if re.search(r'15ma|quindicesima alta', low) else (-12 if re.search(r'8vb|ottava bassa', low) else (12 if re.search(r'8va|ottava alta', low) else 0)))
        set_sem(g, 'event', 'clef', bool(semitones), 'octave' if semitones else None, semitones=semitones or None)
        continue

    if ident.startswith('accidental') or 'accidental' in low:
        if re.search(r'enharmonic|equals|almost equal|tilde', low):
            set_sem(g, 'note', 'accidental', False)
        else:
            cents = g.get('cents')
            set_sem(g, 'note', 'accidental', cents is not None, 'pitch' if cents is not None else None, cents=cents)
        continue

    if re.search(r'notehead|noteshape|mensuralnotehead', low):
        if 'cluster' in low:
            set_sem(g, 'note', 'notehead', False)
        elif re.search(r'dead|muted|cross notehead', low):
            set_sem(g, 'note', 'notehead', True, 'muted', technique='muted')
        elif 'harmonic' in low:
            set_sem(g, 'note', 'notehead', True, 'harmonic', technique='harmonic')
        else:
            set_sem(g, 'note', 'notehead', False)
        continue

    if re.search(r'tremolo', low):
        strokes = 3 if re.search(r'3|three|third', low) else (2 if re.search(r'2|two|second', low) else 1)
        set_sem(g, 'note', 'tremolo', True, 'tremolo', strokes=strokes)
        continue
    if re.search(r'ornament|trill|mordent|turn|shake|tremblement', low):
        pattern = 'trill'
        if 'mordent' in low: pattern = 'mordent-down' if re.search(r'lower|inverted', low) else 'mordent-up'
        elif 'inverted turn' in low: pattern = 'turn-inverted'
        elif 'turn' in low: pattern = 'turn'
        elif 'shake' in low: pattern = 'shake'
        set_sem(g, 'note', 'ornament', True, 'ornament', pattern=pattern)
        continue
    if re.search(r'staccatissimo|staccato|tenuto|marcato|accent|portato|stress|unstress', low):
        profile = 'staccatissimo' if 'staccatissimo' in low else ('staccato' if 'staccato' in low else ('tenuto' if 'tenuto' in low else ('marcato' if 'marcato' in low else ('accent' if 'accent' in low else ('portato' if 'portato' in low else ('unstress' if 'unstress' in low else 'stress'))))))
        set_sem(g, 'note', 'articulation', True, 'articulation', profile=profile)
        continue
    if re.search(r'gliss|portamento', low):
        set_sem(g, 'span', 'pitch-effect', True, 'pitch-effect', effect='portamento' if 'portamento' in low else 'glissando')
        continue
    if re.search(r'scoop|fall|doit|plop|rip|smear|bend|flip|slide', low):
        effect = next((x for x in ('scoop','fall','doit','plop','rip','smear','bend','flip','slide') if x in low), 'slide')
        set_sem(g, 'note', 'pitch-effect', True, 'pitch-effect', effect=effect)
        continue
    if 'vibrato' in low:
        set_sem(g, 'span', 'vibrato', True, 'vibrato')
        continue

    tech = technique_name(text)
    if tech and (re.search(r'string|brass|wind|vocal|guitar|bow|mute|pizz|arco', low) or any(x in range_low for x in ('string','brass','wind','vocal','guitar'))):
        placement = 'note' if re.search(r'up bow|down bow|harmonic note|snap pizz', low) else 'event'
        kind = 'bowing' if re.search(r'up bow|down bow', low) else 'technique'
        sound = 'bowing' if kind == 'bowing' else ('harmonic' if tech == 'harmonic' else 'technique')
        set_sem(g, placement, kind, True, sound, technique=tech)
        continue

    instrument_words = re.compile(r'timpani|drum|cymbal|gong|bell|triangle|wood ?block|agogo|tambourine|siren|whistle|claves|castanet|maraca|shaker|tam-tam|xylophone|marimba|vibraphone|glockenspiel', re.I)
    if ('handbell' in range_low or ident.startswith('handbells')):
        set_sem(g, 'note', 'percussion', True, 'percussion', instrument='handbell', technique=label)
        continue
    if instrument_words.search(text) and not re.search(r'notehead|shape|clef', low):
        set_sem(g, 'note', 'percussion', True, 'percussion', instrument=label)
        continue
    if any(x in range_low for x in ('percussion playing technique','beater pictogram')):
        set_sem(g, 'note', 'percussion', True, 'percussion', instrument=label)
        continue
    if re.search(r'tongue click|finger click|hand clap|slap|snap|stamp|tap|hop', low) and any(x in range_low for x in ('vocal','kahnotation','dance')):
        set_sem(g, 'note', 'percussion', True, 'percussion', instrument=label)
        continue

    if ident.startswith('elec') and re.search(r'mute|unmute|volume|fade|level', low):
        effect = 'unmute' if 'unmute' in low else ('mute' if 'mute' in low else ('fade' if 'fade' in low else 'level'))
        set_sem(g, 'event', 'electronic', True, 'electronic', electronic=effect)
        continue

    if 'pedal' in low:
        set_sem(g, 'span' if re.search(r'line|sustain|pedal ped', low) else 'event', 'pedal', True, 'pedal')
        continue
    if re.search(r'ottava|octave|8va|8vb|15ma|15mb', low):
        shift = -24 if '15mb' in low else (24 if '15ma' in low else (-12 if re.search(r'8vb|bassa|down', low) else 12))
        set_sem(g, 'span', 'octave-line', True, 'octave', semitones=shift)
        continue
    if re.search(r'ritard|rallent|accelerando', low):
        set_sem(g, 'span', 'tempo', True, 'tempo', direction='up' if 'accelerando' in low else 'down')
        continue

    if re.search(r'(^|[^a-z])tie([^a-z]|$)', low):
        set_sem(g, 'span', 'tie', True, 'tie')
        continue
    if re.search(r'(^|[^a-z])slur([^a-z]|$)|phrase mark', low):
        set_sem(g, 'span', 'slur', True, 'slur')
        continue

by_id = {g['id']: g for g in data['glyphs']}
checks = {
    'controlBeginBeam': lambda g: not g['audible'],
    'graceNoteAcciaccaturaStemUp': lambda g: g.get('kind') == 'grace' and g.get('pattern') == 'acciaccatura',
    'breathMarkComma': lambda g: g.get('kind') == 'hold' and g.get('sound') == 'breath',
    'dynamicForte': lambda g: g.get('audible') and g.get('velocity') == 94,
    'dynamicPiano': lambda g: g.get('audible') and g.get('velocity') == 52,
}
for ident, check in checks.items():
    if ident not in by_id or not check(by_id[ident]):
        raise SystemExit('Semantic correction failed for ' + ident)

path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
print('Corrected semantic priorities for', len(data['glyphs']), 'glyphs')
