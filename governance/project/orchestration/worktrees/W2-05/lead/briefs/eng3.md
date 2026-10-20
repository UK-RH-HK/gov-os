You are a fresh engineer. Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. The ticket is implemented. An independent review found two behaviours the acceptance tests missed, and a test designer has written them as acceptance cases (commit `68055fa3`). Your job: make those cases pass, without turning any other case red, inside the ticket's allowed paths.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"` — a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh` — git's own writes. They **must work**. If either fails, stop there and return with the exact error (you could not commit).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0z8c`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`), and `git log --oneline -1` (expect `68055fa3`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. **Commit your work before you run any long suite.** A foreground command is killed after 10 minutes: keep each run within that (the W2-05 suite takes about a minute; for a larger suite run one file at a time).
- **Write only inside the ticket's allowed paths:** `src/gov/**/*.py`, `src/gov/util/gitenv.py`, `lefthook.yml`, `template/lefthook.yml`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`. Never touch `tests/acceptance/**` (the acceptance tests are read-only to you; a test you think wrong is returned as a package, never edited) or `.gov-runtime/**`.
- **DEC-777: you change no file in another unmerged or unclosed ticket's allowed paths:** `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py` (W2-50); `src/gov/context/**`, `src/gov/check/schema.py`, `src/gov/retrieval/semantic.py` (W2-54); `src/gov/close/**` (W2-53); `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py` (W2-03); `src/gov/lock/**`, `src/gov/release/**`, `src/gov/check/commands.py` (W2-16); `src/gov/resources/**`, `src/gov/launch/gate*` (W2-20). If the work cannot be done without one of them, return a package naming the file.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees. Never run `gov rebuild` in this worktree (the lead does; never `--no-embeddings` on a real store), and never `gov close`, `gov adopt`, `gov pause` or `gov checkpoint`.
- Inside a launched session `.gov-runtime/freeze` and some dotfiles show as placeholder device files: conclude nothing from them, and never add them to a commit.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing.
- Never make a guard or gate decision fail open: each failure KPI must still refuse (DEC-580). Proportion rule (DEC-135): no code for edge cases beyond the KPIs and the review's two findings.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and allowed paths.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-712, DEC-135, DEC-580.
- The acceptance tests (read-only): `tests/acceptance/W2-05/README.md` (its section "The review's F1 and F2", and the reading P-1), `test_w2_05_planted.py`, `test_w2_05_code_index_tool.py`, `test_w2_05_sweep.py`, `w2_05_support.py`.
- The code you touch: the helper `src/gov/util/gitenv.py`, the staged-secrets gate in `src/gov/ci/command.py`, the code index `src/gov/codeintel/__init__.py`, and the sweep record `docs/research/AR-2-git-sweep.md`.

## What to do

1. **The review's F1: the staged-secrets gate never passes on an index other than the one being committed.** When `gov ci staged-secrets` runs with an inherited `GIT_INDEX_FILE` that the helper does not keep for the project (not git's own index of the project), the gate refuses, with a refusal that names that index, whatever is staged there or in the project's default index. It never scans the default index in its place. Git's own index (the main tree's, `index.lock` of `commit -a`, `next-index-*.lock` of `commit -- <path>`, a linked worktree's own) is still scanned as now, and a planted `GIT_DIR` alone is still cleared with the project's clean index passing. One place decides what "git's own" is (the helper); the gate asks it, it does not re-derive it.
2. **The review's F2: the code index's tool gets no inherited `GIT_*` variable.** Every start of the code-index tool by `src/gov/codeintel/__init__.py` (its configuration call, its command-line call, its server) gets its environment from the one helper for the project root, keeping whatever else the code index sets there today.
3. **The sweep record:** add the row(s) for the code-index tool's starts (the tool's name and the file that starts it, in the record's own form), and correct row 9: the code builds the declared check's environment with `git_env(root)`, not `git_env(root, base=...)`. Keep the record's counts true.
4. **Builder tests** in `tests/unit/gitenv/` for what you add to the helper, as regression evidence only.

## Verify before you return

- The W2-05 suite, to the end, never with `-x`:

      PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs

  Expected after your work: every case passes except the five that wait on other tickets (`test_the_containment_check_catches_the_change_whatever_its_environment_holds[trace variables]` and `[a trace setting in the person's git configuration]`, `test_the_guard_hook_does_not_run_the_git_first_on_path`, `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs`, `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment`) and `test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable`, which cannot reach its assertion inside a launched session (the code index's daemon folder under `/tmp/gov-cbm-<uid>` is read-only in the sandbox): the lead runs that one outside. Report every case's state.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit -q -p no:cacheprovider` (to the end).
- The suites that exercise the code you change, each in its own pytest process, file by file if a suite is long: `tests/acceptance/W1-40` (the hooks and `gov ci`) and `tests/acceptance/W1-16` (the code index; cases that need the code index's daemon folder may fail in the sandbox for that reason alone: name them, the lead runs them outside).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Stage only the files you changed, by name (never `git add -A` or `git add .`). One commit (or one per step), trailers in the final block:

    git commit -m "W2-05 (DAEO-0z8c): <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-710" --trailer "Implements: DEC-712" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commits; what each change does (the interface as built, in a line or two each); every suite you ran with its counts and every red case with its reason; lines added and removed; any package. Put these in the fields below.

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

Put the sandbox check's result (a) and (b) first in `evidence`.

Refused twice for the same call: stop and say so.
