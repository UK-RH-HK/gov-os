# P2-HO-0022 — Repair iteration 1, round 2: WS-3 (+ docs)

| Field | Value |
|---|---|
| Handoff | P2-HO-0022 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0024** |
| Workstream | WS-3 (+ docs) |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws03/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0024.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

P2-ADJ-0001 (standalone human-gate anchor defaults to off), the BC-P2-08 remaining call-site/guard work, and CLI surface for other workstreams' round-2 features.

## Files you own this round

`runtime/src/authority.rs`; `runtime/src/project.rs`; `runtime/src/orchestration/control.rs`; `runtime/src/orchestration/gates.rs`; `runtime/src/human_channel.rs`; `runtime/src/t2.rs`; `runtime/src/policy*.rs`; `runtime/src/routing.rs`; `cli/src/main.rs` (semantic owner); `framework/policies/{AUTHORITY_POLICY,HUMAN_GATE_POLICY,POLICY_PRECEDENCE,MODEL_ROUTING_POLICY,ENFORCEMENT_MAP,MEMORY_POLICY(failure_memory keys only)}.yaml`; `framework/roles/**`; `framework/schemas/{human-gate,decision,model-routing-overrides,roles}.schema.json`.

## Integration points routed to you

- **P2-ADJ-0001** (`release/orchestration/phase-2/GATES/P2-ADJ-0001-STANDALONE-HUMAN-GATE-ANCHOR.md`): `HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned` defaults to `false`; on an unprovisioned machine a human answer is refused typed and observable with remediation *provision*; regression test.
- from **ws02** (§6): IP-WS02-08 (`control::guard_write` calls `scheduler::guard` — the single G0 site), IP-WS02-09 (authority class of `record_skill_binding`; FREEZE_WRITES/authority class of evidence-writing commands `gov audit`, `gov health run`, `gov verify product`), IP-WS02-11 (optional).
- from **ws04** (§7): IP-6 (`gov continue` must not fail when the derived index cannot be opened — `IndexHandle::Unavailable`; W10 attack 4). Coordinate the signature with WS-5, who owns `status::continue_work`: you change the CLI arm to pass the handle; WS-5 accepts it.
- from **ws06** (§8): IP-6 (ENFORCEMENT_MAP entries for `MEMORY_POLICY.failure_memory.*` if declared; optional `gov memory miss|failures`).
- from **ws08** (§6): IP-3 (`KernelCmd::Reinstall` carries the pinned payload so the pin refusal precedes break-glass entry).
- from **ws09-11**: IP-3 (adopt arms call `a3_map_by`/`a4_plan_by` with `Actor::declared(session, role)` and pass the declared role to every stage).
- from the **round-1 integration report** (`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`):
  **O-1** — projects on the shipped 4.1.4/4.1.5 kernels have their descriptive policy keys refused; doctor D027 goes
  CRITICAL and an update to shipped 4.1.5 is rolled back (reproduces on WS-3's branch alone). Contract v3 S5 (preserve
  project overlay; compatibility/migration) and A1 (weakening refused, not description) both bind: descriptive keys from a
  shipped kernel must be recognised as descriptive, while genuine floor-weakening overrides stay refused. **O-4** — decide,
  with the reason, whether `rebuild-memory` (derived-state rebuild) belongs on the FREEZE_WRITES recovery allow-list
  (framework §74; Contract v3 A5 "Recovery from emergency controls is auditable"). **O-8** — P2-ADJ-0001 (below).
- **CLI for round-2 features of others:** WS-7, WS-9, WS-10 may need new subcommands; they add them additively and must classify them in `g0_label`/`COMMAND_GUARDS` — review their additions at integration, not now.
- **Docs** (ws03 IP-11, ws05 IP-8): `docs/ARCHITECTURE.md` §4.8 and `docs/COMMANDS.md` describe the round-1 behaviour (role resolution and G0, human channel, T2, new refusal codes, claims, context, artefact, oracle, health). You own `docs/**` except `docs/generated/**` in round 2.

## Notes

Do not implement agent L0–L4 credentials (OWNER-DECISION-P2-0001).
