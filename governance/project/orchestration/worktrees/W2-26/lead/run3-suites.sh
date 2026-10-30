#!/bin/bash
# W2-26 run 3: the collection (DEC-868), then tests/unit and tests/acceptance/W2-07/ in the close's parallel form.
cd /home/usain/gov-os-worktrees/W2-26 || exit 90
gate() {
  until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ] && [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ] && awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
}
gate
date > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-collect.start
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-collect.start
TMPDIR=/tmp/gov-os-lead-W2-26 PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-collect.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-collect.exit
gate
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-disk.txt 2>&1
date > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-suites.start
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-suites.start
TMPDIR=/tmp/gov-os-lead-W2-26 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-26/src:/home/usain/gov-os-worktrees/W2-26/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-26 flock /tmp/gov-os-verify.lock python3 -m pytest tests/unit tests/acceptance/W2-07 -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-parallel.xml > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-suites.txt 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-suites.exit
date >> /home/usain/gov-os-worktrees/W2-26/.gov-runtime/scratch/lead/log/run3-suites.start
