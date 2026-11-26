# W2-212 acceptance tests (DAEO-d3sr, STANDARD): the stale route (D3)

Written by the independent test designer from the ticket's KPI lines and the lead's interface, before the implementation and without reading it.
Planted repositories in `tmp_path` only; no network, no model, no embedder. The semantic route is a stand-in that names every chunk
the keyword index held when the plant was built (as vectors built then would), so the retrieve-time filter is judged on that route
too. The adopt cases drive `gov.adopt.stages.run` in-process as `tests/unit/adopt` does (code graph and rebuild replaced); the doctor
cases run `gov doctor --json --root`.

Run: `PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-212 -q -p no:cacheprovider -n auto` (through the heavy slot).

## Interface the cases judge

- Namespace field `stale_class` in `superseded|historical|legacy`; needs `lexical_policy: not indexed` and `embedding_policy: not embedded`, else
  CONFIG_INVALID naming the namespace (and `stale_class` for a bad value); `gov.check.pathmap.check` reports PATH_MAP_INVALID for the same.
- `retrieve(root, query, ..., include_stale=False)`; `gov retrieve [--include-stale]`. Top-level `stale` list, entries `path`, `namespace`,
  `stale_class`, `stale: true`, `excerpt` (read from the file); present for the flag or a question naming the file's path; else absent or empty.
- A3: `ADOPT_STALE_CLASS` (message names the namespace; nothing recorded) for an unclassed namespace stale as a whole: its name holds
  a word part (split on non-alphanumerics, case-insensitive) superseded, historical, legacy or archive, or it has at least one path
  and every path holds one. A namespace only some of whose paths hold one (name does not) is recorded, with a `notices` entry
  `namespace`, `words`, `paths` (the stale-saying paths) and `notice` (move them into a namespace of their own with the stale
  class). `notices` also names a namespace where only a description field says so. A word that is only part of a longer word
  (`legacyish`) is no match.
- **Doctor key:** `result["stale_class"]` of `gov doctor --json`, always present: `status` `report` when a namespace needs the class (never
  `fail`/`drift`), `pass` when none; the section, serialised as JSON, names each such namespace and the lines `stale_class: <word>`
  (`archive` maps to `historical`), `lexical_policy: not indexed`, `embedding_policy: not embedded`, under `add` of the entry in
  `namespaces`; a mixed namespace's entry has `paths` (its stale paths) and no `add`. The plant is a git repo with a minimal
  `governance/project/path-map.yaml` (doctor exits 0 on it on the base).
- `gov update` renders the release's `template/` (copier `_subdirectory`): the schema and both adopt-skill copies are asserted to be under it,
  not excluded or skipped, and to carry the route.

## Map

| KPI id | tests | expected red reason |
|---|---|---|
| Success 1 | `test_w2_212_retrieve.py::test_sr1_default_bundle_leaves_the_stale_design_out_and_keeps_the_current` | `retrieve()` has no `include_stale` |
| Success 1 | `test_w2_212_retrieve.py::test_sr1_each_class_is_left_out` (historical, legacy) | same |
| Success 2 | `test_w2_212_retrieve.py::test_sr2_the_flag_lists_the_stale_file_marked_with_its_excerpt` | no `include_stale`; no `stale` list |
| Success 2 | `test_w2_212_retrieve.py::test_sr2_a_question_naming_the_path_lists_it_without_the_flag` | no `stale` key in the bundle |
| Success 2 | `test_w2_212_retrieve.py::test_sr2_without_flag_or_named_path_there_is_no_stale_list` | no `include_stale` |
| Success 2 | `test_w2_212_retrieve.py::test_sr2_the_command_takes_the_flag_and_carries_the_list` | parser rejects `--include-stale` |
| Success 2 | `test_w2_212_retrieve.py::test_sr2_gov_retrieve_help_names_the_flag` | help lacks `--include-stale` |
| Success 3 | `test_w2_212_adopt.py::test_sr3_an_unclassed_namespace_saying_it_is_stale_is_refused_naming_it_and_records_nothing` (7 plants) | A3 records, no `ADOPT_STALE_CLASS` (green on the head that refused any stale word: GUARD for the corrected rule) |
| Success 3 | `test_w2_212_adopt.py::test_sr3_a_namespace_only_some_of_whose_paths_say_it_is_recorded_with_a_notice_naming_those_paths` (2 plants) | A3 refuses the mixed namespace (`ADOPT_STALE_CLASS`) |
| Success 3 | `test_w2_212_adopt.py::test_sr3_a_catch_all_harbour_map_with_legacy_and_archive_paths_and_no_class_passes_a3` | same |
| Success 3 | `test_w2_212_adopt.py::test_sr3_beside_a_classed_namespace_only_the_mixed_one_gets_a_notice` | same |
| Success 3 | `test_w2_212_adopt.py::test_sr3_a_description_that_says_legacy_is_a_notice_not_a_refusal` | no `notices` key |
| Success 3 | `test_w2_212_adopt.py::test_sr3_the_adopt_skill_has_a_section_on_the_class_and_its_two_copies_are_identical` | no section names the class |
| Success 3 | `test_w2_212_adopt.py::test_sr3_the_same_namespace_with_the_class_and_both_policies_is_recorded` | GUARD: green on the base (the passing side) |
| Success 3 | `test_w2_212_adopt.py::test_sr3_a_word_that_is_only_part_of_a_longer_word_is_no_match` | GUARD: green on the base |
| Success 4 | `test_w2_212_doctor.py::test_sr4_an_unclassed_namespace_is_named_with_the_three_lines_and_the_run_still_exits_0` (legacy, archive) | no `stale_class` part |
| Success 4 | `test_w2_212_doctor.py::test_sr4_all_namespaces_classed_gives_no_notice` | no `stale_class` part |
| Success 4 | `test_w2_212_doctor.py::test_sr4_a_mixed_namespace_is_named_with_its_stale_paths_and_no_lines_to_add` | the mixed entry has no `paths` and carries `add` |
| Success 4 | `test_w2_212_doctor.py::test_sr4_beside_a_mixed_namespace_only_the_wholly_stale_one_gets_the_three_lines` | same |
| Success 4 | `test_w2_212_config.py::test_sr4_gov_update_carries_the_route_the_schema_and_both_skill_copies_under_template` | the carried files do not hold `stale_class` |
| Failure 1 | `test_w2_212_config.py::test_f1_a_class_outside_the_three_is_config_invalid_naming_namespace_and_field` | loader accepts the class |
| Failure 1 | `test_w2_212_config.py::test_f1_a_class_with_a_policy_that_keeps_it_in_index_or_vectors_is_config_invalid` | loader accepts the class without the policies |
| Failure 1 | `test_w2_212_config.py::test_the_kernel_schema_declares_the_class` | schema has no `stale_class` |
| Failure 1 | `test_w2_212_config.py::test_the_schema_accepts_a_classed_namespace_and_refuses_another_class` | schema accepts any class |
| Failure 1 | `test_w2_212_retrieve.py::test_f1_a_file_indexed_before_the_class_is_still_left_out_of_every_route` | no `include_stale`; on the base the stale chunk is still served (plant checked) |
| Failure 1 | `test_w2_212_config.py::test_f1_each_class_with_both_policies_is_valid` | GUARD: green on the base |
| Failure 1 | `test_w2_212_config.py::test_an_unclassed_namespace_is_as_before` | GUARD: green on the base |
