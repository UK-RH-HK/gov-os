# W2-66 acceptance tests — path-scoped regression at close: selection and evidence

Ticket `DAEO-c1uz` (W2-66), profile FULL. Written by the independent test designer (MR-3) before the
implementation, from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md` §2), DEC-880 item 2, DEC-883,
DEC-884, DEC-889, DEC-890, DEC-891, DEC-892, DEC-896 item 2, DEC-899 (P-IS-1 and P-IS-2, both (a)), lens I's
synthesis §4 and its four area reports, and lens H's report. No implementation was read; the existing code was
read as it stands on `w2/integrate` for its public interfaces only (the close's envelope, its record, its
settings, its test runs).

## How the suite runs

- **The code under test is this worktree's `src/`** (DEC-732). Run the suite with
  `PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-66`. Every `gov` the suite starts goes through
  W1-07's console-script stand-in with `PYTHONPATH=<worktree>/src` (`w1_30_support.run_gov`, `sandbox_env`); the
  nightly command is started as `python3 -m gov.close.nightly` in the same environment
  (`w2_66_support.run_nightly`). Nothing uses an installed `gov`.
- **Fixture repositories.** Every project is a temporary git repository built from scratch under pytest's
  `tmp_path` (`w2_66_support.Fixture`): a dozen tickets with `wbs_id` and `allowed_paths`, one small suite each,
  `tests/unit`, a serial-only list, a path map, a test map, a register, and a handful of one-line source files.
  No test copies this repository's tree. The fixture's `src/gov/__init__.py` is a stand-in that appends this
  worktree's `gov` folder to the package's path, so a child of the close that imports `gov` finds the code under
  test behind the fixture's own one-line files.
- **What ran is told by the tests themselves:** every fixture test is W1-30's "telling test": each run adds a line
  to a file of its own outside the project, with the xdist worker it ran in. A case asserts on what ran, on the
  close's evidence block, and on the JUnit XML, never on timings.
- The live test map cases (`test_w2_66_live_test_map.py`) read this repository's tracked tree and write nothing.
- Deterministic; no network; nothing `local_only`.

## The fixture project (`w2_66_support.SUITES`)

| Suite | Ticket's paths | Role in the cases |
|---|---|---|
| `W2-aa` | `src/gov/widget/**` | the ticket closed (`PROJ-aaaa`) |
| `W1-bb`, `W2-bz` | `src/gov/widget/**`, `src/gov/widget/thing.py` | overlap a widget change; W1-bb imports a name from a bare `conftest` (W1-35's form, lens H finding 17), so a run given the two folders as a list cannot collect it |
| `W2-cc`, `W1-dd` | gadget, gizmo | not reached by a widget change |
| `W1-gg`, `W1-hh`, `W2-ii` | gear, hinge, idle | `gg_support` (W1-gg) is imported by `hh_support` (W1-hh), imported by W2-ii |
| `W1-rr` | reader | `test_rr_records.py` reads the register: the record-reading set |
| `W1-ec` | contract | `test_ec_contract.py` runs on every close (W1-07's three contract files' kind) |
| `W1-cp` | coupled | declared coupling: `src/gov/textread/data.txt` is read by it as text |
| `W2-zz` | `src/gov/close/**` | another ticket's shared-core work |

The base: a green nightly record naming the initial commit, committed after it by the orchestrator (a
record-only commit inside the change).

## Interface

What the KPI lines leave open, fixed as little as the tests need. Anything unknown or unreadable fails safe:
the full regression, never less.

1. **The test map** `governance/project/test-map.yaml` (YAML mapping), its schema
   `template/governance/kernel/schemas/test-map.schema.json` (JSON Schema draft 2020-12, as its siblings), and
   the template's copy `template/governance/project/test-map.yaml` (valid against the schema). Keys:
   - `version`: `1`.
   - `shared_core`: list of path patterns (required, non-empty). A changed path matching one runs the full
     regression.
   - `record_only`: list of path patterns. A changed path matching one is placed and selects no suite by itself.
   - `record_reading`: list of pytest targets (a folder, a file, or a node id or its beginning, relative to the
     project), run on every close whatever else is selected.
   - `every_close`: list of pytest targets run on every close.
   - `couplings`: list of `{paths: [patterns], suites: [targets], why: <text>}`; a changed path matching one of
     `paths` selects each of `suites`.
   - `test_inputs`: the path map's `test_inputs` list, moved here (DEC-896 item 2).
   - `per_test_timeout`: seconds, a positive number; default `900` when absent.
   - `distribution`: the parallel runs' pytest-xdist `--dist` mode; default `load` when absent.
   - **Patterns** use the grammar of a ticket's `allowed_paths` as the close reads them on the base: `**` any
     characters, `/` included; `*` any characters but `/`; everything else literal; the whole path. No `?`,
     `[]` or `{}`.
   - A test map that is missing, is not YAML, is not a mapping, or is not valid against the schema runs the full
     regression (`TEST_MAP_MISSING`, `TEST_MAP_UNREADABLE`).
   - A schema that refuses a map without `shared_core`, or with a wrong type under `shared_core` or `record_only`.
2. **The base** (the last fully green commit) is the newest commit, among those the green records name, that is
   `HEAD` or an ancestor of it. Green records, read from the tree being closed:
   - every close record `docs/close/*/CL-*.md` whose `evidence.scope` is `full` (its `evidence.head`);
   - every nightly record `docs/close/nightly/*.json` whose `verdict` is `green` (its `head`).
   No such record, or none naming a commit of `HEAD`'s history: the base is unknown (`base: null`) and the run is
   full (`BASE_UNKNOWN`). **The change** is every path `git diff --name-only <base> HEAD` names, with git's rename
   detection off (`--no-renames`): **a moved file is in the change at both its paths**, the path it left and the
   path it reached, and every rule of item 3 and the full-run reasons read both (a file moved out of the shared
   core runs the full regression, `SHARED_CORE` naming the path it left; a file moved away from a ticket's
   `allowed_paths` selects that ticket's suite, `OVERLAP` naming the path it left). The evidence's `changed`
   names both.
3. **The selection.** The ticket's acceptance run stays as it is. The regression run keeps the full run's form:
   `pytest tests` with `--ignore=<path>` (and `--deselect=<node id>` where a target is finer than a file) for
   what is left out, never a list of folders. **A ticket's suite** is its acceptance folder as W2-07's gate reads
   it (`acceptance_folder` in `src/gov/close/gates.py` on the base): the folder its ticket file declares in
   `acceptance_tests.path` (DEC-892; W2-67, W2-63 and W2-70 declare `tests/acceptance/W1-27/`, `W1-49/` and
   `W1-05/`), else `tests/acceptance/<wbs_id>/`; a ticket **has a suite** when that folder holds a test file
   (`test_*.py`). The closing ticket's own suite is its suite: `selected` names that folder with `OWN`, and none
   of its files is in `left_out` (the acceptance run runs it whole). Every target `selected` names exists in the
   tree closed. It runs: `tests/unit`; the suite of each ticket (any wave) whose `allowed_paths` match a changed
   path (`OVERLAP` naming that ticket, whatever folder its suite is); a suite holding
   a changed file; a suite that imports a helper module of a suite whose folder holds a changed file, directly or
   through another helper (imports read from the test files: `sys.path` folders of other suites and `import x`);
   each coupling's suites; `every_close`; `record_reading`. A changed path is **placed** when the `allowed_paths`
   of a ticket that has a suite, a coupling, `record_only` or a suite folder (`tests/unit`, `tests/acceptance/<x>/`)
   holds it. A path that only the `allowed_paths` of tickets without a suite hold (no declared folder with a test
   file, no `tests/acceptance/<wbs_id>/` with one) maps to no suite: it is not placed. An **unplaced** path runs the
   full regression (`UNPLACED`, naming it). The serial-only cases (`tests/acceptance/serial-only.txt`)
   run afterwards, alone, only those inside what the regression runs; `test_runs`' serial-afterwards run names
   them under `cases` (as today).
4. **`gov close <ticket> --full`** runs the full regression (`FULL_ASKED`).
5. **`gov close <ticket> --check-result <file>`**: the pre-close gate's own `gov check --json` output. The close
   hands every test run the variable `GOV_CLOSE_CHECK_RESULT` naming a file whose content is that output, so the
   record-reading set's context-reproducibility and core-schema cases read it instead of running `gov check`
   again. *The observable:* a record-reading test of the fixture reads the file the variable names, and its
   content is the gate's output byte for byte.
6. **The evidence block** `evidence`: in the close record's frontmatter and under `result.evidence` of a passed
   close (the same object), and under `error.details.evidence` of a refused close (as `test_runs` is today).
   No change to `close.schema.json` (W2-64's line). Fields:
   - `scope`: `scoped` or `full`; `why_full`: list of `{reason, paths?}` with `reason` one of `FULL_ASKED`,
     `SHARED_CORE`, `UNPLACED`, `TEST_MAP_MISSING`, `TEST_MAP_UNREADABLE`, `BASE_UNKNOWN` (`paths` names the
     changed paths for `SHARED_CORE` and `UNPLACED`); empty or absent for a scoped run.
   - `base` (full commit id or `null`), `head` (full commit id), `tree` (`HEAD^{tree}`), `changed` (list of paths).
   - `selected`: list of `{target, why: [{reason, …}]}`, one for each target run, the own suite included. Reasons:
     `OWN`; `UNIT`; `OVERLAP` with `ticket` and `paths` (the changed paths its `allowed_paths` hold);
     `TEST_CHANGED` with `paths`; `HELPER` with `helper` (the changed helper's path) and the chain; `COUPLING`
     with `paths`; `EVERY_CLOSE`; `RECORD_READING`; a full run may name `tests` with `FULL`.
   - `left_out`: list of `{target, why: [{reason: NOT_REACHED}]}`, every acceptance suite (or each of its files,
     where some of its files ran) the run left out; empty for a full run.
   - `skips`: list of `{test, reason}`, every skipped case; `skip_count`: their number.
   - `failures`: list of `{test, text}`, every failing or erroring case, `text` its failure text kept.
   - `junit_xml`: list of paths, relative to the project, of each run's JUnit XML file; each exists after the
     close. A refused close leaves nothing untracked that git does not ignore but its repair ticket (DEC-490):
     its XML goes under `.gov-runtime/`.
   - `per_test_timeout` (seconds) and `distribution` (mode), as the runs used them.
   - `tmp_path_retention_policy`: `failed`, the value every test run of the close was given (item 9).
   - Every case run is in the JUnit XML files; the record does not list 15,000 node ids itself.
7. **The per-test limit:** every test run a close or the nightly makes runs with pytest-timeout,
   `--timeout=<per_test_timeout>` and the `signal` method; a test over it fails with pytest-timeout's text, which
   names the limit. Where pytest-timeout cannot be loaded by the runs' interpreter, the close is refused
   `TIMEOUT_PLUGIN_ABSENT`, exit code 1, nothing recorded.
8. **The nightly command:** `python3 -m gov.close.nightly <branch> --root <project> [--coverage] --json`.
   - Runs the full uncached regression on `<branch>`'s head (not the working tree) in the close's form (parallel,
     then the serial-only cases alone; the per-test limit; the distribution mode; the retention option, item 9),
     with JUnit XML.
   - Writes its record `docs/close/nightly/NR-<UTC stamp>-<head12>.json` in the project's working tree. Prints
     an API-0002 envelope: green: `ok: true`, exit 0, `result.record`; red: `ok: false`, exit 3,
     `error.details.record`.
   - The record: `branch`, `head`, `tree`, `base` (the last green night's head before it, or `null`), `scope:
     full`, `verdict` (`green` or `red`), `junit_xml` (as above), `failures`: `{test, text, alone: passed|failed,
     class: red|flaky_candidate}` (every failing test re-run alone), `packages`: `{priority: P1, kind, test, …}`,
     and with `--coverage`, `measured_map`.
   - A red that fails alone: kind `bisect`, `range` `<last green head>..<head>`, `first_bad` (the full id `git
     bisect run` found). A red that passes alone: `class: flaky_candidate`, never bisected.
   - A red that a scoped close since the last green night left out, or ran and passed: kind `selection_miss`,
     naming the close (its ticket or record), with `test_map_correction: {couplings: [{paths, suites, why}]}`
     that takes the close's changed paths to the red test's suite.
   - `--coverage` (the weekly run): coverage.py with lens H's child-process shim; `measured_map` is the path of a
     JSON object `{source path: [node ids that executed it]}`, child processes included.
9. **The retention option** (DEC-905, DEC-904 item 1): every pytest run a close makes (the acceptance run, the
   regression's parallel run, the serial-only cases afterwards) and every test run of the nightly is given
   `-o tmp_path_retention_policy=failed`, so a passing test's `tmp_path` goes as the test ends and a failing
   test's stays. The evidence block names it (item 6). *The observable:* a fixture test reads its run's
   `config.getini("tmp_path_retention_policy")` (`failed`) and `config.option.override_ini` (holding
   `tmp_path_retention_policy=failed`), and whether its `tmp_path` is still there after the close. pytest's own
   count of three base folders stays: the fixture's refused close has two failing runs.

## KPI map

Expected red reason on the base: **(a)** no evidence block in the close's result or refusal (no scoping, no
evidence); **(b)** `--full` or `--check-result` unknown (argparse: no JSON envelope); **(c)** no
`gov.close.nightly`; **(d)** no test map, schema or template copy; **(e)** no per-test limit (a hung test runs to
its end; a close without pytest-timeout passes); **(f)** no report. **Then (g):** once built, in this worktree
every case that runs a close or the nightly is red until the owner installs pytest-timeout (Interface item 7:
`TIMEOUT_PLUGIN_ABSENT`), the plugin-absent case excepted, which turns green. **(h)**, added with DEC-905 on the
built head: the close's and the nightly's test runs are not given the retention option (the fixture's tests
report `tmp_path_retention_policy` `all` and no such `-o`; a passing test's `tmp_path` is still there after the
close), and the evidence block does not name it.

### Part 1 — the selection (fixture repositories)

| KPI line | Tests | Red on the base |
|---|---|---|
| S1 own suite, `tests/unit`, overlapping tickets' suites; the base; record-only commits in the change; helpers followed; the full run's form; each suite named with why | `test_w2_66_scoped_selection.py` (all but the two below); `test_w2_66_followed_couplings.py::test_a_changed_helper_selects_every_suite_that_imports_it_directly_or_through_another_helper`; `test_w2_66_full_widening.py::test_a_passed_full_close_is_the_base_of_the_next_scoped_close` | (a); the last (b) |
| S2 + F1 the shared core, unplaced, missing or unreadable map, unknown base | `test_w2_66_full_widening.py`: shared core ×4 (fixture list, path map, test map, own commit), unplaced, missing, unreadable ×3, no green record, a record naming no commit ×2, a red night | (a) |
| S3 couplings; every-close files | `test_w2_66_followed_couplings.py::test_a_declared_coupling_selects_its_suites_and_names_why`; `test_w2_66_scoped_selection.py::test_the_every_close_files_run_and_are_named`; the live map's couplings (Part 2) | (a) |
| S4 serial cases scoped, the record says which | `test_w2_66_scoped_selection.py::test_the_serial_cases_of_the_selected_suites_run_alone_and_only_those`, `::test_the_record_says_which_serial_cases_ran` | both serial cases run today |
| S5 + F3 the record-reading set on every head; record-only widens nothing; the gate's check result | `test_w2_66_scoped_selection.py::test_the_record_reading_set_runs_on_a_scoped_close_and_is_named`; `test_w2_66_followed_couplings.py::test_a_record_only_commit_widens_nothing`, `::test_a_record_reading_test_turned_red_by_a_record_only_commit_refuses_the_scoped_close`, `::test_the_record_reading_set_reads_the_pre_close_gate_s_own_check_result` | (a); the last (b) |
| S7 `--full` | `test_w2_66_full_widening.py::test_full_runs_the_full_regression_and_the_record_says_so` | (b) |

### Part 2 — the evidence block, the live test map, the lead's verification

| KPI line | Tests | Red on the base |
|---|---|---|
| S6 + F2 the evidence block | `test_w2_66_evidence.py` (8); `test_w2_66_scoped_selection.py::test_the_close_record_holds_the_same_evidence_block`, `::test_the_junit_xml_holds_every_case_run_and_no_case_left_out`, `::test_a_one_module_change_is_stated_scoped_never_full`, `::test_the_head_and_the_tree_are_stated` | (a); `test_a_refused_close_leaves_nothing_untracked_but_its_repair_ticket` is green on the base (nothing is written today) |
| S2, S3, S5, S8, S9 in the live map; DEC-891's list exactly; no hidden code; `test_inputs` moved | `test_w2_66_live_test_map.py` (68 cases) | (d) |
| S12 the lead's verification unchanged | `test_w2_66_lead_verification.py` (2) | **green on the base by design**: they hold that nothing this ticket builds changes what a plain `pytest tests` reads or collects (no configuration file, conftest outside this folder or serial-only list changed against `w2/integrate`; a fixture's test map changes nothing a plain run collects) |

### Part 3 — limits, distribution, nightly, report

| KPI line | Tests | Red on the base |
|---|---|---|
| S8 + F4 per-test limit, failure names it; no silent pass without it | `test_w2_66_limits.py::test_a_hung_test_fails_at_the_per_test_limit_and_the_failure_names_the_limit[parallel]`, `[serial-afterwards]`, `::test_without_pytest_timeout_the_close_does_not_pass_silently`; `test_w2_66_live_test_map.py::test_the_per_test_limit_is_above_the_slowest_test_measured`; `test_w2_66_scoped_selection.py::test_a_scoped_close_states_its_settings_defaults` | (e), (a) |
| S8b the retention option on every run, the evidence names it; the nightly's runs too [DEC-905, DEC-904 item 1] | `test_w2_66_retention.py` (8): `::test_every_test_run_of_the_close_is_given_the_retention_option[acceptance]`, `[parallel]`, `[serial-afterwards]`; `::test_a_passing_test_s_folder_goes_and_a_failing_test_s_stays[parallel]`, `[serial-afterwards]`; `::test_the_refused_close_s_evidence_names_the_option`; `::test_a_passed_close_names_the_option_in_its_result_and_its_record`; `::test_the_nightly_run_s_test_runs_are_given_the_retention_option` | (h) |
| S9 + F4 distribution one setting, default, no worksteal | `test_w2_66_limits.py::test_the_distribution_mode_is_one_setting_and_the_runs_follow_it`; `test_w2_66_live_test_map.py::test_the_distribution_mode_stays_the_default_and_is_not_worksteal`; the settings-defaults case above | (a), (d) |
| S10 the nightly | `test_w2_66_nightly.py` (5): the branch's head with JUnit XML; bisect P1; flaky candidate; selection miss with the map corrected; the weekly coverage map across child processes (coverage 7.16.2 is installed in the test interpreter; the case skips where it is not) | (c); the selection-miss case first fails at its scoped close (a) |
| S11 the report | `test_w2_66_research.py` (3) | (f) |
| S13 W1-30's revision | `tests/acceptance/W1-30/test_w1_30_close.py::test_regression_includes_other_acceptance_folders` (revised, green on the base and after: a project without a test map runs everything); `tests/acceptance/W1-30/test_w1_30_regression_scope.py` (4) | the new file: (a), (b) |

### Part 4 — the FULL review of 9174e358 (described behaviours, DEC-136)

Written by a fresh test designer after the implementation was built, from the review's described behaviours; no
implementation read. Expected red reason on the built head `9174e358`: **(i)** the change is read with git's rename
detection, so a moved file is in it at the path it reached only (`changed` lacks the path it left; a file moved out
of the shared core runs `scoped`; the suite of the ticket whose paths the file left is `NOT_REACHED` and the close
passes); **(j)** the overlap rule and the own suite read `tests/acceptance/<wbs_id>/` only, never the declared
`acceptance_tests.path` (the declared folder is left out `NOT_REACHED`; `OWN` names the WBS id's folder, and the
declared folder's files are in `left_out`); **(k)** a path that only suiteless tickets' `allowed_paths` hold is
taken as placed (the run is `scoped` and selects nothing for it beyond the always-run set).

| KPI line | Tests | Red on the built head |
|---|---|---|
| S1, S2 + F1 a moved file at both its paths (Interface item 2) | `test_w2_66_moved_files.py` (3): `::test_a_file_moved_out_of_the_shared_core_runs_the_full_regression`, `::test_a_file_moved_away_from_another_ticket_s_paths_selects_that_ticket_s_suite`, `::test_a_file_moved_into_the_shared_core_runs_the_full_regression` | (i); the last runs full today and is red only on `changed` lacking the path the file left |
| S1, S6 a ticket's suite is its declared folder (Interface item 3) | `test_w2_66_declared_folders.py` (2): `::test_the_overlap_rule_selects_a_ticket_s_declared_folder`, `::test_the_own_suite_is_the_closing_ticket_s_declared_folder` | (j) |
| S2 + F1 a path only suiteless tickets hold is unplaced (Interface item 3) | `test_w2_66_suiteless_tickets.py::test_a_path_only_suiteless_tickets_hold_runs_the_full_regression` (one close: one ticket declares its WBS id's folder, which does not exist; one declares a folder with a README and no test) | (k) |

### Expected green on the base

- `test_w2_66_scoped_selection.py::test_the_scoped_close_passes`: the close passes today (a full run).
- `test_w2_66_scoped_selection.py::test_the_selection_keeps_the_full_runs_form_so_a_bare_conftest_import_still_collects`:
  today's full run collects W1-bb; it turns red if the selection passes folders as a list.
- `test_w2_66_evidence.py::test_a_refused_close_leaves_nothing_untracked_but_its_repair_ticket`.
- `test_w2_66_lead_verification.py` (2), and the revised W1-30 function.

## W1-30's revision (KPI 13, I2 F9)

`test_regression_includes_other_acceptance_folders` now states its scope: its project has no test map, so the
close runs the full regression, and another ticket's red folder blocks it; it also asserts that the refusal names
that folder's failing test (so the refusal is that folder's, not a missing checkpoint's: I2 F2). The scoped cases
are in `test_w1_30_regression_scope.py`: the folder selected by its ticket's overlap runs and blocks; left out, it
is named with why; `--full` runs it whatever the change. No other expectation is lowered. Committed alone with
`Rewrite-Reason: DEC-880 item 2 (a path-scoped close runs only the suites a change can reach; I2 F9)`.

## Revisions after W2-07's merge (run 2)

Each its own commit with its `Rewrite-Reason:`; no expectation lowered.

- `test_w2_66_evidence.py::test_a_refused_close_states_its_evidence_and_says_scoped`: a refused close commits its
  repair ticket (DEC-904 item 6, DEC-903 item 3), so the head and tree it closed are read before the close, not
  from `HEAD` after it. No other case of the suite reads `HEAD` after a refused close.
- `tests/acceptance/W1-30/test_w1_30_regression_scope.py`: the closed other ticket's folder is committed by its
  test designer with its trailers, so the in-close `gov check` (DEC-868 item 1 (b)) passes and each case reaches
  the selection it states.
- `tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay`: the overlay holds the path map and
  the test map (DEC-903 item 1, DEC-896 item 2).

## Discoveries recorded for the lead

- `src/gov/errors.py`, named by the KPI line, does not exist: the envelope's error module is
  `src/gov/cli/errors.py` (I4 F12 counts it under the CLI). The live-map case requires `src/gov/cli/errors.py`.
- DEC-891's record places hold code: `governance/project/orchestration/sync_context.py`, and under `docs/plan/`
  `tools/validate_s1.py` and `wave-1-exit/apply_adapter_output.py`. The record-only list must be DEC-891's
  places without these (failure line 3); "the plan files" are held as `docs/plan/*.md` at least.
