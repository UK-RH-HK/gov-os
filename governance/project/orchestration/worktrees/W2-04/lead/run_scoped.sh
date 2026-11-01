#!/usr/bin/env bash
# W2-04 round 2: the scoped verification in the close's form (DEC-952, DEC-968): the parallel run, then the
# selected serial-only cases alone. Literal paths; exit codes to files.
set -u
cd /home/usain/gov-os-worktrees/W2-04 || exit 2
L=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log
mapfile -t OPTS < <(grep -v '^$' "$L/select-2.opts")
mapfile -t SERIAL < <(grep -v '^$' "$L/serial-2.list")
export TMPDIR=/tmp/gov-os-lead-W2-04
export PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH
export PYTHONPATH=/home/usain/gov-os-worktrees/W2-04/src:/home/usain/gov-os-worktrees/W2-04/src/gov/close/pytest_plugin
export GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-04
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
  python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
  --junitxml=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/parallel-2.xml "${OPTS[@]}" \
  > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/parallel-2.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/parallel-2.rc
GOV_CLOSE_SERIAL_ONLY_GIVEN=$(printf '%s\n' "${SERIAL[@]}") \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh \
  python3 -m pytest "${SERIAL[@]}" -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
  --junitxml=/home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/serial-2.xml "${OPTS[@]}" \
  > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/serial-2.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-04/.gov-runtime/scratch/lead/log/serial-2.rc
