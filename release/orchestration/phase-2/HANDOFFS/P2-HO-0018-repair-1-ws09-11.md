# P2-HO-0018 — Repair iteration 1, round 1: WS-9 (part) + WS-11

| Field | Value |
|---|---|
| Handoff | P2-HO-0018 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0021** |
| Workstream | WS-9 (part) + WS-11 |
| Classes | BC-P2-33, BC-P2-52, BC-P2-21 (catalogue/plan identity side), BC-P2-50 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws09-11/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0021.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/adopt.rs`; `runtime/src/migrations/**`; `framework/schemas/{migration,migration-catalogue-entry,adoption-baseline}.schema.json`; `migrations/**`; `runtime/src/upstream.rs`; `runtime/src/lessons.rs`; `framework/policies/LEARNING_POLICY.yaml`; `framework/schemas/{upstream-packet,lesson,framework-change-proposal}.schema.json`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-33** legacy identification, extraction and retirement (no re-archiving the OS's own generated adapter; stable
  artefact IDs across adoption re-runs; dependency proof before retirement — no live code rewired to archived material;
  extraction not limited to cue words).
- **BC-P2-52** the path map represents document citations.
- **BC-P2-21 (catalogue side)** migration plans and audit findings get stable identity; the migration ledger's artefact IDs
  match the catalogue.
- **BC-P2-50** the upstream export gate fails closed on content (no raw project source, index vectors or customer data in
  "synthetic" fixtures). Export *approval* from the authenticated human channel is BC-P2-10 (WS-3): expose the hook and
  record the integration point.
- **Round 2 for you:** BC-P2-34 (independence self-attested — adoption part; depends on WS-3 BC-P2-08) and the adopt call
  sites for BC-P2-08 and the G5 tier hook.

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
