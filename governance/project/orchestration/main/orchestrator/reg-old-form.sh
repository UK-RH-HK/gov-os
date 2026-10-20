#!/bin/bash
# Full regression in the main tree: every acceptance suite and the builder tests, four groups in parallel.
# Prints one line per suite; a suite's full output is kept beside the summary only when it is not green.
# Usage: bash reg.sh <output directory>   (the caller redirects stdout to the summary file)
cd /home/usain/Dynamic-Agentic-Engineering-OS || exit 1
export PATH="$HOME/.nvm/versions/node/v22.23.3/bin:$PATH"
out="$1"
run() {
  local name="$1" path="$2" tmp
  tmp="$(mktemp)"
  python3 -m pytest "$path" -q -p no:cacheprovider >"$tmp" 2>&1
  local last
  last="$(tail -1 "$tmp")"
  echo "$name: $last"
  case "$last" in *failed*|*error*) cp "$tmp" "$out/$name.full.txt" ;; esac
  rm -f "$tmp"
}
slow1="W1-05"
slow2="W1-02 W1-03"
slow3="W1-04 W1-47"
( for s in $slow1; do run "$s" "tests/acceptance/$s"; done ) &
( for s in $slow2; do run "$s" "tests/acceptance/$s"; done ) &
( for s in $slow3; do run "$s" "tests/acceptance/$s"; done ) &
(
  for d in tests/acceptance/W1-*; do
    s="$(basename "$d")"
    case " $slow1 $slow2 $slow3 " in *" $s "*) continue ;; esac
    run "$s" "$d"
  done
  run unit tests/unit
) &
wait
echo "validator: $(python3 docs/plan/tools/validate_s1.py 2>&1 | tail -1)"
echo "SUITES: read every line above; a suite is green only if its line has no 'failed' and no 'error'"
