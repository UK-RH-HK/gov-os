#!/usr/bin/env bash
# P2-AR-0028 (WS-7) — re-run, UNEDITED, the audit-of-record probes of OTHER families whose fixtures declare capability
# plugins by hand (so BC-P2-39 changes what they observe: an unregistered executable plugin no longer runs), against a
# given `gov`, through the round-1 integration builder's owner-channel evidence adapter (unmodified; see run-probes.sh).
# Purpose: disclose, for the integration builder, every line whose outcome this repair changes and why.
# Each family is invoked with its own convention (as repair-1/integration/evidence/audit-probes/run-audit-probe.sh);
# harnesses that resolve `target/release/gov` under a root are given a private mirror root whose entries are symlinks
# to this worktree, except target/release/gov (the adapter). Outputs: ./cross-family/<label>/<family>.<probe>.out only.
# Usage: P2AR0028_SCRATCH=<dir> run-cross-family.sh <label> <gov-binary> [shim|prereg]
#   prereg: the same, but through gov-ws07-preregister.py (beside this script), which first registers every UNREGISTERED
#           fixture plugin the governed way (register -> present -> owner-signed A -> register) and changes nothing
#           else; used only to show the other families' capabilities still work with governed plugins.
set -u
LABEL="${1:?label}"; BIN="${2:?gov binary}"; MODE="${3:-shim}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SCR="${P2AR0028_SCRATCH:?set P2AR0028_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
SHIM="$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py"
HC="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
ROOT="$SCR/mirror-$LABEL-$MODE"
if [ ! -x "$ROOT/target/release/gov" ]; then
  mkdir -p "$ROOT/target/release"
  for e in $(ls -A "$WT"); do [ "$e" = target ] || ln -sfn "$WT/$e" "$ROOT/$e"; done
  cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$BIN"
export P2AR0022_HC_OWNER="$HC"
export P2AR0028_SHIM="$SHIM"
if [ "$MODE" = prereg ]; then exec python3 "$HERE/gov-ws07-preregister.py" "\$@"; fi
exec python3 "$SHIM" "\$@"
EOF
  chmod +x "$ROOT/target/release/gov"
fi
G="$ROOT/target/release/gov"
OUTD="$HERE/cross-family/$LABEL-$MODE"; mkdir -p "$OUTD"
run() {  # run <family> <probe>
  local FAM="$1" P="$2" EVD="$ROOT/release/capability-baseline/audit-0/$1/evidence"
  local S; S="$(mktemp -d "$SCR/cf-$LABEL-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  local OUT="$OUTD/$FAM.$P.out"
  { echo "# P2-AR-0028 cross-family re-run (unedited probe, adapter mode $MODE): $FAM/$P label=$LABEL"
    echo "# gov $(sha256sum "$BIN" | cut -c1-64)"; } > "$OUT"
  export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"
  ( cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 900 python3 "$EVD/$P.py" ;;
      alpha-r)   GOV="$G" PROBE_TMP="$S" timeout 900 python3 "$EVD/$P.py" ;;
      gamma-r)   GOV="$G" WT="$ROOT" PROBES="$S" timeout 900 bash "$EVD/$P.sh" ;;
      epsilon-r) GOV="$G" WT="$ROOT" SCRATCH="$S" timeout 900 bash "$EVD/$P.sh" ;;
    esac ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  echo "$FAM/$P done"
}
run beta-r C5-code-structural-memory
run beta-r C8-failure-memory
run beta-r D4-component-separation
run beta-r D5-model-selection
run beta-r D6-rebuild-guarantee
run alpha-r A3-security-sensitivity
run alpha-r FRESH-invalidation
run epsilon-r O4-suite-currency
run gamma-r F5-layers
