# Governance OS Adoption, Migration & Independent Audit Protocol

**Version:** 3.0  
**Governing documents:**
1. [Dynamic Agentic Software Engineering Operating Framework v4.1](./DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md)
2. [Governance OS Release, Distribution, Adoption & Upstream Learning Protocol](./GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md)

**Purpose:** Independent-agent runbook for recovering an interrupted live repository, adopting a certified Governance OS release, migrating repository structure safely, rebuilding memory, independently verifying adoption, and performing iterative v4 audit/remediation.

**Model-agnostic execution rule:** No role in this protocol is bound to a named model, provider, IDE or harness. Each role must be assigned through the Governance OS model-routing policy to a model tier/reasoning level appropriate for the task. Independence is created by fresh context, role separation, immutable evidence and held-out tests — not by brand/model identity.

---

# 1. Governing precedence

The operating framework defines constitutional architecture.

The distribution/adoption protocol defines release/install/update/upstream mechanics.

This independent adoption/audit protocol defines independent roles and the audit/migration sequence.

If they appear to conflict, apply that precedence order unless a newer approved document explicitly supersedes it.

---

# 2. Fundamental sequence

For a brownfield project:

```text
conditional recover/freeze when needed
 ↓
cold inventory
 ↓
classification
 ↓
target path map
 ↓
migration/adoption plan
 ↓
fresh independent migration reviewer/test author
 ↓
controlled migration
 ↓
fresh independent migration verification
 ↓
legacy-memory extraction/retirement
 ↓
new memory build/rebuild on stable paths
 ↓
fresh independent memory verification
 ↓
fresh comprehensive v4 audit
 ↓
operator remediation plan
 ↓
independent plan review
 ↓
execution
 ↓
independent re-audit
```

Do not reverse the path/memory order merely because vector indexing is convenient.

---

# 3. Role separation

## Conditional Recovery Role — Interrupted Repository Recovery Agent

Same session that was interrupted may perform this role.

It reconstructs state, restores a safe checkpoint and freezes broad governance/memory mutation.

It does not continue inventing v4 inside the live repository.

## Role A — Adoption Auditor/Planner

Fresh or cleanly resumed high-capability session.

Read-only except adoption/audit evidence.

Performs cold inventory, classification and target path/migration planning.

## Role B — Independent Migration Reviewer & Test Author

Fresh session.

Reviews the plan and creates independent acceptance tests before migration execution.

Does not execute migration.

## Role C — Migration/Adoption Executor

Normal CTO/orchestrator role.

Executes only the approved migration/adoption plan in controlled batches.

## Role D — Independent Migration Verifier

Fresh session.

Verifies the actual migrated repo and independently runs/extends tests.

## Role E — Memory Foundation Engineer

Builds/rebuilds the Development Knowledge Fabric after migration acceptance.

## Role F — Independent Memory Verifier/Test Author

Fresh session.

Independently challenges retrieval, graph, code intelligence, freshness, supersession, security and rebuildability.

## Role G — Independent Full v4 Auditor

Fresh session after memory acceptance.

Audits governance/spec/product/tooling/traceability and produces findings/operator prompt.

## Role H — Operator/CTO

Plans and executes remediation after independent review.

---

# 4. Conditional interrupted-session recovery and freeze

If an existing session stopped mid-edit because of quota, crash or context loss, invoke this conditional pre-adoption procedure. It is not a numbered canonical stage prompt:

1. do not continue broad edits;
2. inspect branch/worktree;
3. inspect `git status`;
4. inspect staged/unstaged diffs;
5. inspect latest commits/checkpoint;
6. identify partial edits/migrations/index builds;
7. identify tests already run;
8. classify each mutation:

```text
COMPLETE_AND_VERIFIED
COMPLETE_UNVERIFIED
PARTIAL_SAFE_TO_FINISH
PARTIAL_SHOULD_ROLL_BACK
UNKNOWN
```

Finish only the current atomic mutation when safest, or roll it back.

Run minimum integrity tests.

Write a recovery checkpoint/report.

Then **freeze broad governance/memory work until the canonical Governance OS release is available for adoption.**

---

# 5. Adoption evidence tree

Recommended:

```text
spec/audits/GOVERNANCE-ADOPTION/
├── 00-BASELINE.yaml
├── 01-COLD-INVENTORY.md
├── 02-CLASSIFICATION.jsonl
├── 03-LEGACY-GOVERNANCE-MAP.md
├── 04-TARGET-PATH-MAP.jsonl
├── 05-ADOPTION-MIGRATION-PLAN.md
├── 06-INDEPENDENT-MIGRATION-TEST-DESIGN.md
├── 07-MIGRATION-EXECUTION-REPORT.md
├── 08-INDEPENDENT-MIGRATION-VERIFICATION.md
├── 09-LEGACY-MEMORY-EXTRACTION.md
├── 10-MEMORY-IMPLEMENTATION-REPORT.md
├── 11-INDEPENDENT-MEMORY-VERIFICATION.md
└── 12-ADOPTION-FINAL-REPORT.md
```

The later comprehensive project audit gets its own audit ID/folder.

---

# 6. A1 — Cold deterministic repository inventory

Do not trust old semantic retrieval.

Inspect:

- Git history/tree/status;
- all top-level and material nested paths;
- package/manifests;
- imports/module roots;
- application entry points;
- tests;
- DB schemas/migrations;
- configuration;
- generated files;
- governance/spec/research/reports;
- provider instruction files;
- tasks/decisions/lessons;
- chat/session stores;
- indexes/vector/graph stores;
- CI/CD/devops;
- secrets/sensitive locations.

Inventory must establish existence before interpretation.

---

# 7. A2 — Classification

Every material artefact receives an artefact ID and classification.

Suggested classes:

```text
GOVERNANCE_CURRENT
GOVERNANCE_LEGACY
SPEC_AUTHORITATIVE
SPEC_DERIVED
DECISION
LESSON
RESEARCH_EVIDENCE
REPORT_EVIDENCE
TASK
PRODUCT_SOURCE
PRODUCT_TEST
DEVOPS
DATA_RUNTIME
DATA_TEST
TOOLING
GENERATED
SECRET
HISTORICAL
DEAD_OR_UNUSED
UNKNOWN
```

Authority:

```text
ACTIVE
PROVISIONAL
SUPERSEDED
LEGACY
HISTORICAL
REJECTED
UNKNOWN_OR_CONFLICTING
```

Do not move files during classification.

---

# 8. A3 — Target path map

The target path map is a transformation specification, not merely a directory tree.

For each item:

```yaml
artifact_id:
current_path:
current_class:
authority:
target_path:
target_class:
action:
reason:
references:
imports:
consumers:
generated_from:
index_policy:
sensitivity:
rollback:
verification:
```

Actions:

```text
KEEP_IN_PLACE
MOVE
RENAME
SPLIT
MERGE
EXTRACT
RETIRE
DELETE_FROM_ACTIVE_TREE
```

Unknown items block destructive migration until resolved.

---

# 9. A4 — Adoption/migration plan

The plan must define batches based on dependency/order.

A good order is usually:

1. install/pin Governance OS kernel without activating destructive migration;
2. establish project overlay;
3. migrate governance authority and provider adapters;
4. migrate/spec-normalise non-code records;
5. update citations/links;
6. move product source only where justified;
7. update imports/package references;
8. migrate tests/devops as needed;
9. retire legacy governance mechanisms;
10. only after path stability, rebuild memory.

Each batch defines:

- files/actions;
- dependencies;
- expected behaviour;
- pre/post tests;
- rollback;
- checkpoint.

---

# 10. B — Independent migration review and test authoring

Fresh verifier reviews:

- every destructive move;
- target path completeness;
- unknown/unclassified items;
- good product layouts that should remain;
- references/imports;
- authority changes;
- archive/delete decisions;
- old memory stores needing extraction.

It authors tests *before* execution, including:

### Path integrity
- expected files at target;
- prohibited legacy active paths absent;
- no unexpected duplicates;
- links/citations resolve.

### Code integrity
- imports/module discovery;
- entry points;
- build;
- unit/contract/integration tests.

### Governance integrity
- only v4 kernel active;
- old rules marked legacy;
- generated adapters match canonical policy.

### Behaviour preservation
- baseline user-visible/service scenarios still pass unless an approved decision changes them.

### Rollback/recovery
- migration batch can be reverted;
- project returns to pinned baseline.

Verdict:

```text
MIGRATION_PLAN_APPROVED
MIGRATION_PLAN_APPROVED_WITH_AMENDMENTS
MIGRATION_PLAN_REJECTED
```

---

# 11. C — Controlled migration execution

Use an adoption branch/worktree.

For every batch:

```text
checkpoint
 ↓
execute batch
 ↓
update references/imports
 ↓
run independent-authored tests + affected project tests
 ↓
record evidence
 ↓
commit/checkpoint
```

If a batch fails:

- stop that dependency chain;
- roll back or repair within plan authority;
- do not continue downstream batches that depend on the failed state.

Do not weaken tests to complete migration.

---

# 12. D — Independent migration verification

Fresh verifier:

- ignores executor confidence statements;
- inspects actual paths;
- compares migration map against reality;
- runs independent tests;
- spot-checks unmodified/unknown areas;
- checks no accidental authority remains;
- checks no secrets were moved/index-exposed;
- verifies product behaviour baseline.

Verdict:

```text
MIGRATION_ACCEPTED_FOR_MEMORY_REBUILD
or
MIGRATION_REJECTED_NEEDS_REPAIR
```

Memory rebuild cannot receive an acceptance verdict first.

---

# 13. Legacy memory extraction after migration

Once canonical paths are accepted, inspect old memory mechanisms.

For each:

```text
KEEP_AS_TEMPORARY_EVIDENCE
EXTRACT_UNIQUE_KNOWLEDGE
MIGRATE_STRUCTURED_RECORDS
REBUILD_IN_NEW_SYSTEM
RETIRE
UNKNOWN
```

Raw chat/session DBs are not automatically imported into active semantic memory.

Extract durable decisions/lessons/research/evidence only where useful.

Record provenance.

---

# 14. E — New Development Knowledge Fabric

Build/rebuild against stable canonical paths:

- SQLite/structured deterministic state;
- lexical/FTS;
- semantic/vector;
- graph;
- code intelligence;
- hierarchical parent-child retrieval;
- fusion/reranking;
- temporal/provenance;
- context compiler;
- tool capability memory.

Derived runtime remains rebuildable.

---

# 15. F — Independent memory verifier

Fresh test author creates held-out tests independently.

Must include where applicable:

- exact ID/path retrieval;
- lexical phrases/errors;
- semantic paraphrases;
- graph dependency/impact;
- superseded-vs-active conflicts;
- stale index tests;
- child→parent expansion;
- symbol definition/reference/call/import retrieval;
- secret/sensitive exclusions;
- delete/rebuild derived runtime;
- fresh-agent reconstruction.

Verdict:

```text
MEMORY_ACCEPTED_FOR_V4_AUDIT
or
MEMORY_REJECTED_NEEDS_REPAIR
```

---

# 16. G — Comprehensive v4 project audit

Fresh full auditor now assesses:

- installed framework conformance/version/hash;
- project overlay;
- repository contract;
- governance authority;
- legacy retirement;
- memory;
- commands/natural-language routing;
- models/tools/MCP;
- checkpoints;
- feature/capability readiness;
- spec;
- task DAG;
- architecture;
- product;
- data;
- security;
- devops;
- observability;
- tests;
- traceability;
- CIT;
- learning;
- human gates.

The kernel itself is compared against the certified release; the auditor focuses reasoning on project adoption/configuration and project correctness.

---

# 17. Iterative remediation

```text
independent audit
 ↓
operator remediation plan
 ↓
independent plan review
 ↓
operator execution
 ↓
independent re-audit
```

Maximum ordinary remediation iterations: three.

Then root-cause escalation.

---

# 18. Migration finding states

Use:

```text
PRESENT
ABSENT_CONFIRMED
NOT_FOUND
UNKNOWN
INACCESSIBLE
CONFLICTING
MIGRATED
RETIRED
```

Never treat `NOT_FOUND` as proof of absence.

---

# 19. Human gates during adoption

Raise consequential decisions such as:

- delete vs preserve unique data;
- breaking package restructure;
- destructive DB migration;
- ambiguity over intended product behaviour;
- material security/privacy change;
- expensive infrastructure/tool;
- unresolved authoritative spec conflict.

Low-impact reversible classification/path cleanup can be decided autonomously and recorded.

Questions must appear in chat.

Independent work continues where possible.

---

# 20. Final adoption verdict

Write:

```text
ADOPTED_HEALTHY
ADOPTED_WITH_ACCEPTED_EXCEPTIONS
NOT_ADOPTED_HEALTHY
```

`ADOPTED_HEALTHY` requires at minimum:

- certified kernel pinned;
- project overlay separate;
- path mapping accepted;
- migration independently verified;
- legacy authority retired;
- memory independently verified;
- comprehensive v4 audit completed;
- critical/high unaccepted findings resolved;
- runtime rebuildable;
- clean-machine reconstruction demonstrated.

