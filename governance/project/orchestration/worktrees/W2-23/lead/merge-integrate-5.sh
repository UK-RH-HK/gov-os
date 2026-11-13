#!/bin/bash
# Merge w2/integrate back into w2/W2-23 before run 5; resolve the one import-line conflict in stages.py; commit at once.
set -u
cd /home/usain/gov-os-worktrees/W2-23 || exit 2
git merge --no-ff --no-commit w2/integrate >/dev/null 2>&1
st=$?
conflicts=$(git diff --name-only --diff-filter=U)
if [ "$conflicts" != "src/gov/adopt/stages.py" ]; then
  echo "unexpected conflict set: [$conflicts] (merge exit $st); aborting"; git merge --abort; exit 3
fi
python3 - <<'EOF'
from pathlib import Path
p = Path("src/gov/adopt/stages.py")
t = p.read_text()
old = "<<<<<<< HEAD\nfrom gov.adopt import project, safety\n=======\nfrom gov.adopt import lite_gates, project\n>>>>>>> w2/integrate\n"
assert t.count(old) == 1, "conflict hunk not as expected"
t = t.replace(old, "from gov.adopt import lite_gates, project, safety\n")
assert "<<<<<<<" not in t and ">>>>>>>" not in t
p.write_text(t)
EOF
[ $? -eq 0 ] || { git merge --abort; exit 4; }
git add src/gov/adopt/stages.py
PYTHONPATH=src python3 -c "import gov.adopt.stages as s; assert 'A7' in s.STAGE and 'A10' in s.STAGE; print('import ok')" || { git merge --abort; exit 5; }
git commit -q -F /home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/lead/merge-integrate-5.msg || { git merge --abort; exit 6; }
git log --oneline -1 | cat
git status --short | head
