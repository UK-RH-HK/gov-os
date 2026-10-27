You are the ticket lead for ticket `DAEO-cy5o` (`W2-57`, "Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`.

**This is run 2, the second half of the ticket's one round (DEC-916: its last review is this run's).** `git rev-parse --short=12 HEAD` must show `d0bfeb6afd95`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read first:
- your own checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, and your run 1 package draft;
- after the merge below, the ticket file (`.tickets/DAEO-cy5o.md`, amended by DEC-925) and its card;
- DEC-925 and DEC-924 item 3.

**First,** merge `w2/integrate` into `w2/W2-57` (`git merge --no-ff w2/integrate`, with `Task: DAEO-cy5o` and `Role: orchestrator` in the final trailer block). It brings DEC-925, the amended ticket file, the registry fix (W1-06) and today's head.

## The owner's answers to your packages (DEC-925 item 3)

- **B1 (a):** your paths now include `src/gov/close/command.py`, **for the serial phase's call to `serial.py` only.**
  - W2-07's round 2 runs beside you in the same file and keeps gate (h)'s line (the work-without-a-task gate's subtraction before `_check_unmeasured`). Never touch it, nor any other part of `command.py`.
  - Whichever of you and W2-07's round 2 merges second merges `w2/integrate` back, re-verifies, and gets a fresh probe if its review went stale (DEC-895).
- **B2 (b):** KPI 6's guard deadline is left to the resource gate and the quiet window. No new serial entries.
- **Delegated, as you proposed:**
  - **B3 (a):** W1-19's `test_w1_19_real_models.py` is named for your test designer (W2-M332: time the queries in a pass without the memory sampler; take the memory peaks in a second pass).
  - **R1:** the doctor-budget fix rides along, so an unread Claude Code version is never a pass (reviewer F1).
  - **R2:** W1-30's `test_w1_30_r15_policy_pairs.py` is named for your test designer: its rulesync case must not accept a timeout as its red after the fault (reviewer F2).
  - **A1 (a):** the doctor exception case stays strict.

## This run's order

1. The merge of `w2/integrate`.
2. **Test designer** (fresh, sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`): B3, R2, and a case for R1. Each with a `Rewrite-Reason:`, no expectation lowered. Then **check red yourself.**
3. **Engineer** (fresh, sandboxed, `--effort high`):
   - B1, the route: the close's serial phase takes only the entries not routed to the nightly, so `test_w2_57_nightly_route.py`'s case goes green;
   - R1, the doctor budget.
4. **Rebuild and verify in full,** in the close's form, under the lock, with the retention option and the disk gate first.
   - **Known:** DEC-919's W2-66 lead-verification red. W1-19's warm-query case is on `load_sensitive`.
   - **Base reds, unless W2-74 has merged into `w2/integrate` by then** (if so, merge again before the run): W1-01's `docs/source` cases ×4, W1-47's `docs/source` cases ×2, W1-49's `[not on PATH]`. W1-06's is fixed on your base now.
   - Any other red is named with its cause.
5. **Review 2** (fresh FULL reviewer, brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head. Commit the probe record only when it passes. It is the last review of this round (DEC-916).
6. **Return** DONE (probe passed), or PACKAGES. Include:
   - the `load_sensitive` removals, now with W1-46's 23 and W1-19's warm p95 if the route lets them leave the close;
   - the W1-09 condition, ready for the orchestrator.

**Trailers:** your own commits carry `Implements: DEC-925` (a decision id, not a role). Two of run 1's lead commits carry `Implements: engineer`, from the orchestrator's brief: leave them; they are history.

**Estimate:** about 40 to 80 lines, about 5 to 6 hours with the full run and the review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
