# W2-95 (DAEO-57hm) acceptance tests: core-pathmap checks what it says

Written by the independent test designer (MR-3) from the ticket's KPI lines and its sources
(DEC-959 item 9, DEC-954 Q9f, DEC-381; row W2-H064; package P-W2-H064; the path map's schema
`template/governance/kernel/schemas/path-map.schema.json`), in parallel with the engineer
(DEC-959 item 7). Profile STANDARD (DEC-221): every KPI line's success and failure, and the key
edge cases. No implementation was read: the existing finding codes were seen in the check's
public output only.

## How the tests find the code under test

`w2_95_support.py` derives the repository root from its own location
(`Path(__file__).resolve().parents[3]`, that is `tests/acceptance/W2-95/` → the root) and runs
every subprocess with `PYTHONPATH=<root>/src`. Merged into `/home/usain/gov-os-worktrees/W2-95`
and run there, the tests exercise that worktree's `src/`. The declared command is read at test
time from `<root>/template/governance/kernel/checks/core-pathmap.yaml` (today
`python3 -m gov.check.pathmap`, with `python3` run as the test's own interpreter).

Every test plants its own repository in pytest's `tmp_path`: `git init`, a few files tracked
with `git add` (no commit), `governance/project/path-map.yaml`, and (untracked) a copy of the
check's declaration under `template/governance/kernel/checks/` so that `gov check` registers
`core-pathmap`. **This repository's own path map is never used** (KPI line 4 is the lead's
measure). Subprocesses get a throwaway `HOME`, no `GOV_*` variables, and git with no system or
global configuration. Deterministic, no network.

Interfaces used: the declared command (findings as JSON on stdout, exit non-zero on findings,
zero when green) and `gov check --json`. `gov check` answers in one of two forms, and the tests
read both (`GovCheck` in `w2_95_support.py`): when no hard-block check is red, `ok` is true and
the check `core-pathmap` is in `result.checks`, the family `path-map compliance` in
`result.families`; when any hard-block check is red (core-pathmap is hard-block), `gov check`
exits non-zero with its failure form, `ok` false, `result` empty, `error.code` `CHECK_FAILED`,
and the same checks and families under `error.details.checks` and `error.details.families`.
Any other answer (no JSON, or another error code) is a refusal of the planted project. The codes `PATH_NO_NAMESPACE` and
`PATH_MULTIPLE_NAMESPACES`, with the fields `path` and `namespaces`, are what the check already
gives on `w2/integrate` and are held. For the new path-map faults no code is pinned: the check is
not green, and a finding that is not one of those two per-path codes names `path-map.yaml` and
one word of the cause (see `test_w2_95_path_map_faults.py` for each case's words).

Planted path maps give each namespace entry every field the schema requires, so only `paths`
is judged. A path in no namespace is accepted with `namespaces` absent or empty.

## KPI lines and their tests

| KPI line | Tests |
|---|---|
| 1. Both forms read; each tracked path in none or in two named with the namespaces it matched; green when every path is in exactly one; `*` inside one folder, `**` across folders | `test_w2_95_namespaces.py`: `every_path_in_exactly_one_namespace_is_green[mapping, list]` (also `**` across two folders), `paths_in_none_and_in_two_are_named[mapping, list]`, `star_at_the_root_matches_only_root_files[mapping, list]`, `star_alone_leaves_files_in_folders_unplaced[mapping, list]`, `star_inside_a_folder_does_not_cross_into_a_subfolder`; through `gov check`: `test_w2_95_adopted_and_gov_check.py::gov_check_family_is_not_green_on_a_mapping_form_path_in_none` |
| 2. Missing (under `governance/project/`), unreadable, unparsable, or of neither form: a finding naming the cause, never green | `test_w2_95_path_map_faults.py`: `path_map_that_cannot_be_judged_is_a_finding[...]` for 11 cases (unparsable YAML; top level a list or a string; no `namespaces`; `namespaces` a string or a number; a mapping entry that is a list, has no `paths`, or whose `paths` is a string; a list entry that is a string; not UTF-8), `path_map_without_read_permission_is_a_finding` (skipped as root), `missing_path_map_under_governance_project_is_a_finding`, `missing_path_map_is_never_green_in_gov_check` |
| 3. A refactored path map of an adopted repository validated the same way | `test_w2_95_adopted_and_gov_check.py`: `adopted_repository_refactored_path_map_is_green`, `adopted_repository_names_each_unplaced_and_doubly_placed_path` (both interfaces), `adopted_repository_kept_valid_a_new_unplaced_file_turns_it_red` |
| 4. This repository's own result | Not tested here: measured by the lead |
| 5. Nothing else in `gov check` changes (in proportion) | `test_w2_95_adopted_and_gov_check.py::other_checks_results_do_not_change_with_core_pathmap`: in planted repositories where core-pathmap is green and where it is red, every other check (without provenance) and every other family are the same |

Failure KPIs: a path in none or two reported green (KPI 1 and 3 tests); an unreadable,
unparsable or unknown-form path map reported green (KPI 2 tests); another check's result changed
(KPI 5 test).

Not judged, as the lead read KPI line 2: a folder with no `governance/project/` is no Gov OS
project, and a path map missing there is not tested.

## Red against `w2/integrate` (the code with the fault)

Run: `PYTHONPATH=<root>/src python3 -m pytest tests/acceptance/W2-95 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
Expected: **22 failed, 6 passed** (28 tests; the read-permission test is skipped when run as root).

| Test | Red reason on `w2/integrate` |
|---|---|
| `paths_in_none_and_in_two_are_named[mapping]`, `star_alone_..._unplaced[mapping]`, `star_inside_a_folder_...`, `gov_check_family_is_not_green_...`, `adopted_repository_names_each_...`, `adopted_repository_kept_valid_...` | the mapping form is not judged: exit 0, no findings, `core-pathmap` GREEN |
| `star_at_the_root_matches_only_root_files[list]`, `star_alone_..._unplaced[list]` | in the list form `*` crosses folders: `src/...` and `docs/...` are matched by `*` (in two namespaces, or not named as unplaced) |
| `path_map_that_cannot_be_judged_is_a_finding[unparsable_yaml, top_level_a_list, top_level_a_string, namespaces_a_string, namespaces_a_number, mapping_entry_a_list, mapping_entry_without_paths, mapping_entry_paths_a_string]`, `path_map_without_read_permission_...`, `missing_path_map_under_governance_project_...`, `missing_path_map_is_never_green_in_gov_check` | green: exit 0, no findings (`core-pathmap` GREEN in `gov check`) |
| `[no_namespaces]`, `[list_entry_a_string]` | red, but only per-path `PATH_NO_NAMESPACE` findings: no finding about the path map names the cause |
| `[not_utf8]` | the command crashes with a traceback: no finding on stdout |

Passing already on `w2/integrate` (expected): `every_path_in_exactly_one_namespace_is_green[mapping]`
(trivially: the mapping form is not judged), `every_path_in_exactly_one_namespace_is_green[list]`,
`paths_in_none_and_in_two_are_named[list]`, `star_at_the_root_matches_only_root_files[mapping]`
(trivially), `adopted_repository_refactored_path_map_is_green` (trivially),
`other_checks_results_do_not_change_with_core_pathmap` (KPI 5 holds today).

## Observed, not judged here

`gov check --json` refuses a list-form path map before any check runs (`CONFIG_INVALID`:
"key 'namespaces': must be a map", from the config loader, which is outside this ticket's
paths), and refuses an unparsable one the same way. Neither is green; the list form is therefore
tested through the declared command only.

## Revision (test batch 2)

The first version read only `result`, so once core-pathmap was red the `gov check` cases found no
check and no family in the failure form (`error.details`). `adopted_repository_names_each_...`,
`gov_check_family_is_not_green_...` and `other_checks_results_do_not_change_...` therefore failed
against a correct implementation, and `missing_path_map_is_never_green_in_gov_check` took the
failure form for a refusal. All four now read both forms, and no expectation changed. On
`w2/integrate` the counts and reasons above are unchanged: core-pathmap is never red there
through `gov check`, so only the success form is seen.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `lifted` (`tests/optin-lifted*.txt`), run report-only with `--optin=lifted`.

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: core-pathmap reads the namespaces in the form the path map's schema states (a mapping of name to its entry), and the list form too; f... | `test_w2_95_adopted_and_gov_check.py::test_w2_95_gov_check_family_is_not_green_on_a_mapping_form_path_in_none`, `test_w2_95_adopted_and_gov_check.py::test_w2_95_adopted_repository_refactored_path_map_is_green` | by its words (every function of the suite kept) |
| S2: A path map that is missing where the project declares one, cannot be read, cannot be parsed, or has namespaces of neither form is a f... | `test_w2_95_path_map_faults.py::test_w2_95_missing_path_map_is_never_green_in_gov_check`, `test_w2_95_path_map_faults.py::test_w2_95_missing_path_map_under_governance_project_is_a_finding` | by its words (every function of the suite kept) |
| S3: It validates a refactored path map of an adopted repository the same way: a planted repository with a path map written for it, green ... | `test_w2_95_adopted_and_gov_check.py::test_w2_95_adopted_repository_refactored_path_map_is_green`, `test_w2_95_namespaces.py::test_w2_95_every_path_in_exactly_one_namespace_is_green` | by its words (every function of the suite kept) |
| S4: This repository's own result is measured and recorded: the check run on w2/integrate's head, every path it names listed in the ticket... | `test_w2_95_path_map_faults.py::test_w2_95_missing_path_map_is_never_green_in_gov_check`, `test_w2_95_adopted_and_gov_check.py::test_w2_95_adopted_repository_refactored_path_map_is_green` | by its words (every function of the suite kept) |
| S5: Nothing else in gov check changes: the other checks' results on this repository are the same before and after [DEC-381] | `test_w2_95_adopted_and_gov_check.py::test_w2_95_other_checks_results_do_not_change_with_core_pathmap`, `test_w2_95_adopted_and_gov_check.py::test_w2_95_adopted_repository_refactored_path_map_is_green` | by its words (every function of the suite kept) |
| F1: A tracked path in no namespace or in two, reported green. | `test_w2_95_namespaces.py::test_w2_95_every_path_in_exactly_one_namespace_is_green`, `test_w2_95_adopted_and_gov_check.py::test_w2_95_adopted_repository_refactored_path_map_is_green` | by its words (every function of the suite kept) |
| F2: An unreadable or unparsable path map, or one of an unknown form, reported green. | `test_w2_95_adopted_and_gov_check.py::test_w2_95_adopted_repository_refactored_path_map_is_green`, `test_w2_95_adopted_and_gov_check.py::test_w2_95_gov_check_family_is_not_green_on_a_mapping_form_path_in_none` | by its words (every function of the suite kept) |
| F3: Another check's result changed. | `test_w2_95_adopted_and_gov_check.py::test_w2_95_gov_check_family_is_not_green_on_a_mapping_form_path_in_none`, `test_w2_95_path_map_faults.py::test_w2_95_missing_path_map_is_never_green_in_gov_check` | by its words (every function of the suite kept) |
