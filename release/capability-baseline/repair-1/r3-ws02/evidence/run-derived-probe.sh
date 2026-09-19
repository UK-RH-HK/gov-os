#!/usr/bin/env bash
# P2-AR-0033 — run a labelled DERIVED probe copy (evidence/derived/<file>, header lists every change) against a tree:
# the copy imports the audit-of-record library of that tree (so the tree's own binary is measured) and writes only to
# evidence/<label>/derived_<file>.out and to the private scratch P2AR0033_SCRATCH.
# Usage: P2AR0033_SCRATCH=<dir> run-derived-probe.sh <label> <tree-root> <family> <derived-file>
set -u
LABEL="${1:?label}"; TREE="$(cd "${2:?tree}" && pwd)"; FAM="${3:?family}"; F="${4:?derived file}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRB="${P2AR0033_SCRATCH:?set P2AR0033_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
S="$(mktemp -d "$SCRB/dp-$LABEL-XXXXXX")"; mkdir -p "$S/tmp"
OUTD="$HERE/$LABEL"; mkdir -p "$OUTD"; OUT="$OUTD/derived_$F.out"
EVD="$TREE/release/capability-baseline/audit-0/$FAM/evidence"
{
  echo "# P2-AR-0033 derived probe run: $F (sha256 $(sha256sum "$HERE/derived/$F" | cut -c1-64)) label=$LABEL"
  echo "# tree $TREE (HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || cat "$TREE/.p2ar0033-commit" 2>/dev/null || echo export)); gov $(sha256sum "$TREE/target/release/gov" | cut -c1-64)"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
( cd "$EVD" && export TMPDIR="$S/tmp" && ZPROBE_LIB="$EVD/lib" ZPROBE_SCRATCH="$S" timeout 1200 python3 "$HERE/derived/$F" ) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
printf '%-45s %s\n' "$F" "$(grep -cE '(^|\s)PASS(\s|:|$)' "$OUT") pass-marks, $(grep -cE '(^|\s)FAIL(\s|:|$)' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
