#!/bin/bash
# The scoped parallel run in the close's form (DEC-952, DEC-968), the selection's pytest options added.
cd /home/usain/gov-os-worktrees/W2-55 || exit 99
mapfile -t OPTS < /home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/log/select-opts.txt
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src:/home/usain/gov-os-worktrees/W2-55/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-55
export TMPDIR=/tmp/gov-os-lead-W2-55
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
  python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs \
  --junitxml=/home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/log/parallel.xml "${OPTS[@]}"
