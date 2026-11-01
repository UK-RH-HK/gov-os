#!/bin/bash
# Assembles run 2's worker briefs from their parts (lead's own script).
cd /home/usain/gov-os-worktrees/W2-97/.gov-runtime/scratch/lead/briefs || exit 9
sed 's#Implements: DEC-959, DEC-979, DEC-953, DEC-968#Implements: DEC-985, DEC-983, DEC-959, DEC-968#' part-rules.md > part-rules-2.md
cat part-td-2.md part-rules-2.md part-spec.md part-spec-2.md part-return.md | sed 's#<this worktree>#/home/usain/gov-os-worktrees/W2-97-tests#g' > td-2.md
cat part-eng-3.md part-spec-2.md > eng-3.md
grep -c . td-2.md eng-3.md
grep -n "<this worktree>" td-2.md eng-3.md
grep -c "DEC-985, DEC-983" part-rules-2.md
exit 0
