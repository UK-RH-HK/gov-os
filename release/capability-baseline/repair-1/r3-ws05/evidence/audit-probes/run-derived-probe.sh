#!/usr/bin/env bash
# P2-AR-0036 — run a DERIVED probe copy (./derived/<file>, each file's header states exactly what it changes from its
# audit-of-record original) in one of the modes of run-audit-probe.sh, through the same scratch mirror roots (so
# after-shim / base-shim reach the same adapter over this worktree's binary / the round-3 base binary). The mirror
# roots must already exist (run-audit-probe.sh creates them on first use). Output: ./<mode>/derived.<file-stem>.out
# Usage: P2AR0036_SCRATCH=<dir> run-derived-probe.sh <mode> <family> <derived-file>
#   family: gamma-r (bash, lib.sh conventions) | zeta-r (python, zprobe conventions) | beta-r (python, govprobe conventions)
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; FILE="${3:?derived file}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0036_SCRATCH:?set P2AR0036_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
ROOT="$SCRB/mirror-$MODE"
[ -e "$ROOT/target/release/gov" ] || { echo "no mirror for $MODE under $SCRB (run run-audit-probe.sh $MODE first)"; exit 2; }
case "$MODE" in after|after-shim) REAL="$WT/target/release/gov" ;; *) REAL="${P2AR0036_BASE_GOV:-<base gov of the mirror>}" ;; esac
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
SRC="$HERE/derived/$FILE"
STEM="${FILE%.*}"
S="$(mktemp -d "$SCRB/ap-$MODE-derived-$STEM-XXXXXX")"; mkdir -p "$S/tmp"
OUT="$HERE/$MODE/derived.$STEM.out"; mkdir -p "$HERE/$MODE"
{
  echo "# P2-AR-0036 derived probe re-run: $FAM derived/$FILE mode=$MODE"
  echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
  echo "# derived probe sha256 $(sha256sum "$SRC" | cut -c1-64); real gov $( [ -f "$REAL" ] && sha256sum "$REAL" | cut -c1-64 || echo "$REAL") via $BIN"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
case "$MODE" in *shim) export P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0026_SHIM_LOG" ;; esac
(
  cd "$EVD" || exit 9
  export TMPDIR="$S/tmp"
  case "$FAM" in
    gamma-r) GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1200 bash "$SRC" ;;
    zeta-r)  WT_AUDIT0_ZETA="$EVD" ZPROBE_SCRATCH="$S" timeout 1200 python3 "$SRC" ;;
    beta-r)  WT_AUDIT0_BETA="$EVD" GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$SRC" ;;
    *) echo "unsupported family $FAM"; exit 2 ;;
  esac
) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
printf '%-10s %-10s %-55s %s\n' "$MODE" "$FAM" "derived/$FILE" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
