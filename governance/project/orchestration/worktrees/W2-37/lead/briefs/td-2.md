You are a fresh independent test designer (MR-3). Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`. The ticket's acceptance suite `tests/acceptance/W2-37/` exists and its implementation is committed; an independent review of the implementation found five behaviours the suite does not hold. You add a test design batch for them (DEC-136, DEC-413): new acceptance cases that hold each behaviour below, red against the current code, and the README updated to map them. You do not change what an existing case holds.

## Step 0, before any work: the sandbox check (DEC-789)

Report its result first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6n5k','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (do not delete it).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-6n5k`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37` and `w2/W2-37`), and `git rev-parse HEAD` (expect `59ea2993` as its prefix). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Your tests, run from this worktree, exercise this worktree's code, as the suite's support module already arranges for every process it starts (`child_env`); keep to it.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only, clone into a temporary folder, and are marked `local_only`. (No dev tier is needed here.)
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it). A throwaway stand-in copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch, as the suite's fixtures do. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Untracked names such as `.bashrc`, `.gitconfig`, `.mcp.json`, `docs/source` in `git status` are sandbox placeholders: never add, edit or delete them; stage your files by exact path, never `git add -A` or `git add .`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. The guard refuses tools it does not know (`Monitor` and every `mcp__` tool): do not call them.
- Never run `gov rebuild` (any form). Never run `gov close`, `gov adopt` or `gov pause`.
- **Known limit (package P-W2-38):** inside the sandbox the code graph's folder `/tmp/gov-cbm-<uid>` is read-only, so cases that build a code index (`local_only`) cannot run here; they fail at setup with `OSError: [Errno 30] Read-only file system`. Write them, mark them `local_only` as the suite does, and say in your return which they are: the lead runs them red outside the sandbox. Do not work around it.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- The git hooks are uninstalled until W2-08: never `--no-verify`, never `core.hooksPath`.

## What you read

- The ticket file `.tickets/DAEO-6n5k.md` (read-only): its KPI lines and `allowed_paths`; the W2-37 card in `docs/plan/WAVE_2_WBS.md` section 2.
- CAP-33 in `docs/contract/contract.yaml` (its acceptance line; covers CAP-33.a, .b, .e, .f, .g); DEC-391 (what `gov closure` reports as `uncommitted`, current and stale), DEC-035, DEC-136, DEC-221, DEC-413, DEC-462, DEC-491 in `docs/DECISION_REGISTER.md`; the glue rows "S0b2 G-16" and "S0b2 G-24" in `docs/plan/WAVE_2_TRIAGE.md`.
- The existing suite and its README, `tests/acceptance/W2-37/` (its fixtures, support module, the interface it assumes and readings R1 to R11). Build the new cases on the suite's own fixtures and helpers. You read the public interfaces only (the `gov impact` and `gov closure` command lines and their JSON output, `gov.store.load`, `gov.codeintel.index`), never the implementation under `src/gov/impact/` to learn what a test should expect.

## The behaviours to hold (from the review; DEC-136)

Each is a described behaviour of `gov impact` as its output already names it (`graphs`, `complete`, `gaps`, `change[].deletable`, `radius`, `--out`, `--compare`, `matches`, `differences`). Write the success and the failure of each, thoroughly but with no combinatorial expansion.

1. **A record graph that does not match the working tree is never reported current.** (a) After the store was loaded, a record file is added under a record path and not committed (a ticket that implements the stated decision), or an edge is removed from a record file and not committed: the assessment does not report the record graph as current with a complete result that misses the new ticket or still lists the record whose edge was removed. (b) The store was loaded on one branch and the repository then switched to another branch (an older one, whose records differ): same rule. Accept either reading R4 allows: the record graph not current (not `ok`, with the word `stale` or the uncommitted paths named) and `complete: false`; or a report that reads the tree as it is now, listing the new ticket and not the removed edge's record. `gov closure` on the same repository already reports such files as `uncommitted`. Where the case needs a current code graph for `complete` to matter, make it `local_only`; keep a variant that runs without the code tool when one can hold the record side alone (`graphs.record` not current).
2. **A CIT-E whose kind is not a list never matches.** In the execution record checked with `--compare`, a kind whose value is a single item (`code: some_symbol`) or a map (`decisions: {DEC-099: done}`) while the proposal's list for that kind is empty: the comparison never reports `matches: true` with no differences. Accept a refusal that names the malformed kind, or the item listed as a difference.
3. **A CIT-P written from an incomplete assessment never reads as complete.** When the assessment is incomplete (for example, no code graph can be read), the record that `--out` writes either says so itself (the completeness, the state of each graph and the gaps, as the printed result gives them) or the write is refused, naming why. A complete assessment's file is unaffected by this case.
4. **A name shared by two code definitions is deletable only when every definition of it is.** In a temporary repository, two modules each define a function of the same name; one of them is called (by a function a decision record constrains) and the other is called by nothing. A change stated by that name is not reported `deletable`, and its radius is not lower than the radius the same repository gives when the dead definition is renamed away. `local_only`.
5. **A code file the index does not hold makes the code graph not current, whatever its modification time.** After the code index was built, a new file that calls a function the stated change reaches is moved into the tree with a modification time older than the index (as `mv`, `cp -p` or unpacking an archive keep it): the assessment does not report the code graph as current with a complete result that misses the new caller. Accept either: the code graph not current and `complete: false`; or the new caller listed. `local_only`.

## What you write

- Only inside `tests/acceptance/W2-37/`: one new test file for this batch (or new cases in the existing files where they belong), and the README: a section for this batch mapping each behaviour above to its tests, its expected red reason, and which are `local_only`. You change no existing case's assertions and no earlier ticket's tests; if you think one must change, return it as a package instead.
- Behaviour through public interfaces, never internals. Deterministic, no network. Temporary repositories only.
- Red first: run the suite to its end, never with `-x`: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -rs`. The new cases that can run here fail for the reason the README states; every existing case keeps the result it had (the three known reds stay red, the `local_only` ones error at setup here for P-W2-38).

## Commit

Commit only `tests/acceptance/W2-37/`, in one commit, with the trailers in the final block (DEC-182, DEC-491):

    git commit -m "W2-37: acceptance tests for the first review's findings (red)" --trailer "Task: DAEO-6n5k" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-33.b" --trailer "Implements: DEC-167" --trailer "Rewrite-Reason: test design batch for the first review's findings F1, F2, F3, F6 and F8 (DEC-136, DEC-413); no existing case changed" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log -1 --format='%H%n%B'` and `git status --short` in your return.

## Return

Your commit's hash; the new cases and the behaviour each holds; which are `local_only`; the red reason of each as you saw it (and, for `local_only` ones, the reason you expect); the suite's counts; the `gov.__file__` line; any package in full (question, why now, options, impact, reversibility, cost, recommendation, confidence).

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
