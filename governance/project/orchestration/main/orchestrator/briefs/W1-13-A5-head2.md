You are the ticket lead for ticket `DAEO-w616` (`W1-13`, "gov readiness"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-13` on branch `w1/W1-13`. Its implementer is an engineer (brief A2). FULL: after green, a reviewer (brief A3).

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on.

## State of this ticket

- An earlier lead brought the branch to `9eca416f`: 92 acceptance cases in `tests/acceptance/W1-13/`, red (3 failed, 89 errors: `gov readiness` answers `NOT_IMPLEMENTED`), with the planned W1-07 revision for `readiness`. Nothing is implemented. The worktree was recreated from the branch since, so it holds no lead checkpoint and no scratch files: read the suite's README and `git log`.
- **All four packages are decided as option (a)**, which is what the tests encode: DEC-348 (DP-1), DEC-349 (DP-2, `gov.readiness.close`), DEC-350 (DP-3, the specification record is the frontmatter of the change's `proposal.md`), DEC-351 (DP-4, arguments, report, exit code 3). They are in `docs/DECISION_REGISTER.md` on `w1/integrate`; read them after step 1. No test designer runs before the engineer.
- **DEC-317**: `gov readiness` is built by the file `src/gov/readiness/command.py` alone. The convention a command module follows is the docstring at the top of `src/gov/cli/main.py`: read it word for word and give it to the engineer. `src/gov/cli/**` is outside this ticket's paths. `src/gov/checkpoint/command.py` is a working example, with an exit code 3 of its own.
- The mandatory ten rows of DEC-085 are not in W1-12's schema: the implementation holds them itself or reads `docs/contract/readiness-dimensions.yaml`; the engineer says which and why.
- A W1-46 builder test, `tests/unit/launch/test_command_modules.py`, uses not-yet-built commands as stand-ins. If building `readiness` breaks one of its cases, say so in your return; do not edit it.
- DEC-322: tests and the engineer build their own stores and repositories in temporary directories; `gov.readiness.close` is never run against this repository's own tickets.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-w616` and `Role: orchestrator`. Resolve nothing by hand; a conflict is a package. The containment flag on the merge is a record (DEC-254).
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh). Estimate 170 lines plus about 40 for `close` (DEC-349). Proportion rule DEC-135.
4. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator, with the prefix `PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH` (the W1-12 suite runs `openspec`). Red by design, to report apart: W1-50 (26 failed, 17 passed). The two 100 ms latency cases (`test_a_call_waits_under_100_ms_p95_for_the_hook` in W1-05 and `test_decision_p95_is_under_100_ms` in W1-02) are sensitive to machine load: if one fails, re-run its file alone before you treat it as red.
5. **Reviewer** (brief A3). Besides its own probes: a required row closed by a defaulted or whitespace-only N/A reason; a row whose state differs only in letter case; a specification with no readiness record at all; a `gap_ticket` id that names no ticket or a closed one; a second `close` of the same specification, and a `close` interrupted between the ticket and the status; a record whose `status` is `CLOSED` with a required row open; any path by which the report differs between two runs (ordering, timestamps); any path by which the read command writes a file. A finding that lets a specification with a required open row pass or close is fixed (a test batch first, then a fresh engineer); the rest are residuals.
6. Workers leave nothing behind in this worktree outside what they commit; a designer or reviewer that needs a throwaway copy uses its session scratchpad. Say what, if anything, is left.
7. Return DONE with the summary, the reviewer's findings, the residuals for `bootstrap.md` and the learning metrics (earlier: 4 ambiguity packages, 1 planned revision, 0 rewrites and 0 tests added after implementation).

