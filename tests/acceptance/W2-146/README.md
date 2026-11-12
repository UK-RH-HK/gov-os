# W2-146 acceptance tests: the id reader reads every id form a repository declares

Ticket `DAEO-f6x3` (W2-146), profile STANDARD, class C2. Written by the independent test designer from the ticket's KPI
lines and its `## Interface` (P-W2-146-1 (a)), before and beside the implementation, without reading it. Sources:
DEC-1071 (5), DEC-1099 (2), DEC-900 (also DEC-1098 and DEC-1097, named by the ticket, not needed beyond it).

**192 cases from 57 test functions in three files** (counted by collection), one support module (`w2_146_support.py`).

## How the tests reach the code under test

Public interfaces only (the Interface's own seams, section 6):

- the path-map JSON schema file (`template/governance/kernel/schemas/path-map.schema.json`) validated with
  `Draft202012Validator(schema, format_checker=FormatChecker())` (Interface 1);
- `gov.retrieval.lexical.id_forms(root)` and `ids_in(text, forms)`, with `ids_in(text)` for "not declared"
  (Interfaces 2, 3); every case imports `gov.retrieval.lexical` inside the test, so the folder collects before the
  reader exists;
- `gov retrieve --json --root <planted store> [--id <id>] <question>` run as `python -m gov.cli.main` in a child
  process, read through the API-0002 envelope (Interfaces 4, 5).

Everything is planted in `tmp_path`: a git repository with its own path map (a valid one, built by the support module,
with `id_forms` when declared), its own `.gitleaks.toml` and its own `.gov-runtime/`; its lexical index and record
store are built by a child process (no embedding). Child processes run with no `GOV_*` variable, an empty `HOME`
and the Ollama endpoint at a dead loopback port: the semantic route is down, no model runs, and the stop and the
lexical route do not need it. `gitleaks` and `git` are needed for the end-to-end file (it skips, with the reason,
where either is absent). No marker `real`, `green_here`, `time_limit` or `local_only` is used. No question, label or
id comes from a hidden or spent set.

The five planted forms (`FORMS` in the support module): no hyphen `ABC[0-9]+` (`ABC9`), lowercase `req[0-9]+`
(`req12`), underscore `TKT_[0-9]+` (`TKT_7`), dotted suffix `SPEC-[0-9]+\.[0-9]+` (`SPEC-7.2`, `SPEC-4.2`), a space
`ZQ [0-9]+` (`ZQ 41`). The built-in shape reads none of them whole (it reads `SPEC-4` out of `SPEC-4.2`: the overlap
rule's case).

## KPI lines and their tests

Files: `test_w2_146_schema.py` (S1), `test_w2_146_reader.py` (S2), `test_w2_146_stop.py` (S3, S4, failures). A
parametrised function is one row; the parameter is each planted form (or text). "Red now" is the reason the case fails
on a head that holds none of the Interface; "holds now" marks a regression guard that is green today and must stay so.

| KPI id | tests | expected red reason |
|---|---|---|
| S1 (schema accepts the list) | test_w2_146_schema.py::test_s1_a_map_with_two_well_formed_forms_is_accepted, test_w2_146_schema.py::test_s1_the_five_planted_forms_are_accepted, test_w2_146_schema.py::test_s1_an_empty_list_of_forms_is_accepted, test_w2_146_schema.py::test_s1_premise_the_planted_path_map_without_id_forms_is_valid, test_w2_146_schema.py::test_s1_the_repository_own_path_map_is_still_valid | holds now (the top level is open today); they pin that the fix does not refuse a good map |
| S1 (refuses no name, no pattern, a pattern that does not compile) / F3 | test_w2_146_schema.py::test_s1_a_form_with_no_name_is_refused, test_w2_146_schema.py::test_s1_a_form_with_no_pattern_is_refused, test_w2_146_schema.py::test_s1_a_form_whose_pattern_does_not_compile_is_refused, test_w2_146_schema.py::test_s1_a_form_whose_pattern_is_an_empty_string_is_refused, test_w2_146_schema.py::test_s1_a_form_whose_name_is_an_empty_string_is_refused, test_w2_146_schema.py::test_s1_the_map_with_a_nameless_a_patternless_and_a_non_compiling_form_is_refused_each_time | the schema has no `id_forms` entry: the malformed map is accepted |
| S1 (the entry and the list are closed, Interface 1) | test_w2_146_schema.py::test_s1_a_form_with_a_pattern_that_is_not_text_is_refused, test_w2_146_schema.py::test_s1_a_form_with_a_key_beside_name_and_pattern_is_refused, test_w2_146_schema.py::test_s1_id_forms_that_is_no_list_is_refused | the schema accepts any `id_forms` value |
| S1 (a malformed form is not accepted at run time, Interface 5) / F3 | test_w2_146_stop.py::test_s1_failure3_a_malformed_form_in_the_path_map_makes_retrieve_fail_with_config_invalid | `gov retrieve` ignores `id_forms`: exit 0, not exit 1 `CONFIG_INVALID` |
| S2 (each declared form read whole, once, in order, beside the built-in ids; not read when not declared) | test_w2_146_reader.py::test_s2_a_declared_form_is_read_whole_once_in_order_beside_the_built_in_ids, test_w2_146_reader.py::test_s2_a_declared_form_is_read_in_its_own_text_alone, test_w2_146_reader.py::test_s2_all_five_forms_declared_are_read_in_order_of_position, test_w2_146_reader.py::test_s2_a_token_read_by_two_forms_is_read_once, test_w2_146_reader.py::test_s2_a_form_that_is_not_declared_is_not_read | `lexical.id_forms` does not exist (AttributeError) / `ids_in` takes no forms (TypeError); the "not declared" row's first half holds now, its `ids_in(text, ())` half raises TypeError |
| S2 (whole-token rule) | test_w2_146_reader.py::test_s2_a_token_of_a_declared_form_inside_a_longer_word_is_not_read, test_w2_146_reader.py::test_s2_a_declared_token_bounded_by_punctuation_is_read | `lexical.id_forms` does not exist |
| S2 (overlap: `SPEC-4.2` whole, not `SPEC-4` beside it; Interface 3) | test_w2_146_reader.py::test_s2_under_a_dotted_form_the_dotted_id_is_read_whole_not_its_fragment, test_w2_146_reader.py::test_s2_the_fragment_and_the_dotted_id_apart_in_one_text_are_both_read | `lexical.id_forms` does not exist |
| S2 / F3 (byte-identical with no form) | test_w2_146_reader.py::test_s2_with_no_form_the_result_is_todays_expression, test_w2_146_reader.py::test_s2_the_same_list_with_forms_that_match_nothing_in_the_text, test_w2_146_reader.py::test_s2_the_same_list_with_an_empty_tuple_of_forms, test_w2_146_reader.py::test_s2_the_built_in_shape_is_always_read_beside_declared_forms | the first holds now (today's expression is `ids_in`); the others need `id_forms` / `ids_in(text, forms)` |
| S2 (reading the forms, Interface 2) | test_w2_146_reader.py::test_s2_no_path_map_gives_no_forms, test_w2_146_reader.py::test_s2_a_path_map_with_no_id_forms_key_gives_no_forms, test_w2_146_reader.py::test_s2_an_empty_id_forms_list_gives_no_forms, test_w2_146_reader.py::test_s2_the_forms_are_compiled_patterns_in_the_order_declared, test_w2_146_reader.py::test_s2_a_declared_pattern_is_case_sensitive, test_w2_146_reader.py::test_s2_inline_flags_at_the_start_of_a_pattern_are_the_repositorys, test_w2_146_reader.py::test_s2_a_pattern_that_matches_nothing_in_a_text_reads_nothing | `lexical.id_forms` does not exist |
| S2 / F3 (a malformed entry is `CONFIG_INVALID` naming `id_forms[<i>]`) | test_w2_146_reader.py::test_s2_a_malformed_entry_is_a_config_invalid_error_naming_it, test_w2_146_reader.py::test_s2_a_malformed_first_entry_names_index_zero | `lexical.id_forms` does not exist |
| S3 / F1 (a nonexistent declared-form id stops: `UNRESOLVED_IDS`, no evidence, gap `UNRESOLVED`, no continuation) | test_w2_146_stop.py::test_s3_failure1_a_nonexistent_declared_id_asked_alone_is_the_stated_gap, test_w2_146_stop.py::test_s3_failure1_a_question_naming_a_nonexistent_declared_id_is_the_stated_gap, test_w2_146_stop.py::test_s3_failure1_a_nonexistent_declared_id_given_with_id_is_the_stated_gap, test_w2_146_stop.py::test_s3_failure1_two_nonexistent_declared_ids_of_one_form_are_two_gaps, test_w2_146_stop.py::test_s3_failure1_nonexistent_ids_of_every_form_and_the_built_in_shape_are_all_gaps_in_order, test_w2_146_stop.py::test_s3_failure1_a_declared_id_and_a_nonexistent_built_in_id_are_both_gaps, test_w2_146_stop.py::test_s3_failure1_a_dotted_id_whose_fragment_exists_is_the_stated_gap_for_the_whole_id_alone | the reader does not read the declared id: the request is retrieved (a stopping reason other than `UNRESOLVED_IDS`, evidence offered); the dotted case today stops on the fragment's gap or retrieves |
| S3 / F2 (the same id present as a whole token is retrieved; `UNRESOLVED_IDS` never printed) | test_w2_146_stop.py::test_s3_failure2_a_declared_id_present_on_a_line_is_retrieved_not_stopped, test_w2_146_stop.py::test_s3_failure2_a_declared_id_present_on_a_line_asked_alone_is_retrieved_not_stopped, test_w2_146_stop.py::test_s3_failure2_a_declared_id_present_given_with_id_is_retrieved_not_stopped, test_w2_146_stop.py::test_s3_failure2_the_present_id_asked_alone_cites_the_file_that_holds_it | holds now (nothing is read, so nothing stops): fail-open guards that go red only if the fix stops an existing id |
| S3 (the "every" rule stays) | test_w2_146_stop.py::test_s3_every_rule_a_nonexistent_declared_id_beside_an_existing_built_in_id_is_retrieved, test_w2_146_stop.py::test_s3_every_rule_a_nonexistent_declared_id_beside_an_existing_declared_id_is_retrieved, test_w2_146_stop.py::test_s3_every_rule_two_declared_ids_of_two_forms_one_present_and_one_not_is_retrieved, test_w2_146_stop.py::test_s3_every_rule_an_id_of_a_declared_form_the_question_holds_inside_a_longer_word_is_no_id | holds now; red only if the fix stops a request that names one existing id, or reads a token inside a longer word |
| S3 (premises of the planted store) | test_w2_146_stop.py::test_s3_premise_no_planted_line_of_the_absent_store_holds_a_planted_id, test_w2_146_stop.py::test_s3_premise_the_declared_ids_are_the_forms_and_the_built_in_shape_does_not_read_them | holds now (premises) |
| S4 (no form declared: stops and retrievals as today) | test_w2_146_stop.py::test_s4_with_no_form_declared_a_nonexistent_built_in_id_stops_as_today, test_w2_146_stop.py::test_s4_with_no_form_declared_an_existing_built_in_id_is_retrieved, test_w2_146_stop.py::test_s4_with_no_form_declared_a_declared_form_like_token_does_not_stop_the_request, test_w2_146_stop.py::test_s4_with_no_form_declared_a_dotted_token_stops_on_its_built_in_fragment_as_today | holds now; red only if the fix changes today's stop |
| S4 (a declared form changes only what the reader reads) | test_w2_146_stop.py::test_s4_a_declared_form_moves_nothing_but_the_reader_for_an_id_that_exists | holds now; red if declaring forms changes ranking, evidence or gaps of a question naming an existing id (the declaring path map's own file is left out of the comparison: it holds the patterns' words) |

The existing retrieval and retrieve suites are S4's other half; they are the lead's to run and are not copied here.

## Notes for the engineer's reader of this map

- A closure gap for an id given with `--id` is named by the closure as before (an id no record holds), whatever the
  reader reads; the `--id` cases that expect a retrieval therefore do not assert the id is no gap.
- The test fixture's path map is built by `valid_path_map()` (a minimal, schema-valid map); the repository's own path
  map is read only by `test_s1_the_repository_own_path_map_is_still_valid`, which asks that it still validates.
