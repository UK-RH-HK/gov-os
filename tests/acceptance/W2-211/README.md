# W2-211 acceptance tests (DAEO-esl1, FULL)

Written by the independent test designer from the ticket's KPI lines and `## Interface`, the spec's sections "The
record", "The answer sheet", "`gov decisions answer <sheet>`", "KPIs" and "How each KPI is verified" (PG-1, PG-3 to PG-6),
the rubric's section 2 and the existing `gov decisions basis`, before and beside the implementation, without reading it.
No network, no model; every repository is built under `tmp_path` with its own `git init` and fixture HOME.

## How to run

    T=$(mktemp -d); PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH TMPDIR=$T PYTHONPATH=<worktree>/src bash heavy_slot.sh python3 -m pytest tests/acceptance/W2-211 -q -p no:cacheprovider -n auto

`node` must be on PATH. A missing `node` FAILS PG-3's parity cases (an environment fault); it is never skipped.

## What the cases fix where the ticket leaves a place open (the implementer's contract)

- **Packages** live at `docs/decisions/packages/<id>.md`; a batch is published by `gov decisions page --batches
  docs/decisions/batches --root <repo>` (all open page-ready packages) and read back through
  `<batch>.manifest.json`: key `hash` (a hex digest, optionally prefixed `sha256:`) and key `cards` (the cards in order;
  each an id or an object with `id`). The page file itself is not read here (slice b).
- `page` names, on stdout or stderr, one line per refused package holding its id and the name of the field at fault (and
  no other of: question, found, sources, blocks, rubric, recommendation, touches); `options` for a count outside 2 to 6.
- **Answer**: `gov decisions answer - --batches <dir> --register <path> --root <repo> [--dry-run]` with the sheet on
  stdin, `GOV_ROLE=orchestrator` (or another role for ANSWER_ROLE). A refusal exits 1 with its code in stdout or
  stderr. Output lines as the spec: `DP-0042 -> DEC-1251 (b)`, `skipped: ...`, `notes for the CTO:`, `still open in this
  batch: ...`, `DP-0042 already recorded as DEC-1251`. The stored sheet is `<batch>.sheet-<8 hex>.txt`.
- **Sheet writer**: `gov.decisions.sheet.write_sheet(batch, hash, answered, picks)` with picks a list of
  `(id, letter|"skip", note|None)`; returns the sheet text. A note's line breaks become spaces (no extra lines).
- **JS twin contract** (`template/governance/kernel/assets/decisions-sheet.js`): runnable as `node decisions-sheet.js`,
  reading JSON `{batch, hash, answered, picks:[[id, letter|"skip", note|null],...]}` on stdin and printing the sheet
  to stdout; stdout equals the Python sheet byte for byte, one trailing newline more or less allowed.
- **Parser** is judged through `answer --dry-run` (same stdout for a wrapped sheet as for the plain one, nothing written).
- **Level**: `gov decisions level --touches a,b --reversible yes|no --inside ... [--spends] [--rounds n] [--emergency]`
  prints `level: P1 (touches spec; reversible yes; inside worktree)`; a package path reads its frontmatter; bad words
  exit 1 `LEVEL_FACT_INVALID`. `basis --range` refuses a below-level entry (exit non-zero) with `DECISION_BELOW_LEVEL`
  naming the level and the facts, and lists an entry with no stated facts as `unstated`. Entry facts are bullets
  `- **Touches:** spec`, `- **Reversible:** yes`, `- **Inside:** repository`, `- **Emergency:** yes`.
- **EL-3** is judged by files and a scratch repository carrying the kit's template and schema (and, in one variant, the
  repository's `governance/project/escalation.yaml`); a real `gov update` into an adopted scratch is PG-9's road and
  not run here.
- **Not testable by design**: `answer` is the owner's decision, so it never writes below level; EL-2's "answer runs the same
  check" is shown by a P1 package answered and its entry passing the range check. "A P1 record without the owner's decision
  becomes an open package" has no observable beyond the refusal and is not tested.

## The map

| KPI | Tests | Expected red reason |
|---|---|---|
| success-1 (PG-1) | `test_w2_211_pg1_page_ready.py::test_page_takes_the_clean_package_and_names_each_planted_field`, `test_w2_211_pg1_page_ready.py::test_a_page_of_only_defective_packages_puts_none_on_a_page`, `test_w2_211_pg1_page_ready.py::test_schema_adds_the_fields_as_optional` | `gov decisions page` does not exist; the schema lacks the new properties |
| success-2 (PG-3) | `test_w2_211_pg3_sheet.py::test_python_and_javascript_writers_are_byte_identical`, `test_w2_211_pg3_sheet.py::test_sheet_has_the_fixed_grammar_and_a_note_never_adds_a_line`, `test_w2_211_pg3_sheet.py::test_parser_reads_a_sheet_the_chat_wrapped` | `gov.decisions.sheet` and `decisions-sheet.js` do not exist; the batch fixture cannot be made (no `page`) |
| success-3 (PG-4) | `test_w2_211_pg4_answer.py::test_one_entry_per_pick_in_the_form_with_consecutive_ids`, `test_w2_211_pg4_answer.py::test_status_lines_read_as_the_owners_decision`, `test_w2_211_pg4_answer.py::test_packages_accepted_skip_untouched_and_sheet_stored`, `test_w2_211_pg4_answer.py::test_one_commit_with_the_trailers_and_nothing_left_behind`, `test_w2_211_pg4_answer.py::test_output_names_each_answer_the_skip_and_the_notes`, `test_w2_211_pg4_answer.py::test_basis_and_links_find_nothing_new` | `page` and `answer` do not exist (the batch fixture errors) |
| success-4 (PG-5) | `test_w2_211_pg5_refusals.py::test_refusal_carries_its_code_and_changes_nothing`, `test_w2_211_pg5_refusals.py::test_withdrawn_names_the_newer_package` | as PG-4: no `page`, no `answer`; 22 parametrised refusal cases, one per code and variant |
| success-5 (PG-6) | `test_w2_211_pg6_idempotent.py::test_second_paste_changes_nothing_exits_zero_and_names_the_entries`, `test_w2_211_pg6_idempotent.py::test_a_skip_writes_nothing_and_a_fuller_sheet_answers_only_what_is_open`, `test_w2_211_pg6_idempotent.py::test_another_option_for_an_answered_package_is_refused` | as PG-4 |
| success-6 (EL-1) | `test_w2_211_el1_level.py::test_level_table_cell`, `test_w2_211_el1_level.py::test_the_printed_line_is_the_levels_and_the_facts_that_set_it`, `test_w2_211_el1_level.py::test_spends_rounds_and_emergency`, `test_w2_211_el1_level.py::test_a_package_path_in_place_of_flags_reads_its_frontmatter`, `test_w2_211_el1_level.py::test_an_unknown_word_exits_1_level_fact_invalid` | `gov decisions level` does not exist (usage error, exit 2) |
| success-7 (EL-2) | `test_w2_211_el2_below_level.py::test_the_range_check_judges_the_decider_against_the_level`, `test_w2_211_el2_below_level.py::test_a_p2_call_written_inside_an_owners_decision_passes`, `test_w2_211_el2_below_level.py::test_an_entry_with_no_stated_facts_is_not_judged_and_is_listed`, `test_w2_211_el2_below_level.py::test_emergency_is_the_owners`, `test_w2_211_el2_below_level.py::test_answer_runs_the_same_check_and_the_owner_passes_a_p1_package` | no level check: a below-level entry passes `basis --range`; no `level` command |
| success-8 (EL-3) | `test_w2_211_el3_kit.py::test_kit_template_and_schema_carry_the_record_fields`, `test_w2_211_el3_kit.py::test_level_table_and_code_are_in_the_kit`, `test_w2_211_el3_kit.py::test_a_repository_with_the_kits_files_refuses_a_record_below_its_level`, `test_w2_211_el3_kit.py::test_the_code_default_and_the_kits_table_agree` | the template and schema lack the fields; `escalation.yaml` and `level.py` do not exist |
