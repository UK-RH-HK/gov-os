
## 288. Delegated decisions of 2026-10-23 from W2-66's and W2-07's first runs (register v0.288, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-903 — W1-39's overlay case named for W2-66's test designer; `src/gov/cli/errors.py` in W2-66's shared core; W2-07's six interface readings (delegated)
- **Status:** ACCEPTED (delegated, orchestrator, 2026-10-23, under the prompt §7: P2, reversible, the proposer's recommendation and mine agree, confidence high or medium-high; it changes nothing in the Charter, the master rules or the Contract's scope, and does not weaken the guard; `Task: decision-record`, `Role: orchestrator`). The owner may overturn it. · **Under:** DEC-896 item 2, DEC-899 items 1 and 2, DEC-889 item 16 d, DEC-866, MR-3 · **Basis:** W2-66's return of run 1 (P-W2-66-T1, its record edits) and W2-07's return of run 1 (P-W2-07-C), `governance/project/orchestration/packages/P-W2-07-A-B.md`.
- **Decision:**
  1. **P-W2-66-T1 (a).** `tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay` asserts that `copier copy` makes an overlay holding exactly the path map (DEC-493). DEC-896 item 2 and W2-66's paths ship the test map's template copy too, so the case is outdated, not wrong.
     - W2-66's ticket file names `tests/acceptance/W1-39/test_w1_39_copy.py` among its test designer's files.
     - A fresh test designer revises that one case to "the path map and the test map", with `Rewrite-Reason: DEC-896 item 2`, lowering no other expectation.
  2. **A path corrected in W2-66's KPI and card:** the CLI's error module is `src/gov/cli/errors.py`, not `src/gov/errors.py`. P-IS-1 (a) (DEC-899 item 1) named it by its file name only (lens I's I4 F12). The shared core holds `src/gov/cli/main.py` and `src/gov/cli/errors.py` until measured.
  3. **P-W2-07-C, the six interface readings, accepted as the lead read them:**
     - the evidence of an integration or coordination ticket is named in `acceptance_tests.evidence`;
     - a probe record's findings are a front-matter `findings` list, and the owner's decision names each with its row;
     - the close commits the repair ticket alone;
     - a class the KPIs do not name is judged on its acceptance tests;
     - baseline refusals are read as gate refusals;
     - a name clash between two suites collected in one process is not checked.
     Ticket files for research, integration and coordination tickets will need `acceptance_tests.evidence` lists; each gains one when it next starts.
  4. **Not now:** the path map's `test_inputs` key moves into W2-66's test map, but its removal from the path map waits for W2-66's merge, since today's code still reads it. The orchestrator removes it in the merge's follow-up record edit.
- **Where it goes (DEC-851):** this register; W2-66's ticket file and card (its own commit, `Task: DAEO-c1uz`); RESUME HERE. No brief changes.
- Next free id: DEC-904.

| Version | Date | Change |
|---|---|---|
| 0.288 | 2026-10-23 | Delegated (orchestrator): DEC-903 (W1-39's overlay case named for W2-66's test designer, outdated by DEC-896 item 2; `src/gov/cli/errors.py` corrected in W2-66's shared core; W2-07's six interface readings accepted; the path map's `test_inputs` removed at W2-66's merge). Next free id: DEC-904. |
