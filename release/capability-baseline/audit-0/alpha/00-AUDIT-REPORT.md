# P2-AR-0001 Iteration-0 Capability Baseline Audit: Alpha Family

**Run ID:** P2-AR-0001
**Family:** alpha (Gates A, B, S, T)
**Candidate:** cap2-candidate-0
**Date:** 2026-09-18
**Auditor role:** independent-auditor (L0)
**Branch:** release/4.1.6-rc1
**Candidate commit:** 57177a37ea296ece16b185874831462b6a76db18

## Executive Summary

The alpha family audit covers 17 capabilities across four gates:
- **Gate A** (Constitutional and Trust Foundations): A1-A5
- **Gate B** (Repository Contract, Paths and State): B1-B3
- **Gate S** (Release, Distribution, Init, Adopt and Update): S1-S6
- **Gate T** (Independent Adoption and Audit Roles): T1-T3

**Verdict: FAMILY_AUDIT_COMPLETE**

| Status | Count |
|--------|-------|
| PRESENT_AND_SUBSTANTIAL | 16 |
| PARTIAL | 1 |
| ABSENT | 0 |
| UNCLEAR | 0 |
| N/A_WITH_REASON | 0 |

The single PARTIAL capability (B2 Path Map) has one missing feature set
(RENAME/SPLIT/MERGE target actions) that is non-blocking because existing
actions can compose to achieve the same results. An owner decision is required
on whether to implement these or amend the contract.

## Evidence Method

All evidence is executable. The audit:

1. Built the product binary (`cargo build --release`) from the candidate commit
2. Drove `gov init` on a greenfield scratch project to exercise A1-A5, B1-B3
3. Drove `gov adopt` stages A0-A6 on the brownfield fixture (`tests/fixtures/brownfield-legacy/`)
4. Built and verified a test release (`gov release build`, `gov release verify`)
5. Probed emergency controls (PAUSE, FREEZE_WRITES, CANCEL_AGENTS, RESUME)
6. Tested authority enforcement (L1 role refused L3 operation)
7. Tested kernel tamper detection (modified CONSTITUTION.md, detected by trust check)
8. Ran the full regression suite (42 lib + 79 certification = 121 tests, 0 failures)

No product source was modified. All evidence files are under
`release/capability-baseline/audit-0/alpha/evidence/`.

## Per-Gate Summary

### Gate A: Constitutional and Trust Foundations

| Cap | Status | Findings |
|-----|--------|----------|
| A1 | PRESENT_AND_SUBSTANTIAL | None |
| A2 | PRESENT_AND_SUBSTANTIAL | None |
| A3 | PRESENT_AND_SUBSTANTIAL | None |
| A4 | PRESENT_AND_SUBSTANTIAL | None |
| A5 | PRESENT_AND_SUBSTANTIAL | A0-A5-01 (INFO) |

All five capabilities have executable evidence for every bullet. Policy
precedence enforcement is thoroughly demonstrated with floor, additive, and
immutable modes refusing weakening attempts. The Signed Release Root (SRR)
architecture routes all lifecycle ingresses through a single admit function.
Emergency controls are deterministic and authority-gated.

### Gate B: Repository Contract, Paths and State

| Cap | Status | Findings |
|-----|--------|----------|
| B1 | PRESENT_AND_SUBSTANTIAL | None |
| B2 | PARTIAL | A0-B2-01 (MEDIUM) |
| B3 | PRESENT_AND_SUBSTANTIAL | None |

B2 is PARTIAL because RENAME, SPLIT, and MERGE target actions are not
implemented in the migration planner. The five existing actions (KEEP, MOVE,
EXTRACT, RETIRE, DELETE_FROM_ACTIVE_TREE) can compose to achieve the same
outcomes, so this gap is ergonomic rather than functional. Owner decision
required.

### Gate S: Release, Distribution, Init, Adopt and Update

| Cap | Status | Findings |
|-----|--------|----------|
| S1 | PRESENT_AND_SUBSTANTIAL | None |
| S2 | PRESENT_AND_SUBSTANTIAL | None |
| S3 | PRESENT_AND_SUBSTANTIAL | None |
| S4 | PRESENT_AND_SUBSTANTIAL | None |
| S5 | PRESENT_AND_SUBSTANTIAL | None |
| S6 | PRESENT_AND_SUBSTANTIAL | None |

All six capabilities have executable evidence. The adoption pipeline (S4) was
exercised end-to-end on a brownfield fixture through stages A0-A6 with session
independence enforcement demonstrated (same session as planner refused for
review). Migration A6 correctly rolled back batch 1 on test failure.

### Gate T: Independent Adoption and Audit Roles

| Cap | Status | Findings |
|-----|--------|----------|
| T1 | PRESENT_AND_SUBSTANTIAL | A0-T1-01 (LOW), A0-T1-02 (LOW) |
| T2 | PRESENT_AND_SUBSTANTIAL | None |
| T3 | PRESENT_AND_SUBSTANTIAL | None |

All named roles are functionally present. Recovery-agent and
adoption-auditor/planner are subsumed by orchestrator and independent-auditor
respectively, with authority and session independence providing equivalent
separation. The LOW findings note the naming gap for potential future
improvement.

## Findings Summary

| ID | Severity | Capability | Blocking | Summary |
|----|----------|------------|----------|---------|
| A0-B2-01 | MEDIUM | B2 | No | RENAME/SPLIT/MERGE target actions not implemented |
| A0-T1-01 | LOW | T1 | No | No dedicated recovery-agent role |
| A0-T1-02 | LOW | T1 | No | No dedicated adoption-auditor/planner role |
| A0-A5-01 | INFO | A5 | No | ROLLBACK_TRANSACTION is context-specific, not a standalone command |

No findings are blocking. One finding (A0-B2-01) requires an owner decision on
whether to implement the missing target actions or amend the contract.

## Regression Suite

- **Library tests:** 42 passed, 0 failed
- **Certification tests:** 79 passed, 0 failed
- **Total:** 121 passed, 0 failed

## Cross-Capability Observations

1. **SRR routing** (cross-capability-S-A2.out): All three lifecycle ingresses
   (init, adopt, update) route through `crate::srr::admit()`, confirming a
   single non-circular trust root.

2. **Policy precedence is enforced at multiple layers**: Kernel trust (A2)
   gates operations before policy evaluation (A1) before authority checks (A3).

3. **Session independence** (T2) is enforced structurally: the same session ID
   used for planning is rejected for review, demonstrated in S4 evidence.

## Deliverables

- `capability-audit.yaml` -- machine-readable per-capability audit
- `findings.yaml` -- machine-readable findings
- `evidence/` -- 15 executable evidence files
- `00-AUDIT-REPORT.md` -- this report
