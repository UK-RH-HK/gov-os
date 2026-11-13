# W2-173 acceptance tests: the launch script's follow-ups for the memory audit

Ticket DAEO-qz4p (W2-173), profile FULL, class C3 (DEC-1120 (2)-(3), DEC-1101 (2); S5 under DEC-1112 (3), DEC-1113).
Written by the independent test designer (MR-3) from the ticket's KPI lines S1-S5 and its four failure lines, the lead's
brief (td-1) and the audit briefs' fixed forms (`governance/project/indep-briefs/memory-audit/checker.md` §6-§7 and
`auditor.md` §6-§7), before the engineer's code, reading only `w2/integrate` at `dac438772` (the script as W2-149 left
it at `2f98aecbc`, its schemas and W2-149's acceptance tests). Never read: the branch `w2/W2-173` or its unit tests.

## How they run

    env HOME=<an empty scratch folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-173 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"
    python3 -m gov.cli.main accept W2-173 --root <worktree>

About 40 s, serial, no model, network or GPU. (`PYTHONUSERBASE` only where pytest lives in the real HOME's user site.)

- **W2-149's planted world, imported, never copied.** `conftest.py` builds W2-149's planted repository
  (`w2_149_support.build_repo`) once per session with W2-173's extra briefs (`w2_173_support.EXTRA_BRIEFS`: writer
  briefs naming each of the five efforts and five refused values, a checker brief naming `high`), and per case W2-149's
  `World` (planted HOME, sets root, runs and trees folders under pytest's `tmp_path`; `World.check_planted` fails a
  launch on any real location) and stub `claude`.
- **The argv recorder.** W2-149's stub does not know `--effort`, so `w2_173_support.install_recorder` moves it to
  `bin/claude-w2-149` and puts a recorder at `bin/claude`: it appends each call's raw argv to `argv-raw.jsonl` and execs
  the stub (same pid, parent and stdin) with every `--effort` pair taken out. A real session's argv is matched to the
  stub's own record by pid.
- **The planted question set** `fixtures/evaluation/memory-audit-9/hidden/q01.yaml`..`q03.yaml` (flat, each file named
  by its id) for the checker; the auditor's misses are W2-149's planted `runs/audit-1/misses.jsonl` (m1-m3).
- **Set-up A** (S1's five briefs, S5's stop rule) through `w2_149_setup_a` (`plant_half`, `plant_labels`, `dry`,
  `deliver`, `writer_out`, `stopped_out`).

## The interface held (the lead's brief; readings marked)

- **S1.** A brief's front matter `effort:` one of `low`, `medium`, `high`, `xhigh`, `max`; the real session's argv
  carries `--effort <value>` as two items; with no `effort` line no call carries `--effort`. `WALL.json` has the key
  `effort` (the value, or null) (*reading*: the key's name). The counts gain one top-level field `effort`, a string or
  null, `required` and closed (`enum` of the five and null; W2-149's `schema_holes` stays empty); every line the
  script prints validates. Any other value (*reading*: `loud`, `High`, `5`, `[high]`, `""`): exit 10, reason `brief`,
  before anything is built (the walls folder identical entry for entry, no tree, no seed line, no claude call), the line
  carrying `effort: null`. The canary's argv is not held to `--effort` either way (*unresolved*).
- **S2.** A writer's or checker's result may carry `stopped`, one of the seven words; any word but `none`: exit 21,
  `status: stopped`, `reason: stopped`, the word at `out.stopped`, nothing delivered, whatever else would refuse 20
  (no set, no notes, a result holding only the word: *reading*, the stop word honoured first). `none` or no `stopped`
  delivers as before. Both result schemas gain `stopped` as an optional property closed to the seven (`halted`, `None`,
  `""`, `0`, null and a list refused). Set-up A's stop still ends 20.
- **S3.** `notes.md`: `# Cross-check notes`; `## Questions`; one line per file of `input/set/` in id order,
  `<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>`; `## The set`; five lines starting
  `domains:`, `categories:`, `keyword:`, `supersession `, `set codes:`. The result's `accepted`, `revise`, `rejected`
  equal the three words' counts. Anything else: 20, no `XCHECK-r1.md`, the set's folder identical. Tested only as S3's
  Verify names: well formed; a missing line (each of: the heading, `## Questions`, a question line, `## The set`, a set
  line); a fourth verdict word; an id not in the set (in place of one, or extra); counts that disagree.
- **S4.** `classes.json`: `{"<id>": {"class": ..., "reason": ...}}`, exactly the ids of `input/misses.jsonl`, each
  class one of the five, each reason one line of at most 200 characters (200 delivered), the result's five counts equal
  the classes'. Anything else (also a bare-word class, a missing reason): 20, no `miss-classes.json`, no new
  `AUDITS.log` line, the audit's folder identical.
- **S5 / F3 / F4.** W2-149's own cases are S5's main check (run unchanged by `gov accept W2-149`; see "A conflict"
  below); the script's text diff is the reviewer's. Here: set-up A's stop rule; `git diff --name-only <base>...HEAD`
  (base: the merge-base with `w2/integrate`, else `dac438772`) names no template file, the path map, the guard, a file
  named `APPROVED` or a set-up A brief (F3), and only the ticket's `allowed_paths`, `tests/acceptance/W2-173/**` and the
  ticket's own records `.tickets/DAEO-qz4p.md`, `docs/checkpoints/DAEO-qz4p/**`, `docs/probes/DAEO-qz4p/**` (F4;
  *reading*, W1-01's: a ticket's own file rides its commits). **F3 and F4 are judged only on `w2/W2-173`** (HEAD's full
  ref `refs/heads/w2/W2-173`, read from the repository the test file sits in): on any other checkout (another
  ticket's branch, the merge queue's candidate merge on a detached HEAD, `w2/integrate`, a clone's checkout) they are
  skipped with the reason named (the branch found, or "detached HEAD"), never red and never passed silently. The
  judgements are `judge_f3_paths(root)` and `judge_f4_paths(root)`; the planted cases below call the same functions
  (Revision, below).

## A conflict with S5 (named for the CTO; not settled here)

S5 says W2-149's cases pass unchanged, but five of them plant forms or hold keys that S1, S3 and S4 change, so they
go red once the four changes land (read from their text at `dac438772`, not run against a changed script): `test_w2_149_results.py::test_s16_the_delivery_lands_only_where_the_kind_delivers` (its `checker`
and `auditor` params: `GOOD_DELIVERY`'s notes are `# Cross-check notes (planted)` and one bullet; its classes are bare
words), `test_w2_149_results.py::test_s17_a_finished_wall_is_one_file` and
`test_w2_149_canary_session.py::test_s10_tools_budget_and_timeout_come_from_kinds_yaml_when_the_brief_names_none`
(checker deliveries of those notes), and `test_w2_149_results.py::test_s13_the_counts_schema_is_closed_and_every_value_typed`
and `test_w2_149_results.py::test_s13_a_refusal_line_carries_its_code_reason_word_and_approved_sha256` (`free_text`
holds the counts' top-level keys to `COUNTS_KEYS`, which lacks `effort`).

## The map

| KPI id | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_173_effort.py::test_s1_the_counts_schema_gains_effort_a_closed_string_or_null` | the counts schema has no `effort` |
| S1 | `test_w2_173_effort.py::test_s1_each_of_the_five_values_is_recorded_in_wall_json_and_counts` | `WALL.json` and the counts carry no `effort` |
| S1 | `test_w2_173_effort.py::test_s1_a_brief_with_no_effort_line_records_effort_null` | `WALL.json` and the counts carry no `effort` key |
| S1 | `test_w2_173_effort.py::test_s1_a_brief_naming_high_starts_the_session_with_effort_high` | the session's argv carries no `--effort` |
| S1 | `test_w2_173_effort.py::test_s1_a_checker_brief_naming_high_starts_its_session_with_effort_high` | the session's argv carries no `--effort` |
| S1 | `test_w2_173_effort.py::test_s1_a_brief_with_no_effort_line_passes_no_effort_flag` | green today (holds already) |
| S1 | `test_w2_173_effort.py::test_s1_an_effort_outside_the_five_refuses_10_before_anything_is_built` | the value is ignored: the run builds and delivers (exit 0) |
| S1 | `test_w2_173_effort.py::test_s1_the_five_set_up_a_briefs_still_pass_stage_10_and_build_dry_walls` | green today (holds already) |
| S1 | `test_w2_173_effort.py::test_s1_the_five_set_up_a_dry_walls_record_effort_null` | `WALL.json` carries no `effort` key |
| S2 | `test_w2_173_stopped.py::test_s2_the_result_schema_gains_stopped_an_optional_closed_word` | the schemas take any `stopped` value (`halted` passes) |
| S2 | `test_w2_173_stopped.py::test_s2_a_writer_result_that_stopped_delivers_nothing_and_ends_21` | the set is delivered (exit 0) |
| S2 | `test_w2_173_stopped.py::test_s2_a_checker_result_that_stopped_delivers_nothing_and_ends_21` | the notes are delivered (exit 0) |
| S2 | `test_w2_173_stopped.py::test_s2_a_writer_that_stopped_with_no_set_ends_21_not_20` | exit 20 (missing set) |
| S2 | `test_w2_173_stopped.py::test_s2_a_checker_that_stopped_with_no_notes_ends_21_not_20` | exit 20 (missing notes) |
| S2 | `test_w2_173_stopped.py::test_s2_a_checker_result_holding_only_its_stop_word_ends_21_not_20` | exit 20 (schema) |
| S2 | `test_w2_173_stopped.py::test_s2_a_writer_result_with_none_and_a_set_delivers_as_before` | green today (holds already) |
| S2 | `test_w2_173_stopped.py::test_s2_a_checker_result_with_none_and_good_notes_delivers_as_before` | green today (holds already) |
| S2 | `test_w2_173_stopped.py::test_s2_a_result_without_stopped_still_delivers` | green today (holds already) |
| S2 | `test_w2_173_stopped.py::test_s2_a_stopped_word_outside_the_seven_is_a_schema_refusal_20` | delivered (exit 0) |
| S3 | `test_w2_173_notes.py::test_s3_well_formed_notes_are_delivered` | green today (holds already) |
| S3 | `test_w2_173_notes.py::test_s3_well_formed_notes_with_every_verdict_word_are_delivered` | green today (holds already) |
| S3 | `test_w2_173_notes.py::test_s3_notes_with_a_missing_line_are_refused_20` | the notes are delivered unchecked (exit 0) |
| S3 | `test_w2_173_notes.py::test_s3_notes_with_a_fourth_verdict_word_are_refused_20` | the notes are delivered unchecked (exit 0) |
| S3 | `test_w2_173_notes.py::test_s3_notes_naming_an_id_not_in_the_set_in_place_of_one_are_refused_20` | the notes are delivered unchecked (exit 0) |
| S3 | `test_w2_173_notes.py::test_s3_notes_with_an_extra_line_for_an_id_not_in_the_set_are_refused_20` | the notes are delivered unchecked (exit 0) |
| S3 | `test_w2_173_notes.py::test_s3_result_counts_that_disagree_with_the_lines_are_refused_20` | the notes are delivered unchecked (exit 0) |
| S4 | `test_w2_173_classes.py::test_s4_well_formed_classes_are_delivered` | green today (holds already) |
| S4 | `test_w2_173_classes.py::test_s4_well_formed_classes_using_all_five_classes_are_delivered` | green today (holds already) |
| S4 | `test_w2_173_classes.py::test_s4_a_reason_of_exactly_200_characters_is_delivered` | green today (holds already) |
| S4 | `test_w2_173_classes.py::test_s4_classes_that_do_not_fit_the_form_are_refused_20` | the classes are delivered unchecked (exit 0) |
| S4 | `test_w2_173_classes.py::test_s4_result_counts_that_disagree_with_the_classes_are_refused_20` | the classes are delivered unchecked (exit 0) |
| S5 | `test_w2_173_unchanged.py::test_s5_a_set_up_a_result_with_a_stopped_word_still_ends_20_not_21` | green today (holds already) |
| F1 | `test_w2_173_effort.py::test_s1_a_brief_naming_high_starts_the_session_with_effort_high` | the session's argv carries no `--effort` |
| F1 | `test_w2_173_effort.py::test_s1_an_effort_outside_the_five_refuses_10_before_anything_is_built` | the value is ignored: the run builds and delivers (exit 0) |
| F2 | `test_w2_173_stopped.py::test_s2_a_writer_result_that_stopped_delivers_nothing_and_ends_21` | the set is delivered (exit 0) |
| F2 | `test_w2_173_stopped.py::test_s2_a_checker_result_that_stopped_delivers_nothing_and_ends_21` | the notes are delivered (exit 0) |
| F2 | `test_w2_173_notes.py::test_s3_notes_with_a_missing_line_are_refused_20` | the notes are delivered unchecked (exit 0) |
| F2 | `test_w2_173_classes.py::test_s4_classes_that_do_not_fit_the_form_are_refused_20` | the classes are delivered unchecked (exit 0) |
| F3 | `test_w2_173_unchanged.py::test_f3_the_branch_changes_no_template_path_map_guard_approved_list_or_set_up_a_brief` | judged only on `w2/W2-173` (green there while it changes only `tests/acceptance/W2-173/`); skipped with its reason on any other checkout |
| F4 | `test_w2_173_unchanged.py::test_f4_the_branch_changes_only_the_ticket_s_paths` | judged only on `w2/W2-173` (green there while it changes only the ticket's paths); skipped with its reason on any other checkout |
| F3 | `test_w2_173_unchanged.py::test_f3_planted_w2_173_branch_with_a_forbidden_path_fails_naming_it` | planted `w2/W2-173` with `governance/project/path-map.yaml`: F3's judgement fails naming it |
| F3 | `test_w2_173_unchanged.py::test_f3_planted_w2_173_branch_with_a_change_outside_its_paths_but_no_forbidden_one_passes` | control: a path outside W2-173's paths but in no forbidden glob passes F3 on planted `w2/W2-173` |
| F4 | `test_w2_173_unchanged.py::test_f4_planted_w2_173_branch_with_a_change_outside_its_paths_fails_naming_it` | planted `w2/W2-173` with `docs/changes/W2-178-evidence.md`: F4's judgement fails naming it |
| F3 | `test_w2_173_unchanged.py::test_planted_w2_173_branch_with_a_change_inside_its_paths_passes[f3]` | pass control: `indep_launch.py` on planted `w2/W2-173` passes F3's judgement |
| F4 | `test_w2_173_unchanged.py::test_planted_w2_173_branch_with_a_change_inside_its_paths_passes[f4]` | pass control: `indep_launch.py` on planted `w2/W2-173` passes F4's judgement |
| F3 | `test_w2_173_unchanged.py::test_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason[f3]` | the same change on planted `w2/W2-178`: F3's judgement skipped, the reason naming both branches |
| F4 | `test_w2_173_unchanged.py::test_planted_other_ticket_branch_with_the_same_change_is_skipped_with_its_reason[f4]` | the same change on planted `w2/W2-178`: F4's judgement skipped, the reason naming both branches |
| F3 | `test_w2_173_unchanged.py::test_planted_other_ticket_branch_with_a_forbidden_path_is_skipped_with_its_reason[f3]` | a forbidden path on planted `w2/W2-178`: F3's judgement skipped |
| F4 | `test_w2_173_unchanged.py::test_planted_other_ticket_branch_with_a_forbidden_path_is_skipped_with_its_reason[f4]` | a forbidden path on planted `w2/W2-178`: F4's judgement skipped |
| F3 | `test_w2_173_unchanged.py::test_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason[f3]` | a detached `--no-ff` candidate merge of `w2/W2-178` into `w2/integrate`: F3's judgement skipped ("detached HEAD") |
| F4 | `test_w2_173_unchanged.py::test_planted_candidate_merge_on_a_detached_head_is_skipped_with_its_reason[f4]` | a detached `--no-ff` candidate merge of `w2/W2-178` into `w2/integrate`: F4's judgement skipped ("detached HEAD") |
| F3 | `test_w2_173_unchanged.py::test_planted_integrate_branch_itself_is_skipped_with_its_reason[f3]` | `w2/integrate` itself: F3's judgement skipped |
| F4 | `test_w2_173_unchanged.py::test_planted_integrate_branch_itself_is_skipped_with_its_reason[f4]` | `w2/integrate` itself: F4's judgement skipped |
| F4 | `test_w2_173_unchanged.py::test_planted_paths_are_outside_the_ticket_s_paths_and_inside_it_as_each_case_needs` | the planted paths fall where each case needs them (outside F4's paths and F3's globs; the path map in F3's; `indep_launch.py` inside) |

At `dac438772`: 61 red, 18 green (79 cases).

## Revision (W2-180, DAEO-weh2)

F3 and F4 diffed whatever branch the suite ran on against its merge-base with `w2/integrate` and judged the names against
W2-173's own forbidden list and `allowed_paths`, so they were red on any other ticket's branch (W2-178's, DAEO-7oxm, which changes
`indep_launch.py`) and on the merge queue's candidate merge of it, attributed to that ticket's
batch (the queue had already ejected W2-121 and W2-179 on W2-170's F5 for the same form). Revised under DEC-866 (Rewrite-Reason),
after W2-170's F5 case (DEC-253, DEC-966, DEC-989): both cases now judge only on `w2/W2-173` and are skipped with their
reason elsewhere; the judgement is in `judge_f3_paths(root)` and `judge_f4_paths(root)`, called with the repository the
file sits in and, by the planted cases, with each planted `git init` repository. No other case changed.
