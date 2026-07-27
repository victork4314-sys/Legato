"use strict";
(() => {
  const PATCH_VERSION = "20260727-cursor-priority-1";
  const NOTE_EPSILON = 0.021;

  function noteUnderCursor(logic) {
    const s = logic && logic.state;
    if (!s || !Array.isArray(s.notes)) return null;
    const staff = Number(s.staff) || 0;
    const pos = Number(s.pos) || 0;
    return s.notes
      .filter(n => n && n.s === staff && Math.abs(Number(n.p) - pos) <= NOTE_EPSILON)
      .sort((a, b) => Math.abs(Number(a.p) - pos) - Math.abs(Number(b.p) - pos) || Number(a.rest) - Number(b.rest))[0] || null;
  }

  function install() {
    const root = typeof window.__dcRootName === "function" ? window.__dcRootName() : null;
    const entry = window.__dcRegistry && root && window.__dcRegistry[root];
    const proto = entry && entry.Logic && entry.Logic.prototype;
    if (!proto || !proto.__legatoTotalPlacement) return false;
    if (proto.__legatoCursorPriority === PATCH_VERSION) return true;

    const selected = proto.selected;
    proto.selected = function selectedWithCursorPriority() {
      const s = this.state || {};
      if (s.scoreObjectId) return null;
      const underCursor = noteUnderCursor(this);
      if (underCursor && (s.zone === 3 || s.halo || s.spanDraft)) return underCursor;
      const explicit = typeof selected === "function" ? selected.call(this) : null;
      return explicit || underCursor;
    };

    Object.defineProperty(proto, "__legatoCursorPriority", { value: PATCH_VERSION, configurable: true });
    return true;
  }

  if (!install()) {
    let attempts = 0;
    const timer = setInterval(() => {
      attempts += 1;
      if (install() || attempts > 240) clearInterval(timer);
    }, 50);
  }
})();
