# Governance OS Release, Distribution, Adoption & Upstream Learning Protocol

**Version:** 1.2  
**Governing framework:** [Dynamic Agentic Software Engineering Operating Framework v4.1](./DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md)  
**Purpose:** Define how the canonical Governance OS is developed once, certified, distributed to many repositories, upgraded safely, and improved from sanitised project lessons.

---

# 1. Architecture

```text
                 PRIVATE CANONICAL REMOTE
             agentic-engineering-os repository
                          │
                 build/test/certify
                          │
                     release vX.Y.Z
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
      Product A        Product B        Product C
      gov adopt        gov adopt         gov init
         │                │                │
         └──── framework lessons ──────────┘
                          │
                  sanitised export gate
                          │
                          ▼
                Governance OS lesson inbox
                          │
                   framework change
                          │
                  test + new release
```

The canonical Governance OS repository and every project repository remain separate Git repositories.

Do not make the whole project repository a subdirectory or branch of the Governance OS repository.

---

# 2. Recommended canonical remote

Use one private remote repository for the Governance OS.

Illustrative local machine:

```text
~/projects/
├── agentic-engineering-os/
├── product-a/
└── product-b/
```

Each may have its own private GitHub remote.

The Governance OS remote should hold only framework/runtime/tooling/tests/synthetic fixtures and sanitised upstream framework lessons.

It must not become a dump for product repositories.

---

# 3. Canonical Governance OS repository contract

Recommended:

```text
agentic-engineering-os/
├── framework/
├── runtime/
├── cli/
├── tools/
├── migrations/
├── tests/
├── fixtures/
├── lessons/inbox/
├── change-proposals/
├── release/
└── docs/
```

`fixtures/` contains synthetic or intentionally public/non-sensitive material only.

---

# 4. Consumer repository contract

After installation/adoption:

```text
<product-repo>/
├── governance/
│   ├── kernel/              # exact installed release
│   ├── project/             # project-specific overlay
│   ├── generated/           # generated adapters/manifests
│   └── framework.lock
├── spec/
├── product/
├── archive/
└── .governance-runtime/     # derived/local, normally gitignored
```

The kernel is framework-owned.

The overlay is project-owned.

---

# 5. Why not a Git submodule by default

A submodule can technically pin the Governance OS source, but it creates unnecessary operational complexity for ordinary agents, worktrees, CI and upgrades.

The default should therefore be a **released, installed kernel payload** tracked as normal files in the consumer repository and pinned by `framework.lock`.

Future packaging may use a package registry, executable release bundle or another distribution mechanism, but the logical separation must remain.

---

# 6. Governance OS development lifecycle

```text
framework requirement
 ↓
branch/change proposal
 ↓
implementation
 ↓
unit/schema/policy tests
 ↓
greenfield fixture
 ↓
brownfield fixture
 ↓
migration fixture
 ↓
update fixture
 ↓
upstream-export fixture
 ↓
independent framework verifier
 ↓
release candidate
 ↓
release manifest + hashes
 ↓
tag/release
```

A framework developer must not be the only final verifier of a release candidate.

---

# 7. Synthetic certification projects

## 7.1 Greenfield fixture

Must exercise:

- product ideation;
- scenarios;
- feature-readiness gaps;
- research tasks;
- data/test-data creation;
- independent test author;
- implementation;
- CIT-P/CIT-E;
- checkpoints;
- model/tool routing;
- fresh-agent continuation.

## 7.2 Brownfield fixture

Intentionally include:

- old provider-specific rules;
- contradictory governance;
- old chat/session database;
- stale vector index;
- duplicated decisions;
- superseded specs;
- broken/missing graph edges;
- misplaced files;
- code/spec disagreement;
- missing requirements;
- dead code;
- stale tests;
- secrets that must not be indexed/exported.

The release must successfully adopt and repair this project without allowing legacy authority to survive accidentally.

## 7.3 Migration fixture

Must prove path-mapping and migration logic:

- inventory;
- classification;
- target path mapping;
- moved/renamed files;
- import/reference updates;
- links/citations;
- generated indexes;
- rollback;
- memory rebuild after path stabilisation.

## 7.4 Update fixture

Install previous release, create project overlay/state, then upgrade to the release candidate. Prove project overlay remains intact.

## 7.5 Multi-machine/rebuild fixture

Clone the same project into a clean environment with no runtime DB/index. Prove `gov doctor` and `gov rebuild-memory` reconstruct usable state.

---

# 8. Release manifest

Each release should publish a machine-readable manifest:

```yaml
framework: agentic-engineering-os
version:
release_commit:
release_hash:
schema_versions:
cli_version:
runtime_version:
supported_from_versions:
migration_ids:
adapter_versions:
required_index_rebuilds:
breaking_changes:
human_gates:
```

Release payloads are immutable.

---

# 9. `gov init`

For greenfield projects:

```text
gov init <version>
 ↓
install kernel
 ↓
write framework.lock
 ↓
create project overlay
 ↓
create standard governance/spec roots
 ↓
compile adapters
 ↓
initialise runtime
 ↓
run conformance suite
```

---

# 10. `gov adopt`

`gov adopt` is intentionally more conservative.

It is not "copy framework files and reorganise everything."

It is a staged migration transaction.

## Stage A0 — Safety baseline

This is a permanent conditional adoption/recovery capability, not a dedicated numbered prompt in the canonical prompt pack. If no interrupted prior work exists, it reduces to the normal safety baseline.

- clean/snapshot working tree;
- create adoption branch/worktree;
- pin current commit;
- record baseline tests;
- detect interrupted prior governance work.

## Stage A1 — Cold inventory

Build a deterministic catalogue of:

- directories/files;
- Git-tracked/untracked material;
- product entry points;
- package/module structure;
- tests;
- data/configuration;
- governance/spec/research/report material;
- databases;
- generated files;
- indexes;
- provider rules;
- secrets/sensitive paths.

Do not rely on current semantic memory.

## Stage A2 — Classification

Every material item receives:

```text
GOVERNANCE_CURRENT
GOVERNANCE_LEGACY
SPEC_AUTHORITATIVE
SPEC_DERIVED
RESEARCH_EVIDENCE
REPORT_EVIDENCE
PRODUCT_SOURCE
PRODUCT_TEST
DEVOPS
DATA_RUNTIME
DATA_TEST
GENERATED
SECRET
HISTORICAL
DEAD/UNUSED
UNKNOWN
```

Also classify authority:

```text
ACTIVE
PROVISIONAL
SUPERSEDED
LEGACY
HISTORICAL
REJECTED
UNKNOWN_OR_CONFLICTING
```

## Stage A3 — Target path map

Create a proposed mapping from current to target paths.

Do not move files yet.

For each artefact record:

```yaml
current_path:
target_path:
action:
reason:
authority:
references:
imports:
consumers:
index_policy:
rollback:
verification:
```

A good native product layout can remain in place if the Repository Contract can describe it cleanly. Standardise governance/spec strongly; do not damage a mature package structure for aesthetics.

## Stage A4 — Migration plan

The migration plan includes:

- path moves/renames;
- file splits/merges;
- legacy retirement;
- link/citation updates;
- import/package changes;
- generated-view changes;
- migration batches;
- rollback points;
- memory stores to inspect/extract before retirement;
- post-migration indexing plan.

## Stage A5 — Independent migration review and test authoring

Fresh independent agent/session:

- reviews classification;
- reviews target path map;
- challenges destructive moves;
- identifies missing dependencies;
- authors migration acceptance tests;
- authors behaviour-preservation tests;
- authors legacy-authority negative tests;
- authors path/link/import tests;
- authors rollback/rebuild tests.

It does not execute the migration.

## Stage A6 — Controlled migration

Execute in dependency-aware batches.

After each batch:

- run path/import/link tests;
- run affected product tests;
- checkpoint;
- update migration ledger.

Never perform an unbounded bulk move without evidence.

## Stage A7 — Independent migration verification

The independent verifier checks actual state, not the executor's report.

Verdict:

```text
MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD
or
MIGRATION_REJECTED_NEEDS_REPAIR
```

## Stage A8 — Legacy memory audit/extraction/retirement

Now inspect old DB/chat/vector/graph stores in the context of the stable canonical layout.

Extract any unique durable knowledge.

Retire mechanisms whose useful content has been migrated.

## Stage A9 — Development Knowledge Fabric build/rebuild

Build v4:

- deterministic state;
- lexical retrieval;
- semantic/vector retrieval;
- graph;
- code-symbol index;
- hierarchical parent expansion;
- reranking/fusion;
- context compiler.

Index the stable canonical paths.

## Stage A10 — Independent memory verification

Fresh verifier authors/executes held-out tests.

Verdict:

```text
MEMORY_ACCEPTED_FOR_V4_AUDIT
or
MEMORY_REJECTED_NEEDS_REPAIR
```

## Stage A11 — Full v4 project audit

Only now perform the comprehensive governance/spec/product audit and iterative remediation.

---

# 11. Why path migration precedes new indexing

Indexes bind to locations, content hashes, symbols and relationships.

Building them before the target repository layout is agreed causes:

- unnecessary invalidation/re-indexing;
- stale path metadata;
- duplicate graph nodes;
- misleading retrieval;
- increased migration complexity.

Therefore existing memory is **inventoried before migration**, but the new canonical memory is **built after path stabilisation**.

---

# 12. `gov update`

```text
gov update --check
 ↓
available release manifest
 ↓
compatibility check
 ↓
CIT-P
 ↓
human gate if material
 ↓
adoption branch/checkpoint
 ↓
replace kernel only
 ↓
execute version migration scripts
 ↓
preserve project overlay
 ↓
regenerate adapters
 ↓
rebuild affected derived runtime
 ↓
independent/update tests
 ↓
CIT-E
```

A project may remain on an older certified release when migration is not yet approved.

---

# 13. Upstream framework-learning pipeline

Project lessons remain local unless deliberately promoted.

```text
lesson
 ↓
scope classifier
 ├─ PROJECT → local
 ├─ PRODUCT → local
 └─ FRAMEWORK → upstream candidate
```

A framework candidate is not directly pushed.

Run:

```text
gov upstream prepare <lesson-id>
```

to generate a sanitised packet.

Conceptual packet:

```yaml
scope: FRAMEWORK
failure_pattern:
generic_impact:
suggested_framework_change:
source_project_alias:
local_reference:
sensitive_content_removed: true
raw_product_code: false
raw_spec: false
customer_data: false
```

---

# 14. Upstream Export Gate

Before submission:

- outbound allowlist;
- secret scan;
- data/sensitivity scan;
- path/content scan;
- remove customer/project identifiers where unnecessary;
- prefer synthetic reproducer;
- require configured approval;
- log payload hash.

Only the approved packet and synthetic fixture may be sent to the canonical remote.

The central repository never receives the project DB, vector index, product tree or arbitrary spec folders through this mechanism.

---

# 15. Framework lesson intake

In the central Governance OS repo:

```text
lessons/inbox/
 ↓
deduplicate/cluster
 ↓
severity/frequency/confidence
 ↓
Framework Change Proposal
 ↓
implementation
 ↓
synthetic/regression tests
 ↓
independent verification
 ↓
release
```

The source project learns about the fix later through `gov update`.

---

# 16. Cross-machine mechanics

Authoritative state is Git-tracked.

Derived runtime is rebuilt locally.

On a second machine:

```text
clone/pull project
 ↓
read framework.lock
 ↓
ensure matching gov CLI/kernel
 ↓
gov doctor
 ↓
gov rebuild-memory when needed
```

For the central framework repo, clone/pull it normally from the same private remote.

No manual copying of runtime DBs is required.

---

# 17. Security invariant

> Projects teach the Governance OS through explicit sanitised framework lessons, never through accidental repository replication.

Any upstream operation that attempts to include a forbidden path/content class must fail closed.

---

# 18. Adoption acceptance

A brownfield adoption is complete only when all are true:

1. migration baseline is pinned;
2. every material artefact is classified;
3. target path map is explicit;
4. migration plan was independently reviewed;
5. independent migration tests exist;
6. migrated paths/imports/links pass;
7. behaviour baseline is preserved or deliberately changed by decision;
8. legacy governance no longer has accidental authority;
9. unique knowledge from retired stores was extracted;
10. new memory is built on stable canonical paths;
11. independent memory verifier passes;
12. fresh full v4 auditor passes or accepted exceptions are recorded;
13. installed release is pinned in `framework.lock`;
14. project overlay is separate from the kernel;
15. a clean machine can reconstruct the derived runtime.

