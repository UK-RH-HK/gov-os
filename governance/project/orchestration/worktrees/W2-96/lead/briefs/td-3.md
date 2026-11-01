# Brief: independent test designer, W2-96 (DAEO-ouet), run 2 (DEC-970)

You are a fresh independent test designer (MR-3). Ticket: `DAEO-ouet` (W2-96, the opaque acceptance runner `gov accept`), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-96-tests` on branch `w2/W2-96-tests`. You add the cases run 2's decisions need to the ticket's acceptance tests, revise the cases those decisions change, revise two older tickets' command lists, and show the new cases red.

**Where things stand.** Run 1's designers wrote the suite in `tests/acceptance/W2-96/` (79 cases, marker `qzv96leak`, README map in the forms below). The engineer's run-1 implementation is in this worktree's tree (this branch was made from the ticket's head); you still never read it (Policy 2 (c) below), but your red run executes it, which is what the red check needs. Two independent reviews probed it; the owner's delegate decided the open points (DEC-970). An engineer builds the same addendum in parallel in `/home/usain/gov-os-worktrees/W2-96`; the lead merges your branch after you return.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ouet`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-96-tests` and `w2/W2-96-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src` set **per command** (never in a session's `--settings` env). Your tests, once merged into `/home/usain/gov-os-worktrees/W2-96` and run from there, must exercise that tree's code: run `gov` as `python3 -m gov.cli.main` with the `src/` of the repository that holds the test file (found from the test file's own location), never a bare `gov` from PATH. The suite's support module already does this; keep it so.
- **Policy 2 (DEC-820):** reads are open, writes are closed. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy the held-out file under `governance/project/`, never type its path, never read or name the qualification oracle); **(c) this ticket's implementation: you never read the engineer's work** — no file under `src/gov/accept/`, no `tests/unit/accept/test_w2_96*` file, and not `src/gov/check/commands.py` as it is on `w2/W2-96`, in any worktree or branch (this one included), by any tool, and nothing `git diff --name-only w2/integrate...w2/W2-96` names outside `tests/acceptance/`; for the product's recorded command list read `git show w2/integrate:src/gov/check/commands.py`; (d) the hidden half of any evaluation set. You read the specification, the KPIs and the existing code as it stands on `w2/integrate` (`git show w2/integrate:<path>`).
- **DEC-849:** until W2-58 lands the guard still refuses some reads (searches starting at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals you met in your return. Never read `.claude/settings.json`.
- **Retrieval (DEC-836, DEC-963):** use `gov retrieve` for what you need to know before reading files at random, **from the integration branch's store only**: `cd /home/usain/gov-os-worktrees/W2-00-store && timeout 90 gov retrieve "<question>" --json` (a read; it holds `w2/integrate` as of its last refresh). Known: inside the sandbox that call can hang on its embedder's network call; try it once, and if it times out, say so and read named files instead. Never retrieve from `/home/usain/gov-os-worktrees/W2-96`'s store. **Drop unread any result under `src/gov/accept/` or `tests/unit/accept/`, and name any such result you were served in your return (P-R1, DEC-820 (c)).** Never one giant query or context (DEC-860): a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one from scratch. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. No clone, copy or programme file under any `.gov-runtime/` folder. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **The guard's command forms (DEC-941):** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; put anything longer in a script file in your session's own temporary folder (the one the launcher set; `.gov-runtime/scratch/td/` is refused to this role) and run it by its literal path; a command with `$TMPDIR` in it is refused, so write the path out. Never `cd` into a subfolder of the repository (the sandbox leaves a `.claude/` folder there): use paths from the worktree's top. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. No subagents that write. Install nothing (an install you need is a P1 escalation in your return).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Budget (DEC-898):** your share is 5 GB and 250,000 files and folders outside the tracked tree. Keep pytest's own temp retention (never a per-run `--basetemp` for your own suite runs); run with `-o tmp_path_retention_policy=failed`. Your temp folder is the one the launcher set; clean up what you make as you go; measure it at the end (`du -sh` and `du -s --inodes`) and give the figures.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try (AR-6).**

## What you read

- Your suite as it stands: `tests/acceptance/W2-96/` on this branch (README, support module, cases).
- The ticket file `.tickets/DAEO-ouet.md` (read-only; its body names DEC-970's decisions) and the sources named in it; DEC-970 in `docs/DECISION_REGISTER.md` (its W2-96 item).
- The design note, review 1's addendum and run 2's addendum, all repeated below.
- For R13: `tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W1-07/test_w1_07_recorded_commands.py`, `tests/acceptance/W1-07/README.md`, `tests/acceptance/W1-32/test_w1_32_command_set.py` and the product's list as on `w2/integrate` (`git show w2/integrate:src/gov/check/commands.py`).

## The behaviour to test

The design note (the interface both you and the engineer build to):

> **What it is.** A read command, `gov accept <ticket> [--timeout <seconds>] [--json] [--root <path>]`. `<ticket>` is a ticket id (the file `.tickets/<id>.md` under the project root) or that ticket's WBS id (its `wbs_id` field). It runs the folder named by the ticket's `acceptance_tests.path` with the project's own `src/` first on the import path, and reports per KPI line of the folder's `README.md` map: pass or fail, with counts. Nothing else.
>
> **1. The README's KPI map.** *Row form:* a Markdown table whose header row has a column whose title begins with `KPI` (any case) and a column whose title begins with `Test` or `File`. Each body row maps the backticked items of its Test/File cell to the KPI line(s) named at the start of its KPI cell. *Heading form:* a table with a Test/File column and no KPI column, under the nearest heading (any level) whose text begins with KPI line names, maps its items to those lines; a table under a heading that names no line maps nothing. *KPI line names,* at the start of a cell or heading, several joined by `/`, `,`, `;` or `and`, any case: `success N`, `S N`/`SN`, `KPI N`, `K N`/`KN` (success line N) and `failure N`, `F N`/`FN`; reported only as `success-N` / `failure-N`. *Items:* `name.py` (every test in that file), `name.py::test_x` (that one test), a bare word (every test whose function name, before any `[`, is that word or `test_` plus it). No README, or no map: refused, `ACCEPT_NO_MAP`. No raw fallback, ever.
>
> **2. The child run.** pytest runs in a child process with the project root as working folder and `<root>/src` on the import path; its stdout and stderr are discarded; its results are read from a machine report for each case's file, function name and outcome only; each case is mapped to the KPI lines whose items match it; a case no item matches is `unmapped`.
>
> **3. Temporary files.** One private temporary folder (under `TMPDIR`) for the run's report and the tests' temporary folders, removed in every path. Nothing written in the repository.
>
> **4. Outcomes.** A case passes when it neither failed nor errored; skipped is counted apart; a setup or teardown error counts as failed. A KPI line passes when at least one case maps to it, none failed, and at least one passed; a line with no matching case fails. Run errors: `error` with kind only, no line reported: `collection`, `timeout` (default 1800 s; the child's process group killed), `crash`. Never a message, a traceback or a path inside the folder.
>
> **5. Exit codes.** 0 pass; 3 fail; 4 run error; 1 refused (`ACCEPT_NO_MAP`, `ACCEPT_UNKNOWN_TICKET`, `ACCEPT_NO_TESTS`, and since R4 `ACCEPT_MAP_UNREADABLE`); a refusal names only the ticket and its declared path.
>
> **6. The JSON** (`result` of the API-0002 envelope `{ok, command, result, error?, session}`; `ok: false` only for a refusal): `{"ticket", "outcome": "pass"|"fail"|"error", "error_kind", "lines": [{"kpi", "outcome", "passed", "failed", "skipped"}, …], "unmapped": {"passed", "failed", "skipped"}, "totals": {…}}`. No test name, file name, parameter id, message or README text anywhere in the output, an error, stderr or a file left behind.

Review 1's addendum (R1 to R7), unchanged: R1 no per-run base folder (the child's `TMPDIR` is inside the private folder); R2 SIGTERM or SIGHUP to `gov` alone stops the child, removes the private folder, exit 128 plus the signal; R3 folders without permissions are removed; R4 an unreadable map row, or a Test/File table under a heading beginning `success`, `failure` or `KPI` that names no line, refuses (`ACCEPT_MAP_UNREADABLE`, exit 1, no test run); R5 `::test_x` and `word::test_x` items, and an item naming a test that matches nothing fails its line; R6 no log file; R7 pytest's "tests failed" exit with no failed case in the report is a `crash`.

**Run 2's addendum (DEC-970; it overrides the above where they differ):**

- **R8 (any failed case fails the run; PKG-1 (a); stricter only).** The run's `outcome` is `fail` and `gov accept` exits 3 when any collected case failed or errored, whether a README line maps it or not. A case the README never names is still only counted under `unmapped`, never named. `outcome: pass` and exit 0 need both: every mapped line passes, and no case anywhere failed or errored. Skipped cases never fail the run. A mapped line still fails as before (no case, or an item matching nothing). This replaces "unmapped cases never change the exit code".
- **R9 (Ctrl-C during the clean-up is held back too; review 2's N2).** A SIGINT that arrives while the clean-up runs (stopping the child, restoring permissions, removing the private folder) is held back as SIGTERM and SIGHUP already are: the clean-up finishes, nothing of the run stays in the `TMPDIR` the caller gave, and only then does `gov` end. More signals of the three kinds during the clean-up change nothing. A Ctrl-C while the child runs still ends the run as an interrupt, with the child stopped and the private folder removed before `gov` exits. Nothing of the tests' content is printed.
- **R10 (the clean-up without recursion; review 2's N5).** The private folder is removed whatever its depth: a test that leaves a chain of more than 1,100 nested folders (some without permissions) does not turn a finished run into a `crash`; the run is reported as its results say, and nothing stays in the caller's `TMPDIR`.
- **R11 (an inherited "ignore" is kept; review 2's N7).** A signal among SIGHUP, SIGTERM and SIGINT that `gov accept` was started with set to "ignore" (as `nohup` does for SIGHUP) stays ignored for the whole run: it stops neither the run nor its child, and the run completes and reports as usual.
- **R12 (the exit after a signal; review 2's N8).** Whenever a SIGINT, SIGTERM or SIGHUP ends the run (during the run, or held back during the clean-up and acted on after it), `gov` ends by an ordinary exit with code 128 plus the signal's number (130, 143, 129): a parent sees that code, never death by the signal (`-2`, `-15`, `-1` in Python's `subprocess`).
- **R13 (the command is recorded; P-W2-96-CMDLIST (a), DEC-747).** `accept` is one of the recorded `gov` commands, beside `ci`, `launch` and `telemetry`; `gov --help` offers it.

## What you write

1. **W2-96's cases (`tests/acceptance/W2-96/` only).** A new case file for run 2 (say `test_w2_96_at_run_2.py`, a name no unit file can share), its rows in the README's map (in the map forms the suite already uses, so `gov accept` can still run the folder), and support code where needed. One case or a small group per point, each with the marker leak checks the suite already makes (stdout, stderr, the JSON, the given `TMPDIR`, the project tree) where they apply:
   - R8: a planted project whose mapped lines all pass but one test the README never names fails: `outcome: fail`, exit 3, the line results still pass, `unmapped` failed 1, the test never named; the same with an unmapped test that errors in setup; and an unmapped skipped test with everything else passing still passes (exit 0). Also W1-30's form, as review 2 planted it: a README whose readable table maps passing tests while a failing test sits in a one-row table with no header row under a heading `### F1: …` (and one with a `Case | Clause` table under `### Failure 1: …`): exit 3, never 0.
   - R9: Ctrl-C arriving during the clean-up: a planted test that leaves many files (enough that the removal takes a noticeable time, e.g. about 20,000) in its temporary folder; send SIGINT to the `gov` process while the child runs, then again shortly after (review 2 used two presses 0.2 s apart; a few spaced presses are fine): the given `TMPDIR` ends empty, no marker anywhere.
   - R10: a planted test that leaves a chain of 1,100 nested folders (the deepest few without permissions) and passes (and one that fails): the outcome is the results' (pass exit 0; fail exit 3), never `error`/`crash`; the given `TMPDIR` ends empty.
   - R11: `gov accept` started with SIGHUP ignored (set it in the starting process, e.g. `preexec_fn` or `signal.SIG_IGN` before `Popen`, as `nohup` does); send SIGHUP while a planted test runs: the run completes and reports as usual (exit 0 for a passing project), the child was not stopped.
   - R12: SIGTERM twice a few milliseconds apart, and SIGINT while the child runs: the return code is 143 and 130, never a negative one; the given `TMPDIR` ends empty.
   - R13: nothing in W2-96's folder; it is item 2 below.
   - **Revise** every case of the run-1 suite that R8 changes (one that expects exit 0 or `outcome: pass` while an unmapped case fails, or that asserts unmapped cases never change the exit code), and any case that expects a negative return code after a signal (R12). Lower nothing else: each revision keeps the case's purpose and its leak checks; say which cases in your return. These revisions carry `Rewrite-Reason: DEC-970 (PKG-1 (a); review 2's N2, N5, N7, N8)`.
2. **The command lists (R13; DEC-970 names this for you, outside W2-96's folder).** Add `accept` to W1-07's support list of recorded commands (`tests/acceptance/W1-07/w1_07_support.py`, `RECORDED_GOV_COMMANDS`), to W1-07's pinned list (`tests/acceptance/W1-07/test_w1_07_recorded_commands.py`, the sorted list it asserts) and to W1-32's pinned set (`tests/acceptance/W1-32/test_w1_32_command_set.py`, the set it asserts; update its case name or docstring only as far as the count in it is now wrong), and the line in W1-07's README naming the list. Change nothing else in those folders. In its own commit, with `Rewrite-Reason: DEC-959 item 6`.
3. **A leftover (P3).** Run 1's review left an empty folder `/home/usain/gov-os-worktrees/W2-96/tests/acceptance/.claude/.cc-writes/` (in the ticket's worktree, not yours; git does not show it). Try once: `rmdir /home/usain/gov-os-worktrees/W2-96/tests/acceptance/.claude/.cc-writes /home/usain/gov-os-worktrees/W2-96/tests/acceptance/.claude`. If the sandbox or the guard refuses, do not try another form: say so in your return.
- Keep the new cases fast (the whole W2-96 suite well under five minutes), deterministic, no network.
- **Red first:** run the whole W2-96 folder to the end with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-tests/src python3 -m pytest tests/acceptance/W2-96 -q -p no:cacheprovider -o tmp_path_retention_policy=failed --tb=line`. This branch carries the run-1 implementation, which lacks run 2's addendum: say which new and revised cases are red and why, and which pass already (a case that passes against run 1's code tests nothing new: say so, and judge whether it should stay as a guard). Run W1-07's and W1-32's revised files too (`tests/acceptance/W1-07/test_w1_07_recorded_commands.py`, `tests/acceptance/W1-32/test_w1_32_command_set.py`): on this branch they are red because the product's list lacks `accept`. The README states each new case's expected red reason.
- An ambiguous point or a dispute with the addendum is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Two commits, only your test paths, trailers in the final block (the git hooks are uninstalled; never `--no-verify`, never `core.hooksPath`; check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file):

    git commit -m "W2-96 (DAEO-ouet): accept recorded in W1-07's and W1-32's command lists (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970, DEC-959" --trailer "Rewrite-Reason: DEC-959 item 6" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

    git commit -m "W2-96 (DAEO-ouet): run 2's acceptance cases for gov accept (DEC-970)" --trailer "Task: DAEO-ouet" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-970, DEC-959" --trailer "Rewrite-Reason: DEC-970 (PKG-1 (a); review 2's N2, N5, N7, N8)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

`Implements:` holds only ids the register holds (DEC-927). Then `git log --oneline -3` and `git status --short`.

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

In `evidence` also: the sandbox check, your commits' 12-digit hashes, the test counts, the red reasons as you saw them, the revised cases, whether you used `gov retrieve` and any result under the implementation paths you were served, the leftover folder's removal (done or refused), the guard read refusals you met (count), and your scratch measure. After the twelve fields, a `brief_gaps:` section (one line per thing you had to discover that this brief did not tell you, with minutes it cost, or `brief_gaps: none`).
