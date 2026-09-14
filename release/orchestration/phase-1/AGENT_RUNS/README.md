# Agent runs

Each spawned role has two files:
- **`AR-NNNN.run.yaml`**, written by the orchestrator. It is the claim: role, handoff, worktree, branch, base commit and
  status. The orchestrator also records the outcome here.
- **`AR-NNNN.report.yaml`**, written by the agent itself. It is mandatory. A run without a report is `INCOMPLETE` and
  advances no gate.

Commit the work product first. Then write the report with that commit's hash in `output.commit` and commit the report.
A commit cannot name its own hash.

## Report schema (`governance-os.phase-1.agent-report`, version 1)

```yaml
schema: governance-os.phase-1.agent-report
schema_version: 1
run_id: AR-NNNN
role: <see vocabulary>
objective: <one line>
agent_model: claude-opus-5
independence_statement: <what this run authored before, what it did and did not read>
input:
  base_commit: <full sha>
  release: <version / tag / null>
  handoff: release/orchestration/phase-1/HANDOFFS/HO-NNNN-*.md
inspected: [<paths, commits>]
produced: [<paths>]
tests_or_attacks:
  - id: <id>
    description: <one line>
    result: <PASS | FAIL | FLIPPED | NOT_FLIPPED | CONFIRMED | REFUTED | NOT_RUN | ERROR>
    evidence_path: <path>
findings:
  - id: <id>
    severity: <CRITICAL | HIGH | MEDIUM | LOW | INFO>
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
| `rot-architect` | `ARCHITECTURE_REVISION_READY_FOR_REVIEW`, `INCOMPLETE` |
| `rot-reviewer-trust-security` | `BLOCKING_FINDINGS_PRESENT`, `NO_BLOCKING_FINDINGS` |
| `rot-reviewer-compat-transaction` | `BLOCKING_FINDINGS_PRESENT`, `NO_BLOCKING_FINDINGS` |
| `rot-review-synthesis` | `ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED`, `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` |
| `rot-specialist-architect` / `rot-synthesis-architect` (escalation) | `ALTERNATIVE_PROPOSED`, `ARCHITECTURE_REVISION_READY_FOR_REVIEW` |
| `builder` / `repair-builder` | `AWAITING_PRODUCT_OWNER_CAPABILITY_CONTRACT_UPLOAD`, `READY_FOR_INDEPENDENT_OS_VERIFICATION`, `INCOMPLETE` |
| `verifier-a` / `verifier-b` | `BLOCKING_FINDINGS_PRESENT`, `NO_BLOCKING_FINDINGS` |
| `prompt2-synthesis` | `OS_RELEASE_CANDIDATE_ACCEPTED`, `OS_RELEASE_CANDIDATE_REJECTED` |
