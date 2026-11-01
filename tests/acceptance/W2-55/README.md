# W2-55 acceptance tests (DAEO-arrl)

Ticket: `DAEO-arrl` (W2-55), "Decisions tagged by domain, status and scope; superseded and done entries left out of
what agents see", profile STANDARD. Written by the independent test designer (MR-3) from the ticket's KPI lines, its
sources (DEC-791 item 1, DEC-825 items 2 and 4, DEC-866, DEC-851, DEC-953 item 7, DEC-983) and the lead's interface
specification of this run (S1 to S6: the tags line, the check functions and their codes, the propagation check, the
`left_out` key, `gov context --in-force`, the backfill proposal's sections). The ticket's implementation was not read.

## How the suite runs

- **The code under test (DEC-732).** Every call runs in a child process whose `PYTHONPATH` is the `src/` of the tree
  these files stand in (`w2_55_support.SRC`, found from the support file's own place). Merged into the ticket's
  worktree, the same files exercise that worktree's code. Run it as
  `PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider`.
- **Public interfaces only:** `gov.store.load(root)` first; then `gov.decisions.check_tags(root)`,
  `gov.decisions.check_propagation(root)`, W2-03's `gov.decisions.check(root)`; the commands
  `python3 -m gov.decisions.tags` and `python3 -m gov.decisions.propagation` run in a project root;
  `gov retrieve <query> --json`, `gov context <ticket> --json` and `gov context --in-force --json`
  (`python3 -m gov.cli.main … --json --root <project>`), after `gov.retrieval.lexical.refresh` and `gov.store.load`.
- **Planted projects.** Every project is a temporary git repository built from nothing under pytest's `tmp_path`:
  this repository's path map with its namespaces replaced (everything governance memory, not embedded) and the
  planted register named under `decision_register`, the kernel's gitleaks rules, and the case's files, committed.
  Nothing is written in this repository.
- **Deterministic, offline.** No vector is built (the semantic route is unavailable and gives no hit), no reranker is
  loaded, the embedder endpoint is a dead local port, `HOME` is empty. Every child process has a time limit (300 s).
  The lexical route matches an exact string on a line, so each retrieval case asks a string its entries hold.
- **The backfill cases (KPI 4) read the tree they run in:** `docs/research/W2-55-backfill.md`, and the register at the
  ticket's base, the merge base of `HEAD` with `w2/integrate` (skipped, with that reason, in a clone without that
  branch).
- The retrieval and context cases need `gitleaks` on `PATH` (the lexical index's secret filter, DEC-287); without it
  they are skipped with that reason.

## KPI lines and their tests

| KPI line | Tests | Red at the base because |
|---|---|---|
| **KPI 1, failure 1**: every entry has a domain of the closed list, a status naming what superseded or changed it, a scope; the validator checks all three, naming the entry | `test_w2_55_tags.py`: `test_a_fully_tagged_register_passes` (all eleven domains, both scopes), `test_the_tags_command_exits_0_…`, `test_the_tags_command_exits_1_and_names_the_entry`, `test_an_entry_without_a_tags_line_is_named`, `test_a_tags_line_without_a_part_is_named_with_the_part[domain, scope, lands in]`, `test_a_domain_outside_the_closed_list_is_refused`, `test_a_scope_outside_the_two_is_refused`, `test_a_superseded_entry_naming_no_successor_is_named`, `test_a_superseded_entry_naming_a_successor_the_register_does_not_hold_is_named`, `test_an_entry_another_supersedes_…_old_first`, `test_an_entry_another_changes_…_old_first[Changes, Settles, Corrects, Reverses, Withdraws]` | `gov.decisions.check_tags` does not exist ("cannot be imported"); `python3 -m gov.decisions.tags` is no module (exit 1 without naming the entry) |
| | `test_w2_03s_check_keeps_its_own_codes` | **green at the base by design**: a guard that W2-03's `check(root)` does not take the register checks into its list (S2) |
| **KPI 2**: a lands-in tag, checked | `test_w2_55_tags.py`: `test_a_place_head_does_not_hold_is_named`, `test_a_place_only_in_the_working_tree_is_not_held_by_head`, `test_a_place_outside_where_its_scope_says_is_named[kernel, repository]`, `test_none_on_an_entry_in_force_is_named`, `test_none_on_a_done_or_superseded_entry_is_no_finding`; an entry with two places is in the fully tagged register (DEC-112) | `gov.decisions.check_tags` does not exist |
| **KPI 3, failure 2**: `gov context` and `gov retrieve` leave out superseded and done entries and say how many; Lens B's Q05 no longer happens | `test_w2_55_left_out.py`: `test_retrieve_leaves_out_superseded_and_done_entries` (superseded by status word and by another's `**Supersedes:**`, done by tag; a changed entry still served), `test_retrieve_says_how_many_it_left_out`, `test_lens_b_q05_serves_the_decision_in_force_and_no_superseded_one`, `test_context_leaves_out_superseded_and_done_entries_from_the_supplementary_context`, `test_context_says_how_many_it_left_out` | the bundle and the packet serve DEC-101, DEC-103 and DEC-106 and have no `left_out`; Q05 serves DEC-138, DEC-148 and DEC-149 unmarked (F4) |
| | `test_retrieve_with_nothing_to_leave_out_has_no_key`, `test_context_with_nothing_to_leave_out_has_no_key`, `test_a_superseded_mandatory_input_still_refuses`, `test_a_done_entry_declared_as_a_source_is_still_read` | **green at the base by design**: what must stay as before (S4) |
| **KPI 4, failure 4**: the backfill is a proposal in `docs/research/W2-55-backfill.md`; nothing applied to the register | `test_w2_55_backfill.py`: `test_the_proposal_has_its_three_sections`, `test_one_row_per_register_entry_at_the_base_in_its_order`, `test_every_row_has_a_domain_a_scope_a_lands_in_a_status_and_a_reason`, `test_an_entry_the_register_marks_superseded_is_proposed_superseded_by_its_successor`, `test_every_amends_and_refines_relation_is_listed_with_the_old_entrys_status_note` (every `**Amends:**`/`**Refines:**` relation on a status line of the base register: 121 at `84c1d4277b9c`, DEC-825's "about 120"), `test_the_sample_can_be_drawn_again_and_says_what_the_owner_checks`, `test_the_proposal_states_how_it_was_made` | the file does not exist |
| | `test_the_branch_changes_nothing_in_the_register_against_its_base` | **green at the base by design**: failure 4's guard; red when the branch (or its working tree) changes `docs/DECISION_REGISTER.md` against its merge base with `w2/integrate` |
| **KPI 5, failure 3**: supersession propagates; the sweep of 2026-10-20 is its first fixture | `test_w2_55_propagation.py`: `test_a_place_that_enforces_an_old_decision_is_found_naming_both_and_the_line[a test by id, code by value, a skill by id, a brief by value, a non-closed ticket's KPI, the prompt, a changed entry's value]`, `test_the_path_map_that_enforces_an_old_decision_is_found`, `test_a_place_that_does_not_enforce_gives_no_finding[a closed ticket, docs/, the orchestration record, a file citing the successor, kept on the old entry, kept on the new entry, a changed entry's id alone, whole-word ids]`, `test_the_register_and_the_working_tree_are_not_searched`, `test_the_propagation_command_exits_1_and_names_the_place`, `test_a_project_with_nothing_enforcing_an_old_decision_passes`; the sweep: `test_the_sweep_of_2026_10_20_is_found[W1-49 threshold, W1-49 live session, W1-26 planted authority defect, W1-22 TestCanaryRunner ×2, LEAD_CHECKPOINT in a template]`, `test_the_sweeps_kept_and_closed_places_give_no_finding`, `test_a_changed_entrys_id_alone_in_the_sweep_is_no_finding` | `gov.decisions.check_propagation` does not exist |
| **KPI 6**: W2-61's 20-question measure after the merge, beside its baseline | **no test**: it is the lead's own measurement after the merge | — |
| **KPI 7**: `gov context --in-force` prints the digest of the decisions in force, generated from the register | `test_w2_55_in_force.py`: `test_one_line_per_entry_in_force_in_register_order_beginning_with_its_id`, `test_superseded_and_done_entries_are_left_out_with_their_count`, `test_a_changed_entrys_line_names_what_changed_it`, `test_the_digest_is_generated_from_the_register_not_a_hand_made_file`, `test_no_register_named_gives_an_empty_digest`, `test_a_named_register_that_cannot_be_read_refuses` | the parser refuses `--in-force` ("the following arguments are required: ticket"), so no envelope is printed |
| | `test_context_with_neither_a_ticket_nor_in_force_is_refused_by_the_parser` | **green at the base by design** (S5: still refused) |

The session-start hook's loading of the digest (KPI 7's second half) is the owner's CIT-P question (DEC-952 item 5)
and not part of this run (S5): no test.

## The sweep of 2026-10-20, as planted

From `governance/project/orchestration/packages/SWEEP-2026-10-20.md` §3 and §5: DEC-636 `SUPERSEDED by DEC-838` and
DEC-665 `Changed by: DEC-838` with the window's values (`300_000`, `300000`, and `LEAD_CHECKPOINT` for DEC-636);
DEC-605 `Changed by: DEC-822, DEC-835` with the value of its premise (the judge imports the judged project's code,
planted as `PYTHONPATH=judged/src`). The places: W1-49's `test_w1_49_threshold.py` and `test_w1_49_live_session.py`
(the two window cases); W1-26's `test_planted_authority_defect_decision_checker_exception_not_swallowed` and W1-22's
two `TestCanaryRunner` cases (W2-59's three); the lead brief template teaching `LEAD_CHECKPOINT`; and, giving no
finding, W1-26's `test_w1_26_dec436.py` (kept, with the sweep's reason) and a closed Wave 1 ticket.

## Red result at the base (`84c1d4277b9c`)

76 tests: 69 failed, 7 passed (the seven green by design above), no error. The failures, by reason:
28 `check_propagation cannot be imported`; 21 `check_tags cannot be imported`; 2 the tags command (no module);
7 the backfill proposal does not exist; 6 the parser refuses `--in-force`; 5 the bundle and the packet serve
superseded and done entries with no `left_out` (Q05 among them).
