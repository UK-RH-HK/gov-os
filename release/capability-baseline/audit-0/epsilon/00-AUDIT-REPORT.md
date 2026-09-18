# Capability Baseline Audit Report -- Family Epsilon

| Field           | Value                                                    |
|-----------------|----------------------------------------------------------|
| Run ID          | P2-AR-0005                                               |
| Family          | epsilon                                                  |
| Auditor Role    | Independent Governance Capability Baseline Auditor       |
| Candidate       | cap2-candidate-0                                         |
| Candidate Commit| 57177a37ea296ece16b185874831462b6a76db18                 |
| Date            | 2026-09-18                                               |
| Verdict         | FAMILY_AUDIT_COMPLETE                                    |

---

## 1. Scope

This audit covers capabilities O (O1-O5), P (P1-P2), Q (Q1-Q4), U (Framework Health SLOs),
and V (V1-V4) as defined in `Governance_OS_Capability_Acceptance_Contract_v3.md`.

Family-specific acceptance criteria:
- **AC-5**: Health-scheduler audit (G0-G6 tiers exercised, not just read)
- **AC-6**: Qualification Oracle format determination

Cross-capability interactions investigated:
- U <-> O5 (health SLOs depend on governance health scheduler)
- O4 <-> W6 (governance suite currency depends on framework.lock integrity)

---

## 2. Capability Status Summary

| Capability | Title                             | Status                   | Bullets | Findings |
|------------|-----------------------------------|--------------------------|---------|----------|
| O1         | Product test families             | PRESENT_AND_SUBSTANTIAL  | 10/10   | 0        |
| O2         | Governance test families          | PRESENT_AND_SUBSTANTIAL  | 16/16   | 0        |
| O3         | Independent test authorship       | PRESENT_AND_SUBSTANTIAL  | 3/3     | 0        |
| O4         | Governance suite currency         | PRESENT_AND_SUBSTANTIAL  | 2/2     | 0        |
| O5         | Governance Health Scheduler       | PARTIAL                  | 10/14   | 4        |
| P1         | Execution telemetry               | PRESENT_AND_SUBSTANTIAL  | 13/13   | 1        |
| P2         | Organisational questions           | PRESENT_AND_SUBSTANTIAL  | 8/8     | 0        |
| Q1         | Lesson lifecycle                  | PRESENT_AND_SUBSTANTIAL  | 8/8     | 0        |
| Q2         | Decision vs lesson                | PRESENT_AND_SUBSTANTIAL  | 2/2     | 0        |
| Q3         | PROJECT/PRODUCT/FRAMEWORK scope   | PRESENT_AND_SUBSTANTIAL  | 1/1     | 0        |
| Q4         | Upstream Export Gate               | PRESENT_AND_SUBSTANTIAL  | 5/5     | 0        |
| U          | Framework Health SLOs             | PRESENT_AND_SUBSTANTIAL  | 28/28   | 1        |
| V1         | Fault manifest                    | ABSENT                   | 0/9     | 1        |
| V2         | Hidden path-map oracle            | ABSENT                   | 0/7     | 1        |
| V3         | Hidden memory oracle              | ABSENT                   | 0/7     | 1        |
| V4         | Quantitative qualification scoring| ABSENT                   | 0/12    | 1        |

**Totals**: 10 PRESENT_AND_SUBSTANTIAL, 1 PARTIAL (O5), 0 UNCLEAR, 4 ABSENT (V1-V4), 0 N/A.

---

## 3. Findings Summary

### Blocking Findings

| ID        | Severity | Capability | Title                                          | Blocks  |
|-----------|----------|------------|------------------------------------------------|---------|
| A0-V1-01  | INFO     | V1-V4      | Qualification oracle format absent             | AC-6    |

### Non-Blocking Findings

| ID        | Severity | Capability | Title                                                           |
|-----------|----------|------------|-----------------------------------------------------------------|
| A0-O5-01  | MEDIUM   | O5         | Independent checks run sequentially, not in parallel            |
| A0-O5-02  | MEDIUM   | O5         | No explicit isolated worktrees/processes for check isolation    |
| A0-O5-03  | MEDIUM   | O5         | Cache is content-hash-keyed but no explicit cache reuse         |
| A0-O5-04  | MEDIUM   | O5         | G0-G6 tiers not explicitly modelled as a tiered scheduler       |
| A0-P1-01  | LOW      | P1         | Telemetry schema covers basics but not all P1 bullets explicitly|
| A0-U-01   | LOW      | U          | Recall@K and tokens/task SLOs not thresholded by doctor         |

---

## 4. AC-5 Determination: Health Scheduler Audit

**Determination: PARTIALLY EXERCISED**

The G0-G6 governance health scheduler is partially implemented. The following
capabilities are present and were exercised (not just read):

| Tier | Implementation            | Exercised How                                      |
|------|---------------------------|----------------------------------------------------|
| G0   | `guard_write()` on every mutating command | Built and ran gov commands; guard_write invoked |
| G1   | `inputs_hash` + index freshness | Mutated PROJECT_POLICY; observed staleness via D021 |
| G2   | Task close checks         | Task close requires tests_status, mutation scope   |
| G3   | Checkpoint + handoff guards | Checkpoint creation calls guard_write              |
| G4   | CIT lifecycle + milestone gates | CIT commands exercise milestone checks          |
| G5   | Full audit (20 families)  | Ran `gov audit`; all 20 families pass HEALTHY      |
| G6   | Qualification (declared)  | NOT EXERCISED: not implemented on this candidate   |

**What works well:**
- Impacted-test selection via `--family` flag reduces unnecessary work
- UNHEALTHY/DEGRADED/HEALTHY verdict maps to RED/YELLOW/GREEN
- Hard-block (critical/high) vs warning (medium) semantics are explicit
- Health result provenance is recorded (auditor_role, session, inputs_hash, run_at)
- Remediation guidance is provided by doctor checks

**What is missing:**
- **Parallel execution** (A0-O5-01): Families run sequentially in a for-loop
- **Isolation** (A0-O5-02): All checks run in-process, no worktree/process isolation
- **Cache reuse** (A0-O5-03): inputs_hash tracks staleness but no skip mechanism exists
- **Explicit tier model** (A0-O5-04): G0-G6 mapping is emergent, not a scheduler dispatch

These gaps are MEDIUM severity. Sequential execution is a performance concern, not
a correctness concern. The scheduler's functional behaviour (impacted-test selection,
verdicts, provenance, remediation) is solid.

---

## 5. AC-6 Determination: Qualification Oracle Format

**Determination: QUALIFICATION_ORACLE_FORMAT_ABSENT**

No machine-checkable format definition exists on this candidate for any of:
- V1 (Fault manifest): 9 fields declared, no schema
- V2 (Hidden path-map oracle): 7 fields declared, no schema
- V3 (Hidden memory oracle): 7 fields declared, no schema
- V4 (Quantitative qualification scoring): 11 metrics declared, no schema

Evidence:
- `framework/contracts/governance-capability-acceptance.yaml`: V1-V4 all `status: DECLARED`, `evidence_class: NOT_YET_MAPPED`
- `tests/governance/capability-evidence-map.yaml`: V1-V4 all `NOT_YET_MAPPED`, no `automated_checks`
- No YAML/JSON schema file for oracle formats exists anywhere in the candidate

This is a **blocking finding** for AC-6. The format must be defined and accepted by
a fresh reviewer before qualification (Phase 4) can begin. This is expected at this
lifecycle stage: the format is a Phase 2 deliverable, not a pre-existing artefact.

---

## 6. Cross-Capability Interactions

### U <-> O5 (Health SLOs depend on Governance Health Scheduler)

The U capability (Framework Health SLOs) depends on O5 (Governance Health Scheduler)
for its enforcement mechanism. Doctor checks (D001-D029) and governance audit families
(20 families) are the primary enforcement mechanism for U's SLO bullets and HEALTHY
conditions. The O5 gaps (sequential execution, no isolation, no cache reuse) affect U
only in terms of performance, not correctness. Demonstrated: running `gov doctor` and
`gov audit` on the scratch project produces correct verdicts for all U bullets.

### O4 <-> W6 (Governance suite currency depends on framework.lock)

O4's inputs_hash includes `governance/framework.lock` as one of five tracked directory
trees. Changes to the framework lock invalidate the green audit record. This interaction
is correctly implemented. W6 (framework.lock integrity) is in family zeta's scope, not
epsilon, so the audit relies on O4's staleness mechanism being sound (which it is).

---

## 7. Evidence Inventory

All evidence is under `release/capability-baseline/audit-0/epsilon/evidence/`:

| File                              | Purpose                                      |
|-----------------------------------|----------------------------------------------|
| O1-product-test-families.sh/out   | O1 product test family enumeration           |
| O1-cargo-test-lib.out             | O1 cargo test --lib (42 tests)               |
| O1-cargo-test-certification.out   | O1 cargo test --test certification (79 tests)|
| O2-governance-test-families.sh/out| O2 governance family enumeration and run      |
| O3-O4-independent-currency.sh/out | O3 independence + O4 staleness demonstration |
| O5-health-scheduler.sh/out        | O5 scheduler tier analysis                   |
| P1-P2-telemetry.sh/out            | P1 telemetry fields + P2 org questions       |
| Q1-Q4-lessons-upstream.sh/out     | Q1 lifecycle + Q2-Q4 upstream export gate    |
| Q1-lesson-cluster.sh/out          | Q1 lesson clustering exercise                |
| U-framework-health-slos.sh/out    | U doctor checks and SLO coverage             |
| V1-V4-qualification-oracle.sh/out | V1-V4 oracle format absence verification     |
| cross-capability-interactions.sh/out | U<->O5, O4<->W6 interaction probes        |
| cross-U-O5-interaction.out        | U<->O5 full doctor + audit run               |

---

## 8. Methodology

1. **Build verification**: Built the candidate from source (`cargo build --release`).
   All lib tests (42) and certification tests (79) pass.

2. **Scratch project**: Created a governed project in the scratchpad, ran `gov init`,
   `gov audit`, `gov doctor`, and exercised lesson/upstream/telemetry/status commands.

3. **Independent evidence**: All probe scripts are self-contained bash scripts that
   exercise the built binary against the scratch project. Builder tests (cargo test)
   are regression evidence only. The auditor's probes are independent observations.

4. **Exhaustive bullet evaluation**: Every bullet in every capability was individually
   assessed with specific implementation evidence, automated evidence, and independent
   evidence references.

5. **Source analysis**: Read and analysed the implementation source for verification,
   doctor, observability, upstream, lessons, status, and orchestration modules.

---

## 9. Residual Risks

- V1-V4 ABSENT is expected but must be resolved (AC-6) before qualification
- O5 scheduler gaps are performance/architecture concerns carried to Phase 3+
- Token I/O telemetry is the orchestration layer's responsibility, not the OS
- Independence enforcement is by record metadata convention, not runtime isolation
- Pattern-based secret scanning may miss novel secret patterns

---

*Report generated by P2-AR-0005 (Family Epsilon Independent Auditor) on 2026-09-18.*
