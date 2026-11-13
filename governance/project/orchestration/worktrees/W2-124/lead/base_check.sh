#!/usr/bin/env bash
# Base-red check: the three reds unrelated to W2-124 on w2/integrate's head; then W2-124's two S1 timing cases alone.
set -u
T=/home/usain/gov-os-worktrees/W2-124
B=$T/.gov-runtime/scratch/base
L=$T/.gov-runtime/scratch/lead/log
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
mkdir -p /tmp/w2-124-lead $T/.gov-runtime/scratch/empty-home
[ -d "$B" ] || git -C "$T" worktree add --detach "$B" w2/integrate
git -C "$B" log --oneline -1 > "$L/base-check.txt"
cd "$B" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src \
  bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/adapters/test_w2_153_compose.py::test_the_twelve_sources_are_the_composition" \
  "tests/unit/adapters/test_w2_153_portability.py::test_this_repositorys_sources_are_the_composition" \
  "tests/unit/resources/test_w2_157_backstop.py" >> "$L/base-check.txt" 2>&1
echo "base exit $?" >> "$L/base-check.txt"
cd "$T" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src \
  bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/acceptance/W2-124/test_w2_124_s1_semantic_fails_named.py" -k "hung or part-way-500" > "$L/alone-1.txt" 2>&1
echo "alone exit $?" >> "$L/alone-1.txt"
cd "$T" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src \
  bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
  "tests/unit/resources/test_w2_157_backstop.py" >> "$L/alone-1.txt" 2>&1
echo "backstop alone exit $?" >> "$L/alone-1.txt"
echo done > "$L/base-check.exit"
