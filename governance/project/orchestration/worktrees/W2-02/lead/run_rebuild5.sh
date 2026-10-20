#!/bin/bash
# Lead's run-5 rebuild (DEC-719, DEC-732): waits for no close and a 1-minute load under 20, then one full rebuild.
cd /home/usain/gov-os-worktrees/W2-02 || exit 2
OUT=/home/usain/gov-os-worktrees/W2-02/.gov-runtime/scratch/lead/log/suites5
mkdir -p "$OUT"
until [ ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING ]; do sleep 60; done
until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done
PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -c "import gov; print(gov.__file__)" > "$OUT/import.txt" 2>&1
date +%s > "$OUT/rebuild.start"
uptime >> "$OUT/rebuild.start"
PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m gov.cli.main rebuild --json > "$OUT/rebuild.json" 2>&1
echo $? > "$OUT/rebuild.exit.tmp"
date +%s > "$OUT/rebuild.end"
mv "$OUT/rebuild.exit.tmp" "$OUT/rebuild.exit"
