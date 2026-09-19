#!/usr/bin/env bash
# P2-AR-0035: run a LABELLED DERIVED probe copy written by an earlier run (e.g. WS-4 round 2's
# repair-1/r2-ws04/evidence/derived/K2-cit-e.valid-fixture.P2-AR-0025.py, used unedited) the way run-probe.sh runs the
# audit-of-record probe it derives from: through the same adapter, importing the unedited family harness from the chosen
# root's audit-of-record evidence directory. Derived from repair-1/r2-ws04/evidence/run-derived.sh (P2-AR-0025); only
# the adapter environment (run-probe.sh's) and the scratch/output names change.
# Usage: P2AR0035_SCRATCH=<dir> P2AR0035_BASE_GOV=<gov> run-derived.sh <base|after> <family> <repo-relative derived file>
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; FILE="${3:?derived file}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRB="${P2AR0035_SCRATCH:?}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
"$HERE/run-probe.sh" "$MODE" "$FAM" >/dev/null 2>&1 || true
if [ "$MODE" = base ]; then ROOT="$SCRB/probe-base-tree"; else ROOT="$SCRB/probe-mirror-after"; fi
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
BIN="$ROOT/target/release/gov"
REAL="$(sed -n 's/^export P2AR0026_REAL_GOV="\(.*\)"$/\1/p' "$BIN")"
S="$(mktemp -d "$SCRB/dr-$MODE-$FAM-XXXXXX")"; mkdir -p "$S/tmp"
OUT="$HERE/$MODE/derived.$(basename "$FILE" .py).out"
{ echo "# P2-AR-0035 DERIVED probe run (unedited copy): $FILE mode=$MODE (harness: $EVD)"; echo "# sha256 $(sha256sum "$ROOT/$FILE" | cut -c1-64); real gov $(sha256sum "$REAL" | cut -c1-64)"; } > "$OUT"
export P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0026_SHIM_LOG"
( cd "$EVD" && TMPDIR="$S/tmp" PYTHONPATH="$EVD" GOV_BIN="$BIN" PROBE_SCRATCH="$S" ZPROBE_SCRATCH="$S" SYNTH_SCRATCH="$S" X2_LIB="$EVD/lib" timeout 1500 python3 "$ROOT/$FILE" ) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
echo "$MODE $(basename "$FILE"): $(grep -cE ' PASS' "$OUT") PASS, $(grep -cE ' FAIL' "$OUT") FAIL, $(tail -1 "$OUT")"
