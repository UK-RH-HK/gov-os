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
| S10 (6), N2 (b) | `test_maintain.py`: `test_a_rewritten_heading_section_is_listed_and_a_moved_unchanged_one_is_not`, `test_an_unchanged_heading_section_is_not_listed`, `test_a_section_at_the_end_of_the_file_is_compared_to_the_end_and_the_one_above_it_stops_at_it`, `test_a_sub_section_ends_at_the_next_heading_of_a_higher_level`, `test_a_change_inside_a_sub_section_lists_it_and_the_section_that_holds_it`, `test_an_entry_both_rules_list_is_listed_once`, `test_a_source_with_no_commit_is_never_listed_for_its_section`, `test_the_sources_own_commit_comes_before_the_questions`, `test_a_source_git_cannot_show_at_its_commit_is_skipped_never_the_pass`, `test_the_section_rule_is_measures_span_rule` | pass (red with the new call disabled) |
| S11 | `test_cron.py` (10 cases), `tests/unit/adopt/test_w2_187_walls_act.py` (3) | pass |
| S12 | `test_push.py` (23 cases: a clean scan pushes once and the line is the last of the latest `DIGEST.txt`, a standing week's digest included; findings block the push and no planted secret is written anywhere; a report with entries is a finding whatever the exit; exit 2, an empty or unparsable report, the timeout and a missing binary are `scan failed <word>`; the binary is the flag, else `$GOV_MEMAUDIT_GITLEAKS`, else PATH; no declaration, empty or blank: `PUSH none: no declaration`, nothing called; a malformed declaration is usage 4; a push git refuses is exit 2 with its output in a 0600 `PUSH.log`, never printed); `test_cron.py` (the push is the last step, only when a step started, its line with the step `push`, the wrapper's exit unchanged, never at `maintain`); `tests/unit/adopt/test_w2_187_walls_act.py::test_step_6_names_the_cycles_order_and_how_the_owner_declares_the_push_and_installs_nothing` | pass |
| F1 | `MS-STANDING` for `classes`, `pool`, `pool-import --sets`; `driver.standing` launches no auditor or writer; S4's planted strings | pass |
| F2 | week rule cases; `test_an_edited_set_is_refused_before_any_search_and_the_week_is_not_spent`; `test_measure_kept_on_a_standing_set_prints_used_exits_3_and_writes_nothing` | pass |
| F3 | `test_the_standing_run_has_no_decision_force_or_data_flag`; no command compares configurations | pass |
| F4 | `test_prompts.py` unchanged; the spy case | pass |
| F5 | the fresh path without `--week` is byte for byte as before: the existing W2-170, W2-171, W2-173 and W2-88 suites pass but for the cases named under "Acceptance folders" | see below |
| F6 | `test_maintain.py::test_the_pass_changes_neither_the_retrieval_yaml_nor_the_path_map...`, `test_the_module_writes_no_cron_table_and_applies_no_act` | pass |
| F7 | `test_push.py`: `test_a_scan_that_finds_something_blocks_the_push_and_no_text_of_a_finding_is_written` (the remote unchanged, `SECRET` absent from stdout, stderr and every file written), the `scan failed` cases, `test_no_declaration_runs_neither_the_scan_nor_the_push_and_says_so`, `test_this_module_holds_the_only_scanner_call_of_the_audit_and_the_wrapper` (one `"detect"` call; no other module of `gov.memaudit` and not the wrapper names the scanner); `test_cron.py::test_a_cycle_where_nothing_is_due_or_due_fails_runs_no_push`, `test_maintain_alone_never_runs_the_push` | pass (red with the findings check disabled) |

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
4. **I6, the root (revised by the fix batch after review round 1, F-A).** The driver now hands `preflight`, `measure` and
   `judge` the store link's work tree as `--repo`, on both paths (see "Fix batch 5" below); before that it handed them the
   repository. The pre-flight loads each question at `--repo` (the same root `measure` and `judge` use), with the set's
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


## Fix batch 3 (eng-3): S10 (6) with N2 (b), then S12 and F7 (I13)

**S10 (6), N2 (b) (DEC-1180 (1)).** `matcher.section` is measure's `_span` rule for a `#` heading (from the first line equal
to the heading, trailing whitespace removed, to the line before the next heading of the same or a higher level, else the
end of the file, with measure's own `_HEADING`); `matcher.section_changed(source, base, repo, cache)` compares that
section's lines at the source's own commit (else the question's; read with measure's `_lines_at`, one `git show` per file
and commit) with the section's lines at the head. `maintain._sections_changed` lists the entry (`n` of `n.m`) once, into the
same set as `matcher.questions`'s `unresolved`, so an entry both rules list is one row. `matcher.questions` now also returns
the question's `commit`. A source with no commit, no `#` heading, a heading missing at either side or a file git cannot show
is not listed; a fault reading one source skips that source. The request file, the digest and the printed line keep their
forms (no question, answer or path). `test_the_section_rule_is_measures_span_rule` checks `matcher.section` against
`measure._span` for four headings.

**S12, F7 (I13), word for word.** `src/gov/memaudit/push.py` (`python3 -m gov.memaudit push --sets-root R [--repo D]
[--gitleaks EXE]`; its flags are defined there, so `__main__.py` and the other modules never name the scanner):
`GOV_MEMAUDIT_PUSH="<remote> <branch>"`; one `detect --source <repo> --no-banner --redact --report-format json --report-path
<0600 temporary file outside the repository>`; the entries are counted and the report is deleted in a `finally`; exit 0 with
no entries is clean, exit 1 with entries is `findings <k>`, any other exit, the timeout (`GOV_MEMAUDIT_SCAN_TIMEOUT_S`,
default 600) or no binary is `scan failed <word>` (`exit`, `timeout`, `missing`, plus `report` for a report that cannot
be counted, which fails closed); `git push <remote> <branch>` only on a clean scan; the five lines and exits of I13 (1 blocked,
2 push failed, via the exit words `refused` and `stopped`); git's output in `<key folder>/PUSH.log` (0600); the same line
appended to the newest `DIGEST.txt` of the key folder (a fresh run's or a standing week's). `say` is the only printer.
`memaudit_cron.sh`: `push_step` after the audit steps that started, on the live path and today's path, declared or not; the
wrapper's exit stays the audit steps'. **`push` itself writes** (fix batch 4, the lead's reading of I13, accepted by the CTO
with DEC-1157 (3)) its `cron.log` line (six keys, `mode` `push`, `reason` the line without `PUSH `, quotes and backslashes
removed, `exit` the push's own) and its `DIGEST.txt` last line, **only when a push is declared**; the wrapper writes no push
line, so never two. A no-declaration `push` prints `PUSH none: no declaration`, exits 0, calls no scanner and writes nothing;
the wrapper does not swallow it, so the cron's output names the skip. The log is `<key folder>/cron.log`; the wrapper names
its own log (the key folder's, else the runs folder's) to `push` in `GOV_MEMAUDIT_CRON_LOG` (no new flag; I13's command line is
unchanged). `memory_sets.PUSH_ORDER` is I13's sentence on the
step 6 line.

**Run after the change** (each folder alone through the heavy-slot gate, empty HOME, the same exclusion; the exclusion left
out the `real`, `green_here` and `time_limit` cases and `local_only`):

- `tests/unit/memaudit` and `tests/unit/adopt/test_w2_187_walls_act.py`: `352 passed, 1 deselected` (the final run, after
  the last edit).
- `tests/acceptance/W2-187`: `172 passed`, none red: the test designer's S10 cases naming a rewritten heading section and the
  S12/F7 cases are not merged yet, so they did not run.
- `tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py`: `12 passed`; `tests/acceptance/W2-88/test_w2_88_s18_s23_memory_sets.py`
  with `tests/unit/adopt/test_w2_88_memory_sets.py` and `test_w2_88_fabric.py`: `25 passed`.
- `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` after the runs: nothing of this session's.

**I13 against W2-172 S9's unchanged cases (the lead's reading, fix batch 4).** The live path's S11 case and W2-172 S9's
`one cron.log line a cycle` take exactly one wrapper line; `push` writing its own line only when a push is declared keeps the
audit's line as it was, and the wrapper's exit is the last audit step's (`push`'s own exit goes to its line and its output,
never to the cycle). Unit cases: `test_push.py` (a declared push writes one line with the six keys, `mode` `push` and its exit
0, 1 or 2; a no-declaration push writes nothing; a usage fault writes no line; the wrapper may name the log) and `test_cron.py`
(the wrapper logs no push line and hands `push` its log; no declaration reaches the wrapper's stdout; today's path ends with the
push, declared or not, and exits with the run's code).

## Size after batch 3

`git diff --stat 5336a6fca -- src governance`: `35 files changed, 2303 insertions(+), 271 deletions(-)` (it holds the
other tickets' merged files). The ticket's own source (`src/gov/memaudit/`, `src/gov/adopt/memory_sets.py` and the
wrapper): `17 files, 1532 insertions, 145 deletions`; this batch added `push.py` (206 lines with its docstring), the section
rule (about 45 lines in `matcher.py` and `maintain.py`) and the wrapper's `push_step` (about 18 lines). Tests: `test_push.py`
(23 cases), nine S10 cases, seven S12 cases in `test_cron.py`, one ACT case.

## Fix batch 5 (eng-5): F-A, F-B and R1 after review round 1 (the CTO, 2026-11-14; DEC-1157 (12), DEC-1180 (4), DEC-1156 (7))

Review round 1 (`docs/probes/DAEO-0cd2/PR-DAEO-0cd2.md`) passed. The CTO had F-A fixed in this ticket, with F-B and R1
fixed alongside it.

| finding | KPI | behaviour now | code | unit cases (each red before the change, green after) |
|---|---|---|---|---|
| F-A, the searched store is the declared store | S3, S6/I6, S7 | `preflight`, `measure` and `judge` get the store link's work tree as `--repo`. They get it on the standing path and on the fresh path. The link's `HEAD` is the audit commit: the driver takes the commit from it. So every search (the probe, the control, the measure, judge's later searches) runs in the link and reaches the link's store, the store the declaration names and checks. The anchors are read in that tree, and the fresh run's figures come from the store S7 compares. Nothing changed in `prompts.py`, the reader, the grader or the matcher. The children's cwd stays the repository: the launch steps, `void`, `classes`, `pool` and `figures` are unchanged. | `driver._Cycle.standing`, `driver._Cycle.run` | `test_standing_run.py::test_the_searches_reach_the_links_store_when_the_repositorys_own_store_is_at_another_commit`: the repository's own store sits at the earlier commit and the link's at the head; the planted `gov` answers the commit of the store in its cwd. Before the change the run ended `STOPPED measure 2` on the store-commit fault; now it gives `right 40 of 40: passes` with no `FAULT`, and every `gov` call's cwd is the link. `test_standing_run.py::test_the_planted_gov_answers_the_store_of_the_folder_it_runs_in` shows the stand-in cannot pass for the wrong reason. `test_driver.py::test_preflight_measure_and_judge_are_handed_the_store_link_not_the_repository[standing,run]`, `test_driver.py::test_the_fresh_path_still_starts_its_launch_steps_and_figures_as_before` |
| F-B, push only the scanned commit | S12, F7 | Just before the scan, `push.scanned` records the commit `refs/heads/<branch>` names. A clean scan then pushes with `git push <remote> <sha>:refs/heads/<branch>`, so the remote's branch is the scanned commit. The line stays `PUSH pushed <remote> <branch> <12 hex of the scanned commit>`. A commit that lands during the scan waits for the next cycle's own scan. A branch that names no commit when the scan begins pushes nothing (`PUSH failed: git push exit <git's rev-parse exit, 128>`, exit 2, git's output in the 0600 `PUSH.log`); a branch made during the scan is not pushed either. | `push.scanned`, `push.push`, `push.run` (`_pushed` removed) | `test_push.py::test_a_commit_that_lands_during_the_scan_is_not_pushed_only_the_scanned_one_is` (the planted scanner commits on `main` while it runs: before the change the remote held the late commit; now it holds the scanned one), `test_a_second_cycle_pushes_the_late_commit_after_its_own_scan`, `test_a_branch_that_names_no_commit_when_the_scan_begins_pushes_nothing`, `test_a_branch_made_during_the_scan_is_not_pushed` |
| R1, gitleaks on step 6's cron line | S11, S12 | A9's ACT.md step 6 line is `` `0 21 * * 1 GOV_MEMAUDIT_SETS_ROOT=<sets_root> GOV_MEMAUDIT_GITLEAKS=<gitleaks> <GOV_OS>/…/memaudit_cron.sh --repo <repo>` `` followed by I13's sentence, unchanged. `<gitleaks>` is `os.path.abspath(shutil.which("gitleaks"))` when A9 runs, else the literal `<path to gitleaks>`. The rest of the line is unchanged. | `memory_sets._gitleaks`, `memory_sets.walls_act` | `tests/unit/adopt/test_w2_187_walls_act.py`: `test_the_act_holds_the_cron_line_with_the_repositorys_path_as_step_6` (revised to the new line), `test_step_6_names_the_scanner_found_when_a9_runs_because_crons_path_lacks_it`, `test_with_no_scanner_on_path_step_6_holds_the_placeholder_for_the_operator`, `test_a_relative_answer_of_which_is_written_as_an_absolute_path` (`shutil.which` stood in for each time, never the machine's PATH) |

**Red, then green.** The ten new or revised cases above ran first against `46d131ab9`: `10 failed, 62 passed` over
`test_driver.py`, `test_push.py`, `test_standing_run.py` and `test_w2_187_walls_act.py`. Each failed for the reason it
names: the children got `.../repository`, the run ended `STOPPED measure 2`, the remote held the late commit, the push
printed `exit 1` from git's refspec error, the line had no `GOV_MEMAUDIT_GITLEAKS`. After the change the same files gave
`72 passed`.

**The planted `gov` (`tests/unit/memaudit/fakes.py`).** With `plan["store_from_cwd"]` set, it answers
`result.store.commit` from the fingerprints head of `<its --root, else its cwd>/.gov-runtime/store.db`. With no store
there it gives no field, which is itself a fault. A per-question `store_commit` override still wins. Without the key the
stand-in behaves as before.

**Left as it was (outside the decided fix):** the fresh path's `pool` child still gets the repository as `--repo`, so the
pool's retrieval-only re-measure still searches the repository's own store. The brief named `preflight`, `measure` and
`judge` only. See discoveries in the return.

**Run after the change** (each folder alone through the heavy-slot gate, empty HOME, `-m "not local_only" -k "not real
and not green_here and not time_limit"`; the exclusion left out the `local_only`, `real`, `green_here` and `time_limit`
cases):

- `tests/unit/memaudit`: `363 passed, 1 deselected`.
- `tests/unit/adopt/test_w2_187_walls_act.py`: `7 passed`.
- `tests/acceptance/W2-187`: `205 passed`. The test designer's F-A, F-B and R1 cases are not merged yet, so they did not run.
- `tests/acceptance/W2-172`: `162 passed, 1 skipped`. No W2-172 case pinned the repository as the children's root.
- `tests/acceptance/W2-170`: `184 passed, 1 skipped`.
- `tests/acceptance/W2-171`: `139 passed, 2 skipped`. With `-rs`, the skips are
  `test_w2_171_f3_f4_order_and_servers.py:147` (the sandbox forbids AF_UNIX sockets) and `test_w2_171_f5_paths.py:53` (F5
  judges only the branch `w2/W2-171`). Both are environment skips.
- `tests/acceptance/W2-173`: `91 passed, 2 skipped`.
- `tests/acceptance/W2-88`: `215 passed, 2 skipped`.

**Size.** `git diff --numstat 46d131ab9 -- src`: `driver.py` +14 -10, `push.py` +38 -27, `memory_sets.py` +11 -1
(docstrings included). Tests: +201 -4 over five files.
