# W2-129 acceptance tests: `gov links`, one cheap, incremental, read-only link-integrity check

Ticket DAEO-q7lk (W2-129), profile STANDARD, before re-pin window 4 (DEC-1087 (4); DEC-1073 (5)(b), DEC-1052).
Written by the independent test designer (MR-3) from the ticket's KPI lines and LINK-INTEGRITY.md §4, before any
implementation, reading only the integrated code (branch base `fc61f303d467`; `w2/integrate` `e3355def9f99` holds
the same loader, decisions, CLI and accept code, DEC-963).

**The numbering.** The lines are numbered in the ticket's order: S1 to S15 for its fifteen success lines, F1 to F6
for its failure lines. (The brief counted thirteen and called never-a-gate S11 and the timing S12; in the ticket's
order they are **S13** and **S15**, and "any repository" is S14.) **S16** is the ticket-changes line DEC-1088 (6)
added after them. **S17** (planted ids in test fixtures) and its failure line **F7** are D-6 part 2's (DEC-1109 (2),
DEC-1098 (3) row 24).

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-129 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

About 4 s. No GPU, no model, no network, no store. `gov links` runs as a child process
(`python3 -m gov.cli.main links --root <planted repo> ...`) of the tree `PYTHONPATH` names (without one, this
worktree's `src`), with `PYTHONDONTWRITEBYTECODE=1`, no `GIT_*` variable inherited and git's system and global
configuration unread.

- **Repository A** (`w2_129_support.build_full`, once per session, in a temporary folder; each test that commits,
  writes a mark or applies a patch takes its own copy). Its first commit (`root`) holds only a README, so
  `--since <root>` makes every record and every commit "changed". Then one commit of the records (`Task: DAEO-t002`,
  `Role: orchestrator`), a branch `w2/W2-901` with an engineer's commit (`Implements: DEC-105`) and a test
  designer's (`Implements: DEC-120`), a landing merge (`Role: orchestrator`, `Implements: DEC-113`), a research
  commit with an unknown `Task: DAEO-zzzz` and `Implements: DEC-997`, and a `Task: decision-record` commit.
  - The register (`docs/DECISION_REGISTER.md`, named by the path map): DEC-102 `**Supersedes:** DEC-101` (ids
    alone), DEC-104 `**Changes:** DEC-103 item 2`, DEC-105 `**Changed by:** DEC-106 (item 1)` (marked), DEC-107
    `SUPERSEDED by DEC-108` (marked), DEC-110 `**Supersedes:** the last point of DEC-109` (a part), DEC-112's free
    text "The window of DEC-111 is amended by DEC-112.", entries with no mark (DEC-100, 101, 103, 109, 111, 130),
    DEC-120 PROPOSED, DEC-121 REJECTED, DEC-124 WITHDRAWN, DEC-122 `**Under:** DEC-120`, DEC-123
    `**Under:** DEC-999`, DEC-133 tagged `done`.
  - `governance/project/orchestration/ARCHIVE-SUPERSEDED.md`: §A "DEC-105: changed by DEC-106" (marked) and
    "DEC-130: amended by DEC-131" (unmarked); §B DEC-132 and DEC-133 spent.
    `governance/project/orchestration/DECISIONS-IN-FORCE.md`: DEC-100 and DEC-107.
  - Tickets: DAEO-t001 (in progress: sources DEC-100, PROPOSED DEC-120, unknown DEC-998; KPI brackets
    `[DEC-100, DEC-104]` and `[DEC-121]`; `links: [DAEO-gone]`; a missing acceptance path), DAEO-t002 (closed, with
    its close record, citing DEC-120 and the list row W2-L001), DAEO-t003 (in progress, but a close record exists),
    DAEO-t004 (open: SUPERSEDED DEC-107 in sources, a missing acceptance path), DAEO-t005 (clean).
  - A lesson (unknown DAEO-nope and DEC-992), a plan (unknown DEC-993), the list file `docs/plan/WAVE_2_LIST.md`
    (row W2-L001), checkpoints (one with an unknown task), a checkpoint under `docs/research/` and a close record
    under `docs/audit/` (unknown tasks), a kernel skill line citing PROPOSED DEC-120 and unknown DEC-991, a prompt
    line citing REJECTED DEC-121, a brief line citing WITHDRAWN DEC-124, a path-map comment citing DEC-120,
    `docs/contract/contract.yaml` (status ACCEPTED; MR-1's providers W2-901 and the missing W9-999) with MR-1.md
    PROPOSED and MR-2.md ACCEPTED, `src/app/limits.py` and DAEO-t004 citing the superseded DEC-107 (W2-55's two
    propagation findings), and a test file citing unknown DEC-995.
- **Repository B** (`build_bare`): a path map naming no register; no `.tickets/`, no `contract.yaml`, no archive.
- **The oracles** never read `gov.links`: line numbers and status lines come from the planted text
  (`line_of`, `entry_lines`, `status_line`); the unmarked pairs from the loader's own `register_statements` plus
  ARCHIVE-SUPERSEDED §A read with the loader's `_BY`, as `docs/research/W2-92-proto-drift.py` reads them, under its
  "no hint in its own entry" rule (`statement_pairs`); the ENFORCES_SUPERSEDED set from W2-55's
  `check_propagation` itself; the role from the KPI's table (`role_of`).
- **The probe** (`w2_129_probe.py`) runs `gov links` in one process under an audit hook and reports every process
  started, every socket call, every file opened for writing (or created, renamed, removed) and the modules loaded.

## KPI lines, tests, and the outcome on the branch base `fc61f303d467`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **103 tests, 99 failed, 4 passed** (3.3 s). Every red fails on the same
first cause, `there is no gov links command in the tree under test` (argparse's `invalid choice: 'links'`, caught
before any assertion, so no exit code 2 of argparse passes for one of `gov links`'s), or, for the two S8 source
cases, `there is no gov.links package`. The four greens are two premises and the two S13 guards.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_129_command.py::test_s1_runs_with_no_store_reading_head_as_the_loader_does` | red | no `gov links`; then: exit 1 and the first line on a repository with no store, and no store made |
| S1 | `test_w2_129_command.py::test_s1_reads_head_never_the_working_tree` | red | no `gov links`; then: an uncommitted unknown source and an untracked ticket give no finding |
| S1 | `test_w2_129_command.py::test_s1_writes_nothing_but_its_mark_the_head_it_judged` | red | no `gov links`; then: every file hashed before and after, HEAD, refs and status unchanged; `.gov-runtime/` holds only the mark, HEAD's sha |
| S1 | `test_w2_129_command.py::test_s1_starts_only_git_opens_no_socket_and_writes_only_the_mark` | red | no `gov links`; then (the probe): only git started, no socket call, no write outside `.gov-runtime/links/`, no model or network module |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_names_both_ids_and_the_form[supersedes-ids-alone]` | red | no `gov links`; then: DEC-101 <- DEC-102, the form `Supersedes`, in the register within either entry |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_names_both_ids_and_the_form[changes-a-part]` | red | as above: DEC-103 <- DEC-104, `Changes` |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_names_both_ids_and_the_form[supersedes-a-part]` | red | as above: DEC-109 <- DEC-110, `Supersedes` |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_names_both_ids_and_the_form[free-text-amended-by]` | red | as above: DEC-111 <- DEC-112, `amended` |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_names_both_ids_and_the_form[archive-section-a]` | red | as above: DEC-130 <- DEC-131 from ARCHIVE §A (its entry or the archive's line) |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_says_whether_the_change_is_whole_or_of_a_part[supersedes-ids-alone]` | red | no `gov links`; then: the line says `whole` |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_says_whether_the_change_is_whole_or_of_a_part[changes-a-part]` | red | as above: `part` |
| S2 | `test_w2_129_findings.py::test_s2_unmarked_change_says_whether_the_change_is_whole_or_of_a_part[supersedes-a-part]` | red | as above: `part` |
| S2 | `test_w2_129_findings.py::test_s2_guard_an_entry_that_names_its_changer_gives_no_unmarked_change[changed-by]` | red | no `gov links`; then: DEC-105 names DEC-106 (`Changed by:`), so no finding |
| S2 | `test_w2_129_findings.py::test_s2_guard_an_entry_that_names_its_changer_gives_no_unmarked_change[superseded-by]` | red | as above: DEC-107 `SUPERSEDED by DEC-108` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[ticket-sources]` | red | no `gov links`; then: DEC-998 at DAEO-t001's source line |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[ticket-links]` | red | as above: DAEO-gone at `links:` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[ticket-acceptance-path]` | red | as above: `tests/acceptance/W2-901` at `acceptance_tests` or its `path:` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[register-label-under]` | red | as above: DEC-999 at DEC-123's `**Under:**` line |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[commit-task]` | red | as above: `Task: DAEO-zzzz` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[commit-implements]` | red | as above: `Implements: DEC-997` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[contract-provider]` | red | as above: W9-999 at its line of `contract.yaml` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[lesson-constrains]` | red | as above: DAEO-nope at the lesson's `constrains:` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[lesson-sources]` | red | as above: DEC-992 at the lesson's `sources:` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[plan-decisions]` | red | as above: DEC-993 at the plan's `decisions:` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[checkpoint-task]` | red | as above: DAEO-qqqq at a checkpoint's `task:` |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[kernel-skill-line]` | red | as above: DEC-991 at the kernel skill's line |
| S3 | `test_w2_129_findings.py::test_s3_unknown_id_in_each_typed_place[test-file-id]` | red | as above: DEC-995 at its line of a test file |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[decision-record]` | red | no `gov links`; then: `Task: decision-record` is no finding (DEC-861) |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[W2-L001]` | red | as above: a row the list file holds |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[DAEO-t002]` | red | as above: a ticket (DAEO-t001's parent and dependency) |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[W2-901]` | red | as above: a W2 id read through `external-ref` (MR-1's provider) |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[W2-902]` | red | as above: MR-2's provider |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[DEC-100]` | red | as above: a register entry |
| S3 | `test_w2_129_findings.py::test_s3_guard_what_exists_is_no_unknown_id[DEC-113]` | red | as above: the landing's `Implements:` |
| S3 | `test_w2_129_findings.py::test_s3_guard_no_unknown_id_in_a_ticket_whose_typed_places_resolve_or_are_not_judged[closed-ticket-paths-exist]` | red | no `gov links`; then: DAEO-t002's acceptance path exists and W2-L001 is a list row |
| S3 | `test_w2_129_findings.py::test_s3_guard_no_unknown_id_in_a_ticket_whose_typed_places_resolve_or_are_not_judged[open-ticket-not-judged]` | red | as above: DAEO-t004 is open, so its missing acceptance path is not judged (N-6) |
| S4 | `test_w2_129_findings.py::test_s4_unlinked_id_from_a_kpi_bracket` | red | no `gov links`; then: DEC-104 and DEC-121, in DAEO-t001's KPI brackets, not in its sources |
| S4 | `test_w2_129_findings.py::test_s4_unlinked_id_from_a_worker_commit_s_implements` | red | no `gov links`; then: the engineer's `Implements: DEC-105`, not in DAEO-t001's sources |
| S4 | `test_w2_129_findings.py::test_s4_guard_no_unlinked_id_for_a_linked_id_or_a_landing_commit[linked-in-sources]` | red | no `gov links`; then: DEC-100 is in the sources |
| S4 | `test_w2_129_findings.py::test_s4_guard_no_unlinked_id_for_a_linked_id_or_a_landing_commit[landing-commit-implements]` | red | as above: the landing commit's DEC-113 (never a worker commit) |
| S4 | `test_w2_129_findings.py::test_s4_guard_no_unlinked_id_for_a_linked_id_or_a_landing_commit[worker-implements-in-sources]` | red | as above: the test designer's DEC-120 is in the sources |
| S5 | `test_w2_129_findings.py::test_s5_status_conflict_between_two_records[register-current-archive-spent]` | red | no `gov links`; then: DEC-132 current in the register, spent in §B |
| S5 | `test_w2_129_findings.py::test_s5_status_conflict_between_two_records[in-force-list-register-superseded]` | red | as above: DEC-107 listed in force, SUPERSEDED in the register |
| S5 | `test_w2_129_findings.py::test_s5_status_conflict_between_two_records[ticket-against-its-close-record]` | red | as above: DAEO-t003 in progress, its close record written |
| S5 | `test_w2_129_findings.py::test_s5_status_conflict_between_two_records[mr-record-against-contract-yaml]` | red | as above: MR-1.md PROPOSED, `contract.yaml` ACCEPTED |
| S5 | `test_w2_129_findings.py::test_s5_guard_records_that_agree_give_no_status_conflict[done-and-spent]` | red | no `gov links`; then: DEC-133 done and spent |
| S5 | `test_w2_129_findings.py::test_s5_guard_records_that_agree_give_no_status_conflict[in-force-and-current]` | red | as above: DEC-100 in force and current |
| S5 | `test_w2_129_findings.py::test_s5_guard_records_that_agree_give_no_status_conflict[closed-with-close-record]` | red | as above: DAEO-t002 closed with its close record |
| S5 | `test_w2_129_findings.py::test_s5_guard_records_that_agree_give_no_status_conflict[mr-accepted]` | red | as above: MR-2.md ACCEPTED |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[proposed-in-ticket-sources]` | red | no `gov links`; then: DEC-120 at DAEO-t001's source line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[rejected-in-kpi-bracket]` | red | as above: DEC-121 at DAEO-t001's KPI line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[superseded-in-open-ticket-sources]` | red | as above: DEC-107 at DAEO-t004's source line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[proposed-in-register-under]` | red | as above: DEC-120 at DEC-122's `**Under:**` line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[proposed-in-kernel-skill-line]` | red | as above: DEC-120 at the kernel skill's line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[rejected-in-prompt-line]` | red | as above: DEC-121 at the prompt's line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[withdrawn-in-brief-line]` | red | as above: DEC-124 at the brief's line |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[proposed-in-path-map-comment]` | red | as above: DEC-120 at the path map's comment |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[proposed-in-ticket-sources]` | red | no `gov links`; then: the line names PROPOSED |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[rejected-in-kpi-bracket]` | red | as above: REJECTED |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[superseded-in-open-ticket-sources]` | red | as above: SUPERSEDED |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[proposed-in-register-under]` | red | as above: PROPOSED |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[proposed-in-kernel-skill-line]` | red | as above: PROPOSED |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[rejected-in-prompt-line]` | red | as above: REJECTED |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[withdrawn-in-brief-line]` | red | as above: WITHDRAWN |
| S6 | `test_w2_129_findings.py::test_s6_the_finding_names_the_decision_s_status[proposed-in-path-map-comment]` | red | as above: PROPOSED |
| S6 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_a_judged_commit_s_implements` | red | no `gov links`; then: the test designer's commit's `Implements: DEC-120` |
| S6 | `test_w2_129_findings.py::test_s6_guard_a_closed_ticket_and_a_decision_in_force_give_none` | red | no `gov links`; then: closed DAEO-t002 citing DEC-120, and DEC-100 anywhere, give none |
| S7 | `test_w2_129_findings.py::test_s7_premise_propagation_finds_the_two_planted_places` | green (premise) | W2-55's `check_propagation` finds `src/app/limits.py` and DAEO-t004 on the planted repository |
| S7 | `test_w2_129_findings.py::test_s7_every_propagation_finding_is_carried_with_its_path_and_line` | red | no `gov links`; then: each of propagation's findings, its ids, path and line, and no other ENFORCES_SUPERSEDED |
| S8 | `test_w2_129_findings.py::test_s8_premise_the_loader_s_patterns_give_the_planted_unmarked_pairs` | green (premise) | `register_statements` plus §A give exactly the five planted unmarked pairs |
| S8, F4 | `test_w2_129_findings.py::test_s8_unmarked_change_is_exactly_what_register_statements_and_archive_section_a_state` | red | no `gov links`; then: UNMARKED_CHANGE names those five pairs and no other |
| S8, F4 | `test_w2_129_sources.py::test_s8_links_reads_the_register_s_statements_through_register_statements` | red | no `gov.links` package; then: its source calls `register_statements` |
| S8, F4 | `test_w2_129_sources.py::test_s8_links_compiles_no_second_pattern_set_for_the_register_s_statements` | red | no `gov.links` package; then: no `re` pattern in it names a change verb or label |
| S9, F3 | `test_w2_129_command.py::test_s9_every_finding_carries_its_code_ids_path_line_role_and_fix` | red | no `gov links`; then (`--all`): every finding line has its code and ids, a path (with a line for a file), roles of the six, a fix |
| S9 | `test_w2_129_command.py::test_s9_the_role_comes_from_the_one_fixed_table_by_path` | red | no `gov links`; then: every finding at a file names the table's role for its path; four roles seen |
| S9 | `test_w2_129_command.py::test_s9_a_record_under_docs_audit_or_docs_research_names_that_role[docs-audit]` | red | no `gov links`; then: the close record under `docs/audit/` names independent-auditor (N-7) |
| S9 | `test_w2_129_command.py::test_s9_a_record_under_docs_audit_or_docs_research_names_that_role[docs-research]` | red | as above: the checkpoint under `docs/research/` names research |
| S9 | `test_w2_129_command.py::test_s9_a_commit_s_finding_names_the_role_its_trailer_names` | red | no `gov links`; then: research for `DAEO-zzzz`, independent-test-designer for `Implements: DEC-120` |
| S9, F3 | `test_w2_129_command.py::test_s9_a_free_text_finding_is_marked_text_and_a_label_finding_is_not` | red | no `gov links`; then: DEC-111's line has `(text)`, the three label findings have none |
| S10 | `test_w2_129_incremental.py::test_s10_since_the_root_lists_every_finding_as_new_and_all_lists_the_same` | red | no `gov links`; then: `--since <root>` lists all, 0 standing; `--all` (no mark) lists the same set, N + M lines |
| S10 | `test_w2_129_incremental.py::test_s10_with_no_mark_and_no_since_it_refuses_naming_since` | red | no `gov links`; then: exit 2 naming `--since`, no mark, nothing written |
| S10, F5 | `test_w2_129_incremental.py::test_s10_the_mark_gives_the_range_and_standing_findings_are_counted_by_code_and_role` | red | no `gov links`; then: after the mark, one commit: 1 new (DEC-996), since the mark's head; the rest standing, each code and role named |
| S10, F5 | `test_w2_129_incremental.py::test_s10_a_finding_older_than_the_mark_is_counted_on_the_next_run_and_listed_with_all` | red | no `gov links`; then: the next run 0 new, the finding counted standing, listed by `--all` |
| S10 | `test_w2_129_incremental.py::test_s10_a_changed_register_entry_lists_its_own_findings_and_those_of_the_entries_it_names` | red | no `gov links`; then: DEC-104 edited: DEC-103 <- DEC-104 listed; the other register findings standing |
| S10 | `test_w2_129_incremental.py::test_s10_a_commit_in_the_range_is_judged` | red | no `gov links`; then: an engineer's commit `Implements: DEC-121` in the range is listed (role engineer) |
| S10 | `test_w2_129_incremental.py::test_s10_since_and_all_each_move_the_mark_to_the_head_judged[since]` | red | no `gov links`; then: the mark holds HEAD after `--since HEAD~1` |
| S10 | `test_w2_129_incremental.py::test_s10_since_and_all_each_move_the_mark_to_the_head_judged[all]` | red | as above, after `--all` |
| S11 | `test_w2_129_command.py::test_s11_the_first_line_counts_new_and_standing_since_the_rev` | red | no `gov links`; then: `gov links: N new since <rev>, M standing`, `<rev>` a 7+ prefix of the root |
| S11 | `test_w2_129_command.py::test_s11_one_line_per_new_finding_code_ids_path_line_role_fix` | red | no `gov links`; then: one line per new finding, four fields |
| S11 | `test_w2_129_command.py::test_s11_json_gives_the_same_findings_in_gov_s_shared_envelope` | red | no `gov links`; then: `{ok, command: links, result, session}`, the same findings by code, path and line, each with its fields |
| S11 | `test_w2_129_command.py::test_s11_exit_code_1_with_new_findings` | red | no `gov links`; then: exit 1 |
| S11 | `test_w2_129_command.py::test_s11_exit_code_0_with_no_new_finding` | red | no `gov links`; then: `--since HEAD`: exit 0, 0 new, all standing |
| S11 | `test_w2_129_command.py::test_s11_exit_code_2_named_when_the_register_cannot_be_read` | red | no `gov links`; then: the path map names a register HEAD lacks: exit 2 naming the register, no traceback |
| S11 | `test_w2_129_command.py::test_s11_exit_code_2_named_outside_a_git_work_tree` | red | no `gov links`; then: a plain folder: exit 2 naming git, no traceback |
| S12, F2 | `test_w2_129_patches.py::test_s12_the_patch_applies_with_git_apply_check_and_nothing_is_written[--propose-marks]` | red | no `gov links`; then: `git apply --check` accepts its output; no file but the mark written |
| S12, F2 | `test_w2_129_patches.py::test_s12_the_patch_applies_with_git_apply_check_and_nothing_is_written[--propose-sources]` | red | as above |
| S12 | `test_w2_129_patches.py::test_s12_propose_marks_adds_changed_by_or_superseded_by_to_each_status_line` | red | no `gov links`; then: applied, DEC-101's status line has `SUPERSEDED by DEC-102`, DEC-103's and DEC-109's `**Changed by:**` their changer, DEC-111's and DEC-130's their changer |
| S12 | `test_w2_129_patches.py::test_s12_after_the_marks_patch_no_unmarked_change_is_left` | red | no `gov links`; then: committed, `--all` lists none of the five |
| S12 | `test_w2_129_patches.py::test_s12_propose_sources_adds_each_unlinked_id_to_its_ticket_s_sources` | red | no `gov links`; then: DEC-104, DEC-105, DEC-121 in DAEO-t001's sources; no UNLINKED_ID for it after |
| S13 | `test_w2_129_sources.py::test_s13_premise_the_gate_modules_are_there_to_read` | green (premise) | the close, launch, readiness, claim, merge queue and kernel hook sources are found |
| S13, F1 | `test_w2_129_sources.py::test_s13_no_close_queue_landing_launch_claim_readiness_or_hook_module_calls_gov_links` | green (guard) | none of them imports `gov.links` or runs `gov links`; red only if a gate takes it up |
| S14 | `test_w2_129_command.py::test_s14_a_repository_with_no_register_tickets_or_contract_is_not_applicable` | red | no `gov links`; then (repository B): exit 0, 0 new, "not applicable" naming the register, tickets and contract |
| S14 | `test_w2_129_command.py::test_s14_json_reports_not_applicable_never_an_error` | red | no `gov links`; then: `ok` true, no `error`, "not applicable" in the result |
| S16 | `test_w2_129_tickets.py::test_s16_an_unmarked_change_to_an_in_progress_ticket_is_ticket_change_unmarked[kpis]` | red | no `gov links`; then: a KPI line of DAEO-t005 re-worded, no decision id in the lines or trailers: TICKET_CHANGE_UNMARKED naming DAEO-t005, the commit and `kpis`, at its file, role orchestrator, exit 1 |
| S16 | `test_w2_129_tickets.py::test_s16_an_unmarked_change_to_an_in_progress_ticket_is_ticket_change_unmarked[allowed_paths]` | red | as above: a path added to `allowed_paths` |
| S16 | `test_w2_129_tickets.py::test_s16_an_unmarked_change_to_an_in_progress_ticket_is_ticket_change_unmarked[depends_on]` | red | as above: DAEO-t004 added to `depends_on` |
| S16 | `test_w2_129_tickets.py::test_s16_an_unmarked_change_to_an_in_progress_ticket_is_ticket_change_unmarked[title]` | red | as above: the `title` re-worded |
| S16 | `test_w2_129_tickets.py::test_s16_an_unmarked_change_to_an_in_progress_ticket_is_ticket_change_unmarked[acceptance_tests]` | red | as above: `acceptance_tests`' path changed |
| S16 | `test_w2_129_tickets.py::test_s16_an_unmarked_change_to_an_open_ticket_is_ticket_change_unmarked` | red | no `gov links`; then: the open DAEO-t004's `title` re-worded, unmarked: the same finding |
| S16 | `test_w2_129_tickets.py::test_s16_the_role_is_orchestrator_whatever_the_commit_s_role` | red | no `gov links`; then: the unmarked commit's `Role:` is engineer; the finding's role still names orchestrator |
| S16 | `test_w2_129_tickets.py::test_s16_two_fields_in_one_commit_are_each_named` | red | no `gov links`; then: `title` and `depends_on` in one commit, both named |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[kpis-in-the-line]` | red | no `gov links`; then: the KPI line carries `[re-worded, DEC-113]`: no S16 finding for DAEO-t005; the unmarked control on DAEO-t004 is found |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[kpis-implements]` | red | as above: the commit carries `Implements: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[kpis-decided-by]` | red | as above: `Decided-by: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[allowed_paths-in-the-line]` | red | as above: `allowed_paths`, `# [added, DEC-113]` on the added line |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[allowed_paths-implements]` | red | as above: `Implements: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[allowed_paths-decided-by]` | red | as above: `Decided-by: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[depends_on-in-the-line]` | red | as above: `depends_on`, `# [added, DEC-113]` on the line |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[depends_on-implements]` | red | as above: `Implements: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[depends_on-decided-by]` | red | as above: `Decided-by: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[title-in-the-line]` | red | as above: `title`, `[re-worded, DEC-113]` in it |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[title-implements]` | red | as above: `Implements: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[title-decided-by]` | red | as above: `Decided-by: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[acceptance_tests-in-the-line]` | red | as above: `acceptance_tests`, `# [re-worded, DEC-113]` on the path line |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[acceptance_tests-implements]` | red | as above: `Implements: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_change_marked_with_its_decision_gives_no_finding[acceptance_tests-decided-by]` | red | as above: `Decided-by: DEC-113` |
| S16 | `test_w2_129_tickets.py::test_s16_guard_status_assignee_or_links_alone_give_no_finding[status]` | red | no `gov links`; then: DAEO-t005's `status` alone changed, unmarked: no S16 finding; the control is found |
| S16 | `test_w2_129_tickets.py::test_s16_guard_status_assignee_or_links_alone_give_no_finding[assignee]` | red | as above: `assignee` alone |
| S16 | `test_w2_129_tickets.py::test_s16_guard_status_assignee_or_links_alone_give_no_finding[links]` | red | as above: `links` alone |
| S16 | `test_w2_129_tickets.py::test_s16_guard_status_assignee_or_links_alone_give_no_finding[all-three]` | red | as above: the three in one commit |
| S16 | `test_w2_129_tickets.py::test_s16_a_commit_that_edits_a_closed_ticket_is_closed_ticket_edited[title-unmarked]` | red | no `gov links`; then: the closed DAEO-t002's `title` changed: CLOSED_TICKET_EDITED naming DAEO-t002, the commit and `title`, role orchestrator, exit 1 |
| S16 | `test_w2_129_tickets.py::test_s16_a_commit_that_edits_a_closed_ticket_is_closed_ticket_edited[kpis-with-implements]` | red | as above: a KPI line added with `[added, DEC-113]` and `Implements: DEC-113`; a mark does not excuse it |
| S16 | `test_w2_129_tickets.py::test_s16_a_commit_that_edits_a_closed_ticket_is_closed_ticket_edited[status-reopened]` | red | as above: `status` closed to in_progress; the status exemption is for open tickets only |
| S16 | `test_w2_129_tickets.py::test_s16_a_ticket_closed_in_the_range_is_closed_ticket_edited_only_by_the_commits_after` | red | no `gov links`; then: DAEO-t005 closed in the range (no finding), then its `title` edited (CLOSED_TICKET_EDITED for that commit only) |
| S16 | `test_w2_129_tickets.py::test_s16_a_ticket_change_is_listed_only_when_its_commit_is_in_the_range` | red | no `gov links`; then: `--since <the commit>` lists no S16 finding; `--since <the commit>~1` lists it |
| S16 | `test_w2_129_tickets.py::test_s16_a_closing_commit_that_also_changes_a_field_unmarked_is_ticket_change_unmarked[kpis]` | red | no `gov links`; then (review F2): one unmarked commit closes the in-progress DAEO-t005 and re-words a KPI line: TICKET_CHANGE_UNMARKED naming DAEO-t005, the commit and `kpis`, role orchestrator, exit 1; no CLOSED_TICKET_EDITED for it (the status before decides) |
| S16 | `test_w2_129_tickets.py::test_s16_a_closing_commit_that_also_changes_a_field_unmarked_is_ticket_change_unmarked[allowed_paths]` | red | as above: a path added to `allowed_paths` in the closing commit |
| S16 | `test_w2_129_tickets.py::test_s16_a_closing_commit_that_also_changes_a_field_unmarked_is_ticket_change_unmarked[acceptance_tests]` | red | as above: `acceptance_tests`' path changed in the closing commit |
| S16 | `test_w2_129_tickets.py::test_s16_a_commit_closing_an_open_ticket_with_an_unmarked_change_is_ticket_change_unmarked` | red | as above from status open: DAEO-t004 closed and its `acceptance_tests` path changed in one unmarked commit |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_closing_commit_with_status_assignee_or_a_marked_change_gives_no_finding[status]` | red | no `gov links`; then: DAEO-t005 closed, `status` alone, unmarked: no S16 finding for it; the control on DAEO-t004 is found |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_closing_commit_with_status_assignee_or_a_marked_change_gives_no_finding[status-and-assignee]` | red | as above: `status` and `assignee` in the closing commit |
| S16 | `test_w2_129_tickets.py::test_s16_guard_a_closing_commit_with_status_assignee_or_a_marked_change_gives_no_finding[kpis-marked-in-the-line]` | red | as above: the closing commit's KPI line carries `[re-worded, DEC-113]` |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_an_unknown_id_in_a_non_docstring_literal_of_a_python_test_file_gives_no_unknown_id` | red | today: UNKNOWN_ID for DEC-981 (planted register string), DEC-982 (record path) and W1-90 (f-string path) in `tests/unit/test_s17_planted.py`; after: none there, none for DEC-983's literal, while the control DEC-984 in a comment of the same run is found |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_a_superseded_id_only_inside_a_planted_literal_is_not_carried` | red | today: DEC-107 inside the planted register string is carried as ENFORCES_SUPERSEDED; after: W2-55 still names it and `OLD = "DEC-107"` (premise), neither is carried, the comment `# DEC-107` of the same file is |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_guard_ids_in_comments_are_judged` | green (guard) | DEC-984 in a comment gives UNKNOWN_ID; DEC-107 in a comment is carried; the file's other lines hold planted literals |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_guard_ids_in_module_and_function_docstrings_are_judged` | green (guard) | DEC-985 (module docstring) and DEC-986 (a function's multi-line docstring) give UNKNOWN_ID at their lines |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_guard_non_python_test_files_are_judged` | green (guard) | DEC-107 in `tests/unit/README.md` and in a JSON fixture's string is carried (W2-55 names both) |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_guard_a_python_test_file_that_does_not_parse_is_judged_as_today` | green (guard) | a syntax error in the file: DEC-988 in its "literal" gives UNKNOWN_ID, DEC-107 there is carried |
| S17, F7 | `test_w2_129_fixtures.py::test_s17_guard_a_line_with_the_id_in_a_literal_and_in_a_trailing_comment_is_judged` | green (guard) | `WINDOW = "DEC-107"  # DEC-107 ...` is carried; `RECORD = "...DEC-989.md"  # DEC-989 ...` gives UNKNOWN_ID |
| S17 | `test_w2_129_fixtures.py::test_s17_w2_55_propagation_still_names_the_planted_literal_lines` | green (guard) | `python3 -m gov.decisions.propagation` in the planted repository exits 1 and still names both literal lines |
| F1 | `test_w2_129_sources.py::test_s13_no_close_queue_landing_launch_claim_readiness_or_hook_module_calls_gov_links` | green (guard) | as S13 |
| F2 | `test_w2_129_command.py::test_s1_writes_nothing_but_its_mark_the_head_it_judged` | red | as S1 |
| F2 | `test_w2_129_command.py::test_s1_starts_only_git_opens_no_socket_and_writes_only_the_mark` | red | as S1 |
| F3 | `test_w2_129_command.py::test_s9_every_finding_carries_its_code_ids_path_line_role_and_fix` | red | as S9 |
| F3 | `test_w2_129_command.py::test_s9_a_free_text_finding_is_marked_text_and_a_label_finding_is_not` | red | as S9 |
| F4 | `test_w2_129_sources.py::test_s8_links_compiles_no_second_pattern_set_for_the_register_s_statements` | red | as S8 |
| F4 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_each_rule_bearing_place[proposed-in-ticket-sources]` | red | a PROPOSED decision in an in-progress ticket's sources is not in force |
| F4 | `test_w2_129_findings.py::test_s6_not_in_force_as_rule_in_a_judged_commit_s_implements` | red | a PROPOSED decision in `Implements:` is not in force |
| F5 | `test_w2_129_incremental.py::test_s10_a_finding_older_than_the_mark_is_counted_on_the_next_run_and_listed_with_all` | red | as S10 |
| F5 | `test_w2_129_incremental.py::test_s10_the_mark_gives_the_range_and_standing_findings_are_counted_by_code_and_role` | red | as S10 |

**Not tests (the CTO's checks):**
- **S15 and F6, the timing** (`--all` under 10 s and `--since HEAD~1` under 5 s on this repository's main tree,
  the median of five, recorded in `docs/research/W2-129-links.md`): the CTO's measured run. The planted runs take
  well under a second each and say nothing about it.
- **S8's parity on this repository** (the decisions UNMARKED_CHANGE names agree with
  `docs/research/W2-92-proto-drift.py`'s drifting list at the clean-up's starting head): the CTO's run on the main
  tree; these tests check the same rule on the planted repository (N-3) and never read this repository's store.
- **S13's "the structural pass runs it as a notice"**: the CTO's own tool, outside the tree.

**A check of the tests themselves** (a scratch copy of `src` with a sketch of `gov links` of about 400 lines, never
committed): the sketch passes all 103. Six faults planted in it one at a time are each caught: every finding listed
as new (5 reds, S10 and S11), a file written beside the mark (4 reds, S1 and S12), the `(text)` mark dropped (2,
S9 and S11), the register treated as one record (1, S10), a PROPOSED decision counted as in force (10, S6 and S9),
the role of `src/` changed (2, S9 and S10). The sketch printed the summary line before each patch; `git apply`
accepted it.

**S16, the second pass (DEC-1088 (6), standing; integrate merged at `87cadea15`).** 32 cases in
`test_w2_129_tickets.py`, each on its own copy of repository A with planted commits; S1 to S15 are unchanged. Run in
the launch sandbox through the heavy slot with the same options: **135 tests, 131 failed, 4 passed**; all 32 S16 cases
fail on `there is no gov links command in the tree under test`, after their planted commits are made. A throwaway
sketch of S16 (scratch only, never committed) passes all 32; six faults planted in it one at a time are each caught:
the decision mark ignored (15 reds), status, assignee and links judged (5), the closed status read at HEAD instead
of before the commit (2), the range ignored (1), the commit's `Role:` as the role (1), the field left out (13).

**S16, the third pass (review F2: the closing commit).** 7 cases added to `test_w2_129_tickets.py` (39 S16 cases in
all): a commit that closes an open or in-progress ticket is judged by the status before it, so an unmarked change of
`kpis`, `allowed_paths` or `acceptance_tests` in the same commit is TICKET_CHANGE_UNMARKED (4 reds, one from status
open); the closing commit's `status` alone, `status` with `assignee`, or a KPI change marked in the line, is no finding
(3 guards, each with the unmarked control on DAEO-t004). Every other case is unchanged.

**S17, the fourth pass (D-6 part 2; DEC-1109 (2) restarted it, DEC-1098 (3) row 24).** 8 cases in
`test_w2_129_fixtures.py`, written on `w2/W2-129-d6-tests` from `w2/integrate` at `d48639954`, where `gov links` is
merged. One planted commit on a copy of repository A adds seven test files (`tests/unit/test_s17_*.py`,
`tests/unit/README.md`, `tests/unit/fixtures/planted.json`); none cites DEC-108, so W2-55 names every line citing the
superseded DEC-107; each unknown id (DEC-981 to DEC-989) is used once. One `gov links --all` run on it. Run in the
launch sandbox through the heavy slot with the same options: the 8 cases give **2 failed, 6 passed**; the two reds
fail on the planted literal ids still reported (UNKNOWN_ID at `test_s17_planted.py:8` and `:18`, ENFORCES_SUPERSEDED
at `:11`), each after its control in the same run is found. S1 to S16 are unchanged; repository A itself is unchanged,
so S7's "no other ENFORCES_SUPERSEDED" holds as before.

## The interface the tests assume

- **The command:** `src/gov/links/command.py` (`gov.links.command`), a read command, options `--since <rev>`,
  `--all`, `--json`, `--propose-marks`, `--propose-sources` (with the shared `--root`). The exit codes 0, 1 and 2 are
  the command line's own (`gov.cli.main` reserves 1 and 2 and prints a dict result as JSON), so the module returns
  its code as an int with `CHILD_EXIT_CODE = True` and prints its own output (N-1).
- **The text:** the first line `gov links: <N> new since <rev>, <M> standing (...)`, `<rev>` the range's base
  commit (the full sha or a prefix of 7 or more); the standing count names each code and role on stdout. Then one
  line per listed finding: `<CODE> <ids, form, status...> | <path>:<line> | <role> | <fix>`, the fields split by
  ` | `; the first field names the ids as whole words; `(text)` on a free-text finding; `whole` or `part` on a
  label UNMARKED_CHANGE; the status word on NOT_IN_FORCE_AS_RULE. A commit's finding holds the commit's sha (7+) or
  the word `Implements` on its line, and its role field holds the commit's `Role:`. `--all` lists the standing
  findings too.
- **`--json`:** one envelope on stdout, `{ok, command: "links", result, session}`; the findings are dicts anywhere in
  `result` with `code`, `ids`, `path`, `line`, `role`, `fix`; a free-text one has `text: true` or `(text)` in a
  value; "not applicable" (or `not_applicable`) in the result of repository B.
- **Exit 2:** with no mark and no `--since` (naming `--since`), an unreadable register (naming the register),
  outside a git work tree (naming git); never a traceback.
- **The mark:** `.gov-runtime/links/mark`, HEAD's sha (full or 7+), written by every run that judges; nothing else
  written outside `.gov-runtime/links/`; only git started; no socket.
- **The patches:** stdout that `git apply` accepts (a summary line before the patch is accepted by git); the marks
  patch changes the changed entry's status line (the first line under its heading that is not blank); the sources
  patch keeps the ticket's front matter valid YAML.
- **S16's lines:** `CLOSED_TICKET_EDITED <ticket id> <commit sha, 7+> <field> ... | .tickets/<id>.md:<line> |
  orchestrator | <fix>` and the same for `TICKET_CHANGE_UNMARKED`, in the same four ` | ` fields. The first field
  names the ticket id and the field (`title`, `kpis`, `allowed_paths`, `depends_on`, `acceptance_tests`, `status`)
  as whole words and the commit by a hex token of 7 or more that its sha starts with; the line is any line of the
  ticket's file at HEAD; the role field contains `orchestrator` (whatever the commit's `Role:`); the fix is not
  empty. Two fields in one commit may be one line naming both or a line each. A "decision id" is any `DEC-n` in a
  changed line (added or removed, a YAML comment included) or in the `Implements:` or `Decided-by:` trailer. The
  status before the commit (its parent's file) decides closed; a ticket the commit creates is not tested.
- **S17's places (DEC-1109 (2)):** in a `tests/**/*.py` file that parses, an id inside a string literal that is not a
  docstring (a plain, triple-quoted or f-string, assigned or not) gives no UNKNOWN_ID line, and an ENFORCES_SUPERSEDED
  line at `<path>:<line>` is printed only when the old id also stands on that line outside such a literal (a comment,
  a docstring, code); "a docstring" is the first statement's string of a module, class or function. Ids in comments
  and docstrings, every non-Python file under `tests/` (`README.md`, `*.json`, `*.yaml`, `*.txt`) and a `.py` file
  that does not parse give the same lines as before, in the same four ` | ` fields (`UNKNOWN_ID <id> ... | <path>:<line>
  | independent-test-designer | <fix>`); the first field holds the id. `python3 -m gov.decisions.propagation`, run in
  the repository, still prints every line it printed before (W2-55's module is not changed; the filter is in
  `gov links`' carrying).

## Notes and limits

- **N-1. The exit codes.** `gov.cli.main` reserves 1 (governance error, `ok: false`) and 2 (usage) and may not
  declare them; a dict result exits 0 and is printed as JSON. The KPI's 0/1/2 and its text lines need
  `CHILD_EXIT_CODE = True` (the module prints and returns the int), or a change to `gov.cli.main` outside the
  ticket's paths.
- **N-2. Whole or part, by the loader.** `register_statements` reads a label's value up to the next list line, so
  `**Supersedes:** DEC-101` followed by body text (no list line after it) is read as a part, while the loader's
  own SUPERSEDES edge (the status line alone) reads it as ids alone. The planted DEC-102 and DEC-108 carry a
  `**Tags:**` line after their status line, so both readings say whole. On this repository the two may disagree for
  some entries; the patch's form (`SUPERSEDED by` or `**Changed by:**`) follows whichever the tool uses.
- **N-3. S8's "agree with the drifting list".** The prototype's drifting list holds only current decisions
  (ACCEPTED, no SUPERSEDES edge, not spent), so it never holds a whole supersession by ids alone, which S2 and S12
  make an UNMARKED_CHANGE. The tests therefore check UNMARKED_CHANGE against the same statements under the
  prototype's "no hint in its own entry" rule, whole supersessions included (`statement_pairs`); on this
  repository the drifting list should be a subset of what UNMARKED_CHANGE names.
- **N-4. Where the archive and the in-force list live.** The path map names neither; the tests plant them where this
  repository keeps them, `governance/project/orchestration/`. S14 says the record places come from the path map;
  no key for these exists yet.
- **N-5. `depends_on`.** KPI S3 lists it among UNKNOWN_ID's typed places; LINK-INTEGRITY §4.1 says "not findings:
  depends_on (core-graph keeps it)". No test plants an unknown `depends_on`; DAEO-t002 as a dependency is only a
  guard.
- **N-6. Open tickets.** S3's ticket places are judged "in-progress and closed tickets": DAEO-t004 (open) has a
  missing acceptance path and the guard asks for no UNKNOWN_ID there.
- **N-7. `docs/audit/` and `docs/research/`.** No typed place of S3 to S6 lies there by its path; the tests plant a
  close record and a checkpoint there (found by their `type`, as every record is by the loader) to see the two
  table rows. A tool that finds checkpoints and close records only under `docs/checkpoints/` and `docs/close/`
  fails those two cases.
- **N-8. `--all` with no mark.** The ticket's form `[--since <rev> | --all]` makes `--all` a range of its own; the
  tests run it with no mark and expect every finding listed.
- **N-9. The landing.** `land.py` is the CTO's tool, outside the tree; S13 reads the merge queue, the dispatcher,
  the close, launch, readiness, claims, guard and hook sources, `lefthook.yml` and the settings, but not it.
- **N-10. The generated MR records.** `contract.yaml` has one top-level status; the tests compare each
  `docs/contract/master-rules/MR-n.md`'s status with it. On this repository MR-1 to MR-6 are PROPOSED and the
  Contract ACCEPTED, so a first `--all` names six STATUS_CONFLICTs there.

## Files

- `w2_129_support.py`: the two planted repositories, the runner, the output reader and the oracles.
- `w2_129_probe.py`: the audit-hook probe (S1, F2).
- `conftest.py`: the session's repositories, a copy per test, and the three shared runs.
- `test_w2_129_findings.py` (S2 to S8), `test_w2_129_command.py` (S1, S9, S11, S14),
  `test_w2_129_incremental.py` (S10, F5), `test_w2_129_patches.py` (S12), `test_w2_129_sources.py` (S8, S13),
  `test_w2_129_tickets.py` (S16), `test_w2_129_fixtures.py` (S17, F7).
