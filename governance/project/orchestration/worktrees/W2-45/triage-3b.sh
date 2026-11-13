#!/usr/bin/env bash
# Verify 3b triage: the four reds alone at head (0653dc010), and W1-40 + W2-149 + W2-157 on w2/integrate's head (base-red rule).
cd /home/usain/gov-os-worktrees/W2-45
mkdir -p /tmp/gov-os-lead-W2-45/triage3b
export TMPDIR=/tmp/gov-os-lead-W2-45/triage3b
export PYTHONUSERBASE=/home/usain/.local
export HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home
SLOT=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh
CASES="tests/unit/close/test_run_and_record.py::test_the_environment_of_the_run_is_the_callers_with_the_projects_src_alone_on_the_path
tests/unit/orchestration/test_w2_149_indep_launch.py::test_f3_the_test_hook_is_recorded
tests/unit/resources/test_w2_157_backstop.py::test_s4_only_the_named_group_is_stopped_and_a_same_name_process_runs_on
tests/acceptance/W1-40/test_w1_40_ci_unmeasured.py::test_the_job_names_the_openspec_check_unmeasured_and_fails_where_openspec_is_not_on_the_runner"
echo "=== HEAD $(git rev-parse --short=12 HEAD)"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src bash $SLOT python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -p no:xdist $CASES 2>&1 | tail -40
BASE=/tmp/gov-os-lead-W2-45/triage3b/base
rm -rf $BASE; mkdir -p $BASE
git archive w2/integrate | tar -x -C $BASE
echo "=== BASE w2/integrate $(git rev-parse --short=12 w2/integrate)"
cd $BASE
PYTHONPATH=$BASE/src bash $SLOT python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -p no:xdist $CASES 2>&1 | tail -40
