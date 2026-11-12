# W2-171 (DAEO-k1e2): the memory audit's measure, evidence

Engineer's record. Built to the ticket's `## Interface` (items 1 to 12) and the CTO's ten rulings under it; no item was
changed. Profile FULL, class C2. Every unit test plants its own fake `gov` (in a `pin-<12 hex>` folder), fake `claude`,
sets root, repository and store under pytest's `tmp_path`: never a real search, a real model call, a GPU, the real sets
root (`~/gov-os-eval`) or the real runs folder.

## What was built (`src/gov/memaudit/`)

| module | serves | what it does |
|---|---|---|
| `__main__.py`, `__init__.py` | item 1, 2 | the five subcommands `measure`, `judge`, `classes`, `pool`, `pool-import`; each prints through `say` only; W2-170's three subcommands are unchanged; the exit word `stopped` is exit 2 |
| `measure.py` | S1, S2, S4, F3 | `declare` (W2-170), the ready check, the control, the attempts and the fault rule, the `RETRIEVAL` line; `measure --kept <n>` |
| `runner.py` | S1, S2, S4, F4 | the measure and the probe as child processes, the environment as the fresh 80 ran it, stderr to files |
| `wrapper.py` | S2, S4, F3, F4 | the `gov` wrapper of a run: keeps each `retrieve` output, writes the `search` event before it returns the output |
| `fault.py` | S4, F3 | `degraded` (the fresh 80's), the measure's question lines, the whole-attempt check |
| `events.py` | item 3, S8 | the ledger appended under one lock (`ledger.append` of W2-170, imported) |
| `matcher.py` | S2, S3, S5 | the only importer of `gov.retrieval.measure`'s private names (ruling 3) |
| `prompts.py` | S3 | the pinned reader and grader parts (item 7) |
| `claude.py` | S3, S8 | `run_claude` (the one seam), the model call, the retry once, the spend event |
| `judge.py` | S3, S5, S8 | the reader run, the graders, the brake, the resume |
| `figures.py`, `scores.py` | S3, S5, S6 | `FIGURES.json`, `misses.jsonl`, the five printed lines, the exact interval, the retrieval figures |
| `pool.py` | S7 | `pool` and `pool-import` |
| `classes.py` | S6 | the auditor's five class counts into `FIGURES.json` |

## The pinned prompts: recomputed against item 7's list

`.gov-runtime/scratch/ref/d4b/e2_run.py` has sha256 `f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a`
(checked before copying). `tests/unit/memaudit/test_prompts.py` recomputes each item from `src/gov/memaudit/prompts.py`
(UTF-8 text; a schema as `json.dumps(schema)`; a function by `inspect.getsource` and, in a second test, by its syntax-tree
text):

| item | sha256 (recomputed, equal to item 7's) |
|---|---|
| READER_SYS | `a0e222af4a0f9a6ca2cb8e31dd44dc7c21e684c5a0de0e0d081947eacef85e08` |
| READER_SCHEMA | `216897d1c451e34033fafd75d1f6be408b0f82dacd5ff885dcad37351c578e5d` |
| GRADER_SYS | `58d1ad87b24064b28bb09c498a9915f66f0867ffa1e09565f59fd33c7e2ac6d4` |
| GRADER_SCHEMA | `7bfc5786b59231cb7576cdbeeef713ca3524e18205189f73c598ac323c8370a8` |
| grader prompt (`GRADER_PROMPT`, real newlines) | `c12bc5ee7fe303c4e83d6c8803683e2697b1e2f595ecd382e771e61ead15879e` |
| prompt_of | `4a8c1c65619d7111c6dbdc7aae8de6164306ea0366d9410f8ea5095a04fb8c42` |
| items_of | `38cb4b5de225235759064e88027287fd8de4c1fa48e24007e1e573d048aa19f1` |
| outcome | `41a930d83aa170bb33e703b7daa39d6f9f489db9767c52a152cd1cae23899f13` |
| mcnemar | `48e0099533762dd0b2df6f80e7b1f42c0ae214de94d76ea13964cfbe641557d7` |

`CAP = 3`. The refine strings and `UNRANKED_NOTE` are not copied (a test says so).

## Each KPI line and the unit tests that show it

Files: `tests/unit/memaudit/test_measure.py` (M), `test_judge.py` (J), `test_pool.py` (P), `test_fault.py` (F),
`test_prompts.py` (PR).

| KPI line | tests |
|---|---|
| **S1** the control first, 34 and 33 proceed, 31 stops before the audit set's first search, `USED` as written | M `test_a_control_at_34_proceeds…`, `test_a_control_at_33_proceeds`, `test_a_control_at_31_stops_before_the_audit_sets_first_search_and_leaves_used_as_written` (the fake `gov`'s own call log holds no audit question), `test_the_control_compares_with_the_last_audits_figure`, `test_a_missing_control_set_ends_the_ready_check_with_notready` |
| **S2** one attempt's figures equal the planted ranks; the kept outputs re-score with `--kept` | M `test_a_control_at_34_proceeds…` (the `RETRIEVAL` line against ranks planted over 40 questions; 40 kept files; `--kept 1` prints the same line and writes nothing), `test_the_kept_flag_of_an_attempt_that_does_not_exist_is_ms_kept_exit_1_never_3` |
| **S3** the judged run, the verdict line, the bar (34 and 2 at n = 40), the beside figures | J `test_the_verdict_lines_show_the_planted_right_wrong_interval_and_the_bar` (34 of 40, 2 wrong claims, exact interval 70.2 to 94.3 % cross-checked against scipy's beta quantiles, 0.7016 and 0.9429), `test_figures_json_holds_exactly_item_10s_keys_and_counts` (A1 33, A3 35, one gain, McNemar p 1.0), `test_each_call_is_the_fresh_80s_argv_with_no_tools_and_the_models_of_item_7`, `test_a_call_that_returns_nothing_is_run_once_more_never_a_third_time`, `test_the_second_grader_disagreeing_is_counted_beside_the_verdict`, `test_the_calls_are_the_fresh_80s_form_one_search_failure_is_counted_and_named`; PR (all) |
| **S4** the fault rule | M `test_a_degraded_search_makes_the_attempt_not_whole_one_restart_then_it_passes`, `test_two_faults_stop_the_audit_for_the_owner`, `test_a_measure_that_exits_non_zero_is_a_fault_of_cause_exit`, `test_a_pool_fallback_is_degraded_too`, `test_a_store_that_changed_during_the_attempt_stops_with_no_restart_and_no_rebuild`, `test_a_probe_not_answered_as_declared_stops_before_anything_is_spent` (and the parametrized `why` words), `test_no_restart_into_the_same_outage`; F `test_degraded_is_the_fresh_80s_rule_on_a_kept_result` (16 cases), `test_an_attempt_not_whole_names_whole` |
| **S5** a miss is a result: `misses.jsonl`, never run again | J `test_misses_jsonl_has_one_line_a_miss_in_the_briefs_form_with_json_booleans`, `test_an_audit_with_no_miss_writes_an_empty_misses_file`, `test_a_verdict_below_the_bar_stands_is_never_run_again_and_misses_is_byte_identical`; M `test_a_second_measure_is_refused_by_used_and_writes_nothing` |
| **S6** `FIGURES.json` counts only, by rank bucket, namespace, category, route; the class counts | J `test_figures_json_holds_exactly_item_10s_keys_and_counts`, `test_the_misses_are_counted_by_rank_bucket_namespace_category_and_route`, the unique-word test (F1); P `test_classes_adds_the_five_counts_to_figures_json_summing_to_the_misses`, `test_classes_for_other_ids_or_another_class_is_ms_classes_and_changes_nothing`, `test_classes_without_figures_is_ms_nofigures` |
| **S7** the pool: whole to 400, else a seeded draw, the regression named, the import | P `test_a_pool_of_300_is_measured_whole_and_the_audits_questions_join_it`, `test_a_pool_of_900_is_a_seeded_draw_of_400_measured_as_the_copied_set`, `test_the_draw_is_400_of_the_sorted_ids_and_the_same_seed_gives_the_same_draw`, `test_the_default_seed_is_fifteen_hex_digits_of_the_audit_and_the_digest`, `test_a_fall_of_3_points_or_more_in_either_figure_is_named_a_regression` (a fall of 4 named, of 2 not), `test_a_fall_in_full_evidence_alone_is_named_with_its_own_word`, `test_pool_needs_figures_and_runs_once`, `test_a_different_file_in_the_pool_under_the_audits_name_is_ms_pooldiff…`, `test_a_map_that_cannot_take_the_entry_is_dc_map_and_nothing_is_written`, `test_a_pool_run_that_is_not_whole_is_ms_poolfault`, `test_pool_import_copies_the_79_and_the_138…`, `test_pool_import_with_another_count_is_ms_importcount_and_writes_nothing` |
| **S8** spend bounded and recorded; a brake stop; the resume | J `test_every_calls_cost_is_a_spend_event_with_the_runs_running_total`, `test_the_run_stops_at_twice_its_projection_to_the_owner_and_writes_no_misses_or_figures`, `test_a_stopped_run_resumes_asking_only_the_unfinished_questions_from_the_ledger_total`, `test_resume_needs_a_raised_projection_and_a_brake_stop_else_it_is_refused`, `test_a_planted_ledger_over_the_brake_stops_before_any_call_and_resume_starts_from_its_total`, `test_the_default_projection_is_0_157_a_question_and_the_flag_overrides_it` |
| **F1** no question, gold answer, answer or source path leaves | J `test_a_unique_word_in_a_question_gold_answer_answer_and_path_is_found_nowhere_but_misses_and_reader` (standard output and error of `measure` and `judge`, the ledger, `FIGURES.json`, every log and marker of the run folder: 0 times; the words are in `misses.jsonl` and the reader's row, as item 9 designs) |
| **F2** a set measured twice, or re-scored to pass | J `test_a_verdict_below_the_bar_stands…`; M `test_a_second_measure_is_refused…` |
| **F3** a search before `DECLARATION.json` and `USED`; the store rebuilt | M `test_no_search_precedes_the_declaration_and_used_by_ledger_or_file_time`, `test_a_store_that_changed…` (only `retrieve` ever reached the fake `gov`: no rebuild call), `test_a_set_that_changed_since_the_declaration_is_ms_digest_and_nothing_is_searched` |
| **F4** the shared servers touched only by their ordinary query calls | M `test_the_shared_servers_are_reached_only_by_the_fake_gov_with_query_calls` (a stub server on a stand-in port, its address passed on in `OLLAMA_HOST` and `GOV_QUERY_OLLAMA_HOST`: its request log holds one query call a search and nothing else), `test_no_module_of_the_measure_names_a_server_address_or_signals_a_process`, `test_the_children_get_the_environment_as_the_fresh_80_ran_it` |
| **F5** nothing outside the ticket's paths | `git diff --name-only 8d87ac134 HEAD` (below) |

Also: the wrapper (F: install, keep, ledger-before-output, passthrough, stderr to a file, four writers one lock), the
ownership rule of ruling 3 (`test_only_the_matcher_imports_the_measures_private_names`), W2-170's tests (green).

## Results (the whole folders, `-m "not local_only" -k "not real and not green_here and not time_limit"`, `HOME` an empty scratch folder)

- `tests/unit/memaudit` and `tests/acceptance/W2-170` together: **392 passed** (390 on the run before the two renames
  below, 2 deselected by the `-k` filter's word "real" in their names, since renamed and run: 38 passed in `test_fault.py`).
  W2-170's own 263 are among them, unchanged.
- The exclusion left out nothing of W2-171's: no test uses `local_only`, a real embedder, reranker or model.

## Readings taken (each also in the return's `unresolved`)

1. **`outcome`'s last line has no trailing comment.** Item 7's hash of `outcome` is of its syntax-tree text, which ends
   at the last statement; `inspect.getsource` carries the comment `# cut before answering, or settled` and hashes
   differently. The copy omits that one comment, so the hash holds by either method (both are tested).
2. **The grader prompt's hash** is of the text with real newlines (the other form, with the two characters `\n`, hashes to
   `8f527b75…`).
3. **A control that did not run as declared** (the measure exited non-zero, a kept search degraded, the kept files not
   the sum of the calls, a missing set) is `STOPPED notready`; a control that ran but shows other than 40 question lines,
   no `families:` line, or a hit@5 more than 2 from the last, is `STOPPED control`.
4. **Printed lines beyond item 8's**: `measure` prints W2-170's `DECLARED`/`USED written` lines, a `CONTROL control-<k>`
   line (with the words `control out of range` when it is), `NOT READY: …`, `FAULT attempt-<n>: <cause>…`, then
   `RETRIEVAL…` last or `STOPPED <cause>` last; `judge` prints only item 8's five lines, then `SEARCH FAILED <n>: <ids>`
   when a later search failed; `pool` prints a `POOL <n> of <size>: …` line and the `POOL REGRESSION …` lines;
   `classes` and `pool-import` one line each.
5. **`search.attempt`** is the control's `k` for a control search, the attempt number for an attempt, null for the probe,
   a later search and the pool.
6. **`POOL.json` `drawn`** is the count of questions measured (the pool's size when it is measured whole).
   `last_hit5` and `last_full` are the earlier audit's counts; the rate of the earlier audit is its own `hit5 / n`.
7. **A pool run that is not whole** (`MS-POOLFAULT`) leaves `POOL.json` with the seed only, so a second `pool` is exit 3.
   Item 4 gives no restart for the pool: this is a gap, named for the CTO.
8. **Files of the audit's own in the pool folder** (`<A>-*`, only a hand-removed `POOL.json` can leave them) are not the
   pool: the run is then measured as the copied set `memory-pool-draw`, whole.
9. **An attempt or control folder that exists** at start is `STOPPED fault` (the closed list has no other word).
10. **A reader that returned nothing twice** (a row with `final_verdict` `error`) counts as not right, is a miss of
    outcome `not_found` and its `answer` is the empty string. A question answered at the third attempt is a miss of
    outcome `not_found` at the A2 cut; its `answer` is the third-attempt answer the grader was shown.
11. **`judge --resume`** compares `--projection` with the figure recorded in `reader/plan.json` (the default `0.157 x n`
    when none is recorded).
12. **`classes`** recomputes the counts when run again (same files, same counts); with no misses and no
    `miss-classes.json` the five counts are zero.
13. **A second judge on the same folder at the same moment** (the lock held) is exit 3.
14. **`not_run`** in `FIGURES.json` is always 0 (`judge` ends only with every row).
