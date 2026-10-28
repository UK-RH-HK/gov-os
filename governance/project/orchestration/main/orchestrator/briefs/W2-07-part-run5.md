You are the ticket lead for ticket `DAEO-r9ss` (`W2-07`, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`.

**This is run 5, the end of round 2 (DEC-924 item 3).** `git rev-parse --short=12 HEAD` must show `750481148aeb` (run 4's DONE head), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

- **W2-57 merged first** into `w2/integrate` (`57e363c5`, 2026-10-28), after the close queue of 2026-10-27 ended. By the owner's merge order (DEC-924 item 3), whichever of W2-57 and W2-07's round 2 merges second merges `w2/integrate` back and re-verifies. That is this run.
- **Both changed `src/gov/close/command.py`:** W2-57 its serial phase (`_run_tests`) and `serial.py` (new), round 2 gate (h)'s line. git's trial merge of the two is clean, with no conflict. Your job is to prove the merged code works, not to change it.
- **The integrate head also brings** the owner's `accepted_history` entry for `611955faffaa` (`048f5758`), the 39 DEC-927 entries (`e95d3520`), W2-74 and the seven closes of 2026-10-27.

## This run's order

1. **Merge** `w2/integrate` into `w2/W2-07` (`git merge --no-ff w2/integrate`, with `Task: DAEO-r9ss`, `Implements: DEC-924` and `Role: orchestrator` in the final trailer block). If git reports a conflict, stop: `git merge --abort`, and return PACKAGES naming each file.
2. **Rebuild** (`gov rebuild` from this worktree's `src`, as the common part says).
3. **Your check on the three tickets** (the script file you wrote in run 4 under `.gov-runtime/scratch/lead/`, or a new one there; never `python3 -c` with braces, DEC-409): the judge's work-without-a-task gate from this worktree's `src` for `DAEO-5j8b`, `DAEO-pl6k` and `DAEO-r9ss`. **Expected: 0, 0 and 0** (the `611955faffaa` entry is now on the head you merged). Report each count.
4. **The suites the merge touches, first:** `tests/acceptance/W2-07/`, `tests/acceptance/W2-57/`, `tests/unit/close/`. Any red: name it with its cause before the full run.
5. **Verify in full** in the close's form, under the lock, with the retention option and the disk gate first.
   - **Known:** W1-19's warm-query case and W1-46's 23 live-session cases are on `load_sensitive` (W2-57's nightly route takes them out of the close only once the second re-pin pins it). W2-54's green-here case may time out under load (row W2-L429; re-run it alone). The seven base reds of the settings regeneration were fixed by W2-74 (merged `6ee7b4d0`): any of them red again is a finding.
   - Any other red is named with its cause.
6. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return; every `Implements:` item of your commits is a decision id the register holds.
7. **Return** DONE (ready to merge; it rides the second re-pin), or PACKAGES.

**No review and no probe (STANDARD; no code changes in this run).** You start no engineer and no test designer. If the merged code needs a change to pass, do not make it: return PACKAGES with the failing case, its cause and the smallest fix you see.

**Estimate:** about 2 hours, most of it the full run (which may wait for the verification lock: another full run holds it until about 02:00).

**Time:** your session's Bash calls each have a two-hour limit; run the full verification in the background with its output in a file, and wait for it.

---
