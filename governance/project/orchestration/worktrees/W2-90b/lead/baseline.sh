#!/usr/bin/env bash
# Baseline: the ticket's listed test files on the starting head, in the close's parallel form.
cd /home/usain/gov-os-worktrees/W2-90b || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-90b
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-90b/src:/home/usain/gov-os-worktrees/W2-90b/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-90b
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest \
  tests/acceptance/W1-05/test_w1_05_live_hooks.py \
  tests/acceptance/W1-46/test_w1_46_research_installs.py \
  tests/acceptance/W1-46/test_w1_46_live_sessions.py \
  tests/acceptance/W2-59/test_w2_59_hook_lines.py \
  tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py \
  tests/acceptance/W2-65/test_w2_65_hook_lines.py \
  tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py \
  tests/acceptance/W1-47 \
  tests/acceptance/W1-50/test_w1_50_freeze_launcher.py \
  tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py \
  -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
  --junitxml=/home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/baseline.xml \
  > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/baseline.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-90b/.gov-runtime/scratch/lead/log/baseline.exit
