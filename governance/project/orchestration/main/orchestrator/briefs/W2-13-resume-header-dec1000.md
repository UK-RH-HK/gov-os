# W2-13 (DAEO-zqvn) — resume after P-W2-13-1 and P-W2-13-3 (2026-11-01, DEC-1000, delegated)

**Read this first; it overrides the run's steps below where they differ.** Your run 1 returned PACKAGES at
`12bca6c5`. The CTO decided (DEC-1000, delegated, P2s):
- **P-W2-13-3 (b):** the build stays as it is (`hits` exact, a separate `ranked` list carries the BM25 order). One
  fresh test-design batch (a tests worktree as before, effort xhigh) rewrites W2-13's 7 S1/S2 cases to read `ranked`,
  `Rewrite-Reason: DEC-1000 (P-W2-13-3 (b))`, lowering no expectation; W1-17's and W2-87's cases are untouched.
- **P-W2-13-1 (a):** the one-line change in `src/gov/retrieve/retrieve.py` (fuse `answer.get("ranked", answer["hits"])`)
  is W2-13's, but W2-92 holds that file while it runs. **Do not touch it in this resume.** The CTO adds the path to
  your ticket and merges `w2/integrate` into your branch once W2-92 has landed; a later short resume makes the line.
  Until then, success 2's bundle case may stay red: name it in your return as waiting for W2-92, not as yours.
- **TD-1:** the closure's half goes to the ticket that owns `src/gov/closure/**` as a Wave 2 list residual (return
  it as a residual). **TD-2 (a):** whole tokens; the trigram table is a W2-32 or Wave 3 row.
- **Do now:** the test-design batch above and, in parallel, one engineer batch for the latency fix (DEC-802 ride-along);
  merge the tests while no worker runs; `gov accept` once; then hold the scoped run, the review and the probe record
  until the `retrieve.py` line is in (one merge per ticket, DEC-988: no interim landing). Return PACKAGES naming only
  "waiting for W2-92's landing" if that is the one thing left, with your head.

---

