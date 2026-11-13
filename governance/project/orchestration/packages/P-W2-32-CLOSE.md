# P-W2-32-CLOSE: close W2-32 on its own fresh review, and S11's speed clause (owner's items; short form)

**The questions.**
- **Q1:** your rule makes W2-32 (`DAEO-0pyc`, retrieval components) close together with W2-15a, which has not started.
  That holds four closes: W2-32, W2-137 (after W2-32), W2-145 (after W2-137) and W2-155 (after W2-145, and W2-138).
  Do we close W2-32 on its own fresh review?
- **Q2:** the fresh review fails one KPI line on its own measure: S11's speed clause. How should S11 read?

**The fresh review** (`.gov-runtime/scratch/orchestrator/reviews/w2-32-fresh-20261113.md`; `gov accept W2-32` passes, 266 passed, 0 failed, 2 skipped, every mapped line; an independent auditor, Opus
high, on integrate `79159cd44c5b`): the verdict block computes **READY**, with 0 blocking findings and 7 rows. The
acceptance folder gives 266 passed, 1 skipped (S5's order case, by design) and 1 strict xfail (S7's R2-F1, parked as
W3-P22 by DEC-1083 (3)).
- **S11, the speed clause:** "at or under the pin's" is not met. PAT-1 §3: the old pin 1.44 s; the new pin 1.45 s with
  the pool off, 1.68 s with the pool on. No decision re-words or waives it. S11's equality clause is met (107 against
  107; E0b 106 against 108, within 2).
- **F1, the failure line:** its band is D-4b measure 1 on W2-15a's 48 questions. No adopted round lowered a total, so it
  passes, but W2-15a's own baseline is not yet recorded.
- **Rows** (ride along when W2-32 next changes, DEC-802): F3, the ticket still states a 16-text cap that DEC-1090 (2)
  superseded (the code uses 64); F5 and F6, stale evidence rows; F1 (S1), the real-model swap's dev-tier regression is on
  no record.

**Options for Q1.**
- **(a) Close W2-32 now on its fresh review**, with S11 settled by Q2. W2-15a then records its own baseline as its own
  evidence. W2-137, W2-145 and W2-155 can close today and tomorrow, in that order (W2-155 also after W2-138). Cost: none.
  W2-32's F1 band stays as measured on D-4b.
- **(b) Keep the rule:** the four closes wait for W2-15a. W2-15a needs your metric approval (Q-2) and its run, about
  11-15 at the earliest.

**Options for Q2 (DEC-105).**
- **(a) Re-word S11 to the measured cost:** +0.23 s at the median with the pool on, for 4.5 to 1.0 overlapping items an
  answer. The trade is already in the evidence.
- **(b) Measure again with the cap at 64** (the code's real cap, F3). About 1 hour.
- **(c) Defer S11's speed clause to the memory audit.**

**Recommendation: Q1 (a), Q2 (a).** Confidence: medium. The pool's speed cost buys fewer overlapping items an answer,
which is the point of the line. The measured trade is the honest statement of it.

Your line: `W2-32 Q1 (a), Q2 (a)` (or name others).
