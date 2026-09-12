# Implementer test evidence — agentic-engineering-os 4.1.4 (repair candidate)

Collected: 2026-09-12T16:28:08Z · commit: c6b594b · script: `scripts/collect_evidence.sh` · raw outputs: `release/evidence/`

> Implementer evidence only. Certification remains pending independent re-verification.
> Status vocabulary: PASS | FAIL | NOT_AVAILABLE (tool missing) | NOT_RUN (not executed) | NOT_APPLICABLE (with reason).
> An unavailable tool is never counted as evidence.

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
| Rust unit tests (gov-runtime) | PASS (16 passed; 0 failed) |
| Certification harness (7 fixtures + architectural + repair regressions, 4.1.2 and 4.1.3 findings) | PASS (44 passed; 0 failed) |
| Python capability plugin tests | PASS (4 passed in 0.11s) |
| Clippy (`cargo clippy --all-targets`) | PASS (exit 0, warnings=0, errors=0; warning lines include per-crate summaries) |
| rustfmt (`cargo fmt --check`) | PASS (rustfmt --check: formatted) |
| Release build (`cargo build --release`) | PASS (exit 0) |
| First independent held-out harness rerun (unchanged, 4.1.2 verifier) | first verifier harness (4.1.2) rerun 2026-09-12T16:28:08Z: PASS=36, FAIL=1, INFO=1, ERROR=0 (original: PASS=12, FAIL=25, INFO=1, ERROR=0); harness unchanged; non-PASS: ['HV-08', 'HV-08b'] |
| Second independent held-out harness rerun (unchanged, 4.1.3 verifier) | second verifier harness (4.1.3) rerun 2026-09-12T16:28:08Z: PASS=13, FAIL=2, INFO=0, ERROR=0 (original: PASS=6, FAIL=9, INFO=0, ERROR=0); harness unchanged; non-PASS: ['NV-19', 'NV-09'] |

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
- repair2::framework_lock_is_release_identifying_and_portable ... ok
- repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent ... ok
- repair2::cit_approval_derives_only_from_an_answered_gate ... ok
- repair2::plugins_are_governed_capabilities_not_arbitrary_commands ... ok
- repair2::release_build_reproduces_released_versions_from_their_commit ... ok
- repair2::incremental_rebuild_follows_record_relocation ... ok
- repair2::project_policy_cannot_weaken_constitutional_floors ... ok
- repair2::task_close_uses_observed_mutations_not_self_attestation ... ok
- repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger ... ok
- repair::authority_levels_are_enforced_on_executable_paths ... ok
- repair::budget_parallel_agents_threshold_raises_gate ... ok
- repair::cit_auto_simulation_and_secret_redaction ... ok
- repair::claims_survive_full_memory_rebuild ... ok
- repair::context_packet_layers_and_contradiction_flags ... ok
- repair::embedded_kernel_installs_without_canonical_root ... ok
- repair::destructive_migration_requires_answered_gate_record ... ok
- repair::embedder_pin_change_escalates_to_full_rebuild_without_mixed_index ... ok
- repair::freeze_writes_is_honoured_by_adopt_and_upstream ... ok
- repair::plugin_host_large_response_through_cli ... ok
- repair::implementation_prerequisites_and_symbol_route ... ok
- repair::policy_enforcement_coverage_is_complete_and_honest ... ok
- repair::reranker_hook_invoked_and_never_silently_skipped ... ok
- repair::embedder_replaceable_end_to_end_and_no_silent_fallback ... ok
- repair::sensitivity_classes_and_namespaces_are_enforced ... ok
- repair::task_close_enforces_mutation_scope ... ok
- repair::unmeasured_memory_recall_is_not_green ... ok
- repair::smaller_findings_regressions ... ok
- repair::update_approval_requires_presented_answered_gate ... ok
- upstream::upstream_export_gate_fails_closed_and_sanitises ... ok
- update::update_from_previous_release_preserves_project_and_rolls_back ... ok
- repair::benchmark_records_evidence_and_selection_pins_through_decision ... ok

## Unit tests
- lock::tests::versions_and_compat ... ok
- memory::embeddings::tests::sha1_matches_known_vector ... ok
- policy_precedence::tests::floors_and_additive_sets ... ok
- policy_precedence::tests::pattern_matching ... ok
- util::tests::hashing_is_canonical ... ok
- memory::chunking::tests::hierarchical_chunks ... ok
- util::tests::deep_helpers ... ok
- records::tests::parse_yaml_and_markdown_records ... ok
- memory::embeddings::tests::deterministic_unit_vectors ... ok
- security::secrets::tests::detects_and_redacts ... ok
- paths::tests::secret_classification_can_never_be_downgraded ... ok
- capabilities::host::tests::bad_json_and_protocol_mismatch_are_reported ... ok
- util::tests::glob_semantics ... ok
- capabilities::host::tests::large_stdin_request_and_stderr_flood_are_drained ... ok
- capabilities::host::tests::large_response_well_above_pipe_buffer_does_not_deadlock ... ok
- capabilities::host::tests::timeout_kills_child_promptly ... ok
