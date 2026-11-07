# W2-138 — the test designer's second pass: W2-133's "unchanged" acceptance rows and the token's new key (DAEO-rmhj)

You are the independent test designer for **W2-138** (`.tickets/DAEO-rmhj.md`, read its "Built" section). W2-138's
build (DEC-1090 (3), S3) puts the store's commit into every continuation token as a new key `s`. W2-133's acceptance
guard compares today's token with the one the old code made, so four rows go red on `continuation` alone, every other
field equal (named by the engineer's regression run):
- `tests/acceptance/W2-133/test_w2_133_unchanged.py`: the two `[every-chunk-batched-*]` rows and both
  `test_s3_the_continued_pages_…` rows.

## The task
Revise the comparison so a decoded token is compared without its `s` key (and only that), keeping everything W2-133's
guard protects: the same items in the same order, the batches, the expansions, the repeats, the gaps, the budget, and
the rest of the token. The commit carries
`--trailer "Rewrite-Reason: DEC-1090 (3): continuation tokens carry the store's commit (W2-138 S3)"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-138-tests`, branch `w2/W2-138-tests` (integrate merged). Write only
  `tests/acceptance/W2-133/test_w2_133_unchanged.py` (and its support file in that folder if the comparison lives there).
  You may read W2-138's built code on `w2/W2-138` (`git show w2/W2-138:src/gov/retrieval/retrieve.py`): you are
  revising another ticket's guard, not testing W2-138's own KPIs.
- Run `tests/acceptance/W2-133` against W2-138's code (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-138/src`) and
  against integrate's (your own `src`): green on both.

## Rules
As `W2-138-designer.md`: the hidden-half rule, no GPU, no model, DEC-1080, commit on `w2/W2-138-tests` with
`--trailer "Task: DAEO-rmhj" --trailer "Implements: DEC-1090" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
plus the Rewrite-Reason trailer. Return the twelve fields with both runs' counts.
