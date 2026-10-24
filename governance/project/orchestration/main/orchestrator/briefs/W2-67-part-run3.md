You are the ticket lead for ticket `DAEO-9nys` (`W2-67`, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, a test-revision ticket whose role is engineer (DEC-907), working only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`.

**This is run 3: rounds 2 and 3 together (DEC-914).** `git log --oneline -1` must show `09c327d2`. `git status --short` must show only `?? tests/acceptance/W1-27/w2_67_td4_plant.py`, round 1's inert plant: your first test designer removes it. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first. Round 1 merged into `w2/integrate` at `4da40b60`, and your old temp folder is removed.

## Why you start now

- **Your ticket's round 2** waited for W2-07 and W2-66: both are merged (`2a9d1a11`, `c60c9704`).
- **Your round 3** waited for W2-69: merged (`2d5a829a`).
- No ticket in flight holds these folders. W2-65, in flight, holds the hooks and one W1-27 doctor case (`test_w1_27_doctor.py`), which you do not touch.

## The decisions (DEC-914, delegated; on `w2/integrate`)

- **Round 2:**
  - W1-30's 13 first-round cases, each shown red against a planted fault, then green on the head, with a `Rewrite-Reason`, as your ticket's KPI line says.
  - **Row W2-L420:** `tests/acceptance/W1-30/test_w1_30_context_failures.py::test_a_decision_checker_that_cannot_run_refuses_the_close`, and the module docstrings of `test_w1_30_governance_checks.py` and `test_w1_30_context_failures.py`, follow DEC-868 and DEC-908 (DEC-866).
  - The 15 nested-run unit close functions (`tests/unit/close/**`), bounded. W2-07's and W2-66's code is now in the close.
- **Round 3:** W2-50's large-store and hang cases (`tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`), on W2-69's merged code. W2-69 revised these files' scale cases for its own check: build on its revision.
- **Round 1's ride-alongs (DEC-802), accepted:**
  - P-W2-67-TD4-A: the root conftest's static guard also catches an f-string `--basetemp=`.
  - Your engineer's P1, option A: the time-limit case in `tests/unit/close` gets a `TMPDIR` of its own.
  - TD1C-A: the fixtures remove the code-graph folders they make.
  - Review F3.
- **W1-05's nested run and the retention option:** W2-70 retired W1-05's switch-over case. Re-check the code (DEC-718): name any nested run left as a row; otherwise say it is gone.
- **Roles (DEC-907, DEC-906):**
  - every change under `tests/acceptance/` is a fresh test designer's, in the folders your ticket body names;
  - your engineer changes `tests/unit/close/**`, `tests/unit/guard/**` and `tests/conftest.py` only.
- **The review waits for the owner (P-W2-67-R23).** Round 1 used both of DEC-413's reviews. **Run no review in this run.**

## This run's order

1. **Merge `w2/integrate` into this branch,** in one Bash call, with its trailers in the message's final block (`Task: DAEO-9nys`, `Implements: DEC-914`, `Role: orchestrator`, `Co-Authored-By`).
   - The tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2` when the merge is clean, or the recorded resolution otherwise.
   - DEC-912's rule now passes a merge whose acceptance files equal git's own merge.
   - Then rebuild.
2. **A fresh test designer** (launched sandboxed, `--effort xhigh`): W1-30's cases, W2-L420, the plant's removal; then W2-50's cases. Two batches if that is cleaner.
3. **Check red yourself:** each revised case red against its planted fault.
4. **A fresh engineer** (launched sandboxed, `--effort high`): the 15 nested-run functions and the ride-alongs in its paths.
5. **Verify in full** in the close's form, under the lock, with the retention option and the disk gate first: rebuild, collection, `gov check`, the parallel run, the serial-only run.
   - Put JUnit XML under `/tmp/gov-os-lead-W2-67/`, never in the worktree.
   - Run row W2-L423's early warning on this worktree after the runs.
6. **Return:**
   - **DONE-UNREVIEWED** (the verification green, no review run), with everything a review would need: the commits, the planted-fault evidence per case, the changes' line counts;
   - or PACKAGES.

   The orchestrator then runs the review step the owner decides.

**Estimate:** about 300 to 400 lines over 13 W1-30 cases, 15 unit functions and W2-50's cases; about 4 to 5 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
