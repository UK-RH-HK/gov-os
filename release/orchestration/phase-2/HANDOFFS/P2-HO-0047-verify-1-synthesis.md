# P2-HO-0047 — Verification iteration 1: synthesis and verdict

| Field | Value |
|---|---|
| Handoff | P2-HO-0047 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent **synthesis verifier**, run **P2-AR-0052** — not any auditor, builder, integrator or iteration-1 verifier |
| Candidate | `cap2-candidate-1` (identities in your dispatch message and `ORCHESTRATOR_STATE.yaml`) |
| Base commit | your worktree's commit: the release branch with all eight iteration-1 verifications merged |
| Active gate | `GATE-P2-CAPABILITY-BASELINE-ACCEPT` |
| Evidence directory | `release/capability-baseline/verify-1/synthesis/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0052.report.yaml` |
| Required verdict | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` or `GOVERNANCE_CAPABILITY_BASELINE_REJECTED` |

## Who you are

A fresh, independent **capability baseline synthesis verifier**, and the sole issuer of the iteration-1 Phase-2 verdict;
the orchestrator will not overrule it. Read `P2-HO-0043-verify-1-common-protocol.md` in full (and through it P2-HO-0000 and
P2-HO-0009 — their standard, schemas and prohibitions apply to you) and the frozen gate contract in full. Then read
`P2-HO-0007-audit-0-synthesis.md`: its "What you do" steps 1–7 and its outputs apply to you, for `cap2-candidate-1`, with
the changes below.

## Inputs — the verifications of record

| Run | Scope | Evidence |
|---|---|---|
| P2-AR-0044 | AC-14 R1 preservation | `verify-1/r1-preservation/` |
| P2-AR-0045 | AC-6 oracle format | `verify-1/oracle-format/` |
| P2-AR-0046 … 0051 | families alpha, beta, gamma, delta, epsilon, zeta | `verify-1/<family>/` (each with `heldout/RUN-ALL`) |

They are evidence, not verdicts. Verify, don't adopt: re-run each family's `heldout/RUN-ALL` (or a documented subset if one
is prohibitively slow — say which) and every probe behind a status you rely on for acceptance, a thin
`PRESENT_AND_SUBSTANTIAL`, or a blocking finding you classify. Correct any status or label you find wrong, with evidence.
The iteration-0 synthesis (`release/capability-baseline/audit-0/synthesis/`) is the inventory you measure against, not
evidence about this candidate.

## Changes from P2-HO-0007

1. **AC-14** is required for this candidate: adjudicate it from P2-AR-0044's evidence (re-run what you rely on).
   **AC-6**: adjudicate from P2-AR-0045's review; AC-6 fails unless the format is accepted by that fresh reviewer.
2. **AC-10** now has a product evidence map (round-4 BC-P2-02): regenerate the suite-to-contract matrix **with the product**
   (`gov contract verify` and the product's matrix generator), then check for a sample of owners per gate that the owner
   actually runs and exercises its capability. A capability with zero owners, or an owner that does not run, fails AC-10.
3. **AC-15**: run `cargo test --lib` and `cargo test --test certification` yourself on the candidate.
4. **AC-16**: exercise every listed cross-capability interaction end to end across family boundaries, including the
   cross-machine chain (P2-ADJ-0002) and the availability rule across scheduler, task, CIT, gate and update hosts.
5. **Convergence (frozen contract §8).** For every blocking finding: `RESIDUAL` (name the iteration-0 class) or
   `MATERIALLY_NEW`, with the reason; check and correct the families' labels. Group materially new blocking findings into
   new classes numbered from **BC-P2-53** (capability ID(s) plus mechanism; precise and non-overlapping). Produce
   `convergence.yaml`: per iteration-0 class `CLOSED | RESIDUAL | PARTIALLY_CLOSED` with evidence, the new classes, and
   `introduces_materially_new_blocker_classes: true | false`.
6. **Owner decisions.** Adjudicate every `owner_decision_required: true` flag as P2-HO-0007 step 7 says: a capability the
   contract already requires is not an owner decision. The owner decisions and adjudications in force are sources.

## Output

`release/capability-baseline/verify-1/synthesis/`: `00-SYNTHESIS-REPORT.md` (verdict first, then AC-1…AC-16 each HOLDS /
FAILS with evidence), the four matrices of P2-HO-0007, `blocker-classes.yaml` (iteration-0 classes with their iteration-1
state plus new classes), `convergence.yaml`, `findings.yaml` (your findings plus your disposition of every verifier finding:
CONFIRMED / CORRECTED / REFUTED, with evidence), `repair-delta.md` (if rejecting), `owner-decisions-required.md` (write
"none" explicitly if none), `later-lifecycle-notes.md`, `evidence/`.

Commit the evidence directory first, then your run report with that commit's hash, on the branch you are given. Do not
merge, rebase, tag or push.
