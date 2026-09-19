#!/usr/bin/env bash
# P2-AR-0030 — run the second-generation DERIVED copy of P2-AR-0021's round-1 builder probe
# (derived-B-ws0911-regression-probes.owner-channel.reviewer-tests.P2-AR-0030.py.txt) against one tree's gov, from a scratch
# mirror root that places the copy at the depth its worktree resolution expects. Output: ./<tree>/B-ws0911-regression.derived.out
# Usage: P2AR0030_SCRATCH=<dir> P2AR0030_BASE_TREE=<dir> run-derived-b.sh <after|before>
set -u
TREE="${1:?tree}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../../.." && pwd)"
SCRB="${P2AR0030_SCRATCH:?}"
case "$TREE" in after) ROOT="$WT" ;; before) ROOT="${P2AR0030_BASE_TREE:?}" ;; *) exit 2 ;; esac
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
M="$(mktemp -d "$SCRB/mirror-b-$TREE-XXXXXX")"
for e in $(ls -A "$ROOT"); do [ "$e" = release ] || ln -sfn "$ROOT/$e" "$M/$e"; done
mkdir -p "$M/release/capability-baseline/repair-1/x/evidence"
ln -sfn "$ROOT/release/capability-baseline/audit-0" "$M/release/capability-baseline/audit-0"
ln -sfn "$WT/release/capability-baseline/repair-1/ws03" "$M/release/capability-baseline/repair-1/ws03"
cp "$HERE/derived-B-ws0911-regression-probes.owner-channel.reviewer-tests.P2-AR-0030.py.txt" "$M/release/capability-baseline/repair-1/x/evidence/derived_b.py"
OUTD="$HERE/$TREE"; mkdir -p "$OUTD"; OUT="$OUTD/B-ws0911-regression.derived.out"
S="$(mktemp -d "$SCRB/p-derived-b-$TREE-XXXXXX")"
{ echo "# P2-AR-0030 DERIVED round-1 builder probe (reviewer tests added) tree=$TREE"; echo "# gov $(sha256sum "$ROOT/target/release/gov" | cut -c1-64)"; echo "# date $(date -u +%FT%TZ)"; } > "$OUT"
( cd "$M" && GOV_BIN="$ROOT/target/release/gov" SYNTH_SCRATCH="$S" timeout 1800 python3 "$M/release/capability-baseline/repair-1/x/evidence/derived_b.py" ) >> "$OUT" 2>&1
echo "# exit $?" >> "$OUT"
echo "$OUT"
