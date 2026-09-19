# P2-HO-0034 — Repair iteration 1, round 3: WS-4

| Field | Value |
|---|---|
| Handoff | P2-HO-0034 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0035** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws04/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0035.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

sealing and lineage completeness for CIT/context/records, the product-release record type, BC-P2-31 CIT snapshot move, and the round-3 IPs routed to you.

## Files you own this round

`runtime/src/cit/**`; `runtime/src/graph/**`; `runtime/src/context/**`; `runtime/src/checkpoints.rs`; `runtime/src/orchestration/handoffs.rs`; `runtime/src/records.rs` (relation fields/edges, `TYPE_DIR`/`TYPE_PREFIX`); `runtime/src/lib.rs` (`INDEX_VERSION` only); `framework/policies/{CHANGE_POLICY,CHECKPOINT_POLICY,CONTEXT_POLICY}.yaml`; the cit/checkpoint/context-packet/handoff/record/requirement/feature/interface schemas.

## Items routed to you

- WS-5 r2 IP-R3-1 (re-seal task records rewritten by CITs), IP-R3-2 (seal every CIT write — then WS-3 adds `cit` to `SEALED_RECORD_TYPES`), IP-R3-3 (re-seal reports/test obligations the OS writes, or record the path in the CIT's touched list), IP-R3-4 (producer rule into `manifest::resolve`), IP-R3-5 (UNTRACEABLE_IMPLEMENTATION only when implementation was produced), IP-R3-6 (CIT coverage by content hash — API complete for WS-5).
- WS-2 r2 R3-1 (CIT rollback re-seals the approval decision it marks REJECTED), R3-2 (`stale_links` drops a completed CIT's own targets), R3-3 (`evidence_refs` as a relation edge).
- WS-10 r2 IP-WS10-08 (`data_requirements`, `test_data`, `realises` relation fields), IP-WS10-09 (experiment promotions checked at CIT approve/execute), IP-WS10-10 (non-governed evidence flagged in the context manifest).
- WS-6 r2 IP-R2-2 (CIT-E graph-integrity verification uses `memory::integrity::check`), IP-R2-6 (a retrieval-profile change is material for CIT-P), IP-R2-10 (CIT snapshots to the BC-P2-31 store path).
- WS-8 r2 IP-R2-WS08-7 (product-release record type and relation fields; WS-3 adds the command).
- Apply the availability rule (common protocol) at your host sites.
