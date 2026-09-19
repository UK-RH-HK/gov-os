#!/usr/bin/env bash
# P2-AR-0025 (WS-4, repair-1 round 2) — re-run audit-of-record probes UNEDITED against a chosen gov binary.
#
# Derived from release/capability-baseline/repair-1/integration/evidence/audit-probes/run-audit-probe.sh (P2-AR-0022):
# same per-family invocation conventions and the same owner-channel adapter (gov-owner-channel-shim.py, unedited),
# which adapts ONLY the three paths WS-3 (round 1) removed by design (role declaration, the pre-WS-3 human-answer relay,
# absent gate-package fields). Both the "before" and the "after" run go through the adapter, so they are comparable.
#
#   before  root = a read-only `git archive` export of the base commit 843d79c (the integrated round-1 tree), with its
#           target/release/gov = the adapter running the base binary built from that commit
#   after   root = a private mirror of THIS worktree (symlinks to every entry except target/), with its
#           target/release/gov = the adapter running this worktree's target/release/gov
#
# Usage: P2AR0025_SCRATCH=<dir> run-probe.sh <before|after> <family> <probe> [<probe> ...]
# Output: evidence/<mode>/<family>.<probe>.out (+ .shimlog). The probe files are never edited; their sha256 is logged.
set -u
MODE="${1:?mode}"; FAM="${2:?family}"; shift 2
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
SCRB="${P2AR0025_SCRATCH:?set P2AR0025_SCRATCH}"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
case "$MODE" in
  before)
    ROOT="$SCRB/base-tree"
    REAL="$SCRB/bin/gov-base-843d79c"
    ;;
  after)
    ROOT="$SCRB/mirror-after"
    REAL="$WT/target/release/gov"
    if [ ! -d "$ROOT" ]; then
      mkdir -p "$ROOT"
      for e in $(ls -A "$WT"); do [ "$e" = target ] || ln -sfn "$WT/$e" "$ROOT/$e"; done
    fi
    ;;
  *) echo "mode must be before|after"; exit 2 ;;
esac
SHIM="$ROOT/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py"
HC="$ROOT/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
mkdir -p "$ROOT/target/release"
cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$REAL"
export P2AR0022_HC_OWNER="$HC"
exec python3 "$SHIM" "\$@"
EOF
chmod +x "$ROOT/target/release/gov"
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
OUTD="$HERE/$MODE"; mkdir -p "$OUTD"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/pr-$MODE-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.out"
  {
    echo "# P2-AR-0025 audit-of-record probe re-run (unedited, through the P2-AR-0022 owner-channel adapter): $FAM/$P mode=$MODE"
    echo "# worktree HEAD $(git -C "$WT" rev-parse HEAD); product files differing from HEAD: $(git -C "$WT" status --porcelain -- runtime cli framework migrations Cargo.toml Cargo.lock | wc -l)"
    echo "# probe sha256 $(sha256sum "$EVD/$P."* 2>/dev/null | cut -c1-64 | head -1); real gov $(sha256sum "$REAL" | cut -c1-64) ($REAL)"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      synthesis) if [ -f "$EVD/$P.py" ]; then GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1500 bash "$EVD/$P.sh"; fi ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      alpha-r)   if [ -f "$EVD/$P.py" ]; then GOV="$BIN" PROBE_TMP="$S" timeout 1500 python3 "$EVD/$P.py"; else GOV="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1500 bash "$EVD/$P.sh"; fi ;;
      gamma-r)   if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1500 bash "$EVD/$P.sh"; else GOV="$BIN" GOV_BIN="$BIN" WT="$ROOT" PROBE_TMP="$S" timeout 1500 python3 "$EVD/$P.py"; fi ;;
      epsilon-r) if [ -f "$EVD/$P.sh" ]; then GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1500 bash "$EVD/$P.sh"; else GOV="$BIN" WT="$ROOT" SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py"; fi ;;
      *) echo "unknown family $FAM"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-7s %-10s %-40s %s\n' "$MODE" "$FAM" "$P" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
