# Governance OS — Phase 2 orchestration control record

**Phase 2 — GOVERNANCE CAPABILITY BASELINE.** Target token `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`: the exhaustive
Capability Acceptance Contract v3 baseline audit and implementation closure, capability by capability, on one exact frozen
candidate.

This directory is the durable, repository-held memory of Phase 2. It holds facts, decisions, references to independent
evidence and commits, verdicts and the next deterministic action. It holds no product source and no hidden reasoning.
Phase-1 state under `release/orchestration/phase-1/` is never overwritten or reused.

| Path | Content |
|---|---|
| `ORCHESTRATOR_STATE.yaml` | machine-readable resumable state (lifecycle, candidates, runs, gates, findings, blocker classes, next action) |
| `PHASE_LEDGER.md` | append-only human-readable chronology (`P2-L-NNNN`) |
| `GATES/PHASE-2-FROZEN-GATE-CONTRACT.md` | the frozen acceptance criteria AC-1…AC-16 for this phase, hashed in the state file |
| `GATES/GATE-REGISTER.yaml` | every hard gate, its preconditions and satisfaction evidence |
| `HANDOFFS/P2-HO-*.md` | the task each receiving role reconstructs its work from |
| `AGENT_RUNS/P2-AR-*.run.yaml` / `.report.yaml` | claim/outcome (orchestrator) and typed report (the role itself) — schema in `AGENT_RUNS/README.md` |
| `CHECKPOINTS/P2-CP-*.yaml` | point-in-time state at checkpoint triggers |
| `tools/check_state.py` | `verify`, `seal`, `show` |
| `tools/product_identity.py` | `product_code_digest` / `governed_state_digest` for a commit (Contract v3 item 9) |

Evidence produced by Phase-2 roles lives under `release/capability-baseline/`.

## Resume (compaction or a fresh orchestrator session)

```sh
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 release/orchestration/phase-2/tools/check_state.py show     # lifecycle, candidate, gates, running work, next action
python3 release/orchestration/phase-2/tools/check_state.py verify   # exit 2 = ORCHESTRATION_STATE_CONFLICT
```

Then read the newest `CHECKPOINTS/P2-CP-*.yaml`. For every entry in `running_work`, look for its report; a run with no
`P2-AR-*.report.yaml` is **INCOMPLETE** and advances no gate — its branch is recorded, so it can be inspected or re-run by
a fresh agent. Execute `next_deterministic_action`. Never restart Phase 2 from conversational memory.

## Invariants

- The orchestrator routes and adjudicates provenance; it never issues a capability status or a Phase-2 verdict.
- Auditors, test authors and verifiers are fresh, isolated, and never modify product source.
- No role grades its own work. Builders never see held-out tests before that verifier's verdict is committed.
- Every product change mints a new immutable candidate (`cap2-candidate-N`) and invalidates dependent evidence
  (Contract v3 evidence freshness, Gate W); a candidate whose product code differs from `srr1-r1-accepted` needs an
  independent R1-preservation verification (frozen contract AC-14).
- Owner gates are presented to the product owner and never answered on their behalf.
- Nothing here starts Phase 3, selects a retrieval profile, certifies (R2/R3), publishes or merges to `main`.
