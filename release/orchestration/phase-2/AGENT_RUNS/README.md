# Phase 2 agent runs

Run identifiers are phase-qualified (`P2-AR-NNNN`) so they never collide with Phase-1 `AR-NNNN` records.

Each spawned role has two files:
- **`P2-AR-NNNN.run.yaml`**, written by the orchestrator: the claim — role, handoff, worktree, branch, base commit, candidate
  and status. The orchestrator also records the outcome here.
- **`P2-AR-NNNN.report.yaml`**, written by the agent itself. Mandatory. A run without a report is `INCOMPLETE` and advances no gate.

Commit the work product first. Then write the report with that commit's hash in `output.commit` and commit the report.
A commit cannot name its own hash.

## Report schema (`governance-os.phase-2.agent-report`, version 1)

```yaml
schema: governance-os.phase-2.agent-report
schema_version: 1
run_id: P2-AR-NNNN
role: <see vocabulary>
objective: <one line>
agent_model: claude-opus-5
independence_statement: <what this run authored before, what it did and did not read>
input:
  base_commit: <full sha>
  candidate: <cap2-candidate-N>
  product_code_digest: <64 hex>
  contract_v3_sha256: 4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3
  frozen_gate_contract_sha256: <64 hex>
  handoff: release/orchestration/phase-2/HANDOFFS/P2-HO-NNNN-*.md
inspected: [<paths, commits>]
produced: [<paths>]
tests_or_attacks:
  - id: <id>
    description: <one line>
    result: <PASS | FAIL | CONFIRMED | REFUTED | NOT_RUN | ERROR>
    evidence_path: <path>
capability_status_summary:        # auditors/verifiers only
  PRESENT_AND_SUBSTANTIAL: <n>
  PARTIAL: <n>
  ABSENT: <n>
  UNCLEAR: <n>
  N/A_WITH_REASON: <n>
findings:
  - id: <id>
    severity: <CRITICAL | HIGH | MEDIUM | LOW | INFO>
    capability: <id(s)>
    blocking: <true | false>
    blocker_class: <class id or null>
    new_vs_residual: <MATERIALLY_NEW | RESIDUAL | BASELINE>
    owner_decision_required: <true | false>
    title: <one line>
    path: <file holding the full statement>
verdict: <role verdict vocabulary>
output:
  branch: <branch>
  commit: <full sha of the work-product commit>
  evidence_path: <directory>
unresolved: [<ids or one-line items>]
recommended_next_action: <one line>
completed_at: <UTC ISO-8601>
```

Store facts, evidence and verdicts only. No private reasoning.

## Role and verdict vocabulary

| Role | Verdicts |
|---|---|
| `capability-family-auditor` | `FAMILY_AUDIT_COMPLETE`, `INCOMPLETE` |
| `capability-baseline-synthesis` | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`, `GOVERNANCE_CAPABILITY_BASELINE_REJECTED` |
| `capability-builder` / `capability-repair` | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`, `OWNER_DECISION_REQUIRED`, `INCOMPLETE` |
| `independent-test-author` | `HELD_OUT_TESTS_COMMITTED`, `INCOMPLETE` |
| `r1-preservation-verifier` | `R1_ACCEPTANCE_PRESERVED`, `R1_ACCEPTANCE_NOT_PRESERVED` |
| `oracle-format-reviewer` | `QUALIFICATION_ORACLE_FORMAT_ACCEPTED`, `QUALIFICATION_ORACLE_FORMAT_REJECTED` |
| `capability-verifier` | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`, `GOVERNANCE_CAPABILITY_BASELINE_REJECTED` |
