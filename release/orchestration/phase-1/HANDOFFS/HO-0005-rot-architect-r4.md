# HO-0005 — Handoff to the RoT-1 revision-4 architect

| Field | Value |
|---|---|
| Handoff | HO-0005 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh Root-of-Trust architect, run `AR-0005` (role `rot-architect`) |
| Completed stage | Independent synthesis review of RoT-1 revision 3: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (`79a09a12e34fd883192efd9f9e529cecbee9a6c8`) |
| Integration branch | `release/4.1.6-rc1` |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r4-architect` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/arch-r4` |

Reconstruct your task from this file and the repository. Read the review files themselves: this handoff routes you to
them and does not replace them.

You did not author revision 3 or any review of it.

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 3 (the design you amend) | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` | `ca77a431418bd6b349f465aa2521ca43bccfd5a6` |
| Consolidated review of revision 3 (**read in full**) | `release/root-of-trust/4.1.6-review-r3/`: `00-REVIEW-REPORT.md`, `10-BLOCKING-FINDINGS.md`, `11-CORRECTION-DELTA.md`, `D-synthesis/` | `79a09a12e34fd883192efd9f9e529cecbee9a6c8` |
| Panel reviews of revision 3 | `release/root-of-trust/4.1.6-review-r3/B-trust-security/` (`7d8c73a91a7c5fc7912427c59314d9259fbe25c9`), `…/C-compat-transaction/` (`9e013c161210f6fec0a9869cb3387fd57f033ebb`) | as stated |
| Earlier reviews | `release/root-of-trust/4.1.6-review-r2/` (`e5a6b8a`), `release/root-of-trust/4.1.6-review/` (`1c6027c`) | as stated |
| Owner requirements (binding, unchanged) | `release/orchestration/phase-1/HANDOFFS/HO-0001-rot-architect-r3.md` §3–§4 | at base |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `release/releases/4.1.2`–`4.1.5` | unchanged since `da9c851` |

## 2. What you must close

The consolidated blocking findings are in `10-BLOCKING-FINDINGS.md`. The synthesis correction delta states each blocking
**class** and what closes it.

The delta is direction, not the acceptance criterion. The next panel will attack each class with new held-out attacks.
Where you choose a different mechanism, show that it closes the class and say so in the response matrix.

Keep everything the consolidated review confirms sound. Do not regress any prior finding recorded as `CLOSED` by the
review of revision 3.

## 2a. Routing for revision 4 (facts from review r3; read the files)

| Blocking class | Findings | Correction direction |
|---|---|---|
| BC-1 constitutional-surface soundness for project-owned strength and for absence | RV3-H1; absorbs the root of RV3-M5 and the precedence case of RV3-M7 | `11-CORRECTION-DELTA.md` CD3-1 |
| BC-2 anchor satisfaction and anchor currency | RV3-H2 | CD3-2 |
| BC-3 built-source legitimacy of production binaries | RV3-H3 | CD3-3 |
| BC-4 owner options restated from corrected rules (OP-2, OP-4, OP-7 consequence statements materially incorrect) | follows BC-2 and BC-3 | CD3-4 |

- **Retain** everything in CD3-0, which the synthesis reviewer reproduced and confirmed sound.
- **Status of earlier findings.**
  - R2-H4 is closed as a class, and HO-0001 §3.4 is SATISFIED. Do not regress legacy containment; re-run P3r3 unchanged.
  - R2-M4 and R2-M6 are closed.
  - HO-0001 §3.1, §3.2 and §3.3 are NOT SATISFIED.
- **Non-blocking items** in `11-CORRECTION-DELTA.md` §6: RV3-M1…M9, RV3-L1…L8, CR-01…CR-12 and C-1…C-5. Close each in the
  design where you can. Otherwise carry it with a named acceptance test. The next panel will attack them again.
- **Re-review entry criteria** are in `11-CORRECTION-DELTA.md` §7 and are binding:
  - P1r4 (executed) and P4r4 (reference);
  - the CD3-3 `verify-artifact` source scenarios;
  - P3r3, unchanged;
  - every RV3-B, RV3-C and RV3-D probe, against the revision-4 rules;
  - a response matrix over RV3-H1…RV3-I1, CR-01…CR-12 and C-1…C-5;
  - a conformance oracle that distinguishes anchor semantics from sequence comparison, using only realisable
    constructions;
  - an acceptance plan meeting RV3-M9.
- **Adjudication precedence.** Where panel B or C and the synthesis disagree, the synthesis adjudication in
  `00-REVIEW-REPORT.md` and `10-BLOCKING-FINDINGS.md` governs. For example, C's claim that `governance/trust/**` is
  outside every legacy write set is refuted except on the intact layout (RV3-D-A06).
- **Persistence.**
  - BC-1…BC-3 are narrowed remainders of R2-H1…R2-H3 that have survived revisions 1, 2 and 3.
  - For each class, state in the pack why earlier corrections left a remainder.
  - Prefer mechanisms that remove the lower-trust input from the decision over mechanisms that add conditions to it.
  - Present every genuine product or security trade-off as an owner option. Never pre-decide it.


## 3. Deliverables

1. **Revision 4 of the pack**, amending `release/root-of-trust/4.1.6/` in place. Git keeps revision 3
   at `ca77a431418bd6b349f465aa2521ca43bccfd5a6`.
   - Update `22` as a response matrix over every consolidated finding of review r3: change, file, evidence.
     No "resolved" may rest on untested evidence.
2. **D-0008 and ARCH-0002 as PROPOSED revision 4.** Keep file status `PROVISIONAL` and the "PROPOSED … not active,
   not approved" wording. Update only these two rows in `docs/DECISIONS.md`.
3. **Architect evidence** under `release/root-of-trust/4.1.6/evidence/`.
   - Re-run every probe named in the review's re-review entry criteria against revision 4, and each probe the panel
     used to demonstrate a blocking finding. Each must flip, or be removed by a stated design change.
   - You may copy reviewer probe scripts into your evidence directory with attribution. Never edit
     `release/root-of-trust/4.1.6-review*/`.
4. **Commits on your branch.**
   - Work product: `RoT-1 revision 4 root-of-trust architecture for 4.1.6 (architecture only; D-0008 PROPOSED, not approved)`.
   - Then your typed report, `release/orchestration/phase-1/AGENT_RUNS/AR-0005.report.yaml` (schema in
     `AGENT_RUNS/README.md`), in a second commit.

## 4. Constraints

- **Architecture only.** Do not modify `runtime/`, `cli/`, `framework/`, `migrations/`, `tests/`, `fixtures/`,
  `capabilities/`, `Cargo.*`, `release/releases/**`, `release/verification/**`, `release/root-of-trust/4.1.6-review*/**`
  or D-0001…D-0007.
- **Allowed writes:**
  - `release/root-of-trust/4.1.6/**`;
  - `spec/decisions/D-0008.yaml`;
  - `spec/architecture/ARCH-0002.yaml`;
  - the D-0008 and ARCH-0002 rows of `docs/DECISIONS.md`;
  - your `AGENT_RUNS/AR-0005.report.yaml`.
- **Probe hygiene.**
  - Probes run only in scratch (`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0005/`).
  - Never mutate the canonical checkout or any other worktree.
  - Strip `GOV_*` from child environments and point `GOV_KERNEL_CACHE` into scratch.
  - Move `__pycache__` and other artefacts out of the worktree before committing.
- **Do not claim acceptance.** Do not decide OP-1…OP-7, or any later option, for the owner. D-0008 and ARCH-0002 must not
  be described as active, approved or accepted.
- **Stay in your branch.** Do not inspect other branches or worktrees. Under `release/orchestration/`, read only this
  handoff, `HO-0001` and `AGENT_RUNS/README.md`.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Legacy binaries**, for read-only use: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}`.
- **Toolchain:** `~/.cargo/bin/cargo`, Python 3 with PyYAML.

## 5. Forbidden assumptions

- That applying the correction-delta text is sufficient, or that closing the demonstrated examples closes the class.
- That a stateless machine can know unseen metadata; or, conversely, that attacker-selected stale signed state may become
  a current fact.
- That a repository-delivered record, or a file the governed account can write, can authorise a trust decision.
- That a pre-RoT binary reads any RoT-1 file before it acts.
- That any key below the declared threshold, or any single purpose, implies binary or TCB authenticity.
- That earlier probe results transfer unchanged to revision 4. Re-run them.

## 6. Next roles

Fresh reviewers B (trust and security) and C (compatibility and transactions) will run in parallel, followed by a fresh
synthesis reviewer. They receive your committed revision and the review evidence, not your reasoning.
