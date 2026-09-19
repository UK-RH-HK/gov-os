#!/usr/bin/env bash
# P2-AR-0038 (WS-7, repair iteration 1 round 3) — run audit-of-record probes UNEDITED against the `gov` of a given tree.
# Adapted from WS-6's round-2 runner (repair-1/r2-ws06/evidence/RERUN-probes.sh) with these changes only: the run id;
# gamma-r support (the round-2 WS-7 runner's invocation of its .sh probes); and the shim mode reaches `gov` through the
# round-2 integration builder's derived evidence adapter
#   repair-1/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py
# (used UNEDITED) — the round-1 adapter provisions a standalone human-channel anchor, which P2-ADJ-0001 turned off; the
# derived one provisions the throw-away root that delegates `human-gate` to the same test owner key instead.
#
#   run-probes.sh <tree> <outdir> <mode> <family> <probe> [<probe> ...]
#     tree    a checkout whose target/release/gov is the binary under test (this worktree at its final commit, or the
#             private export of the base 53897c1 with the base binary); the probe files are read from <tree>
#             (release/capability-baseline/audit-0 is identical in both)
#     mode    direct  the probe's own invocation convention against <tree>/target/release/gov
#             shim    the same probe file reached through a private scratch mirror root whose entries are symlinks to
#                     <tree> except target/release/gov, which runs the derived adapter over the real binary of <tree>
#     family  beta-r gamma-r synthesis
# Scratch: $P2AR0038_SCRATCH (required). Every run gets its own mktemp directory under it; nothing is written outside
# <outdir> and the scratch directory.
set -u
TREE="$(cd "${1:?tree}" && pwd)"; OUTD="${2:?outdir}"; MODE="${3:?mode}"; FAM="${4:?family}"; shift 4
SCRB="${P2AR0038_SCRATCH:?set P2AR0038_SCRATCH}"
mkdir -p "$OUTD" "$SCRB"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV WT_OVERRIDE
SHIM_REL="release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived/gov-owner-channel-shim.root-channel.P2-AR-0032.py"
if [ "$MODE" = shim ]; then
  ROOT="$(mktemp -d "$SCRB/mirror-XXXXXX")"
  mkdir -p "$ROOT/target/release"
  for e in $(ls -A "$TREE"); do [ "$e" = target ] || ln -sfn "$TREE/$e" "$ROOT/$e"; done
  cat > "$ROOT/target/release/gov" <<EOF
#!/usr/bin/env bash
export P2AR0022_REAL_GOV="$TREE/target/release/gov"
export P2AR0022_HC_OWNER="$TREE/release/capability-baseline/repair-1/ws03/evidence/hc_owner.py"
exec python3 "$ROOT/$SHIM_REL" "\$@"
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
    echo "# P2-AR-0038 audit-of-record probe re-run (unedited): $FAM/$P mode=$MODE"
    echo "# tree $TREE HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo '(export of 53897c1)')"
    echo "# probe sha256 $(sha256sum "$TREE/release/capability-baseline/audit-0/$FAM/evidence/$P."* 2>/dev/null | cut -c1-64 | head -1); gov $(sha256sum "$TREE/target/release/gov" | cut -c1-64) via $BIN"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  if [ "$MODE" = shim ]; then export P2AR0022_SHIM_LOG="$OUT.shimlog"; : > "$P2AR0022_SHIM_LOG"; fi
  (
    cd "$EVD" || exit 9
    export TMPDIR="$S/tmp"
    case "$FAM" in
      beta-r)    GOV_WT="$ROOT" PROBE_TMP="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      synthesis) GOV_BIN="$BIN" SYNTH_SCRATCH="$S" timeout 1500 python3 "$EVD/$P.py" ;;
      gamma-r)   GOV="$BIN" WT="$ROOT" PROBES="$S" timeout 1500 bash "$EVD/$P.sh" ;;
      *) echo "family $FAM not supported by this runner"; exit 2 ;;
    esac
  ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
done
