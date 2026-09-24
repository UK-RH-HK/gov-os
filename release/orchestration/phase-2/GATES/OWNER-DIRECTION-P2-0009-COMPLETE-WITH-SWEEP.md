# OWNER-DIRECTION-P2-0009 — Complete Phase 2 with a pre-final decision sweep, a binding simplification boundary, and a bounded Review 8

| Field | Value |
|---|---|
| Record | Owner direction (product owner, 2026-09-24) |
| Id | **OD-P2-09** |
| Status | IN FORCE. Extends OD-P2-08; does not supersede it. |
| Objective | Finish Phase 2 without weakening accepted trust requirements **and** without an indefinitely expanding repair/review loop around optional mechanisms whose complexity exceeds their value. |
| Terminal state | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`, issued only by the required fresh independent formal verifier. |

## 1. What changed from OD-P2-08

OD-P2-08 §8 authorised automatic repair-and-re-review with seven stop conditions, **none of which was a round
budget**. The outer orchestrator raised that gap on 2026-09-24 after the seventh review. This direction closes it.

**Review 8 is the convergence decision point for this architecture.** There is to be no automatic Review 9, 10, 11
continuing the same mechanism-hardening loop.

## 2. The simplification principle — now binding

```
required core property FAILS                          → repair structurally
optional / recovery / convenience feature
    repeatedly creates HIGH findings                  → DELETE or simplify the feature
MEDIUM / LOW residual, bounded, non-blocking          → record honestly with lifecycle disposition
KNOWN HIGH in a required current-phase property       → do not ship
```

> Do not keep increasing the trusted computing base solely to preserve a rare operator convenience. A smaller
> product with stronger, clearer guarantees is preferred to a larger product with complicated recovery paths.

## 3. Property A — converged

Held under **three** consecutive fresh independent adversarial reviews. Not to be modified or re-litigated merely
because a new review is taking place. `runtime/src/exec_resolve.rs` is not to be touched unless a change elsewhere
invalidates its evidence, or genuinely new evidence falsifies Property A. The final reviewer may confirm
preservation; it may not reopen settled design questions without evidence.

## 4. Mandatory pre-final owner-question sweep

Before freezing AR95 for Review 8, the orchestrator must perform **one** explicit sweep and present **all** genuine
owner-level questions in **one consolidated message**, each with: the exact decision required; why authoritative
material does not already answer it; current implemented behaviour; options; a recommendation; security, usability
and complexity consequences; whether one option allows deletion; and what Review 8 may then assume.

Routine engineering questions are **not** permitted. If none are genuine, state `PRE_FINAL_OWNER_QUESTION_SWEEP:
NONE` and continue automatically.

Three questions must be explicitly checked: **5A** whether `gov floor-reanchor` is required at all, or whether
governed re-onboarding is the acceptable relocation semantic; **5B** the required semantics for concurrent
re-anchor; **5C** whether a sandbox exemption must remain authority-bearing after its creating process dies.

## 5. Decision rule after Review 8

| Outcome | Action |
|---|---|
| No HIGH blocker | Proceed automatically: freeze → mint `cap2-candidate-2` → re-establish evidence → fresh formal verification. No owner permission needed. |
| Another HIGH in `floor-reanchor` | **Delete `floor-reanchor`.** Adopt relocation → governed re-adoption. No further identity-transfer guard layer. Then one fresh independent verification of the simplified surface. |
| HIGH in another new optional/recovery mechanism | Ask whether it can be deleted or narrowed without compromising core purpose. If yes, simplify rather than wrap. Then verify. |
| Material HIGH in an **old/untouched core subsystem** | **STOP and return to the owner** — that is scope expansion, not convergence. |
| Only MEDIUM/LOW | Do **not** keep Phase 2 open. Classify against the frozen contract; if non-blocking and bounded, document, assign lifecycle, proceed. |

## 6. The acceptance standard, stated

```
defined private/local deployment boundary
+ Contract-v3 current-phase obligations satisfied
+ required properties independently evidenced
+ no known blocking HIGH
+ R0/R1 preserved
+ residual MEDIUM/LOW explicitly bounded and dispositioned
+ evidence fresh for the exact candidate
```

> It is **not** "no conceivable defect can ever be found in future." Do not transform a finite engineering
> acceptance criterion into an impossible claim of absolute security.

## 7. Profile — do not expand

Owner-controlled WSL/Linux machine; private repositories; one owner; explicit OS/admin/hardware trust assumptions;
models/agents/projects lower-trust than Governance OS authority; no public SaaS; no hostile multi-tenant
environment. Landlock, bubblewrap, hermetic containerisation, gVisor, microVMs, high-assurance supply-chain ceremony
and the R3 multi-tenant threat model remain deferred **unless current evidence proves one strictly necessary for an
already-claimed Phase-2 property**.

## 8. Formal acceptance

Mint `cap2-candidate-2` against the exact frozen tree, then dispatch a fresh independent Opus 5 formal Phase-2
acceptance verifier. **The outer orchestrator may not self-award the token.** An ordinary implementation/evidence
defect found there loops automatically (repair → invalidate → mint new candidate → fresh verification); a genuine new
owner-level architecture question stops and returns to the owner.

## 9. Interruption policy

Continue autonomously except for the mandatory sweep. After those answers, do not interrupt for routine
implementation, test execution, checkpointing, evidence regeneration, integration, reviewer dispatch, candidate
minting when conditions are met, or routine formal-verification repair loops. Return only for: a sweep question;
architecture falsification; a material new HIGH in an old/untouched core subsystem; a new trusted-authority
requirement; R0/R1 reopening; a material security/product/usability boundary decision; a destructive or irreversible
action; an unresolved normative contradiction; a credential/key action; or another genuine Human Gate.

## 10. Standing constraints, unchanged

V8.2 remains the active Phase-2 baseline. **V8.3 must not be designed, installed or activated during Phase 2**, and
Phase 3 must not be started here. DeepSeek remains paused. Anti-stall rules remain active. Failed iterations are
historical evidence and are not erased. Phase-2 certification cost is **not** the intended cost model for normal
governed development (see the G1–G6 tiering and the routine-overhead objective recorded in
`V8_3_EVIDENCE_PACKAGE.md`).
