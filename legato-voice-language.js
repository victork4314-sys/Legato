"use strict";
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.LegatoVoiceLanguage = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  const VERSION = "20260806-voice-language-1";
  const MAX_COMMANDS = 8;
  const MAX_REPEAT = 16;

  const NUMBER_WORDS = Object.freeze({
    zero: 0, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7,
    eight: 8, nine: 9, ten: 10, eleven: 11, twelve: 12, thirteen: 13,
    fourteen: 14, fifteen: 15, sixteen: 16, seventeen: 17, eighteen: 18,
    nineteen: 19, twenty: 20, thirty: 30, forty: 40, fifty: 50, sixty: 60,
    seventy: 70, eighty: 80, ninety: 90, hundred: 100
  });

  const DURATION_ALIASES = Object.freeze([
    { index: 0, id: "w", label: "whole note", patterns: ["whole", "semibreve"] },
    { index: 1, id: "h", label: "half note", patterns: ["half", "minim"] },
    { index: 2, id: "q", label: "quarter note", patterns: ["quarter", "crotchet"] },
    { index: 3, id: "e", label: "eighth note", patterns: ["eighth", "8th", "quaver"] },
    { index: 4, id: "s", label: "sixteenth note", patterns: ["sixteenth", "16th", "semiquaver"] },
    { index: 5, id: "t", label: "thirty-second note", patterns: ["thirty second", "thirty-second", "32nd", "demisemiquaver"] }
  ]);

  const ACTIONS = Object.freeze([
    { action: "undo", label: "Undo", phrases: ["undo", "undo that", "go back"] },
    { action: "redo", label: "Redo", phrases: ["redo", "redo that"] },
    { action: "play-toggle", label: "Play or stop", phrases: ["play", "start playback", "play score", "stop", "stop playback", "pause playback"] },
    { action: "delete", label: "Delete selection", phrases: ["delete", "delete selection", "remove selection", "remove this"] },
    { action: "confirm", label: "Confirm", phrases: ["confirm", "select", "press a", "add note"] },
    { action: "command-halo", label: "Open music catalog", phrases: ["open music", "open symbols", "open music catalog", "music catalog", "symbols"] },
    { action: "project-menu", label: "Open project menu", phrases: ["open menu", "project menu", "open project menu"] },
    { action: "toggle-pointer", label: "Toggle pointer", phrases: ["toggle pointer", "pointer mode", "turn pointer on", "turn pointer off"] },
    { action: "copy", label: "Copy", phrases: ["copy", "copy selection"] },
    { action: "paste", label: "Paste", phrases: ["paste"] },
    { action: "toggle-rest", label: "Toggle note or rest", phrases: ["toggle rest", "toggle note and rest", "rest mode", "note mode"] },
    { action: "next-staff", label: "Next staff", phrases: ["next staff", "staff down"] },
    { action: "previous-staff", label: "Previous staff", phrases: ["previous staff", "staff up"] },
    { action: "move-left", label: "Move left", phrases: ["move left", "go left", "previous beat", "cursor left"] },
    { action: "move-right", label: "Move right", phrases: ["move right", "go right", "next beat", "cursor right"] },
    { action: "move-up", label: "Move up", phrases: ["move up", "go up", "pitch up", "cursor up"] },
    { action: "move-down", label: "Move down", phrases: ["move down", "go down", "pitch down", "cursor down"] },
    { action: "previous-zone", label: "Previous area", phrases: ["previous area", "previous zone"] },
    { action: "next-zone", label: "Next area", phrases: ["next area", "next zone"] },
    { action: "cycle-articulation", label: "Next articulation", phrases: ["next articulation", "cycle articulation"] },
    { action: "duration-wheel", label: "Open duration wheel", phrases: ["duration wheel", "open duration wheel"] },
    { action: "explain-context", label: "Explain context", phrases: ["explain context", "where am i", "what is selected"] }
  ]);

  const MODE_NAMES = Object.freeze({ setup: 0, write: 1, engrave: 2, play: 3, print: 4, controller: 5 });
  const ACCIDENTALS = Object.freeze({ sharp: "sh", flat: "f", natural: "n" });

  function normalize(value) {
    return String(value == null ? "" : value)
      .normalize("NFKD")
      .replace(/[♯#]/g, " sharp ")
      .replace(/[♭]/g, " flat ")
      .replace(/[♮]/g, " natural ")
      .replace(/[–—]/g, "-")
      .toLowerCase()
      .replace(/\bplease\b/g, " ")
      .replace(/\bcould you\b|\bcan you\b|\bwould you\b/g, " ")
      .replace(/[^a-z0-9/\-\s,;]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function wordsToNumber(text) {
    const clean = normalize(text);
    if (/^-?\d+$/.test(clean)) return Number(clean);
    const tokens = clean.split(/\s+/).filter(Boolean);
    if (!tokens.length) return null;
    let total = 0;
    let current = 0;
    for (const token of tokens) {
      if (!(token in NUMBER_WORDS)) return null;
      const value = NUMBER_WORDS[token];
      if (value === 100) current = Math.max(1, current) * value;
      else if (value >= 20) current += value;
      else current += value;
    }
    total += current;
    return Number.isFinite(total) ? total : null;
  }

  function replaceNumberWords(text) {
    let source = normalize(text)
      .replace(/\bthirty[ -]second\b/g, "32nd")
      .replace(/\bsixteenth\b/g, "16th")
      .replace(/\beighth\b/g, "8th");
    const token = "(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)";
    return source.replace(new RegExp("\\b" + token + "(?:[ -]" + token + "){0,3}\\b", "g"), function (match) {
      const value = wordsToNumber(match);
      return value == null ? match : String(value);
    });
  }

  function applyAliases(text, aliases) {
    let out = normalize(text);
    const entries = aliases && typeof aliases === "object" ? Object.entries(aliases) : [];
    entries.sort((a, b) => normalize(b[0]).length - normalize(a[0]).length);
    for (const [heard, expected] of entries) {
      const from = normalize(heard);
      const to = normalize(expected);
      if (!from || !to) continue;
      if (out === from) return to;
      const escaped = from.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      out = out.replace(new RegExp("\\b" + escaped + "\\b", "g"), to);
    }
    return out;
  }

  function splitSegments(text) {
    return normalize(text)
      .replace(/\b(?:and then|after that|then)\b/g, ";")
      .split(/[;,]+/)
      .map(s => s.trim())
      .filter(Boolean);
  }

  function findDuration(text) {
    const source = normalize(text);
    for (const duration of DURATION_ALIASES) {
      if (duration.patterns.some(pattern => source.includes(pattern))) return duration;
    }
    return null;
  }

  function parsePitchToken(letter, accidental, octave) {
    const l = String(letter || "").toUpperCase();
    if (!/^[A-G]$/.test(l)) return null;
    const o = Number(octave);
    if (!Number.isInteger(o) || o < -1 || o > 9) return null;
    const acc = accidental ? normalize(accidental) : "natural";
    const normalizedAcc = acc === "#" || acc === "sharp" ? "sharp" : acc === "b" || acc === "flat" ? "flat" : "natural";
    return { letter: l, accidental: normalizedAcc, octave: o, label: l + (normalizedAcc === "sharp" ? "♯" : normalizedAcc === "flat" ? "♭" : "") + o };
  }

  function extractPitches(text) {
    let source = replaceNumberWords(text)
      .replace(/\bmiddle c\b/g, "c 4")
      .replace(/\b([a-g])\s+(sharp|flat|natural)\s+minus\s+(\d)\b/g, "$1 $2 -$3");
    const found = [];
    const re = /\b([a-g])\s*(sharp|flat|natural|#|b)?\s*(-?\d)\b/g;
    let match;
    while ((match = re.exec(source))) {
      const pitch = parsePitchToken(match[1], match[2], match[3]);
      if (pitch) found.push(pitch);
    }
    return found;
  }

  function exactAction(source) {
    for (const item of ACTIONS) {
      if (item.phrases.some(phrase => source === phrase)) return item;
    }
    return null;
  }

  function repeatedAction(source) {
    const match = source.match(/^(.*?)(?:\s+)(\d+)(?:\s+times?)$/);
    if (!match) return null;
    const count = Number(match[2]);
    if (!Number.isInteger(count) || count < 1) return null;
    const action = exactAction(match[1].trim());
    if (!action) return null;
    return { type: "action", action: action.action, count, label: action.label + " × " + count, confidence: 1 };
  }

  function parseSegment(raw, options) {
    const source = applyAliases(replaceNumberWords(raw), options && options.aliases);
    if (!source) return null;

    if (/^(run|execute|confirm) (the )?(voice )?(commands|plan)$/.test(source) || source === "run commands") {
      return { type: "voice-run", label: "Run the previewed commands", confidence: 1 };
    }
    if (/^(clear|cancel|discard) (the )?(voice )?(commands|plan)$/.test(source) || source === "clear commands") {
      return { type: "voice-clear", label: "Clear the voice command preview", confidence: 1 };
    }

    const repeat = repeatedAction(source);
    if (repeat) return repeat;

    const action = exactAction(source);
    if (action) return { type: "action", action: action.action, count: 1, label: action.label, confidence: 1 };

    let match = source.match(/^(?:set |change )?tempo(?: to)? (\d{1,3})$/);
    if (match) {
      const bpm = Number(match[1]);
      if (bpm >= 20 && bpm <= 400) return { type: "tempo", bpm, label: "Set tempo to " + bpm, confidence: 1 };
      return { type: "invalid", label: "Tempo must be between 20 and 400", confidence: 0 };
    }

    match = source.match(/^(setup|write|engrave|play|print|controller)(?: mode)?$/);
    if (match) return { type: "mode", mode: MODE_NAMES[match[1]], label: match[1][0].toUpperCase() + match[1].slice(1) + " mode", confidence: 1 };

    match = source.match(/^(?:go to |move to )?bar (\d+)(?: beat (\d+(?:\.\d+)?))?$/);
    if (match) {
      const bar = Number(match[1]);
      const beat = match[2] == null ? 1 : Number(match[2]);
      if (bar >= 1 && beat >= 1) return { type: "goto", bar, beat, label: "Go to bar " + bar + ", beat " + beat, confidence: 1 };
    }

    match = source.match(/^(?:go to |select )?staff (\d+)$/);
    if (match) {
      const staff = Number(match[1]);
      if (staff >= 1) return { type: "staff", staff, label: "Select staff " + staff, confidence: 1 };
    }

    if (/^(?:save|save project|save score)$/.test(source)) return { type: "project", operation: "save", label: "Save project", confidence: 1 };
    if (/^(?:new project|new score)$/.test(source)) return { type: "project", operation: "new", label: "New project", confidence: 1 };
    if (/^(?:open project|open score)$/.test(source)) return { type: "project", operation: "open", label: "Open project", confidence: 1 };

    const duration = findDuration(source);
    const pitches = extractPitches(source);
    const isRest = /\brest\b/.test(source);
    const isNoteIntent = /\b(note|notes|chord|enter|add|write|put|place)\b/.test(source) || pitches.length > 0;

    if (isRest && duration) {
      return { type: "rest", durationIndex: duration.index, durationId: duration.id, label: "Add " + duration.label + " rest", confidence: 1 };
    }

    if (pitches.length && isNoteIntent) {
      const d = duration || DURATION_ALIASES[2];
      return {
        type: pitches.length > 1 || /\bchord\b/.test(source) ? "chord" : "note",
        pitches,
        durationIndex: d.index,
        durationId: d.id,
        label: (pitches.length > 1 ? "Add chord " : "Add ") + pitches.map(p => p.label).join(" + ") + " as " + d.label,
        confidence: duration ? 1 : 0.92
      };
    }

    if (duration && /^(?:select |set |use )?/.test(source) && !/\b(add|enter|write|rest|chord)\b/.test(source) && pitches.length === 0) {
      return { type: "duration", durationIndex: duration.index, durationId: duration.id, label: "Select " + duration.label, confidence: 1 };
    }

    match = source.match(/^(?:set |use |select )?(sharp|flat|natural)(?: accidental)?$/);
    if (match) return { type: "accidental", accidental: ACCIDENTALS[match[1]], accidentalName: match[1], label: "Select " + match[1], confidence: 1 };

    match = source.match(/^(?:add|apply|insert|place|put|attach) (?:a |an |the )?(.+)$/);
    if (match && match[1].trim()) {
      return { type: "catalog", query: match[1].trim(), label: "Place " + match[1].trim(), confidence: 0.9 };
    }

    return { type: "unknown", source, label: "Unrecognized: " + source, confidence: 0 };
  }

  function validatePlan(commands) {
    const errors = [];
    if (!Array.isArray(commands) || !commands.length) errors.push("No Legato command was recognized.");
    if (commands.length > MAX_COMMANDS) errors.push("A voice plan may contain at most " + MAX_COMMANDS + " commands.");
    const unknown = commands.filter(c => c.type === "unknown" || c.type === "invalid");
    if (unknown.length) errors.push("Every spoken segment must resolve before the plan can run.");
    const excessive = commands.filter(c => c.type === "action" && Number(c.count || 1) > MAX_REPEAT);
    if (excessive.length) errors.push("A repeated voice action may run at most " + MAX_REPEAT + " times.");
    const controlCommands = commands.filter(c => c.type === "voice-run" || c.type === "voice-clear");
    if (controlCommands.length && commands.length > 1) errors.push("Run or clear must be spoken by itself.");
    return { valid: errors.length === 0, errors };
  }

  function parsePlan(text, options) {
    const normalized = applyAliases(replaceNumberWords(text), options && options.aliases);
    const segments = splitSegments(normalized);
    const commands = segments.map(segment => parseSegment(segment, options || {})).filter(Boolean);
    const validation = validatePlan(commands);
    return { version: VERSION, transcript: String(text || ""), normalized, commands, valid: validation.valid, errors: validation.errors };
  }

  function levenshtein(a, b) {
    const x = normalize(a), y = normalize(b);
    const matrix = Array.from({ length: x.length + 1 }, () => Array(y.length + 1).fill(0));
    for (let i = 0; i <= x.length; i++) matrix[i][0] = i;
    for (let j = 0; j <= y.length; j++) matrix[0][j] = j;
    for (let i = 1; i <= x.length; i++) {
      for (let j = 1; j <= y.length; j++) {
        const cost = x[i - 1] === y[j - 1] ? 0 : 1;
        matrix[i][j] = Math.min(
          matrix[i - 1][j] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j - 1] + cost
        );
        if (i > 1 && j > 1 && x[i - 1] === y[j - 2] && x[i - 2] === y[j - 1]) {
          matrix[i][j] = Math.min(matrix[i][j], matrix[i - 2][j - 2] + cost);
        }
      }
    }
    return matrix[x.length][y.length];
  }

  function catalogScore(query, glyph) {
    const q = normalize(query), label = normalize(glyph && glyph.label), id = normalize(glyph && glyph.id);
    if (!q || !label) return 0;
    if (q === label || q === id) return 1;
    if (label.startsWith(q + " ")) {
      const direction = /\babove\b/.test(label) ? 0.012 : /\bbelow\b/.test(label) ? -0.006 : 0;
      const extraWords = Math.max(0, label.split(" ").length - q.split(" ").length);
      return Math.min(0.99, 0.955 + direction - extraWords * 0.004);
    }
    if (q.startsWith(label + " ")) return 0.945;
    if (new RegExp("(^| )" + q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "( |$)").test(label)) return 0.92;
    const qTokens = new Set(q.split(" "));
    const lTokens = label.split(" ");
    const overlap = lTokens.filter(token => qTokens.has(token)).length / Math.max(qTokens.size, lTokens.length, 1);
    const distance = levenshtein(q, label);
    const similarity = 1 - distance / Math.max(q.length, label.length, 1);
    const tierBoost = glyph && (glyph.tier === "popular" || glyph.tier === "core") ? 0.04 : 0;
    return Math.min(0.99, overlap * 0.55 + similarity * 0.4 + tierBoost);
  }

  function bestCatalogMatch(query, glyphs) {
    const list = Array.isArray(glyphs) ? glyphs : [];
    const scored = list.map(glyph => ({ glyph, score: catalogScore(query, glyph) }))
      .filter(item => item.score >= 0.62)
      .sort((a, b) => b.score - a.score || String(a.glyph.label).localeCompare(String(b.glyph.label)));
    if (!scored.length) return { match: null, ambiguous: false, alternatives: [] };
    const best = scored[0];
    const second = scored[1];
    const ambiguous = !!(second && best.score < 0.98 && Math.abs(best.score - second.score) < 0.018);
    return { match: ambiguous ? null : best.glyph, score: best.score, ambiguous, alternatives: scored.slice(0, 5) };
  }

  return {
    VERSION, MAX_COMMANDS, MAX_REPEAT, DURATION_ALIASES, ACTIONS,
    normalize, wordsToNumber, replaceNumberWords, applyAliases, splitSegments,
    findDuration, extractPitches, parseSegment, parsePlan, validatePlan,
    levenshtein, catalogScore, bestCatalogMatch
  };
});
