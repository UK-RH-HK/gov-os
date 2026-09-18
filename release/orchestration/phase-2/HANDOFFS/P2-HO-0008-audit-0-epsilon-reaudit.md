# P2-HO-0008 — Iteration-0 capability family RE-AUDIT: `epsilon`

| Field | Value |
|---|---|
| Handoff | P2-HO-0008 |
| From | Phase-2 orchestrator (routing only) |
| To | fresh independent `capability-family-auditor`, run **P2-AR-0008** — not P2-AR-0005 |
| Candidate | `cap2-candidate-0` (pinned identities in the common protocol) |
| Active gate | `GATE-P2-BASELINE-AUDIT-0` |
| Family | `epsilon` — scope, duties and governing trace exactly as in `P2-HO-0005-audit-0-epsilon.md` |
| Evidence directory | `release/capability-baseline/audit-0/epsilon-r/` |
| Run report | `release/orchestration/phase-2/AGENT_RUNS/P2-AR-0008.report.yaml` |
| Required verdict | `FAMILY_AUDIT_COMPLETE` or `INCOMPLETE` |

**Read in full, in this order:** `P2-HO-0000-audit-0-common-protocol.md` (the standard, schemas and prohibitions — all
apply unchanged), `P2-HO-0005-audit-0-epsilon.md` (your scope: O1–O5, P1–P2, Q1–Q4, U, V1–V4; the AC-5 health-scheduler
audit; the AC-6 oracle-format determination), the frozen gate contract, and `AGENT_RUNS/README.md`.

## Why this family is being re-audited

An earlier epsilon audit (P2-AR-0005) was recorded by the orchestrator as **COMPLETED_NONCONFORMING** with the common
protocol's evidence standard: several bullet statuses rested on printed assertions rather than demonstrated behaviour,
and some capability statuses were inconsistent with the same run's own findings. Its evidence is retained unchanged as
a historical record. You re-audit the family from scratch.

**Do not read `release/capability-baseline/audit-0/epsilon/` or `AGENT_RUNS/P2-AR-0005.*`** — your judgement must not be
anchored on it. Do not read other families' evidence either.

## The evidence standard, restated (it is the common protocol's, not a new one)

- **Each bullet needs its own demonstration.** A printed `echo` of what the product is believed to do is not evidence; a
  help string or a flag's existence is not evidence. Show the behaviour: construct the input, run the product, capture
  the observable result that proves or disproves the bullet.
- **A bullet's status may not contradict a finding.** If you record a gap for a bullet, that bullet is not
  `PRESENT_AND_SUBSTANTIAL`; if any bullet of a capability is not `PRESENT_AND_SUBSTANTIAL`, neither is the capability
  (frozen contract §4).
- **Blocking is determined by the frozen acceptance criteria, not by severity labels.** A gap that leaves an AC unmet is
  blocking (frozen contract §6). AC-5 names its required behaviours explicitly — impacted-test selection driven by a real
  mutation, parallel execution of independent checks, isolation, cache reuse, cache invalidation, stale evidence,
  RED/YELLOW/GREEN aggregation, hard-block vs warning, provenance, remediation/task generation, and not serially re-running
  the whole suite on a trivial mutation. Each is exercised or recorded as unmet.
- **A failing observation is recorded as failing.** If a probe's output shows an error or an UNHEALTHY verdict, explain it;
  do not record the interaction as passing.
- **SLOs (U) mean tracked AND thresholded.** For each U metric, show where it is computed, where its threshold lives, and
  a run in which crossing the threshold changes the health state. Each of the thirteen HEALTHY conditions: show the check
  that enforces it and a run in which violating it flips the state.
- **Owner decisions** only where closing a gap needs a choice the accepted sources do not make. That the contract requires
  something the product lacks is not an owner decision.

Worktree, branch and commit procedure are given in your dispatch message.
