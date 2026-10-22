
## 283. The owner's answer of 2026-10-22 on P-W2-58-C1 (register v0.283, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-896 — Decision records measured by their decision (a W2-07 KPI); the test-selection lists in their own file; W2-07 before the first re-pin; no close unless every pre-close gate predicts a pass
- **Status:** ACCEPTED (owner, 2026-10-22, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`) · **Under:** DEC-490, DEC-500, DEC-734, DEC-891, DEC-892, DEC-894, DEC-889, DEC-890, DEC-884, DEC-861 · **Basis:** package P-W2-58-C1 (`governance/project/orchestration/packages/P-W2-58-C1.md`). W2-58's close was refused on WORK_WITHOUT_TASK for seven `Task: decision-record` commits that changed its paths (the path map) or its ticket file; W2-63's range holds one such commit.
- **Decision:**
  1. **(a), a W2-07 KPI, rule-based:** a decision-record commit that changes only governance records, under an ACCEPTED decision, counts as measured for the work-without-a-task gate. **Not (c):** a decision-close would hide the gap.
  2. **(d), corrected.**
     - The orchestrator's commits that change a ticket file carry that ticket's `Task:` (as the prompt §7 says), with `Implements:` and `Role: orchestrator`.
     - W2-66's draft must edit the path map's shared-core and record-only lists, which conflicts with "no ticket names the path map". So **the test-selection lists move into their own file**, for example `governance/project/test-map.yaml`, owned by W2-66 and W2-68.
     - **The path map stays a shared record that no ticket's allowed paths name.** This applies to the W2-66 and W2-68 drafts.
  3. **Priority:** W2-07 comes forward to sit with W2-66, before the first re-pin, so that the first re-pin carries W2-07 too. Its KPIs:
     - the work-without-a-task rule of item 1;
     - test-revision tickets judged on their declared `acceptance_tests.path` (DEC-892);
     - a stale probe named before the close spends its run (W2-M403).
     W2-07's card is drafted for the review bundle (DEC-889 item 14).
  4. **Until that re-pin, no close starts unless all pre-close gates (a) to (h) predict a pass:**
     - (a) the collection;
     - (b) `gov check`;
     - (c) a fresh checkpoint;
     - (d) the tree as the close reads it;
     - (e) the trailers as the close reads them;
     - (f) the record-reading suites;
     - (g) the network;
     - (h) the work-without-a-task gate with the pinned code.
     W2-58 and W2-63 wait for the re-pin.
- **Changes:**
  - DEC-884 and DEC-889 item 15 (the first re-pin now carries W2-07: W2-58, W2-59, W2-65, W2-66, W2-07);
  - DEC-890 (W2-66's and W2-68's paths: the test map in place of the path map);
  - DEC-892 (W2-07's KPIs gathered).
- **Where it goes (DEC-851):**
  - this register, with DEC-884's and DEC-890's status lines marked;
  - the prompt §3 (order; the re-pin), §7 (ticket-file commits) and §15 (the pre-close gates (a) to (h)), v3.16;
  - RESUME HERE;
  - the review bundle's drafts of W2-07's, W2-66's and W2-68's cards;
  - the orchestrator's queue script (gates (a) to (h) all in place).
  It does not reach the lead or auditor briefs: leads do not commit ticket files or the path map.
- Next free id: DEC-897.

| Version | Date | Change |
|---|---|---|
| 0.283 | 2026-10-22 | Owner (recorded by the orchestrator, DEC-861): DEC-896 (P-W2-58-C1 (a) with (d) corrected: a W2-07 KPI counting decision records under an ACCEPTED decision as measured; ticket-file commits carry the ticket's Task; the test-selection lists in their own file, the path map named by no ticket; W2-07 with W2-66 before the first re-pin; until then no close unless gates (a) to (h) predict a pass; W2-58 and W2-63 wait). Next free id: DEC-897. |
