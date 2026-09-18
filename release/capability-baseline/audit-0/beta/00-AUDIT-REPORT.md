# Iteration-0 Capability Baseline Audit: Family Beta

| Field | Value |
|---|---|
| Run | P2-AR-0002 |
| Family | beta |
| Capabilities | C1-C10, D1-D6, R1-R3 |
| Candidate | cap2-candidate-0 (57177a37ea296ece16b185874831462b6a76db18) |
| product_code_digest | bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547 |
| Contract v3 SHA-256 | 4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3 |
| Frozen gate contract SHA-256 | d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e |
| Date | 2026-09-18 |
| Verdict | FAMILY_AUDIT_COMPLETE |

## Pinned Input Verification

All pinned inputs verified:
- Candidate commit and tag match (57177a3, cap2-candidate-0).
- product_code_digest verified via `product_identity.py HEAD`.
- Contract v3 SHA-256 matches expected hash.
- Frozen gate contract SHA-256 matches ORCHESTRATOR_STATE.yaml.

## Method

1. Built `gov` in release mode in the isolated worktree.
2. Initialized a greenfield project under a disposable scratch directory.
3. Created representative governed records (project, feature, requirement, decision, task, scenario, test-obligation, interface, experiment, lesson, research) and source files under governed paths.
4. Exercised each capability bullet through CLI commands, capturing probe scripts and outputs.
5. Ran `cargo test --lib` (42 passed, 0 failed) and `cargo test --test certification` (79 passed, 0 failed).
6. Verified cross-capability interactions (K2<->D1, D1<->W6, supersession tracking, context compilation with conflicting decisions).

## Summary Table

| Capability | Status | Findings |
|---|---|---|
| C1 | PRESENT_AND_SUBSTANTIAL | - |
| C2 | PRESENT_AND_SUBSTANTIAL | - |
| C3 | PRESENT_AND_SUBSTANTIAL | - |
| C4 | PRESENT_AND_SUBSTANTIAL | - |
| C5 | PARTIAL | A0-C5-01 (ecosystem detection not auto-triggered on greenfield) |
| C6 | PRESENT_AND_SUBSTANTIAL | - |
| C7 | PRESENT_AND_SUBSTANTIAL | - |
| C8 | PARTIAL | A0-C8-01 (failure subtypes share a single record type) |
| C9 | PRESENT_AND_SUBSTANTIAL | A0-C9-01 (minor: duplicate artifact IDs in retrieved evidence) |
| C10 | PRESENT_AND_SUBSTANTIAL | - |
| D1 | PRESENT_AND_SUBSTANTIAL | - |
| D2 | PRESENT_AND_SUBSTANTIAL | - |
| D3 | PRESENT_AND_SUBSTANTIAL | - |
| D4 | PRESENT_AND_SUBSTANTIAL | - |
| D5 | PRESENT_AND_SUBSTANTIAL | - |
| D6 | PRESENT_AND_SUBSTANTIAL | - |
| R1 | PRESENT_AND_SUBSTANTIAL | - |
| R2 | PRESENT_AND_SUBSTANTIAL | - |
| R3 | PRESENT_AND_SUBSTANTIAL | A0-R3-01 (archive content not retrievable via CLI even with --include-historical) |

Status counts: PRESENT_AND_SUBSTANTIAL=17, PARTIAL=2, ABSENT=0, UNCLEAR=0, N/A_WITH_REASON=0

## AC-7 Determination

The candidate provides an executable, evidenced path to establish a provisional retrieval profile:

1. **Pluggable, separately identifiable components (D4):** Embedder (id, version, dimensions, source), reranker (provider, version), vector store (SQLite vectors table), lexical engine (FTS5 with configurable tokenizer), code intelligence (builtin generic + plugin system), retrieval router, and context compiler are all independently identifiable and replaceable where designed. The plugin system (API-0001) allows embedding and reranking plugins to be registered, governed, and invoked.

2. **Benchmark/compare/select mechanism (D5):** `gov memory benchmark` compares multiple candidate embedders/rerankers on a held-out set with Recall@K, MRR, precision@K, stale-hit rate, superseded-hit rate, symbol recall, latency, and index cost. `gov memory select` pins the chosen candidate through a decision record and triggers a full governed rebuild. A starter held-out set is auto-generated from the live index.

3. **Governed reindex/migration on profile change:** Changing the embedder pin in MEMORY_POLICY triggers a full rebuild (pin_mismatch detection in freshness and for_query). The index manifest records the exact embedder identity, and `for_query()` enforces that the live index matches the policy pin, returning EMBEDDER_MISMATCH if not.

**AC-7 is satisfied for Phase 2.** Profile selection is Phase 3.

## Key Findings

### Blocking: None

### Non-blocking:

- **A0-C5-01** (MEDIUM): Ecosystem detection returns empty for a greenfield project with Python source files under `product/`. The "language-appropriate adapters are resolved via capability registry" bullet is functional in the code path (plugins are looked up) but the auto-detection does not fire until a package manager manifest is present. This does not undermine qualification because code intelligence falls back to the builtin generic analyzer for all supported languages.

- **A0-C8-01** (LOW): Failure memory uses the generic lesson/report record types for all failure subtypes (bugs, failed approaches, wrong assumptions, retrieval misses, regressions, migration failures, tool failures). There is no dedicated per-subtype record kind with typed fields. This is functional for storage and retrieval but reduces the precision of failure-class queries. Cannot undermine qualification because the semantic retrieval can still find failure-related records through tags and content.

- **A0-C9-01** (LOW): Context packet retrieved_intelligence contains duplicate artifact IDs (2 of 12 retrieved items share IDs). The code drops per-artifact duplicates above 2 but does not suppress them entirely. This is minor and cannot undermine qualification.

- **A0-R3-01** (MEDIUM): Archive content with `default_retrieval: false` requires the `include_archive` option, but the CLI only exposes `--include-historical` (which controls superseded status filtering). The `include_archive` option is not exposed in the CLI, making archive content unretrievable through the retrieval interface even when deliberately requested. The core R3 requirement (exclusion from default retrieval) is met.

## What Could Not Be Established

- **D5 benchmark with multiple real embedder plugins:** Only the builtin embedder was tested since no external embedder plugin was available in the test environment. The benchmark mechanism was verified to exist and the comparison logic inspected in code, but end-to-end multi-plugin benchmark was not executed. This is expected for Phase 2 (profile selection is Phase 3).

- **R1/R2 full brownfield adoption flow:** The adopt command pipeline was verified to exist with all required stages (A0-A11), and the implementation was read including legacy extraction, but a full end-to-end brownfield adoption was not executed because it requires a pre-existing non-governed repository. The certification test `brownfield_adoption_end_to_end` passed, providing regression evidence.
