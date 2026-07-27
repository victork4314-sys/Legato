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
  "setupRows:"; do
  echo "===== $needle ====="
  line=$(grep -nF "$needle" index.html | head -1 | cut -d: -f1 || true)
  if [[ -z "$line" ]]; then
    echo "NOT FOUND"
    continue
  fi
  start=$((line > 35 ? line - 35 : 1))
  end=$((line + 90))
  sed -n "${start},${end}p" index.html
  echo
 done
