#!/usr/bin/env bash
# P2-AR-0012 (family zeta-r, Gate W) - re-run every independent probe against this worktree's target/release/gov.
# Prerequisites: `~/.cargo/bin/cargo build --release` in the worktree root; python3 with PyYAML; git.
# Each probe writes <probe>.out next to itself. ZPROBE_SCRATCH (optional) selects the scratch root for disposable projects.
set -u
cd "$(dirname "$0")"
export ZPROBE_SCRATCH="${ZPROBE_SCRATCH:-$(mktemp -d -t zprobe-XXXXXX)}"
echo "scratch root: $ZPROBE_SCRATCH"
echo "gov: $(../../../../../target/release/gov version 2>/dev/null | tr '\n' ' ')"
for p in W00-harness-smoke W01-artefact-identity W01b-migration-plan-identity W02-typed-contracts W03-task-input-manifest \
         W04-context-delivery W04b-input-class-delivery W05-consumption-receipt W06-staleness-propagation W07-orphan-detection W08-lineage \
         W09-session-handoff-continuity W10-hard-invariant-attacks W11-quantitative-health W12-scheduler-integration \
         FR-freshness-invalidation DV-derived-view-reconciliation; do
  start=$(date -u +%FT%TZ)
  python3 "$p.py" > "$p.out" 2>&1
  rc=$?
  echo "$start $p exit=$rc $(grep -E '^total=' "$p.out" | tail -1)"
done
