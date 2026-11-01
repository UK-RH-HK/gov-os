You are a fresh engineer. Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`, head `110125ddda0b`. This is one small fix batch: the lead's verification found one of this ticket's own acceptance cases red after a merge of the integration branch (below), and the round's review had described the same behaviour (R6-2). You build to the specification, its KPIs and the behaviour described, never to the tests (DEC-957). You make no merge.

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error (you could not commit).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`), `git rev-parse --short=12 HEAD` (expect `110125ddda0b`) and `git status --short` (expect no line but the sandbox's placeholder device files at the worktree root: names such as `.bashrc`, `.gitconfig`, `.mcp.json`, `.idea`, `.vscode`, each a character device `1, 3`; they exist only inside the sandbox and are never staged). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **What you may not read (DEC-820 (c) and (d), DEC-957).** (c) Never read any acceptance-test code: nothing under `tests/acceptance/W2-05/`, by any tool (no Read, cat, grep, diff, `git show` or `git log -p` of it), and nothing in the tests worktree `/home/usain/gov-os-worktrees/W2-05-tests`. You may run the acceptance tests and see only which pass and which fail (the run form below shows names and results, no failure text). You work from the decision, the specification, the KPIs, the behaviour stated here and the existing code; your test-driven development is your own unit tests. (d) Never read the hidden half of any evaluation set.
- **Memory first (DEC-836, DEC-859, DEC-860).** Use `gov retrieve` for what you need to know before reading files at random. **The retrieval index also holds acceptance tests, which you may not read:** ask through the lead's wrapper, which drops every answer item that names `tests/acceptance/W2-05` before printing (it prints only how many it withheld): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 300 python3 /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/retrieve_safe.py "<question>" [--batch-size N] [--continue <token>]` (it runs `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main retrieve "<question>" --json` for you). Never run `gov retrieve` bare. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. In the sandbox the semantic facet may be unavailable (no embedder) and a call can hang: the `timeout` caps it; the lexical facet still answers. This worktree's store was rebuilt at 01:15 at this head. Say in your return which questions you asked.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead (`src/gov/...`). Count the refusals you met and give the count in your return.
- **The guard has five rules now (ACT 1, DEC-953 item 2, DEC-954):** the implementer never writes acceptance tests; reviewers and auditors write only their own records; no reads of the hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner. The tool's own command checker refuses here-documents, `$TMPDIR` in compound commands and `rm` (a permission prompt nobody can answer): put anything long in a script file written with the Write tool under your temporary folder. Report every refusal you meet (its time, the command's form in one line, the reason it gave, and whether it was one of the five rules or a false positive).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. **Commit your work before you run any long suite.** A foreground command is killed after 10 minutes: keep each run within that.
- **Write only** `src/gov/retrieval/lexical.py`, `tests/unit/gitenv/**` and `docs/research/AR-2-git-sweep.md` (row 24, the lexical index's git calls). If the work needs another file, stop and return a package naming it. Never touch `tests/acceptance/**` (read-only to you, unread; a test you think wrong is returned as a package), `.rulesync/`, `template/` or `.gov-runtime/**`.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- **Protected material (DEC-820).** Never read, print, search, diff or copy the held-out material under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never print a secret. **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees. Never run `gov rebuild` in this worktree (the lead does; never `--no-embeddings` anywhere), and never `gov close`, `gov adopt`, `gov pause` or `gov checkpoint`.
- Inside a launched session `.gov-runtime/freeze` and some dotfiles show as placeholder device files: conclude nothing from them, and never add them to a commit.
- No subagents. Install nothing: an install you need is raised as a P1 escalation in your return (DEC-957).
- Never make a guard or gate decision fail open: each failure KPI must still refuse (DEC-580). Proportion rule (DEC-135): no code for edge cases beyond the decision and the behaviour below.
- **Disk and files (DEC-898).** Your share of the ticket's budget is 3 GB and 150,000 files and folders outside the tracked tree. Your temporary folder is the one `gov launch`'s sandbox set: keep it (do not set `TMPDIR` yourself). Keep pytest's own temp retention (never `--basetemp`). Remove any folder you made outside pytest as soon as you no longer need it. Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Nobody asks or notifies the owner (no question box, no `owner-ping`): a question comes back to the lead as a package in your return. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).


## What you read

- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-804 (item 3), DEC-580, DEC-135; row W2-M161 in `docs/plan/WAVE_2_LIST.md` (a trace setting the person planted reaches no child git call of `gov close`); the ticket's KPI lines in `.tickets/DAEO-0z8c.md`.
- `src/gov/util/gitenv.py` (the module docstring: `pinned` is "for the calls that only read, where a setting there (`trace2.eventTarget`) could write or change an answer"), `src/gov/retrieval/lexical.py` (`_git` and its four callers: `_tracked`'s `ls-files -z` and `hash-object --stdin-paths`; W2-108's `_tree`, merged from the integration branch at `d1533bf30a10`: `rev-parse HEAD --git-path index` and `ls-files -z`, run by `_checked`, the freshness key every `gov check`, `gov retrieve` and `gov close` works out), row 24 of `docs/research/AR-2-git-sweep.md`, and the unit tests in `tests/unit/gitenv/`.

## The red (the failing output, as the lead's verification gave it)

`tests/acceptance/W2-05/test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment`, red at `110125ddda0b`, in the full scoped run and again alone, in the close's environment:

    AssertionError: gov close with planted trace variables and a trace setting (W2-M161): a child git call wrote the planted trace target(s) ['user-config-trace2']

The case runs `gov close` on a throwaway project whose person has `[trace2] eventTarget = <a file>` in `~/.gitconfig` (and trace variables planted in the environment). The lead read the trace file it left: three git processes wrote it, all from the lexical index's `_git`: `git -C <project> rev-parse HEAD --git-path index` (twice) and `git -C <project> ls-files -z` (once). They run under `git_env(root)`, unpinned, so the person's global configuration is read and its trace target written. These calls came with W2-108's freshness key (merged here at `d1533bf30a10`); the same case was green in the last round, before that merge. The round's reviewer found the same thing by probe (R6-2: a person's global `trace2.eventTarget` gets 20 events from the lexical index's calls; the path-map check's pinned call wrote none).

## What should happen (the KPIs, W2-M161, gitenv's own rule)

No git call the lexical index makes reads the system's or the person's configuration where a setting there could write or change an answer: under `gov close`, `gov check`, `gov retrieve` and `gov rebuild` a person's `trace2.eventTarget` (or any other trace setting in `~/.gitconfig`, the XDG file or the system file) is never written by them. The answers stay the same: the freshness key, the listing and the blob ids the index records are what they are now for an ordinary project. An inherited `GIT_INDEX_FILE` of the root's own git directory is still kept (as `git_env(root)` keeps it).

## What to do

1. **Fix:** the lexical index's git calls that only read run pinned (`git_env(root, pinned=True)`), as gitenv's rule says. Judge `hash-object --stdin-paths` on its merits: it also only reads (no `-w`), but its answer can depend on the repository's own attributes and filters; the repository's own configuration is still read when pinned, so say in your return whether pinning it changes any blob id for an ordinary project and why you chose as you did. Proportion (DEC-135): nothing beyond this; no change to `_checked`'s logic or W2-108's key.
2. **Builder tests** in `tests/unit/gitenv/` (written first, seen red): a throwaway repository and a person's `~/.gitconfig` (a `HOME` of the test's own) with `trace2.eventTarget` naming a file; the lexical index's freshness key, listing and a refresh of a small project write nothing to it; the answers are those of an unpinned run; an inherited `GIT_INDEX_FILE` of the root's own git directory is still used.
3. **The sweep record** row 24: what the lexical index's calls now get and why (W2-M161, W2-108's calls, R6-2). Counts stay true.

## Verify before you return (once, after your last commit)

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit/gitenv tests/unit/retrieval -q -p no:cacheprovider`. Expected: all green (one skip for a missing `govbridge` module is known).
- The acceptance case above, once, name and result only: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest "tests/acceptance/W2-05/test_w2_05_planted.py::test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment" -v --tb=no -rN -p no:cacheprovider`. Then `tests/acceptance/W2-05/test_w2_05_planted.py` whole and `tests/acceptance/W2-108/` the same way (names and results only). Expected: green.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Stage only the files you changed, by name (never `git add -A` or `git add .`: placeholder files show in this sandbox). One commit; trailers in the final block, `Implements:` holding decision ids only (DEC-927 item 2):

    git commit -m "W2-05 (DAEO-0z8c): the lexical index's read-only git calls run pinned, W2-108's freshness calls among them (W2-M161)" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-710, DEC-804, DEC-980" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Do not start the commit message's body with a row id followed by a colon (git reads such a paragraph as trailers). After the commit, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commit; which calls are now pinned and why, and your judgement on `hash-object`; each unit test and its red before the fix; every suite you ran with its counts and every red case by name; lines added and removed in `src/`, `docs/` and tests; the `gov retrieve` questions you asked; the read refusals you met; any package. Put these in the fields below.

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
