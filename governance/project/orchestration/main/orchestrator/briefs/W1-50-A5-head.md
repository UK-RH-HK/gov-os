You are the ticket lead for ticket `DAEO-xnbx` (`W1-50`, "Containment attribution by commit trailers"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-50` on branch `w1/W1-50`.

**This run is the test design batch only (owner decision DEC-256).** You run steps 1 and 2 of the loop and then return. You start no engineer and no reviewer: the implementation waits until another ticket that touches the same guard files is merged.

## State of this ticket

- New today, by owner decisions DEC-253 to DEC-256; read them, with DEC-182 (trailers), DEC-171, DEC-235, DEC-254, the Contract's CAP-58 with its covers item CAP-58.h, and the section "Parallel run: containment records that are not defects" at the end of `governance/project/bootstrap.md`.
- What happened: the main orchestrator merged a ticket branch into `w1/integrate` (merge commit `00e3d539`, trailer `Role: orchestrator`; the merged side holds a test-designer commit under `tests/acceptance/W1-37/` and an engineer commit). Two things followed.
  - `tests/acceptance/W1-01/test_w1_01_history.py::test_only_the_test_designer_commits_to_acceptance_tests` fails on this branch now: it lists the merge commit among the commits touching `tests/acceptance`, and the merge commit does not carry `Role: independent-test-designer`. Run it first and see it fail.
  - The containment check (`src/gov/guard/containment.py`, W1-03) flagged the merge as "HEAD moved (not a forward move on the same branch)". In worktrees it also attributed a test designer's commit to the call of the lead that was waiting for it.

## The test design batch (brief A1, one fresh designer, profile FULL, DEC-221)

It has two parts, in two commits if that is cleaner, both with `Task: DAEO-xnbx` and `Role: independent-test-designer`:

1. **The W1-01 revision (DEC-253).** Revise `test_only_the_test_designer_commits_to_acceptance_tests` (and its support code under `tests/acceptance/W1-01/` if needed) so that an integration merge commit passes when every change it brings under `tests/acceptance/` comes from commits on the merged side carrying `Role: independent-test-designer`. Every non-merge commit is still checked exactly as now. A merge that brings an acceptance-test change from a commit without that role, or that itself changes a file under `tests/acceptance/` beyond what its parents hold (an "evil merge"), still fails. The designer shows both directions with small temporary repositories if the suite has a way to do so, and shows the real history of this branch passing. It is reported as a rewrite after implementation, reason "owner decision: integration merges".
   - After the revision the whole W1-01 suite must be green on this branch.
2. **The W1-50 suite**, under `tests/acceptance/W1-50/`: the four success lines and three failure lines of the ticket, through the public interface the W1-03 suite uses (the PostToolUse hook as the harness calls it, in a temporary repository). Cases the KPIs name: a forward move of several commits each judged by its own `Role` and `Task` trailers; an integration merge by the orchestrator whose commits all pass, with no finding for the merge commit itself; a merge that brings a commit outside its own trailers' allowed paths, with a finding; a worker's commit made during another actor's call, judged by its own trailers; a commit with no `Role` or `Task` trailer, judged against the caller as today. If the KPIs leave a case open (for example a trailer naming an unknown role or ticket, a ticket that is closed, a commit with several `Role` trailers, a non-forward move such as a reset), that is a decision package with a recommendation, not a guess; fail-closed readings are preferred.
   - If an earlier suite (W1-03, W1-45, W1-47) has a test that asserts today's behaviour and this ticket's KPIs make it wrong, the designer reports it and leaves it unchanged in this batch unless the KPI names the change; say which, so that the main orchestrator can decide.
   - Red first: the W1-50 suite fails for the reason its README states; the W1-01 revision is green.

## Then

- Check yourself: W1-01 green on this branch; the W1-50 suite red for the stated reason; W1-02, W1-03, W1-45 and W1-47 unchanged and green (run them). You need not run the other suites in this run.
- Return `DONE` for the test batch (say "test design batch only"), with the commits, the counts, the W1-01 result, the red reason, the rewrite count with its reason, and any packages in full. If there are packages, still return the committed batch: the main orchestrator merges it for the W1-01 revision.

