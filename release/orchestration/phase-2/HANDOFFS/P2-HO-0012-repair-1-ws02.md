# P2-HO-0012 — Repair iteration 1, round 1: WS-2 (part)

| Field | Value |
|---|---|
| Handoff | P2-HO-0012 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0015** |
| Workstream | WS-2 (part) |
| Classes | BC-P2-03, BC-P2-06, BC-P2-42, BC-P2-43 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws02/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0015.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/verification/**`; `runtime/src/doctor.rs`; `runtime/src/observability.rs`; `runtime/src/skills.rs`; a new scheduler module; `framework/policies/TEST_POLICY.yaml`; `framework/schemas/audit.schema.json`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-03** green-evidence currency key covers every Contract v3:97-109 input class relevant to the evidence
  (including non-decision spec, source files, index manifest, registries, research/experiment/checkpoint/handoff records,
  adoption evidence, machine trust state and the runtime implementation identity) and staleness is enforced.
- **BC-P2-06** the G0-G6 health scheduler mechanics: dependency-aware impacted selection, concurrent independent checks,
  isolation of state-mutating checks, cache keyed by the BC-P2-03 key, declared hard-block vs warning with the governed
  operations actually refused, persisted health-result provenance; a trivial mutation does not re-run the whole suite
  serially. Define the **tier contract** (the API each host calls at its trigger) — the host call sites (task close, CIT,
  checkpoint/handoff, update/release, adopt) are wired in later rounds by their owners; record each as an integration point.
- **BC-P2-42** skill regression actually executes validation scenarios; a skill version identifies its content.
- **BC-P2-43** per-family product-test results are governed, freshness-bound evidence; failures change health and are
  verified from recorded evidence at close (close itself lives in `tasks.rs`, WS-5 — expose the verification API and
  record the integration point).

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
