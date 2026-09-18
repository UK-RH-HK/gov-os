# P2-HO-0017 — Repair iteration 1, round 1: WS-8 (part)

| Field | Value |
|---|---|
| Handoff | P2-HO-0017 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh `capability-repair` builder, run **P2-AR-0020** |
| Workstream | WS-8 (part) |
| Classes | BC-P2-35, BC-P2-36 (presentation and disclosure only), BC-P2-37, BC-P2-38 |
| Base | the commit your worktree is checked out at (integration branch after the iteration-0 synthesis merge) |
| Output directory | `release/capability-baseline/repair-1/ws08/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0020.report.yaml` |
| Required verdict | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED` or `INCOMPLETE` |

**First read `release/orchestration/phase-2/HANDOFFS/P2-HO-0010-repair-1-common-protocol.md` in full.** Then read
`release/capability-baseline/audit-0/synthesis/repair-delta.md` §0, §2, §3 and **every class listed above** in full,
with the findings each class cites (`blocker-classes.yaml`, `findings.yaml`, and the family audit evidence).

## Files you own

`runtime/src/kernel_trust.rs`; `runtime/src/kernel.rs`; `runtime/src/lock.rs`; `runtime/src/srr/**` except `plugins.rs`; `runtime/src/init.rs`; `runtime/src/update.rs`; `runtime/src/release.rs`; `runtime/src/recovery.rs`; `framework/schemas/{framework-lock,kernel-manifest,release-manifest}.schema.json`.

Shared hot spots and additive exceptions are in the common protocol.

## Your classes

- **BC-P2-35** post-install kernel integrity is checked against the machine's own protected installed-release record
  (ARCH-0003 §7), not only against repository files that can be rewritten consistently; no change to D-0007's text.
- **BC-P2-36 — presentation/disclosure part only:** an installation whose authenticity is UNKNOWN (unprovisioned machine)
  is never presented as current, verified or certified, and doctor/audit disclose it (Contract v3:150; OWNER-DIRECTIVE-0004).
  Doctor lives in WS-2's `doctor.rs`: expose the posture API and record the integration point. **The admission part —
  whether an unprovisioned machine may install external-source kernel material at all — is OD-P2-02, pending with the
  owner. Do not change admission behaviour.**
- **BC-P2-37** trust decisions never taken from unsigned release fields (e.g. manifest `certification` removing the update
  Human Gate; who may build a CERTIFIED release); framework.lock records the authenticated identity and its basis, not
  unsigned manifest values, and is independent of `XDG_CACHE_HOME`.
- **BC-P2-38** rollback behaviour on a provisioned machine as the repair delta states.
- You are the workstream most able to break R1: run **every** prior R1 held-out suite unedited before and after, keep
  `tests/certification/section6.rs` and `srr.rs` green, and report the counts. The `init.rs` role plumbing for BC-P2-08
  waits for WS-3's API (round 2).

## Seven other builders run in parallel

WS-1/12, WS-2, WS-3, WS-4, WS-5, WS-6, WS-8 and WS-9/11 each own disjoint files. You will not see their work until
integration. Where you need something they own, expose your side and record the integration point.
