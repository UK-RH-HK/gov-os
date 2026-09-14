# HO-0011 — Handoff to the synthesis architect for RoT-1 revision 5 (escalation)

| Field | Value |
|---|---|
| Handoff | HO-0011 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh synthesis architect, run `AR-0011` (role `rot-synthesis-architect`) |
| Completed stages | revision 4 rejected (`97a554525a4677035b56c10c6ff6f1096c818e6c`); specialist A (`afda6635184311f58188a000105f753bce604540`, run `AR-0009`); specialist B (`ed079269282748b7e1e464ad395ab85177efb61f`, run `AR-0010`) |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r5-synthesis-architect` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/arch-r5` |

You did not author any RoT-1 revision, any review or either specialist proposal.

Your job:
1. Judge the two independent root-cause alternatives against all review evidence.
2. Choose or combine the mechanisms that remove BC4-1 independent TCB decisions (RV4-H1; remainder of R2-H3/BC-3), BC4-2 anchored non-circular first TCB acceptance (RV4-H2; remainder of R2-H2/BC-2 where it meets R2-H3/BC-3), BC4-3 release-scoped registration of constitutional content (RV4-H3; remainder of R2-H1/BC-1), and BC4-4 owner-option and blast-radius statements at the root.
3. Author **RoT-1 revision 5** as the architect of record.

Fresh independent reviewers B and C, then a synthesis reviewer, will review it. You do not accept your own architecture.

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Latest rejected revision | `release/root-of-trust/4.1.6/`, D-0008, ARCH-0002 | `bca05a7e2c2791126fde1d3d812facdaa45b2e45` |
| Its consolidated review (synthesis governs) | `release/root-of-trust/4.1.6-review-r4/` | `97a554525a4677035b56c10c6ff6f1096c818e6c` |
| Specialist proposals | `release/root-of-trust/4.1.6-alternatives-r5/specialist-a/`, `…/specialist-b/` | `afda6635184311f58188a000105f753bce604540`, `ed079269282748b7e1e464ad395ab85177efb61f` |
| All earlier reviews | `release/root-of-trust/4.1.6-review*/` | Git history |
| Owner requirements (binding) | `release/orchestration/phase-1/HANDOFFS/HO-0001-rot-architect-r3.md` §3–§4 | at base |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, released payloads | unchanged since `da9c851` |
| Legacy binaries | `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}` | read-only |

## 2. Deliverables

1. **`release/root-of-trust/4.1.6-alternatives-r5/SYNTHESIS.md`.** For each persistent class, give:
   - the root cause you accept;
   - the chosen mechanism, with each specialist's position and why one was preferred or the two combined;
   - the rejected alternatives and why;
   - the genuine owner trade-offs, which you do not decide.
2. **Revision 5 of the pack**, amending `release/root-of-trust/4.1.6/` in place.
   - Keep everything the reviews list as sound unless the chosen mechanism replaces it, and say so.
   - `22` is a response matrix over every consolidated finding of the latest review.
   - The class-remainder analysis is updated.
3. **D-0008 and ARCH-0002 as PROPOSED revision 5** (status `PROVISIONAL`; not active, not approved). Update
   only these two rows in `docs/DECISIONS.md`.
4. **Evidence** under `release/root-of-trust/4.1.6/evidence/`: every re-review entry criterion of the latest review, and
   every blocking probe of the latest two reviews, re-run against revision 5.
5. **Commits.**
   - Work product: `RoT-1 revision 5 root-of-trust architecture for 4.1.6 (escalation synthesis; architecture only; D-0008 PROPOSED, not approved)`.
   - Then your typed report, `release/orchestration/phase-1/AGENT_RUNS/AR-0011.report.yaml` (verdict
     `ARCHITECTURE_REVISION_READY_FOR_REVIEW` or `INCOMPLETE`).

## 2a. Routing facts

- **Binding criteria.** The re-review entry criteria in `release/root-of-trust/4.1.6-review-r4/11-CORRECTION-DELTA.md`
  §7 apply to revision 5. So do the carried requirements in §6 (RV4-M1…M7, RV4-L1…L10, C-2…C-6, and the D-A03 oracle
  mutants), in addition to `HO-0001` §3–§4.
- **Owner options.**
  - Specialist A lists owner choices OC-1…OC-8 and specialist B lists OC-1…OC-5, with overlapping numbering.
  - Reconcile them, and the existing OP-1…OP-7, into one consistently numbered owner-option set. Every genuine trade-off
    stays an owner option with its security and operational consequences.
  - Derive the consequences from the corrected rules. Where a proposal supplies a calculator or enumeration, use it and
    cite it.
  - Decide no option and propose no hidden default.
- **Specialist claims.** Neither specialist's findings about revision 4, nor their falsification results, have been
  independently adjudicated. Treat them as claims. Re-run what revision 5 relies on.
- **Scope.** Implementation facts a proposal raises, for example build reproducibility prerequisites in `runtime/`,
  belong in the pack as implementation requirements with acceptance tests. Do not change product source.

## 3. Constraints

- **Independence.** Under `release/orchestration/`, read only this handoff, `HO-0001` and `AGENT_RUNS/README.md`. Do not
  inspect other branches or worktrees.
- **Writes.**
  - `release/root-of-trust/4.1.6/**`;
  - `release/root-of-trust/4.1.6-alternatives-r5/SYNTHESIS.md`;
  - D-0008 and ARCH-0002;
  - their two rows in `docs/DECISIONS.md`;
  - your report.

  Never write to the specialist directories, reviews, product source, payloads or verification evidence.
- **Probes.** Scratch only (`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0011/`). Strip `GOV_*` and point `GOV_KERNEL_CACHE` into scratch.
  Keep the worktree clean.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Owner decisions.** Decide no owner option. End each commit message with
  `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
