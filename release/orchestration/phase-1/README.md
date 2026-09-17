# Governance OS — Phase 1 orchestration control record

This directory is the durable, repository-held memory of Phase 1. The historical CP-1/RoT-1 revision loop is frozen at
revision 7. OWNER-DIRECTIVE-0004 rebased the active path to the separate Signed Release Root lineage (D-0009/ARCH-0003),
whose next action is fresh R0 architecture review. This directory holds no product source, no evidence of its own, and no
hidden reasoning. It holds only:
- facts and decisions;
- references to independent evidence and commits;
- verdicts;
- the next deterministic action.

| Path | Content |
|---|---|
| `ORCHESTRATOR_STATE.yaml` | machine-readable resumable state (lifecycle, commits, runs, gates, findings, next action) |
| `PHASE_1_LEDGER.md` | append-only human-readable chronology |
| `GATES/GATE-REGISTER.yaml` | every hard gate, its preconditions and its satisfaction evidence |
| `HANDOFFS/HO-*.md` | the task a receiving role reconstructs its work from |
| `AGENT_RUNS/AR-*.run.yaml` | claim and outcome record for each spawned role |
| `AGENT_RUNS/AR-*.report.yaml` | typed report written by the role itself (schema in `AGENT_RUNS/README.md`) |
| `CHECKPOINTS/CP-*.yaml` | point-in-time copies of the state at checkpoint triggers |
| `tools/check_state.py` | `verify`, `seal` and `show` (non-product tooling) |

## Current operator UI

The sole current canonical operator interface is
[`release/orchestration/control-panel/Governance_OS_Interactive_Stage_Control_Panel_FINAL_AUDITED_v8_1.html`](../control-panel/Governance_OS_Interactive_Stage_Control_Panel_FINAL_AUDITED_v8_1.html),
SHA-256 `54730e8e0b8b14bfac7280b52fc6593c8e72dc4e35782fd051aed4af36bc585d`.
Its classification is `NON_NORMATIVE_OPERATOR_UI`: it is an orchestration/runbook interface and does not establish or
change Governance OS authority. Earlier root control-panel copies remain recoverable from Git history but are not
current operator interfaces.

## Resume (compaction or a fresh orchestrator session)

Governance OS has no `gov orchestration resume phase-1` command yet. Until it does, the equivalent is:

```sh
cd /home/usain/Dynamic-Agentic-Engineering-OS
python3 release/orchestration/phase-1/tools/check_state.py show     # lifecycle, gates, running work, next action
python3 release/orchestration/phase-1/tools/check_state.py verify   # exit 2 = ORCHESTRATION_STATE_CONFLICT
```

Then:
1. Read the newest `CHECKPOINTS/CP-*.yaml`.
2. Read only the evidence named for the current stage.
3. For every entry in `running_work`, find its report. A run with no `AR-*.report.yaml` is **INCOMPLETE** and advances
   no gate. Its worktree and branch are recorded, so it may be inspected or re-run by a fresh agent.
4. Execute `next_deterministic_action`.

Never restart Phase 1 from memory. If `verify` fails, reconcile Git and the record before any automatic continuation.

## Invariants

- The orchestrator routes; it never issues an independent verdict.
- Rejected evidence is never rewritten.
- Independent reviewers and verifiers never modify product source.
- Builders never see held-out verifier tests before that verifier's verdict is committed.
- Owner gates are presented to the product owner and never answered on their behalf.
- The Capability Acceptance Contract is supplied by the owner and never reconstructed.
- Nothing here certifies a release, starts Phase 2 or pushes a stable release.
- CP-1/RoT-1 receives no Revision 8; its evidence remains immutable and it is not the active Phase-1 target.
- R0 architecture acceptance, R1 candidate acceptance, R2 standard release certification and optional R3
  high-assurance qualification are separate gates.
- A review finding blocks only the gate whose normative source and lifecycle it matches; stronger proposals require
  owner adoption.
