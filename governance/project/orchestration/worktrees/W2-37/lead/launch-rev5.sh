#!/usr/bin/env bash
# Appends JUDGEMENT.md word for word to rev-5, checks it, and launches the narrow check (independent-auditor, Opus high, C2).
set -u
B=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/briefs
J=/home/usain/gov-os-worktrees/W2-37/governance/project/briefs/JUDGEMENT.md
cat "$J" >> "$B/rev-5.md"
grep -nE '\{[A-Z_]+\}' "$B/rev-5.md" && { echo "SLOT in rev-5"; exit 1; }
grep -c 'Can an honest agent hit this in ordinary work' "$B/rev-5.md"
echo "rev-5: no slots, $(wc -c < "$B/rev-5.md") bytes"
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh
cd /home/usain/gov-os-worktrees/W2-37 && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-37 LAUNCH_TICKET=DAEO-6n5k bash "$L" --model claude-opus-5-5 --class C2 independent-auditor high "$B/rev-5.md" 2>&1 | tail -5
