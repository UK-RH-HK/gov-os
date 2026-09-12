# Governance OS — Architecture (release candidate 4.1.2)

Source framework: [DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md](../DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md),
[release/distribution protocol v1.2](../GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md),
[adoption/audit protocol v3.0](../GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md).
Governing decision: [D-0002 Rust-first deterministic core, polyglot capability ecosystem](../spec/decisions/D-0002.yaml);
architecture record [ARCH-0001](../spec/architecture/ARCH-0001.yaml).

## 1. Layers

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ KERNEL PAYLOAD (data, immutable per release)            framework/ + migrations/ + tools/ │
│  constitution · hard invariants · 13 policies · 59 schemas · skills · adapters · roles     │
│  taxonomy · command contract · overlay templates · declarative migrations · registries      │
├──────────────────────────────────────────────────────────────────────────────┤
│ DETERMINISTIC CORE (Rust)                          runtime/ (lib gov-runtime) · cli/ (bin gov) │
│  kernel install/verify · framework.lock · overlay + policy enforcement · repository contract │
│  records · Development Knowledge Fabric (SQLite/FTS5, vectors, graph, code intel, router,    │
│  context compiler, manifests) · tasks/DAG/claims/gates/control · checkpoints · CIT-P/CIT-E   │
│  doctor · governance suite/audit · init/adopt/update/release/upstream/recovery              │
│  tool/permission/MCP registry · model routing · telemetry · plugin host · ecosystem detection│
├──────────────────────────────────────────────────────────────────────────────┤
│ CAPABILITY ECOSYSTEM (polyglot, behind API-0001)                              capabilities/  │
│  python: python-ast code intel, reference embedder · shell: protocol proof · (future: LSP,   │
│  rerankers, model runtimes, MCP servers)                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ GOVERNED PROJECT (any language)  described by REPOSITORY_CONTRACT.yaml; native toolchains  │
│  resolved by ecosystem detection (Cargo, pytest, npm, go, cmake, make, maven, …)            │
└──────────────────────────────────────────────────────────────────────────────┘
```

Coupling rules (tested by `tests/certification/arch.rs`): the core has no build/run-time dependency on Python, Node
or any governed toolchain; kernel data contains no language assumptions; external processes are spawned only from
registry/plugin descriptors or ecosystem data tables; embedder, reranker, index store and generative model are
separate, individually pinned concerns.

## 2. Logical → physical layout

| Framework §75A logical | Physical | Notes |
|---|---|---|
| `framework/{constitution,policies,schemas,skills,adapters}` | `framework/` (+ `roles/`, `taxonomy/`, `commands/`, `overlay-templates/`) | kernel payload, `KERNEL.yaml` lists payload dirs |
| `runtime/{memory,retrieval,graph,code-intelligence,context,cit,orchestration,checkpoints,observability}` | `runtime/src/{memory,retrieval,graph,code_intelligence,context,cit,orchestration,checkpoints.rs,observability.rs}` | Rust library crate |
| `cli/` | `cli/src/main.rs` | `gov` binary, JSON contract API-0002 |
| `tools/{registry,mcp,installers}` | `tools/` | data; copied into the kernel payload |
| `migrations/` | `migrations/` (definitions) + `runtime/src/migrations/` (engine) | declarative, schema-validated |
| `tests/` | `tests/certification/` (Rust integration tests linked from `cli/Cargo.toml`), in-crate unit tests | |
| `fixtures/` | `fixtures/{greenfield,brownfield,migration,update,upstream-learning,multi-machine,failure-injection}` | synthetic only |
| `lessons/inbox/`, `change-proposals/`, `release/`, `docs/` | same | |
| — | `capabilities/` | polyglot plugins (D-0002) |
| — | `spec/` | the canonical repository's own governed records (dogfooding) |

## 3. Consumer repository contract

```text
<repo>/
├── framework.json                 # derived projection of the repository contract
├── governance/
│   ├── kernel/                    # immutable installed payload + KERNEL_MANIFEST.json (file hashes)
│   ├── project/                   # project-owned overlay (7 files) + optional plugins/, tools/, skills/, mcp/
│   ├── generated/                 # index-manifest.json, memory-manifest.json, tool-registry.json,
│   │                              # adapter-manifest.json, adapters/<id>/…
│   ├── tests/memory/heldout.yaml  # held-out retrieval regression queries
│   └── framework.lock             # version, release_hash, kernel_manifest_hash, source, schema versions
├── spec/{now,product,features,requirements,architecture,workflows,interfaces,scenarios,data,security,
│         performance,research,experiments,decisions,planning,tasks,reports(/checkpoints),lessons,audits}
├── product/ (or any native layout mapped by the contract)
├── archive/{governance,spec,research,code-reference}
└── .governance-runtime/           # derived, gitignored: state.db (SQLite+FTS5), context/, cit/<id>/snapshot,
                                   # migration/batch-n, update/<version>, telemetry/, routing/, outbound/, control.json
```

## 4. Development Knowledge Fabric

Authoritative truth = Git-tracked records (YAML, or Markdown with front-matter) under `spec/`, `governance/project/`,
`archive/`. Everything in `.governance-runtime/` is derived and rebuildable (`gov rebuild-memory`); the tracked
`index-manifest.json` (content hashes per artefact, embedder/chunking pins, exclusions) makes rebuilds verifiable
(`manifest_hash` equality is asserted by the multi-machine fixture and the `recovery_rebuild` suite family).

| Memory class | Implementation |
|---|---|
| deterministic | `artifacts` table + record JSON; records loaded from files by `RecordStore` |
| relationship | `edges` (20 typed relations from record fields + code imports/tests); traversal in `graph/` |
| semantic | `vectors` (built-in hashed-ngram baseline or plugin embedder; pinned in the manifest) |
| lexical | `chunks_fts` (FTS5, bm25) |
| code-structural | `symbols`/`symbol_refs` from built-in multi-language extractor or `code_intel` plugins |
| temporal | `repo_commit` per artefact, CIT journals, checkpoints, ledgers |
| episodic | telemetry JSONL, retrieval log, reports, checkpoints |
| failure | reports with outcome failed/blocked, lessons, recovery reports |
| working | context packet (`.governance-runtime/context/<task>.json`) |
| capability | `meta.capability.*` (ecosystems, plugins, degradations), `tool-registry.json` |

Retrieval router: query classification → routes (structured id/path, symbol, lexical exact/phrase, semantic, graph)
→ reciprocal-rank fusion → authority filter (excluded statuses, superseded_by, archive default_retrieval) →
per-artefact dedup → parent/section + 1-hop graph expansion → bounded cited slices. Secret-class paths are never read;
secret-content hits block indexing of that file (fail closed).

## 5. Change control

`gov cit propose|simulate|approve|reject|execute|rollback`. Simulation = deterministic impact traversal (depth by
radius from CHANGE_POLICY) + bounded retrieval → radius R0–R5, consequences, tests required, human-gate requirement
(radius above `auto_approve_max_radius` or trigger in `human_gate_triggers`) → gate record. Approval requires a
presented, answered gate (INV-008). Execution: snapshot → mutation manifest ops → propagation (retest flags, stale
tests) → derived views → incremental index → verification (schema, new dangling edges, freshness) → COMMITTED or
automatic ROLLED_BACK; explicit rollback restores the snapshot at any later time; interrupted executions are
classified and rolled back by `gov recover`.

## 6. Adoption (brownfield)

Stages A0–A11 map 1:1 to `gov adopt` subcommands with an evidence tree under `spec/audits/GOVERNANCE-ADOPTION/`
(files 00–12 per protocol §5). Independence is enforced mechanically: the reviewer (A5), migration verifier (A7)
and memory verifier (A10) must use a session id different from the planner/executor/builder that they check; A6 refuses
to run without an approved plan verdict; A8/A9 refuse without `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD`; A11 refuses
without `MEMORY_ACCEPTED_FOR_V4_AUDIT`; unknown artefacts block destructive batches; destructive actions require an
answered human gate; every batch has a snapshot and ledger and is rolled back when independent tests fail.

## 7. Releases, updates, upstream learning

`gov release build` stages an immutable payload + manifest (file hashes, schema/CLI/runtime/adapter versions,
migration ids, index rebuilds, breaking changes, human gates, rollback procedure, certification status).
`gov update --check` is a CIT-P against the project; `--apply` snapshots kernel/overlay/lock/generated, replaces the
kernel only, runs declarative migrations (overlay/lock/generated only — never `spec/` or `product/`), verifies overlay
preservation, regenerates adapters, rebuilds indexes, runs doctor + suite, and rolls back on failure.
`gov upstream prepare` builds a sanitised FRAMEWORK lesson packet (identifier redaction, path stripping, secret and
code-line scans, synthetic fixture only) and fails closed; `submit` re-validates, requires approval, enforces the
outbound allowlist (packet + declared synthetic fixture files) and records the payload hash in a ledger.
