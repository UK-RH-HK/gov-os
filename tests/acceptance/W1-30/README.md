# W1-30 Acceptance Tests — `gov close`

Ticket: DAEO-2lwj (W1-30, "gov close"), profile FULL.
Round 5 (see "Round 5" below): containment without exemption, context failures, the repair ticket,
the probe, the time limit. Round 5b (see "Round 5b"): the four points DEC-470 decides. The rule for
all of it: nothing is closed, and nothing is recorded, that was not measured. Round 6 (see
"Round 6"): the suite's sandbox, the governance checks of a close under DEC-476, stale evidence,
a ticket without acceptance tests. Round 6b (see "Round 6b"): DEC-480, `gov close` refuses on
what `gov check` blocks on. Round 7 (see "Round 7"): the blocking state without a red hard-block
check. Round 8 (see "Round 8"): DEC-487, the findings of the review of `gov close`. The counts of
the last run are in "Round 8".

```
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs
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
| `test_a_ticket_without_acceptance_tests_is_refused_and_nothing_is_closed` (2 forms) | no_acceptance_tests | passes with no tests (round 6: replaces the two cases of `close`) |
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

The fifteen cases of earlier rounds are replaced in round 6 by the 21 cases of
`test_w1_30_governance_checks.py` and the 5 of `test_w1_30_stale.py`; the table of what replaced
what is in "Round 6".

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

Round 6 replaces the cases named below; DEC-476 answered the open question. What follows is
the finding of round 5, kept as written.

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

### Packages of round 5

Eight points were returned with round 5. DEC-470 decides four (the store, a missing source,
the probe gate's exit code, session models); two were tightenings of this suite (the ticket
tool on `PATH`, the unused fixture). All six are in "Round 5b". Two stay as they were:

- **The decision checker being unable to run** is not an error of `gov context` (W1-24's
  README): in a shallow clone the context still builds. The case is written from the brief
  and W1-11's README: the close is refused and the answer says the decisions could not be
  checked.
- **Which red checks refuse a close** is with the owner: no case. The facts are in "Stale
  evidence".

## Round 5b (DEC-470)

DEC-470 is in the register of the main tree (section 118), not yet in this branch's. New file:
`test_w1_30_commit_models.py`.

| Point of DEC-470 | Cases | What they hold |
|------------------|-------|----------------|
| No record store | context_failures: `test_a_project_without_a_record_store_refuses_the_close`, `test_a_refusal_for_no_record_store_is_counted`, `test_a_refusal_for_no_record_store_carries_no_hash`, `test_the_close_does_not_build_the_record_store`, `test_the_same_project_closes_once_it_has_a_record_store` | each first holds that `gov context` answers `STORE_MISSING`; the close is refused with exit code 3, the answer says the context failed and gives that reason, no close record, the ticket in progress, one iteration counted, no hash in the answer; afterwards `gov context` still answers `STORE_MISSING`; with the store loaded the same ticket closes |
| A missing source | receipt: `test_unresolvable_source_refuses_the_close` (was `test_unresolvable_source_listed_with_reason`) | holds first that `gov context` answers `BLOCKED`; refused with exit code 3, the answer names the source, no close record, the ticket in progress |
| The probe gate's exit code | probe: the 14 refusal cases; probe_commits: the three cases of the reviewer's commit | exit code 3. `test_full_ticket_requires_probe_record` no longer accepts 1 or 4 |
| Session models | commit_models: `test_commits_of_two_roles_are_listed_with_their_roles_and_models`, `test_no_commit_of_the_ticket_is_left_out_and_no_other_is_listed`, `test_a_commit_without_a_co_author_line_is_listed_as_not_measured`, `test_a_commit_with_a_co_author_line_beside_one_without_keeps_its_model` | the close record lists each of the ticket's commits once with its role and the model its `Co-Authored-By` line names; "not measured" for a commit without the line |

**Must the fixtures give the projects a store? Yes.** Under DEC-470 a project without a
record store cannot close, and `gov close` does not build one. Every case that expects a
close, or a refusal for another reason, therefore needs the store before the close. The suite
already does it in one place: `support.run_close` calls `gov.store.load` on the project before
each close (round 5), and no case reaches `gov close` by another way. The cases that load the
store themselves pass `store=False`. Only the four no-store cases close without one. Nothing
else had to change.

**The git failure in the probe gate keeps exit code 1**
(`test_a_git_failure_while_the_probes_commits_are_read_refuses`): DEC-470 gives 3 to a
refusal that is a finding about the ticket's work; git failing is the tool unable to work
(API-0002, B6).

**A malformed probe file** (`test_probe_malformed_yaml_is_refused`) is read as a refusal by
the probe gate: the ticket has no valid probe record. Exit code 3.

**Session models: what is settled here** (settlement 11). DEC-470 names the content, not the
shape. The cases read one list in the close record's frontmatter whose entries each hold
`commit`, `role` and `model`; the list's name is the implementation's. "Exactly as read" is
the name written in the line (`Claude Opus 4.6 (1M context)`), unchanged; the whole value of
the line with the address is accepted too. A commit with two co-author lines has no case:
DEC-470 does not say which is read.

**Tightened or removed:**

- `test_close_fails_when_ticket_tool_absent` (close): the project's script is removed and
  `PATH` holds no `tk`; the ticket stays in progress.
- The fixture `full_project` and the class `FullProject` are removed, with the `copy_tree`
  argument of `Project`. The fixture `built` asks its question in a minimal project, so the
  suite no longer copies the working tree anywhere.

### The last run

`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`:
184 cases in 14 files; 144 passed, 40 failed, none skipped. The figures under "Red before
implementation" above are those of an earlier round.

Red since round 5, unchanged (16): the four of containment_places, five of context_failures
(missing input, missing `depends_on` id, decision checker, the answer and the repair ticket of
a failing close with a class), the two of repair_ticket, the four of time_limit, and
`test_a_reviewer_commit_before_the_probed_commit_that_names_no_session_refuses`
(probe_commits; it closes the ticket).

Red from this round (24):

| Red case | File | What `gov close` did |
|----------|------|----------------------|
| `test_a_project_without_a_record_store_refuses_the_close` | context_failures | closed the ticket without a store |
| `test_a_refusal_for_no_record_store_is_counted` | context_failures | closed the ticket without a store |
| `test_a_refusal_for_no_record_store_carries_no_hash` | context_failures | closed the ticket without a store |
| `test_the_close_does_not_build_the_record_store` | context_failures | closed the ticket without a store |
| `test_unresolvable_source_refuses_the_close` | receipt | closed although `gov context` answers `BLOCKED` |
| 13 refusal cases (all but `test_reviewer_commit_in_ticket_commits_refused`) | probe | refused with `PROBE_INVALID` and exit code 1, not 3 |
| `test_a_reviewer_commit_before_the_probed_commit_refuses`, `test_a_reviewer_commit_after_the_probed_commit_that_names_no_session_refuses` | probe_commits | refused with `PROBE_INVALID` and exit code 1, not 3 |
| the four cases | commit_models | closed; the close record holds no list of commits with role and model |

Green from this round: `test_the_same_project_closes_once_it_has_a_record_store`,
`test_close_fails_when_ticket_tool_absent`.

## Round 6 (DEC-476)

DEC-476 is in the register of the main tree (section 120), not yet in this branch's: "`gov close`
holds no baseline: it stays strict for every project." New files:
`test_w1_30_governance_checks.py`, `test_w1_30_no_acceptance_tests.py`,
`test_w1_30_test_runner.py`; `test_w1_30_stale.py` is rewritten.

### The sandbox

Every process the suite starts gets one environment, `support.sandbox_env`: W1-07's stand-in
environment (the sandbox's own `HOME`, `TMPDIR` and bytecode folder, `src/` on `PYTHONPATH`,
the caller's `PATH`) and one more variable.

- **The means.** Of everything an interpreter imports, only its per-user folder is found
  through `HOME`. The suite replaces `HOME`, so the interpreter a case starts, and the one
  `gov close` starts for the tests, lost the packages installed there (on the machine of this
  round: pytest). The interpreter running the suite is asked where its per-user folder is
  (`site.getuserbase()`), and the answer is passed as `PYTHONUSERBASE`. Nothing of one machine
  is written in a case. Where the running interpreter uses no per-user folder (a virtual
  environment), nothing is set.
- **Everything else stays the sandbox's**: `HOME` is still the sandbox's folder, so settings,
  git configuration and caches of the user are not read.
- **Held once per run**: the fixture `built` asks the interpreter the cases start whether it
  finds `pytest` and `yaml` in that environment, and fails every case with that reason if not.
- `Project.gov` runs through `support.run_gov`, which does what W1-07's
  `run_gov_with_code` does, in that environment. W1-07's file is not changed.
- **No pytest reachable** (`test_w1_30_test_runner.py`, one case): the answer is
  `TEST_RUNNER_ABSENT` with exit code 1 (API-0002: the tool cannot work; it is no finding about
  the ticket's work), the ticket stays in progress, no close record. The interpreter of that
  case is a virtual environment without packages (`venv`, no pip, no system packages), so it
  sees no folder of installed packages wherever pytest lies on a machine; each such folder of
  the running interpreter is given back on `PYTHONPATH` as a folder of links to everything in
  it except pytest. The case holds first that this interpreter finds `yaml` and no `pytest`.

After this change alone, before any case of the points below: 185 cases, 185 passed, none
failed, none skipped (round 5b's 184 and the new case).

### Which paths are governance files

Revised in round 8: DEC-487 adds the installed kernel, `governance/kernel/`, as the eighth prefix
(see "Round 8", point 12). What follows is round 6's text.

Settlement 5, unchanged, seven prefixes. Sources: the brief of the third start (A7) names five
"at least" (`template/governance/kernel/checks/`, `.../schemas/`, `governance/project/`,
`.../hooks/`, `.../skills/`) and leaves the exact set to the designer; round 4 added
`.../policies/` and `.../roles/` (its cases cite DEC-454). DEC-454 and DEC-476 say "governance
files" without a list in the register's text; no source names another path, and none takes
one of the seven away. One case per prefix
(`test_a_change_under_each_governance_prefix_has_the_checks_run`).

### How a case's project declares its checks

`gov check` runs the declarations in the project's `template/governance/kernel/checks/`
(W1-26). Until now every project of the suite held a copy of the kernel's seventeen, seven of
which are red in a test project for reasons of the test project (round 5). The projects of the
governance cases hold none of them: `project_with_checks(check, ...)` writes the project's own
declarations into its first commit (`support.declared_check`). Each command measures the
project itself (`test -s README.md`; `grep -qx 'mode: strict' governance/project/settings.yaml`;
`test -s LICENSE`), so a green check is green because the project is so, and a red one because
it is not. No case tolerates a red check.

Three checks are built into the runner and run in every project: `readiness` and
`skill-version` are GREEN in these projects; `openspec-validate` (hard-block) is YELLOW,
"openspec is not on PATH", as in W1-26's suite, which has no `openspec` tool either. YELLOW is
not red: DEC-454 refuses "on any hard-block red". The green-path cases hold first that no
hard-block check is RED and that the project's own hard-block checks are GREEN. DEC-480 decides
it: "A hard-block check the runner reports yellow (not applicable, or a built-in check whose
tool is absent) refuses nothing. Whether the runner should report an absent tool of a
hard-block check as red is a question for W1-26, listed for the Wave 2 list of DEC-466."

Every case asks W1-26's runner (`gov check --json`) for the state right before the close and
fails there if the project is not what the case is about.

### Cases and their sources

| Point | Cases | Source |
|-------|-------|--------|
| 1. Any red hard-block check refuses, named | governance_checks: `test_a_red_hard_block_check_the_ticket_declared_refuses_the_close`; `..._the_ticket_did_not_touch_refuses_the_close` (the check is red from the project's first commit; the ticket adds another declaration); `test_a_red_hard_block_check_refuses_a_ticket_whose_governance_change_declares_no_check` (the ticket changes `governance/project/notes.yaml`). Exit code 3, the answer names the check, nothing closed | DEC-454 ("refuses on any hard-block red"); DEC-476 (no baseline, strict for every project); DEC-470 (exit code 3 for a finding) |
| 1. A failing warning refuses nothing | `test_a_failing_check_of_severity_warning_refuses_nothing` | W1-26 README ("warnings alone do not block"); DEC-454 |
| 1. The refusal is a finding | `test_a_refusal_for_a_red_check_is_counted`, `test_a_refusal_for_a_red_check_opens_a_dependent_repair_ticket` | DEC-455 ("the governance checks"); KPI S2 |
| 2. The green path | `test_a_governance_changing_ticket_closes_when_no_hard_block_check_is_red`; `test_the_close_record_names_the_commit_being_closed` (it is not the commit that changed the file); `test_the_close_record_states_every_checks_status_as_run_at_that_commit` (equal to the runner's answer, check by check, a YELLOW warning among them); seven prefix cases | DEC-454; the brief of the third start (A7: "The close record states the commit and the result") |
| 3. No governance file changed | `test_a_ticket_that_changes_no_governance_file_needs_no_check_result` (the project holds a red hard-block check and the ticket closes), `test_the_close_record_of_a_ticket_that_changes_no_governance_file_claims_no_check_result` | DEC-454 ("when a ticket's commits change governance files"); A7 ("no check result is needed and none is claimed") |
| 4. Stale evidence | stale: five cases, below | KPI S4; DEC-454; "Stale evidence" above |
| 5. A check that cannot run | `test_a_hard_block_check_whose_command_is_absent_refuses_the_close`: exit code 3, the answer names the check and the absent command, nothing closed. `test_a_warning_check_whose_command_is_absent_refuses_nothing` (round 6b): the ticket closes and the close record states the check's status as the runner gave it. No case for a check over its time limit (round 6b, below) | DEC-480; DEC-454; DEC-455 |
| 6. No acceptance tests | no_acceptance_tests: three cases in two forms (no folder; a folder without a test) | below |

**Stale evidence, measured exactly.** The statement of round 5 stands: W1-26's runner writes
nothing into the project, so a close can stand only on its own run at the commit being closed.
The green evidence of each case is the runner's own answer, with the commit in its `provenance`.

| Case | What it holds |
|------|---------------|
| `test_a_check_green_at_an_earlier_commit_and_red_at_the_commit_being_closed_refuses` | the runner says GREEN at the ticket's first commit; the second commit makes the check red; refused, the check named |
| `test_a_check_red_at_an_earlier_commit_and_green_at_the_commit_being_closed_closes` | the other direction: an earlier red refuses nothing |
| `test_the_close_record_states_the_status_of_the_commit_being_closed_not_an_earlier_one` | the record names HEAD and GREEN for that check |
| `test_a_check_green_at_this_commit_before_what_it_reads_changed_refuses` | the same commit, other inputs: the check reads a file git ignores; the runner says GREEN, the file changes, HEAD and `git status` do not; refused, the check named |
| `test_a_declaration_changed_in_two_commits_and_green_at_the_commit_being_closed_closes` | no source gives a rule about how often a governance file changed in the ticket's commits; green at closing closes |

On "inputs hash": the runner's `inputs_hash` of the check in the fourth case is the same before
and after the ignored file changed (observed), so the case is named by what happened, not by
that field. What a close does with a tracked file changed and not committed has no source and
no case: the suite commits the project before every close.

**A warning check that cannot run.** W1-26's runner gives a warning check whose command is
absent the same YELLOW as one that ran and failed. Round 6 wrote the case to a refusal, on the
round's order alone ("never a close", without a severity). DEC-480 reverses it: "A check of
severity warning refuses nothing, whether it ran and failed or could not run: the runner gives
both the same status, and `gov close` does not read more into it." The case is now
`test_a_warning_check_whose_command_is_absent_refuses_nothing` (see "Round 6b").

**A ticket without acceptance tests is a finding about the ticket's work.** DEC-455 counts "a
close refused for a finding about the ticket's work" and names what it leaves uncounted: the
ticket unknown, the arguments invalid, the ticket already closed, the escalation in force, the
count file corrupt. All of those are states of the call or of the count. A ticket without an
acceptance test is none of them, and it is not in the counted list by name either. The
sources decide it this way: the acceptance tests are part of the ticket (its file names their
folder and author; MR-3, DEC-069; KPI S1 "runs tests/acceptance/<ticket>/"), work on the ticket
repairs their absence, and DEC-455's heading is "every refusal for a finding counts". So:
exit code 3, counted, one dependent repair ticket. An absent test runner is the other kind:
the machine's state, exit code 1, not a finding.

### Replaced or removed

| Earlier case | File | Now |
|--------------|------|-----|
| `test_governance_change_reruns_checks`, the five `test_governance_prefix_*` (accepted any envelope) | stale | `test_a_change_under_each_governance_prefix_has_the_checks_run`, seven prefixes: the ticket closes and the record names HEAD |
| `test_governance_change_hard_block_red_refuses` (accepted "hard" in place of the check's name) | stale | the three refusal cases of point 1 |
| `test_governance_change_warning_does_not_refuse` | stale | `test_a_failing_check_of_severity_warning_refuses_nothing` |
| `test_governance_change_green_hard_block_closes` | stale | `test_a_governance_changing_ticket_closes_when_no_hard_block_check_is_red` |
| `test_checks_run_at_head` (asserted inside three conditions) | stale | `test_the_close_record_names_the_commit_being_closed` |
| `test_governance_change_passing_checks_in_close_record`, `test_close_record_states_each_check_status` (asserted only if the close succeeded) | stale | `test_the_close_record_states_every_checks_status_as_run_at_that_commit` |
| `test_no_governance_change_no_check_needed`, `test_no_governance_change_no_check_result_in_record` | stale | the two cases of point 3 |
| `test_stale_evidence_after_governance_change` (accepted any refusal; nothing was stale) | stale | the five cases of `test_w1_30_stale.py`; its project now closes (`..._changed_in_two_commits_...`) |
| `test_close_refuses_when_no_acceptance_tests_exist`, `test_close_refuses_when_acceptance_dir_is_empty` (no checkpoint, any refusal accepted) | close | `test_w1_30_no_acceptance_tests.py` |

### The run of round 6

Superseded by "Round 6b", "The last run".
`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`:
200 cases in 17 files; 186 passed, 14 failed, none skipped.

| Red case | File | What `gov close` did |
|----------|------|----------------------|
| `test_a_red_hard_block_check_the_ticket_did_not_touch_refuses_the_close` | governance_checks | closed the ticket; `license-present` is red |
| `test_a_red_hard_block_check_refuses_a_ticket_whose_governance_change_declares_no_check` | governance_checks | closed the ticket; `license-present` is red |
| `test_a_refusal_for_a_red_check_is_counted` | governance_checks | closed the ticket |
| `test_a_refusal_for_a_red_check_opens_a_dependent_repair_ticket` | governance_checks | closed the ticket |
| `test_a_hard_block_check_whose_command_is_absent_refuses_the_close` | governance_checks | closed the ticket; `tool-absent` is red |
| `test_a_warning_check_whose_command_is_absent_refuses_the_close` | governance_checks | closed the ticket |
| `test_a_check_over_its_time_limit_refuses_the_close` | governance_checks | did not end within the 30 s the suite gives a command (`--timeout 8`, a check that sleeps 120 s) |
| `test_a_check_green_at_an_earlier_commit_and_red_at_the_commit_being_closed_refuses` | stale | closed the ticket; `settings-strict` is red at HEAD |
| `test_a_check_green_at_this_commit_before_what_it_reads_changed_refuses` | stale | closed the ticket; `not-in-maintenance` is red |
| `test_a_declaration_changed_in_two_commits_and_green_at_the_commit_being_closed_closes` | stale | refused: "governance evidence is stale: feature-present changed after evidence was collected" |
| `test_a_refusal_for_no_acceptance_tests_is_counted` (2 forms) | no_acceptance_tests | refused with `NO_ACCEPTANCE_TESTS`, exit code 3; no iteration counted |
| `test_a_refusal_for_no_acceptance_tests_opens_a_dependent_repair_ticket` (2 forms) | no_acceptance_tests | refused; no repair ticket |

Green among the new cases: the check the ticket declared itself and that is red refuses; the
failing warning refuses nothing; the green path with the commit and every status in the
record; the seven prefixes; the two cases without a governance change; an earlier red that is
green at closing; a ticket without acceptance tests is refused with nothing closed; no test
runner.

## Round 6b (DEC-480)

DEC-480 is in the register of the main tree (section 122), not yet in this branch's: "For a
governance-changing ticket, `gov close` refuses on exactly the checks `gov check` reports red at
hard-block; it holds no rule of its own about checks." W1-26's runner is the authority on a
check's status. Two cases change, in `test_w1_30_governance_checks.py`; nothing else does.

| Point of DEC-480 | Case | Change |
|------------------|------|--------|
| "A check of severity warning refuses nothing, whether it ran and failed or could not run" | `test_a_warning_check_whose_command_is_absent_refuses_nothing` | reversed (was `..._refuses_the_close`): the fixture holds that no hard-block check is red and that the runner does not give the check GREEN; the ticket closes; the close record states for that check the status the runner gave |
| "The time limit of a check is the runner's own; `gov close` adds none, and its `--timeout` stays the limit of its test runs" | `test_a_check_over_its_time_limit_refuses_the_close` | removed, with its declaration (`sleep 120`) and its `--timeout 8`; no case replaces it, see below |
| "A hard-block check the runner reports yellow ... refuses nothing" | `test_a_governance_changing_ticket_closes_when_no_hard_block_check_is_red` | unchanged (no hard-block check red; the project's own hard-block checks green); the sentence is quoted in "How a case's project declares its checks" |

**No case for a hard-block check over the runner's time limit.** DEC-480 says such a check
refuses "when the runner reports it red, as the runner does today". A case needs the runner's
limit to be reached within the 30 s this suite gives a command. No source states a means:
`tests/acceptance/W1-26/README.md` names no time limit of a check and no key, argument or
variable by which a project sets one (its declaration fields are `id`, `family`, `tier`,
`severity`, `command`, `allows-not-applicable`); W1-26's cases time nothing but their own calls
(60 s and 30 s). The runner's code holds the limit as a constant of 60 s
(`src/gov/check/runner.py`), which no project can change and which is twice this suite's own
limit. A case would wait a minute and rest on a number no source gives, so none is written. The
point is returned as a package: either W1-26 states the limit and a way for a project to set
it (then the case is one declaration with a short limit and a command that sleeps longer), or
the point stays without a case in this suite.

### The last run

`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`:
199 cases in 17 files; 187 passed, 12 failed, none skipped. Against round 6: one case removed,
one reversed and green; the twelve red cases are round 6's, for the same reasons.

| Red case | File | What `gov close` did |
|----------|------|----------------------|
| `test_a_red_hard_block_check_the_ticket_did_not_touch_refuses_the_close` | governance_checks | closed the ticket; `license-present` is red |
| `test_a_red_hard_block_check_refuses_a_ticket_whose_governance_change_declares_no_check` | governance_checks | closed the ticket; `license-present` is red |
| `test_a_refusal_for_a_red_check_is_counted` | governance_checks | closed the ticket |
| `test_a_refusal_for_a_red_check_opens_a_dependent_repair_ticket` | governance_checks | closed the ticket |
| `test_a_hard_block_check_whose_command_is_absent_refuses_the_close` | governance_checks | closed the ticket; `tool-absent` is red |
| `test_a_check_green_at_an_earlier_commit_and_red_at_the_commit_being_closed_refuses` | stale | closed the ticket; `settings-strict` is red at HEAD |
| `test_a_check_green_at_this_commit_before_what_it_reads_changed_refuses` | stale | closed the ticket; `not-in-maintenance` is red |
| `test_a_declaration_changed_in_two_commits_and_green_at_the_commit_being_closed_closes` | stale | refused: "governance evidence is stale: feature-present changed after evidence was collected" |
| `test_a_refusal_for_no_acceptance_tests_is_counted` (2 forms) | no_acceptance_tests | refused with `NO_ACCEPTANCE_TESTS`, exit code 3; no iteration counted |
| `test_a_refusal_for_no_acceptance_tests_opens_a_dependent_repair_ticket` (2 forms) | no_acceptance_tests | refused; no repair ticket |

## Round 7 (DEC-480)

DEC-480 (register of the main tree) says of a governance-changing ticket that `gov close`
refuses on "the same condition on which `gov check` blocks a merge". Rounds 6 and 6b fixed
that condition as "a hard-block check is red". One state differs: `gov check` ends with its
blocking exit code (3) while no single hard-block check is red, and `gov close` closed the
ticket. The cases are in `test_w1_30_check_blocks.py`; nothing else changes.

**The blocking states taken.** `tests/acceptance/W1-26/README.md` states one blocking state in
words: "Hard-block RED: `ok: false`, exit 3". Of a family it says that each has a status RED,
YELLOW or GREEN and that a family the runner does not name is "reported by name, never silently
missing"; it states no further blocking state. The one written here is the state the order
names, which W1-26's own cases fix (`test_w1_26_dec436.py`, DEC-436: a declaration whose family
is none of the runner's families "is reported by name and makes the result not green"): the
check runs and passes, its family is RED, `gov check` blocks. No other state is written.

**The fixture, held by running `gov check`.** A project with its own two checks
(`project_with_checks`): `readme-present`, and `feature-present`, declared in the family
`licence hygiene`, which is none of the runner's. Before the close each case runs
`gov check --json` at the commit being closed and fails there unless: the exit code is 3 and
`ok` is false; no hard-block check is red; `feature-present` is GREEN; the families the runner
reports RED are exactly `licence hygiene`. The family the answer must name is read from the
runner's answer.

| Case | What it holds |
|------|---------------|
| `test_a_close_is_refused_where_gov_check_blocks_and_no_hard_block_check_is_red` (2 forms: the passing check declared hard-block, declared warning) | refused, exit code 3; the answer names the family the runner reports RED; the ticket is not closed |
| `test_a_refusal_where_gov_check_blocks_is_counted` | the refusal is one iteration |
| `test_a_refusal_where_gov_check_blocks_opens_a_dependent_repair_ticket` | one repair ticket; by the ticket tool it depends on the ticket |
| `test_the_same_ticket_closes_where_gov_check_does_not_block` | the converse guard: the same project, ticket and check, the check declared in `graph integrity`; `gov check` ends with exit code 0, no check and no family red; the ticket closes |

### The run of round 7

`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`,
against the engineer's commit `5505ba57`: 204 cases in 18 files; 200 passed, 4 failed, none
skipped. The 199 cases of round 6b are green. Of the five new cases the converse guard is
green and four are red:

| Red case | What `gov close` did |
|----------|----------------------|
| `test_a_close_is_refused_where_gov_check_blocks_and_no_hard_block_check_is_red[hard-block]` | closed the ticket (exit code 0); `gov check` blocks, family `licence hygiene` RED |
| `test_a_close_is_refused_where_gov_check_blocks_and_no_hard_block_check_is_red[warning]` | closed the ticket (exit code 0); the same |
| `test_a_refusal_where_gov_check_blocks_is_counted` | closed the ticket; nothing refused, nothing counted |
| `test_a_refusal_where_gov_check_blocks_opens_a_dependent_repair_ticket` | closed the ticket; no repair ticket |

Not written: a hard-block policy key of the path map that no check covers. The runner reports
it as a check entry of its own (`policy-<key>`, hard-block, RED), so it is "a hard-block check
is red", the state of rounds 6 and 6b, and the W1-26 README does not state it as a blocking
state of its own.

## Round 8 (DEC-487, made exact by DEC-490)

A fresh reviewer probed `gov close` and found ways in which it closes a ticket whose work it did
not measure. DEC-487 (register section 124) states, behaviour by behaviour, what `gov close` does
after the follow-up. The cases are in six new files, `test_w1_30_r8_*.py`; new helpers are at the
end of `w1_30_support.py` ("Round 8"). Each case builds the project the reviewer described, by the
suite's own means, and holds the outcome DEC-487 names. "Closed" below is what `gov close` did at
`e5560b9a`: exit code 0, the ticket closed.

**Round 8b.** Round 8 returned seven points no source settled. DEC-490 (register section 127)
decides them, and the cases were brought to it: which commits that name no task refuse (behaviour
4), the words of a judgement (7), what a refusal's own repair ticket does to the tree rule (1), the
exit codes (1, 8, 9, 11, 13). Store freshness (11) keeps its behaviour-only case; "written whole
or not at all" (9) gets no case with timing. What changed is marked "8b" below; "Packages of
round 8" says how each point was decided.

**Existing cases changed: one, for point 12.**
`test_a_change_under_each_governance_prefix_has_the_checks_run` (governance_checks) has an eighth
form, `governance/kernel/`. With it `support.GOVERNANCE_PREFIXES` holds eight prefixes and
`support.GOVERNANCE_TICKET_PATHS` holds `governance/kernel/**` (the paths of the governance cases'
ticket, so that W1-50's judgement passes the engineer's commit there). No other existing case and
no existing helper is changed. No case held the contrary of point 12; the settlement did
(settlement 5, "Which paths are governance files" in round 6: "no source names another path").
DEC-487 is that source now: "The suite's earlier settlement to the contrary is revised."

### The behaviours, the cases, and why each is red

`tree` = `test_w1_30_r8_tree.py`, `test_runs`, `commits`, `probe_record`, `escalation`, `last_step`
likewise.

**1. The tree a close measures is the commit it records** (tree). Held in every refusal: the answer
names the path; the exit code is 1 (8b: "could not measure", DEC-490; before: neither 0 nor 3);
nothing closed; the count stays 0; no repair ticket.

| Case | The project | Red now because |
|------|-------------|-----------------|
| `test_an_uncommitted_edit_that_makes_the_failing_acceptance_test_pass_refuses` | the committed acceptance test fails, the working tree's passes | closed |
| `test_an_untracked_file_at_the_root_that_makes_every_test_pass_refuses` | an untracked `conftest.py` at the root answers for every test function | closed |
| `test_an_uncommitted_edit_of_the_ticket_file_that_takes_the_full_profile_away_refuses` (2 forms: lowered to STANDARD, line removed) | the committed ticket is FULL, no probe record | closed, both forms |
| `test_an_uncommitted_governance_change_refuses_where_a_hard_block_check_is_red` | `license-present` red (held by `gov check`); `governance/project/notes.yaml` written, not committed | closed |
| `test_source_changed_after_the_probed_commit_and_not_committed_refuses` | FULL, probe record committed; the source rewritten in the working tree | closed |
| `test_a_file_git_ignores_refuses_nothing` | a file under an ignored folder | green: the converse guard |
| 8b: `test_a_second_close_with_the_refusals_repair_ticket_left_untracked_is_measured` | the failing ticket is closed twice, nothing committed in between; held first: the refusal left one untracked ticket file whose `parent` is the ticket. The second close: exit code 3, the failing test named, the count 2, a second repair ticket | green: the converse guard of the tree rule |
| 8b: `test_an_untracked_ticket_file_that_is_not_a_repair_ticket_of_this_ticket_refuses` (2 forms: its `parent` is another ticket of the project; it names no parent) | a green, committed ticket; one untracked file under `.tickets/` | closed, both forms |

DEC-490: "An untracked ticket file whose parent is the ticket being closed does not refuse the
next close. Every other untracked, not ignored file and every change to a tracked file does, the
ticket's own file included." The ticket's own file changed and not committed is the third row.

**2. The caller's environment** (test_runs). `PYTEST_ADDOPTS` is set in the environment of
`gov close` only; the ticket's one acceptance test fails.

| Case | Red now because |
|------|-----------------|
| `test_options_in_the_callers_environment_do_not_reach_the_test_runs[collect only]` | closed |
| `...[deselect the failing test]` | refused with exit code 3 for "no test was collected": the option reached the run; the answer does not name `test_fail` |

**3. Nothing ran** (test_runs). `test_a_ticket_whose_only_acceptance_test_is_skipped_refuses`:
exit code 3, nothing closed, one iteration counted, as for a ticket without acceptance tests
(round 6). Red: closed.

**13. The time limit** (test_runs).
`test_a_time_limit_that_is_not_a_positive_number_is_refused_as_an_invalid_argument` (`0`, `-5`).
8b (DEC-490: "refused like any other invalid argument, before anything runs"): the ticket's
acceptance test now fails, so anything that ran would be counted. The case first gives the other
invalid argument the suite holds for this command, a disposition that is none of the six names
(`test_only_six_disposition_names_accepted`), holds exit code 1 for it, and holds the same exit
code for the time limit; the answer names the argument; nothing closed, nothing counted, no repair
ticket. Red: with `0` the tests ran (read as "no limit given"): exit code 3, counted, a repair
ticket; `-5` was refused with exit code 3 as a test run over its time limit, counted, with a
repair ticket.

**4. Commits that name no task** (commits). 8b, DEC-490: "Among the commits after the ticket's
first, one that names no task refuses the close when it changes the ticket's acceptance tests, a
path inside the ticket's allowed paths, or the ticket's own file: that is work on this ticket
which no ticket measured. One that changes a governance file has the governance checks run, as a
ticket commit would. After the probed commit, one that changes a path inside the ticket's allowed
paths makes the probe stale. Any other task-less commit (a decision record, a checkpoint, a probe
record, another folder) refuses nothing. A commit that names another ticket is that ticket's."

What refuses is what the commit changes, not its role or its author. Every case holds first that
its commit names no task and changes the one path named (`_task_less`). A refusal is a finding,
exit code 3.

| Case | The commit, after the ticket's first, changes only | Held | Red now because |
|------|----------------------------------------------------|------|-----------------|
| `test_a_commit_without_trailers_that_weakens_the_acceptance_test_refuses` (8b: no longer adds `src/other/outside.py`) | the ticket's failing acceptance test, so that it passes; no trailer | the commit named, "task" said | closed |
| `test_a_commit_with_the_engineers_role_and_no_task_refuses` (8b: the same) | the same, `Role: engineer` alone | the same | closed |
| 8b: `test_a_commit_with_the_orchestrators_role_and_no_task_that_weakens_the_acceptance_test_refuses` | the same, `Role: orchestrator` alone, by the orchestrator | the same | closed |
| 8b: `test_a_commit_without_trailers_that_adds_a_file_inside_the_tickets_allowed_paths_refuses` | a new `src/example/more.py`; the ticket is green | the same | closed |
| 8b: `test_a_commit_without_trailers_that_changes_the_tickets_own_file_refuses` | the ticket's file: FULL lowered to STANDARD, no probe record | the same | closed |
| `test_a_commit_without_trailers_that_changes_a_governance_file_refuses_where_a_check_is_red` (8b: renamed; the answer names the red check, no longer the commit and "task") | `governance/project/notes.yaml`, outside the ticket's paths; `license-present` red | `license-present` named | closed |
| 8b: `test_a_commit_without_trailers_that_changes_a_governance_file_has_the_checks_run` | the same file; every check green | closed, and the close record's `check_commit` is the commit being closed | the ticket closes; the close record names no `check_commit` |
| `test_a_commit_without_trailers_that_rewrites_the_source_after_the_probed_commit_refuses` (8b: "task" no longer required) | the probed source, inside the ticket's paths | the commit named | closed |
| 8b: `test_a_commit_without_trailers_that_changes_only_a_folder_that_is_none_of_the_tickets_refuses_nothing` (2 forms: `src/other/outside.py`, `notes/meeting.txt`) | a file that is no acceptance test of the ticket, not inside its allowed paths, not its file, no governance file | closed; the close record claims no check result | green: the converse guard, both forms |
| `test_a_commit_that_names_another_ticket_refuses_nothing` | another ticket's commit, inside that ticket's paths | closed | green: the converse guard |

The four cases of round 8 against the sentence: the first two refused for two things at once, the
weakened test and a file outside the ticket's paths; the second is no reason, and was taken out.
The third asked for the commit and the word "task"; a governance file outside the ticket's paths
is not work on the ticket, it has the checks run, so the case asks for the red check. The fourth
changes a path inside the ticket's allowed paths after the probed commit: it refuses for both
reasons the sentence gives, and the case no longer says which word the answer uses.

**5. A commit of the ticket without a role** (commits).
`test_a_commit_of_the_ticket_without_a_role_refuses`: `Task` and `Implements`, no `Role`; widens
the ticket's allowed paths in the ticket file and adds a file under `governance/kernel/`. Exit
code 3, the commit named, "role" said. Red: closed.

**6. Merges and the first commit** (commits).

| Case | Red now because |
|------|-----------------|
| `test_a_merge_with_the_tickets_trailers_that_brings_a_governance_file_refuses_where_a_check_is_red` (the answer names the red check, the side commit or the merge) | closed |
| `test_a_merge_with_the_tickets_trailers_that_brings_a_source_rewrite_after_the_probed_commit_refuses` | closed |
| `test_the_paths_of_a_ticket_commit_that_is_the_first_commit_are_judged` | closed |

The first commit of the last case carries the ticket's trailers with the orchestrator's role and
holds the project's check declarations and a file under `governance/project/`; W1-50's judgement
has no finding (held), `license-present` is red (held). So the only reason to refuse is that the
first commit's paths are governance files. A first commit with the engineer's role and a path
outside the ticket's paths is refused today, by W1-50's judgement; that form was written, was
green, and is not kept.

**7. The probe record** (probe_record). Exit code 3 (DEC-470).

| Case | Red now because |
|------|-----------------|
| 8b: `test_a_judgement_that_is_neither_pass_nor_passed_refuses` (3 forms: `fail`, `failed`, `inconclusive`; the answer names the judgement; replaces `test_a_judgement_that_says_the_probe_failed_refuses`) | closed, all three forms |
| 8b: `test_a_judgement_of_pass_or_passed_is_accepted` (2 forms; replaces `test_a_judgement_that_says_the_probe_passed_is_accepted`) | green, both forms |
| `test_a_probe_record_that_is_written_and_not_committed_refuses` (any refusal that names the record's file: for the tree or for the record) | closed |
| `test_a_probe_record_committed_without_the_orchestrators_role_refuses` (the engineer's ticket commit; the ticket's paths hold `docs/probes/**`, W1-50 has no finding; the answer says "orchestrator") | closed |
| `test_a_probed_commit_given_as_a_name_that_moves_refuses` (`HEAD`, `main`; an engineer's commit follows) | closed, both forms |
| `test_a_commit_with_the_reviewers_role_and_no_task_before_the_probed_commit_refuses` (adds a source file; the answer names the commit) | closed |

DEC-490: "The judgement of a probe record is `pass` or `passed` to be accepted; `fail`, `failed`
or any other value refuses."

**8. The owner's decision** (escalation). The escalation is made by `support.escalate`: three
refusals for the failing test, a fourth blocked. "Not lifted" is held twice: the close given the
decision stays blocked, with the blocked exit code 4 (8b, DEC-490: "an owner's decision that does
not qualify lifts nothing: the close stays blocked, with the blocked exit code"; before: refused,
not 0), and the next close, given none, is blocked (exit code 4). One case accepts exit code 1
beside 4: in `test_a_file_no_commit_holds_lifts_no_escalation` the planted file also makes the
tree another than its commit, and no source states whether the close answers the escalation or
the tree first.

| Case | Red now because |
|------|-----------------|
| `test_a_file_no_commit_holds_lifts_no_escalation` (untracked `docs/adr/DEC-planted.md` holding `status: ACTIVE` only) | lifted: the close given the decision ran the tests (exit code 3) |
| `test_a_path_to_a_file_outside_the_project_lifts_no_escalation` (`../`-paths from each place a decision is looked for) | lifted, the same |
| `test_the_tickets_own_checkpoint_lifts_no_escalation` | lifted, the same |
| `test_a_decision_recorded_before_the_escalation_began_lifts_none` (the owner's, ACTIVE, no finding of W1-11's checker) | lifted, the same |
| `test_a_decision_that_lifted_one_escalation_lifts_no_second` | the same decision lifted the second escalation: the close ran the tests again (exit code 3) |

**9. The escalation state** (escalation). 8b, DEC-490: a counter that is not a count is "could
not measure": exit code 1, the file named in the answer, not counted, no repair ticket (before:
neither 0 nor 3). An escalation in force whose counter is missing blocks (exit code 4, DEC-487).

| Case | Red now because |
|------|-----------------|
| `test_an_escalation_in_force_whose_counter_is_missing_blocks_and_says_so` (exit code 4, the counter's path named) | the close ran: exit code 3 |
| `test_a_counter_that_is_not_a_count_from_zero_up_blocks_and_says_so[below zero]` (preset `-5`; exit code 1, the path named, counter unchanged, no repair ticket) | the close ran: exit code 3, a repair ticket |
| `...[not a whole number]` (`1.5`) | refused with `ITERATION_CORRUPT`, exit code 1; the answer does not name the file |
| `test_a_counter_that_cannot_be_read_blocks_and_names_its_file` (exit code 1, the path named, no repair ticket, nothing closed) | refused with `ITERATION_CORRUPT`, exit code 1; the answer does not name the file |
| `test_a_refusal_leaves_the_counter_and_the_escalation_whole_and_nothing_beside_them` | green: after each of three refusals the counter's folder holds the one readable file, and so does the escalation's |

"Written whole or not at all" has no case beyond the last one. DEC-490: it "is held by the unit
tests and by reading (write beside, then rename); no acceptance case with timing."

**10. The last step fails** (last_step). The ticket stays in progress and
`support.records_saying_closed` finds nothing: no close record with status ACTIVE, no checkpoint of
the ticket whose `next_action` is "ticket closed".

| Case | Red now because |
|------|-----------------|
| `test_a_ticket_tool_that_fails_on_closing_leaves_nothing_that_says_the_ticket_closed` | refused (`TICKET_TOOL_FAILED`), the ticket in progress; the close record and the checkpoint "ticket closed" are left |
| `test_a_close_record_that_cannot_be_written_leaves_nothing_that_says_the_ticket_closed` | refused (`CLOSE_RECORD_FAILED`); the checkpoint "ticket closed" is left |

**11. A stale record store** (last_step).
`test_a_record_store_older_than_the_commit_being_closed_refuses_and_names_the_rebuild`: the store
is loaded, the owner's commit supersedes `DEC-000`, the close runs without a reload. Held
afterwards: with the store loaded again `gov context` answers `BLOCKED` and names `DEC-000`. The
close is refused, the answer holds "gov rebuild", nothing closed. 8b (DEC-490): it is "could not
measure": exit code 1, not counted, no repair ticket (before: refused, not 0). How the store's
freshness is told stays out of the case: "the engineer uses a mark the store or the runtime
already keeps of the commit it was built from; if none exists inside what `gov close` may read,
that case is returned, not guessed." Red: closed.

**12. The installed kernel is governance** (last_step, governance_checks).

| Case | Red now because |
|------|-----------------|
| `test_a_ticket_commit_under_the_installed_kernel_refuses_where_a_hard_block_check_is_red` (W1-50 has no finding, `license-present` red, both held) | closed |
| `test_a_change_under_each_governance_prefix_has_the_checks_run[governance/kernel/]` | closed; the close record names no `check_commit` |

### Packages of round 8

1. **"A commit that names no task at all refuses", and the suite's own projects.** Every project
   of this suite holds commits without a `Task` trailer after the ticket's first commit: the
   orchestrator's (`Role: orchestrator`: the checkpoint, the probe record, what a refusal left) and
   the owner's (`Role: owner`: decision records, the owner's decision that lifts an escalation).
   DEC-487 itself needs both (the probe record "by a commit with the orchestrator's role", the
   owner's decision "committed"). Read to the letter, the sentence refuses every close of the
   suite. The cases hold the two ends: a commit with no trailer at all, or with the engineer's
   role alone, refuses; the orchestrator's and the owner's commits of the existing 208 green cases
   refuse nothing. Where the line lies between them (by role, by the paths a role may write under
   W1-50, by who committed) no source states. Not written: a commit with `Role: orchestrator` and
   no task that weakens an acceptance test.
   **Decided (DEC-490):** the line is what the commit changes: the ticket's acceptance tests, a
   path inside its allowed paths, its own file refuse; a governance file has the checks run; any
   other refuses nothing; the role lifts nothing. The middle cases are written (behaviour 4). An
   audit of every `gov close` the suite starts (a scratch plugin, not part of the suite) found no
   case outside the round-8 files whose project holds a task-less commit, after the ticket's
   first, on one of the three kinds of path, but for
   `test_reviewer_commit_in_ticket_commits_refused` (probe), which holds a refusal.
2. **The words of a probe's judgement.** No source states them (CAP-38.f, DEC-137: the
   orchestrator "judges"; the README named the field only). On this round's order the cases use
   `failed` (refuses) and `passed` (accepted). The suite's fixtures have written `pass` since
   round 4, and every FULL ticket that closes in the suite does so with `pass`. So either `pass`
   and `passed` are both accepted, or `support.probe_record`'s word is changed in a later round.
   **Decided (DEC-490):** `pass` and `passed` are accepted; `fail`, `failed` and any other value
   refuse. The fixtures keep `pass`.
3. **How a store's freshness against the head commit is told.** The READMEs of W1-06 (pins),
   W1-10 (the store: `load`, the digest) and W1-27 (`gov rebuild`; "index freshness" is the lexical
   index's) state no way to ask whether the store was built from `HEAD`; there is no W1-51 folder.
   The case holds the behaviour only.
   **Decided (DEC-490):** unchanged; the mark is the engineer's to find, and the case is returned
   if none exists inside what `gov close` may read. Only the exit code was added (package 5).
4. **A refused close leaves its repair ticket untracked, and the next close must find the tree
   committed.** Under the first behaviour the second of two closes in a row would be refused for
   the repair ticket's file, uncounted, so no escalation could be reached that way. The new cases
   commit what a refusal left, as the orchestrator, before the next close
   (`support.commit_what_a_refusal_left`). The existing cases that close twice or more in a row
   without a commit in between (most of iteration, two of time_limit) were not changed. Either
   the files `gov close` itself wrote are no refusal, or those cases get the commit in a later
   round.
   **Decided (DEC-490):** an untracked ticket file whose parent is the ticket being closed
   refuses no later close; every other untracked file does. Three cases hold it (behaviour 1).
   The existing cases that close repeatedly without a commit were not changed, and none collides:
   the same audit looked at the working tree at every `gov close` the suite starts, and outside
   the round-8 files it found nothing waiting but repair tickets whose `parent` is the ticket
   being closed. That covers every case of iteration, time_limit, disposition, repair_ticket and
   close that closes more than once. A refused close leaves nothing else that git sees (the
   counter and the escalation are under the ignored `.gov-runtime/`). The audit could not look
   at two cases, which break git on purpose and close once:
   `test_git_failure_is_error_not_empty_list` (close) and
   `test_a_git_failure_while_the_probes_commits_are_read_refuses` (probe_commits). The new cases
   of round 8 still commit what a refusal left (`support.commit_what_a_refusal_left`).
5. **Exit codes DEC-487 does not give.** A refusal for the tree: the cases hold "neither 0 nor 3".
   A counter that is no count: "neither 0 nor 3" (the suite holds exit code 1 for an unreadable
   counter since round 4; DEC-487 says "blocks"). A stale store, an owner's decision that lifts
   nothing: "refused, not 0". A time limit that is no limit: 1 or 2.
   **Decided (DEC-490):** a tree that is not its commit, a store older than the commit, a counter
   that is no count: exit code 1, not counted, no repair ticket
   (`support.refused_without_a_finding` now holds exit code 1). An owner's decision that does not
   qualify: exit code 4. A time limit that is no limit: the exit code of this command's other
   invalid argument. The suite held no exit code for one until now:
   `test_only_six_disposition_names_accepted` holds an error in the envelope. The time-limit case
   gives that invented disposition first and holds exit code 1 for it (what `gov close` answers
   today, `INVALID_DISPOSITION`, and API-0002's code for an error in the envelope), then the same
   for the time limit. Left open, in one case: whether an escalated close with an untracked file
   answers 4 or 1 (behaviour 8).

### The run of round 8

`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`, at
`e5560b9a`: 247 cases in 24 files; 208 passed, 39 failed, none skipped. The 204 cases of round 7
are green. Of the 43 new cases (42 in the new files and the eighth form of the prefix case) 39 are
red for the reasons above and four are green: the ignored file, the other ticket's commit, the
judgement `passed`, the counter left whole.

### The run of round 8b

The same command, with `gov close` as at `e5560b9a` (the branch holds no later change of it): 259
cases in 24 files; 212 passed, 47 failed, none skipped. The 204 cases of round 7 are green. Of
the 55 cases of round 8 (54 in the six files and the eighth form of the prefix case) 47 are red
for the reasons above and eight are green: the ignored file, the second close beside its untracked
repair ticket, the other ticket's commit, the commit in a folder that is none of the ticket's (2
forms), the judgements `pass` and `passed`, the counter left whole.

Against round 8: twelve cases more. Eight are red (the orchestrator's task-less commit, the file
inside the allowed paths, the ticket's own file, the governance file with green checks, the
untracked ticket file in 2 forms, and two more judgement words: `fail`, `inconclusive`); four are
green (the second close, the other folder in 2 forms, the judgement `pass`). No case that was
green in round 8 is red, and none that was red is green.

## Round 9: every finding in one run; the ticket tool on PATH (DEC-492)

DEC-492 (owner, 2026-10-07; register v0.129), first point: "`gov close` reports every finding in
one run instead of stopping at the first, and finds the ticket tool on PATH as well as at the
kernel path." The round's order makes it exact: one refusal names every finding the run can
establish, is counted once and opens one repair ticket that lists them all; what an earlier part
made unmeasurable is said as not measured, by name, never left out and never reported as passed;
the "could not measure" states of DEC-490 still end the run before anything is measured. The
ticket tool is the installed kernel's and, where that is not there, the one on `PATH`; where both
exist the kernel's is used; with neither the answer says so.

Two new files, 15 cases, and three additions to the support code (`tk` and
`assert_dependent_repair_ticket` take another tool than the kernel's; `path_with_tool`;
`says_not_measured`).

### 1. Every finding in one run (`test_w1_30_r9_every_finding.py`, 10 cases)

The combined ticket holds four findings, each planted by its own commit and each held by the
fixture before the close: a commit of the ticket, by its engineer, inside its paths, without
`Implements:`; an engineer's commit of `NOTES.md` at the project's root (W1-50's judgement is
asked and gives that commit and that path alone); a failing acceptance test (`test_fail`); a red
hard-block check (`license-present`, red by W1-26's runner at the commit being closed; the ticket
changes `governance/project/notes.yaml`, so the checks run).

| Case | Holds | Red reason, as observed at `18c9c34b` |
|------|-------|---------------------------------------|
| `test_one_refusal_names_every_finding_of_the_ticket` | exit code 3; the answer names the commit and `Implements`, the commit and `NOTES.md`, `test_fail`, `license-present`; nothing closed | the answer is `TRAILER_MISSING` alone: it does not name the containment finding, the failing test, the red check |
| `test_the_refusal_for_several_findings_is_counted_once` | the same answer; the count is 1 | the same: the answer names one finding of four |
| `test_the_refusal_for_several_findings_opens_one_repair_ticket_that_lists_them_all` | one repair ticket, dependent on the ticket by the ticket tool; its file lists all four | one dependent repair ticket is opened; its file lists the commit without `Implements:` and none of the other three |
| `test_an_early_finding_does_not_hide_the_failing_acceptance_test` (3 forms: no probe record on a FULL ticket, a commit without `Implements:`, a containment finding) | exit code 3; the answer names the early finding and `test_fail`; the count is 1; one dependent repair ticket | the answer is `PROBE_MISSING`, `TRAILER_MISSING`, `CONTAINMENT_FINDING` alone: `test_fail` is not in it |
| `test_without_acceptance_tests_the_acceptance_run_is_said_as_not_measured` | a ticket without acceptance tests and with the red check: exit code 3; the answer names the missing tests and says of the acceptance run that it was not measured (settlement 14); nothing closed | the answer is `NO_ACCEPTANCE_TESTS` alone and says of nothing that it was not measured |
| `test_without_acceptance_tests_the_governance_checks_are_still_reported` | the same ticket: the answer names the missing tests and `license-present`; the count is 1 | the answer does not name `license-present`: the checks were not reached |
| `test_a_measured_part_is_not_said_as_not_measured` | the other side, on the combined ticket: the answer names `test_fail` and does not say of the acceptance run that it was not measured | the answer is `TRAILER_MISSING` alone: `test_fail` is not in it |
| `test_a_tree_that_is_not_its_commit_still_ends_the_run_before_any_finding` | the combined ticket with an untracked `stray.txt`: exit code 1, the file named, none of the four findings reported, not counted, no repair ticket (DEC-490) | green: the behaviour of round 8, held so that "every finding" does not reach past it |

Not held, and why. "Never reported as passed" has no form of its own in any source: the cases hold
that the refusal says "not measured" of the acceptance run and that the ticket is not closed, and
the other side holds that the words are not said of a run that ran. Only the DEC's own instance of
a part that cannot be measured is written (no acceptance tests, so no acceptance run); which other
parts depend on which is the engineer's to state in the answer. The order of the findings in the
answer and in the repair ticket, and the error code of a refusal with several findings, are held
nowhere: no case of the suite holds the code of an early finding.

### 2. Where the ticket tool is found (`test_w1_30_r9_ticket_tool.py`, 5 cases)

This machine has a `tk` on `PATH`, so every case builds its own `PATH`: the caller's without any
`tk` (`support.path_without`), and before it, where the case wants one, a folder of its own that
holds the tool (`support.path_with_tool`: a copy of the kernel's, or a planted script). A project
without the tool at the kernel's place has it removed by the owner before the ticket's first
commit, so the removal is no commit of the ticket's range. Where a case is about which tool was
used, the one on `PATH` writes a line to a file outside the project whenever it is started.

| The kernel's place | `PATH` | Case | Holds | As observed at `18c9c34b` |
|--------------------|--------|------|-------|---------------------------|
| no tool | the tool | `test_a_clean_ticket_closes_where_the_ticket_tool_is_on_path_only` | the ticket closes: status `closed`, one close record | red: `TICKET_TOOL_ABSENT`, exit code 1 ("not available at governance/kernel/bin/tk") |
| no tool | the tool | `test_a_refused_close_opens_its_repair_ticket_where_the_ticket_tool_is_on_path_only` | a failing acceptance test: exit code 3, `test_fail` named, one repair ticket that depends on the ticket (read back with the tool on `PATH`), the count is 1 | red: no repair ticket; the answer says "not opened: the ticket tool (tk) is not available at governance/kernel/bin/tk" |
| the tool | a tool that fails and records | `test_the_kernels_ticket_tool_is_used_where_path_holds_another` | the ticket closes; the tool on `PATH` was never started | green |
| a tool that fails | the tool, recording | `test_a_failing_kernel_ticket_tool_is_not_replaced_by_the_one_on_path` | the close fails; nothing says the ticket closed; the tool on `PATH` was never started | green |
| no tool | no tool | `test_the_answer_says_so_where_the_ticket_tool_is_at_neither_place` | the close fails; the answer names the ticket tool; nothing says the ticket closed | green |

The three green cases hold today's behaviour against the change: a search of `PATH` that comes
first, or that follows a failure of the kernel's tool, turns the two middle ones red.

### Existing cases against DEC-492

None was rewritten. Looked for, in every file of the suite:

- **"The first finding only".** No case holds the error code of an early finding, the number of
  findings in an answer, or that a later part did not run after an early finding (no assertion on
  `error["code"]` for a refusal of the ticket's work, none of the form "not in" the answer). The
  cases with an early finding hold what the answer names and that the refusal is counted and
  opens a repair ticket, and each of their tickets is otherwise clean and green, so a run that
  goes on finds nothing more there.
- **"The tool only at the kernel path".** Every case with the kernel's tool removed or failing
  (`test_close_fails_when_ticket_tool_absent`; the four of `test_w1_30_repair_ticket.py`;
  `test_a_ticket_tool_that_fails_on_closing_leaves_nothing_that_says_the_ticket_closed`) runs on a
  `PATH` without `tk`. Those are the row "no tool, no tool" and the kernel's tool failing with no
  other: unchanged by the decision.

### The run of round 9

`env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-30 -q -p no:cacheprovider -rs`, at
`18c9c34b` (the engineer's round 8, `308bad42`, and the merge of `w1/integrate`): 274 cases in 26
files; 263 passed, 11 failed, none skipped. The 259 cases of round 8b are green. Of the 15 new
cases 11 are red for the reasons above and four are green: the tree that is not its commit, the
two cases of precedence, the tool at neither place.

## Covers ids

| Covers id | Tests |
|-----------|-------|
| CAP-13.a | close: envelope, success, checkpoint, containment |
| CAP-24.a | close: kernel/vendor skill versions |
| CAP-31.b | iteration: persistence, reset, escalation |
| CAP-38.a | close: runs tests, refuses on failure, regression |
| CAP-38.b | traceability: 5 tests |
| CAP-38.c | close: Implements, Task trailers |
| CAP-38.d | governance_checks: 20 tests; stale: 5 tests |
| CAP-38.f | probe: 16 tests; probe_record (round 8): 10 tests |
| DEC-487, DEC-490 | the six `test_w1_30_r8_*.py` files: 54 tests; governance_checks: the `governance/kernel/` form |
| DEC-492 | the two `test_w1_30_r9_*.py` files: 15 tests (every finding: 10; the ticket tool: 5) |
| CAP-50.c | receipt: 16 tests |
| DEC-460, DEC-470 | commit_models: 4 tests; context_failures: no store (5 tests) |
| CAP-59.a | iteration: escalation, options, repair, outcomes |
| CAP-59.b | iteration: count/budget hidden (5 tests) |
| CAP-59.c | disposition: 13 tests |
| DEC-137 | probe: reviewer verification (6 A5 tests) |

## Settlements

1. **Disposition argument name**: `--disposition` (value: one of the six DISPOSITIONS names)
2. **Owner decision argument name**: `--owner-decision` (value: decision register id)
3. **Iteration file location**: `.gov-runtime/iterations/<ticket>.json`
4. **Repair ticket dependency direction**: repair ticket depends_on the failing ticket
5. **Governance file prefixes** (A7): `template/governance/kernel/checks/`, `template/governance/kernel/schemas/`, `governance/project/`, `template/governance/kernel/hooks/`, `template/governance/kernel/skills/`, `template/governance/kernel/policies/`, `template/governance/kernel/roles/`. Revised in round 8 (DEC-487): the installed kernel, `governance/kernel/`, is the eighth
6. **Exit codes**: 0 success, 1 GovError, 3 check failed, 4 blocked
7. **Regression tests**: all under `tests/` except `tests/acceptance/<ticket-wbs>/`
8. **Time limit argument**: `--timeout` (seconds)
9. **Escalation file**: `.gov-runtime/escalations/<ticket>.json`
10. **Probe record probed_commit**: required field naming the commit the probe covers
11. **Models of the commits** (DEC-470): one list in the close record's frontmatter; each entry has `commit`, `role`, `model`; `model` is `not measured` for a commit without a `Co-Authored-By` line
12. **The governance checks in the close record** (round 6): `check_commit` holds the full id of the commit being closed; under `governance_checks`, every check that ran is an object with `id` and `status`, at any depth; a ticket that changed no governance file has neither key, or both empty
13. **The time limit of a governance check** (round 6b, DEC-480): the runner's own; `gov close` adds none, and `--timeout` (settlement 8) is the limit of the close's test runs only. Round 6's settlement (the close's `--timeout` as the limit of each check) is withdrawn
14. **How an answer says "not measured, by name"** (round 9, DEC-492): no source gives the form. Taken, in the refusal's `error` object: one sentence of one string holds both "not measured" and the part's name (for the acceptance run: "acceptance"), or one of the two is in a key and the other is under that key; `_` and `-` read as blanks, case is not held (`support.says_not_measured`). So `"the acceptance run was not measured: ..."`, `{"not_measured": ["acceptance tests"]}` and `{"acceptance": "not measured"}` all say it; the finding "no acceptance tests for ..." alone does not
15. **Where the ticket tool is found** (round 9, DEC-492): `governance/kernel/bin/tk`, else `tk` on `PATH`; the kernel's wherever it exists, also when it fails

## Residuals

- **S0a-G-12**: among the ticket's sources; its text is not in the tree. No test is
  derived from unread text.

## Size note

Estimate: 220 LOC. Second-start implementation: 732 LOC. Tests cover the full scope of
A1–A8 and B1–B7; no shrinkage applied.
