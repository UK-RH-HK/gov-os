#!/usr/bin/env bash
# A clean run (the auditor's F1): the named skills' scenarios with every skill's scenario-summaries.md moved out of
# its folder for the run, so no session sees earlier replies; the files are put back unchanged afterwards.
# Usage: run_clean.sh <tag> <skill>...
set -u
tag=$1; shift
cd /home/usain/gov-os-worktrees/W2-100 || exit 2
ASIDE=/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/summaries-aside-$tag
mkdir -p "$ASIDE"
for s in backend api data security; do
  mv template/governance/kernel/skills/$s/scenario-summaries.md "$ASIDE/$s.md" || exit 3
done
for s in "$@"; do ls template/governance/kernel/skills/$s; done > "$ASIDE/folders-during-run.txt"
bash /home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/run_skilleval2.sh "$tag" "$@"
rc=$?
for s in backend api data security; do
  mv "$ASIDE/$s.md" template/governance/kernel/skills/$s/scenario-summaries.md || exit 4
done
git status --short
exit $rc
