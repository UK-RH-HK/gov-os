#!/usr/bin/env bash
set -u
B=/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/briefs
cat $B/td-1.head.md $B/interface.md $B/td-1.tail.md > $B/td-1.md
cat $B/en-1.head.md $B/interface.md $B/en-1.tail.md > $B/en-1.md
grep -n '{[A-Z_]*}' $B/td-1.md $B/en-1.md && { echo "unfilled slot"; exit 1; }
wc -l $B/td-1.md $B/en-1.md
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools
cd /home/usain/gov-os-worktrees/W2-94-fix-tests && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-94-fix-tests LAUNCH_TICKET=DAEO-g87r bash $T/launch_worker.sh --model claude-sonnet-5-5 --class C2 independent-test-designer high $B/td-1.md
echo "td rc=$?"
cd /home/usain/gov-os-worktrees/W2-94-fix && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-94-fix LAUNCH_TICKET=DAEO-g87r bash $T/launch_worker.sh --model claude-sonnet-5-5 --class C2 engineer high $B/en-1.md
echo "en rc=$?"
