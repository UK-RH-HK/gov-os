# OWNER-DECISION-0006 — Below-floor recovery: option (b) BREAK-GLASS, authorised and recorded

| Field | Value |
|---|---|
| Record | OWNER-DECISION-0006 |
| Date | 2026-09-17 |
| Gate | `GATE-OWNER-R0-BELOW-FLOOR-RECOVERY` |
| Raised by | AR-0023 (fresh independent R0 reviewer), finding `SRR-R0-H1`, correction item CD-R0-1 |
| Classification | binding owner product/security decision, lifecycle R0 |
| Not | an R0 acceptance; an implementation authorisation; any change to D-0007, D-0008, ARCH-0002 or the frozen R0/R1/R2/R3 boundary |

## Decision

**Option (b) — BREAK-GLASS, AUTHORISED AND RECORDED.**

For the standard private/local Governance OS profile, below-floor recovery is permitted **only** as an explicit
owner-authorised emergency recovery mode.

## Binding requirements

1. **The recovery release must still be an authentic Governance OS release.** Break-glass does **not** permit arbitrary
   or unsigned code.
2. **Authority source.** The authority must come from an owner-controlled local/out-of-band recovery mechanism that
   **cannot be manufactured by**: repository content; environment variables; caller fields; plugins; model output.
3. **Durable record on entry.** Entering break-glass must be durably recorded with, where available: machine identity;
   the current signed security floor / high-water; the recovery release identity; the reason; timestamp/evidence.
4. **Explicit marking.** While below floor, the machine must be explicitly marked:

   `DEGRADED — RECOVERY ONLY`

5. **Permitted activities may include:** inspection; backup/export; diagnosis; repair; uninstall/reinstall; restoration
   of an authenticated Governance OS release.
6. **Below-floor recovery MUST NOT permit:**
   - normal privileged Governance OS operation;
   - creation or approval of new Human Gates;
   - release certification;
   - trust-policy mutation;
   - privileged plugin/profile acquisition;
   - lowering or resetting the signed security floor / high-water;
   - treating the below-floor release as current or fully trusted.
7. **Exit condition.** Normal governed operation resumes only after an authenticated release **at or above the signed
   minimum secure version** is installed and verified.
8. **The security floor itself is NOT lowered by break-glass.**
9. **Ingress consistency.** The floor rule must govern `recovery`, `rollback` and every other backward-capable
   privileged lifecycle ingress consistently.
10. **Availability constraint.** GitHub/network access is **not** the sole break-glass authority. Recovery must remain
    possible when GitHub/network access is unavailable.

## Effect on the R0 correction

This record supplies the owner input that CD-R0-1 was blocked on. The bounded R0 correction cycle may now run, limited
to `SRR-R0-H1` (CD-R0-1) and `SRR-R0-M1` (CD-R0-2).

The correction must reconcile the existing revoked/below-floor recovery language — including the allowance at
`ARCH-0003.yaml:91` permitting a known-revoked binary to perform `recovery` — with this decision.

Designing the break-glass authority mechanism in architectural terms is within CD-R0-1. Its implementation, storage
format, CLI surface and tests are R1 and are not part of this correction.

## Standing direction carried forward

`OWNER-DECISION-0005` applies unchanged: do not convert optional later-lifecycle assurance into an architecture
blocker. In particular, `SRR-R0-M1` must be closed by declaring the time/clock assumption and its non-guarantee
honestly — including making no claim of knowledge of unseen future revocations — and **must not** be broadened into
another trust-state protocol.
