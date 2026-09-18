# P2-HO-0013 — Repair iteration 1, round 1: WS-3

| Field | Value |
|---|---|
| Handoff | P2-HO-0013 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0016** |
| Workstream | WS-3 |
| Classes | BC-P2-08, BC-P2-09, BC-P2-10, BC-P2-12 (answer side), BC-P2-18 (resolution rules), BC-P2-45, BC-P2-49 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws03/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0016.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/authority.rs`; `runtime/src/project.rs`; `runtime/src/orchestration/control.rs`; `runtime/src/orchestration/gates.rs`; `runtime/src/policy.rs`; `runtime/src/policy_precedence.rs`; `runtime/src/policy_coverage.rs`; `runtime/src/routing.rs`; `cli/src/main.rs` (semantic owner); `framework/policies/{AUTHORITY_POLICY,HUMAN_GATE_POLICY,POLICY_PRECEDENCE,MODEL_ROUTING_POLICY,ENFORCEMENT_MAP}.yaml`; `framework/schemas/{human-gate,decision,model-routing-overrides,roles}.schema.json`; `framework/roles/**`; `framework/overlay-templates/MODEL_ROUTING_OVERRIDES.yaml`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-08** role resolution applied consistently on every command (init/adopt call sites are owned by WS-8/WS-9: expose
  the resolution API and record the integration points); no declared role ⇒ no privileged authority; every mutating
  command has an authority class; nothing mutates under FREEZE_WRITES/PAUSE outside an explicit recovery allow-list.
- **BC-P2-09** the **T2 binding primitive**: a T2 fact (gate presentation/answer, decision, CIT state, plugin registration)
  is honoured only when it provably results from the OS operation; lower-trust writes to OS-written state are detectable.
  Other workstreams will consume this primitive (close side WS-5, registry WS-7, CIT WS-4) — make its API explicit.
- **BC-P2-10** human answers, human-approval assertions and presentation evidence come from a channel the acting agent
  cannot operate through CLI arguments, environment, role claims, defaults, repository files, plugins or model output.
  The **authority class is determined** by the accepted sources (owner-controlled local/out-of-band authority anchored
  in the administrator-provisioned boundary — OWNER-DECISION-0006 req. 2, ARCH-0003 §5/§8, D-0007 rule 2,
  OWNER-DIRECTIVE-0004); the concrete mechanism is yours, graded later. The R1 break-glass authorisation
  (`srr/breakglass.rs`, owner-signed token against the provisioned root's `recovery` role, machine-protected inbox) is the
  owner-accepted precedent for this class — **read it; reuse its primitives through their public API rather than editing
  `srr/**`** (owned by WS-8). The verifier will attack it from an agent process with the operator's OS privileges.
  **Out of scope: OD-P2-01** (OS binding of *agent* L0–L4 identity) — do not implement agent credentials.
- **BC-P2-12** answer side of task-blocking gate semantics (the DAG side is WS-5, later round).
- **BC-P2-18** contradiction resolution rules (detection in context/readiness is WS-4, later round): agent resolution only
  within policy, on assessed impact/reversibility/confidence not resting solely on the resolver's own declaration.
- **BC-P2-45** every project overlay (routing overrides, readiness switches, any key) goes through POLICY_PRECEDENCE; floors
  may be raised, never lowered; refusals are reported (readiness read site in `dag.rs` is WS-5: record the point).
- **BC-P2-49** the Human Decision Gate package is enforced (every field substantive, ≥1 option, answer ∈ options, exact
  permitted next actions).

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
