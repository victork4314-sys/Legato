#!/usr/bin/env bash
set -euo pipefail
for needle in \
  "toggleTie" \
  "focusList" \
  "activateFocus" \
  "componentDidUpdate" \
  "data-score-caret" \
  "tieStyle" \
  "autoRests:" \
  "staffHits:" \
  "timeTopStyle:" \
  "setupRows:" \
  "themeRows:"; do
  echo "===== $needle ====="
  grep -nF "$needle" index.html || true
  echo
done
