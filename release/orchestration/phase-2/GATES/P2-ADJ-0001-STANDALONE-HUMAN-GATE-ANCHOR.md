# P2-ADJ-0001 — Orchestrator adjudication: standalone human-gate anchor on machines with no release root

| Field | Value |
|---|---|
| Record | P2-ADJ-0001 (orchestrator adjudication — **not** an owner decision; the owner may override) |
| Date | 2026-09-19 |
| Raised by | P2-AR-0016 (WS-3), `release/capability-baseline/repair-1/ws03/00-REPAIR-REPORT.md`, owner question |
| Question | On a machine with no Signed Release Root, may an administrator-provisioned standalone anchor authenticate human gate answers (`HUMAN_GATE_POLICY.human_channel.standalone_anchor_when_unprovisioned`, builder default `true`), or must answers always come from a release root's `human-gate` delegation? |

## Ruling: determined by accepted sources — the standalone anchor is off by default (`false`)

- **OWNER-DECISION-P2-0002 (Option A, 2026-09-19)** fixed the posture for machines with no trust anchor: external-source kernel
  ingress is refused until provisioned, the binary's embedded payload installs only as a marked **bootstrap** mode, dev/test
  machines **provision a throw-away root**, and Phase-4 qualification and release evidence run on **provisioned** machines.
  The owner's chosen first-run path is *provision, then work*.
- **ARCH-0003 §3** (owner-adopted) defines one trust chain: trusted platform/admin bootstrap → root metadata → delegated
  roles. **§2**: "no domain silently substitutes for another". A standalone anchor outside the root's delegations would be a
  second, parallel authority domain for Human Gate approval.
- **BC-P2-10's determined authority class** (owner-controlled authority anchored in the administrator-provisioned boundary)
  is met by the release root's `human-gate` delegation on a provisioned machine — including a dev/test machine provisioned
  with a throw-away root, as OWNER-DECISION-P2-0002 requires.

Therefore governed Human Gate answers derive from the provisioned release root's `human-gate` delegation; the standalone
anchor path is disabled by default. Whether it may ever be enabled is left as a kernel policy switch that only a
floor-raising (never floor-lowering) policy change could affect, under POLICY_PRECEDENCE.

## Routing

Round 2, WS-3 follow-up: set the default to `false`, keep the refusal typed and observable on an unprovisioned machine
(remediation: provision), and add the regression test. Recorded as an owner-overridable orchestrator interpretation in the
ledger and surfaced to the owner in the active chat; if the owner prefers `true`, that is a one-key change recorded as an
owner decision.
