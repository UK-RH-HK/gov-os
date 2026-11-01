#!/bin/bash
# The scoped run in the close's form (DEC-952, DEC-968): the selected targets and pytest_options in one parallel run.
# serial.args is empty for this selection (no serial-only entry reached), so there is no serial phase.
cd /home/usain/gov-os-worktrees/W2-105 || exit 9
export TMPDIR=/tmp/gov-os-lead-W2-105
L=/home/usain/gov-os-worktrees/W2-105/.gov-runtime/scratch/lead/log
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > $L/scoped-disk.txt 2>&1 || exit 8
mapfile -t ARGS < $L/parallel.args
date -Is > $L/parallel.time
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-105/src:/home/usain/gov-os-worktrees/W2-105/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-105 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest "${ARGS[@]}" -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=$L/parallel.xml > $L/parallel.txt 2>&1
echo $? > $L/parallel.exit
date -Is >> $L/parallel.time
