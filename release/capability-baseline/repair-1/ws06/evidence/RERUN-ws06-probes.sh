#!/usr/bin/env bash
# P2-AR-0019: re-run beta-r audit-of-record probes UNEDITED against this worktree's target/release/gov.
# Usage: SCR=<empty scratch dir> ./RERUN-ws06-probes.sh <outdir> <probe-name>...   (e.g. C3-semantic-memory D1-incremental-freshness)
# Prerequisites: cargo build --release in the worktree; python3 + PyYAML; git.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
WT="$(cd "$HERE/../../../../.." && pwd)"
OUT="$1"; shift
SCR="${SCR:?set SCR to an empty scratch directory}"
mkdir -p "$OUT" "$SCR"
cd "$WT/release/capability-baseline/audit-0/beta-r/evidence"
export PYTHONDONTWRITEBYTECODE=1
for p in "$@"; do
  mkdir -p "$SCR/$p"
  (echo "# command: PROBE_TMP=<scratch> python3 $p.py   (HEAD $(git -C "$WT" rev-parse --short HEAD), run $(date -u +%FT%TZ))"; PROBE_TMP="$SCR/$p" python3 "$p.py" 2>&1) > "$OUT/$p.out"
  echo "$p: $(grep -c '^\[PASS\]' "$OUT/$p.out") pass / $(grep -c '^\[FAIL\]' "$OUT/$p.out") fail$(grep -q Traceback "$OUT/$p.out" && echo ' TRACEBACK')"
done
