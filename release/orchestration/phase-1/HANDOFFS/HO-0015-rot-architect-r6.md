# HO-0015 — Handoff to the RoT-1 revision-6 architect

| Field | Value |
|---|---|
| Handoff | HO-0015 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh Root-of-Trust architect, run `AR-0015` (role `rot-architect`) |
| Completed stage | Independent synthesis review of RoT-1 revision 5: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (`d1228cb77b9253c90406ab0cc3a8c3bd4b480e64`) |
| Integration branch | `release/4.1.6-rc1` |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r6-architect` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/arch-r6` |

Reconstruct your task from this file and the repository. Read the review files themselves: this handoff routes you to
them and does not replace them.

You did not author revision 5 or any review of it.

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 5 (the design you amend) | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` | `cdb4e14009bba60bea9b805563c1b60e84f30b4b` |
| Consolidated review of revision 5 (**read in full**) | `release/root-of-trust/4.1.6-review-r5/`: `00-REVIEW-REPORT.md`, `10-BLOCKING-FINDINGS.md`, `11-CORRECTION-DELTA.md`, `D-synthesis/` | `d1228cb77b9253c90406ab0cc3a8c3bd4b480e64` |
| Panel reviews of revision 5 | `release/root-of-trust/4.1.6-review-r5/B-trust-security/` (`248f12a6b98c939ec2d9c3fef8045d9c19c82aae`), `…/C-compat-transaction/` (`840d583273088caff4880c02edec03d2ade83156`) | as stated |
| Earlier reviews | `release/root-of-trust/4.1.6-review-r2/` (`e5a6b8a`), `release/root-of-trust/4.1.6-review/` (`1c6027c`) | as stated |
| Owner requirements (binding, unchanged) | `release/orchestration/phase-1/HANDOFFS/HO-0001-rot-architect-r3.md` §3–§4 | at base |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `release/releases/4.1.2`–`4.1.5` | unchanged since `da9c851` |

## 2. What you must close

The consolidated blocking findings are in `10-BLOCKING-FINDINGS.md`. The synthesis correction delta states each blocking
**class** and what closes it.

The delta is direction, not the acceptance criterion. The next panel will attack each class with new held-out attacks.
Where you choose a different mechanism, show that it closes the class and say so in the response matrix.

Keep everything the consolidated review confirms sound. Do not regress any prior finding recorded as `CLOSED` by the
review of revision 5.

## 2a. Routing for revision 6 (facts from review r5; read the files)

| Blocking class | Findings | Kind of fix (per the synthesis review) | Correction direction |
|---|---|---|---|
| BC5-1 first-contact root of trust | RV5-H1 | engineering correction for enforcement and statements, plus an owner trade-off for the composition of the first-contact root | `11-CORRECTION-DELTA.md` CD5-1 |
| BC5-2 byte-determining build environment | RV5-H2 | engineering correction to assign the selector, plus an owner trade-off for the remaining common-mode environment | CD5-2 |
| BC5-3 first-hand constitutional content | RV5-H3 | engineering correction only | CD5-3 |
| BC5-4 complete decision register and derived statements | option statements, RV5-M5, D-A07 | engineering correction only | CD5-4 |

- **Retain** everything in CD5-0, which the synthesis reviewer reproduced and confirmed sound.
- **Legacy containment.** R2-H4 is closed as a class; reviewer C's `matrix5` was reproduced with 0 violations over 30,165
  rows, and HO-0001 §3.4 is SATISFIED. Do not regress it.
- **Owner trade-offs (T1-a…T1-d and E-a…E-c).**
  - Route them exactly as the review does ("architect, then owner", §7 item 4). Present them as owner options, with
    consequences computed by the corrected calculator.
  - Integrate them into the existing owner-option set with one consistent numbering and a mapping table.
  - The owner answers them only in the single consolidated decision package opened after an independent synthesis
    reviewer accepts an architecture.
  - The architecture must be sound under every option it offers, or state precisely which options it cannot support.
    Choose none, and label no hidden default.
- **Non-blocking items** in `11-CORRECTION-DELTA.md` §6: RV5-M1…M9, RV5-L1…L9, RV5-I2, CR5-B-01…CR5-B-12, and the carried
  CR4-B and C items. Close each in the design, or carry it with its named acceptance test.
- **Re-review entry criteria** in `11-CORRECTION-DELTA.md` §7 are binding. That includes item 2(e): unchanged instruments
  must still refuse what they refuse.
- **Adjudication precedence.** Where panels B and C and the synthesis disagree, the synthesis adjudication governs.
- **Background.** The escalation proposals of specialists A and B and `SYNTHESIS.md` are in
  `release/root-of-trust/4.1.6-alternatives-r5/`. They explain why revision 5 chose its mechanisms; they are not findings.


## 3. Deliverables

1. **Revision 6 of the pack**, amending `release/root-of-trust/4.1.6/` in place. Git keeps revision 5
   at `cdb4e14009bba60bea9b805563c1b60e84f30b4b`.
   - Update `22` as a response matrix over every consolidated finding of review r5: change, file, evidence.
     No "resolved" may rest on untested evidence.
2. **D-0008 and ARCH-0002 as PROPOSED revision 6.** Keep file status `PROVISIONAL` and the "PROPOSED … not active,
   not approved" wording. Update only these two rows in `docs/DECISIONS.md`.
3. **Architect evidence** under `release/root-of-trust/4.1.6/evidence/`.
   - Re-run every probe named in the review's re-review entry criteria against revision 6, and each probe the panel
     used to demonstrate a blocking finding. Each must flip, or be removed by a stated design change.
   - You may copy reviewer probe scripts into your evidence directory with attribution. Never edit
     `release/root-of-trust/4.1.6-review*/`.
4. **Commits on your branch.**
   - Work product: `RoT-1 revision 6 root-of-trust architecture for 4.1.6 (architecture only; D-0008 PROPOSED, not approved)`.
   - Then your typed report, `release/orchestration/phase-1/AGENT_RUNS/AR-0015.report.yaml` (schema in
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
  - your `AGENT_RUNS/AR-0015.report.yaml`.
- **Probe hygiene.**
  - Probes run only in scratch (`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0015/`).
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
- That earlier probe results transfer unchanged to revision 6. Re-run them.

## 6. Next roles

Fresh reviewers B (trust and security) and C (compatibility and transactions) will run in parallel, followed by a fresh
synthesis reviewer. They receive your committed revision and the review evidence, not your reasoning.
