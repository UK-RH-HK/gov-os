# Brief: independent test designer (a revision of earlier tests named by this ticket's KPI)

You are a fresh independent test designer (MR-3). Ticket: DAEO-r30l (W2-20, "Machine-wide resource gate"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-20` on branch `w2/W2-20`. The ticket's own acceptance tests exist and pass; an implementer's commit exists (so DEC-491 applies to anything you rewrite).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-r30l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-20` and `w2/W2-20`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists (or with a package and no commit).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Read nothing under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it) anywhere. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never write the real `~/.gov-os/`.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild --no-embeddings`. On ESCALATION_BLOCKED from any command, stop and return it.
- The git hooks are uninstalled until W2-08. Before your commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return a package. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-r30l.md` (read-only): its first success KPI line names a new command, `gov resources`. The W2-20 card in `docs/plan/WAVE_2_WBS.md` §2; the plan is approved by DEC-729.
- In `docs/DECISION_REGISTER.md`: DEC-542 (commands beside the twelve are recorded in the command list, each with one test-designer line), DEC-491 (a rewrite after an implementer's commit carries `Rewrite-Reason:`), DEC-221, DEC-462, DEC-729, DEC-732.
- The earlier acceptance tests that hold the command set: `tests/acceptance/W1-07/w1_07_support.py` (the recorded lines), `tests/acceptance/W1-07/test_w1_07_recorded_commands.py`, `tests/acceptance/W1-32/test_w1_32_command_set.py`, `tests/acceptance/W1-26/test_w1_26_recorded_commands.py`, and any other earlier acceptance test you find that pins the command set exactly.
- `tests/acceptance/W2-20/README.md` for what `gov resources` is.

## The behaviour

The ticket's KPI adds the command `gov resources`. The earlier suites hold the set of `gov` commands exactly: the twelve reserved ones plus the commands recorded in the command list. With `gov resources` built, W1-32 now fails:

    test_the_command_set_is_the_twelve_and_the_three_recorded_ones
    AssertionError: gov has commands the command list does not record: ['resources']

Record `resources` in the command list the way DEC-542 records a command (one test-designer line), and revise every earlier acceptance test that pins the recorded set so that it holds the set exactly with `resources` in it — nothing looser: a command that is in neither the twelve nor the list must still fail those tests. Keep each revision to the lines that pin the set; change no other behaviour of those tests. If you judge that recording a new command needs an owner decision beyond DEC-729 and DEC-542, or the guard refuses you those paths, write nothing and return a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## What you write

- Only the earlier acceptance-test lines that pin the recorded command set (under `tests/acceptance/W1-07/`, `tests/acceptance/W1-32/`, `tests/acceptance/W1-26/`, or another earlier suite you name), and, if useful, one line in `tests/acceptance/W2-20/README.md` saying so. Nothing under `src/`.
- Run each suite you touched to its end (never `-x`): `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-20/src python3 -m pytest tests/acceptance/<suite> -q -p no:cacheprovider -rs`. The W1-07 suite can fail on its latency case under machine load (`test_decision_p95_is_under_100_ms`, `test_a_call_waits_under_100_ms_p95_for_the_hook` are DEC-372 named cases); report it and do not change it.

## Commit

One commit, only your test paths, trailers in the final block (DEC-182, DEC-476, DEC-491), after checking the hooks folder as above:

    git commit -m "W2-20 (DAEO-r30l): record gov resources in the command list (DEC-542)" --trailer "Task: DAEO-r30l" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" --trailer "Rewrite-Reason: <one line: the KPI adds gov resources; the earlier tests hold the recorded set exactly>" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash; each earlier test you rewrote, with its reason; the suites you ran with their counts; the `gov.__file__` line; any package.

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
