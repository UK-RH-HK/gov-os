You are the ticket lead for ticket `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 2, the resume after your run 1's PACKAGES.** `git log --oneline -1` must show `c76cddf5`, and `git status --short` must show nothing but sandbox placeholder files, if any (anything else: stop and return PACKAGES naming it). Read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; it holds, and this brief adds to it.

## Your packages, decided (DEC-864, delegated, 2026-10-20; in the register after step 1's merge)

1. **P-W2-59-4 (a):** a fresh independent test designer revises the three earlier cases, each change with `Rewrite-Reason: DEC-822 item 3, DEC-835 (DEC-864)`: W1-26's `test_planted_authority_defect_decision_checker_exception_not_swallowed` plants its raising decision checker in the judge's own code (not in the judged project's `src/gov/`); W1-22's `TestCanaryRunner::test_lexical_canary_hits_after_reindex` and `::test_semantic_canary_hits_after_reindex` give their fixture project the kernel's canary declarations, as an adopted project carries them through the copier template (DEC-579). The behaviours they guard stay; no KPI of W1-22 or W1-26 changes; no expectation is lowered.
2. **P-W2-59-1 (b):** row W2-M389 (for W2-10). **P-W2-59-2 (a)** as built, (c) row W2-L371. Your residual (the hook programs still read from the tree) is row W2-M390; the secrets scan's vanishing file is W2-M388. Nothing more to do for these.

## This run's order

1. **Merge `w2/integrate` into this branch** (DEC-750's form: `Task: DAEO-kh9l`, `Role: orchestrator`, `--no-ff`; never `-s ours`; never drop a side; a conflict you cannot resolve keeping both sides is PACKAGES). It brings W2-62 (the session-start hook, merged `6e4b2750`), W2-50 (the secrets scan fix, merged `98effadc`: `secrets-indexing` should now be GREEN), the lighter path map (DEC-856: the raw orchestration record is no longer indexed), DEC-856 to DEC-864, and the W2-58 ticket.
2. **Tests:** the test designer's batch of item 1, launched sandboxed (`--effort high`), in `tests/acceptance/W1-26/` and `tests/acceptance/W1-22/` only, for those three cases only.
3. **Verify in full** (a full rebuild first; record its wall time, the first lead rebuild under the new path map; then every suite in its own process, `tests/unit`, `gov check`). Known reds you did not cause: W1-42's two accepted reds; W1-49's two retired-window tests (package P-W2-52 with the owner); adapter portability until the owner regenerates the settings.
4. **Independent review of the CIT-P (CAP-33):** one fresh read-only reviewer (brief A3 with `JUDGEMENT.md`, `--effort max`), on the final code and `docs/changes/W2-59-CIT-P.md`, the merge-back included. Commit its probe record under `docs/probes/DAEO-kh9l/` only if it passes.
5. Return DONE with the owner acts in order: after the merge, the owner re-pins at the merge commit (it holds W2-50's fix, DEC-853 item 4), then regenerates the settings from `.rulesync/hooks.jsonc`.

---

