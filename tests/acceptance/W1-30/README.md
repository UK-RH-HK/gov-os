# W1-30 Acceptance Tests — `gov close`

Ticket: DAEO-2lwj (W1-30, "gov close"), profile FULL.
Round 5 (see "Round 5" below): containment without exemption, context failures, the repair ticket,
the probe, the time limit. Round 5b (see "Round 5b"): the four points DEC-470 decides. The rule for
all of it: nothing is closed, and nothing is recorded, that was not measured. Round 6 (see
"Round 6"): the suite's sandbox, the governance checks of a close under DEC-476, stale evidence,
a ticket without acceptance tests. Round 6b (see "Round 6b"): DEC-480, `gov close` refuses on
what `gov check` blocks on. The counts of the last run are in "Round 6b".

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
| CAP-38.f | probe: 16 tests |
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
5. **Governance file prefixes** (A7): `template/governance/kernel/checks/`, `template/governance/kernel/schemas/`, `governance/project/`, `template/governance/kernel/hooks/`, `template/governance/kernel/skills/`, `template/governance/kernel/policies/`, `template/governance/kernel/roles/`
6. **Exit codes**: 0 success, 1 GovError, 3 check failed, 4 blocked
7. **Regression tests**: all under `tests/` except `tests/acceptance/<ticket-wbs>/`
8. **Time limit argument**: `--timeout` (seconds)
9. **Escalation file**: `.gov-runtime/escalations/<ticket>.json`
10. **Probe record probed_commit**: required field naming the commit the probe covers
11. **Models of the commits** (DEC-470): one list in the close record's frontmatter; each entry has `commit`, `role`, `model`; `model` is `not measured` for a commit without a `Co-Authored-By` line
12. **The governance checks in the close record** (round 6): `check_commit` holds the full id of the commit being closed; under `governance_checks`, every check that ran is an object with `id` and `status`, at any depth; a ticket that changed no governance file has neither key, or both empty
13. **The time limit of a governance check** (round 6b, DEC-480): the runner's own; `gov close` adds none, and `--timeout` (settlement 8) is the limit of the close's test runs only. Round 6's settlement (the close's `--timeout` as the limit of each check) is withdrawn

## Residuals

- **S0a-G-12**: among the ticket's sources; its text is not in the tree. No test is
  derived from unread text.

## Size note

Estimate: 220 LOC. Second-start implementation: 732 LOC. Tests cover the full scope of
A1–A8 and B1–B7; no shrinkage applied.
