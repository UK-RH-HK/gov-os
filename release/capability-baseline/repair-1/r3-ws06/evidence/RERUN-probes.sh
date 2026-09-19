#!/usr/bin/env bash
# P2-AR-0037 (WS-6, repair iteration 1 round 3) — run audit-of-record probes UNEDITED against the `gov` of a given tree.
# Derived from this workstream's round-2 runner (repair-1/r2-ws06/evidence/RERUN-probes.sh); the only change is the
# evidence adapter of `shim` mode: the round-2 integration's derived owner-channel adapter
# (repair-1/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py, used
# UNEDITED), which relays a pre-WS-3 human `decide` through the provisioned throw-away root's `human-gate` delegation
# instead of the standalone anchor P2-ADJ-0001 turned off.
#   RERUN-probes.sh <tree> <outdir> <mode> <family> <probe> [<probe> ...]
#     tree    a checkout whose target/release/gov is the binary under test (this worktree, or the private `git archive`
#             export of the base 53897c1 with its own release binary: before-runs); probe files are read from <tree>
#             (identical in both: release/capability-baseline/audit-0 is unchanged)
#     mode    direct  the probe's own invocation convention against <tree>/target/release/gov
#             shim    the same probe reached through a private scratch mirror of <tree> whose target/release/gov runs the
#                     adapter above over the real binary of <tree>
#             shim5   as shim, with the round-2 integration's derived WS-5 adapter instead
#                     (derived/gov-adapter.ws05.root-channel.P2-AR-0032.py, UNEDITED: shim's adaptations plus completion of
#                     the W5 receipt fields at task close), for probes whose own task close predates BC-P2-20
#     family  beta-r delta-r zeta-r synthesis
#     probe   a probe name of the family's audit-of-record evidence directory, or `derived:<file>` for a LABELLED
#             derived copy under this directory's derived/ (run from the family's evidence directory, with its helpers
#             on PYTHONPATH; the copy's header lists every change)
# Scratch: $P2AR0037_SCRATCH (required). Every run gets its own mktemp directory under it; nothing is written outside
# <outdir> and the scratch directory.
set -u
TREE="$(cd "${1:?tree}" && pwd)"; OUTD="${2:?outdir}"; MODE="${3:?mode}"; FAM="${4:?family}"; shift 4
SCRB="${P2AR0037_SCRATCH:?set P2AR0037_SCRATCH}"
mkdir -p "$OUTD" "$SCRB"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
R="$TREE/release/capability-baseline/repair-1"
if [ "$MODE" = shim ] || [ "$MODE" = shim5 ]; then
  ROOT="$(mktemp -d "$SCRB/mirror-XXXXXX")"
  mkdir -p "$ROOT/target/release"
  for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$ROOT/$e"; done
  if [ "$MODE" = shim ]; then AD="gov-owner-channel-shim.root-channel.P2-AR-0032.py"; else AD="gov-adapter.ws05.root-channel.P2-AR-0032.py"; fi
  cat > "$ROOT/target/release/gov" <<EOS
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$TREE/target/release/gov"
export P2AR0022_HC_OWNER="$R/ws03/evidence/hc_owner.py"
export P2AR0026_REAL_GOV="$TREE/target/release/gov"
export P2AR0026_HC_OWNER="$R/ws03/evidence/hc_owner.py"
exec python3 "$R/integration-2/evidence/builder-probes/derived/$AD" "\$@"
EOS
  chmod +x "$ROOT/target/release/gov"
else
  ROOT="$TREE"
fi
BIN="$ROOT/target/release/gov"
EVD="$ROOT/release/capability-baseline/audit-0/$FAM/evidence"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for P in "$@"; do
  case "$P" in
    derived:*) PF="$HERE/derived/${P#derived:}"; PN="$(basename "${P#derived:}" .py)" ;;
    *) PF="$EVD/$P.py"; PN="$P" ;;
  esac
  S="$(mktemp -d "$SCRB/run-$MODE-$FAM-$PN-XXXXXX")"; mkdir -p "$S/tmp"
  OUT="$OUTD/$FAM.$PN.$MODE.out"
  {
    echo "# P2-AR-0037 audit-of-record probe re-run (unedited): $FAM/$P mode=$MODE"
    echo "# tree $TREE HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo '(git archive export of 53897c1)')"
    echo "# probe $PF sha256 $(sha256sum "$PF" 2>/dev/null | cut -c1-64); gov $(sha256sum "$TREE/target/release/gov" | cut -c1-64) via $BIN"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  if [ "$MODE" != direct ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog" P2AR0026_SHIM_LOG="$OUT.shimlog"; : > "$OUT.shimlog"; fi
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp" PYTHONPATH="$EVD:$EVD/lib${PYTHONPATH:+:$PYTHONPATH}"
    case "$FAM" in
      zeta-r)    ZPROBE_SCRATCH="$S" timeout 1500 python3 "$PF" ;;
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1500 python3 "$PF" ;;
      synthesis) GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1500 python3 "$PF" ;;
      delta-r)   GOV_BIN="$BIN" PROBE_SCRATCH="$S" timeout 1500 python3 "$PF" ;;
      *) echo "family $FAM not supported by this runner"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-10s %-40s %-6s %s\n' "$FAM" "$PN" "$MODE" "$(grep -cE '(^|\s)(PASS)(\s|:|$)|\[PASS\]' "$OUT") pass-marks, $(grep -cE '(^|\s)(FAIL)(\s|:|$)|\[FAIL\]' "$OUT") fail-marks, $(grep -c Traceback "$OUT") tracebacks, $(tail -1 "$OUT")"
done
