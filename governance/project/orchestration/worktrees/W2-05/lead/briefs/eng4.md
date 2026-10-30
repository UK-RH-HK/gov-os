You are a fresh engineer. Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. The ticket was implemented in earlier runs. The branch has since merged `w2/integrate` (commit `1814315f106e`), and an independent test designer has written this resume's acceptance cases (commit `9e6572e8bc22`). This is **batch 1 of 2** of the resume. Your job: make the batch-1 cases below pass, without turning any other case red, inside the ticket's allowed paths.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error (you could not commit).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`) and `git log --oneline -1` (expect `9e6572e8bc22`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **What you may not read (DEC-820 (c) and (d)).** (c) Never read this ticket's acceptance-test code: nothing under `tests/acceptance/W2-05/`, by any tool (no Read, cat, grep, diff, `git show` or `git log -p` of it). You may run those tests and read their results: names, pass or fail, failure messages. You work from the specification, the KPIs, the behaviours stated here and the existing code. (d) Never read the hidden half of any evaluation set.
- **Memory first (DEC-836, DEC-859, DEC-860).** Use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main retrieve "<question>" --json`. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return which questions you asked. **The retrieval index also holds this ticket's acceptance tests, which you may not read:** ask through the lead's wrapper, which drops every answer item that names `tests/acceptance/W2-05` before printing (it prints only how many it withheld): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 300 python3 /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/retrieve_safe.py "<question>" [--batch-size N] [--continue <token>]`. Never run `gov retrieve` bare. In the sandbox the semantic facet may be unavailable (no embedder) and a call can hang: the `timeout` caps it; the lexical facet still answers.
- **An untracked file you must leave alone:** `tests/acceptance/W2-05/test_zz_scratch_b1.py` (an empty scratch file the test designer could not remove). Do not read, stage or touch it; it collects no test.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead (`src/gov/...`). Count the refusals you met and give the count in your return.
- **The guard's command forms (DEC-941 item 4a).** The guard refuses a shell command it cannot read whole. No shell variable as a write target (`> "$OUT/x"`, `mkdir -p $D/t`, `sed -i` on a `$VAR` path): use literal paths. No here-document (`<<EOF`), no backticks, no `bash -c '…'` script it cannot read, no long inline `python3 -c` with braces. Put anything longer in a script file written with the Write tool under your temporary folder, and run that file. A refused form is not retried in another disguise.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. **Commit your work before you run any long suite.** A foreground command is killed after 10 minutes: keep each run within that (the W2-05 suite takes about 1 to 2 minutes; for a larger suite run one file at a time).
- **Write only inside the ticket's allowed paths, and in this batch only these files:** `src/gov/util/gitenv.py`, `src/gov/check/runner.py`, `src/gov/guard/decide.py` (its freeze look-up only), `src/gov/adapters/portability.py`, the one `matcher` line of `template/.rulesync/hooks.jsonc`, and `tests/unit/gitenv/**`. Never touch `tests/acceptance/**` (read-only to you; a test you think wrong is returned as a package, never edited) or `.gov-runtime/**`. Within `src/gov/**/*.py` the ticket is limited to calls that start git.
- **Files other leads hold right now: never change them.** `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py` (W2-03); `src/gov/secrets/**` (W2-71); `src/gov/retrieval/measure.py` (W2-61); `src/gov/launch/**` (W2-60a, W2-56); `src/gov/close/nightly.py` (W2-77). If the work cannot be done without one of them, stop and return a package naming the file.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- **Protected material (DEC-820).** Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never print a secret. **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees. Never run `gov rebuild` in this worktree (the lead does; never `--no-embeddings` anywhere), and never `gov close`, `gov adopt`, `gov pause` or `gov checkpoint`.
- Inside a launched session `.gov-runtime/freeze` and some dotfiles show as placeholder device files: conclude nothing from them, and never add them to a commit.
- No subagents. Install nothing: a tool you need is returned as a package.
- Never make a guard or gate decision fail open: each failure KPI must still refuse (DEC-580). Proportion rule (DEC-135): no code for edge cases beyond the KPIs and the behaviours below.
- **Disk and files (DEC-898).** Your share of the ticket's budget is 3 GB and 150,000 files and folders outside the tracked tree. Your temporary folder is the one `gov launch`'s sandbox set: keep it (do not set `TMPDIR` yourself). Keep pytest's own temp retention (never `--basetemp`). Remove any folder you made outside pytest as soon as you no longer need it. Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Nobody asks or notifies the owner (no question box, no `owner-ping`): a question comes back to the lead as a package in your return. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and allowed paths; the W2-05 card in `docs/plan/WAVE_2_WBS.md` §2.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-135, DEC-580, DEC-777, DEC-783 (item 2), DEC-804 (items 1 and 3), DEC-805, DEC-807, DEC-822 (item 3).
- The sweep record `docs/research/AR-2-git-sweep.md` (the helper's rules, P-1 as it stood, the rows).
- The code you touch: `src/gov/util/gitenv.py`, `src/gov/check/runner.py`, `src/gov/guard/decide.py` (its freeze look-up only), `src/gov/adapters/portability.py`, the one `matcher` line of `template/.rulesync/hooks.jsonc`, and `tests/unit/gitenv/**`.

## What to do (batch 1)

The lead's red check at `9e6572e8bc22` (outside the sandbox) gave 15 failed, 33 passed. Batch 1 takes 13 of the 15: the three declared-check cases, the six hooks-source cases, the two containment cases, `test_the_guard_hook_does_not_run_the_git_first_on_path` and `test_the_guard_hook_refuses_within_its_own_limit_when_the_freeze_look_up_hangs`. The other 2 (`test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment`, `test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`) are batch 2's: leave them red.

1. **F-A with P-1 (DEC-804 items 1 and 3, DEC-807 item 2), in `src/gov/util/gitenv.py` and `src/gov/check/runner.py`.** The ticket's second review found that a check the project declares, run on a hooked commit (by the pre-commit hook through `gov ci checks`, or by `gov check`), that runs git in a temporary repository of its own, acted on the project's index. The declared-check runner gives the check `git_env(root)`, which keeps git's own index of the root as an absolute path; the check's `git add`/`git commit` in its own repository then wrote the project's index. The commit landed with a deletion nobody staged; a variant left the project's index naming a missing object.
   - **What must hold (P-1, accepted by the owner):** an inherited `GIT_INDEX_FILE` is honoured only for git calls in the project root; a program that may start git elsewhere gets no index. A declared check is such a program: it receives no `GIT_INDEX_FILE` (and, as now, no `GIT_DIR`, `GIT_WORK_TREE` or `GIT_COMMON_DIR`), in all three shapes: the main tree with a plain commit (git exports a relative `.git/index`), the main tree with `git commit -a` (`.git/index.lock`), and a linked worktree (its index under `.git/worktrees/<name>/`). The commit then lands with exactly what was staged, the project's index matches it, and it names no missing object.
   - **What stays as it is:** git's own index is still the one the staged-secrets gate scans on a hooked commit (`gov ci staged-secrets`, row 13: gitleaks runs `git diff --staged` in the root); an inherited index that is not git's own is still refused by that gate, naming it (review F1, `foreign_index`); a planted `GIT_DIR` or `GIT_INDEX_FILE` still reaches no child git call; git calls of the form `git -C <root> …` keep git's own index as today.
   - One place decides (the helper): give it a way to build the environment of a program that may start git elsewhere (no index kept), and use it for the declared check. Keep W2-59's change in `_run_command` as it is: `command = _judged(command)` first, then the environment; no `PYTHONPATH` lines (DEC-822 item 3: a declared check runs on the judge's own package, not the project's).
   - Update the helper's docstrings to P-1 as decided.
2. **Row 42, W2-L160 and DEC-783 item 2, in `src/gov/guard/decide.py` (`_mirror_path`, the guard hook's freeze look-up, `git -C <root> rev-parse --git-common-dir`).** W2-50 has merged and closed, so this row is now this ticket's (DEC-777 item 2).
   - **git by absolute path (W2-L160):** the guard hook does not run whatever `git` comes first on `PATH`; it runs git resolved by an absolute path. If no git can be resolved, the guard does not pass the call on that account (fail closed, DEC-580).
   - **Its environment:** the helper's, pinned (`git_env(root, pinned=True)` or its equivalent): no inherited `GIT_*` variable (trace variables included) and no trace setting from the person's git configuration reaches it. Today this call is the only git call that writes the planted trace targets in the containment cases.
   - **Its own time limit, 15 seconds (DEC-783 item 2):** when the look-up hangs, the guard gives up on it at 15 s by its own limit and answers **refuse** (DEC-580: fail closed), well inside the hook's own 20 s deadline. Today a hanging look-up runs into the hook's deadline (`decision=timeout` at 20 s); the case requires `deny`, not before about 14.5 s and by 18 s. A look-up that fails for another reason keeps today's behaviour unless that would pass a frozen tree; never make the freeze check fail open.
3. **DEC-805 (W2-M281), in `src/gov/adapters/portability.py` and the one `matcher` line of `template/.rulesync/hooks.jsonc`.**
   - Adapter-portability compares the template's hooks source (`template/.rulesync/hooks.jsonc`) with the repository's (`.rulesync/hooks.jsonc`) **by hook events and matchers, paths normalised**, whenever the template's hooks source exists in a project whose kernel is at `template/governance/kernel` (this repository's shape). **Drift, red:** an event in one source and not the other; an event whose matcher differs; a matcher present in one and absent in the other. Each drift gives a finding that names the hooks source (`hooks.jsonc`) and the event. **Not drift, green:** a difference only in the hook's paths (`governance/kernel/hooks/<name>.py` against `template/governance/kernel/hooks/<name>.py`), only in the order of the events or of the hooks of an event, or only in the command wrapper around the hook (the repository's commands call the pinned interpreter; the template's call `python3`). Findings are grouped by cause (W2-L109's spirit): one finding per drifted event, not one per line.
   - **Add the template's missing `sessionStart` matcher**, `"matcher": "compact|clear|resume"` (the repository's), to `template/.rulesync/hooks.jsonc`: that one line only (DEC-805 item 2 widens the ticket by it). With it, adapter-portability is green over this repository's two sources. If the guard refuses that write, stop and return a package; do not try another form.
4. **Builder tests** in `tests/unit/gitenv/` for what you add to the helper (and, if you like, a unit test of the hooks comparison in the same folder), as regression evidence only.

Do not touch the sweep record or any other file in this batch: batch 2 re-runs the sweep and records every change.

## Verify before you return

- The W2-05 suite, to the end, never with `-x`:

      PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -q -p no:cacheprovider -rs

  Expected after your work, inside the sandbox: every case passes except (a) batch 2's two (`test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment`, `test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`), and (b) the cases that fail inside a launched session for a reason not their own: the five retrieval-regression cases ("Ollama is unavailable … hit@5: 0.0": the sandbox reaches no embedder; they pass outside it, the lead checked) and `test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` (the code index's daemon folder under `/tmp/gov-cbm-<uid>` is read-only in the sandbox). The lead runs those outside. Report every case's state.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit/gitenv -q -p no:cacheprovider` and the unit suites of the packages you change, to the end.
- The suites that exercise the code you change, each in its own pytest process, file by file if a suite is long (same `PATH` and `PYTHONPATH` as above): the guard hook's (`tests/acceptance/W1-02`, and `tests/acceptance/W2-50` if present), the declared checks' and `gov ci`'s (`tests/acceptance/W1-40`, `tests/acceptance/W2-59` if present), adapter-portability's (`tests/acceptance/W1-38`), and `tests/unit/guard`, `tests/unit/adapters` and `tests/unit/check` where they exist. Cases that need an embedder or the code index's daemon folder may fail in the sandbox for that reason alone: name them, the lead runs them outside.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Stage only the files you changed, by name (never `git add -A` or `git add .`: placeholder files show in this sandbox). One commit per step is fine; trailers in the final block, `Implements:` holding decision ids only (DEC-927 item 2):

    git commit -m "W2-05 (DAEO-0z8c): <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-804, DEC-807, DEC-805, DEC-783, DEC-580, DEC-710" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commits; what each change does (the interface as built, in a line or two each); every suite you ran with its counts and every red case with its reason; lines added and removed; the `gov retrieve` questions you asked; the read refusals you met; any package. Put these in the fields below.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
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
