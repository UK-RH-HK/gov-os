#!/bin/bash
# Read-only simulation: a synthetic commit (objects only, no ref) = w2/W2-11 with the resolved W1-35 support file;
# then git's own merge of it with w2/integrate: is the file still a conflict?
set -u
R=/home/usain/gov-os-worktrees/W2-11
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/w2-11
REL=tests/acceptance/W1-35/w1_35_orchestration_support.py
export GIT_INDEX_FILE=$D/tmp/sim-index
rm -f "$GIT_INDEX_FILE"
git -C $R read-tree w2/W2-11
blob=$(git -C $R hash-object -w "$D/W1-35-orchestration-support.PRE-MERGE.py")
git -C $R update-index --cacheinfo 100644,$blob,$REL
tree=$(git -C $R write-tree)
commit=$(git -C $R commit-tree "$tree" -p w2/W2-11 -m simulation)
unset GIT_INDEX_FILE
echo "synthetic commit ${commit:0:12}"
git -C $R merge-tree --write-tree --name-only "$commit" w2/integrate > "$D/tmp/mt2.txt" 2>&1
echo "merge-tree rc=$?"
grep -c 'CONFLICT' "$D/tmp/mt2.txt"
grep -n 'w1_35_orchestration_support' "$D/tmp/mt2.txt"
t2=$(head -1 "$D/tmp/mt2.txt")
git -C $R show "$t2:$REL" | diff -q - "$D/W1-35-orchestration-support.PRE-MERGE.py" && echo "merged file == pre-merge file (unexpected)"
rm -f "$D/tmp/sim-index"
