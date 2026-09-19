# P2-HO-ORCH-0002 — Orchestrator continuity handoff: SAFE HOLD (usage limit)

| Field | Value |
|---|---|
| Written | 2026-09-19, by the Phase-2 outer orchestrator, on the owner's USAGE-PRESERVATION / SAFE-HOLD order |
| For | this session after the owner confirms the usage reset, or a fresh replacement outer orchestrator launched with the V8.2 launcher |
| Supersedes | `P2-HO-ORCH-0001-orchestrator-continuity.md` (kept as history; its conventions and hazards still apply) |
| Authority | Durable state wins over this note. First run `python3 release/orchestration/phase-2/tools/check_state.py show`, then `verify`, then read `CHECKPOINTS/P2-CP-0008.yaml`. |

## Hold rule (owner, 2026-09-19)

Do **not** start any builder, integration, candidate minting, independent verification or repair round until the owner
**explicitly** says the usage limit has reset. Do not launch replacement or follow-on agents. Model routing (`model: "opus"`
on every Agent call) and the acceptance criteria (frozen gate contract, SHA-256 `d2f33e89…a26a9f25e`) are unchanged.

## Where Phase 2 stands

- Branch `release/4.1.6-rc1`. Candidate `cap2-candidate-0` REJECTED (P2-AR-0007: 52 classes BC-P2-01…52, 134 blocking
  findings). `cap2-candidate-1` **not minted**.
- Repair iteration 1: rounds 1–3 integrated and merged; last product merge **`e4cb662`** (`product_code_digest`
  `1d3e9f59…85df7`, `governed_state_digest` `2514b9fb…35be`; orchestrator reproduced lib 262/0, certification 189/0).
- **Round 4** (from `cae2f67`), both builders still working when the hold was ordered — the orchestrator did not stop them:
  - **P2-AR-0042** BC-P2-02 evidence map, handoff P2-HO-0041, branch `phase2/repair-1-r4-ws01` — at hold: tip `9bafcb3`
    (2 commits), 9 uncommitted files snapshotted to `refs/safe-hold/P2-AR-0042` (`7d94516`), no report yet.
  - **P2-AR-0043** residual integration points (INT3-O1/O2, WS-2/3/4/6/7/8/9 IPs), handoff P2-HO-0042, branch
    `phase2/repair-1-r4-residual` — at hold: no commits, 26 uncommitted files snapshotted to `refs/safe-hold/P2-AR-0043`
    (`b7e1e55`), no report yet.
  - Snapshots were made with a temporary index (the builders' worktrees, indexes and branches were not touched). They are
    recovery material, not builder commits.
- Verification iteration 1 is prepared, not dispatched: handoffs P2-HO-0043…0047 (commit `d267f97`), runs P2-AR-0044…0052
  reserved.
- No owner gate pending. Adjudications in force: P2-ADJ-0001, -0002, -0003. Owner decisions: OD-P2-01 A, OD-P2-02 A.

## Resume procedure (after the owner confirms the reset)

1. `check_state.py show` and `verify` must print `STATE_CONSISTENT`; otherwise stop with `PHASE_STATE_CONFLICT`.
2. **Determine each round-4 run's state** from Git only (never from transcripts or task-output stores):
   - report present — `git cat-file -e phase2/repair-1-r4-ws01:release/orchestration/phase-2/AGENT_RUNS/P2-AR-0042.report.yaml`
     (same for `-residual` / `P2-AR-0043`) → **completed**: verify scope against its handoff, record it
     (`tools/record_builder_round.py P2-AR-00NN <ws01|residual> "<notes>" r4`; it reads
     `release/capability-baseline/repair-1/r4-<ws>/claims.yaml`), status `COMPLETED_AWAITING_INTEGRATION`, prune
     `running_work`, seal, verify, commit.
   - no report, and the agent is still live in this session → wait for its completion notice.
   - no report and no live agent → **INCOMPLETE**. Preserve first: if the worktree still exists and has uncommitted work,
     snapshot it again to `refs/safe-hold/<run>-2` (temporary `GIT_INDEX_FILE`, `read-tree HEAD`, `add -A`, `write-tree`,
     `commit-tree -p HEAD`, `update-ref`); if the worktree is gone (e.g. `/tmp` cleared), the branch commits and
     `refs/safe-hold/<run>` are what remain. Then dispatch a **fresh** builder (model `opus`) from the same handoff on a new
     branch `phase2/repair-1-r4-<ws>-b` created from the release-branch HEAD; tell it the prior branch tip and the
     safe-hold ref exist as **unverified prior work it may inspect and reuse on its own judgement** (never as evidence);
     claim a new run id (next free after P2-AR-0052, e.g. P2-AR-0053), mark the old run `INCOMPLETE_SAFE_HOLD` in its run
     record and state.
3. **When both round-4 runs are completed:** merge both into `release/4.1.6-rc1` with `--no-ff` if they merge cleanly and
   `gov contract verify` passes on the merged tree; otherwise dispatch a fresh integration builder (model `opus`) with a
   short integration handoff. Reproduce `cargo build --release` (0 warnings), `cargo test --lib`, `cargo test --test
   certification` yourself (background shell: `. "$HOME/.cargo/env"` first — `cargo` is not on the background PATH).
4. **Mint `cap2-candidate-1`:** tag the merge commit, record `product_code_digest` / `governed_state_digest` in
   `candidates` and `current_candidate`, reopen `GATE-P2-R1-PRESERVATION` for it.
5. **Verification iteration 1:** fill the candidate identity into the dispatch messages of P2-HO-0043…0047 and dispatch, all
   fresh, `model: "opus"`, isolated worktrees from one orchestration commit whose digests equal the tag's: P2-AR-0044
   (AC-14, P2-HO-0045), P2-AR-0045 (AC-6, P2-HO-0046), P2-AR-0046…0051 (families alpha…zeta, P2-HO-0044), then — after
   merging their evidence — P2-AR-0052 synthesis (P2-HO-0047).
6. If REJECTED: check convergence labels (frozen contract §8), then repair iteration 2 from the new delta; stop with
   `PHASE_CONVERGENCE_ESCALATION_REQUIRED` at three consecutive iterations with materially new classes. If ACCEPTED:
   finalise; do not start Phase 3.

## Open items to carry

- 52 iteration-0 classes all open pending independent verification (builder claims recorded per run).
- Not routed, for the verifier: INT3-O4 (legacy unsealed task/CIT records reported `os_managed_unbound`, never blessed);
  R3-WS5-11 (not reproduced in integration-3).
- Whatever remaining IPs the round-4 reports list — route into the integration step or iteration-2 repair.
- WS-2 left one superseded R1 output file in `r3-ws02/evidence/` (`rm` denied); harmless.

## Hazards (in addition to P2-HO-ORCH-0001's)

- `rm` is denied by the permission system; a compound command containing `rm` is denied whole — move files instead.
- Background shells lack `cargo` on PATH.
- The scratchpad (`/tmp/claude-1000/…/scratchpad/`) holds every worktree and does not survive a machine restart; committed
  branches and `refs/safe-hold/*` do. Recreate worktrees from branches with `git worktree add` (run `git worktree prune`
  first if the old paths are gone).
