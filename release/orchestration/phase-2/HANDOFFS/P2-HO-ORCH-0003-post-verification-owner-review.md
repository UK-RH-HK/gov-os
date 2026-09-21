# P2-HO-ORCH-0003 — Orchestrator continuity: Phase 2 stopped for owner review

| Field | Value |
|---|---|
| Written | 2026-09-21, by the Phase-2 outer orchestrator, on the owner's stop condition of 2026-09-20 |
| For | this session after an owner instruction, or a fresh replacement outer orchestrator |
| Supersedes | `P2-HO-ORCH-0002-safe-hold-continuity.md` (kept as history; its conventions and hazards still apply) |
| Authority | Durable state wins over this note. Run `python3 release/orchestration/phase-2/tools/check_state.py show`, then `verify`, then read `CHECKPOINTS/P2-CP-0011.yaml` and `PHASE_2_DECISION_PACKAGE.md`. |

## Stop rule now in force

Verification iteration 1 **rejected** `cap2-candidate-1`. Under the owner's instruction of 2026-09-20 the orchestrator
recorded the verifier evidence and **stopped**. Until the owner gives an explicit instruction:

- start **no** repair iteration 2, no repair or build agent, and no further verification;
- do not alter the candidate, its tag, the frozen gate contract or any recorded verdict;
- do not relabel any finding or class — the convergence count is 1 of 3 and only a fresh independent verifier may change
  a label.

Model routing (`model: "opus"` on every Agent call) and the acceptance criteria are unchanged.

## Where Phase 2 stands

- Branch `release/4.1.6-rc1`. Candidate **`cap2-candidate-1`** (`0bad524`, `product_code_digest` `e6332fc7…2220`,
  `governed_state_digest` `3d2aeba2…20c0`) — **REJECTED** by P2-AR-0052 on AC-3, AC-4 and AC-5; the other thirteen
  acceptance criteria hold.
- Repair iteration 1 is complete: rounds 1–4 integrated (`b7e6d52`, `e8e1ff2`, `e4cb662`, `0bad524`). Orchestrator
  reproduction at the candidate: release build 0 warnings, `gov contract verify` `CONTRACT_SOURCE_BOUND`, lib 276/0,
  certification 207/0.
- Verification iteration 1 is complete: P2-AR-0044 (`R1_PRESERVED`), P2-AR-0045 (`ORACLE_FORMAT_ACCEPTED`),
  P2-AR-0046…0051 (six families), P2-AR-0052 (synthesis verdict). All evidence is merged under
  `release/capability-baseline/verify-1/`.
- Gates: `GATE-P2-ORACLE-FORMAT` SATISFIED; `GATE-P2-R1-PRESERVATION` SATISFIED for this candidate; `GATE-P2-REPAIR-1`
  SATISFIED; `GATE-P2-CAPABILITY-BASELINE-ACCEPT` NOT_SATISFIED. No owner gate pending.
- Owner decisions in force: OD-P2-01, OD-P2-02, OD-P2-03. Adjudications: P2-ADJ-0001, -0002, -0003.
- Six iteration-0 classes still leave an acceptance criterion unmet — BC-P2-07, -32, -33, -37, -41, -45 — plus one new
  class, **BC-P2-53**.

## If the owner authorises repair iteration 2 (option A)

1. Re-read `release/capability-baseline/verify-1/synthesis/repair-delta.md` — it is the normative source for the round,
   stating requirements, not designs.
2. Lifecycle → `P2_REPAIR_ITERATION_2`; iteration counter → 2; write a round-1 common protocol handoff carrying forward
   P2-HO-0031's availability rule, the R1 private-path census rule, and the no-test-rename rule (the evidence map names
   **477** tests by path; renaming, removing or ignoring one fails `gov contract verify`, the binding-chain test and
   `release build`).
3. Six workstreams, fresh builders, `model: "opus"`, isolated worktrees, non-overlapping file scopes:
   **WS-A** tool-installation trust surface (BC-P2-53 + BC-P2-41), **WS-B** overlay precedence coverage (BC-P2-45),
   **WS-C** adoption on a secret-bearing tree (BC-P2-33), **WS-D** update ingress (BC-P2-37), **WS-E** failure memory
   (BC-P2-32), **WS-F** health tier coverage (BC-P2-07).
   **Sequence WS-B before or with WS-A** — WS-A's "trusted OS state" is only trustworthy once WS-B closes, and both read
   `role_permissions`. The only other overlap is `scheduler/catalogue.rs` between WS-C and WS-F.
4. Then a fresh integration builder, an orchestrator regression reproduction, `cap2-candidate-2`, and verification
   iteration 2 from the P2-HO-0043…0047 templates updated for the new candidate. The eight non-blocking requirements the
   repair delta lists travel with the round.
5. Convergence: if verification iteration 2 and then iteration 3 each introduce materially new blocker classes, stop with
   `PHASE_CONVERGENCE_ESCALATION_REQUIRED` and produce the root-cause/meta-review package.

## If the owner chooses B, C or D

- **B (amend the gate contract or a class's lifecycle placement)** is an owner act. The orchestrator records the amendment
  as an owner decision, re-hashes the frozen contract, notes the new hash in `ORCHESTRATOR_STATE.yaml`, and a **fresh
  independent verifier** re-adjudicates the affected criteria on the same candidate. The orchestrator never grades the
  candidate itself and never narrows a criterion on its own judgement.
- **C (meta-review)** — dispatch a fresh reviewer over the loop itself: the handoffs, the round structure, the evidence
  standard and this orchestrator's routing, as Phase 1's root-of-trust escalation did.
- **D (stop)** — final checkpoint, leave the release uncertified, do not start Phase 3.

## Hazards (in addition to P2-HO-ORCH-0002's)

- YAML: an unquoted value containing `: ` breaks the state, the gate register or a run record. `check_state.py verify` now
  refuses an unparseable gate register or run record; quote such values, or build the file with `yaml.safe_dump`.
- `tools/product_identity.py` resolves `<rev>^{commit}`, so annotated tags report the commit, not the tag object (fixed
  2026-09-20 after V1-R1P-02).
- Background shells lack `cargo` on PATH: `. "$HOME/.cargo/env"` first.
- Under heavy parallelism several verifiers reported load artefacts; one beta test failed once under six concurrent suites
  and passed isolated. Re-run contested figures serially before treating them as findings.
- The scratchpad holds every worktree and does not survive a restart; branches and `refs/safe-hold/*` do.
