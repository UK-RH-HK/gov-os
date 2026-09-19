# P2-HO-0024 — Repair iteration 1, round 2: WS-5

| Field | Value |
|---|---|
| Handoff | P2-HO-0024 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0026** |
| Workstream | WS-5 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws05/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0026.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-16 (runnable/READY derived from the task graph — manifest, gates, blocks, readiness, and `claim` consults the DAG), BC-P2-12 (DAG side), BC-P2-20 (close-side receipt validation), BC-P2-34 (task-role side of independence), and the task-host call sites of every round-1 API.

## Files you own this round

`runtime/src/orchestration/{tasks,dag,readiness,claims,intents}.rs`; `runtime/src/memory/claims.rs`; `runtime/src/status.rs`; `framework/schemas/{task,report,worker-return,test-obligation}.schema.json`; `framework/taxonomy/**`.

## Integration points routed to you

- from **ws02** (§6): IP-WS02-01 (`tasks::close` uses `verification::close_gate`), IP-WS02-02/03 (scheduler guard at task create, claim, `continue --claim`), IP-WS02-04 (`status` shows health).
- from **ws03** (§9): IP-1 (task close uses `t2::classify_path` instead of the OS-managed exemption; refuse close unless the task's gate is Authorised), IP-2 (DAG readiness via `task_gate_authorisation_in`), IP-3 (intents/status stop proposing `--by human`).
- from **ws04** (§7): IP-1 (manifest `resolve`/`require_ready` in DAG, READY routes, claim, replan), IP-2 (close: `report_from_worker_return` → `require_valid` → `outputs_produced`), IP-3 (`continue_work` compiles tolerantly and refuses non-dispatchable packets), IP-4 (provenance at task create), IP-5 (task schema declares the manifest fields), IP-6 (accept `IndexHandle::Unavailable` from the CLI — WS-3 changes the arm).
- from **ws05** (your own §5): IP-4 (`control::guard_write` in `tasks::release` — check the R1 §5 below-floor allow-list first: `release` of a claim must stay available where §5 requires it; run the R1 held-out suites), IP-5 (T2 primitive into `closed_states`/`cit_window_paths`), IP-9 (= BC-P2-16 claim consults the DAG).
- from **ws08** (§6): IP-4 (`status` builds `release_trust` from this project's `srr::installation::posture_of`).

## Notes

BC-P2-24 (work generated from events) and the in-task material-change hook for BC-P2-13 are round 3.
