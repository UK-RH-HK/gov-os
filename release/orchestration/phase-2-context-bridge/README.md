# Phase-2 Context/Retrieval Bridge: orchestration domain (P2X-FAIL-1)

This directory holds **orchestration support only** (OD-P2-10 §3, OD-P2-10B). It is not the Governance OS product, not
a Phase-2 candidate, not an authority source, not Phase 3, and not V8.3 CURRENT.

**Resume from here, never from a conversation:**

```
git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree list | grep bridge-p2-orchestrator
cd <that worktree>          # branch bridge/p2-context-retrieval
python3 release/orchestration/phase-2-context-bridge/tools/check_state.py show
python3 release/orchestration/phase-2-context-bridge/tools/check_state.py verify   # exit 2 = ORCHESTRATION_STATE_CONFLICT
```

Then read `ORCHESTRATOR_STATE.yaml`, the newest `PHASE_LEDGER.md` entry and the newest `CHECKPOINTS/BR-CP-*.yaml`.
The owner's instructions for this lifecycle are in `GATES/OWNER-LAUNCHER-BR-0001-P2X-FAIL-1.md`, recorded verbatim.

| Path | Holds |
|---|---|
| `ORCHESTRATOR_STATE.yaml` | the sealed state, including the next deterministic action |
| `PHASE_LEDGER.md` | the narrative ledger, `BR-L-NNNN` |
| `GATES/` | the gate register, the owner launcher and the enforcement of each gate |
| `HANDOFFS/` | typed briefs to roles, `BR-HO-NNNN` |
| `AGENT_RUNS/` | run records plus each role's typed return (`.report.yaml`) and enforced checkpoint (`.checkpoint.yaml`) |
| `CHECKPOINTS/` | orchestrator checkpoints, `BR-CP-NNNN` |
| `EVIDENCE/` | preserved inputs, such as the Review-8 return, with provenance |
| `telemetry/` | model/provider identity per run; rebuild and freshness telemetry |
| `tools/check_state.py` | `show`, `verify` (includes the **mutation boundary**) and `integrate-check RUN` (the **enforced** pre-merge checkpoint) |

**The invariant `verify` enforces on every commit:** nothing outside this directory differs from the bridge base
commit `6e7a2a3`. The frozen product `3c880d8` and `release/orchestration/phase-2/` are therefore never touched.
