#!/bin/bash
# Run 2, part 1: the close's parallel phase over tests/, under the machine's verification lock.
cd /home/usain/gov-os-worktrees/W2-51 || exit 99
O=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
until [ ! -e $O/CLOSE-RUNNING ] && [ ! -e $O/NIGHTLY-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash $O/tools/disk_gate.sh > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel-gate.txt 2>&1
date >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel-gate.txt
cat /proc/loadavg >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel-gate.txt
TMPDIR=/tmp/gov-os-lead-W2-51 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-51/src:/home/usain/gov-os-worktrees/W2-51/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-51 flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml=/home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel.xml > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel.log 2>&1
echo $? > /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel.exit
date >> /home/usain/gov-os-worktrees/W2-51/.gov-runtime/scratch/lead/verify2/parallel-gate.txt
