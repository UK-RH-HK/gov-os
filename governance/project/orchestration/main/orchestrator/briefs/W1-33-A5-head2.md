You are the ticket lead for ticket `DAEO-xog0` (`W1-33`, "Wave 1 role definitions"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-33` on branch `w1/W1-33`. This is a short closing round: no new test design and no implementer are expected.

**Read this first: a headless lead's turn ends its background work.** If you start anything in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more.

## State of this ticket

- An earlier lead brought the branch to `7ddf9986`: the kernel role files and the roster are done, and every suite was green except 26 W1-33 cases on `.claude/agents/`. It returned P-1 (the owner copies the five generated files) and P-2 to P-4.
- **P-1 is done by the owner**: commit `0f8b0d2969019e3d03503eef666b0fd685f37f95` on this branch (`Task: DAEO-xog0`, `Implements: CAP-22.a, CAP-58.b`, `Role: owner`) places the five generated definitions under `.claude/agents/`; `research.md` is unchanged. If containment flags that HEAD move at your first call here, it is a record of an owner action (DEC-254), not a finding to act on.
- **P-2 to P-4 are decided: DEC-352** in `docs/DECISION_REGISTER.md` (read it after step 1).
- Never Read, print or diff `.claude/settings.json`; never read `governance/project/held-out.yaml`.

## What you do, in order

1. `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-xog0` and `Role: orchestrator`. Resolve nothing by hand; if it conflicts, abort and return PACKAGES saying so. A containment flag on the merge is a record (DEC-254).
2. **Re-check**: run W1-33's suite and W1-05's and W1-46's role tests. The 26 cases on `.claude/agents/` should now be green. If a case is red because the generated files and the kernel role files disagree, do not edit `.claude/agents/` (no headless session can): return PACKAGES with the exact difference. If a W1-05 or W1-46 case pins the minimal definitions this ticket replaced, that is a planned revision by a fresh test designer (brief A1), not an edit by you.
3. **Full verify**: every suite under `tests/acceptance/`, `tests/unit` and the validator. Red by design, to report apart: W1-50 (its implementation is not merged) and W1-28 and W1-11 if their suites are on `w1/integrate` (they are not expected to be).
4. Return DONE with the commits, each suite's result, the whole ticket's residuals for `bootstrap.md` (the earlier lead's list plus anything new; say whether the roster or the `systems` snapshot of W1-08 changed), and the learning metrics for the whole ticket as far as you can tell them from the branch and the suite's README (KPI disputes, rewrites after implementation with reasons, tests added after implementation, lines added against the estimate of 300, false findings).

