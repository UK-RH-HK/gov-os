# W2-177 (DAEO-1k7y): the six W2-96 signal reds, diagnosis (S1)

Written before any code or test change. "Before" counts come from `run_forms.sh before 2` (the lead's script, four
forms, two runs each) and one extra form of mine (`real-home-bg`), all run in this tree at its base commit 2a35ec307.
The cases of every run: the six cases of the ticket plus `test_w2_96_r11_an_inherited_ignore_is_kept` (three
parameters), nine tests per run.

## The cause: two independent defects, each explains some of the six in some start forms

### (A) `gov accept`'s child lost `PYTHONUSERBASE` (an empty HOME cannot find pytest)

- `src/gov/accept/runner.py:539` builds the run's environment without every key that starts with `PYTEST_` or
  `PYTHON`; `:540` then adds only `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE` and `TMPDIR`. `PYTHONUSERBASE` is gone.
- pytest is installed in the user site (`/home/usain/.local`). Under an empty HOME the child's `python3 -m pytest`
  cannot import it, ends at once, and `_run` reports a crash (`runner.py:563`, exit code not in (0, 1)): gov exits 4.
  The planted test never runs, so `started` is never written and the case's 60 s `_wait_for(started)` fails.
- W2-96's own acceptance README says the run is given the user base as `PYTHONUSERBASE` and `HOME/.local` as the way
  pytest is found (README.md lines 29-35, 455-456); the acceptance support gives both, so its cases hide (A).
- Evidence: form `empty-home` below (foreground, SIGINT not ignored): exactly cases 2, 4, 5, 6 fail (the four
  60 s cases) and R11's three parameters; with the real HOME the same nine pass. In `setsid-bg` and `bg-job`
  (empty HOME and a background start) cases 1 and 3 fail with `assert 4 == (128 + 2)`: gov's exit code is 4 (the
  crash), not 130 and not 0, so (A) masks (B) there.
- Not an effect of the nightly: `nightly_cron.sh:19` exports `HOME=/home/usain`, so (A) is absent from the nightly.

### (B) The start form: a background job begins with SIGINT ignored, and the test launcher never resets it

- A background job of a non-interactive bash (job control off) starts with SIGINT and SIGQUIT ignored; an ignored
  signal stays ignored across `exec`, and Python keeps an inherited SIG_IGN of SIGINT.
  `lead_verify.sh:30` (`setsid bash ... &`) and the cron nightly (`nightly_restart.sh:181`, `bash -c '...' &` under
  `systemd-run --scope`; the nightly's pytest, and `nightly_alone.py`'s re-run, are inside it) are both such starts.
  Probe by the lead: `python3 -c ... & wait` in a bash script gives SIGINT ignored = 1, `setsid python3 ... & wait`
  = 1, foreground = 0. My runs print it first in every log (`SIGINT-ignored-at-start:` below).
- `tests/unit/accept/w2_96_reap.py:145-147` (`launch_gov`'s `_ignore`) only sets the signals named in `ignore` to
  SIG_IGN; it never sets the others to SIG_DFL. A planted gov therefore starts with whatever the test process had:
  with SIGINT ignored, gov keeps it (R11, by design; `test_w2_96_r11_an_inherited_ignore_is_kept` stays green) and
  a SIGINT sent to it changes nothing.
- Evidence: form `real-home-bg` below, the nightly's own form (real HOME, background start): exactly the six
  cases fail, R11's three pass; cases 1 and 3 fail with `assert 0 == (128 + 2)` (gov ended normally with 0: the
  SIGINT was ignored), cases 2, 4, 5, 6 wait 60 s and never see gov end. Same outcomes as the nightly
  20261112-0404 (`parallel.txt` lines 412 and 519: `assert 0 == (128 + 2)`, 2.4 s each).
- Direct proof in the nightly: `test_premise_r11_a_process_started_this_way_begins_with_the_signal_ignored`
  (acceptance, premise of R11) got `'1 1 0'` where it expects `'1 0 0'` (`parallel.txt` lines 576-578; test file
  line 384): the child started with SIGHUP ignored as asked and SIGINT ignored too, inherited from the pytest
  process.
- The W2-96 acceptance support has the same gap: `tests/acceptance/W2-96/w2_96_support.py:1380-1388` (`_popen`'s
  `ignoring` only ignores, never resets). NOT mine (acceptance folder, read only): it is why five acceptance cases of
  the same family are red in the nightly (premise R11, r9 second press, r12 SIGINT, at_no_leak interrupted run).
  The lead packages it for a test designer's revision.

### Which of the six each explains

| case | (A) empty HOME, foreground | (B) real HOME, background | both (empty HOME, background) |
|---|---|---|---|
| 1 `clean_up_is_held_back[signals0]` | passes | fails (0 != 130) | fails (4 != 130) |
| 2 `run_then_more_during_the_clean_up[2-more0]` | fails (`started` never written) | fails (60 s) | fails |
| 3 `presses_until_gov_ends_never_kill_it[kinds0]` | passes | fails (0 != 130) | fails (4 != 130) |
| 4 `ctrl_c_during_the_run_stops_it` | fails (`started` never written) | fails (60 s) | fails |
| 5 `r14_a_stopped_run_keeps_128_plus_the_signal[True-2]` | fails | fails (60 s) | fails |
| 6 `r16_an_own_session_orphan_is_reaped...[2]` | fails | fails (60 s) | fails |
| R11 unit case, 3 parameters | fails (child cannot start) | passes | fails |

(A) alone: 4 of the six and R11; (B) alone: all six; together: all six and R11.

## The start forms and their counts (before any change)

| form | HOME | start | SIGINT ignored at start | runs | counts per run |
|---|---|---|---|---|---|
| empty-home | empty folder | foreground | 0 | 2 | 7 failed, 2 passed (424 s), 7 failed, 2 passed (424 s) |
| real-home | /home/usain | foreground | 0 | 2 | 9 passed (13.9 s), 9 passed (13.9 s) |
| setsid-bg | empty folder | `setsid ... &` (lead_verify's form) | 1 | 2 | 9 failed (425 s), 9 failed (424 s) |
| bg-job | empty folder | `... &` | 1 | 2 | 9 failed (425 s), 9 failed (425 s) |
| real-home-bg (mine, the nightly's form) | /home/usain | `... &` | 1 | 2 | 6 failed, 3 passed (252 s), 6 failed, 3 passed (251 s) |

Run files: `.gov-runtime/scratch/forms/before/<form>-<i>.txt` and `counts.txt` (my `real-home-bg` runs were one inline
command, output kept in the sandbox's TMPDIR, not committed).

## Why some runs passed

- Alone with the real HOME: form `real-home`: foreground, SIGINT at default, `~/.local` found: nine passed in 14 s.
  Both defects absent.
- The W2-110 verify that passed: W2-110's `lead/log/verify-4/parallel.xml` (11-12 00:32, a hand-driven run: its
  `driver.log` is empty) has the six cases `ok` in 0.4-3.5 s. Its start form is not recorded in anything I can read,
  so: not established. It fits a foreground or non-background start (SIGINT at default; the cases passed at once, not
  after 60 s) with a HOME that finds pytest. W2-110's later verify through `lead_verify.sh` (11-12 01:31, `setsid`
  start) failed the same cases (`verify/parallel.txt`), as the other trees' did.

## The nightly's "alone at load 18"

Not established as load: the gate line of run 20261112-0404 reads `load=0.9/1.2` at its start (`run.txt` line 7), and
the real-HOME background form fails the same six cases in my runs twice in a row, and fails at once (2.4 s) for cases
1 and 3, which no load explains. `nightly_alone.py` (lines 30-38) re-runs each failing case with `subprocess.run`, in the
foreground of `nightly.sh:224`, which is itself inside the background job of `nightly_restart.sh:181`: its pytest
starts with SIGINT ignored, and HOME is the real one (`nightly_cron.sh:19`; `nightly_alone.py` drops only
`PYTEST_ADDOPTS` and `PYTEST_PLUGINS`). So the alone re-run has the same start form as the run it re-runs: "red
alone" says nothing against a start-form cause, and the form is the cause. Read-only; nothing of the nightly changed.

## W2-56's two SIGINT ending cases (DAEO-wnnz; a non-goal to fix)

`test_s12_an_ending_signal_to_the_launcher_reaches_the_sessions_process_group[SIGINT]` and
`test_s12_the_temp_folder_is_removed_when_the_launcher_is_signalled[SIGINT]` are red in the nightly (85-87 s,
"gov launch did not end within 35 s") for SIGINT only, SIGTERM and SIGHUP are green. That is the signature of (B):
`tests/acceptance/W2-56/w2_56_support.py:531-537` (`start_launch`) starts the launcher with `Popen(...,
start_new_session=True)` and no reset of SIGINT, so a pytest started as a background job passes SIGINT-ignored on
to the launcher, which keeps it. I did not run them; the evidence is the signal-specific pattern and the shared
start code path. Probable same cause (B); the fix would be in W2-56's acceptance support (not mine).

## The fix

1. (A) `runner._run` (`runner.py`, two lines after the environment is built): keep the caller's `PYTHONUSERBASE` in
   the child's environment; every other `PYTHON*` variable stays dropped, `PYTHONPATH` and `PYTHONDONTWRITEBYTECODE`
   as they are. Commit 0ca819544.
2. (B) `w2_96_reap.launch_gov`: SIGINT, SIGTERM and SIGHUP are set to SIG_IGN when named in `ignore`, and to
   SIG_DFL otherwise. `gov accept` keeps an inherited ignore unchanged (R11 stays green: its three parameters pass in
   every form). Commit 003f3d84e, trailer `Rewrite-Reason`.
3. New cases `tests/unit/accept/test_w2_177_start_forms.py` (commit 3f1401596), written red first: on the code
   before the fix three of its five cases failed for the intended reasons (the child's `PYTHONUSERBASE` was `None`;
   the planted gov started with SIGINT/SIGTERM/SIGHUP `[1, 1, 1]` ignored where `[0, 0, 0]` and `[1, 0, 0]` were
   expected); the two that passed are guards that hold before and after (no `PYTHON*` variable but the user base
   passes; the launcher ignores all three when all three are named). The new file has no parametrised case, since the
   repository's opt-in lists keep only a parametrised case's first row and would report the others as deselected.
   No assertion, timeout, marker or skip of any W2-96 case changed; `skip_known.json` and `tests/acceptance/` are
   untouched (`git diff --name-only` against the base lists these four files only: this evidence, `runner.py`,
   `w2_96_reap.py`, `test_w2_177_start_forms.py`).

## After the fix (S2): ten runs per form

Each run is the nine cases above plus the five of `test_w2_177_start_forms.py`: 14 tests, every run through the
heavy slot (`inner.sh`, changed by the lead for the CTO's order after incident T1 0556).

| form | SIGINT ignored at start | runs | result |
|---|---|---|---|
| empty-home | 0 | 10 | 10 of 10 runs: 14 passed (13.9-14.2 s each), none failed, none skipped |
| real-home | 0 | 10 | 10 of 10 runs: 14 passed (14.1-14.8 s each) |
| setsid-bg | 1 | 10 | 10 of 10 runs: 14 passed (14.2-14.5 s each) |
| bg-job | 1 | 10 | 10 of 10 runs: 14 passed (14.0-14.4 s each) |
| real-home-bg (the nightly's form) | 1 | 10 | 10 of 10 runs: 14 passed (14.2-14.5 s each) |

Run files: `.gov-runtime/scratch/forms/after/<form>-<i>.txt` and `counts.txt` (the lead's four forms); the
`real-home-bg` runs were one inline command (same `inner.sh`), output in the sandbox's TMPDIR.
Before and after, same cases: the six went from 60 s waits (and two 2.4 s asserts) to 14 s for all fourteen tests.

The whole unit folder, once (slot, empty HOME, the command of the brief):
`env HOME=<tree>/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<tree>/src python3 -m
pytest tests/unit/accept -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real
and not green_here and not time_limit"`:

    95 passed, 117 deselected in 43.23s

The 117 deselected are the `-k`/`-m` exclusions of the brief and the repository's opt-in lists (parametrised cases'
other rows); the six and this ticket's five cases are not among them (the six, R11's three parameters and the five new
cases run in every form above by node id; in the folder run R11 runs its first row only).

## What is not done here (named for the lead)

- The same start-form gap in the W2-96 acceptance support (`_popen`, `w2_96_support.py:1380-1388`) and W2-56's
  (`start_launch`, `w2_56_support.py:531-537`): acceptance folders, a test designer's revision with a Rewrite-Reason.
  Five W2-96 acceptance cases and W2-56's two SIGINT cases stay red in a background start until then. Whether (A)
  matters there: the acceptance support builds its own environment with `HOME/.local` linked and `PYTHONUSERBASE` set.
- `nightly_alone.py` re-runs a failing case in the same start form as the run: a red there does not separate a start-form
  cause from a defect of the head (for the nightly's owner, not changed here).

## The lead's verify (head f5f050c87ddf, `lead_verify.sh`: a `setsid ... &` start, SIGINT ignored, empty HOME)

`RED parallel exit 1 in 734 s (3934 tests 5 failed 0 errors 6 skipped)`, `.gov-runtime/scratch/lead/log/verify/`.
The six cases of this ticket and its five new cases pass. The five reds, none of them in `skip_known.json`:

- Four W2-96 acceptance cases of the same family: `test_w2_96_at_no_leak.py::test_an_interrupted_run_stops_its_child_and_leaves_nothing`,
  `test_w2_96_at_run_2.py::test_r9_a_ctrl_c_during_the_clean_up_is_held_back_until_the_clean_up_ends[a-second-press-once-the-removal-began]`,
  `::test_r12_..._128_plus_the_signal[SIGINT]` and `::test_premise_r11_a_process_started_this_way_begins_with_the_signal_ignored`.
  Run once in the foreground (real HOME, through the heavy slot), the same four functions, all their parameters,
  pass: `8 passed in 4.74s`. Their red is cause (B) in the acceptance support's `_popen` (`w2_96_support.py:1380-1388`),
  outside this ticket's paths: a test designer's revision with a Rewrite-Reason.
- `tests/acceptance/W2-02/test_w2_02_green_here.py::test_core_schema_is_green_on_this_repository`: `core-schema has 1
  findings: .tickets/DAEO-1k7y.md: unknown record type 'bug'`. This ticket's own file, not its change: its `type: bug`
  is not a type the core schema knows. It reddens every tree once the ticket file is in the base.

## Run 2: the acceptance supports' revision (P-W2-177-1 (a), the CTO 07:05) and the verify of 7cde9429ea0c

The CTO ruled P-W2-177-1 (a) and P-W2-177-2 (a) (done on w2/integrate, `type: task`); w2/integrate (c62b66bb4) merged
in at ee18860f7. An independent test designer (td-1, session a0cc944e-c34e-427b-b311-6532d82128bc, Sonnet, high, C2)
revised `tests/acceptance/W2-96/w2_96_support.py` `_popen` and `tests/acceptance/W2-56/w2_56_support.py`
`start_launch` (8f40881d9, `Rewrite-Reason` naming DAEO-1k7y cause (B) and DEC-866): the started process always gets a
`preexec_fn` that sets SIGINT, SIGTERM and SIGHUP to SIG_IGN when the case names them, otherwise to SIG_DFL, as
`w2_96_reap.launch_gov` does. No test file changed; no assertion, timeout, marker, skip or parameter. Merged at
7cde9429e.

### Counts per start form (the three files whole: test_w2_96_at_run_2.py, test_w2_96_at_no_leak.py, test_w2_56_endings.py)

Every run through `heavy_slot.sh`, empty HOME, `PYTHONUSERBASE=/home/usain/.local`; the 9 deselected are the
repository's opt-in representative rows (`tests/conftest.py:292-317`), the same 9 in every run before and after.

| when | who | form | SIGINT ignored at start | runs | each run |
|---|---|---|---|---|---|
| before (ee18860f7) | td-1 | fg | 0 | 1 | 29 passed |
| before (ee18860f7) | td-1 | setsid-bg | 1 | 1 | 6 failed, 23 passed (430 s): W2-96 premise R11, r9 `[a-second-press-once-the-removal-began]`, r12 `[SIGINT]`, at_no_leak interrupted run; W2-56 s12 `ending_signal...[SIGINT]`, `temp_folder...[SIGINT]` |
| after (8f40881d9) | td-1 | fg | 0 | 3 | 29 passed (26.9-28.4 s) |
| after (8f40881d9) | td-1 | setsid-bg | 1 | 3 | 29 passed (24.0-27.9 s) |
| after (7cde9429e) | lead, TMPDIR in /tmp | fg | 0 | 3 | 29 passed (23.2-23.5 s) |
| after (7cde9429e) | lead, TMPDIR in /tmp | setsid-bg | 1 | 3 | 29 passed (22.5-23.0 s) |
| after (7cde9429e) | lead, TMPDIR in /tmp | bg-job | 1 | 3 | 29 passed (21.7-21.9 s) |

td-1's runs were inside the launch sandbox, where `/tmp` is read-only: its TMPDIR fell back to the tree (a
`pytest-of-usain/` left in W2-177-tests, removed by the lead, never committed); the lead's runs repeat them with TMPDIR
in `/tmp`. Run files: `.gov-runtime/scratch/acc-forms/{lead-after,lead-after-fg}/` (this tree) and
`W2-177-tests/.gov-runtime/scratch/acc-forms/{before,after}/` (td-1's).

W2-56's two SIGINT ending cases (DAEO-wnnz, a non-goal) are green after the revision in every form: their cause was
(B), as S1 said.

### The lead's verify (head 7cde9429ea0c, `lead_verify.sh`: `setsid ... &`, SIGINT ignored, empty HOME)

`RED parallel exit 1 in 1045 s (4270 tests 1 failed 0 errors 10 skipped)`, `.gov-runtime/scratch/lead/log/verify/`.
The six cases of this ticket, its five new cases, the four W2-96 acceptance cases and W2-02's core-schema case (run
1's five reds) all pass. The one red is not this ticket's:
`tests/unit/orchestration/test_w2_149_indep_launch.py::test_f6_a_failed_canary_keeps_its_16_and_counts_its_trace`
(`assert (14 == 16)`; 14 is `indep_launch.py`'s repository/commit refusal, lines 2209-2216). Not in `skip_known.json`.
Re-run alone once per form: green on this head (foreground 1 passed in 0.46 s; `setsid` background 1 passed in 0.28 s)
and on w2/integrate's head 6c9a5bb52 (0.41 s; 0.26 s). A load-sensitive red of the parallel run, outside this ticket's
paths; it does not fail on w2/integrate alone, so it is not named a shared base red. No other tree's verify or nightly
log names it.
The 10 skipped are the opt-in real/bwrap/scratch-tool skips (W2-56 real sandbox 4, test_dispatcher 3, W2-149 bwrap 3).

### gov accept

- `gov accept W2-177`: `ACCEPT_NO_MAP: ticket DAEO-1k7y: the README of tests/unit/accept/ maps no KPI line`. The
  ticket's `acceptance_tests.path` is `tests/unit/accept/`, which has no README map, and a README there is not in
  allowed_paths. The ticket's acceptance is the named cases (S2), run above by node id in every form.
- `gov accept W2-96` (DAEO-ouet, the revised support's folder): pass, 11 lines, 251 passed, 0 failed, 0 skipped.
- `gov accept W2-56` (DAEO-wnnz, the revised support's folder): 19 of 20 lines pass, totals 292 passed, 0 failed, 4
  skipped; line success-13 holds one case only, `test_s13_real_sandbox_...`, skipped here by design (the CTO's real
  run; W2-56's README lines 139, 161). Not this ticket's.
Outputs: `.gov-runtime/scratch/lead/accept/{W2-96,W2-56}.json`, each run through `heavy_slot.sh`.
