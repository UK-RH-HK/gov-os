# Phase-2 Context/Retrieval Bridge: orchestration domain (P2X-FAIL-1)

This directory holds **orchestration support only** (OD-P2-10 §3, OD-P2-10B). It is not the Governance OS product, not
a Phase-2 candidate, not an authority source, not Phase 3, and not V8.3 CURRENT.

**Resume from here, never from a conversation.** OD-BR-06 §8 sets a deterministic order. A fresh outer session,
after compaction or a session replacement, reads these in turn:

1. **`ORCHESTRATOR_STATE.yaml`** on the bridge branch. Get the worktree from
   `git -C /home/usain/Dynamic-Agentic-Engineering-OS worktree list | grep bridge-p2-orchestrator`, then run
   `python3 tools/check_state.py show` and `python3 tools/check_state.py verify`. Exit 2 means
   ORCHESTRATION_STATE_CONFLICT. **If `demonstration_freeze.status` is IN FORCE**, also read `PENDING-STATE-UPDATES.md`
   on the freeze side branch `bridge/orch-pending-*`.
2. **The latest validated outer checkpoint.** This is the highest-numbered `CHECKPOINTS/BR-CP-NNNN.yaml` across the
   bridge branch **and** any `bridge/orch-pending-*` side branch. Check that its `content_sha256` round-trips. Its
   `next_deterministic_action` is the current one; `state_next_action_as_sealed` may be stale during a freeze.
3. **`GATES/OWNER-DIRECTION-BR-0006-CONTEXT-RETRIEVAL-AND-CONTINUITY.md`**: the durable architecture and continuity
   requirements.
4. **The active owner decisions**:
   * the state's `owner_records`;
   * `GATES/OWNER-*.md`, which covers the launcher BR-0001, OC-BR-02, OD-BR-03, OD-BR-04, OD-BR-05 and OD-BR-06;
   * the Phase-2 OD-P2-10 and OD-P2-10A/B that `owner_records` names;
   * the orchestrator rulings `GATES/BR-ARCH-RULING-*.md`. These are **not** owner decisions.
5. **The latest ledger transition**: the newest `## BR-L-NNNN` in `PHASE_LEDGER.md`.
6. **The current handoff and running-work records**: the state's `running_work` and `handoffs`, and
   `HANDOFFS/BR-HO-NNNN-*.md` for every running run. Check liveness from each run's transcript and branch commits,
   **never from elapsed time**.
7. **Execute the next deterministic action.** After every material transition, write a checkpoint with
   `python3 tools/check_state.py checkpoint --reason "<transition>" [--next "<current action>"] --commit`
   (OD-BR-04/06). The PreCompact/SessionEnd hooks do this automatically **only where they are confirmed active**.
   Otherwise, checkpoint by hand before compaction and before closing the session.

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
