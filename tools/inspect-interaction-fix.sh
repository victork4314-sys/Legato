#!/usr/bin/env bash
set -euo pipefail
for spec in \
  "toggleTie()|28|55" \
  "function midiFor|8|18" \
  "const DOC_KEYS|3|12" \
  "constructor(props)|3|90"; do
  IFS='|' read -r needle before after <<< "$spec"
  echo "===== $needle ====="
  line=$(grep -nF "$needle" index.html | head -1 | cut -d: -f1 || true)
  echo "LINE=${line:-missing}"
  if [[ -z "$line" ]]; then continue; fi
  start=$((line > before ? line - before : 1))
  end=$((line + after))
  sed -n "${start},${end}p" index.html
  echo
 done
