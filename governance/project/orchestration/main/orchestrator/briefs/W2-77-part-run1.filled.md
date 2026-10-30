You are the ticket lead for ticket `DAEO-b6hm` (`W2-77`, "The nightly's clean-up removes only its own clone, by its exact path (row W2-M406)"), profile FULL, keystone 2, working only in the worktree `/home/usain/gov-os-worktrees/W2-77` on branch `w2/W2-77`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `23079f92a6fa`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-b6hm.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-77");
- DEC-939 (item 5), DEC-915 (item 4), DEC-890, DEC-803 and DEC-941; row W2-M406 in `docs/plan/WAVE_2_LIST.md`;
- W2-68's probe record, `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md`, finding F1 (its fixture);
- `src/gov/close/nightly.py`, above all `night`'s clone and its `finally:` block (lines 280 to 327), and its `_bisect`; `src/gov/close/batch.py`'s call of `nightly.night`.

## Why you start now

- **The nightly can lose another worktree's work.** `gov.close.nightly` removes its clone and then runs a repo-wide `git worktree prune` (`src/gov/close/nightly.py:327`). Any worktree of the repository whose folder its process cannot see loses its registration and its administrative folder, and with them its staged index (row W2-M406).
- **W2-68's reviewer reproduced it on a fixture** (F1). The batch passed and closed its ticket; the second worktree's registration was gone, and git answered "not a git repository" in its folder.
- **The batch waits on you.** W2-68 is merged (`848f5ab3`), but its batch reaches the nightly. So the close queue stays on single closes until this fix is merged and re-pinned (DEC-939 item 5, P-W2-68-PRUNE (b), DEC-803). Then the batch is switched on and its gain measured on this repository. The re-plan's date depends on that gain (REPLAN-W2 §3).
- **First in block A** (DEC-941; REPLAN-W2 §2.1). W2-78 follows you.

## The decisions for this run

- **Design first, short.** The ticket's paths hold no note, so you write it in your scratch: `.gov-runtime/scratch/lead/design.md`, at most a page, in behaviour; it is a plan, not code. It says:
  - the clone the nightly adds is removed by that exact path, `git worktree remove --force <that path>`, and by nothing else;
  - no repo-wide `git worktree prune` runs anywhere in the nightly or in anything it calls;
  - **if the removal fails,** only that clone's own administrative entry goes. Its name is read from the clone's own `.git` file (`gitdir: <common dir>/worktrees/<name>`), never guessed from the folder's name: every nightly's clone is a folder called `tree`, and git can give a later one another entry name. Otherwise the failure is written in the night's record and reported;
  - nothing else changes: the selection, the runs, the record and the verdict.
  
  It goes into the test designer's and the reviewer's briefs as text.
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-77/`:
  - one case per KPI line, in temporary repositories built from scratch, with a tiny suite so that a night runs in seconds;
  - **W2-68's F1 as a case:** a second worktree holding a staged change has its folder moved aside while the nightly runs, and separately made unreadable, then restored. Its registration, its administrative folder and its staged index are kept;
  - a failed removal of the clone touches no other worktree's entry, a registered worktree with a name like the clone's included, and the failure is in the record;
  - **no repo-wide prune, shown by behaviour:** a stale registration of a missing folder, planted before the run, is still there after it;
  - the batch's route (`python3 -m gov.close.batch run`), which reaches the nightly, also keeps the hidden worktree;
  - the nightly's selection, runs, record and verdict are unchanged on the same fixture.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in the allowed paths: `src/gov/close/nightly.py` (the clean-up only) and new files `tests/unit/close/test_nightly_cleanup*`.
- **Fail closed:**
  - a removal whose result cannot be confirmed is reported, never hidden;
  - no fallback widens to other entries;
  - nothing in the nightly prunes by pattern or by age.
- **Running beside you:**
  - W2-67 (`DAEO-9nys`, in progress) holds `tests/unit/close/**`. Write only new `test_nightly_cleanup*` files there, and edit no existing file (`test_nightly.py` included).
  - W2-05 (`DAEO-0z8c`, merge-back) holds `src/gov/**/*.py` for the git environment of git calls. Leave how the nightly's git calls build their environment as it stands; the later merge takes the conflict.
  - W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
  - W2-61, W2-60a and W2-56 hold `src/gov/retrieval/measure.py` and `src/gov/launch/**`.
  - W2-78 (`src/gov/close/` readers, not `nightly.py`) follows you; it does not run now.
  
  Do not touch their files. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
  - **Every rebuild** runs as `flock /tmp/gov-os-rebuild.lock …` (DEC-939 item 2).
  - **Never run `python3 -m gov.close.nightly`, or the batch, against this worktree or the main tree** (DEC-915 item 4): only the tests' temporary repositories.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **Reviews:** one (the ticket). A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head, given the design note. **A fault here loses work.**
  - **The probe looks above all for any path that prunes, or removes, another worktree's registration, administrative folder or index:**
    - the clean-up and its fallback;
    - a failed or partial removal;
    - a removal by a guessed name;
    - `git worktree add --force`;
    - the bisect's start and reset in the clone;
    - the batch's route into the nightly;
    - every other git command the nightly runs against the shared repository.
  - **A finding that shows one of the ticket's failure lines fails the review.** Those lines are any repo-wide prune left, another worktree's registration or index lost, and a failed removal hidden. The owner ordered this fix for exactly that loss (DEC-939 item 5).
  - Commit the probe record only when it passes. If it fails on such a finding: one test-design batch, one engineer, a full run, and a second, last review (DEC-413).

## This run's order

1. The design note (yours, in scratch).
2. Tests first (the test designer), then **check red yourself.**
3. The engineer.
4. Rebuild and verify in full.
5. The review.
6. **Return** DONE or PACKAGES. DONE means the probe passed and the branch is ready to merge. It is then re-pinned, and the queue switches to the batch.

**Estimate:** about 20 lines, about 5 hours with the full run and one review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
