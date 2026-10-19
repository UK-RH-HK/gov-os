You are a fresh engineer. Ticket: DAEO-siiz (W2-52, "The lite A7 and A10 stage records"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-52` on branch `w2/W2-52`. Your change is small and exactly named below; then you run the suites to their end.

**The state of the branch.** An earlier engineer committed the gates at `bd9fdfec` (`src/gov/adopt/lite_gates.py`, the A7 and A10 entries in `stages.py`, the adopt skill's A7 and A10 steps, `tests/unit/adopt/test_lite_gates.py`). A later engineer found them passing all 65 W2-52 cases with a throwaway stand-in that added `"A7"` and `"A10"` to `STAGES` in `src/gov/adopt/command.py`, and failing 54 cases plainly (argparse "invalid choice"), because `command.py` was outside the ticket's paths. The owner has now widened the paths (DEC-800, committed in the ticket file at `f6317639`). **No stand-in for `command.STAGES` any more: the change is real now.**

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-siiz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-52` and `w2/W2-52`), and `git log --oneline -1` (expect `f6317639`). If anything differs, stop and say so.
- This session is not sandboxed (the adopt suites need the code graph's folder under `/tmp`, which the sandbox makes read-only until W2-56). The lead watches every file outside this worktree before and after your session: write nothing outside this worktree except your own temporary folders under `/tmp` made with `mktemp -d`, and say which you made.
- **The code under test (owner's DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag. Never `git stash`.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nothing under `~/.claude/` is read.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme is put under a `.gov-runtime/` folder (DEC-673). Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths (a byte copy of one named file with `cp <file> <file>` is fine). No subagents. Install nothing: a tool you need is returned as a package.
- Never run `gov rebuild --no-embeddings`. Never run `gov close`, `gov adopt` or `gov pause` against this worktree (the cases run `gov adopt` in their own temporary projects; that is fine). On ESCALATION_BLOCKED from any command, stop and return it.
- **The git hooks are uninstalled until W2-08.** Never `--no-verify`, never `core.hooksPath`.
- If the guard refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-siiz.md` (read-only) and the card in `docs/plan/WAVE_2_WBS.md` §2 (W2-52).
- `tests/acceptance/W2-52/README.md` (read-only), for what the cases expect.
- `src/gov/adopt/command.py`, `src/gov/adopt/stages.py`, `template/governance/kernel/skills/adopt/SKILL.md`.

## What you write: exactly this, nothing else

1. `src/gov/adopt/command.py`: add `"A7"` and `"A10"` to the `STAGES` tuple (keep the stage order: `"A6", "A7", "A8", "A10"`), and add A7 and A10 to the module docstring's stage list beside it (`<A0|A1|...>`), in the same order. No other line of that file changes.
2. `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md`: byte copies of `template/governance/kernel/skills/adopt/SKILL.md` (`cp` that one file onto each; check with `cmp`).
3. Nothing else. **Do not touch `.claude/skills/adopt/SKILL.md`** (it already differed before this ticket; the owner leaves it alone). Do not change `stages.py`, `lite_gates.py`, the template skill or the unit tests unless a suite below fails because of them; if one does, stop and return it as a package with the failing output instead of changing the code. **Never** `tests/acceptance/**` (MR-3): a test you think is wrong is returned as a package.

Check `git diff --stat` shows those three files only, then commit them (only those three staged), before any suite, with the trailers in the final block:

    git commit -m "W2-52 (DAEO-siiz): gov adopt --lite takes A7 and A10; the adopt skill's synced copies" --trailer "Task: DAEO-siiz" --trailer "Role: engineer" --trailer "Implements: DEC-741" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After the commit, check `git log --oneline -2` and `git status --short`.

## Then run the suites, each to its end, never with `-x`, each in its own pytest process

- `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/acceptance/<suite> -q -p no:cacheprovider -rs` for each of these suites: `W2-52` (expect 65 passed, no stand-in), `W1-36`, `W1-27`, `W1-38`, `W1-26`, `W1-07`, and `W1-41`.
- the builder tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-52/src python3 -m pytest tests/unit/adopt -q -p no:cacheprovider`.

A foreground command is killed after 10 minutes. W1-41 takes about 30 minutes and W2-52 3 to 4 minutes: start every suite that may pass 10 minutes with the Bash tool's `run_in_background: true` and `timeout: 7200000`, with its output in a file and its exit code in a file in a `mktemp -d` folder of yours (for example `...pytest ... > <dir>/w1-41.log 2>&1; echo $? > <dir>/w1-41.exit`), and wait in the foreground with `until [ -s <dir>/w1-41.exit ]; do sleep 20; done` given a timeout of 600000, repeated until the file exists. Never end your session while a run of yours is running. Run the suites one after another, not together.

## Return

Your final message gives, in the fields below: your commit hash with its trailers; the three files changed with `git diff --stat` of your commit; the `gov.__file__` line; each suite you ran with its counts, and for every failure its test id and one line of reason; the temporary folders you made; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

Return one message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
