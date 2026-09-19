#!/usr/bin/env bash
# P2-AR-0035 (WS-4, repair-1 round 3) — run the observational probe ws04r3_observe.rs against a tree's own `gov`.
#
# The probe is not product code. This runner exports the named commit with `git archive` into a private scratch
# directory, adds the probe to that copy's certification harness (one `mod` line), builds the copy with its own target
# directory and runs only the probe's tests. The same probe source therefore measures the base tree (negative control)
# and this branch. Optionally a patch (e.g. the IP-R3-WS04-01 gates.rs change offered to WS-3) is applied to the copy
# first, and extra test filters (e.g. an ignored builder test) are run with `--ignored`.
#
# Usage: P2AR0035_SCRATCH=<dir> run-observe.sh <label> <commit> [<patch-file>] [<ignored-test-filter>]
# Output: evidence/observe/<label>.out
set -u
LABEL="${1:?label}"; COMMIT="${2:?commit}"; PATCH="${3:-}"; IGN="${4:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(git -C "$HERE" rev-parse --show-toplevel)"
SCR="${P2AR0035_SCRATCH:?set P2AR0035_SCRATCH}/observe-$LABEL-$(date +%s)-$$"
mkdir -p "$SCR/tree" "$HERE/../observe"
OUT="$HERE/../observe/$LABEL.out"
export PATH="$HOME/.cargo/bin:$PATH" CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR="$SCR/target"
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
git -C "$WT" archive "$COMMIT" | tar -x -C "$SCR/tree"
cp "$HERE/ws04r3_observe.rs" "$SCR/tree/tests/certification/ws04r3_observe.rs"
printf '\nmod ws04r3_observe;\n' >> "$SCR/tree/tests/certification/main.rs"
{
  echo "# P2-AR-0035 observational probe: label=$LABEL commit=$(git -C "$WT" rev-parse "$COMMIT")"
  echo "# probe sha256 $(sha256sum "$HERE/ws04r3_observe.rs" | cut -d' ' -f1)"
  [ -n "$PATCH" ] && echo "# patch applied to the copy: $PATCH (sha256 $(sha256sum "$PATCH" | cut -d' ' -f1))"
  echo "# scratch $SCR"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
if [ -n "$PATCH" ]; then
  ( cd "$SCR/tree" && patch -p1 < "$PATCH" ) >> "$OUT" 2>&1 || { echo "[patch failed]" >> "$OUT"; exit 3; }
fi
( cd "$SCR/tree" && cargo build --tests -q 2>&1 | tail -20 ) >> "$OUT"
echo "# gov $(sha256sum "$SCR/target/debug/gov" | cut -d' ' -f1)" >> "$OUT"
( cd "$SCR/tree" && timeout 1800 cargo test -q --test certification ws04r3_observe -- --nocapture --test-threads=4 2>&1 ) >> "$OUT"
echo "[observe exit=$?]" >> "$OUT"
if [ -n "$IGN" ]; then
  ( cd "$SCR/tree" && timeout 1200 cargo test -q --test certification "$IGN" -- --ignored 2>&1 | grep -E "^test |test result|panicked|MUTATION_SCOPE|assertion" ) >> "$OUT"
  echo "[ignored-test exit=$?]" >> "$OUT"
fi
printf '%-10s %s PASS, %s FAIL\n' "$LABEL" "$(grep -c 'OBSERVE .* PASS ' "$OUT")" "$(grep -c 'OBSERVE .* FAIL ' "$OUT")"
