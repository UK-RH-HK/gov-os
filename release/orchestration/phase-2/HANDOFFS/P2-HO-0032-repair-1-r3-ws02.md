# P2-HO-0032 — Repair iteration 1, round 3: WS-2

| Field | Value |
|---|---|
| Handoff | P2-HO-0032 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0033** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws02/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0033.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

BC-P2-07 (tier duties at every trigger, incl. G1 on every material mutation however made, and G6 observing qualification runs), BC-P2-23 (Gate W W11 artifact-flow metrics), BC-P2-44 (every Gate U SLO computed, thresholded and observed; one HEALTHY verdict = the thirteen conditions of Contract v3:995-1008), and the **availability rule** on the scheduler side (catalogue semantics: block scope, remedy operations, non-global blocking).

## Files you own this round

`runtime/src/verification/**`; `runtime/src/doctor.rs`; `runtime/src/observability.rs`; `runtime/src/skills.rs`; `runtime/src/scheduler/**`; `runtime/src/error.rs` (exit-code mapping); `framework/policies/TEST_POLICY.yaml`; `framework/health/**`; `framework/schemas/audit.schema.json`.

## Items routed to you

- Availability: WS-3 r2 IP-R2-2; WS-5 r2 O-R2-1, O-R2-2; WS-4 r2 R2-9 (the decision whether a critical block may refuse *proposing* a repairing CIT); WS-8 r2 IP-R2-WS08-5 (update entry guard). Design the block-scope and remedy semantics once, in the catalogue, and give hosts one API.
- WS-6 r2 IP-R2-1 (`graph_integrity` and D015 call `memory::integrity::check`), IP-R2-3 (`profile::status` in audit/doctor; D025 runtime drift), IP-R2-5 (index manifest in currency — confirm), IP-R2-12 (sandbox, currency key and doctor use the real store paths after BC-P2-31 moves; report misplaced state).
- WS-4 r2 R2-7 (doctor/audit over freshness, bindings, contradictions, detect), R2-8 (G4 results recorded as audit records), R2-9 (above), and flip SKL-IMPACT-ANALYSIS V1 to executable (IP-WS02-20).
- WS-10 r2 IP-WS10-06 (family `research_experiment_data_lifecycle` via `lifecycle::suite_findings`), IP-WS10-07 (SKL-RESEARCH-BENCHMARK V1 executable — precondition met).
- WS-9 r2 IP-R2-4 (T2-unbound `00-BASELINE.yaml` is an adoption-integrity finding).
- WS-8 r2 IP-R2-WS08-2/3 (admission/authenticity in doctor and audit), IP-R2-WS08-4 (installed records in `machine_trust`), IP-R2-WS08-8 (G6 qualification only on provisioned machines, OWNER-DECISION-P2-0002 item 4).
- WS-5 r2 IP-R3-7 (map `GATE_NOT_AUTHORISED` and the other blocked-class codes to exit 4, API-0002).
- **Secret-like literal (WS-8 r2 IP-R2-WS08-6):** `framework/health/SKILL_SCENARIO_CHECKS.yaml` carries a planted `AKIA…EXAMPLE` literal that the kernel's own scanner flags when installed. Keep the scenario's meaning without a scannable literal in a kernel file (e.g. construct the probe value at run time).
- WS-2 r2 own R3-4 (coverage checker's heading-line false gaps — coordinate: the checker is WS-6's; keep your confirmation step until WS-6 fixes it), R3-8 (= BC-23, BC-44 above), R3-11 (sealed plugin-registry entries in `t2::audit` — `t2.rs` is WS-3's; consume their API).
- From the **round-2 integration report** (`release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`):
  **IF-1** (integration regression routed to you) — a WS-5 closing receipt lists inherited requirements in
  `inputs_consumed` (→ `CONSUMES` edges), and the W7 lineage counts a `CONSUMES` edge as an implementation path, so a
  requirement the receipt declares *not implemented* is no longer reported as a delivery gap (your line W7.2b). Decide
  BC-P2-22's semantics for "reaches a requirement" from Contract v3 W7/W5 (consumption ≠ implementation) and fix it;
  **O-1** — a W7 remediation subject later deleted leaves a dangling `AFFECTS` edge, DEGRADES the suite and refuses
  governance closes until a CIT repairs the generated task: apply the availability rule (a generated investigation task
  whose subject is gone must be closable/withdrawn without deadlock); **O-5** — the planted literal (above) also sits in a
  test project's embedded-kernel cache.
- IP-WS02-11 (optional; `TEST_POLICY` governance-affecting task classes).
