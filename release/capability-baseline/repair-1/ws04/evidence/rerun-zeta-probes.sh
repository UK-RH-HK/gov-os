#!/usr/bin/env bash
# P2-AR-0017 (WS-4 repair builder): re-run the zeta-r (Gate W) audit-of-record probes UNEDITED against this
# worktree's target/release/gov, writing their outputs into this repair's evidence directory (never into the
# audit-of-record directory, which is read-only for repair builders).
#
# usage: rerun-zeta-probes.sh <out-dir> [probe ...]
#   default probes: every probe the WS-4 round-1 classes cite plus the neighbouring Gate W probes.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
wt="$(cd "$here/../../../../.." && pwd)"
probes_dir="$wt/release/capability-baseline/audit-0/zeta-r/evidence"
out="${1:?out dir}"; shift
mkdir -p "$out"
out="$(cd "$out" && pwd)"
if [ "$#" -eq 0 ]; then
  set -- W00-harness-smoke W01-artefact-identity W01b-migration-plan-identity W02-typed-contracts W03-task-input-manifest \
         W04-context-delivery W04b-input-class-delivery W05-consumption-receipt W06-staleness-propagation W07-orphan-detection \
         W08-lineage W09-session-handoff-continuity W10-hard-invariant-attacks W11-quantitative-health W12-scheduler-integration \
         FR-freshness-invalidation
fi
export ZPROBE_SCRATCH="${ZPROBE_SCRATCH:-$(mktemp -d -t ws04-zprobe-XXXXXX)}"
echo "scratch root: $ZPROBE_SCRATCH" | tee "$out/run.log"
echo "gov: $("$wt/target/release/gov" version 2>/dev/null | tr '\n' ' ')" | tee -a "$out/run.log"
echo "worktree HEAD: $(git -C "$wt" rev-parse HEAD) dirty=$(git -C "$wt" status --porcelain -- runtime cli framework | wc -l)" | tee -a "$out/run.log"
cd "$probes_dir"
for p in "$@"; do
  start=$(date -u +%FT%TZ)
  python3 "$p.py" > "$out/$p.out" 2>&1
  rc=$?
  echo "$start $p exit=$rc $(grep -E '^total=' "$out/$p.out" | tail -1)" | tee -a "$out/run.log"
done
