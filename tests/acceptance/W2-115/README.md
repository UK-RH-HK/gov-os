# W2-115 acceptance tests: gov close, the smart close (DAEO-emq1)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines, its Interface (DEC-1112 (3))
and the lead's naming for what the Interface leaves open (build run 2's brief), never from the implementation.

## How the suite runs

- **Public interfaces only:** `gov close <ticket> --json`, `gov close --select <ticket>`, `gov close --verify <ticket>
  [--out <dir>]` (W1-07's console-script stand-in, this worktree's `src/` on `PYTHONPATH`), the close record
  `docs/close/<ticket>/CL-<ticket>.md`, the files the close writes, `python3 -m gov.close.batch run <ticket> ...
  --root <project> --json` (W2-68's command) and `python3 -m gov.close.nightly main --root <project> --json` (W2-66's).
- **Planted projects under pytest's `tmp_path`** (`w2_115_support.Smart`), a few files each: a stand-in `gov`
  package that points at this worktree's code (W2-66's form), seven small suites (`W2-aa` the ticket's own, `W2-bb`
  reached by a widget change, `W2-cc` coupled to the shared core in the test map, `W2-dd` reached by nothing,
  `W2-ee` importing the shared core, `W2-rr` the record-reading suite, `W2-ff` a second ticket's), a test map, a path
  map, a nightly record on the base, and `governance/project/close.yaml` (`close: scoped` unless a case says
  otherwise). Nothing is written in this repository's tree.
- **Telling tests:** each planted test appends one JSON line per run to a file of its own outside the project: the
  tree it ran in, what it saw of the watched files (the widget's text says `CHANGED` on the change's side and not on
  the head without it), whether it passed. Run counts "each way" are read from these lines.
- **No model:** every command runs with the embedding endpoint pointed at a dead local address and a stand-in
  program (`quiet_env`, W2-68's form); no case starts an embedder, reranker or model. Deterministic, no network.
- **Session- and module-scoped scenarios** (`conftest.Unowned`, `core_close`, the batches, the clone's two closes)
  share one close among several cases; a scenario that fails is reported as a failure of each case that reads it.
- Run: `env HOME=<empty folder> PYTHONUSERBASE=<the user site's base> PYTHONPATH=<tree>/src python3 -m pytest
  tests/acceptance/W2-115 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real
  and not green_here and not time_limit"` (add `-n 8` for speed). No case is `local_only`; the `-k` filter leaves
  none out. About one minute under `-n 8` on today's code.

## Interface (as used)

From the ticket's Interface and the lead's naming (the brief): the switch `governance/project/close.yaml`
(`close: scoped|strict`; no file runs strict; an unreadable file or another value is refused); the refusal codes
`SELECTION_REFUSED`, `BATCH_UNEXPLAINED`, `CANDIDATE_NOT_ISOLATED`, `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER`,
`FINDING_BLOCKS`; `--select` printing `{"ticket", "suites" (sorted), "pytest_options"}` (exit 0) or
`SELECTION_REFUSED: <reason>` on stderr (exit 2, no set); `--verify` writing `select.json`, `parallel.xml`,
`serial.xml`, `summary.txt`, `verify.exit` (last) in `<dir>` (default `.gov-runtime/close/verify/<ticket>/`), exit
0/1/2/3; the scoped record's keys `close`, `commit`, `selection`, `runs`, `review`, `reds`, `culprits`, `clone`,
`nightly`; a repair ticket in `.tickets/` (`assignee: orchestrator`, the red's node id and failure type in its text);
the reviewer's fenced `verdict` block (JUDGEMENT.md); the warm clone at `.gov-runtime/close/clone/`.

Readings this suite takes where the Interface is silent (each named to the lead as a discovery):

1. **Batch candidates** are tickets whose work waits, unmerged, on branches `w2/<WBS>` made from `main`; the batch is
   W2-68's `run <ticket> ...` command; "landing" is the candidate's work merged into `main` and its ticket closed;
   "going back" is neither. "The rest land on the same run": both close records name the same `commit`.
2. **A load-sensitive case** is an entry of the serial-only list (`tests/acceptance/serial-only.txt`) whose comment
   names the kind `latency` (the path map's `load_sensitive` list may not be read in the scoped close, F2).
3. **The head without the change** of a single ticket's close is the tree before the ticket's commits; the planted
   reds exist there from the initial commit, and the nightly's record on the base names them (`test`,
   `failure_type`).
4. **The reviewer's probe record** is committed by the reviewer (`Role: independent-auditor`, no `Task` trailer),
   as the lead's naming says ("judged from the commit that wrote the probe record"). Today's strict probe gate refuses
   a reviewer's commit in the ticket's range (`PROBE_INVALID`, DEC-137); the scoped close must accept this one.
5. **A killed run** is planted as a test that SIGKILLs its own test run (the xdist controller from a worker, else its
   own process).
6. **The nightly's store rebuild** is observed as a file under the project's `.gov-runtime/` (outside `close/` and
   `nightly/`) written after the nightly began and before its first planted test ran, plus the record's
   `secrets_full_scan: true`.
7. **The green base** (review round 1's F-1, PK-3 (a), td-4) is the commit a green nightly record names (`head`,
   `verdict: green`, under `docs/close/nightly/`); each case plants exactly one such record, so "the newest green
   record" is never in doubt. When it is an ancestor of HEAD, reds are judged against it; otherwise against the
   parent of the ticket's oldest own commit (the oldest commit with `Task: <ticket>`). An honest slip is an
   engineer's commit with `Role: engineer` and no `Task:` trailer. A caused red's refusal names `RED_CAUSED` (the
   brief's code, from F-1; the Interface's code list does not name it). Today's refused close writes no close
   record; the cases ask only that a record, when one is written, marks the red `caused: true` (whether a refused
   scoped close must write its record is put to the lead as a proposed decision, td-4).
8. **A culprit whose red is its own new test** (F-3): the candidate adds the failing test; built without it the test
   does not exist. "Confirmed alone" is a red run of the test on the base plus that candidate only (observed by what
   the test saw: the candidate's change, neither other candidate's). A new test red only beside another
   candidate's change, and still red without either other one, is the existing `BATCH_UNEXPLAINED`.

## KPI map

| KPI id | tests | expected red reason |
|---|---|---|
| S1 the switch: `close: scoped` (a new project's default) or `close: strict` (today's close, every lifted gate built); this repository runs scoped | `test_w2_115_switch.py::test_a_new_project_s_config_holds_close_scoped`, `test_w2_115_switch.py::test_this_repository_s_config_reads_close_scoped`, `test_w2_115_switch.py::test_a_scoped_project_s_close_is_recorded_scoped`, `test_w2_115_switch.py::test_an_unreadable_or_other_setting_is_refused`, `test_w2_115_selection.py::test_the_scoped_close_runs_only_the_selection_and_no_full_suite`, `test_w2_115_strict.py::test_the_strict_close_still_runs_the_full_regression_on_a_shared_core_change` | no `close.yaml` in the template or this repository; today's record has no `close`; today's close ignores an unreadable setting and closes. The strict cases are green by design (today's close is the strict close) |
| S2 the scoped close runs only the selection: own suite and reachable suites, a shared-core change's mapped suites (never the full), records alone the record-reading suites, governance files nothing, an unmapped change refused; no full-suite run recorded | `test_w2_115_selection.py::test_the_ticket_s_own_change_selects_its_suite_and_the_reachable_suites`, `test_w2_115_selection.py::test_a_shared_core_change_selects_its_mapped_suites_never_the_full_suite`, `test_w2_115_selection.py::test_records_alone_select_the_record_reading_suites_and_nothing_else`, `test_w2_115_selection.py::test_governance_files_alone_select_nothing_by_themselves`, `test_w2_115_selection.py::test_a_change_nothing_maps_is_refused_with_its_reason_never_widened`, `test_w2_115_selection.py::test_a_scoped_close_of_a_change_nothing_maps_is_refused`, `test_w2_115_selection.py::test_the_scoped_close_runs_only_the_selection_and_no_full_suite` | `gov close --select` does not exist (argparse: exit 2, a usage line, no `SELECTION_REFUSED`); today's close widens an unmapped change and a shared-core change to the full suite and records no `close`/`runs` |
| S3 one selection command: `--select` prints the set the close runs | `test_w2_115_selection.py::test_select_prints_the_set_the_close_runs` | `--select` does not exist (exit 2) |
| S4 every failing test run again alone; judged against the head without the change, one run each way; same failure type only; nightly read first; no nightly-baseline clone; 3 rounds only for load-sensitive cases; a timeout or no record never matches | `test_w2_115_reds.py::test_an_unowned_red_does_not_refuse_the_scoped_close`, `test_w2_115_reds.py::test_every_failing_test_is_run_again_alone_and_once_on_the_head_without_the_change`, `test_w2_115_reds.py::test_only_the_load_sensitive_case_gets_three_rounds`, `test_w2_115_reds.py::test_the_nightly_s_recorded_result_is_read_first`, `test_w2_115_reds.py::test_no_clone_is_built_for_the_nightly_baseline`, `test_w2_115_reds.py::test_a_red_the_head_without_the_change_does_not_have_refuses_the_close`, `test_w2_115_reds.py::test_a_red_with_another_failure_type_on_the_head_without_the_change_is_the_change_s`, `test_w2_115_reds.py::test_a_timeout_never_matches`, `test_w2_115_reds.py::test_a_failing_test_the_ticket_added_has_no_record_and_never_matches`; F-1 (td-4): `test_w2_115_reds.py::test_a_red_an_untrailered_commit_after_the_green_base_caused_is_never_excused`, `test_w2_115_reds.py::test_a_red_a_trailered_commit_after_a_green_untrailered_one_caused_is_refused`, `test_w2_115_reds.py::test_with_the_green_base_not_an_ancestor_a_red_the_parent_has_is_not_the_change_s`, `test_w2_115_reds.py::test_with_the_green_base_not_an_ancestor_a_red_the_parent_does_not_have_is_the_change_s` | today's close refuses every red (`CHECK_FAILED`) and runs a failing test once: no run alone, none on the head without the change (the caused-red cases fail on "was not run again alone: 1 run(s)"). F-1 at 1a3664a20: the untrailered-commit case fails on "the command was not refused" (the close judges against the untrailered commit, where the red already is, and closes); the other three are controls, green |
| S5 an unowned red named in the record and opened as a repair ticket for the orchestrator; no list read or written | `test_w2_115_reds.py::test_an_unowned_red_is_named_in_the_record_and_opened_as_a_repair_ticket_for_the_orchestrator`, `test_w2_115_reds.py::test_no_accepted_reds_or_load_sensitive_list_is_written` | today's close refuses the unowned red (`CHECK_FAILED`): no close record, no `reds` |
| S6 a batch's culprit found by building without each candidate; only culprits go back, the rest land on the same run; an unexplained red or a candidate that cannot be isolated refuses; nothing lands before | `test_w2_115_batch.py::test_only_the_culprit_goes_back`, `test_w2_115_batch.py::test_the_rest_land_on_the_same_run`, `test_w2_115_batch.py::test_the_build_without_the_culprit_is_green`, `test_w2_115_batch.py::test_the_culprit_is_named_and_nothing_landed_before_it_was_found`, `test_w2_115_batch.py::test_a_red_no_single_candidate_explains_refuses_the_batch`, `test_w2_115_batch.py::test_a_candidate_that_cannot_be_isolated_refuses_the_batch`; F-3 (td-4): `test_w2_115_batch.py::test_a_culprit_whose_red_is_its_own_new_test_goes_back_and_the_rest_land`, `test_w2_115_batch.py::test_a_culprit_s_own_new_test_is_confirmed_red_with_that_candidate_alone`, `test_w2_115_batch.py::test_nothing_landed_before_the_culprit_with_its_own_new_test_was_found`, `test_w2_115_batch.py::test_a_new_test_green_with_its_candidate_alone_is_not_blamed_and_the_batch_is_refused` | today's batch closes tickets already on `main` (`BATCH_CLOSE_REFUSED` … `TRAILER_MISSING` here): it lands no branch, builds nothing without a candidate, names no culprit, `BATCH_UNEXPLAINED` or `CANDIDATE_NOT_ISOLATED`. F-3 at 1a3664a20: the three own-new-test cases fail on `BATCH_UNEXPLAINED` ("1 red(s) no single candidate explains: …test_w2_115_added; nothing lands"; no run on the base plus A alone); the beside-others case is a control, green |
| S7 each close writes its record (commit, runs and counts, review verdict, every red with its reason, culprits); a missing field fails | `test_w2_115_record.py::test_the_close_record_holds_every_field`, `test_w2_115_record.py::test_the_record_names_the_commit_closed`, `test_w2_115_record.py::test_the_record_names_the_runs_and_their_counts`, `test_w2_115_record.py::test_the_record_names_the_review_s_verdict`, `test_w2_115_record.py::test_the_record_names_each_red_with_its_reason`, `test_w2_115_record.py::test_the_record_names_the_culprits_sent_back`, `test_w2_115_record.py::test_the_record_names_the_clone_and_the_nightly_read` | today's close refuses the planted unowned reds, so no record ("no close record to read: the close did not pass"); today's record lacks every key of the list |
| S8 the nightly rebuilds its stores with `GOV_SECRETS_FULL_SCAN=1` before its run; its record says so | `test_w2_115_nightly.py::test_the_nightly_rebuilds_the_stores_with_the_full_secrets_scan_before_its_run` | today's nightly record has no `secrets_full_scan` |
| S9 measured: `close_build.py` and this close give the same verdict on three recorded batches (clean, caused red, unowned red) | `test_w2_115_research.py::test_the_research_record_compares_both_verdicts_on_three_recorded_batches` | `docs/research/W2-115-smart-close.md` does not exist |
| S10 the warm clone kept between closes (reset, stores kept), replaced when it cannot be reset; the record says so | `test_w2_115_clone.py::test_the_first_close_keeps_its_clone_at_the_named_place`, `test_w2_115_clone.py::test_the_second_close_reuses_the_first_s_clone_reset_with_its_stores_kept`, `test_w2_115_clone.py::test_a_clone_that_cannot_be_reset_is_replaced_and_the_record_says_so` | today's close refuses the planted red (`CHECK_FAILED`) and keeps no clone at `.gov-runtime/close/clone` |
| S11 READY computed from the reviewer's structured verdict; refuses only an in-scope, ordinary, fails-open or loses-work finding; malformed or incomplete refuses; a lead's verdict over the reviewer's refused | `test_w2_115_verdict.py::test_a_complete_verdict_with_only_harmless_findings_is_ready`, `test_w2_115_verdict.py::test_an_in_scope_ordinary_finding_that_fails_open_or_loses_work_refuses`, `test_w2_115_verdict.py::test_a_malformed_or_incomplete_verdict_refuses`, `test_w2_115_verdict.py::test_a_verdict_the_lead_wrote_over_the_reviewer_s_is_refused` | today's close refuses the reviewer's probe commit (`PROBE_INVALID`) and reads no verdict block: no `FINDING_BLOCKS`, `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER`, no `review` in a record |
| S12 the trailers switch (`product-traceability-trailers` as a warning) | **none**: the line changes a kernel check file and waits for its CIT-P (`docs/changes/W2-115-CIT-P.md`), its independent review and the owner's approval (CAP-33; the ticket's "Delegated" P4). Its tests are written in that later round. | — |
| S13 `gov close --verify`: selection, parallel then serial phase, `select.json`, one JUnit file per phase, one summary line, exit file last; exit 0/1/2/3 | `test_w2_115_verify.py::test_a_red_and_a_serial_entry_exit_1_with_both_junit_files_and_the_summary`, `test_w2_115_verify.py::test_a_green_verify_exits_0_in_the_default_folder`, `test_w2_115_verify.py::test_a_refused_selection_exits_2`, `test_w2_115_verify.py::test_a_killed_run_exits_3` | `gov close --verify` does not exist (argparse: exit 2, no files) |
| F1 a scoped close refused by a red its change did not cause, or closed with one it caused | `test_w2_115_reds.py::test_an_unowned_red_does_not_refuse_the_scoped_close`, `test_w2_115_reds.py::test_a_red_the_head_without_the_change_does_not_have_refuses_the_close`, `test_w2_115_reds.py::test_a_red_an_untrailered_commit_after_the_green_base_caused_is_never_excused`, `test_w2_115_reds.py::test_with_the_green_base_not_an_ancestor_a_red_the_parent_has_is_not_the_change_s`, `test_w2_115_reds.py::test_with_the_green_base_not_an_ancestor_a_red_the_parent_does_not_have_is_the_change_s` | today's close refuses the unowned red (`CHECK_FAILED`); the caused case fails on "was not run again alone". F-1: as S4 |
| F2 a scoped close that runs the full suite or reads or writes an accepted-reds or load-sensitive list | `test_w2_115_selection.py::test_the_scoped_close_runs_only_the_selection_and_no_full_suite`, `test_w2_115_selection.py::test_a_shared_core_change_selects_its_mapped_suites_never_the_full_suite`, `test_w2_115_reds.py::test_no_accepted_reds_or_load_sensitive_list_is_written` | today's close widens a shared-core change to the full suite and records no `close`; `--select` does not exist; today's close refuses the unowned reds |
| F3 a batch that closes a culprit, or closes the rest when a red is unexplained | `test_w2_115_batch.py::test_only_the_culprit_goes_back`, `test_w2_115_batch.py::test_a_red_no_single_candidate_explains_refuses_the_batch`, `test_w2_115_batch.py::test_a_culprit_whose_red_is_its_own_new_test_goes_back_and_the_rest_land`, `test_w2_115_batch.py::test_a_new_test_green_with_its_candidate_alone_is_not_blamed_and_the_batch_is_refused` | as S6 |
| F4 the strict close changed in any verdict | `test_w2_115_strict.py::test_the_strict_close_gives_the_recorded_verdict`, `test_w2_115_strict.py::test_the_strict_close_still_runs_the_full_regression_on_a_shared_core_change`; and the strict close's own suites, unchanged: `tests/acceptance/W1-30/` and `tests/acceptance/W2-07/` | green by design on today's code: the recorded verdicts (`RECORDED` in the file) are today's answers on the same planted cases, run at f4f9c3204 |

## Not tested here

- S12 (above). The lifted lines (former S12 to S15) and the queue lines moved to W2-115b (DAEO-j9z6).
- Whether each phase of `--verify` takes a heavy-job slot (`gov.resources`): not observable from outside without
  reading the slot's internals; the verify's files and exit codes are tested.
- A real model, embedder or reranker: none is started.
