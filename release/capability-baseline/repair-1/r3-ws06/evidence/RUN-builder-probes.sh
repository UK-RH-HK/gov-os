#!/usr/bin/env bash
# P2-AR-0037 — re-run, UNEDITED, the round-2 integration's labelled derived copies of the builder probes that exercise
# WS-6's area (repair-1/integration-2/evidence/builder-probes/derived/, read only), with the environment the
# integration's runner gives each (run-builder-probe.sh), against the gov of <tree>. Output goes to <outdir> only.
#   RUN-builder-probes.sh <tree> <outdir> <probe-id>...   probe ids: ws02 ws06-r1 ws06-r2 ws10, and ws06-r1-unedited
#   (WS-6 round 1's own SUPP-ws06-behaviours.py, not a derived copy)
#   Scratch: $P2AR0037_SCRATCH (required).
set -u
TREE="$(cd "${1:?tree}" && pwd)"; OUTD="${2:?outdir}"; shift 2
SCRB="${P2AR0037_SCRATCH:?set P2AR0037_SCRATCH}"; mkdir -p "$SCRB" "$OUTD"
D="$TREE/release/capability-baseline/repair-1/integration-2/evidence/builder-probes/derived"
REAL="$TREE/target/release/gov"
export PYTHONDONTWRITEBYTECODE=1
for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
unset GOV
for P in "$@"; do
  SCR="$(mktemp -d "$SCRB/bp-$P-XXXXXX")"
  case "$P" in
    ws02) F="$D/WS02-r2-supplementary.fixtures.P2-AR-0032.py"; ENV=(GOV="$REAL" P2AR0023_SCRATCH="$SCR") ;;
    ws06-r1) F="$D/SUPP-ws06-behaviours.root-channel-registered.P2-AR-0032.py"; ENV=(GOV_WT="$TREE" PROBE_TMP="$SCR") ;;
    ws06-r2) F="$D/SUPP-ws06-r2.root-channel.P2-AR-0032.py"; ENV=(GOV_WT="$TREE" PROBE_TMP="$SCR") ;;
    ws10) F="$D/ws10_supplementary.root-channel.P2-AR-0032.py"; ENV=(GOV_BIN="$REAL" PROBE_SCRATCH="$SCR") ;;
    ws06-r1-unedited) F="$TREE/release/capability-baseline/repair-1/ws06/evidence/SUPP-ws06-behaviours.py"; ENV=(GOV_WT="$TREE" PROBE_TMP="$SCR") ;;
    *) echo "unknown probe $P" >&2; continue ;;
  esac
  OUT="$OUTD/$(basename "$F").out"
  {
    echo "# P2-AR-0037 builder-probe re-run (derived copy, unedited): $F sha256 $(sha256sum "$F" | cut -c1-64)"
    echo "# tree $TREE HEAD $(git -C "$TREE" rev-parse HEAD 2>/dev/null || echo '(git archive export of 53897c1)'); gov sha256 $(sha256sum "$REAL" | cut -c1-64)"
    echo "# date $(date -u +%FT%TZ)"
  } > "$OUT"
  ( export TMPDIR="$SCR"; env "${ENV[@]}" timeout 1500 python3 "$F" ) >> "$OUT" 2>&1
  echo "[exit=$?]" >> "$OUT"
  printf '%-8s %s\n' "$P" "$(grep -E '^SUMMARY|^total=|^TOTAL|PASS [0-9]+/|[0-9]+/[0-9]+ PASS' "$OUT" | tail -1) $(tail -1 "$OUT")"
done
