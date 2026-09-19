# P2-HO-0027 — Repair iteration 1, round 2: WS-8

| Field | Value |
|---|---|
| Handoff | P2-HO-0027 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0029** |
| Workstream | WS-8 |
| Base | the commit your worktree is checked out at (integrated round-1 tree) |
| Output directory | `release/capability-baseline/repair-1/r2-ws08/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0029.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**Read first, in full:** `P2-HO-0020-repair-1-round-2-common.md`, then `P2-HO-0010-repair-1-common-protocol.md` (all of it
applies), then `release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and every class named below with
the findings and probes it cites, then the round-1 integration report
`release/capability-baseline/repair-1/integration/00-INTEGRATION-REPORT.md`.

## Classes

BC-P2-36 **admission** per OWNER-DECISION-P2-0002 (Option A) with harness/fixture/docs provisioning, BC-P2-35 unprovisioned sub-case (none remains under Option A — confirm), the kernel-cache race root cause, and the lifecycle-host call sites.

## Files you own this round

`runtime/src/kernel_trust.rs`; `runtime/src/kernel.rs`; `runtime/src/lock.rs`; `runtime/src/srr/**` except `plugins.rs`; `runtime/src/init.rs`; `runtime/src/update.rs`; `runtime/src/release.rs`; `runtime/src/recovery.rs`; `framework/KERNEL.yaml`; `framework/schemas/{framework-lock,kernel-manifest,release-manifest}.schema.json`; **`tests/certification/common.rs` and the fixtures' provisioning setup** (harness provisioning of a throw-away root for the whole certification suite — additive helpers; other test files may call them).

## Integration points routed to you

- **OWNER-DECISION-P2-0002 (read it in full):** on an unprovisioned machine, refuse external-source kernel ingress (`init --source`, `update`, `adopt`, `kernel reinstall`, any path staging kernel material not embedded in the running binary) — typed, observable, remediation *provision*; the embedded payload only as an explicitly marked bootstrap mode tied to the binary's identity, never presented as current/verified/certified; the certification harness, fixtures and docs provision a throw-away root so the documented path is provision-then-install; Phase-4 and release evidence run on provisioned machines. Provisioned behaviour (refuse unsigned/tampered/below-floor at every ingress) unchanged.
- from **ws02** (§6): IP-WS02-12 (G5 at update apply; guard at entry), IP-WS02-13 (guard + G5 at release build), IP-WS02-14 (conformance after `record_installed`), **IP-WS02-15 (root-cause fix of the `embedded_kernel_dir` materialisation race — per-call staging and verification of an existing cache against the embedded listing)**, IP-WS02-16 (`health` in `KERNEL.yaml` payload_dirs if the integration builder did not already).
- from **ws01-12** (§4): IP-2 (`release::build` refuses unless `contracts::verify` is `CONTRACT_SOURCE_BOUND`).
- from **ws03** (§9): IP-7 (`update.rs` reads answers through `gates::verified_answer`; `init.rs` role handling).
- from **ws04** (§7): IP-16 (release artefacts as governed records with `derived_from`/`validated_by` edges).
- **R1 (AC-14):** you are the workstream most able to break it. Run every R1 held-out suite unedited before and after; keep `section6.rs` and `srr.rs` green; changing admission is a floor-adjacent change — the four ingress/floor properties and the §5 allow-list must hold exactly.

## Notes

The harness change touches every certification test's setup: keep each test's asserted property intact and make the provisioning explicit.
