#!/usr/bin/env bash
# The real F4 case in a clone of the head, checked out as w2/W2-157 (clean; then with a change outside its paths),
# as w2/W2-121c and detached. Output to log/clone-check.txt.
set -u
TREE=/home/usain/gov-os-worktrees/W2-181
HEAD=$(git -C "$TREE" rev-parse HEAD)
INTEG=$(git -C "$TREE" rev-parse w2/integrate)
WORK=/tmp/w2-181-clone-check
rm -rf "$WORK"; mkdir -p "$WORK/home" "$WORK/tmp"
git clone -q --no-checkout "$TREE" "$WORK/repo"
R="$WORK/repo"
git -C "$R" branch -f w2/integrate "$INTEG"
CASE=tests/acceptance/W2-157/test_w2_157_nothing_else.py
run() {
  echo "=== $1 (HEAD: $(git -C "$R" symbolic-ref -q HEAD || echo detached) $(git -C "$R" rev-parse --short=12 HEAD))"
  (cd "$R" && env HOME="$WORK/home" TMPDIR="$WORK/tmp" PYTHONUSERBASE=/home/usain/.local PYTHONDONTWRITEBYTECODE=1 \
     PYTHONPATH="$R/src" bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
     python3 -m pytest "$CASE" -q -rs -p no:cacheprovider -o tmp_path_retention_policy=failed -k "test_f4" 2>&1 | tail -6)
}
git -C "$R" checkout -q -b w2/W2-157 "$HEAD"
run "w2/W2-157, clean (expect the real F4 passed)"
echo x > "$R/src/gov/resources/slots_planted.py"
git -C "$R" -c user.name=p -c user.email=p@example.invalid -c core.hooksPath=/dev/null add src/gov/resources/slots_planted.py
git -C "$R" -c user.name=p -c user.email=p@example.invalid -c core.hooksPath=/dev/null commit -q -m planted
run "w2/W2-157 with src/gov/resources/slots_planted.py (expect the real F4 failed, naming it)"
git -C "$R" checkout -q -b w2/W2-121c
run "w2/W2-121c with the same change (expect skipped, naming w2/W2-121c)"
git -C "$R" checkout -q --detach w2/integrate
git -C "$R" -c user.name=p -c user.email=p@example.invalid -c core.hooksPath=/dev/null merge -q --no-ff -m candidate w2/W2-121c
run "detached candidate merge of w2/W2-121c (expect skipped, detached HEAD)"
rm -rf "$WORK"
