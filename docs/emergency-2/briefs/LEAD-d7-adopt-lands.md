# Lead brief: D7, real adopted repositories land: `gov adopt`'s stage commits pass the landing (a fix under W1-41 `DAEO-cdoi` or W2-115b `DAEO-j9z6`, whichever you change)

Read `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it. Name: `d7-adopt-lands`; worktree
`/home/usain/gov-os-worktrees/E2-d7-adopt-lands`, branch `e2/d7-adopt-lands` from `w2/integrate`; **then merge
`e2/l2-4-queue` into it first** (that branch lands `gov queue`'s selection fix before yours; read only, never commit to
it). **Do not merge into `w2/integrate`.** It rides release 0.1.5. **Models (DEC-1225):** every helper Sonnet.

**The owner's decision, DEC-1227 D7:** "the fix must make real adopted repositories land, not only the proving run's
test setup. Choose between gov adopt writing the trailers and the landing accepting adopt's own commits by a marker,
whichever is simpler, and tell me which." Read `docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md` rows R2b and D7:
`gov adopt`'s stage commits are subject-only by design (`src/gov/adopt/project.py:128-146`, `commit()`;
`governance/project/bootstrap.md` "The adoption's commits"); W2-81's set-up line F1 (`tools/setup_0.1.4.py:125`)
asked for `Role: orchestrator` on every commit touching `governance/adoption/`, and the same line sank 0.1.1.

## Step 1: measure, then choose (before any test is written)
In a scratch adopted repository under `~/gov-os-runs/d7/` (a small synthetic one; `gov adopt --lite` on it with this
branch's code), make one ordinary feature change after adoption and land it through `gov queue` (and `gov accept`
where a ticket exists). Record exactly what refuses or warns on adopt's commits, if anything: the trailer check
(CAP-63.a), the paths/containment check (CAP-58.h judges a trailer-less commit against the caller), test authorship,
or nothing. Then choose the simpler of:
- **(T) `gov adopt` writes trailers** on its stage commits (which `Role:` and `Task:`; where the `Task:` comes from in
  a repository with no ticket yet), or
- **(M) the landing accepts adopt's own commits by a marker** (for example the subject `gov adopt --lite <stage>` with
  the commit touching only the stage's own record paths).
"Simpler" means: fewer lines and files changed, nothing new the adopter must supply, and no change to the Contract.
If step 1 shows nothing refuses a real repository, say so: then the fix is that the landing's behaviour is pinned by
a test on a real adopted repository, and W2-81's F1 is rewritten to what the product guarantees.

## Step 2: the fix (failing test first; recorded in the owning ticket's record, `Fix:` trailer)
- **L1** On a freshly adopted synthetic repository, a feature change after adoption lands green through `gov queue`
  with adopt's stage commits in its range. Verify: the planted repository, red on the base if anything refuses today.
- **L2** The choice (T or M) built, and a hand edit of a stage record outside `gov adopt` is still caught as today
  (`stands_on`, record hashes).
- **L3** W2-81's set-up F1 (`tools/setup_0.1.4.py` or its successor on `w2/integrate` / `e2/w2-81-fixes`) rewritten to
  what the product now guarantees: name the exact change in your return; change it only if the file is on your base.

## Green and return
`gov accept` of the owning ticket green, `tests/unit/adopt`, `tests/unit/queue` (or the packages you touched), W1-41's
and W2-115b's acceptance folders, `tests/unit/optin`. Return: **step 1's finding first, then the choice (T or M) and
why, in three lines** (the CTO tells the owner); branch and head; L1 to L3 with tests; the trial figures; reds not yours.
