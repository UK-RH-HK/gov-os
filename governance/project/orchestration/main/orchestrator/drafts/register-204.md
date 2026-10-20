
## 204. W1-42 lead run 3 returns PACKAGES: delegated decisions and finish-line classifications (register v0.204, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-674 — W1-42 lead's run 3: the lesser packages
- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-13; told to the owner, who may replace it) · **Under:** DEC-584, DEC-658, DEC-662 · **Basis:** the W1-42 lead's third return (`log/W1-42-lead-run3.json`, PACKAGES; branch `w1/W1-42` at `55827091`; a-dev clone at `82dca10`, b-dev clone at `fc28272`). Both programmes reached a green implementation (ORION 84 of 84 acceptance cases, ARGUS 65 of 65); both `gov close` attempts refused with exit 3
- **Decision** (each P3, reversible, on a throwaway clone of a synthetic programme):
  - **A5 verdict hash (a-dev):** left as it is; `verdict_commit` is the anchor. The lead's recommendation and mine agree; confidence medium.
  - **PKG-B, the b-dev close refusal, needs no new decision:** DEC-658 and DEC-662 say ARGUS's `gov close` is attempted once and its refusal reported. It was attempted (first `STORE_STALE` before the gates, then, after a rebuild, `CONTEXT_FAILED`: the ticket the lead wrote lists the source `REQ-004`, which b-dev's store does not hold at A2). No further close in b-dev. The lead recommended correcting the ticket's sources and closing once more; that is told to the owner as his to order if he wants it.
  - **Finish line (DEC-584), no new round, Wave 2 list or named residual in the exit report:**
    - PKG-7, the ARGUS audit's major finding (what counts as a missing `created_at`, values that are not aware datetimes, a missing "now", whether the error text is in the contract; `None` raises `AttributeError` today). The lead's recommended rule is recorded with the residual.
    - A closed specification changed in place (a-dev `f59aa0e`): a rule is wanted.
    - The b-dev audit report's form (the kernel audit validator's frontmatter and table).
    - `gov close` judges every commit that carries the ticket's `Task:` trailer, the lead's own ticket-creating commit included; a clone's path map has no trailers base.
    - `gov close` leaves its repair ticket untracked, and in b-dev without `role`.
    - `python3 -m gov.guard.heldout --help` has no help and executes.
    - The lesser findings of the ORION and ARGUS audits, as the lead lists them.
  - **Deviations of run 3, for the exit auditor:** the lead wrote ticket files in the clones and ran `checker.close`, `tk close` and `tk start` there; a closed specification was edited in place; three auditor sessions ran on one a-dev audit ticket; b-dev's close was invoked twice (the first refused before the gates); the lead ran pytest read-only in b-dev while a worker ran there; ARGUS's red rested on the absent module alone; b-dev's specification was closed and its engineer run with PKG-7 open; the lead committed the two repair tickets after the refusals.
  - **With the owner:** PKG-A (the a-dev close refuses with `TRAILER_MISSING` on run 2's lead commit `540004a`, which lacks `Implements:`; the DEC-511 proof), and the permitted roles of the a-dev namespace that holds the two secret-named files (the worker recommends narrowing; the lead leaves it to the owner).

| Version | Date | Change |
|---|---|---|
| 0.204 | 2026-10-13 | Orchestrator, delegated: DEC-674 (W1-42 lead's run 3: A5 verdict hash left; the b-dev close attempted once as DEC-658 and DEC-662 say, no further close; seven items to the Wave 2 list or the exit report's residuals by the finish line; run 3's deviations for the exit auditor; PKG-A and the secret-file namespace's roles with the owner). Next free id: DEC-675. |
