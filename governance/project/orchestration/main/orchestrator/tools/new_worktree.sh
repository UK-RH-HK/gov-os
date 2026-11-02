#!/usr/bin/env bash
# A lead's worktree, seeded (owner, DEC-1032 (iv)): the CTO creates every lead's worktree with this from now on.
#   bash new_worktree.sh <W2 id> [<start>]        (start: default w2/integrate)
# `git worktree add ~/gov-os-worktrees/<W2> -b w2/<W2> <start>` (w2-orchestrator.md's form), then seed_store.py warm
# from the integration store (~/gov-os-worktrees/W2-00-store): its whole store at the same commit, else its vectors,
# so the lead's first rebuild re-embeds only what changed; where the tree's own `gov rebuild` offers --seed (W2-122),
# the seeded rebuild runs here instead. A seed refused is named and the worktree stands (its first rebuild is then
# cold, as before). Exit: 2 bad id or the folder exists, git's code when the worktree cannot be added, else 0.
# NEW_WORKTREE_REPO, NEW_WORKTREE_ROOT, NEW_WORKTREE_BASE: tests only.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=${NEW_WORKTREE_REPO:-/home/usain/Dynamic-Agentic-Engineering-OS}
ROOT=${NEW_WORKTREE_ROOT:-/home/usain/gov-os-worktrees}
[ $# -ge 1 ] || { echo "usage: new_worktree.sh <W2 id> [<start>]" >&2; exit 2; }
id=$1
start=${2:-w2/integrate}
case "$id" in ""|*/*|.*|*" "*) echo "new_worktree: not a ticket id: '$id'" >&2; exit 2 ;; esac
tree=$ROOT/$id
[ -e "$tree" ] && { echo "new_worktree: $tree exists; nothing done" >&2; exit 2; }
git -C "$REPO" worktree add -q "$tree" -b "w2/$id" "$start" || exit $?
echo "worktree $tree on w2/$id at $(git -C "$tree" rev-parse --short=12 HEAD)"
python3 "$HERE/seed_store.py" warm "$tree" ${NEW_WORKTREE_BASE:+--base "$NEW_WORKTREE_BASE"} --who "lead $id"
rc=$?
[ "$rc" -eq 0 ] || echo "new_worktree: the seed step ended $rc; the worktree stands and its first rebuild runs as before"
exit 0
