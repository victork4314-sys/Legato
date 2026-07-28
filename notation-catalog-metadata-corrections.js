"use strict";
(() => {
  const C = window.__LEGATO_CATALOG_CORE__;
  if (!C) return console.error("[Legato catalog metadata] core missing");
  const VERSION = C.VERSION + "-metadata-1";
  const baseClassify = C.classify;

  function classify(meta, name, glyph) {
    const source = meta || {};
    const out = baseClassify(source, name, glyph);
    const id = String(source.id || "").toLowerCase();
    const label = String(name || source.label || "").toLowerCase();
    const declaredPlacement = String(source.placement || "").toLowerCase();
    const declaredKind = String(source.kind || "").toLowerCase();

    // textTie is a printable character used inside beamed-note text. It is not the
    // controller's Tie command and it is not a two-point organ tie span.
    if (id === "texttie" || (declaredPlacement === "event" && declaredKind === "text" && label === "tie")) {
      out.kind = "text";
      out.placement = "event";
      out.auditRole = "event";
      out.auditBand = "above";
      out.audible = false;
      out.audioRoute = "silent-notation";
    }
    return out;
  }

  function auditCatalog() {
    const glyphs = window.LEGATO_SMUFL_CATALOG && window.LEGATO_SMUFL_CATALOG.glyphs || [];
    const rows = glyphs.map(g => {
      const p = classify(g, g.label, g.glyph);
      return {
        id: g.id,
        label: g.label,
        placement: p.placement,
        kind: p.kind,
        band: p.auditBand,
        role: p.auditRole,
        audible: !!p.audible,
        audioRoute: p.audioRoute
      };
    });
    const failures = rows.filter(r => !r.placement || !r.kind || !r.role || (r.audible && (!r.audioRoute || r.audioRoute === "silent-notation")));
    const byPlacement = rows.reduce((a, r) => (a[r.placement] = (a[r.placement] || 0) + 1, a), {});
    const audible = rows.filter(r => r.audible);
    window.__LEGATO_CATALOG_AUDIT__ = {
      version: VERSION,
      expected: 3451,
      checked: rows.length,
      failures,
      audibleChecked: audible.length,
      byPlacement,
      rows
    };
    if (rows.length !== 3451 || failures.length) console.error("[Legato catalog audit]", window.__LEGATO_CATALOG_AUDIT__);
    else console.info("[Legato catalog audit] 3451/3451 placement profiles and " + audible.length + "/" + audible.length + " audible routes checked");
  }

  C.classify = classify;
  C.auditCatalog = auditCatalog;
  auditCatalog();
  window.__LEGATO_CATALOG_METADATA_CORRECTIONS__ = { version: VERSION, classify, auditCatalog };
})();
