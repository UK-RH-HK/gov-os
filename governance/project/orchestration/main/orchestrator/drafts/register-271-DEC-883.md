
## 271. The owner's decision of 2026-10-21 for W2-66: batched closes on one head, no repeat regression on the same code (register v0.271, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-883 — Batched closes (a merge queue): one rebuild, one check and one full regression per integrated head; same code, no repeat regression; the index fresh by code fingerprint; the serial-only tests examined
- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-880, DEC-881, DEC-879, DEC-726, DEC-780, DEC-868, DEC-866, DEC-861 · **Basis:** the orchestrator's measurement of the close queue of 2026-10-21. A close takes about 85 minutes: a full rebuild of about 6 min, `gov check` of about 7 min, and `gov close` of 72 min, of which the ticket's own suite is 24 s, the parallel regression 31 min and the serial-only tests 29 min. The queue's six closes run the same code six times, because only records are committed between them. The pinned judge has no way to reuse a run, and needs a store built at exactly HEAD. Lens H's findings refine the details when they come (DEC-881).
- **Decision (for W2-66):**
  1. **Batched closes, a merge queue.** Queued closes on the same integrated head form one batch:
     - a. one rebuild, one `gov check` and one full regression for the whole batch, on that head;
     - b. then each ticket's own checks, one after another: its acceptance suite, the tests that read records, its trailers, paths, probe record and checkpoint;
     - c. no code merges into `w2/integrate` while a batch runs (as DEC-879 does today); merges wait for the batch to end;
     - d. each close record cites the batch's run (its fingerprint and commit), and states its validation scope under the evidence rule.
  2. **When a batch's regression fails:**
     - a. no ticket in the batch closes on that run;
     - b. the failure is attributed to its cause, by `git bisect` over the batch's merges or by the failing tests' own ticket, and recorded with the evidence;
     - c. the ticket that caused it gets its repair; the batch re-runs once that fix is in. A ticket proven unrelated still waits for a green run: a close never cites a red regression;
     - d. a cause outside every ticket (the environment, load, records) is fixed by the orchestrator and recorded, as today.
  3. **Same code, no repeat regression.** A close whose code is byte-identical to the last fully passing run reuses that run as its evidence, and runs only its own ticket's checks. Byte-identical means the same tree fingerprint, which leaves out record-only paths such as `docs/checkpoints/` and `governance/project/orchestration/`. A failing run is never reused, and any code difference means a fresh run.
  4. **The same fingerprint for the index.** The store-freshness check accepts a store built on the same code fingerprint, so a record-only commit doesn't force a full rebuild.
     - The orchestrator's design note for W2-66 and lens H to settle: the record store indexes records itself, so it still has to hold the record-only commit's records (for example the new checkpoint). That part is an incremental load of the changed records, measured in seconds; the lexical, semantic and code indexes are reused when the code fingerprint matches.
  5. **The serial-only tests** (263 tests, 29 minutes): find out why each must run alone, and run in parallel every one that safely can. This goes to lens H's findings and W2-57.
- **Target:** a batch of queued closes in about the time of one regression plus a few minutes per ticket; measured and reported.
- **Until W2-66 lands, today's queue runs as it is.** Items 3 and 4 change what the judge accepts, so they take effect only after a re-pin that holds W2-66.
- **Where it goes (DEC-851):**
  - this register;
  - W2-66's card in `docs/plan/WAVE_2_WBS.md` and its ticket file `.tickets/DAEO-c1uz.md` (KPIs, paths, estimate);
  - W2-57's card (item 5);
  - the prompt §3 (closes) and §15 (closes), v3.9;
  - RESUME HERE.
  It does not reach the lead or auditor briefs: leads run no closes, and their full verification stays (DEC-880 item 2 (b)).
- Next free id: DEC-884.

| Version | Date | Change |
|---|---|---|
| 0.271 | 2026-10-21 | Owner (recorded by the orchestrator, DEC-861): DEC-883 (batched closes on one integrated head: one rebuild, one check, one full regression, then each ticket's own checks; a red batch closes nothing and is attributed by bisect; same code reuses the last passing run; the index fresh by code fingerprint; the serial-only tests examined; target about one regression per batch). Next free id: DEC-884. |
