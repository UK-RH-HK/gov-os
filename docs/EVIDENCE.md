# Implementer test evidence — agentic-engineering-os 4.1.3 (repair candidate)

Collected: 2026-09-12T03:53:33Z · commit: 78f6853 · script: `scripts/collect_evidence.sh` · raw outputs: `release/evidence/`

> Implementer evidence only. Certification remains pending independent re-verification.
> Unavailable tools are reported as NOT_RUN and are never counted as evidence.

## Toolchain and tool status
```
toolchain:
rustc 1.98.1 (48a229cea 2026-09-01)
cargo 1.98.1 (797e8a9bc 2026-08-05)
Python 3.12.3
git version 2.43.0
clippy: available
rustfmt: available
python3: available
pytest: available
```

## Results
| Suite | Result |
|---|---|
| Rust unit tests (gov-runtime) | test result: ok. 14 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.40s |
| Certification harness (7 fixtures + architectural + repair regressions) | test result: ok. 35 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 51.88s |
| Python capability plugin tests | 4 passed in 0.11s |
| Clippy (`cargo clippy --all-targets`) | RAN exit=0 warnings=7 errors=0 |
| rustfmt (`cargo fmt --check`) | RAN formatted=no (diff in rustfmt.txt; formatting is advisory in this release) |
| Release build (`cargo build --release`) | exit 0 |
| Independent held-out harness rerun (unchanged, 4.1.2 verifier) | heldout rerun 2026-09-12T03:45:45Z: PASS=36, FAIL=1, INFO=1, ERROR=0 (original: PASS=12, FAIL=25, INFO=1, ERROR=0); harness unchanged; residual FAIL: HV-08b (MEDIUM, baseline embedder paraphrase) |

## Certification tests
- arch::core_crates_have_no_python_or_node_bindings ... ok
- arch::kernel_data_contains_no_language_or_toolchain_assumptions ... ok
- arch::builtin_embedder_matches_python_reference_plugin ... ok
- arch::rust_sources_never_hardcode_external_language_runtimes ... ok
- arch::ecosystem_resolution_follows_the_governed_project_not_the_os ... ok
- arch::schemas_policies_and_registries_validate_against_kernel_schemas ... ok
- arch::plugin_protocol_is_language_neutral_bash_embedder ... ok
- arch::core_runs_without_any_governed_toolchain_on_path ... ok
- greenfield::greenfield_end_to_end ... ok
- multi_machine::clone_rebuilds_identical_derived_state ... ok
- migration::path_migration_with_rollback_and_memory_rebuild ... ok
- failure_injection::injected_failures_are_detected_and_recovered ... ok
- brownfield::brownfield_adoption_end_to_end ... ok
- repair::authority_levels_are_enforced_on_executable_paths ... ok
- repair::budget_parallel_agents_threshold_raises_gate ... ok
- repair::cit_auto_simulation_and_secret_redaction ... ok
- repair::benchmark_records_evidence_and_selection_pins_through_decision ... ok
- repair::embedded_kernel_installs_without_canonical_root ... ok
- repair::context_packet_layers_and_contradiction_flags ... ok
- repair::claims_survive_full_memory_rebuild ... ok
- repair::embedder_replaceable_end_to_end_and_no_silent_fallback ... ok
- repair::freeze_writes_is_honoured_by_adopt_and_upstream ... ok
- repair::destructive_migration_requires_answered_gate_record ... ok
- repair::plugin_host_large_response_through_cli ... ok
- repair::embedder_pin_change_escalates_to_full_rebuild_without_mixed_index ... ok
- repair::reranker_hook_invoked_and_never_silently_skipped ... ok
- repair::sensitivity_classes_and_namespaces_are_enforced ... ok
- repair::implementation_prerequisites_and_symbol_route ... ok
- repair::policy_enforcement_coverage_is_complete_and_honest ... ok
- repair::update_approval_requires_presented_answered_gate ... ok
- repair::unmeasured_memory_recall_is_not_green ... ok
- repair::task_close_enforces_mutation_scope ... ok
- repair::smaller_findings_regressions ... ok
- upstream::upstream_export_gate_fails_closed_and_sanitises ... ok
- update::update_from_previous_release_preserves_project_and_rolls_back ... ok

## Unit tests
- lock::tests::versions_and_compat ... ok
- memory::embeddings::tests::sha1_matches_known_vector ... ok
- util::tests::hashing_is_canonical ... ok
- records::tests::parse_yaml_and_markdown_records ... ok
- memory::chunking::tests::hierarchical_chunks ... ok
- util::tests::deep_helpers ... ok
- memory::embeddings::tests::deterministic_unit_vectors ... ok
- security::secrets::tests::detects_and_redacts ... ok
- paths::tests::secret_classification_can_never_be_downgraded ... ok
- util::tests::glob_semantics ... ok
- capabilities::host::tests::bad_json_and_protocol_mismatch_are_reported ... ok
- capabilities::host::tests::large_stdin_request_and_stderr_flood_are_drained ... ok
- capabilities::host::tests::large_response_well_above_pipe_buffer_does_not_deadlock ... ok
- capabilities::host::tests::timeout_kills_child_promptly ... ok
