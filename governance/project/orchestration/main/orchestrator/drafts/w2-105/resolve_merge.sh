#!/usr/bin/env bash
# Makes the merge commit of w2/integrate into w2/W2-105 with the one conflict (template/.rulesync/permissions.jsonc)
# resolved, by plumbing: no conflicted state in any tree, nothing checked out until the last line.
# Not run by the helper. Usage: bash resolve_merge.sh            (dry: prints the new commit, moves nothing)
#                              bash resolve_merge.sh --apply     (also fast-forwards w2/W2-105 in its worktree)
set -eu
MAIN=/home/usain/Dynamic-Agentic-Engineering-OS
WT=/home/usain/gov-os-worktrees/W2-105
D=$MAIN/.gov-runtime/scratch/orchestrator/drafts/w2-105
SRC=template/.rulesync/permissions.jsonc
cd "$MAIN"
[ -z "$(git -C "$WT" status --porcelain)" ] || { echo "worktree not clean"; exit 3; }
[ "$(git -C "$WT" rev-parse --abbrev-ref HEAD)" = "w2/W2-105" ] || { echo "worktree not on w2/W2-105"; exit 3; }
[ "$(git rev-parse w2/W2-105)" = "$(git -C "$WT" rev-parse HEAD)" ] || { echo "branch and worktree differ"; exit 3; }
out=$(git merge-tree --write-tree --name-only w2/W2-105 w2/integrate || true)
tree=$(printf '%s\n' "$out" | sed -n 1p)
conflicts=$(printf '%s\n' "$out" | sed -n '2,/^$/p' | grep -v '^$' || true)
if [ "$conflicts" != "$SRC" ]; then
  echo "unexpected conflict list (integrate moved?): $conflicts"; exit 4
fi
export GIT_INDEX_FILE="$D/tmp/idx-resolve"
rm -f "$GIT_INDEX_FILE"
git read-tree "$tree"
blob=$(git hash-object -w "$D/tmp/resolved.jsonc")
git update-index --cacheinfo "100644,$blob,$SRC"
newtree=$(git write-tree)
unset GIT_INDEX_FILE
rm -f "$D/tmp/idx-resolve"
commit=$(git commit-tree "$newtree" -p w2/W2-105 -p w2/integrate -F "$D/merge-msg.txt")
echo "resolved blob: $(printf %.12s "$blob")  merge commit: $(printf %.12s "$commit")"
git diff --stat "w2/integrate" "$commit" | tail -9
if [ "${1:-}" = "--apply" ]; then
  git -C "$WT" merge --ff-only "$commit"
fi
