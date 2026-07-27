#!/usr/bin/env bash
set -euo pipefail
for needle in \
  "toggleTie()" \
  "autoRests:" \
  "focusList()" \
  "activateFocus()" \
  "function midiFor" \
  "timeTopStyle:" \
  "staffHits:" \
  "componentDidUpdate()" \
  "const DOC_KEYS" \
  "constructor(props)" \
  "themeRows:" \
  "setupRows:" \
  "previous-zone':" \
  "selectNote(" \
  "enterNote()" \
  "tieStyle:" \
  "data-score-caret"; do
  printf '%-28s ' "$needle"
  grep -nF "$needle" index.html | head -1 || true
done
