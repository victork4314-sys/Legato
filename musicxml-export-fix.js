"use strict";
(() => {
  const VERSION = "20260728-musicxml-1";
  const DIVISIONS = 10080;
  const BASE_BEATS = { w: 4, h: 2, q: 1, e: 0.5, s: 0.25, t: 0.125 };
  const NOTE_TYPES = { w: "whole", h: "half", q: "quarter", e: "eighth", s: "16th", t: "32nd" };
  const ACCIDENTALS = {
    "\uE260": ["flat", -1],
    "\uE261": ["natural", 0],
    "\uE262": ["sharp", 1],
    "\uE263": ["double-sharp", 2],
    "\uE264": ["flat-flat", -2],
    "\uE280": ["quarter-flat", -0.5],
    "\uE281": ["three-quarters-flat", -1.5],
    "\uE282": ["quarter-sharp", 0.5],
    "\uE283": ["three-quarters-sharp", 1.5]
  };
  const PUA_RE = /[\uE000-\uF8FF]/g;

  const xml = value => String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");

  const ticks = beats => Math.max(0, Math.round(Number(beats || 0) * DIVISIONS));
  const baseBeats = note => BASE_BEATS[note && note.d] || 1;
  const noteBeats = note => {
    const base = baseBeats(note);
    const dotted = Number(note && note.dots) === 2 ? base * 1.75 : Number(note && note.dots) === 1 ? base * 1.5 : base;
    const tuplet = Number(note && note.tup) || 0;
    return tuplet ? dotted * (tuplet === 3 ? 2 / 3 : (tuplet - 1) / tuplet) : dotted;
  };
  const dotXml = note => "<dot/>".repeat(Math.max(0, Math.min(2, Number(note && note.dots) || 0)));
  const timeModificationXml = note => {
    const actual = Number(note && note.tup) || 0;
    if (!actual) return "";
    const normal = actual === 3 ? 2 : Math.max(1, actual - 1);
    return `<time-modification><actual-notes>${actual}</actual-notes><normal-notes>${normal}</normal-notes></time-modification>`;
  };
  const normalText = value => String(value == null ? "" : value)
    .replace(PUA_RE, "")
    .replace(/[\u0000-\u001F\u007F]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const isDebugText = value => {
    const t = normalText(value).toLowerCase();
    return !t || /^\d+\/\d+\s*\([^)]*(?:\+|q,|e,|s,)/.test(t) ||
      /^\d+\s+(?:major|minor)$/.test(t) ||
      /^(?:cursor|grid|selection|selected|staff|voice|bar)\b.*(?:px|index|position|debug)/.test(t) ||
      /^(?:legato|controller|keyboard)\s+(?:debug|status|hint)/.test(t);
  };
  const safeWords = value => {
    const t = normalText(value);
    return isDebugText(t) ? "" : t;
  };
  const slugLabel = value => String(value || "Instrument").replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());

  function meterParts(value) {
    const match = String(value || "4/4").match(/^(\d+)\s*\/\s*(\d+)$/);
    return match ? [Number(match[1]), Number(match[2])] : [4, 4];
  }
  function keyFifths(key) {
    if (!key || !key.type || !Number(key.n)) return 0;
    return key.type === "flat" ? -Number(key.n) : Number(key.n);
  }
  function clefXml(clef, octave) {
    const c = String(clef || "treble");
    let sign = "G", line = 2;
    if (c === "bass") { sign = "F"; line = 4; }
    else if (c === "alto") { sign = "C"; line = 3; }
    else if (c === "tenor") { sign = "C"; line = 4; }
    else if (c === "percussion") { sign = "percussion"; line = 3; }
    const oct = Number(octave) || 0;
    return `<clef><sign>${sign}</sign><line>${line}</line>${oct ? `<clef-octave-change>${oct}</clef-octave-change>` : ""}</clef>`;
  }
  function accidentalXml(note) {
    if (note && note.acc && ACCIDENTALS[note.acc]) return `<accidental>${ACCIDENTALS[note.acc][0]}</accidental>`;
    if (note && note.accCents != null && isFinite(Number(note.accCents))) {
      const cents = Number(note.accCents);
      if (Math.abs(cents - 50) < 0.1) return "<accidental>quarter-sharp</accidental>";
      if (Math.abs(cents + 50) < 0.1) return "<accidental>quarter-flat</accidental>";
      if (Math.abs(cents - 150) < 0.1) return "<accidental>three-quarters-sharp</accidental>";
      if (Math.abs(cents + 150) < 0.1) return "<accidental>three-quarters-flat</accidental>";
    }
    return "";
  }
  function pitchXml(component, note, step, state) {
    const copy = Object.assign({}, note, { step, chord: [] });
    const clef = typeof component.clefAt === "function" ? component.clefAt(note.s, note.p, state) : ((state.clefs || [])[note.s] || "treble");
    const bass = clef === "bass";
    const index = ((Number(step) % 7) + 7) % 7;
    const octaveBlock = Math.floor(Number(step) / 7);
    const letters = bass ? ["G", "A", "B", "C", "D", "E", "F"] : ["E", "F", "G", "A", "B", "C", "D"];
    const semis = bass ? [0, 2, 4, 5, 7, 9, 10] : [0, 1, 3, 5, 7, 8, 10];
    const base = bass ? 43 : 64;
    const clefOctave = Number((state.clefOctaves || [])[note.s]) || 0;
    const naturalMidi = base + octaveBlock * 12 + semis[index] + clefOctave * 12;
    const sounding = typeof component.noteMidi === "function" ? Number(component.noteMidi(copy, state)) : naturalMidi;
    const rawAlter = sounding - naturalMidi;
    const alter = Math.abs(rawAlter) < 0.0001 ? 0 : Math.round(rawAlter * 10000) / 10000;
    const octave = Math.floor(naturalMidi / 12) - 1;
    return `<pitch><step>${letters[index]}</step>${alter ? `<alter>${alter}</alter>` : ""}<octave>${octave}</octave></pitch>`;
  }
  function articulationTags(note) {
    const tags = [];
    const glyph = note && note.art;
    const label = normalText(note && note.artPlayback && (note.artPlayback.label || note.artPlayback.id || note.artPlayback.profile)).toLowerCase();
    if (glyph === "\uE4A2" || /(^|\b)staccato\b/.test(label)) tags.push("<staccato/>");
    else if (glyph === "\uE4A6" || /staccatissimo/.test(label)) tags.push("<staccatissimo/>");
    else if (glyph === "\uE4A4" || /tenuto/.test(label)) tags.push("<tenuto/>");
    else if (glyph === "\uE4AC" || /marcato|strong accent/.test(label)) tags.push("<strong-accent/>");
    else if (glyph === "\uE4A0" || /accent/.test(label)) tags.push("<accent/>");
    return tags;
  }
  function ornamentTags(note) {
    const tags = [];
    const glyph = note && note.orn;
    const semantic = note && (note.ornPlayback || note.tremoloPlayback || note.pitchPlayback);
    const label = normalText(semantic && (semantic.label || semantic.id || semantic.pattern || semantic.effect)).toLowerCase();
    if (glyph === "\uE566" || /trill/.test(label)) tags.push("<trill-mark/>");
    else if (glyph === "\uE56C" || /mordent(?!-down)|upper mordent/.test(label)) tags.push("<mordent/>");
    else if (glyph === "\uE56D" || /mordent-down|lower mordent|inverted mordent/.test(label)) tags.push("<inverted-mordent/>");
    else if (glyph === "\uE567" || /(^|\b)turn\b/.test(label)) tags.push("<turn/>");
    else if (glyph === "\uE568" || /inverted turn/.test(label)) tags.push("<inverted-turn/>");
    const trem = Number(semantic && semantic.strokes) || (glyph === "\uE220" ? 1 : glyph === "\uE221" ? 2 : glyph === "\uE222" ? 3 : 0);
    if (trem) tags.push(`<tremolo type="single">${Math.max(1, Math.min(4, trem))}</tremolo>`);
    return tags;
  }
  function spanEndpoints(state, note) {
    const out = [];
    (state.scoreSpans || []).forEach((span, index) => {
      const sameStart = Number(span.s1) === Number(note.s) && Math.abs(Number(span.p1) - Number(note.p)) < 0.001;
      const sameEnd = Number(span.s2 == null ? span.s1 : span.s2) === Number(note.s) && Math.abs(Number(span.p2) - Number(note.p)) < 0.001;
      if (!sameStart && !sameEnd) return;
      const number = index % 6 + 1;
      if (span.type === "tie") {
        if (sameStart) out.push('<tied type="start"/>');
        if (sameEnd) out.push('<tied type="stop"/>');
      } else if (span.type === "slur" || span.type === "phrase") {
        const placement = span.curveDirection === "down" || span.flipped ? ' placement="below"' : span.curveDirection === "up" ? ' placement="above"' : "";
        if (sameStart) out.push(`<slur type="start" number="${number}"${placement}/>`);
        if (sameEnd) out.push(`<slur type="stop" number="${number}"/>`);
      } else if (span.type === "gliss" || span.type === "portamento") {
        const tag = span.type === "portamento" ? "slide" : "glissando";
        if (sameStart) out.push(`<${tag} type="start" number="${number}"/>`);
        if (sameEnd) out.push(`<${tag} type="stop" number="${number}"/>`);
      }
    });
    return out;
  }
  function lyricXml(note) {
    const marks = (note && note.marks || []).filter(mark => mark && mark.text && mark.place === "below");
    if (!marks.length) return "";
    const text = safeWords(marks[0].g || marks[0].name || "");
    return text ? `<lyric><text>${xml(text)}</text></lyric>` : "";
  }
  function noteheadXml(note) {
    const label = normalText(note && note.noteheadPlayback && (note.noteheadPlayback.label || note.noteheadPlayback.id)).toLowerCase();
    if (/diamond|harmonic/.test(label)) return "<notehead>diamond</notehead>";
    if (/cross|dead|x notehead/.test(label)) return "<notehead>x</notehead>";
    if (/slash/.test(label)) return "<notehead>slash</notehead>";
    if (/triangle/.test(label)) return "<notehead>triangle</notehead>";
    return "";
  }
  function noteXml(component, note, step, state, chordMember, tieFlags) {
    const duration = ticks(noteBeats(note));
    const body = note.rest ? "<rest/>" : pitchXml(component, note, step, state);
    const notation = [];
    if (!chordMember) {
      const arts = articulationTags(note);
      const orns = ornamentTags(note);
      const spans = spanEndpoints(state, note);
      if (arts.length) notation.push(`<articulations>${arts.join("")}</articulations>`);
      if (orns.length) notation.push(`<ornaments>${orns.join("")}</ornaments>`);
      notation.push(...spans);
      if (tieFlags && tieFlags.start) notation.push('<tied type="start"/>');
      if (tieFlags && tieFlags.stop) notation.push('<tied type="stop"/>');
    }
    const tieSound = !chordMember ? `${tieFlags && tieFlags.stop ? '<tie type="stop"/>' : ""}${tieFlags && tieFlags.start ? '<tie type="start"/>' : ""}` : "";
    const stem = !chordMember && note && (note.stem === "up" || note.stem === "down") ? `<stem>${note.stem}</stem>` : "";
    const accidental = note.rest ? "" : accidentalXml(note);
    return `<note>${chordMember ? "<chord/>" : ""}${note.cue ? "<cue/>" : ""}${body}<duration>${duration}</duration>${tieSound}<voice>${Math.max(1, Number(note.voice) || 1)}</voice><type>${NOTE_TYPES[note.d] || "quarter"}</type>${dotXml(note)}${timeModificationXml(note)}${accidental}${stem}${noteheadXml(note)}${notation.length ? `<notations>${notation.join("")}</notations>` : ""}${chordMember ? "" : lyricXml(note)}</note>\n`;
  }
  function dynamicName(event) {
    const text = normalText([event && event.name, event && event.text, event && event.playback && event.playback.label].filter(Boolean).join(" ")).toLowerCase();
    const match = text.match(/(^|\s)(pppp|ppp|pp|mp|mf|ffff|fff|ff|fp|sfz|sffz|rfz|p|f)(?=\s|$)/);
    return match ? match[2] : "";
  }
  function directionXml(event, staffNumber) {
    const type = String(event && event.type || "");
    const offset = Number(event && event._offsetTicks) || 0;
    const offsetXml = offset ? `<offset>${offset}</offset>` : "";
    const staffXml = staffNumber ? `<staff>${staffNumber}</staff>` : "";
    if (type === "tempo") {
      const bpm = Math.max(20, Math.min(400, Number(event.value) || 100));
      return `<direction placement="above"><direction-type><metronome><beat-unit>quarter</beat-unit><per-minute>${bpm}</per-minute></metronome></direction-type>${offsetXml}<sound tempo="${bpm}"/>${staffXml}</direction>\n`;
    }
    if (type === "dynamic") {
      const dyn = dynamicName(event);
      return dyn ? `<direction placement="below"><direction-type><dynamics><${dyn}/></dynamics></direction-type>${offsetXml}${staffXml}</direction>\n` : "";
    }
    if (type === "rehearsal") {
      const text = safeWords(event.text || event.value || event.name);
      return text ? `<direction placement="above"><direction-type><rehearsal>${xml(text)}</rehearsal></direction-type>${offsetXml}${staffXml}</direction>\n` : "";
    }
    if (type === "technique" || type === "text" || type === "staff-text" || type === "system-text") {
      const text = safeWords(event.text || event.value || event.name);
      return text ? `<direction placement="${event.placement === "below" ? "below" : "above"}"><direction-type><words>${xml(text)}</words></direction-type>${offsetXml}${staffXml}</direction>\n` : "";
    }
    if (type === "hold") {
      const text = normalText(event.name || event.text).toLowerCase();
      if (/breath/.test(text)) return `<direction placement="above"><direction-type><words>breath</words></direction-type>${offsetXml}${staffXml}</direction>\n`;
      if (/caesura/.test(text)) return `<direction placement="above"><direction-type><words>caesura</words></direction-type>${offsetXml}${staffXml}</direction>\n`;
    }
    if (type === "structure") {
      const text = safeWords(event.name || event.text || event.value);
      if (/^(coda|segno|to coda|fine|d\.c\.|d\.s\.)/i.test(text)) return `<direction placement="above"><direction-type><words>${xml(text)}</words></direction-type>${offsetXml}${staffXml}</direction>\n`;
    }
    return "";
  }
  function spanDirectionXml(span, start, offset, staffNumber) {
    const off = offset ? `<offset>${offset}</offset>` : "";
    const staff = staffNumber ? `<staff>${staffNumber}</staff>` : "";
    if (span.type === "hairpin-up" || span.type === "hairpin-down" || span.type === "hairpin-swell") {
      const type = start ? (span.type === "hairpin-down" ? "diminuendo" : "crescendo") : "stop";
      return `<direction placement="below"><direction-type><wedge type="${type}" number="1"/></direction-type>${off}${staff}</direction>\n`;
    }
    if (/^octave-(?:up|down)/.test(span.type || "")) {
      const down = /down/.test(span.type), size = /-2$/.test(span.type) ? 15 : 8;
      const type = start ? (down ? "down" : "up") : "stop";
      return `<direction placement="above"><direction-type><octave-shift type="${type}" size="${size}" number="1"/></direction-type>${off}${staff}</direction>\n`;
    }
    if (span.type === "pedal") {
      return `<direction placement="below"><direction-type><pedal type="${start ? "start" : "stop"}" line="yes"/></direction-type>${off}${staff}</direction>\n`;
    }
    return "";
  }
  function harmonyXml(chord, offset) {
    const text = normalText(chord && chord.text);
    const match = text.match(/^([A-G])([#b]?)(.*)$/);
    if (!match) return "";
    const alter = match[2] === "#" ? 1 : match[2] === "b" ? -1 : 0;
    const suffix = match[3] || "";
    let kind = "major";
    if (/^m(?!aj)/.test(suffix)) kind = "minor";
    else if (/dim/.test(suffix)) kind = "diminished";
    else if (/aug|\+/.test(suffix)) kind = "augmented";
    else if (/sus/.test(suffix)) kind = "suspended-fourth";
    else if (/7/.test(suffix)) kind = /maj7/.test(suffix) ? "major-seventh" : /^m7/.test(suffix) ? "minor-seventh" : "dominant";
    return `<harmony>${offset ? `<offset>${offset}</offset>` : ""}<root><root-step>${match[1]}</root-step>${alter ? `<root-alter>${alter}</root-alter>` : ""}</root><kind text="${xml(suffix || match[1])}">${kind}</kind></harmony>\n`;
  }
  function barlineXml(state, bar) {
    const marks = (state.measureMarks && state.measureMarks[bar] || []).map(mark => normalText(mark && mark.name));
    const joined = marks.join(" ");
    const out = [];
    if (/Start repeat/i.test(joined)) out.push('<barline location="left"><bar-style>heavy-light</bar-style><repeat direction="forward"/></barline>\n');
    if (/End repeat/i.test(joined)) out.push('<barline location="right"><bar-style>light-heavy</bar-style><repeat direction="backward"/></barline>\n');
    else if (/Final barline/i.test(joined)) out.push('<barline location="right"><bar-style>light-heavy</bar-style></barline>\n');
    else if (/Double barline/i.test(joined)) out.push('<barline location="right"><bar-style>light-light</bar-style></barline>\n');
    return out.join("");
  }

  function buildMusicXML() {
    const state = this.state || {};
    const players = state.players || [];
    const partCount = Math.max(1, players.length, (state.clefs || []).length, (state.instruments || []).length);
    const bars = Math.max(1, Number(state.bars) || 1);
    const baseCapacity = typeof this.barCapacity === "function" ? Number(this.barCapacity()) || 4 : 4;
    let output = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n<score-partwise version="4.0">\n';
    output += `<work><work-title>${xml(state.title || "Untitled score")}</work-title></work>\n`;
    if (state.composer) output += `<identification><creator type="composer">${xml(state.composer)}</creator><encoding><software>Legato</software></encoding></identification>\n`;
    else output += '<identification><encoding><software>Legato</software></encoding></identification>\n';
    output += "<part-list>\n";
    for (let staff = 0; staff < partCount; staff++) {
      const player = players[staff] || {};
      const name = player.name || `Part ${staff + 1}`;
      const short = player.short || name.slice(0, 8);
      const instrument = slugLabel((state.instruments || [])[staff] || player.instrument || name);
      output += `<score-part id="P${staff + 1}"><part-name>${xml(name)}</part-name><part-abbreviation>${xml(short)}</part-abbreviation><score-instrument id="I${staff + 1}"><instrument-name>${xml(instrument)}</instrument-name></score-instrument></score-part>\n`;
    }
    output += "</part-list>\n";

    for (let staff = 0; staff < partCount; staff++) {
      output += `<part id="P${staff + 1}">\n`;
      let previousKey = null, previousMeter = null, previousClef = null;
      for (let bar = 0; bar < bars; bar++) {
        const barStart = bar * baseCapacity;
        const barEnd = barStart + baseCapacity;
        const key = typeof this.keyAt === "function" ? this.keyAt(barStart, state) : null;
        const meter = typeof this.meterAt === "function" ? this.meterAt(barStart, state) : "4/4";
        const clef = typeof this.clefAt === "function" ? this.clefAt(staff, barStart, state) : ((state.clefs || [])[staff] || "treble");
        const keySig = keyFifths(key), meterSig = meterParts(meter), clefSig = `${clef}:${Number((state.clefOctaves || [])[staff]) || 0}`;
        output += `<measure number="${bar + 1}">\n`;
        const attributes = [];
        if (bar === 0) attributes.push(`<divisions>${DIVISIONS}</divisions>`);
        if (bar === 0 || keySig !== previousKey) attributes.push(`<key><fifths>${keySig}</fifths></key>`);
        if (bar === 0 || `${meterSig[0]}/${meterSig[1]}` !== previousMeter) attributes.push(`<time><beats>${meterSig[0]}</beats><beat-type>${meterSig[1]}</beat-type></time>`);
        if (bar === 0 || clefSig !== previousClef) attributes.push(clefXml(clef, (state.clefOctaves || [])[staff]));
        if (attributes.length) output += `<attributes>${attributes.join("")}</attributes>\n`;
        previousKey = keySig;
        previousMeter = `${meterSig[0]}/${meterSig[1]}`;
        previousClef = clefSig;

        const eventList = (state.scoreEvents || []).filter(event => {
          if (Number(event.p) < barStart - 0.0005 || Number(event.p) >= barEnd - 0.0005) return false;
          return event.system ? staff === 0 : Number(event.s || 0) === staff;
        }).sort((a, b) => Number(a.p) - Number(b.p));
        if (bar === 0 && staff === 0 && !eventList.some(event => event.type === "tempo" && Math.abs(Number(event.p)) < 0.001)) {
          eventList.unshift({ type: "tempo", value: state.tempo || 100, p: 0, system: true });
        }
        eventList.forEach(event => {
          const exportEvent = Object.assign({}, event, { _offsetTicks: ticks(Number(event.p) - barStart) });
          output += directionXml(exportEvent, event.system ? 0 : 1);
        });
        if (staff === 0) {
          (state.chords || []).filter(chord => Number(chord.p) >= barStart - 0.0005 && Number(chord.p) < barEnd - 0.0005)
            .sort((a, b) => Number(a.p) - Number(b.p))
            .forEach(chord => { output += harmonyXml(chord, ticks(Number(chord.p) - barStart)); });
        }
        (state.scoreSpans || []).forEach(span => {
          const startStaff = Number(span.s1 || 0), endStaff = Number(span.s2 == null ? startStaff : span.s2);
          if (!span.system && startStaff !== staff && endStaff !== staff) return;
          const start = Math.min(Number(span.p1), Number(span.p2));
          const end = Math.max(Number(span.p1), Number(span.p2));
          if (start >= barStart - 0.0005 && start < barEnd - 0.0005) output += spanDirectionXml(span, true, ticks(start - barStart), span.system ? 0 : 1);
          if (end >= barStart - 0.0005 && end < barEnd - 0.0005) output += spanDirectionXml(span, false, ticks(end - barStart), span.system ? 0 : 1);
        });

        const measureNotes = (state.notes || []).filter(note => Number(note.s) === staff && Number(note.p) >= barStart - 0.0005 && Number(note.p) < barEnd - 0.0005);
        const voices = Array.from(new Set(measureNotes.map(note => Math.max(1, Number(note.voice) || 1)))).sort((a, b) => a - b);
        const activeVoices = voices.length ? voices : [1];
        activeVoices.forEach((voice, voiceIndex) => {
          if (voiceIndex) output += `<backup><duration>${ticks(baseCapacity)}</duration></backup>\n`;
          let cursor = 0;
          const voiceNotes = measureNotes.filter(note => Math.max(1, Number(note.voice) || 1) === voice).sort((a, b) => Number(a.p) - Number(b.p) || Number(a.step) - Number(b.step));
          voiceNotes.forEach((note, noteIndex) => {
            const onset = Math.max(0, Number(note.p) - barStart);
            if (onset > cursor + 0.0005) output += `<forward><duration>${ticks(onset - cursor)}</duration></forward>\n`;
            const next = voiceNotes[noteIndex + 1];
            const prev = voiceNotes[noteIndex - 1];
            const samePitch = (a, b) => a && b && !a.rest && !b.rest && Math.abs(Number(this.noteMidi(a, state)) - Number(this.noteMidi(b, state))) < 0.001;
            const tieFlags = {
              start: !!note.tie && samePitch(note, next),
              stop: !!(prev && prev.tie) && samePitch(prev, note)
            };
            const steps = note.rest ? [Number(note.step) || 0] : [Number(note.step) || 0].concat((note.chord || []).map(offset => Number(note.step) + Number(offset))).filter((value, index, all) => all.indexOf(value) === index);
            steps.forEach((step, index) => { output += noteXml(this, note, step, state, index > 0, tieFlags); });
            cursor = Math.max(cursor, onset + noteBeats(note));
          });
          if (cursor < baseCapacity - 0.0005) output += `<forward><duration>${ticks(baseCapacity - cursor)}</duration></forward>\n`;
        });
        output += barlineXml(state, bar);
        output += "</measure>\n";
      }
      output += "</part>\n";
    }
    output += "</score-partwise>\n";
    return output;
  }

  function install() {
    const root = typeof window.__dcRootName === "function" ? window.__dcRootName() : null;
    const entry = window.__dcRegistry && root && window.__dcRegistry[root];
    const prototype = entry && entry.Logic && entry.Logic.prototype;
    if (!prototype || typeof prototype.noteMidi !== "function") return false;
    if (prototype.__legatoMusicXmlFix === VERSION) return true;
    prototype.buildMusicXML = buildMusicXML;
    Object.defineProperty(prototype, "__legatoMusicXmlFix", { value: VERSION, configurable: true });
    window.__LEGATO_MUSICXML_AUDIT__ = {
      version: VERSION,
      divisions: DIVISIONS,
      chords: "one onset with MusicXML chord members",
      rhythm: "dots and tuplets use the same exact duration as Legato",
      voices: "independent voices with backup and invisible forward movement",
      filtering: "no editor labels, comments, PUA glyph words, SVG, images, or layout graphics",
      ok: true
    };
    return true;
  }

  if (!install()) {
    let attempts = 0;
    const timer = setInterval(() => {
      if (install() || ++attempts > 240) clearInterval(timer);
    }, 50);
  }
})();
