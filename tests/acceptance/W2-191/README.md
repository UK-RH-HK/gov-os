# W2-191 acceptance tests: the test map accepts any project-relative test target

Ticket DAEO-v6pf (W2-191), profile STANDARD, class C2. Written by the independent test designer (MR-3) from the
ticket's KPI lines S1, S2 and F1 as described behaviour (DEC-136), before any implementation, reading only the code as
it stands at the ticket's base (`dbaf4474e`): `gov.close.select` (`load_map`, `_schema`, `scoped`, `plan`, `unresolved`,
`_within`), `gov.close.batch.reused_form`, `gov.store.loader` (`SCHEMA_DIRS`), the kernel's
`template/governance/kernel/schemas/test-map.schema.json`, and `tests/unit/close/test_select.py`,
`tests/unit/close/test_w2_115_select.py`, `tests/acceptance/W2-66/` for method. DEC-1199 (2): the test map accepts any
project-relative test target, for 0.1.2. In the ticket's numbering: `success-1` is S1, `success-2` is S2 and
`failure-1` is F1.

## How they run

    env TMPDIR=<scratch> HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest -p no:cacheprovider -o tmp_path_retention_policy=failed tests/acceptance/W2-191 -q \
      -m "not local_only" -k "not real and not green_here and not time_limit"

About 4 s for the 28 cases, in process, no network, no model (one case starts `gov close --select` as a process, from
the tree's own `src`). No case is marked `skip`, `xfail` or `flaky`, none is `local_only`, and no case name holds
`real`, `green_here` or `time_limit`, so the whole-folder run selects all 28. No loop is a `parametrize` (the tree's
opt-in list keeps one row of one): a loop inside a case names the failing form in its assertion.

## The planted project (`w2_191_support.plant`)

One git repository per case under `tmp_path`, built from nothing, every git call pinned (no system or user
configuration): a ticket `T-0001` (WBS `W-1`; its own acceptance folder holds no suite, so the own suite selects
nothing and every expected selection is exact), a test map, `governance/project/close.yaml` (`close: scoped`), suites
outside `tests/` (`governance/scripts/tests/`, `product/tests/test_a.py` with `test_case` and `TestK::test_m`,
`checks/`), suites under `tests/unit/`, a coupled input `governance/scripts/rules.txt` (not Python, so no import
places it: only a coupling can), a record `docs/notes.md`, and, beside the project, `outside/` holding real suites an
escaping target could name. The ticket's work is a commit with `Task: T-0001`; `green_night()` commits a green nightly
record, the strict close's base (`plan` needs one). Nothing is written in the tree the tests run in; the schema read is
the tree's own.

## What the cases read, where the ticket states no form

- **Schema and loader.** Targets are judged by the tree's schema (`jsonschema.Draft202012Validator`), as `load_map`
  judges. A **refusal** is asserted through `select.load_map(root)`: `(None, reason)`, the reason a non-empty string;
  no reason name is pinned (the ticket names none). The refusal may come from the schema's pattern or from the loader
  (F1's own words), so no case asserts it of the schema alone. Acceptance is asserted both of the schema alone (S1) and
  of the loader on a project that holds the suites.
- **"Names no existing folder or file"** (F1): never selected as resolved, **refused by the loader or by the
  selection, either**. `select.scoped` raises `SelectionRefused`, and `select.plan` is `scope` `full` with a non-empty
  `why_full` (today `UNRESOLVED_TARGET`). Three kinds are tried, each in every place a target may stand: a folder that
  is not there, a file that is not there, and a case that is not in its file.
- **`..` that stays inside** (`tests/../product/tests`, a real folder of the project): S1 says "a path with `..` is
  refused" and the ticket's approach says "no `..` segment"; read literally, so it is refused.
- **A symlink out**: a symlinked folder (`tests/linked` to a real suite in `outside/`), and a symlinked folder above
  the suite (`linkedproduct/tests` with `linkedproduct` pointing at `outside/`), each named as the folder, as a file in
  it, and (for `tests/linked`) as a node id. A symlink to a place inside the project is not asserted either way.
- **S2's selection** is read at the selection's interfaces: `select.scoped` (and `gov close --select <ticket>` as JSON
  on stdout, exit 0), `select.plan` (`scope`, `why_full`, `selected` as `{target, why}`) and `batch.reused_form`
  (`selected`, `ignore`, `deselect`; `select.runs` shows the entry is neither ignored nor deselected).
  `scoped` drops a target that lies inside another selected folder (its own `_within` rule), so a record-reading
  node inside a coupled folder is not listed beside it; one case pins that.

## KPI lines, cases and the outcome at the base (`dbaf4474e`)

28 cases: **18 red, 10 green (guards)** (td-1's 27, then td-2's one). Every red fails on its own line's behaviour: the schema's `^tests/` refuses
what the line says validates (`'governance/scripts/tests' does not match '^tests/'`), so `load_map` gives
`TEST_MAP_UNREADABLE`, `scoped` raises `SelectionRefused` ("the test map ... cannot be read (TEST_MAP_UNREADABLE)"),
`plan` goes `full` with `TEST_MAP_UNREADABLE`, and `gov close --select` exits 2; and, for the three escapes that begin
with `tests/`, `load_map` gives the map (the pattern takes it) in every place. None fails on a premise about the
fixture (the guards prove the fixture selects as expected on the base). The 10 guards are green on the base and must
stay green.

| KPI line | Test (node id) | At the base | Why |
|---|---|---|---|
| success-1 | `test_w2_191_schema.py::test_s1_the_schema_accepts_project_relative_targets_in_every_place` | red | the schema refuses every form outside `tests/` in all three places (`does not match '^tests/'`) |
| success-1 | `test_w2_191_schema.py::test_s1_the_schema_accepts_the_example_map_of_the_line` | red | the line's own example (`governance/scripts/tests`, `product/tests/test_a.py`) is refused by `^tests/` |
| success-1 | `test_w2_191_schema.py::test_s1_the_loader_takes_a_map_naming_existing_suites_outside_tests` | red | `load_map` gives `TEST_MAP_UNREADABLE` |
| success-1 | `test_w2_191_schema.py::test_s1_the_loader_takes_a_map_naming_one_suite_in_each_place` | red | `load_map` gives `TEST_MAP_UNREADABLE` in each place |
| success-1 | `test_w2_191_schema.py::test_s1_tests_targets_validate_as_today_guard` | green (guard) | `tests/` targets in every place and form validate before and after |
| success-1 | `test_w2_191_schema.py::test_s1_an_empty_or_non_text_target_is_still_refused_guard` | green (guard) | `""`, `null`, a number and a list stay refused (the widened pattern keeps a non-empty string) |
| success-1 | `test_w2_191_escapes.py::test_f1_an_absolute_path_is_refused_guard` | green (guard) | an absolute path (inside, a real file or folder; outside; `/`) is refused today by `^tests/`; must stay refused |
| success-1 | `test_w2_191_escapes.py::test_f1_a_path_climbing_out_without_a_tests_beginning_is_refused_guard` | green (guard) | `../outside/suite`, `governance/../../outside/suite`, `<suite>/..`: refused today by `^tests/`; must stay refused |
| success-1 | `test_w2_191_escapes.py::test_f1_a_target_with_a_dot_dot_segment_is_refused_even_where_it_stays_inside` | red | `tests/../product/tests` begins `tests/`: the map loads today in every place |
| failure-1 | `test_w2_191_escapes.py::test_f1_a_target_beginning_tests_that_climbs_out_of_the_project_is_refused` | red | `tests/../..`, `tests/../../outside/suite`, `tests/../../outside/suite/test_o.py::test_ok`: the loader takes the map in every place |
| failure-1 | `test_w2_191_escapes.py::test_f1_a_symlink_under_tests_that_points_out_of_the_project_is_refused` | red | `tests/linked` (a symlink to a real suite outside), as a folder, a file and a node id: the loader takes the map in every place |
| failure-1 | `test_w2_191_escapes.py::test_f1_a_symlink_out_of_the_project_is_refused_where_the_name_is_not_under_tests_guard` | green (guard) | a symlinked folder and a symlinked folder above the suite, named outside `tests/`: refused today by `^tests/`; must stay refused |
| failure-1 | `test_w2_191_escapes.py::test_f1_an_absolute_path_is_refused_guard` | green (guard) | as above: absolute targets stay refused (F1 lists "absolute") |
| failure-1 | `test_w2_191_escapes.py::test_f1_a_path_climbing_out_without_a_tests_beginning_is_refused_guard` | green (guard) | as above: `..` targets stay refused (F1 lists ".." ) |
| failure-1 | `test_w2_191_escapes.py::test_f1_a_target_naming_nothing_is_not_selected_as_resolved_guard` | green (guard) | a missing folder, file or case, in every place, is refused today (the loader, by `^tests/`); after the change, by the loader or the selection |
| failure-1 | `test_w2_191_escapes.py::test_f1_the_strict_close_does_not_scope_on_a_target_naming_nothing_guard` | green (guard) | `plan` is `full` today (`TEST_MAP_UNREADABLE`); after the change it must be `full` (`UNRESOLVED_TARGET`) |
| failure-1 | `test_w2_191_selection.py::test_f1_a_tests_only_project_selects_its_coupling_as_before_guard` | green (guard) | change `data/t.txt`: `scoped` suites exactly `["tests/unit/test_data_contract.py"]`, `why` `{that: ["COUPLING data/t.txt"]}` |
| failure-1 | `test_w2_191_selection.py::test_f1_a_tests_only_project_selects_its_record_reading_as_before_guard` | green (guard) | change `docs/notes.md`: `scoped` suites exactly `["tests/unit/test_records.py"]`, `records_only` true |
| failure-1 | `test_w2_191_selection.py::test_f1_a_tests_only_project_plans_as_before_guard` | green (guard) | at a green base, change `data/t.txt`: `plan` scoped, `selected` exactly `tests/unit` (UNIT), `tests/unit/test_data_contract.py` (COUPLING), `tests/unit/test_records.py` (RECORD_READING); `reused_form` selects `tests/unit/test_records.py` alone |
| success-2 | `test_w2_191_selection.py::test_s2_a_change_a_coupling_maps_to_an_outside_suite_selects_that_folder` | red | the map is unreadable: `SelectionRefused` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_gov_close_select_prints_the_outside_suite` | red | `gov close --select` exits 2 with `SELECTION_REFUSED` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_the_strict_close_plan_selects_the_outside_suite_for_a_coupled_change` | red | `plan` is `full`, `why_full` `[TEST_MAP_UNREADABLE]` |
| success-2 | `test_w2_191_selection.py::test_s2_a_coupling_to_a_node_id_in_a_file_outside_tests_selects_that_node` | red | `SelectionRefused` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_a_coupling_the_change_does_not_reach_selects_nothing_of_it` | red | `SelectionRefused` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_a_record_only_change_runs_the_record_reading_target_outside_tests` | red | `SelectionRefused` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_the_plan_selects_the_record_reading_target_outside_tests` | red | `plan` is `full` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_the_record_reading_set_of_a_reusing_close_holds_the_target_outside_tests` | red | the map is unreadable, so `reused_form` selects no record-reading target (`selected` is `[]`) |
| success-2 | `test_w2_191_selection.py::test_s2_every_close_outside_tests_joins_a_change_holding_a_record_and_code` | red | `plan` is `full` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_selection.py::test_s2_targets_outside_tests_and_under_it_select_together` | red | `SelectionRefused` (`TEST_MAP_UNREADABLE`) |
| success-2 | `test_w2_191_run_line.py::test_s2_the_strict_and_reused_close_run_line_collects_the_targets_outside_tests` | red | `command._scope_form` adds only `--ignore`/`--deselect`: `pytest <root>/tests --ignore <own> <options>` collects nothing of the selected `governance/scripts/tests`, `product/tests/test_a.py::test_case` (strict and reused form); the `tests/` side and the premise hold ("the strict close's run line collects outside tests/: []") |

"The existing close selection cases (tests/unit/close) pass unchanged" (failure-1) is mapped in prose: it is the lead's
run of `tests/unit/close` (the designer ran `tests/unit/close/test_select.py` and `tests/acceptance/W2-66`: 163 passed
on the base, the 65 `real`/`green_here`/`time_limit`/`local_only` cases left out). The three `..`, symlink and
absolute guard groups and the "names nothing" guards pass on the base for one reason, the schema's `^tests/` pattern,
which the change replaces: they are the cases that hold the refusals once it does.

## The run line (td-2, P-W2-191-1 (b), DEC-1156 (7))

`test_w2_191_run_line.py` (one case, written by a second test designer on the ticket lead's brief td-2, from S2 as
described behaviour): the strict close (`plan`, scoped) and the reusing close (`batch.reused_form`) run
`pytest <root>/tests --ignore <own suite>` plus `gov.close.command._scope_form(root, scope, <own suite>)`, and a selected
target outside `tests/` is not collected by `pytest tests`. The case builds that argument list as the close does and
reads what `pytest --collect-only -q` collects with it, in the planted project's folder (importlib import mode, so two
files of one name do not clash in the observation); the form of `_scope_form`'s arguments is not pinned.

- **The scope** is a real `select.plan` (strict, scoped) and `batch.reused_form` of the planted project, not a
  hand-built dict, from a project that carries a **project-local, relaxed copy of the test-map schema** (`target` any
  non-empty text; `w2_191_support.relaxed_schema_files`): the loader reads the project's kernel schema before the
  tree's, so the map naming outside targets is read on the base too, and the case is red for the run line, not for
  the schema's `^tests/` (whose new bytes come by the owner's approval, CIT-P). The case asserts that premise first
  (the plan is scoped and selects the outside targets).
- **Asserted** (exact sets, not subsets): the strict run line collects, outside `tests/`, every case of the selected
  folder `governance/scripts/tests` and the named node `product/tests/test_a.py::test_case` alone (not
  `TestK::test_m`, not `checks/`); under `tests/`, exactly what it collected before (`tests/unit` and the selected node
  of a partly selected suite; the file, node and suite left out are not collected). The reusing close's line collects
  the record-reading set alone: the outside node and the one `tests/` node. A project with `tests/` targets only
  collects as before (strict and reused).
- **Red at the base:** the premise and the `tests/` side hold; the first failing assertion is the outside side:
  "the strict close's run line collects outside tests/: []". Sanity: with a stand-in `_scope_form` that appends each
  selected outside target as a positional argument (a throwaway, run from a scratch folder, not committed) the case
  passes.

## Open

- **S2's "record_reading targets outside tests/ run in the record-reading set"** is now covered at the selection (td-1's
  cases: `scoped`, `plan`, `reused_form`) and at the close's run line (td-2's case above), per P-W2-191-1 (b).
- **Not covered:** the whole `_run_tests` (the parallel and serial-only forms, `--tb` and timeout options) is not run;
  the case asserts the arguments `_scope_form` returns, as the ticket names it. A serial-only entry (`serial_only.entries`)
  outside `tests/` is out of the ticket's lines and not asserted.
