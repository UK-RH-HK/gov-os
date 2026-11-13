#!/usr/bin/env bash
# Alone re-runs (once) of the reds not this ticket's at 461d03775: the W2-157 backstop file and the W2-149 case, in
# W2-124; the W2-149 case also on w2/integrate's head (ae806c3fe), a detached worktree removed after.
set -u
T=/home/usain/gov-os-worktrees/W2-124
L=$T/.gov-runtime/scratch/lead/log
OUT=$L/alone-2.txt
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
CASE=tests/unit/orchestration/test_w2_149_indep_launch.py::test_overrides_are_said_in_the_wall_and_the_counts
mkdir -p /tmp/w2-124-lead $T/.gov-runtime/scratch/empty-home
: > "$OUT"
cd "$T" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src \
  timeout 900 bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  tests/unit/resources/test_w2_157_backstop.py "$CASE" 2>&1 | tail -15 >> "$OUT"
echo "alone W2-124 exit ${PIPESTATUS[0]}" >> "$OUT"
B=/home/usain/gov-os-worktrees/W2-124-base-ae806c3fe
git -C "$T" worktree add --detach "$B" ae806c3fe >> "$OUT" 2>&1
cd "$B" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src \
  timeout 900 bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  "$CASE" 2>&1 | tail -15 >> "$OUT"
echo "base ae806c3fe exit ${PIPESTATUS[0]}" >> "$OUT"
cd "$T" && git -C "$T" worktree remove --force "$B" >> "$OUT" 2>&1
echo done > "$L/alone-2.exit"
