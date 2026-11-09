# Brief: engineer

You are a fresh engineer. Ticket: DAEO-r30l (W2-20, "Machine-wide resource gate"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-20` on branch `w2/W2-20`. You implement the ticket until its acceptance tests pass.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-r30l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-20` and `w2/W2-20`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Read nothing under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. (This ticket needs no dev tier.)
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere; copy single named files only, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Code that reads a flag is tried in a temporary repository.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never write the real `~/.gov-os/`.** Anything you run by hand that touches the registry runs with a temporary `HOME`; builder tests do the same, and never depend on this machine's real memory, load or sessions.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. On ESCALATION_BLOCKED from any command, stop and return it.
- The git hooks are uninstalled until W2-08. Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return a package. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-r30l.md` (read-only): its KPI lines and its `allowed_paths`; the W2-20 card in `docs/plan/WAVE_2_WBS.md` §2 and §0 rule 9.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W2-20/`. The README states the public interface you build: the command, its options and exit codes, the configuration file and its defaults, the reading sources.
- The list rows it takes in: W2-M188, W2-M244, W2-M262 (`docs/plan/WAVE_2_LIST.md`, `docs/plan/WAVE_2_TRIAGE.md`).
- The sources: DEC-729. The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-135, DEC-182, DEC-476, DEC-718, DEC-732.
- The code the ticket touches: the command-module convention in the docstring of `src/gov/cli/main.py`, `src/gov/cli/errors.py`, and `src/gov/launch/` for orientation (read only).

## The values and one open question

- The gate's values are not yet given by the owner (P-W2-9). They are configuration, **in one place**, with the proposed values as the defaults: at least 4 GiB available memory, the 1-minute load below the processor count, heavy sessions counting double, at most 8 weighted Gov OS sessions on the machine. The owner's answer must change one setting, not the code's shape.
- Open with the owner (P-1): whether the session limit counts the session being started. No acceptance test sits on that boundary. Implement the source's words as they stand — the gate is open while the weighted count of live sessions is at most the maximum — and keep that comparison in one place, so the owner's answer changes one line.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/resources/**` (new; `gov resources` is `src/gov/resources/command.py` by the command-module convention), `src/gov/launch/gate*`, `tests/unit/resources/**`. Nothing else: `src/gov/launch/launcher.py`, `src/gov/launch/command.py` and `src/gov/cli/**` belong to other tickets. The start check a launcher calls lives in this ticket's paths; calling it from `gov launch` is W2-21's.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/resources/`, as regression evidence only (MR-3).
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the three list rows; the estimate is about 120 lines. Never make the gate fail open: a reading that cannot be taken, a registry that cannot be read, or a configuration that cannot be parsed shuts the gate (or refuses the start) with a named reason; it never opens it.
- Run the ticket's acceptance tests with `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/acceptance/W2-20 -q -p no:cacheprovider -rs` in the foreground, to its end (never `-x`), until they pass; then the builder tests with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/unit/resources -q -p no:cacheprovider`. Afterwards check that `~/.gov-os/` was not created or changed by your runs (`ls -la ~/.gov-os` should show it absent if it was absent).

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476), after checking the hooks folder as above:

    git commit -m "W2-20 (DAEO-r30l): gov resources and the machine-wide resource gate" --trailer "Task: DAEO-r30l" --trailer "Role: engineer" --trailer "Implements: DEC-729" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash; the files changed; the tests you ran with their results; the lines added and removed; the interface as built (command, options, exit codes, configuration file and defaults, registry location and format); the `gov.__file__` line; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
