#!/bin/bash
# Run 3's scoped verification (decision 4): tests/acceptance/W2-71 and tests/unit/secrets_check in the close's form.
cd /home/usain/gov-os-worktrees/W2-71 || exit 9
LOG=/home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
cat /proc/loadavg > /home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log/scoped3.load
date > /home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log/scoped3.start
TMPDIR=/tmp/gov-os-lead-W2-71 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH \
PYTHONPATH=/home/usain/gov-os-worktrees/W2-71/src:/home/usain/gov-os-worktrees/W2-71/src/gov/close/pytest_plugin \
GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-71 \
flock /tmp/gov-os-verify.lock python3 -m pytest tests/acceptance/W2-71 tests/unit/secrets_check -n auto -q \
  -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs \
  --junitxml=/home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log/scoped3.xml \
  > /home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log/scoped3.out 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log/scoped3.exit
date > /home/usain/gov-os-worktrees/W2-71/.gov-runtime/scratch/lead/log/scoped3.end
