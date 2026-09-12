# Synthetic certification fixtures

All fixtures are synthetic; none contain real customer, product or credential material (the "secrets" are the
well-known AWS documentation example key and obviously fake tokens). Each fixture directory has a README with the
hazards it contains and the scenario that exercises it; the harness is `tests/certification/`.

| # | Fixture | Governed language(s) | Scenario file | Proves |
|---|---|---|---|---|
| 1 | `fixtures/greenfield` | Rust (Cargo) | `greenfield.rs` | init, ideation → scenarios → readiness gaps → generated tasks in one DAG, implementation gated on readiness, deterministic context packet, independent test obligation, CIT with human gate (INV-008), retest propagation, native `cargo test`, routing evidence, telemetry, checkpoints/watchdog, fresh-agent continuation, HEALTHY conformance |
| 2 | `fixtures/brownfield` | Python + TypeScript, dirty | `brownfield.rs` | A0–A11 with independence gates; legacy rules/chat/index retired (INV-004); secrets never indexed or extracted (INV-009); contradictions + duplicate ids surfaced, resolved by CIT (R5 gate); remediation iteration → adopted verdict |
| 3 | `fixtures/migration` | Python + TypeScript | `migration.rs` | inventory/classification/map/plan, review independence, batched moves with link and import rewrites, byte-identical batch rollback, independent verification, legacy extraction, memory built after path stabilisation on canonical paths |
| 4 | `fixtures/update` | none (governance only) | `update.rs` | synthetic 4.1.1 → 4.1.2: CIT-P check, human gate, migration ops, overlay preserved, `spec/` untouched (INV-013), adapters regenerated, rollback byte-for-byte |
| 5 | `fixtures/upstream-learning` | none | `upstream.rs` | export gate: scope, secrets, raw code, identifiers, forbidden paths, approval, remote transport refusal, outbound allowlist, ledger, inbox never leaks |
| 6 | `fixtures/multi-machine` | Rust | `multi_machine.rs` | clone without runtime → doctor → rebuild → identical manifest hash, status and deterministic context hash |
| 7 | `fixtures/failure-injection` | Rust | `failure_injection.rs` | 13 injected faults detected by doctor/suite and repaired by recovery primitives (see fixture README table) |
| — | architectural | Rust + Python | `arch.rs` | no toolchain coupling (core runs with only `git` on PATH), language-neutral kernel data, bash plugin satisfies API-0001, Rust/Python embedder bit-identical, ecosystem resolution per project, all kernel data + canonical records validate against schemas |
