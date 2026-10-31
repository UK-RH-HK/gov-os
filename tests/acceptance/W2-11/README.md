# W2-11 acceptance tests (DAEO-k7hz, STANDARD, round 1)

Written by the independent test designer from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md` §2,
W2-11), ROLES-SPEC-1 §3.0 and §6.1 (G13, G14, G15), ROLES-RESEARCH-1 §2 and §5.3, SWEEP-2026-10-20 and the
decisions they cite, in parallel with the implementer and without reading its work (DEC-959 item 7, DEC-820 (c)).
Round 1 covers every KPI line but the three-layer split (round 2).

## How to run

The cases find the repository from their own location (`parents[3]` of `w2_11_support.py`), so merged into the
ticket's worktree they judge that worktree's files; the validator case runs that worktree's `src/` (DEC-732):

    TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

Text checks of files (the deliverables are text), plus one subprocess (the skill validator) and one opt-in
subprocess (the brief builder). No network, no copy of the tree; planted files go in `tmp_path`. The suite
takes about 3 seconds.

**Kinds.** Every case is an acceptance case on the repository's own files. `test_w2_11_brief_gaps.py` is
**repository-state**: it reads the live register of gaps (`governance/project/orchestration/brief-gaps.md`) and
the tracked common brief, both outside this ticket's paths; it is green on the base and guards the fixes.

**Reading rules.** A *statement* is a paragraph, a list item with its continuation lines, or a table row, with
whitespace collapsed and `*` and backticks dropped. A rule is *stated* when one statement carries every idea
(case-insensitive patterns). No heading and no sentence is fixed except where the KPI quotes words (the two
judgement questions and the two finding lines, KPI 12).

## KPI map

The map below is the form a per-KPI runner reads (W2-96, `gov accept`): one entry per KPI line, its pytest node
ids (a node id without brackets covers every parametrised case of that test), and the red reason on the base
(`4c064bab02b4`).

```yaml
kpi_map:
  - kpi: "1. Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule and the two-refusal stop [AR-5, AR-6]"
    tests: [test_w2_11_briefs.py::test_the_twelve_fields_come_first_payload_after_and_two_refusals_stop]
    red_on_base: "the briefs and the skill do not name the twelve fields"
  - kpi: "2. They carry Policy 2's read rule (DEC-820) and the decision-record rule (DEC-861, DEC-862) [DEC-866]"
    tests: [test_w2_11_briefs.py::test_policy_2_reads_open_with_its_refusals,
            test_w2_11_briefs.py::test_the_owners_decisions_are_recorded_by_decision_record_commits]
    red_on_base: "no file cites DEC-820 or DEC-861"
  - kpi: "3. The audit brief states DEC-430 [F-m1, W2-L268]"
    tests: [test_w2_11_briefs.py::test_the_audit_brief_of_the_orchestration_skill_states_dec_430]
    red_on_base: "the orchestration skill does not state DEC-430 (the audit skill already does)"
  - kpi: "4. The launcher command is stated as a command, not a code span [W2-L257]"
    tests: [test_w2_11_briefs.py::test_the_launcher_command_is_a_command_not_a_code_span]
    red_on_base: "brief-lead.md has the <launcher command> placeholder and `gov launch` in a code span"
  - kpi: "5. The five brief templates carry record frontmatter [W2-L258]; loose citations are fixed [W2-L256]"
    tests: [test_w2_11_briefs.py::test_the_brief_template_carries_record_frontmatter,
            test_w2_11_briefs.py::test_identity_through_the_settings_argument_is_not_cited_to_dec_183,
            test_w2_11_briefs.py::test_dec_486_is_not_cited_for_the_stops_short_block]
    red_on_base: "no brief has frontmatter; the skill cites DEC-183 for identity and DEC-486 for the stop's block"
  - kpi: "6. Supersession (DEC-866): no LEAD_CHECKPOINT or 'at about <context limit> tokens', no listing or search refusal, held-out names readable, no fixed ceiling, owner decisions by decision-record commits; DEC-460 stays; a planted file teaching an old rule fails"
    tests: [test_w2_11_supersession.py::test_every_swept_file_is_there,
            test_w2_11_supersession.py::test_the_file_teaches_no_superseded_rule,
            test_w2_11_supersession.py::test_dec_460s_citation_for_naming_the_model_stays,
            test_w2_11_supersession.py::test_a_planted_file_that_still_teaches_the_old_rule_fails,
            test_w2_11_supersession.py::test_a_file_stating_only_the_current_rules_passes]
    red_on_base: "all 13 swept files teach an old rule; the DEC-460 and planted cases pass on the base (they test the check)"
  - kpi: "7. W1-35's cases that require the old sentences are revised with Rewrite-Reason"
    tests: ["../W1-35/test_w1_35_orchestration.py::TestBriefTemplates::test_the_brief_carries_the_standing_sentences_word_for_word",
            "../W1-35/test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated",
            "../W1-35/test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_says_what_a_lead_returns"]
    red_on_base: "after the revision: [parallel tickets], [the ticket loop] and [temp hygiene and protected files] are red (no 'no fixed number', no checkpoint at every handover, no DEC-820); the other two pass"
  - kpi: "8. The test-design skill: proportion (DEC-951 item 5), test kinds, run-time cost, no whole-tree copies, live-repository tests declared (DEC-889 item 11 c), the parallel work order, red against the base, ISTQB's techniques, the README map for gov accept (DEC-959 items 6 and 7)"
    tests: [test_w2_11_skills.py::test_the_test_design_skill_states]
    red_on_base: "test-design cites none of DEC-951, DEC-889, DEC-959"
  - kpi: "9. One skill template, template/governance/kernel/templates/skill.md [DEC-959 item 5]"
    tests: [test_w2_11_skills.py::test_the_skill_template_has_the_front_matter_and_the_sections_in_order,
            test_w2_11_skills.py::test_the_skill_template_states_its_rules]
    red_on_base: "skill.md does not exist"
  - kpi: "10. Orchestration's three reference files and the qa-review skill [DEC-959 items 1 and 3]"
    tests: [test_w2_11_skills.py::test_orchestration_has_the_reference_file,
            test_w2_11_skills.py::test_the_qa_review_skill_states,
            test_w2_11_skills.py::test_the_qa_review_skill_has_its_three_copies,
            test_w2_11_skills.py::test_every_copy_carries_the_kernel_skills_body]
    red_on_base: "no reference file and no qa-review skill; the copies of test-design, orchestration and audit already match (green)"
  - kpi: "11. Every gap fixed in the common brief or the brief builder stays fixed [DEC-943 item 1, DEC-954]"
    tests: [test_w2_11_brief_gaps.py::test_the_register_has_fixed_gaps_to_keep,
            test_w2_11_brief_gaps.py::test_the_fixed_gap_is_still_in_the_brief,
            test_w2_11_brief_gaps.py::test_a_brief_built_today_carries_every_fix]
    red_on_base: "green on the base (repository-state: the ten fixed gaps are in the common brief); the builder case is skipped unless GOV_BRIEF_BUILDER names the builder"
  - kpi: "12. G15: brief-reviewer and the audit skill ask the two questions word for word, require the two finding lines, and say a 'no' is a row, never a round [DEC-808]"
    tests: [test_w2_11_briefs.py::test_the_judgement_rules_stand_word_for_word]
    red_on_base: "neither file carries the two questions"
  - kpi: "13. G14: brief-lead carries the common brief's role-independent rules and requires brief_gaps: in the return [DEC-943 item 1]"
    tests: [test_w2_11_briefs.py::test_the_lead_brief_carries_the_role_independent_rule]
    red_on_base: "brief-lead.md cites none of DEC-836, DEC-860, DEC-859, DEC-732, DEC-898, DEC-837, DEC-959, DEC-943"
  - kpi: "14. G13: every kernel skill but adopt carries one version in its kernel source, both rulesync sources and its .claude copy [DEC-832 item 2, DEC-981]"
    tests: [test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places]
    red_on_base: "no .claude/skills copy carries metadata.version"
  - kpi: "15. DEC-791 (ii): the skill and the briefs state DEC-715/731, 719, 732/733, 847, 750/754, 757 item 6, 766, 768 item 4, 779, 780/787 with their ids"
    tests: [test_w2_11_briefs.py::test_the_kernel_states_the_distilled_decisions]
    red_on_base: "none of the ids is cited in the kernel corpus"
  - kpi: "16. Failure: the skill validator refuses a brief without the twelve-field rule"
    tests: [test_w2_11_validator.py::test_the_validator_accepts_the_brief_and_refuses_it_without_the_twelve_fields]
    red_on_base: "the validator refuses the brief as it stands (SKILL_NO_FRONTMATTER): it reads no brief"
  - kpi: "17. Nothing scoped to this repository in the kernel files tested (no W ids, ticket ids or main-tree paths)"
    tests: [test_w2_11_briefs.py::test_no_id_or_path_of_this_repository_in_a_kernel_file]
    red_on_base: "green on the base; it guards the new text"
```

## Notes for the lead and the reviewer

- **KPI 4 (W2-L257), reading:** "stated as a command" is read as a command line beginning `gov launch ` in a
  fenced or indented command block of `brief-lead.md`, with no `<launcher command>` placeholder and no inline code
  span holding `gov launch`. The role file's part of the row is W2-33's (DEC-981: the role file keeps only DEC-866's
  sweep sentences here), so it is not tested.
- **KPI 5 (W2-L256):** of the five loose citations the bootstrap note names, the two with one clear fix are
  tested (DEC-183 for identity, DEC-371 superseded it; DEC-486 for the stop's block). The other three (DEC-235
  and DEC-416 for "never into the main branch", DEC-254 for two writing sessions, DEC-236 and DEC-449 for the last
  known state) have no stated correct citation; they are left to the reviewer.
- **KPI 5 (W2-L258):** the frontmatter is checked against the shared record frontmatter of
  `common.schema.json` (`id`, `type`, `status`, `state_class`). A brief schema is not in this ticket's paths.
- **KPI 14 (G13):** in the `.claude/skills/` copy the version is read from `metadata.version`, the one key rulesync
  writes that can hold it, and every top-level key must be one rulesync writes. Elsewhere `version` or
  `metadata.version`. The vendored skills (`superpowers/`) and the openspec skills are not kernel skills; `adopt`
  is W2-52's.
- **KPI 15:** every group is required in the kernel corpus (the orchestration skill's folder and the five briefs),
  as the KPI lists them. Which groups are scoped to this repository (and so belong in the project prompt) is
  package P-W2-11-TD-1; a group the orchestrator rules repository-scoped is dropped by a test revision.
- **KPI 16:** the validator's code (`src/gov/check/skill_validator.py`) is outside this round's implementer's
  paths, so the case may stay red until the orchestrator decides (package P-W2-11-TD-2).
- **KPI 11:** the case that runs the builder is opt-in, because the builder is untracked and absent from every
  clone: `GOV_BRIEF_BUILDER=<path of build_lead_brief.py>` runs it on this repository's common brief
  (`GOV_BRIEF_COMMON`). A row marked fixed in the register without a matching entry in `FIXES` fails until the test
  designer adds its case.
