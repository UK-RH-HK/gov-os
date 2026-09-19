# P2-HO-0026 — Repair iteration 1, round 2: WS-7

| Field | Value |
|---|---|
| Handoff | P2-HO-0026 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0028** |
| Workstream | WS-7 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws07/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0028.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-39 (plugin cannot decide its own elevation), BC-P2-40 (plugin code hash-bound, including `python3 -m <module>` registrations), BC-P2-41 (tool review and approval bound to the install), BC-P2-11 plugin side (elevated registration authorised only by a presented, answered gate raised for that plugin identity/version/permission set), BC-P2-09 registry side.

## Files you own this round

`runtime/src/capabilities/**`; `runtime/src/srr/plugins.rs`; `runtime/src/tools.rs`; `framework/policies/TOOL_POLICY.yaml`; `framework/schemas/{plugin-descriptor,plugin-registry,tool,tool-registry,tool-permissions,mcp-registry}.schema.json`; `capabilities/**` except `capabilities/python/govos_capabilities/code_intel_*`; `tools/**` (registries).

## Integration points routed to you

- from **ws03** (§9): IP-6 (seal plugin registry entries with `t2::seal_value`; honour only `Verified`).
- from **ws06** (§8): IP-3 (tool/plugin health failures recorded via `memory::failures::record_tool_failure`).
- **R1 care:** `srr/plugins.rs` and `tools::install` are §6 effect sites (privileged plugin acquisition below floor) and `guard_acquisition*` was examined at R1 (AR31-N1/N2, AR27-N6). Run every R1 held-out suite unedited before and after, and keep `tests/certification/section6.rs` green; any new acquisition path must be caught by the §6 derivation or conform to it.
- **BC-P2-39** is determined (Contract v3 F4:426; ARCH-0003 §9; synthesis `owner-decisions-required.md` row 2): choose a conforming design within the accepted architecture; a design needing a new external dependency class (e.g. an OS sandbox) would need owner adoption — do not choose one without stopping that class and recording the question.

## Notes

This workstream was not in round 1; read `repair-delta.md` classes 39-41 and the gamma-r/beta-r F4/C10 evidence in full.
