You are the ticket lead for ticket `DAEO-be7u` (`W1-11`, "Decision checker and owner-approval facts"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-11` on branch `w1/W1-11`. Its implementer is an engineer (brief A2). FULL: after green, a reviewer (brief A3). You resume from the lead checkpoint an earlier lead wrote in this worktree (`.gov-runtime/scratch/lead/CHECKPOINT.md`); where this brief and that checkpoint differ, this brief holds (workers now start with `gov launch`, sandboxed).

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

**An engineer starts only on decided ground.** If the test designer returns a new package the implementation depends on, you return PACKAGES and no engineer runs.

## State of this ticket

- Branch head `e7981fb9`: 55 acceptance cases, all red (`No module named 'gov.decisions'`); nothing implemented. The earlier lead returned DP-1 to DP-4.
- **All four are decided.** Read them in `docs/DECISION_REGISTER.md` after step 1:
  - **DEC-329** (DP-1, option (a)): the checker reads frontmatter and git, never prose.
  - **DEC-330** (DP-4, option (a)): the checker fails a ticket that waits on a declined, revoked or stale package.
  - **DEC-331** (DP-3, option (a)): a record cites its gate in `approval` and names its change in `cit`; read its fail-closed points, which need cases (about four).
  - **DEC-360** (owner, DP-2, option (a)): the owner's approval fact is the `Role: owner` trailer on the commit that sets the decision `ACTIVE`. A later owner commit approves nothing earlier. A signature as the stricter form is a residual. The safeguard against an agent writing that trailer is in W1-50 (a `Role: owner` commit made during an agent session's call is a finding), not in this ticket.
- The four DP-2 cases on the branch follow option (a) as recommended; the designer confirms them against DEC-360's wording (the trailer is read from the final trailer block; before 2026-10-03 the message body, DEC-182; the commit is the one that sets `ACTIVE`, not a later one).
- Read "W1-08 residuals", "W1-09 residuals", "W1-10 residuals" and "W1-34 residuals" in `governance/project/bootstrap.md`. The fixtures HZ-B-03, HZ-B-04 and HZ-B-06 are in the b-dev tier: `GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`; tests clone the tier into a temporary directory and are marked `local_only`. Never list `~/gov-os-workbench/` itself; read nothing under `~/gov-os-workbench/w1-tests/` or `~/gov-os-workbench/s0b2/`.
- DEC-322: tests build their own store in temporary directories; nobody writes this repository's live `.gov-runtime/store.db`.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-be7u` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES. A containment flag on the merge is a record (DEC-254).
2. **Test design batch 2** (brief A1, a fresh designer, profile FULL, DEC-221; before implementation): the DEC-331 fail-closed cases, the check of the DP-2 cases against DEC-360, and any case DEC-329 or DEC-330 makes wrong.
3. **Check red** yourself.
4. **Engineer** (brief A2, fresh). Estimate 310 lines. Proportion rule DEC-135. The checker only reads: "files stay byte-identical" is a KPI.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator. Red by design, to report apart: W1-50.
6. **Reviewer** (brief A3). Besides its own probes: a decision hazard the fixtures don't plant (a cycle of length one, a superseded record in another directory, ids that differ only in case); an approval fact forged by a non-owner commit, by a `Role: owner` line in the message body of a commit made after 2026-10-03, or by an owner commit that touches the file without setting `ACTIVE`; a gate whose `status` is in another case or missing; any path by which the checker writes a file.
7. Return DONE with the summary, the reviewer's findings, the residuals and the learning metrics for the whole ticket (so far: 4 packages and one gap worker), as your last message.

