#!/usr/bin/env bash
# Run 3: alone re-runs (once) of the reds at 7a3aecb38 (the W2-157 backstop file, the W2-23 space case) in W2-124, the
# W2-23 case and the backstop also on w2/integrate's head (95c957ae9), a detached worktree removed after; and the
# local_only W2-13 latency case (revised case 9) here, outside the sandbox.
set -u
T=/home/usain/gov-os-worktrees/W2-124
L=$T/.gov-runtime/scratch/lead/log
OUT=$L/alone-3.txt
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
SPACE=tests/acceptance/W2-23/test_w2_23_space.py::test_s6_every_kernel_hook_exits_alike_with_a_space_in_the_project_dir
BACK=tests/unit/resources/test_w2_157_backstop.py
LAT=tests/acceptance/W2-13/test_w2_13_latency.py::test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget
mkdir -p /tmp/w2-124-lead $T/.gov-runtime/scratch/empty-home
: > "$OUT"
cd "$T" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src \
  timeout 900 bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  "$BACK" "$SPACE" 2>&1 | tail -12 >> "$OUT"
echo "alone W2-124 exit ${PIPESTATUS[0]}" >> "$OUT"
cd "$T" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$T/src \
  timeout 1500 bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  "$LAT" 2>&1 | tail -12 >> "$OUT"
echo "latency W2-124 exit ${PIPESTATUS[0]}" >> "$OUT"
B=/home/usain/gov-os-worktrees/W2-124-base-95c957ae9
git -C "$T" worktree add --detach "$B" 95c957ae9 >> "$OUT" 2>&1
cd "$B" && env TMPDIR=/tmp/w2-124-lead PYTHONUSERBASE=/home/usain/.local HOME=$T/.gov-runtime/scratch/empty-home PYTHONPATH=$B/src \
  timeout 900 bash "$SLOT" python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rf \
  "$SPACE" 2>&1 | tail -12 >> "$OUT"
echo "base 95c957ae9 exit ${PIPESTATUS[0]}" >> "$OUT"
cd "$T" && git -C "$T" worktree remove --force "$B" >> "$OUT" 2>&1
echo done > "$L/alone-3.exit"
