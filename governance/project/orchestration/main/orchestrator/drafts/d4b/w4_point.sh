#!/usr/bin/env bash
# Re-pin window 4's measures (DEC-1074 (5)): one point = a measure clone at a commit, its store rebuilt (the D-4b
# rebuild lock), the hidden and verdict gold re-pinned at its head (counts only), then the harness's runs on the 80
# (memory-retrieval, all) and the 60 (memory-verdict, hidden). Counts only. Only the CTO runs it.
#   w4_point.sh <point> <commit> <pool-on 0|1> <name> '<GOV_RX json>' [<name> '<json>' ...]
# pool-on 1 commits S11's five pool settings (60, 40, 2, both true) into the clone's retrieval.yaml, so '{}' (the
# harness's no-op, which equals the product's own path) measures the product with v456 built in.
set -uo pipefail
POINT=$1; COMMIT=$2; POOL=$3; shift 3
R=/home/usain/Dynamic-Agentic-Engineering-OS; O=$R/.gov-runtime/scratch/orchestrator; EVAL=$HOME/gov-os-eval
RUN=$HOME/gov-os-runs/D4B/$POINT; mkdir -p "$RUN"
exec > >(tee -a "$RUN/point.log") 2>&1
echo "== $(date '+%F %T') $POINT at $COMMIT (pool on: $POOL)"
[ -d "$RUN/repo" ] || git clone -q --no-hardlinks "$R" "$RUN/repo"
git -C "$RUN/repo" fetch -q "$R" "+refs/heads/*:refs/remotes/main/*" && git -C "$RUN/repo" checkout -q --detach "$COMMIT" || { echo "STOP: checkout"; exit 1; }
if [ "$POOL" = 1 ]; then
  printf 'pool:\n  meaning_uncut: true\n  route_depth: 60\n  rerank_depth: 40\n  per_file_first10: 2\n  drop_nested: true\n' >> "$RUN/repo/governance/project/retrieval.yaml"
  git -C "$RUN/repo" -c user.name=measure -c user.email=measure@localhost commit -q -m "measure clone: S11's pool on" -- governance/project/retrieval.yaml
fi
HEAD12=$(git -C "$RUN/repo" rev-parse --short=12 HEAD); echo "clone at $HEAD12"
t0=$(date +%s)
flock /tmp/gov-os-d4b-rebuild.lock env -u GOV_TICKET PYTHONPATH="$RUN/repo/src" \
  bash "$O/tools/rebuild_slot.sh" "$RUN/repo" --seed > "$RUN/rebuild.out" 2>&1 || { echo "REBUILD FAILED"; tail -5 "$RUN/rebuild.out"; exit 1; }
echo "rebuild: $(( $(date +%s) - t0 )) s"
# DEC-1084 (ACT-GUARD-SETS-1): the sets-root form for the sets root's halves; no line names a hidden folder
python3 "$O/drafts/d4b/repin_gold.py" --sets-root "$EVAL" --set memory-retrieval --part hidden "$RUN/repo" --write | tail -1 || { echo "STOP: hidden anchors unresolved"; exit 1; }
python3 "$O/drafts/d4b/repin_gold.py" "$RUN/repo/fixtures/evaluation/memory-retrieval/visible" "$RUN/repo" | tail -1 || { echo "STOP: visible anchors unresolved"; exit 1; }
python3 "$O/drafts/d4b/repin_gold.py" --sets-root "$EVAL" --set memory-verdict --part hidden "$RUN/repo" --write | tail -1 || { echo "STOP: verdict anchors unresolved"; exit 1; }
echo "visible half: the sets root keeps integrate's; a branch that re-labels a visible question is measured on its own copy (VISIBLE_FROM_CLONE=1), restored after"
if [ "${VISIBLE_FROM_CLONE:-0}" = 1 ]; then cp -r "$EVAL/fixtures/evaluation/memory-retrieval/visible" "$RUN/visible-sets-root-backup"; cp -r "$RUN/repo/fixtures/evaluation/memory-retrieval/visible/." "$EVAL/fixtures/evaluation/memory-retrieval/visible/"; fi
export CLONE="$RUN/repo"
while [ $# -ge 2 ]; do
  NAME=$1 VARIANT=$2; shift 2
  bash "$O/drafts/d4b/measure_rx.sh" "$POINT-rx" 1 "$NAME" "$VARIANT"
  bash "$O/drafts/d4b/measure_verdict.sh" "$POINT-rx" 1 "$NAME-60" "$VARIANT"
  P=$HOME/gov-os-runs/D4B/$POINT-rx
  python3 "$O/drafts/d4b/score138.py" "$POINT/$NAME" "$P/$NAME/run1/measure.txt" "$P/$NAME-60/run1/measure.txt"
done
echo "== $(date '+%F %T') $POINT done"
