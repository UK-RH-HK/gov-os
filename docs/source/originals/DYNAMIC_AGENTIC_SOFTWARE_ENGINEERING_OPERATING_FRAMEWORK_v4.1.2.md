# Dynamic Agentic Software Engineering Operating Framework v4.1

**Status:** Proposed constitutional architecture  
**Revision:** 4.1.2 — fully model-agnostic canonical package; no provider/model-specific audit roles  
**Purpose:** Model-agnostic operating framework for a virtual AI software-development and computer-science R&D organisation  
**Lineage:** Evolves the Dynamic Agentic Project Governance Framework v3.5 into a complete software-engineering operating system  
**Core principle:** **The agent session is not the source of truth. The governed project system is the source of truth.**

---

## 0. Executive Definition

This framework defines how a human product owner can operate a persistent, multi-agent software-development and computer-science R&D organisation in which AI models are replaceable workers rather than holders of project memory.

The framework is not merely a set of instructions for a coding agent. It is an **Agentic Software Engineering Operating System** containing:

1. a constitutional governance and policy plane;
2. a persistent Development Knowledge Fabric;
3. a standard, navigable repository contract;
4. role-based agent organisation and authority;
5. reusable skills and methods;
6. governed tools, MCP servers, APIs and executable capabilities;
7. a stable command/control surface with natural-language intent routing;
8. specification, research and planning machinery;
9. a dynamic task/WBS dependency graph;
10. product and R&D delivery systems;
11. independent testing and verification;
12. Change-Impact Transactions for safe state mutation;
13. observability, model routing, budgets and checkpoints;
14. institutional learning and framework evolution;
15. independent audit and recovery mechanisms.

The objective is **not to remove the human from the loop**. The objective is to reserve human attention for decisions where human judgement has the highest value while making routine discovery, planning, engineering, integration, testing, documentation and controlled change increasingly autonomous.

---

# PART I — CONSTITUTIONAL PRINCIPLES

## 1. The organisation, not the conversation, owns continuity

Agent conversations are disposable.

Long-term continuity must survive:

- model changes;
- context compaction;
- session termination;
- IDE changes;
- provider changes;
- agent crashes;
- parallel work;
- repository refactors;
- months or years of development.

Therefore:

> **No essential project knowledge may exist only inside a conversation.**

Material project knowledge must be committed into structured project state as an appropriate artefact such as a decision, requirement, research finding, experiment, task, report, lesson, skill, test, scenario, interface contract or change transaction.

Raw conversation history is not normal project memory.

---

## 2. Authority precedence

When project information conflicts, use the following precedence unless an explicit project policy overrides it:

1. explicit current human-approved decision;
2. current constitutional hard invariant;
3. active structured project state;
4. active specification and interface contract;
5. active architecture/workflow decision;
6. approved task contract and mutation manifest;
7. active scenario and acceptance criteria;
8. current verified implementation behaviour;
9. current research evidence and execution reports;
10. historical/superseded project records;
11. semantic memory retrieval;
12. agent inference.

Semantic retrieval can identify evidence or a possible relationship. It **cannot silently make something authoritative**.

Existing code is evidence of present behaviour; it is not automatically proof of intended behaviour.

---

## 3. State classes

Every material governance/specification artefact must be classifiable as one of:

- `AUTHORITATIVE`
- `DERIVED`
- `NARRATIVE`
- `EVIDENCE`
- `HISTORICAL`
- `UNKNOWN_OR_CONFLICTING`

Every stateful item must also support an authority/lifecycle status as applicable:

- `ACTIVE`
- `PROVISIONAL`
- `SUPERSEDED`
- `LEGACY`
- `HISTORICAL`
- `REJECTED`
- `DEPRECATED`
- `RETIRED`

`LEGACY` is especially important during migration from earlier governance systems. Legacy material may contain useful evidence but has **no default authority** over the new framework.

---

## 4. The framework is model-agnostic

No canonical project policy, skill, task or decision may depend permanently on a current model/vendor name.

The framework owns a canonical representation and exposes adapters for execution environments.

Examples:

- A provider adapter may generate the instruction/configuration file required by its target harness.
- Another provider adapter may generate a different harness-specific instruction/configuration file.
- another IDE may consume a settings/rules file;
- a CLI agent may consume a bootstrap packet;
- an API-hosted model may consume a compiled system instruction.

These are **adapters**, not the constitution.

The constitution lives under `governance/`.

---

## 5. The framework is self-observing and self-improving, not uncontrolled self-modifying

Ordinary execution may produce:

- execution evidence;
- lesson candidates;
- failure records;
- skill proposals;
- policy proposals;
- retrieval-improvement proposals;
- tooling proposals.

But an executing agent must not rewrite the rules governing its own execution.

Framework, policy and skill changes must pass:

1. evidence;
2. corroboration where required;
3. proposal;
4. independent review/test;
5. human approval where material;
6. versioned promotion.

This is closed-loop institutional learning, not uncontrolled recursive self-modification.

---

# PART II — THE OPERATING SYSTEM

## 6. High-level architecture

```text
                         HUMAN / PRODUCT OWNER
                                  │
                                  ▼
                     GOVERNANCE / CONTROL PLANE
                                  │
          ┌───────────────────────┼────────────────────────┐
          │                       │                        │
          ▼                       ▼                        ▼
 DEVELOPMENT KNOWLEDGE      AGENT ORGANISATION       TOOL / CAPABILITY
       FABRIC               & ORCHESTRATION              PLANE
          │                       │                        │
          └───────────────────────┼────────────────────────┘
                                  ▼
                      SPEC / R&D / PLANNING
                                  │
                                  ▼
                         DYNAMIC TASK DAG
                                  │
                                  ▼
                     PRODUCT / R&D DELIVERY
                                  │
                                  ▼
                      INDEPENDENT VERIFICATION
                                  │
                                  ▼
                         CHANGE CONTROL / CIT
                                  │
                                  ▼
                          OBSERVABILITY
                                  │
                                  ▼
                          LEARNING LOOP
                                  │
                 lessons → skills/policies → release
```

---

## 7. The constitutional systems

Every mature repository should be able to identify the following systems even if a small project implements them minimally:

1. Constitution and policies
2. Development Knowledge Fabric
3. Repository contract and path maps
4. Agent organisation and authority
5. Skill system
6. Tool/capability system
7. Command/control surface
8. Model/provider adapters
9. Orchestration and A2A handoffs
10. Specification and planning
11. Research/experiment system
12. Dynamic task/WBS system
13. Product delivery system
14. Verification and governance testing
15. Change-impact and mutation control
16. Checkpoint/recovery system
17. Observability and cost telemetry
18. Organisational learning
19. Independent audit
20. Security and permissions
21. Budget/resource governance
22. Emergency stop/rollback

---

# PART III — STANDARD REPOSITORY CONTRACT

## 8. Standard top-level structure

A framework-adopted repository should converge on the following logical layout:

```text
<repo>/
│
├── governance/
│   ├── constitution/
│   ├── policies/
│   ├── memory/
│   ├── skills/
│   ├── tools/
│   ├── commands/
│   ├── orchestration/
│   ├── adapters/
│   ├── tests/
│   ├── framework/
│   └── generated/
│
├── spec/
│   ├── now/
│   ├── product/
│   ├── features/
│   ├── requirements/
│   ├── architecture/
│   ├── workflows/
│   ├── interfaces/
│   ├── scenarios/
│   ├── data/
│   ├── security/
│   ├── performance/
│   ├── research/
│   ├── experiments/
│   ├── decisions/
│   ├── planning/
│   ├── tasks/
│   ├── reports/
│   ├── lessons/
│   └── audits/
│
├── product/
│   ├── <native application/service layout>
│   ├── tests/
│   ├── tools/
│   ├── devops/
│   └── data/        # runtime only where appropriate; sensitive data governed separately
│
├── archive/
│   ├── governance/
│   ├── spec/
│   ├── research/
│   └── code-reference/
│
├── framework.json
├── README.md
└── provider-specific generated adapter files where required
```

### 8.1 Do not break good application architecture to satisfy the framework

The governance/spec layout is standard.

The product source tree is represented through `framework.json` path maps and capability roots. A mature existing application must not be mechanically rearranged into artificial layer folders if doing so would damage package/import/runtime structure.

---

## 9. Repository Contract and Path Map

`framework.json` or equivalent machine-readable configuration defines the repository topology.

Example:

```yaml
roots:
  governance: governance/
  spec: spec/
  product: product/
  archive: archive/

paths:
  product/backend/**:
    class: source
    owner_role: backend-engineer
    semantic_index: true
    code_index: true
    graph_index: true

  spec/decisions/**:
    class: authoritative
    owner_role: change-controller
    semantic_index: true
    graph_index: true

  spec/reports/**:
    class: evidence
    semantic_index: true
    graph_index: true

  archive/**:
    class: historical
    default_retrieval: false
    mutation: restricted

  "**/.env*":
    class: secret
    semantic_index: false
    vector_index: false
    agent_read: restricted
```

The path map determines:

- what belongs where;
- what may be indexed;
- what is authoritative;
- what is generated;
- who may read/write it;
- what must never be indexed;
- what changes require elevated authority;
- what files form a feature/layer;
- what derived views are regenerated.

---

# PART IV — DEVELOPMENT KNOWLEDGE FABRIC

## 10. Memory architecture

The repository is the authoritative physical record.

SQLite, vector indexes, graph projections, lexical indexes and code-intelligence indexes are **derived representations**, not independent copies of truth.

```text
                         GIT REPOSITORY
                    authoritative artefacts
                              │
                   incremental index pipeline
                     hashes + git diff
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
 SQLite / structured     Vector / semantic     Code intelligence
 deterministic state      dense/sparse index     AST/symbol/index
 + graph edge store       contextual memory      imports/calls/refs
 + FTS lexical index
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                       RETRIEVAL ROUTER
                              │
          ┌──────────────┬────┼─────┬───────────────┐
          ▼              ▼          ▼               ▼
       exact/ID        lexical    semantic       graph/code
          │              │          │               │
          └──────────────┴────┬─────┴───────────────┘
                              ▼
                       fusion/reranking
                              │
                              ▼
                       CONTEXT COMPILER
                              │
                              ▼
                            AGENT
```

---

## 11. Required memory classes

The Development Knowledge Fabric should provide at least:

### 11.1 Deterministic memory
Use SQLite/structured files for current truth:

- projects
- features
- requirements
- decisions
- tasks
- scenarios
- tests
- interfaces
- experiments
- releases
- claims
- transactions
- statuses
- skill versions
- tool versions
- model-routing records
- index manifests

### 11.2 Relationship memory
Typed graph relationships:

- `DEPENDS_ON`
- `BLOCKS`
- `IMPLEMENTS`
- `REALISES`
- `GOVERNED_BY`
- `CONSTRAINS`
- `DERIVED_FROM`
- `SUPERSEDES`
- `VALIDATED_BY`
- `TESTS`
- `USES`
- `PRODUCES`
- `CONSUMES`
- `AFFECTS`
- `GENERATED_FROM`
- `CALLS`
- `IMPORTS`
- `OWNS`
- `FAILED_BECAUSE`
- `LEARNED_FROM`

### 11.3 Semantic memory
Embeddings for concept/rationale discovery:

- decisions and rationale;
- lessons;
- failures;
- reports;
- research findings;
- architectural discussions;
- experiments;
- requirements;
- specifications;
- selected source-code units.

### 11.4 Lexical memory
FTS/BM25/sparse retrieval for:

- exact terms;
- identifiers;
- filenames;
- error strings;
- API names;
- configuration keys;
- literal phrases.

### 11.5 Code-structural memory
AST/LSP/SCIP or equivalent:

- symbols;
- definitions;
- references;
- inheritance;
- calls;
- imports;
- interfaces;
- route registrations;
- database models;
- test coverage relationships.

### 11.6 Temporal memory
Git and version lineage:

- what changed;
- when;
- why;
- which decision caused it;
- which version superseded it.

### 11.7 Episodic memory
Execution records:

- agent;
- task;
- context packet;
- tools used;
- files read;
- files changed;
- tests;
- outcomes;
- failures;
- discoveries.

### 11.8 Failure memory
Structured records of:

- bugs;
- failed approaches;
- incorrect assumptions;
- retrieval misses;
- regressions;
- migration failures;
- tool failures.

### 11.9 Working memory
Small reproducible context packet for the current task.

### 11.10 Capability memory
Current organisational capability:

- available tools;
- MCP servers;
- A2A agents;
- packages/dependencies;
- model providers;
- credentials/permissions status;
- environment/tool versions.

---

## 12. The databases do not each own a separate repository copy

SQLite stores structured facts/relationships and possibly FTS text.

The vector store stores embeddings and retrieval metadata and may cache chunk text for performance.

The code index stores structural code facts.

All must carry enough provenance to reconstruct a hit:

```yaml
artifact_id:
path:
repo_commit:
content_hash:
section_or_symbol:
namespace:
authority_class:
status:
index_version:
```

Deleting a derived index must never destroy project truth.

---

## 13. Incremental indexing and freshness

Every indexed artefact is keyed by content hash and repository commit.

On change:

```text
git diff / changed hashes
        ↓
invalidate affected chunks/nodes/symbols
        ↓
re-index only affected material
        ↓
update index manifest
        ↓
run freshness/integrity checks
```

A task close must fail or mark the state degraded when a required index is stale beyond policy.

---

## 14. Retrieval routing

The framework classifies the question before retrieval.

```text
known ID/path?              → structured lookup
exact symbol/code?          → symbol/AST/LSP index
exact text/error?           → lexical/FTS/BM25
dependency/impact?          → graph traversal
concept/rationale/history?  → semantic vector retrieval
complex question?           → several routes + fusion/reranker
```

A default complex retrieval flow:

```text
query
 ↓
authority + namespace filter
 ↓
lexical + vector + graph/code candidates
 ↓
rank fusion
 ↓
cross-encoder/reranker where justified
 ↓
deduplication
 ↓
active-state precedence
 ↓
parent/section + graph-neighbour expansion where useful
 ↓
bounded cited slices
 ↓
context packet
```

### 14.1 Hierarchical / parent-child retrieval

Do not assume that useful context is always a fixed-size chunk.

Index information at several logical levels where appropriate:

```text
document
  ↓
section / record / module
  ↓
child chunk / function / symbol
```

Retrieve precise child units first, then expand only high-value hits to their parent section, governing record, neighbouring graph nodes or related code symbols. This preserves retrieval precision without forcing the agent to reason from tiny fragments.

For code, prefer structural units such as module/class/function/symbol/reference over arbitrary token windows wherever possible.

### 14.2 Embeddings, runtimes and LLMs are different concerns

The framework must distinguish:

- **embedding model** — creates semantic vectors;
- **inference runtime** — e.g. ONNX Runtime, local model server or equivalent;
- **vector/index store** — persists/searches vectors;
- **reranker** — scores query/candidate relevance more precisely;
- **generative LLM** — optional query planning, decomposition or context compression.

A local small LLM may assist retrieval planning, query rewriting, entity extraction or context compression, but must not replace deterministic authority resolution.

### 14.3 Retrieval model selection is evidence-driven

Do not permanently hard-code a particular embedding or reranking model into the constitutional standard.

For each repository/environment, benchmark candidate local or approved remote models against repository-specific held-out retrieval queries. Select based on:

- recall and ranking quality;
- supported context length;
- latency;
- hardware footprint;
- privacy/security;
- reproducibility;
- multilingual needs;
- cost.

The chosen embedding and reranker versions are pinned in the memory/index manifest and may be changed only through a measured migration with re-indexing and regression testing.

---

## 15. Context packet

The context packet contains two classes:

### 15.1 Deterministic authority block
Reproducible and content-hashed:

- task;
- objective;
- current project state;
- governing requirements;
- active decisions;
- architecture;
- interfaces;
- scenarios;
- acceptance criteria;
- allowed/prohibited writes;
- required skills/tools;
- dependency state.

### 15.2 Retrieved intelligence block
Supplementary context:

- query;
- retrieval strategy;
- index snapshot/version;
- ranked evidence references;
- semantic candidates;
- relevant lessons/failures;
- code references.

Semantic retrieval must **augment**, not replace, the deterministic authority block.

---

## 16. Memory security boundaries

Development/governance memory and customer/runtime product data must be physically and logically separated.

Never place live customer invention disclosures, credentials, private production data or other sensitivity-classified material into the generic governance vector index.

Each namespace requires:

- sensitivity class;
- permitted roles;
- retention policy;
- export policy;
- embedding policy;
- provenance;
- deletion/rebuild behaviour.

---

## 17. Memory regression tests

The memory itself must be tested.

Maintain held-out questions such as:

```yaml
query: "Why was the retrieval architecture changed?"
expected_refs:
  - D-...
  - REPORT-...
forbidden:
  - superseded decision as authority
```

Metrics:

- Recall@K
- MRR
- precision
- stale-hit rate
- superseded-hit rate
- graph edge coverage
- symbol recall
- retrieval latency
- tokens retrieved
- tokens used
- retrieval-to-answer evidence coverage

A governance suite that is green while memory recall silently collapses is not healthy.

---

## 18. Retrieval learning loop

A retrieval failure creates an explicit memory-quality event.

```text
agent misses existing knowledge
        ↓
retrieval miss recorded
        ↓
root cause:
chunking / metadata / routing / graph / lexical / stale index
        ↓
repair
        ↓
held-out retrieval test added
        ↓
future regression prevented
```

---

## 19. Rebuild guarantee

A disaster-recovery test must periodically prove:

```text
delete vector index
delete derived SQLite/index database
delete graph projection
delete generated views
        ↓
rebuild from Git + authoritative records
        ↓
same authoritative project state
```

Indexes are useful only if they remain replaceable.

---

# PART V — CONSTITUTION, POLICIES AND MODEL ADAPTERS

## 20. Canonical policy layer

Recommended files:

```text
governance/constitution/
    CONSTITUTION.md

governance/policies/
    AUTHORITY_POLICY.yaml
    MEMORY_POLICY.yaml
    CHANGE_POLICY.yaml
    SECURITY_POLICY.yaml
    TOOL_POLICY.yaml
    MODEL_ROUTING_POLICY.yaml
    CONTEXT_POLICY.yaml
    HUMAN_GATE_POLICY.yaml
    BUDGET_POLICY.yaml
    CHECKPOINT_POLICY.yaml
    TEST_POLICY.yaml
    LEARNING_POLICY.yaml
    ARCHIVE_POLICY.yaml
```

These are canonical.

Provider-specific files are generated projections.

---

## 21. Policy hierarchy

```text
CONSTITUTION / HARD INVARIANTS
             ↓
SECURITY + AUTHORITY
             ↓
PROJECT POLICY
             ↓
ACTIVE DECISIONS / SPEC
             ↓
TASK CONTRACT + MUTATION MANIFEST
             ↓
ROLE + SKILL
             ↓
RETRIEVED CONTEXT
             ↓
MODEL INFERENCE
```

A lower layer may never silently override a higher one.

---

## 22. Model/provider adapters

Recommended:

```text
governance/adapters/
    provider-a/
    provider-b/
    generic/
    ide/
    cli/
```

Adapters can generate:

- harness-specific instruction files
- IDE rule files
- tool configuration
- MCP connection manifests
- bootstrap/system prompts

Adapter conformance tests verify that core policies remain semantically equivalent.

---

# PART VI — AGENT ORGANISATION

## 23. Authority levels

```text
L0  Read-only analyst/auditor
L1  Worker — scoped source/document mutation
L2  Domain maintainer — scoped domain-state mutation
L3  Change Controller — cross-artifact state transaction
L4  Orchestrator/CTO — planning, routing, dispatch and coordination
L5  Human/Product Owner — final authority at defined gates
```

No spawned worker behaves as an orchestrator unless explicitly assigned that role.

---

## 24. Representative roles

Roles are capability contracts, not personalities.

- CTO / Senior Full-Stack Orchestrator
- Product/Specification Agent
- Research Agent
- Architecture Agent
- UX Agent
- Frontend Engineer
- Backend Engineer
- Database/Data Engineer
- Integration/API Engineer
- AI/ML Engineer
- DevOps/SRE Engineer
- Security Engineer
- Performance Engineer
- Data Author
- Independent Test Designer
- Test Execution Agent
- Integration Agent
- Change Controller
- Memory/Knowledge Engineer
- Tooling/MCP Engineer
- Independent Auditor
- Release Agent

---

## 25. Typed A2A handoffs

Agent-to-agent communication is a delegation layer, not memory.

A material handoff must be typed.

```yaml
handoff_id: HND-0128
from_role: orchestrator
to_role: backend-engineer
task: TASK-0208
inputs:
  spec: SPEC-...
  interface: API-...
  scenarios: [SCN-...]
expected_outputs:
  - implementation
  - evidence
authority:
  allowed:
    - product/backend/**
  prohibited:
    - governance/**
    - spec/decisions/**
required_return:
  - changed_files
  - tests
  - discoveries
  - unresolved
```

All material outputs return to project state rather than remaining only in inter-agent chat.

Use A2A-compatible interoperability when crossing independently hosted/vendor agent systems where practical.

---

# PART VII — SKILLS

## 26. Skills are methods

A skill defines **how** an authorised role performs a repeatable class of work.

Examples:

- backend implementation;
- database migration;
- API contract review;
- architecture impact analysis;
- security threat modelling;
- live migration;
- repository adoption;
- task close;
- research benchmark;
- test design;
- tool installation;
- memory reconstruction.

A skill is not a tool and not a policy.

---

## 27. Skill lifecycle

```text
missing/repeated method
      ↓
lesson cluster / capability gap
      ↓
skill proposal
      ↓
draft skill
      ↓
held-out validation scenarios
      ↓
independent review
      ↓
human approval where material
      ↓
ACTIVE version
```

Execution records must capture the exact skill version used.

---

# PART VIII — TOOL, MCP AND CAPABILITY PLANE

## 28. Tools are first-class governed capabilities

A tool provides an executable capability.

Examples:

- filesystem/shell;
- Git;
- GitHub/GitLab APIs;
- web search/fetch/browser;
- package managers;
- AST parsers;
- language servers;
- symbol/reference indexes;
- dependency scanners;
- database clients;
- test runners;
- container engines;
- cloud CLIs/APIs;
- CI/CD;
- security scanners;
- observability clients;
- vector databases;
- graph stores;
- MCP servers;
- A2A endpoints.

Every task may declare:

```text
required skills
required tools
required permissions
minimum model tier
```

---

## 29. Tool Capability Registry

Maintain:

```yaml
tool_id: TOOL-WEB-001
name: governed-web-fetch
type: MCP | CLI | API | library
capabilities:
  - web_search
  - fetch_page
permissions:
  network: true
  repo_write: false
credential_scope: none
status: active
version: ...
health_check: ...
approved_roles:
  - research-agent
  - orchestrator
```

For dependency/library tools:

```yaml
tool_id: TOOL-AST-001
package: tree-sitter
source: package-manager
version_pin: ...
purpose: code-structural-index
security_review: passed
license_review: passed
installed_by: TASK-...
```

---

## 30. Tool discovery and installation policy

If a task requires a capability not currently available:

```text
TASK
 ↓
capability resolver
 ↓
missing tool/dependency
 ↓
search existing approved capabilities
 ↓
if absent:
   research candidates
   evaluate security/licence/maintenance/cost
   choose reversible option
   assess authority level
 ↓
install/configure if policy permits
 ↓
register tool
 ↓
health/conformance test
 ↓
update capability memory
 ↓
continue task
```

Agents may install dependencies/tools automatically **only** when all are true:

- the project policy grants that role installation authority;
- installation is reversible;
- cost is within budget;
- no secret/privilege escalation is required beyond granted scope;
- licence/security policy is satisfied;
- version is pinned/recorded;
- the tool is registered;
- the environment remains reproducible.

Otherwise raise a Human Decision Gate.

---

## 31. MCP architecture

MCP is a preferred interoperability mechanism for exposing portable tools/resources when suitable.

The framework should support:

```text
governance/tools/mcp/
    registry.yaml
    servers/
    permissions/
    health/
```

Examples of useful capability families:

- GitHub repository inspection;
- issue/PR access;
- web/browser research;
- package/library documentation;
- cloud management;
- database introspection;
- observability;
- CI/CD;
- artifact stores;
- internal repository intelligence.

Do not grant every agent every MCP server.

Tool exposure is role/task scoped.

---

## 32. Tool permissions

Permission classes should include:

```text
READ_REPO
WRITE_REPO_SCOPED
RUN_TESTS
NETWORK_READ
NETWORK_WRITE
PACKAGE_INSTALL
SYSTEM_INSTALL
DB_READ
DB_WRITE
CLOUD_READ
CLOUD_WRITE
CI_TRIGGER
SECRET_READ
DEPLOY_STAGING
DEPLOY_PRODUCTION
```

Privilege follows least authority.

---

# PART IX — COMMAND/CONTROL SURFACE

## 33. Natural language is the primary human interface

The human should not need to memorise framework commands.

Examples:

> "Discover the best approach for X and tell me the impact."

should compile to:

```text
DISCOVER
   ↓
research/evidence
   ↓
candidate change
   ↓
CIT-P
   ↓
human-readable impact
```

If the human then says:

> "Approve it."

the orchestrator resolves the pending proposal and executes:

```text
APPROVE
  ↓
Decision record
  ↓
CIT-E
  ↓
state propagation
  ↓
tests/validation
  ↓
continue
```

Natural-language intent is translated into deterministic operations.

---

## 34. Small human-facing command set

A minimal explicit surface is recommended:

```text
gov status
gov continue
gov decide
gov audit
gov pause
```

Most other operations are internal workflow actions.

The user can express the same intent in plain language.

---

## 35. Internal governance operations

The internal API may be much larger:

- `discover()`
- `impact_simulate()`
- `approve()`
- `reject()`
- `compile_context()`
- `claim_task()`
- `release_task()`
- `create_task()`
- `close_task()`
- `rebuild_memory()`
- `run_governance_suite()`
- `run_product_suite()`
- `checkpoint()`
- `resolve_skill()`
- `resolve_tool()`
- `install_tool()`
- `create_handoff()`
- `replan()`
- `rollback_transaction()`

Expose these consistently through CLI, MCP/API and provider adapters.

---

# PART X — SPECIFICATION AND FEATURE/CAPABILITY READINESS

## 36. SPEC is the engineering contract

The specification captures the lineage:

```text
IDEA
 ↓
MISSION / OUTCOMES
 ↓
USERS / ACTORS
 ↓
JOURNEYS
 ↓
SCENARIOS
 ↓
FEATURES / CAPABILITIES
 ↓
DATA
 ↓
REQUIREMENTS + NFRs
 ↓
RESEARCH / EXPERIMENTS
 ↓
DECISIONS
 ↓
PROCESSING / ALGORITHMS
 ↓
ARCHITECTURE
 ↓
INTERFACES
 ↓
SECURITY / PERFORMANCE / OPERATIONS
 ↓
WBS / TASK DAG
 ↓
ACCEPTANCE / TEST OBLIGATIONS
 ↓
LIVE EVIDENCE
```

---

## 37. Feature/Capability Readiness Contract

Every feature/capability has a machine-readable checklist.

Recommended dimensions:

1. intent/outcome;
2. user/actor;
3. journey/workflow;
4. scenarios;
5. inputs;
6. data model/schema;
7. representative test data;
8. processing/algorithm;
9. expected outputs;
10. functional requirements;
11. non-functional requirements;
12. UX/interactions where applicable;
13. backend/service behaviour;
14. database/state requirements;
15. interface/API/event contracts;
16. security/privacy;
17. integrations;
18. DevOps/runtime;
19. observability;
20. performance/capacity;
21. cost constraints;
22. recovery/fallback;
23. measurable success criteria;
24. measurable failure criteria;
25. independent acceptance/system tests;
26. documentation/operations needs.

Every cell is:

```text
PRESENT
MISSING
PROVISIONAL
BLOCKED
N/A_WITH_REASON
```

Silent N/A is invalid.

---

## 38. Readiness generates work

A checker does not merely report gaps.

Example:

```text
F27:
scenarios              ✓
data model             ✓
test dataset           MISSING
performance threshold  MISSING
security analysis      MISSING
independent tests      MISSING
```

The planner creates:

```text
TASK-201 construct/discover representative dataset
TASK-202 benchmark/propose performance threshold
TASK-203 security analysis
TASK-204 independent acceptance-test design
```

Their dependency relationships are added to the same DAG.

Only when required pre-implementation cells satisfy policy can production code tasks become `READY`.

---

## 39. Scenarios drive data and tests

```text
FEATURE
 ↓
SCENARIOS
 ↓
DATA REQUIREMENTS
 ↓
TEST DATA DESIGN
 ↓
SUCCESS/FAILURE CRITERIA
 ↓
INDEPENDENT TEST DESIGN
```

The data author should normally be independent of both the implementation author and end-to-end test author.

Data may be:

- approved real data;
- open/public datasets;
- repository/GitHub test corpora;
- generated synthetic data;
- simulator output;
- fixtures.

Provenance must be recorded.

---

## 40. Standard capability taxonomy

The framework defines a broad capability taxonomy. Projects explicitly mark applicability.

Core categories:

- Product/Outcome
- UX
- Frontend
- Backend
- Database/Storage
- Integration/API
- DevOps/Infrastructure
- Security/Privacy
- Testing/Quality

Optional but first-class categories:

- Data Engineering
- AI/ML/Model
- Evaluation
- Observability/SRE
- Performance/Capacity
- Operations/Recovery
- Scientific/R&D

A project may extend the taxonomy through a governed change.

---

# PART XI — DYNAMIC WORK SYSTEM

## 41. One task system, many task classes

Tasks are bounded units of work that move project state forward.

Classes may include:

- discovery;
- research;
- experiment;
- specification;
- decision preparation;
- data;
- architecture;
- implementation;
- integration;
- test design;
- test execution;
- security;
- DevOps;
- performance;
- validation;
- refactor;
- repair;
- documentation;
- release;
- tooling;
- memory;
- governance.

Do not create a separate plan for “research” and another for “coding”. Their dependencies are the reason a unified DAG exists.

---

## 42. Task contract

Example:

```yaml
id: TASK-0143
class: implementation
feature: F27
objective: ...
requirements: [...]
decisions: [...]
dependencies: [...]
blocks: [...]
scenarios: [...]
required_data: [...]
acceptance_tests: [...]
required_skills: [...]
required_tools: [...]
minimum_model_tier: T2
minimum_reasoning: medium
allowed_paths: [...]
forbidden_paths: [...]
production_merge_allowed: true
```

An experiment might specify:

```yaml
class: experiment
production_merge_allowed: false
```

---

## 43. Dynamic task generation

Tasks may be created by:

- new features;
- missing readiness cells;
- failed tests;
- audit findings;
- research discoveries;
- human decisions;
- CIT effects;
- lessons;
- missing skills/tools;
- retrieval failures;
- security findings;
- performance regressions.

The WBS is therefore a continuously compiled execution graph, not a static plan.

---

## 44. Parallel and serial execution

Maintain:

- runnable set;
- longest open dependency chain;
- per-feature end-to-end path;
- blocked set;
- human-gate dependencies.

The orchestrator continues independent runnable work when one branch is waiting for human input.

---

# PART XII — RESEARCH, DISCOVERY AND EXPERIMENTATION

## 45. Research must become evidence

Research outputs must record:

- question;
- reason;
- method;
- sources/data;
- measurements;
- uncertainty;
- conclusion;
- confidence;
- decisions/tasks influenced.

Unstructured research notes remain reference only until transformed into a governed finding or decision.

---

## 46. Discovery flow

A normal discovery sequence may be:

```text
product intent
 → actors/users
 → journeys
 → scenarios
 → feature/capability
 → data needs
 → processing
 → research/experiments
 → architecture
 → readiness gaps
 → task DAG
```

A human can invoke this in plain language.

---

# PART XIII — CHANGE CONTROL

## 47. Change-Impact Transaction

Every accepted material state change is handled atomically.

### 47.1 CIT-P — Change Impact Simulation

Before approval:

```text
proposal
 ↓
deterministic graph traversal
 ↓
semantic/lexical/code candidate retrieval
 ↓
bounded reasoning
 ↓
impact radius
 ↓
human-readable consequences
```

### 47.2 CIT-E — Change Impact Execution

After approval:

```text
decision finalised
 ↓
mutation manifest
 ↓
authoritative updates
 ↓
staleness/retest/rework propagation
 ↓
derived-view regeneration
 ↓
memory/index refresh
 ↓
verification
 ↓
commit or rollback/block
```

---

## 48. Automatic impact simulation

The human should not need to type `/impact`.

When a proposed change meets an impact threshold, CIT-P is automatic.

Typical triggers:

- architecture change;
- behaviour change;
- interface change;
- security change;
- governance/policy change;
- high-cost infrastructure choice;
- acceptance-criteria change;
- large data migration.

The result is surfaced in chat.

---

## 49. Impact radius

```text
R0 editorial/local
R1 local semantic change
R2 component/module
R3 subsystem/workflow
R4 project-wide
R5 governance/framework-wide
```

Radius affects:

- graph traversal;
- semantic breadth;
- test scope;
- model tier;
- number of specialist agents;
- required human approval;
- rollback plan.

---

# PART XIV — HUMAN DECISION GATES AND CONFLICT RESOLUTION

## 50. Agent-resolvable versus human-resolvable contradictions

For each contradiction evaluate:

- impact;
- reversibility;
- confidence;
- authority;
- cost of being wrong;
- downstream blast radius.

Resolution:

```text
conflict
 ↓
deterministic precedence resolves?
 ├─ yes → fix + record
 └─ no
      ↓
low impact + high confidence + reversible?
 ├─ yes → agent resolves + records rationale
 └─ no → Human Decision Gate
```

---

## 51. Human-gate examples

Normally raise to the human for:

- product behaviour/direction;
- expensive or irreversible architecture;
- material privacy/security/legal issue;
- major database/data migration;
- destructive data action;
- major external service/vendor choice;
- significant UX direction;
- commercial assumptions;
- high-cost infrastructure;
- material acceptance/success criterion;
- low-confidence decision on critical path;
- governance/framework change.

---

## 52. Human questions must appear in the active chat

Hard invariant:

> **A Human Decision Gate that exists only in a file is not considered presented.**

The orchestrator must surface it in the active human interface.

A decision package contains:

- plain-language question;
- why it matters now;
- current state;
- options;
- impact;
- reversibility;
- cost/rework;
- recommendation;
- confidence;
- exact permitted next actions.

---

## 53. Do not globally stop when one branch needs the human

```text
Feature A blocked by human decision
Feature B runnable
Feature C runnable
```

The orchestrator:

1. presents A's question;
2. continues B and C;
3. applies the answer when received;
4. recomputes the DAG.

Only stop globally when the gate blocks all valid work or policy requires a freeze.

---

## 54. Decision prioritisation

Rank human questions by:

- critical-path effect;
- number of tasks blocked;
- impact radius;
- time sensitivity;
- irreversibility.

Batch low-priority decisions when possible.

---

# PART XV — MODELS AND ROUTING

## 55. Capability tiers

```text
T0 — deterministic/no LLM
SQL, graph, AST, parsing, validation, tests, generation.

T1 — lightweight/economical
classification, extraction, formatting, routine small edits.

T2 — strong engineering
normal implementation, debugging, integration, substantial test work.

T3 — frontier/high-reasoning
orchestration, major architecture, difficult R&D, high-impact refactor,
critical security, governance evolution, independent final audit.
```

---

## 56. Reasoning requirement

A task may declare:

```text
low
medium
high
extra_high
```

The router enforces the minimum capability supported by the chosen provider.

---

## 57. Role defaults

Example:

```yaml
orchestrator:
  minimum_tier: T3
  default_reasoning: high

memory_engineer:
  minimum_tier: T3
  default_reasoning: high

backend_engineer:
  minimum_tier: T2
  default_reasoning: medium

routine_documentation:
  minimum_tier: T1
  default_reasoning: low

independent_auditor:
  minimum_tier: T3
  default_reasoning: high
```

A provider may map current model names to tiers without rewriting project records.

---

## 58. Empirical model routing

Record:

- model;
- provider;
- task class;
- reasoning effort;
- cost;
- latency;
- pass/fail;
- repair count;
- reviewer findings.

Use evidence to improve future routing.

---

# PART XVI — CHECKPOINTS, COMPACTION AND HANDOFFS

## 59. Checkpoint policy

Persist structured resumable state:

```yaml
session:
role:
task:
mode:
claim:
last_completed_step:
next_action:
pending_decisions:
open_questions:
open_transactions:
files_changed:
tests_status:
context_packet_hash:
memory_snapshot:
```

Do not use a giant prose conversation summary as the checkpoint.

---

## 60. Checkpoint triggers

Mandatory after:

- task transition;
- material decision;
- accepted CIT;
- significant mutation;
- before handoff;
- before model/provider switch;
- before session close;
- before known compaction.

A provider adapter should use native pre-compaction hooks where available.

A provider-independent watchdog should additionally checkpoint based on context utilisation/execution boundaries so correctness does not depend on a proprietary hook.

---

## 61. Spawned-agent return contract

Every worker returns structured state:

```yaml
task:
status:
work_completed:
files_changed:
evidence:
tests:
discoveries:
risks:
lessons:
proposed_decisions:
unresolved:
recommended_next_action:
```

Its conversation may disappear. Its material result may not.

---

# PART XVII — VERIFICATION AND GOVERNANCE TESTS

## 62. Product verification

Maintain:

- unit tests;
- contract tests;
- integration tests;
- system tests;
- acceptance tests;
- scenario tests;
- security tests;
- performance tests;
- recovery tests;
- live/smoke evidence.

Independent test authors should derive behavioural tests from approved specifications/scenarios rather than copying implementation assumptions.

---

## 63. Governance verification

Test families:

- schema/invariants;
- graph integrity;
- index freshness;
- memory retrieval regression;
- authority/role limits;
- mutation scope;
- repository/path-map compliance;
- context reproducibility;
- concurrency/session claims;
- adapter/model portability;
- skill regression;
- command-contract consistency;
- secrets/sensitivity indexing;
- recovery/rebuild;
- fresh-agent reconstruction;
- product traceability;
- audit reproducibility.

---

## 64. Governance suite currency

A green governance suite is itself a governed record.

If inputs relevant to the suite change, the prior green result becomes stale.

A task affecting governance cannot close on an obsolete green record.

---

# PART XVIII — OBSERVABILITY

## 65. Organisational telemetry

Record at minimum:

- agent/session;
- model/provider;
- role;
- task;
- skill versions;
- tool versions;
- context packet;
- retrieval queries/hits;
- token input/output;
- latency;
- cost;
- files read;
- files written;
- tests;
- retries;
- failures;
- handoffs;
- decisions raised;
- human interventions.

Use OpenTelemetry-compatible tracing where practical.

---

## 66. Questions telemetry should answer

- Which role causes the most rework?
- Did semantic retrieval lower tokens per completed task?
- Which model tier is over/under-powered?
- Which skill version has the lowest repair rate?
- Which workstream creates the most human gates?
- Which retrieval route misses known knowledge?
- What is the cost per feature/task class?
- What is the first-pass completion rate?

---

# PART XIX — LEARNING AND DYNAMICS

## 67. Lesson lifecycle

```text
execution/report
 ↓
lesson candidate
 ↓
corroboration
 ↓
classification
 ↓
rule/skill/retrieval/tool proposal
 ↓
independent validation
 ↓
human approval where required
 ↓
new governed version
```

A lesson can be scoped:

```text
framework
governance
project
product
feature
engineering
```

A lesson is evidence, not authority.

---

## 68. Decision versus lesson

A **decision** records what the project chooses to do.

A **lesson** records what execution taught the organisation.

A lesson influences the project only through a governed change/decision where required.

---

# PART XX — LEGACY GOVERNANCE MIGRATION

## 69. Legacy Governance Retirement Protocol

On v4 adoption:

```text
activate v4 authority baseline
 ↓
mark prior governance LEGACY
 ↓
inventory legacy mechanisms
 ↓
extract useful:
  decisions
  lessons
  skills
  evidence
  research
 ↓
reconcile contradictions
 ↓
retire/remove duplicate mechanisms
 ↓
validate no active dependency remains
```

Old governance must never remain silently co-authoritative.

---

## 70. Raw chat databases

A historical chat store may be preserved if useful for forensics, but raw chats should not normally be active/default project memory.

Distil durable knowledge into governed artefacts.

If a chat DB is retired:

- prove no active functionality depends on it;
- export any unique durable knowledge;
- classify retention requirements;
- remove it through CIT-E;
- update memory indexes;
- run regression tests.

---

# PART XXI — ARCHIVE AND HISTORY

## 71. Archive policy

Use archive for historical material that genuinely benefits from browsable retention.

Do not archive every dead source file.

For unused code:

```text
remove from active tree
Git preserves history
```

Keep code under `archive/code-reference/` only when a deliberate reference implementation is valuable.

Historical/superseded artefacts are excluded from default current-state retrieval unless explicitly requested.

---

# PART XXII — SECURITY, BUDGET AND EMERGENCY CONTROL

## 72. Security and sensitivity

Every tool, dataset, path and memory namespace has an access/sensitivity classification.

Never index:

- secrets;
- credentials;
- unapproved customer material;
- production personal data;
- restricted legal/security material

into generic semantic memory.

---

## 73. Budget/resource policy

Govern:

- model spend;
- API spend;
- cloud changes;
- number of parallel agents;
- network calls;
- package/tool installation;
- high-cost experiments.

A task exceeding delegated thresholds creates a Human Decision Gate.

---

## 74. Emergency controls

The human must be able to invoke:

```text
PAUSE
FREEZE_WRITES
CANCEL_AGENTS
ROLLBACK_TRANSACTION
```

These map to deterministic governance operations.

---

# PART XXIII — FRAMEWORK HEALTH

## 75. Suggested health SLOs

Track:

- governance suite freshness;
- product test health;
- retrieval Recall@K;
- stale index count;
- orphan graph-node count;
- unresolved contradictions;
- unresolved human gates;
- task traceability percentage;
- feature readiness coverage;
- context packet size;
- tokens/completed task;
- first-pass task completion;
- handoff failure rate;
- memory rebuild success;
- fresh-agent reconstruction success.

---

## 76. Definition of a healthy repository

A repository is `HEALTHY` only when:

1. authority is unambiguous;
2. no legacy mechanism remains accidentally authoritative;
3. deterministic state is internally consistent;
4. graph/index freshness passes;
5. memory retrieval meets agreed regression thresholds;
6. sensitive material is correctly isolated;
7. active features have explicit readiness status;
8. runnable/blocked task state is correct;
9. tests/traceability satisfy policy;
10. governance tests are current and green;
11. no unresolved critical audit finding exists;
12. a fresh strong agent can reconstruct the current project state within the context/read budget;
13. derived memory/indexes can be rebuilt from authoritative sources.

---

# PART XXIV — CANONICAL GOVERNANCE OS SOURCE, RELEASES AND UPSTREAM LEARNING

## 75A. The framework is developed once as a product

The Governance OS itself must be developed in a dedicated, clean canonical repository.

Recommended logical repository:

```text
agentic-engineering-os/
├── framework/
│   ├── constitution/
│   ├── policies/
│   ├── schemas/
│   ├── skills/
│   └── adapters/
├── runtime/
│   ├── memory/
│   ├── retrieval/
│   ├── graph/
│   ├── code-intelligence/
│   ├── context/
│   ├── cit/
│   ├── orchestration/
│   ├── checkpoints/
│   └── observability/
├── cli/
├── tools/
│   ├── registry/
│   ├── mcp/
│   └── installers/
├── migrations/
├── tests/
├── fixtures/
│   ├── greenfield/
│   ├── brownfield/
│   ├── migration/
│   ├── update/
│   ├── upstream-learning/
│   └── failure-injection/
├── lessons/
│   └── inbox/
├── change-proposals/
├── release/
└── docs/
```

The canonical repository should normally be hosted in a private remote Git service such as a private GitHub repository so releases, issues, pull requests and version history are available across machines.

---

## 75B. Product repositories are consumers, not framework-development branches

A project repository consumes a released Governance OS version.

It must not independently reinterpret and rebuild the company OS from prose every time.

The installed release is recorded in `governance/framework.lock`.

Example:

```yaml
framework: agentic-engineering-os
version: 4.1.0
release_commit: <commit>
release_hash: <sha256>
source: <private-release-source>
```

This makes framework conformance deterministic.

---

## 75C. Release certification

A Governance OS release candidate must pass more than unit tests.

Mandatory certification classes should include:

1. framework/schema/policy tests;
2. greenfield synthetic project;
3. deliberately dirty brownfield project;
4. path-migration fixture;
5. legacy-governance retirement fixture;
6. memory rebuild/retrieval fixture;
7. independent test-author fixture;
8. framework-update fixture;
9. multi-machine clone/rebuild fixture;
10. upstream lesson sanitisation/export fixture;
11. secrets/outbound-data negative controls;
12. provider/model-adapter conformance.

The synthetic brownfield fixture should intentionally contain contradictions, stale rules, obsolete chat memory, broken indexes, conflicting specs and path problems.

A release is not certified merely because the framework can start a new clean repository.

---

## 75D. Immutable releases and semantic versioning

Released framework kernels are immutable.

Suggested version semantics:

```text
PATCH  x.y.Z  backward-compatible repair
MINOR  x.Y.z  backward-compatible capability addition
MAJOR  X.y.z  intentional breaking governance/schema contract
```

Every release must provide:

- release manifest;
- file hashes;
- supported migration paths;
- schema versions;
- CLI/runtime versions;
- adapter versions;
- release notes;
- affected indexes;
- required human decisions;
- rollback procedure.

---

## 75E. Lessons flow upstream selectively

Projects teach the company OS, but project repositories do not upload themselves to the Governance OS repository.

Lesson scopes:

```text
PROJECT
PRODUCT
FRAMEWORK
```

Only `FRAMEWORK` candidates are eligible for upstream export.

Flow:

```text
local lesson
 ↓
scope classification
 ↓
framework candidate
 ↓
sanitisation
 ↓
secret/sensitivity/outbound-path scan
 ↓
synthetic reproducer where possible
 ↓
approval policy
 ↓
upstream lesson packet
 ↓
canonical Governance OS lessons/inbox/
```

Raw code, product specs, customer data, project vector stores and unrelated repository files are prohibited by default.

---

## 75F. Upstream lesson packet

A framework lesson packet should contain the minimum useful abstraction:

```yaml
lesson_id:
category:
problem_statement:
generic_failure_mode:
impact:
evidence_strength:
suggested_framework_change:
source_project_alias:
local_reference:
sensitive_content_removed: true
raw_product_code_included: false
raw_customer_data_included: false
```

Where reproduction matters, prefer a synthetic regression fixture generated from the failure pattern.

---

## 75G. Upstream Export Gate

Before any project-derived content leaves the project repository:

1. classify the lesson as framework-relevant;
2. remove project/customer-identifying content;
3. run secret scanning;
4. run sensitivity policy;
5. enforce an outbound allowlist;
6. prefer a synthetic reproducer;
7. require approval according to project policy;
8. record the exported packet hash and destination.

The default allowed payload is only:

- a sanitised framework lesson packet;
- a synthetic regression fixture;
- optional aggregate non-sensitive metrics if explicitly enabled.

Everything else is denied.

---

## 75H. Framework learning and releases

One lesson does not necessarily trigger a release.

Framework lessons accumulate and cluster.

Possible triggers:

```text
critical framework defect → immediate patch candidate
same failure across multiple projects → strong change candidate
repeated related low-level lessons → batched minor release
```

Accepted lessons create a Framework Change Proposal.

That change is implemented only in the canonical Governance OS repo, tested against synthetic/regression fixtures, independently reviewed, and then released.

Projects subsequently receive the improvement through `gov update`, never by directly copying another project's governance edits.

---

# PART XXV — PROJECT INITIALISATION, ADOPTION, MIGRATION AND UPDATES

## 77. Two official onboarding modes

The Governance OS supports two official project onboarding paths:

```text
gov init
```

for a genuinely new/greenfield repository, and:

```text
gov adopt
```

for an existing/brownfield repository.

The same certified Governance OS kernel is used in both cases. The difference is the migration/adoption procedure.

---

## 78. Greenfield `gov init`

Recommended sequence:

```text
certified Governance OS release
 ↓
install kernel
 ↓
create project overlay
 ↓
create repository contract/path map
 ↓
initialise tracked authoritative state
 ↓
initialise/rebuildable runtime
 ↓
define product intent
 ↓
discover scenarios/features
 ↓
generate readiness gaps/tasks
 ↓
execute
 ↓
verify
```

Greenfield projects should never need project-specific copies of the Governance OS source repository. They consume a released version.

---

## 79. Brownfield `gov adopt`: path-first, memory-safe migration

For an existing repository, do **not** immediately index the current tree and then reorganise it. That would build expensive memory against paths that are about to change.

The safe order is:

```text
A0 safety snapshot / conditional interrupted-session recovery when applicable
 ↓
A1 cold deterministic repository inventory
 ↓
A2 classify every material artefact and legacy mechanism
 ↓
A3 design target canonical repository map
 ↓
A4 write path-migration + governance-adoption plan
 ↓
A5 fresh independent migration-plan review
    + independent migration-test design
 ↓
A6 controlled path/governance migration in batches
 ↓
A7 behavioural/path/integrity verification
 ↓
A8 audit/extract/retire legacy memory mechanisms
 ↓
A9 build/rebuild Development Knowledge Fabric on stable canonical paths
 ↓
A10 fresh independent memory verification
 ↓
A11 fresh full v4 project audit
 ↓
A12 audited remediation/refactor iterations
 ↓
ADOPTED_HEALTHY
```

### 79.1 Existing memory is inspected before path migration, but rebuilt afterwards

Legacy memory stores may contain unique durable knowledge. Therefore the cold inventory/classification phase must identify:

- existing SQLite/DB stores;
- chat/session stores;
- old decisions/lessons;
- path maps;
- vector indexes;
- graph stores;
- checkpoint state;
- generated indexes;
- unique information not present elsewhere.

However, broad semantic/vector/code indexing for the new v4 system should normally wait until canonical paths are stable.

Before retiring an old store, extract any unique durable knowledge into governed records.

### 79.2 Do not move before mapping

No broad file move begins until the migration plan contains a target path for every material artefact class.

A migration catalogue should capture:

```yaml
artifact_id:
current_path:
current_class:
authority_status:
target_path:
target_class:
action: KEEP_IN_PLACE | MOVE | SPLIT | MERGE | RENAME | EXTRACT | RETIRE | DELETE_FROM_ACTIVE_TREE
dependencies:
imports_or_refs:
indexing_policy:
verification:
```

### 79.3 Preserve native product architecture where justified

Canonical governance/spec paths should converge strongly.

Product source code should only be moved when the target structure is materially better and migration risk is justified. Good native framework/package layouts may remain and be mapped through the Repository Contract.

The goal is navigability and determinism, not cosmetic folder uniformity.

### 79.4 Migration must be independently challenged

The migration engineer does not author the only acceptance tests.

A fresh independent Migration Verifier/Test Author should:

- review the proposed target path map;
- challenge classification decisions;
- author held-out path/reference/import/navigation tests;
- define behaviour-preservation tests;
- define legacy-authority negative tests;
- define rollback/recovery checks;
- verify the migrated repository without trusting the migration report.

Only after migration passes should new memory indexes be treated as canonical-development infrastructure.

---

## 80. Project overlay versus installed kernel

Every consumer repository must separate framework-owned files from project-owned configuration:

```text
governance/
├── kernel/                 # installed immutable release payload
├── project/                # project-owned overlay/configuration
├── generated/              # adapter/manifests generated from kernel + overlay
└── framework.lock          # exact installed release/version/hash
```

Recommended project overlay:

```text
governance/project/
├── PROJECT_POLICY.yaml
├── REPOSITORY_CONTRACT.yaml
├── CAPABILITY_PROFILE.yaml
├── TOOL_PERMISSIONS.yaml
├── MODEL_ROUTING_OVERRIDES.yaml
├── DATA_SENSITIVITY.yaml
└── PROJECT_EXCEPTIONS.yaml
```

Agents do not customise `governance/kernel/` directly inside a product repo.

Framework improvements are proposed upstream and released centrally.

---

## 81. Local derived runtime

Derived project memory should normally live outside tracked source:

```text
.governance-runtime/
├── state.db
├── vector/
├── graph/
├── code-index/
└── cache/
```

and normally be ignored by Git.

Tracked manifests provide reproducibility:

```text
governance/generated/
├── memory-manifest.json
├── index-manifest.json
├── tool-registry.json
└── adapter-manifest.json
```

A new machine must be able to clone the project and run:

```text
gov doctor
gov rebuild-memory
```

to reconstruct derived state.

---

## 82. `gov update`

Framework updates must be versioned and impact-checked.

```text
gov update --check
 ↓
compare current framework.lock with available release
 ↓
read release/migration manifest
 ↓
CIT-P against this project
 ↓
automatic low-risk approval or Human Decision Gate
 ↓
safety checkpoint/branch
 ↓
install new kernel
 ↓
run migrations
 ↓
preserve project overlay
 ↓
regenerate adapters
 ↓
rebuild affected indexes
 ↓
governance + integration tests
 ↓
CIT-E commit or rollback
```

A framework update must never overwrite project decisions/specifications merely because the framework changed.

---

## 83. Multi-machine operation

Git synchronises authoritative tracked project state.

Derived memory/indexes are rebuilt locally.

Therefore:

```text
Machine A:
  git pull
  gov doctor
  gov rebuild-memory if required

Machine B:
  git pull
  gov doctor
  gov rebuild-memory if required
```

The two machines do not need to synchronise opaque vector/SQLite/cache binaries.

---

# PART XXVI — HUMAN OPERATING EXPERIENCE

## 79. Example: discover → impact → approve

Human:

> Discover whether adding capability X is worthwhile and tell me the impact.

Framework:

```text
intent parser
 ↓
DISCOVERY task(s)
 ↓
research/evidence
 ↓
candidate specification/decision
 ↓
CIT-P
 ↓
plain-language outcome + recommendation
```

Human:

> Approve option B.

Framework:

```text
resolve pending proposal
 ↓
record decision
 ↓
CIT-E
 ↓
update spec/WBS/tasks/graph/tests
 ↓
refresh memory
 ↓
continue independent work
```

The human need not know the internal command names.

---

# PART XXVII — FINAL OPERATING PHILOSOPHY

The system should behave like a controlled, adaptive software-engineering organisation:

```text
INTENT
  ↓
DISCOVER
  ↓
SPECIFY
  ↓
IDENTIFY GAPS
  ↓
CREATE R&D / SPEC / DATA / TEST TASKS
  ↓
DECIDE
  ↓
PLAN DAG
  ↓
BUILD
  ↓
INTEGRATE
  ↓
VERIFY
  ↓
OBSERVE
  ↓
LEARN
  ↓
SIMULATE CHANGE
  ↓
HUMAN GATE WHEN NECESSARY
  ↓
EXECUTE CHANGE
  ↓
CONTINUE
```

The critical design rule is:

> **A new high-capability agent should be able to enter the repository with no prior conversation, use the governed memory and control plane to reconstruct the current state, determine what it is allowed to do, discover the correct next work, execute within bounded authority, produce evidence, and leave the project in a state from which another agent can continue immediately.**

That is the standard v4 should enforce.
