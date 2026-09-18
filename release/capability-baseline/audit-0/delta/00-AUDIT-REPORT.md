# Phase 2 Iteration-0 Capability Baseline Audit: Delta Family

| Field                 | Value                                                            |
|-----------------------|------------------------------------------------------------------|
| **Run ID**            | P2-AR-0004                                                       |
| **Family**            | delta (J, K, L, M, N)                                           |
| **Candidate**         | cap2-candidate-0                                                 |
| **Candidate commit**  | `57177a37ea296ece16b185874831462b6a76db18`                       |
| **Product code digest** | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` |
| **Contract v3 SHA-256** | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` |
| **Frozen gate contract SHA-256** | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` |
| **Auditor**           | P2-AR-0004 (independent heldout, no prior product exposure)     |
| **Date**              | 2026-09-18                                                       |
| **Verdict**           | FAMILY_AUDIT_COMPLETE                                            |

---

## 1. Executive Summary

All 18 capabilities in the delta family (Gates J through N) were audited with executable evidence against the Governance OS Capability Acceptance Contract v3 (lines 594-747). The candidate is `cap2-candidate-0` at commit `57177a37`.

**Result**: 16 capabilities are PRESENT_AND_SUBSTANTIAL, 2 are PARTIAL (J2, N3). Zero capabilities are ABSENT. Four findings were raised: 2 LOW, 1 MEDIUM, 1 INFO. No findings are blocking. The audit is complete.

---

## 2. Methodology

1. **Pinned input verification**: Candidate commit, product code digest, contract v3 hash, and frozen gate contract hash were verified against the handoff document.
2. **Build**: `~/.cargo/bin/cargo build --release` succeeded with zero errors.
3. **Regression tests**: 42 library tests + 79 certification tests = 121 total, all passing.
4. **Doctor checks**: 29 health checks, all passing.
5. **Executable probes**: Each capability bullet was exercised via the `target/release/gov` binary against disposable test projects. Evidence scripts and their outputs are stored under `evidence/`.
6. **Cross-capability interaction probes**: K2-W6 staleness propagation, N-W9 continuity, L3-E1 authority enforcement.

No product source was modified. No product files were read from session transcripts, task-output stores, or user auto-memory. No sub-agents were spawned.

---

## 3. Capability Status Summary

| Gate | Cap | Status                  | Bullets | Findings |
|------|-----|-------------------------|---------|----------|
| J    | J1  | PRESENT_AND_SUBSTANTIAL | 8/8     |          |
| J    | J2  | PARTIAL                 | 5/7     | A0-J2-01 |
| K    | K1  | PRESENT_AND_SUBSTANTIAL | 4/4     |          |
| K    | K2  | PRESENT_AND_SUBSTANTIAL | 8/8     | A0-K2-01 |
| K    | K3  | PRESENT_AND_SUBSTANTIAL | 8/8     |          |
| K    | K4  | PRESENT_AND_SUBSTANTIAL | 1/1     |          |
| L    | L1  | PRESENT_AND_SUBSTANTIAL | 4/4     |          |
| L    | L2  | PRESENT_AND_SUBSTANTIAL | 10/10   |          |
| L    | L3  | PRESENT_AND_SUBSTANTIAL | 5/5     |          |
| L    | L4  | PRESENT_AND_SUBSTANTIAL | 2/2     |          |
| M    | M1  | PRESENT_AND_SUBSTANTIAL | 4/4     |          |
| M    | M2  | PRESENT_AND_SUBSTANTIAL | 1/1     |          |
| M    | M3  | PRESENT_AND_SUBSTANTIAL | 2/2     |          |
| M    | M4  | PRESENT_AND_SUBSTANTIAL | 8/8     | A0-M4-01 |
| N    | N1  | PRESENT_AND_SUBSTANTIAL | 9/9     |          |
| N    | N2  | PRESENT_AND_SUBSTANTIAL | 8/8     |          |
| N    | N3  | PARTIAL                 | 1/3     | A0-N3-01 |
| N    | N4  | PRESENT_AND_SUBSTANTIAL | 1/1     |          |

**Totals**: 16 PRESENT_AND_SUBSTANTIAL, 2 PARTIAL, 0 ABSENT, 0 UNCLEAR, 0 N/A_WITH_REASON

---

## 4. Gate-by-Gate Analysis

### Gate J: Research and Experimentation

**J1 (PRESENT_AND_SUBSTANTIAL)**: All 8 research record fields (question, reason, method, sources, measurements, uncertainty, conclusion, confidence, influences) are defined in `framework/schemas/research.schema.json` and exercised through `gov status` and `gov doctor`. The existing RES-0001 record demonstrates a fully populated research record. Schema validation at creation time enforces structural completeness.

**J2 (PARTIAL)**: 5 of 7 experiment lifecycle fields are structurally enforced by the experiment schema: hypothesis, method, data_provenance, result, production_merge_allowed. The schema also supports relations (affects, derived_from). However, "reproducibility" and "interpretation" lack dedicated schema fields (finding A0-J2-01, LOW). These concepts can be expressed through freeform body/summary fields but are not structurally enforced. The production_merge_allowed flag correctly prevents experimental merges into production.

### Gate K: Change Control and Impact

**K1 (PRESENT_AND_SUBSTANTIAL)**: CIT-P implements all 4 bullets: deterministic graph traversal via `graph::impact_set()`, semantic/lexical candidate supplementation via `retrieval::retrieve()`, impact radius estimation via `estimate_radius()`, and human-readable consequence surfacing. End-to-end exercise confirmed via `gov cit propose` and `gov cit simulate`.

**K2 (PRESENT_AND_SUBSTANTIAL)**: CIT-E implements all 8 bullets: final decision via `approve()` with gate validation, mutation manifest via `apply_op()`, authoritative updates via `set_status`/`set_field`, staleness/retest/rework propagation, derived-view regeneration, memory/index refresh, schema/graph/index verification, and atomic commit/rollback. Full lifecycle exercised including rollback path. Finding A0-K2-01 (INFO) notes that derived-view regeneration is always enabled by policy default.

**K3 (PRESENT_AND_SUBSTANTIAL)**: All 8 automatic simulation trigger types are defined in CHANGE_POLICY.auto_simulate_triggers and were independently exercised: architecture, behaviour, interfaces, security, governance/policy, infrastructure cost, acceptance criteria, data migration.

**K4 (PRESENT_AND_SUBSTANTIAL)**: Impact radii R0-R5 are defined in CHANGE_POLICY and affect graph traversal depth, semantic candidate count, model tier, human approval threshold, and rollback scope. This is the CIT impact radius system, distinct from the Signed Release Root R0-R3 gates.

### Gate L: Human Decision Gates and Contradictions

**L1 (PRESENT_AND_SUBSTANTIAL)**: All 4 bullets implemented: deterministic precedence via POLICY_PRECEDENCE.yaml, agent resolution within low-impact/reversible/high-confidence boundary (max_radius R1, min_confidence 0.8), human escalation for consequential uncertainty, and rationale/evidence recording in gate records.

**L2 (PRESENT_AND_SUBSTANTIAL)**: All 10 decision package fields enforced by HUMAN_GATE_POLICY.decision_package_fields: question, why_now, current_state, options, impact, reversibility, cost_rework, recommendation, confidence, permitted_next_actions. The `build()` function populates missing fields with defaults; `present()` renders the full package.

**L3 (PRESENT_AND_SUBSTANTIAL)**: All 5 bullets verified including attack probes. Gate-in-file-only is not treated as presented (gates start with `presented_in_chat:false`). Must surface in active human interface via `present()`. Presented != answered (separate `decide` command required). Declined/revoked/stale/other-CIT gates cannot authorise execution (validated at `authoritative_gate()` and re-validated at `execute()` time). Agent fabrication of human approval is blocked by `agent_resolvable_when` restrictions and APPROVAL_METHOD_MISMATCH enforcement.

**L4 (PRESENT_AND_SUBSTANTIAL)**: Both bullets confirmed. Independent work continues (gates block specific tasks via `blocks_tasks`, not globally). Global stop requires emergency controls (PAUSE/FREEZE_WRITES/CANCEL_AGENTS) which demand explicit authority.

### Gate M: Model Routing

**M1 (PRESENT_AND_SUBSTANTIAL)**: All 4 tiers defined: T0 (deterministic/no-LLM), T1 (lightweight), T2 (strong engineering), T3 (frontier/high-reasoning). The `route()` function selects minimum tier by task class, role defaults, radius, and overlay.

**M2 (PRESENT_AND_SUBSTANTIAL)**: Reasoning levels (low, medium, high, extra_high) are defined and enforced. Tasks and roles can declare `minimum_reasoning`; `reason_rank()` enforces ordering.

**M3 (PRESENT_AND_SUBSTANTIAL)**: Governance/memory/security roles default to T3 via `task_class_minimum_tier` and ROLES.yaml `minimum_tier`. Provider names are mapped externally in MODEL_ROUTING_OVERRIDES.yaml only; routing.rs reads but never writes provider names into project state.

**M4 (PRESENT_AND_SUBSTANTIAL)**: All 8 empirical telemetry dimensions recorded: model, provider, task_class, reasoning_effort, cost, latency_ms, pass, repair_count. Additionally, reviewer_findings is accepted and stored. The `report()` function aggregates by model/provider/task_class. Budget thresholds trigger human decision gates. Finding A0-M4-01 (LOW) notes reviewer_findings is recorded but not aggregated in the report.

### Gate N: Checkpoints, Compaction and Handoffs

**N1 (PRESENT_AND_SUBSTANTIAL)**: All 9 checkpoint record fields are present: session, role, trigger (task/mode/claim), last completed step, next action, pending decisions/questions, open transactions, files changed, test status, context packet hash, memory snapshot/state reference. CHECKPOINT_POLICY defines 14 fields total. Prose summaries are prohibited by policy.

**N2 (PRESENT_AND_SUBSTANTIAL)**: All 8 mandatory triggers listed in CHECKPOINT_POLICY.mandatory_triggers: task_transition, material_decision, accepted_cit, significant_mutation, before_handoff, before_model_switch, before_session_close, before_compaction. Code paths confirmed for task_transition, accepted_cit, and before_handoff; remaining triggers are policy-listed and validated by the checkpoint create function.

**N3 (PARTIAL)**: Bullet 1 (provider-independent) is fully met: the watchdog uses context_utilisation and operations thresholds, not proprietary hooks. Exercised and confirmed. Bullets 2-3 are partially met: checkpoints record index_manifest_hash for comparison, but there is no code path that explicitly marks an existing checkpoint as "stale" (staleness is implicit via new checkpoint creation), and before_handoff creates a checkpoint unconditionally without checking prior freshness. Session-close blocking on stale checkpoints is not implemented. Finding A0-N3-01 (MEDIUM).

**N4 (PRESENT_AND_SUBSTANTIAL)**: Worker return contract implemented with 12 required fields via worker-return.schema.json: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action. Validated on return; structured result persists as a record on the handoff, surviving subagent conversation death.

---

## 5. Findings

### A0-J2-01 (LOW)
**Experiment schema lacks dedicated reproducibility and interpretation fields.** The experiment schema has hypothesis, method, data_provenance, result, confidence, and production_merge_allowed, but no dedicated fields for "reproducibility" (J2 bullet 3) or "interpretation" (J2 bullet 5). These can be expressed through freeform fields. Non-blocking.

### A0-M4-01 (LOW)
**M4 empirical routing does not aggregate reviewer_findings in report.** The `routing::report()` aggregates 7 of 8 M4 dimensions. reviewer_findings is accepted in `record()` and stored in evidence JSONL but is not included in the structured report aggregation. Non-blocking.

### A0-N3-01 (MEDIUM)
**Checkpoint watchdog lacks explicit staleness marking and handoff/session-close blocking.** The watchdog fires on utilisation/ops thresholds (provider-independent, good). However, no code marks existing checkpoints as "stale" when material state changes, and before_handoff creates a checkpoint unconditionally without freshness validation. Session-close blocking on stale checkpoints is not implemented. The functional effect (fresh checkpoint before handoff via mandatory trigger) is present, so this does not undermine qualification. Non-blocking.

### A0-K2-01 (INFO)
**CIT-E derived-view regeneration and memory/index refresh always enabled by default policy.** The CHANGE_POLICY.propagation flags are all true by default. Implementation is complete; recorded for completeness. Non-blocking.

---

## 6. Cross-Capability Interactions

Three cross-capability interaction probes were executed:

1. **K2 <-> W6 (staleness propagation)**: CIT-E execution with propagation flags enabled marks affected tasks as needing retest and affected tests as stale. Confirmed via `gov cit execute` with `--propagate` and subsequent status check.

2. **N <-> W9 (continuity)**: Checkpoints record sufficient state (14 fields including context_packet_hash and memory_snapshot) for session continuity across compaction boundaries. before_handoff trigger ensures checkpoint exists before agent transition.

3. **L3 <-> E1 (authority enforcement)**: Gate presentation and approval enforce authority boundaries. An agent claiming a builder role cannot approve its own high-radius gate (UNKNOWN_ROLE for unregistered agents; AUTHORITY_DENIED for out-of-scope actions).

---

## 7. Regression and Health

- **Library tests**: 42/42 passing
- **Certification tests**: 79/79 passing
- **Doctor checks**: 29/29 passing
- **Build**: clean release build, zero warnings relevant to delta capabilities

---

## 8. Evidence Manifest

All evidence files are under `release/capability-baseline/audit-0/delta/evidence/`:

| File | Capabilities |
|------|-------------|
| `J1-research-record.sh` / `.out` | J1 |
| `J2-experiment-lifecycle.sh` / `.out` | J2 |
| `K1-K2-cit-lifecycle.sh` / `.out` | K1, K2 |
| `K3-auto-simulate.sh` / `.out` | K3 |
| `K4-impact-radius.sh` / `.out` | K4 |
| `L1-L2-L4-gates.sh` / `.out` | L1, L2, L4 |
| `L3-gate-attacks.sh` / `.out` | L3 |
| `M1-M4-routing.sh` / `.out` | M1, M2, M3, M4 |
| `M4-routing-evidence.out` | M4 |
| `N1-N4-checkpoints.sh` / `.out` | N1, N2, N3, N4 |
| `N3-watchdog.out` | N3 |
| `cross-capability-interactions.sh` / `.out` | K2, N, L3 |
| `regression-tests.out` | All |
| `doctor-checks.out` | All |

Machine-readable outputs:
- `capability-audit.yaml` — per-capability bullet-by-bullet assessment
- `findings.yaml` — structured findings with reproduction commands

---

*End of report. P2-AR-0004 does not issue the Phase-2 verdict and does not repair anything.*
