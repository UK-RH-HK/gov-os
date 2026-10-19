
**Read this first: a headless lead's turn ends its background work.** After you start a worker or a test run in the background, wait for it in the foreground before you say anything: `until [ -s (its log or exit-code file) ]; do sleep 20; done` with the longest timeout allowed, repeated until it is there. Never end a message with "waiting". **Your return is one message, your last, and complete in itself**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

**If a worker's log or your own call shows an authentication or access error (401, 403, "Failed to authenticate", "access grant"): start nothing more, write your checkpoint, and return at once with the first line `AUTH_REQUIRED` and the state of the branch (DEC-420).**

**An engineer starts only on decided ground.** A package the implementation depends on stops the part it touches, not the rest. You decide no package.

## What you do, in order

1. The branch starts at the current `w1/integrate`; no merge is needed now. If you merge `w1/integrate` later: first compare the list of paths under `tests/acceptance` and `.tickets` that your branch changed since the merge base with the list that `w1/integrate` changed since it (`git diff --name-only`); a path on both lists means no merge until a test designer has brought the branch's file to `w1/integrate`'s version plus the branch's own lines (DEC-412). **A merge is always one committing command with `-m` and the trailers `Task:` and `Role: orchestrator`; never `git merge --no-commit` (DEC-436).** After it, `git diff --stat w1/integrate HEAD -- tests/acceptance` lists only this ticket's own files and its own lines in shared files; anything else is a defect of the merge: return it.
2. **Test design** (brief A1, fresh, through `gov launch independent-test-designer`, in proportion, DEC-221). No throwaway implementation left in the tree. Shared lists (W1-07's `w1_07_support.py`) are touched only on lines of its own; W1-24, W1-26 and W1-50 are adding lines there on other branches.
3. **Check red** yourself, to the end of the suite, behaviour assertions apart from the absent module.
4. **Engineer** (brief A2, fresh, through `gov launch engineer`). Proportion rule DEC-135. It runs its tests in the foreground and commits before it ends its turn. **Every worker's commit carries both a `Task:` and a `Role:` trailer; you check each one (`git log -1 --format='%(trailers:key=Role,valueonly)'`) before going on; a commit without it is amended by a worker of the same kind while it is still the unpushed tip.**
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, each to its end, never `-x`. A latency case that fails under load is run again alone and reported (DEC-372); so are W1-16's `test_this_repository_is_not_indexed_by_the_run` and W1-46's live sessions.
6. **Review:** as the top of this brief says for this ticket.
7. Return DONE or PACKAGES, one message, your last: head, commits with roles, each suite's count, findings and what was done, residuals for `bootstrap.md`, the interface as built, the three learning metrics (KPI disputes; acceptance tests rewritten after implementation began, with reasons; source lines against the estimate), temp folders left.

