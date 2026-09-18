# P2-HO-0005 — Iteration-0 capability family audit: `epsilon`

| Field | Value |
|---|---|
| Handoff | P2-HO-0005 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0005** |
| Candidate | `cap2-candidate-0` (see common protocol for the pinned identities) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` under `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Family | `epsilon` |
| Capabilities owned | O (O1–O5), P (P1–P2), Q (Q1–Q4), U (Framework Health SLOs — no numbered heading; audit it as capability `U`), V (V1–V4) — verification and the Governance Health Scheduler, observability/telemetry, learning/upstream improvement, framework health SLOs, qualification oracle |
| Owner-source location | Contract v3 lines 749–866 (Gates O, P, Q) and 976–1062 (Gates U, V) |
| Evidence directory | `release/capability-baseline/audit-0/epsilon/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0005.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0000-audit-0-common-protocol.md` in full.** It defines who you
are, the standard you apply, the output schemas and the prohibitions. This handoff only scopes your family.

## Your capabilities

O (O1–O5), P (P1–P2), Q (Q1–Q4), U (Framework Health SLOs — no numbered heading; audit it as capability `U`), V (V1–V4) — verification and the Governance Health Scheduler, observability/telemetry, learning/upstream improvement, framework health SLOs, qualification oracle. Establish the exact capability and bullet set yourself from the owner source at the lines above — not from the
compiled YAML or the evidence map, which are derived views (frozen contract §1). If you find that a derived view omits
or distorts anything in your scope, that is itself a finding.

## Governing-document trace

framework Part XVII §§62–64, Part XVIII §§65–66, Part XIX §§67–68, Part XXIII §§75–76, Part XXIV; Release/Distribution protocol §§13–15 (upstream learning, export gate, lesson intake), §7 (synthetic certification projects); decision D-0004.

## Where the implementation starts (orientation only — find the rest yourself)

`runtime/src/verification/` (governance suite families), `doctor.rs`, `observability.rs`, `lessons.rs`, `upstream.rs`, `memory/heldout.rs`, `status.rs`, `orchestration/`; `framework/policies/` (TEST, LEARNING policies); `lessons/`, `change-proposals/`; `fixtures/` (all seven, incl. `failure-injection`, `upstream-learning`); `tests/certification/`.

These are starting points, not conclusions. A module's existence says nothing about whether a bullet is met.

## Family-specific duties

- **AC-5 — Health-scheduler audit.** This is yours in full. Exercise the G0–G6 scheduler (O5) as behaviour, not as
  vocabulary: impacted-test selection from a real mutation; parallel execution of independent checks; isolation; cache
  reuse and cache invalidation keyed by content/policy/framework hashes; stale evidence; RED/YELLOW/GREEN (or equivalent)
  aggregation; hard-block vs warning semantics; health-result provenance; remediation/task generation. Establish whether a
  trivial mutation re-runs the whole suite serially. Record an explicit AC-5 determination in `00-AUDIT-REPORT.md`.
- **AC-6 — Qualification Oracle format.** Determine whether a machine-checkable oracle format covering V1 (fault manifest),
  V2 (hidden path-map oracle), V3 (hidden memory oracle) and V4 (quantitative scoring) exists on this candidate. If one
  exists, you are a fresh independent reviewer: record `QUALIFICATION_ORACLE_FORMAT_ACCEPTED` or `_REJECTED` against V1–V4
  with reasons. If none exists, record `QUALIFICATION_ORACLE_FORMAT_ABSENT`. You do **not** generate any hidden fault.
- **O3** (independent test authorship) and **O4** (suite currency) are about the product's own mechanisms for consumer
  projects; establish what the OS enforces, not how Phase 2 is run.
- **U** — the SLO list and the thirteen HEALTHY conditions are each a bullet.
- Cross-capability interactions you own (AC-16): U ↔ O5 (health SLOs observed by the scheduler), O4 ↔ W6 (staleness).

## Five other families are auditing in parallel

Other fresh auditors own the other gates. Do not audit their capabilities, and do not read their evidence directories
(they are on other branches and are not merged). A separate fresh synthesis auditor assembles all six families, checks the
cross-cutting criteria (AC-9, AC-10, AC-11, AC-13, AC-14, AC-15, AC-16) and issues the Phase-2 verdict.
