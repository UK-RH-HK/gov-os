#!/usr/bin/env bash
# run 4: the five W2-115 acceptance reds at this head, short tracebacks, for the fresh engineer (failing output only)
export HOME=/home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local
export TMPDIR=/tmp/gov-os-lead-W2-115-reds5
mkdir -p "$TMPDIR"
T=/home/usain/gov-os-worktrees/W2-115
cd "$T" || exit 2
echo "head $(git -C $T rev-parse --short=12 HEAD)"
PYTHONPATH=$T/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=short \
  "tests/acceptance/W2-115/test_w2_115_batch.py::test_a_culprit_whose_red_is_its_own_new_test_goes_back_and_the_rest_land" \
  "tests/acceptance/W2-115/test_w2_115_batch.py::test_nothing_landed_before_the_culprit_with_its_own_new_test_was_found" \
  "tests/acceptance/W2-115/test_w2_115_reds.py::test_a_red_the_head_without_the_change_does_not_have_refuses_the_close" \
  "tests/acceptance/W2-115/test_w2_115_reds.py::test_a_red_an_untrailered_commit_after_the_green_base_caused_is_never_excused" \
  "tests/acceptance/W2-115/test_w2_115_reds.py::test_a_red_a_trailered_commit_after_a_green_untrailered_one_caused_is_refused" 2>&1
echo "exit ${PIPESTATUS[0]}"
