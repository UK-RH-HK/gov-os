session: 2ddd0f47-0cc9-4858-a7bd-17c976e23674 is_error: False turns: 99 duration_ms: 2257002
**Step 0 (sandbox check):** (a) the write outside the worktree failed with `OSError: [Errno 30] Read-only file system`, and no file was written. (b) `echo sandbox-trial | git hash-object -w --stdin` printed 1ae28402a109… and exited 0; `git update-index --refresh` exited 0. `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-ouet`; top `/home/usain/gov-os-worktrees/W2-96`, branch `w2/W2-96`, head 382e6d8fba8c. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src python3 -c "import gov; print(gov.__file__)"` gives `/home/usain/gov-os-worktrees/W2-96/src/gov/__init__.py`.

task: Review 3 (FULL, read-only) of W2-96 (DAEO-ouet), `gov accept`, at head 382e6d8fba8c. Probe what run 2 changed (R8 to R13) for behaviour the tests miss: leaks, results that fail open, and writes in the repository.

status: PACKAGES. The probe fails on one finding that is "yes / fails open" (V1). Run 2's new clean-up stops at its first error, which run 1's did not. So a stop that lands while a process the tests started in a session of its own is changing the private folder leaves test-named folders and files in the caller's TMPDIR, and the run is reported as `crash`. One package is proposed.

work_completed:
- **Read:**
  - the ticket, `design.md`, `design-r1.md`, `design-r2.md`, review 2's record and `main.py` (its docstring and how it dispatches);
  - the run-2 diff of `src`, `tests/unit/accept`, and `tests/acceptance/W2-96`, `W1-07` and `W1-32`;
  - `commands.py` and its two users (the core-commands check and the skill validator).
- **Planted runs:**
  - About 115 `gov accept` runs on projects I built from scratch in my TMPDIR (marker `rv3mark`), plus a nested run inside 46 of them.
  - Each run was checked for:
    - the exit code and the envelope;
    - stdout and stderr, for the marker and generic words;
    - what stays in the given TMPDIR (count, names, the marker in names and in content);
    - the planted project (a tree snapshot and `git status --porcelain --ignored`);
    - whether the child, the grandchild or a process a test started still runs (checked in the same Bash call).
- **How signals were sent:**
  - Always from outside, timed by what is on disk: a note file, a 20,000-file folder starting to shrink, the given TMPDIR emptying.
  - No in-process placement was used for the head's behaviour.
  - Two wrappers in my TMPDIR, marked as such: one records only the type and errno of an exception the removal raises; the other puts run 1's removal back, for comparison only.
- I timed the removal of wide folders in-process.
- I ran `gov accept DAEO-ouet --json` once on this worktree, with an empty TMPDIR of my own and a snapshot and status before and after.

files_changed: none in the repository. The head is unchanged and the working tree is clean. My only status difference from the start is 7 ignored `__pycache__/` folders in other tickets' acceptance folders, written by the lead's scoped run beside me; they were already there before my DAEO-ouet run, which changed nothing.

evidence:
- **R13:**
  - The `commands.py` diff is the one `accept` line.
  - W1-07 and W1-32 only add `accept`: W1-07's support tuple, its pinned sorted list and one README sentence; W1-32's pinned set and a docstring paragraph.
  - `gov --help` offers `accept`, and `python3 -m gov.check.commands` exits 0.
- **R8, 12 planted runs:**
  - These unmapped cases each give `outcome: fail`, exit 3, `unmapped` failed 1, with every line still passing: an assertion failure, a setup error, a teardown error, a class-setup error, a strict xpass, and a failing pytest 9 built-in subtest.
  - An unmapped skip or xfail gives pass, exit 0, `unmapped` skipped 1.
  - W1-30's headerless row under "F1: …" and a `Case | Clause` table under "Failure 1: …" both give exit 3.
  - A mapped line whose only case is skipped fails, exit 3.
  - Text mode gives exit 3.
- **R9 and R12:**
  - SIGINT or SIGHUP while the child runs gives 130 or 129; two SIGTERMs 5 ms apart give 143.
  - SIGTERM, SIGINT, SIGHUP or three SIGINTs sent once the removal of a passing run's 20,000 files had begun (folder at 19,183 to 19,947 files) give 143, 130, 129 and 130, with no envelope and nothing left.
  - A signal during the run, then more during the removal, gives 130 or 143.
  - Storms of 145 and 150 signals, every 5 ms until gov ended, give 130 or 143, never a death by a signal.
  - `timeout --preserve-status 3` gave 143 with nothing left in 10 of 10 runs.
- **R10:** a 1,500-deep chain (every 97th folder and the deepest three without permissions, the bottom file mode 0) gives:
  - pass: 0;
  - fail: 3;
  - `--timeout 8`: 4, `timeout`;
  - SIGTERM: 143;
  - Ctrl-C twice: 130.
  
  Nothing was left in any of the five.
- **R11:** with `nohup` and SIGHUP, with SIGINT ignored and SIGINT sent, and with SIGTERM ignored and SIGTERM sent, gov and the child still ran 1.5 s later, and the run gave pass, exit 0.
- **V1, on the head:**
  - Stop timed at the nested gov's removal: 4 of 13 runs ended with exit 4 `crash`.
  - SIGTERM to the outer and the nested gov together: 2 of 5.
  - Random timing: 1 of 5 effective stops.
  - Leftovers at check time were 6 to 1,798 entries; what persists is 6 to 2,670 entries.
  - With run 1's removal put back: 0 of 12.
  - The observing wrapper recorded `FileNotFoundError` (errno 2) in the nested gov's removal in 6 of 6 runs; in those runs the outer removal won the race.
- **V2:** 1,000, 2,000, 4,000 and 8,000 sibling folders take 0.39, 2.48, 8.99 and 22.66 s to remove, against 0.15, 0.47, 0.52 and 0.63 s for `shutil.rmtree`.
- **V3:**
  - The run window opens 0.137 to 0.419 s after the start (load average 55 to 76).
  - SIGINT at 0.04 s: Python's own start fails (exit 1).
  - SIGINT at 0.07 or 0.1 s: a traceback of import frames only, then −2.
  - SIGTERM at 0.1, 0.15 or 0.25 s: −15.
  - After a normal clean-up, 3 of 4 placed signals gave −15 or −2, after the `pass` envelope was printed.
- **DAEO-ouet:**
  - Exit 0 in 170 s, `outcome: pass`.
  - Passed per line: success 1 to 5 are 14/16/23/10/32; failure 1 to 4 are 13/23/10/28.
  - `unmapped` 20 passed; `totals` 100 passed, 0 failed, 0 skipped.
  - stderr was empty, and the given TMPDIR was empty afterwards.
  - The worktree snapshot (7,367 entries) was unchanged apart from `.gov-runtime`'s own mtime, and `git status --porcelain --ignored` was unchanged by the run.
- **Leaks and writes:**
  - The marker never reached stdout, stderr or the envelope in any run.
  - No planted project changed in any run.

tests: no suite was re-run (DEC-959 item 1). I ran `gov accept DAEO-ouet --json` once (100 passed, exit 0), plus my own probe runs.

discoveries:
- **V1, new with this head.** The clean-up stops at its first error, and processes a test starts in their own session are outside gov's kill. Nine suites here start such processes: W2-96 (every nested run), W2-76, W2-69, W2-71, W2-50, W1-32, W1-28 and W1-27.
- **V2:** the removal is quadratic in the number of sibling folders.
- **V3:** two short windows outside the run end gov by the signal, and Python's own start can exit 1, which is gov's refusal code.
- **Cosmetic:** the exit-3 text in `EXIT_CODES` lacks a space after its comma. The text is shown nowhere.

risks:
- **My probe folders stay**, since `rm` is refused and was not tried. They are under `/tmp/gov-launch-independent-auditor-p_am01o7/claude-1000/rev3/`, 9,637 entries and 41 MB in all:
  - `runs/*`: planted projects and given TMPDIRs, including V1's leftovers (`nested-term-random-1` with 2,670 entries; `nested-term-1`, `-2`, `-3`, `-13` and `nested-tree-term-1`, `-2` with 6 each);
  - scripts: `probe.py`, `snap.py`, `wide_timing.py`, `gov_run1_removal.py`, `gov_log_remove.py`;
  - worktree snapshots, with `governance/project/` and `.claude/` pruned;
  - status files;
  - `accept-out.json`, plus the empty `accept-err.txt` and `accept-tmp/`;
  - `remove-log-*.jsonl`.
- V1's rate depends on load, and on the real suite it is not measured.
- The comparison with run 1 used a wrapper, not run 1's commit.

lessons:
- Gov's kill cannot reach the processes tests start in their own sessions; probe the clean-up with a nested `gov accept`, as W2-96's harness runs it.
- Timing stops by what is on disk reaches the clean-up from outside, without in-process placement.
- A wrapper that only observes still shifts timing. With it the outer removal won 6 of 6; without it the outer lost 4 of 13. Compare on the plain head.

proposed_decisions:
- **PKG-R3 (V1).** Classification: 1 yes / fails open (V1); 0 yes / other; 2 rows (V2, V3). Options (DEC-105):
  - **(a) Apply now.**
    - The removal tolerates concurrent changes, as V1's "should have happened" describes, with a bounded number of passes.
    - A stop keeps its 128+N exit even if the clean-up still fails.
    - V2 rides along (each folder listed once).
    - The test designer first adds red cases in the nested form: SIGTERM to the outer gov while the nested gov removes its folder, and to both at once. Both must end 143 with the given TMPDIR empty, repeated enough to be red on the head (about one run in three).
    - Cost: one function, plus 2 to 3 cases; one short round with a re-review of that change only.
  - **(b) Defer as a Wave 3 row.** The leak stays possible on stopped runs of the nine suites above, W2-96's own among them.
  - **(c) Restore run 1's tolerance as a fallback.** When the removal stops on an error, finish with a removal that ignores errors and carries on. Cost: smallest. Residual: narrow (a recursive fallback over a very deep chain that another process is changing).
  - Recommendation: (a), possibly with (c) as its inner fallback. Confidence: medium-high. V1 reproduced on the head in 7 of 23 effective stops, in three forms, and in 0 of 12 with run 1's removal; the real suite's rate is not measured.

unresolved:
- V1's rate on the real W2-96 suite.
- Which signal the harness sends on a Bash timeout, a task stop or a session end: to gov alone, to its group, or to the whole process tree. Still not observed.
- How long the other eight suites' own-session processes write: not probed.

recommended_next_action: The lead takes PKG-R3 to its decision. On (a), the test designer adds the nested red cases first, the engineer then makes the clean-up tolerate concurrent changes (V2 riding along), and a short re-review probes that change only.

---

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

brief_gaps:
- The probe list has no item for processes a test starts outside the child's process group (in its own session). The clean-up cannot stop them, and it races with them. Nine suites here start such processes.
- A stop of the real suite cannot be measured: the brief allows the DAEO-ouet run once, and DEC-959 item 1 forbids re-running suites. A planted nested case stands in. The brief could allow one interrupted run with a given TMPDIR when a finding needs its real rate.
- What the harness sends on a Bash timeout, a task stop or a session end (to gov, to its group, or to the whole tree) is still not stated. V1's rate depends on it.
- `rm` is still refused and no clean-up form is allowed; my probe folders are listed under risks.

Guard refusals met: read refusals (DEC-849): 0. Other refusals: 0.
