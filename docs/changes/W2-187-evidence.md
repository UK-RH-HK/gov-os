# W2-187 evidence: the standing hidden set, the maintenance pass, the state per repository

Ticket DAEO-0cd2, engineer. Built to the ticket's `## Interface` (I1 to I12, the gaps and the CTO's routings G1, G2, U1,
U2). The acceptance suite `tests/acceptance/W2-187/` was not merged when this was written: the per-KPI rows below name the
engineer's own unit cases only.

## What was built

- `src/gov/memaudit/standing.py` (new): the record `STANDING.jsonl` (`live`, `retire`, `declared_sets`), `declare` (I3),
  the week rule (`week_of`, `week_state`, `restart`), `drift` (I7), the repair (`repair_after`, `repair_state`,
  `repair_status`), `is_standing`, `latest_maintain`.
- `src/gov/memaudit/maintain.py` (new): the six items of the maintenance pass (I10).
- `schedule.py`: `state_dir`/`state_of` replace `folder`; `decide(repo, state, head, at, lines, standing=, gov=)`;
  `fresh_due`; `due(..., fresh=)`; `retrieval_changed(repo, since, until, gov=None)` with the `gov-pin` trigger; the
  baseline writes `<key folder>/indep/AUDITS.log`.
- `driver.py`: every state path is the key folder; the children get `GOV_INDEP_RUNS_DIR=<key folder>` and
  `GOV_MEMAUDIT_STATE=<key folder>`; `_refusal(..., standing=)`; `standing(...)` beside `run(...)` on the same `_Cycle`,
  `_history`, `_finish`; a fresh run beside a live set writes `kind: fresh` and calls `standing.drift`.
- `layout.py` (`SET_RE`, `WEEK_RE`, `paths(..., week)`), `declare.py` (`bar`, `ROUNDING`, `week`), `preflight.standing` (I6),
  `matcher.questions(..., only=, default=)`, `fault.not_whole(..., store_commit=)`, `measure.run/rescore(week=)`,
  `judge.run(week=)` (live questions, store-commit check on a later search, no `misses.jsonl`, no id in a line),
  `digest.py` (`standing_figures`, `standing_lines`, `drift_line`), `pool.py` (`MS-STANDING`, `--sets`, the diagnostic
  re-measure of a retired set), `classes.py` (`MS-STANDING`), `__main__.py` (the new subcommands and flags).
- `governance/project/orchestration/tools/memaudit_cron.sh`: `--repo`, the live path, today's path unchanged.
- `src/gov/adopt/memory_sets.py`: `walls_act(..., repo=None)` adds step 6 to ACT.md; `fabric.py` is unchanged.
- `prompts.py`, `figures.py`, `runner.py`, `wrapper.py`, `classes.py`'s logic and the launch script are unchanged.

## Per KPI line (engineer's unit cases; `tests/unit/memaudit/` and `tests/unit/adopt/`)

| KPI | cases | result |
|---|---|---|
| S1 | `test_standing.py`: `test_a_new_standing_set_is_recorded_with_each_field`, `..._refused_spent_with_a_count_never_an_id`, `test_an_auditor_run_in_the_log_or_a_class_file_spends_a_set`, `test_a_wave0_verdict_set_with_used_and_its_record_is_accepted...`, `test_a_used_set_without_its_result_record...`, `test_a_second_live_set_is_refused...`, `test_a_set_with_no_delivered_briefs_or_a_bad_form_is_refused`, `test_standing_live_...` | pass |
| S2 | `test_standing.py`: `test_the_week_rule_by_the_markers_in_the_week_folder`, `test_a_verdict_in_the_week_folder_is_final`; `test_standing_run.py`: `test_the_declaration_comes_before_used_before_the_first_search`, `test_a_second_run_in_the_same_week_exits_3_and_writes_nothing`, `test_a_stop_before_the_reader_run_allows_one_restart_in_the_week_and_a_second_is_refused`, `test_a_gate_that_stays_shut...` | pass |
| S3 | `test_standing_run.py`: `test_the_judged_path_is_the_fresh_audits_one_a_spy_sees_the_same_functions_called`, `test_a_result_from_another_store_commit_makes_the_attempt_a_fault_and_one_restart_goes_on`; `test_prompts.py` unchanged | pass |
| S4 | `test_standing_run.py`: `test_five_planted_misses_leave_only_counts_in_every_line_and_file_outside_the_run_folder` | pass |
| S5 | `test_standing.py::test_the_bar_is_95_percent_for_40_79_and_80`; `test_standing_run.py::test_right_at_the_need_right_passes_and_one_under_it_misses[2-pass,3-miss]`; `test_declare.py`, `test_judge.py` (bar and BAR line at 38) | pass |
| S6 | `test_standing_run.py::test_three_broken_anchors_are_dropped_by_count_and_the_set_is_never_edited`; `test_standing.py::test_fewer_than_70_live_questions_prints_standing_thin_in_the_block_and_70_does_not` | pass |
| S7 | `test_standing.py`: the five `drift` cases (S 96 / F 90 retires; S 90 / F 96 stale; S 95 / F 92 none; two figures `not yet (2 of 4)`; no live set) | pass |
| S8 | `test_standing.py`: `fresh_due` 27 and 28 days, the miss, the repair cases (pass-miss-miss, pass 96 then miss 90, under 5 points), `test_status_repair_exits_1_while_open...`, `test_due_answers_for_the_live_set_and_due_fresh_for_the_fresh_one`; the P1 line in the five-misses case | pass |
| S9 | `test_standing.py`: the key, two repositories, the pin change, the change of `retrieval.yaml` and the path map, `test_pool_import_sets_imports_exactly_those_sets_once...` | pass |
| S10 | `test_maintain.py` (13 cases: refresh once, head printed, failing rebuild keeps the store, links count, two unindexed paths, not found and second searches, one changed block listed and one moved block not, standing sets left out, never fails, digests unchanged, no cron writer, usage) | pass |
| S11 | `test_cron.py` (10 cases), `tests/unit/adopt/test_w2_187_walls_act.py` (3) | pass |
| F1 | `MS-STANDING` for `classes`, `pool`, `pool-import --sets`; `driver.standing` launches no auditor or writer; S4's planted strings | pass |
| F2 | week rule cases; `test_an_edited_set_is_refused_before_any_search_and_the_week_is_not_spent`; `test_measure_kept_on_a_standing_set_prints_used_exits_3_and_writes_nothing` | pass |
| F3 | `test_the_standing_run_has_no_decision_force_or_data_flag`; no command compares configurations | pass |
| F4 | `test_prompts.py` unchanged; the spy case | pass |
| F5 | the fresh path without `--week` is byte for byte as before: the existing W2-170, W2-171, W2-173 and W2-88 suites pass but for the cases named under "Acceptance folders" | see below |
| F6 | `test_maintain.py::test_the_pass_changes_neither_the_retrieval_yaml_nor_the_path_map...`, `test_the_module_writes_no_cron_table_and_applies_no_act` | pass |

## G6: a store at the main line's head whose layout is stale

`test_maintain.py::test_a_stale_layout_at_the_main_lines_head_gets_one_rebuild_by_the_same_command_else_stale_kept`: the
link is at the head (item 1 says `current`), the store's layout stamp is one version old. `maintain` runs `<gov> rebuild
--integration main` once (item 2); a stub that re-stamps the store gives `2 layout rebuilt`, a stub that leaves it gives
`2 layout stale kept`. The stub stands for `gov rebuild --integration` (no real rebuild is run in the sandbox). That the
real command rebuilds at an unchanged head when the layout changed rests on `gov.rebuild.integration._complete`, which
compares the half's W2-122 record with `seed.code_fingerprint()`; I did not run it.

## pytest summary lines (the heavy-slot gate, empty HOME, `-m "not local_only" -k "not real and not green_here and not time_limit"`)

Left out by the exclusion: the cases whose names hold `real`, `green_here` or `time_limit` and the `local_only` marker.

- `tests/unit/memaudit` (before the last edits): `300 passed, 1 deselected`, 2 failed: the two `test_judge.py` cases that
  pinned the 85 % BAR line, since fixed; `test_judge.py` then `27 passed`.
- Final run, after the last edits: `tests/unit/memaudit`: `303 passed, 1 deselected`; `tests/unit/adopt`: `192 passed, 54 deselected`.
- `tests/acceptance/W2-170`: `180 passed, 1 skipped, 4 failed` (the four cases that pin the old bar: `need_right` 32 and 36).
- `tests/acceptance/W2-171`: `126 passed, 2 skipped, 13 failed`.
- `tests/acceptance/W2-172`: `26 passed, 1 skipped, 136 failed`.
- `tests/acceptance/W2-173`: `91 passed, 2 skipped`.
- `tests/acceptance/W2-88`: `212 passed, 2 skipped, 3 failed`.

## Fix batch (eng-2): the acceptance suite merged, 14 cases red on the code's side, now green

Run after the fix, each folder alone through the heavy-slot gate, empty HOME, same exclusion:

- `tests/acceptance/W2-187`: `2 failed, 170 passed`. The two reds are the cases the test designer is revising
  (`test_s2_a_run_writes_the_declaration_then_used_before_any_search`,
  `test_s8_the_owners_decision_id_closes_it_and_is_recorded`).
- `tests/acceptance/W2-170`: `184 passed, 1 skipped`.
- `tests/acceptance/W2-171`: `2 failed, 137 passed, 2 skipped`. The two reds are the lead's package P1
  (`test_the_ledger_events_have_item_3s_fields`, `test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result`).
- `tests/acceptance/W2-172`: `2 failed, 160 passed, 1 skipped`. The two reds are the ones the designer is fixing
  (`test_s6_a_log_present_but_empty_is_empty`, `test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log`).
- `tests/acceptance/W2-173`: `91 passed, 2 skipped`.
- `tests/acceptance/W2-88`: `215 passed, 2 skipped`.
- `tests/unit/memaudit`: `306 passed, 1 deselected`. `tests/unit/adopt` was not touched by this batch (last run:
  `192 passed, 54 deselected`).

The fourteen cases and their causes (all in the code, none in the Interface):

| cases | cause | change |
|---|---|---|
| S10 (9 cases) | item 4 printed `none` when the store holds no `lexical_chunk` table (the line must be `4 unindexed <k>`) | `maintain.unindexed_item`: no chunk table is an empty set of held paths; the guarded fallback is 0, a count |
| S1 Wave 0 (2 cases) | the spent check counted the set's own `misses.jsonl` when the Wave 0 conditions failed | `standing._spent` skips the own run's `misses.jsonl` and `miss-classes.json` whenever `USED` exists; `declare` then answers `STANDING_SPENT 0` |
| S6 (1 case) | `STANDING_THIN` was in a `flags` field, not in the HISTORY line's `word` | `driver._standing_line`: `word` is `[word, "STANDING_THIN <n>"]` below 70 live questions |
| S8 (2 cases) | the digest line was `REPAIR open since <week>`, I12 says `REPAIR open` | `digest.standing_lines`; `status --repair` keeps `since <week>` (I8) |

Unit cases added or changed: `test_maintain.py::test_a_store_with_no_chunk_table_...`; `test_standing.py` (the used set
without its record or at another commit is `STANDING_SPENT 0`; another run's record of a used set's question still counts;
the digest line `REPAIR open`; the thin plant's `word` list); `test_standing_run.py` (the `word` list for the 40-question plant).

## Acceptance folders: the reds, and why (before the fix batch, kept for the record)

All are expected until the designer's revision is merged (the files are named by their results only; I did not read the
ticket's six revised files or the two G1 helpers).

- W2-170 (4): `test_w2_170_s3_declare.py`, the old bar values.
- W2-171 (13): `test_w2_171_s3_judge.py` (6), `test_w2_171_s6_figures.py` (4, `figures.bar.need_right` 38 against 34 and 36
  against 32), `test_w2_171_s5_misses_f2.py` (1, line 82 expects the text `BAR at least 34 right (NOT met)`),
  `test_w2_171_cli_layout_ledger.py::test_the_ledger_events_have_item_3s_fields` (the verdict `passes` is now False, the case
  plants 35 right), and `test_help_prints_usage_...` which my own help text broke and I fixed.
  **Not in the designer's list of six:** `test_w2_171_s5_misses_f2.py`, `test_w2_171_s6_figures.py` and
  `test_w2_171_cli_layout_ledger.py`. F5 says W2-171's S5 case passes unchanged; with the bar at 95 % it cannot (its BAR line
  names 34). A package for the lead.
- W2-172 (136) and W2-88 `test_s21_the_baseline_line_holds_the_verdict_commit` (reads `repo.audits_log` of the G1 helper) fail
  on the state moving to `<runs>/indep/memaudit/<key>/` (the planted history and the log are read from the old place; one
  case shows `REASON start` where `churn` is expected). The G1 helpers are the designer's.
- W2-88 `test_s15_guard_the_declared_bar_...` (2) read W2-170's helper `bar` (the designer's).

## Size

`git diff --stat 5336a6fca`: source and the wrapper `1447 insertions, 144 deletions` in 17 files (docstrings included);
tests `1410+` insertions. S10 (`maintain.py`, 231 lines) and S11 (the wrapper, about 60 lines; the ACT text, about 25) are
separate commits, so a split into W2-187b leaves S1 to S9 clean.

## Readings of the Interface

1. **I6, `STANDING_THIN` in the HISTORY line (revised after the acceptance run).** I4 gives `"word": "pass"|"miss"` and I6
   says `STANDING_THIN` goes "in the HISTORY line's `word` list". `word` is the string `pass` or `miss`; below 70 live
   questions it is the list `["pass"|"miss", "STANDING_THIN <live>"]` (no `flags` field any more). Readers (`--replaces`,
   repair, drift, `verdict_of`) accept `word` as a string or a list.
2. **I3, the Wave 0 check (revised after the acceptance run).** "The first line of the repository's `AUDITS.log`" is the
   first line of `<key folder>/indep/AUDITS.log`, else of `<runs-dir>/indep/AUDITS.log`. The spent check skips the set's own
   `runs/<set>/misses.jsonl` and `miss-classes.json` whenever `runs/<set>/USED` exists, whether or not the Wave 0
   conditions then hold (the lead's reading of I3); a used set that lacks its record or is at another commit is then
   `STANDING_SPENT 0`. A retired set's name is `STANDING_SPENT 0` on a second declaration.
10. **I10, item 4 and I12's `REPAIR` line (revised after the acceptance run).** Item 4 is always a count: a store with no
    `lexical_chunk` table holds no path (every indexed tracked path counts), and an unreadable store counts 0 (item 1 names
    a store that could not be read). The digest's line is `REPAIR open` (I12), without the week; `status --repair` keeps
    `REPAIR open since <week>` (I8).
3. **I4, refusals.** `STANDING_NONE`, `STANDING_RETIRED` (a record exists, none live), `STANDING_DIGEST` and `USED` print as
   the bare code; an `RN-` refusal prints `REFUSED RN-<x>`. Nothing is written for any of them but the `LOCK` file of an `RN-`
   refusal (as in `run`). `RN-NOBASE`, `RN-RECENT` and `RN-NAME` are not asked of a standing run.
4. **I6, the root.** The pre-flight loads each question at `--repo` (the same root `measure` and `judge` use), with the set's
   default map entry when the sets root's map has none yet (`declare` adds it at the first week). A set-level fault
   (`MatcherError`) is raised, not a drop. `ok` is False only when a standing record exists whose digest differs; the driver
   finds the record through `GOV_MEMAUDIT_STATE`.
5. **I7.** `drift` writes its own HISTORY and STANDING lines; `STANDING_STALE` also writes a HISTORY line. The digest line is
   `DRIFT not yet (k of 4)` (I12), not the S7 text `drift: not yet (k of 4)`.
6. **I8.** `miss` for `due --fresh` has no weekday condition: due when the live set's last standing line missed and no
   fresh start lies in the current ISO week. The repair is also read from the lines: a standing line that passes after an
   `open` closes it, with or without a `closed` line.
7. **I10, item words.** Item 1: `current <12>`, `refreshed <12>`, `kept <12> (refresh exit <c>)`; item 2: `current`,
   `rebuilt`, `stale kept`. `entry` in a request is the integer `n` of `entry n` and of `entry n.m`, one row a question and
   entry. Item 6 reads `visible` and `hidden` of every set in the map but the standing ones (live, retired, and any name
   `memory-standing-<date>`).
8. **I11.** `cron.log` is the key folder's when `standing live` prints a `KEY` line, else the old place. `<GOV_OS>` in the ACT
   line is the absolute path of the Gov OS checkout the module lies in.
9. **`--week` with a standing-form name and without it.** A name `memory-standing-<date>` given to `preflight`, `void`,
   `declare`, `measure`, `judge`, `classes` or `pool` without `--week` is `MS-STANDING` (exit 1), so a standing set cannot
   take the fresh path.

## Risks for the lead

- **RN-STALE on a quiet Monday.** `standing run` reuses RN-STALE (the head's commit older than 24 hours is refused). A
  weekend with no commit refuses Monday's run unless the maintenance pass's refreshed head is newer. The same holds for
  `run`. I did not change the rule.
- **A broken anchor can stop the measure.** The pre-flight drops a question whose anchors no longer resolve, but
  `gov.retrieval.measure` loads the whole set; a source with a heading and no `lines` whose file is gone raises
  `MeasureError` there (`_span`), the attempt is a fault and the week stops at `STOPPED fault`. Questions with `lines` and a
  commit (the writer brief's form) resolve to "unresolved" and are measured as not found.
- The real `gov rebuild --integration`, `gov links` and the model calls were never run (stubs only).
