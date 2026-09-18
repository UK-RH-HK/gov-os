# P2-HO-0004 — Iteration-0 capability family audit: `delta`

| Field | Value |
|---|---|
| Handoff | P2-HO-0004 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0004** |
| Candidate | `cap2-candidate-0` (see common protocol for the pinned identities) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` under `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Family | `delta` |
| Capabilities owned | J (J1–J2), K (K1–K4), L (L1–L4), M (M1–M4), N (N1–N4) — research/experimentation, change control and impact, Human Decision Gates and contradictions, model routing, checkpoints/compaction/handoffs |
| Owner-source location | Contract v3 lines 594–747 (Gates J, K, L, M, N) |
| Evidence directory | `release/capability-baseline/audit-0/delta/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0004.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full.** It defines who you
are, the standard you apply, the output schemas and the prohibitions. This handoff only scopes your family.

## Your capabilities

J (J1–J2), K (K1–K4), L (L1–L4), M (M1–M4), N (N1–N4) — research/experimentation, change control and impact, Human Decision Gates and contradictions, model routing, checkpoints/compaction/handoffs. Establish the exact capability and bullet set yourself from the owner source at the lines above — not from the
compiled YAML or the evidence map, which are derived views (frozen contract §1). If you find that a derived view omits
or distorts anything in your scope, that is itself a finding.

## Governing-document trace

framework Part XII §§45–46, Part XIII §§47–49, Part XIV §§50–54, Part XV §§55–58, Part XVI §§59–61; CIT-0001.

## Where the implementation starts (orientation only — find the rest yourself)

`runtime/src/cit/`, `graph/`, `orchestration/gates.rs`, `orchestration/handoffs.rs`, `orchestration/tasks.rs`, `routing.rs`, `checkpoints.rs`, `observability.rs`, `records.rs`, `status.rs`; `framework/policies/` (CHANGE, HUMAN_GATE, MODEL_ROUTING, CHECKPOINT policies), `framework/adapters/`; `spec/research/`; `tests/certification/`.

These are starting points, not conclusions. A module's existence says nothing about whether a bullet is met.

## Family-specific duties

- **L3** — *"Gate in a file only is NOT presented"*, *"must surface in active human interface"*, *"Presented ≠ answered"*,
  *"Declined/revoked/stale/other-CIT gates cannot authorise execution"*, *"Human approval cannot be fabricated by agent/CLI
  metadata"*. Attack each: try to execute a CIT with a declined, revoked, stale and other-CIT gate; try to fabricate
  approval through CLI flags, environment, role claims and record edits.
- **N3** checkpoint watchdog must not depend solely on proprietary hooks; establish what actually marks a checkpoint stale
  and what blocks/degrades a handoff.
- **M4** empirical routing: establish whether telemetry can actually compare the eight listed dimensions from recorded data.
- **K4** — the contract's K4 *impact radius R0–R5* is unrelated to the Signed Release Root's R0–R3 assurance gates; do
  not conflate them.
- Cross-capability interactions you own (AC-16): K2 ↔ W6 (CIT-E staleness/retest propagation), N ↔ W9 (checkpoint
  mandatory-input continuity), L3 ↔ E1 (gate presentation/authority) — exercise the K/N/L side.

## Five other families are auditing in parallel

Other fresh auditors own the other gates. Do not audit their capabilities, and do not read their evidence directories
(they are on other branches and are not merged). A separate fresh synthesis auditor assembles all six families, checks the
cross-cutting criteria (AC-9, AC-10, AC-11, AC-13, AC-14, AC-15, AC-16) and issues the Phase-2 verdict.
