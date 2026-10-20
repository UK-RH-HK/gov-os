# W2-59 (DAEO-kh9l) packages, run 1

## P-W2-59-4 — three earlier acceptance cases assume the judge reads the project's own code or the install's data (blocks green, the review and DONE; not the code)

1. Context. DEC-822 item 3 and DEC-835 (W2-59's KPIs 1 and 3): the judge runs every declared check with its own
   interpreter and package (only the code under test comes from the tree), and modules find repository files from
   the project root, never from their install path. W2-59's tests (922dd542) and code (771e9a0c) do this.
2. What happened. The lead's regression (each suite in its own process, this worktree's src) has three reds the
   change causes, all by design:
   - W1-26 `test_w1_26_planted_defects.py::test_planted_authority_defect_decision_checker_exception_not_swallowed`:
     plants a raising `src/gov/decisions/checker.py` in the judged project and expects the authority family not to be
     GREEN; the judge no longer imports the project's `src/gov`, so the family is GREEN.
   - W1-22 `test_w1_22_canaries.py::TestCanaryRunner::test_lexical_canary_hits_after_reindex` and
     `::test_semantic_canary_hits_after_reindex`: the fixture project holds no canary declarations and expects the
     ones of the Gov OS install (found from the install path); now `FACET_UNAVAILABLE, unreadable canary declaration`.
   W2-59's test designer was asked to check W1-38 only (the brief named the hook-line change); these three were found
   in verification.
3. Why it matters. Exit criterion 1 needs a clean `gov close`; the three are reds the ticket causes. The behaviour they
   test is still wanted (an exception in the decision checker must not be swallowed; canaries hit after a reindex), so
   they should be re-expressed in the pinned-judge model, not dropped.
4. Options.
   (a) A test-designer batch in this ticket's resume revises the three cases (W1-26: put the raising checker into the
       judge's own code, for example a judge run whose own `src` holds it, not the judged project's; W1-22: the fixture
       project carries the kernel's canary declarations, as an adopted project does through the copier template's
       `governance/kernel/canaries`, DEC-579). Cost: one batch (~30 min) plus re-running W1-22 and W1-26 (~7 min) and
       the review. Risk low. Changes two earlier tickets' tests (MR-3: needs this decision, since the KPIs do not name them;
       `Rewrite-Reason:` trailer).
   (b) The owner lists the three on `accepted_reds` with a fixing row. Cost: an owner commit; leaves W1-26's defect
       untested; violates the spirit of "accepted_reds only shrink" (DEC-766).
   (c) For W1-22 only: ship the canary declarations inside the package as a fallback when the project has none
       (widens the engineer's paths to new package data under `src/gov/`; W2-59's no-fallback case still passes because
       its decoy is outside the package). W1-26 still needs (a).
5. Recommendation: (a), confidence medium-high. Classification: not review findings; test-premise conflicts with an
   approved decision (no fail-open, no lost work). Delegable (P2, reversible, guard not weakened).
6. Blocks: green verification, the CIT-P review and DONE for W2-59 (all its own work is done and green). Waiting costs
   W2-59's merge and keystone 1's re-pin.

## P-W2-59-1 — precompact.py and sessionstart.py put the project's src on their own import path (blocks nothing)
(from the test designer) Options: (a) widen W2-59's paths to the two programs; (b) a row (they fail soft: checkpoint
and context, not the guard); (c) accept. Lead: (b) a row, confidence medium (ordinary work: yes; consequence: other).

## P-W2-59-2 — must an installed wheel name its commit in `gov --version`? (blocks nothing)
Today: from a source tree `gov 0.1.0 (commit <HEAD>)`; from a wheel `(commit unknown)`. Options: (a) as built;
(b) widen to `.gitattributes` + an export-subst file; (c) W2-16/W2-18 decide how a release records its commit.
Lead: (a) now and (c), confidence medium.

## Owner acts (not decisions): A1 regenerate the generated settings from `.rulesync/hooks.jsonc` after the merge
(adapter-portability is RED GENERATED_DIFFERS until then; W1-05's live-hook cases run the generated settings); A2 re-pin
at the merge commit with W2-50's fix (DEC-835 item 4, DEC-853). Order: re-pin first, then regenerate, so the live
hook programs and the pin's package match.
