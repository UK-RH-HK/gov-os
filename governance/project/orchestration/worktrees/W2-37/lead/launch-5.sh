#!/usr/bin/env bash
# Appends gov context to ps-5 (version 1.1.0), checks it, and launches it as engineer (C2: Sonnet high).
set -u
B=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/briefs
cat "$B/ctx-eng-5.md" >> "$B/ps-5.md"
grep -nE '\{[A-Z_]+\}' "$B/ps-5.md" && { echo "SLOT in ps-5"; exit 1; }
echo "ps-5: no slots, $(wc -c < "$B/ps-5.md") bytes"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh
cd /home/usain/gov-os-worktrees/W2-37 && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-37 LAUNCH_TICKET=DAEO-6n5k bash "$L" --model claude-sonnet-5-5 --class C2 engineer high "$B/ps-5.md" 2>&1 | tail -5
