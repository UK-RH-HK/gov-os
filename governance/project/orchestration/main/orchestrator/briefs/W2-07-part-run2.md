You are the ticket lead for ticket `DAEO-r9ss` (`W2-07`, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`.

**This is run 2,** after your run 1 returned PACKAGES (P-W2-07-A and P-W2-07-B). `git log --oneline -1` must show `44062fec`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first.

## The owner's answers (DEC-904, on `w2/integrate`, which you merge first)

- **P-W2-07-B (a): your test designer's batch is widened to the 196 cases.** Your ticket file names them; each revision carries a `Rewrite-Reason:` naming its decision, and no expectation is lowered.
  - **W1-30's shared fixture** (`tests/acceptance/W1-30/w1_30_support.py`, `conftest.py`): its fixture projects green under the in-close `gov check` (`Rewrite-Reason: DEC-868 item 1 (b)`). This clears 175 cases.
  - **The 20 gate-order cases,** to DEC-868 item 3's order (`Rewrite-Reason: DEC-868 item 3`). They include W2-53's one load-sensitive case.
  - **The repair-ticket case,** to KPI 8 (`Rewrite-Reason: KPI 8, AR-9, W2-L209`).
  DEC-492, DEC-490 (one part) and DEC-493 (one part) are marked superseded for these parts (DEC-866).
- **P-W2-07-A, the verification run, until the retention trial reports:**
  - the run alone may use 6,000,000 files and folders and 60 GB in your temp folder, `/tmp/gov-os-lead-W2-07`;
  - **one verification run at a time across the machine:** run your full parallel run and your serial-only run each under `flock /tmp/gov-os-verify.lock <command>`, which waits while another session's run, or the orchestrator's retention trial, holds the lock;
  - run the disk gate just before;
  - do not try to remove your temp folder (you cannot): name it and its size in your return, and the orchestrator removes it.
- **P-W2-07-C and DEC-903:** the six interface readings of your run 1 are accepted.
- **The order (DEC-899 item 2):** this ticket merges before W2-66. W2-66's lead is idle until you return DONE.

## This run's order

1. **Merge `w2/integrate` into this branch, in one Bash call, with its trailers** (DEC-750):
   `git merge --no-ff w2/integrate -m "<subject>" -m "Task: DAEO-r9ss
   Implements: DEC-904
   Role: orchestrator
   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
   - The merge's tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2`.
   - A conflict you cannot resolve keeping both sides is PACKAGES.
   - Read the widened ticket file after the merge.
2. **Test designer round 2:** a fresh independent test designer, launched sandboxed, `--effort high`, on exactly the widened batch.
   - Give it run 1's engineer payload (`log/eng-1b.result.md` in your scratch) with the 196 cases and their causes.
   - Its share of your budget: 6 GB and 300,000 files and folders.
3. **Check:** run W1-30, W2-53, W2-07 and `tests/unit/close` with this worktree's `src/`, each in its own process. Every case is green or a known accepted red; `accepted_reds` is now empty, and the p95 entries are gone.
   - **If a case shows a real gap in the implementation,** a fresh engineer, launched sandboxed, `--effort high`, fixes it inside the allowed paths.
4. **Verify** in the close's form, under the lock:
   - a full rebuild;
   - the collection check;
   - `gov check` (if the secrets-indexing family alone is red, or `CHECK_FAILED` as in run 1, re-run `python3 -m gov.secrets` alone and report both; do not re-run the full check to green);
   - the full parallel run with JUnit XML;
   - the serial-only run.
   Record the temp folder's peak size.
5. **Return** DONE (the orchestrator merges you first), or PACKAGES.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
