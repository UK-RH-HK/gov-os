session: 46800eb8-736c-4933-805a-898535b94925 is_error: False turns: 95 duration_ms: 1626761
Cleanup was refused twice: first for pairing `cd` with a git command, then at the permission prompt for `rm -rf`. Per AR-6 I stop and report it. The worktree is as I found it: same untracked sandbox placeholders as at the start, head `6ec6cbd6e158`.

task: Review 1 (FULL, read-only) of W2-96 (DAEO-ouet), `gov accept`, at head 6ec6cbd6e158: find any way test content reaches the caller, and any result that fails open, that the tests miss.

status: PACKAGES. The probe fails: three findings are both "yes" and "fails open" (F2, F3, F6). F3's fix changes the design note's rule "unmapped cases never change the exit code", so it needs a decision (PKG-1).

work_completed:
- Step 0 passed: (a) was refused (`OSError: [Errno 30] Read-only file system`, no file written); (b) `hash-object -w` and `update-index --refresh` exited 0. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-ouet`, top level `/home/usain/gov-os-worktrees/W2-96`, branch `w2/W2-96`, head 6ec6cbd6e158. `gov.__file__` is `/home/usain/gov-os-worktrees/W2-96/src/gov/__init__.py`.
- Read: the ticket, DEC-959 items 6–7, DEC-957, DEC-820 (c), DEC-317, DEC-430 (MR-3), ROLES-RESEARCH-1 §2.7, `main.py`'s docstring, the lead's design note, `src/gov/accept/`, the unit tests, `tests/acceptance/W2-96/` and its support module.
- Probes: about 60 `gov accept` runs on planted projects built from scratch in my `TMPDIR` (marker `rvw96mark`). Each run checked stdout, stderr, the project tree (ignored files included), `git status --ignored`, the given `TMPDIR` and `HOME`.
- Ran `gov accept DAEO-ouet` on this worktree twice, with before/after snapshots of the tree.

files_changed: none in the repository. The session's sandbox created two empty folders, `tests/acceptance/.claude/.cc-writes/`, at 04:04:06, when one of my commands changed into `tests/acceptance` (see risks).

evidence:
- `gov accept DAEO-ouet --json` on this worktree gave `{"outcome": "error", "error_kind": "crash"}`, exit 4, in 1.7 s. The runner's child command run by hand stops with `ERROR: a per-run --basetemp (…) is refused (DEC-898, DEC-907 item 2) … set GOV_ALLOW_BASETEMP=1`, exit 4.
- With `GOV_ALLOW_BASETEMP=1`: `outcome: pass`, success 1–5 pass with 7/4/9/7/17 passed (failure 1–4 the same), `unmapped` 10 passed, `totals` 54 passed, exit 0, 89.6 s. The tree was unchanged (every path, size and mtime), and so was `git status --porcelain --ignored`.
- SIGTERM to `gov` alone, 3 s into a 6 s failing test: exit −15, no output. The child's "finished" record exists. Left in the given `TMPDIR`: `gov-accept-*/report.xml`, holding the planted assertion message, plus `basetemp/test_rvw96mark_slow0/rvw96mark-tmp.txt`. SIGHUP gave the same. SIGINT was clean.
- Copy of W2-58's README: 54 named tests planted, 43 unmapped. With all 43 failing: `exit 0 outcome pass … unmapped {'passed': 0, 'failed': 43, …}`. With one mapped test failing: exit 3.
- `--timeout 5` while a test held a folder at 0o555 (restore in `finally`): `error`/`timeout`. Left: `gov-accept-*/basetemp/test_rvw96mark_careful_lock0/rvw96mark-locked/rvw96mark-fixture.txt`.

tests: no suite re-run (DEC-959 item 1). The two `gov accept DAEO-ouet` runs above, as the brief asks. Plus my own probe runs.

discoveries:
- F1: the repository's `tests/conftest.py` makes `gov accept` crash for every acceptance folder here.
- Of the 70 acceptance READMEs, 14 have no map the reader accepts, so `gov accept` refuses them (fails closed). 30 have at least one row that names tests but names its KPI line in a form the reader does not take. Ten use the `::test_x` shorthand, which the reader matches to nothing.
- Neither the test-design skill nor the common lead brief states the map forms; the brief asks only for "a README mapping each KPI line to its tests".
- In this harness, a Bash tool timeout moves the command to the background; it is not killed.
- Every sandboxed command changes the worktree root's mtime.
- This session's environment already carries `PYTHONPATH=<worktree>/src`.

risks:
- My probe folders are still in my `TMPDIR`: `rv/`, `diag1/` and seven snapshot text files, 15 MB, about 3,660 entries. Removal was refused twice (first the form pairing `cd` with git, then the permission prompt for `rm -rf`); I stopped (AR-6). The lead may remove them.
- The lead may remove the empty `tests/acceptance/.claude/.cc-writes/` folders; empty folders do not show in `git status`.
- F2's fix cannot cover a SIGKILL of `gov` itself (a residual).

lessons:
- W2-96's planted projects have no copy of the repository's `tests/conftest.py`, so no planted case can see F1. Run `gov accept` on a real ticket too.
- Do not `cd` into a repository subfolder in a sandboxed session: it leaves `.claude/.cc-writes/` there.
- Ignore the root folder's mtime when snapshotting the tree; the sandbox changes it on every command.

proposed_decisions:
- PKG-1 (F3), classification: 1 finding, yes / fails open. Options (DEC-105):
  - (a) Apply now: any failed or errored case, mapped or not, makes the run `fail` (exit 3); unmapped cases stay counted only; a map row that names tests but no line is refused. Cost: a small runner change, and the test designer revises the W2-96 case that asserts an unmapped failure leaves exit 0 (red first).
  - (b) Teach the reader today's forms (`::test_x`, unnumbered "Failure"/"Success", "3a") and state the forms in the test-design skill and the lead brief. Cost: reader plus skill and brief changes; any form nobody foresaw still fails open.
  - (c) Re-baseline: keep the rule and add a designer-side check that every collected test is mapped. Cost: a new check.
  - Recommendation: (a), high confidence. It fails closed whatever the form, and a failing unmapped premise rightly fails the run.
- F1, F2 and F6 need no decision; their fixes ride along in the resume (DEC-802). Recommendations: run without `--basetemp`, since pytest's default base folder already falls under the private `TMPDIR` (medium-high confidence); turn SIGTERM and SIGHUP into the same cleanup path as Ctrl-C and make the child end when `gov` ends (high); remove the private folder with an error handler that restores permissions, as pytest's own clean-up does (high).

unresolved:
- Which signal the Bash tool uses to stop a background command after 10 minutes: not observed.
- SIGKILL of `gov`: not probed; by reasoning, the folder stays and the child runs on.
- How likely F5 is in adopted projects: a judgement.

recommended_next_action: The lead takes PKG-1 to its decision, then resumes the engineer with F1, F2, F6 and F3 as decided, the test designer adding review cases red before each fix (DEC-136).

Guard read refusals met (DEC-849): 0.

---

# Probe record: W2-96 (DAEO-ouet) `gov accept`, review 1

probed_commit: 6ec6cbd6e158

Base ab1ea26c5585. Engineer 9859695c8fcc. Tests 73e50896445c, merged in 986fa7cf4b1e. Lead checkpoint 6ec6cbd6e158.

## Probed and found sound

- **Pass, fail and every case kind.** Tested: a pass, a failure with values, a setup error, a teardown error (counted failed), a skip, parameter ids, prints, stderr writes, log records and warnings, in `--json` and text and by WBS id. Per-line results are correct, and the marker is in no output, no file and no `TMPDIR`. Nothing is written in the project, ignored files included.
- **The caller's environment.** `PYTEST_ADDOPTS` (with `-rA`, a `--junitxml` into the project, `-p no:junitxml`), `PYTEST_PLUGINS`, `PYTEST_DEBUG`, `PYTEST_TIMEOUT`, `PYTEST_XDIST_AUTO_NUM_WORKERS`, `PYTHONSTARTUP`, `PYTHONFAULTHANDLER`, `PY_COLORS`, `FORCE_COLOR` and `COLUMNS` are dropped or harmless; the result is unchanged. `PYTHONWARNINGS` and `PYTHONVERBOSE` act on `gov` itself only, and show no test content.
- **The project's pytest configuration.** `addopts -rA`, `junit_logging = all`, a `--junitxml` into the repository, `-n 2`, `-x` (fails closed), `log_cli`, `cache_dir` and `--doctest-modules` are all read correctly. `-p no:junitxml`, `--testmon` and `--debug` end as `crash` with nothing written. `--continue-on-collection-errors` gives `collection`.
- **Exits inside a test.** `sys.exit(0)` counts as a failure. `os._exit(0)` is `crash`. Closing descriptors 1 and 2 is read correctly.
- **The terminal.** The child has no controlling terminal: `/dev/tty` fails with ENXIO, and nothing reached a pseudo-terminal.
- **Ctrl-C.** SIGINT stops the child, removes the folder, and prints only `gov`'s own traceback.
- **Error kinds.** An unreadable README, a non-UTF-8 README, a folder at mode 000, a conftest import error and a malformed JUnit file are `crash`. A folder at mode 300 is `collection`. A README that is a folder is `ACCEPT_NO_MAP`.
- **Refusals.** They name only the caller's input or the declared path; `../` ids are refused. `--timeout 0` gives `timeout`.
- **A test's own-session process.** It outlives the timeout but cannot write once the folder is gone.
- **The Bash tool's timeout.** It moved the run to the background, where it ended normally and left nothing.
- **Real READMEs.** W2-61 (row form) and W2-72 (heading form) read sanely, and a mapped failing test fails its line.

## Findings

**F1. `gov accept` cannot run any acceptance folder of this repository.**
- Done: `gov accept DAEO-ouet` on this worktree.
- Happened: `error`/`crash`, exit 4. The repository's `tests/conftest.py` refuses any run given a base folder of its own unless `GOV_ALLOW_BASETEMP=1`, and the runner always gives one. With the allowance set, the result is sane.
- Should have happened: the per-line result.
- Severity: high for the ticket's purpose (success 1 is unmet in this repository).
- Ordinary work: yes, because every engineer's run in this repository hits it.
- Consequence: other (fails closed, but the engineer is left with no opaque way to run its tests).

**F2. SIGTERM or SIGHUP leaves the run's content in the caller's `TMPDIR`.**
- Done: SIGTERM, and separately SIGHUP, to `gov` alone during a run.
- Happened: `gov` died without its cleanup. The child, in a session of its own, ran to the end and wrote the full JUnit report, holding assertion messages and tracebacks, into the private folder. That folder stayed, with the tests' temporary files under folders named after the tests.
- Should have happened: as for Ctrl-C: the child stopped and the folder removed ("removed in every path").
- Severity: high.
- Ordinary work: yes, because `timeout(1)`, a task stop, a supervisor or a closed terminal is how ordinary tools end a long command.
- Consequence: fails open.

**F3. Map rows in forms used today are silently dropped, and their failing tests are reported as a pass.**
- Done: a parse-only scan of all 70 READMEs, then a planted ticket with a copy of W2-58's README.
- Happened: rows whose KPI cell reads "Failure: …" with no number, "Success 3a", "S8b" or "F …" map nothing, and the `::test_x` shorthand matches nothing. The tests they name are unmapped, and an unmapped failure never changes the exit code. With 43 named tests failing, the run reported `pass`, exit 0.
- Should have happened: no failing named test hidden behind a pass.
- Severity: high. It is bounded downstream: the lead's scoped run and the merge queue run the folder with pytest itself, so the cost is a wasted round, not a bad merge.
- Ordinary work: yes, because nothing tells designers the forms, and W2-58's form was written under today's instruction.
- Consequence: fails open.

**F6. A read-only folder in a test's temporary folder outlives the cleanup.**
- Done: (a) a test that locks a folder and fails before restoring it; (b) a careful test, restoring in `finally`, that holds a folder read-only when the runner's timeout ends the run.
- Happened: in both, the private folder stays in the caller's `TMPDIR`, with a folder named after the test and the fixture's content. The runner removes it with errors ignored, which cannot clear a folder without write permission.
- Should have happened: removed in every path.
- Severity: medium.
- Ordinary work: yes, because 18 acceptance files here drop write permission (several of them on folders) while they run the code under test, and that code hanging ends in the runner's SIGKILL, so no `finally` runs.
- Consequence: fails open.

**F9. Some error kinds are approximate.**
- Happened: a KeyboardInterrupt inside a test and a folder at mode 300 give `collection`; a conftest import error and F1's refusal give `crash`.
- Severity: low.
- Ordinary work: yes, because each is an ordinary accident.
- Consequence: other (fails closed).

**F4 (row). A test's relative write lands in the project root.**
- Happened: the planted value showed in `git status` as an untracked file.
- Ordinary work: no, because it needs a test that writes outside its temporary folder, which raw pytest leaves the same way; the runner cannot keep a test from writing where it likes.
- Consequence: fails open.

**F5 (row). `log_file` in the project's pytest configuration.**
- Happened: the child wrote the tests' log records into a file in the project root.
- Ordinary work: no, because this repository has no pytest configuration. It is an entry criterion for adopting a project that sets `log_file` (DEC-803); the cheap override can ride along.
- Consequence: fails open.

**F7 (row). `pytest.exit` inside a test.**
- Happened: with return code 0 or 1, the run reported `pass`, exit 0, although later tests never ran. The interrupted case was read as passed, and pytest's exit code 1 is not cross-checked against the report.
- Ordinary work: no, because neither acceptance tests nor the code under test call it.
- Consequence: fails open.

**F8 (row). Deliberate constructions.**
- Happened: a test writing through `/proc/<parent>/fd/2` reaches `gov`'s stderr, and a conftest that rewrites the report forges a pass.
- Ordinary work: no, because both need a deliberate construction.
- Consequence: fails open.

**F10 (row). `PYTHONUSERBASE` is dropped.**
- Happened: where pytest is reachable only through `PYTHONUSERBASE`, the child cannot import it and the run is `crash`.
- Ordinary work: no, because pytest here is in the default `~/.local`.
- Consequence: other.

Classification: 3 yes / fails open (F2, F3, F6); 2 yes / other (F1, F9); 5 rows for Wave 3 (F4, F5, F7, F8, F10).

## Verdict

**Fail.** F2, F3 and F6 are both "yes" and "fails open".

brief_gaps:
- The brief asks for the probe folders to be cleaned up, but `rm -rf` is refused at the permission prompt in this non-interactive session. Name an allowed form, or let the launcher remove the reviewer's `TMPDIR`.
- The interrupt line names only Ctrl-C. SIGTERM and SIGHUP are the ordinary ways tools end a command and deserve their own line (the design note's "every path" list omits them too).
- The judgement rules don't say how to treat a fail-open that the design note itself sanctions (F3). I used a DEC-105 package.
- The brief says `PYTHONPATH` is never set in a session's environment, but this session's environment carries it.
- Warn reviewers not to `cd` into repository subfolders, because the sandbox leaves `.claude/.cc-writes/` there.
