# P2-AR-0042 — Repair iteration 1, round 4: WS-1 evidence map (BC-P2-02)

| Field | Value |
|---|---|
| Run | P2-AR-0042, a fresh `capability-repair` builder, WS-1, repair iteration 1, round 4. Model: Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0041 (this round). Rules from P2-HO-0031, P2-HO-0020 and P2-HO-0010 |
| Branch / base | `phase2/repair-1-r4-ws01`, from `cae2f67` (release branch recording P2-AR-0041). Its product tree is the round-3 integrated tree (merge `e4cb662`; `product_code_digest 1d3e9f59…85df7`) |
| Work commits | `5aebf23` (owners, resolver, enforcement, matrix, map), `9bafcb3` (mapping review, `owner_sources_fingerprint`), then the evidence/report commit named in the run report (`output.commit`); it changes no product file |
| Product | `product_code_digest d0c6a0d4bb82b11f458c3082c6c86a9e6ce8e46c888b02f466ca497bf595a4c9` at `9bafcb3` (and at the final work commit) |
| Class | **BC-P2-02 — `REPAIRED_CLAIMED`**, with the gaps of §9 listed for the verifier (none has zero owners) |
| Verdict | **`READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`**. `cargo build --release`: 0 warnings. `cargo test --lib` 271/0, `cargo test --test certification` 193/0 at `9bafcb3`. R1 held-out suites at their baselines (§10.2). No owner decision is needed |

This is a builder's claim with regression evidence (Contract v3 O3). It grades nothing and accepts nothing. The
evidence below is the product's own output on disposable trees and projects, plus builder tests.

---

## 1. Requirement

**BC-P2-02 (frozen gate contract AC-10; repair-delta §1).** Each of the 101 capabilities (100 numbered, plus Gate U)
names at least one evidence owner that actually runs. The owner kinds are a G0…G6 tier check, an independent held-out
suite, Human Decision Gate evidence, or release/clean-clone evidence. The handoff adds a `cargo test` path in `--lib`
or `--test certification` that is not `#[ignore]`d. The Contract v3:53-73 governed fields must be populated:

- evidence class, from :81-91;
- automated check/test ids;
- tiers ⊆ G0–G6;
- freshness triggers ⊆ :97-109;
- the independent-verification obligation;
- the other fields, where a source supports a value.

`gov contract verify` must fail with a typed error in each of these cases:

- zero owners;
- an owner id that does not resolve to a check or test that exists and runs;
- an out-of-vocabulary value;
- a governed field mutated without a recompile.

The product must generate the suite-to-contract matrix from its own map. AC-13 must still hold: compile preserves the
governed fields, and verify still refuses every round-1 mutation control. AC-10's second sentence (a changed input
invalidates prior green evidence) was built by BC-P2-03. This run records which owner proves it for each trigger class.

## 2. What changed (all inside the files P2-HO-0041 assigns)

| File | Change |
|---|---|
| `runtime/src/contracts.rs` | **Owner model and resolver.** Eight owner kinds (`OWNER_KINDS`): `check`, `doctor`, `g0`, `test`, `human-gate`, `release`, `heldout`, `obligation`. `OwnerRegistry` and `resolve_id` resolve each kind as follows. A `check:` or `doctor:` owner must be a check the scheduler catalogue declares on that surface, and a family must also be in the embedded kernel `TEST_POLICY.governance_families`. Its stated `tiers` must equal the catalogue's. A `g0:` owner is a `COMMAND_GUARDS` label whose scope is `Project`. A `human-gate:` or `release:` owner is a `COMMAND_GUARDS` label plus a `record` that is a kernel record type or schema. A `test:` owner is resolved through `test_index`. That function reads the harness's module tree from `runtime/src/lib.rs` or `tests/certification/main.rs` the way the compiler does (`mod x;` → `x.rs`/`x/mod.rs`, inline modules), with comments and literals blanked, and records `#[ignore]`. A `heldout:` owner is a `release/verification/**/heldout-tests` directory with its `Cargo.toml.txt`, and each named `binary::fn` must be a `#[test]` of that suite. An `obligation:` owner is an `AC-n` row of the frozen gate contract that assigns the work to an independent verifier or reviewer. **What the owners determine** (`derived_fields`): evidence classes, tiers, freshness triggers (the catalogue's declared input classes → `currency::contract_class_of`), the adoption and operational-audit obligations (the G5 owners) and the remediation rule. `complete_governed` fills these at compile. **Checks** (`owner_differences`): owners are well formed and placed by independence, every capability has a running owner, derived fields are exactly derived, item owners belong to their capability, and every trigger in use names an invalidation owner. **Lock** (`evidence_map_governed`): its digest is bound by `contract-source.lock` (`evidence_map_governed_sha256`). **Matrix** (`suite_to_contract`, `write_suite_to_contract`, `RunEvidence`). **`owner_sources_fingerprint`** is for a cache key (§11). **`verify`** order: … map → owners → governed digest → view → lock. **`generate`** (compile) resolves strictly and refuses before writing. **View**: owners, item owners and governed fields per capability. 9 new unit tests. The fixture helper links the owners' sources, and one existing test body was changed (§6.3) |
| `framework/schemas/governance-capability-acceptance.schema.json` | `$defs/evidence_owner` (id pattern over the eight kinds, class, tiers, record, tests, exercises), `evidence_owners`, `owner_obligation`; row `automated_checks` = owners; `independent_verification` = owners; per-item `automated_checks` = owner ids; `allowed_status` enum = frozen §4; top-level `freshness_invalidation` |
| `tests/governance/capability-evidence-map.yaml` | the governed owners of all 101 capabilities, the per-item owners and `freshness_invalidation`, written from `evidence/mapping/owner-spec.yaml` by `apply_owner_spec.py`, then `gov contract compile` |
| `framework/contracts/contract-source.lock`, `docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md` | regenerated by `gov contract compile` (never hand-edited). The compiled form `framework/contracts/governance-capability-acceptance.yaml` is unchanged |
| `cli/src/main.rs` (declared additive exception) | `gov contract matrix [--lib-results F]… [--certification-results F]… [--heldout-results F]… [--health-results F]… [--out DIR]`: the `ContractCmd::Matrix` arm, its dispatch and its `g0_label` arm. No existing line changed |
| `runtime/src/orchestration/control.rs` (declared additive exception) | `outside("contract matrix", …)` in `COMMAND_GUARDS` |
| `tests/certification/ws01r4.rs` + its `mod` line in `tests/certification/main.rs` | 4 certification tests (§6) |

No other file was edited. No test was renamed or removed. The owner source and its canonical import are unchanged
(`4c2df291…5ed3`).

## 3. How `gov contract verify` enforces BC-P2-02

After the existing faithfulness checks (import, lock, compiled form, map source-derived fields and vocabularies, schema):

1. **Owners** (`CONTRACT_EVIDENCE_OWNER_UNRESOLVED` > `_MISSING` > `_INVALID`; the details carry every difference):
   - Every owner id resolves. For check, doctor and g0 owners, the stated tiers are the tiers the product declares.
   - Every capability has at least one **running** owner. An `obligation:` owner is a future verifier's duty, so it is recorded but never counts toward this minimum.
   - An independent owner (`heldout`, `obligation`) appears only in `independent_verification`, never in `automated_checks`.
   - Every owner's class is from Contract v3:81-91 and is one its kind produces.
   - `evidence_class`, `health_scheduler_tiers`, `freshness_triggers`, `adoption_obligation`, `operational_audit_obligation` and `remediation_rule` are exactly what the owners determine.
   - A checklist item names only owners of its own capability.
   - Every freshness trigger in use has a `freshness_invalidation` entry whose owners resolve.
2. **Governed digest.** A governed value that differs from what the last `gov contract compile` bound fails with `CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED`.
3. **Sources absent.** Some trees do not carry what an owner resolves against: a release-tooling tree without `runtime/src`, `tests/certification`, `release/verification` or the gate contract. There, `verify` **defers** those owners and **discloses** them (`evidence_owners.deferred`, `not_in_this_tree`). It still resolves everything the binary itself holds (catalogue, `COMMAND_GUARDS`, kernel payload), and it still fails on an owner no tree could resolve. `gov contract compile` never defers, so no owner is bound without having been resolved. This is what keeps `ws08_r2::a_release_is_built_only_from_a_contract_bound_tree…` binding in its chain-only canonical copy.

## 4. The map: owners per capability

`gov contract verify` at `9bafcb3` returns `CONTRACT_SOURCE_BOUND` with 101 capabilities, 762 owners, 0 deferred and
nothing absent from the tree (`evidence/matrix-inputs`, `suite-to-contract.json`). The per-capability census is in
`evidence/mapping/owner-census.9bafcb3.out`, and the full matrix is in `suite-to-contract.md`.

**Owners by kind** (762): `test` 441 (lib and certification), `check` 127, `obligation` 110, `doctor` 34, `g0` 19,
`human-gate` 13, `heldout` 13, `release` 5.

**By evidence class (Contract v3:83-91)**

| Class | Owners | Capabilities carrying it |
|---|---|---|
| unit/integration/system test | 426 | 100 |
| governance health check | 161 | 74 |
| independent audit evidence | 105 | 101 (the AC-12 obligation, and AC-6 for V1-V4) |
| automated invariant/guard | 19 | 9 |
| independent held-out test | 18 | 7 |
| human-gate evidence | 13 | 13 |
| clean-clone/release evidence | 12 | 7 |
| migration/rollback evidence | 8 | 6 |
| synthetic-repository evidence | 0 | 0 (Phase 4; nothing exists to own it) |

These counts are the `evidence_owners` summary that `gov contract verify` returns (`owners_by_class`, `capabilities_by_evidence_class`), repeated in `suite-to-contract.json` → `summary.owners`.

**By tier (capabilities with at least one owner at the tier):** G0 9 · G1 44 · G2 32 · G3 25 · G4 69 · G5 74 · G6 71.
**76 capabilities have a G-tier owner.**

**The remaining 25 have no G-tier owner** (A4, C5, F3, F5, G1, H3, K1, K3, K4, M2, M3, N2, Q1, Q2, Q3, Q4, R2, S1, S2,
S4, S5, T2, V1, V2, V3). Of these:

- **9** have a human-gate, release/clean-clone or independent held-out owner: A4, F3, K1, K4, Q1, S1, S2, S4, S5.
- **16** are owned only by builder regression tests, plus the AC-12 or AC-6 obligation: C5, F5, G1, H3, K3, M2, M3, N2, Q2, Q3, Q4, R2, T2, V1, V2, V3. They are listed in §9 as a gap.

**Checklist items that name an owner:** 586 of 713. The 127 items without one are listed in the census, with counts per
capability in §9.

**The other Contract v3:53-73 fields**, filled where a source supports a value:

- `allowed_status`: the frozen gate contract §4 vocabulary. The schema enum refuses anything else.
- `applicability`: frozen AC-2/§4.
- `na_requirements`: Contract v3:514-515 and frozen AC-2/§4.
- `adoption_obligation` and `operational_audit_obligation`: Contract v3:122-123 and :126, naming the capability's G5 owners (or none, with the rule that applies then).
- `remediation_rule`: Contract v3 I3:573-575 and frozen AC-5 when a tier owner exists; I3:574 and AC-15 otherwise.
- **`severity` stays `null`.** No normative source states a per-capability severity, and the compiler may not invent one.

**Freshness triggers → owners proving invalidation** (the `freshness_invalidation` entries in the map, and the table in `suite-to-contract.md`):

| Trigger (Contract v3:97-109) | Owners | What is proven |
|---|---|---|
| governing contract/policy | `verification::currency::tests::every_contract_input_class_has_an_owner_class` (lib), `repair::embedder_pin_change_escalates_to_full_rebuild_without_mixed_index` (cert) | policy files are key classes (unit); a project-policy pin change makes the index stale and blocks close (end to end) |
| runtime/kernel implementation | `ws08_r2::an_update_over_a_defect_the_full_suite_detects_is_refused_and_rolled_back`, `currency::tests::non_file_classes_are_keyed_and_never_file_classes` | a kernel change re-runs G5 fresh; the runtime identity is a keyed class |
| schema, migration, security/sensitivity policy | `currency::tests::every_contract_input_class_has_an_owner_class` + `…snapshot_attributes_changes_to_classes_and_ignores_its_own_outputs` | class membership + class change → key change. **Unit-level only**: no end-to-end scenario changes these inputs specifically |
| tool/plugin | `every_contract_input_class_has_an_owner_class`, `ws07::every_byte_a_plugin_executes_is_bound` | class membership; a changed plugin byte fails closed |
| model/retrieval profile | `repair::embedder_pin_change_…`, `ws06::embedder_components_are_identified_bound_and_fail_closed_on_change` | stale index, blocked close, forced full re-embed |
| project path map | `ws06r3::freshness_judges_exactly_what_the_indexer_indexes`, `every_contract_input_class_has_an_owner_class` | a lifted path-map exclusion makes freshness stale |
| authoritative spec/decision | `ws05r3::stale_inputs_are_seen_propagated_at_claim_and_cleared_only_by_retest_evidence`, `ws04r2::upstream_change_reaches_completed_work`, `…snapshot_attributes…` | dependent work and evidence stale until re-test |
| relevant source files | `…snapshot_attributes…`, `failure_injection::injected_failures_are_detected_and_recovered` | key change attributed to `source`; `INDEX_STALE` blocks close |
| relevant index manifest | `currency::tests::manifest_normalisation_drops_volatile_fields_only`, `failure_injection::…` | manifest digest follows embedder/content, not volatile fields |

## 5. Routed items (P2-HO-0041 "Items routed to you")

Each was read in its report and treated as a requirement. Before mapping, the owners each report names were checked to
still exist in the integrated tree: every mapped owner resolves through the product.

| Item | Status | Where it is in the map |
|---|---|---|
| ws01-12 IP-3 (governed fields; compile preserves; verify enforces vocabularies) | done | §2-§4; AC-13 controls §6 |
| ws02 IP-WS02-19 | done | O4 → D021, `audit_reproducibility`, currency tests. O5 → G0 (`g0:task close`) plus the G1/G2/G3/G4 families, D031 and the scheduler tests. O1 and U → `product_test_health` + D030. O2 → the 17 families; F1 → `skill_regression`. L/K/N/M → `human_gate_integrity` (L2, L3), `change_control_integrity` (K2), `continuity_checkpoint_handoff` (N1, N3, W9), `model_routing_integrity` (M1, M4) |
| ws04 IP-11 | done | W1/W2/W3/W4/W5/W8/W10 → `graph::*`, `graph::lineage::*`, `graph::identity::*`, `context::manifest::*`, `context::receipt::*` tests. The families are `graph_integrity`, `context_reproducibility` and `product_traceability`. The CLI subcommands it names (`context manifest|verify|receipt`, `artefact check`) are not owners in their own right: no owner kind covers a bare command without a guard/gate/release record, and their behaviour is exercised through the tests mapped |
| ws05 IP-6 (+§5) | done | E4 → `memory::claims::tests::*`, `orchestration::claims::tests::*`, `concurrency_claims`, D017, D026. **I2 fields → the WS-5 supplementary probe: not mapped**, because a builder probe script is not a product owner. I2 is owned by `task_contract_integrity` and the tests listed |
| ws06 IP-1 | done | C3/C4/D3 → `index_content_coverage` + chunking tests. C3/C4/C9/D2 → `memory_retrieval_regression`. C5 → `code_intelligence::generic::tests::*` + indexer tests. D1 → `index_freshness`, D010, D025, `ws06r3::freshness…`. C8 → `memory::failures` + D034 |
| ws08 IP-5 | done | A2 → D003/D004/D032/`installation_authenticity`/`mutation_scope` + the `srr::*`/`ws08::*` tests. S5 atomicity → AR-0027 `heldout_srr4::e3…` |
| ws09-11 item 6 | done | R1/R2/S4/B2/T3 → adoption stage tests (`brownfield`, `migration::*`, `adopt::tests::*`). W1 plan/catalogue → `migration::adoption_dependency_proof_citations_and_rerun_identity`. Q4 → `upstream::export_gate_fails_closed_on_content_whatever_the_name` |
| r2-ws02 R3-6 | done, one part not mappable | W7 → `lineage_orphans`. BC-P2-09 → `os_binding_integrity` + D033 (F4, L3, T3). BC-P2-36 → D032 + `installation_authenticity` (A2). W1/W8 → `graph_integrity`; W5 → `product_traceability`; W4 → `context_reproducibility`; BC-P2-25 → `index_content_coverage`; Contract v3:614 → `task_contract_integrity` (I2, J2). **`contract_binding` (BC-P2-01) is not mapped to a capability**: it owns the contract chain (AC-13), and none of the 101 capabilities is "the acceptance contract binds its views". Mapping it anywhere would be invented. **G6 `gov health qualify`: not mapped**, because no test or run exercises it (§9) |
| r2-ws04 R2-14 | done | the `ws04r2` tests (C6, K1-K3, W6, N1-N3, L1, W3, F5) and the lib tests `cit::materiality`, `cit::propagation`, `context::manifest`, `graph::*` |
| r2-ws05 IP-R3-8 | done | I4/W3/E4 → `ws05::runnable…` + DAG tests. L3/I4 task gates → `ws05::gates_decide_runnability_and_completion`. W5 → `ws05::close_requires…`. E1/H4/O3/T2 → `ws05::independence…`. BC-P2-09 close → `ws05::close_observes_os_written_state…` (E1.3) |
| r2-ws06 IP-R2-4 | done | C2 → `graph_integrity`, D015, `ws06::graph_integrity_*`. D1/D4/D5 → profile tests. B1/B3/D6 → `paths::tests::*`, `recovery_rebuild`, `ws06::deleting_everything_*` |
| r2-ws08 IP-R2-WS08-11 | done | A2 → `ws08_r2` refusal, bootstrap and rewrite tests. O5 G5 update → `ws08_r2::an_update_over_a_defect…`. Release build → `ws08_r2::a_release_is_built_only_from…` (S2) |
| r2-ws09-11 IP-R2-6 | done | T1/T2/T3/S4/O3 → `migration::adoption_independence…`, `adopt::tests::*`. Q1 → `upstream::export_approval_comes_only_from…` + `human-gate:upstream prepare`. A11 G5 → `adopt::tests::a11_names…` |
| r2-ws10 IP-WS10-14 | done | H4 → `lifecycle::scenario::tests::*`; J1 → `lifecycle::research::tests::*`; J2 → `lifecycle::experiment::tests::*`. All three are also owned by `research_experiment_data_lifecycle` |
| r3-ws04 IP-R3-WS04-10 | done | `cit::binding` tests and `ws04r3::*`, each where it exercises: C1, C6, K2, W5, W6, W8, J2, K3, A5, B3, W2, W3, I2 |
| r3-ws06 IP-R3-WS06-6 | done | D1, N2, C3/C4 (`ws06r3::markdown_headings…`, chunking), C5/F4/D4 (`ws06r3::a_refused_code_intelligence…`), J1/D5 (`ws06r3::the_benchmark…`, `…the_index_holds…`), B1 (`ws06r3::the_repository_contract…`) |
| r3-ws08 IP-R3-WS08-10 | done | S6 → `ws08_r3::t2_facts…`. A2.9 → `ws08_r3::a_t2_binding_authority_installs_only…`. S2 → `kernel::tests::the_payload_declares…` + `ws08_r3::the_next_kernel_payload…`. S1 → `repair3::current_release…`. L4/S5/B3 → `ws08_r3::update_entry_guard…`. `a_binding_authority_is_not_installed_below_floor` is not mapped: it is §6 break-glass behaviour, and none of the 101 capabilities states it |
| r3-ws09-11 IP-R3-WS09-5 | done | A3 → `migrations::verify` tests + `migration::command_tests…`. B3/S4 → `migrations::executor::tests::*` + `migration::path_migration…`. S5 → `migrations::framework::tests::*`. A11 disclosure → `adopt::tests::a11…` |
| integration-3 §8 evidence-map rows | done | IP-R3-WS08-10, -WS06-6, -WS09-5 and -WS04-10, as above |

## 6. Mutation controls (typed failures) — `evidence/mutation-controls/`

### 6.1 BC-P2-02 controls through `gov contract verify` / `compile`

`owner-mutation-controls.py` → `.9bafcb3.out`, against the release `gov` (`2817913a…66ad5`). **29/29 as expected.**

- The unmutated chain binds.
- `CONTRACT_EVIDENCE_OWNER_MISSING`: zero owners (U); a capability whose only owner is an obligation (A1).
- `CONTRACT_EVIDENCE_OWNER_UNRESOLVED`:
  - a test owner renamed away (W3);
  - a test owner `#[ignore]`d in a copied certification crate (L3);
  - a check not in the catalogue (B2);
  - a check at a tier the catalogue does not declare (A3);
  - `g0:` on a command G0 does not guard (E1, `release build`);
  - a held-out test the suite lacks (A2);
  - a held-out suite that does not exist (O3);
  - `obligation:AC-10` (not an independent-verifier criterion);
  - a human-gate record type that does not exist (L2).
- `CONTRACT_EVIDENCE_MAP_DIVERGED`: an unknown owner kind (refused first by the schema's id pattern); a row evidence class, tier (G7), freshness trigger or allowed status out of vocabulary.
- `CONTRACT_EVIDENCE_OWNER_INVALID`:
  - an owner class out of vocabulary (E4);
  - an independent owner filed as builder evidence (A2);
  - an evidence class claimed without an owner (C4);
  - a tier claimed without an owner (Q2);
  - an in-vocabulary trigger no owner's inputs include (A4);
  - a trigger in use with no invalidation owner;
  - an item naming a foreign owner (A1.1).
- `CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED`: `severity` edited (O5); an owner's statement edited (W8).
- A release-tooling tree with no sources: `verify` binds and discloses its deferred owners; `compile` refuses (`_UNRESOLVED`).
- **AC-13:** `gov contract compile` over the committed chain rewrites the map byte-identically.

The first run expected `_UNRESOLVED` for the unknown kind, but the schema refuses it first (`_MAP_DIVERGED`). That
result is kept as `owner-mutation-controls.9bafcb3.first-run-expected-code-13-wrong.out`; the corrected script's run is
the record.

### 6.2 Round-1 BC-P2-01 controls (AC-13), re-run unedited

`release/capability-baseline/repair-1/ws01-12/evidence/bc-p2-01/mutation-controls.py`, run from its own directory
against the same release binary → `bc-p2-01-round1-mutation-controls.9bafcb3.out`. **20/20 PASS, with the same codes
as round 1.** It runs on chain-only copies, so it also exercises the deferral path.

### 6.3 Builder tests

**Lib** (`contracts::tests`, 9 new):

- `the_owner_resolver_lists_exactly_the_tests_the_lib_harness_runs`: the resolver equals the lib harness's own `--list` and `--list --ignored`, both ways.
- `the_resolver_reads_items_not_text`
- `owner_references_resolve_against_the_product`
- `what_the_owners_determine_is_derived_from_the_product`
- `every_capability_names_a_running_owner_and_every_owner_resolves`
- `an_owner_mutation_is_a_typed_failure` (15 mutations)
- `a_tree_without_the_owners_sources_defers_and_discloses_and_never_compiles`
- `the_matrix_is_generated_from_the_map_with_the_supplied_run_evidence`
- `the_owner_sources_fingerprint_follows_what_owners_resolve_against`

**Certification** (`ws01r4`, 4):

- the resolver equals the certification harness's own list;
- `gov contract verify` enforces the owners through the CLI (6 mutations, plus an `#[ignore]`d owner test);
- a chain-only tree discloses deferred owners and refuses to compile;
- the matrix is generated by `gov contract matrix`.

**Changed builder test:** the body of `contracts::tests::governed_evidence_values_survive_regeneration`. Its old
fixture wrote a string owner plus hand-set `evidence_class` and tiers. Under BC-P2-02, owners are objects and those
fields are derived, so the old fixture is now invalid by design. Its property is asserted unchanged:

- a governed value survives regeneration;
- a governed edit without a recompile is detected, now by the specific `CONTRACT_EVIDENCE_MAP_NOT_RECOMPILED` rather than by the view;
- data regeneration would discard is refused.

The `fixture()` helper now links the owners' sources in read-only. `bare_fixture()` is the chain-only tree.

## 7. Owners exercise their capability: one sample per gate (labelled)

**PLANTED-FAULT** means: a fault that breaks the capability is planted in a disposable governed project, and the
owner, run by the release `gov`, reports it. It did not report it on the same project before the fault.

**MUTATION** means: the product source is broken in a private copy of the tree (`git archive` under
`target/P2-AR-0042/mutants/`), and the owner test fails there. The owner passes on the unmutated copy (the control).
The tree is `5aebf23`, and none of the mutated files differs at `9bafcb3`.

| Gate | Capability | Owner | Evidence | Result |
|---|---|---|---|---|
| A | A3 | `check:path_map_compliance`, `doctor:D011` | PLANTED-FAULT: AWS-shaped key in `src/creds.rs` | both fail (critical) |
| B | B1 | `doctor:D024` | PLANTED-FAULT: `.governance-runtime` dropped from `.gitignore` | fails |
| C | C2 | `check:graph_integrity` | PLANTED-FAULT: `depends_on` a missing requirement | fails (dangling edge) |
| D | D1 | `check:index_freshness` | PLANTED-FAULT: source edited after indexing | fails (stale) |
| E | E1 | `test:lib:authority::tests::undeclared_is_level_zero_and_never_orchestrator` | MUTATION: undeclared role → level 4 | control PASSED, mutant FAILED |
| F | F4 | `check:plugin_governance` | PLANTED-FAULT: unregistered executable descriptor | fails |
| G | G2 | `check:command_contract_consistency` | PLANTED-FAULT: command-contract op mapped to an unknown CLI | fails |
| H | H2 | `check:feature_readiness` | PLANTED-FAULT: silent N/A cell | fails |
| I | I1 | `check:graph_integrity` | PLANTED-FAULT: task dependency cycle | fails |
| J | J1 | `check:research_experiment_data_lifecycle` | PLANTED-FAULT: incomplete research cited by a decision | fails |
| K | K2 | `check:change_control_integrity` | PLANTED-FAULT: COMMITTED CIT without approval | fails |
| L | L3 | `check:os_binding_integrity` | PLANTED-FAULT: hand-written ANSWERED gate | fails |
| M | M1 | `check:model_routing_integrity` | PLANTED-FAULT: task class with no routing floor | **finding raised; the check stays ok** (warning level) |
| N | N1 | `check:continuity_checkpoint_handoff` | PLANTED-FAULT: handoff naming a missing task | fails |
| O | O2 | `check:schema_invariants` | PLANTED-FAULT: decision with an invalid status | fails |
| P | P1 | `test:certification:greenfield::greenfield_end_to_end` | MUTATION: telemetry events never read | control PASSED, mutant FAILED (`tel.events > 5`) |
| Q | Q4 | `test:certification:upstream::export_gate_fails_closed_on_content_whatever_the_name` | MUTATION: opaque hex/base64 export not blocked | control PASSED, mutant FAILED |
| R | R1 | `check:legacy_authority` | PLANTED-FAULT: `.cursorrules` and `CLAUDE.md` in the active tree | fails |
| S | S2 | `release:release verify` | PLANTED-FAULT: one byte appended to a built release's `kernel/KERNEL.yaml` | as written: ok; tampered: `ok false`, `modified [KERNEL.yaml]` |
| T | T3 | `check:os_binding_integrity` | PLANTED-FAULT: hand-written adoption baseline | **finding raised; the check stays ok** |
| U | U | `check:health_slos`, `doctor:D035` | PLANTED-FAULT: orphan ACTIVE feature; secret | both fail |
| V | V1 | `test:lib:qualification_oracle::tests::a_record_missing_any_v1_v4_field_is_rejected` | MUTATION: `expected_severity` dropped from the fault's required fields | control PASSED, mutant FAILED |
| W | W7, W3 | `check:lineage_orphans`; `test:lib:context::manifest::tests::absent_wrong_type_superseded_and_non_authoritative_inputs_block` | PLANTED-FAULT: orphan requirement (finding; check stays ok). MUTATION: superseded inputs no longer blocked | finding raised; control PASSED, mutant FAILED |

Evidence files:

- `evidence/owner-faults/planted-faults.9bafcb3.out`: 20/20 detected across 18 gates.
- `release-tamper.9bafcb3.out`.
- `product-mutations.5aebf23.out`: 5/5.

The first release-tamper run used a version the build refuses (`VERSION_MISMATCH`). It is kept as
`…first-run-version-mismatch.out`.

Three of the sampled owners raise a warning-level finding: M1, T3 and W7. Each reports the planted fault, but the check
stays `ok` and blocks nothing. That is the catalogue's declared semantics for those findings, and it is stated here
rather than counted as a failure.

## 8. The suite-to-contract matrix

`suite-to-contract.md` and `suite-to-contract.json` in this directory were generated by `gov contract matrix` from the
committed map, after `gov contract verify` returned `CONTRACT_SOURCE_BOUND`. The inputs were this run's own outputs
(`--out` this directory), and nothing in the matrix was hand-written:

- `cargo test --lib` and `--test certification` at `9bafcb3`;
- the R1 held-out re-run;
- a G5 `gov health run` and `gov doctor` on a disposable bootstrap project (`evidence/matrix-inputs/`).

Each owner's row gives:

- its resolution: file and line, catalogue tiers and duty, guard class, suite or criterion;
- its tiers;
- its last-run status, read from those outputs: `PASSED`/`FAILED` for tests, `RAN: ok|findings (executed)` for checks, `RAN: p passed, f failed` for held-out suites (with the named tests' status);
- `NOT_IN_SUPPLIED_EVIDENCE` where no supplied output covers the owner (G0, human-gate and release owners);
- `OBLIGATION` for criteria discharged by the independent verification.

The run statistics are in §10.3.

## 9. Gaps for the verifier (recorded, not closed by invention)

1. **16 capabilities owned only by builder regression tests.** C5, F5, G1, H3, K3, M2, M3, N2, Q2, Q3, Q4, R2, T2, V1, V2 and V3 have no G-tier, held-out, human-gate or release owner. Their owners are tests the harness runs, which the handoff's "what actually runs" counts, and the AC-12 obligation (AC-6 for V). Under a reading of AC-10's parenthetical list that excludes builder tests, these are the capabilities without an owner of the listed kinds. No product check exists that would exercise them at a tier. What each would need:
   - C5: a family over the index's code-structural facts (symbols, refs, `TESTS` edges);
   - K3/K4: a G4 check of CIT-P materiality/radius on recorded changes;
   - Q1-Q4: a check over lesson lifecycle and export ledgers;
   - R2: a legacy-memory retirement check;
   - T2: a session-independence check over adoption and independent roles;
   - H3: a readiness-generated-work check;
   - G1: an intent-mapping check;
   - M2/M3: routing floors for reasoning and role defaults inside `model_routing_integrity`;
   - N2: a checkpoint-trigger coverage check;
   - F5: a layer-substitution check;
   - V1-V3: see item 2.
2. **G6 (`gov health qualify`) has no owner.** No test or run exercises it: `scheduler::qualification_run` validates oracle and report files (ws01-12 IP-4 is wired) but is never run. V1-V4 are owned at G6 only in principle, so they are not mapped at G6. Their Phase-2 owners are the oracle-format tests and the AC-6 independent review.
3. **127 of 713 checklist items name no owner**, per capability: H2 23, I1 14, H1 9, P1 9, D4 5, P2 5, Q1 4, S2 4, N1 4, B1/B2/B3/C6/C7/D2/F1/K1/K2/N2/R3/S3/W2/W4/W8/W12 1 each, C4/C9/C10/D3/E2/F3/H3/I2/I4/K3/O3/O5/S5/W9/W10 2-3 each. The full list is in `evidence/mapping/owner-census.9bafcb3.out`. Per-item owners are builder claims, and a verifier should sample them.
4. **Unit-level-only invalidation proofs** for the schema, migration and security/sensitivity triggers (§4).
5. **`severity` is `null` for all 101 capabilities.** No source states it.
6. `contract_binding` owns BC-P2-01/AC-13, not one of the 101 capabilities, so it is not mapped (§5).
7. Owners that only guard a command's authority were **removed in review** (`9bafcb3`). An example is `g0:readiness plan` for H3: the G0 guard decides authority, it does not exercise readiness-generated work. G0 owners remain only where the guard *is* the mechanism: A3, A5, E1, G2, I4, L4, O5, T1, W12.

## 10. Regression and R1

### 10.1 Suites (`evidence/regression/`)

| Suite | Result |
|---|---|
| `cargo build --release` at `9bafcb3` | 0 warnings (`cargo-build-release.9bafcb3.out`) |
| `cargo test --lib` at `9bafcb3` | **271 passed, 0 failed** (262 + 9 new). At `5aebf23`: 270/0 |
| `cargo test --test certification` at `9bafcb3` | **193 passed, 0 failed, 0 ignored** (189 + 4 `ws01r4`). At `5aebf23`: 193/0 |
| rustfmt (edition 2021) | `contracts.rs` and `ws01r4.rs` formatted. `rustfmt --check` on `cli/src/main.rs` and `control.rs`: 0 hunks. `tests/certification/main.rs --check` reports hunks only in untouched child modules |

`export CARGO_BUILD_JOBS=2` was set for every cargo command, and no `GOV_*` variable was set for any suite.

### 10.2 R1 held-out suites — unedited, private path (`evidence/r1-heldout/`)

The runner is `run-r1-heldout.sh`: P2-AR-0041's runner with only the run id, the labels and the private root changed.
The private root is `<worktree>/target/P2-AR-0042/r1-P2-AR-0042-private`. The `wt/srr1-r1-verify*` symlinks point only
at this worktree, and the suites are copied byte-identically, with `cmp` recorded for each.

The run was made at `9bafcb3` (0 product files differing from HEAD), against this tree's own debug `gov`.

| Suite | Baseline | `9bafcb3` | Failing tests (identical to the baselines) |
|---|---|---|---|
| AR-0027 | 26/3 | **26/3** | heldout_srr2 b1, b2; heldout_srr3 d3 |
| AR-0029 | 26/2, `ho_f` does not compile | **26/2**, `ho_f_preservation` does not compile | ho_b b3, b6 |
| AR-0031 | 27/7 | **27/7** | hx_a a1, a5, a8; hx_b b6; hx_c c2, c3; hx_d d2 |
| AR-0033 | 30/1 | **30/1** | hv_a a1 (the size pin: 84 files / 740 functions) |

- **Census:** AR-0033 `hv_a::a1`'s own independent walk of this tree finds **123 files and 2340 functions**. The round-3 integration had 123 / 2304; the 36 additional functions are this run's `contracts.rs`. `hv_a::a1` fails as expected on any tree larger than candidate 4.
- **S1:** the labelled copy `hv_a_derivation.a1-unpinned.P2-AR-0042.rs.txt` is byte-identical to P2-AR-0032's and P2-AR-0041's copies, and its only difference from the held-out original is the two size assertions, now printed. It **passes**. §6 census (derived / writers / exempt / violations):
  - human_gate_create 49/44/1/**0**
  - human_gate_approve 1/1/0/**0**
  - release_certification 1/1/0/**0**
  - trust_policy_mutation 8/1/0/**0**
  - privileged_plugin_acquisition 9/2/0/**0**
  - floor_lower_or_reset 4/1/0/**0**
  - present_below_floor_release_as_current 1/1/0/**0**

  These are identical to the round-3 integration: this run added no §6 writer.
- **S2:** AR-0033's `derive.py`, with only its ROOT line substituted, gives the same census and **0 violations** in all three splitter configurations.
- **Failure messages:** the normalised failure and panic messages of the unedited suites are **identical** to the round-3 integration's run (42 lines each, empty diff): `failure-messages-vs-integration-3.txt`.

### 10.3 Matrix statistics

`gov contract matrix` read the supplied outputs (`suite-to-contract.json` → `run_evidence_supplied`, each with its SHA-256). It
recorded the last-run status of the 762 owners as follows:

| Status | Owners |
|---|---|
| test owners | **441 PASSED**, none failed or ignored |
| governance families | 127 RAN at G5: ok (executed) |
| doctor checks | 33 RAN: ok, and 1 RAN with findings: `doctor:D032`, installation authenticity not established. That is the disclosed posture of an unprovisioned bootstrap machine, not a defect |
| held-out suites | 13 RAN at their recorded baselines. All 10 held-out tests named by owners PASSED |
| G0, human-gate and release owners | 37 NOT_IN_SUPPLIED_EVIDENCE. No supplied output records a run of the guard, gate or release command itself. Their behaviour is exercised by the tests mapped beside them, and by §7's S2 tamper for `release:release verify` |
| obligations | 110 OBLIGATION |

## 11. Remaining integration points (nothing edited outside my files for them)

- **IP-R4-WS01-1 (WS-2, `scheduler/mod.rs` `Extra::ContractSource` / `verification/reporting.rs` `contract_files`).** Add `contracts::owner_sources_fingerprint(root)` to the `contract_binding` cache key. `verify` now reads the test harnesses' module trees, the held-out suites and the gate contract. Without that input in the key, a cached green `contract_binding` could survive a renamed or ignored owner test.
- **IP-R4-WS01-2 (WS-2, `verification/reporting.rs::contract_binding`; WS-8, `release.rs::pre_release_contract`).** Carry `v["evidence_owners"]` (at least `deferred` and `not_in_this_tree`) into the family detail and into `PRE_RELEASE_CHECKS.json`, so a G5 run or a release built from a chain-only tree states which owners it could not resolve.
- **IP-R4-WS01-3 (the integrator of round 4, and every later builder).** The map names 441 tests. Renaming, removing or `#[ignore]`ing one makes `gov contract verify` fail `CONTRACT_EVIDENCE_OWNER_UNRESOLVED`, and with it `contracts::tests::the_committed_binding_chain_verifies`, the `contract_binding` family and `release build`. After merging P2-AR-0043, run `gov contract verify`. If an owner moved, update `evidence/mapping/owner-spec.yaml` (or the map's governed fields), run `apply_owner_spec.py` and then `gov contract compile`. The map is the product's claim, so it is never edited around `compile`.
- **IP-R4-WS01-4 (WS-2).** Add a test or run of `gov health qualify` with a FORMAT_SAMPLE oracle. G6 owners for V1-V4, and "G6 injects hidden artifact-flow failures" (W12.7), can then be mapped.
- **IP-R4-WS01-5 (WS-2 and the owning workstreams).** Tier owners for the 16 test-only capabilities (§9.1).
- **IP-R4-WS01-6 (WS-2).** `index_freshness` on a minimal project did not report an edited `README.md` after indexing, but did report an edited `src/lib.rs`. It may be deliberate: a narrative file's index treatment. It is recorded, not judged.

## 12. Owner decisions

None. The one reading that shapes the verdict is whether a builder test counts as an AC-10 owner (§9.1). The handoff
settles it: its "what actually runs" includes test owners. The count of capabilities without an owner of AC-10's
parenthetical kinds is stated, so a verifier can apply either reading.

## 13. Process disclosures

- Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`, fresh context. No sub-agents were used, and the owner was not contacted. I read no session or agent transcript and no user auto-memory.
- One early trial of the planted-fault harness was started by a tool call that moved it into a background task-output store. That output was **not read**. The harness was re-run with output redirected to my own files, first as a trial with the debug binary in the scratchpad, then as the recorded run with the release binary. Long commands were run with `nohup`, writing to my own files.
- `rm` is denied and was not used. Superseded outputs were renamed and kept (the two `first-run` files above). Scratch projects are under `target/P2-AR-0042/`, and superseded scratch roots were renamed `.old-*`.
- `product-mutations.5aebf23.out` was committed in `9bafcb3` while its run was still in progress. The complete file is in the final evidence commit.
- The mapping was reviewed twice. Owners that only guard authority were removed. Item claims were narrowed to what the tests assert (for example, N1's state-reference item became 9, and several family items were removed). Owners named by routed IPs were added where they exercise the capability. The final map is the one `9bafcb3` binds.
- The first `cargo` runs failed because `~/.cargo/bin` was not on the non-login `PATH`. They are kept as `target/P2-AR-0042/logs/*no-cargo-on-path*`, outside the evidence.
