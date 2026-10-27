#!/usr/bin/env bash
# Lead verification, run 4, part A: the full rebuild, the collection in one process (DEC-868), gov check.
# Exit codes in log/v4-*.exit; log/v4a.done at the end.
cd /home/usain/gov-os-worktrees/W2-07 || exit 90
L=/home/usain/gov-os-worktrees/W2-07/.gov-runtime/scratch/lead/log
GATE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/disk_gate.sh
CLOSE=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING
SRC=/home/usain/gov-os-worktrees/W2-07/src
export TMPDIR=/tmp/gov-os-lead-W2-07
mkdir -p "$TMPDIR"
rm -f "$L/v4a.done"
trap 'echo done > "$L/v4a.done"' EXIT
until [ ! -e "$CLOSE" ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
PYTHONPATH=$SRC python3 -c "import gov; print(gov.__file__)" > "$L/v4-gov-file.txt"
git log --oneline -1 > "$L/v4-head.txt"
{ date -Is; cat /proc/loadavg; bash "$GATE"; du -s --inodes "$TMPDIR"; du -sh "$TMPDIR"; } > "$L/v4-rebuild.gate" 2>&1 \
  || { echo 91 > "$L/v4-rebuild.exit"; exit 91; }
PYTHONPATH=$SRC python3 -m gov.cli.main rebuild --json > "$L/v4-rebuild.json" 2>&1; echo $? > "$L/v4-rebuild.exit"
PYTHONPATH=$SRC python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header > "$L/v4-collect.txt" 2>&1; echo $? > "$L/v4-collect.exit"
PYTHONPATH=$SRC python3 -m gov.cli.main check --json > "$L/v4-check.json" 2>&1; echo $? > "$L/v4-check.exit"
