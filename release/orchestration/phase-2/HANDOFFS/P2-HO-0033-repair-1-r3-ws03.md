# P2-HO-0033 — Repair iteration 1, round 3: WS-3 (+ docs, spec amendments, adapters)

| Field | Value |
|---|---|
| Handoff | P2-HO-0033 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0034** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws03/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0034.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

**P2-ADJ-0002** (T2 facts portable across the owner's provisioned machines; forged/unauthorised records still refused — with WS-8 for provisioning), BC-P2-31 control-state move, the T2 completeness items, and documentation/spec records for everything rounds 1-2 changed.

## Files you own this round

`runtime/src/authority.rs`; `runtime/src/project.rs`; `runtime/src/orchestration/{control,gates}.rs`; `runtime/src/human_channel.rs`; `runtime/src/t2.rs`; `runtime/src/policy*.rs`; `runtime/src/routing.rs`; `runtime/src/adapters.rs`; `cli/src/main.rs` (semantic owner); `framework/policies/{AUTHORITY_POLICY,HUMAN_GATE_POLICY,POLICY_PRECEDENCE,MODEL_ROUTING_POLICY,ENFORCEMENT_MAP}.yaml`; `framework/roles/**`; `framework/adapters/**`; the human-gate/decision/roles/model-routing-overrides schemas; `docs/**` except `docs/generated/**`; `spec/decisions/**`, `spec/interfaces/**` (new governed amendment records only — never rewrite an accepted record's history).

## Items routed to you

- **P2-ADJ-0002** (read it in full): make OS-written T2 facts written on one provisioned machine honoured on the owner's other provisioned machines after clone/pull, forged/unprovisioned/unauthorised records still refused; no secret in any repository; no new external dependency class. WS-8 owns provisioning (`srr/**`, harness): define the API you need from it and record the IP; coordinate by API, not by editing `srr/**`.
- **T2 completeness:** add `cit` to `t2::SEALED_RECORD_TYPES` once WS-4 seals every CIT write (WS-5 r2 §5.4, IP-R3-2 — coordinate); re-seal task records rewritten by `gates.rs` (WS-5 r2 IP-R3-1, gates side); include sealed plugin-registry entries in `t2::audit` (WS-2 r2 R3-11).
- **BC-P2-31:** move control state to `paths::store_path` / `.governance-state/` (WS-6 r2 IP-R2-8) with `relocate_legacy`; treat `governance/registry/` as OS-managed.
- WS-10 r2 IP-WS10-01 (L1 authority class for `research-agent`/`data-author` write commands), IP-WS10-02 (gates refuse citing non-governed evidence and record the backlink), IP-WS10-15 (optional: `experiment_promotion` human-only).
- WS-9 r2 IP-R2-1 (`install_declared_session`), IP-R2-5 (optional: `upstream_export` human-only).
- WS-7 r2 IP-W7-3 (ENFORCEMENT_MAP descriptions of plugin keys), IP-W7-4 (optional: `plugins registry` view → `registry::report`), **IP-W7-6** (a governed amendment record: D-0005 consequence 3 narrowed to conform with Contract v3 F4 / ARCH-0003 §9, and API-0001 updated — authored as a new record within delegated authority, owner may supersede, consistent with how D-0005/D-0007 were approved; never edit D-0005's text in place).
- WS-4 r2 R2-12 (adapter provider hooks for pre-compaction and session close — `framework/adapters/**`, `adapters.rs`), R2-13 (review the new command labels' classes).
- WS-8 r2 IP-R2-WS08-7 (product-release record: the CLI command and its G0 class; WS-4 adds the record type).
- **Docs:** WS-3 r2 IP-R2-5, WS-8 r2 IP-R2-WS08-1 (exact text supplied), WS-9 r2 IP-R2-7, WS-10 r2 IP-WS10-17, WS-5 r2 IP-R3-9, WS-2 r2 R3-10, and WS-4/WS-6/WS-7 round-2 behaviour.
