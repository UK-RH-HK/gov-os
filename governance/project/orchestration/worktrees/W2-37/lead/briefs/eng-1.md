You are a fresh engineer. Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37` on branch `w2/W2-37`. You implement the ticket until its acceptance tests pass.

## Step 0, before any work: the sandbox check (DEC-789)

Report its result first in your return.
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6n5k','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, naming any file you made outside this worktree (do not delete it).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-6n5k`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37` and `w2/W2-37`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it); copy single named files only, never `governance/project/`. A test that needs a repository builds a temporary one. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Untracked names such as `.bashrc`, `.gitconfig`, `.mcp.json` in `git status` are sandbox placeholders: never add, edit or delete them; stage your files by exact path, never `git add -A` or `git add .`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause`.
- The git hooks are uninstalled until W2-08: never `--no-verify`, never `core.hooksPath`.
- **Known limit (package P-W2-38):** inside the sandbox the code graph's folder `/tmp/gov-cbm-<uid>` is read-only, so the cases that build the code graph (the suite's `local_only` cases) cannot run here. If they fail only for that reason, commit what you have, say so plainly in your return (which cases, the exact error), and stop; do not work around it.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-6n5k.md` (read-only): its KPI lines and its `allowed_paths`; the W2-37 card in `docs/plan/WAVE_2_WBS.md` section 2.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W2-37/`. They are the specification of the command's interface and output. The README lists, per test, the KPI line, row or glue item it covers and the readings the test designer took.
- The sources: CAP-33 in `docs/contract/contract.yaml` (its acceptance line; covers CAP-33.a, .b, .e, .f, .g); the list rows W2-L319, W2-M056, W2-M150, W2-M285, W2-M320 in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`; the glue rows "S0b2 G-16" and "S0b2 G-24" in `docs/plan/WAVE_2_TRIAGE.md`.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-167, DEC-391, DEC-035, DEC-105, DEC-135, DEC-466, DEC-500, DEC-747, DEC-732.
- The code the ticket touches: `src/gov/cli/` (how `gov` finds a command from its package folder), `src/gov/closure/` (read API only: you change **no** file there), the record store and decision records (`src/gov/store/`, `src/gov/records/`, `src/gov/decisions/`: read through their public API only, change nothing), the code index (`src/gov/codeintel/`, read only), and the path map (`governance/project/path-map.yaml`, by that exact name).

## What you write

- **Only inside the ticket's `allowed_paths`, as the card narrows them:** `src/gov/impact/**` (new) and `tests/unit/impact/**`. `src/gov/closure/**` is read API only: you change no file there. If the closure graph's API lacks what a test needs, stop that part and return a package naming the function. No other file anywhere: not `src/gov/check/commands.py`, not a skill, not a schema, not another ticket's code.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/impact/`, as regression evidence only.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows the ticket takes in. Estimate: about 280 lines. Never make a guard or gate decision fail open: an impact report never reads as complete when a graph was missing, stale or unreadable; a refusal stays a refusal. `gov impact` is a read command: it writes nothing outside its declared output, and it never builds or rebuilds the store or the code index.
- **Readings still with the owner.** The test designer took readings that are returned as packages for confirmation: what the record-to-code id mapping (G-16) follows, what "deletable" means (G-24), which specification status counts as closed (W2-M320), and the output's key names. Build to the tests as written, and keep each of these readings in one named, commented place, so that a different answer is a small change.
- **Tests that are expected to stay red after your work; do not try to make them pass:**
  - the two cases of `test_w2_37_skill_routing.py::test_the_skill_runs_gov_impact_for_the_question` (the change skill is outside your paths);
  - `test_w2_37_rows.py::test_the_depth_of_a_radius_comes_from_an_owner_decision_or_a_measurement`, if it can only pass with an owner decision or a measurement that does not exist yet: never cite a decision id that does not say so.
  Report each with its failure line.
- `gov impact` will be missing from the recorded command lists (`RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`, DEC-747, and W1-07's tests' list); both are outside your paths. Do not edit them: report the exact line each needs.
- Run the ticket's acceptance tests in the foreground to their end, never with `-x`, until they pass:
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -rs`
  then the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/unit/impact -q -p no:cacheprovider`
  and W1-20's suite (the closure graph you read): `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src python3 -m pytest tests/acceptance/W1-20 -q -p no:cacheprovider -rs`.

## Commit

Commit only your paths, staged by exact path, with the trailers in the final block (DEC-182):

    git commit -m "W2-37: gov impact" --trailer "Task: DAEO-6n5k" --trailer "Role: engineer" --trailer "Implements: CAP-33.b" --trailer "Implements: CAP-33.g" --trailer "Implements: DEC-167" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

A later fix is a new commit with the same trailers. Show `git log --format='%h %s' -3`, `git show --stat --format='%(trailers)' HEAD` and `git status --short` in your return.

## Return

Your commit hashes; the files changed; the lines added and removed (`git diff --stat 4d79565e..HEAD -- src tests/unit`); the tests you ran with their counts, and each test still red with its failure line and why; the interface as built (command line, options, output keys, exit codes); where each owner-pending reading lives; the exact lines the two command lists need; the `gov.__file__` line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
