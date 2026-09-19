# P2-HO-0025 — Repair iteration 1, round 2: WS-6

| Field | Value |
|---|---|
| Handoff | P2-HO-0025 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0027** |
| Workstream | WS-6 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws06/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0027.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-28 (graph integrity: stale, reversed, ill-typed edges detected), BC-P2-30 (retrieval-profile identity and change governance), BC-P2-31 (non-rebuildable state not classified as derived).

## Files you own this round

`runtime/src/memory/**` except `claims.rs`; `runtime/src/retrieval/**`; `runtime/src/code_intelligence/**`; `runtime/src/paths.rs`; `runtime/src/security/**`; `runtime/src/records.rs` (record-text/chunk region); `framework/policies/{MEMORY_POLICY (except failure_memory keys),SECURITY_POLICY,ARCHIVE_POLICY}.yaml`; `framework/overlay-templates/{REPOSITORY_CONTRACT,DATA_SENSITIVITY}.yaml`; `framework/schemas/{index-manifest,memory-manifest,repository-contract,data-sensitivity,heldout-tests}.schema.json`; `capabilities/python/govos_capabilities/code_intel_*`.

## Integration points routed to you

- from **ws03** (§9): IP-8 (`memory select` derives `human_approved` only from `gates::human_approval_for`).
- from **ws04** (§7): IP-12 (BC-P2-28 uses `Record::edges()`/`graph::canonical_of`), IP-13 (benchmark result records carry `content_hash`/`version`).
- from **ws06** (your own §8): IP-7 is WS-9's; nothing else routed back.
- **BC-P2-31:** claims, emergency-control state and the plugin registry must not live where the product classifies state as throwaway/derived (the synthesis corrected B1/B3 on this: deleting them lost claims and lifted FREEZE_WRITES). Coordinate locations with the owners by API: claims store (WS-5), control state (WS-3), plugin registry (WS-7) — you own the *classification* (repository contract / paths), they own their writers; record IPs for any writer move.
- **BC-P2-30:** a profile change needs benchmark evidence, regression and an authenticated gate (use WS-3's gate APIs); runtime/model artefact identity bound into the pin (A0-D4-01, A0-D5-01, A0-D5-02). Link to CIT-P materiality (WS-4 BC-P2-13) by recording the IP for round 3.

## Notes

Language adapters stay resolved via the capability registry (D-0002/ARCH-0001).
