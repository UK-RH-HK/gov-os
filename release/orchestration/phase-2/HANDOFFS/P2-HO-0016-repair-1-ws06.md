# P2-HO-0016 — Repair iteration 1, round 1: WS-6 (part)

| Field | Value |
|---|---|
| Handoff | P2-HO-0016 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0019** |
| Workstream | WS-6 (part) |
| Classes | BC-P2-25, BC-P2-26, BC-P2-27, BC-P2-29, BC-P2-32 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws06/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0019.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/memory/**` except `claims.rs`; `runtime/src/retrieval/**`; `runtime/src/code_intelligence/**`; `runtime/src/paths.rs`; `runtime/src/security/**`; `runtime/src/records.rs` (record-text/chunk region only); `framework/policies/{MEMORY_POLICY,SECURITY_POLICY,ARCHIVE_POLICY}.yaml`; `framework/overlay-templates/{REPOSITORY_CONTRACT,DATA_SENSITIVITY}.yaml`; `framework/schemas/{index-manifest,memory-manifest,repository-contract,data-sensitivity,heldout-tests}.schema.json`; `capabilities/python/govos_capabilities/code_intel_*`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-25** index content coverage and chunk granularity (list/nested record fields, module-level code, methods as units).
- **BC-P2-26** retrieval filtering before candidate cut (namespace/authority/role exclusion before anything reaches a
  reranker plugin), routing (bare filenames), de-duplication, graph answers not buried by fusion.
- **BC-P2-27** code-structure extraction (routes, DB models, inheritance, test-coverage edges) through language adapters
  resolved via the capability registry.
- **BC-P2-29** incremental index invalidation (path-map reclassification applied incrementally; stale edges owned by
  unchanged files; CIT-E refresh uses current policy).
- **BC-P2-32** failure memory durable (retrieval misses, tool failures and the other C8 facets leave durable records).
- **Round 2 for you:** BC-P2-28 (graph integrity — needs WS-4's edge direction), BC-P2-30 (retrieval-profile identity and
  change governance — needs WS-4 CIT-P and context), BC-P2-31 (non-rebuildable state classified as derived — with WS-3/7).

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
