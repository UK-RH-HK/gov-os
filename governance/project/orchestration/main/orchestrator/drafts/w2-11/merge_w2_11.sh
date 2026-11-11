#!/usr/bin/env bash
# The CTO's merge of w2/integrate into w2/W2-11, after the product-spec pre-merge commits (drafts/w2-11/ROUTE.md, step 3).
# Not run by the helper that wrote it (dry-run only, in a scratch clone).  Run it outside any sandbox, in one command:
#   bash merge_w2_11.sh <message file> [<worktree>]
# The message file ends with the trailers `Task: DAEO-k7hz` and `Role: orchestrator`.
# It merges in one `git merge`.  If git leaves exactly the two generated copies unmerged, it takes integrate's whole
# file for each (the copies are regenerated from the resolved sources afterwards, ROUTE.md step 6) and commits with the
# same message.  Any other unmerged path: it aborts the merge and says which.  It never leaves a merge open.
set -u
MSG=$(realpath "${1:?message file}")
T=${2:-/home/usain/gov-os-worktrees/W2-11}
EXPECT=$'.claude/skills/orchestration/SKILL.md\n.claude/skills/test-design/SKILL.md'
[ -f "$MSG" ] || { echo "no message file $MSG"; exit 2; }
tail -n 4 "$MSG" | grep -q '^Task: DAEO-k7hz$' || { echo "the message must carry Task: DAEO-k7hz"; exit 2; }
tail -n 4 "$MSG" | grep -q '^Role: orchestrator$' || { echo "the message must carry Role: orchestrator"; exit 2; }
[ -z "$(git -C "$T" status --short)" ] || { echo "the tree is not clean"; exit 2; }
git -C "$T" rev-parse -q --verify MERGE_HEAD > /dev/null && { echo "a merge is already open"; exit 2; }
# the read first: the conflict list must be exactly the two copies (or empty)
mt=$(git -C "$T" merge-tree --write-tree --name-only HEAD w2/integrate 2>&1); rc=$?
if [ $rc -gt 1 ]; then echo "merge-tree failed (exit $rc), nothing merged: $mt" | head -3; exit 3; fi
got=$(printf '%s\n' "$mt" | sed -n 's/^CONFLICT (.*): Merge conflict in //p' | sort)
if [ -n "$got" ] && [ "$got" != "$EXPECT" ]; then echo "unexpected conflicts, nothing merged:"; echo "$got"; exit 3; fi
before=$(git -C "$T" rev-parse HEAD)
git -C "$T" merge --no-ff w2/integrate -F "$MSG" > /dev/null 2>&1
if git -C "$T" rev-parse -q --verify MERGE_HEAD > /dev/null; then
  unm=$(git -C "$T" diff --name-only --diff-filter=U | sort)
  if [ "$unm" != "$EXPECT" ]; then git -C "$T" merge --abort; echo "unexpected unmerged paths, merge aborted:"; echo "$unm"; exit 4; fi
  for f in $unm; do
    git -C "$T" checkout --theirs -- "$f" && git -C "$T" add -- "$f" || { git -C "$T" merge --abort; echo "could not take $f"; exit 5; }
  done
  git -C "$T" commit -q -F "$MSG" || { git -C "$T" merge --abort; echo "commit failed, merge aborted"; exit 6; }
fi
after=$(git -C "$T" rev-parse HEAD)
[ "$before" != "$after" ] || { echo "nothing was merged (HEAD unchanged)"; exit 7; }
git -C "$T" log --oneline -1
git -C "$T" log -1 --format='parents: %p'
git -C "$T" status --short | head -5
