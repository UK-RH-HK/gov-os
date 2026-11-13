# W2-128 acceptance tests, round 1: the text half

Ticket DAEO-t8mp (W2-128), profile STANDARD. Written by the independent test designer (MR-3) before any
implementation, from the ticket's KPI lines and its body's "Interface and rounds" section (DEC-1109 (2)), reading
`R3-TEMPLATES.md` §B, §C, §D and the Appendix, `LINK-INTEGRITY.md` §5, `D5-ROWS.md` rows 1-17 and today's
integrated text (`w2/integrate` at `75a29ff64`). Nothing of this ticket's implementation was read.

**Revision 2 (2026-11-09, a fresh designer):** the CTO's P1 (b) and P2 (a) on D1 and D2 (ticket `d1f50e2f`):
`waits_on` items are a string or `{ref, reason}` (S10, S19); `role` a plain string, `any` for T-0 and T-1 (S1); no
`{FACT:…}` family (S5). Counts unchanged; S10's waits_on case renamed (map below).

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
  `name` equal to the stem, `version` semver (`1.2.3`, a string), `role` a plain non-empty string with no brace
  (never a placeholder), `any` for T-0 and T-1 (revision 2, the ticket's "Files").
- **The prose measure (S2)** is the ticket's: the body after the front matter, less fenced code blocks and lines
  starting `|` (indented ones too), counted in characters with the kept lines joined by newlines; T-0 unfilled.
  Budgets are R3 §C's (T-0 and T-1 4,000; T-2 to T-6 3,500; T-7 8,000; T-8 6,000); `facts.yaml`'s `budgets`
  must name each stem at or under them.
- **Placeholders (S5, F1)**: `{KEY}` or `{KEY: description}` with KEY in `[A-Z][A-Z0-9_]*`; `{CMD:name …}` (the
  name runs to the first space or brace, so `{CMD:commit role=x}` names `commit`); `{STEP:name}`. A brace a shell's
  `$` opens (`${HOME}`) and lower-case braces are not placeholders. No other family: an upper-case name and a colon
  with no space after it (`{FACT:x}`) fails S5 unless it is `CMD:` or `STEP:`, so a key's description needs the
  space (`{KEY: description}`). The scan covers the nine templates and the
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
| S10 | `test_w2_128_schemas.py::test_s10_ticket_schema_declares_waits_on_as_a_string_or_ref_and_reason` | red | `waits_on` not declared: a bare string passes, and an object without `ref` passes |
| S10 | `test_w2_128_schemas.py::test_s10_every_existing_ticket_stays_valid` | green (guard) | all 213 tickets validate today; they must after the change (see N-2: `DAEO-2bdu`) |
| S10 | `test_w2_128_schemas.py::test_s10_t1_is_the_ticket_template_with_its_skeleton_in_one_yaml_block` | red | today's `ticket.md` is front matter, with no `name: ticket` and no yaml block |
| S11 | `test_w2_128_round2a.py::test_s11_test_design_read_rule_permits_integrate_and_forbids_only_this_tickets_implementation` | red (2a); green (2b, strengthened) | 2a: no `w2/integrate`, "any path under src/" barred outright; 2b (F3) adds a permitting sentence naming `w2/integrate` or the integrated code, and no clause barring source code or implementation without "ticket"; revised for W2-11 (DEC-866, DEC-981, DEC-1137): the rule is found where it stands (`read_rule`) and may name the integration branch generically |
| S11 | `test_w2_128_round2a.py::test_s11_orchestration_briefs_points_to_the_kernel_templates` | red (2a) | Briefs names the five `brief-*.md` texts and no kernel template |
| S11 | `test_w2_128_round2a.py::test_s11_orchestration_skill_no_longer_says_a_brief_states_each_step_in_full` | red (2a) | "The ticket loop" says `brief-lead.md` "states each step in full" |
| S11 | `test_w2_128_round2a.py::test_s11_k4_no_bar_on_globbing_the_governance_folder` | red (2a) | "No glob, search or listing runs over the project's governance folder" (DEC-508) |
| S11 | `test_w2_128_round2a.py::test_s11_k4_no_bar_on_reading_the_settings_file` | red (2a) | "The settings file and the held-out file are never read" (DEC-525) |
| S11 | `test_w2_128_round2a.py::test_s11_k4_guard_still_bars_the_held_out_contents` | green (guard) | the held-out file is barred today; the restated lines must keep it barred |
| S11 | `test_w2_128_round2a.py::test_s11_k4_lines_are_restated_citing_dec_820` | red (2a); green (2b, strengthened) | 2a: no DEC-820 in the section; 2b (F3) adds that one line citing DEC-820 names all four refusals (secrets, held-out, counterpart/same ticket, hidden half) |
| S11 | `test_w2_128_round2a.py::test_review_f6_orchestration_skill_names_no_retired_brief_text_as_content` | red (2a) | lines 14, 29 and 61 name `brief-*.md` texts as the content |
| S11 | `test_w2_128_round2a.py::test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content[kernel]` | red (2a); green (2b) | `roles/orchestrator.md:39` started a lead "from the kernel template `brief-lead.md`"; round 2a fixed it |
| S11 | `test_w2_128_round2a.py::test_review_f6_orchestrator_role_names_no_retired_brief_text_as_content[rulesync]` | red (2b) | `template/.rulesync/subagents/orchestrator.md:47` still starts a lead "from the kernel template `brief-lead.md`" (review F1) |
| S11 | `test_w2_128_round2a.py::test_s11_judgement_rules_are_in_t6_and_in_no_other_kernel_template` | green (guard) | only `role-reviewer.md` holds `Ordinary work:` and `Consequence:` today |
| S11 | `test_w2_128_round2a.py::test_s11_checkpoint_example_holds_no_daeo_0000` | red (2a) | `checkpoint.md` names `DAEO-0000` in `task:` and `inputs` |
| S11 | `test_w2_128_round2a.py::test_s11_checkpoint_planted_from_its_example_gives_gov_links_no_unknown_id` | red (2a) | `gov links` gives `UNKNOWN_ID` on `DAEO-0000` (line 7, `task:`) |
| S11 | `test_w2_128_round2a.py::test_s11_rulesync_skill_copy_is_byte_equal_to_the_kernel_skill[discovery]` | red (2a) | the copy differs from the kernel skill (version and a line) |
| S11 | `test_w2_128_round2a.py::test_s11_rulesync_skill_copy_is_byte_equal_to_the_kernel_skill[retrieval]` | red (2a) | the copy differs from the kernel skill |
| S11 | `test_w2_128_round2a.py::test_s11_rulesync_skill_copy_is_byte_equal_to_the_kernel_skill[orchestration]` | green (guard) | equal today; must stay equal after the skill changes |
| S11 | `test_w2_128_round2a.py::test_s11_rulesync_skill_copy_is_byte_equal_to_the_kernel_skill[test-design]` | green (guard) | as above |
| S11 | `test_w2_128_round2a.py::test_s11_skill_version_is_one_minor_above_integrates[orchestration]` | red (2b) | `1.1.0` (round 2a's), not `1.2.0`; baseline `a2576c6f` (revised in 2b); revised for W2-11 (DEC-866, DEC-981, DEC-1137): at least one minor above that base, semver, and one version in `version` and `metadata.version` of the kernel skill and its template rulesync copy, not pinned to `1.2.0` (W2-11 raises it again) |
| S11 | `test_w2_128_round2a.py::test_s11_skill_version_is_one_minor_above_integrates[test-design]` | red (2b) | as above |
| S11 | `test_w2_128_round2a.py::test_s11_skills_validator_passes_on_both_skills` | green (guard) | `{"findings": []}` today |
| S11 | `test_w2_128_round2a.py::test_s11_guard_test_design_skill_changes_only_its_read_rule` | green (guard) | only the read rule changed in 2a; 2b also lets a unit elsewhere differ by CAP-38.b re-cited as CAP-38.c; revised for W2-11 (DEC-866, DEC-981, DEC-1137): the front matter may add `metadata.version` equal to `version`, and the read rule's section is the one `read_rule` finds; revised again for W2-11 (DEC-1112 (3) P-W2-11-R6-2 (c)): the sections and the units outside the read rule are read at W2-128's last merge into w2/integrate that changed the skill (`w2_128_merge`, found from history; a shallow clone or no such merge fails), as W2-11 restructures the sections; the front matter is still read now |
| S11 | `test_w2_128_round2a.py::test_s11_guard_orchestration_skill_changes_only_the_named_parts` | green (guard) | only 2a's named lines changed; 2b also frees F2's three lines (DEC-511, DEC-254, DEC-386); revised for W2-11 (DEC-866, DEC-981, DEC-1137): the front matter may add `metadata.version` equal to `version`; the sections and units are read at W2-128's own merge that changed the skill (`w2_128_merge`, found from history; fails if none), as W2-11 rewrites units in most sections (DEC-1112 (3) P-W2-11-R6-2 (c)); the front matter still reads now |
| S11 | `test_w2_128_round2b.py::test_s11_f2_orchestration_requires_no_gov_checkpoint_record_per_round_on_dec_511` | red (2b) | `SKILL.md:76` "A lead writes a real checkpoint with `gov checkpoint` at each round boundary" on DEC-511 alone (lifted by DEC-1057, R-6) |
| S11 | `test_w2_128_round2b.py::test_s11_f2_one_writer_per_tree_cites_dec_963_not_dec_254` | red (2b) | `SKILL.md:55` cites DEC-254 for "never two writing sessions in one tree" |
| S11 | `test_w2_128_round2b.py::test_s11_f2_no_bar_on_reading_another_sessions_folders` | red (2b) | `SKILL.md:83` "nothing is left in or read from another session's folders", a read bar beyond DEC-820's four |
| S11 | `test_w2_128_round2b.py::test_s11_f4_test_design_read_rule_cites_cap_38c_not_cap_38b_or_dec_136` | red (2b) | the read rule cites "(CAP-38.b, DEC-136)" and no CAP-38.c; revised for W2-11 (DEC-866, DEC-981, DEC-1137): the rule is found where it stands (`read_rule`) |
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
| S14 | `test_w2_128_round2b.py::test_s14_checkpoint_template_task_is_empty_with_a_comment_to_fill_it` | red (2b) | `checkpoint.md:7` holds `task: '{ID}'` |
| S14 | `test_w2_128_round2b.py::test_s14_gov_links_on_a_tree_holding_the_checkpoint_template_gives_no_unknown_id[template]` | red (2b) | `gov links` gives `UNKNOWN_ID` `{ID}` (line 7) on the unfilled template at its own path (review F5) |
| S14 | `test_w2_128_round2b.py::test_s14_gov_links_on_a_tree_holding_the_checkpoint_template_gives_no_unknown_id[adopted]` | red (2b) | as above, at an adopted project's `governance/kernel/templates/checkpoint.md` |
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
| S21 | `test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-lead]` | green (revised, DEC-1163 (1), W2-182) | red only when the "until W2-56" line is planted back into the template |
| S21 | `test_w2_128_rows.py::test_row_8_no_unit_carries_the_gov_accept_outside_the_sandbox_until_w2_56_line[role-cto]` | green (revised, DEC-1163 (1), W2-182) | red only when the "until W2-56" line is planted back into the template |
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

**Round 2, not mapped here:** S7, S9, S12, S13 and F2-F6 whole; S11's TPL-6 S1 and S2 (Appendix A's pointer,
`LEAD-w2-common.md` and `build_lead_brief.py`: the CTO's lane) and S4's project half (`JUDGEMENT.md` itself); and
these halves of round-1 lines:
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

## Round 2a (2026-11-09, a fresh designer; S11's text part)

From the ticket's body "Round 2a", S11 (TPL-6 S1-S4) and the round-1 review's F6 and F7, reading integrate's text
(`w2/integrate` at `61231e618`, DEC-963). Nothing of this ticket's implementation was read. 21 cases in
`test_w2_128_round2a.py`, mapped to S11 above: **14 red, 7 green guards** on integrate (the whole folder: 113 collected, 14 failed, 99 passed, 9.0 s). Round 1's 92 cases are
unchanged.

- **The baseline is pinned.** The versions and the guards compare with integrate's text read by
  `git show 61231e61839e…:<path>` at test time, not with the moving `w2/integrate`: once this ticket is merged,
  `w2/integrate` holds the change, and "one minor above integrate" would turn red at the close. "One minor above" is
  `major.(minor+1).0`.
- **Sentences** are a unit (README above) split after `.`, `;`, `:`, `?`, `!` or at a spaced dash. A *bar* is a
  sentence with a negation (`no`, `never`, `not`, `forbid…`, `refus…`, `without`, `n't`).
  - The read rule (the `## ` section whose heading holds "read") must name `w2/integrate`, cite DEC-963, and hold a
    bar naming "implementation" and "ticket". No sentence of the skill may bar `src/` without naming "ticket".
  - K-4: no sentence may name `glob`/`listing`/`search` and "governance", or "settings" and "read", in a bar unless
    it also holds a permitting word (`open`, `may`, `allowed`, `permitted`, `readable`, `free`, `no longer`, `lifted`).
    A sentence naming "held-out" with a bar (`never`, `not`, `no`, `but for`, `except`, `only`, `refus…`) must remain.
    The "protected files" section must cite DEC-820.
- **Briefs and F6.** A retired text (`brief-engineer.md`, `brief-test-designer.md`, `brief-reviewer.md`,
  `brief-product-spec.md`, `brief-lead.md`) may stand in a unit only beside the template that replaces it
  (`role-*.md`). Briefs must name `template/governance/kernel/templates` or a `role-*.md`. "word for word" may not
  stand in Briefs, and neither "each step in full" nor "standing sentences word for word" anywhere in the skill.
  `roles/orchestrator.md` must name a role template, the templates folder or `gov brief`.
- **The guards.** The front matter is unchanged except `version`, and the `## ` headings are the same, in order.
  - test-design: every section other than the read rule is unchanged, unit for unit, white space folded.
  - orchestration: Briefs may change whole. In "Temp hygiene and protected files" the units citing DEC-508 or DEC-525
    may change, and every other unit stays, in order. Elsewhere the unit count is kept, and only a unit that names a
    retired brief text may change (F6: lines 14 and 29).
- **The checkpoint.** It holds no `DAEO-0000`. It is planted as round 1 plants it, with `{ID}` filled with
  `DAEO-t8mp` and any other `{KEY…}` with a plain word, and no other substitution. No `UNKNOWN_ID` may name it.
  `gov links` reads `task:`, not `inputs`, so the string case covers the `inputs` id.
- **The skills validator** runs as `python3 -m gov.check.skill_validator --both-layouts
  template/governance/kernel/skills/{orchestration,test-design}` from the tree root and must exit 0. It refuses an
  unknown `gov` subcommand in code. `gov brief` is not one of its commands on integrate (W2-152 is not merged), so a
  skill naming `` `gov brief` `` in code fails it today.
- **A check of the cases** (a scratch worktree, removed): a stand-in 2a passed all 113 (92 + 21). Each of 19 wrong
  changes then failed the case meant for it, among them:
  - `src/` barred outright; the ticket bar dropped;
  - "word for word" kept; no template named; "each step in full" kept;
  - the glob or the settings bar kept; the held-out bar dropped;
  - `brief-engineer.md` named in the role file; JUDGEMENT copied into T-7; `task: DAEO-9999` in the checkpoint;
  - a stale rulesync copy; version `1.0.1`; an unknown `gov` command;
  - a test-design Inputs line or description changed; an orchestration line added, a temp-hygiene line changed or a
    section renamed.

## Round 2b (2026-11-09, a fresh designer; round 2a's review F1-F4 and its F5 link notice)

From the ticket's body "Round 2b", `reviews/w2-128-r2a.md` (F1-F5), DEC-511/DEC-1057 (R-6), DEC-254, DEC-963,
DEC-820, DEC-1052 and `contract.yaml` CAP-38.b/CAP-38.c, reading integrate's text (`w2/integrate` at `a2576c6f6`,
merged into this branch by the CTO; DEC-963). Nothing of this ticket's implementation was read. Run in the launch
sandbox: **121 collected, 10 failed, 111 passed** (15 s); the exclusion left nothing out.

- **New cases** (`test_w2_128_round2b.py`, 7 node ids; 7 red):
  - F2, per-round checkpoint: no clause naming `gov checkpoint`, "round" and "checkpoint" without a negation or a
    permitting word; no unit cites DEC-511 without DEC-1057.
  - F2, one writer: no DEC-254 in the skill; a unit naming writing sessions (or one writer) and a tree exists and
    cites DEC-963.
  - F2, other sessions: no clause naming another session and "read" in a bar, unless it holds a permitting word or
    names the counterpart / same ticket (DEC-820 (c)). The temp-hygiene line may also be dropped.
  - F4: the read rule cites CAP-38.c and neither CAP-38.b nor DEC-136.
  - The link notice: `checkpoint.md`'s `task:` is empty (`''` or null) and its line carries a `#` comment naming the
    id or ticket; the unfilled template, planted at `template/governance/kernel/templates/checkpoint.md` and at
    `governance/kernel/templates/checkpoint.md` (one tree each, with round 1's `_judge`), gives no `UNKNOWN_ID`.
- **Revised cases** (`test_w2_128_round2a.py`; DEC-866, `Rewrite-Reason:`):
  - F1: the F6 role case is parametrised over the kernel role (`[kernel]`, green) and
    `template/.rulesync/subagents/orchestrator.md` (`[rulesync]`, red). Root `.rulesync/` is the ACT's, not read.
  - F3: the read rule also needs a sentence with a permitting word, "read", no negation, and `w2/integrate` or "the
    integrated code"; no *clause* (a sentence cut again at each comma) may bar `src/`, "source code",
    "implementation" or "production director…" without "ticket". K-4: one unit of "protected files" citing DEC-820
    names secrets, held-out, counterpart or same ticket, and hidden half. Both green on integrate (2a holds them).
  - Versions: baseline `a2576c6f66ae…` (integrate as merged for these cases, 1.1.0); expected `1.2.0`. Red.
  - Guards (still against `61231e618`, so 2a's and 2b's changes together): orchestration frees, in addition, the
    units citing DEC-511 or DEC-254 anywhere and DEC-386 in "protected files"; in every section other than Briefs
    the other units stay in order, and new units may not outnumber the freed ones (a freed unit is restated one for
    one or dropped). Test-design: outside the read rule a unit may differ only by CAP-38.b re-cited as CAP-38.c.
    Both green.
- **Revised for W2-11** (`Rewrite-Reason: DEC-866, DEC-981, DEC-1137`; DEC-1112 (3) P-W2-11-R6-2 (c), P-b):
  - The read rule (`read_rule`): the one section whose heading names reading (not "README") or the work order (W2-11
    moves the rule into "The work order in parallel", DEC-959 item 7; its README map heading also holds "read"),
    cut to its units on reading, the specification and KPIs, the implementation or the integrated code. The branch
    may be named generically ("the integration branch", a kernel skill naming no project branch) in place of
    `w2/integrate`; the permitting sentence, the bar on this ticket's implementation, DEC-963, CAP-38.c and the
    absence of CAP-38.b and DEC-136 stay.
  - Versions: at least `1.2.0` (one minor above `a2576c6f`'s 1.1.0), semver, and `metadata.version`, where carried,
    equal to `version` in the kernel skill and the template's rulesync copy.
  - Guards: the front matter may also carry `metadata` holding only `version` equal to `version`; nothing else.
- **A check of the cases** (a scratch worktree, removed): a stand-in 2b passed all 121. Each of 19 wrong changes
  failed only the case(s) meant for it (`task: '{ID}'` kept fails the three checkpoint cases): the rulesync role keeping `brief-lead.md`; a per-round `gov
  checkpoint` kept after ", and none …"; DEC-511 alone; DEC-254 kept; the one-writer line dropped; the other-session
  read bar kept, or joined by a comma; CAP-38.b or DEC-136 kept beside CAP-38.c; "it does not read source code"
  inside the ticket sentence; the permitting sentence removed; refusal (c) or (d) dropped; `task: '{ID}'` kept; the
  comment removed; version 1.2.1; an unrelated orchestration line changed or one added; a test-design Inputs line
  changed. Two allowed changes stayed green: an Inputs line re-cited to CAP-38.c, the temp-hygiene line dropped.

## Notes and limits

- **N-1 (D1). `on:` in YAML: decided.** PyYAML (YAML 1.1) reads an unquoted key `on` as the boolean `true`. The
  CTO's P1 (b) (2026-11-09, DEC-1109 (2), in the ticket's "Interface and rounds"): the object's key is `ref`, never
  `on`. S19 reads T-1's skeleton as YAML and takes an item that is a non-empty string or an object with `ref` and
  `reason`; an object without `reason` (or keyed `on`) fails it. S10 refuses an object without `ref`, `{on, reason}`
  among them.
- **N-2 (D2). String items: decided.** `DAEO-2bdu` has `waits_on:` as a list of strings. The CTO's P2 (a): an item
  is a string or `{ref, reason}`, so DAEO-2bdu stays valid. S10 now asks the schema to accept string items,
  `{ref, reason}` items and both mixed, and to refuse a bare string (not a list); the guard on every existing ticket
  stays.
- **N-3. F7's rule** is the brief's: a bracketed id must be ACCEPTED. The register's 108 `DONE` entries (records of
  fact) fail it as rules too.
- **N-4. Placeholders outside the interface: decided.** R3's T-7 uses `{FACT:accepted_reds}`; the ticket now says no
  `{FACT:…}` family (a fact is a KEY or a `CMD:`), so S5 fails any such family whatever `keys.yaml` lists.
- **N-5. dod quoting** asks T-1 and T-7 each to hold at least one literal `DOD-n` that `facts.yaml` holds, and to copy
  no dod line of 30 characters or more word for word.
- **N-6. The `.claude/` copies** and the `.rulesync/` sources are not read here (TPL-4, round 2).

## Files

- `w2_128_support.py`: paths, the nine stems and budgets, front matter, the prose measure, units, placeholders,
  `facts.yaml`, the check runner, the register's statuses, the schema validator, the record finder.
- `conftest.py`: puts this folder on the import path.
- `test_w2_128_templates.py` (S1-S5, S18, S20, F1, F7), `test_w2_128_facts.py` (S6, S8, S15),
  `test_w2_128_schemas.py` (S10, S16), `test_w2_128_links.py` (S14, S17, S19), `test_w2_128_rows.py` (S21),
  `test_w2_128_round2a.py` (S11, round 2a, revised in 2b; it reuses `test_w2_128_links.py`'s planting),
  `test_w2_128_round2b.py` (S11 and S14, round 2b; it reuses round 2a's helpers and round 1's planting).
