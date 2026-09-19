# P2-HO-0039 — Repair iteration 1, round 3: WS-9 + WS-11

| Field | Value |
|---|---|
| Handoff | P2-HO-0039 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0040** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws09-11/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0040.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

BC-P2-31 migration snapshots and overlay-template migration, adoption follow-ups, and the command-test privilege observation.

## Files you own this round

`runtime/src/adopt.rs`; `runtime/src/migrations/**`; `migrations/**`; the migration/migration-catalogue-entry/adoption-baseline schemas; `runtime/src/upstream.rs`; `runtime/src/lessons.rs`; `framework/policies/LEARNING_POLICY.yaml`; the upstream-packet/lesson/framework-change-proposal schemas.

## Items routed to you

- WS-6 r2 IP-R2-10 (migration snapshots to the BC-P2-31 store path), IP-R2-11 (overlay template rules delivered to installed projects through a migration operation, with WS-6's template change and the `framework.json` projection).
- WS-2 r2 R3-9 (A11 states the posture as the reason when D032 is its only doctor failure — note the harness is provisioned now, so this matters for real unprovisioned bootstrap installs).
- WS-9 r2 observation: a reviewer-written `command` test runs an arbitrary command at A6/A7 with the executor's privileges. Contract v3 A3 (*"Tool execution respects role/authority/permission boundaries"*): bound what such a test may execute to what the policy and the declared roles permit, typed refusal otherwise, without breaking reviewer-authored tests' purpose.
- Coordinate `migrations/M-4.1.5-4.1.6.yaml` with WS-8's version/payload decision.
