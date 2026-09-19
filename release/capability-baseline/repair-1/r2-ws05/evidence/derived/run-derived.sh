#!/usr/bin/env bash
# P2-AR-0026 — run a labelled DERIVED probe copy from this directory against a chosen gov, writing ./<mode>/<name>.out.
#   modes: after | base | after-shim | base-shim — the same binaries/adapter as ../audit-probes/run-audit-probe.sh (the
#   *-shim modes reuse that runner's scratch mirrors, so run that runner once per mode first).
# Usage: P2AR0026_SCRATCH=<dir> P2AR0026_BASE_GOV=<gov> run-derived.sh <mode> <derived-file.py> [extra env assignments]
set -u
MODE="${1:?mode}"; F="${2:?derived probe}"; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0026_SCRATCH:?}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
case "$MODE" in
  after) BIN="$WT/target/release/gov" ;;
  base) BIN="${P2AR0026_BASE_GOV:?}" ;;
  after-shim) BIN="$SCRB/mirror-after-shim/target/release/gov" ;;
  base-shim) BIN="$SCRB/mirror-base-shim/target/release/gov" ;;
esac
NAME="$(basename "$F" .py)"
OUTD="$HERE/$MODE"; mkdir -p "$OUTD"; OUT="$OUTD/$NAME.out"
S="$(mktemp -d "$SCRB/dv-$MODE-$NAME-XXXXXX")"; mkdir -p "$S/tmp"
{ echo "# P2-AR-0026 DERIVED probe run: $NAME mode=$MODE"; echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); derived sha256 $(sha256sum "$HERE/$F" | cut -c1-64); gov $BIN"; echo "# date $(date -u +%FT%TZ)"; } > "$OUT"
case "$MODE" in *shim) export P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0026_SHIM_LOG" ;; esac
( cd "$HERE"; export TMPDIR="$S/tmp"; env "$@" GOV_BIN="$BIN" SYNTH_SCRATCH="$S" X2_LIB="$WT/release/capability-baseline/audit-0/synthesis/evidence/lib" timeout 1500 python3 "$HERE/$F" ) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
printf '%-10s %-60s %s\n' "$MODE" "$NAME" "$(grep -cE '^X \S+ PASS' "$OUT") PASS, $(grep -cE '^X \S+ FAIL' "$OUT") FAIL, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
