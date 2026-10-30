# W2-77 design note: the nightly's clean-up removes only its own clone

Ticket `DAEO-b6hm` (W2-77), row W2-M406, DEC-939 item 5, DEC-915 item 4. A plan in behaviour, not code.

## Today

`python3 -m gov.close.nightly <branch> --root <project>` adds a detached worktree of the branch's head (the
"clone", a folder named `tree` inside a fresh temporary folder), runs the night there, and at its end removes
the clone with `git worktree remove --force <clone>`, deletes its temporary folder, and then runs a repo-wide
`git worktree prune`. That prune drops the registration and the administrative folder (with its index) of every
worktree of the repository whose folder the process cannot see at that moment (moved, unmounted, unreadable).
W2-68's batch (`python3 -m gov.close.batch run`) reaches the same code (W2-68's probe, F1).

## After this ticket

1. **Only the clone, by its exact path.** The clone the nightly adds is removed by that exact path,
   `git worktree remove --force <that path>`, and by nothing else.
2. **No repo-wide prune.** No `git worktree prune` runs anywhere in the nightly or in anything it calls, and
   nothing in the nightly prunes or removes worktree entries by pattern, by age or by a missing folder.
3. **Its own entry, known from the clone itself.** The clone's administrative entry is known from the clone's
   own `.git` file (`gitdir: <common dir>/worktrees/<name>`), read when the clone has been added, never guessed
   from the folder's name: every clone is a folder called `tree`, and git may give a later one another entry
   name (`tree1`, ...) while some other worktree holds `tree`.
4. **If the removal fails** (git's exit is not 0, or the entry is still there afterwards, so its result cannot
   be confirmed): only that clone's own administrative entry goes, the exact folder read in 3, and only when that
   entry is confirmed to be the clone's (it lies directly under the common directory's `worktrees/`, and its own
   `gitdir` file names the clone's `.git`). No other entry is touched in any case. If the entry cannot be read,
   cannot be confirmed as the clone's, or is still there after its removal, nothing more is removed.
5. **A failure is never hidden.** Whenever the removal by path did not succeed (whether or not 4 then removed
   the entry), the night's record carries a `cleanup` key: `{"ok": false, "clone": <the clone's path>,
   "entry": <the entry's path, or null when unknown>, "entry_removed": true|false, "error": <git's message or the
   reason>}`, and one line naming the clone and the failure goes to standard error. A night that ends in an
   exception (no record written) still writes that line, and the exception is kept unchanged.
6. **Nothing else changes:** the selection, the runs, the bisect, the record (no `cleanup` key when the removal
   succeeded, every other key as today), the verdict, the exit code and the envelope. A failed clean-up does not
   change the verdict. The batch's record, built from the night's, carries the same `cleanup` key when present.
7. **Unchanged on purpose, outside the clean-up:** the `git worktree add --detach --force <fresh path> <head>`
   (its path is new in a fresh temporary folder), the bisect's `start`/`run`/`reset` inside the clone (bisect
   state is per worktree), and how the nightly's git calls build their environment (W2-05's ground).

## Where

`src/gov/close/nightly.py`, the clean-up of `night` only; builder tests in new files
`tests/unit/close/test_nightly_cleanup*`. About 20 lines.
