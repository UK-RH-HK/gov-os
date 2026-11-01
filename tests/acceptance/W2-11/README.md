# W2-11 acceptance tests (DAEO-k7hz, STANDARD, round 1)

Written by the independent test designer from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md` §2,
W2-11), ROLES-SPEC-1 §3.0 and §6.1 (G13, G14, G15), ROLES-RESEARCH-1 §2 and §5.3, SWEEP-2026-10-20 and the
decisions they cite, in parallel with the implementer and without reading its work (DEC-959 item 7, DEC-820 (c)).
Round 1 covers every KPI line but the three-layer split and the lines DEC-983 puts in round 2 (below).

## How to run

The cases find the repository from their own location (`parents[3]` of `w2_11_support.py`), so merged into the
ticket's worktree they judge that worktree's files; the run uses that worktree's `src/` (DEC-732):

    TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

Text checks of files (the deliverables are text), plus one opt-in subprocess (the brief builder). No network, no copy of the tree; planted files go in `tmp_path`. The suite
takes about 3 seconds.

**Kinds.** Every case is an acceptance case on the repository's own files. `test_w2_11_brief_gaps.py` is
**repository-state**: it reads the live register of gaps (`governance/project/orchestration/brief-gaps.md`) and
the tracked common brief, both outside this ticket's paths; it is green on the base and guards the fixes.

**Reading rules.** A *statement* is a paragraph, a list item with its continuation lines, or a table row, with
whitespace collapsed and `*` and backticks dropped. A rule is *stated* when one statement carries every idea
(case-insensitive patterns). No heading and no sentence is fixed except where the KPI quotes words (the two
judgement questions and the two finding lines, the card's G15).

## KPI map

The table is the form `gov accept` reads (W2-96, DEC-959 item 6): one row per KPI line of the ticket file, named
by its numbering there (`success-N`, `failure-N`), with the cases that show it as code spans (a case without
brackets covers every parametrised case of that test) and the red reason on the base (`4c064bab02b4`).

| KPI | Test | Red on the base |
|---|---|---|
| success-1 (proportion, DEC-951 item 5) | `test_w2_11_skills.py::test_the_test_design_skill_states[proportion: the minimum that shows each KPI line and failure line [DEC-951 item 5]]`, `test_w2_11_skills.py::test_the_test_design_skill_states[W2-60a's 2,980 test lines for 713 code lines are out of proportion]` | test-design cites no DEC-951 |
| success-2 (twelve fields, payload after, two-refusal stop) | `test_w2_11_briefs.py::test_the_twelve_fields_come_first_payload_after_and_two_refusals_stop` | the briefs and the skill do not name the twelve fields |
| success-3 (Policy 2's read rule, the decision-record rule) | `test_w2_11_briefs.py::test_policy_2_reads_open_with_its_refusals`, `test_w2_11_briefs.py::test_the_owners_decisions_are_recorded_by_decision_record_commits` | no file cites DEC-820 or DEC-861 |
| success-4 (the audit brief states DEC-430) | `test_w2_11_briefs.py::test_the_audit_brief_of_the_orchestration_skill_states_dec_430` | the orchestration skill does not state DEC-430 (the audit skill already does) |
| success-5 (the launcher command as a command) | `test_w2_11_briefs.py::test_the_launcher_command_is_a_command_not_a_code_span` | brief-lead.md has the launcher-command placeholder and gov launch in a code span |
| success-6 (record frontmatter, loose citations) | `test_w2_11_briefs.py::test_the_brief_template_carries_record_frontmatter`, `test_w2_11_briefs.py::test_identity_through_the_settings_argument_is_not_cited_to_dec_183`, `test_w2_11_briefs.py::test_dec_486_is_not_cited_for_the_stops_short_block` | no brief has frontmatter; the skill cites DEC-183 for identity and DEC-486 for the stop's block |
| success-7 (supersession, DEC-866) | `test_w2_11_supersession.py::test_every_swept_file_is_there`, `test_w2_11_supersession.py::test_the_file_teaches_no_superseded_rule`, `test_w2_11_supersession.py::test_dec_460s_citation_for_naming_the_model_stays` | all 13 swept files teach an old rule; the DEC-460 case passes on the base |
| success-8 (test kinds, run-time cost, no whole-tree copy, live-repository tests declared) | `test_w2_11_skills.py::test_the_test_design_skill_states[the test kinds [DEC-889 item 11 c]]`, `test_w2_11_skills.py::test_the_test_design_skill_states[the run-time cost a test may take and how it is measured]`, `test_w2_11_skills.py::test_the_test_design_skill_states[no copy of the whole working tree where a minimal fixture will do]`, `test_w2_11_skills.py::test_the_test_design_skill_states[a test of the live repository's own state is declared as such]` | test-design cites no DEC-889 |
| success-9 (every fixed brief gap stays fixed) | `test_w2_11_brief_gaps.py::test_the_register_has_fixed_gaps_to_keep`, `test_w2_11_brief_gaps.py::test_the_fixed_gap_is_still_in_the_brief`, `test_w2_11_brief_gaps.py::test_a_brief_built_today_carries_every_fix` | green on the base (repository-state: the ten fixed gaps are in the common brief); the builder case is skipped unless GOV_BRIEF_BUILDER names the builder |
| success-10 (one skill template) | `test_w2_11_skills.py::test_the_skill_template_has_the_front_matter_and_the_sections_in_order`, `test_w2_11_skills.py::test_the_skill_template_states_its_rules` | skill.md does not exist |
| success-11 (work order in parallel, red against the base, ISTQB, proportion, the README map) | `test_w2_11_skills.py::test_the_test_design_skill_states[the work order in parallel, never reading the engineer's work [DEC-959 item 7]]`, `test_w2_11_skills.py::test_the_test_design_skill_states[red against the ticket's base]`, `test_w2_11_skills.py::test_the_test_design_skill_states[ISTQB's black-box techniques]`, `test_w2_11_skills.py::test_the_test_design_skill_states[proportion: the minimum that shows each KPI line and failure line [DEC-951 item 5]]`, `test_w2_11_skills.py::test_the_test_design_skill_states[the README map of KPI lines to tests that gov accept reads]` | test-design cites no DEC-959 |
| success-12 (orchestration's three reference files, the qa-review skill) | `test_w2_11_skills.py::test_orchestration_has_the_reference_file`, `test_w2_11_skills.py::test_the_qa_review_skill_states`, `test_w2_11_skills.py::test_the_qa_review_skill_has_its_three_copies`, `test_w2_11_skills.py::test_every_copy_carries_the_kernel_skills_body` | no reference file and no qa-review skill; the copies of test-design, orchestration and audit already match (green) |
| success-13 (the lead brief's brief_gaps section) | `test_w2_11_briefs.py::test_the_lead_brief_carries_the_role_independent_rule[brief_gaps in the return]` | brief-lead.md does not cite DEC-943 |
| failure-1 (a file still teaching a superseded rule fails a test) | `test_w2_11_supersession.py::test_a_planted_file_that_still_teaches_the_old_rule_fails`, `test_w2_11_supersession.py::test_a_file_stating_only_the_current_rules_passes` | both pass on the base (they test the check) |

**The failure line that moved, not in the table (DEC-995, DEC-996).** The former failure line "the skill
validator refuses a brief without the twelve-field rule" (row W2-L097) moved to W2-120, a child engineer ticket
that runs after W2-11, under DEC-995 and DEC-996; W2-120's own test designer writes its case, so this suite has
none. With that line removed from the ticket file, the DEC-866 line is `failure-1`; it was `failure-2` before the
removal, and its cases and red reason are unchanged.

**Round 2's lines, not in the table (DEC-983).** success-14 (the anti-drift kit), success-15 (scope control) and
success-16 (a timing test measures the work under test) have no case in round 1; they are round 2's, so the table
names no line that no case shows. success-13's second half (the orchestration skill states that the gaps are fixed
in the template within the week) has no case in round 1 either; its row shows the first half only.

**Cases not under a ticket line (`gov accept` counts them as unmapped, without names).** These show the card's
lines (ROLES-SPEC-1 §6.1 and DEC-791 (ii)), which no ticket KPI line plainly states:

- G13, one version in all four places of every kernel skill but adopt (DEC-832 item 2, DEC-981):
  `test_w2_11_skills.py::test_the_skill_carries_one_version_in_all_four_places`; red on the base: no `.claude/skills`
  copy carries `metadata.version`.
- G15, the judgement rules word for word in brief-reviewer and the audit skill (DEC-808):
  `test_w2_11_briefs.py::test_the_judgement_rules_stand_word_for_word`; red on the base: neither file carries the
  two questions.
- G14, the lead brief's other seven role-independent rules (DEC-836, DEC-860, DEC-859, DEC-732, DEC-898, DEC-837,
  DEC-959): the other cases of `test_w2_11_briefs.py::test_the_lead_brief_carries_the_role_independent_rule`; red on
  the base: brief-lead.md cites none of them.
- DEC-791 (ii), the standing decisions distilled: `test_w2_11_briefs.py::test_the_kernel_states_the_distilled_decisions`;
  red on the base: none of the ids is cited in the kernel corpus.
- Nothing scoped to this repository in the kernel files:
  `test_w2_11_briefs.py::test_no_id_or_path_of_this_repository_in_a_kernel_file`; green on the base, it guards the
  new text.

**success-7's last sentence (W1-35's cases revised with Rewrite-Reason)** is shown in `tests/acceptance/W1-35/`,
outside the folder `gov accept` runs for this ticket, so it is not in the table:
`test_w1_35_orchestration.py::TestBriefTemplates::test_the_brief_carries_the_standing_sentences_word_for_word`,
`test_w1_35_orchestration.py::TestRows::test_every_clause_of_the_row_is_stated` and
`test_w1_35_orchestration.py::TestTicketLeadSection::test_the_section_says_what_a_lead_returns`. After the revision,
the rows [parallel tickets], [the ticket loop] and [temp hygiene and protected files] are red on the base (no "no
fixed number", no checkpoint at every handover, no DEC-820); the other two pass.

## Notes for the lead and the reviewer

- **success-5 (W2-L257), reading:** "stated as a command" is read as a command line beginning `gov launch ` in a
  fenced or indented command block of `brief-lead.md`, with no `<launcher command>` placeholder and no inline code
  span holding `gov launch`. The role file's part of the row is W2-33's (DEC-981: the role file keeps only DEC-866's
  sweep sentences here), so it is not tested.
- **success-6 (W2-L256):** of the five loose citations the bootstrap note names, the two with one clear fix are
  tested (DEC-183 for identity, DEC-371 superseded it; DEC-486 for the stop's block). The other three (DEC-235
  and DEC-416 for "never into the main branch", DEC-254 for two writing sessions, DEC-236 and DEC-449 for the last
  known state) have no stated correct citation; they are left to the reviewer.
- **success-6 (W2-L258):** the frontmatter is checked against the shared record frontmatter of
  `common.schema.json` (`id`, `type`, `status`, `state_class`). A brief schema is not in this ticket's paths.
- **G13:** in the `.claude/skills/` copy the version is read from `metadata.version`, the one key rulesync
  writes that can hold it, and every top-level key must be one rulesync writes. Elsewhere `version` or
  `metadata.version`. The vendored skills (`superpowers/`) and the openspec skills are not kernel skills; `adopt`
  is W2-52's.
- **DEC-791 (ii):** every group is required in the kernel corpus (the orchestration skill's folder and the five
  briefs), as the card lists them. Which groups are scoped to this repository (and so belong in the project prompt)
  is package P-W2-11-TD-1; a group the orchestrator rules repository-scoped is dropped by a test revision.
- **success-9:** the case that runs the builder is opt-in, because the builder is untracked and absent from every
  clone: `GOV_BRIEF_BUILDER=<path of build_lead_brief.py>` runs it on this repository's common brief
  (`GOV_BRIEF_COMMON`). A row marked fixed in the register without a matching entry in `FIXES` fails until the test
  designer adds its case.
