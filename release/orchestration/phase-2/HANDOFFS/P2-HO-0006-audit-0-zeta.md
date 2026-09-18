# P2-HO-0006 — Iteration-0 capability family audit: `zeta`

| Field | Value |
|---|---|
| Handoff | P2-HO-0006 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0006** |
| Candidate | `cap2-candidate-0` (see common protocol for the pinned identities) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` under `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Family | `zeta` |
| Capabilities owned | W (W1–W12) — Artifact Flow, Dependency Consumption and End-to-End Traceability |
| Owner-source location | Contract v3 lines 1066–1194 (Gate W, including the W10 hard invariant and the Gate W advanced-qualification challenge) |
| Evidence directory | `release/capability-baseline/audit-0/zeta/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0006.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full.** It defines who you
are, the standard you apply, the output schemas and the prohibitions. This handoff only scopes your family.

## Your capabilities

W (W1–W12) — Artifact Flow, Dependency Consumption and End-to-End Traceability. Establish the exact capability and bullet set yourself from the owner source at the lines above — not from the
compiled YAML or the evidence map, which are derived views (frozen contract §1). If you find that a derived view omits
or distorts anything in your scope, that is itself a finding.

## Governing-document trace

framework §§15 (context packet), 36–39 (SPEC, readiness, scenarios), 41–44 (task system), 47–49 (change control), 59–61 (checkpoints, return contract); Contract v3 C9, H1, I2, K2, N1, O5 for the interactions W12 names.

## Where the implementation starts (orientation only — find the rest yourself)

`runtime/src/context/` (context compiler), `orchestration/tasks.rs`, `orchestration/dag.rs`, `orchestration/handoffs.rs`, `records.rs`, `graph/`, `cit/`, `checkpoints.rs`, `verification/`, `memory/` (retrieval vs deterministic inputs), `schemas.rs`; `framework/schemas/` (context-packet, handoff, checkpoint and task-related schemas); `tests/certification/`.

These are starting points, not conclusions. A module's existence says nothing about whether a bullet is met.

## Family-specific duties

- **AC-8 — Artifact Flow Coverage Matrix.** Yours in full. Produce `artifact-flow-coverage-matrix.yaml` in your evidence
  directory with one row per governed artefact type the contract names in W1 (specifications, scenarios, decisions,
  datasets, experiments, architecture records, interfaces, test designs, migration plans, audit findings, benchmark
  results and equivalents): producer artefact → stable ID/version → relationship type → downstream consumer/task →
  mandatory/optional → task input manifest → context-packet evidence → consumption receipt → output traceability →
  invalidation trigger → qualification challenge. Mark each cell with the executable evidence that proves it or `GAP`.
  Record an explicit AC-8 determination against its three rejection conditions (semantic retrieval relied on to rediscover
  mandatory inputs; stale versions silently satisfying downstream work; completion not traceable to upstream evidence).
- **W10 hard invariant** — verify each of its five bullets by construction: remove the current spec from the semantic
  index and confirm it is still delivered; index a superseded spec with higher similarity and confirm it cannot replace
  the current one; apply token pressure and confirm supplementary context drops first; simulate an index outage; confirm
  required-input delivery is independently testable.
- **W12** maps Gate W onto G0–G6 — exercise each tier's Gate-W duty.
- Cross-capability interactions you own (AC-16): W12 ↔ O5, W6 ↔ K2/D1/O4, W9 ↔ N — exercise the W side.

## Five other families are auditing in parallel

Other fresh auditors own the other gates. Do not audit their capabilities, and do not read their evidence directories
(they are on other branches and are not merged). A separate fresh synthesis auditor assembles all six families, checks the
cross-cutting criteria (AC-9, AC-10, AC-11, AC-13, AC-14, AC-15, AC-16) and issues the Phase-2 verdict.
