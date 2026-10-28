# Lead checkpoint — DAEO-2gc7 (W2-68), run 1

- **State:** design drafted by the lead (`design-draft.md` here). Worker eng-0 (engineer, sandboxed, `--effort high`) writes `docs/research/W2-68-batched-close.md` from it. No code, no tests yet.
- **Branch head at start:** 966b9f6b5596 (clean). Base: w2/integrate.
- **Plan (this run's order):** 1 note (eng-0) → 2 test designer (td-1, xhigh) → red check (lead) → 3 engineer batches (eng-1..) → 4 trial → 5 rebuild + full verification (close's form, lock, retention) → 6 review 1 (max) [→ fix round → review 2] → return.
- **Decisions taken by the lead:** the batch is `python3 -m gov.close.batch run|refresh` (no new gov command); the batch's run record is a nightly-form record in `docs/close/nightly/` (`kind: batch`); reuse reads only W2-66's green records; the governance check result of a batch is reused by closes on the same code fingerprint; the batch commits nothing (the caller commits its record and each close's outputs).
- **Loop count:** 0.
- **Workers:** eng-0 launched (log `log/eng-0-note.json`, tripwire `tripwire-before-0.json`).
- **Guard read refusals so far (lead):** 0.
- **Resume:** if eng-0's log has a final JSON, read its `result`, check the twelve fields, tripwire compare, check its commit's trailers, then write the test designer's brief.
