# OWNER-AUTHORISATION-P2-0006 — Option A: one final bounded repair round, with a hard stop after it

| Field | Value |
|---|---|
| Record | Owner authorisation (product owner, 2026-09-22) |
| Id | **OA-P2-06** |
| Status | IN FORCE for the remainder of Phase 2 |
| Answers | `PHASE_2_PRE_MINT_DECISION_PACKAGE.md`, the escalation P2-ADJ-0006's stopping rule produced |
| Does not change | Contract v3, the frozen Phase-2 gate contract, OD-P2-01..03, OC-P2-04, OD-P2-05, or any acceptance criterion |

## What the owner authorised

Option A, as the package stated it: **one final bounded repair round for exactly AR75-F1 and AR75-F2**, plus correction of
AR75-F3's factually incorrect justification, followed by one fresh Opus 5 adversarial review.

The owner's own words on each:

> **AR75-F1**: close the demonstrated cp/curl command-shape escape without returning to an interpreter/program denylist.
> Follow the reviewer's principled fix: evaluate every relevant non-flag argument relative to the project boundary rather
> than only tokens containing a slash, and make the proof sensitive to actual escape behaviour including symlink-resolved
> destinations. Preserve ordinary conforming acquisition and all existing negative controls.

> **AR75-F2**: treat `class` as authority-bearing in restrictiveness/overlay comparison because `class: derived` changes
> whether mutations are governed/observed. A project-side declaration must not gain an exemption merely by changing class.

> Also correct AR75-F3's factually incorrect justification while touching this surface, but do not turn that LOW item into
> broader architecture work.

## The two constraints that bind minting

1. > Do not mint `cap2-candidate-2` while either HIGH finding remains open.
2. > STOP and return to me for an architecture/meta-review if that fourth adversarial review: finds another materially new
   > HIGH blocker on the install-trust surface; or leaves AR75-F1 or AR75-F2 materially open.

Only if the fourth review closes the surface with no blocking finding does the orchestrator mint `cap2-candidate-2` and
run the formal fresh Opus 5 Phase-2 acceptance verification. Phase 3 does not begin until
`GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` is independently earned.

This is a **stricter** stop than P2-ADJ-0006's: the orchestrator committed to stopping after one structural round, and the
owner has now spent that allowance and closed the door behind it. There is no fifth round on this surface without a
further owner decision.

## Why this is an authorisation and not a new decision

Nothing here trades anything the sources leave open. AR75-F1's fix implements OD-P2-05 clause 3 (a missed classification
must fail towards the gate); AR75-F2's implements OC-P2-04 (a project-editable file must not manufacture authority — and
an exemption from governed observation is authority). The owner's contribution is **scope and permission to proceed**:
the orchestrator had stopped itself, as it said it would, and could not restart on its own authority.

## Ancillary instructions recorded with this authorisation

- **Performance diagnostic** (P2-PERF-0001): measure where the ~2.5 h certification run goes, deterministically, and
  record findings as V8.3 input. "Do not perform a major performance refactor during this bounded Phase-2 repair unless
  required for correctness." Measurement only; it does not gate the repair.
- **Testing protocol for this round**: targeted tests while iterating, affected dependency tests where appropriate, and
  exactly one genuine full certification suite once the repair is ready for adversarial review. "Acceptance-critical
  evidence must remain trustworthy. Do not introduce parallelism merely for speed unless isolation/concurrency safety is
  demonstrated."
- **Routing unchanged**: outer orchestrator, final acceptance verifier and architecture/security synthesis on Opus 5;
  cross-cutting and normal engineering repair on Sonnet 5; cheap mechanical work on Haiku; build/test/schema work
  deterministic T0. **DeepSeek remains paused** and must not be launched unless the owner explicitly re-enables it.
- **V8.3 transition rule**: Phase 2 continues under V8.2 plus the approved worker/runtime improvements. V8.3 must not be
  designed, installed or activated during Phase 2. A dedicated **non-normative** V8.3 input/evidence package is preserved
  meanwhile (`V8_3_EVIDENCE_PACKAGE.md`), and it "must not alter Phase-2 acceptance criteria, product behaviour or the
  frozen Phase-2 contract." After acceptance, a `PHASE_2_TO_V8_3_HANDOFF` is produced, and the V8.3 design itself is done
  by a fresh post-Phase-2 architecture session, not by this orchestrator.
