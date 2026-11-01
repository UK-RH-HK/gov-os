# Brief: independent test designer, DAEO-wq2b (W2-97), run 2 (a revision batch under DEC-985)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-wq2b` (`W2-97`, "the local merge queue"). You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-97-tests` on branch `w2/W2-97-tests` (DEC-963); you never read or write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-97`. Expect `GOV_ROLE=independent-test-designer` and `GOV_TICKET=DAEO-wq2b`.

The ticket's acceptance suite `tests/acceptance/W2-97/` exists (18 cases, written by an earlier test designer from the specification below; its README maps each KPI line to its cases). An engineer built the tool from the same specification; 17 cases pass and one is disputed. Two things have been decided since, and the ticket's KPI lines changed. Your job is a small revision, nothing more.

**Your worktree holds the engineer's implementation** (it was made from the ticket branch's head). Never read it (DEC-820 (c)): nothing under `governance/project/orchestration/tools/` or `tests/unit/orchestration/`, by any tool, and no `git diff`, `git show` or `git log -p` that prints them. You may run your tests against it and read their results.

## Your retrieval (DEC-963)

- Use the integration branch's store only, never the ticket worktree's: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. For what changed on `w2/integrate` since that store's last refresh, read it with `git show w2/integrate:<path>`. (In run 1 `gov retrieve` inside the sandbox hung 2 to 5 minutes trying to reach ollama.com, which the sandbox denies; if it does not answer within about 3 minutes, stop it, say so in your return, and read the named sources directly.)
- **P-R1:** drop unread any `gov retrieve` result under the ticket's implementation paths (`governance/project/orchestration/tools/`, `tests/unit/orchestration/`), and name in your return any such result you were served.

## What you read

- The ticket file `.tickets/DAEO-wq2b.md` (read-only), as it stands in your worktree: its KPI lines, as DEC-983 changed them (KPI 1: the run takes a heavy-job slot, not a test lock; KPI 3: the full suite never runs here, only in the nightly).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-985, DEC-983 (item 4), DEC-979 (D1), DEC-968, DEC-959 (item 1), DEC-491 (rewrites after implementation), DEC-866 (supersession).
- The suite `tests/acceptance/W2-97/` (yours to revise) and the specification below.

## The three changes (and nothing else)

1. **P-W2-97-ENQ-1 (b), DEC-985 item 1:** in `test_w2_97_entry.py::test_only_an_approved_ticket_enters`, its helper runs `enqueue` with a 12-hex commit id from its temp folder and no repository, and expects the full id in `requested/`. Add `--repo <the planted repository>` to that `enqueue` call (one line). Lower no other expectation: the case still expects the full id, a request alone never entering, and the approval being the entry. Commit it alone, with `Rewrite-Reason: P-W2-97-ENQ-1`.
2. **DEC-983 (DEC-866):** read every case against the KPI lines as they now stand. If a case asserts the old rule (that the run holds a shared test lock, or that a change to the core gets the full suite), revise only that assertion to the new rule, lowering nothing else, and commit it with `Rewrite-Reason: DEC-983`. The lead's own reading found none (the lock case is the queue's own one-writer lock, which stays); if you agree, change nothing for this item and say so.
3. **One case added for KPI 3's new text** (the full suite never runs here): a selection stand-in that answers scope `full` (with targets) is never run: `run` exits 4, the test stand-in did not run, the integration branch and `main` did not move, the entry is still approved, and nothing is ejected or landed. Fit it into the suite's existing support (its stand-in selection already has a refusing mode; give it a way to answer `full`), and map it in the README under S3 and the failure line "A second run …" only if it shows that line; at least under S3. Update the README's KPI lines to their DEC-983 wording. Commit it, with `Rewrite-Reason: DEC-983` (a case added after the implementation began).

KPI 1's heavy-job slot is not observable through the stand-ins (a `--test-cmd` stand-in replaces the whole run, slot included): add no case for it, and say in the README that no acceptance case covers it and why.

## Red and green, as you can see them

Run your suite to its end from your worktree: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA`. Do not set `TMPDIR` to `/tmp/gov-os-lead-W2-97` (your sandbox cannot write it; use your session's own temp folder, and if pytest writes a `pytest-of-*` folder into the worktree, say so and leave it). Expect: the revised case passes on the tool as it stands (it already takes `--repo`); the new case fails because the tool as it stands runs a `full` selection (give the failure message you saw); the other 17 pass. Report each case's name and result. Then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-97-tests/src python3 -m pytest tests/acceptance/W2-97 --collect-only -q -p no:cacheprovider` (no import clash).

- **Your share of the scratch budget:** 2 GB and 100,000 files and folders.

## Commits

Commit only `tests/acceptance/W2-97/`, in your worktree, one commit per change above, for example:

    git commit -m "W2-97 acceptance: enqueue's case passes --repo (P-W2-97-ENQ-1, DEC-985)" --trailer "Task: DAEO-wq2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-985, DEC-983, DEC-959, DEC-968" --trailer "Rewrite-Reason: P-W2-97-ENQ-1" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

In your return, also give: your commits (12 digits) with their trailers, the case count, each case's result as you saw it, the new case's failure message, the lines changed per commit, and every point of the specification you found unclear.

