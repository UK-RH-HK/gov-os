# W1-27 Acceptance Tests — gov doctor and gov rebuild

Ticket: DAEO-xw3k (W1-27).  
Test designer: independent-test-designer (MR-3, DEC-069).  
Profile: STANDARD.

## KPI-to-test mapping

### Success KPI 1 — doctor reports installation health [CAP-02.a, CAP-06.a, CAP-25.a]

> doctor reports pinned vs found tool versions, hooks wired, path map with zero
> unclassified paths, index freshness, canaries, framework.lock MATCH/DRIFT,
> per-repository isolation; non-zero on any failure

| Test | File | Red reason |
|------|------|------------|
| `test_doctor_is_a_read_command` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_envelope_is_valid_on_healthy_project` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_tool_versions` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_hooks` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_path_map_coverage` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_index_freshness` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_canaries` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_framework_lock` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_report_mentions_isolation` | test_w1_27_doctor.py | `gov doctor` not implemented |
| `test_doctor_exit_nonzero_on_any_failure` | test_w1_27_doctor.py | `gov doctor` not implemented |

### Success KPI 2 — rebuild guarantees [CAP-07.a, CAP-20.a, CAP-46.a]

> rebuild recreates every derived store; two rebuilds give the same digest; a
> fresh clone plus doctor plus rebuild works

| Test | File | Red reason |
|------|------|------------|
| `test_rebuild_is_an_act_command` | test_w1_27_rebuild.py | `gov rebuild` not implemented |
| `test_rebuild_recreates_derived_stores` | test_w1_27_rebuild.py | `gov rebuild` not implemented |
| `test_two_rebuilds_give_the_same_digest` | test_w1_27_rebuild.py | `gov rebuild` not implemented |
| `test_fresh_clone_doctor_rebuild` | test_w1_27_rebuild.py | `gov doctor` / `gov rebuild` not implemented |
| `test_rebuild_needs_only_git` | test_w1_27_rebuild.py | `gov rebuild` not implemented |
| `test_rebuild_digest_matches_store_loader` | test_w1_27_rebuild.py | `gov rebuild` not implemented |

### Success KPI 3 — path-map compliance [CAP-06.d]

> Path-map compliance is checked by doctor: every tracked path matches a
> path-map entry, and a recorded reference to a moved path is reported

| Test | File | Red reason |
|------|------|------------|
| `test_full_coverage_is_healthy` | test_w1_27_path_compliance.py | `gov doctor` not implemented |
| `test_unclassified_path_is_reported` | test_w1_27_path_compliance.py | `gov doctor` not implemented |
| `test_moved_path_reference_is_reported` | test_w1_27_path_compliance.py | `gov doctor` not implemented |

### Success KPI 4 — recovery/rebuild family check [CAP-38.b]

> Registers the recovery/rebuild family check: derived state deleted and rebuilt
> gives the same digest

| Test | File | Red reason |
|------|------|------------|
| `test_recovery_rebuild_check_declaration_exists` | test_w1_27_recovery_check.py | Check YAML not yet created under `template/governance/kernel/checks/` |
| `test_recovery_rebuild_check_has_correct_family` | test_w1_27_recovery_check.py | Check YAML not yet created |
| `test_recovery_rebuild_check_has_id` | test_w1_27_recovery_check.py | Check YAML not yet created |
| `test_recovery_rebuild_check_is_listed` | test_w1_27_recovery_check.py | `gov check --list` does not yet include it |
| `test_derived_state_deleted_and_rebuilt_gives_same_digest` | test_w1_27_recovery_check.py | `gov rebuild` not implemented |

### Success KPI 5 — adoption level [CAP-54.a]

> doctor reports an adoption level: a repository with only the kernel installed
> passes at the minimal level, and each completed adoption stage raises it
> toward ADOPTED_HEALTHY

| Test | File | Red reason |
|------|------|------------|
| `test_doctor_report_mentions_adoption_level` | test_w1_27_adoption.py | `gov doctor` not implemented |
| `test_minimal_kernel_passes_at_minimal_level` | test_w1_27_adoption.py | `gov doctor` not implemented |
| `test_completed_stages_raise_adoption_level` | test_w1_27_adoption.py | `gov doctor` not implemented |

### Success KPI 6 — Claude Code drift [DEC-210, DEC-214]

> doctor reports Claude Code drift; the CLI and extension differing, either
> being newer than the registry, or the extension's bundled binary at the
> recorded version with another sha256, is drift; below minimum 2.1.285 or CLI
> sha256 mismatch at recorded version is failure

| Test | File | Red reason |
|------|------|------------|
| `test_cli_newer_than_registry_is_drift` | test_w1_27_drift.py | `gov doctor` not implemented |
| `test_cli_and_extension_different_versions_is_drift` | test_w1_27_drift.py | `gov doctor` not implemented |
| `test_extension_bundled_binary_different_sha256_is_drift` | test_w1_27_drift.py | `gov doctor` not implemented |
| `test_cli_below_minimum_is_failure` | test_w1_27_drift.py | `gov doctor` not implemented |
| `test_extension_below_minimum_is_failure` | test_w1_27_drift.py | `gov doctor` not implemented |
| `test_cli_at_recorded_version_different_sha256_is_failure` | test_w1_27_drift.py | `gov doctor` not implemented |

### Success KPI 7 — held-out.yaml missing [DEC-223]

> doctor reports a missing governance/project/held-out.yaml in this repository,
> because the guard treats a missing file as no held-out rule

| Test | File | Red reason |
|------|------|------------|
| `test_missing_held_out_yaml_is_reported` | test_w1_27_held_out.py | `gov doctor` not implemented |
| `test_present_held_out_yaml_is_not_reported` | test_w1_27_held_out.py | `gov doctor` not implemented |

### Success KPI 8 — path-map schema replacement [DEC-185, DEC-189, DEC-228]

> gov validates governance/project/path-map.yaml against the kernel's path-map
> schema of W1-08, which replaces the minimal schema of W1-07 in
> src/gov/config/; the W1-07 acceptance cases that depend on the provisional
> shape are revised in this ticket's test design

| Test | File | Red reason |
|------|------|------------|
| `test_valid_w1_08_path_map_loads` | test_w1_27_schema.py | Schema in `src/gov/config/` not yet replaced |
| `test_valid_w1_08_path_map_is_not_reported_as_invalid` | test_w1_27_schema.py | Schema not yet replaced |
| `test_valid_w1_08_path_map_with_code_intelligence_loads` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_required_top_level_key_names_the_key[state_class]` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_required_top_level_key_names_the_key[capabilities]` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_required_top_level_key_names_the_key[policies]` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_required_top_level_key_names_the_key[systems]` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_namespaces_names_the_key` | test_w1_27_schema.py | Schema not yet replaced |
| `test_code_intelligence_enabled_without_languages_is_invalid` | test_w1_27_schema.py | Schema not yet replaced (DEC-265) |
| `test_code_intelligence_disabled_languages_optional` | test_w1_27_schema.py | Schema not yet replaced (DEC-265) |
| `test_namespace_missing_required_field_is_invalid` | test_w1_27_schema.py | Schema not yet replaced |
| `test_namespaces_of_the_wrong_type_names_the_key` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_policy_key_is_invalid` | test_w1_27_schema.py | Schema not yet replaced |
| `test_missing_system_is_invalid` | test_w1_27_schema.py | Schema not yet replaced |
| `test_absent_system_without_reason_is_invalid` | test_w1_27_schema.py | Schema not yet replaced |
| `test_repairing_the_key_clears_the_error` | test_w1_27_schema.py | Schema not yet replaced |

### Failure KPI 1 — doctor passes with a wrong tool version

| Test | File | Red reason |
|------|------|------------|
| `test_doctor_does_not_pass_with_wrong_tool_version` | test_w1_27_doctor.py | `gov doctor` not implemented |

### Failure KPI 2 — rebuild needs anything not in git

| Test | File | Red reason |
|------|------|------------|
| `test_rebuild_needs_only_git` | test_w1_27_rebuild.py | `gov rebuild` not implemented |

## Revised W1-07 cases (DEC-228, reason: planned: schema replaced)

The following cases in `tests/acceptance/W1-07/test_w1_07_config_details.py`
were marked *Provisional (DEC-189)* and are revised by this ticket's test
design. Their fixtures now use documents valid (or invalid) under the W1-08
schema instead of the minimal schema.

| Case name | Reason |
|-----------|--------|
| `test_a_valid_path_map_loads` | planned: schema replaced |
| `test_a_valid_path_map_is_not_reported_as_invalid_by_any_command` | planned: schema replaced |
| `test_namespaces_of_the_wrong_type_names_the_key` | planned: schema replaced |
| `test_a_missing_namespaces_names_the_key` | planned: schema replaced |
| `test_a_namespace_that_is_not_a_map_is_invalid` | planned: schema replaced |
| `test_repairing_the_key_clears_the_error` | planned: schema replaced |

## Residuals

- **S0a-G-04**: listed as a source in the ticket; its text is not in the tree.
  Noted as a residual.

## Decision packages

None. All KPI lines are settled from the ticket sources.

## Covers coverage

| Covers item | Tests |
|-------------|-------|
| CAP-02.a (framework.lock) | `test_doctor_report_mentions_framework_lock` |
| CAP-06.a (path classification) | `test_doctor_report_mentions_path_map_coverage`, `test_full_coverage_is_healthy` |
| CAP-06.d (path-map compliance) | `test_unclassified_path_is_reported`, `test_moved_path_reference_is_reported` |
| CAP-07.a (derived state) | `test_rebuild_recreates_derived_stores`, `test_rebuild_digest_matches_store_loader` |
| CAP-20.a (rebuild idempotent) | `test_two_rebuilds_give_the_same_digest` |
| CAP-25.a (tool registry) | `test_doctor_report_mentions_tool_versions`, `test_doctor_does_not_pass_with_wrong_tool_version` |
| CAP-38.b (recovery/rebuild check) | `test_recovery_rebuild_check_*`, `test_derived_state_deleted_and_rebuilt_gives_same_digest` |
| CAP-46.a (clone+doctor+rebuild) | `test_fresh_clone_doctor_rebuild` |
| CAP-54.a (adoption level) | `test_*_adoption_*` |
| DEC-210/214 (Claude Code drift) | `test_*_drift*`, `test_*_failure*` in test_w1_27_drift.py |
| DEC-223 (held-out.yaml) | `test_missing_held_out_yaml_is_reported`, `test_present_held_out_yaml_is_not_reported` |
| DEC-228 (schema replacement) | All tests in test_w1_27_schema.py, revised W1-07 cases |
| DEC-265 (languages conditional) | `test_code_intelligence_enabled_without_languages_is_invalid`, `test_code_intelligence_disabled_languages_optional` |

## Round 3 — rebuild recreates lexical index properly (DEC-416)

> KPI success 2: "rebuild recreates every derived store" [CAP-07.a, CAP-20.a, CAP-46.a]

| Test | File | Red reason |
|------|------|------------|
| `test_rebuild_lexical_index_is_fresh` | test_w1_27_rebuild_r3.py | rebuild creates empty tables via `_LEXICAL_SCHEMA`; `freshness()` returns "empty" not "fresh" |
| `test_rebuild_lexical_search_finds_tracked_text` | test_w1_27_rebuild_r3.py | empty tables return no search hits; FACET_UNAVAILABLE reason "stale" |
| `test_rebuild_result_names_derived_stores_with_measured_status` | test_w1_27_rebuild_r3.py | result has a "skipped" list with constant reasons instead of per-store recreated/not_recreated status |
| `test_rebuild_does_not_hold_lexical_schema_copy` | test_w1_27_rebuild_r3.py | `_LEXICAL_SCHEMA` and hardcoded DDL are present in `src/gov/rebuild/command.py` |

## Round 3 — doctor unmeasured vs error (DEC-416, DEC-425)

> KPI success 1: "non-zero on any failure" [CAP-02.a, CAP-06.a, CAP-25.a]
> KPI success 5: "adoption level" [CAP-54.a]

Section-by-section classification of unmeasured states:

| # | Section | Unmeasured condition | Classification |
|---|---------|---------------------|----------------|
| 1 | tools | "no tool-registry.yaml" | absence (OK) |
| 2 | hooks | no `lefthook.yml` | absence (OK) |
| 3 | path_map | "no path-map.yaml" | absence (OK) |
| 4 | path_compliance | (no unmeasured state) | — |
| 5 | index_freshness | `freshness()` exception: "cannot check index freshness" | **ERROR → should be fail** |
| 5 | index_freshness | status "missing"/"empty" | absence (OK) |
| 6 | canaries | `run_canaries()` exception: "canary runner failed" | **ERROR → should be fail** |
| 6 | canaries | "no canary results" | absence (OK) |
| 6 | canaries | all FACET_UNAVAILABLE | absence (OK) |
| 7 | framework_lock | "no framework.lock" | absence (OK) |
| 8 | isolation | no `.gov-runtime` | absence (OK) |
| 8 | isolation | "cannot determine git root" (`.gov-runtime` exists, git broken) | **ERROR → should be fail** |
| 9 | adoption_level | (no unmeasured state) | — |
| 10 | claude_code | (no unmeasured state) | — |
| 11 | held_out | (no unmeasured state; uses "report") | — |

| Test | File | Red reason |
|------|------|------------|
| `test_doctor_index_freshness_error_is_fail` | test_w1_27_doctor_unmeasured_r3.py | `_check_index_freshness` returns "unmeasured" on exception, not "fail"; doctor exits 0 |
| `test_doctor_canary_error_is_fail` | test_w1_27_doctor_unmeasured_r3.py | `_check_canaries` returns "unmeasured" on exception, not "fail"; doctor exits 0 |
| `test_doctor_isolation_broken_git_is_fail` | test_w1_27_doctor_unmeasured_r3.py | `_check_isolation` returns "unmeasured" when `.gov-runtime` exists but git root fails, not "fail" |
| `test_unmeasured_absence_prevents_adopted_healthy` | test_w1_27_doctor_unmeasured_r3.py | `_check_adoption_level` returns ADOPTED_HEALTHY despite unmeasured sections (only checks path-map systems) |
| `test_healthy_false_when_measurement_error` | test_w1_27_doctor_unmeasured_r3.py | `healthy` considers only "fail"/"drift", ignoring "unmeasured" from errors; healthy=true with corrupt store |

## Residuals

- **S0a-G-04**: listed as a source in the ticket; its text is not in the tree.
  Noted as a residual.

## Decision packages

None. All KPI lines are settled from the ticket sources.

## Covers coverage

| Covers item | Tests |
|-------------|-------|
| CAP-02.a (framework.lock) | `test_doctor_report_mentions_framework_lock` |
| CAP-06.a (path classification) | `test_doctor_report_mentions_path_map_coverage`, `test_full_coverage_is_healthy` |
| CAP-06.d (path-map compliance) | `test_unclassified_path_is_reported`, `test_moved_path_reference_is_reported` |
| CAP-07.a (derived state) | `test_rebuild_recreates_derived_stores`, `test_rebuild_digest_matches_store_loader`, `test_rebuild_lexical_index_is_fresh`, `test_rebuild_lexical_search_finds_tracked_text`, `test_rebuild_result_names_derived_stores_with_measured_status`, `test_rebuild_does_not_hold_lexical_schema_copy` |
| CAP-20.a (rebuild idempotent) | `test_two_rebuilds_give_the_same_digest` |
| CAP-25.a (tool registry) | `test_doctor_report_mentions_tool_versions`, `test_doctor_does_not_pass_with_wrong_tool_version` |
| CAP-38.b (recovery/rebuild check) | `test_recovery_rebuild_check_*`, `test_derived_state_deleted_and_rebuilt_gives_same_digest` |
| CAP-46.a (clone+doctor+rebuild) | `test_fresh_clone_doctor_rebuild` |
| CAP-54.a (adoption level) | `test_*_adoption_*`, `test_unmeasured_absence_prevents_adopted_healthy` |
| DEC-210/214 (Claude Code drift) | `test_*_drift*`, `test_*_failure*` in test_w1_27_drift.py |
| DEC-223 (held-out.yaml) | `test_missing_held_out_yaml_is_reported`, `test_present_held_out_yaml_is_not_reported` |
| DEC-228 (schema replacement) | All tests in test_w1_27_schema.py, revised W1-07 cases |
| DEC-265 (languages conditional) | `test_code_intelligence_enabled_without_languages_is_invalid`, `test_code_intelligence_disabled_languages_optional` |
| DEC-416 (rebuild lexical + unmeasured vs error) | All tests in test_w1_27_rebuild_r3.py, all tests in test_w1_27_doctor_unmeasured_r3.py |
| DEC-425 (unmeasured is never green) | `test_doctor_index_freshness_error_is_fail`, `test_doctor_canary_error_is_fail`, `test_doctor_isolation_broken_git_is_fail`, `test_healthy_false_when_measurement_error` |

## Test count

- **W1-27 new tests**: 49 (rounds 1–2) + 9 (round 3) = 58
- **W1-07 revised cases**: 6
- **Total**: 64
