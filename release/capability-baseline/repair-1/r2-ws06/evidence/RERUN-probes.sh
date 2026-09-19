#!/usr/bin/env bash
# P2-AR-0027 (WS-6, repair iteration 1 round 2) — run audit-of-record probes UNEDITED against the `gov` of a given tree.
#   RERUN-probes.sh <tree> <outdir> <mode> <family> <probe> [<probe> ...]
#     tree    a checkout whose target/release/gov is the binary under test (this worktree, or the private base export
#             of 843d79c with the base binary: before-runs); the probe files are read from <tree> (they are identical
#             in both: release/capability-baseline/audit-0 is unchanged)
#     mode    direct  the probe's own invocation convention against <tree>/target/release/gov
#             shim    the same probe file reached through a private scratch mirror root whose entries are symlinks to
#                     <tree> except target/release/gov, which runs the round-1 integration's evidence adapter
#                     (repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py, used UNEDITED: role
#                     declaration, owner-signed relay of pre-WS-3 `decide`, absent gate-package fields) over the real
#                     binary of <tree>
#     family  alpha-r beta-r gamma-r delta-r epsilon-r zeta-r synthesis
# Scratch: $P2AR0027_SCRATCH (required). Every run gets its own mktemp directory under it; nothing is written outside
# <outdir> and the scratch directory.
set -u
TREE="$(cd "${1:?tree}" && pwd)"; OUTD="${2:?outdir}"; MODE="${3:?mode}"; FAM="${4:?family}"; shift 4
SCRB="${P2AR0027_SCRATCH:?set P2AR0027_SCRATCH}"
mkdir -p "$OUTD" "$SCRB"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
if [ "$MODE" = shim ]; then
  ROOT="$(mktemp -d "$SCRB/mirror-XXXXXX")"
  mkdir -p "$ROOT/target/release"
  for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$ROOT/$e"; done
  cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$TREE/target/release/gov"
export P2AR0022_HC_OWNER="$TREE/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$TREE/release/capability-baseline/repair-1/integration/evidence/audit-probes/gov-owner-channel-shim.py" "\$@"
EOF
  chmod +x "$ROOT/target/release/gov"
else
  ROOT="$TREE"
fi
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
for P in "$@"; do
  S="$(mktemp -d "$SCRB/run-$MODE-$FAM-$P-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$P.$MODE.out"
  {
    echo "# P2-AR-0027 audit-of-record probe re-run (unedited): $FAM/$P mode=$MODE"
    echo "# tree $TREE HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo '(export of 843d79c)')"
    echo "# probe sha256 $(sha256sum "$TREE/release/capability-baseline/audit-0/$FAM/evidence/$P."* 2>/dev/null | cut -c1-64 | head -1); gov $(sha256sum "$TREE/target/release/gov" | cut -c1-64) via $BIN"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"; fi
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      synthesis) GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 1200 python3 "$EVD/$P.py" ;;
      *) echo "family $FAM not supported by this runner"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-10s %-40s %-6s %s\n' "$FAM" "$P" "$MODE" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
