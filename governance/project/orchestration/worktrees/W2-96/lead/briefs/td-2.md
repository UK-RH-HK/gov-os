# Brief: independent test designer, W2-96 (DAEO-ouet), run 1, review 1's batch

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests`. You add review 1's cases to the ticket's acceptance tests, from the reviewer's findings given below as described behaviours (DEC-136), and you show them red.

**Where things stand.** A first test designer wrote the suite (`73e50896445c` on this branch: 54 cases, marker `qzv96leak`, README map in the design note's form). The engineer's implementation exists on `w2/W2-96`; you still never read it (Policy 2 (c) below). An independent reviewer probed it and found behaviour the suite misses; the lead turned the findings into the addendum below.

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
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 90 gov retrieve "<question>" --json` (a read; it holds `w2/integrate` as of its last refresh). Known: inside the sandbox that call can hang on its embedder's network call; try it once, and if it times out, say so and read named files instead. Never retrieve from `/home/usain/gov-os-worktrees/W2-96`'s store. **Drop unread any result under `src/gov/accept/` or `tests/unit/accept/`, and name any such result you were served in your return (P-R1, DEC-820 (c)).** Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/td/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository (the sandbox leaves a `.claude/` folder there): use paths from the worktree's top. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your own suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure it at the end (`du -sh` and `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- Your suite as it stands: `tests/acceptance/W2-96/` on this branch (its README, support module and cases).
- The ticket file `.tickets/DAEO-ouet.md` (read-only) and the sources named in it; the first brief's design note is repeated below.
- For R1, how this repository's `tests/conftest.py` refuses a per-run base folder (read it, `git show w2/integrate:tests/conftest.py`).

## The behaviour to test

The design note (unchanged, the interface both you and the engineer build to):

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

## Review 1's addendum to the design note (behaviour only; it overrides the note where they differ)

- **R1 (no per-run base folder).** The runner never gives pytest a base folder of its own on the command line. The child's `TMPDIR` is a folder inside the private folder, so pytest's own default base folder, and every test's temporary folder, falls inside it and is removed with it. A project whose `conftest.py` refuses a run given a per-run base folder (as this repository's `tests/conftest.py` does) runs normally and is reported per line.
- **R2 (SIGTERM and SIGHUP).** A SIGTERM or SIGHUP sent to `gov accept` alone, during a run, ends it as an interrupt does: the child and everything it started are stopped, and the private folder is removed, before `gov` exits. Nothing of the run (no report, no test's temporary file) stays in the `TMPDIR` the caller gave, and nothing of the tests' content is printed; `gov` ends with exit code 128 plus the signal's number.
- **R3 (folders without permissions).** The private folder is removed even when a test left a folder or a file in it without read, write or execute permission, after a failure and after a timeout's kill alike: nothing stays in the caller's `TMPDIR`.
- **R4 (an unreadable map row refuses).** In a map table with a KPI column, a body row whose Test/File cell holds at least one backticked item while its KPI cell begins with no line name the reader takes (for example `Failure: …` with no number, `Success 3a`, `S8b`) makes the whole run refused before any test runs: `ACCEPT_MAP_UNREADABLE`, exit 1, `ok: false`, the refusal naming only the ticket and its declared path, never the row. The same holds for a Test/File table with no KPI column whose nearest heading begins with the word `success`, `failure` or `KPI` (any case) but names no line the reader takes. A table under any other heading still maps nothing, as before.
- **R5 (items).** An item holding `::` whose part before the `::` is empty or does not end in `.py` (`::test_x`, `every_form::test_x`) means every test of the folder whose function name is the part after the last `::`. An item that names a test — it holds `::`, or it begins with `test_` (a file `test_….py` included) — and matches no collected case makes its line fail (counted only; never named).
- **R6 (no log file).** No log file is written, whatever the project's pytest configuration says (`log_file`).
- **R7 (an exit that contradicts the report).** pytest ending with its "tests failed" exit code while the report holds no failed or errored case is a `crash`.
- **Unchanged (KPI 3 and 5):** a test the README never names is counted under `unmapped`, and unmapped cases never change the exit code. Whether they should is a question for the orchestrator (package), not for this round.


## What you write

- Only inside `tests/acceptance/W2-96/`: a new case file for review 1 (say `test_w2_96_at_review_1.py`, a name no unit file can share) and its rows in the README's map (in the map form, so `gov accept` can still run the folder), plus support code where needed. A case of the first batch that the addendum changes is revised with its reason; say which in your return. Do not touch any other ticket's tests.
- One case or a small group per point R1 to R7, each with the marker leak checks the suite already makes (stdout, stderr, the JSON, the given `TMPDIR`, the project tree) where they apply:
  - R1: a planted project whose `conftest.py` refuses a run given a per-run base folder; `gov accept` reports per line (a passing line passes, a failing line fails), the given `TMPDIR` ends empty.
  - R2: SIGTERM, and separately SIGHUP, to the `gov` process alone while a planted test is running (wait until the planted test has recorded that it started); `gov` ends with exit code 128 plus the signal's number; the planted child is gone afterwards (it records nothing after the signal, or its process no longer exists); the given `TMPDIR` holds nothing; no marker in the output.
  - R3: a failing planted test that leaves a folder without permissions in its temporary folder; and a timeout while a planted test holds such a folder; in both the given `TMPDIR` ends empty.
  - R4: a row-form row naming a failing test with an unreadable KPI cell (`Failure: …` with no number; `Success 3a`); a heading-form table under `### Failure: …` with no number: each refused with `ACCEPT_MAP_UNREADABLE`, exit 1, `ok: false`, no test run (a planted test records whether it ran), no marker anywhere.
  - R5: `::test_x` and `stem::test_x` items map their tests (a failing one fails its line); a `test_` item and a `file::test_x` item that match no collected test make their line fail; a line whose items all match and pass still passes.
  - R6: a planted project whose pytest configuration names a `log_file` inside the project: no file is written, the marker logged by a test appears nowhere.
  - R7: a planted test that ends the session early by pytest's own exit call with the "tests failed" code while every case so far passed: `error` with kind `crash`, exit 4.
- Keep the new cases fast (the whole suite well under five minutes), deterministic, no network.
- **Red first:** run the whole folder to the end with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (on this branch `gov accept` does not exist, so the new cases are red for that reason; the lead red-checks them against the implementation after the merge). The README states each new case's expected red reason against an implementation without the addendum.
- An ambiguous point or a dispute with the addendum is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`):

    git commit -m "W2-96 (DAEO-ouet): review 1's acceptance cases for gov accept" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-959" --trailer "Rewrite-Reason: review 1's findings F1, F2, F3, F5, F6, F7 (DEC-136)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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
