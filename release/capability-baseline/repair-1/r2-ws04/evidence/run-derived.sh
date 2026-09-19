#!/usr/bin/env bash
# P2-AR-0025: run a LABELLED DERIVED probe copy (evidence/derived/) the same way run-probe.sh runs the audit-of-record
# probe it derives from: through the same owner-channel adapter, importing the unedited family harness from the chosen
# root's audit-of-record evidence directory. Usage: P2AR0025_SCRATCH=<dir> run-derived.sh <before|after> <family> <file>
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; FILE="${3:?derived file}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRB="${P2AR0025_SCRATCH:?}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
# reuse run-probe.sh's root/adapter set-up (a no-op probe list creates it)
"$HERE/run-probe.sh" "$MODE" "$FAM" >/dev/null 2>&1 || true
if [ "$MODE" = before ]; then ROOT="$SCRB/base-tree"; else ROOT="$SCRB/mirror-after"; fi
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
BIN="$ROOT/target/release/gov"
S="$(mktemp -d "$SCRB/dr-$MODE-$FAM-XXXXXX")"; mkdir -p "$S/tmp"
OUT="$HERE/$MODE/derived.$(basename "$FILE" .py).out"
{ echo "# P2-AR-0025 DERIVED probe run: $FILE mode=$MODE (harness: $EVD)"; echo "# sha256 $(sha256sum "$HERE/derived/$FILE" | cut -c1-64)"; } > "$OUT"
export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"
( cd "$EVD" && TMPDIR="$S/tmp" PYTHONPATH="$EVD" GOV_BIN="$BIN" PROBE_SCRATCH="$S" ZPROBE_SCRATCH="$S" timeout 1500 python3 "$HERE/derived/$FILE" ) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
echo "$MODE $FILE: $(grep -cE ' PASS' "$OUT") PASS, $(grep -cE ' FAIL' "$OUT") FAIL, $(tail -1 "$OUT")"
