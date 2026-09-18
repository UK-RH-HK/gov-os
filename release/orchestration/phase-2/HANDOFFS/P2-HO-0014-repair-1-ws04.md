# P2-HO-0014 — Repair iteration 1, round 1: WS-4 (part)

| Field | Value |
|---|---|
| Handoff | P2-HO-0014 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0017** |
| Workstream | WS-4 (part) |
| Classes | BC-P2-21 (records side), BC-P2-17, BC-P2-19, BC-P2-20 (contract and lineage side) |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws04/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0017.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/cit/**`; `runtime/src/graph/**`; `runtime/src/context/**`; `runtime/src/checkpoints.rs`; `runtime/src/orchestration/handoffs.rs`; `runtime/src/records.rs` (relation fields/edges region only); `framework/policies/{CHANGE_POLICY,CHECKPOINT_POLICY,CONTEXT_POLICY}.yaml`; `framework/schemas/{cit,checkpoint,context-packet,handoff,record,requirement,feature,interface}.schema.json`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-21** stable artefact identity for every W1 artefact type with provenance and lineage, and relation edges in
  the right direction (migration-plan/catalogue identity is WS-9's side).
- **BC-P2-17** mandatory task-input manifest semantics (W3): required IDs, required authority/lifecycle state,
  version/hash constraints, reason per dependency, supplementary context separate; deterministic resolution; superseded
  input cannot satisfy a current requirement. (READY-state derivation is WS-5 later: expose the check and record the point.)
- **BC-P2-19** context-packet delivery (W4/W10): mandatory authoritative inputs loaded deterministically with exact
  IDs/versions/hashes, separated from retrieval, never displaced by token pressure without a governed failure, packet hash
  proving what was supplied, missing input ⇒ refusal/blocked, and **retrieval/index outage must not withhold
  deterministic inputs**.
- **BC-P2-20** consumption receipt and implementation traceability — the receipt contract and lineage edges (close-side
  validation lives in `tasks.rs`, WS-5: expose the validator and record the integration point).
- Classes BC-P2-04, -05, -11, -13 are **round 2** for your workstream; do not start them.

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
