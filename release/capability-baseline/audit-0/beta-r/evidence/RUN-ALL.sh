#!/usr/bin/env bash
# P2-AR-0009 (family beta re-audit): re-run every independent probe against the candidate build.
# Prerequisites: `~/.cargo/bin/cargo build --release` in the candidate checkout (target/release/gov), python3 + PyYAML, git.
# Usage: PROBE_TMP=/some/empty/scratch/dir ./RUN-ALL.sh     (disposable projects are created under PROBE_TMP)
set -u
cd "$(dirname "$0")"
export PROBE_TMP="${PROBE_TMP:-$(mktemp -d -t p2ar0009-XXXX)}"
export PYTHONDONTWRITEBYTECODE=1
for p in C1-deterministic-structured-memory C2-relationship-graph C3-semantic-memory C4-lexical-memory C5-code-structural-memory \
         C6-temporal-memory C7-episodic-memory C8-failure-memory C9-context-packet C10-capability-memory \
         D1-incremental-freshness D2-retrieval-router D3-hierarchical-retrieval D4-component-separation D5-model-selection \
         D6-rebuild-guarantee R1-R2-legacy-and-chat-retirement R3-archive-policy X-K2-D1-W6-interactions \
         FRESH-evidence-invalidation DERIVED-views-reconciliation SCALE-retrieval-latency; do
  (echo "# command: PROBE_TMP=<scratch> python3 $p.py   (run $(date -u +%FT%TZ))"; python3 "$p.py" 2>&1) > "$p.out"
  echo "$p: $(grep -c '^\[PASS\]' "$p.out") pass / $(grep -c '^\[FAIL\]' "$p.out") fail$(grep -q Traceback "$p.out" && echo ' TRACEBACK')"
done
