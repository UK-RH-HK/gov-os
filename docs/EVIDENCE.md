# Implementer test evidence — agentic-engineering-os 4.1.2 (release candidate)

Collected: 2026-09-12T02:05:29Z · commit: c0abe4c · script: `scripts/collect_evidence.sh` · raw outputs: `release/evidence/`

> This is **implementer** evidence. It does not certify the release. Status remains
> READY_FOR_INDEPENDENT_OS_VERIFICATION until an independent verifier records a verdict.

## Toolchain
```
toolchain:
rustc 1.98.1 (48a229cea 2026-09-01)
cargo 1.98.1 (797e8a9bc 2026-08-05)
Python 3.12.3
git version 2.43.0
```

## Results
| Suite | Result |
|---|---|
| Rust unit tests (gov-runtime) | test result: ok. 10 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s |
| Certification harness (7 fixtures + architectural tests) | test result: ok. 15 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 25.98s |
| Python capability plugin tests | 4 passed in 0.11s |
| Release build (`cargo build --release`) | exit 0 |

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
- upstream::upstream_export_gate_fails_closed_and_sanitises ... ok
- update::update_from_previous_release_preserves_project_and_rolls_back ... ok

## Unit tests
- lock::tests::versions_and_compat ... ok
- memory::embeddings::tests::sha1_matches_known_vector ... ok
- util::tests::hashing_is_canonical ... ok
- memory::chunking::tests::hierarchical_chunks ... ok
- util::tests::deep_helpers ... ok
- records::tests::parse_yaml_and_markdown_records ... ok
- memory::embeddings::tests::deterministic_unit_vectors ... ok
- security::secrets::tests::detects_and_redacts ... ok
- paths::tests::secret_classification_can_never_be_downgraded ... ok
- util::tests::glob_semantics ... ok

## What each certification test proves
See [docs/FIXTURES.md](FIXTURES.md) and the fixture READMEs under `fixtures/`.
