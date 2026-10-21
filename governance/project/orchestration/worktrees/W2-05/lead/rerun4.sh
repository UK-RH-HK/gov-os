#!/bin/bash
# Run 2: W1-46 alone again, without the caller's CLAUDE* variables (a live-session case, DEC-762).
cd /home/usain/gov-os-worktrees/W2-05 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/suites2
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src
for v in $(env | grep -oE '^CLAUDE[A-Z_]*=' | tr -d =); do unset "$v"; done
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -rs > "$LOG/rerun2-W1-46-noclaude.txt" 2>&1
echo $? > "$LOG/rerun2-W1-46-noclaude.exit"
