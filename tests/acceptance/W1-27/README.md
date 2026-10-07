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

## Round 4 — rebuild goes through the lexical index's owner and its secrets filter; the code index's outcome is measured (DEC-440)

> KPI success 2: "rebuild recreates every derived store" [CAP-07.a, CAP-20.a, CAP-46.a]

Two things are wrong in `src/gov/rebuild/command.py` at `7b424f2b`, and the
present cases let both through:

1. `_preseed_lexical` inserts the text of every tracked file into the lexical
   tables directly and only then calls `lexical.refresh`, which finds the files
   already indexed (blob hashes match) and does not re-run the secret filter.
   A file holding a secret ends up in the index.

2. The code index entry is hardcoded as `"not_recreated"` with the constant
   reason `"no code index module exists"`, but `src/gov/codeintel/` is W1-16's
   module and has `index(root)`.

### Lexical secrets (W1-17/W1-21 own the index and its secret rule)

| Test | File | Red reason |
|------|------|------------|
| `test_rebuild_secret_file_not_in_lexical_index` | test_w1_27_rebuild_r4.py | `_preseed_lexical` inserts the secret file directly; `search(root, secret, refresh=False)` finds the secret text (1 hit from `secret_holder.py`) |
| `test_rebuild_lexical_digest_matches_owner_refresh` | test_w1_27_rebuild_r4.py | digest after rebuild differs from digest after the owner's `refresh` alone: rebuild indexes the secret file, refresh filters it out |
| `test_rebuild_stores_hold_no_secret` | test_w1_27_rebuild_r4.py | `stores_with_secrets(root)` finds the secret in `.gov-runtime/store.db` after rebuild — the secrets-indexing backstop (W1-15) fails |

### Code index (W1-16 owns the module; DEC-440)

| Test | File | Red reason |
|------|------|------------|
| `test_rebuild_codeintel_reason_is_measured` | test_w1_27_rebuild_r4.py | the reason is the hardcoded constant `"no code index module exists"` but `src/gov/codeintel/__init__.py` exists and has `index(root)` |
| `test_rebuild_codeintel_is_recreated_when_tool_answers` | test_w1_27_rebuild_r4.py | `status` is `"not_recreated"` despite `codebase-memory-mcp` being on PATH; rebuild never calls `codeintel.index(root)` |

### What each case needs

- The three lexical-secrets cases need `gitleaks` on PATH (the secret filter
  uses it); they skip when it is absent.
- `test_rebuild_codeintel_is_recreated_when_tool_answers` needs
  `codebase-memory-mcp` and `gitleaks` on PATH (`local_only`); it skips when
  either is absent.
- `test_rebuild_codeintel_reason_is_measured` needs nothing beyond the project
  copy.

### W1-16's public interface for the code index

`gov.codeintel.index(root)` builds or refreshes the code index (W1-16 README,
`src/gov/codeintel/__init__.py:98`). The tool is present when
`codebase-memory-mcp` is on PATH (W1-16 README: "The functions need the
`codebase-memory-mcp` and `gitleaks` binaries on PATH"). W1-16 cases that need
the tool are marked `local_only` and skip when it is absent.

## Covers coverage

| Covers item | Tests |
|-------------|-------|
| CAP-02.a (framework.lock) | `test_doctor_report_mentions_framework_lock` |
| CAP-06.a (path classification) | `test_doctor_report_mentions_path_map_coverage`, `test_full_coverage_is_healthy` |
| CAP-06.d (path-map compliance) | `test_unclassified_path_is_reported`, `test_moved_path_reference_is_reported` |
| CAP-07.a (derived state) | `test_rebuild_recreates_derived_stores`, `test_rebuild_digest_matches_store_loader`, `test_rebuild_lexical_index_is_fresh`, `test_rebuild_lexical_search_finds_tracked_text`, `test_rebuild_result_names_derived_stores_with_measured_status`, `test_rebuild_does_not_hold_lexical_schema_copy`, `test_rebuild_secret_file_not_in_lexical_index`, `test_rebuild_lexical_digest_matches_owner_refresh`, `test_rebuild_stores_hold_no_secret`, `test_rebuild_codeintel_reason_is_measured`, `test_rebuild_codeintel_is_recreated_when_tool_answers` |
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
| DEC-440 (rebuild through owner + measured code index) | All tests in test_w1_27_rebuild_r4.py |

## Round 5 — doctor finds tools at their registered locations and excludes historical records from the stale-path check (DEC-448)

> KPI success 1: "doctor reports pinned vs found tool versions" [CAP-25.a]
> KPI success 3: "path-map compliance checked by doctor" [CAP-06.d]

DEC-448 (owner, 2026-10-07) adds two things:

1. Each tool is checked at its registered location (the PATH prefix of DEC-202
   and the registry's paths), not only on PATH.
2. Historical records (the register, CIT records, bootstrap.md, archived
   sources) are excluded from the stale-path check.

### Measured rebuild times (DEC-440 motivation)

| Fixture | Tracked files | Rebuild time |
|---------|--------------|--------------|
| Full working tree | ~955 | 157.4 s |
| Tiny project (`make_rebuild_project`) | 3 | 2.5 s |

The 30 s timeout made 18 cases fail; they are revised to use tiny projects
with `run_gov_with_code` (code root separated from the project directory).

### Revised cases (18 rebuild/recovery cases use tiny projects)

| Test | File | Revision reason |
|------|------|-----------------|
| `test_rebuild_is_an_act_command` | test_w1_27_rebuild.py | revised after implementation: rebuild goes through the lexical index's owner and its secrets filter (DEC-440); the fixture's size, not the behaviour, made it time out |
| `test_rebuild_recreates_derived_stores` | test_w1_27_rebuild.py | (same) |
| `test_two_rebuilds_give_the_same_digest` | test_w1_27_rebuild.py | (same) |
| `test_fresh_clone_doctor_rebuild` | test_w1_27_rebuild.py | (same) |
| `test_rebuild_needs_only_git` | test_w1_27_rebuild.py | (same) |
| `test_rebuild_digest_matches_store_loader` | test_w1_27_rebuild.py | (same) |
| `test_rebuild_lexical_tables_exist_after_rebuild` | test_w1_27_rebuild_r2.py | (same) |
| `test_rebuild_names_unreconstructed_stores` | test_w1_27_rebuild_r2.py | (same) |
| `test_rebuild_envelope_has_digest` | test_w1_27_rebuild_r2.py | (same) |
| `test_rebuild_lexical_index_is_fresh` | test_w1_27_rebuild_r3.py | (same) |
| `test_rebuild_lexical_search_finds_tracked_text` | test_w1_27_rebuild_r3.py | (same) |
| `test_rebuild_result_names_derived_stores_with_measured_status` | test_w1_27_rebuild_r3.py | (same) |
| `test_rebuild_secret_file_not_in_lexical_index` | test_w1_27_rebuild_r4.py | (same) |
| `test_rebuild_lexical_digest_matches_owner_refresh` | test_w1_27_rebuild_r4.py | (same) |
| `test_rebuild_stores_hold_no_secret` | test_w1_27_rebuild_r4.py | (same) |
| `test_rebuild_codeintel_reason_is_measured` | test_w1_27_rebuild_r4.py | (same) |
| `test_rebuild_codeintel_is_recreated_when_tool_answers` | test_w1_27_rebuild_r4.py | (same) |
| `test_derived_state_deleted_and_rebuilt_gives_same_digest` | test_w1_27_recovery_check.py | (same) |
| `test_recovery_rebuild_command_exits_nonzero_on_tampered_store` | test_w1_27_recovery_check_r2.py | (same) |

### New cases — tools at registered locations (DEC-448, DEC-202)

Doctor already runs each tool's `install` command, which may contain a PATH
prefix (e.g. `PATH=~/.nvm/.../bin:$PATH node --version`).  That mechanism
already finds tools at their registered location.  All five cases are green
on the current implementation.

| Test | File | Red reason |
|------|------|------------|
| `test_tool_at_registered_location_passes` | test_w1_27_doctor_r5.py | (green: doctor runs the install command whose PATH prefix finds the tool at its registered location) |
| `test_tool_at_registered_location_wrong_version_fails` | test_w1_27_doctor_r5.py | (green: doctor runs the install command, gets the wrong version, fails correctly) |
| `test_tool_at_empty_registered_location_fails` | test_w1_27_doctor_r5.py | (green: doctor runs the install command which fails because nothing is at the location, then fails correctly) |
| `test_tool_without_registered_location_found_on_path` | test_w1_27_doctor_r5.py | (green: the PATH lookup already works; this case confirms the fallback) |
| `test_doctor_does_not_modify_path` | test_w1_27_doctor_r5.py | (green: doctor is a read command and does not alter PATH or the project) |

### New cases — historical records excluded from stale-path check (DEC-448)

| Test | File | Red reason |
|------|------|------------|
| `test_stale_path_in_historical_record_is_not_reported[register]` | test_w1_27_doctor_r5.py | doctor checks all tracked files including `docs/DECISION_REGISTER.md`; historical records are not excluded |
| `test_stale_path_in_historical_record_is_not_reported[cit-records]` | test_w1_27_doctor_r5.py | doctor checks all tracked files including `docs/changes/`; historical records are not excluded |
| `test_stale_path_in_historical_record_is_not_reported[bootstrap]` | test_w1_27_doctor_r5.py | doctor checks all tracked files including `governance/project/bootstrap.md`; historical records are not excluded |
| `test_stale_path_in_historical_record_is_not_reported[archived-sources]` | test_w1_27_doctor_r5.py | doctor checks all tracked files including `docs/source/`; historical records are not excluded |
| `test_stale_path_in_live_document_is_reported` | test_w1_27_doctor_r5.py | (should pass: the stale-path check already reports moved paths in live documents) |
| `test_stale_path_section_counts_excluded_historical` | test_w1_27_doctor_r5.py | doctor does not report how many files were excluded as historical |

### Path-map and historical marking — what couldn't be settled

The path-map schema has a top-level `state_class` whose enum includes
`HISTORICAL` (in `common.schema.json`), but **no per-namespace or per-file
state class**.  Namespace fields are: `paths`, `memory_class`, `sensitivity`,
`permitted_roles`, `retention`, `export_policy`, `embedding_policy`,
`provenance`, `deletion_rebuild` — none marks a file as historical.

The `HISTORICAL` state class is used in individual record frontmatter, but
DEC-448's four kinds are not all records with YAML frontmatter (the register
and bootstrap.md are plain Markdown, `docs/source/` is a directory tree).

**The path-map has no field or entry kind that marks a file as historical.**
The cases identify the four kinds by the paths the decision names.

### Covers coverage

| Covers item | Tests |
|-------------|-------|
| CAP-25.a (tool registry) | `test_tool_at_registered_location_passes`, `test_tool_at_registered_location_wrong_version_fails`, `test_tool_at_empty_registered_location_fails`, `test_tool_without_registered_location_found_on_path`, `test_doctor_does_not_modify_path` |
| CAP-06.d (path-map compliance) | `test_stale_path_in_historical_record_is_not_reported[*]`, `test_stale_path_in_live_document_is_reported`, `test_stale_path_section_counts_excluded_historical` |
| DEC-448 (tools at registered locations + historical exclusion) | All tests in test_w1_27_doctor_r5.py |
| DEC-202 (PATH prefix for Node 22 tools) | `test_tool_at_registered_location_passes` |
| DEC-440 (rebuild through lexical owner) | All 18 revised rebuild/recovery cases |

## Round 6 — tools found under registered prefixes and never pass unverified (DEC-440, DEC-448, DEC-452)

> KPI failure 1: "doctor passes with a tool at the wrong version" [CAP-25.a]

| Test | File | Red reason |
|------|------|------------|
| `test_tool_found_under_another_entrys_prefix` | test_w1_27_doctor_r6.py | doctor only looks under the tool's own prefix; for an entry with no prefix it falls back to PATH, finding the system python3 at the wrong version |
| `test_tool_absent_from_all_prefixes_found_on_path` | test_w1_27_doctor_r6.py | (green: PATH fallback works) |
| `test_own_prefix_wins_over_other_entrys_prefix` | test_w1_27_doctor_r6.py | (green: own prefix already wins) |
| `test_tool_no_version_no_hash_not_ok` | test_w1_27_doctor_r6.py | code sets ok=true when version command fails and hash does not match |
| `test_tool_no_version_hash_match_ok` | test_w1_27_doctor_r6.py | (green: hash match passes) |
| `test_tool_version_raises_no_hash_not_ok` | test_w1_27_doctor_r6.py | code catches version-command failure and sets ok=true regardless of hash |
| `test_tool_version_mismatch_fails_despite_hash_match` | test_w1_27_doctor_r6.py | (green: version mismatch already fails for binary tools) |

## Round 7 — an entry without a binary passes by a version compared or a hash computed, never by a folder that exists (DEC-452)

> KPI failure 1: "doctor passes with a tool at the wrong version" [CAP-25.a]
> DEC-452: a tool passes only when the version read equals the pin, or the
> file's hash equals the pinned hash; a tool for which neither can be
> established fails, with the reason.
> DEC-425: a field that says "matched" when nothing was compared is a false record.

Round 6's cases test binary tools on PATH.  No case before round 7 tests the
six entries that have no binary (`NO_BINARY_TOOLS`: superpowers, pyyaml,
sqlite-vec, qwen3-embedding, reranker-venv, reranker).  The current code
passes every one as soon as a folder exists (or a module imports), with
`sha256_match: true` and no hash computed, and with no version comparison
for pyyaml.

### Cases — vendored folder (superpowers)

| Test | File | Red reason |
|------|------|------------|
| `test_vendored_folder_wrong_content_sha256_match_false` | test_w1_27_doctor_r7.py | code says `sha256_match: true, ok: true` when the vendor folder exists, without computing the DEC-199 digest |
| `test_vendored_folder_wrong_content_has_reason` | test_w1_27_doctor_r7.py | code gives no `reason` field; the folder's existence is enough for `ok: true` |
| `test_vendored_folder_right_content_passes` | test_w1_27_doctor_r7.py | (green: code says `sha256_match: true, ok: true` regardless, correct by accident) |
| `test_vendored_folder_absent_not_ok` | test_w1_27_doctor_r7.py | (green: the existing fallback correctly returns `ok: false`) |

### Cases — version compared (pyyaml)

| Test | File | Red reason |
|------|------|------------|
| `test_python_package_wrong_version_not_ok` | test_w1_27_doctor_r7.py | code reads `yaml.__version__` (6.0.1) but returns `ok: true` without comparing it to the pin 99.99.99 |
| `test_python_package_right_version_ok` | test_w1_27_doctor_r7.py | (green: code says `ok: true` regardless, correct here) |

### Cases — distribution-package hash (DEC-425)

| Test | File | Red reason |
|------|------|------------|
| `test_distribution_package_sha256_match_not_true` | test_w1_27_doctor_r7.py | code says `sha256_match: true` without computing any hash; the registered hash is of a .deb package not on the machine |

The expected value of `sha256_match` for a distribution-package hash is `false`
or a value that says "not comparable" (e.g. `"not_comparable"` or `"skipped"`);
the assertion accepts any value that is not `True`.

### Cases — file under the home (DEC-452, DEC-425)

| Test | File | Red reason |
|------|------|------------|
| `test_home_tool_wrong_sha256_not_ok[sqlite-vec]` | test_w1_27_doctor_r7.py | code says `sha256_match: true` when `~/.local/lib/.../sqlite_vec` exists, without hashing `vec0.so` |
| `test_home_tool_wrong_sha256_not_ok[qwen3-embedding]` | test_w1_27_doctor_r7.py | code says `sha256_match: true` when `~/.ollama/models` exists, without hashing the model blob |
| `test_home_tool_wrong_sha256_not_ok[reranker-venv]` | test_w1_27_doctor_r7.py | code says `sha256_match: true` when the venv dir exists, without hashing the freeze output |
| `test_home_tool_wrong_sha256_not_ok[reranker]` | test_w1_27_doctor_r7.py | code says `sha256_match: true` when the HF hub model dir exists, without hashing `model.safetensors` |

### Residual — generic kernel knows six tool names

The four home-based tools (sqlite-vec, qwen3-embedding, reranker-venv, reranker)
can only be tested under the six real names because the code dispatches on
`name in NO_BINARY_TOOLS`.  Their checks use `_real_home()` (`pwd.getpwuid`),
which ignores the sandbox's HOME.  On this machine, where the real tools are
installed, the code finds the real installation and falsely says
`sha256_match: true`; on a clean machine without these tools, the code falls to
absent and the tests pass (masking the bug).  After the fix (the code should use
HOME or accept a configurable home), the tests will reliably use fake content
under the sandbox home.  No case reads the real home's models; no case hashes a
large real file.

### Covers coverage

| Covers item | Tests |
|-------------|-------|
| CAP-25.a (tool registry) | All tests in test_w1_27_doctor_r7.py |
| DEC-452 (verified pass for no-binary tools) | All tests in test_w1_27_doctor_r7.py |
| DEC-425 (false record) | `test_vendored_folder_wrong_content_sha256_match_false`, `test_distribution_package_sha256_match_not_true`, `test_home_tool_wrong_sha256_not_ok[*]` |
| DEC-199 (vendored folder digest) | `test_vendored_folder_wrong_content_sha256_match_false`, `test_vendored_folder_right_content_passes` |

## Follow-up — the move table and the old cli tree are historical; an old path inside its new path is no stale reference (DEC-456)

> KPI success 3: "path-map compliance checked by doctor" [CAP-06.d]

DEC-456 (owner, 2026-10-07) amends DEC-448's set of historical records:

1. `docs/SOURCES.md` is a historical table of moves: left out of doctor's
   stale-path check.
2. The old `cli/` tree is legacy code (the live CLI is `src/gov/cli/`):
   treated as historical and left out of the check.
3. An occurrence of an old path that is only a part of its own new path,
   in the file that names the new path, is not a stale reference.  A file
   that names the old path on its own (not as the tail of the new path)
   is still reported, also when the same file names the new path elsewhere.

`historical_excluded` counts the number of files left out of the stale-path
check as historical records (round 5 README, DEC-448).  On this repository
after the one rebuild, doctor reported `historical_excluded: 0` although the
register is full of old paths.

### Point 1 — docs/SOURCES.md is historical

| Test | File | Red reason |
|------|------|------------|
| `test_stale_path_in_sources_md_is_not_reported` | test_w1_27_path_compliance_r2.py | doctor checks all tracked files including `docs/SOURCES.md`; the move table is not excluded from the stale-path check |
| `test_stale_path_in_live_document_not_sources_is_reported` | test_w1_27_path_compliance_r2.py | (should pass: the stale-path check already reports moved paths in live documents) |

### Point 2 — the old cli/ tree is historical

| Test | File | Red reason |
|------|------|------------|
| `test_stale_path_in_old_cli_tree_is_not_reported` | test_w1_27_path_compliance_r2.py | doctor checks all tracked files including `cli/`; the old CLI tree is not excluded from the stale-path check |
| `test_stale_path_in_src_gov_cli_is_reported` | test_w1_27_path_compliance_r2.py | (should pass: `src/gov/cli/` is the live CLI and is checked by the stale-path check) |

### Point 3 — an old path inside its new path is not a stale reference

| Test | File | Red reason |
|------|------|------------|
| `test_old_path_inside_its_new_path_is_not_stale` | test_w1_27_path_compliance_r2.py | doctor reports the old path because it appears as a substring of the text even when it is only part of its own new path |
| `test_old_path_standalone_is_stale_when_new_path_elsewhere` | test_w1_27_path_compliance_r2.py | (should pass: a standalone old path is reported even when the same file names the new path elsewhere) |

### historical_excluded count

| Test | File | Red reason |
|------|------|------------|
| `test_historical_excluded_nonzero_when_historical_holds_old_path` | test_w1_27_path_compliance_r2.py | `historical_excluded` is 1 (the register only, from DEC-448); it should be >= 3 because DEC-456 adds `docs/SOURCES.md` and `cli/` to the historical set, and the count must include them |

### Covers coverage

| Covers item | Tests |
|-------------|-------|
| CAP-06.d (path-map compliance) | All tests in test_w1_27_path_compliance_r2.py |
| DEC-456 (move table + old cli + sub-path) | All tests in test_w1_27_path_compliance_r2.py |
| DEC-448 (historical records) | `test_historical_excluded_nonzero_when_historical_holds_old_path` |

## Test count

- **W1-27 new tests**: 49 (rounds 1–2) + 9 (round 3) + 5 (round 4) + 11 (round 5) + 7 (round 6) + 11 (round 7) + 7 (follow-up DEC-456) = 99
- **W1-27 revised cases (round 5)**: 18 (rebuild/recovery using tiny projects)
- **W1-07 revised cases**: 6
- **Total**: 105
