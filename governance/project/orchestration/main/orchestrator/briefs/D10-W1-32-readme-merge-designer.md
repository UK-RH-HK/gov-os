# D-10's red-fix list: settle one README conflict between two D-10 branches (W2-20, DAEO-r30l)

You are a fresh **independent test designer**, launched under W2-20's ticket (`.tickets/DAEO-r30l.md`).

## What happened
- Two D-10 branches each appended one paragraph at the end of `tests/acceptance/W1-32/README.md`:
  - `w2/W2-116-d10-tests` (already merged into `w2/integrate`, `9a1b21cf1`): the failed-removal cases' paragraph;
  - `w2/W2-20-d10c-tests` (this worktree's branch, review READY): the command-set paragraph.
- Merging this branch into `w2/integrate` conflicts on that file alone. The CTO's helper may not write under
  `tests/acceptance/` (MR-3).
- The sandbox cannot run a real `git merge` here, because it would write `.claude/` and `.tickets/`. So, as a
  designer did for W2-145 tonight, you settle it in git objects only.

## The task
1. Run `git merge-tree --write-tree w2/integrate HEAD` (it writes git objects only, no files) and confirm the only
   conflict is `tests/acceptance/W1-32/README.md`. If any other file conflicts, stop and return PACKAGES.
2. Build the settled README:
   - integrate's version, with this branch's command-set paragraph appended after the failed-removal paragraph;
   - each paragraph exactly as its branch wrote it;
   - nothing else changed.
   Write it as a blob with `git hash-object -w <file in your TMPDIR>`.
3. Build the full settled tree: take merge-tree's tree, replace the README entry with your blob (a temporary index
   under your TMPDIR, `GIT_INDEX_FILE`, `git update-index --cacheinfo`, `git write-tree`). Check that it differs from
   `w2/integrate` only in this branch's own files.
4. Return the blob id and the tree id. Do not commit or move any ref; the CTO's helper commits the merge from your
   tree.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-d10c-tests` (branch `w2/W2-20-d10c-tests`).
- You write only git objects and files in your TMPDIR.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. Never run `git worktree prune`, never commit, merge,
  push or move a ref.
- Estimate: 5 minutes. Return the twelve fields, short: the blob, the tree, the files the tree differs in.
