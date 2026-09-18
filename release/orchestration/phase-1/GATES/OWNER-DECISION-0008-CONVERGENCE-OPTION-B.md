# OWNER-DECISION-0008 — Convergence decision: Option B, structural repair authorised

| Field | Value |
|---|---|
| Record | OWNER-DECISION-0008 |
| Date | 2026-09-18 |
| Gate | `GATE-OWNER-R1-CONVERGENCE-DECISION` |
| Answers | `PHASE_CONVERGENCE_ESCALATION_REQUIRED` package, SHA-256 `82d87c963c1bf423e181e006c157d4ded9171ade9683f24223c22d602b46d829` |
| Classification | binding owner decision on orchestration scope and convergence policy at R1 |
| Not | an R1 acceptance; a release authorisation; any change to D-0007, D-0009, the accepted ARCH-0003 body, the frozen R0/R1/R2/R3 boundary or any prior owner record |

## Decision

**Option B.** One additional bounded R1 **structural** repair is authorised.

## Mandate

1. **Fix `AR31-B1`** — §6 bullet 7 must be enforced, and the "every reporting surface carries the marking" claim must
   be made true.
2. **Fix `AR31-B2`** — the enforcement points must fail **closed** when they cannot determine their subject.
3. **Remove the root cause.** §6 coverage must be **derived from the product** rather than relying on a manually
   asserted enumeration.
4. **Tests must be able to falsify any "no primitive exists" claim.** A bullet whose census entry asserts that no
   primitive realises it must be refutable by the product's own suite.

## Convergence policy — this supersedes the three-iteration rule for the remainder of R1

- **Residual defects within the already-identified blocker classes** (`BC-R1-1` guard decision, `BC-R1-2` guard
  coverage, `BC-R1-3` undetermined-subject fail-open) **may be repaired and re-verified automatically**, without
  interrupting the product owner, for as many cycles as that takes.
- **A genuinely new material blocker class, or any architecture/owner decision, STOPS the loop and escalates
  immediately** — not after another three iterations. One occurrence is enough.

## After the repair

Mint a new immutable candidate and run a **fresh independent verifier**. If R1 passes, continue automatically to
`ROT_PHASE1_CANDIDATE_ACCEPTED_R1`, checkpoint Phase 1, and **stop before Phase 2**.

## Scope discipline

This record authorises orchestration to continue. It accepts no candidate, certifies no release, and changes no
normative source. `ROT_ARCHITECTURE_ACCEPTED_R0` is unaffected and is not reopened.
