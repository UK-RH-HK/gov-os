# P-W2-81-VERDICT-1: W2-81's full run on release 0.1.0: NOT_READY, 74 reasons; triage and what next

Seed 1324021. Six repositories were adopted headless through A1 to A10 lite, overnight, by the adopter brief (65438a2e).
All six wrote "ADOPTION STOPPED" with a clean tree. Your operator then ran the read step on 0.1.0. The causes below
were found from the runner's and judge's code, the adopted repositories and clones, without opening the report or any
hidden-set material.

## 1. The runner not finding what the adopters built
- **A7 and A10 NOT_BUILT in all six: the runner reads the wrong list.**
  - The judge counts A7 and A10 as built only if `gov.adopt.project.STAGES` lists them (`w2_81_judge.py:135-141`).
    That list is `A0`-`A6`, `A8`, `A9`. The product lists A7 and A10 in `gov.adopt.command.STAGES`, and its lite gates
    wrote exactly the records the judge looks for: `governance/adoption/A7-independent-migration-verification.md` and
    `A10-independent-memory-verification.md`, present in every repository.
  - **Fix: the runner.** The judge reads `command.STAGES` (or the product exposes one list). This is W2-81's
    acceptance code, so it is a test designer's change.
- **hit_at_5 = 0 in five repositories, 90 in python-app-clean: five stores are stale.**
  - In the five, the store's commit is not HEAD, so `gov retrieve` stops with `FACET_UNAVAILABLE` and returns no
    evidence. Checked with a neutral word, under the runner's own empty-HOME environment and a normal one. The runner
    counts that as a miss.
  - python-app-clean's store commit equals its HEAD; it returned evidence and scored 90.
  - **Cause:** the adopters committed after A9's rebuild (the A10 record, verdicts, tickets), and my brief said to stop
    at the lite verdict with no final rebuild.
  - **Fix now: the adopters' form.** A final `gov rebuild` as the last step.
  - **Fix in the product:** the adoption's own closing commits leave the store stale, and `gov retrieve` then serves
    nothing. Either the last stage rebuilds, or retrieve serves the last good store and names its commit, as the store
    practice intends (W2-88 S11).

## 2. Real failures
- **gov close exit 3 on all six: my setup's ticket, not the product.** `gov close` refuses `NO_ACCEPTANCE_TESTS`: the
  adoption tickets my set-up script created have no `tests/acceptance/<id>/` suite (reproduced on a clone). The product
  is right to refuse.
  - **Fix: the set-up's form.** A closable ticket per repository needs a real ticket cycle: an independent test
    designer writes its acceptance tests, then an engineer, as EXAMIN's LITE ticket does.
- **secret-history: hidden variants #11 and #12 MISHANDLED.** The only actions secret-history's adoption took that
  were not KEEP were two `DELETE_FROM_ACTIVE_TREE` removals of superseded documents, `docs/plans/0003-storage-migration.md`
  and `docs/specs/upload-limit.md`. The judge's rule for a superseded plan is "never deleted".
  - Without opening hidden material I cannot confirm these are #11 and #12. Your operator can: print only the `record`
    field of the evidence of each MISHANDLED item.
  - If it is them, the cause is real and shared. The adopter chose deletion by its own judgement, and the product
    accepted a delete of a superseded document that its successor still references.
  - **Fix in the product:** A3 refuses DELETE_FROM_ACTIVE_TREE of a file that another tracked file references, or of
    one classed superseded.
- **legacy-docs: two controls FLAGGED.** A control is flagged when any of these holds (`w2_81_judge.py:716-744`):
  - it is classed in a flagging class;
  - it maps to no namespace;
  - it is left out of the lexical index;
  - it was changed in place, retired, or taken as a legacy document;
  - a finding names it.

  legacy-docs kept superseded and obsolete documents out of the embeddings through its path map, and its store is
  stale. One of these likely touched the controls. Your operator can confirm by printing each flagged control's
  evidence `said` lines; controls are not hidden variants, but check that first.
  - **Fix:** the adopter's path map, or the product's classing, depending on that evidence.
- **python-app-clean: stacked_share 85, below 99.** A retrieval figure, measured on the one current store. Its
  retrieve stops `BUDGET_EXHAUSTED_WITH_GAPS`. This is a real retrieval-quality result for the product's memory, not
  the adoption; the other five have no figure yet because of their stale stores.
- **VERDICT and findings NOT_BUILT in all six: real, the product has not built them.** There is no lite verdict stage
  (CAP-44.h) and no findings records (CAP-44.g). The adopters reported "none exists", which is right.

## 3. What to fix, and whether W2-81 re-runs
- **(a) Tonight, on 0.1.0. Recommended.**
  - I resume the five stale adopters headless with one reply: run `gov rebuild` as the final step. That is the
    product's own command, in their brief.
  - Your operator runs the read step again. hit_at_5 and stacked_share then measure real stores.
  - The close and A7/A10 reasons remain, now explained.
  - **Cost:** about 30 minutes of rebuilds; no new decision.
- **(b) Tickets, each on your P1 (DEC-974):**
  - W2-81's judge reads the product's stage list (a reopen within its purpose, test-designer work);
  - the product rebuilds after the adoption's last commit, or retrieve serves the last good store;
  - A3 refuses deleting a referenced or superseded document;
  - the lite verdict stage and the findings records (Wave 3, CAP-44.g, 44.h).
- **(c) A full re-run on 0.1.1.** After 0.1.1 is cut and re-pinned, with:
  - the adopter brief corrected (the final rebuild, the A3 and A7/A10 forms, the launch form, A9's `--out`);
  - a LITE ticket cycle per repository for the close;
  - the runner fix if (b) lands.

  That measures 0.1.1 as released.

**Recommendation:** (a) now; (b) as tickets; (c) after 0.1.1's re-pin, as 0.1.1's proving ground. Confidence
medium-high. The two items needing your operator's targeted print (secret-history's records, legacy-docs' control
evidence) are counts and record names, not hidden text.

**Your line:** `P-W2-81-VERDICT-1 (a)`, plus which tickets of (b), and `(c) yes` or `(c) no`.
