#!/usr/bin/env bash
# P2-AR-0032 (round-2 integration builder) — re-run one round-2 builder's OWN probe, unedited, from its
# repair-1/r2-<ws>/evidence/ directory (or the round-1 probe it re-ran), against the INTEGRATED binary. Derived from the
# round-1 integration runner (repair-1/integration/evidence/builder-probes/run-builder-probe.sh). Output goes to this
# directory only (<label>/<probe>.out); nothing is written into another workstream's repair-1 directory: every run sets
# PYTHONDONTWRITEBYTECODE=1 and every scratch path is private to this run (P2AR0032_SCRATCH).
#
# Usage: P2AR0032_SCRATCH=<dir> run-builder-probe.sh <label> <probe-id>
#   probe ids: ws02-r2-supplementary ws03-r2-probes ws03-r2-named-checks ws04-r2-scenarios ws05-r2-supplementary
#              ws06-r2-supplementary ws06-r1-supplementary ws07-r2-named-checks ws08-r1-P1..P4 ws08-r1-invariants
#              ws08-cold-cache ws09-11-r2-named-checks ws10-r2-supplementary
#   A derived copy (derived/<file>) is run with probe id `derived:<file>` and the same environment as its original.
set -u
LABEL="${1:?label}"; PROBE="${2:?probe id}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
R="$WT/release/capability-baseline/repair-1"
SCR="${P2AR0032_SCRATCH:?set P2AR0032_SCRATCH}/bp-$LABEL-${PROBE//[:\/]/_}-$(date +%s)-$$"
mkdir -p "$SCR"
REAL="${GOV_UNDER_TEST:-$WT/target/release/gov}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV
mkdir -p "$HERE/$LABEL"
OUT="$HERE/$LABEL/${PROBE//[:\/]/_}.out"
{
  echo "# P2-AR-0032 builder-probe re-run: probe=$PROBE label=$LABEL"
  echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
  echo "# gov $REAL sha256 $(sha256sum "$REAL" | cut -d' ' -f1)"
  echo "# scratch $SCR"
  [ -n "${ADAPTER:-}" ] && echo "# evidence adapter (derived, labelled): $ADAPTER (sha256 $(sha256sum "$ADAPTER" | cut -c1-64))"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
run() { echo "# \$ $*" >> "$OUT"; "$@" >> "$OUT" 2>&1; echo "[exit=$?]" >> "$OUT"; }
# the round-1 integration's owner-channel adapter, reached through a private mirror of this worktree (WS-4 convention)
mirror_with_adapter() {
  local ROOT="$SCR/mirror"
  mkdir -p "$ROOT/target/release"
  for e in $(ls -A "$WT"); do [ "$e" = target ] || ln -sfn "$WT/$e" "$ROOT/$e"; done
  cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$REAL"
export P2AR0022_HC_OWNER="$R/ws03/evidence/hc_owner.py"
export P2AR0026_REAL_GOV="$REAL"
export P2AR0026_HC_OWNER="$R/ws03/evidence/hc_owner.py"
exec python3 "${ADAPTER:-$R/integration/evidence/audit-probes/gov-owner-channel-shim.py}" "\$@"
EOF
  chmod +x "$ROOT/target/release/gov"
  echo "$ROOT"
}
case "$PROBE" in
  derived:*) F="$HERE/derived/${PROBE#derived:}"; ORIG="$(sed -n 's/^# ORIGINAL-PROBE-ID: //p' "$F" | head -1)"
             echo "# derived copy $F (sha256 $(sha256sum "$F" | cut -c1-64)) of probe id $ORIG" >> "$OUT" ;;
  *) F=""; ORIG="$PROBE" ;;
esac
case "$ORIG" in
  ws02-r2-supplementary)
    run env GOV="$REAL" P2AR0023_SCRATCH="$SCR" python3 "${F:-$R/r2-ws02/evidence/WS02-r2-supplementary.py}" ;;
  ws03-r2-probes)
    ( cd "$R/r2-ws03/evidence" && run python3 "${F:-$R/r2-ws03/evidence/R2-WS03-probes.py}" "$REAL" "$SCR" ) ;;
  ws03-r2-named-checks)
    run env GOV="$REAL" SCR="$SCR" python3 "${F:-$R/r2-ws03/evidence/ws03_named_checks.r2-derived.py}" ;;
  ws04-r2-scenarios)
    ROOT="$(mirror_with_adapter)"; EVD="$ROOT/release/capability-baseline/audit-0/delta-r/evidence"
    export P2AR0022_SHIM_LOG="$OUT.shimlog" P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"
    mkdir -p "$SCR/tmp"
    ( cd "$EVD" && run env TMPDIR="$SCR/tmp" PYTHONPATH="$EVD" GOV_BIN="$ROOT/target/release/gov" PROBE_SCRATCH="$SCR" ZPROBE_SCRATCH="$SCR" timeout 1500 python3 "${F:-$R/r2-ws04/evidence/derived/ws04r2-scenarios.py}" ) ;;
  ws05-r2-supplementary)
    run env GOV_BIN="$REAL" PROBE_SCRATCH="$SCR" python3 "${F:-$R/r2-ws05/evidence/probes/ws05_r2_supplementary.py}" ;;
  ws06-r2-supplementary)
    run env GOV_WT="$WT" PROBE_TMP="$SCR" python3 "${F:-$R/r2-ws06/evidence/SUPP-ws06-r2.py}" ;;
  ws06-r1-supplementary)
    run env GOV_WT="$WT" PROBE_TMP="$SCR" python3 "${F:-$R/ws06/evidence/SUPP-ws06-behaviours.py}" ;;
  ws07-r2-named-checks)
    run env GOV_BIN="$REAL" WS07_SCRATCH="$SCR" python3 "${F:-$R/r2-ws07/evidence/ws07_named_checks.py}" ;;
  ws08-r1-P1|ws08-r1-P4)
    n="${ORIG#ws08-r1-}"; d="$R/integration/evidence/builder-probes/derived-ws08"; p="$(cd "$d" && ls WS08-$n-*.py)"
    export WS03_REAL_GOV="$REAL"
    ( cd "$d" && run env GOV="$R/ws03/evidence/gov-role-shim.sh" PROBE_TMP="$SCR" timeout 900 python3 "${F:-$d/$p}" ) ;;
  ws08-r1-P2|ws08-r1-P3)
    n="${ORIG#ws08-r1-}"; d="$R/ws08/evidence"; p="$(cd "$d" && ls WS08-$n-*.py)"
    export WS03_REAL_GOV="$REAL"
    ( cd "$d" && run env GOV="$R/ws03/evidence/gov-role-shim.sh" PROBE_TMP="$SCR" timeout 900 python3 "${F:-$d/$p}" ) ;;
  ws08-r1-invariants)
    run bash "$R/r2-ws08/evidence/r1-invariants.sh" 843d79c33e8a8db8b223611abc23d317edbc82a1 ;;
  ws08-cold-cache)
    run env GOV="$REAL" P2AR0022_SCRATCH="$SCR" python3 "${F:-$R/integration/evidence/concurrency/cold_cache_scheduler.py}" ;;
  ws09-11-r2-named-checks)
    run env GOV_BIN="$REAL" R2_SCRATCH="$SCR" HC_OWNER="$R/ws03/evidence/hc_owner.py" python3 "${F:-$R/r2-ws09-11/evidence/probes/R2-ws0911-named-checks.py}" ;;
  ws10-r2-supplementary)
    run env GOV_BIN="$REAL" PROBE_SCRATCH="$SCR" python3 "${F:-$R/r2-ws10/evidence/probes/ws10_supplementary.py}" ;;
  *) echo "unknown probe $PROBE ($ORIG)" >&2; exit 2 ;;
esac
grep -E '^SUMMARY|^total=|^TOTAL|^\[exit=|PASS [0-9]+/|[0-9]+/[0-9]+ PASS' "$OUT" | tail -4
