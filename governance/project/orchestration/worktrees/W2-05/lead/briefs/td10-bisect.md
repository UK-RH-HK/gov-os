You are a fresh independent test designer (MR-3). Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-05-tests` on branch `w2/W2-05-tests`, made from the ticket's head `ba807a032603`. The ticket's independent review found a behaviour the acceptance tests miss; this is the test-design batch for it (DEC-136): you write the acceptance case(s) for the behaviour described below, from the specification and the KPIs, before the fix is merged.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error (you could not commit).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05-tests` and `w2/W2-05-tests`) and `git rev-parse --short=12 HEAD` (expect `ba807a032603`). If anything differs, stop and say so. Inside the sandbox `git status` shows placeholder device files at the worktree root (`.bashrc`, `.gitconfig`, `.mcp.json` and the like, character devices `1, 3`): they are not real; never stage them.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
  - **For you, "this worktree" is the tests worktree:** use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-tests/src` on every run, and quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-tests/src python3 -c "import gov; print(gov.__file__)"` (it must point under `/home/usain/gov-os-worktrees/W2-05-tests/src/`). Its `src/` is the ticket's code at `ba807a032603`, before the fix. Run nothing from `/home/usain/gov-os-worktrees/W2-05`, and read nothing there. The suites' support puts the `src/` beside the test files first on the `PYTHONPATH` of the processes it starts; keep it so, so that once merged your case exercises the ticket worktree's own code.
- **What you may not read (DEC-820 (c) and (d)).** (c) Never read this ticket's implementation: no file that `git diff --name-only w2/integrate...HEAD` names (run it in your worktree and keep to it), other than the tests under `tests/acceptance/`. That list includes `src/gov/close/nightly.py`, `src/gov/close/command.py`, `src/gov/util/gitenv.py` and others. Nothing in the ticket's worktree `/home/usain/gov-os-worktrees/W2-05`, by any tool. The existing code as it stands on the integration branch you may read with `git show w2/integrate:<path>` (for example `git show w2/integrate:src/gov/close/nightly.py`, the nightly as W2-77 merged it: its entry points and how a red found alone is bisected). (d) Never read the hidden half of any evaluation set.
- **Memory first (DEC-836, DEC-860, DEC-859, DEC-963).** Use `gov retrieve` for what you need to know before reading files at random, **on the integration branch's store only**, never this ticket's store: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 300 gov retrieve "<question>" --json` (a read; that store holds `w2/integrate` as of its last refresh; for what changed since, read `w2/integrate` itself with `git show w2/integrate:<path>`). A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any result under this ticket's implementation paths (its `allowed_paths` outside `tests/acceptance/`: `src/gov/**/*.py`, `src/gov/util/gitenv.py`, `lefthook.yml`, `template/lefthook.yml`, `template/.rulesync/hooks.jsonc`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`), and name in your return any such result you were served. In the sandbox a call may hang on the embedder: the `timeout` caps it. Say in your return which questions you asked.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead. Count the refusals you met and give the count in your return.
- **The guard has five rules now (ACT 1, DEC-953 item 2, DEC-954):** the implementer never writes acceptance tests; reviewers and auditors write only their own records; no reads of the hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner. The tool's own command checker refuses here-documents, `$TMPDIR` in compound commands and `rm` (a permission prompt nobody can answer): write long scripts with the Write tool under your temporary folder and run them. Report every refusal you meet (its time, the command's form in one line, the reason it gave, and whether it was one of the five rules or a false positive).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A foreground command is killed after 10 minutes: keep each run within that. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- **Protected material (DEC-820).** Never read, print, search, diff or copy the held-out material under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never print a secret. **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees.
- Inside a launched session `.gov-runtime/freeze` and some dotfiles show as placeholder device files: conclude nothing from them, and never add them to a commit.
- No subagents. Install nothing: an install you need is raised as a P1 escalation in your return (DEC-957). Never write `.gov-runtime/**`. Never run `gov close`, `gov adopt`, `gov pause`, `gov rebuild` or `gov checkpoint` against this repository or any of its worktrees (inside a throwaway project of your own, the product's commands are what you test).
- **You write only** under `tests/acceptance/W2-05/`: one new test file for this behaviour, `README.md` (a row mapping the behaviour to its case(s) and the expected red reason), and `w2_05_support.py` only if a shared builder must live there (say so). No other path.
- **Disk and files (DEC-898).** Your share of the ticket's budget is 2 GB and 100,000 files and folders outside the tracked tree. Your temporary folder is the one `gov launch`'s sandbox set: keep it (do not set `TMPDIR` yourself). Keep pytest's own temp retention (never `--basetemp`). Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- Never ask or notify the owner (no question box, no `owner-ping`): a question comes back to the lead as a package in your return. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines (above all: "Every check, test helper and command that runs git in another folder clears the inherited GIT_* variables" and the failure KPI "A planted GIT_DIR or GIT_INDEX_FILE in a hook's environment reaches no child git call").
- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-804 (item 3, P-1), DEC-970 (its W2-05 line: the nightly's bisect judges each commit in the environment of the run that found the red), DEC-580, DEC-136, DEC-462, DEC-491; row W2-M161 in `docs/plan/WAVE_2_LIST.md`.
- The nightly as the integration branch has it: `git show w2/integrate:src/gov/close/nightly.py` (its module docstring: a red that fails alone is bisected with `git bisect run` over the commits since the last green night).
- The suite's support and README: `tests/acceptance/W2-05/w2_05_support.py`, `README.md`, and one existing case for the house style (for example `test_w2_05_planted.py`).

## The behaviour (the review's finding R4-1, as a behaviour; DEC-136)

**What was done:** a throwaway project (its main tree on one branch, a second branch such as `main` checked out nowhere, a green night recorded, then commits of which one turns a test red). That test runs git in a temporary folder of its own (`git init` there, then commits, a branch, a checkout or a merge), with the environment it inherits, as an honest test does. The nightly finds the red, runs it alone (red), and bisects it with `git bisect run` over the commits since the last green night.

**What happened:** `git bisect run` itself puts `GIT_DIR` (the night clone's git directory), `GIT_EXEC_PATH` and `GIT_PREFIX` into the step's environment. The step's test therefore inherited `GIT_DIR`: its `git init` re-initialised the clone instead of making its own repository, and its commits, branches and checkouts acted on the clone and, through it, on the project. The project's `main` moved onto a foreign commit, a foreign branch appeared, once the person's own commit fell off `main` (reflog only), and the bisect named a commit outside the project's history as the first bad one.

**What should happen (the KPIs, P-1, DEC-970):** each bisect step's test runs in exactly the environment the run that found the red gave it: no `GIT_*` variable of anyone but the three the close's test runs get (`GIT_CONFIG_GLOBAL`, `GIT_CONFIG_NOSYSTEM`, `GIT_NO_LAZY_FETCH`); so a test's git in a folder of its own acts only on that folder; the project's branches, HEAD and reflogs are as they were before the night; and the first bad commit named is a commit of the project's history (the one that made the test red).

**Severity:** high (loses work).

## What to write

Acceptance case(s) for that behaviour, in a new file under `tests/acceptance/W2-05/`, that:
- run a **real** `git bisect run` through the nightly as the product runs it (its entry point as the integration branch has it, at the level you judge stable; never a stand-in for `subprocess` or for git, which cannot see what git adds to a child's environment);
- build the throwaway project from scratch in a temporary folder, with a red test of the kind above (it runs git in a folder of its own with its inherited environment; it may also record the `GIT_*` variable names it saw into a file outside every repository, which the case reads);
- require: every branch, HEAD and reflog of the project unchanged after the night; the first bad commit named is the commit that made the test red; the step's test saw no `GIT_*` variable but those three (by name; never print a value).

Keep the case within a few minutes. The expected red reason at `ba807a032603` (before the fix) goes in the README row: the project's refs moved or a foreign commit was named, and the step saw `GIT_DIR`.

## Runs (inside your sandbox)

- Your new case(s), before you commit: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05-tests/src python3 -m pytest tests/acceptance/W2-05/<your file> -q -p no:cacheprovider -rfEs`. Expected: red at `ba807a032603` for the reason above. Report the counts and the failure messages. If a case is green before the fix, it does not show the behaviour: rebuild it, or say why.
- Then W2-05's hooks-source file and sweep file (to check your new file changed nothing else): `... -m pytest tests/acceptance/W2-05/test_w2_05_hooks_source.py tests/acceptance/W2-05/test_w2_05_sweep.py -q -p no:cacheprovider`.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Stage only the files you wrote, by name (never `git add -A` or `git add .`). One commit, the trailers in the final block, `Implements:` holding decision ids only (DEC-927 item 2):

    git commit -m "W2-05 (DAEO-0z8c): acceptance case for the nightly's bisect step environment (review finding R4-1)" --trailer "Task: DAEO-0z8c" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970, DEC-710, DEC-804" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After it, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commit's hash (12 digits); each case with what it builds and what it asserts; its red at `ba807a032603` with the failure message; the lines added; every run's counts; the `gov retrieve` questions you asked and any P-R1 result you were served; the read refusals you met; any package. Put these in the fields below.

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

Put the sandbox check's result (a) and (b) first in `evidence`. After the twelve fields, a section `guard_refusals:` (one line per refusal, or `none`) and the count of read refusals.

Refused twice for the same call: stop and say so.
