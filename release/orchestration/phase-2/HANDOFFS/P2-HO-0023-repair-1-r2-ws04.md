# P2-HO-0023 — Repair iteration 1, round 2: WS-4

| Field | Value |
|---|---|
| Handoff | P2-HO-0023 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0025** |
| Workstream | WS-4 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws04/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0025.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-04 (upstream changes invalidate completed work, its evidence and context packets), BC-P2-05 (checkpoint triggers, staleness, handoff blocking), BC-P2-11 (CIT side: approval bound to content, impact and CIT), BC-P2-13 (CIT-P side: materiality not self-labelled; material changes reach impact simulation), BC-P2-18 (detection side: contradictions in mandatory inputs detected and routed).

## Files you own this round

`runtime/src/cit/**`; `runtime/src/graph/**`; `runtime/src/context/**`; `runtime/src/checkpoints.rs`; `runtime/src/orchestration/handoffs.rs`; `runtime/src/records.rs` (relation fields/edges, `TYPE_DIR`/`TYPE_PREFIX`); `runtime/src/lib.rs` (`INDEX_VERSION` constant only); `framework/policies/{CHANGE_POLICY,CHECKPOINT_POLICY,CONTEXT_POLICY}.yaml`; `framework/schemas/{cit,checkpoint,context-packet,handoff,record,requirement,feature,interface}.schema.json`.

## Integration points routed to you

- from **ws02** (§6): IP-WS02-05 (scheduler guard at CIT propose/approve/execute), IP-WS02-06 (G4 `tier_run` after CIT execute), IP-WS02-07 (G3 at checkpoint and handoff create; guard at handoff create).
- from **ws03** (§9): IP-4 (CIT reads answers only via `gates::verified_answer`; CIT gates via `create_system`; seal CIT state; undecidable contradictions → a `contradiction` system gate).
- from **ws05** (§5): IP-1 (task contract enforcement in the context packet), IP-3 (CIT execution records per touched path the hash it wrote, so in-window CIT coverage binds content — expose the API; WS-5 consumes it in round 3).
- from **ws06** (§8): IP-5 (`failure` record type `FAIL`, `spec/reports/failures`; `spec/reports/memory-quality/` canonical for retrieval-miss records).
- from **ws09-11**: IP-5 (`migration-plan` type at `spec/audits/GOVERNANCE-ADOPTION`, prefix `MPLAN`).
- from **ws04** (your own §7): IP-17 (`INDEX_VERSION` bump — edge derivation changed).
- **BC-P2-13 split:** you own the materiality classifier and CIT-P triggering; expose `cit::materiality(...)`-style detection that WS-5 will call at task close in round 3 (record the IP).

## Notes

Classes BC-P2-04/05 must also make the round-1 `context` packets and receipts stale when their inputs change.
