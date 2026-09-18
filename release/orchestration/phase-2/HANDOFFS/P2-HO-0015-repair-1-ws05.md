# P2-HO-0015 — Repair iteration 1, round 1: WS-5 (part)

| Field | Value |
|---|---|
| Handoff | P2-HO-0015 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0018** |
| Workstream | WS-5 (part) |
| Classes | BC-P2-14, BC-P2-15 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws05/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0018.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/orchestration/{tasks,dag,readiness,claims,intents}.rs`; `runtime/src/memory/claims.rs`; `runtime/src/status.rs`; `framework/schemas/{task,report,worker-return,test-obligation}.schema.json`; `framework/taxonomy/**`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-14** task-contract fields (blocks, required_data, required_tools, production-merge permission, allowed/forbidden
  paths, designated role) are enforced, and path scope is not permanently widened by earlier CITs.
- **BC-P2-15** claims are atomic under concurrent sessions (no double grant) and carry scope (worktree, file scope), with
  overlapping scopes refused where dependency/mutation constraints forbid parallel work.
- You own `tasks.rs`. In round 2 you will receive integration points from WS-2 (G2 tier call, test-evidence verification),
  WS-3 (T2 primitive replacing the OS-managed exemption), WS-4 (receipt validation, in-task material-change detection). Do
  **not** anticipate them now; keep `tasks.rs` changes focused so those later edits merge cleanly.

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
