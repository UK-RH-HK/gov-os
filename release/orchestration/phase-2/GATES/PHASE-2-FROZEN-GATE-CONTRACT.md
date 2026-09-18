# Phase 2 — frozen gate contract for `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`

| Field | Value |
|---|---|
| Gate | `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Target token | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` |
| Rejection token | `GOVERNANCE_CAPABILITY_BASELINE_REJECTED` |
| Frozen by | Phase-2 outer orchestrator at Phase-2 initialisation, 2026-09-18, **before** any Phase-2 audit was dispatched |
| Nature | A **compilation** of already-normative text plus procedure. It adds no product requirement. Where two normative sources need reconciling, the reconciliation is logged in §9 as an orchestrator interpretation that the product owner may override. |
| Change control | Frozen. Any change is a new, separately hashed revision recorded in the Phase-2 ledger **before** the next verification it affects. A reviewer, verifier or builder cannot amend it. |

## 1. Normative sources and precedence

Precedence follows the V8.2 launcher's authoritative order. Where V8.2 text conflicts with a higher source, the higher source wins
and the conflict is logged.

| # | Source | Identity |
|---|---|---|
| 1 | Original governing documents: `DYNAMIC_AGENTIC_SOFTWARE_ENGINEERING_OPERATING_FRAMEWORK_v4.1.2.md`, `GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md`, `GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md` | repository root |
| 2 | Owner-supplied **Capability Acceptance Contract v3**: `Governance_OS_Capability_Acceptance_Contract_v3.md` | SHA-256 `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| 3 | Its hash-bound canonical/executable views: `framework/contracts/source/…_v3.md`, `framework/contracts/governance-capability-acceptance.yaml`, `framework/contracts/contract-source.lock`, `tests/governance/capability-evidence-map.yaml`, `docs/generated/GOVERNANCE_CAPABILITY_ACCEPTANCE.md` | verified `CONTRACT_SOURCE_BOUND` by `gov contract verify` at Phase-2 entry |
| 4 | Active owner decisions/directives and accepted architecture: D-0002…D-0007, D-0009, CIT-0001, ARCH-0001, ARCH-0003 (owner-adopted, `OWNER-DECISION-0009`), OWNER-DIRECTIVE-0004, OWNER-DECISION-0005…0009 | `spec/`, `release/orchestration/phase-1/GATES/` |
| 5 | Frozen lifecycle contracts: the Signed Release Root boundary (`release/root-of-trust/signed-release-root-v1/01-FROZEN-R0-R1-R2-R3-ACCEPTANCE-BOUNDARY.md`, SHA-256 `70977d11…99c1`) and **this** document for Phase 2 | — |
| 6 | Exact candidate and evidence state | this phase's candidates and evidence |
| 7 | V8.2 operator UI, `NON_NORMATIVE_OPERATOR_UI` — its CAP-1 role prompt is a workflow template only | SHA-256 `6fecfb6b…8269c` |

The **owner source (row 2) defines the audit universe.** The compiled YAML, the evidence map and the generated view are
derived views; a reviewer establishes the universe from the owner source text and reconciles the derived views against it,
never the reverse.

## 2. The acceptance items (verbatim, Contract v3 lines 1197–1215)

> Before sophisticated synthetic repositories are executed, require:
>
> 1. Every original constitutional capability above has a status and evidence location.
> 2. No `ABSENT` or `UNCLEAR` item remains for a required capability.
> 3. Any `PARTIAL` item has an explicit justification and cannot undermine the qualification scenario.
> 4. All post-verification trust hardening relevant to the release is incorporated.
> 5. Governance Health Scheduler G0-G6 is implemented enough to observe the qualification work.
> 6. Qualification Oracle format is accepted before generating hidden faults.
> 7. A provisional retrieval profile is available so sophisticated qualification is not run on intentionally inadequate semantic retrieval.
> 8. Artifact Flow & Consumption Integrity (Gate W) has executable evidence and dedicated advanced-qualification challenges.
> 9. The exact candidate commit/hash is frozen for qualification.
>
> Gate result: `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`

Also normative for how a status may be earned (Contract v3):

- line 93: *"A capability may not be reported `PRESENT_AND_SUBSTANTIAL` solely because a file/schema/policy exists."*
- lines 81–91: each item maps to one or more evidence classes — automated invariant/guard; unit/integration/system test;
  governance health check; independent held-out test; migration/rollback evidence; synthetic-repository evidence;
  human-gate evidence; clean-clone/release evidence; independent audit evidence.
- lines 95–111: evidence freshness — a green capability becomes `STALE` when a relevant input changes, and stale evidence
  must trigger re-check before work relies on it.
- lines 53–73: required contract fields per capability.
- lines 37–49: contract authority model — *"Any semantic difference between source and compiled representation is a hard failure."*
- O3 (lines 782–785): builder tests are regression evidence, not independent certification; a fresh verifier adds held-out tests.

## 3. Acceptance criteria

`GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` is issued only when **every** criterion below holds for one exact frozen
candidate. Each criterion cites the text it compiles.

| AC | Criterion | Compiles |
|---|---|---|
| AC-1 | Every capability in the owner source has a recorded status from §4 and an evidence location. | item 1 |
| AC-2 | No required capability is `ABSENT` or `UNCLEAR`. "Required" means every capability unless recorded `N/A_WITH_REASON` under §4, where the reason cites the exact normative text that places the obligation outside Phase 2. | item 2 |
| AC-3 | Every `PARTIAL` capability carries an explicit justification **and** an argued statement of why it cannot undermine the advanced-qualification scenario. A `PARTIAL` whose gap could invalidate qualification fails AC-3. | item 3; V8.2 CAP-1 acceptance rule |
| AC-4 | The `POST_VERIFICATION_HARDENING` capabilities (A2, F4) relevant to the release are incorporated, and the R1 acceptance they rest on is still valid for the candidate (AC-14). | item 4 |
| AC-5 | The G0–G6 Governance Health Scheduler is implemented enough to observe qualification work, established by exercising it, not by reading it: impacted-test selection; parallel execution of independent checks; safe isolation; cache reuse; cache invalidation; stale evidence; RED/YELLOW/GREEN aggregation; hard-block vs warning semantics; health-result provenance; remediation/task generation; and it does **not** serially run the whole suite for every trivial mutation. | item 5; O5; V8.2 CAP-1 "Health scheduler audit" |
| AC-6 | A Qualification Oracle **format** covering V1–V4 exists as a machine-checkable definition and is accepted by a fresh independent reviewer in this phase. No hidden fault is generated in Phase 2. | item 6; Gate V |
| AC-7 | Item 7 as interpreted in §9.1. | item 7 |
| AC-8 | Gate W has executable evidence and dedicated advanced-qualification challenges, shown by an **Artifact Flow Coverage Matrix**: producer artefact → stable ID/version → relationship type → downstream consumer/task → mandatory/optional → task input manifest → context-packet evidence → consumption receipt → output traceability → invalidation trigger → qualification challenge. Fails if semantic retrieval is relied on to rediscover mandatory inputs, if stale versions can silently satisfy downstream work, or if completion cannot be traced to upstream evidence. | item 8; Gate W; V8.2 "Gate W baseline audit" |
| AC-9 | The exact candidate is frozen: commit, tag, `product_code_digest` and `governed_state_digest` (`release/orchestration/phase-2/tools/product_identity.py`). | item 9 |
| AC-10 | **Suite-to-contract matrix**: every required capability has at least one evidence owner (G0 guard, G1 mutation, G2 task-close, G3 checkpoint/handoff, G4 milestone, G5 full suite, G6 qualification, independent held-out verification, Human Decision Gate evidence, release/clean-clone evidence). No required capability has zero evidence owners. Changing a relevant implementation/policy/spec/tool/model/index/path-map input is shown to invalidate prior green evidence rather than leave it green. | lines 75–111; V8.2 CAP-1 "Suite-to-contract audit" |
| AC-11 | **Qualification Coverage Matrix**: every applicable capability maps to a Repo A challenge, a Repo B challenge, a hidden-oracle fault class, and chaos/scale/soak and retrieval challenges where relevant. A capability not meaningfully challengeable in the synthetic repositories states why and names another independent evidence route. | V8.2 CAP-1 "Pre-qualification coverage plan"; Contract v3 per-capability "advanced-qualification challenge IDs" field |
| AC-12 | Evidence relied on is fresh for the exact candidate and independent wherever independence is required; builder evidence counts as regression evidence only. | lines 95–111; O3; O4 |
| AC-13 | The contract-binding chain is intact and semantically faithful: canonical import byte-identical to the owner source; compiled form, lock, evidence map and generated view carry no semantic difference from the owner source. | lines 37–49 |
| AC-14 | **R1 preservation.** If the candidate's `product_code_digest` differs from `srr1-r1-accepted` (`bd4d65d9…0547`), a fresh independent verifier re-runs every prior R1 held-out suite (`release/verification/4.1.6-r1*/evidence/heldout-tests/`) unedited and confirms the twelve frozen R1 items still hold for every changed area, before or within the verification that grades the candidate. | V8.2 CAP-1: *"Any source/kernel/runtime repair after rejection creates a new candidate and requires R1 verification again before this audit is rerun"*, applied under Contract v3 evidence freshness (§9.3) |
| AC-15 | Regression is green on the candidate: `cargo test --lib` and `cargo test --test certification`, zero failures. | O1; O3 |
| AC-16 | Cross-capability interactions the contract states are exercised, at minimum: W12 (Gate W ↔ G0–G6); O4/W6 (staleness ↔ scheduler); K2 ↔ D1 ↔ W6 (CIT-E ↔ index freshness ↔ staleness propagation); N ↔ W9 (checkpoint ↔ mandatory-input continuity); L3 ↔ E1 (gate presentation ↔ authority); S3/S4/S5 ↔ A2 (lifecycle ingress ↔ root of trust); U ↔ O5 (health SLOs ↔ scheduler). | lines 1185–1192 and each named capability |

## 4. Status vocabulary

Contract v3 names `PRESENT_AND_SUBSTANTIAL`, `PARTIAL`, `ABSENT` and `UNCLEAR` (lines 93, 1202–1203); V8.2 CAP-1 adds
`N/A_WITH_REASON`, consistent with H2's rule that silent N/A is invalid.

| Status | Meaning |
|---|---|
| `PRESENT_AND_SUBSTANTIAL` | Every checklist bullet of the capability is implemented and **executably evidenced** on the exact candidate. |
| `PARTIAL` | Some bullets are executably evidenced and some are not; requires AC-3 justification. |
| `ABSENT` | The capability's behaviour is not implemented. |
| `UNCLEAR` | The reviewer cannot establish the status from executable evidence. Blocks like `ABSENT`. |
| `N/A_WITH_REASON` | Not applicable to the Governance OS product at this lifecycle, with the exact normative text that says so. Never silent. |

**Granularity.** Phase 2 is exhaustive, not a sample. Every checklist bullet of every capability is evaluated individually and
the capability status is derived from its bullets. A capability is `PRESENT_AND_SUBSTANTIAL` only if all its applicable
bullets are.

## 5. Per-capability record

For every capability a reviewer records at minimum: governing source (file:line in the owner source and the originating
governing-document section); requirement class (`ORIGINAL` / `POST_VERIFICATION_HARDENING` / `EXECUTION_REFINEMENT`);
bullet-by-bullet status; implementation evidence (file:line); automated suite/check evidence (test IDs, commands);
independent evidence (what the reviewer ran); current freshness; health-scheduler tier(s); advanced-qualification
challenge(s); adoption/post-adoption obligation; residual risk. (Contract v3 lines 53–73; V8.2 CAP-1.)

## 6. Findings

Every finding states: exact normative source and clause; provenance class (the frozen boundary's classes:
`ORIGINAL-NORMATIVE`, `OWNER-ADDED-NORMATIVE`, `NECESSARY-DERIVED`, `IMPLEMENTATION-CHOICE`, `VERIFIER-HARDENING`,
`NEW-OWNER-DECISION-REQUIRED`, `LATER-QUALIFICATION/CERTIFICATION`, `OUT-OF-SCOPE / UNSATISFIABLE-AS-STATED`);
lifecycle/gate (`P2`, `P3`, `P4`, `R2`, `R3`, adoption, operations); whether it **falsifies** a Phase-2 requirement or
**proposes stronger later assurance**; severity (`CRITICAL`/`HIGH`/`MEDIUM`/`LOW`/`INFO`); reproducible evidence;
`owner_decision_required` with the reason; **blocker class** and **residual-vs-materially-new** (§8).

A finding blocks this gate only if its normative source and lifecycle are Phase 2 — i.e. it leaves an AC unmet — or it
falsifies an explicit Phase-2 claim. Stronger-assurance ideas are recorded as recommendations, not blockers.

## 7. Outside this gate (never Phase-2 blockers unless Contract v3 explicitly places them here)

- R2 standard release certification: production signatures/key custody, key ceremony, SBOM/licences/provenance, private-remote publication, rotation/revocation drill (frozen boundary §R2). The `PHASE-1-RESIDUAL-RISKS.md` register is R2 input.
- R3 high-assurance qualification in full.
- Phase 3 selection of the provisional retrieval profile itself (see §9.1); Phase 4 generation and execution of the synthetic qualification repositories and hidden faults; Phase 5 reference retrieval bake-off.
- Public/multi-tenant cloud assurance.
- The open D-0007 explicit transition record (not requested by the owner).

## 8. Iteration, classes and convergence

- The iteration-0 exhaustive audit establishes the **blocker-class inventory**. A class is identified by the capability
  ID(s) it concerns plus its defect mechanism.
- A later finding is a **residual** if it lies in an inventoried class — the same capability and the same mechanism,
  including an incomplete fix. It is **materially new** if it concerns a capability or mechanism absent from the
  inventory, including any regression a repair introduced into a previously held capability. The reviewer labels it with
  reasons; the orchestrator checks the label and never relabels to avoid escalation.
- If **three consecutive** verification iterations each introduce materially new blocker classes, the orchestrator stops
  with `PHASE_CONVERGENCE_ESCALATION_REQUIRED` and produces a root-cause/meta-review package (owner Phase-2 directive).

## 9. Logged interpretations (orchestrator; owner may override)

### 9.1 Item 7 — provisional retrieval profile

Contract v3 lists item 7 in the gate whose result is this token, while its own **PROPOSED ORDER** (lines 1219–1255) places
*"Provisional retrieval bootstrap ↓ PROVISIONAL_RETRIEVAL_PROFILE_READY"* **after** `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`
and before qualification repositories are generated. V8.2's Phase 3 card (owner-supplied) likewise requires this token
*before* the provisional profile is established. Item 7's stated purpose is *"so sophisticated qualification is not run on
intentionally inadequate semantic retrieval"*.

Reconciliation, preserving both texts: at this gate, item 7 holds when the candidate provides an **executable, evidenced
path** to establish a provisional retrieval profile — pluggable, separately identifiable embedder/reranker/runtime
components (D4), the benchmark/compare/select/pin mechanism with golden or held-out queries and metrics (D5), and a
reindex/migration route on profile change — so that Phase 3 can earn `PROVISIONAL_RETRIEVAL_PROFILE_READY`. Selecting the
profile is Phase 3's token, and advanced qualification (Phase 4) may not execute until it exists, which is what item 7
protects. This is derivable from accepted sources, so it is not raised as an owner gate.

### 9.2 Item 6 — who accepts the oracle format

Contract v3 does not name the acceptor. The format is accepted by a fresh independent reviewer against V1–V4, recorded in
this phase's evidence, before any hidden fault exists. The format is a Phase-2 artefact; hidden faults are Phase 4.

### 9.3 R1 re-verification after repair

V8.2 CAP-1 says a source repair after rejection *"requires R1 verification again before this audit is rerun"*. Contract v3's
evidence-freshness rule governs *what* is invalidated. AC-14 applies both: an independent R1-preservation verification
runs on every candidate whose product code differs from `srr1-r1-accepted`, re-running all prior R1 held-out suites and
re-establishing the frozen R1 items for changed areas, before or within the Phase-2 verification of that candidate. It
does not re-issue `ROT_PHASE1_CANDIDATE_ACCEPTED_R1`; it records whether that acceptance remains valid for the new candidate.

### 9.4 Gate U

Gate U (Framework Health SLOs) carries checklist items but no numbered `## U<n>.` heading. It is still a capability section
of the owner source and is inside the audit universe (§1).

## 10. Independence (V8.2; frozen boundary)

- Auditors, independent test authors and verifiers run fresh, in isolated worktrees, and never modify product source.
- A builder or repair role never grades its own work and never sees held-out tests before that verifier's verdict is committed.
- The acceptance verdict comes only from a fresh independent role. The orchestrator routes and adjudicates provenance; it
  never substitutes its own judgement for required independent evidence.
- No role reads session/agent transcripts, task-output stores or user auto-memory.
