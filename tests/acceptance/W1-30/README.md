# W1-30 Acceptance Tests — `gov close`

Ticket: DAEO-2lwj (W1-30, "gov close"), profile FULL.
Round 5 (see "Round 5" below): containment without exemption, context failures, the repair ticket,
the probe, the time limit. The rule for all of it: nothing is closed, and nothing is recorded, that
was not measured. The counts of the last run are in "Round 5".

```
python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider
```

## How the tests run

- Through public interfaces only: the `gov close` command line (W1-07's console-script
  stand-in), its API-0002 envelope and exit code; `gov check` for the product-traceability
  family check (S3).
- Every project is a temporary git repository (DEC-322): its own `.tickets/`, its own
  commits, its own acceptance tests. No test creates a file in this repository.
- Before `gov close` runs, the project is committed.
- Deterministic, no network.

## Red before implementation

Expected: 27 failed, 88 passed.

The 27 failures are tests for features from owner decisions A2–A7 and items B4–B5
that have not been implemented yet. Each fails for its stated reason (the feature
is absent), not because of a test bug:

- **A2** (regression, timeout): 5 tests — regression not run end-to-end, `--timeout` ignored
- **A3** (disposition argument): 4 tests — `--disposition` not wired, invented names accepted
- **A4** (context failure): 1 test — close succeeds when context is broken
- **A5** (probe verification): 5 tests — probed_commit not checked, reviewer commits undetected
- **A6** (iteration tracking): 5 tests — owner-decision ignored, corrupt count file = zero
- **A7** (governance checks in record): 1 test — check result not recorded in close record
- **B4** (skill versions): 2 tests — kernel/vendor skills not listed
- **B5** (receipt fields): 2 tests — outputs lists only close artifacts, deviations = empty list
- **S2** (escalation options): 2 tests — six options missing, count increment wrong

The 88 passing tests cover the existing `gov close` implementation: basic close
flow, envelope structure, iteration basics, traceability check, probe gate, watchdog,
close record timing, and receipt basics.

## KPI → Test Mapping

### S1: Runs tests, requires trailers, runs containment, writes checkpoint and close record with skill versions
**Covers: CAP-13.a, CAP-24.a, CAP-38.a, CAP-38.c**

| Test | File | Red reason |
|------|------|------------|
| `test_close_returns_api_0002_envelope` | close | NOT_IMPLEMENTED |
| `test_close_succeeds_on_green_standard_ticket` | close | not implemented |
| `test_close_sets_ticket_status` | close | status not set |
| `test_close_runs_acceptance_tests` | close | tests not run |
| `test_close_runs_regression_tests_when_present` | close | regression not run |
| `test_close_requires_implements_trailer` | close | no trailer check |
| `test_close_requires_task_trailer` | close | no trailer check |
| `test_close_runs_containment_check` | close | containment not run |
| `test_close_writes_checkpoint_on_success` | close | no checkpoint |
| `test_close_record_has_kernel_skill_versions` | close | skills not listed |
| `test_close_record_lists_vendor_skill_without_version` | close | vendor skill dropped |
| `test_close_record_empty_skill_versions_when_none` | close | non-empty list |
| `test_close_refuses_when_no_acceptance_tests_exist` | close | passes with no tests |
| `test_close_refuses_when_acceptance_dir_is_empty` | close | passes with empty dir |
| `test_task_trailer_exact_match_not_substring` | close | substring match |
| `test_regression_includes_other_acceptance_folders` | close | other folders skipped |
| `test_regression_runs_to_end_all_failures_collected` | close | stops at first failure |
| `test_collection_error_refuses_close` | close | syntax error ignored |
| `test_regression_failure_blocks_close` | close | regression ignored |
| `test_close_record_lists_test_counts` | close | no test counts |
| `test_time_limit_exceeded_refuses_close` | close | timeout = pass |
| `test_time_limit_is_configurable` | close | --timeout ignored |

### S2: Iteration count, escalation, repair ticket
**Covers: CAP-31.b, CAP-59.a**

| Test | File | Red reason |
|------|------|------------|
| `test_first_failure_records_iteration` | iteration | no state written |
| `test_iteration_count_persists_across_failures` | iteration | not persisted |
| `test_different_failures_still_increment_count` | iteration | different failures reset count |
| `test_successful_close_resets_count` | iteration | not reset on success |
| `test_escalation_after_three_non_converging` | iteration | 4th not blocked |
| `test_escalation_package_lists_outcomes` | iteration | no escalation file |
| `test_escalation_package_has_six_options` | iteration | options missing |
| `test_escalation_includes_reason_not_converging` | iteration | no reason |
| `test_fourth_attempt_runs_nothing` | iteration | 4th writes records |
| `test_owner_decision_resets_count` | iteration | --owner-decision ignored |
| `test_owner_decision_invalid_id_refused` | iteration | invalid id accepted |
| `test_owner_decision_must_be_active` | iteration | DRAFT accepted |
| `test_count_file_unreadable_refuses` | iteration | corrupt file = zero |
| `test_count_file_invalid_json_refuses` | iteration | truncated JSON = zero |
| `test_count_file_wrong_shape_list_refuses` | iteration | list shape accepted |
| `test_count_file_wrong_shape_string_count_refuses` | iteration | string count accepted |
| `test_iteration_file_under_gov_runtime` | iteration | file elsewhere |
| `test_containment_refusal_counts_as_iteration` | iteration | containment not counted |
| `test_mixed_causes_reach_escalation` | iteration | mixed causes not counted |
| `test_each_refusal_opens_repair_ticket` | iteration | no repair ticket on refusal |
| `test_unknown_ticket_does_not_count` | iteration | unknown ticket escalates |
| `test_escalation_already_in_force_not_counted` | iteration | reescalates |
| `test_owner_decision_unapproved_refused` | iteration | unapproved accepted |
| `test_owner_decision_checker_failing_refuses` | iteration | corrupt decision accepted |
| `test_owner_decision_only_when_escalated` | iteration | pre-escalation accepted |
| `test_owner_decision_id_recorded_in_count` | iteration | decision id not recorded |

### S3: Product-traceability family check
**Covers: CAP-38.b**

`test_product_traceability_check_in_family` asserts on the family; its status
depends on all checks in the product-traceability family, not only this ticket's
`product-traceability-trailers` check. All other traceability cases assert on the
`product-traceability-trailers` check entry itself (DEC-425 revision).

| Test | File | Red reason |
|------|------|------------|
| `test_product_traceability_check_in_family` | traceability | not registered |
| `test_check_red_when_closed_ticket_lacks_implements_trailer` | traceability | passes without Implements |
| `test_check_red_when_closed_ticket_lacks_task_trailer` | traceability | passes without Task |
| `test_check_green_when_trailers_present_and_resolve` | traceability | fails with valid trailers |
| `test_check_red_when_implements_does_not_resolve` | traceability | passes with bad Implements |
| `test_traceability_git_failure_is_check_failure` | traceability | git failure = pass |
| `test_traceability_commits_from_head_not_all_branches` | traceability | all branches counted |
| `test_traceability_unreadable_record_store_reported` | traceability | unreadable store = GREEN |
| `test_no_closed_ticket_not_applicable` | traceability | RED with no closed ticket |

### S4: Stale evidence rejected for governance changes
**Covers: CAP-38.d**

| Test | File | Red reason |
|------|------|------------|
| `test_governance_change_reruns_checks` | stale | checks not re-run |
| `test_governance_change_hard_block_red_refuses` | stale | hard-block not refused |
| `test_governance_change_warning_does_not_refuse` | stale | warning refuses |
| `test_governance_change_passing_checks_in_close_record` | stale | result not in record |
| `test_checks_run_at_head` | stale | wrong commit |
| `test_no_governance_change_no_check_needed` | stale | checks run unnecessarily |
| `test_governance_prefix_checks` | stale | prefix not recognized |
| `test_governance_prefix_schemas` | stale | prefix not recognized |
| `test_governance_prefix_project` | stale | prefix not recognized |
| `test_governance_prefix_policies` | stale | policies/ not recognized |
| `test_governance_prefix_roles` | stale | roles/ not recognized |
| `test_governance_change_green_hard_block_closes` | stale | green hard-block refused |
| `test_close_record_states_each_check_status` | stale | check status not in record |
| `test_no_governance_change_no_check_result_in_record` | stale | check result claimed |
| `test_stale_evidence_after_governance_change` | stale | stale evidence accepted |

### S5: Close record is a consumption receipt
**Covers: CAP-50.c**

| Test | File | Red reason |
|------|------|------------|
| `test_close_record_has_packet_hash` | receipt | no packet_hash |
| `test_close_record_has_input_ids_and_hashes` | receipt | no inputs |
| `test_close_record_has_outputs` | receipt | no outputs |
| `test_close_record_has_requirements_implemented` | receipt | no requirements |
| `test_close_record_has_decisions_applied` | receipt | no decisions |
| `test_close_record_has_tests_and_deviations` | receipt | no tests/deviations |
| `test_close_record_packet_hash_matches_context` | receipt | hash mismatch |
| `test_close_refuses_when_context_cannot_be_built` | receipt | close with broken context |
| `test_no_fallback_hash_when_context_fails` | receipt | fallback hash |
| `test_outputs_lists_files_from_ticket_commits` | receipt | outputs empty |
| `test_deviations_says_not_measured_when_unverified` | receipt | says "none" |
| `test_input_hash_is_of_file_content` | receipt | hash of id string |
| `test_unmeasurable_inputs_listed_with_reason` | receipt | no reason |
| `test_ticket_file_is_always_an_input` | receipt | ticket not listed |
| `test_unresolvable_source_listed_with_reason` | receipt | source dropped |
| `test_sources_resolve_through_defined_lookup` | receipt | tree-wide search |
| `test_context_failure_non_cycle_refuses_close` | receipt | superseded source accepted |
| `test_failing_close_with_context_failure_no_context_hash` | receipt | context hash in repair |
| `test_tests_produced_lists_ticket_own_tests` | receipt | other tickets' tests included |

### S6: Finding disposition
**Covers: CAP-59.c**

| Test | File | Red reason |
|------|------|------------|
| `test_no_disposition_records_unclassed` | disposition | auto-classified |
| `test_no_disposition_output_names_findings_awaiting_class` | disposition | no mention of class |
| `test_valid_disposition_records_class` | disposition | class not recorded |
| `test_valid_disposition_builds_context_first` | disposition | no context hash |
| `test_disposition_with_context_failure` | disposition | "context: whole-system" |
| `test_only_six_disposition_names_accepted` | disposition | invented name accepted |
| `test_all_six_dispositions_recognized` | disposition | (unit, always passes) |
| `test_no_context_whole_system_literal` | disposition | literal appears |
| `test_repair_ticket_created_through_ticket_tool` | disposition | no repair ticket |
| `test_repair_ticket_records_findings` | disposition | findings not recorded |
| `test_repair_ticket_has_dependency_on_failing_ticket` | disposition | no dependency |
| `test_repair_ticket_no_invented_id` | disposition | constant id/date |
| `test_repair_ticket_create_failure_reported` | disposition | failure silent |
| `test_repair_ticket_known_to_tk_show` | disposition | tk doesn't know repair |
| `test_repair_ticket_dependency_direction` | disposition | wrong dependency direction |
| `test_tk_fails_no_repair_ticket_file` | disposition | orphan file on tk failure |

### S7: Probe-record gate for FULL tickets
**Covers: CAP-38.f, DEC-137**

| Test | File | Red reason |
|------|------|------------|
| `test_full_ticket_requires_probe_record` | probe | FULL closes without probe |
| `test_full_ticket_closes_with_valid_probe` | probe | valid probe rejected |
| `test_probe_from_non_implementer` | probe | same session accepted |
| `test_probe_reviewer_wrote_nothing_required` | probe | wrote=False accepted |
| `test_standard_profile_closes_without_probe` | probe | STANDARD blocked |
| `test_reviewer_commit_in_ticket_commits_refused` | probe | reviewer commit undetected |
| `test_reviewer_commit_between_probed_and_head_refused` | probe | post-probe reviewer undetected |
| `test_probe_must_name_probed_commit` | probe | missing probed_commit ok |
| `test_probed_commit_must_be_ancestor_of_head` | probe | non-ancestor ok |
| `test_ticket_commit_after_probed_commit_refused` | probe | stale probe accepted |
| `test_reviewer_session_name_not_in_trailers` | probe | session in commit ok |
| `test_probe_missing_reviewer_wrote_nothing_field` | probe | missing field ok |
| `test_probe_requires_commissioned_by_orchestrator` | probe | wrong value ok |
| `test_probe_requires_judged_by_orchestrator` | probe | wrong value ok |
| `test_probe_requires_judgement_present` | probe | missing judgement ok |
| `test_probe_malformed_yaml_is_refused` | probe | malformed YAML skipped |

### F1: Failing acceptance test

| `test_close_refuses_when_acceptance_tests_fail` | close | failing test not caught |

### F2: Fourth non-converging without owner decision

| `test_fourth_non_converging_blocked_without_owner` | iteration | 4th proceeds |

### F3: Iteration count/budget not in output (CAP-59.b)

| Test | File | Red reason |
|------|------|------------|
| `test_iteration_count_not_in_output` | iteration | field exposed |
| `test_budget_not_in_output` | iteration | budget exposed |
| `test_iteration_count_hidden_across_multiple_failures` | iteration | field after N failures |
| `test_escalation_output_to_looping_session_has_no_count` | iteration | outcomes list reveals count |
| `test_escalation_outcome_has_no_iteration_field` | iteration | iteration field in outcome |

### MWA-04: Containment (DEC-453)

| Test | File | Red reason |
|------|------|------------|
| `test_containment_blocks_close_for_out_of_scope_commit` | close | out-of-scope accepted |
| `test_containment_refuses_ticket_changing_acceptance_tests` | close | other acceptance tests accepted |
| `test_containment_refuses_ticket_changing_docs_outside_paths` | close | docs/ accepted |
| `test_containment_clean_within_paths` | close | within-paths refused |

### B1: Watchdog

| Test | File | Red reason |
|------|------|------------|
| `test_close_refuses_on_stale_checkpoint` | watchdog | stale accepted |
| `test_close_refuses_on_missing_checkpoint` | watchdog | missing accepted |
| `test_closing_checkpoint_written_after_checks_pass` | watchdog | no checkpoint |
| `test_any_watchdog_error_refuses_close` | watchdog | non-standard error ignored |
| `test_close_uses_w1_25_thresholds` | watchdog | wrong thresholds |

### B2: Ticket status via ticket tool

| Test | File | Red reason |
|------|------|------------|
| `test_ticket_closed_through_ticket_tool_interface` | close | frontmatter invalid |
| `test_close_record_exists_before_ticket_status_changes` | close | record missing |
| `test_checkpoint_exists_before_ticket_status_changes` | close | checkpoint missing |
| `test_ticket_tool_close_is_what_tk_produces` | close | tk show fails |
| `test_close_fails_when_ticket_tool_absent` | close | absent tk = success |
| `test_close_record_unwritable_ticket_stays_open` | close | ticket closed without record |

### B6: Commits from HEAD only

| Test | File | Red reason |
|------|------|------------|
| `test_ticket_commits_from_head_only` | close | other branches counted |
| `test_git_failure_is_error_not_empty_list` | close | git failure = empty list |

## Round 5

New files: `test_w1_30_containment_places.py`, `test_w1_30_context_failures.py`,
`test_w1_30_repair_ticket.py`, `test_w1_30_probe_commits.py`, `test_w1_30_time_limit.py`.
New cases guard their own fixture first (W1-50's judgement, `gov context`'s error, W1-11's
checker), so none can pass on a project that does not hold what the case is about.

### The projects of this suite, repaired (DEC-453)

Before this round every project of the suite had commits W1-50's judgement flags, and closed
all the same: the ticket was `open`, and the engineer's one commit held the ticket file and
the acceptance tests. Changed for every project (`w1_30_support.py`):

- a ticket is `in_progress` unless the case says otherwise;
- `Project.commit` with the engineer's trailers commits waiting ticket files as the
  orchestrator and waiting acceptance tests as the test designer first, then the rest as
  given; `exact=True` makes one commit as given (a planted violation);
- the first commit holds the ACTIVE decision `DEC-000` every ticket names as its source, and
  `run_close` loads the record store before the close, so the ticket's context can be built;
- `run_close` asks W1-50's public `judge_commits` for the ticket's commits before every
  close and fails the case when the close succeeds while that judgement has findings.

Changed one by one, because the engineer's commit held a file outside the ticket's paths:

| Case | File | What changed |
|------|------|--------------|
| `test_close_runs_regression_tests_when_present` | close | the regression test is the orchestrator's commit |
| `test_close_record_has_kernel_skill_versions` | close | the skills are the orchestrator's commit |
| `test_close_record_lists_vendor_skill_without_version` | close | the skills are the orchestrator's commit |
| `test_time_limit_is_configurable`, `test_time_limit_exceeded_refuses_close` | close | the slow test is the orchestrator's commit |
| `test_containment_refuses_ticket_changing_acceptance_tests` | close | the planted file is one commit made exactly as the engineer |
| every case on `_green_project` | receipt | `DEC-test` is the owner's commit |
| every case on a closed ticket | traceability | the status replaced is `in_progress` |

Removed: `test_failing_close_with_context_failure_no_context_hash` (receipt). Its project's
context could be built, and it asserted on the repair ticket only if one existed. Two cases
in `test_w1_30_context_failures.py` replace it.

### Cases and their sources

| Point | Cases | Source |
|-------|-------|--------|
| The close record cannot be written | `test_close_record_unwritable_ticket_stays_open` (close), rewritten: the place of the record is taken from a twin project's answer; a file stands where the record's folder goes; error answer, exit code 1, ticket file unchanged, no close record | B2; API-0002 (exit code 1) |
| Containment, place by place | `test_w1_30_containment_places.py`: `governance/project/`, a kernel file under `template/`, a test outside the acceptance folder and the paths, the project's root, another ticket's file, a file inside another ticket's paths; one clean ticket that closes | KPI S1; DEC-453; `tests/acceptance/W1-50/README.md` |
| Context failures | `test_w1_30_context_failures.py`: missing source, missing `depends_on` id, superseded source, source superseded by several, contradiction, decision checker cannot run; the answer and the repair ticket of a failing close with a class | KPI S5, S6; DEC-454; DEC-455; `tests/acceptance/W1-24/README.md`; `tests/acceptance/W1-11/README.md` (DEC-387) |
| Repair ticket | `test_w1_30_repair_ticket.py`: tool absent and tool failing (no file written, the answer names the tool beside the finding); the dependency read back with `tk dep tree`, both directions | KPI S2 ("a failure opens a dependent repair ticket"); B2; the project's ticket tool (`tk dep tree`); `tests/acceptance/W1-09/README.md` (a `PATH` without `tk`) |
| Probe | `test_w1_30_probe_commits.py`: the reviewer's commit before the probed commit, with and without a session; after it without a session; git failing for the probed commit | KPI S7; DEC-137; DEC-454 (A5) |
| Time limit | `test_w1_30_time_limit.py`: counted, one dependent repair ticket, escalation at the third, the next blocked | KPI S2; DEC-455 |

The brief for this round names `tests/acceptance/W1-25/README.md` as the context command's
README. W1-25 is `gov checkpoint`; `gov context` is W1-24, and its README is the one used.

### Stale evidence: what the KPI sentence means in a project (CAP-38.d)

"A ticket that changes governance files cannot close on check results recorded for another
commit or inputs hash: gov close re-runs the checks or rejects the stale green evidence."

- Which recorded check results exist. `gov check` is a read command (W1-26 README): its
  answer gives each check's `provenance` (`commit`, `check_version`, `inputs_hash`) and it
  writes no file in the project (observed: no file differs after it). No source names a
  stored check result. The one check result a project keeps is the one `gov close` itself
  writes into the close record of a ticket whose commits changed governance files:
  `check_commit` and `governance_checks` (family statuses).
- So there is no earlier result in a project that a close could lean on. DEC-454 says the
  same from the other side: "re-runs the checks at HEAD through W1-26's runner ... It trusts
  no recorded result."
- What `gov close` must therefore do, measurably: for such a ticket, run the checks at the
  commit being closed, and write into the close record that commit and the statuses that run
  gave; for a ticket that changed no governance file, claim no check result.

Do the present cases measure exactly that? No.

- `test_checks_run_at_head` asserts only inside three nested conditions and passes when none
  holds.
- `test_governance_change_reruns_checks` and the five `test_governance_prefix_*` cases
  accept any answer that is an envelope.
- `test_stale_evidence_after_governance_change` runs `gov check`, changes a check's
  severity, and accepts any refusal. `gov check` recorded nothing, so nothing was stale.
- `test_governance_change_passing_checks_in_close_record`,
  `test_close_record_states_each_check_status`, `test_governance_change_green_hard_block_closes`
  and `test_governance_change_warning_does_not_refuse` need a close that succeeds after a
  governance change; `test_governance_change_hard_block_red_refuses` needs one that is
  refused for a red hard-block check. Both sit on the open question below.

What is missing, and why it is not written this round: the exact case is "the close record
of a ticket that changed governance files names HEAD as `check_commit`, and the status it
records for a check whose result differs between an earlier commit and HEAD is HEAD's". It
needs a close that succeeds after a governance change. In every project this suite can
build, seven hard-block checks are red at closing (below), and DEC-454 says a close refuses
"on any hard-block red". Which red checks refuse a close is with the owner; until that is
answered the case would assert one of two outcomes. No case was written for it.

Fact: the hard-block checks that are red at closing in the projects of
`test_close_record_has_kernel_skill_versions` and
`test_close_record_lists_vendor_skill_without_version` (the same seven in both, read from
`gov check --json` in the project right before the close; exit code 3):

| Check | Family | Reason given |
|-------|--------|--------------|
| `context-reproducibility` | context reproducibility | `unmeasured: no tickets in the store` |
| `fresh-agent-reconstruction` | fresh-agent reconstruction | exited 127, `/bin/sh: 1: gov: not found` (the suite runs `gov` through W1-07's launcher; no `gov` is on `PATH`) |
| `index-freshness` | index freshness | `the lexical index is missing` |
| `retrieval-regression` | retrieval regression | `unmeasured: GOV_DEV_TIERS is not configured` |
| `secrets-indexing` | secrets indexing | exited 1 with a Python traceback; the answer cuts it before the error line |
| `skill-regression-a` | skill regression | `path does not exist: template/governance/kernel/skills/test-design` (kernel case), `.../skills/discovery` (vendor case) |
| `skill-regression-b1` | skill regression | `path does not exist: template/governance/kernel/skills/retrieval` |

Also hard-block and YELLOW there: `audit-reproducibility` (not applicable until the first
audit), `product-traceability-trailers` (no closed ticket), `openspec-validate` (`openspec`
is not on `PATH`). Both projects close with exit code 0. With the skills committed by the
orchestrator (this round's repair) the ticket changed no governance file and the record
holds no check result. With the skills committed by the engineer inside the ticket's paths,
the record holds `check_commit` = HEAD and `governance_checks` with six families RED, and
the close still succeeds.

The fixture `full_project` in `conftest.py` copies the working tree; no case uses it.

### Session models (DEC-460): no case

DEC-460 ("Each session's model is recorded in close records") is in the register of
`w1/integrate`, not yet in this branch's. The sources do not say where a session's model is
recorded:

- `tests/acceptance/W1-50/README.md` has neither "launch" nor "model";
- the launch suite's README (W1-46) describes no launch record that holds a model;
- commits carry `Task`, `Role` and `Co-Authored-By: Claude <model>`, and no session trailer,
  so a commit names a model but no session, and one commit may carry two co-author lines.

No case was written. Recommendation: the launcher writes one launch record per session
(session id, role, ticket, model as given to `--model`), and each commit carries a
`Session:` trailer; `gov close` then lists, for every session among the ticket's commits,
the model from its launch record, and "not measured" where there is none. Until a source
says so, a close record should carry `session_models: not measured` rather than a model
read from `Co-Authored-By`.

### Packages

1. **Session models** (above): where a session's model is recorded.
2. **The store**: `gov context` answers `STORE_MISSING` in a project whose store was never
   loaded (not among the errors W1-24's README lists), and `gov close` closed such a
   project, writing a `packet_hash`. Must `gov close` build the store itself or refuse?
   The suite now loads the store before each close, so no case stands on the answer.
3. **The decision checker being unable to run** is not an error of `gov context` (W1-24's
   README): in a shallow clone the context still builds. The case is written from the brief
   and W1-11's README: the close is refused and the answer says the decisions could not be
   checked.
4. **Exit codes of refusals**: 3 is asserted where the finding is about the ticket's work
   (tests, containment, context, time limit), 1 where the tool could not do its work (the
   close record cannot be written, git fails). For a refusal by the probe gate no source
   gives the code (the implementation answers 1; `test_full_ticket_requires_probe_record`
   accepts 1 or 4); the new probe cases do not assert it.
5. **"Another ticket's file"** is read both ways: the other ticket's file under `.tickets/`
   and a file inside the other ticket's paths. One case each.
6. **B7** ("an unresolvable source is listed with its reason") against DEC-454 and W1-24
   (a missing mandatory input is `BLOCKED`, so the close is refused):
   `test_unresolvable_source_listed_with_reason` (receipt) asserts only if a close record
   exists, and under DEC-454 none may. One of the two has to give way.
7. **Which red checks refuse a close** (with the owner): the facts are in "Stale evidence".
8. **The ticket tool on `PATH`**: `test_close_fails_when_ticket_tool_absent` (close) removes
   the project's script only; a `tk` on the caller's `PATH` is still there. The new cases
   remove both.

### The last run

`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`:
175 cases in 13 files; 159 passed, 16 failed, none skipped. The figures under "Red before
implementation" above are those of an earlier round.

| Red case | File | What `gov close` did |
|----------|------|----------------------|
| `test_an_engineer_commit_under_the_projects_governance_folder_refuses` | containment_places | closed the ticket; W1-50 flags the commit |
| `test_an_engineer_commit_of_a_kernel_file_under_template_refuses` | containment_places | closed the ticket; W1-50 flags the commit |
| `test_an_engineer_commit_of_a_test_outside_its_acceptance_folder_and_paths_refuses` | containment_places | closed the ticket; W1-50 flags the commit |
| `test_an_engineer_commit_of_another_tickets_file_refuses` | containment_places | closed the ticket; W1-50 flags the commit |
| `test_a_missing_mandatory_input_refuses_the_close` | context_failures | closed although `gov context` answers `BLOCKED` |
| `test_a_missing_depends_on_id_refuses_the_close` | context_failures | closed although `gov context` answers `BLOCKED` |
| `test_a_decision_checker_that_cannot_run_refuses_the_close` | context_failures | closed in a shallow clone where W1-11's checker raises |
| `test_the_answer_of_a_failing_close_with_a_class_says_the_context_failed` | context_failures | the answer says "context could not be built" and does not name the record |
| `test_the_repair_ticket_of_a_failing_close_with_a_class_says_the_context_failed` | context_failures | the repair ticket says nothing about the context |
| `test_a_reviewer_commit_before_the_probed_commit_that_names_no_session_refuses` | probe_commits | closed the ticket |
| `test_the_answer_names_the_absent_ticket_tool_beside_the_finding` | repair_ticket | the answer does not say that no repair ticket was opened |
| `test_the_answer_names_the_failing_ticket_tool_beside_the_finding` | repair_ticket | the answer does not say that no repair ticket was opened |
| `test_a_close_over_its_time_limit_is_counted` | time_limit | refused with `TIMEOUT`, count stays 0 |
| `test_a_close_over_its_time_limit_opens_a_dependent_repair_ticket` | time_limit | no repair ticket |
| `test_the_third_close_over_its_time_limit_writes_the_escalation` | time_limit | no escalation |
| `test_after_three_closes_over_their_time_limit_the_next_is_blocked` | time_limit | the fourth is refused with exit code 3, not blocked |

## Covers ids

| Covers id | Tests |
|-----------|-------|
| CAP-13.a | close: envelope, success, checkpoint, containment |
| CAP-24.a | close: kernel/vendor skill versions |
| CAP-31.b | iteration: persistence, reset, escalation |
| CAP-38.a | close: runs tests, refuses on failure, regression |
| CAP-38.b | traceability: 5 tests |
| CAP-38.c | close: Implements, Task trailers |
| CAP-38.d | stale: 10 tests |
| CAP-38.f | probe: 16 tests |
| CAP-50.c | receipt: 16 tests |
| CAP-59.a | iteration: escalation, options, repair, outcomes |
| CAP-59.b | iteration: count/budget hidden (5 tests) |
| CAP-59.c | disposition: 13 tests |
| DEC-137 | probe: reviewer verification (6 A5 tests) |

## Settlements

1. **Disposition argument name**: `--disposition` (value: one of the six DISPOSITIONS names)
2. **Owner decision argument name**: `--owner-decision` (value: decision register id)
3. **Iteration file location**: `.gov-runtime/iterations/<ticket>.json`
4. **Repair ticket dependency direction**: repair ticket depends_on the failing ticket
5. **Governance file prefixes** (A7): `template/governance/kernel/checks/`, `template/governance/kernel/schemas/`, `governance/project/`, `template/governance/kernel/hooks/`, `template/governance/kernel/skills/`, `template/governance/kernel/policies/`, `template/governance/kernel/roles/`
6. **Exit codes**: 0 success, 1 GovError, 3 check failed, 4 blocked
7. **Regression tests**: all under `tests/` except `tests/acceptance/<ticket-wbs>/`
8. **Time limit argument**: `--timeout` (seconds)
9. **Escalation file**: `.gov-runtime/escalations/<ticket>.json`
10. **Probe record probed_commit**: required field naming the commit the probe covers

## Residuals

- **S0a-G-12**: among the ticket's sources; its text is not in the tree. No test is
  derived from unread text.

## Size note

Estimate: 220 LOC. Second-start implementation: 732 LOC. Tests cover the full scope of
A1–A8 and B1–B7; no shrinkage applied.
