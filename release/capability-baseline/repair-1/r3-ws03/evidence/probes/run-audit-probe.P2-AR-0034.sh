#!/usr/bin/env bash
# P2-AR-0034 (WS-3 round 3) — DERIVED from WS-3 round 2's runner (repair-1/r2-ws03/evidence/probes/run-audit-probe.P2-AR-0024.sh):
# re-run audit-of-record probes (release/capability-baseline/audit-0/<family>/evidence/), UNEDITED, against a chosen
# binary. Changes: (1) output goes to this directory (./audit-<label>/); (2) the binary under test is $GOV_UNDER_TEST
# (the base 53897c1 build or this tree's build), recorded in each output; (3) the shim is the round-2 integration
# builder's ROOT-CHANNEL derived shim (repair-1/integration-2/evidence/builder-probes/derived/
# gov-owner-channel-shim.root-channel.P2-AR-0032.py), used read-only from its directory: it adapts only role declaration,
# the pre-WS-3 human-answer relay (through a provisioned throw-away root, never the standalone anchor, P2-ADJ-0001) and
# missing gate-package fields; (4) the scratch mirror is private to this run (P2AR0034_SCRATCH). With GOV_ADAPTER=ws05 the
# adapter is instead the integration builder's derived WS-5 adapter (gov-adapter.ws05.root-channel.P2-AR-0032.py: the
# same adaptations plus completion of ABSENT consumption-receipt fields at task close, and `passed` -> n/a), for probes
# whose closes predate WS-5's receipt contract; each output names the adapter it used.
#   shim   the probe file reached through a scratch mirror root whose entries are symlinks to the tree the binary was
#          built from ($GOV_TREE: this worktree by default, the `git archive` export of the base commit for the base
#          binary — the product finds its canonical framework there) except target/release/gov, which runs the shim
#          over $GOV_UNDER_TEST.
# Usage: P2AR0034_SCRATCH=<private dir> GOV_UNDER_TEST=<gov> run-audit-probe.P2-AR-0034.sh <label> <family> <probe>...
#   family: alpha-r beta-r gamma-r delta-r epsilon-r zeta-r synthesis   probe: file name without extension, or
#   derived:<file> for a labelled derived copy in ./derived/ (its header lists every change), run exactly as its
#   original family's probes are.
set -u
LABEL="${1:?label}"; FAM="${2:?family}"; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../../.." && pwd)"
REAL="${GOV_UNDER_TEST:?set GOV_UNDER_TEST}"
TREE="${GOV_TREE:-$WT}"
SCRB="${P2AR0034_SCRATCH:?set P2AR0034_SCRATCH}/$LABEL"; mkdir -p "$SCRB"
DER="$WT/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived"
case "${GOV_ADAPTER:-shim}" in
  ws05) SHIM="$DER/gov-adapter.ws05.root-channel.P2-AR-0032.py" ;;
  *)    SHIM="$DER/gov-owner-channel-shim.root-channel.P2-AR-0032.py" ;;
esac
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do case "$v" in GOV_UNDER_TEST|GOV_TREE|GOV_ADAPTER) ;; *) unset "$v" ;; esac; done
unset GOV WT_OVERRIDE
ROOT="$SCRB/mirror-${GOV_ADAPTER:-shim}"
if [ ! -x "$ROOT/target/release/gov" ]; then
  mkdir -p "$ROOT/target/release"
  for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$ROOT/$e"; done
  cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$REAL"
export P2AR0022_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
export P2AR0026_REAL_GOV="$REAL"
export P2AR0026_HC_OWNER="$WT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$SHIM" "\$@"
EOF
  chmod +x "$ROOT/target/release/gov"
fi
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/audit-$LABEL"; mkdir -p "$OUTD"
for P in "$@"; do
  case "$P" in
    derived:*) PF="$HERE/derived/${P#derived:}"; PN="${P#derived:}"; PN="${PN%.py}" ;;
    *) PF="$EVD/$P.py"; PN="$P" ;;
  esac
  S="$(mktemp -d "$SCRB/ap-$FAM-$PN-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$PN.out"
  {
    echo "# P2-AR-0034 audit-of-record probe re-run (unedited, through the root-channel shim): $FAM/$P label=$LABEL"
    echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations tools Cargo.toml Cargo.lock | wc -l)"
    echo "# probe $PF sha256 $(sha256sum "$PF" 2>/dev/null | cut -c1-64)"
    echo "# tree $TREE"
    echo "# gov under test $REAL sha256 $(sha256sum "$REAL" | cut -c1-64) via $BIN"
    echo "# shim $SHIM sha256 $(sha256sum "$SHIM" | cut -c1-64)"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  export P2AR0022_SHIM_LOG="$OUT.shimlog" P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 900 python3 "$PF" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 900 python3 "$PF" ;;
      synthesis) if [ -f "$PF" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 900 python3 "$PF"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 900 bash "$EVD/$P.sh"; fi ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 900 python3 "$PF" ;;
      alpha-r)   if [ -f "$PF" ]; then GOV="$BIN" PROBE_TMP="$S" timeout 900 python3 "$PF"; else GOV="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 900 bash "$EVD/$P.sh"; fi ;;
      gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 900 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 900 python3 "$EVD/$P.py"; fi ;;
      epsilon-r) if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 900 bash "$EVD/$P.sh"; else GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 900 python3 "$EVD/$P.py"; fi ;;
      *) echo "unknown family $FAM"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-10s %-45s %s\n' "$FAM" "$PN" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
