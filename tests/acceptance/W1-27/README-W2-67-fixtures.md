# W2-67 (DAEO-9nys), round 1, batch 3: the copying fixtures and the `--basetemp` refusal

The second, fresh independent test designer of W2-67 (DEC-907 item 1 and item 2). Two pieces:

1. **the copying fixtures (KPI 1):** the per-test copies of W1-07, W1-25, W1-26 and W1-27 no longer race git's
   background gc;
2. **the `--basetemp` refusal's acceptance tests (KPI 6):** `test_w2_67_basetemp_refusal.py` and its probe
   `w2_67_basetemp_probe.py`, written before the root `tests/conftest.py` exists.

This designer did not read batch 1's KPI tests (`test_w2_67_copies.py`, `test_w2_67_temp_folders.py`,
`w2_67_tmp_probe.py`) or its `README-W2-67.md` files (DEC-907 item 1, Policy 2 (c)); it ran them and read their
results only. Every run below used this worktree's `src/` (DEC-732) and `-o tmp_path_retention_policy=failed`
(DEC-905).

## Piece 1: the copying fixtures (KPI 1; I3 F9, I4 F5, I4 §2.1)

**The race.** Each suite makes one session copy of the working tree (`live`), commits it, and copies that copy's
`.git` again for every test (`shutil.copytree`). Past about 6,700 loose objects, the session copy's first commit
starts git's automatic gc in the background, and its packing removes `.git/objects/NN` folders while a per-test
copy is reading them: `shutil.Error: … .git/objects/NN: No such file or directory`.

**The change (one file, `tests/acceptance/W1-07/w1_07_support.py`).** `copy_working_tree` sets `gc.auto=0` in
the copy's own repository config right after `git init` and before its first commit. Every copying chain of the
four suites makes its session copy through this one function:

| Suite | Session copy | Per-test copy |
|---|---|---|
| W1-07 | `conftest.live` → `copy_working_tree` | `conftest.project` / `small_project`: `shutil.copytree` |
| W1-25 | `conftest.live` → `cli_support.copy_working_tree` (+ `add_fixtures`, a commit) | `conftest.built`, `_copy`, `test_w1_25_live_session.answer`: `shutil.copytree` |
| W1-26 | `w1_26_support` → `cli_support.copy_working_tree` | its projects' later commits |
| W1-27 | `conftest.live` → `w1_27_support.copy_working_tree` (the same function) | `conftest.project`: `shutil.copytree` |

**Why it meets the KPI, and why this change is the smallest.**

- The KPI's first branch: *every per-test copy commits with `gc.auto=0`*. The setting is in the repository's
  own `.git/config`, so it travels with every `shutil.copytree` of the session copy: the session copy's first
  commit, W1-25's `add_fixtures` commit, and every later commit a case makes in its own copy (`commit_all`,
  checkpoints, W1-26's history) all run with automatic gc off. No background gc starts, so none races a copy.
- One line in the one function all four suites share; the fixtures' names, scopes and signatures are unchanged,
  and `copy_working_tree(destination, root=REPO_ROOT)` is callable as before.
- What the copies are for is kept: the same files (the held-out file left out by its path, DEC-385; the settings
  without the held-out deny rules, DEC-399), a committed repository with the same history (one commit), and no
  case's expectation changed. The second branch (copy the working files without `.git`) would have changed each
  per-test fixture in three suites and given each test a fresh commit id; not needed.
- W1-27's old-path case builds a project of its own (batch 1, commit `05d7ffd4`): left as it is.
- No `gc.auto` is set for git outside these copies: `w1_07_support.git` gives git the copy as `HOME` and
  `GIT_CONFIG_NOSYSTEM=1`, and the setting is written with `git config` in the copy's repository only.

**Shown (in this designer's sandbox, 2026-10-23):**

- Batch 1's KPI tests, `tests/acceptance/W1-27/test_w2_67_copies.py -n 2`:
  - on the head (`acb45c3c`): **3 failed, 3 passed**. Red: `test_w1_07_…`, `test_w1_25_…` and
    `test_w1_27_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc`, each with the race's
    `shutil.Error: … .git/objects/2d … No such file or directory` and "automatic gc in the session copy after its
    commit: 1 pack(s)". Green guards: the three `test_a_per_test_copy_from_the_working_files_carries_no_copied_git_while_gc_runs`
    cases (`W1-26-FullProject`, `W1-26-Project-copy_tree`, `W1-27-copy_working_tree-per-test`).
  - with the change: **6 passed**, twice (23.4 s, 25.5 s).
- W1-28's fixture-copy check, `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`: **18 passed**.
- Selections that use the changed fixtures, `-n 2`:
  - W1-07 `test_w1_07_envelope.py`: `test_status_succeeds_with_exit_code_0`,
    `test_a_governance_error_has_exit_code_1_and_its_code_in_the_json`, `test_an_unknown_command_is_a_usage_error`,
    `test_the_envelope_carries_the_session_given`: **4 passed**;
  - W1-25 `test_w1_25_record.py`: `test_a_checkpoint_is_a_file_git_can_track`,
    `test_writing_a_checkpoint_changes_nothing_else`,
    `test_the_checkpoint_records_the_ticket_the_trigger_and_the_next_step`,
    `test_the_ticket_is_an_input_with_its_id_version_and_hash`: **4 passed**;
  - W1-27 `test_w1_27_doctor.py`: `test_doctor_is_a_read_command`,
    `test_doctor_envelope_is_valid_on_healthy_project`, `test_doctor_real_registry_every_entry_reported`:
    **3 passed**.
  - No code-graph case was in these selections. The whole suites are the lead's to run, outside the sandbox.

Commit trailer: `Rewrite-Reason: the copy races git's background gc (I3 F9, I4 F5)`.

## Piece 2: the `--basetemp` refusal (KPI 6; DEC-907 item 2; DEC-898)

The KPI line: *the root tests/conftest.py refuses, at the start, a run given a per-run --basetemp, naming DEC-898;
one opt-out stays, the environment flag GOV_ALLOW_BASETEMP=1, for a measured trial.*

**How it is observed.** Each case starts a nested pytest of this repository (its root folder, `--rootdir` set, so a
root `tests/conftest.py` is loaded) on the probe `w2_67_basetemp_probe.py`, one case that records the temp folder
pytest gave it. The probe's name does not start with `test_`, so a run of `tests` never collects it. Every nested
run is bounded: the one probe case, one worker (two in the parallel cases), its own `TMPDIR` inside the case's
`tmp_path`, `-p no:cacheprovider`, a 180 s limit, no `PYTEST_*` variable or `GOV_ALLOW_BASETEMP` from the session
that runs it, and a `--basetemp` inside the case's `tmp_path`.

"Refused at the start" is read as all four of: a non-zero exit; the probe case did not run; the output names
`DEC-898`; the folder given as `--basetemp` is absent or empty (it received no test's temp folder).

| Case | Expected | On the head (no root `tests/conftest.py`) |
|---|---|---|
| `test_a_run_given_a_per_run_basetemp_is_refused_at_the_start[equals]` (`--basetemp=<dir>`) | refused | **red**: exit code 0; the probe ran once; no DEC-898 in the output; the folder given received `test_the_probe_records_its_tem0` |
| `…[separate]` (`--basetemp <dir>`) | refused | **red**, the same four reasons |
| `…[PYTEST_ADDOPTS]` (`PYTEST_ADDOPTS=--basetemp=<dir>`) | refused | **red**, the same four reasons |
| `…[parallel-n2]` (`-n 2 --basetemp=<dir>`) | refused | **red**, the same four reasons; the folder given received `popen-gw0` |
| `test_gov_allow_basetemp_1_lets_the_run_use_the_folder_it_was_given[equals, separate, PYTEST_ADDOPTS]` | goes ahead; the probe's temp folder is inside the folder given | **green: guards** (nothing refuses yet; they must stay green) |
| `test_a_flag_value_other_than_1_opens_nothing[0, true, yes, empty]` (with `--basetemp=<dir>`) | refused | **red**, the same four reasons |
| `test_a_run_given_no_basetemp_is_not_refused` | goes ahead; the temp folder under the run's own `TMPDIR` | **green: guard** |
| `test_a_parallel_run_given_no_basetemp_is_not_refused` (`-n 2`; xdist gives each worker a base folder of its own) | goes ahead | **green: guard** |

On the head (`d4874425`, no root `tests/conftest.py`), one worker: **8 failed, 5 passed in 3.65 s**. The 8 reds
fail for the four reasons in the table, which an implementation of the KPI line removes; the 5 greens are guards
that an implementation must keep green (the opt-out, and the runs given no `--basetemp`, serial and parallel).
The whole collection of `tests` (`--collect-only`) collects these 13 cases and not the probe.

**Readings this designer made (for the engineer and the auditor):**

- The forms covered are the ordinary ones a person or a script uses: `--basetemp=<dir>`, `--basetemp <dir>`,
  `PYTEST_ADDOPTS`, and the same with `-n 2`. An abbreviated option or an `addopts` line in an ini file is not
  covered: the repository has no pytest ini section.
- The refusal is of the run, not of a worker: xdist itself hands each worker a `basetemp` under the controller's
  (`…/pytest-N/popen-gwN`), so a run of `-n 2` given no `--basetemp` must go ahead, and a run of `-n 2` given one
  must be refused.
- Only the exact value `1` opens the refusal; `0`, `true`, `yes` and an empty value do not.
