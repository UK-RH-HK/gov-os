#!/bin/bash
# The scoped run in the close's form: the parallel phase, then the serial phase.
TREE=/home/usain/gov-os-worktrees/W2-152
LOG=/home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log
TOOLS=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
cd "$TREE" || exit 90
export TMPDIR=/tmp/gov-os-lead-W2-152
export PYTHONUSERBASE=/home/usain/.local
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=$TREE/src:$TREE/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=$TREE
mapfile -t OPTS < /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/pytest_options.txt

bash "$TOOLS/heavy_slot.sh" python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only \
  -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/parallel.xml \
  "${OPTS[@]}" > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/parallel.log 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/parallel.exit

PYTHONPATH=$TREE/src python3 /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/serial_entries.py > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial_entries.txt
mapfile -t SER < /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial_entries.txt
if [ "${#SER[@]}" -gt 0 ]; then
  export GOV_CLOSE_SERIAL_ONLY_GIVEN="$(cat /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial_entries.txt)"
  bash "$TOOLS/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider -p gov_close_serial_only \
    -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial.xml \
    "${OPTS[@]}" "${SER[@]}" > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial.log 2>&1
  echo $? > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial.exit
else
  echo none > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/serial.exit
fi
echo done > /home/usain/gov-os-worktrees/W2-152/.gov-runtime/scratch/lead/log/scoped.done
