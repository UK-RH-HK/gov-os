Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-5: engineer for DAEO-0cd2 (W2-187), the fix batch after review round 1, FULL, class C2

You are a fresh engineer for ticket DAEO-0cd2 (W2-187). Build the decided fix below and nothing else. The ticket's
Interface (I1-I13 and the CTO's notes) is binding; a case you cannot meet within it or your allowed paths comes back as
a package.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 (head 46d131ab9) |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the review's findings (F-A, F-B, R1, with file and line) | docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md |
| the code | src/gov/memaudit/driver.py (`_Cycle.standing`, `_Cycle.run`, the link), runner.py, preflight.py, measure.py, judge.py, push.py, src/gov/adopt/memory_sets.py; how `gov retrieve` finds its store: src/gov/cli/main.py, src/gov/retrieve/command.py; src/gov/retrieval/measure.py (read only) |

Search with Read, Grep and Glob (DEC-1065); no `gov retrieve` or `gov context`. Never open the real sets root, the real
runs folder, any hidden or memory-verdict folder; never print any hidden set's ids or text (DEC-820).

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

## How
- Keep one judged path: the change is the children's root (the link's work tree at the audit commit) and nothing in
  `prompts.py`, the reader, the grader or the matcher. The anchors are read at that commit (I6). The fresh path's
  children move with it, so the fresh run's figures come from the same store S7 compares.
- Unit cases under `tests/unit/memaudit/` for each of the three, including a world where the repository's own store sits
  at another commit than the link's, and a branch that moves during a planted scan.
- Keep green: `tests/unit/memaudit`, `tests/unit/adopt/test_w2_187*`, `tests/acceptance/W2-170`, `W2-171`, `W2-172`,
  `W2-173`, `W2-88`, `W2-187`. The test designer writes the F-A, F-B and R1 acceptance cases in parallel; they are
  merged later. If a W2-172 case goes red because it pinned the repository as root, report it by name (it is the test
  designer's or a path case); never edit `tests/acceptance/`.
- Update `docs/changes/W2-187-evidence.md` (the three fixes, cases and results).
- Every pytest through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  each as its own Bash call with run_in_background and a 3600000 ms timeout; a heavy-slot refusal is a wait.
- Literal paths only as write targets; if a Write into `.gov-runtime/scratch/` is refused, write no script.
- Commit your paths only, the trailers in ONE final paragraph:
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1179, DEC-1182, DEC-1097, DEC-1098" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call: stop and say so; never reach the same effect by another form (DEC-1142 (9)). A
  permission denial of a Write or a Bash form is a refusal too.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line: task / status / work_completed / files_changed / evidence (pytest summary lines)
/ tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` and
`guard_refusals:`.
