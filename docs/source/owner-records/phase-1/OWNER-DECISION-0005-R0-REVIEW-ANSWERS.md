# OWNER-DECISION-0005 — Product-owner answers to the AR-0023 R0 review questions

| Field | Value |
|---|---|
| Record | OWNER-DECISION-0005 |
| Date | 2026-09-17 |
| Raised by | AR-0023, fresh independent R0 architecture reviewer |
| Candidate | D-0009 / ARCH-0003 at `5fd8358`; review work commit `2dc08c2` |
| Classification | binding owner answers; **not** an R0 acceptance and **not** an authorisation to implement |

The reviewer surfaced three `NEW_OWNER_DECISION_REQUIRED` items: one inside the blocking finding `SRR-R0-H1`, and two
attached to non-blocking later-lifecycle conditions. The owner answered the two non-blocking items. The blocking item
remains open.

## 1. `SRR-R0-H1` / CD-R0-1 — below-floor recovery — **PENDING**

Still open as `GATE-OWNER-R0-BELOW-FLOOR-RECOVERY`. The bounded R0 correction cycle does not start until it is
answered, because an architecture role must not select this security-versus-availability posture on the owner's behalf.

## 2. `SRR-R0-L6` — plugin / tool / skill first-acquisition source authenticity — **DEFERRED TO R1**

**Owner answer.** Defer to R1. Verbatim direction:

> This is explicitly non-blocking for R0, so do not expand R0 again. At R1, the sensible design can distinguish
> remotely acquired privileged plugins/tools from built-in/local tools and decide how delegated signed targets apply.
> We already learned not to turn optional later assurance into an architecture blocker.

**Binding effects.**
- `SRR-R0-L6` stays a non-blocking R1/R2 condition. It is not routed into the R0 correction delta and must not be
  raised as an R0 blocker by any later R0 reviewer of this lineage.
- The architecture's existing `may additionally` formulation stands unchanged at R0.
- At R1, the design is expected to distinguish **remotely acquired privileged plugins/tools** from **built-in/local
  tools** and decide how delegated signed targets apply to each. This is an R1 design obligation, not an R0 one.
- General standing direction, applying to this lineage as a whole: do not convert optional later-lifecycle assurance
  into an architecture blocker.

## 3. `SRR-R0-L7` — offline / air-gapped install path — **NOT NEEDED**

**Owner answer.** No — not needed in the private/local profile.

**Binding effects.**
- `SRR-R0-L7` is closed as an owner decision. An offline/air-gapped install from a held authentic envelope is **out of
  scope** for the Phase-1 private/local profile.
- No architecture change is required to close it: the candidate never claimed the capability, so the finding is
  answered by this record rather than by edited text.
- Consistent with direction 2 above, this answer is **not** routed into the R0 correction delta. Reflecting it in the
  architecture's stated non-goals is optional and belongs to R1 planning, not to the bounded R0 correction.

## Scope discipline

This record answers questions. It does not accept the architecture, does not authorise implementation, does not alter
D-0007, D-0008, ARCH-0002 or the frozen R0/R1/R2/R3 acceptance boundary, and does not revive CP-1.
