#!/bin/bash
# read-only: files changed on a ticket branch and on integrate since their merge base, and the overlap
cd /home/usain/Dynamic-Agentic-Engineering-OS
T=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/batch-prep/hand/tmp
for b in "$@"; do
  mb=$(git merge-base w2/$b w2/integrate)
  echo "== $b merge-base ${mb:0:12}"
  git diff --name-only $mb w2/$b | sort > $T/a-$b.txt
  git diff --name-only $mb w2/integrate | sort > $T/b-$b.txt
  echo "branch files: $(wc -l < $T/a-$b.txt)"
  echo "overlap:"
  comm -12 $T/a-$b.txt $T/b-$b.txt
done
