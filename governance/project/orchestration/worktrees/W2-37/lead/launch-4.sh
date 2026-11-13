#!/usr/bin/env bash
# Appends gov context to the td-4 and eng-4 briefs, checks them, and launches both (C2: Sonnet high).
set -u
B=/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/briefs
cat "$B/ctx-td-4.md" >> "$B/td-4.md"
cat "$B/ctx-eng-4.md" >> "$B/eng-4.md"
for f in td-4 eng-4; do
  grep -nE '\{[A-Z_]+\}' "$B/$f.md" && echo "SLOT in $f" || echo "$f: no slots, $(wc -c < "$B/$f.md") bytes"
done
L=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/launch_worker.sh
cd /home/usain/gov-os-worktrees/W2-37-tests && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-37-tests LAUNCH_TICKET=DAEO-6n5k bash "$L" --model claude-sonnet-5-5 --class C2 independent-test-designer high "$B/td-4.md"
cd /home/usain/gov-os-worktrees/W2-37 && LAUNCH_TREE=/home/usain/gov-os-worktrees/W2-37 LAUNCH_TICKET=DAEO-6n5k bash "$L" --model claude-sonnet-5-5 --class C2 engineer high "$B/eng-4.md"
