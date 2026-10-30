#!/bin/bash
# The lead's full verification, parallel phase, in the close's form (DEC-889, DEC-905, DEC-939 item 2).
# Usage: verify-parallel.sh <tag>
cd /home/usain/gov-os-worktrees/W2-84 || exit 2
TAG="$1"
ORCH=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator
LOG=/home/usain/gov-os-worktrees/W2-84/.gov-runtime/scratch/lead/log
while [ -e "$ORCH/CLOSE-RUNNING" ] || [ -e "$ORCH/NIGHTLY-RUNNING" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash "$ORCH/tools/disk_gate.sh" > "$LOG/parallel-$TAG.out" 2>&1 || { echo 97 > "$LOG/parallel-$TAG.rc"; exit 97; }
mkdir -p /tmp/gov-os-lead-W2-84
{ date; cat /proc/loadavg; du -sh /tmp/gov-os-lead-W2-84; du -s --inodes /tmp/gov-os-lead-W2-84; } >> "$LOG/parallel-$TAG.out" 2>&1
TMPDIR=/tmp/gov-os-lead-W2-84 PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-84/src:/home/usain/gov-os-worktrees/W2-84/src/gov/close/pytest_plugin GOV_CLOSE_SERIAL_ONLY_OF=/home/usain/gov-os-worktrees/W2-84 flock /tmp/gov-os-verify.lock python3 -m pytest tests -n auto -q -p no:cacheprovider -p gov_close_serial_only -o tmp_path_retention_policy=failed -rs --junitxml="$LOG/parallel-$TAG.xml" >> "$LOG/parallel-$TAG.out" 2>&1
RC=$?
{ date; du -sh /tmp/gov-os-lead-W2-84; du -s --inodes /tmp/gov-os-lead-W2-84; } >> "$LOG/parallel-$TAG.out" 2>&1
echo $RC > "$LOG/parallel-$TAG.rc"
