You are the ticket lead for ticket `DAEO-ye2a` (`W2-72`, "Containment's merge rule matches DEC-912: a merge-back file equal to git's own merge is no change"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-72` on branch `w2/W2-72`.

**This is run 1.** `git log --oneline -1` must show `92d5c273`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read the ticket file (`.tickets/DAEO-ye2a.md`), its card in `docs/plan/WAVE_2_WBS.md` §2, and DEC-918 first.

## Why you start now

- **The close's containment gate refuses two closes.** It (`src/gov/close/command.py`, `_check_containment` → `judge_commits`) refuses W2-66's and W2-65's closes on their merge-backs: `03f470a5` (W1-30's close file) and `4ef3293a` (two W1-26 files).
- **The cause is DEC-410 DP-24.** Under `tests/acceptance/**`, it reads every path both parents changed as the merge commit's own change (`read_merge` in `src/gov/guard/containment_merge.py`; `_judge_commit` in `src/gov/guard/containment.py`). Both merges are git's own clean merges of two test designers' edits.
- **W1-01's rule already passes them** since DEC-912. The live hook flags them.
- **The owner's decision (DEC-918 item 1), exactly:** a merge-back file under `tests/acceptance/` equal to git's own merge of its parents (`git merge-tree --write-tree`) is neither reverted, refused nor counted as a change, by the live hook or by the close's gate. Any file that differs from git's own merge (a hand edit, a conflict resolution) is still caught as before.
- **Not (a2):** do not add a condition on the commits that brought each side.
- **You ride the first re-pin,** which waits for you. Work steadily, without shortcuts.

## The decisions for this run

- **Where the change goes:** in containment's judgement, the path both `_judge_commit` (the live check) and `judge_commits` (the close) use. Mirror DEC-572's lift for ticket files, but on the owner's single condition: the merge's blob of the file equals merge-tree's blob for it, with no conflict on that file.
  - Merge-tree runs once per merge, with the full commit ids, within the existing git-process budgets.
  - A merge-tree that errors, an octopus merge, and parents with several merge bases or none give no allowance (fail closed).
  - Leave `read_merge`'s own result and the approval check (`src/gov/decisions/checker.py`) unchanged, unless your design shows that the live check cannot reach the rule otherwise; then say why in your return.
- **Ticket files keep DEC-421's and DEC-572's rule.**
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort high`), in `tests/acceptance/W2-72/`:
  - one case per KPI line, in temporary repositories built from scratch: a clean merge of two edits of one acceptance file passes the live check and the close's gate; the same merge hand-edited, a conflict resolution, an octopus merge and a criss-cross merge stay caught;
  - a case that `judge_commits` returns no finding for `03f470a5` and `4ef3293a` in this repository's objects (full ids from `git rev-parse`; write them in the test, not in your records).
  - **W1-50's DP-24 cases** that read a clean merge of a both-changed acceptance file as the merge's own are revised by the same designer, `Rewrite-Reason: DEC-918`, with no other expectation lowered. They are named in the ticket body (MR-3).
  - **The designer's brief must not set `TMPDIR`:** inside the sandbox it keeps the launcher's own.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in `src/gov/guard/containment.py`, `src/gov/guard/containment_merge.py` and new unit tests `tests/unit/guard/test_w2_72_*.py`. W2-67, in flight, holds the rest of `tests/unit/guard/`.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **Known:** `adapter-portability` may be RED on `.claude/settings.json` in a worktree until the owner's regeneration; W1-19's warm-query case is on `load_sensitive`; W2-54's context-reproducibility case may time out under parallel load (re-run alone).
  - Any other red is named with its cause.
- **Reviews:** two (DEC-413). A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head. Commit the probe record only when it passes.

## This run's order

1. Tests first (the test designer), then **check red yourself.**
2. The engineer.
3. Rebuild and verify in full.
4. Review 1. If it fails on a fail-open or lose-work finding an honest agent can hit: one test-design batch, one engineer, a full run, review 2 (the last).
5. **Return** DONE (probe passed; ready to merge for the first re-pin), or PACKAGES.

**Estimate:** about 40 to 60 lines in `src/gov/guard/`, about 5 hours with the full run and one review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
