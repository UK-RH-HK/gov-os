#!/usr/bin/env bash
# The lead's rebuild of this worktree's stores, by this worktree's code, under the machine's rebuild lock (DEC-939
# item 2), bounded by timeout 3600 inside the flock. Arg 1: a tag for the log names.
TAG=${1:-r}
LOG=/home/usain/gov-os-worktrees/W2-76/.gov-runtime/scratch/lead/log
mkdir -p /tmp/gov-os-lead-W2-76
cd /home/usain/gov-os-worktrees/W2-76 || exit 2
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING ]; do sleep 60; done
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh || exit 3
start=$(date +%s)
echo "start $(date '+%F %T')" > "$LOG/rebuild-$TAG.summary"
TMPDIR=/tmp/gov-os-lead-W2-76 PYTHONPATH=/home/usain/gov-os-worktrees/W2-76/src flock /tmp/gov-os-rebuild.lock timeout 3600 python3 -m gov.cli.main rebuild --json > "$LOG/rebuild-$TAG.json" 2> "$LOG/rebuild-$TAG.err"
code=$?
echo "end $(date '+%F %T') exit $code after $(( $(date +%s) - start )) s" >> "$LOG/rebuild-$TAG.summary"
echo "$code" > "$LOG/rebuild-$TAG.exit"
