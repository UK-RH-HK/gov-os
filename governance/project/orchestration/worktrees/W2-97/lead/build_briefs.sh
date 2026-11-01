#!/bin/bash
# Assembles the two worker briefs from their parts (lead's own script).
cd /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/briefs || exit 9
cat part-td.md part-rules.md part-spec.md part-return.md | sed 's#<this worktree>#/home/usain/gov-os-worktrees/W2-97-tests#g' > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/briefs/td-1.md
cat part-eng.md part-rules.md part-spec.md part-return.md | sed 's#<this worktree>#/home/usain/gov-os-worktrees/W2-97#g' > /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/briefs/eng-1.md
grep -c . td-1.md eng-1.md
grep -n "<this worktree>" td-1.md eng-1.md
exit 0
