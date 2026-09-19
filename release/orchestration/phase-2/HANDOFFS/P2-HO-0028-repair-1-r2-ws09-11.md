# P2-HO-0028 — Repair iteration 1, round 2: WS-9 + WS-11

| Field | Value |
|---|---|
| Handoff | P2-HO-0028 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0030** |
| Workstream | WS-9 + WS-11 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws09-11/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0030.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-34 adoption side (adoption verdicts bound to what the independent reviewer approved; roles checked, not free strings; A10/A11 independence real), the adopt host call sites, and BC-P2-10 export approval use.

## Files you own this round

`runtime/src/adopt.rs`; `runtime/src/migrations/**`; `migrations/**`; `framework/schemas/{migration,migration-catalogue-entry,adoption-baseline}.schema.json`; `runtime/src/upstream.rs`; `runtime/src/lessons.rs`; `framework/policies/LEARNING_POLICY.yaml`; `framework/schemas/{upstream-packet,lesson,framework-change-proposal}.schema.json`.

## Integration points routed to you

- from **ws02** (§6): IP-WS02-18 (G5 `tier_run` at A11 in place of the deep audit; scheduler guard at A6).
- from **ws03** (§9): IP-9 (upstream submit requires `gates::human_approval_for(p, gate, packet_sha256)`), IP-10 (adopt uses the role resolution API).
- from **ws06** (§8): IP-7 (REPOSITORY_CONTRACT template rule for `spec/reports/memory-quality/**` plus the migration overlay operation — you own `migrations/**`; the template file itself is WS-6's: coordinate by adding the migration and recording the template rule as an IP if WS-6 has not added it).
- from **ws09-11** (your own): IP-2 (export approval from the authenticated channel), IP-3 (adopt arms — the CLI change is WS-3's; you expose `Actor::declared` use in every stage), IP-4 (G5 at adopt).
- **BC-P2-34 adoption side** (alpha-r A0-T2-01, beta/gamma independence findings): an A7 accept with 0 tests, an executor emptying tests or turning a KEEP into an ungated delete after approval, must be refused; stage roles are checked against the declared role (OWNER-DECISION-P2-0001: roles are adapter-declared, so bind to the *declared* role consistently and to T2-sealed approvals, not free strings); A10's held-out set must not be builder-generated; A11 has an independence check.

## Notes

Keep `tests/certification/brownfield.rs` and `migration.rs` properties intact.
