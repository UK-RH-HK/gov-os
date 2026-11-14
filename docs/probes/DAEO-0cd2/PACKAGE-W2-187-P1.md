---
task: DAEO-0cd2
kind: package (interim, the ticket lead)
blocks: a green tests/acceptance/W2-171 on w2/W2-187, so the lead's verify and the landing
---
# PACKAGE W2-187-P1: two W2-171 acceptance files pin the 85 % bar and are outside W2-187's allowed_paths

**Question.** S5 moves the bar to 95 % for fresh and standing runs (DEC-1179 (2)). The ticket lists six W2-170 to W2-172
files for the test designer's revision (DEC-1156 (7)). Two more W2-171 files pin the 85 % bar and are not in
`allowed_paths`. At 87d6fd835 (the code and the designer's revisions merged) `tests/acceptance/W2-171` runs
`2 failed, 138 passed, 1 skipped`, and these are the two failures:
- `tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py:120-121`
  (`test_the_ledger_events_have_item_3s_fields`): plants 35 right of 40 and expects `"passes": True`. That is 85 %; at
  95 % the bar is 38.
- `tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py:82`
  (`test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result`): expects
  `BAR at least 34 right (NOT met)`; at 95 % the line reads 38.

The ticket's F5 says "W2-171's S5 case passes unchanged". That cannot hold for `test_w2_171_s5_misses_f2.py:82` at the
decided bar. The behaviour the case guards (a verdict below the bar is recorded as a result) is unchanged; only the
figure differs. Both the test designer (td-1) and the engineer (eng-1) found this independently.

**Options.**
- **(a) Route it as a path case (DEC-1156 (7)), recommended.** Add both files to W2-187's `allowed_paths` for the test
  designer, about 3 lines of values with `Rewrite-Reason: DEC-1179 (2)`, and read F5's "unchanged" as "with only its
  bar value revised", as F5 already reads for W2-170. Cost: one short test-designer batch (about 15 minutes) and a
  narrow check. Nothing else moves.
- **(b) Re-baseline F5 and S5's wording only (DEC-105).** The same two-file edit is still needed for a green suite, so
  this adds a register step without saving the edit. Cost: a decision record and the same batch.
- **(c) Defer.** W2-187 lands with two named reds in W2-171. Cost: the lead's verify is not green, and the landing
  refuses (no `skip_known.json` entry covers them).

**Recommendation:** (a). Confidence: high.
**What it blocks:** a green `tests/acceptance/W2-171` on this branch, and so DONE. The rest of the loop goes on: the
fix batch, `gov accept`, QA and review.
