#!/bin/bash
# The lead's scoped verification, parallel phase, in the close's form (DEC-889, DEC-952, DEC-905).
cd /home/usain/gov-os-worktrees/W2-112 || exit 99
OPTS=$(cat /tmp/gov-os-lead-W2-112/pytest_options.txt)
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src:/home/usain/gov-os-worktrees/W2-112/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-112
export TMPDIR=/tmp/gov-os-lead-W2-112
# shellcheck disable=SC2086
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/log/parallel.xml $OPTS
