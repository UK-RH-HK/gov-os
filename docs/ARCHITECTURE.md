# Governance OS — Architecture (repair candidate 4.1.3)

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

Retrieval router: query classification → routes (structured id/path, symbol incl. bare identifiers, lexical
exact/phrase, semantic, graph) → reciprocal-rank fusion → pinned reranker (optional plugin) → authority filter
(excluded statuses, superseded_by, archive default_retrieval) → namespace/role filter (`MEMORY_POLICY.namespaces` ×
`ROLES.yaml` groups) → per-artefact dedup → parent/section + 1-hop graph expansion → bounded cited slices.
Secret-class paths are never read; secret-content hits block indexing of that file (fail closed).

### 4.1 Replaceable embedder and reranker (pins, no silent fallback)
`EmbedSpec {id, version, dimensions, source}` is resolved from `MEMORY_POLICY.embedding` (overlay override
`MODEL_ROUTING_OVERRIDES` / `PROJECT_EXCEPTIONS` via `gov memory select`) to either the built-in hashed n-gram baseline
(`gov-builtin-embed`, zero dependencies) or a `gov-capability/1` embed plugin. The indexer records the live spec in
`meta.embedder` and in `index-manifest.json`; every query path (retrieval, context compiler, held-out regression, CIT
simulation, benchmark) embeds with the *live* spec and fails closed: `EMBEDDER_UNAVAILABLE` (pinned plugin missing),
`EMBEDDER_MISMATCH` (policy pin ≠ index, or vector dimension ≠ pinned dimension), `EMBEDDER_BAD_OUTPUT` (wrong
count/dimension from a plugin). The reranker (`MEMORY_POLICY.reranker`) is resolved the same way (`RERANKER_UNAVAILABLE`,
`RERANKER_MISMATCH`). Selection is evidence-driven: `gov memory benchmark` re-indexes each candidate into an isolated
database under `.governance-runtime/benchmarks/`, runs the held-out set and writes a research record; `gov memory
select` records a decision, sets the overlay override and performs a full rebuild.

### 4.2 Pin-aware builds and heterogeneous-index prevention
Before an incremental build the indexer compares the expected pins (embedder, chunking, lexical tokenizer, index
version) with the live `meta.*`; any difference escalates to a full build (`escalated_to_full`). Full builds are staged
into `state.db.building` and swapped in atomically, so a failed build never leaves a partial store. Freshness reports
`pin_mismatch` (fresh = false); doctor D025 counts vector dimension groups (mixed = CRITICAL) and pin differences
(HIGH); `task close` refuses with `INDEX_PIN_MISMATCH`.

### 4.3 State that survives rebuilds
Session claims live in `.governance-runtime/claims.db` (`ClaimsStore`), control state in `control.json`; neither is
touched by `gov rebuild-memory` (doctor D026 checks the claims store). Everything in `state.db` is derived.

### 4.4 Sensitivity classes
`SECURITY_POLICY.never_index_classes` / `never_export_classes` and `DATA_SENSITIVITY.classifications` become
`SensitivityRules` in the repository contract: a path classified restricted/confidential/secret is never indexed
(reason `sensitivity:<class>`), never retrievable, export-denied, and a dangling import to it is recorded as
`excluded:<path>`. The suite family reports such artefacts in the index as CRITICAL.

## 4.5 Authority and policy enforcement
`authority::require(project, operation)` maps the session role (ROLES.yaml level L0–L5, `UNKNOWN_ROLE` otherwise)
against `AUTHORITY_POLICY.authority_levels_required` (missing operation → L3) and returns `AUTHORITY_DENIED` with the
required and actual level. It guards task create/status/claim/release/close, CIT propose/simulate/approve/execute/
rollback, gate create/present/answer, emergency/resume controls, checkpoints, handoffs, kernel install/reinstall,
update apply/rollback, tool install, adoption batches, upstream prepare/submit, benchmark/select, claims sweep.
`framework/policies/ENFORCEMENT_MAP.yaml` maps every policy key to its enforcing function; `policy_coverage::report`
verifies the map against the core and the `policy_enforcement_coverage` suite family fails on any unmapped key
(decision D-0003).

## 5. Change control

`gov cit propose|simulate|approve|reject|execute|rollback`. Simulation = deterministic impact traversal (depth by
radius from CHANGE_POLICY) + bounded retrieval → radius R0–R5, consequences, tests required, human-gate requirement
(radius above `auto_approve_max_radius` or trigger in `human_gate_triggers`) → gate record. Approval requires a
presented, answered gate (INV-008); triggers in `CHANGE_POLICY.auto_simulate_triggers` simulate automatically at propose
time. The proposal and mutation manifest are secret-scanned at propose: matches are redacted, the record is
`secret_flagged`, and execution refuses with `SECRET_IN_MANIFEST`. Execution: snapshot → mutation manifest ops → propagation (retest flags, stale
tests) → derived views → incremental index → verification (schema, new dangling edges, freshness) → COMMITTED or
automatic ROLLED_BACK; explicit rollback restores the snapshot at any later time; interrupted executions are
classified and rolled back by `gov recover`.

## 6. Adoption (brownfield)

Stages A0–A11 map 1:1 to `gov adopt` subcommands with an evidence tree under `spec/audits/GOVERNANCE-ADOPTION/`
(files 00–12 per protocol §5). Independence is enforced mechanically: the reviewer (A5), migration verifier (A7)
and memory verifier (A10) must use a session id different from the planner/executor/builder that they check; A6 refuses
to run without an approved plan verdict; A8/A9 refuse without `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD`; A11 refuses
without `MEMORY_ACCEPTED_FOR_V4_AUDIT`; unknown artefacts block destructive batches; every destructive entry gets a Human Decision Gate record at A4 and A6
executes it only when that gate was presented and answered A (a CLI flag is never an answer; a gate answered B withdraws
the removal and defers its scaffolded tests with the recorded reason); every batch has a snapshot and ledger and is
rolled back when independent tests fail. `ARCHIVE_POLICY.unused_code_action` decides between removal and archival of
dead code. Catalogue entries carry `imports`/`references`/`consumers` from the import graph.

## 7. Releases, updates, upstream learning

`gov release build` stages an immutable payload + manifest (file hashes, schema/CLI/runtime/adapter versions,
migration ids, index rebuilds, breaking changes, human gates, rollback procedure, certification status).
`gov update --check` is a CIT-P against the project and creates the framework-update gate; `--apply` requires that
gate presented and answered (`--approve` alone returns `applied: false`), snapshots kernel/overlay/lock/generated,
replaces the kernel only, runs declarative migrations (overlay/lock/generated only — never `spec/` or `product/`), verifies overlay
preservation, regenerates adapters, rebuilds indexes, runs doctor + suite, and rolls back on failure.
`gov upstream prepare` builds a sanitised FRAMEWORK lesson packet (identifier redaction incl. hyphen/underscore
variants over every emitted field, path stripping, secret and code-line scans, `never_export_classes`,
`corroboration_min_sources`, lesson lifecycle, synthetic fixture only) and fails closed; `gov lessons cluster` groups
lessons into Framework Change Proposal records (D-0004); `submit` re-validates, requires approval, enforces the
outbound allowlist (packet + declared synthetic fixture files) and records the payload hash in a ledger.

## 8. Capability plugin host
`capabilities/host.rs` runs a plugin with a stdin writer thread, concurrent stdout/stderr drain threads (stderr tail
retained) and a watchdog that polls the child and kills its whole process group at the timeout (`PLUGIN_TIMEOUT`).
Responses far larger than the OS pipe buffer never deadlock; malformed output is `PLUGIN_BAD_RESPONSE`, a wrong
protocol id `PLUGIN_PROTOCOL_MISMATCH`. The kernel payload is embedded in the binary (`runtime/build.rs`), so
`gov init` needs no build-machine paths; the lock records a logical source id.
