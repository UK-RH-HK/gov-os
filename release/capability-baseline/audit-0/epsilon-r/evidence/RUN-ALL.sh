#!/usr/bin/env bash
# P2-AR-0008 — re-run every epsilon-r probe against a fresh scratch area and rewrite the captured outputs.
# Prerequisite (from the worktree root): ~/.cargo/bin/cargo build --release
# Usage (from the worktree root): bash release/capability-baseline/audit-0/epsilon-r/evidence/RUN-ALL.sh [scratch-dir]
# Regression (AC-15) is captured separately in AC15-cargo-test-{lib,certification}.out:
#   ~/.cargo/bin/cargo test --lib ; ~/.cargo/bin/cargo test --test certification
set -u
EVD="$(cd "$(dirname "$0")" && pwd)"
export SCRATCH="${1:-$(mktemp -d)}"
mkdir -p "$SCRATCH"
echo "# SCRATCH=$SCRATCH  started $(date -u +%FT%TZ)"
for p in 00-baseline-healthy-project O1-product-families O2-governance-families O2-context-reproducibility-race \
         O3-independent-authorship O4-suite-currency O5-scheduler-requirements O5-G0-focus O5-tiers-G1-G6 O5-G5-update \
         P1-P2-telemetry Q-learning-upstream U-slos-and-healthy V-oracle-format-and-contract-views; do
  echo "== $p"; timeout 1800 bash "$EVD/$p.sh" > "$EVD/$p.out" 2>&1; echo "   exit $?"
done
echo "== O5-G0-guard-matrix"; SCRATCH="$SCRATCH/g0" timeout 3600 python3 "$EVD/O5-G0-guard-matrix.py" > "$EVD/O5-G0-guard-matrix.out" 2>&1; echo "   exit $?"
echo "# finished $(date -u +%FT%TZ)"
