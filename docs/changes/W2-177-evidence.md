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

## The fix (steps 2 and 3, to follow)

1. (A) `runner._run`: keep the caller's `PYTHONUSERBASE` in the child's environment; every other `PYTHON*` variable
   stays dropped, `PYTHONPATH` and `PYTHONDONTWRITEBYTECODE` as they are.
2. (B) `w2_96_reap.launch_gov`: SIGINT, SIGTERM and SIGHUP are set to SIG_IGN when named in `ignore`, and to
   SIG_DFL otherwise. `gov accept` keeps an inherited ignore unchanged (R11 stays green).
3. New cases `tests/unit/accept/test_w2_177_start_forms.py`, written red first.
