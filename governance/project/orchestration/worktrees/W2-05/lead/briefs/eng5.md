You are a fresh engineer. Ticket: DAEO-0z8c (W2-05, "The git environment of every check, hook and helper; the settings re-sort"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-05` on branch `w2/W2-05`. The ticket was implemented in earlier runs; batch 1 of this resume is commit `8b8a3baa347a`; the branch has since merged `w2/integrate` (head `04bd5e11b01b`). This is **batch 2 of 2**. You build to the specification and its KPIs (the behaviours below, the ticket's KPI lines, the decisions), never to the tests (DEC-957). At the same time an independent test designer revises W1-02's deadline cases in a separate tests worktree; you merge its commit once when the lead says it is ready (below).

## Step 0, before any work: the sandbox check (owner, DEC-789)

You were started through `gov launch`, sandboxed. Before anything else, run these and report their exact output first in your return (in `evidence`, and say in `status` whether the check passed):

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"`: a write outside your worktree. It **must fail**. If it wrote the file, do not delete it: stop there and return, naming the file.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and then `git update-index --refresh`: git's own writes. They **must work**. If either fails, stop there and return with the exact error (you could not commit).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0z8c`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-05` and `w2/W2-05`), `git log --oneline -1` (expect `04bd5e11 Merge w2/integrate into w2/W2-05: DEC-959, before its resume`) and `git status --short` (expect no line but the sandbox's placeholder device files at the worktree root: names such as `.bashrc`, `.gitconfig`, `.mcp.json`, `.idea`, `.vscode`, each a character device `1, 3`; they exist only inside the sandbox and are never staged). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. **This rule goes into every worker brief you write, word for word.** Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **What you may not read (DEC-820 (c) and (d), DEC-957).** (c) Never read any acceptance-test code: nothing under `tests/acceptance/W2-05/` or `tests/acceptance/W1-02/`, by any tool (no Read, cat, grep, diff, `git show` or `git log -p` of them), and nothing in the tests worktree `/home/usain/gov-os-worktrees/W2-05-tests`. You may run the acceptance tests and see only which pass and which fail (the run forms below show names and results, no failure text). You work from the specification, the KPIs, the behaviours stated here and the existing code; your test-driven development is your own unit tests. (d) Never read the hidden half of any evaluation set.
- **Memory first (DEC-836, DEC-859, DEC-860).** Use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main retrieve "<question>" --json`. A large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget, never one giant query or context. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return which questions you asked. **The retrieval index also holds acceptance tests, which you may not read:** ask through the lead's wrapper, which drops every answer item that names `tests/acceptance/W2-05` before printing (it prints only how many it withheld): `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src timeout 300 python3 /home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/retrieve_safe.py "<question>" [--batch-size N] [--continue <token>]`; drop unread any item it prints that names `tests/acceptance/W1-02`. Never run `gov retrieve` bare. In the sandbox the semantic facet may be unavailable (no embedder) and a call can hang: the `timeout` caps it; the lexical facet still answers. This worktree's store dates from before the last merges: check what it serves against the file itself.
- **Untracked files you must leave alone:** if `tests/acceptance/W2-05/test_zz_scratch_b1.py` is still there (an earlier test designer's scratch file; a test designer deals with it), do not read, stage or touch it.
- **Read refusals (DEC-849).** Until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal; never look for another form; search named folders instead (`src/gov/...`). Count the refusals you met and give the count in your return.
- **The guard has five rules now (ACT 1, DEC-953 item 2, DEC-954):** the implementer never writes acceptance tests; reviewers and auditors write only their own records; no reads of the hidden half of an evaluation set or of the held-out material; no reads of secrets; no installs without the owner. Shell command forms are no longer refused; still, put anything long in a script file written with the Write tool under your temporary folder. Report every refusal you meet (its time, the command's form in one line, the reason it gave, and whether it was one of the five rules or a false positive).
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. **Commit your work before you run any long suite.** A foreground command is killed after 10 minutes: keep each run within that (for a large suite run one file or a few files at a time).
- **Write only inside the ticket's allowed paths** (`src/gov/**/*.py`, limited to calls that start git or a program that starts git; `src/gov/util/gitenv.py`; `tests/unit/gitenv/**`; `docs/research/AR-2-git-sweep.md`), and **never** in the files other tickets hold (next rule). Never touch `tests/acceptance/**` (read-only to you, unread; a test you think wrong is returned as a package) or `.gov-runtime/**`.
- **Files other tickets hold: never change them.** List their git calls in the sweep record, each marked "after <ticket> merges" (DEC-777):
  - `src/gov/guard/reads.py` (W2-84);
  - `src/gov/secrets/__init__.py` and `src/gov/secrets/cache.py` (W2-107; `secrets/__init__.py` starts `gitleaks stdin`, which starts no git: list it as before);
  - `src/gov/rebuild/**` (W2-76), `src/gov/retrieval/**` (W2-87; `measure.py` also W2-61);
  - `src/gov/launch/launcher.py`, `role.py`, `record.py` (W2-60a), the rest of `src/gov/launch/**` and `src/gov/codeintel/**` (W2-56), `src/gov/launch/gate*` and `src/gov/resources/**` (W2-20);
  - `src/gov/impact/**` (W2-37); `src/gov/release/**` and `src/gov/lock/**` (W2-16).
  - If the work cannot be done without one of them, stop and return a package naming the file.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no push, no tag in this worktree. The one merge you make is the tests merge below, `--no-ff`.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- **Protected material (DEC-820).** Never read, print, search, diff or copy the held-out material under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never print a secret. **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- **The git hooks stay uninstalled until W2-08.** Nobody runs `lefthook install` or `lefthook uninstall` in this repository or any of its worktrees. Never run `gov rebuild` in this worktree (the lead does; never `--no-embeddings` anywhere), and never `gov close`, `gov adopt`, `gov pause` or `gov checkpoint`.
- Inside a launched session `.gov-runtime/freeze` and some dotfiles show as placeholder device files: conclude nothing from them, and never add them to a commit.
- No subagents. Install nothing: an install you need is raised as a P1 escalation in your return (DEC-957).
- Never make a guard or gate decision fail open: each failure KPI must still refuse (DEC-580). Proportion rule (DEC-135): no code for edge cases beyond the KPIs and the behaviours below.
- **Disk and files (DEC-898).** Your share of the ticket's budget is 3 GB and 150,000 files and folders outside the tracked tree. Your temporary folder is the one `gov launch`'s sandbox set: keep it (do not set `TMPDIR` yourself). Keep pytest's own temp retention (never `--basetemp`). Remove any folder you made outside pytest as soon as you no longer need it. Measure `du -sh` and `du -s --inodes` of your temporary folder at the end and give the figures in `evidence`.
- **Row W2-L423's rule (DEC-911).** In anything you write, give commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- Nobody asks or notifies the owner (no question box, no `owner-ping`): a question comes back to the lead as a package in your return. On an authentication or access error (401, 403, "Failed to authenticate"), stop and return with status `AUTH_REQUIRED`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0z8c.md` (read-only): its KPI lines and allowed paths; the W2-05 card in `docs/plan/WAVE_2_WBS.md` §2; rows W2-M161 and W2-L160 in `docs/plan/WAVE_2_LIST.md`.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-710, DEC-135, DEC-580, DEC-777, DEC-783 (item 2), DEC-802, DEC-804 (items 1 and 3), DEC-805, DEC-807, DEC-822 (item 3), DEC-951.
- The sweep record `docs/research/AR-2-git-sweep.md` (the helper's rules, P-1, the rows).
- The helper as batch 1 left it, `src/gov/util/gitenv.py` (read it first), and the code you touch.

## What to do (batch 2)

Batch 1 (commit `8b8a3baa347a`) made the declared check's environment follow P-1 (`program_env` in the helper), gave the guard's freeze look-up in `src/gov/guard/decide.py` git by absolute path from the system folders, the pinned environment and its own 15 s limit, and added the hooks comparison to adapter-portability. Two W2-05 acceptance cases are left for this batch: `test_gov_close_runs_its_subprocesses_and_the_ticket_tests_with_a_sanitised_environment` and `test_every_file_of_the_source_that_starts_git_is_named_in_the_sweep`. The rule for every call is the helper's, as batch 1 left it. **P-1 (DEC-804 item 3):** an inherited `GIT_INDEX_FILE` is honoured only for git calls in the project root; a program that may start git elsewhere gets no index.

1. **The close's calls, rows 32 to 36 and 38 of the sweep (W2-M161; W2-53 has merged and closed, so they are this ticket's, DEC-777 item 2).** "All subprocesses of close run with a sanitised environment and pinned git configuration" (W2-M161), through the one helper:
   - `src/gov/close/repo.py` `git` (every git call of the close through `gov.close.repo`, `gov.close.history` and `gov.close.batch` included): the helper's environment for the root. **Pin the configuration where the call only reads.** The close also commits through this function (`gov.close.batch._commit`, `gov.close.history`'s `commit-tree` with its own `-c user.name`), and it decides whose identity a commit carries by asking `git config user.email`, which today reads the person's `~/.gitconfig`: **who authors the close's commits must not change.** Choose a form that keeps that (for example, unpinned for that function, pinned for the reads elsewhere, or the identity carried explicitly), and say which in the sweep row.
   - `src/gov/close/traceability.py` `_read_trailers` and `_commits_for_ticket`: the helper's environment, pinned (they only read).
   - `src/gov/close/command.py` `_started` (row 36: the ticket's acceptance tests, the parallel-runner probe and the timeout-plugin probe) and `src/gov/close/gates.py` (its collection run through `_started`; add it to the sweep if it is not there): the test run starts git elsewhere (in the tests' temporary repositories), so under P-1 it gets **no** `GIT_*` variable of the caller, no index, no trace variable, while keeping everything else the close puts in its environment today (its `PYTHONPATH`, the plugin variables, the check result). The planted `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_TRACE`, `GIT_TRACE2`, `GIT_TRACE2_EVENT`, `GIT_TRACE_PACKET` and `GIT_TRACE_SETUP` must reach no test run of `gov close`. Changing `_started` itself is fine.
   - `src/gov/close/tool.py` `tk` (the ticket tool, which runs `git config user.name`): the helper's environment for the root with `TICKETS_DIR`, as `src/gov/tasks/tickets.py` row 30 already does.
   - **`src/gov/close/nightly.py` (W2-77 has merged; its calls are this batch's now):** route its git calls (`bisect start/run/reset`, `worktree remove`, `worktree prune`) and its test run through `_started` by the same rules. **Change only each call's environment;** arguments, paths and order stay as W2-77 left them.
   - Any other git call under `src/gov/close/` (`select.py`, `fingerprint.py`, `batch.py`, ...): read it against the same rules, and record it.
2. **Rows 39 to 41, now this batch's (W2-03 has merged):** `src/gov/decisions/checker.py` (`_git` and the `cat-file --batch` process of its batch reader) and `src/gov/store/loader.py` (`_git`, the record store, in the project root or the check's temporary clone): the helper's environment, pinned where the call only reads. **Change only each call's environment;** arguments, paths and order stay as W2-03 left them. Today `checker.py` clears every `GIT_*` by hand: keep what that clearing protects.
3. **`src/gov/cli/main.py` `_version`** (`git -C <tree> rev-parse --show-toplevel HEAD`, run with the whole environment): the helper's environment for that tree, pinned (it only reads).
4. **Containment's `git` by absolute path (P-B1-2, a row riding along, DEC-802):** `src/gov/guard/containment.py` (and `containment_merge.py`, if it starts git) runs the `git` first on `PATH` today. Give it git by the same absolute path the guard's freeze look-up uses (batch 1, `decide.py`): one resolver, in one place (the helper is the natural one; if you move batch 1's into it, `decide.py`'s look-up must keep exactly its behaviour: the system folders, the pinned environment, 15 s, refuse when no git is found or the limit passes, never allow). If no git can be resolved, containment must not pass the change on that account (fail closed, DEC-580). Keep containment's environment as it is.
5. **Every program start of the files already in the sweep, read against P-1:** for each row that starts a program other than `git -C <root> …` (row 9 the declared check, done in batch 1; row 13 gitleaks, which runs `git diff --staged` in the root and **must keep git's own index**, unchanged; row 30 `tk`; rows 43 to 45 the code-index tool, which W2-56 holds: record only), decide whether it may start git outside the project root. If it may, it gets no index (the helper's `program_env`); if it starts git only in the root, it stays as it is. Change only what P-1 requires, and say in each row which it is.
6. **The sweep record `docs/research/AR-2-git-sweep.md`, re-run on this tree** (`src/gov/**/*.py`, every call that starts git or a program that starts git, `subprocess` calls through other names included):
   - add a row for every new call (`close/gates.py`, `close/nightly.py`, `cli/main.py`, `guard/reads.py`, `guard/containment_merge.py` if it starts git, and any new call in a file already listed); correct every row this batch changed (rows 32 to 36, 38, 39 to 41, containment's) and the rows batch 1 changed (row 42: git by absolute path, pinned environment, 15 s limit, refuse on time-out or no git; row 9 as batch 1 built it);
   - every call in a file another ticket holds (the list above) is listed, marked "after <ticket> merges";
   - the helper's section states P-1 as accepted (DEC-804 item 3) and the forms the helper now has; "Not settled here" loses what is now settled (W2-L160, W2-M161) and keeps what is not (F-B and D-1 are Wave 3 rows W2-M375 and W2-M376, DEC-807);
   - the counts at the end are true;
   - the record is written in the house style it has (short sentences, tables), with commit hashes as 12 digits.
7. **Builder tests** in `tests/unit/gitenv/` for anything you add to the helper (the resolver among them), as regression evidence only; write them first (test-driven development is your own unit tests).

## The tests merge (DEC-963)

The test designer's W1-02 revision is made in the branch `w2/W2-05-tests`. **At each step boundary, and before your final runs,** check whether the file `/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/TESTS-READY` exists (read it: it names the commit). When it does, and only once:

- commit what you have first (never merge over uncommitted work);
- check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file;
- `git merge --no-ff w2/W2-05-tests -m "Merge w2/W2-05-tests into w2/W2-05: the W1-02 revision (DEC-951)" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-951"` (if your git does not take `--trailer` on a merge, put the three trailer lines in the message's final block instead). The paths are disjoint from yours, so it must be clean; if it is not, `git merge --abort` and return a package. Read none of the merged files.

If it does not exist when you are ready to return, do not wait for it: say so.

## Verify before you return (once, after your last commit)

- Your own unit tests and the unit suites of the packages you change, to the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit/gitenv -q -p no:cacheprovider`, and `tests/unit/close`, `tests/unit/guard`, `tests/unit/decisions`, `tests/unit/store`, `tests/unit/cli` where they exist (file by file if long).
- The acceptance tests, once, names and results only, never with `-x`:

      PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/acceptance/W2-05 -v --tb=no -rN -p no:cacheprovider

  and the same for `tests/acceptance/W1-02` once the tests merge is in (a few files per run if needed). Expected in the sandbox: every W2-05 case passes except those that fail inside a launched session for a reason not their own: the five retrieval-regression cases (the sandbox reaches no embedder) and `test_the_code_index_tool_started_by_gov_rebuild_gets_no_inherited_git_variable` (the code index's daemon folder under `/tmp/gov-cbm-<uid>` is read-only in the sandbox). The lead runs those outside. Report every case's state.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, do not commit, and say so. Never `--no-verify`, never `core.hooksPath`. Stage only the files you changed, by name (never `git add -A` or `git add .`: placeholder files show in this sandbox). One commit per step is fine; trailers in the final block, `Implements:` holding decision ids only (DEC-927 item 2):

    git commit -m "W2-05 (DAEO-0z8c): <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-804, DEC-777, DEC-802, DEC-580, DEC-710, DEC-951" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

After each commit, run `git log --oneline -2`, `git log -1 --format=%B` and `git status --short` and quote them.

## Return

Your commits; what each change does (the interface as built, in a line or two each, and for each close call the form you chose); every suite you ran with its counts and every red case by name; lines added and removed in `src/` and in `docs/`, and in tests; the `gov retrieve` questions you asked; the read refusals you met; any package. Put these in the fields below.

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
