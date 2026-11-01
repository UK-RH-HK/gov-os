# Brief: engineer, W2-96 (DAEO-ouet), run 1, review 1's test run

You are a fresh engineer. Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`. You build the code to the specification and its KPIs, never to the tests (DEC-957); your test-driven development is your own unit tests.

**Where things stand.** `gov accept` is built (`9859695c8fcc`) and review 1's addendum below is built on it (`d8ac34ff71de`: `src/gov/accept/runner.py`, `tests/unit/accept/test_w2_96_accept.py`; 41 unit tests pass). The independent test designer's cases, review 1's included, are merged on this branch (`382ef3b6`: 79 cases). The R4 rule is read literally: in a map table with a KPI column, any body row with a backticked item in its Test/File cell whose KPI cell begins with no line name the reader takes refuses the run (`ACCEPT_MAP_UNREADABLE`), and that refusal wins over `ACCEPT_NO_MAP`. Your job: run the acceptance tests once and fix the code to the specification where they fail. You may read and change the earlier engineers' code: it is this ticket's own.

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
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random. This worktree has no store yet (its rebuild waits for the shared lock and runs after you), so retrieve from the integration branch's store, which holds this branch's base: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 90 gov retrieve "<question>" --json` (a read). Do not run `gov rebuild` yourself. Known: inside the sandbox that call can hang on the embedder's network call (the first engineer and the test designer both met it); try it once, and if it times out, say so and search named folders under `src/gov/` instead. Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). Drop unread any result under `tests/acceptance/W2-96/`.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); a test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/eng/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
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

## Review 1's addendum to the design note (behaviour only; it overrides the note where they differ)

- **R1 (no per-run base folder).** The runner never gives pytest a base folder of its own on the command line. The child's `TMPDIR` is a folder inside the private folder, so pytest's own default base folder, and every test's temporary folder, falls inside it and is removed with it. A project whose `conftest.py` refuses a run given a per-run base folder (as this repository's `tests/conftest.py` does) runs normally and is reported per line.
- **R2 (SIGTERM and SIGHUP).** A SIGTERM or SIGHUP sent to `gov accept` alone, during a run, ends it as an interrupt does: the child and everything it started are stopped, and the private folder is removed, before `gov` exits. Nothing of the run (no report, no test's temporary file) stays in the `TMPDIR` the caller gave, and nothing of the tests' content is printed; `gov` ends with exit code 128 plus the signal's number.
- **R3 (folders without permissions).** The private folder is removed even when a test left a folder or a file in it without read, write or execute permission, after a failure and after a timeout's kill alike: nothing stays in the caller's `TMPDIR`.
- **R4 (an unreadable map row refuses).** In a map table with a KPI column, a body row whose Test/File cell holds at least one backticked item while its KPI cell begins with no line name the reader takes (for example `Failure: …` with no number, `Success 3a`, `S8b`) makes the whole run refused before any test runs: `ACCEPT_MAP_UNREADABLE`, exit 1, `ok: false`, the refusal naming only the ticket and its declared path, never the row. The same holds for a Test/File table with no KPI column whose nearest heading begins with the word `success`, `failure` or `KPI` (any case) but names no line the reader takes. A table under any other heading still maps nothing, as before.
- **R5 (items).** An item holding `::` whose part before the `::` is empty or does not end in `.py` (`::test_x`, `every_form::test_x`) means every test of the folder whose function name is the part after the last `::`. An item that names a test — it holds `::`, or it begins with `test_` (a file `test_….py` included) — and matches no collected case makes its line fail (counted only; never named).
- **R6 (no log file).** No log file is written, whatever the project's pytest configuration says (`log_file`).
- **R7 (an exit that contradicts the report).** pytest ending with its "tests failed" exit code while the report holds no failed or errored case is a `crash`.
- **Unchanged (KPI 3 and 5):** a test the README never names is counted under `unmapped`, and unmapped cases never change the exit code. Whether they should is a question for the orchestrator (package), not for this round.

Points that make this fail closed, never open: any unexpected exception inside the runner (a file it cannot read, a README it cannot decode, XML it cannot parse) is caught and reported as `crash` with no message — an uncaught Python traceback or an `OSError`'s file name would leak a path from the acceptance folder; nothing is ever printed from the child; a line with no test fails.

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/accept/**` (a package: `__init__.py`, `command.py` as the convention says, and any helper module you need there) and `tests/unit/accept/test_w2_96*.py` (your builder tests; no `__init__.py` there, it is outside your paths: give every file a unique basename starting `test_w2_96_`).
- **Do not touch `src/gov/cli/main.py` or `src/gov/check/commands.py`.** Adding the command turns W1-07's, W1-26's and W1-32's command-list cases red (the command set recorded in `RECORDED_GOV_COMMANDS`); that record is outside your paths and the lead returns it as a package (DEC-747). Do not try to make those cases green.
- Never `tests/acceptance/**` (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): no code for edge cases beyond the KPIs and the design note; about 250 lines expected. Never make a refusal fail open.
- Unit tests first (TDD), run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, to the end, never `-x`. They plant tiny projects in temporary folders; never run anything against this worktree's own acceptance folders.
- **Commit each fix before the next run.** Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Trailers in the final block:

      git commit -m "W2-96 (DAEO-ouet): gov accept, the opaque acceptance runner" --trailer "Task: DAEO-ouet" --trailer "Role: engineer" --trailer "Implements: DEC-959, DEC-317" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  `Implements:` holds only ids the register holds (DEC-927). After every commit: `git log --oneline -2` and `git status --short`.

## The acceptance tests (already merged)

The independent test designer's tests are in `tests/acceptance/W2-96/` on this branch (merged by the lead in `986fa7cf`). You never open them (DEC-820 (c)).

1. Run them **through pytest this once** (gov accept is what is being built, so it cannot be the judge of its own first run), reading results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. You see names, pass or fail and the one-line failure messages; you never open the test files. The suite takes about two minutes.
2. If some fail: fix the code to the specification and the design note (never to a test's text), add a unit test for the behaviour, commit, and run them again; at most three runs in all. A failure you believe the specification does not ask for is a package, with the test's name and its one-line message, and you leave that behaviour as the specification says.
3. Then run `gov accept` on this ticket once and quote its JSON: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -m gov.cli.main accept DAEO-ouet --json` (it must run in this repository and report per line).
4. Run your unit tests again (`tests/unit/accept`) and return. Commit each fix with the trailers above (`--trailer "Implements: DEC-959, DEC-317"`).

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
