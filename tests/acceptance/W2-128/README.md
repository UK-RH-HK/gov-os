# W2-128 acceptance tests, round 1: the text half

Ticket DAEO-t8mp (W2-128), profile STANDARD. Written by the independent test designer (MR-3) before any
implementation, from the ticket's KPI lines and its body's "Interface and rounds" section (DEC-1109 (2)), reading
`R3-TEMPLATES.md` §B, §C, §D and the Appendix, `LINK-INTEGRITY.md` §5, `D5-ROWS.md` rows 1-17 and today's
integrated text (`w2/integrate` at `75a29ff64`). Nothing of this ticket's implementation was read.

KPI cells use positions in the ticket: `S<n>` is the n-th success line, `F<n>` the n-th failure line (the ticket's
lines begin with TPL labels). S1-S5 are TPL-1 S1-S5; S6 is TPL-2; S8 is TPL-3 S5; S10 is TPL-5; S14 the link
lines; S15 the links command; S16 the three schemas; S17 the CIT-P; S18 the reviewer's reversal line; S19 the
dependency fields; S20 search again once; S21 D5-ROWS rows 1-9.

## How they run

    HOME=<empty folder> PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed

About 6 s. No model, no network, no GPU, no store, no `gov retrieve`. With an empty `HOME`, Python's user site
moves too: set `PYTHONUSERBASE` to the real one (`~/.local` here) so pytest is found; the cases pass that base on to
the check forms they run. The cases need `git`, the `jsonschema` package (4.x, Draft 2020-12) and `PyYAML`.

## What the cases read, and how

- **The nine templates** are `template/governance/kernel/templates/{brief,ticket,role-research,role-product-spec,
  role-test-designer,role-engineer,role-reviewer,role-lead,role-cto}.md` (the ticket's "Files"). Front matter:
  `name` equal to the stem, `version` semver (`1.2.3`, a string), `role` a non-empty string or list.
- **The prose measure (S2)** is the ticket's: the body after the front matter, less fenced code blocks and lines
  starting `|` (indented ones too), counted in characters with the kept lines joined by newlines; T-0 unfilled.
  Budgets are R3 §C's (T-0 and T-1 4,000; T-2 to T-6 3,500; T-7 8,000; T-8 6,000); `facts.yaml`'s `budgets`
  must name each stem at or under them.
- **Placeholders (S5, F1)**: `{KEY}` or `{KEY: description}` with KEY in `[A-Z][A-Z0-9_]*`; `{CMD:name …}` (the
  name runs to the first space or brace, so `{CMD:commit role=x}` names `commit`); `{STEP:name}`. A brace a shell's
  `$` opens (`${HOME}`) and lower-case braces are not placeholders. The scan covers the nine templates and the
  record templates (`checkpoint`, `decision-record`, `decision-package`, `failure`, `lesson`, `research`), front
  matter included. `keys.yaml` must also list the Appendix's keys `ID W2 PROFILE IMPL EST TREE TESTS_TREE MAIN TOOLS
  STORE_TREE` and `BASE` (LINK-INTEGRITY §5 names `{BASE}` a generator key).
- **F1, commands**: every `gov <subcommand>` in a template's code (inline code spans and fenced blocks) and every
  `*.sh` a template names anywhere must occur in some `commands` entry's `run` form. Prose such as "never run gov
  close" outside code is not read as a command.
- **F7**: every `DEC-n` inside square brackets in those templates must have the status word `ACCEPTED` on its
  register entry's `- **Status:**` line, read from `docs/DECISION_REGISTER.md` at test time. `DONE`, `SUPERSEDED`,
  `PROPOSED`, `DEFERRED` and the rest fail (the brief's rule: "not ACCEPTED").
- **Lines (S14, S18, S21)** are read as units: a paragraph or list item with its wrapped lines joined; a line that
  ends with a bracketed decision id ends its unit and a line opening with a label (`Start:`, `**Done when:**`)
  starts one. A `{CMD:name}` in a unit counts as that command's `run` form, so "run {CMD:links}" reads as "run gov
  links --since {BASE}". Needles are matched case-insensitively with white space folded; the cases test the
  substance §5 and D5-ROWS quote (field names, flags, ids), never the wording.
- **The check runner (S6, S8, S15)**: each `commands` entry's `check` runs with `bash -c` in a temporary git
  repository (two commits), stdin closed, under a 5-second limit ("a few seconds"), with an empty `HOME`, a dead
  proxy (`http://127.0.0.1:9`) for every proxy variable, `CUDA_VISIBLE_DEVICES=""`, `OLLAMA_HOST=127.0.0.1:9` and
  `PYTHONPATH` this tree's `src`; it must exit 0. Before it runs, `{TREE}`, `{WRITE_TREE}`, `{TESTS_TREE}` and
  `{ROOT}` are filled with the temporary repository, `{BASE}` with `HEAD`, `{ID}` `DAEO-t8mp`, `{W2}` `W2-128`,
  `{ROLE}` `engineer`, `{PROFILE}` `STANDARD`, and any other `{KEY}` from `paths[key.lower()]` (nested keys
  resolved); a placeholder left after that fails the case by name. Statically, no check may name `ollama`,
  `llama-server`, `nvidia-smi`, `curl`, `wget`, `pip install`, a URL, `huggingface`, `heavy_slot` or
  `rebuild_slot`, and a check naming `gov retrieve` or `gov context` must be its `--help`.
- **The schemas (S10, S16)** are validated with `jsonschema`'s Draft 2020-12 validator, `common.schema.json`
  resolved locally, as `gov check`'s schema check validates records (front matter as JSON, dates as ISO text).
  "Allows a field" is read as declaring it in the ticket's form: the form is accepted and a value of another shape
  (a bare string where a list is due) is refused. Today's schemas accept any extra key, so only the refusal shows a
  declaration. The ticket cases start from this ticket's own front matter (valid today).
- **The planted records (S14)**: each record template's example (the template as it stands, with `{ID}` and the
  example ticket id `DAEO-0000`/`DAEO-xxxx` filled with `DAEO-t8mp`, whose ticket file is planted beside it) and
  T-1's yaml skeleton (as a ticket's front matter, its own id kept) is planted alone in a temporary repository
  beside a copy of the register and `path-map.yaml`, committed, and judged by `gov links --all --json` from this
  tree; no finding may name the planted file. One record per repository: a planted ticket's prefix would make
  another template's placeholder id read as a ticket id. `gov links` runs in the sandbox on a temporary tree
  (0.5 s), so this half is testable here.

## KPI lines, tests, and the outcome on `w2/integrate` (`75a29ff64`)

Run in the launch sandbox: **92 tests, 84 failed, 8 passed** (6.0 s). Every red fails on what its line asks for: a
file not there yet (the nine templates, `keys.yaml`, `facts.yaml`, `facts.schema.json`, the CIT-P), a schema that
does not declare the field, or a record template without its link lines. The 8 greens are guards.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_128_templates.py::test_s1_the_nine_templates_exist` | red | none of the nine files exists (`ticket.md` is today's old form, the others are missing) |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[brief]` | red | `brief.md` does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[ticket]` | red | today's `ticket.md` front matter is a ticket's, with no `name: ticket` |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-research]` | red | the file does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-product-spec]` | red | the file does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-test-designer]` | red | the file does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-engineer]` | red | the file does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-reviewer]` | red | the file does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-lead]` | red | the file does not exist |
| S1 | `test_w2_128_templates.py::test_s1_front_matter_holds_name_version_and_role[role-cto]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[brief]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[ticket]` | green (guard) | today's `ticket.md` body is far under 4,000; T-1 must stay under it |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-research]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-product-spec]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-test-designer]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-engineer]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-reviewer]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-lead]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_prose_is_within_r3_budget[role-cto]` | red | the file does not exist |
| S2 | `test_w2_128_templates.py::test_s2_facts_budgets_name_each_template_within_r3` | red | `facts.yaml` does not exist |
| S3 | `test_w2_128_templates.py::test_s3_engineer_template_holds_no_instruction_to_read_the_acceptance_tests` | red | `role-engineer.md` does not exist |
| S3 | `test_w2_128_templates.py::test_s3_test_designer_template_permits_reading_code_on_w2_integrate` | red | `role-test-designer.md` does not exist |
| S3 | `test_w2_128_templates.py::test_s3_reviewer_template_carries_the_dec_1010_verdict_block` | red | `role-reviewer.md` does not exist |
| S4 | `test_w2_128_templates.py::test_s4_old_brief_is_removed_or_a_one_line_pointer[brief-engineer.md]` | red | 51 body lines today |
| S4 | `test_w2_128_templates.py::test_s4_old_brief_is_removed_or_a_one_line_pointer[brief-lead.md]` | red | 115 body lines today |
| S4 | `test_w2_128_templates.py::test_s4_old_brief_is_removed_or_a_one_line_pointer[brief-product-spec.md]` | red | 57 body lines today |
| S4 | `test_w2_128_templates.py::test_s4_old_brief_is_removed_or_a_one_line_pointer[brief-reviewer.md]` | red | 45 body lines today |
| S4 | `test_w2_128_templates.py::test_s4_old_brief_is_removed_or_a_one_line_pointer[brief-test-designer.md]` | red | 59 body lines today |
| S4 | `test_w2_128_templates.py::test_s4_engineer_role_line_5_says_to_fulfil_the_spec_and_its_kpis` | red | line 5 says "implement one ticket until its acceptance tests pass" |
| S5 | `test_w2_128_templates.py::test_s5_every_key_placeholder_is_in_keys_yaml` | red | `keys.yaml` does not exist |
| S5 | `test_w2_128_templates.py::test_s5_keys_yaml_lists_the_appendix_keys` | red | `keys.yaml` does not exist |
| S5 | `test_w2_128_templates.py::test_f1_every_cmd_and_step_placeholder_is_a_facts_key` | red | `facts.yaml` does not exist (S5's `{CMD:}`/`{STEP:}` half) |
| S6 | `test_w2_128_facts.py::test_s6_facts_yaml_validates_against_facts_schema` | red | `facts.schema.json` does not exist |
| S6 | `test_w2_128_facts.py::test_s6_facts_schema_refuses_a_facts_file_without_commands_or_a_command_without_check` | red | `facts.yaml` does not exist |
| S6 | `test_w2_128_facts.py::test_s6_commands_hold_the_named_ones_each_with_run_and_check` | red | `facts.yaml` does not exist |
| S6 | `test_w2_128_facts.py::test_s6_no_check_reaches_a_model_the_network_a_gpu_or_gov_retrieve` | red | `facts.yaml` does not exist |
| S6 | `test_w2_128_facts.py::test_s6_every_check_runs_and_exits_0_in_a_temporary_repository` | red | `facts.yaml` does not exist |
| S6 | `test_w2_128_facts.py::test_s6_dod_has_at_most_six_items_quoted_by_id_in_t1_and_t7` | red | `facts.yaml` does not exist |
| S7 | round 2: not mapped | none | TPL-3 S1-S4, S6, S7 (`gov brief`), the code half |
| S8 | `test_w2_128_facts.py::test_s8_facts_names_the_three_scripts_and_the_templates_name_each` | red | `facts.yaml` does not exist |
| S9 | round 2: not mapped | none | TPL-4 (delivery), the code half |
| S10 | `test_w2_128_schemas.py::test_s10_ticket_schema_declares_non_goals_as_a_list_of_strings` | red | the schema does not declare `non_goals`: a bare string passes |
| S10 | `test_w2_128_schemas.py::test_s10_ticket_schema_accepts_a_kpi_line_as_line_and_verify_beside_the_string_form` | red | KPI items must be strings today |
| S10 | `test_w2_128_schemas.py::test_s10_ticket_schema_declares_reads_and_needs_as_lists_of_strings[reads]` | red | `reads` not declared: a bare string passes |
| S10 | `test_w2_128_schemas.py::test_s10_ticket_schema_declares_reads_and_needs_as_lists_of_strings[needs]` | red | `needs` not declared: a bare string passes |
| S10 | `test_w2_128_schemas.py::test_s10_ticket_schema_declares_waits_on_as_on_and_reason` | red | `waits_on` not declared: a bare string passes |
| S10 | `test_w2_128_schemas.py::test_s10_every_existing_ticket_stays_valid` | green (guard) | all 213 tickets validate today; they must after the change (see N-2: `DAEO-2bdu`) |
| S10 | `test_w2_128_schemas.py::test_s10_t1_is_the_ticket_template_with_its_skeleton_in_one_yaml_block` | red | today's `ticket.md` is front matter, with no `name: ticket` and no yaml block |
| S11 | round 2: not mapped | none | TPL-6, after TPL-4 and the owner's row decisions |
| S12 | round 2: not mapped | none | TPL-7, the measures |
| S13 | round 2: not mapped | none | TPL-8, the pilot |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[brief]` | red | `brief.md` does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[ticket]` | red | today's `ticket.md` says nothing of `closes` or the KPI brackets |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-research]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-product-spec]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-test-designer]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-engineer]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-reviewer]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-lead]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[role-cto]` | red | the file does not exist |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[decision-record]` | red | no `Under:`, `Changes:` or `Changed by` |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[lesson]` | red | no `sources:` or `constrains:` |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[failure]` | red | no `sources:` or `constrains:` |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[research]` | red | no `decisions:` |
| S14 | `test_w2_128_links.py::test_s14_template_carries_its_link_lines[checkpoint]` | red | no `decisions_applied:` |
| S14 | `test_w2_128_links.py::test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template[checkpoint]` | green (guard) | the example gives no finding today; the added link lines must keep it so |
| S14 | `test_w2_128_links.py::test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template[decision-record]` | green (guard) | as above |
| S14 | `test_w2_128_links.py::test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template[failure]` | green (guard) | as above |
| S14 | `test_w2_128_links.py::test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template[lesson]` | green (guard) | as above |
| S14 | `test_w2_128_links.py::test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template[research]` | green (guard) | as above |
| S14 | `test_w2_128_links.py::test_s14_gov_links_finds_nothing_on_a_record_planted_from_the_template[ticket]` | red | `ticket.md` has no yaml skeleton to plant |
| S15 | `test_w2_128_facts.py::test_s15_links_command_and_its_check_and_t7_quotes_its_first_line` | red | `facts.yaml` does not exist |
| S16 | `test_w2_128_schemas.py::test_s16_schema_declares_optional_sources_as_a_list_of_ids[lesson.schema.json]` | red | `sources` not declared: a bare string passes |
| S16 | `test_w2_128_schemas.py::test_s16_schema_declares_optional_sources_as_a_list_of_ids[failure.schema.json]` | red | as above |
| S16 | `test_w2_128_schemas.py::test_s16_schema_declares_optional_sources_as_a_list_of_ids[research.schema.json]` | red | as above |
| S16 | `test_w2_128_schemas.py::test_s16_research_schema_declares_optional_decisions_as_a_list_of_ids` | red | `decisions` not declared: a bare string passes |
| S16 | `test_w2_128_schemas.py::test_s16_every_existing_lesson_failure_and_research_record_stays_valid` | green (guard) | 5 lessons and 4 research records (no failure record) validate today; they must after |
| S17 | `test_w2_128_links.py::test_s17_the_cit_p_record_exists_naming_its_evidence_r2_r3_and_cap_33` | red | `docs/changes/W2-128-CIT-P.md` does not exist |
| S18 | `test_w2_128_templates.py::test_s18_reviewer_template_asks_per_finding_for_the_evidence_that_would_reverse_it` | red | `role-reviewer.md` does not exist |
| S19 | `test_w2_128_links.py::test_s19_t1_sets_reads_needs_and_waits_on_beside_allowed_paths_with_their_meanings` | red | today's `ticket.md` has no yaml skeleton |
| S20 | `test_w2_128_templates.py::test_s20_t0_carries_search_again_once_right_after_ask_memory_first` | red | `brief.md` does not exist |
| S20 | `test_w2_128_templates.py::test_s20_t8_names_search_again_once_on_its_start_line` | red | `role-cto.md` does not exist |
| S21 | `test_w2_128_rows.py::test_row_1_t4_a_revised_case_carries_that_ticket_s_task_trailer` | red | `role-test-designer.md` does not exist |
| S21 | `test_w2_128_rows.py::test_row_2_t5_a_whole_branch_diff_uses_stat_or_excludes_the_acceptance_tests` | red | `role-engineer.md` does not exist |
| S21 | `test_w2_128_rows.py::test_row_3_a_worker_brief_is_built_with_gov_context_and_role[role-lead]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_3_a_worker_brief_is_built_with_gov_context_and_role[role-cto]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_4_a_pair_runs_under_its_ticket_s_own_id[role-lead]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_4_a_pair_runs_under_its_ticket_s_own_id[role-cto]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_5_t0_no_merge_inside_the_sandbox` | red | `brief.md` does not exist |
| S21 | `test_w2_128_rows.py::test_row_6_t0_and_facts_the_pytest_marker_form_empty_home_and_no_retrieve_in_the_sandbox` | red | `facts.yaml` does not exist |
| S21 | `test_w2_128_rows.py::test_row_7_t4_the_readme_map_names_every_case_by_its_full_node_id` | red | `role-test-designer.md` does not exist |
| S21 | `test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-lead]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_8_gov_accept_runs_outside_the_sandbox_until_w2_56[role-cto]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_9_the_ticket_s_interface_is_stated_before_the_pair_starts[role-lead]` | red | the file does not exist |
| S21 | `test_w2_128_rows.py::test_row_9_the_ticket_s_interface_is_stated_before_the_pair_starts[role-cto]` | red | the file does not exist |
| F1 | `test_w2_128_templates.py::test_f1_every_cmd_and_step_placeholder_is_a_facts_key` | red | `facts.yaml` does not exist |
| F1 | `test_w2_128_templates.py::test_f1_every_gov_command_and_script_a_template_names_is_in_facts` | red | `facts.yaml` does not exist |
| F2 | round 2: not mapped | none | `gov brief` byte-identical output (TPL-3 F1) |
| F3 | round 2: not mapped | none | a launch without its role template (TPL-4 F1) |
| F4 | round 2: not mapped | none | the ready check (TPL-5 F1) |
| F5 | round 2: not mapped | none | `/doctor prompt-audit`, a review step (TPL-6 F1) |
| F6 | round 2: not mapped | none | a measure blocking a launch, close or landing (TPL-7 F1) |
| F7 | `test_w2_128_templates.py::test_f7_every_bracketed_decision_id_in_a_template_is_accepted` | red | the nine templates do not exist |

**Round 2, not mapped here:** S7, S9, S11, S12, S13 and F2-F6 whole; and these halves of round-1 lines:
- S6's TPL-2 S3 (a `steps` switch flipped in a filled brief removes its one line and nothing else): needs
  `gov brief`.
- S10's TPL-5 S3 (the ready check inside `gov brief`: refusals per required field, warnings per advisory item).
- S19's refusals `READS_MISSING`, `NEEDS_MISSING`, `WAITS_ON_MISSING` and the `waits_on` id check (the ready check).
- S17's independent review, the owner's approval, the versioned promotion and the operator's `.claude/` ACT: later
  steps of the CIT-P (CAP-33), not text this round writes. S17 here checks only the record's draft.

**A check of the tests themselves** (a scratch copy of the tree, never committed): a stand-in implementation built
from R3's Appendix, with D5 rows 1-9, §5's link lines, a `facts.yaml` whose checks are `--help`, `bash -n` or
no-op forms of the real tools, the schema changes and the CIT-P draft, passed all 92. Each of 32 wrong changes
then failed the case meant for it, among them: an engineer line telling it to read the acceptance tests; the
verdict block removed; an unknown `{CMD:}`, `{STEP:}` or `{KEY}`; `gov close` or an unknown script in code; a
SUPERSEDED or a DONE decision cited in brackets; T-7's prose over 8,000; the search-again line moved away from "Ask
memory first" or off T-8's Start line; the reversal line removed; a row line without its decision id or without
`W2-56`; a record template citing `DEC-999999` (the planted `gov links` case); a check that exits 1, sleeps 6 s or
runs `gov retrieve "x"`; seven dod items; a dod line copied into T-7; the links command changed; the ticket
schema losing the `{line, verify}` form, `non_goals` or `waits_on`; the lesson schema losing `sources`.

## Notes and limits

- **N-1. `on:` in YAML.** PyYAML (YAML 1.1), which gov's front-matter reader uses, reads an unquoted key `on` as the
  boolean `true`. A ticket written `waits_on: [{on: DAEO-x, reason: …}]` has no `on` key once read, so a schema
  requiring `on` refuses it. The S19 case reads T-1's skeleton as YAML and asks for the keys `on` and `reason`: the
  template must quote `"on":` (or the interface rename the key). Returned to the CTO as a discovery.
- **N-2. `DAEO-2bdu` already has `waits_on:`** as a list of strings (`"DAEO-qskx — W2-142: …"`). A schema allowing
  only `{on, reason}` items turns it invalid, which the S10 guard catches (shown in the self-check). The S10 cases
  ask that objects are accepted and a bare string (not a list) is refused; they leave string items open, so an
  `anyOf` of string and `{on, reason}` items satisfies both. Returned as a discovery.
- **N-3. F7's rule** is the brief's: a bracketed id must be ACCEPTED. The register's 108 `DONE` entries (records of
  fact) fail it as rules too.
- **N-4. Placeholders outside the interface.** R3's T-7 uses `{FACT:accepted_reds}`, which these cases read as the
  KEY `FACT` with a description; it passes only if `keys.yaml` lists `FACT`.
- **N-5. dod quoting** asks T-1 and T-7 each to hold at least one literal `DOD-n` that `facts.yaml` holds, and to copy
  no dod line of 30 characters or more word for word.
- **N-6. The `.claude/` copies** and the `.rulesync/` sources are not read here (TPL-4, round 2).

## Files

- `w2_128_support.py`: paths, the nine stems and budgets, front matter, the prose measure, units, placeholders,
  `facts.yaml`, the check runner, the register's statuses, the schema validator, the record finder.
- `conftest.py`: puts this folder on the import path.
- `test_w2_128_templates.py` (S1-S5, S18, S20, F1, F7), `test_w2_128_facts.py` (S6, S8, S15),
  `test_w2_128_schemas.py` (S10, S16), `test_w2_128_links.py` (S14, S17, S19), `test_w2_128_rows.py` (S21).
