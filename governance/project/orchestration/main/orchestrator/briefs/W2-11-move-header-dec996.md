# W2-11 (DAEO-k7hz) — one test-design batch: failure-1 leaves W2-11 (2026-11-01, DEC-995, DEC-996)

**Read this first; it overrides the round's steps below where they differ.** Your verification at `c895bb6283a6` is
accepted. The owner decided P-W2-11-9 (c) (DEC-995, DEC-996): W2-11's failure line "the skill validator refuses a
brief without the twelve-field rule" and row W2-L097 leave W2-11 for a child engineer ticket, W2-120, after W2-11; the
CTO removes the line from W2-11's ticket file in the main tree. **Your only work now:** one fresh test-design batch
(independent-test-designer, a tests worktree as before, effort high) that removes that one case
(`tests/acceptance/W2-11/test_w2_11_validator.py::test_the_validator_accepts_the_brief_and_refuses_it_without_the_twelve_fields`)
from W2-11's suite and updates the README map to say it moved to W2-120 (`Rewrite-Reason: DEC-995, DEC-996`), lowering
nothing else; W2-120's own designer will write it afresh. Merge the tests branch while no worker runs here, then run
W2-11's own acceptance tests once (`gov accept DAEO-k7hz`, or the plain run of W2-11's acceptance folder in the
close's form): nothing else (a test revision's scoped check, as P-W2-64-1 (a)). Known reds you saw are not yours: the
four W1-33 cases and the two W1-05 install cases were red in the 31 Oct nightly (W2-90b's). Return DONE with the exact
head. One merge per ticket: the CTO lands it through the merge queue (DEC-988, DEC-989).

---

