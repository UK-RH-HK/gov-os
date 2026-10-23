You are the ticket lead for ticket `DAEO-r9ss` (`W2-07`, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`.

**This is run 1.** `git log --oneline -1` must show `c2d539c6`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

The owner passed the review point on 2026-10-23 (DEC-899, in your register). This ticket came forward to sit with W2-66, before the first re-pin, and rides in it (DEC-896 item 3). Its ticket file and card are confirmed. Read the ticket file (`.tickets/DAEO-r9ss.md`) and the card (`docs/plan/WAVE_2_WBS.md` §2, W2-07) first. Then read lens I's synthesis (`docs/assessment/2026-10/I-SYNTHESIS.md`): §4's W2-07 block and P-IS-4.

## The owner's decisions for this run

- **DEC-899 item 2, the merge order.** W2-66 (`DAEO-c1uz`) is built in parallel with this ticket, in its own worktree. Both edit `src/gov/close/command.py`: this ticket the gates, W2-66 the record's evidence lines and the calls into its new modules (`select.py`, `nightly.py`, `evidence.py`).
  - **This ticket merges first.** Keep your edits to `command.py` in their own functions, so W2-66's merge-back is easy.
  - Never write W2-66's or W2-68's new modules.
- **DEC-896 items 1 and 3, the three KPIs added:**
  - a decision-record commit that changes only governance records and names an ACCEPTED decision counts as measured for the work-without-a-task gate;
  - a test-revision ticket is judged on its declared `acceptance_tests.path`;
  - a stale probe is named before the close spends its run (W2-M403).
  W2-58's refused close of 2026-10-22 (WORK_WITHOUT_TASK, `log/repair-tickets/DAEO-aneq.md` in the orchestrator's scratch) and W2-50's (PROBE_INVALID) are the cases these come from.
- **P-IS-4 (a):** the commit gates run first and stop before any test, spending no ratchet attempt. They are the trailers, task-less work, accepted history, the probe gate, and the ratchet's own reading of both lists' entries.
- **DEC-898:** before its regression, `gov close` reads the shared disk's free space and inodes (100 GiB and 10,000,000 from the configuration, until W2-20's reading lands) and refuses below either floor, naming the reading.
- **MR-3 (core-mutation):** your `allowed_paths` hold no `tests/acceptance/` path. W1-30's two files, named at the end of your ticket file, are your test designer's to revise (each with a `Rewrite-Reason:`). The unit `test_a_collection_error_is_a_finding` is your engineer's.
- **DEC-898, the scratch budget:** as in the common brief below. Report the scratch size in every return.

## This run's order

1. **Tests first:** a fresh independent test designer, launched sandboxed, `--effort high`, on every KPI line, STANDARD proportion (every KPI line's success and failure, plus the key edge cases), and the named W1-30 revisions.
2. **Check red yourself.**
3. **Implement:** a fresh engineer, launched sandboxed, `--effort high`, inside the allowed paths only.
4. **Verify** in the close's form (one parallel run, then the serial cases, with JUnit XML), with `gov check` after a rebuild.
5. **Return** DONE, or PACKAGES. The orchestrator merges this ticket before W2-66.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit); split larger work into rounds.

---
