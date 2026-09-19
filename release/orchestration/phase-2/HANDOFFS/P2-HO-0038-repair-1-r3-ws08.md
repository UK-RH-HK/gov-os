# P2-HO-0038 — Repair iteration 1, round 3: WS-8

| Field | Value |
|---|---|
| Handoff | P2-HO-0038 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0039** |
| Base | the commit your worktree is checked out at (integrated round-2 tree) |
| Output directory | `release/capability-baseline/repair-1/r3-ws08/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0039.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0031-repair-1-round-3-common.md` (incl. the availability rule), `P2-HO-0020-repair-1-round-2-common.md`,
`P2-HO-0010-repair-1-common-protocol.md`, the round-2 integration report `release/capability-baseline/repair-1/integration-2/00-INTEGRATION-REPORT.md`,
`release/capability-baseline/audit-0/synthesis/repair-delta.md` for every class named below, and each round-2 report the IPs cite
(`release/capability-baseline/repair-1/r2-<ws>/00-REPAIR-REPORT.md`).

## Scope

P2-ADJ-0002 provisioning side, BC-P2-31 update-snapshot move, kernel payload/version consistency, product-release records (WS-8 side), and the round-3 IPs routed to you.

## Files you own this round

`runtime/src/kernel_trust.rs`; `runtime/src/kernel.rs`; `runtime/src/lock.rs`; `runtime/src/srr/**` except `plugins.rs`; `runtime/src/init.rs`; `runtime/src/update.rs`; `runtime/src/release.rs`; `runtime/src/recovery.rs`; `framework/KERNEL.yaml`; the framework-lock/kernel-manifest/release-manifest schemas; `tests/certification/common.rs` (harness) and fixture provisioning.

## Items routed to you

- **P2-ADJ-0002** (read it): the provisioning side of T2 cross-machine continuity — whatever WS-3's mechanism needs from provisioning (e.g. a delegated binding role in the provisioned root, or authorised machine keys), plus a two-machine harness helper (two provisioned machines from the same test root, one unprovisioned/foreign) for the certification suite.
- **Kernel payload/version consistency** (WS-8 r2 IP-R2-WS08-6, WS-9 r2 IP-R2-3, WS-7 r2 IP-W7-5): `KERNEL.yaml` `schema_versions` must match the actual schema files; decide how the `framework/health` payload and schema changes are carried given that `release/releases/4.1.5` is immutable (the branch is `release/4.1.6-rc1`; the recorded next version is 4.1.6) — keep `repair3::current_release_payload_identity_and_hygiene` meaningful and never edit `release/releases/**`; complete `migrations/M-4.1.5-4.1.6.yaml` coordination with WS-9.
- WS-8 r2 IP-R2-WS08-5 (update entry guard vs its own remedy — implement against WS-2's availability API), IP-R2-WS08-7 (release artefacts in lineage — your side), IP-R2-WS08-12/13 (harness convention for new tests; external-install probes on provisioned machines).
- WS-6 r2 IP-R2-10 (update snapshots to the BC-P2-31 store path).
- R1 care as in round 2: run every R1 held-out suite through a private path on your tree, before/after, with census.
