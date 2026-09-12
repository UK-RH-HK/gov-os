# Independent OS Verification Report — agentic-engineering-os 4.1.2 (release candidate)

| | |
|---|---|
| **Verdict** | **OS_RELEASE_CANDIDATE_REJECTED** (repairable; precise repair delta in §11) |
| Verifier | Independent Governance OS Verifier and Test Author, fresh session, no builder context (Claude Fable 5.1) |
| Date | 2026-09-12 |
| Candidate | commit `8ad06be`, release payload `release/releases/4.1.2` (release_commit `f709834`, release_hash `9964830b…e324`) |
| Toolchain | rustc/cargo 1.98.1, Python 3.12.3 (harness only), git 2.43.0, Linux x86_64 |
| Independence | Builder evidence was not trusted. Clean `cargo clean` + rebuild; builder suite re-executed; 37 verifier-authored black-box scenarios driven only through the `gov --json` contract (API-0002) |
| Held-out harness | `release/verification/4.1.2/heldout/harness.py`, results `heldout/results.json`, first-run log `heldout/run-full.log` |

## 0. Summary

The candidate is a real, substantial implementation: a Rust deterministic core (~8.2k dense lines, libc-only binary) and `gov` CLI, a language-neutral kernel payload, a working init / adopt (A0–A11) / update / rollback / release / upstream pipeline, SQLite+FTS5 derived memory that rebuilds bit-identically from Git, fail-closed secret exclusion on the index side, and seven synthetic fixtures whose harness reproduces cleanly (15/15 certification tests, 10/10 unit tests, 4/4 plugin tests on my clean rebuild).

It is rejected because the held-out tests expose two CRITICAL and seven HIGH defects, several of which are architectural rather than incidental:

1. **The embedding model is not replaceable in practice.** Retrieval embeds every query with the built-in hashed n-gram embedder regardless of the embedder pinned in the index manifest (`runtime/src/retrieval/mod.rs:108`). With a plugin embedder actually used for the index, 0/4 exact-title queries rank their own record first, and the ranking is bit-identical to what the built-in query embedding predicts (HV-01).
2. **The capability plugin host deadlocks on any response larger than the OS pipe buffer** (`runtime/src/capabilities/host.rs`: polls `try_wait()` until exit before reading stdout). A 300 KB response takes the full timeout and fails (HV-36). A real 512-dim embedder answering a 256-text batch produces ~1 MB, so no real embedding or reranking plugin can work at repository scale through API-0001.
3. **Declared policy is not enforced.** Twenty kernel policy keys are never read by the core, including `AUTHORITY_POLICY.authority_levels_required` (an L0 read-only auditor can propose, approve and execute a CIT; HV-03), `SECURITY_POLICY.never_index_classes` (restricted-class material is indexed and retrieved; HV-09), `CHANGE_POLICY.auto_simulate_triggers`, `TEST_POLICY.implementation_task_requires` and all `BUDGET_POLICY` thresholds.
4. **Deterministic state and derived state are conflated for claims**: a full `gov rebuild-memory` (also run by `gov recover`, A10 and the deep suite) silently drops all session claims, after which a second session can claim an in-progress task (HV-05).
5. **Mutation scope is not enforced at task close** (HV-04), **destructive migration batches are gated by a CLI flag rather than an answered gate** (HV-29), and **an embedder pin change leaves a mixed 512/64-dimension index that the manifest, freshness and doctor all report as healthy** (HV-07).
6. **No reranker hook and no benchmark/selection mechanism** exist for the unresolved embedding/reranker choice (HV-02, HV-08b); the memory regression family is green with zero held-out queries (HV-20).

None of these requires an architectural rewrite. The repair delta (§11) is bounded and testable with the shipped held-out harness.

## 1. Reproduction of builder evidence (independent rerun)

| Suite | Builder claim | Verifier rerun (clean `cargo clean`) |
|---|---|---|
| `cargo build --release` | exit 0 | exit 0, 0 compiler warnings |
| Unit tests (gov-runtime) | 10 passed | 10 passed |
| Certification harness | 15 passed | 15 passed (26.05 s) |
| Python plugin tests | 4 passed | 4 passed |
| Clippy diagnostics | `release/evidence/clippy-diagnostic-count.txt` = 1 | **evidence defect**: cargo-clippy is not installed; the "1" is the line `error: 'cargo-clippy' is not installed` counted as a diagnostic. No clippy run has ever occurred. |
| `gov release verify release/releases/4.1.2` | — | ok: 113 files, no modified/missing/added, release_hash matches kernel |
| Released payload vs `framework/`+`migrations/`+`tools/` at HEAD | — | identical (0 differences) |
| Core needs no Python/Node | arch test | confirmed: `ldd` shows libc/libm/libgcc only; HV-25 runs init/status/continue/audit/doctor with only `git` on PATH |

## 2. Answers to the mandatory questions

1. **Substantially complete relative to the governing documents?** No. The control-plane skeleton, repository intelligence, adoption engine, rebuildable memory and release mechanics are substantial. The Development Knowledge Fabric's replaceable-component promise, policy enforcement and several security boundaries are PARTIAL; reranking, MCP, lesson clustering/FCP and benchmark-based model selection are ABSENT.
2. **PARTIAL/ABSENT/UNCLEAR pillars:** see §3. PARTIAL: authority/policy engine, portable CLI, tool registry, checkpoint triggers, semantic memory, code intelligence, temporal memory, context compiler authority layering, sensitive-path handling, destructive-action controls, observability (tokens/cost), migration dependency graph, update fixture (synthetic prior release derived in-test). ABSENT: reranker wiring, embedder/reranker benchmark mechanism, MCP server, lesson clustering/deduplication, executable Framework Change Proposal mechanism, precision metric, namespace/role retrieval filter, CALLS graph edges.
3. **Deterministic core language:** Rust (workspace `runtime/` library + `cli/` binary; rusqlite bundled SQLite with FTS5, serde, jsonschema, regex, walkdir, sha2, chrono, uuid, clap).
4. **Rust-first exceptions:** none in the deterministic core. Polyglot pieces: Python-AST code-intelligence plugin and a Python reference embedder (justified in RPT-0001/D-0002: Python parsing Python with its own AST is the strongest implementation; the reference embedder proves cross-implementation determinism), and a bash echo embedder as a protocol proof. Justified.
5. **Can the core operate without Python?** Yes (HV-25; builder arch test reproduced). Python is required only for the optional plugins and for the verifier harness.
6. **Can it govern non-Rust and mixed-language projects without architectural change?** Yes for inventory/classification/path-map/indexing (Python+TypeScript fixtures; a verifier-authored Go project HV-13). Native tool resolution comes from a hard-coded ecosystem table (11 ecosystems), not from the Tool Capability Registry, whose only test-runner/AST entries are Python-specific (HV-06). Go module-path imports are not resolved into graph edges.
7. **Structured-state database:** SQLite (rusqlite, bundled, WAL) at `.governance-runtime/state.db`: tables artifacts, chunks, chunks_fts (FTS5), vectors, edges, symbols, symbol_refs, meta, claims, retrieval_log, excluded, capability. Chosen for zero-dependency, single-file, bundled FTS5, offline determinism (TOOLS.yaml TOOL-SQLITE-001, ARCH-0001). No alternatives recorded; acceptable for a derived store. Defect: `claims` (deterministic memory per framework §11.1) lives only in this derived, rebuild-deleted database (HV-05).
8. **Lexical search:** SQLite FTS5 with bm25 ranking, `unicode61` tokenizer (no stemming: "retry" ≠ "retries" ≠ "retried"; V-SEM-2 succeeded only via a chat-extracted record with the exact token). Chosen implicitly with SQLite. No alternatives recorded.
9. **Vector/index implementation:** vectors stored as JSON text in SQLite `vectors`, brute-force cosine scan over every vector per query, no ANN index. Baseline model: built-in deterministic hashed n-gram (512-d, SHA-1 feature hashing, unigram+bigram, camel-case splitting; bit-identical to the Python reference). Recorded in MEMORY_POLICY (comment), `embeddings.rs` docstring, release notes "Known limits". No benchmark, no alternatives evaluated.
10. **Graph implementation:** SQLite `edges(src,type,dst,source_artifact,provenance)` with 20 declared relation types; BFS neighbours/impact traversal in Rust. Materialised: record-field relations (29 field→edge mappings), IMPORTS (resolved imports), TESTS (test file → imported product file), SUPERSEDES. CALLS is declared but never materialised (HV-23).
11. **Code intelligence:** built-in line-oriented regex extractor (Python, Rust, JS/TS, Go, C/C++, Java/Kotlin/C#/Scala, Ruby, shell) producing symbols/imports/structural units with brace/indent end-line heuristics; optional `code_intel` plugins (shipped: Python stdlib AST, adds calls). No LSP/SCIP/tree-sitter, no references/inheritance. Chosen for zero external dependency. Symbol route misses bare identifiers (HV-33).
12. **Embedding model:** `hashed-ngram` v1 (built-in). Why: reproducible offline baseline that makes routing, fusion, manifests and regression tests testable; stronger models "plugged in via API-0001 and pinned per repository after a measured benchmark" (release notes). Verifier finding: the plug-in path is broken (HV-01, HV-36) and no benchmark exists.
13. **Reranker:** none (`reranker: {provider: none}` pinned in MEMORY_POLICY and manifest). API-0001 defines a `rerank` capability but the core never invokes it (HV-02).
14. **Alternatives benchmarked:** none. No `gov memory benchmark`, no decision record comparing candidates, no retrieval report across embedders.
15. **Retrieval metrics supporting the choice:** `run_heldout` computes Recall@K, MRR, stale-hit rate, superseded-hit rate, forbidden violations and per-query latency. On the adopted brownfield with a verifier-authored 12-query set: Recall@K 0.83, MRR 0.68, stale 0.0, superseded 0.0 (HV-08). Exact-ID, path, literal, symbol-with-`def`, cross-file and superseded-vs-current queries succeed; the token-overlap-free paraphrase fails (expected for a lexical baseline). Greenfield ships zero held-out queries and the family passes trivially (HV-20).
16. **Generative/orchestrator routing mechanism:** tier (T0–T3) and reasoning (low…extra_high) resolved from task class, task fields, role defaults (ROLES.yaml), impact radius and overlay overrides; candidate models come only from `MODEL_ROUTING_OVERRIDES.yaml` (empty by default), cheapest model meeting the tier floor wins; empirical evidence recorded via `gov route --record/--report` (model, provider, class, reasoning, cost, latency, pass, repairs) and mirrored into telemetry. Kernel contains no vendor/model names (arch test reproduced). Adequate.
17. **Pinned and replaceable?** Model routing: pinned in overlay, replaceable — yes. Embedder: pinned in `index-manifest.json` — yes; replaceable — **no** (HV-01/HV-36/HV-07). Reranker: pinned as none; replaceable — **no hook**. Vector/lexical/graph stores: fixed to SQLite by code (acceptable for a derived store; not abstracted). Tools: descriptors carry `version_pin`; the kernel registry pins Python tools only.
18. **Can all derived state be deleted and rebuilt?** Yes. HV-12 deleted `.governance-runtime/`, all of `governance/generated/` and `framework.json` and rebuilt identical manifest, adapter hashes, `framework.json`, deterministic context hash and status; HV-30 reproduced the manifest hash on a clean clone after a full brownfield adoption. Exception: claims and control state are lost (HV-05).
19. **Can a fresh agent reconstruct authoritative context?** Yes for state and next work (`gov status` lists ≤25 reads, `gov continue` compiles a hash-stable deterministic packet; reproduced in HV-12/HV-30 and on the adopted brownfield). But the packet omits hard invariants and project policy and includes two contradictory ACTIVE decisions without a flag (HV-15), so a fresh agent relying on the packet alone can act on superseded authority.
20. **Top critical gaps preventing release:** (1) query-time embedder coupling; (2) plugin-host deadlock; (3) unenforced authority levels; (4) unenforced mutation scope at close; (5) claims lost on rebuild; (6) restricted/confidential sensitivity classes indexed; (7) destructive migration gated by a flag; (8) mixed-embedder index after pin change undetected; (9) no reranker hook and no benchmark/selection mechanism; (10) memory regression green with zero queries.

## 3. Architecture Completeness Matrix

Status legend: PRESENT_AND_SUBSTANTIAL (P&S), PARTIAL, ABSENT, UNCLEAR. Severity is for incomplete items only.

### A. Governance / deterministic control plane
| Requirement | Status | Implementation | Evidence | Verifier notes | Sev |
|---|---|---|---|---|---|
| Deterministic Governance OS core | P&S | `runtime/`, `cli/` | builder suite rerun; HV-12, HV-25 | ~510 KB Rust, no warnings | — |
| Rust-first control plane | P&S | D-0002, ARCH-0001, workspace | `tests/certification/arch.rs`; `ldd` | libc-only binary | — |
| Justified non-Rust deterministic components | P&S | RPT-0001, D-0002 §5 | plugins only | none in the core | — |
| Portable `gov` CLI | PARTIAL | `kernel.rs::canonical_root` | HV-24 | kernel not embedded; build path `…/runtime` baked in; `framework.lock.source` is an absolute machine path | MEDIUM |
| Authority / policy engine | PARTIAL | `policy.rs`, `paths.rs` | HV-03, HV-04, HV-09, HV-10, HV-39; grep | overlay/exception merge + schema validation work; 20 policy keys never read; authority levels unenforced | HIGH |
| Constitution / policy precedence | PARTIAL | CONSTITUTION.md, HARD_INVARIANTS, AUTHORITY_POLICY, retrieval filter | HV-08 (superseded 0.0), HV-15 | precedence enforced in retrieval; not surfaced/ordered in the context packet | MEDIUM |
| Kernel vs overlay separation | P&S | `governance/kernel` + KERNEL_MANIFEST, 7 overlay files, D003/INV-007 | builder failure-injection #6 reproduced | | — |
| framework.lock | P&S | `lock.rs` | HV-27 schema-valid | absolute `source` path (LOW) | — |
| Checkpoint / recovery | PARTIAL | `checkpoints.rs`, `recovery.rs` | HV-19; builder #1/#2 reproduced | structured, watchdog, recover work; `before_handoff` not automatic; utilisation/op counting rely on caller | LOW |
| CIT-P / CIT-E | P&S | `cit/mod.rs` | HV-14, HV-17 pass; HV-10, HV-34 fail | simulation, gate, snapshot, verify, rollback solid; no auto-simulation; unscanned proposal content | MEDIUM |
| Dynamic task DAG | P&S | `orchestration/dag.rs` | HV-22 | 23 classes, cycles, longest chain, gates, readiness gating | — |
| Human Decision Gate handling | PARTIAL | `gates.rs` (INV-008) | HV-11, HV-29 fail; builder #12 reproduced | enforced for CIT/decide; bypassed by `update --approve` and `adopt migrate --gate-answer` | HIGH |
| Model-routing policy / reasoning tiers | P&S | `routing.rs`, MODEL_ROUTING_POLICY | greenfield reproduced | | — |
| Tool / capability / permission registry | PARTIAL | `tools.rs`, TOOLS.yaml, TOOL_PERMISSIONS | HV-06 | permissions, install gate, health present; registry content Python-biased; `run_tests` on a Rust project resolves to pytest | MEDIUM |
| Release / install / update / rollback | P&S | `release.rs`, `update.rs`, `kernel.rs` | update fixture reproduced; HV-11 | | — |
| Immutable release manifest / hashes / provenance | P&S | `release/releases/4.1.2/manifest.*` | `gov release verify` ok; payload == HEAD | binary hash not covered (source distribution) | — |
| Observability / execution evidence | PARTIAL | `observability.rs` | greenfield telemetry reproduced | JSONL spans/events, summary; no token measurement; cost only if reported | LOW |

### B. Repository intelligence and adoption / migration
| Requirement | Status | Implementation | Evidence | Notes | Sev |
|---|---|---|---|---|---|
| Cold deterministic inventory | P&S | `migrations/inventory.rs` | brownfield/migration reproduced | | — |
| Artefact classification | P&S | `classify.rs` | all 12 brownfield hazards classified as expected | | — |
| Authority classification | P&S | `classify.rs` | superseded-but-ACTIVE flagged | | — |
| Target canonical path map | PARTIAL | `planner.rs` | catalogue schema-valid | `references/imports/consumers` always `[]` (placeholders); dependency-awareness is by protocol batch order only | MEDIUM |
| Repository contract | P&S | `paths.rs`, REPOSITORY_CONTRACT | HV-09 (sensitivity), unit test | secret lock-in works; `sensitivity: restricted` ignored | HIGH (see J) |
| Governed migration engine | P&S | `executor.rs`, `refs.rs` | HV-31 (TS import rewrite), migration fixture | | — |
| Dependency-aware batches | PARTIAL | `planner::batches` | — | 8 fixed batches by class; no per-artefact dependency graph | MEDIUM |
| Independent migration test hooks | P&S | `verify.rs`, verdict gates | independence errors reproduced | session-id independence is declarative | — |
| Rollback / recovery | P&S | batch snapshots, `recover` | byte-identical rollback reproduced | | — |
| Legacy governance retirement | P&S | INV-004, D013, LEG record | reproduced | | — |
| Legacy memory inspection/extraction before retirement | P&S | `adopt.rs::a8` | extracted D-C/L-C records with provenance; secret string skipped | cue-based heuristics; PROVISIONAL status | — |
| Greenfield `gov init` | P&S | `init.rs` | reproduced | | — |
| Brownfield `gov adopt` | P&S | `adopt.rs` | reproduced; HV-16, HV-29 | freeze ignored; destructive gate is a flag | HIGH |
| Framework `gov update` | P&S | `update.rs`, `migrations/framework.rs` | reproduced; HV-11 | | MEDIUM |
| Preserve native layouts | P&S | `native_layout_rules`, capability_roots | migration fixture (lib/** mapped) | | — |

### C. Development Knowledge Fabric / memory
| Requirement | Status | Implementation | Evidence | Notes | Sev |
|---|---|---|---|---|---|
| Git records as source of truth | P&S | `records.rs` (YAML / MD front-matter) | HV-12 | | — |
| Structured deterministic state (SQLite) | PARTIAL | `memory/db.rs` | HV-05 | schema present; claims/control not preserved across rebuild | HIGH |
| Lexical FTS/BM25 | P&S | FTS5 bm25 | HV-08 lexical queries | no stemming | LOW |
| Semantic / vector retrieval | PARTIAL | hashed n-gram builtin; plugin embed | HV-01, HV-07, HV-08b, HV-36 | baseline has no paraphrase capability; plugin path broken; linear scan | CRITICAL |
| Graph relationships | PARTIAL | `graph/mod.rs`, edges | HV-23 | CALLS never materialised; IMPORTS/TESTS/record relations present | LOW |
| Temporal / supersession | PARTIAL | `superseded_by`, `repo_commit` | HV-08 superseded 0.0 | no git lineage (when/why/which decision) | MEDIUM |
| Episodic / execution evidence | P&S | telemetry, retrieval_log, reports, checkpoints | reproduced | | — |
| Code intelligence (AST/LSP/symbol/ref/import/call) | PARTIAL | `code_intelligence/generic.rs` + plugins | HV-13, HV-23, HV-33 | regex heuristics; no LSP/SCIP; no references; Go module imports unresolved | MEDIUM |
| Retrieval router | P&S | `retrieval::classify` | HV-08 routes | keyword/regex classification | — |
| Exact / lexical / semantic / graph / code-structural routes | PARTIAL | `retrieval::retrieve` | HV-08, HV-33 | exact/path/lexical/graph fine; symbol route needs `def`/dotted form; semantic see above | MEDIUM |
| Candidate fusion | P&S | reciprocal-rank fusion | | | — |
| Hierarchical parent-child | P&S | document/section/child chunks; parent expansion | unit test + HV-08 parent_excerpt | | — |
| Graph-neighbour expansion | P&S | 1-hop neighbours on top hits | | | — |
| Reranking | ABSENT | none | HV-02 | `rerank` capability defined, never invoked | HIGH |
| Authority filtering | P&S | status exclusions, superseded_by, archive default_retrieval | HV-08 | namespace/role filtering absent (HV-21) | LOW |
| Provenance | P&S | artifact_id, path, chunk, section, status, state_class, index snapshot | | | — |
| Stale / superseded filtering | P&S | flags + held-out rates | HV-08 | | — |
| Context compiler | PARTIAL | `context/mod.rs` | HV-15; HV-12 hash-stable | deterministic + retrieved blocks; missing invariants/policy layer; contradictions unflagged; size limit warns only | MEDIUM |
| Bounded authoritative context | PARTIAL | `max_packet_chars` warning | | not enforced | LOW |
| Rebuildability of all derived indexes | P&S | `indexer::rebuild` | HV-12, HV-30 | | — |
| Deletion-and-rebuild tests | P&S | builder multi-machine, deep suite; HV-12 | | | — |
| Retrieval regression / golden queries | PARTIAL | `run_heldout`, A9 auto-generation | HV-20 | greenfield ships 0 queries; auto-set is title lookups only | MEDIUM |
| Recall@K / MRR | P&S | `run_heldout` | HV-08 | | — |
| Precision / stale-hit analysis | PARTIAL | stale/superseded rates | | no precision metric | LOW |
| Latency / context-size / token metrics | PARTIAL | latency_ms, packet chars | | tokens not measured | LOW |

### D. Memory component separation
| Concern | Status | Notes | Sev |
|---|---|---|---|
| Embedding model | PARTIAL | pinned in manifest; plugin used for indexing; **query always built-in** (HV-01) | CRITICAL |
| Embedding inference runtime | PARTIAL | subprocess plugin (any language); deadlocks > 64 KiB (HV-36) | CRITICAL |
| Vector / index store | PARTIAL | SQLite JSON column, no abstraction; acceptable for baseline scale | LOW |
| Lexical engine | P&S (fixed) | FTS5 by code; justified by zero-dependency SQLite | — |
| Graph implementation | P&S (fixed) | SQLite edges; justified | — |
| Code-intelligence implementation | P&S | builtin + plugin protocol | — |
| Reranker | ABSENT | no call site | HIGH |
| Retrieval router | P&S | deterministic, in core | — |
| Generative LLM | P&S | tiers only; names in overlay | — |
| Context compiler | P&S | in core | — |
| No constitutional provider dependency | P&S | arch test reproduced | — |

### E. Rust-first core / polyglot independence
| Requirement | Status | Evidence | Sev |
|---|---|---|---|
| Deterministic components in Rust | P&S | source | — |
| Core runs without Python | P&S | HV-25 | — |
| Specialised capabilities behind stable interfaces | PARTIAL | API-0001 exists; HV-36 deadlock; HV-01 coupling | CRITICAL |
| Governed language not hard-coded | P&S | Rust, Python+TS, Go (HV-13) | — |
| OS language does not dictate product language | P&S | fixtures | — |
| Registry resolves native tooling per language | PARTIAL | HV-06: ecosystem table yes, registry no | MEDIUM |
| Fixture in a different language than the core | P&S | brownfield/migration (Python+TS), HV-13 (Go) | — |
| Mixed-language repositories | P&S | brownfield | — |
| Language-native tooling patterns (Cargo/clippy/rustfmt/LSP…) | PARTIAL | ecosystem table has build/test/lint/format/metadata commands; no LSP/rust-analyzer resolution; registry lacks descriptors | MEDIUM |

### F. Agent organisation / orchestration
| Requirement | Status | Evidence | Sev |
|---|---|---|---|
| Role separation | P&S | ROLES.yaml (28 roles) | — |
| Authority levels | PARTIAL | declared L0–L5; unenforced (HV-03) | HIGH |
| Task contracts | P&S | task schema, `task create` defaults | — |
| Mutation manifests | PARTIAL | CIT manifests; handoff return enforces scope; task close does not (HV-04) | HIGH |
| Worktree / claim collision controls | PARTIAL | lease claims; lost on rebuild (HV-05) | HIGH |
| Typed subagent results | P&S | worker-return schema; HV-32 | lessons in returns not promoted (LOW) |
| Checkpoint before handoff / close / model switch | PARTIAL | HV-19 | LOW |
| Fresh-session independence for verification roles | P&S | session gates reproduced | — |
| Continue independent branches while gates pending | P&S | `continue_work` presents gate and proceeds | — |
| Durable promotion of results | P&S | handoff/report/checkpoint records | — |

### G. Tools / interfaces / extensibility
| Requirement | Status | Evidence | Sev |
|---|---|---|---|
| Stable interfaces | P&S | API-0001, API-0002 | — |
| MCP support | ABSENT (documented) | `gov mcp` → MCP_NOT_IMPLEMENTED; registry entry `planned` | MEDIUM |
| A2A separation from memory/tool execution | P&S | handoff records | — |
| CLI / JSON-RPC / HTTP / stdio | PARTIAL | CLI JSON + stdio plugins only | LOW |
| Capability discovery | P&S | plugins dir, ecosystems | — |
| Tool registration / health / acquisition gate / pinning | P&S | `tools install` conditions → gate; health checks | — |
| Secrets handling | PARTIAL | index-side fail closed; HV-17 pass; HV-34, HV-09 fail | HIGH |
| Privilege / destructive-action gates | PARTIAL | HV-03, HV-29 | HIGH |
| Loose coupling core ↔ external AI services | PARTIAL | HV-01, HV-36 | CRITICAL |

### H. Model routing / reasoning policy
All PRESENT_AND_SUBSTANTIAL: tier-based, per-task minimum reasoning, tier floors by class/role/radius, cheapest-meeting-tier selection, T0 deterministic paths (every governance operation and intent routing), evidence record/report, overlay-replaceable policy.

### I. Synthetic certification fixtures
| Fixture | Status | Notes |
|---|---|---|
| Greenfield | P&S | reproduced |
| Dirty brownfield | P&S | contains every listed hazard (legacy rules ×3, chat sqlite+jsonl with secret, stale index, superseded-but-ACTIVE, duplicate id, misplaced spec/test/source, code/spec disagreement, missing tests, stale test, dead code, secrets ×3 incl. planted, dangling REQ-R1) |
| Migration | P&S | reproduced; HV-31 |
| Framework update | PARTIAL | the "previous release" is synthesised inside the test from the current payload, not a stored immutable prior release |
| Upstream learning / export | P&S | reproduced; HV-26 gap |
| Multi-machine | P&S | reproduced; HV-30 |
| Failure injection | P&S | 13 faults reproduced |
| Model/provider adapter conformance | PARTIAL | 5 adapter templates; verify checks invariant statements verbatim + hashes; no semantic-equivalence test of policies |
| Secrets / outbound negative controls | P&S | reproduced |

### J. Security / safety / outbound
| Requirement | Status | Evidence | Sev |
|---|---|---|---|
| Secret detection / exclusion | P&S | index fail-closed; D011/D012; HV-17 | — |
| Sensitive-path handling (restricted/confidential) | PARTIAL→ABSENT | HV-09: only `secret` honoured | HIGH |
| Outbound allowlist / default deny | P&S | upstream fixture reproduced | — |
| Project/customer data separation from governance memory | PARTIAL | namespaces declared, not enforced (HV-09, HV-21) | HIGH |
| Upstream lesson sanitisation | PARTIAL | HV-26: `category`/title/tags not scanned | MEDIUM |
| Synthetic reproducer preference | P&S | code-line cap unless fixture | — |
| Destructive-action controls | PARTIAL | HV-29, HV-03 | HIGH |
| Privilege boundaries | PARTIAL | roles → tool permissions only | HIGH |
| Auditable security decisions | P&S | gate/decision/audit records, ledgers | — |

### K. Learning / upstream
| Requirement | Status | Notes | Sev |
|---|---|---|---|
| PROJECT / PRODUCT / FRAMEWORK scoping | P&S | | — |
| Local lesson capture | P&S | lesson records; A8 extraction | — |
| Sanitised framework-candidate preparation | P&S | `upstream prepare` | — |
| Upstream Export Gate | P&S | fail-closed, approval, ledger, allowlist | — |
| No whole-project export | P&S | | — |
| Clustering / deduplication | ABSENT | README prose only | MEDIUM |
| Framework Change Proposal mechanism | ABSENT (convention only) | README; no command, no schema, no record in repo | MEDIUM |
| Central release path | P&S | `gov release build/verify` | — |
| Downstream update | P&S | `gov update` | — |

### L. Observability / governance health
PRESENT: task traceability, feature readiness coverage, unresolved contradictions (D014, schema_invariants), graph orphans/dangling, stale/superseded retrieval, context size, retrieval latency, command latency, tests, decisions, human interventions, rebuild/fresh-agent reconstruction. PARTIAL: retrieval quality (only via held-out set, trivially empty on greenfield), cost and retries/repair (only if reports carry them), handoff failure (authority_violations only). ABSENT: token usage.

## 4. Model / Retrieval Selection Matrix

| Component | Selected | Version | Alternatives considered | Benchmark / evidence | Rationale recorded | Pinned | Replaceable | Privacy / locality | Verifier verdict |
|---|---|---|---|---|---|---|---|---|---|
| Generative / orchestrator model | none (tier T3 floor for orchestrator, governance, memory, security, architecture) | n/a | n/a (overlay decides) | routing evidence ledger exists, empty | MODEL_ROUTING_POLICY, ROLES.yaml | overlay | yes | provider-agnostic | ACCEPT (deferral is by design; kernel is vendor-free) |
| Specialist / worker tiers | T1/T2 by class | n/a | n/a | same | same | overlay | yes | same | ACCEPT |
| Embedding model | built-in hashed n-gram (SHA-1 feature hashing, uni+bigram, camel split, L2-normalised) | v1, 512-d | none recorded | none; verifier HV-08: paraphrase recall 0 | MEMORY_POLICY comment, `embeddings.rs`, release notes | yes (index-manifest) | **no in practice** (HV-01, HV-07, HV-36) | local, deterministic | **REJECT**: coupled at query time, plugin path broken, no selection mechanism |
| Embedding inference runtime | in-process (builtin) / subprocess plugin (any language) | protocol gov-capability/1 | none | HV-36 deadlock | API-0001 | plugin version in manifest | protocol yes; host broken | local | **REJECT** until host fixed |
| Vector store / index | SQLite `vectors` (JSON text), brute-force cosine | index 4.1.2-idx1 | none | none | ARCH-0001 (SQLite owns structured state) | index_version | code change only | local | ACCEPT with note (no ANN; fine for baseline scale; must be behind a trait before real embedders) |
| Lexical engine | SQLite FTS5 bm25, unicode61 | bundled | none | HV-08 lexical queries pass | TOOL-SQLITE-001 | n/a | code change only | local | ACCEPT with note (add porter/stemming option) |
| Graph implementation | SQLite `edges` + Rust BFS | — | none | HV-08 graph query; dangling/orphan checks | ARCH-0001 | n/a | code change only | local | ACCEPT |
| Reranker | none | — | none | none | MEMORY_POLICY `provider: none` | yes | **no hook** (HV-02) | — | **REJECT**: absence is acceptable at baseline only if a hook exists |
| Code-intelligence tooling | builtin regex extractor + python-ast plugin | 1.0.0 | LSP/SCIP/tree-sitter not evaluated | HV-13/23/33 | ARCH-0001, RPT-0001 | plugin version | yes (plugin) | local | PARTIAL: acceptable baseline; symbol route and CALLS gaps |
| Query-planning / rewrite LLM | none (T0 intent patterns) | — | — | HV-18 | COMMAND_CONTRACT | — | adapters may add one | — | ACCEPT |

**Embedding / reranker selection quality (§3 of the directive):** no comparison against multiple candidates exists; no benchmark covers the required query classes; the held-out runner can compute Recall@K/MRR/stale/superseded/latency but cannot compare candidates, has no precision, symbol-recall, graph-coverage, reranking-lift, memory-footprint, indexing-cost or token-impact metrics, and greenfield projects run it with zero queries. The chosen baseline is locally runnable and deterministic and the index rebuilds deterministically, but "the model can be swapped and the indexes rebuilt" is false today (HV-01, HV-07, HV-36).

## 5. Structured-state (SQLite) verification

- Authoritative state in Git: every record under `spec/`, `governance/project/`, `archive/` (YAML or Markdown front-matter), `framework.lock`, tracked `governance/generated/*.json` manifests. Confirmed.
- Derived state in SQLite: artifacts (+`data_json` copy of records), chunks, FTS, vectors, edges, symbols, symbol_refs, excluded, capability memory, retrieval log, **claims**. Schema created idempotently; no DB-level migration system (acceptable because the DB is fully derived and versioned by `index_version`), integrity via `PRAGMA integrity_check`, transactions in batches of 500 inserts, WAL journal; corrupt DB is detected (D009) and rebuilt by `gov recover` (reproduced).
- Graph edges: `edges` table with provenance; FTS: `chunks_fts` external content by insert.
- Rebuild: full rebuild deletes `state.db` and regenerates; manifest hash reproducible on the same tree (HV-12, HV-30). Incremental rebuild is content-hash driven and **does not react to embedder/chunking pin changes** (HV-07: mixed 64-d/512-d vectors, manifest says 64-d, freshness fresh, doctor D010/D012 ok, audit recovery_rebuild family ok).
- Vector/semantic indexes remain derived (never read as truth); authority resolution uses record status/superseded_by, not vectors. Confirmed.
- Defect: `claims` are deterministic memory (framework §11.1) but live only in the rebuild-deleted DB (HV-05): after `gov rebuild-memory` a task stays IN_PROGRESS while its claim vanishes and another session claims it. `control.json` lives in the runtime directory too and is lost when the runtime is deleted (a FREEZE is silently lifted by deleting `.governance-runtime/`).

## 6. Context compiler verification

Deterministic block: task, objective, project state (framework version, task counts, pending gates, control mode, projects), feature, governing requirements, active decisions, architecture, interfaces, scenarios, acceptance criteria, allowed/prohibited writes (task forbidden paths + `governance/kernel/**` + contract `mutation: prohibited` rules), required skills (resolved with versions), tools, dependency state, tier/reasoning. Keys are sorted alphabetically, hashed (stable: HV-12 identical across delete/rebuild and across machines). Retrieved block: query, strategy, routes, index snapshot (version + manifest hash), ranked evidence with excerpts/parent/neighbours/flags/status/state_class, lessons/failures, code references. Packet bounded only by a warning at `max_packet_chars`.

Gaps: (a) hard invariants and the security/authority/project-policy layers are not in the packet (framework §21 hierarchy: constitution → security/authority → project policy → decisions/spec → task → role/skill → retrieved → inference); (b) `active_decisions` is filtered by status only, so a superseded-but-ACTIVE decision and its superseder both appear as active with no flag (HV-15); (c) global human-approved decisions without `affects` are not included; (d) duplicate suppression is per-artefact (max 2 chunks) — fine. Fresh-agent reconstruction of state and next work is otherwise demonstrated (HV-12, HV-30, adopted brownfield).

## 7. Feature / capability readiness

26 dimensions with `gap_task_class` and `pre_implementation` flags (READINESS_DIMENSIONS.yaml); cell states PRESENT / MISSING / PROVISIONAL / BLOCKED / N/A_WITH_REASON(reason ≥ 3 chars) validated by the feature schema; silent N/A rejected; `gov readiness plan` creates one task per non-OK cell with the declared class and links implementation tasks of the feature as dependent (BLOCKED until PRESENT). Reproduced in the greenfield rerun (data, test-design, performance tasks generated). Executable and enforceable. Gap: implementation tasks without a feature bypass readiness entirely and `TEST_POLICY.implementation_task_requires` is never read (HV-39).

## 8. Dynamic task DAG

Task class enum covers all 22 required classes plus `migration`; dependencies are free-form ids; runnable/blocked/waiting-human/done sets, longest open chain, cycle detection, per-feature paths, human-gate dependencies, missing-dependency reporting; `replan` persists READY/BLOCKED/WAITING_HUMAN. HV-22 built an 11-step research → experiment → decision-preparation → specification → data → specification → test-design → architecture → implementation → integration → validation chain: longest chain 11, only the root runnable. Confirmed.

## 9. Critical Gap Register

### CRITICAL
| ID | Gap | Evidence | Affected architecture | Risk | Required repair | Acceptance test |
|---|---|---|---|---|---|---|
| C1 | Query embedding hard-coded to built-in embedder | HV-01 (0/4 exact-title top-1 with pinned plugin; ranking == builtin prediction 4/4); `retrieval/mod.rs:108` | DKF semantic route; component separation D; §14.3 | any non-baseline embedder silently yields noise; held-out metrics, CIT-P candidates and context packets built on a wrong space | embed queries with the embedder recorded in the index manifest (dispatch builtin/plugin by id+version+dim); persist embedder identity in `meta`; refuse the semantic route with a clear error when the live index and policy pin disagree | `harness.py HV01` → PASS; builder test: reversed-embedder plugin, 4/4 exact-title queries top-1 |
| C2 | Plugin host deadlock on responses > pipe buffer | HV-36 (300 KB → 61 s → PLUGIN_TIMEOUT); `capabilities/host.rs` try_wait loop | API-0001, all AI/ML capabilities | no real embedder/reranker/code-intel plugin can process realistic batches | read stdout/stderr on separate threads (or `wait_with_output` with a watchdog thread that kills on timeout); write stdin from a thread; document max payload | `harness.py HV36` → PASS in < 2 s; rebuild of the greenfield fixture with a 512-d plugin embedder completes without degradation |

### HIGH
| ID | Gap | Evidence | Affected | Risk | Required repair | Acceptance test |
|---|---|---|---|---|---|---|
| H1 | Embedder pin change leaves a mixed index reported as healthy | HV-07 (vectors 64-d ×2, 512-d ×292; manifest 64-d; fresh; D010/D012 ok) | freshness, doctor, §14.3 measured migration | corrupted semantic space undetected | freshness compares manifest `embedder`/`chunking`/`index_version` with effective policy; incremental rebuild escalates to full when they differ; doctor check; refuse `task close` | HV07 → PASS |
| H2 | Claims (and control state) lost on full rebuild | HV-05 | concurrency/session claims, emergency controls | duplicate work, silent unfreeze | keep claims and `control.json` outside the rebuild-deleted store (separate `.governance-runtime/claims.db` or tracked `spec/planning/claims.yaml`), or preserve tables across rebuild; sweep instead of drop | HV05 → PASS |
| H3 | Authority levels not enforced | HV-03 (L0 auditor: task create, CIT propose/simulate/approve/execute; L1: gate create+decide, freeze, kernel reinstall) | authority/policy engine, F, J | any session can do anything by naming a role | map `--role` to ROLES.yaml level; enforce `AUTHORITY_POLICY.authority_levels_required` per operation class in `guard_write`-style check; reject unknown roles; `decide --by` for non-human roles requires `agent_resolvable_when` conditions | HV03 → PASS (all 9 refused) |
| H4 | Mutation scope not checked at task close | HV-04 | task contract, mutation manifests | workers close tasks after out-of-scope writes | validate `report.files_changed` against task allowed/forbidden paths and contract `mutation: prohibited` (as `handoff return` does); MUTATION_SCOPE_VIOLATION | HV04 → PASS |
| H5 | Restricted/confidential sensitivity classes indexed and retrievable | HV-09 | security boundaries §16/§72, namespaces | customer/legal material in generic memory | honour `SECURITY_POLICY.never_index_classes` and `DATA_SENSITIVITY.classifications` in `RepositoryContract::decide` (sensitivity ≥ restricted ⇒ no index flags, default_retrieval false, export denied); doctor/suite check; namespace/role filter in retrieval | HV09 → PASS; HV21 → PASS |
| H6 | Destructive migration batches gated by a CLI flag | HV-29 (dead code deleted with `--gate-answer ART-…`, no gate record) | Human Decision Gates, INV-008, adoption A6 | irreversible deletion without a presented decision | A4 creates a human-gate record per `requires_human_gate` entry; A6 accepts only ANSWERED gates (presented_in_chat=true) | HV29 → PASS |
| H7 | No reranker hook; no benchmark/selection mechanism | HV-02, HV-08b, HV-20 | §14.2–14.3, D | embedder/reranker cannot be selected on evidence | invoke `rerank` plugin between fusion and dedup when pinned; add `gov memory benchmark --candidates <plugin,…>` reporting Recall@K, MRR, precision, stale/superseded, symbol recall, latency, index cost per candidate on the held-out set; require ≥ N held-out queries for a green regression family; record the choice as a decision with alternatives | HV02 → PASS; HV20 → PASS; benchmark report on the brownfield fixture with ≥ 2 candidates |

### MEDIUM
| ID | Gap | Evidence | Required repair | Acceptance |
|---|---|---|---|---|
| M1 | Kernel registry Python-biased; `run_tests` on Rust resolves pytest | HV-06 | registry descriptors per ecosystem (cargo test/clippy/rustfmt, npm test, go test…) tagged by language; `tools resolve` filters by detected ecosystem; extend the language-neutrality arch test to `tools/` | HV06 → PASS |
| M2 | CIT-P not automatic for `auto_simulate_triggers` | HV-10 | `cit propose` runs simulation when trigger ∈ policy list | HV10 → PASS |
| M3 | `update --apply --approve` bypasses gate presentation | HV-11 | require the created gate to be presented+answered (or `--gate <HDG>`); clean up stale pending gate | HV11 → PASS |
| M4 | Context packet lacks invariants/policy layer; contradictory active decisions unflagged | HV-15 | add ordered `authority_layers` (invariants → security/authority → project policy → decisions) and flag `UNKNOWN_OR_CONFLICTING` on superseded-but-ACTIVE | HV15 → PASS |
| M5 | FREEZE_WRITES ignored by `adopt migrate` and `upstream submit` | HV-16 | `guard_write` in adopt stages ≥ A6, A8, and upstream submit | HV16 → PASS |
| M6 | Kernel not embedded; build path baked; absolute `source` in lock | HV-24 | embed the payload (`include_dir!`/tar) with `gov init --source` override; write a logical source id in the lock | HV24 → PASS |
| M7 | Upstream packet `category`/title/tags unsanitised | HV-26 | sanitise every emitted field | HV26 → PASS |
| M8 | Symbol route ignores bare identifiers | HV-33 | treat a single identifier token matching `symbols.name` as a symbol query | HV33 → PASS |
| M9 | `cit propose` persists unscanned manifest content (secret in `spec/decisions/CIT-*.yaml`) | HV-34 | scan proposal/manifest at propose; refuse or redact | HV34 → PASS |
| M10 | Implementation tasks without a feature bypass scenario/test gating | HV-39 | enforce `TEST_POLICY.implementation_task_requires` in DAG/replan | HV39 → PASS |
| M11 | Semantic paraphrase recall 0 with baseline; no stemming | HV-08b | delivered by H7 (benchmark) + FTS5 porter option | benchmark report |
| M12 | 20 declared policy keys never read (budget thresholds, `never_export_classes`, `agent_resolvable_when`, `corroboration_min_sources`, `release_triggers`, `prose_summary_as_checkpoint`, `independent_test_author_required_for`, …) | grep | either enforce or remove from kernel policy (a policy that is data-only misleads adopters) | audit family `policy_enforcement_coverage` |
| M13 | Migration catalogue `references/imports/consumers` always empty | planner.rs | populate from code-intel/link scan | catalogue entries non-empty for the migration fixture |
| M14 | MCP server absent; lesson clustering and FCP mechanism absent | release notes, READMEs | acceptable to defer with explicit decision records; add `gov lessons cluster` and an FCP record type/schema | records + tests |
| M15 | Clippy evidence is a tool-missing error counted as a diagnostic | `release/evidence/clippy-diagnostic-count.txt` | install clippy or record "not run"; never count tool errors | evidence file shows a real count |
| M16 | Update fixture derives the previous release in-test | update.rs | store an immutable 4.1.1 payload under `release/releases/4.1.1` (or a fixture tarball) | fixture uses stored payload |

### LOW
| ID | Gap | Evidence | Repair |
|---|---|---|---|
| L1 | No checkpoint before handoff | HV-19 | auto-checkpoint in `handoff create` |
| L2 | No namespace/role retrieval filter | HV-21 | see H5 |
| L3 | CALLS edges never materialised; Go module imports unresolved | HV-23, HV-13 | emit CALLS edges from symbol_refs; resolve Go module paths via go.mod module prefix |
| L4 | `gov audit` leaves the index stale (audit record added) | HV-28 | incremental rebuild after persisting the audit record, or exclude `spec/audits/AUD-*` from freshness |
| L5 | Held-out test file is lexically indexed (test leakage into retrieval; appeared in HV-08 top-4 twice) | HV-08 | `governance/tests/**` lexical_index false |
| L6 | Worker-return `lessons` not promoted to lesson records | HV-32 | create PROVISIONAL lessons from returns |
| L7 | Approval decision record survives CIT rollback | HV-14 | mark decision REJECTED/ROLLED_BACK on rollback |
| L8 | Timestamps written unquoted (YAML 1.1 loaders read datetimes) | HV-27 | quote timestamp-like strings |
| L9 | `max_packet_chars` only warns | context/mod.rs | truncate retrieved block deterministically |

## 10. Independent test additions (held-out, not part of builder evidence)

Harness: `release/verification/4.1.2/heldout/harness.py` (Python, black-box via `gov --json`; later definitions of HV01/HV07 supersede earlier ones). Run: `cargo build --release && python3 release/verification/4.1.2/heldout/harness.py [HV01 …]`. Results: `heldout/results.json`.

| ID | Scenario | Result |
|---|---|---|
| HV-01 | Plugin embedder pinned and used for the index; is the query embedded with the same model? | FAIL (CRITICAL) |
| HV-02 | Pinned `rerank` plugin invoked during retrieval | FAIL (HIGH) |
| HV-03 | L0/L1 roles refused mutating/approval operations | FAIL (HIGH) |
| HV-04 | Task close rejects out-of-scope `files_changed` | FAIL (HIGH) |
| HV-05 | Claims survive full rebuild; second session cannot steal | FAIL (HIGH) |
| HV-06 | Registry resolves native `run_tests` for a Rust project | FAIL (MEDIUM) |
| HV-07 | Embedder pin change forces full re-index; no mixed index | FAIL (HIGH) |
| HV-08 | 12 verifier golden queries on adopted brownfield (metrics by category) | INFO: R@K 0.83, MRR 0.68, superseded 0.0, stale 0.0 |
| HV-08b | Token-overlap-free paraphrase retrieval | FAIL (MEDIUM) |
| HV-09 | Restricted-class material excluded from memory | FAIL (HIGH) |
| HV-10 | Automatic CIT-P on policy triggers | FAIL (MEDIUM) |
| HV-11 | `update --apply --approve` requires a presented, answered gate | FAIL (MEDIUM) |
| HV-12 | Delete runtime + all generated views + framework.json → identical rebuild | PASS |
| HV-13 | Go governed project (new language) inventoried/indexed without `go` on PATH | PASS |
| HV-14 | CIT rollback reverts retest propagation | PASS |
| HV-15 | Context packet flags contradictory active decisions; carries invariants/policy | FAIL (MEDIUM) |
| HV-16 | FREEZE_WRITES honoured by adopt batches and upstream submit | FAIL (MEDIUM) |
| HV-17 | CIT-E refuses to commit a record containing a secret | PASS |
| HV-18 | Intent routing: discover / approve (binds pending CIT) / rollback / unknown | PASS |
| HV-19 | Checkpoint before handoff | FAIL (LOW) |
| HV-20 | Memory regression family green with 0 held-out queries | FAIL (MEDIUM) |
| HV-21 | Namespace/role filter in retrieval | FAIL (LOW) |
| HV-22 | 11-class research→validation dependency chain in one DAG | PASS |
| HV-23 | python-ast plugin used; CALLS edges in graph | FAIL (LOW) |
| HV-24 | Kernel obtainable without the build checkout | FAIL (MEDIUM) |
| HV-25 | Core with only `git` on PATH: init/status/continue/audit/doctor | PASS |
| HV-26 | Upstream packet sanitises category/title/tags | FAIL (MEDIUM) |
| HV-27 | All generated artefacts + records validate against kernel schemas (independent validator) | PASS |
| HV-28 | `gov audit` leaves index fresh | FAIL (LOW) |
| HV-29 | Destructive batch requires an answered gate record | FAIL (HIGH) |
| HV-30 | Multi-machine rebuild after full brownfield adoption | PASS |
| HV-31 | TypeScript relative import rewritten on relocation | PASS |
| HV-32 | Worker return promoted to state | PASS |
| HV-33 | Symbol route resolves a bare identifier | FAIL (MEDIUM) |
| HV-34 | `cit propose` scans manifest content | FAIL (MEDIUM) |
| HV-35 | Held-out file not indexed | PASS (at k=3; leakage observed in HV-08) |
| HV-36 | Plugin host handles a 300 KB response | FAIL (CRITICAL) |
| HV-39 | Implementation task without feature gated by scenarios/tests policy | FAIL (MEDIUM) |

Totals: 12 PASS, 25 FAIL, 1 INFO.

## 11. Builder repair delta (ordered)

1. **C1** Retrieval query embedding: dispatch on the manifest-pinned embedder (`retrieval/mod.rs` semantic route, `context::compile`, `run_heldout`, `cit::simulate` all inherit). Store `{id, version, dim, source}` in `meta.embedder`; error `EMBEDDER_MISMATCH` when policy pin ≠ live index.
2. **C2** Plugin host: concurrent stdout/stderr readers + stdin writer thread; timeout watchdog kills the child; add a host unit test with a 1 MB response and a slow-reader plugin.
3. **H1** Freshness/doctor/indexer: pin-aware freshness (embedder, chunking, index_version); incremental → full escalation; `task close` refuses on pin mismatch.
4. **H2** Move claims and control state out of the rebuild-deleted DB; `rebuild` preserves or migrates them; add doctor check `D025 claims store present`.
5. **H3** Enforce authority levels from ROLES.yaml against `AUTHORITY_POLICY.authority_levels_required` for: task create/status/close(--force), cit propose/simulate/approve/execute/rollback, decide (human only unless `agent_resolvable_when`), gate create, freeze/pause/cancel/resume, kernel reinstall, update apply, tools install, adopt destructive batches, upstream submit. Unknown role → `UNKNOWN_ROLE`.
6. **H4** `task close`: validate `files_changed` against task allowed/forbidden paths and contract prohibitions.
7. **H5** Honour `never_index_classes`/`never_export_classes` and `DATA_SENSITIVITY.classifications` in `paths.rs`; namespace/role filter in `retrieve`; suite family check.
8. **H6** A4 creates human-gate records for `requires_human_gate` entries; A6 requires ANSWERED gates; remove flag-only path.
9. **H7** Wire `rerank`; add `gov memory benchmark`; require a minimum held-out query count (policy `regression.min_queries`) for a green family; auto-generate a richer starter set (id, path, symbol, graph, superseded, paraphrase placeholders) and record the embedder/reranker choice as a decision with alternatives and metrics.
10. **M1–M16, L1–L9** as listed in §9.
11. Re-run the builder suite, the Python plugin tests, a real clippy run, and this held-out harness; regenerate `docs/EVIDENCE.md`; rebuild the release with the same version only if the kernel payload is unchanged (it is data; all repairs above are runtime code) — otherwise bump to 4.1.3 per immutability.

## 12. What was verified sound (do not regress)

Rust-only core with no Python/Node dependency; language-neutral kernel data; init/adopt/update/rollback mechanics; byte-identical batch rollback; TS and Python import rewriting; legacy retirement and chat-store extraction with secret skipping; index-side secret fail-closed (planted secret in `src/app/config.py` never reaches chunks); CIT snapshot/verify/rollback including retest propagation; INV-008 for CIT and `decide`; deterministic context hash across machines and across full delete/rebuild; release payload integrity and manifest; schema validity of all generated artefacts; readiness-driven task generation; DAG semantics; intent routing; failure-injection recoveries.

## 13. Verdict

**OS_RELEASE_CANDIDATE_REJECTED.** Rejection triggers met (§10 of the directive): model/component choice tightly coupled (C1); no credible benchmark/selection mechanism (H7); security/export boundaries materially incomplete (H5, H6, M9); held-out tests expose unresolved critical/high defects (C1, C2, H1–H7). The release manifest certification block has been set to REJECTED by this verifier; `certified_at` remains empty.
