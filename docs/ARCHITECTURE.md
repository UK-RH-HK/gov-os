# Governance OS — Architecture (repair candidate 4.1.5)

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

## 4.4a Verified kernel trust root
Every constitutional decision — authority levels, security floors, sensitivity classes, human-gate rules, export
rules, budget limits, plugin permissions, precedence itself — is read through one boundary (`kernel_trust`), never by
reading `governance/kernel/**` directly. The boundary: identify the installed release from `framework.lock`; verify
the payload against its own `KERNEL_MANIFEST.json`; verify that manifest against `framework.lock.kernel_manifest_hash`
(so neither file nor manifest can be rewritten alone); only then expose the payload as the policy root. When
verification fails, the immutable payload embedded in the binary is substituted **explicitly** — verified and
unverified sources are never mixed — the substitution appears in `gov policy overrides`, the context packet and doctor
D029, and every mutating operation (including `gov rebuild-memory`) fails closed with `KERNEL_TAMPERED`. The remedy is
`gov kernel reinstall`; an L4+ role may instead answer a presented gate raised by `gov kernel override`, bound to a
fingerprint of that exact kernel state so it cannot outlive it. Presenting and answering gates stay available while
untrusted, because that is the channel the remedy is recorded through.

## 4.5 Constitutional policy precedence
`framework/policies/POLICY_PRECEDENCE.yaml` is kernel data: an ordered list of layers (hard invariants →
security/authority → kernel policy → project policy → decisions/spec → task contracts → retrieved context) and, per
policy key, a mode — `immutable`, `floor` (only raise), `ceiling` (only lower), `additive` (lists may only grow),
`shrink_only`, `strengthen_only_bool`, `overridable`; keys without a rule are not overridable (deny by default).
`policy_precedence::evaluate` decides every `PROJECT_POLICY.policy_overrides` entry and every `PROJECT_EXCEPTIONS`
entry (which additionally needs a decision record and may relax only keys flagged `exception_relaxable`) before it
touches the effective policy. A refused override is recorded (`gov policy overrides`), reported by doctor D027
(CRITICAL), by the suite family `policy_precedence` and in context-packet layer 3, and leaves the effective policy
unchanged. Authority requirements can therefore only be raised, never lowered, by a repository.

## 4.6 Authority and policy enforcement
`authority::require(project, operation)` maps the session role (ROLES.yaml level L0–L5, `UNKNOWN_ROLE` otherwise)
against `AUTHORITY_POLICY.authority_levels_required` (missing operation → L3) and returns `AUTHORITY_DENIED` with the
required and actual level. It guards task create/status/claim/release/close, CIT propose/simulate/approve/execute/
rollback, gate create/present/answer, emergency/resume controls, checkpoints, handoffs, kernel install/reinstall,
update apply/rollback, tool install, adoption batches, upstream prepare/submit, benchmark/select, claims sweep.
`framework/policies/ENFORCEMENT_MAP.yaml` maps every policy key to its enforcing function; `policy_coverage::report`
verifies the map against the core and the `policy_enforcement_coverage` suite family fails on any unmapped key
(decision D-0003).

## 4.7 Governed capability plugins
A plugin descriptor is discovery, not authorisation (D-0005, D-0007). `TOOL_POLICY.plugins.min_authority` comes from
verified kernel policy and gates **every** plugin execution, registered or not; nothing inside a descriptor can widen
it. `approved_roles` in a descriptor may only narrow, and for a registered plugin the authoritative list is the
registry's; `provenance` and `status` in a descriptor prove nothing. Registration is an OS-written record in
`governance/generated/plugin-registry.json` (`gov plugins register|unregister|registry`) binding plugin id, version,
descriptor bytes and implementation bytes to the acting session, role and approving gate; an edited, re-versioned or
id-spoofing descriptor is `PLUGIN_REGISTRY_MISMATCH` for every role. Elevated permissions are approved only by the gate
recorded in that registry entry. `capabilities::governance::plugin_set` classifies every
descriptor for the acting role: **rejected** (fails the kernel `plugin-descriptor` schema — identity, version pin and
capability required — never executable), **denied** (valid but the role may not trigger it) or **usable**. Execution
requires: the role at/above `TOOL_POLICY.plugins.min_authority` for hand-declared descriptors or in `approved_roles`
for registered ones; every `required_permission_classes` entry held by the role (TOOL_PERMISSIONS); a presented,
answered registration gate for elevated permissions (`gov plugins register`); a resolvable executable; and a content
pin — a declared `pin.sha256` must match, and an implementation that changes without a version change is refused
(`PLUGIN_PIN_MISMATCH`). Plugins appear in the generated Tool/Capability Registry as `type: plugin`; doctor D028 and
the suite family `plugin_governance` report invalid, denied or drifting plugins.

## 4.8 Human Decision Gates and CIT approval
Human approval is never caller-supplied. `cit approve` derives the approval from the gate record raised for that
transaction: the gate must reference the CIT, be presented (`presented_by`/`presented_at`), be ANSWERED with option A,
and its decision record (written by `gov decide`) must be ACTIVE; the approval object records gate, decision,
answerer, answer kind and time, presenter and recorder. A presented-but-unanswered gate is `GATE_NOT_ANSWERED`, a
decline is `GATE_DECLINED` and marks the CIT REJECTED, a withdrawn gate is `GATE_REVOKED`, a re-answered or replaced
gate makes the approval `APPROVAL_STALE`. `cit execute` revalidates the same state before touching the repository.
Without a gate only the automatic path within `CHANGE_POLICY.auto_approve_max_radius` exists and its decision record
carries `human_approved: false`. `gov gate revoke` withdraws a gate and every approval derived from it.

**Trust classes (D-0007).** Immutable release state (verified kernel, embedded baseline) > OS-written project state
(governed records, plugin registry, ledgers) > verified derived state > project configuration (overlay, plugin
descriptors) > caller input (`--role`, `--by`, report fields) > plugin and model output. A fact named `approved`,
`registered`, `verified`, `human_approved`, `authority`, `provenance` or `override` is established only by the two
highest classes; the same field arriving from a lower class is a request that is recorded and ignored.

**Trust boundary.** The acting role is declared by the caller (`--role`, `GOV_ROLE`); the OS enforces what a role may
do but does not authenticate who holds the session. Deployments that need authenticated human answers must bind
`gov decide` to an authenticated channel (adapter responsibility); this is a documented boundary, not a hidden one.

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

### 6.1 Observed mutation scope
`task claim` snapshots the working tree (git `ls-files -co --exclude-standard` + sha256; walk fallback). `task close`
diffs the tree against that baseline, discards OS-managed paths (generated views, evidence records, gate/CIT/task
records) and contract-declared generated classes, and compares the observed set with the report's `files_changed`
and the task contract: undeclared or out-of-scope changes are `MUTATION_SCOPE_VIOLATION` unless a committed CIT
governs them (propagation writes count as governed). The report and checkpoint record `observed_files_changed` and
the baseline used.

## 7. Releases, updates, upstream learning

`gov release build` stages an immutable payload + manifest (file hashes, schema/CLI/runtime/adapter versions,
migration ids, index rebuilds, breaking changes, human gates, rollback procedure, certification status).
`gov update --check` is a CIT-P against the project and creates the framework-update gate; `--apply` requires that
gate presented and answered (`--approve` alone returns `applied: false`), snapshots kernel/overlay/lock/generated,
replaces the kernel only, applies the declared migration chain, then **reconciles template defaults**: every overlay
leaf that still equals the OLD kernel template inherits the NEW default (rule lists keyed by `pattern`/`id`), values
the project customised are preserved, and each change is listed in `overlay_reconciled`. The lock records the
release's commit (`release_commit`, from the release manifest / embedded payload / framework checkout — never the
consumer's HEAD, which goes to `installed_at_commit`) and a logical `source` label. `gov update --rollback [--reason]`
restores the snapshot, appends a `rollback` entry to `spec/reports/framework-updates.jsonl` (source and target
versions, identity and authority level, reason, migrations reverted, resulting lock, verification) and consumes the
snapshot (`SNAPSHOT_CONSUMED` on a second attempt). Migrations may use `set_overlay_rule` to change one element of a
rule list; `gov release build` refuses a new version whose migrations neither perform nor declare
(`overlay_template_changes`) an overlay-template change, and reproduces an already-released version from its recorded
`release_commit` (`git archive`) rather than the working tree.
It then runs declarative migrations (overlay/lock/generated only — never `spec/` or `product/`), verifies overlay
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
