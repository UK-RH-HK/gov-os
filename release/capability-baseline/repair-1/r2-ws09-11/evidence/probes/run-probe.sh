#!/usr/bin/env bash
# P2-AR-0030 — re-run audit-of-record probes (release/capability-baseline/audit-0/<family>/evidence/), UNEDITED, against
# the `gov` of one of two trees, in one of two modes. Output only to ./<tree>-<mode>/<family>.<probe>[.<label>].out.
#
#   tree   after   this worktree (target/release/gov built from the work commit)
#          before  a `git archive` of the base 843d79c (the integrated round-1 tree) with the base binary copied to its
#                  target/release/gov — the negative control; the probe file is run from that tree, so its fixtures
#                  and canonical root are the base ones too
#   mode   direct  the real binary, each family's own invocation convention
#          shim    the same probe file, but `gov` is the round-1 integration's evidence adapter
#                  (repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py, used UNEDITED by path, with
#                  WS-3's test-material signer hc_owner.py): it adapts only (a) an invocation that declares no role →
#                  `--role orchestrator`, (b) a relayed human `decide` → an owner-signed answer, (c) missing gate-package
#                  fields. Adoption stage roles, sessions and every other argument pass through unchanged.
#
# Usage: P2AR0030_SCRATCH=<dir> P2AR0030_BASE_TREE=<dir> run-probe.sh <tree> <mode> <family> <probe> [label|-] [VAR=value ...]
set -u
TREE="${1:?tree}"; MODE="${2:?mode}"; FAM="${3:?family}"; P="${4:?probe}"; LABEL="${5:--}"
[ "$LABEL" = "-" ] && LABEL=""
if [ $# -ge 5 ]; then shift 5; else shift $#; fi
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
SCRB="${P2AR0030_SCRATCH:?set P2AR0030_SCRATCH}"
case "$TREE" in
  after) ROOT="$WT" ;;
  before) ROOT="${P2AR0030_BASE_TREE:?set P2AR0030_BASE_TREE}" ;;
  *) echo "tree must be after|before"; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV
REAL="$ROOT/target/release/gov"
if [ "$MODE" = shim ]; then
  W="$SCRB/shim-$TREE"; mkdir -p "$W"
  cat > "$W/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$REAL"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$WT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py" "\$@"
EOF
  chmod +x "$W/gov"; BIN="$W/gov"
else
  BIN="$REAL"
fi
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/$TREE-$MODE"; mkdir -p "$OUTD"
OUT="$OUTD/$FAM.$P${LABEL:+.$LABEL}.out"
S="$(mktemp -d "$SCRB/p-$TREE-$MODE-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
{
  echo "# P2-AR-0030 audit-of-record probe re-run (unedited): $FAM/$P tree=$TREE mode=$MODE ${LABEL:+label=$LABEL} extra-env: $*"
  echo "# tree HEAD $(git -C "$WT" rev-parse HEAD 2>/dev/null) (after) / base 843d79c (before); probe sha256 $(sha256sum "$EVD/$P."* 2>/dev/null | cut -c1-64 | head -1)"
  echo "# gov $(sha256sum "$REAL" | cut -c1-64) via $BIN"
  echo "# date $(date -u +%FT%TZ)"
} > "$OUT"
if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"; fi
(
  cd "$EVD" || exit 9
  export TMPDIR="$S/tmp"
  for kv in "$@"; do export "$kv"; done
  case "$FAM" in
    alpha-r)   GOV="$BIN" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py" ;;
    epsilon-r) GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 bash "$EVD/$P.sh" ;;
    gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1200 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py"; fi ;;
    beta-r)    GOV_WT="$ROOT" GOV="$BIN" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py" ;;
    zeta-r)    ZPROBE_SCRATCH="$S" GOV="$BIN" timeout 1200 python3 "$EVD/$P.py" ;;
    synthesis) if [ -f "$EVD/$P.py" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1200 bash "$EVD/$P.sh"; fi ;;
    *) echo "unknown family $FAM"; exit 2 ;;
  esac
) >> "$OUT" 2>&1
echo "# exit $?" >> "$OUT"
echo "$OUT"
