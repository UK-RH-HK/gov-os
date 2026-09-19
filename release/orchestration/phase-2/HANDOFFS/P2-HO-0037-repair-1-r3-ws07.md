# P2-HO-0037 — Repair iteration 1, round 3: WS-7

| Field | Value |
|---|---|
| Handoff | P2-HO-0037 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0038** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws07/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0038.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

BC-P2-31 plugin-registry move and the round-3 IPs routed to you.

## Files you own this round

`runtime/src/capabilities/**`; `runtime/src/srr/plugins.rs`; `runtime/src/tools.rs`; `framework/policies/TOOL_POLICY.yaml`; the plugin-descriptor/plugin-registry/tool/tool-registry/tool-permissions/mcp-registry schemas; `capabilities/**` except `code_intel_*`; `tools/**`.

## Items routed to you

- WS-6 r2 IP-R2-9 (move the plugin registry to `governance/registry/plugin-registry.json` via `paths::store_path`, with `relocate_legacy`), IP-R2-13 (descriptor fields declaring model/runtime artefacts outside the plugin directory, so BC-P2-30 identity binding covers them).
- WS-2 r2 R3-11 (expose sealed registry entries to `t2::audit` — WS-3 consumes).
- Your own r2 observation: plugin authorisation re-hashes each implementation on every call (debug-binary plugin tests take ~3 minutes) — cache by a sound key without weakening the pin (any changed byte must still be refused).
- WS-7 r2 IP-W7-1: confirm close reports are sealed now (WS-5 r2) so a governed security review can satisfy BC-P2-41's condition; adjust if not.
- R1 care as in round 2 (`srr/plugins.rs`, `tools::install` are §6 sites).
