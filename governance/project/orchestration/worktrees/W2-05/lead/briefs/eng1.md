You are a fresh engineer. Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. You implement the ticket until its acceptance tests pass, except the cases this brief names as red until another ticket merges.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0z8c`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. A foreground command is killed after 10 minutes: give each test run `timeout 540` and split anything longer. **Commit your work before you run any long suite.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase in this worktree. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Never run `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees: they share `.git/hooks` with the main tree. To try lefthook, build a temporary repository from scratch in a temporary folder, with its own stand-in `.claude/settings.json` that you write, and run lefthook there with its working folder set there and no `GIT_*` variable of yours in its environment.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Code that reads a flag is tried in a temporary repository.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`; never run `gov close`, `gov adopt` or `gov pause`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **On an authentication or access error, stop and say so.**

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines, its `allowed_paths` and its `list_rows`; the W2-05 card in `docs/plan/WAVE_2_WBS.md` §2.
- The ticket's acceptance tests and their README (read-only): `tests/acceptance/W2-05/`. The README's "Readings the tests rest on" section states how a `GIT_*` value that names the call's own repository's git directory (git's own index for `commit -a`, `commit -- <path>`) is honoured while any other is cleared: implement to it.
- The sources: AR-2 in `docs/plan/WAVE_2_LIST.md` ("### AR-2: the hook's git environment"); the list rows W2-L109, W2-L160, W2-M012, W2-M105, W2-M113, W2-M161, W2-M231, W2-M281 in `docs/plan/WAVE_2_LIST.md` and `docs/plan/WAVE_2_TRIAGE.md`.
- The decisions that apply, in `docs/DECISION_REGISTER.md`: DEC-710, DEC-711, DEC-712, DEC-719, DEC-135, DEC-500, DEC-580, DEC-718, DEC-732, DEC-737.
- The code the ticket touches: every call in `src/gov/**/*.py` that starts git.

## What you write

- **Your paths, narrowed (DEC-777, stricter-only):** `src/gov/**/*.py`, limited to calls that start git (and the import of the helper they use); `src/gov/util/__init__.py` and `src/gov/util/gitenv.py` (new); `lefthook.yml`; `tests/unit/gitenv/**`; `docs/research/AR-2-git-sweep.md`. **You change no file in another unmerged or unclosed ticket's paths:**
  - W2-50's: `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`;
  - W2-54's: `src/gov/context/**`, `src/gov/check/schema.py`, `src/gov/retrieval/semantic.py`;
  - W2-53's: `src/gov/close/**`;
  - the held tickets': `src/gov/check/schema.py`; `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py`; `src/gov/lock/**`, `src/gov/release/**`, `src/gov/check/commands.py`; `src/gov/resources/**`, `src/gov/launch/gate*`.
- **Do not create `template/lefthook.yml`,** and do not edit `template/lefthook.yml.jinja` (outside your paths): the ticket's allowed path names a file the tree does not hold, which is with the owner as a package. If the settings fix needs the template's hooks file to change, say exactly what change in your return.
- **First, the sweep record** `docs/research/AR-2-git-sweep.md`, as the acceptance tests ask: every call that starts git in `src/gov/**/*.py` (file, call, the folder it acts on, whether it inherited the caller's environment, how it was changed). Every call in a file of the list above is still listed, marked "after <W2 id> merges" (for example "after W2-50 merges"), and left unchanged in this run.
- **Then one helper** that every such call uses, so that inherited `GIT_*` variables (and the trace, configuration and lazy-fetch variables the rows W2-M105, W2-M113 and W2-M161 name) never reach a child git call in another folder, without clearing a value git itself gave the call for its own repository. Change the calls in your files to use it. Then the settings re-sort (KPI success 3) within your paths.
- **Expected red at the end of this run:** `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` (W2-53's `src/gov/close/**`), `test_the_guard_hook_does_not_run_the_git_first_on_path` and `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs` (W2-50's `src/gov/guard/decide.py`), and `test_install_and_uninstall_leave_the_settings_byte_identical[the template's hooks file]` if it needs the template's hooks file. Every other case must pass. If a KPI cannot be met at all without one of the files above, stop and return a package naming the file.
- **The list rows (DEC-718):** re-check each row against the code. For each, say whether it is fixed by your commit, was already fixed before (with the commit that fixed it), or lies outside your narrowed paths (and why). Do not widen your paths for a row.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Builder tests go in `tests/unit/gitenv/`, as regression evidence only (MR-3).
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows. Never make a guard or gate decision fail open: each failure KPI must still refuse.
- Run the ticket's acceptance tests in the foreground, to their end, never with `-x`, until they pass (save the expected reds above): `timeout 540 env PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs`; then the builder tests `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit/gitenv -q -p no:cacheprovider`, and, after your commit, the unit folders of the packages you changed (for example `tests/unit/guard`, `tests/unit/ci`, `tests/unit/retrieval`, `tests/unit/containment`), each under `timeout 540`.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-05 (DAEO-0z8c): <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-710" --trailer "Implements: DEC-712" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2` and `git status --short` and quote them.

## Return

Your commits' hashes; the files changed; the sweep record's count of calls, of calls changed and of calls marked "after <W2 id> merges"; the interface of the helper as built; the tests you ran with their results; the lines added and removed; each list row's state; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). Put these in the fields below.

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
