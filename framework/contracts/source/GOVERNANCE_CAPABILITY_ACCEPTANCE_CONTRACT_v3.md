# Governance OS Capability Acceptance Contract — v3

**Role:** First-class, versioned Governance OS capability contract and second-layer health/audit baseline.

This contract is derived from the original three Governance OS governing documents. Later independent-verification hardening requirements remain explicitly labelled as such rather than silently rewriting the original requirements.

## Canonical implementation in the Governance OS repository

The human/product owner controls the normative checklist source. The IDE agent must **not invent or rewrite its semantics from memory**.

Use this structure:

```text
framework/
  contracts/
    source/
      GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md
        # HUMAN-APPROVED NORMATIVE SOURCE; uploaded by the product owner
    governance-capability-acceptance.yaml
        # executable compiled representation consumed by Governance OS
    contract-source.lock
        # binds the compiled representation to the exact uploaded source hash
  schemas/
    governance-capability-acceptance.schema.json

tests/
  governance/
    capability-evidence-map.yaml
        # capability → test/check/evidence mapping

docs/
  generated/
    GOVERNANCE_CAPABILITY_ACCEPTANCE.md
        # generated readable runtime view
```

### Contract authority model

`framework/contracts/source/GOVERNANCE_CAPABILITY_ACCEPTANCE_CONTRACT_v3.md` is the **human-approved normative source**.

`framework/contracts/governance-capability-acceptance.yaml` is the **machine-executable compiled form**.

The runtime consumes the YAML, but it is valid only when `contract-source.lock` proves that it was compiled/validated from the exact approved source hash.

The builder may create the destination path and compiler/schema machinery, but MUST stop and ask the product owner to upload the approved contract file. It must not fabricate the contract from remembered conversation context or silently change its semantics.

Any semantic difference between source and compiled representation is a hard failure.

The generated docs view is derived and non-authoritative.

Consumer projects do **not** receive giant synthetic qualification repositories. They receive the contract, the governance health scheduler, and the executable evidence/check families needed to evaluate the real project.

## Required contract fields per capability

Every capability item should carry, where applicable:

- stable capability ID;
- title/description;
- source governing-document reference;
- requirement class: `ORIGINAL`, `POST_VERIFICATION_HARDENING`, or `EXECUTION_REFINEMENT`;
- severity if violated;
- applicability rule;
- evidence class(es);
- automated check/test IDs;
- independent-verification obligation;
- evidence-freshness triggers;
- health-scheduler tier(s) G0–G6;
- advanced-qualification challenge IDs;
- adoption verification obligation;
- periodic operational-audit obligation;
- allowed status values;
- N/A requirements;
- remediation/task-generation rule.

## Relationship between the contract and the governance suite

The contract is the umbrella acceptance definition.

The governance suite is the continuous executable evidence layer beneath it.

Not every capability can be proven by a unit test. Each item must therefore map to one or more evidence classes:

- automated invariant/guard;
- unit/integration/system test;
- governance health check;
- independent held-out test;
- migration/rollback evidence;
- synthetic-repository evidence;
- human-gate evidence;
- clean-clone/release evidence;
- independent audit evidence.

A capability may not be reported `PRESENT_AND_SUBSTANTIAL` solely because a file/schema/policy exists.

## Evidence freshness

A previously green capability becomes `STALE` when any relevant evidence input changes, including where applicable:

- governing contract/policy;
- runtime/kernel implementation;
- schema;
- migration;
- tool/plugin;
- model/retrieval profile;
- project path map;
- authoritative spec/decision;
- relevant source files;
- relevant index manifest;
- security/sensitivity policy.

Stale evidence must trigger the appropriate G0–G5 re-check before work is allowed to rely on it.

## Lifecycle

The same contract is used at:

1. Governance OS build/Prompt 2 verification;
2. pre-qualification capability-baseline acceptance;
3. sophisticated synthetic qualification;
4. final release certification;
5. `gov init`;
6. `gov adopt`;
7. post-adoption acceptance;
8. `gov update`;
9. major architecture/security/memory/tool/retrieval changes;
10. periodic operational governance-health audits;
11. framework-upgrade regression.


# GATE A — Constitutional and Trust Foundations

## A1. Canonical authority and policy precedence
- [ ] Constitution/hard invariants are identifiable and machine-readable.
- [ ] Security and authority floors cannot be weakened by lower-precedence policy.
- [ ] Project policy may specialise/strengthen only within allowed override modes.
- [ ] Active decision/spec/task context follows deterministic precedence.
- [ ] Retrieved context/model inference cannot override higher authority.
- [ ] Invalid weakening attempts fail closed and are observable.

**Advanced qualification challenge:** inject contradictory project policies, obsolete provider rules, active/superseded decisions, malicious exceptions, and attempted authority/sensitivity weakening.

## A2. Authentic root of trust **[POST-VERIFICATION HARDENING]**
- [ ] Release/source authenticity is established before any privileged kernel material is staged or installed.
- [ ] Integrity and authenticity are treated as separate properties.
- [ ] Init/adopt/update/reinstall/recovery/rollback ingress paths share a non-circular trust root.
- [ ] Installed-kernel verification detects post-install tampering.
- [ ] Source-release authentication detects pre-install tampering.
- [ ] A source directory cannot regenerate its own trusted identity.
- [ ] Trusted release identity is recorded, not invented, by `framework.lock`.
- [ ] Bootstrap/dev/test trust modes cannot masquerade as certified production.
- [ ] Signing keys/trust anchors support rotation/revocation/recovery.
- [ ] Release verification works offline after obtaining an authentic release envelope where designed.

**Advanced qualification challenge:** tampered source payload, stale/forged manifest, wrong key, altered security policy, modified migration, downgrade/replay attempt, interrupted install.

## A3. Security, sensitivity and permissions
- [ ] Paths/datasets/tools/namespaces carry sensitivity/access classification.
- [ ] Secret/credential/restricted content is excluded according to policy.
- [ ] Restricted/confidential namespaces cannot be weakened by project overrides.
- [ ] Tool execution respects role/authority/permission boundaries.
- [ ] Destructive/elevated operations require correct gates.
- [ ] Outbound/export controls are default-deny where required.

**Advanced qualification challenge:** seeded secrets, restricted research, confidential project files, malicious plugin descriptors, weakened project policy.

## A4. Budget/resource governance
- [ ] Model/API/cloud/network/tool-install/parallel-agent/experiment budgets are governed.
- [ ] Delegated thresholds are executable, not merely declared.
- [ ] Exceeding delegated limits creates the required Human Decision Gate.
- [ ] Budget state and interventions are observable.

## A5. Emergency controls
- [ ] `PAUSE`
- [ ] `FREEZE_WRITES`
- [ ] `CANCEL_AGENTS`
- [ ] `ROLLBACK_TRANSACTION`
- [ ] Emergency commands are deterministic and authority-gated.
- [ ] Recovery from emergency controls is auditable.

---

# GATE B — Repository Contract, Paths and State

## B1. Standard repository contract
- [ ] Governance/framework/project/generated/runtime boundaries are explicit.
- [ ] Good native product architecture is preserved when healthy.
- [ ] Repository contract maps project-specific layout without cosmetic refactoring.
- [ ] Generated/runtime state is distinguished from authoritative tracked state.

## B2. Path map
- [ ] Every material artefact can be classified by current path, class, authority and intended target.
- [ ] Target action supports KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE/DELETE_FROM_ACTIVE_TREE.
- [ ] Unknown material artefacts block destructive migration.
- [ ] Imports/references/citations/consumers are represented.
- [ ] Path-map compliance is machine-checkable.

**Advanced qualification challenge:** Repo B starts without a path map; includes misplaced specs, duplicate authority, provider rules, dead code, generated files in wrong locations and hidden cross-references.

## B3. Authoritative vs derived state
- [ ] Git/project records remain authoritative.
- [ ] SQLite/vector/graph/lexical/code indexes are derived.
- [ ] Deleting derived state cannot delete project truth.
- [ ] Derived records carry provenance sufficient to reconstruct source hits.

---

# GATE C — Development Knowledge Fabric

## C1. Deterministic structured memory
Must represent current truth for:
- [ ] projects
- [ ] features/capabilities
- [ ] requirements
- [ ] decisions
- [ ] tasks
- [ ] scenarios
- [ ] tests
- [ ] interfaces
- [ ] experiments
- [ ] releases
- [ ] claims
- [ ] transactions
- [ ] statuses
- [ ] skill versions
- [ ] tool versions
- [ ] model-routing records
- [ ] index manifests

## C2. Relationship/graph memory
- [ ] Typed relationships support DEPENDS_ON/BLOCKS/IMPLEMENTS/REALISES/GOVERNED_BY/CONSTRAINS/DERIVED_FROM/SUPERSEDES/VALIDATED_BY/TESTS/USES/PRODUCES/CONSUMES/AFFECTS/GENERATED_FROM/CALLS/IMPORTS/OWNS/FAILED_BECAUSE/LEARNED_FROM or equivalent.
- [ ] Graph integrity checks detect orphan/stale/reversed/invalid relationships.
- [ ] Impact traversal is executable.

## C3. Semantic memory
- [ ] Decisions/rationale
- [ ] lessons/failures
- [ ] reports/research
- [ ] experiments
- [ ] requirements/specifications
- [ ] selected code units
- [ ] Semantic namespace/authority filters apply before or during retrieval.

## C4. Lexical memory
- [ ] Exact terms
- [ ] identifiers
- [ ] filenames
- [ ] error strings
- [ ] APIs/config keys
- [ ] literal phrases

## C5. Code-structural memory
- [ ] AST/LSP/SCIP or equivalent
- [ ] symbols/definitions/references
- [ ] inheritance/interfaces
- [ ] calls/imports
- [ ] route registrations
- [ ] DB models
- [ ] test-coverage relationships
- [ ] language-appropriate adapters are resolved via capability registry

## C6. Temporal memory
- [ ] what changed
- [ ] when
- [ ] why
- [ ] causal decision
- [ ] supersession/version lineage

## C7. Episodic execution memory
- [ ] agent/session
- [ ] task/context
- [ ] tools
- [ ] files read/changed
- [ ] tests/outcomes
- [ ] failures/discoveries

## C8. Failure memory
- [ ] bugs
- [ ] failed approaches
- [ ] wrong assumptions
- [ ] retrieval misses
- [ ] regressions
- [ ] migration failures
- [ ] tool failures

## C9. Working memory/context packet
- [ ] small reproducible current-task context
- [ ] deterministic authority block
- [ ] retrieved supplementary intelligence
- [ ] bounded size
- [ ] provenance/citations
- [ ] duplicate suppression
- [ ] active-vs-historical separation

## C10. Capability memory
- [ ] tools
- [ ] MCP servers
- [ ] A2A agents
- [ ] packages/dependencies
- [ ] model providers
- [ ] permission/credential status
- [ ] environment/tool versions

---

# GATE D — Indexing, Retrieval and Context

## D1. Incremental indexing/freshness
- [ ] Content-hash/repo-commit based invalidation.
- [ ] Changed artefacts invalidate affected chunks/nodes/symbols.
- [ ] Rename/move/delete+add are handled.
- [ ] Model/embedder/dimension change invalidates incompatible semantic state.
- [ ] Index manifest records compatible component identity.
- [ ] Required stale indexes degrade/block task close according to policy.

## D2. Retrieval router
- [ ] structured lookup for known IDs/paths
- [ ] code/symbol route
- [ ] lexical route
- [ ] graph/impact route
- [ ] semantic route
- [ ] multi-route fusion for complex questions

## D3. Hierarchical retrieval
- [ ] document → section/record → child chunk
- [ ] code file → module/class → function/symbol
- [ ] child-first retrieval
- [ ] selective parent/graph-neighbour expansion

## D4. Component separation
- [ ] embedding model
- [ ] embedding runtime
- [ ] vector/index store
- [ ] lexical engine
- [ ] graph engine
- [ ] code intelligence
- [ ] reranker
- [ ] retrieval router
- [ ] generative/query-planning model
- [ ] context compiler
are independently identifiable and replaceable where designed.

## D5. Evidence-driven retrieval model selection
- [ ] benchmark mechanism exists
- [ ] multiple candidate models/runtimes can be compared
- [ ] golden/held-out retrieval queries exist
- [ ] Recall@K/MRR/precision/stale-hit/latency/resource metrics exist
- [ ] selected embedder/reranker revisions are pinned
- [ ] changing them requires governed migration/reindex/regression

## D6. Rebuild guarantee
- [ ] All derived memory/index state can be deleted and rebuilt.
- [ ] Fresh rebuild preserves authoritative structured state and claims where required.
- [ ] Fresh-agent reconstruction succeeds after rebuild.
- [ ] Multi-machine/path-independent rebuild is deterministic where required.

**Advanced qualification challenge:** deliberately missing index coverage, stale chunks, wrong authority namespace, archive indexed as current, renamed files duplicated, graph edges stale, deleted indexes, wrong embedder pins.

---

# GATE E — Agent Organisation and Independent Work

## E1. Authority levels
- [ ] L0-L5 or equivalent are executable.
- [ ] Role authority is checked on every privileged/mutating path.
- [ ] Lower roles cannot manufacture higher-trust facts.
- [ ] Independent auditors/testers are appropriately constrained.

## E2. Representative roles
- [ ] Orchestrator/CTO
- [ ] architecture/research/data/implementation roles as needed
- [ ] memory engineer
- [ ] independent test author
- [ ] independent verifier/auditor
- [ ] security/release roles
- [ ] project-specific roles through governed extension

## E3. Typed A2A handoffs
- [ ] Work completed
- [ ] files changed
- [ ] evidence/tests
- [ ] discoveries/risks
- [ ] lessons/proposed decisions
- [ ] unresolved items
- [ ] next action
persist beyond conversation lifetime.

## E4. Concurrency/task claims
- [ ] Sessions/worktrees/tasks can be claimed.
- [ ] Claim collision is detected.
- [ ] Claims survive derived-memory rebuild.
- [ ] Stale claims have governed recovery.
- [ ] Parallel work is allowed only where dependency/mutation constraints permit.

---

# GATE F — Skills, Tools, MCP and Capabilities

## F1. Skill lifecycle
- [ ] Skills are versioned methods, not authority.
- [ ] Skill applicability/inputs/outputs/evidence are defined.
- [ ] Skill regression is testable.
- [ ] Lessons can propose skill updates through governed promotion.

## F2. Tool Capability Registry
- [ ] identity/version
- [ ] executable/transport
- [ ] permissions
- [ ] allowed roles/task classes
- [ ] sensitivity/network/filesystem scope
- [ ] health status
- [ ] provenance/hash pin
- [ ] installation/approval status

## F3. Missing-tool acquisition
- [ ] capability gap → candidate discovery
- [ ] security/licence/maintenance/cost review
- [ ] reversible selection
- [ ] approval when required
- [ ] install/configure
- [ ] version pin
- [ ] register
- [ ] health test
- [ ] continue task

## F4. Plugin trust boundary **[POST-VERIFICATION HARDENING]**
- [ ] Descriptor cannot authorise itself.
- [ ] Registration/provenance live in trusted OS state.
- [ ] Descriptor/implementation bytes are hash-bound.
- [ ] Drift/tampering fails closed.
- [ ] Elevated permissions reference authoritative gate/decision.
- [ ] Security review cannot be self-attested.

## F5. MCP/A2A/tool separation
- [ ] MCP/tools = action/capability
- [ ] A2A = communication
- [ ] Knowledge Fabric = knowing
- [ ] No layer silently substitutes for another.

---

# GATE G — Human Command Surface

## G1. Natural-language intent
- [ ] Human can express intent without knowing internal command syntax.
- [ ] Intent maps deterministically to governed operations.
- [ ] Consequential changes automatically invoke required impact/gate logic.

## G2. Small explicit human control set
At minimum equivalent controls for:
- [ ] status
- [ ] continue
- [ ] decide
- [ ] audit
- [ ] pause/freeze/rollback as applicable

---

# GATE H — Specification and Readiness

## H1. SPEC lineage
The system can trace:
- [ ] idea
- [ ] mission/outcomes
- [ ] users/actors
- [ ] journeys
- [ ] scenarios
- [ ] features/capabilities
- [ ] data
- [ ] requirements/NFRs
- [ ] research/experiments
- [ ] decisions
- [ ] algorithms/processing
- [ ] architecture
- [ ] interfaces
- [ ] security/performance/operations
- [ ] WBS/task DAG
- [ ] acceptance/test obligations
- [ ] live evidence

## H2. 26-dimension Feature/Capability Readiness Contract
Each feature/capability explicitly tracks:
1. [ ] intent/outcome
2. [ ] user/actor
3. [ ] journey/workflow
4. [ ] scenarios
5. [ ] inputs
6. [ ] data model/schema
7. [ ] representative test data
8. [ ] processing/algorithm
9. [ ] expected outputs
10. [ ] functional requirements
11. [ ] non-functional requirements
12. [ ] UX/interactions where applicable
13. [ ] backend/service behaviour
14. [ ] database/state requirements
15. [ ] interface/API/event contracts
16. [ ] security/privacy
17. [ ] integrations
18. [ ] DevOps/runtime
19. [ ] observability
20. [ ] performance/capacity
21. [ ] cost constraints
22. [ ] recovery/fallback
23. [ ] measurable success criteria
24. [ ] measurable failure criteria
25. [ ] independent acceptance/system tests
26. [ ] documentation/operations

Statuses:
- [ ] PRESENT
- [ ] MISSING
- [ ] PROVISIONAL
- [ ] BLOCKED
- [ ] N/A_WITH_REASON
and silent N/A is invalid.

## H3. Readiness generates work
- [ ] Missing data → data task.
- [ ] Missing performance target → benchmark/research task.
- [ ] Missing security analysis → security task.
- [ ] Missing independent test → independent test-design task.
- [ ] Production implementation does not become READY before required prerequisite cells satisfy policy.

## H4. Scenarios drive data/tests
- [ ] FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE → INDEPENDENT TESTS.
- [ ] Test-data author independence is supported.
- [ ] Data provenance is recorded.

**Advanced qualification challenge:** deliberately omit scenarios, test datasets, failure criteria, NFRs, security analysis, performance targets, recovery and operations documentation.

---

# GATE I — Dynamic Work System

## I1. Unified task DAG
Supports:
- [ ] discovery
- [ ] research
- [ ] experiment
- [ ] specification
- [ ] decision-preparation
- [ ] data
- [ ] architecture
- [ ] implementation
- [ ] integration
- [ ] test design
- [ ] test execution
- [ ] security
- [ ] DevOps
- [ ] performance
- [ ] validation
- [ ] refactor
- [ ] repair
- [ ] documentation
- [ ] release
- [ ] tooling
- [ ] memory
- [ ] governance

## I2. Task contract
- [ ] objective
- [ ] requirements/decisions
- [ ] dependencies/blocks
- [ ] scenarios/data
- [ ] acceptance tests
- [ ] required skills/tools
- [ ] minimum model tier/reasoning
- [ ] allowed/forbidden paths
- [ ] production-merge permission

## I3. Dynamic generation
Tasks can be generated from:
- [ ] readiness gaps
- [ ] failed tests
- [ ] audit findings
- [ ] research discoveries
- [ ] human decisions
- [ ] CIT effects
- [ ] lessons
- [ ] missing tools/skills
- [ ] retrieval failures
- [ ] security findings
- [ ] performance regressions

## I4. Parallel execution
- [ ] runnable/blocked sets
- [ ] critical path
- [ ] per-feature end-to-end path
- [ ] human-gate dependencies
- [ ] independent branches continue while one branch waits for human input

---

# GATE J — Research and Experimentation

## J1. Research becomes evidence
Each governed research output records:
- [ ] question/reason
- [ ] method
- [ ] sources/data
- [ ] measurements
- [ ] uncertainty
- [ ] conclusion
- [ ] confidence
- [ ] influenced decisions/tasks

## J2. Experiment lifecycle
- [ ] hypothesis/question
- [ ] method/data
- [ ] reproducibility
- [ ] results
- [ ] interpretation
- [ ] decision influence
- [ ] production merge prohibited where experimental

**Advanced qualification challenge:** unsupported research conclusion, irreproducible experiment, decision taken before required evidence, conflicting scientific reference data.

---

# GATE K — Change Control and Impact

## K1. CIT-P
- [ ] Proposed material change triggers deterministic graph traversal.
- [ ] Semantic/lexical/code candidates can supplement impact.
- [ ] Impact radius is produced.
- [ ] Human-readable consequences are surfaced.

## K2. CIT-E
- [ ] Final decision
- [ ] mutation manifest
- [ ] authoritative updates
- [ ] staleness/retest/rework propagation
- [ ] derived-view regeneration
- [ ] memory/index refresh
- [ ] verification
- [ ] commit or rollback/block atomically

## K3. Automatic impact simulation
Auto-trigger for material:
- [ ] architecture
- [ ] behaviour
- [ ] interfaces
- [ ] security
- [ ] governance/policy
- [ ] infrastructure cost
- [ ] acceptance criteria
- [ ] data migration

## K4. Impact radius
- [ ] R0-R5 or equivalent affects traversal/test scope/model tier/agents/human approval/rollback.

---

# GATE L — Human Decision Gates and Contradictions

## L1. Contradiction resolution
- [ ] deterministic precedence first
- [ ] low-impact/reversible/high-confidence agent resolution where allowed
- [ ] human escalation for consequential uncertainty
- [ ] rationale/evidence recorded

## L2. Human Decision Gate package
- [ ] plain-language question
- [ ] why now
- [ ] current state
- [ ] options
- [ ] impact
- [ ] reversibility
- [ ] cost/rework
- [ ] recommendation
- [ ] confidence
- [ ] exact permitted next actions

## L3. Gate presentation
- [ ] Gate in a file only is NOT presented.
- [ ] It must surface in active human interface.
- [ ] Presented ≠ answered.
- [ ] Declined/revoked/stale/other-CIT gates cannot authorise execution.
- [ ] Human approval cannot be fabricated by agent/CLI metadata.

## L4. Non-global blocking
- [ ] Independent runnable branches continue.
- [ ] Global stop only when policy or critical-path state requires.

---

# GATE M — Model Routing

## M1. T0-T3 or equivalent capability tiers
- [ ] deterministic/no-LLM route
- [ ] lightweight route
- [ ] strong engineering route
- [ ] frontier/high-reasoning route

## M2. Reasoning requirement
- [ ] low/medium/high/extra-high or equivalent minimum can be declared/enforced.

## M3. Role defaults
- [ ] orchestration/memory/audit default to strong enough tier.
- [ ] provider names are mapped externally without rewriting project state.

## M4. Empirical routing
Telemetry can compare:
- [ ] model/provider
- [ ] task class
- [ ] reasoning effort
- [ ] cost
- [ ] latency
- [ ] pass/fail
- [ ] repair count
- [ ] reviewer findings

---

# GATE N — Checkpoints, Compaction and Handoffs

## N1. Structured checkpoint
Records:
- [ ] session/role/task/mode/claim
- [ ] last completed step
- [ ] next action
- [ ] pending decisions/questions
- [ ] open transactions
- [ ] files changed
- [ ] test status
- [ ] context packet hash
- [ ] memory snapshot/state reference

## N2. Mandatory triggers
- [ ] task transition
- [ ] material decision
- [ ] accepted CIT
- [ ] significant mutation
- [ ] before handoff
- [ ] before model/provider switch
- [ ] before session close
- [ ] before known compaction

## N3. Provider-independent checkpoint watchdog
- [ ] Does not depend solely on proprietary hooks.
- [ ] Can mark checkpoint stale when material state changed.
- [ ] Handoff/session close can be blocked or degraded when checkpoint freshness violates policy.

## N4. Worker return contract
- [ ] structured result survives subagent conversation death.

---

# GATE O — Verification and Continuous Governance Health

## O1. Product test families
- [ ] unit
- [ ] contract
- [ ] integration
- [ ] system
- [ ] acceptance
- [ ] scenario
- [ ] security
- [ ] performance
- [ ] recovery
- [ ] live/smoke

## O2. Governance test families
- [ ] schema/invariants
- [ ] graph integrity
- [ ] index freshness
- [ ] retrieval regression
- [ ] authority/role limits
- [ ] mutation scope
- [ ] repository/path-map compliance
- [ ] context reproducibility
- [ ] concurrency/session claims
- [ ] adapter/model portability
- [ ] skill regression
- [ ] command-contract consistency
- [ ] secrets/sensitivity indexing
- [ ] recovery/rebuild
- [ ] fresh-agent reconstruction
- [ ] product traceability
- [ ] audit reproducibility

## O3. Independent test authorship
- [ ] Release-critical behavioural tests are authored independently of implementation.
- [ ] Builder tests remain regression evidence, not independent certification.
- [ ] Fresh verifier adds held-out tests.

## O4. Governance suite currency
- [ ] A green result becomes stale when relevant inputs change.
- [ ] Governance-affecting work cannot close on stale green evidence.

## O5. Governance Health Scheduler **[NEW EXECUTION REFINEMENT]**
Tiered checks:
- [ ] G0 Guard — every privileged/mutating command
- [ ] G1 Mutation — changed paths/schema/secrets/index invalidation
- [ ] G2 Task Close — mutation scope/readiness/tests/references/memory freshness
- [ ] G3 Checkpoint/Handoff — claims/decisions/gates/checkpoint freshness
- [ ] G4 Milestone — CIT-E/migration/memory/architecture changes
- [ ] G5 Full Suite — adopt/update/release/full audit
- [ ] G6 Qualification — synthetic repos/chaos/soak/hidden tests

Scheduler requirements:
- [ ] dependency-aware impacted-test selection
- [ ] independent checks run in parallel when safe
- [ ] isolated worktrees/processes where required
- [ ] cache keyed by relevant content/policy/framework hashes
- [ ] RED/YELLOW/GREEN or equivalent machine state
- [ ] hard-block vs warning semantics are explicit
- [ ] health result provenance is recorded

---

# GATE P — Observability and Telemetry

## P1. Execution telemetry
- [ ] agent/session/model/provider
- [ ] role/task
- [ ] skill/tool versions
- [ ] context packet
- [ ] retrieval queries/hits
- [ ] token input/output
- [ ] latency/cost
- [ ] files read/written
- [ ] tests
- [ ] retries/failures
- [ ] handoffs
- [ ] decisions
- [ ] human interventions

## P2. Organisational questions
Telemetry supports analysis of:
- [ ] rework by role
- [ ] retrieval effect on token use
- [ ] model over/under-power
- [ ] skill repair rate
- [ ] human-gate concentration
- [ ] retrieval misses
- [ ] cost by task/feature
- [ ] first-pass completion

---

# GATE Q — Learning, Lessons and Upstream Improvement

## Q1. Lesson lifecycle
- [ ] execution/report
- [ ] lesson candidate
- [ ] corroboration
- [ ] scope classification
- [ ] rule/skill/retrieval/tool proposal
- [ ] independent validation
- [ ] human approval where required
- [ ] governed version

## Q2. Decision vs lesson
- [ ] Lessons are evidence, not authority.
- [ ] Decisions record chosen action.

## Q3. PROJECT/PRODUCT/FRAMEWORK scope
- [ ] Only FRAMEWORK candidates are eligible for upstream export.

## Q4. Upstream Export Gate
- [ ] sanitisation
- [ ] secret/sensitivity scan
- [ ] outbound allowlist/default deny
- [ ] synthetic reproducer preference
- [ ] no raw project/customer/vector-store export

---

# GATE R — Legacy, Archive and Historical State

## R1. Legacy Governance Retirement
- [ ] activate current authority
- [ ] mark old governance LEGACY
- [ ] inventory
- [ ] extract useful decisions/lessons/skills/evidence/research
- [ ] reconcile contradictions
- [ ] retire/remove duplicate mechanisms
- [ ] verify no active dependency remains

## R2. Chat-memory retirement
- [ ] raw chat DB is not active/default truth
- [ ] unique durable knowledge extracted
- [ ] dependency proof before retirement
- [ ] CIT-E/index refresh/regression on retirement

## R3. Archive policy
- [ ] historical/superseded material excluded from default current retrieval
- [ ] Git history preferred over unnecessary dead-code archive
- [ ] deliberate reference implementations may be retained explicitly

---

# GATE S — Release, Distribution, Init, Adopt and Update

## S1. Canonical OS repo
- [ ] framework/runtime/CLI/tools/migrations/tests/fixtures/lessons/change-proposals/release/docs separation exists.
- [ ] canonical OS developed once, consumer repos do not rebuild it independently.

## S2. Immutable releases
- [ ] semantic versioning
- [ ] release manifest
- [ ] file hashes
- [ ] supported migrations
- [ ] schema versions
- [ ] CLI/runtime versions
- [ ] adapter/capability versions
- [ ] release notes
- [ ] affected indexes
- [ ] human decisions
- [ ] rollback

## S3. `gov init`
- [ ] certified kernel installation
- [ ] project overlay creation
- [ ] repository contract
- [ ] initial memory/state
- [ ] health checks
- [ ] reference retrieval profile bootstrap when certified

## S4. `gov adopt`
Stages are executable/evidenced:
- [ ] A0 safety baseline
- [ ] A1 cold inventory
- [ ] A2 classification
- [ ] A3 target path map
- [ ] A4 migration plan
- [ ] A5 independent migration review/test authoring
- [ ] A6 controlled migration
- [ ] A7 independent migration verification
- [ ] A8 legacy memory extraction/retirement
- [ ] A9 new Knowledge Fabric
- [ ] A10 independent memory verification
- [ ] A11 full project audit

## S5. `gov update`
- [ ] check/impact simulation
- [ ] authenticated source
- [ ] compatibility/migration
- [ ] preserve project overlay
- [ ] regenerate adapters/views
- [ ] rebuild affected indexes
- [ ] verify
- [ ] rollback
- [ ] ledger/provenance

## S6. Cross-machine mechanics
- [ ] tracked truth syncs through Git/private remote
- [ ] derived runtime rebuilds locally
- [ ] machine-specific absolute paths do not define release identity

---

# GATE T — Independent Adoption and Audit Roles

## T1. Role separation
- [ ] recovery agent
- [ ] adoption auditor/planner
- [ ] independent migration reviewer/test author
- [ ] migration executor
- [ ] independent migration verifier
- [ ] memory engineer
- [ ] independent memory verifier/test author
- [ ] comprehensive independent auditor
- [ ] operator/CTO

## T2. Fresh-session independence
- [ ] independent roles do not simply continue builder/executor context.
- [ ] held-out tests/evidence separation is enforced.

## T3. Adoption evidence tree
- [ ] inventory → classification → path map → migration plan → independent tests → migration → independent verification → memory → memory verification → full audit is traceable.

---

# GATE U — Framework Health SLOs

Track and threshold:
- [ ] governance-suite freshness
- [ ] product-test health
- [ ] retrieval Recall@K
- [ ] stale-index count
- [ ] orphan-graph count
- [ ] unresolved contradictions
- [ ] unresolved human gates
- [ ] task traceability %
- [ ] feature readiness coverage
- [ ] context packet size
- [ ] tokens/completed task
- [ ] first-pass completion
- [ ] handoff failure
- [ ] memory rebuild success
- [ ] fresh-agent reconstruction success

A repository is HEALTHY only when:
- [ ] authority unambiguous
- [ ] no accidental legacy authority
- [ ] deterministic state consistent
- [ ] graph/index freshness passes
- [ ] retrieval meets thresholds
- [ ] sensitive material isolated
- [ ] feature readiness explicit
- [ ] task runnable/blocked state correct
- [ ] tests/traceability satisfy policy
- [ ] governance suite current/green
- [ ] no unresolved critical audit finding
- [ ] fresh strong agent reconstructs state within budget
- [ ] derived memory is rebuildable

---

# GATE V — Qualification Oracle **[NEW TESTING REFINEMENT]**

The sophisticated qualification repositories must have a verifier-owned hidden oracle.

## V1. Fault manifest
Each injected defect records:
- [ ] fault ID
- [ ] class
- [ ] hidden authoritative truth
- [ ] injected repository state
- [ ] expected detection
- [ ] expected severity
- [ ] expected impacted artefacts/nodes
- [ ] expected governed action
- [ ] forbidden outcomes

## V2. Hidden path-map oracle
For brownfield Repo B:
- [ ] current artefact
- [ ] correct classification
- [ ] authority
- [ ] expected target path
- [ ] KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE
- [ ] expected references/consumers
- [ ] sensitivity/indexing expectation

## V3. Hidden memory oracle
- [ ] which material must be indexed
- [ ] which must never be indexed
- [ ] expected authority namespace
- [ ] expected current/superseded status
- [ ] expected graph relationships
- [ ] expected code symbols
- [ ] expected retrieval results

## V4. Quantitative qualification scoring
Report:
- [ ] injected defect detection recall
- [ ] false positives
- [ ] severity accuracy
- [ ] impact-map accuracy
- [ ] path-map accuracy
- [ ] missed authoritative artefacts
- [ ] wrong-indexing count
- [ ] stale-index count
- [ ] retrieval metrics
- [ ] recovery/chaos pass rate
- [ ] human-gate correctness
- [ ] task/readiness correctness

The permanent public qualification suite and fresh verifier hidden oracle must remain separate.

---

# GATE W — Artifact Flow, Dependency Consumption and End-to-End Traceability

## W1. Stable artefact identity
Every material output that may feed downstream work has:
- [ ] stable artefact ID
- [ ] artefact type
- [ ] canonical path
- [ ] authoritative status
- [ ] lifecycle state
- [ ] version/content hash
- [ ] producer/provenance
- [ ] supersedes/superseded-by lineage
- [ ] expected downstream consumers where known

Applies to specifications, scenarios, decisions, datasets, experiments, architecture records, interfaces, test designs, migration plans, audit findings, benchmark results and equivalent governed outputs.

## W2. Typed output → input contracts
- [ ] Upstream/downstream relationship type is explicit.
- [ ] Required vs optional dependency is explicit.
- [ ] Authority semantics are preserved across stages.
- [ ] Research evidence cannot silently become a decision.
- [ ] Lessons cannot silently become authoritative policy.
- [ ] Historical/retrieved material cannot replace current authoritative input.
- [ ] Output schemas define what downstream stages may consume.
- [ ] Relationships such as `EVIDENCE_FOR`, `CONSTRAINS`, `IMPLEMENTS`, `TESTS`, `GENERATES`, `VALIDATES`, `SUPERSEDES` or equivalent are machine-usable.

## W3. Mandatory task-input manifest
Every governed task that depends on upstream artefacts declares:
- [ ] required input IDs
- [ ] required authority/lifecycle state
- [ ] required version/hash constraints where applicable
- [ ] reason for each dependency
- [ ] supplementary/retrieved context separately from mandatory inputs

Rules:
- [ ] Task cannot become READY if a mandatory input is absent.
- [ ] Superseded input cannot silently satisfy a current requirement.
- [ ] Conflicting mandatory inputs trigger contradiction handling.
- [ ] Required inputs are resolved deterministically, not by semantic retrieval ranking.

## W4. Context compiler delivery proof
- [ ] Mandatory authoritative inputs are loaded deterministically into the task context packet.
- [ ] Required inputs are separated from supplementary semantic/lexical/graph/code retrieval.
- [ ] Required inputs cannot be displaced by context-ranking/token pressure without an explicit governed failure/degradation.
- [ ] Exact input IDs/versions/hashes are recorded in the context packet.
- [ ] Context packet hash/provenance proves what the worker was supplied.
- [ ] Missing required input causes refusal or explicit blocked state.

## W5. Consumption receipt and implementation traceability
Worker/task return records:
- [ ] exact required inputs supplied/consumed
- [ ] outputs produced
- [ ] requirements/features/scenarios implemented
- [ ] decisions/architecture constraints applied
- [ ] tests/acceptance evidence produced
- [ ] deviations/unknowns

Task close:
- [ ] refuses missing mandatory traceability where required
- [ ] detects undocumented/untraceable implementation
- [ ] links code/test/output evidence back to authoritative upstream inputs

## W6. Upstream-change staleness propagation
When an authoritative upstream artefact changes:
- [ ] dependent task evidence becomes stale as appropriate
- [ ] implementation/release/test evidence is invalidated according to impact
- [ ] affected context packets are invalidated
- [ ] graph/CIT computes impacted downstream nodes
- [ ] revalidation/rework tasks are generated
- [ ] `COMPLETE` does not imply permanently valid
- [ ] stale evidence cannot remain green merely because the original task closed successfully

## W7. Orphan/dead-output and unexplained-output detection
- [ ] Completed authoritative outputs with expected consumers but no actual consumer are detectable.
- [ ] Requirement/spec without downstream implementation/test path is detectable.
- [ ] Research expected to feed a decision but never consumed is visible.
- [ ] Acceptance test without requirement/scenario is visible.
- [ ] Implementation/code with no active requirement/decision/spec justification is detectable.
- [ ] Orphans produce governed investigation/remediation rather than silent deletion.

## W8. Forward and reverse lineage
Governance can answer:
- [ ] outcome/feature → scenario → requirement → decision → architecture → task → code → test → evidence → release
- [ ] reverse impact from changed requirement/decision/spec to affected implementation/tests/release evidence
- [ ] missing lineage link detection
- [ ] stale lineage link detection
- [ ] cross-language/cross-repository relationships where in scope

## W9. Session/handoff continuity of mandatory inputs
- [ ] Required-input manifest persists across session end.
- [ ] Checkpoint records input IDs/versions/hashes or equivalent state reference.
- [ ] Model/provider switch reconstructs the same authoritative task inputs.
- [ ] Fresh agent reconstructs mandatory inputs without prior chat.
- [ ] Compaction cannot silently remove mandatory project state.
- [ ] Handoff with stale/missing required-input state is blocked or explicitly degraded.

## W10. Deterministic mandatory inputs outrank retrieval
Hard invariant:
> Mandatory task inputs are resolved through authoritative structured dependency/state mechanisms before supplementary retrieval. Semantic/lexical/graph/code retrieval may enrich the task but may not substitute for a required authoritative input.

Verify:
- [ ] current spec is delivered even if absent from semantic index
- [ ] superseded but semantically similar spec cannot replace current required spec
- [ ] token pressure drops supplementary context before mandatory authoritative inputs
- [ ] retrieval/index outage does not erase deterministic required dependencies
- [ ] required-input delivery is independently testable

## W11. Artifact-flow quantitative health
Track where applicable:
- [ ] required-input delivery accuracy
- [ ] current-version selection accuracy
- [ ] superseded-input leakage rate
- [ ] missing-required-input detection
- [ ] staleness propagation accuracy
- [ ] requirement→code traceability coverage
- [ ] requirement→test traceability coverage
- [ ] orphan-output detection recall/false positives
- [ ] fresh-agent reconstruction correctness

## W12. Health-scheduler integration
- [ ] G0 blocks invalid authority/current-version substitution on privileged operations.
- [ ] G1 invalidates affected dependency/lineage evidence after material mutations.
- [ ] G2 verifies task input/consumption/traceability before task close.
- [ ] G3 verifies mandatory-input continuity across checkpoint/handoff.
- [ ] G4 runs wider staleness/impact propagation after CIT/spec/decision/architecture changes.
- [ ] G5 audits end-to-end lineage and orphan states.
- [ ] G6 injects hidden artifact-flow failures in sophisticated qualification.

**Advanced qualification challenge:** intentionally omit current specs from semantic index, index superseded specs with higher semantic similarity, change specs after implementation, move files while retaining stable IDs, omit task dependency declarations, return code without consumption receipts, create contradictory mandatory inputs, induce context pressure, switch model/session, and create orphan authoritative outputs. The hidden oracle defines the correct required input/version and expected downstream propagation.


# PRE-ADVANCED-QUALIFICATION ACCEPTANCE GATE

Before sophisticated synthetic repositories are executed, require:

1. [ ] Every original constitutional capability above has a status and evidence location.
2. [ ] No `ABSENT` or `UNCLEAR` item remains for a required capability.
3. [ ] Any `PARTIAL` item has an explicit justification and cannot undermine the qualification scenario.
4. [ ] All post-verification trust hardening relevant to the release is incorporated.
5. [ ] Governance Health Scheduler G0-G6 is implemented enough to observe the qualification work.
6. [ ] Qualification Oracle format is accepted before generating hidden faults.
7. [ ] A provisional retrieval profile is available so sophisticated qualification is not run on intentionally inadequate semantic retrieval.
8. [ ] Artifact Flow & Consumption Integrity (Gate W) has executable evidence and dedicated advanced-qualification challenges.
9. [ ] The exact candidate commit/hash is frozen for qualification.

Gate result:

`GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`

Only then may the advanced qualification repositories be executed.

---

# PROPOSED ORDER AFTER THIS CHECKLIST IS ACCEPTED

```text
Prompt 2 core verification/repair
  ↓
OS_RELEASE_CANDIDATE_ACCEPTED
  ↓
Capability Acceptance Checklist audit
  ↓
GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED
  ↓
Provisional retrieval bootstrap
  ↓
PROVISIONAL_RETRIEVAL_PROFILE_READY
  ↓
Generate two sophisticated qualification repos + hidden oracle
  ↓
Advanced qualification
  ↓
ADVANCED_QUALIFICATION_ACCEPTED
  ↓
Final Qwen/BGE/other retrieval bake-off using those repos
  ↓
REFERENCE_RETRIEVAL_PROFILE_SELECTED
  ↓
Package + fresh clean-install integration verification
  ↓
REFERENCE_RETRIEVAL_PROFILE_ACCEPTED
  ↓
Prompt 3 final certification
  ↓
Private remote publication + remote-clone smoke
  ↓
PRIVATE_REMOTE_RELEASE_READY
  ↓
Product A / Product B adoption
```
