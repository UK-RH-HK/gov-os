#!/usr/bin/env bash
set -u
B=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/briefs
L=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/log
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
cd /home/usain/gov-os-worktrees/W2-94-fix && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-94-fix LAUNCH_TICKET=DAEO-g87r bash $T/launch_worker.sh --model claude-opus-5-5 --class C3 engineer high $B/en-5.md
echo "en-5 rc=$?"
