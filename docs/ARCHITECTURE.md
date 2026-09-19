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
│   │                              # adapter-manifest.json, adapters/<id>/… (incl. adapters/hooks/provider-hooks.json)
│   ├── registry/plugin-registry.json  # where the OS-written plugin registry belongs (tracked T2; BC-P2-31)
│   ├── tests/memory/heldout.yaml  # held-out retrieval regression queries
│   └── framework.lock             # version, release_hash, kernel_manifest_hash, source, schema versions
├── spec/{now,product,features,requirements,architecture,workflows,interfaces,scenarios,data,security,
│         performance,research,experiments,decisions,planning,tasks,reports(/checkpoints),lessons,audits}
├── product/ (or any native layout mapped by the contract)
├── archive/{governance,spec,research,code-reference}
├── .governance-state/             # OS operational state that cannot be rebuilt (self-ignored by Git, never indexed,
│                                  # never deleted by a rebuild): control.json (emergency controls), claims, claim-tree
│                                  # snapshots, CIT/update/migration rollback snapshots (paths::OS_STORES)
└── .governance-runtime/           # derived, gitignored: state.db (SQLite+FTS5), context/, telemetry/, routing/,
                                   # outbound/ … — and, until each writer has moved (§4.3), legacy copies of the stores above
```

**Classification of the OS's own stores (BC-P2-31).** The kernel declares the stores the OS keeps and cannot rebuild
(`paths::OS_STORES`: claims, emergency control, claim-time tree snapshots, CIT/update/migration rollback snapshots —
class `operational`, machine-local — and the plugin registry — class `authoritative`, tracked, OS-written T2) and
applies that classification after the overlay's rules, so no overlay rule (the template's blanket
`.governance-runtime/**: derived`, a hostile `**: derived`) can make the product call them derived or generated: they
are never indexed, retrieved or exported and are `mutation: os-only`, wherever they currently are. Writers resolve
their location with `paths::store_path` and move a legacy copy once with `paths::relocate_legacy` (identical copies are
removed; differing copies are `STATE_LOCATION_CONFLICT`, nothing overwritten); `paths::misplaced_os_state` lists every
store still kept inside the derived runtime directory or `governance/generated/`.

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
Everything in `state.db` is derived; `gov rebuild-memory` never touches the OS stores of §3, wherever they are.
**Emergency-control state** lives in `.governance-state/control.json` (`paths::store_path(root, "emergency-control")`),
so deleting the whole derived runtime directory never lifts a freeze or a pause. A `control.json` an older binary left in
the runtime directory is still honoured — while both exist the stricter state is in force (frozen if either is frozen,
paused if either is paused) — and the next control command (`pause`, `freeze-writes`, `cancel-agents`, `resume`) moves
the state where it belongs and removes the legacy copy. The other writers (claims and claim trees, the CIT/update/
migration snapshots, the plugin registry) resolve their locations through the same API as each moves; until then
`paths::misplaced_os_state` reports them, and the classification above already keeps them out of every derived
deletion set (doctor D026 checks the claims store). Because a rebuild changes only derived state, it stays available
under FREEZE_WRITES and PAUSE (§4.6).

Failure memory (BC-P2-32, framework §18) is durable: tool failures observed while indexing or retrieving are governed
evidence records under `spec/reports/failures/`; retrieval misses — an agent's logged query whose best evidence covers
less than `MEMORY_POLICY.failure_memory.retrieval_miss.min_evidence_coverage` of the question, or a miss an agent
reports with `gov memory miss` — are memory-quality events under `spec/reports/memory-quality/` that are never indexed.
One record per signature; `gov memory failures` lists those whose follow-up is not yet linked to work. The
`failure_memory` keys are strengthen-only.

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

**Admission on a machine with no trust anchor (OWNER-DECISION-P2-0002, Option A).** The one verification policy
(`srr::verifier::admit`) decides it for every ingress (`init --source`, `update`, `adopt migrate`, `kernel reinstall`,
rollback, recovery): on a machine with no administrator-provisioned Signed Release Root, kernel material from any
external source is refused `SRR_UNPROVISIONED_EXTERNAL_SOURCE_REFUSED` (typed, remediation: provision), decided by the
digest of the privately staged bytes, never by path; the only payload such a machine admits is the one embedded in the
running `gov` binary, and only as a marked **bootstrap** installation (`admission: BOOTSTRAP_EMBEDDED_PAYLOAD`, tied to
the binary's identity) that is never presented as current, verified or certified — every command envelope says
`presented_as: UNAUTHENTICATED` with the BOOTSTRAP disclosure, `framework.lock` and `gov trust status` carry the
marking, and doctor D032 fails on it. A bootstrap installation rewritten after install, or kernel material the machine
never admitted (e.g. arriving with a clone), is `KERNEL_TAMPERED` / `KERNEL_UNANCHORED` (remediation: provision, then
verify the pinned signed release). The documented first run is therefore **provision, then install**:
`gov trust provision --anchor <root metadata from the administrator domain>`, then `gov init --source <release signed
under it>`; a dev/test machine provisions a throw-away root, as the certification harness does. On a provisioned
machine the embedded payload without signed metadata is refused `SRR_RELEASE_UNVERIFIED` (R1 behaviour unchanged).

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

Every key of the project overlay documents `PROJECT_POLICY.yaml` and `MODEL_ROUTING_OVERRIDES.yaml` is evaluated the
same way, not only `policy_overrides` (BC-P2-45): a value equal to the kernel/template value changes nothing; any other
value must satisfy its rule (`PROJECT_POLICY.readiness.*` strengthen-only, `staleness.on_stale_close` ordered floor,
descriptive keys such as `project.*` overridable, the rest immutable; `MODEL_ROUTING_OVERRIDES` tier and reasoning
floors, `providers`/`preferences` free). A refused weakening is replaced by the kernel value in what the product reads
(`Project::project_policy`, `routing::effective_overrides`) and reported as above.

**Which rules govern.** Two rule sets can speak about a key: the installed, verified kernel's rules and the
constitutional floor compiled into the running binary. `policy_precedence::Governing` evaluates a key against every
set that declares a rule for its policy or overlay label and accepts it only when every such set accepts it, so a
newer binary never lowers a floor an installed kernel declares and an older kernel never lowers a floor the binary
enforces. A set with no rule at all for a label predates that label's evaluation and does not govern it: the kernels
shipped as 4.1.4 and 4.1.5 carry no `PROJECT_POLICY`/`MODEL_ROUTING_OVERRIDES` rules, so on those kernels the binary's
rules decide the overlay documents — descriptive keys stay descriptive and every floor is still enforced (round-1
integration observation O-1). `gov policy overrides` lists the governing sets under `precedence.governing_sets`.

## 4.6 Authority, acting role and the G0 guard
**Acting role (BC-P2-08).** Every invocation resolves its role once: the global `--role <id>`, else `GOV_ROLE`, else
*undeclared*. An undeclared invocation carries **L0** — no privileged authority (framework §23: no worker behaves as
an orchestrator unless assigned); the old default `orchestrator` is gone. The resolved role is installed process-wide,
so every project the command opens internally (`init`, every `adopt`/`migrate` stage, the first install batch) is
evaluated against the same declared role. A stage flag (`adopt review --reviewer-role`, `verify-migration
--verifier-role`, `verify-memory --verifier-role`) may declare the role when nothing else does and must agree with it
otherwise (`ROLE_CONFLICT`). A declared L5 role (`human`) carries L0: human authority is exercised only through the
authenticated human channel (§4.8). Agent roles L0–L4 remain declared by the harness or adapter that launches the
agent (OWNER-DECISION-P2-0001); the OS enforces what the declared role may do and gives an undeclared one nothing.

**Authority.** `authority::require(project, operation)` maps the acting role (ROLES.yaml level, `UNKNOWN_ROLE`
otherwise) against `AUTHORITY_POLICY.authority_levels_required` (a class the installed kernel lacks is read from the
kernel embedded in the binary, else L3) and refuses `AUTHORITY_DENIED` with `details.cause` = `ROLE_UNDECLARED`,
`HUMAN_ROLE_CLAIM` or `LEVEL_TOO_LOW` and the remediation. Before the first install, lifecycle ingress is checked
against the embedded kernel (`require_with_embedded_kernel`).

**G0.** `orchestration::control::COMMAND_GUARDS` classifies every CLI command label by effect (`Read`/`Write`),
authority class and scope; the CLI maps each invocation to one label (`g0_label`) and `control::g0` runs before
dispatch: an unclassified label is refused (`G0_UNCLASSIFIED`); a `Write` is refused under FREEZE_WRITES (`FROZEN`)
or PAUSE (`PAUSED`, exit 4) unless its label is on the explicit recovery allow-list, each entry with its reason —
the emergency controls themselves, `cit rollback` (ROLLBACK_TRANSACTION), `telemetry emit`, `rebuild-memory` /
`memory rebuild` (they rebuild only derived index state, deterministically, from Git and the authoritative records),
and under PAUSE also `gate present`; then the authority class is evaluated for the declared role. Evidence-writing
commands (`audit`, `verify governance|product`, `health run|product|close-check`) are writes of the `record_audit`
class and are refused under the controls; their non-persisting forms (`audit --no-persist`, `health run
--no-persist`) stay available for diagnosis. The runtime guard `control::guard_write` (kernel trust, OWNER-DECISION-0006
§6, emergency state) still runs inside every mutating path.

**Hard-blocks at G0.** `control::guard_write` also passes governed work that starts, hands off or completes work —
`task create|claim|close`, `cit propose`, `handoff create` — through the health scheduler's hard-blocks
(`scheduler::guard`): while a check whose block rule governs the operation stands failed, the operation is refused
`HEALTH_HARD_BLOCK` naming the check; a block whose inputs changed is re-evaluated first, so a repaired condition never
keeps refusing work. Operations that apply a sanctioned change which may itself be the remedy (`cit approve|execute`,
`update --apply`, `adopt migrate`, `release build`) are guarded at their own hosts with their targets, never here.

`framework/policies/ENFORCEMENT_MAP.yaml` maps every policy key to its enforcing function; `policy_coverage::report`
verifies the map against the core and the `policy_enforcement_coverage` suite family fails on any unmapped key
(decision D-0003).

## 4.7 Governed capability plugins
A plugin descriptor is discovery, never authorisation (D-0005 as amended by
[D-0010](../spec/decisions/D-0010.yaml); D-0007; Contract v3 F4; ARCH-0003 §9; API-0001 1.2). The OS classifies a
plugin by **what its command executes**, never by what its descriptor declares (`capabilities::binding`):

* **OS-provided** — the command runs this very `gov` binary (same inode, or byte-identical) as its own capability server
  (`capabilities serve-embed [--id X] [--reverse]`). Its effects are the release's own, so it keeps the hand-declared
  allowance: roles at/above `TOOL_POLICY.plugins.min_authority` may run it.
* **Executable** — anything else (a script, an interpreter running a module or inline code, a binary). It runs only
  with a registration `gov plugins register` wrote (T2-sealed, §4.8) **and** an owner-answered Human Decision Gate raised
  for exactly that plugin identity, version, implementation and permission set (trigger `privilege_elevation`,
  human-only), both re-verified at every execution; unregistered it is refused `PLUGIN_NOT_APPROVED` (`cause:
  UNREGISTERED_EXECUTABLE`) for every role.

The registration binds every byte the command executes as the OS derives it — the program resolved on `PATH`, every
script argument, the whole top-level package of a `python3 -m` command (with `__pycache__`), inline code (inside the
descriptor), and any path listed under `implementation:` — plus the descriptor bytes, the registration subject digest
the gate's answer is bound to, and the authoritative `approved_roles`, permission classes and permissions. Any changed,
added or removed byte, an edited descriptor, a version drift or a widened permission set fails closed
(`PLUGIN_PIN_MISMATCH`, `PLUGIN_REGISTRY_MISMATCH`); an implementation the OS cannot locate never runs
(`PLUGIN_IMPLEMENTATION_UNRESOLVED`); a registry entry that does not verify is `PLUGIN_REGISTRATION_UNBOUND`. There is no
trust-on-first-use: nothing machine-local re-baselines a plugin. Plugins run without the caller's loader variables
(`PYTHONPATH`, `LD_PRELOAD`, `NODE_OPTIONS`, …). Declared `permissions` / `required_permission_classes` only narrow (the
acting role must hold them) and are shown in the gate package, raising its impact radius; they never decide whether
approval is needed. `gov plugins registry` shows every entry with its T2 binding and whether it is honoured. Plugins
appear in the generated Tool/Capability Registry as `type: plugin` (an unregistered executable as `unregistered`, with
no approved roles); doctor D028 and the suite family `plugin_governance` report unregistered executables, drift,
unbound entries and unapproved registrations. A tool installation's approval is likewise bound to that installation
(`gates::create_system` trigger `tool_install`, subject = the installation digest), and a security review is evidence
only as a T2-verified close report of a `security`-class task naming exactly that tool and version, written by another
session and role.

## 4.8 Human Decision Gates, the authenticated human channel and CIT approval
**Decision package (BC-P2-49).** A gate is created only with substantive content for every
`HUMAN_GATE_POLICY.decision_package_fields` entry and at least one option with a unique id (`GATE_PACKAGE_INCOMPLETE`
lists what is missing or non-substantive); system-raised gates get framework-authored content per trigger for the
fields the raising code did not supply; the OS derives the exact permitted next actions; an answer outside the offered
options is `GATE_OPTION_INVALID`. Each option states whether it authorises the blocked work (default: `A` only).

**Human answers (BC-P2-10, mechanism HC-1).** A human answer, a human-approval assertion and the evidence that a gate
reached the human come only from **owner-signed documents** verified against the administrator-provisioned anchor:
the provisioned Signed Release Root's delegation of the `human-gate` role (the same anchor that governs releases and
break-glass). `gov gate present <HDG>` renders the package, records `presented_at`/`presented_by` and the package
SHA-256, writes the exact bytes to the channel outbox and seals the record — rendering is **not** presentation. The
owner signs a `human-gate-answer` binding the product, gate id, the OS-issued `gate_instance`, the package SHA-256, the
option, `answered_by`, a single-use nonce and an expiry; it is placed in the channel inbox or passed with `gov decide
<HDG> --answer-file`. Anything else is refused: `HUMAN_ANSWER_UNAUTHENTICATED` (missing, unsigned, wrong key, below
threshold, expired, replayed, bound to another gate/instance/package/option), `HUMAN_ANSWER_MISMATCH` (`--option`
disagrees with the signed option). `presented_in_chat` becomes true only on an owner-signed answer or an owner-signed
`human-gate-receipt` (`gov gate present <HDG> --receipt-file f | --receipt-inbox`). The signed envelope is stored and
re-verified against the current anchor at every use (`HUMAN_ANSWER_UNVERIFIED`). `gov` holds no signing key; CLI flags
(`--by`, `--option`, `--role human`), environment variables, defaults, repository files, plugins and model output cannot
produce an answer. `gov trust human-channel` reports the anchor, inbox/outbox, what a document binds and whether the
anchor is writable by the invoking account (the ARCH-0003 §1 premise).

**No release root, no human channel (P2-ADJ-0001).** `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned`
is `false`: on a machine with no Signed Release Root a human answer is refused `HUMAN_CHANNEL_UNAVAILABLE` with
`details.cause: UNPROVISIONED` and the remediation — provision a root whose `human-gate` role delegates the product
owner's key(s) (`gov trust provision --anchor <root.json>`); `gov trust human-channel --provision` of a standalone
anchor is refused `HUMAN_CHANNEL_STANDALONE_DISABLED`; an anchor file placed in machine state is not honoured. The key
is strengthen-only: a project may keep it false, never set it true; a kernel that predates the key reads as false. A
dev/test machine provisions a throw-away root (OWNER-DECISION-P2-0002: provision, then work).

**T2 binding (BC-P2-09).** OS-written state — gate and decision records, CIT state (`os_state`), close reports and
claim baselines, the plugin registry (every entry and the document), the adoption record, health evidence, research/
experiment/data records, retrieval-profile decisions — carries an `os_binding` seal: HMAC-SHA256 over the record's
canonical content, the operation and the time, under a key kept in protected machine state, never in a repository
(`t2`). A consumer honours a T2 fact only when the seal verifies; a hand-written or edited record is `UNSEALED` /
`BROKEN` and never honoured (`T2_UNBOUND`). An OS writer that rewrites a record the OS sealed re-seals it only when its
seal verified immediately before the write — the OS never blesses content it did not write (gate writes to task and CIT
records, CIT propagation markers, lifecycle backlinks). `gov gate list` reports unverified gates separately, `gov gate
show <HDG>` reports the binding and scope, the answer's verification and what the gate authorises, and `t2::audit`
(suite family `os_binding_integrity`, doctor D033) lists every T2 record and plugin-registry entry no OS operation
produced, with the severity of what it is (tampering in force is high).

**T2 facts across the owner's machines (P2-ADJ-0002).** A seal has a scope. *Machine scope* (`hmac-sha256/t2-v1`,
the machine's own key) is honoured only on the machine that wrote it. *Provisioned scope* (`hmac-sha256/t2-v2`) is made
under the owner's **T2 binding authority** and is honoured on every machine provisioned with that authority, so gates,
decisions, CIT state, plugin registrations and governed evidence written on one of the owner's machines are honoured on
the others after a Git clone or pull. The authority is delegated through the provisioned root, and nothing about it is
in any repository:

1. the owner's Signed Release Root delegates the role `t2-binding` to the owner's key(s);
2. the owner generates a 32-byte binding key and signs a `t2-binding-authority` document with the `t2-binding` key(s)
   at threshold, binding the product, the authority id (`t2a-` + a digest of the key) and a commitment to the key, with
   `issued`/`expires` — `gov` verifies and never signs;
3. the administrator installs the bundle (`t2-binding-provisioning`: the signed authority and the key) on each of the
   owner's provisioned machines from the administrator domain, `gov trust t2-binding --provision <bundle>`. It is
   refused on an unprovisioned machine (`T2_AUTHORITY_UNPROVISIONED`), for a file inside a repository
   (`T2_AUTHORITY_FROM_REPOSITORY_REFUSED`), when this machine's root delegates no `t2-binding` role
   (`T2_AUTHORITY_ROLE_NOT_DELEGATED`) or does not verify the signature at threshold (`T2_AUTHORITY_UNAUTHORISED` —
   another owner's root, an agent's own key), for an expired authorisation (`T2_AUTHORITY_EXPIRED`), for a key other
   than the one authorised (`T2_AUTHORITY_KEY_MISMATCH`), and below floor (OWNER-DECISION-0006 §6 bullet 4). The key is
   kept with mode 0600 and never printed;
4. a portable seal binds the authority, the sealing machine's id, the operation, the time and the content. A machine
   honours it only when it holds the authority's key (the MAC verifies) **and** its own trusted root authorises the
   authority now — the signature is re-verified against the current root, so a root successor that drops the
   `t2-binding` key revokes it (records become `UNAUTHORISED`). Expiry bounds when an authority may seal new records;
   what it sealed while valid stays honoured.

Anything else is refused, typed and observable: a record written by an unprovisioned machine, by a machine the owner's
provisioning did not give the authority, or sealed before the authority existed, is `FOREIGN` (machine scope); one
written by another owner's machine is `FOREIGN` (provisioned scope, an authority this machine does not hold). A machine
without a usable authority keeps working in the machine scope, and `gov trust t2-binding` says so and why (unprovisioned,
no `t2-binding` delegation, none installed, revoked, expired). `gov trust t2-binding --reseal [--dry-run]` (L4) re-seals
under the authority exactly the records this machine sealed while it was provisioned, keeping their recorded operation
and time; records sealed while it was unprovisioned, and records whose seal does not verify, are left as they are.
*What it proves:* a process that can write the repository but cannot read protected machine state cannot produce a
honoured record on any machine. A process with the operator's OS privileges on one of the owner's machines can read the
binding key; against it the seal is detection-grade, and what it forges there is honoured on the owner's other machines
holding the same authority (inherent in the requirement that one machine's facts are honoured on the others). The facts
that must hold against it — human answers and human-approval assertions — stay bound to the owner's signature. The key
is shared by the machines that hold it (`gov` never signs, so no per-machine signature exists): revocation is per
authority, or per machine when the owner issues one authority per machine.

**Agent resolution (BC-P2-18).** An agent answer (`gov decide <HDG> --option X --by <acting role>`) is accepted only
for an L3+ role resolving as itself, on a complete assessment (radius ≤ R1, confidence ≥ 0.8, reversible) made by
another session or the OS, with a recorded rationale; it records `by_kind: agent` and is never a human approval. Gates
raised for `HUMAN_GATE_POLICY.human_only_triggers` (`framework_update`, `destructive_migration`, `privilege_elevation`,
`kernel_integrity_override`, `tool_install`, `budget_threshold`, `upstream_export`, `experiment_promotion` — a kernel
floor a project may extend, never shrink) are never agent-resolvable, at answer time or at use.

**Evidence a gate rests on (J1).** A gate created with `derived_from` / `evidence_refs`, and an answer citing
`--evidence` (or answering a gate so derived), may rest only on governed research and experiment evidence: research
that is not complete governed evidence (J1 fields, CONCLUDED) is refused `EVIDENCE_NOT_CITABLE` before anything is
written, and the cited records gain the gate and the decision in their `influences` backlink (re-sealed only when their
seal verified).

**Blocking and CIT approval.** An authorising answer moves the tasks the gate blocks from WAITING_HUMAN to READY, a
declining answer to BLOCKED, and `gov gate revoke` withdraws the gate (derived decisions REJECTED, the linked CIT back
to SIMULATED, blocked work BLOCKED). `cit approve` derives the approval from the gate raised for that transaction: the
gate must reference the CIT, be presented, be ANSWERED with an authorising option through a verified answer, and its
decision must be ACTIVE (`GATE_NOT_PRESENTED`, `GATE_NOT_ANSWERED`, `GATE_DECLINED`, `GATE_REVOKED`, `APPROVAL_STALE`,
`APPROVAL_METHOD_MISMATCH` for `--method human` on an agent resolution); `cit approve|execute` and `update --apply`
first require that the gates they rely on are records gov wrote whose answers verify. Without a gate only the
automatic path within `CHANGE_POLICY.auto_approve_max_radius` exists and its decision carries `human_approved: false`.

**Trust classes (D-0007).** Immutable release state (verified kernel, embedded baseline) > OS-written project state
(governed records, plugin registry, ledgers) > verified derived state > project configuration (overlay, plugin
descriptors) > caller input (`--role`, `--by`, report fields) > plugin and model output. A fact named `approved`,
`registered`, `verified`, `human_approved`, `authority`, `provenance` or `override` is established only by the two
highest classes; the same field arriving from a lower class is a request that is recorded and ignored.

**Trust boundary.** Agent roles are declared by the harness or adapter (OWNER-DECISION-P2-0001); the OS enforces what
a declared role may do and gives an undeclared or `human`-claiming invocation L0. Human answers are authenticated by the
owner's signature against the provisioned root; the private key is never on the agents' machine.

## 4.9 Health scheduler, context delivery, artefact identity, qualification oracle
**Health scheduler (BC-P2-03/06/42/43).** `gov health` runs tiered checks G0–G6 (`scheduler::catalogue` declares each
check's inputs, isolation, cache treatment, tiers and hard-block vs warning rule; `gov health checks` prints it).
Checks whose declared inputs changed execute — concurrently when independent, state-writing ones in disposable
sandboxes — and the rest are served from a cache keyed by those inputs; each result is recorded with its provenance
(`gov health history|show`). Green governance evidence is keyed by every input class (`verification::currency`,
`gov health currency`); a change makes it stale and doctor D021 says which class changed. `gov health status` reports
RED/YELLOW/GREEN and the active hard-blocks; `gov health guard <op>` shows whether a governed operation would be
refused (§4.6). Product-test results are recorded per family as governed evidence (`gov health product`,
`gov verify product`); skill regression executes the kernel's skill scenarios (`gov health skills [--record]`).
**Only T2-honoured evidence counts:** governance-suite and product-test records are sealed when written, and currency
(`currency::latest_green`, the product-evidence cache) honours only records whose seal verifies on this machine —
under the owner's binding authority that includes records written on the owner's other provisioned machines (§4.8);
doctor D021 names green records that are not honoured. The currency key includes the class `t2_bindings` (a digest of
`t2::audit`), so a forged or edited T2 record, or a changed binding, stales green evidence. The suite families added in
repair iteration 1 are `lineage_orphans` (W7: unconsumed outputs, requirements without an implementation/test path,
unconsumed research, unjustified acceptance tests and code — each turned into one idempotent investigation task at a
persisted G4-G6 run, never a deletion), `os_binding_integrity` (T2 records no OS operation produced), `installation_
authenticity` (an installation whose release authenticity is not established), `contract_binding` (the canonical
contract chain, G5/G6), `index_content_coverage` (indexed chunks cover the artefact's current content),
`task_contract_integrity` (production-merge violations), plus the W8 stale-link, W1 misplaced-record and W5
untraceable-work findings of `graph_integrity` / `product_traceability` and W4 delivery verification in
`context_reproducibility`. Doctor adds D032 (installation authenticity / admission: fails on a bootstrap or not-admitted
installation), D033 (T2 binding: tampering and an unsealed gate in force fail; legacy, hand-written and other-machine
records are disclosed) and D034 (failure memory: an open tool failure degrades). `gov health qualify --kind K --oracle
f --report f [--public-suite d]… [--repository d]… [--run-id id]` is the G6 entry: it refuses unless the oracle conforms
and is separate from the public suites, the given repositories and this repository, and the score report conforms and
is bound to it; the record keeps only a one-way commitment to the oracle, the report digest and numeric metrics.

**Context delivery (BC-P2-17/19/20).** A task's mandatory inputs form a manifest resolved deterministically from the
task record (`gov context manifest <TASK>`); the packet delivers each input's full content with its version and hash,
marks an index outage explicitly (the supplementary block alone depends on the derived index) and is kept by hash
(`gov context show <TASK> [--hash]`); `gov context verify <TASK>` re-resolves the manifest against a compiled packet;
`gov context receipt <TASK> --file f` validates a worker's consumption receipt (a dry run).

**Change propagation and continuity (BC-P2-04/05, WS-4).** An upstream change — through CIT-E or made directly —
reaches open and completed consumers: open work is marked `retest_required`, completed work `revalidation` with a
generated revalidation task, and closing reports, test obligations, scenarios, checkpoints, handoffs and stored packets
are marked stale or `invalidated` (idempotently; normative-content hashing keeps bookkeeping edits from looking like
upstream changes). `gov cit propagate [--dry-run]` detects direct changes from what each task consumed; `gov context
staleness <TASK>` shows a task's stale inputs; a close is refused `INPUTS_STALE` / `RETEST_EVIDENCE_REQUIRED` until
retested (the close-side call is the host's). A checkpoint records the task's mandatory inputs (ids, versions,
content/normative hashes, what was delivered), a state reference taken after the index is current and the triggers
observed since the previous one; it is stale when what it captured changed (`gov checkpoint freshness`). Handoffs refuse
unsatisfied mandatory inputs (`HANDOFF_INPUTS_UNSATISFIED`) and re-deliver a stale packet as an explicitly degraded
handoff; `gov session close` is never refused for staleness but states its degradation; the watchdog counts commands
and changed files itself and checkpoints every unobserved trigger at the next boundary. The generated
**provider hooks** (`governance/generated/adapters/hooks/provider-hooks.json`) let a harness wire the triggers it owns —
`gov checkpoint create --trigger before_compaction` before a known compaction, `gov session close` at session end,
`gov checkpoint create --trigger before_model_switch` before a model switch — so they fire without relying on the
agent (the hooks run with the session's declared `GOV_ROLE`/`GOV_SESSION`; like every write they are refused under
FREEZE_WRITES/PAUSE, and a refusal is typed). Contradictions precedence cannot resolve among current authoritative
records (declared conflicts, supersession forks, decisions answering one question differently) are detected, every
member is flagged `CONTRADICTORY` in any manifest that includes it (the packet is `BLOCKED`, never delivered as
authority) and each is routed to a system gate (`trigger: contradiction`) whose verified answer resolves it.

**Knowledge-fabric integrity and retrieval profile (BC-P2-28/30, WS-6).** Every index build runs the graph-integrity
check (`gov memory integrity`): orphan (low), dangling and stale (medium: an in-force relation to a superseded,
retired or historical target), reversed / ill-typed (medium, per relation-type endpoint signatures) and supersession
cycles (high). The embedder and reranker are identified by adapter, model artefact and inference runtime; pins bind the
revision actually executed and fail closed on any component change (`EMBEDDER_MISMATCH` naming the component,
`EMBEDDER_REVISION_MISMATCH`, `RERANKER_REVISION_MISMATCH`; an incremental build escalates to a full re-embed). A
profile change is governed (`gov memory select <candidate> --research RES-x [--gate HDG-x]`): T2-verified benchmark
evidence measuring exactly the candidate (`PROFILE_EVIDENCE_REQUIRED|_UNBOUND|_STALE`), the change gate for its radius
(R5: an owner-signed answer bound to the exact change), a full re-index, a recorded held-out regression — a regressed or
unmeasured result rolls back (`PROFILE_REGRESSION_FAILED|_UNMEASURED`) — and a sealed decision. `gov memory profile`
reports whether the pinned profile is governed (`UNGOVERNED_CHANGE` names a hand edit).

**Research, experiments and test data (BC-P2-46/47/48, WS-10).** Research is governed evidence only when complete (J1:
question, reason, method, sources or data, measurements, uncertainty, conclusion, confidence) and CONCLUDED
(`gov research record|update|conclude|withdraw|sync|show|check`; incomplete → `RESEARCH_INCOMPLETE`, a draft is held
reference-only); experiments run a DESIGNED → RUN → reproduced → CONCLUDED lifecycle with frozen design, recorded runs
and reproducibility, and enter production only through a promotion gate answered by the owner
(`gov experiment design|update|run|reproduce|conclude|promote|abandon|show|check`; `EXPERIMENT_*`); test data carries
provenance and independent authorship (`gov data register|show`; `DATA_*`) and scenarios trace to data and tests
(`gov scenario trace|check`; `SCENARIO_*`). Every lifecycle write is T2-sealed and records the decisions and tasks it
influenced.

**Artefact identity (BC-P2-21).** `gov artefact show <id>` reports the W1 identity of a governed artefact (type,
canonical location, authority, lifecycle, content hash, provenance, supersession, expected and actual consumers);
`gov artefact check` lists misplaced records, duplicate ids, stale links and unconsumed outputs; `gov artefact lineage
<id> --direction down|up` walks canonical edges.

**Qualification oracle (BC-P2-51).** `gov oracle format` prints the Qualification Oracle format compiled into the binary
and its crosswalk to Contract v3 Gate V; `gov oracle validate <file> [--oracle f] [--public-suite d] [--repository d]`
validates an oracle or a score report held in verifier custody, fail-closed. Neither opens a governed project.

## 5. Change control

`gov cit propose|simulate|approve|reject|execute|rollback|classify|propagate`. **Materiality is derived** (BC-P2-13):
`cit::materiality` classifies what a change touches (record types and fields, paths, file content, declared path
targets) into the eight Contract v3 classes — architecture, interface, acceptance criteria, behaviour, security,
governance, infrastructure, data migration — and the effective triggers are the declared label ∪ the derived classes, so
a mislabelled material change is still simulated and gated (`gov cit classify [--id] [--paths] [--base]`). Simulation =
deterministic impact traversal (depth by radius from CHANGE_POLICY) + bounded retrieval → radius R0–R5 (at least the
floor of every derived class), consequences, tests required, human-gate requirement (radius above
`auto_approve_max_radius` or an effective trigger in `human_gate_triggers`) → a system gate whose subject digest binds
the transaction content and its simulated impact (BC-P2-11). CIT state is T2-sealed (`os_state`); approve and execute
re-derive the content, impact and binding digests and refuse `APPROVAL_STALE` (changed after the answer),
`GATE_MISMATCH`, `T2_UNBOUND` / `CIT_STATE_MISMATCH` (hand-written, copied or unsealed state), and a re-simulation that
changes the content or impact raises a new gate. Approval requires a
presented, answered gate (INV-008); triggers in `CHANGE_POLICY.auto_simulate_triggers` simulate automatically at propose
time. The proposal and mutation manifest are secret-scanned at propose: matches are redacted, the record is
`secret_flagged`, and execution refuses with `SECRET_IN_MANIFEST`. Execution: snapshot → mutation manifest ops → propagation (retest flags, stale
tests) → derived views → incremental index → verification (schema, new dangling edges, freshness) → COMMITTED or
automatic ROLLED_BACK; explicit rollback restores the snapshot at any later time; interrupted executions are
classified and rolled back by `gov recover`.

## 6. Adoption (brownfield)

Stages A0–A11 map 1:1 to `gov adopt` subcommands with an evidence tree under `spec/audits/GOVERNANCE-ADOPTION/`
(files 00–12 per protocol §5). **Independence from recorded authorship (BC-P2-34, WS-9).** Every stage resolves its
actor — the invocation's declared role and declared session (the global `--session`, else `GOV_SESSION`, installed once
by the CLI; `adopt review --reviewer-session` as the stage's own declaration) — and records it in the T2-sealed adoption
record `00-BASELINE.yaml` (a hand-edited record decides nothing: `T2_UNBOUND`). An undeclared session cannot author a
stage (`ADOPTION_SESSION_UNDECLARED`); two declarations conflict (`SESSION_CONFLICT`, `ROLE_CONFLICT`); a session keeps
the role it first acted under (`ADOPTION_ROLE_INCONSISTENT`). Each independent stage is performed by its designated
kernel role — A5 `migration-reviewer`, A7 `migration-verifier`, A10 `memory-verifier`, A11 `independent-auditor` — in a
session and role that authored no planner, executor or builder stage (`INDEPENDENCE`, `details.cause`). The A5 approval
needs at least one reviewer-authored test (`INDEPENDENT_TESTS_REQUIRED`, `INDEPENDENT_TESTS_INVALID`) and binds the
catalogue, plan and tests by digest: A6/A8 refuse `APPROVAL_STALE` when any changed after approval; A7 accepts only a
computed verdict with at least one executed test against exactly the approved artefacts (a contradicting claim is
`VERDICT_CONFLICT`); A10 needs verifier-authored held-out queries (`INDEPENDENT_HELDOUT_REQUIRED`); A11 runs the G5
tier. Destructive-migration gates are bound to the catalogue entry they were raised for. Mechanically, A6 refuses
to run without an approved plan verdict; A8/A9 refuse without `MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD`; A11 refuses
without `MEMORY_ACCEPTED_FOR_V4_AUDIT`; unknown artefacts block destructive batches; every destructive entry gets a Human Decision Gate record at A4 and A6
executes it only when that gate was presented and answered A (a CLI flag is never an answer; a gate answered B withdraws
the removal and defers its scaffolded tests with the recorded reason); every batch has a snapshot and ledger and is
rolled back when independent tests fail. `ARCHIVE_POLICY.unused_code_action` decides between removal and archival of
dead code. Catalogue entries carry `imports`/`references`/`consumers` from the import graph.

### 6.1 Claims and observed mutation scope
`task claim` is decided in one store transaction (`ClaimsStore::claim_exclusive`): another session's live claim is
`TASK_CLAIMED`; the same session holding it from another worktree `CLAIM_WORKTREE_MISMATCH`; a task the DAG does not
find runnable `TASK_NOT_RUNNABLE` (every reason listed — dependencies, `blocks`, required data/tools/skills, the
mandatory input manifest, every governing gate, readiness and test policy, recorded-authorship independence, explicit
holds); a new session beyond
`BUDGET_POLICY.defaults.max_parallel_agents` `BUDGET_EXCEEDED` (with a budget gate); a live claim of another session
whose mutation scope (`allowed_paths`, unrestricted when empty) may share a path `CLAIM_SCOPE_CONFLICT`; a store kept
busy beyond its timeout `CLAIMS_BUSY`. Linked git worktrees of one repository claim against one store. A task's `role`
binds claim and close (`ROLE_NOT_DESIGNATED`), and `task create` refuses a role the kernel does not define
(`UNKNOWN_ROLE`). The claim snapshots the working tree; `task close` requires the closing session to hold the claim
(`CLAIM_REQUIRED`) from the same worktree, diffs the tree against the baseline, attributes changes to other live claims
or accepted closes in the window, and compares the rest with the report's `files_changed`, the scope the claim reserved
and the task contract: undeclared or out-of-scope changes are `MUTATION_SCOPE_VIOLATION` unless a CIT **committed after
this task's claim baseline** covers them (the permanent "any committed CIT" exemption is gone); a task whose contract
forbids production merge, and every experiment task, cannot close with production-tree changes
(`PRODUCTION_MERGE_NOT_ALLOWED`). An L3+ `--force` close records every override it used. The report and checkpoint
record `observed_files_changed` and the baseline used.

**Runnable is derived (BC-P2-16/12, WS-5).** One DAG evaluation decides every route: `task create --status READY`
stores the status the DAG derives, `task status X READY` is refused `TASK_NOT_READY` unless runnable, `DONE`/`CLAIMED`/
`IN_PROGRESS` are reached only through close/claim (`TASK_STATUS_REQUIRES_OPERATION`), a `BLOCKED`/`WAITING_HUMAN` set
by `task status` is an explicit hold that replan never lifts, and `gov continue` offers only runnable work this session
may take. **The close, in order:** worker-return normalisation → another session's live claim → evidence payload → the
claim (session, worktree) → the sealed claim baseline (`CLAIM_BASELINE_UNBOUND`) → designated role → independence from
recorded authorship (`INDEPENDENCE_VIOLATION`) → every governing gate authorises the work (`GATE_NOT_AUTHORISED`; never
overridden by `--force`) → observed mutations, including OS-written state no OS operation produced
(`MUTATION_SCOPE_VIOLATION`, `details.t2_violations`) → production merge → index pins/freshness → the consumption
receipt (`RECEIPT_INVALID`) → the health close gate (`HEALTH_HARD_BLOCK`, `GOVERNANCE_SUITE_STALE|_MISSING`,
`PRODUCT_TEST_EVIDENCE_REQUIRED|_STALE`, `PRODUCT_TESTS_FAILED`). The report is sealed and the task records
`outputs_produced`. **Recorded authorship:** the author of a path is the latest sealed close report that accepted a
change to it; test and test-data independence is established from it, never from `independent_of_implementer` or
`author_role`. **The producer rule:** a task that produces its feature's specification (a readiness gap task or a
specification-class task) is not blocked by inputs it only inherits from its feature and is itself writing; what it
declares itself still binds.

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
`corroboration_min_sources`, lesson lifecycle, synthetic fixture only) and fails closed, and raises the packet's
export-approval gate (`trigger: upstream_export`, a human-only trigger; its subject binds the packet id, the lesson and
the payload hash); `gov lessons cluster` groups lessons into Framework Change Proposal records (D-0004); `submit`
re-validates, enforces the outbound allowlist (packet + declared synthetic fixture files) and honours only an
owner-signed answer to that gate bound to exactly this packet (`gates::human_approval_for`: `HUMAN_GATE_REQUIRED` while
pending, `GATE_DECLINED`, `APPROVAL_STALE` after the content changed, `HUMAN_APPROVAL_REQUIRED` for an agent
resolution, `T2_UNBOUND` for a hand-edited gate); `--approved-by` is recorded as a claim and ignored; the ledger records
the payload hash and the signed answer's `answered_by`.

## 8. Capability plugin host
`capabilities/host.rs` runs a plugin with a stdin writer thread, concurrent stdout/stderr drain threads (stderr tail
retained) and a watchdog that polls the child and kills its whole process group at the timeout (`PLUGIN_TIMEOUT`).
Responses far larger than the OS pipe buffer never deadlock; malformed output is `PLUGIN_BAD_RESPONSE`, a wrong
protocol id `PLUGIN_PROTOCOL_MISMATCH`. The kernel payload is embedded in the binary (`runtime/build.rs`), so
`gov init` needs no build-machine paths; the lock records a logical source id.
