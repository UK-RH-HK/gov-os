# P2-HO-ORCH-0001 — Orchestrator continuity handoff (pre-compaction)

| Field | Value |
|---|---|
| Written | 2026-09-19, by the Phase-2 outer orchestrator at ~94% of its 1M context window (943,882 tokens, 247 requests) |
| For | this session after compaction, or a fresh replacement outer orchestrator launched with the V8.2 launcher |
| Authority | Durable state wins over this note: run `python3 release/orchestration/phase-2/tools/check_state.py show` then `verify` first. |

## Where things stand

> **Superseded in part (2026-09-19, P2-CP-0007):** round 3 is integrated and merged (`e4cb662`; P2-L-0022, P2-L-0023). Steps 1–3
> are done. Round 4 (step 4) runs as **two** parallel builders — P2-AR-0042 (BC-P2-02, P2-HO-0041) and P2-AR-0043 (residual
> integration points, P2-HO-0042). Resume from `CHECKPOINTS/P2-CP-0007.yaml`, then steps 4 (merge both) to 7 below.

- Phase 2, lifecycle `P2_REPAIR_ITERATION_1`, **repair round 3 of 4**. Candidate `cap2-candidate-0` was REJECTED (P2-AR-0007:
  134 blocking findings, 52 classes BC-P2-01…52, `release/capability-baseline/audit-0/synthesis/`). No `cap2-candidate-1` yet.
- Rounds 1 and 2 are integrated and merged (`b7e6d52`, `e8e1ff2`; last reproduced 207/0 lib, 136/0 certification).
- **Round 3** (base `53897c1`, handoffs P2-HO-0031…0039): DONE and recorded — P2-AR-0034 WS-3, 0037 WS-6, 0038 WS-7,
  0039 WS-8, 0040 WS-9/11 (status `COMPLETED_AWAITING_INTEGRATION`; reports on their branches `phase2/repair-1-r3-<ws>`).
  **RUNNING** — P2-AR-0033 WS-2, P2-AR-0035 WS-4, P2-AR-0036 WS-5 (worktrees
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/1b6c780e-2b37-439f-a969-a8d96b7ad35e/scratchpad/wt/p2-repair1-r3-{ws02,ws04,ws05}`).
  If this session was replaced, those agents' completion notices go to the old session: detect completion by the presence of
  `release/orchestration/phase-2/AGENT_RUNS/P2-AR-00{33,35,36}.report.yaml` on their branch. A branch with no report and no
  live agent is INCOMPLETE → re-dispatch a fresh builder from the same handoff on a new branch.
- Owner decisions in force: OWNER-DECISION-P2-0001 (OD-P2-01 A), OWNER-DECISION-P2-0002 (OD-P2-02 A). Orchestrator
  adjudications: P2-ADJ-0001 (applied), P2-ADJ-0002 (T2 cross-machine continuity; round 3). No owner gate pending.

## Exact next actions, in order

1. **As each running round-3 builder completes:** verify scope (`git diff --name-only 53897c1 phase2/repair-1-r3-<ws>`),
   record with `python3 release/orchestration/phase-2/tools/record_builder_round.py P2-AR-00NN <ws> "<notes>" r3`
   (notes are JSON-quoted by the tool), update `ORCHESTRATOR_STATE.yaml` (status → `COMPLETED_AWAITING_INTEGRATION`, remove
   from `running_work`), seal, verify, commit.
2. **When all eight round-3 runs are done:** create worktree/branch `phase2/repair-1-r3-integration` from the release branch
   HEAD, claim **P2-AR-0041**, dispatch a fresh integration builder (model `opus`) with **`HANDOFFS/P2-HO-0040-integration-3.md`**
   (already committed). Its central duty: **unify the two P2-ADJ-0002 mechanisms** (WS-3 `trust t2-binding --provision`/v2
   seals vs WS-8 `srr/binding.rs` `trust bind`/`keyring()`) into one, with no signing inside `gov`. Add to its list any new
   integration points WS-2/WS-4/WS-5 round-3 reports raise.
3. On integration: verify declared product changes, merge `--no-ff` into `release/4.1.6-rc1`, reproduce `cargo test --lib`
   and `--test certification` yourself, record, checkpoint.
4. **Round 4:** one fresh builder for **BC-P2-02** (evidence map: every one of the 101 capabilities names ≥1 evidence owner
   that actually runs, with Contract v3:53-73 fields; `gov contract verify` enforces) over the integrated tree; write its
   handoff (P2-HO-0041) from repair-delta BC-P2-02 plus every `IP-…-WS-1`/evidence-map IP in the round-1..3 reports.
   Merge; reproduce regression.
5. **Mint `cap2-candidate-1`:** tag the merge commit, record `product_code_digest`/`governed_state_digest` in `candidates`.
6. **Verification iteration 1** (all fresh, model `opus`, isolated worktrees, never builders): AC-14 R1-preservation verifier
   (re-run all four R1 held-out suites unedited through private paths; judge AR-0033 `hv_a::a1` size-pin failure on property;
   re-establish the twelve frozen R1 items for changed areas); AC-6 oracle-format reviewer (format_sha256 from
   `framework/qualification-oracle/`); six family verifiers (full re-audit — product code changed broadly, all evidence stale;
   each authors fresh held-out tests; required cross-machine attack for P2-ADJ-0002; availability-rule attacks);
   one fresh synthesis verifier issuing `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED|REJECTED` and labelling each finding
   RESIDUAL vs MATERIALLY_NEW against the iteration-0 inventory. Use P2-HO-0000/0007/0009 as templates; update for iteration 1.
7. If REJECTED: repair iteration 2 from the new delta; convergence stop at 3 consecutive iterations with materially new classes.
   If ACCEPTED: finalise per the owner's Phase-2 completion instructions; do not start Phase 3.

## Conventions and hazards (learned this phase)

- Always dispatch subagents with `model: "opus"` — unpinned subagents ran `claude-opus-4-6` and produced nonconforming audits.
- Builders' R1 held-out re-runs must use **private paths measuring their own tree** (shared scratch symlinks once measured the
  wrong tree). Check the census file/function counts in their reports.
- `record_builder_round.py` JSON-quotes notes; 17 run records were once unparseable because notes were not quoted.
  `check_state.py verify` now refuses unparseable run records.
- Keep `running_work` to truly running runs only.
- `rm` commands are denied by the permission system in this environment — do not retry; move files instead.
- Transcript reading is prohibited for every role; the orchestrator lifted it once, metadata-only, for the owner's telemetry
  request (P2-L-0021). Do not read running agents' transcripts.
