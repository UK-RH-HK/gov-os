# Synthetic certification fixtures

All fixtures are synthetic; none contain real customer, product or credential material (the "secrets" are the
well-known AWS documentation example key and obviously fake tokens). Each fixture directory has a README with the
hazards it contains and the scenario that exercises it; the harness is `tests/certification/`. The documented first
run is "provision, then install": every scenario machine is provisioned with the suite's throw-away test root
(`tests/certification/common.rs::provision`) and installs releases signed under it; a scenario about the unprovisioned
posture itself says so and uses `setup_fixture_unprovisioned`.

| # | Fixture | Governed language(s) | Scenario file | Proves |
|---|---|---|---|---|
| 1 | `fixtures/greenfield` | Rust (Cargo) | `greenfield.rs` | init, ideation → scenarios → readiness gaps → generated tasks in one DAG, implementation gated on readiness, deterministic context packet, independent test obligation, CIT with human gate (INV-008), retest propagation, native `cargo test`, routing evidence, telemetry, checkpoints/watchdog, fresh-agent continuation, HEALTHY conformance |
| 2 | `fixtures/brownfield` | Python + TypeScript, dirty | `brownfield.rs` | A0–A11 with independence gates; legacy rules/chat/index retired (INV-004); secrets never indexed or extracted (INV-009); contradictions + duplicate ids surfaced, resolved by CIT (R5 gate); remediation iteration → adopted verdict |
| 3 | `fixtures/migration` | Python + TypeScript | `migration.rs` | inventory/classification/map/plan, review independence, batched moves with link and import rewrites, byte-identical batch rollback, independent verification, legacy extraction, memory built after path stabilisation on canonical paths |
| 4 | `fixtures/update` | none (governance only) | `update.rs` | synthetic 4.1.1 → current release (stored synthetic payload): CIT-P check, human gate, migration ops, overlay preserved, `spec/` untouched (INV-013), adapters regenerated, rollback byte-for-byte |
| 5 | `fixtures/upstream-learning` | none | `upstream.rs` | export gate: scope, secrets, raw code, identifiers, forbidden paths, approval, remote transport refusal, outbound allowlist, ledger, inbox never leaks |
| 6 | `fixtures/multi-machine` | Rust | `multi_machine.rs` | clone without runtime → the second machine is provisioned and verifies the pinned release → doctor → rebuild → identical manifest hash, status and deterministic context hash. `ws03_r3.rs` adds the T2 continuity scenario (P2-ADJ-0002): gates, decisions, CIT state, plugin registrations and governed evidence written on one of the owner's provisioned machines are honoured on another after a clone/pull, and refused from an unprovisioned machine, a machine without the owner's binding authority, another owner's machine and a hand edit |
| 7 | `fixtures/failure-injection` | Rust | `failure_injection.rs` | 13 injected faults detected by doctor/suite and repaired by recovery primitives (see fixture README table) |
| — | architectural | Rust + Python | `arch.rs` | no toolchain coupling (core runs with only `git` on PATH), language-neutral kernel data, bash plugin satisfies API-0001, Rust/Python embedder bit-identical, ecosystem resolution per project, all kernel data + canonical records validate against schemas |

## Repair regression scenarios (4.1.3)
`tests/certification/repair.rs` adds one builder regression test per verifier root cause on top of the seven fixtures:
embedder replaceable end-to-end with no silent fallback (C1), pin change escalates to a full rebuild and mixed indexes
are detected (H1), reranker hook and benchmark/selection through a decision (H7), unmeasured held-out sets are never
green, authority levels on executable paths (H3), mutation scope at task close (H4), claims survive rebuilds (H2),
budget gate on parallel claims, destructive gate records vs. `--gate-answer` (H6), sensitivity classes and namespace
roles (H5), CIT auto-simulation + secret redaction, update approval gate, freeze on adoption/upstream, context
authority layers, implementation-task prerequisites + bare-identifier symbol route, embedded kernel, policy coverage
map, and a plugin response larger than the pipe buffer through the CLI (C2; unit tests in `capabilities/host.rs`).
`fixtures/update/previous-release/4.1.1/` is a stored synthetic 4.1.1 payload (108 files, `SYNTHETIC.md`) used by the
framework-update fixture instead of deriving the previous release in-test (M16).

## Second repair iteration scenarios (4.1.4)
`tests/certification/repair2.rs`: gate-derived CIT approval with every bypass route (unanswered, declined, forged
approval object, revoked gate, stale re-answer, insufficient role, automatic path never human); constitutional
precedence (authority/sensitivity/gate/change-control/export weakening refused, strengthening applied, exceptions
need a decision, doctor D027 / suite / context packet); governed plugins (malformed, unregistered, unauthorised
role, pin drift, declared pin, approved_roles, elevated-permission registration gate, health, registry); portable
release-identifying `framework.lock` on three install paths; a genuine 4.1.2 payload updated through 4.1.3 to 4.1.4
with template reconciliation, then two ledgered rollbacks; observed mutation scope at close; record relocation
under incremental rebuild; interface/kernel-YAML/migration-substance consistency; release reproduction from the
recorded commit. The greenfield fixture now carries a realistic `.gitignore` (`target/`, `Cargo.lock`).

## Third repair iteration scenarios (4.1.5)
`tests/certification/repair3.rs`: plugin descriptors can never authorise themselves (self-declared `approved_roles`,
forged provenance, everything at once, registration by an authorised role, edited descriptor, version drift, identity
spoofing, orphan registration, elevated permissions with and without an answered gate — each checked for L0, L1 and L4
roles and for actual command execution during `rebuild-memory`); constitutional floors require a verified kernel
(precedence and security tampering, refused overrides, every mutating path refused with `KERNEL_TAMPERED`, D003/D004/
D029 diagnostics, manifest rewrite, the L4+ override gate and its binding to one kernel state, restoration);
policy exceptions require a real governing decision (nonexistent, wrong type, out of scope, superseded, rejected,
revoked, expired, insufficient authority, wrong project, and constitutional floors that no exception can reach); and a
trust-boundary sweep (self-certified tool security review, forged approval decision, self-attested mutation report,
hand-written plugin registry entry).

## Repair iteration 1 (Phase 2) builder scenarios
`tests/certification/ws03.rs`, `ws03_r3.rs`, `ws04r2.rs`, `ws05.rs`, `ws06.rs`, `ws07.rs`, `ws08.rs`, `ws08_r2.rs` hold one
test per repaired class: acting-role resolution and the G0 guard, the owner-signed human channel, T2 binding and its
cross-machine continuity, policy precedence on older kernels, CIT approval bound to content and impact, materiality,
change propagation and continuity, runnable derivation and the ordered close, recorded authorship, graph integrity and
retrieval-profile governance, executable-plugin registration and byte binding, tool approval bound to the installation,
admission on unprovisioned machines and the bootstrap marking, the operational store of the emergency controls and the
generated provider lifecycle hooks. They are builder regression evidence (Contract v3 O3), not acceptance evidence.
