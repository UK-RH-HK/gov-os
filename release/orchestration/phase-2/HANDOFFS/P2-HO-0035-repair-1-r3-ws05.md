# P2-HO-0035 — Repair iteration 1, round 3: WS-5

| Field | Value |
|---|---|
| Handoff | P2-HO-0035 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0036** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws05/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0036.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

BC-P2-24 (governed, linked work generated from every Contract v3:572-583 source and each health failure), BC-P2-13 in-task hook, the close/DAG wiring of WS-4's round-2 APIs, and BC-P2-31 claims-store move.

## Files you own this round

`runtime/src/orchestration/{tasks,dag,readiness,claims,intents}.rs`; `runtime/src/memory/claims.rs`; `runtime/src/status.rs`; the task/report/worker-return/test-obligation schemas; `framework/taxonomy/**`.

## Items routed to you

- **BC-P2-24** engine: failed tests, audit findings, research discoveries, human decisions, CIT effects, lessons, missing tools/skills, retrieval failures (`memory::failures::open_failures` + `link_follow_up`, WS-6 round-1 IP-4), security findings, performance regressions and each health failure generate linked work in the same DAG; adopt WS-2's W7 investigation tasks into the engine (WS-2 r2 R3-5); idempotent.
- **BC-P2-13 hook:** task close uses `cit::materiality::classify_paths` and `binding::verified_writes` (WS-4 r2 R2-4; round-1 WS-5 IP-3 / WS-4 IP-R3-6).
- WS-4 r2 R2-1 (close calls `require_current_inputs`), R2-2 (claim/dag/show use `task_staleness`), R2-3 (index rebuild or claim runs `detect_and_propagate`), R2-5 (READY derived through `require_ready` — confirm), R2-6 (status changes and claims call `observe_boundaries`).
- WS-10 r2 IP-WS10-11 (closing an experiment task needs an experiment record), IP-WS10-12 (DAG blockers and readiness cells from the scenario chain), IP-WS10-13 (`test_data` in the test-obligation schema; backlink at task create).
- **BC-P2-31:** claims store and claim trees to `paths::store_path` (WS-6 r2 IP-R2-7) with `relocate_legacy`.
- Apply the availability rule (common protocol) at task create/claim/close.
