# P2-HO-0036 — Repair iteration 1, round 3: WS-6

| Field | Value |
|---|---|
| Handoff | P2-HO-0036 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0037** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws06/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0037.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

BC-P2-31 completion (classification + template rules), index freshness correctness, and the round-3 IPs routed to you.

## Files you own this round

`runtime/src/memory/**` except `claims.rs`; `runtime/src/retrieval/**`; `runtime/src/code_intelligence/**`; `runtime/src/paths.rs`; `runtime/src/security/**`; `runtime/src/records.rs` (record-text/chunk region); `framework/policies/{MEMORY_POLICY (except failure_memory keys),SECURITY_POLICY,ARCHIVE_POLICY}.yaml`; `framework/overlay-templates/{REPOSITORY_CONTRACT,DATA_SENSITIVITY}.yaml`; the index-manifest/memory-manifest/repository-contract/data-sensitivity/heldout-tests schemas; `capabilities/python/govos_capabilities/code_intel_*`.

## Items routed to you

- WS-4 r2 R2-10 (pre-existing: memory freshness treats files the indexer skips — over 2 MB or duplicate id — as unindexed forever, so every CIT-E fails verification), R2-11 (observe boundaries at index rebuild).
- WS-2 r2 R3-4 (coverage checker reports held Markdown heading lines as gaps).
- WS-7 r2 IP-W7-2 (record a degradation when a code_intel plugin is refused; today a tampered adapter falls back silently).
- WS-10 r2 IP-WS10-03/04 (backlinks from `memory select` and `memory benchmark`), IP-WS10-05 (hold non-governed evidence reference-only in the indexer).
- WS-9 r2 IP-R2-2 (`REPOSITORY_CONTRACT` template rule for `spec/reports/memory-quality/**`) and your own r2 observation that the template's rule order makes every `spec/` file authoritative so the `evidence` class never applies; WS-6 r2 IP-R2-11 (template rules with WS-9's migration operation and the `framework.json` projection).
- BC-P2-31 classification is done; confirm it against the writer moves WS-3/4/5/7/8/9 make this round via `paths::store_path` (they own the writers).
