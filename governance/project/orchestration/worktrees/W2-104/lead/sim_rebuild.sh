#!/usr/bin/env bash
# Simulation only (throwaway clone outside the repository, never pushed): would a history with the resolved files
# committed on the ticket side before the merge, and a merge that takes "ours" on every conflict, pass W1-01's rule?
set -u
SIM=/tmp/gov-os-lead-W2-104/sim-r3b
rm -rf "$SIM"; mkdir -p /tmp/gov-os-lead-W2-104
git clone -q --shared --no-checkout /home/usain/gov-os-worktrees/W2-104 "$SIM" || exit 2
cd "$SIM" || exit 2
G="git -c user.name=sim -c user.email=sim@example.invalid -c commit.gpgsign=false -c core.hooksPath=/dev/null"
$G checkout -q -b sim 713fcf744 || exit 2
FILES="src/gov/check/commands.py tests/unit/skilleval/test_w2_104_skilleval.py tests/acceptance/W1-07/README.md tests/acceptance/W1-07/test_w1_07_recorded_commands.py tests/acceptance/W1-07/w1_07_support.py tests/acceptance/W1-32/test_w1_32_command_set.py tests/acceptance/W2-104/w2_104_support.py"
for f in $FILES; do git show 23a30c332f80:"$f" > "$f"; done
$G commit -q -am "sim: resolved contents on the ticket side" || exit 2
$G merge -q --no-ff --no-commit 8801ffd17df9 > /dev/null 2>&1
echo "conflicted: $(git diff --name-only --diff-filter=U | tr '\n' ' ')"
for f in $(git diff --name-only --diff-filter=U); do git checkout --ours -- "$f" && git add -- "$f"; done
$G commit -q -m "sim merge" || exit 2
echo "tree equals 23a30c332f80: $( [ "$(git rev-parse HEAD^{tree})" = "$(git rev-parse 23a30c332f80^{tree})" ] && echo yes || echo NO)"
git diff --stat 23a30c332f80 HEAD | tail -1
cd "$SIM/tests/acceptance/W1-01" 2>/dev/null || { $G checkout -q -- . ; cd "$SIM/tests/acceptance/W1-01"; }
python3 -c "
import sys; sys.path.insert(0, '.')
import w1_01_support as s
from pathlib import Path
root = Path('$SIM')
sha = s.git('rev-parse', 'HEAD', root=root).strip()
print('merge_offences of the sim merge:', s.merge_offences(sha, 'tests/acceptance', root))
"
