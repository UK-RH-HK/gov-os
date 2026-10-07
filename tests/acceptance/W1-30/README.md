# W1-30 Acceptance Tests — `gov close`

Ticket: DAEO-2lwj (W1-30, "gov close"), profile FULL.
Third-start revision: updated from owner decisions A1–A8, B1–B7.
115 cases in 8 files.

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
| `test_iteration_file_under_gov_runtime` | iteration | file elsewhere |

### S3: Product-traceability family check
**Covers: CAP-38.b**

| Test | File | Red reason |
|------|------|------------|
| `test_product_traceability_check_in_family` | traceability | not registered |
| `test_check_red_when_closed_ticket_lacks_implements_trailer` | traceability | passes without Implements |
| `test_check_red_when_closed_ticket_lacks_task_trailer` | traceability | passes without Task |
| `test_check_green_when_trailers_present_and_resolve` | traceability | fails with valid trailers |
| `test_check_red_when_implements_does_not_resolve` | traceability | passes with bad Implements |

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

### MWA-04: Containment

| `test_containment_blocks_close_for_out_of_scope_commit` | close | out-of-scope accepted |

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

### B6: Commits from HEAD only

| `test_ticket_commits_from_head_only` | close | other branches counted |

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
5. **Governance file prefixes** (A7): `template/governance/kernel/checks/`, `template/governance/kernel/schemas/`, `governance/project/`, `template/governance/kernel/hooks/`, `template/governance/kernel/skills/`
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
