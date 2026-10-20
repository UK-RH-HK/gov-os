You are a fresh engineer. Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. This is a repair: an earlier ticket's acceptance suite is red on this branch's head, and you find out whether this ticket's change causes it and, if it does, fix it within the ticket's paths.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0z8c`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists (or, if no change is needed, after your evidence is complete and the tree is clean). A foreground command is killed after 10 minutes: give each test run `timeout 540` and split anything longer. Commit your work before you run any long suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. A correction is a new commit. Leave no uncommitted change behind.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files (`git show <commit>:<path>` of a single named file is fine), never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Never run `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Code that reads a flag is tried in a temporary repository.
- Any edit to `src/gov/guard/containment.py` or to the helper it imports must leave them importable and working at every save: your own session's hooks run this worktree's `src/`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`; never run `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **On an authentication or access error, stop and say so.**

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and its `allowed_paths`.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W2-05/`; the failing suite `tests/acceptance/W1-46/` (read-only).
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-710, DEC-712, DEC-135, DEC-732, DEC-737.
- The code the ticket touches: `git log c94e1507..HEAD` and `git diff c94e1507..HEAD -- src` show this ticket's change so far.

## The failing output

`PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -rs`, run alone on head `b212be84`, twice: `470 passed, 23 errors in 204.86s`. Every error is at the setup of the module fixture `research`; the first:

```
_ ERROR at setup of test_a_research_install_succeeds_into_a_venv_inside_the_experiment_folder _
the launched research session did not run the probe to its end (no complete experiments/spikes/exp-901/results.txt)
gov launch research DAEO-zz97 -- -p Do exactly these two steps, once each, and nothing else. If a step is refused or fails, do not retry it and do not work around it. Step 1: run this Bash command as written: cd experiments/spikes/exp-901 && uv --no-cache venv .venv && uv --no-cache pip install --offline --no-index --python .venv/bin/python vendor/w1_46_probe-0.1-py3-none-any.whl  Step 2: run this Bash command as written: cd /tmp/pytest-of-usain/pytest-3453/w1-46-live-research0/repo && bash experiments/spikes/exp-901/probe.sh  Then answer DONE. --permission-mode acceptEdits --model haiku --max-turns 8 --allowedTools Bash,Write
exit code: 0
stdout:
Step 1 completed successfully. Step 2 failed: `bash: experiments/spikes/exp-901/probe.sh: No such file or directory`. Per your instructions, I have not retried or worked around this failure.
```

The 23 cases: `test_a_research_install_succeeds_into_a_venv_inside_the_experiment_folder`, `test_a_research_install_outside_the_repository_fails_at_the_write_fence`, `test_a_research_bash_write_to_a_sibling_directory_fails`, `test_a_research_write_to_a_new_path_outside_the_folder_is_refused_or_reported`, the 17 parameters of `test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist`, `test_the_research_allowlist_refuses_a_domain_that_is_not_on_it`, `test_each_session_uses_a_temp_directory_of_its_own`.

## What you do

1. Find out whether this ticket's change causes it. Show the cause with evidence (for example, by reproducing the steps the session takes in a temporary repository built from scratch, under the old and the new git environment of the code involved). Do not take the failure for load or chance without evidence.
2. If this ticket's change causes it, fix it inside your paths, without making a guard or gate decision fail open and without undoing what the W2-05 acceptance cases need (every W2-05 case that passes on `b212be84` must still pass). If a file is lost or changed that a session did not mean to change, say exactly how in your return: that is a lost-work case.
3. If it is not this ticket's change, change nothing, and give the evidence.

**Your paths (DEC-777, stricter-only):** `src/gov/**/*.py`, limited to calls that start git (and the import of the helper they use); `src/gov/util/**`; `lefthook.yml`; `tests/unit/gitenv/**`; `docs/research/AR-2-git-sweep.md`. **You change no file in another unmerged or unclosed ticket's paths:** W2-50's `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`; W2-54's `src/gov/context/**`, `src/gov/check/schema.py`, `src/gov/retrieval/semantic.py`; W2-53's `src/gov/close/**`; and `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py`, `src/gov/lock/**`, `src/gov/release/**`, `src/gov/check/commands.py`, `src/gov/resources/**`, `src/gov/launch/gate*`. If the fix needs one of them, stop and return a package naming the file.

Never the acceptance tests (MR-3): a test you think is wrong is returned as a package. Builder tests go in `tests/unit/gitenv/`. Proportion (DEC-135).

After a fix, run in the foreground, each to its end, never with `-x`, each under `timeout 540`: `tests/acceptance/W1-46`, `tests/acceptance/W2-05`, `tests/acceptance/W1-03`, `tests/unit/gitenv`, `tests/unit/containment`, `tests/unit/guard`, with `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH` (quoted inside `env`) and the `PYTHONPATH` above.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-05 (DAEO-0z8c): <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-710" --trailer "Implements: DEC-712" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2` and `git status --short` and quote them.

## Return

The cause, with its evidence; your commit's hash (or "no change", with the evidence); the files changed; the tests you ran with their results; the lines added and removed; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Put these in the fields below.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Refused twice for the same call: stop and say so.
