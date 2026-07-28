"use strict";
(() => {
  const VERSION = "20260728-catalog-audit-6";
  const HOLD_MS = 360;
  const NORWEGIAN_KEYS = ("abcdefghijklmnopqrstuvwxyzæøå0123456789").split("")
    .concat(["É", "é", "♭", "♯", ".", ",", "-", "'", "SPACE", "DEL", "DONE"]);

  const textOf = (m, n) => [m && m.id, m && m.label, m && m.range, m && m.rangeId,
    m && m.group, m && m.kind, m && m.placement, m && m.sound, m && m.pattern,
    m && m.effect, m && m.technique, n].filter(Boolean).join(" ").toLowerCase();

  function isStructureNoteMark(m, n) {
    return /lyricstextrepeat|text repeats/.test(textOf(m, n));
  }

  function isScoreStructure(m, n) {
    const t = textOf(m, n);
    if (isStructureNoteMark(m, n)) return false;
    if (/barline|bar repeat|start repeat|end repeat|left repeat|right repeat|repeat.*left|repeat.*right|repeat barline|coda|segno|(^|[^a-z])fine([^a-z]|$)|da.?capo|dal.?segno|volta/.test(t)) return true;
    return /ending/.test(t) && /repeats|barlines|score structure/.test([m && m.group, m && m.range].filter(Boolean).join(" ").toLowerCase());
  }

  function isCompositePlayOrder(m, n) {
    return String(m && m.kind || "").toLowerCase() === "structure" &&
      String(m && m.placement || "").toLowerCase() === "structure" &&
      !isScoreStructure(m, n) && !isStructureNoteMark(m, n);
  }

  function isAudibleScoreStructure(m, n) {
    const t = textOf(m, n);
    if (!isScoreStructure(m, n)) return false;
    if (/repeatbarlowerdot|repeatbarupperdot|repeatbarslash|repeatdots?$/.test(String(m && m.id || "").toLowerCase())) return false;
    if (/dashed barline|dotted barline|double barline|final barline|heavy barline|heavy double barline|reverse final barline|short barline|single barline|tick barline/.test(t)) return false;
    if (/lutebarlinefinal/.test(t)) return false;
    return /repeat last|repeat1bar|repeat2bars|repeat4bars|start repeat|end repeat|left repeat|right repeat|repeat.*left|repeat.*right|coda|segno|da.?capo|dal.?segno|fine|volta/.test(t);
  }

  function canonicalStructure(m, n) {
    const t = textOf(m, n);
    if (/repeat1bar|repeat last bar/.test(t)) return "Repeat previous 1 bar";
    if (/repeat2bars|repeat last two bars/.test(t)) return "Repeat previous 2 bars";
    if (/repeat4bars|repeat last four bars/.test(t)) return "Repeat previous 4 bars";
    if (/repeatrightleft|right and left repeat|repeat right left/.test(t)) return "End repeat + Start repeat";
    if (/da.?capo|d\.c\./.test(t)) return /coda/.test(t) ? "D.C. al Coda" : /fine/.test(t) ? "D.C. al Fine" : "D.C.";
    if (/dal.?segno|d\.s\./.test(t)) return /coda/.test(t) ? "D.S. al Coda" : /fine/.test(t) ? "D.S. al Fine" : "D.S.";
    if (/to.?coda/.test(t)) return "To Coda";
    if (/coda/.test(t)) return "Coda";
    if (/fine/.test(t)) return "Fine";
    if (/segno/.test(t)) return "Segno";
    if (/start.*repeat|repeat.*start|left repeat/.test(t)) return "Start repeat";
    if (/end.*repeat|repeat.*end|right repeat/.test(t)) return "End repeat";
    return n || (m && m.label) || "Structure";
  }

  function audioRoute(t, kind, placement, audible) {
    if (!audible) return "silent-notation";
    if (kind === "play-order" || kind === "structure") return "play-order";
    if (kind === "accidental") return "pitch";
    if (/fermata|caesura|breath/.test(t)) return "hold";
    if (/dynamic|sforz|rinforz|fortissimo|pianissimo|niente/.test(t) || /(^|[^a-z])(pppp|ppp|pp|mp|mf|ff|fff|ffff|fp|sfz|sffz|rfz|p|f)([^a-z]|$)/.test(t)) return "dynamic";
    if (/hairpin|crescendo|diminuendo|swell/.test(t)) return "hairpin";
    if (/gliss|portamento|slide line/.test(t)) return "glissando";
    if (/pedal|una corda|tre corde/.test(t)) return "pedal";
    if (/8va|8vb|15ma|15mb|octave/.test(t)) return "octave";
    if (/ritard|rallent|accelerando|tempo/.test(t)) return "tempo";
    if (/slur|phrase|legato/.test(t)) return "slur";
    if (/trill|mordent|turn|shake|ornament|grace|arpeggio/.test(t)) return "ornament";
    if (/tremolo|ricochet|buzz roll|roll/.test(t)) return "tremolo";
    if (/vibrato|fall|doit|scoop|bend|smear|flip|plop|rip|lift|pitch/.test(t)) return "pitch-effect";
    if (/pizz|mute|harmonic|bow|technique|open|closed|stopped/.test(t)) return "technique";
    if (/accent|staccat|tenuto|marcato|articulation/.test(t)) return "articulation";
    if (placement === "span") return "continuous-line";
    if (placement === "note") return "audible-mark";
    return "audible-event";
  }

  function classify(meta, name, glyph) {
    const m = Object.assign({}, meta || {}), t = textOf(m, name);
    const commandName = String(name || m.label || m.id || "").trim().toLowerCase();
    let kind = String(m.kind || "glyph").toLowerCase();
    let placement = String(m.placement || "").toLowerCase();
    const declaredPlacement = placement;
    const structureNoteMark = isStructureNoteMark(m, name);
    let band = "above", role = "event";

    if (/controlbeginbeam/.test(t)) { kind = "beam-control"; placement = "note"; role = "beam-join"; }
    else if (/controlendbeam/.test(t)) { kind = "beam-control"; placement = "note"; role = "beam-break"; }
    else if (/^(stem up|stemup)$/.test(commandName)) { kind = "stem-direction"; placement = "note"; role = "stem-up"; }
    else if (/^(stem down|stemdown)$/.test(commandName)) { kind = "stem-direction"; placement = "note"; role = "stem-down"; }
    else if (/^(automatic stem|stem auto|stemauto)$/.test(commandName)) { kind = "stem-direction"; placement = "note"; role = "stem-auto"; }
    else if (structureNoteMark) { kind = "note-mark"; placement = "note"; role = "stack"; band = "below"; }
    else if (isCompositePlayOrder(m, name)) { kind = "play-order"; placement = "note"; role = "stack"; }
    else if (isScoreStructure(m, name) && (kind === "structure" || placement === "structure")) { kind = "structure"; placement = "structure"; role = "stack"; band = /barline/.test(t) ? "barline" : "system"; }
    else if (/notehead|note head/.test(t) || /percussion note/.test(commandName)) { kind = /percussion/.test(t) ? "percussion" : "notehead"; placement = "note"; role = "replacement"; }
    else if (kind === "accidental" || /(^|[^a-z])accidental/.test(t) || /range accidentals|accidentals and microtones/.test(t)) { kind = "accidental"; placement = "note"; role = "replacement"; }
    else if (/fingering|string number|fret|hand sign|solf[eè]ge/.test(t)) { kind = "note-mark"; placement = "note"; role = "stack"; }
    else if (/articulation|staccat|tenuto|accent|marcato|bowing/.test(t)) { kind = "articulation"; placement = "note"; role = "stack"; }
    else if (/ornament|trill|mordent|turn|grace|arpeggio/.test(t)) { kind = "ornament"; placement = "note"; role = "stack"; }
    else if (/tremolo|ricochet|buzz roll/.test(t)) { kind = "tremolo"; placement = "note"; role = "stack"; }
    else if (declaredPlacement === "note" && /vibrato/.test(t)) { kind = "pitch-effect"; placement = "note"; role = "stack"; }
    else if (/fall|doit|scoop|bend|smear|flip|plop|rip|lift|pitch effect/.test(t)) { kind = "pitch-effect"; placement = "note"; role = "stack"; }
    else if (/playing technique|technique|pizz|mute|harmonic|open string|stopped/.test(t)) { kind = "technique"; placement = "note"; role = "stack"; }
    else if (/fermata|caesura|breath mark/.test(t)) { kind = "hold"; placement = "event"; role = "singleton"; }
    else if (kind === "dynamic" || /range dynamics|dynamics combined|sforz|rinforz|fortissimo|pianissimo|niente/.test(t) || /(^|[^a-z])(pppp|ppp|pp|mp|mf|ff|fff|ffff|fp|sfz|sffz|rfz|p|f)([^a-z]|$)/.test(t)) { kind = "dynamic"; placement = "event"; role = "singleton"; band = "below"; }
    else if (/clef/.test(t)) { kind = "clef"; placement = "structure"; role = "singleton"; band = "staff"; }
    else if (/time signature|timesig|meter/.test(t)) { kind = "meter"; placement = "structure"; role = "singleton"; band = "staff"; }
    else if (/key signature/.test(t)) { kind = "key"; placement = "structure"; role = "singleton"; band = "staff"; }

    if ((kind === "tie" || /control(?:begin|end)tie/.test(t) || String(name || "").toLowerCase() === "tie") && !/texttie|tie segment/.test(t)) { kind = "tie"; placement = "note"; role = "tie"; }
    const fixedPlacementException = /^(beam-control|stem-direction|tie|play-order)$/.test(kind) || structureNoteMark;
    if (!fixedPlacementException && declaredPlacement !== "note" && /slur|phrase mark|gliss|portamento|hairpin|crescendo|diminuendo|swell|pedal|8va|8vb|15ma|15mb|octave line|let ring|vibrato|ritard|rallent|accelerando|trill extension/.test(t)) {
      placement = "span"; role = "span";
      if (/slur|phrase/.test(t)) kind = /phrase/.test(t) ? "phrase" : "slur";
    }
    if (m.audible && placement === "event" && /^(glyph|text)$/.test(kind)) { placement = "note"; role = "stack"; }
    if (!placement) placement = /^(notehead|accidental|articulation|ornament|tremolo|note-mark|percussion|technique|pitch-effect|play-order)$/.test(kind) ? "note" : "event";

    if (!fixedPlacementException && /^(note|event|span|structure)$/.test(declaredPlacement)) {
      placement = declaredPlacement;
      if (placement === "span") role = "span";
      else if (placement === "structure") { kind = "structure"; role = role === "singleton" ? role : "stack"; }
      else if (placement === "event" && /^(stack|replacement|span)$/.test(role)) role = "event";
      else if (placement === "note" && /^(event|span)$/.test(role)) role = "stack";
    }

    if (placement === "note" && role === "event") role = "stack";
    if (placement === "span") role = "span";
    if (placement === "structure" && band === "above") band = "system";
    if (/below|lower|under|heel|toe|stem down/.test(t)) band = "below";
    else if (/above|upper|over|stem up/.test(t)) band = "above";
    if (/lyrics|figured bass/.test(t)) band = "below";
    if (/combining|stem|flag|beam/.test(t) && placement === "note") band = "stem";

    const audible = !!m.audible && !/^(beam-control|stem-direction)$/.test(kind) && !structureNoteMark && !(kind === "structure" && !isAudibleScoreStructure(m, name));
    return Object.assign(m, { kind, placement, auditBand: band, auditRole: role,
      audioRoute: audioRoute(t, kind, placement, audible),
      curveDirection: /below|downward|down|lower|descending|desc\b/.test(t) ? "down" : /above|upward|up|upper|ascending|asc\b/.test(t) ? "up" : "auto",
      audible, glyph: glyph || m.glyph || "", auditVersion: VERSION });
  }

  function spanType(m, name) {
    const t = textOf(m, name);
    if (/diminuendo|decrescendo|hairpin.*down/.test(t)) return "hairpin-down";
    if (/crescendo|hairpin.*up/.test(t)) return "hairpin-up";
    if (/swell/.test(t)) return "hairpin-swell";
    if (/phrase/.test(t)) return "phrase";
    if (/slur/.test(t)) return "slur";
    if (/pedal/.test(t)) return "pedal";
    if (/portamento/.test(t)) return "portamento";
    if (/gliss/.test(t)) return "gliss";
    if (/arpeggiato|arpeggio|wiggle/.test(t)) return "arpeggio-line";
    if (/15mb/.test(t)) return "octave-down-2";
    if (/15ma/.test(t)) return "octave-up-2";
    if (/8vb/.test(t)) return "octave-down";
    if (/8va/.test(t)) return "octave-up";
    if (/ritard|rallent/.test(t)) return "tempo-down";
    if (/accelerando/.test(t)) return "tempo-up";
    if (/let ring/.test(t)) return "let-ring";
    if (/vibrato/.test(t)) return "vibrato";
    if (/trill extension/.test(t)) return "trill-line";
    return m && m.audible ? "let-ring" : "line";
  }

  function replacePx(style, key, fn) {
    return String(style || "").replace(new RegExp(key + ":(-?\\d+(?:\\.\\d+)?)px;"), (_, n) => key + ":" + fn(Number(n)) + "px;");
  }

  function markCss(mark, index, note) {
    const text = !mark.glyph || /^[a-z0-9 .,'’+-]+$/i.test(mark.glyph);
    const up = note.stem ? note.stem === "up" : !((note.voice || 1) === 2 || (note.voice || 1) === 4 || note.step >= 8);
    let left = -7, top;
    if (mark.band === "below") top = 42 + index * 16;
    else if (mark.band === "stem") { left = up ? 4 : -14; top = (up ? -30 : 24) + (up ? -index * 13 : index * 13); }
    else if (mark.kind === "articulation") top = -24 - index * 14;
    else if (mark.kind === "ornament" || mark.kind === "tremolo") top = -42 - index * 17;
    else if (mark.kind === "technique" || mark.kind === "note-mark" || mark.kind === "play-order") top = -55 - index * 15;
    else top = -34 - index * 15;
    left += Number(mark.offsetX) || 0; top += Number(mark.offsetY) || 0;
    return "position:absolute;left:" + left + "px;top:" + top + "px;z-index:6;white-space:nowrap;color:var(--ink);" +
      (text ? "font-family:var(--ui-font);font-size:12px;font-style:italic;" : "font-family:Bravura,'Noto Music',serif;font-size:30px;line-height:1;");
  }

  function auditCatalog() {
    const glyphs = window.LEGATO_SMUFL_CATALOG && window.LEGATO_SMUFL_CATALOG.glyphs || [];
    const rows = glyphs.map(g => { const p = classify(g, g.label, g.glyph); return { id:g.id,label:g.label,placement:p.placement,kind:p.kind,band:p.auditBand,role:p.auditRole,audible:!!p.audible,audioRoute:p.audioRoute }; });
    const failures = rows.filter(r => !r.placement || !r.kind || !r.role || (r.audible && (!r.audioRoute || r.audioRoute === "silent-notation")));
    const byPlacement = rows.reduce((a,r)=>(a[r.placement]=(a[r.placement]||0)+1,a),{}), audible = rows.filter(r=>r.audible);
    window.__LEGATO_CATALOG_AUDIT__ = { version:VERSION, expected:3451, checked:rows.length, failures, audibleChecked:audible.length, byPlacement, rows };
    if (rows.length !== 3451 || failures.length) console.error("[Legato catalog audit]", window.__LEGATO_CATALOG_AUDIT__);
    else console.info("[Legato catalog audit] 3451/3451 placement profiles and " + audible.length + "/" + audible.length + " audible routes checked");
  }

  window.__LEGATO_CATALOG_CORE__ = { VERSION, HOLD_MS, NORWEGIAN_KEYS, textOf, isStructureNoteMark, isScoreStructure, isCompositePlayOrder, isAudibleScoreStructure, canonicalStructure, classify, spanType, replacePx, markCss, auditCatalog };
  auditCatalog();
})();
