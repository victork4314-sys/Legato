"use strict";
(() => {
  const PATCH_VERSION = "20260727-total-placement-1";
  const NOTE_EPSILON = 0.021;

  function cursorNote(logic) {
    const s = logic && logic.state;
    if (!s || !Array.isArray(s.notes)) return null;
    const staff = Number(s.staff) || 0;
    const pos = Number(s.pos) || 0;
    return s.notes
      .filter(n => n && n.s === staff && Math.abs(Number(n.p) - pos) <= NOTE_EPSILON)
      .sort((a, b) => Math.abs(Number(a.p) - pos) - Math.abs(Number(b.p) - pos) || Number(a.rest) - Number(b.rest))[0] || null;
  }

  function cursorAnchor(logic) {
    const s = logic.state || {};
    const note = cursorNote(logic);
    return note
      ? { s: note.s, p: note.p, step: note.step, noteId: note.id || null }
      : { s: Number(s.staff) || 0, p: Number(s.pos) || 0, step: Number(s.step) || 6, noteId: null };
  }

  function words(meta, name) {
    return [meta && meta.id, meta && meta.label, meta && meta.kind, meta && meta.range, meta && meta.group, name]
      .filter(Boolean).join(" ").toLowerCase();
  }

  function inferredKind(meta, name) {
    const declared = String((meta && meta.kind) || "").toLowerCase();
    const text = words(meta, name);
    if (declared && declared !== "glyph") return declared;
    if (/fermata|breath mark|caesura/.test(text)) return "hold";
    if (/sforz|rinforz|forte|piano|mezzo|dynamic|niente/.test(text)) return "dynamic";
    if (/clef/.test(text)) return "clef";
    if (/time signature|timesig|meter/.test(text)) return "meter";
    if (/barline|repeat|segno|coda|fine|dal segno|da capo/.test(text)) return "structure";
    if (/accidental|sharp|flat|natural/.test(text)) return "accidental";
    if (/notehead/.test(text)) return "notehead";
    if (/articulation|staccat|tenuto|accent|marcato|bow/.test(text)) return "articulation";
    if (/ornament|mordent|turn|trill|grace note|arpeggio/.test(text)) return "ornament";
    if (/tremolo/.test(text)) return "tremolo";
    if (/fingering|string number|fret|hand sign/.test(text)) return "note-mark";
    if (/playing technique|technique|pizz|mute|harmonic/.test(text)) return "technique";
    return declared || "glyph";
  }

  function inferredPlacement(meta, kind, name) {
    const declared = String((meta && meta.placement) || "").toLowerCase();
    if (declared) return declared;
    const text = words(meta, name);
    if (/slur|phrase|hairpin|crescendo|diminuendo|pedal|gliss|portamento|octave line|8va|8vb|15ma|15mb|let ring|vibrato|ritard|accelerando/.test(text)) return "span";
    if (/^(notehead|accidental|articulation|ornament|tremolo|note-mark|bowing|percussion)$/.test(kind)) return "note";
    if (/^(clef|meter|structure)$/.test(kind)) return "structure";
    return "event";
  }

  function spanType(logic, meta, name) {
    if (typeof logic.catalogSpanType === "function") {
      try { return logic.catalogSpanType(meta); } catch (_) {}
    }
    const text = words(meta, name);
    if (/diminuendo|decrescendo|hairpin.*down/.test(text)) return "hairpin-down";
    if (/crescendo|hairpin.*up/.test(text)) return "hairpin-up";
    if (/swell/.test(text)) return "hairpin-swell";
    if (/phrase/.test(text)) return "phrase";
    if (/slur/.test(text)) return "slur";
    if (/tie/.test(text)) return "tie";
    if (/pedal/.test(text)) return "pedal";
    if (/portamento/.test(text)) return "portamento";
    if (/gliss/.test(text)) return "gliss";
    if (/15mb/.test(text)) return "octave-down-2";
    if (/15ma/.test(text)) return "octave-up-2";
    if (/8vb/.test(text)) return "octave-down";
    if (/8va/.test(text)) return "octave-up";
    if (/ritard|rallent/.test(text)) return "tempo-down";
    if (/accelerando/.test(text)) return "tempo-up";
    if (/let ring/.test(text)) return "let-ring";
    if (/vibrato/.test(text)) return "vibrato";
    return "line";
  }

  function notePatch(kind, meta, glyph) {
    const playback = Object.assign({}, meta || {});
    switch (kind) {
      case "notehead": return { noteheadGlyph: glyph, noteheadSmufl: meta && meta.id, noteheadPlayback: playback };
      case "accidental": return { acc: glyph, accCents: meta && meta.cents == null ? null : Number(meta.cents), accSmufl: meta && meta.id };
      case "articulation": return { art: glyph, artPlayback: playback };
      case "ornament": return { orn: glyph, ornPlayback: playback };
      case "tremolo": return { orn: glyph, tremoloPlayback: playback };
      case "percussion": return { noteheadGlyph: glyph, percussionPlayback: playback };
      case "bowing": return { techniqueGlyph: glyph, techniquePlayback: playback };
      default: return null;
    }
  }

  function applyNoteAttachment(logic, kind, meta, name, glyph) {
    const target = cursorNote(logic) || (typeof logic.selected === "function" ? logic.selected() : null);
    const patch = notePatch(kind, meta, glyph);
    if (target) {
      if (!target.id) target.id = "n" + Math.random().toString(36).slice(2, 9);
      if (patch) {
        logic.editNote(patch, name + " applied to the note");
      } else {
        logic.editNote(n => ({
          marks: (n.marks || []).concat([{ g: glyph || name, name, smufl: meta && meta.id, place: /fingering|string number|fret/.test(words(meta, name)) ? "below" : "above" }])
        }), name + " attached to the note");
      }
      logic.setState({ halo: false, scoreObjectId: null, spoken: name + " applied to the note" });
      if (typeof logic.audition === "function" && !target.rest) {
        try { logic.audition(target.step, target.s, patch && patch.acc || target.acc, patch && patch.art || target.art, Object.assign({}, target, patch || {})); } catch (_) {}
      }
      return true;
    }

    if (patch) {
      logic.setState(s => ({ armed: Object.assign({}, s.armed || {}, patch), halo: false, scoreObjectId: null, spoken: name + " armed — the next note gets it" }));
      return true;
    }

    logic.placeScoreEvent("glyph", name, glyph, glyph || name, { system: false, text: glyph || name, meta });
    return true;
  }

  function patchLogic(Logic) {
    const proto = Logic && Logic.prototype;
    if (!proto || proto.__legatoTotalPlacement === PATCH_VERSION) return !!proto;

    const originalSelected = proto.selected;
    proto.selected = function selectedWithCursorFallback() {
      const explicit = typeof originalSelected === "function" ? originalSelected.call(this) : null;
      if (explicit) return explicit;
      const s = this.state || {};
      if (s.scoreObjectId) return null;
      return cursorNote(this);
    };

    const originalScoreAnchor = proto.scoreAnchor;
    proto.scoreAnchor = function stableScoreAnchor() {
      const s = this.state || {};
      if (s.zone === 3 || s.halo || s.spanDraft || s.panel && /^score-/.test(String(s.panel))) return cursorAnchor(this);
      return typeof originalScoreAnchor === "function" ? originalScoreAnchor.call(this) : cursorAnchor(this);
    };

    proto.placeScoreEvent = function placeCommittedScoreEvent(type, name, glyph, value, options) {
      const opts = options || {};
      const anchor = opts.anchor || cursorAnchor(this);
      const system = opts.system != null ? !!opts.system : /^(key|meter|tempo|rehearsal|structure|system-text)$/.test(type);
      const meta = opts.meta || null;
      const semanticKey = meta && (meta.id || meta.smufl) || String(name || value || type);
      if (typeof this.rumble === "function") this.rumble("soft");
      this.setState(s => {
        const draft = s.scoreEventDraft || {};
        const editing = opts.editing || draft.editing || null;
        const ev = {
          id: editing || (typeof this.scoreId === "function" ? this.scoreId("e") : "e" + Math.random().toString(36).slice(2, 9)),
          object: "event", type, name: name || value || type, text: opts.text || name || value || type,
          glyph: glyph || "", value, s: anchor.s, p: anchor.p, step: anchor.step, noteId: anchor.noteId || null,
          system, semanticKey, placement: meta && meta.placement || "event"
        };
        if (meta) Object.assign(ev, { smufl: meta.id || null, range: meta.range || null, playback: Object.assign({}, meta) });
        ["offsetX", "offsetY", "scale", "flipped", "hidden"].forEach(k => { if (opts[k] != null) ev[k] = opts[k]; });

        const singleton = /^(clef|key|meter|tempo|dynamic|hold)$/.test(type);
        let list = (s.scoreEvents || []).filter(x => {
          if (x.id === editing) return false;
          const samePoint = x.type === type && x.system === system && (system || x.s === anchor.s) && Math.abs(Number(x.p) - Number(anchor.p)) < .002;
          if (!samePoint) return true;
          if (singleton) return false;
          return String(x.semanticKey || x.smufl || x.name || x.value) !== String(semanticKey);
        });
        list = list.concat([ev]).sort((a, b) => Number(a.p) - Number(b.p));
        return {
          scoreEvents: list,
          scoreObjectId: null,
          scoreEventDraft: null,
          editingScoreObject: null,
          panel: null,
          halo: false,
          selId: null,
          spoken: ev.name + " placed at bar " + (Math.floor(anchor.p / this.barCapacity()) + 1) + " beat " + (anchor.p % this.barCapacity() + 1).toFixed(2)
        };
      });
    };

    const originalFinishScoreSpan = proto.finishScoreSpan;
    if (typeof originalFinishScoreSpan === "function") {
      proto.finishScoreSpan = function finishAndReleaseScoreSpan(anchor) {
        const done = originalFinishScoreSpan.call(this, anchor);
        if (done) this.setState({ scoreObjectId: null });
        return done;
      };
    }

    proto.applyCatalogCommand = function applyEveryCatalogCommand(meta, name, glyph) {
      meta = Object.assign({}, meta || {});
      const label = name || meta.label || meta.id || "Notation";
      const mark = glyph || meta.glyph || label;
      const kind = inferredKind(meta, label);
      const placement = inferredPlacement(meta, kind, label);
      meta.kind = kind;
      meta.placement = placement;

      if (kind === "tie") {
        const note = cursorNote(this);
        if (note && !note.id) note.id = "n" + Math.random().toString(36).slice(2, 9);
        if (typeof this.toggleTie === "function") this.toggleTie();
        return this.setState({ halo: false, scoreObjectId: null, spoken: label + " applied" });
      }
      if (placement === "span") {
        this.beginScoreSpan(spanType(this, meta, label), label, mark, null, Object.assign({}, meta));
        return;
      }
      if (kind === "clef") {
        const value = typeof this.catalogClefValue === "function" ? this.catalogClefValue(meta) : (/bass|fclef/.test(words(meta, label)) ? "bass" : "treble");
        this.placeScoreEvent("clef", label, mark, value, { system: false, meta });
        return;
      }
      if (kind === "meter") {
        if (/common/.test(words(meta, label)) && !/cut/.test(words(meta, label))) this.placeScoreEvent("meter", label, mark, "4/4", { system: true, meta });
        else if (/cut/.test(words(meta, label))) this.placeScoreEvent("meter", label, mark, "2/2", { system: true, meta });
        else this.placeScoreEvent("meter-glyph", label, mark, mark, { system: true, text: mark, meta });
        return;
      }
      if (kind === "dynamic") {
        this.placeScoreEvent("dynamic", label, mark, mark, { system: false, meta });
        return;
      }
      if (kind === "hold") {
        this.placeScoreEvent("hold", label, mark, mark, { system: false, meta });
        return;
      }
      if (kind === "tempo" && placement !== "span") {
        if (typeof this.openScoreEventPanel === "function") this.openScoreEventPanel("tempo", label, mark);
        else this.placeScoreEvent("tempo", label, mark, Number(meta.bpm) || 92, { system: true, meta });
        return;
      }
      if (kind === "rest") {
        const dur = typeof this.durationFromCatalog === "function" ? this.durationFromCatalog(meta.id, label) : "q";
        this.setState(s => ({ entry: "rest", halo: false, scoreObjectId: null, armed: Object.assign({}, s.armed || {}, { restGlyph: mark, restSmufl: meta.id }), spoken: label + " armed — A enters it" }));
        if (typeof this.setDur === "function") {
          const di = { w: 0, h: 1, q: 2, e: 3, s: 4, t: 5 }[dur];
          if (di != null) this.setDur(di);
        }
        return;
      }
      if (placement === "note" || /^(notehead|accidental|articulation|ornament|tremolo|note-mark|bowing|percussion)$/.test(kind)) {
        applyNoteAttachment(this, kind, meta, label, mark);
        return;
      }
      if (kind === "technique") {
        this.placeScoreEvent("technique", label, mark, label, { system: false, text: label, meta });
        return;
      }
      if (kind === "text") {
        this.placeScoreEvent("text", label, mark, mark, { system: false, text: mark || label, meta });
        return;
      }
      if (kind === "structure" || placement === "structure") {
        this.placeScoreEvent("structure", label, mark, label, { system: true, text: mark || label, meta });
        return;
      }
      this.placeScoreEvent("glyph", label, mark, mark, { system: false, text: mark || label, meta });
    };

    const originalRenderVals = proto.renderVals;
    if (typeof originalRenderVals === "function") {
      proto.renderVals = function placementAwareRenderVals() {
        const vals = originalRenderVals.call(this) || {};
        if (this.state && this.state.scoreObjectId && !this.state.spanDraft) vals.caretStyle = "display:none;";
        return vals;
      };
    }

    Object.defineProperty(proto, "__legatoTotalPlacement", { value: PATCH_VERSION, configurable: true });
    return true;
  }

  function install() {
    try {
      const root = typeof window.__dcRootName === "function" ? window.__dcRootName() : null;
      const registry = window.__dcRegistry;
      const entry = registry && root && registry[root];
      if (!entry || !entry.Logic) return false;
      return patchLogic(entry.Logic);
    } catch (error) {
      console.error("[Legato placement] patch failed", error);
      return false;
    }
  }

  if (!install()) {
    let tries = 0;
    const timer = setInterval(() => {
      tries += 1;
      if (install() || tries > 240) clearInterval(timer);
    }, 50);
  }

  window.__LEGATO_PLACEMENT_PATCH__ = { version: PATCH_VERSION, install, cursorNote, inferredKind, inferredPlacement };
})();
