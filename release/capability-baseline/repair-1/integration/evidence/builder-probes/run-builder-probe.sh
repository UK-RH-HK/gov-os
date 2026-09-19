#!/usr/bin/env bash
# P2-AR-0022 (integration builder) — P2-HO-0019 step 6: re-run one round-1 builder's OWN probe script, unedited, from
# its repair-1/<ws>/evidence/ directory against the INTEGRATED binary. Output goes to this directory only
# (<probe>.<mode>.out); nothing is written into another workstream's repair-1 directory:
#   * every run sets PYTHONDONTWRITEBYTECODE=1 (no __pycache__ beside the probes or the audit-of-record libraries);
#   * probes that write beside themselves are run as a byte-identical copy (cmp-verified) from a scratch mirror whose
#     target/ is a symlink to this worktree's target/ (WS-1/12 oracle-format-checks.py writes ./samples and
#     gov-oracle-format.json; WS-8's ws08-probes.sh writes its .out beside itself, so its four probes are run directly).
#
# Usage: P2AR0022_SCRATCH=<dir> run-builder-probe.sh <probe-id> [integrated|roleshim]
#   mode `roleshim` runs the same probe through WS-3's evidence adapter (repair-1/ws03/evidence/gov-role-shim.sh),
#   which injects `--role orchestrator` only where an invocation declares no role; it separates failures caused by
#   WS-3's intended removal of the default role (BC-P2-08) from other integration effects.
set -u
PROBE="${1:?probe id}"
MODE="${2:-integrated}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
R="$WT/release/capability-baseline/repair-1"
SCR="${P2AR0022_SCRATCH:?set P2AR0022_SCRATCH}/bp-$PROBE-$MODE-$(date +%s)"
mkdir -p "$SCR"
REAL="$WT/target/release/gov"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV
if [ "$MODE" = roleshim ]; then
  export WS03_REAL_GOV="$REAL"
  GOVX="$R/ws03/evidence/gov-role-shim.sh"
else
  GOVX="$REAL"
fi
OUT="$HERE/$PROBE.$MODE.out"
{
  echo "# P2-AR-0022 builder-probe re-run: probe=$PROBE mode=$MODE"
  echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
  echo "# gov $REAL sha256 $(sha256sum "$REAL" | cut -d' ' -f1); invoked as $GOVX"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
run() { echo "# \$ $*" >> "$OUT"; "$@" >> "$OUT" 2>&1; echo "[exit=$?]" >> "$OUT"; }
case "$PROBE" in
  ws01-bc01-mutation-controls)
    [ "$MODE" = roleshim ] && { echo "n/a: the probe resolves gov from its worktree path" >> "$OUT"; exit 0; }
    run python3 "$R/ws01-12/evidence/bc-p2-01/mutation-controls.py" "$SCR" ;;
  ws01-bc01-probe-encoding-check)
    run python3 "$R/ws01-12/evidence/bc-p2-01/probe-encoding-check.py" ;;
  ws01-bc51-oracle-format-checks)
    [ "$MODE" = roleshim ] && { echo "n/a: the probe resolves gov from its worktree path" >> "$OUT"; exit 0; }
    M="$SCR/mirror"; D="$M/release/capability-baseline/repair-1/ws01-12/evidence/bc-p2-51"
    mkdir -p "$D"; ln -sfn "$WT/target" "$M/target"
    cp "$R/ws01-12/evidence/bc-p2-51/oracle-format-checks.py" "$D/"
    cp -r "$R/ws01-12/evidence/bc-p2-51/samples" "$D/"
    cmp "$R/ws01-12/evidence/bc-p2-51/oracle-format-checks.py" "$D/oracle-format-checks.py" && echo "# identical copy: oracle-format-checks.py (run from the scratch mirror $M)" >> "$OUT"
    run python3 "$D/oracle-format-checks.py" "$SCR/run" ;;
  ws02-supplementary)
    run env GOV="$GOVX" WS02_SCRATCH="$SCR" python3 "$R/ws02/evidence/supplementary/WS02-supplementary.py" ;;
  ws03-named-checks)
    run env GOV="$GOVX" SCR="$SCR" python3 "$R/ws03/evidence/ws03_named_checks.py" ;;
  ws03-o5-g0-guard-matrix)
    run env WT="$WT" GOV="$GOVX" SCRATCH="$SCR" python3 "$R/ws03/evidence/derived-probes/O5-G0-guard-matrix.derived.py" ;;
  ws04-scenarios)
    run env WS04_GOV="$GOVX" ZPROBE_SCRATCH="$SCR" python3 "$R/ws04/evidence/ws04-scenarios.py" ;;
  ws05-supplementary)
    run env GOV_BIN="$GOVX" PROBE_SCRATCH="$SCR" python3 "$R/ws05/evidence/probes/ws05_supplementary.py" ;;
  ws06-supplementary)
    [ "$MODE" = roleshim ] && { echo "n/a: the beta-r harness resolves gov from its worktree path and declares --role on every call" >> "$OUT"; exit 0; }
    run env PROBE_TMP="$SCR" python3 "$R/ws06/evidence/SUPP-ws06-behaviours.py" ;;
  ws08-P1|ws08-P2|ws08-P3|ws08-P4)
    n="${PROBE#ws08-}"; p="$(cd "$R/ws08/evidence" && ls WS08-$n-*.py)"
    ( cd "$R/ws08/evidence" && run env GOV="$GOVX" PROBE_TMP="$SCR" timeout 900 python3 "$p" ) ;;
  ws09-11-regression-probes)
    run env GOV_BIN="$GOVX" SYNTH_SCRATCH="$SCR" python3 "$R/ws09-11/evidence/B-ws0911-regression-probes.py" ;;
  *) echo "unknown probe $PROBE" >&2; exit 2 ;;
esac
grep -E '^SUMMARY|^total=|^\[exit=' "$OUT" | tail -3
