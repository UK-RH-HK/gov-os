# Brief td-5: independent test designer for DAEO-0cd2 (W2-187), the fix batch after review round 1, FULL, class C2

You are a fresh independent test designer (MR-3) for ticket DAEO-0cd2 (W2-187). Write the acceptance cases for the
decided fix below, as described behaviour (DEC-136), before the engineer's fix exists. Change nothing else. The
ticket's Interface (I1-I13 and the CTO's notes) is binding; a reading you cannot settle comes back as a package.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187-tests |
| branch | w2/W2-187-tests (now at 46d131ab9) |
| your allowed paths | tests/acceptance/W2-187/**, tests/acceptance/W2-172/w2_172_world.py, tests/acceptance/W2-172/w2_172_git.py, tests/acceptance/W2-172/test_w2_172_s7_digest.py |
| the ticket | /home/usain/gov-os-worktrees/W2-187-tests/.tickets/DAEO-0cd2.md |
| the review's findings | docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md |
| the suite | tests/acceptance/W2-187/ (README.md, fake_gov_x.py, w2_187_world.py, w2_187_push.py, test_w2_187_s3_method.py, test_w2_187_s6_stale.py, test_w2_187_s7_drift.py, test_w2_187_s11_cron.py, test_w2_187_s12_push.py) |

You may run the engineer's code; do not read the engineer's changes under `src/gov/memaudit/`, `src/gov/adopt/memory_sets.py`
or `governance/project/orchestration/tools/memaudit_cron.sh` (the base copies are at `git show 5336a6fca:<path>`).
Search with Read, Grep and Glob (DEC-1065); no `gov retrieve` or `gov context`. Everything planted under `tmp_path`;
never the real sets root, the real runs folder or any hidden or memory-verdict folder (DEC-820).

## The decided fix (the CTO, 2026-11-14, after review round 1 passed; DEC-1157 (12), DEC-1180 (4), DEC-1156 (7))
Review round 1 (`docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md`, read its findings F-A, F-B and row R1) passed. The CTO decided
to fix F-A in this ticket, with F-B and R1 riding along. These three, as described behaviour (DEC-136):

1. **F-A, the searched store is the declared store (S3, S6/I6, S7).**
   - Now: the `standing run` driver hands its `preflight`, `measure` and `judge` children the repository as their root
     (`src/gov/memaudit/driver.py:177,184,186`; the fresh `run` does the same). `gov retrieve` therefore answers from the
     repository's own `.gov-runtime/store.db` while the declaration names and checks the store link's store.
   - Then: when the repository's own store sits at another commit than the link's, every attempt faults on the
     store-commit check and the week ends `STOPPED fault`.
   - Wanted: on both the standing and the fresh path, the `preflight`, `measure` and `judge` children work in the store
     link's work tree at the audit commit (I6 already says the pre-flight's root is the link's work tree). So the commit
     of the store every search reaches equals the link's, and S7 compares the same store.
   - The acceptance cases' planted `gov` (`tests/acceptance/W2-187/fake_gov_x.py:102-103`) answers the plan's store
     commit whatever folder it runs in, so it cannot show which store a search reached. The new case needs a planted
     `gov` that answers the commit of the store in the folder it is run from (its cwd, or its `--root`).
2. **F-B, push only the scanned commit (S12, F7).**
   - Now: `push.py` scans the repository, then pushes the branch name, which git reads again after the scan. A commit
     landing on the branch during the scan is pushed unscanned.
   - Wanted: the commit the branch names when the scan starts is recorded. `git push <remote>
     <that sha>:refs/heads/<branch>` pushes it, so the remote's branch is the scanned commit. The line stays
     `PUSH pushed <remote> <branch> <12 hex of the scanned commit>`.
3. **R1, gitleaks on step 6's cron line (S11, S12).**
   - Now: cron's `PATH` does not hold `~/.local/bin`, so a declared push is blocked every week as
     `scan failed missing`.
   - Wanted: A9's ACT.md step 6 line (`memory_sets.walls_act`) carries
     `GOV_MEMAUDIT_GITLEAKS=<gitleaks>` before the wrapper. `<gitleaks>` is the absolute path `shutil.which("gitleaks")`
     gives when A9 runs, else the literal `<path to gitleaks>`. The rest of the line and I13's step-6 sentence stay.

**Path cases:** if any of this needs a file outside your allowed paths (for instance a W2-172 *test* file that pins the
repository as the children's root, as opposed to `w2_172_world.py`, `w2_172_git.py` or `test_w2_172_s7_digest.py`),
stop and return PACKAGES naming the path and the line. Never widen the paths yourself.

## Your cases
- **F-A:** in the standing world and in a fresh world, plant the repository's own `.gov-runtime/store.db` at a commit
  other than the link's, and a planted `gov` (an extension of `fake_gov_x.py` or a new one) whose `result.store.commit`
  is the commit of the store in the folder it runs in. A standing run passes the store-commit check: no
  `FAULT ... store_commit`, a verdict, every search logged from the link's work tree. A fresh run's measure and judge
  also search from the link's work tree. Map them under `success-3` (standing) and `success-7` (the fresh run S7 compares).
  If a W2-172 case breaks because it pinned the repository as root and the fix is only in its helper, revise the
  helper with `Rewrite-Reason: DEC-1156 (7)` (the CTO's routing); if the change would be in a W2-172 test file other
  than `test_w2_172_s7_digest.py`, return PACKAGES naming it.
- **F-B:** a planted scanner that, while it runs, lands a commit holding a planted key on the declared branch: the
  remote's branch is the scanned commit, the `PUSH pushed` line names the scanned commit's 12 hex, and the planted key
  is in no output. Map under `success-12` and `failure-7`.
- **R1:** `walls_act(..., repo=<dir>)` with a planted `gitleaks` first on `PATH`: step 6's line holds
  `GOV_MEMAUDIT_GITLEAKS=<its absolute path>`; with none on `PATH`: `GOV_MEMAUDIT_GITLEAKS=<path to gitleaks>`. Map
  under `success-11`.
- Run them: red now where the fix is missing; say which and why. Check the README with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -c "from pathlib import Path; from gov.accept.runner import parse_map; m = parse_map(Path('tests/acceptance/W2-187/README.md').read_text()); print(sorted(m))"`.

## Rules
- Every pytest through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest <file or folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  with a Bash timeout of 3600000 ms; a heavy-slot refusal is a wait. Run the whole `tests/acceptance/W2-172` folder if
  you touch its helpers.
- Literal paths only as write targets; if a Write into `.gov-runtime/scratch/` is refused, write no script.
- Commit your paths only, the trailers in ONE final paragraph (`git add` new files first):
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1179, DEC-1182, DEC-1156" [--trailer "Rewrite-Reason: DEC-1156 (7)"] --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call: stop and say so; never reach the same effect by another form (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line: task / status / work_completed / files_changed / evidence / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` and
`guard_refusals:`.
