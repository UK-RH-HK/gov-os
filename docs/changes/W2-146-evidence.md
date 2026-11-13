# W2-146 evidence: the id reader reads every declared id form (DAEO-f6x3; DEC-1071 (5), DEC-1099 (2), DEC-900)

## The change (engineer's commits `de8378720`, `ed8aaa8ca`; Interface P-W2-146-1 (a))

- **Schema (`template/governance/kernel/schemas/path-map.schema.json`, S1).** An optional top-level `id_forms`: an
  array (may be empty) of `$defs/id_form` = `{type: object, additionalProperties: false, required: [name, pattern],
  name: $ref #/$defs/text, pattern: {type: string, minLength: 1, format: regex}}`. Nothing else moves; the top level
  stays open. **sha256 before** `7a1a1cd8cbf6fb073e2e1eb6f816d2ba83e2b647e2dc94efb1dfa96f359a8469`, **after**
  `d22efa5ada515c8cd0132b8c4960e7aa4d34d4e3fe345b07f576cedfba0fc7be`; **15 lines added, none removed** (a property of
  five lines after `close_workers`, a `$defs` entry of ten lines before `evaluation_set`). `src/gov/config/loader.py`
  is untouched (it ignores the key). The CIT-P record for the kernel schema change is the lead's.
- **`lexical.id_forms(root)` (S1, S2).** Reads only `id_forms` of `<root>/governance/project/path-map.yaml` with
  `read_yaml`, as `kept_out` does. No file, no key (or a null one), `[]`: `()`. Not a list, or an entry that is not a
  map, lacks a non-empty string `name` or `pattern`, or whose pattern does not compile: `GovError("CONFIG_INVALID")`
  naming `id_forms[<i>]` and the reason. Compiled with no flags. (`src/gov/retrieval/lexical.py`)
- **`lexical.ids_in(text, forms=())` (S2).** `forms` empty: the old expression, unchanged. With forms: the built-in
  matches that hold a digit, plus each form's non-empty `finditer` matches that are a whole token by `whole_id`'s rule
  at the match's span; sorted by start, longest first; a candidate overlapping one kept is dropped; then each text once,
  in position order. Other callers (`_lead_id`, `_words`, `_ranked`, `ID_SHAPE.sub`, `gov.memaudit.preflight`) are
  unchanged and pass no forms.
- **The stop (`src/gov/retrieve/command.py::_nowhere`, S3).** `forms = lexical.id_forms(root)` once, first; `ids_in(…,
  forms)` for the question and for the `--id`/ticket check. The records check's `GovError` catch is untouched and does
  not wrap `id_forms`, so a `CONFIG_INVALID` propagates (`gov retrieve` exits 1, before any search). `_stated_gap` and
  the rest of `_nowhere` are unchanged.

## The KPI lines and how each is met

| KPI | How it is met | Tests (unit, in `tmp_path`, invented ids) |
|---|---|---|
| S1 declared forms in the schema; malformed refused | `id_forms`/`$defs/id_form` | `test_w2_146_id_forms.py`: `test_the_schema_accepts_declared_forms[empty,five,two]`, `test_the_schema_refuses_a_malformed_form[nameless,patternless,non-compiling,empty-pattern,empty-name,extra-key,not-a-map]`, `test_the_schema_refuses_forms_that_are_no_list`, `test_the_repository_map_is_valid_without_forms` (`Draft202012Validator` with `FormatChecker`); runtime: `test_a_malformed_form_is_config_invalid_naming_its_index[8 kinds]`, `test_no_file_no_key_and_an_empty_list_declare_nothing` |
| S2 the reader reads them; byte-identical with none | `ids_in(text, forms)` | `test_a_declared_form_is_read_when_declared_and_not_when_not[bare,lower,under,dotted,spaced]`, `test_every_form_is_read_beside_the_built_in_shape_once_and_in_order`, `test_with_no_form_declared_the_result_is_today_s`, `test_ids_in_without_forms_is_the_built_in_expression[13 texts]`, `test_a_form_s_match_must_be_a_whole_token[9]`, `test_a_dotted_form_is_read_whole_not_as_its_fragment`, `test_overlaps_keep_the_earlier_and_then_the_longer` |
| S3 the stop fires on them | `_nowhere` passes the forms | `test_w2_146_stop.py`: for each of the five forms, `test_a_declared_form_id_that_exists_nowhere_is_the_stated_gap` (UNRESOLVED_IDS, no evidence, no continuation), `test_a_declared_form_id_present_as_a_whole_token_is_retrieved_as_before`, `test_one_named_id_that_exists_means_the_request_is_retrieved_as_before` (the "every" rule), `test_an_id_and_a_ticket_of_a_declared_form_that_exist_nowhere_are_the_stated_gap`, `test_a_prefix_of_a_held_id_is_not_that_id`, `test_a_dotted_id_is_stopped_whole_not_answered_by_its_fragment`, `test_a_malformed_form_is_config_invalid_before_any_search`, `test_a_malformed_form_makes_gov_retrieve_exit_1`, `test_nowhere_reads_the_forms_once` |
| S4 nothing else moves | no form: the old expression; only `_nowhere` passes forms | `test_with_no_form_declared_the_same_question_is_retrieved_as_before`; the existing folders below, unchanged |
| Failure lines | as S3/S2/S4 | the same tests |

**Interface point 5 (F2), checked end to end:** the stop's per-name search (`lexical.search(root, name, refresh=False)`
+ `whole_id`) finds a declared-form id present as a whole token on one line for every kind, including the one with a
space (`PX 41`) and the lowercase one (`bug7`): the "present" cases above are retrieved, never stopped. The FTS phrase
(`_phrase`) tokenizes `PX 41`, `SPEC-4.2`, `KV_12` (underscore a token character) and `bug7` as the index does. No
package needed.

## Results (launch sandbox, 2026-11-12; every run through the heavy slot, real-model cases left out)

- The new files, every row (`GOV_TESTS_OPTIN=lifted,breadth`; a default run keeps only the first row of each
  parametrised case under the repository's opt-in lists): 85 passed (`test_w2_146_id_forms.py` 57, `test_w2_146_stop.py`
  28 at the last full run; the only failure there was a wrong case of mine, `ZQ41-b`, which the built-in shape reads
  itself; fixed, 57 passed).
- `tests/unit/retrieve`: 43 passed. `tests/acceptance/W2-13`: 96 passed, 5 deselected. `W1-20`: 25 passed, 26
  deselected. `W1-21`: 79 passed, 48 deselected. `W2-138`: 18 passed.
- `tests/unit/retrieval`: 524 passed, 2 skipped, 20 failed, 399 deselected. All 20 are in `test_w2_112_shared_reranker.py`
  (a file this ticket does not touch), every one because the sandbox refuses the client's Unix socket (`PermissionError:
  [Errno 1] Operation not permitted`, or no socket file): the same family W2-145's record names. Not run on the merge
  base here; the CTO's outside run decides.
- Left out by the exclusion: the cases named `real`, `green_here`, `time_limit` and the `local_only` marker.
