# P2-HO-0021 — Repair iteration 1, round 2: WS-2

| Field | Value |
|---|---|
| Handoff | P2-HO-0021 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0023** |
| Workstream | WS-2 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws02/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0023.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-22 (orphan/unexplained outputs detected — Gate W W7), and the reporting side of every check other workstreams built.

## Files you own this round

`runtime/src/verification/**`; `runtime/src/doctor.rs`; `runtime/src/observability.rs`; `runtime/src/skills.rs`; `runtime/src/scheduler/**`; `framework/policies/TEST_POLICY.yaml`; `framework/health/**`; `framework/schemas/audit.schema.json`; `runtime/src/error.rs` (exit-code mapping only).

## Integration points routed to you

- from **ws01-12** (`release/capability-baseline/repair-1/ws01-12/00-REPAIR-REPORT.md` §4): IP-1 (contract verify at G5/doctor), IP-4 (G6 entry validates oracle and score report), IP-5 (hidden-oracle material inside a governed repository is a HIGH finding).
- from **ws03** (§9): IP-5 (`t2::audit`, `gates::unverified` reported and in the currency key).
- from **ws02** (§6, your own round-1 report): IP-WS02-10 (`HEALTH_HARD_BLOCK` → exit 4, API-0002 blocked class), IP-WS02-17 (doctor posture/authenticity and plugin checks), IP-WS02-22 (honour only T2-bound green and product-test records).
- from **ws04** (§7): IP-7 (misplaced records, stale links, unconsumed outputs), IP-8 (untraceable closed tasks), IP-9 (`verify_delivery` in `context_reproducibility`), IP-10 (stable finding ids).
- from **ws05** (§5): IP-2 (production-merge findings, dangling blocks), IP-7 (D017 message names the real claims store).
- from **ws06** (§8): IP-2 (index content coverage check at G1/G5; persisted regression misses into failure memory; open failures reported), IP-8 (index manifest in the currency key).
- from **ws08** (§6): IP-1 (doctor posture check), IP-2 (audit finding for unestablished authenticity).
- from the **round-1 integration report** (`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`):
  **O-2** — doctor D019 reports gates that were rendered but not acknowledged as "exist only in files"; align its wording and
  semantics with WS-3's presentation rule (presented = signed answer or signed receipt). **O-6** — stale comment in
  `skills.rs` about `record_skill_binding` (now declared at L3). Note the integration fix `811317b`: `currency.rs` must read
  the trust anchor through `srr::verifier::trusted_root`, never by a hand-built path (R1 AR-0031 `hx_a::a4`).
- from **ws09-11**: IP-1 (`assign_finding_ids` replaces positional `GF-` ids — reconcile with ws04 IP-10 into one stable-id scheme).

## Notes

BC-P2-07 (tier duties) closes in round 3 once every host has wired its call site in round 2; BC-P2-23 (W11 metrics) and BC-P2-44 (SLO thresholds and the HEALTHY conjunction) are round 3. Keep the tier contract stable: hosts are wiring against it in parallel.
