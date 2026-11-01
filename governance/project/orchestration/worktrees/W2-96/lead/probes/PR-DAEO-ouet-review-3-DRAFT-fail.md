# Probe record: W2-96 (DAEO-ouet) `gov accept`, review 3 (run 2, DEC-970)

probed_commit: 382e6d8fba8ce49fed1b329cc9d9114065a8b8d3

**Scope.** This probes run 2 over 549dd29b1c6f, which is run 1's code with `w2/integrate` merged in:
- the engineer's 41b9fdddf109 and 917aba42cd9c;
- the test designer's 1bf0c1d2e18f and a5ad2254e97b, merged in 7bc8a0303e0d;
- the lead's checkpoint 382e6d8fba8c.

**Method.** Read-only. The probes ran on projects planted from scratch in the reviewer's TMPDIR. Signals were sent from outside, timed by what is on disk.

## Probed and found sound

- **R8.** Any failed or errored case fails the run, mapped or not: exit 3, `outcome: fail`, counted under `unmapped`, never named.
  - Forms tried: an assertion failure, a setup error, a teardown error, a class-setup error, a strict xpass, and a failing built-in subtest.
  - Review 2's N1 forms now fail closed: W1-30's headerless row under "F1: …" and a `Case | Clause` table under "Failure 1: …" both give exit 3.
  - Skipped and xfail cases never fail the run.
  - A line whose only case is skipped fails.
  - Text mode agrees with `--json`.
- **R9.** A Ctrl-C during the clean-up is held back, whether it follows a Ctrl-C or SIGTERM during the run or comes during the clean-up of a run that finished. The removal completes, nothing stays in the given TMPDIR, and then gov ends. Storms of 145 to 150 signals of the three kinds, every 5 ms through the removal and after it, change nothing.
- **R10.** A chain 1,500 folders deep, with some folders and the bottom file without permissions, is removed after a pass (exit 0), a failure (exit 3), a timeout (exit 4, `timeout`), a SIGTERM (143) and a double Ctrl-C (130). Nothing is left.
- **R11.** A SIGHUP under `nohup`, a SIGINT ignored at start and a SIGTERM ignored at start each stop neither gov nor the child; the run completes and passes.
- **R12.** A run ended by SIGINT, SIGTERM or SIGHUP, during the run or held during the clean-up, ends with 130, 143 or 129 by an ordinary exit. `timeout` (coreutils), which sends SIGTERM to gov and then to its group, gave 143 with nothing left in 10 of 10 runs.
- **R13.** `accept` is recorded on one line of `commands.py` and nothing else changed there. `gov --help` offers it, and the core-commands check passes. W1-07's and W1-32's revisions only add `accept`.
- **Revisions of run 1's W2-96 cases.** The seven revised cases change only the run's outcome (pass to fail) and its exit code (0 to 3), as R8 asks. Every line and every count is unchanged, and the leak checks are kept. Nothing is lowered.
- **No leak.** The marker never reached stdout, stderr or the envelope. A Ctrl-C during the run now prints nothing.
- **No write.** No planted project changed (tree snapshot and `git status --porcelain --ignored`).
- **`gov accept DAEO-ouet --json`.** Exit 0, `outcome: pass`, all nine lines pass, `unmapped` 20, `totals` 100 passed. stderr was empty, the given TMPDIR was empty afterwards, and the worktree and its ignored status were unchanged.

## Findings

**V1. A stop that lands while a process the tests started in a session of its own is changing the run's private folder aborts the clean-up. The run is reported as a crash, and the tests' folders, named after the tests, stay in the caller's TMPDIR.**
- **Done.** A planted test runs a nested `gov accept` on a nested planted project in a session of its own. W2-96's own harness starts every nested run this way, and eight other suites here start processes like this. The nested test writes 3,000 small files and sleeps 1 s. SIGTERM was sent to the outer gov three ways:
  - once the nested gov's removal had begun (13 runs);
  - to the outer and the nested gov at once, as a stop of the whole process tree does (5 runs);
  - at a random time in the 2.5 s after the nested start (5 runs landed before the outer run ended).
  
  For comparison, the same runs were made with run 1's removal put back in both govs (12 runs).
- **Happened.**
  - On the head, 4 of 13, 2 of 5 and 1 of 5 runs ended with `ok: true`, `outcome: error`, `error_kind: crash` and exit 4, not 143.
  - The given TMPDIR kept the private folder. Always at least its chain of folders down to the nested run's TMPDIR, through the outer test's temporary folder, which pytest names after the test. Once, when the stop landed while the nested test was writing, 2,670 entries stayed, among them 2,657 files the nested test wrote, with their content, and both tests' names as folder names.
  - The removal stops at the first entry that another process removed meanwhile ("file not found"). With two removals over the same tree, whichever loses that race stops.
  - With run 1's removal, which ignores such errors and carries on: 143 and nothing left, 12 of 12.
- **Should have happened.** The private folder is removed in every path even when a process the run cannot stop changes it meanwhile: an entry already gone is passed over, a folder found not empty is emptied again, and no single entry stops the removal of the rest. A stopped run then ends with 128 plus the signal, and nothing of the run stays in the given TMPDIR (KPI 2, "or any file it leaves"; R9; R12).
- **Not reproduced.** The same could happen at the end of a run that was not stopped, if a test leaves such a process writing; one planted try did not hit it.
- **Severity: medium.**
  - It happens only on a stopped run, and only in suites that leave processes outside the child's process group.
  - In a planted measure, about one stop in three to five that lands during their file activity hits it. The rate on the real suite is not measured.
  - Nothing reaches stdout, stderr or the envelope; the leak is files in the caller's own TMPDIR.
  - It is new with this head: R10's removal replaced run 1's tolerant one.
- Ordinary work: yes, because a stop of a long `gov accept` (a timeout, a task stop, a closed terminal) is the ordinary case R2, R9 and R12 exist for, and processes in a session of their own are ordinary here: W2-96's own suite starts one for every nested run, and eight other suites start them too. No deliberate construction or in-process placement is needed; the activity windows last tens to hundreds of milliseconds and recur through the suite.
- Consequence: fails open. Test names and test-written files are left in the given TMPDIR. The stop's exit code is also lost (other).

**V2 (row). The clean-up's time grows with the square of the number of folders side by side, and the three signals are held throughout.**
- **Done.** The removal was timed on 1,000 to 8,000 sibling folders.
- **Happened.** 0.39, 2.48, 8.99 and 22.66 s, against 0.15, 0.47, 0.52 and 0.63 s for a plain recursive removal of the same shape. During that time, Ctrl-C, SIGTERM and SIGHUP are held (R9), so only SIGKILL stops gov.
- **Should have happened.** Removal time grows with the number of entries.
- **Severity:** low.
- Ordinary work: no, because an acceptance folder here holds about 100 tests at most, and thousands of sibling folders in one folder need an unusual suite.
- Consequence: other.

**V3 (row). Two short signal windows outside the run end gov by the signal. Nothing is created and nothing leaks.**
- **Done.** Signals were placed by time at gov's start and right after a normal clean-up.
- **Happened.**
  - Before the run window opens (0.14 to 0.42 s after the start, under load):
    - SIGTERM ends gov by the signal (−15);
    - SIGINT gives Python's traceback of import frames only (no test content) and −2;
    - at 0.04 s Python's own start fails with exit 1, which is gov's refusal code.
  - After a run that was not stopped, the clean-up restores the default handlers. A signal in the last tens of milliseconds ended gov by the signal in 3 of 4 placed sends, twice after the `pass` envelope had been printed.
- **Should have happened.** R12 states only the windows "during the run" and "held back during the clean-up", so these windows lie outside it.
- **Severity:** low.
- Ordinary work: no, because each window is tens of milliseconds at one end of the run.
- Consequence: other (fails closed: never exit 0).

Classification: 1 yes / fails open (V1); 0 yes / other; 2 rows for Wave 3 (V2, V3).

## Verdict

**Fail.** V1 is both "yes" and "fails open".

