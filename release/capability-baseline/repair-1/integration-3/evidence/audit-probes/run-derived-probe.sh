#!/usr/bin/env bash
# P2-AR-0041 — run a LABELLED DERIVED audit-probe copy (./derived/<file>; each file's header states exactly what it changes
# from its audit-of-record original) through the same scratch mirror run-audit-probe.sh created for the same ADAPTER
# (mode shim), so it reaches the same evidence adapter over this worktree's target/release/gov. Modelled on WS-5's
# P2-AR-0036 run-derived-probe.sh. Output: ./<label>/derived.<file-stem>.out (+ .shimlog).
# Usage: P2AR0041_SCRATCH=<dir> [ADAPTER=<adapter>] run-derived-probe.sh <label> <family> <derived-file>   (family: synthesis | zeta-r | beta-r)
set -u
LABEL="${1:?label}"; FAM="${2:?family}"; FILE="${3:?derived file}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0041_SCRATCH:?set P2AR0041_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
ADAPTER="${ADAPTER:-$WT/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py}"
ROOT="$SCRB/mirror-shim-$(echo "$WT|$ADAPTER" | sha256sum | cut -c1-12)"
[ -x "$ROOT/target/release/gov" ] || { echo "no mirror $ROOT (run run-audit-probe.sh <label> $WT shim ... with the same ADAPTER first)"; exit 2; }
BIN="$ROOT/target/release/gov"; EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
# FILE: a file in ./derived/, or (P2-AR-0041) an absolute path to another builder's labelled derived copy, run unedited
case "$FILE" in /*) SRC="$FILE" ;; *) SRC="$HERE/derived/$FILE" ;; esac
STEM="$(basename "${FILE%.*}")"
S="$(mktemp -d "$SCRB/ap-$LABEL-derived-$STEM-XXXXXX")"; mkdir -p "$S/tmp" "$HERE/$LABEL"
OUT="$HERE/$LABEL/derived.$STEM.out"
{
  echo "# P2-AR-0041 derived audit-probe run: $FAM derived/$FILE label=$LABEL mode=shim"
  echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
  echo "# derived probe sha256 $(sha256sum "$SRC" | cut -c1-64); real gov $(sha256sum "$WT/target/release/gov" | cut -c1-64) via $BIN"
  echo "# evidence adapter $ADAPTER (sha256 $(sha256sum "$ADAPTER" | cut -c1-64))"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
export P2AR0022_SHIM_LOG="$OUT.shimlog" P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$OUT.shimlog"
(
  cd "$EVD" || exit 9
  export TMPDIR="$S/tmp"
  case "$FAM" in
    synthesis) SYNTH_LIB="$EVD/lib" GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1200 python3 "$SRC" ;;
    zeta-r)    WT_AUDIT0_ZETA="$EVD" ZPROBE_SCRATCH="$S" timeout 1200 python3 "$SRC" ;;
    beta-r)    WT_AUDIT0_BETA="$EVD" GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$SRC" ;;
    *) echo "unsupported family $FAM"; exit 2 ;;
  esac
) >> "$OUT" 2>&1
echo "[exit=$?]" >> "$OUT"
printf '%-10s %-60s %s\n' "$FAM" "$STEM" "$(grep -cE '(^|\s)(PASS)(\s|:|$)' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
