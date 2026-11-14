#!/usr/bin/env bash
# Run 6 (the auditor's F1): the twelve scenarios at 1.0.1 with scenario-summaries.md moved out of the four skill
# folders for the run, so no session sees earlier replies; the files are put back unchanged afterwards.
set -u
cd /home/usain/gov-os-worktrees/W2-100 || exit 2
ASIDE=/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/summaries-aside
mkdir -p "$ASIDE"
for s in backend api data security; do
  mv template/governance/kernel/skills/$s/scenario-summaries.md "$ASIDE/$s.md" || exit 3
done
ls template/governance/kernel/skills/backend template/governance/kernel/skills/api template/governance/kernel/skills/data template/governance/kernel/skills/security > "$ASIDE/folders-during-run.txt"
bash /home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/run_skilleval2.sh 6 backend api data security
rc=$?
for s in backend api data security; do
  mv "$ASIDE/$s.md" template/governance/kernel/skills/$s/scenario-summaries.md || exit 4
done
git status --short
exit $rc
