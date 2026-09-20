#!/usr/bin/env bash
# P2-AR-0043 (round 4) — copy of the round-3 integration P2-AR-0041 runner (itself a copy of WS-2 P2-AR-0033), changed ONLY in the scratch variable name P2AR0043_SCRATCH (same directory depth: r4-residual/evidence/audit-probes). Re-run audit-of-record probes
# (release/capability-baseline/audit-0/<family>/evidence/) UNEDITED against a tree + its target/release/gov, writing
# ONLY to ./<label>/<family>.<probe>.out next to this script (never into the audit-of-record or another workstream's
# directory). Modelled on the round-1 integration builder's runner (P2-AR-0022 audit-probes/run-audit-probe.sh).
#
# Usage: P2AR0033_SCRATCH=<dir> run-audit-probe.sh <label> <tree-root> <mode> <family> <probe> [<probe> ...]
#   label      output sub-directory (e.g. before, after, before-shim, after-shim)
#   tree-root  a checkout / `git archive` export holding the probes and target/release/gov (the binary under test)
#   mode       direct  — the tree's own target/release/gov
#              shim    — the same probe reached through a scratch mirror of <tree-root> whose target/release/gov runs
#                        the integration builder's evidence adapter (P2-AR-0022 gov-owner-channel-shim.py, unedited;
#                        it adapts only role declaration, the pre-WS-3 human-answer relay and absent gate-package fields)
#                        in front of the real binary of <tree-root>
set -u
LABEL="${1:?label}"; TREE="$(cd "${2:?tree root}" && pwd)"; MODE="${3:?mode}"; FAM="${4:?family}"; shift 4
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0043_SCRATCH:?set P2AR0043_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
# P2-AR-0033: the evidence adapter is the round-2 integration builder's derived owner-channel shim (root channel,
# P2-ADJ-0001) unless ADAPTER names another labelled derived adapter (e.g. its derived WS-5 adapter, which also completes
# consumption receipts at close, BC-P2-20)
ADAPTER="${ADAPTER:-$WT/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py}"
if [ "$MODE" = shim ]; then
  ROOT="$SCRB/mirror-shim-$(echo "$TREE|$ADAPTER" | sha256sum | cut -c1-12)"
  if [ ! -x "$ROOT/target/release/gov" ]; then
    mkdir -p "$ROOT/target/release"
    for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$ROOT/$e"; done
    cat > "$ROOT/target/release/gov" <<EOS
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$TREE/target/release/gov"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
export P2AR0026_REAL_GOV="$TREE/target/release/gov"
export P2AR0026_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$ADAPTER" "\$@"
EOS
    chmod +x "$ROOT/target/release/gov"
  fi
else
  ROOT="$TREE"
fi
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/$LABEL"; mkdir -p "$OUTD"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/ap-$LABEL-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.out"
  {
    echo "# P2-AR-0033 audit-of-record probe re-run (unedited): $FAM/$P label=$LABEL mode=$MODE"
    echo "# tree $TREE (HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || cat "$TREE/.p2ar0033-commit" 2>/dev/null || echo export))"
    echo "# probe sha256 $(sha256sum "$TREE/release/capability-baseline/audit-0/$FAM/evidence/$P."* 2>/dev/null | cut -c1-64 | head -1); gov $(sha256sum "$TREE/target/release/gov" | cut -c1-64) via $BIN"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog" P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$OUT.shimlog"; echo "# evidence adapter $ADAPTER (sha256 $(sha256sum "$ADAPTER" | cut -c1-64))" >> "$OUT"; fi
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      synthesis) if [ -f "$EVD/$P.py" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 bash "$EVD/$P.sh"; fi ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      alpha-r)   if [ -f "$EVD/$P.py" ]; then GOV="$BIN" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py"; else GOV="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1200 bash "$EVD/$P.sh"; fi ;;
      gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1200 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py"; fi ;;
      epsilon-r) if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 bash "$EVD/$P.sh"; else GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py"; fi ;;
      *) echo "unknown family $FAM"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-10s %-45s %s\n' "$FAM" "$P" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
