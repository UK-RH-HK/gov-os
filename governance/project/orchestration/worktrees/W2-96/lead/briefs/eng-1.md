# Brief: engineer, W2-96 (DAEO-ouet), run 1

You are a fresh engineer. Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`. You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96` and `w2/W2-96`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag. The one merge you make is the one below.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). Show it once with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"` and quote the line.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's acceptance tests: you never read `tests/acceptance/W2-96/`** (here, in `/home/usain/gov-os-worktrees/W2-96-tests`, or on branch `w2/W2-96-tests`), by any tool — no `cat`, `Read`, `Grep`, `git show`, `git diff` of it; you may run them and see their names, results and failure messages; (d) the hidden half of any evaluation set.
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet (its rebuild waits for the shared lock and runs after you), so retrieve from the integration branch's store, which holds this branch's base: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Do not run `gov rebuild` yourself. Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). Drop unread any result under `tests/acceptance/W2-96/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); a test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/eng/` and run it. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure at the end (`du -sh`, `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md` (read-only): its KPI lines and its `allowed_paths`.
- The sources in `docs/DECISION_REGISTER.md`: DEC-959 (items 6 and 7), DEC-957 (the work order), DEC-820 (c), DEC-317, MR-3; `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §2.7.
- The command-module convention: `src/gov/cli/main.py`'s docstring (where a module goes, `run`, `add_arguments`, `CLASS`, `HELP`, `EXIT_CODES`, the tuple return, `GovError` with `exit_code`), and an existing module such as `src/gov/launch/command.py`; `src/gov/cli/errors.py`; the ticket front matter (`.tickets/*.md`) and the existing ticket readers you can reuse (find them with `gov retrieve` or the code graph).

## The behaviour to build (the KPIs, and the lead's design note)

The KPI lines are in the ticket. The design note, fixed by the lead for you and the test designer alike:

> **What it is.** A read command, `gov accept <ticket> [--timeout <seconds>] [--json] [--root <path>]`. `<ticket>` is a ticket id (the file `.tickets/<id>.md` under the project root) or that ticket's WBS id (its `wbs_id` field). It runs the folder named by the ticket's `acceptance_tests.path` with the project's own `src/` first on the import path, and reports per KPI line of the folder's `README.md` map: pass or fail, with counts. Nothing else.
>
> **1. The README's KPI map (the form designers' READMEs use today).** *Row form:* a Markdown table whose header row has a column whose title begins with `KPI` (any case) and a column whose title begins with `Test` or `File`. Each body row maps the backticked items of its Test/File cell to the KPI line(s) named at the start of its KPI cell. *Heading form:* a table with a Test/File column and no KPI column, under the nearest heading (any level) whose text begins with KPI line names (`### KPI 1: …`, `### K2 — …`, `### Success 3 …`), maps its items to those lines; a table under a heading that names no line maps nothing. *KPI line names,* at the start of a cell or heading, several joined by `/`, `,`, `;` or `and`, any case: `success N`, `S N`/`SN`, `KPI N`, `K N`/`KN` (all three mean success line N) and `failure N`, `F N`/`FN`; reported only in the normal form `success-N` / `failure-N`, never as the README's text. *Items:* each backticked item in the Test/File cell: `name.py` (or a path ending in it) means every test in that file; `name.py::test_x` that one test; a bare word means every test whose function name (before any `[`) is that word or `test_` plus that word. Anything else in the cell, and text outside the map, is ignored. No README, or a README with no map (no row maps a line): refused, `ACCEPT_NO_MAP`. No raw fallback, ever.
>
> **2. The child run, and how its results are read without its text.** pytest runs in a child process (`python -m pytest <folder>` with the project root as working folder, `PYTHONPATH=<root>/src`, its own `--basetemp` and a JUnit XML file both inside one private temporary folder outside the repository, the cache plugin off, no bytecode written, `PYTEST_ADDOPTS` and similar caller settings dropped, stdin closed). Its stdout and stderr go to the null device, never captured. The JUnit file (xunit1, so each case has its `file`; captured output not logged into it) is read only for each case's file, function name and outcome: no `failure`, `error` or `skipped` element's message or text, no `system-out`/`system-err`, is ever read. Each case is then mapped to the KPI lines whose items match it; a case no item matches is `unmapped`.
>
> **3. Temporary files.** One private temporary folder (under `TMPDIR`), holding the JUnit file and the basetemp, removed in every path (pass, fail, error, timeout, an exception of the runner's own, Ctrl-C). Nothing written in the repository: no `.pytest_cache`, no `__pycache__` from the child, no report file.
>
> **4. Outcomes.** A case passes when it has no failure or error element; `skipped` is counted apart; an error (setup/teardown) or a failure counts as failed. A KPI line passes when at least one case maps to it, none failed, and at least one passed. A line with no matching case fails (nothing proves it). Run errors, reported as `error` for the run with their kind only, and no line reported pass or fail: `collection` (pytest exit 2 or 5, or any collection error in the JUnit file), `timeout` (the child passed `--timeout`, default 1800 s; its whole process group is killed), `crash` (pytest exit 3 or 4, killed by a signal, the JUnit file missing or unreadable, or any unexpected exception in the runner itself). Never a message, a traceback or a path inside the folder.
>
> **5. Exit codes.** 0: every mapped line passes. 3 (declared): a mapped line fails. 4 (declared): the run errored. 1: refused (`ACCEPT_NO_MAP`, `ACCEPT_UNKNOWN_TICKET`, `ACCEPT_NO_TESTS` for a ticket with no acceptance path or a path that is not a folder inside the root); the refusal names only the ticket and the ticket's declared path. Unmapped cases never change the exit code.
>
> **6. The JSON** (`result` of the API-0002 envelope `{ok, command, result, error?, session}`; `ok: true` for pass, fail and error, `ok: false` only for a refusal): `{"ticket": "DAEO-xxxx", "outcome": "pass"|"fail"|"error", "error_kind": null|"collection"|"timeout"|"crash", "lines": [{"kpi": "success-1", "outcome": "pass"|"fail", "passed": 2, "failed": 0, "skipped": 0}, …], "unmapped": {"passed": 1, "failed": 1, "skipped": 0}, "totals": {"passed": 3, "failed": 1, "skipped": 0}}`. Lines in order `success-1…`, then `failure-1…`. On `error`, `lines` is `[]` and the counts are 0. Without `--json` the same `result` is printed as text. No test name, file name, parameter id, message or README text appears anywhere in the output, the envelope, an error, stderr or a file left behind.

Points that make this fail closed, never open: any unexpected exception inside the runner (a file it cannot read, a README it cannot decode, XML it cannot parse) is caught and reported as `crash` with no message — an uncaught Python traceback or an `OSError`'s file name would leak a path from the acceptance folder; nothing is ever printed from the child; a line with no test fails.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/accept/**` (a package: `__init__.py`, `command.py` as the convention says, and any helper module you need there) and `tests/unit/accept/test_w2_96*.py` (your builder tests; no `__init__.py` there, it is outside your paths: give every file a unique basename starting `test_w2_96_`).
- **Do not touch `src/gov/cli/main.py` or `src/gov/check/commands.py`.** Adding the command turns W1-07's, W1-26's and W1-32's command-list cases red (the command set recorded in `RECORDED_GOV_COMMANDS`); that record is outside your paths and the lead returns it as a package (DEC-747). Do not try to make those cases green.
- Never `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): no code for edge cases beyond the KPIs and the design note; about 250 lines expected. Never make a refusal fail open.
- Unit tests first (TDD), run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end, never `-x`. They plant tiny projects in temporary folders; never run anything against this worktree's own acceptance folders.
- **Commit your work before any longer run.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block:

      git commit -m "W2-96 (DAEO-ouet): gov accept, the opaque acceptance runner" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-959, DEC-317" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only ids the register holds (DEC-927). After every commit: `git log --oneline -2` and `git status --short`.

## The acceptance tests, once ready (DEC-959 item 7)

The independent test designer writes `tests/acceptance/W2-96/` in parallel, on branch `w2/W2-96-tests`. When its tests are committed, the lead writes the file `/home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/TESTS-READY` naming the commit.

1. When you have built and committed, look for that file. If it is not there yet, wait for it with short foreground checks (`until [ -s /home/usain/gov-os-worktrees/W2-96/.gov-runtime/scratch/lead/TESTS-READY ]; do sleep 30; done` with a limit of nine minutes per call; repeat), for at most 60 minutes in all; if it never comes, return DONE for the build and say so.
2. When it is there: `git merge --no-ff --no-commit w2/W2-96-tests`, then `git commit -m "Merge w2/W2-96-tests: the acceptance tests" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. The paths are disjoint, so the merge is clean; if it is not, abort it (`git merge --abort`) and return.
3. Run them **through pytest this once** (gov accept is what you are building, so it cannot be the judge of its own first run), reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. You see names, pass or fail and the one-line failure messages; you never open the test files.
4. If some fail: fix the code to the specification and the design note (never to a test's text), commit, and run them again; at most three runs in all. A failure you believe the specification does not ask for is a package, with the test's name and its one-line message. Then run your unit tests again and return.

## Return

Your last message, complete in itself. Refused twice for the same call: stop and say so. The twelve fields come first, each as a labelled line, any payload after them:

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

In `evidence` also: the sandbox check, your commits' 12-digit hashes, the `gov.__file__` line, the lines added and removed, whether you used `gov retrieve`, the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
