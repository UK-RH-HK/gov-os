# Brief: independent test designer, W2-96 (DAEO-ouet), run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests`. You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with the engineer (DEC-959 item 7, DEC-963), and you show them red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96-tests` and `w2/W2-96-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src` set per command (never in a session's `--settings` env). Your tests, once merged into `/home/usain/gov-os-worktrees/W2-96` and run from there, must exercise that tree's code: run `gov` as `python3 -m gov.cli.main` with the `src/` of the repository that holds the test file (found from the test file's own location), never a bare `gov` from PATH. Your README says how.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's implementation: you never read the engineer's work** — no file under `src/gov/accept/` and no `tests/unit/accept/test_w2_96*` file, in any worktree or branch (`/home/usain/gov-os-worktrees/W2-96`, `w2/W2-96`), by any tool, and nothing `git diff --name-only w2/integrate...w2/W2-96` names; (d) the hidden half of any evaluation set. You read the specification, the KPIs and the existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`).
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read; it holds `w2/integrate` as of its last refresh). Never retrieve from `/home/usain/gov-os-worktrees/W2-96`'s store. **Drop unread any result under `src/gov/accept/` or `tests/unit/accept/`, and name any such result you were served in your return (P-R1, DEC-820 (c)).** Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-96-tests/.gov-runtime/scratch/td/` and run it. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your own suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure it at the end (`du -sh` and `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- The ticket file `.tickets/DAEO-ouet.md` (read-only): its KPI lines (success 1 to 6, failure 1 to 4), its `allowed_paths` and its sources.
- The sources in `docs/DECISION_REGISTER.md`: DEC-959 (items 6 and 7), DEC-957 (the work order), DEC-820 (c), DEC-317, MR-3; and `governance/project/orchestration/packages/ROLES-RESEARCH-1.md` §2.7 (why the runner exists).
- The public interfaces the ticket works with: the `gov` command line and its API-0002 envelope and exit codes (`src/gov/cli/main.py`'s docstring, as on `w2/integrate`); the ticket file form (`.tickets/*.md` front matter, `acceptance_tests.path`); the configuration loader's tolerance of a project without configuration (`src/gov/config/loader.py`). Existing acceptance suites show how a temporary project and a `gov` run are planted (for example `tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W2-61/`).

## The behaviour to test (the KPIs, and the design note the lead fixed for both workers)

The KPI lines, success: (1) `gov accept <ticket>` runs that ticket's acceptance tests (its declared `acceptance_tests.path`) with the tree's own `src/` and reports, per KPI line of the designer's README map, pass or fail, with the counts passed and failed under each line; `--json` gives the same in the API-0002 envelope. (2) Nothing of the tests' content reaches the caller: no test source, assertion text or values, traceback, captured output, fixture or file names from the acceptance folder, in its output, its `--json`, its exit message or any file it leaves; pytest runs in a child process whose output is parsed and discarded, and the run's temporary files are removed. (3) A test the README does not map is counted under unmapped (pass and fail counts), never named; a README with no map refuses with `ACCEPT_NO_MAP`, never falls back to raw output. (4) A collection error, a timeout or a crash is reported as error for the run with its kind only (`collection`, `timeout`, `crash`), never its message. (5) Exit code 0 when every mapped line passes, a declared code when any fails, another when the run errors; a read command, it writes nothing in the repository. (6) The brief change: the orchestrator's at merge; **no test for it** (say so in the README). Failure lines: any test source, assertion text, value, traceback or captured output in the output, the JSON or a file left behind; an unmapped test named, or a README without a map answered with raw output; a run error reported as pass or fail, or with its message; a write in the repository.

The design note (the interface both you and the engineer build to, verbatim):

> **What it is.** A read command, `gov accept <ticket> [--timeout <seconds>] [--json] [--root <path>]`. `<ticket>` is a ticket id (the file `.tickets/<id>.md` under the project root) or that ticket's WBS id (its `wbs_id` field). It runs the folder named by the ticket's `acceptance_tests.path` with the project's own `src/` first on the import path, and reports per KPI line of the folder's `README.md` map: pass or fail, with counts. Nothing else.
>
> **1. The README's KPI map (the form designers' READMEs use today).** *Row form:* a Markdown table whose header row has a column whose title begins with `KPI` (any case) and a column whose title begins with `Test` or `File`. Each body row maps the backticked items of its Test/File cell to the KPI line(s) named at the start of its KPI cell. *Heading form:* a table with a Test/File column and no KPI column, under the nearest heading (any level) whose text begins with KPI line names (`### KPI 1: …`, `### K2 — …`, `### Success 3 …`), maps its items to those lines; a table under a heading that names no line maps nothing. *KPI line names,* at the start of a cell or heading, several joined by `/`, `,`, `;` or `and`, any case: `success N`, `S N`/`SN`, `KPI N`, `K N`/`KN` (all three mean success line N) and `failure N`, `F N`/`FN`; reported only in the normal form `success-N` / `failure-N`, never as the README's text. *Items:* each backticked item in the Test/File cell: `name.py` (or a path ending in it) means every test in that file; `name.py::test_x` that one test; a bare word means every test whose function name (before any `[`) is that word or `test_` plus that word. Anything else in the cell, and text outside the map, is ignored. No README, or a README with no map (no row maps a line): refused, `ACCEPT_NO_MAP`. No raw fallback, ever.
>
> **2. The child run.** pytest runs in a child process with the project root as working folder and `<root>/src` on the import path; its stdout and stderr are discarded, never captured; its results are read from a machine report for each case's file, function name and outcome only (never a message, a captured output or a traceback); each case is mapped to the KPI lines whose items match it; a case no item matches is `unmapped`.
>
> **3. Temporary files.** One private temporary folder (under `TMPDIR`) for the run's report and the tests' temporary folders, removed in every path (pass, fail, error, timeout, an exception of the runner's own, an interrupt). Nothing written in the repository: no `.pytest_cache`, no `__pycache__` from the child, no report file.
>
> **4. Outcomes.** A case passes when it neither failed nor errored; skipped is counted apart; an error in setup or teardown counts as failed. A KPI line passes when at least one case maps to it, none failed, and at least one passed; a line with no matching case fails. Run errors are reported as `error` for the run with their kind only, and no line is reported pass or fail: `collection` (a collection error, or nothing collected), `timeout` (the child passed `--timeout`, default 1800 s; its whole process group is killed), `crash` (pytest's internal or usage error, the child killed by a signal, the report missing or unreadable, or any unexpected exception in the runner itself). Never a message, a traceback or a path inside the folder.
>
> **5. Exit codes.** 0: every mapped line passes. 3: a mapped line fails. 4: the run errored. 1: refused (`ACCEPT_NO_MAP`, `ACCEPT_UNKNOWN_TICKET`, `ACCEPT_NO_TESTS` for a ticket with no acceptance path or a path that is not a folder inside the root); the refusal names only the ticket and the ticket's declared path. Unmapped cases never change the exit code.
>
> **6. The JSON** (`result` of the API-0002 envelope `{ok, command, result, error?, session}`; `ok: true` for pass, fail and error, `ok: false` only for a refusal, with `error.code`):
> `{"ticket": "DAEO-xxxx", "outcome": "pass"|"fail"|"error", "error_kind": null|"collection"|"timeout"|"crash", "lines": [{"kpi": "success-1", "outcome": "pass"|"fail", "passed": 2, "failed": 0, "skipped": 0}, …], "unmapped": {"passed": 1, "failed": 1, "skipped": 0}, "totals": {"passed": 3, "failed": 1, "skipped": 0}}`. Lines in order `success-1…`, then `failure-1…`. On `error`, `lines` is `[]` and the counts are 0. Without `--json` the same `result` is printed as text. No test name, file name, parameter id, message or README text appears anywhere in the output, the envelope, an error, stderr or a file left behind.

## What you write

- Only inside `tests/acceptance/W2-96/`. Do not touch any earlier ticket's tests. Note for your return only: adding a `gov` command turns W1-07's, W1-26's and W1-32's command-list cases red; that revision is outside your paths and the lead returns it as a package (DEC-747) — do not revise them.
- **Planted tickets in a temporary repository** built from scratch per test (git init, a `.tickets/<id>.md` with `acceptance_tests.path`, a `src/` holding a small planted module the planted tests import, so a planted test passes only if the child ran with the planted tree's `src/`), an acceptance folder with its README map (both forms), and planted tests that pass, fail, error (in setup), are skipped, and are unmapped. Planted test files are written at test time from strings in your support module: **never commit a planted `test_*.py` file the real suite would collect**, and keep your folder free of a `conftest.py` of its own unless W2-66's rule on acceptance-folder conftests (DEC-880; read W2-66's README) allows it.
- **Leak probes by a marker:** every assertion message, compared value, print to stdout and stderr, warning, exception message, fixture name, parameter id, test function name and planted file name carries a recognisable marker string (yours to choose, built so it is unique). After each run, search stdout, stderr, the JSON, the error message and every file created or changed in the planted repository and under the `TMPDIR` the run was given (list before and after) for the marker: none may hold it. Unmapped tests' names must not appear; their counts must.
- Cover, thoroughly but without combinatorial expansion: every KPI line's success and failure (1 to 5); both map forms and the name forms; `ACCEPT_NO_MAP` (no README; a README with no map) with no raw output; a collection error (a planted import or syntax error whose message carries the marker), a timeout (a planted test that sleeps, with a short `--timeout`), a crash (a planted test that kills its own process); each with its kind, no message, the declared exit code, no line reported pass or fail; a mapped line with no matching test fails; the exit codes 0, 3, 4, 1 and the envelope's `ok`; `--json` and text agreeing; the temporary folder removed (the given `TMPDIR` holds nothing new after the run, pass, fail, error and timeout alike); nothing written in the planted repository (its tree, ignored files included, unchanged: no `.pytest_cache`, no `__pycache__`, no report); the WBS id form of `<ticket>`.
- Keep each case fast (a planted run is a second or two; the timeout case a few seconds); the whole suite well under five minutes. Deterministic, no network.
- **A README** mapping each KPI line to its tests and its expected red reason, **written in the map form above** (so `gov accept` can run this very folder), stating how the tests run the merged tree's code (DEC-732), the marker, and that KPI 6 has no test.
- **Red first:** run your tests to the end (never `-x`) with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`; they fail for the reason the README states (on this branch `gov accept` does not exist; premises and guards may pass and the README says which).
- An ambiguous KPI line or a dispute with the design note is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`):

    git commit -m "W2-96 (DAEO-ouet): acceptance tests for gov accept" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only ids the register holds (DEC-927). Then `git log --oneline -2` and `git status --short`.

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

In `evidence` also: the sandbox check, your commit's 12-digit hash, the test count, the red reason as you saw it, whether you used `gov retrieve` and any result under the implementation paths you were served, the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
