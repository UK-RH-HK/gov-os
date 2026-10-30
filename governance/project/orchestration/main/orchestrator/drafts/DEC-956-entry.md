
### DEC-956 — W2-76's packages: the watchdog case's setup revised; the test harness gives each run its own rebuild lock (delegated)
- **Status:** ACCEPTED (orchestrator, delegated under DEC-936 item 2.5: P2, reversible, the orchestrator's recommendation and the lead's agree, confidence medium-high, nothing in the Charter, the master rules or the Contract's scope, the guard not weakened; for the owner to overturn) · **Under:** DEC-953, DEC-954 Q5, DEC-939 item 2, ADR-0001 · **Basis:** W2-76's run-1 return (`log/W2-76-A5-run1.json`, 2026-10-30 20:27)
- **Decision:**
  1. **P-W2-76-1 (a):** a fresh independent test designer revises the setup of `tests/acceptance/W2-76/test_w2_76_watchdog.py::test_a_slow_rebuild_records_what_it_waits_on_and_goes_on`, so the slowed rebuild is the first on its tree (the lexical index is incremental by blob). It is the ticket's own test, revised before its close, with a `Rewrite-Reason:`; no expectation lowered.
  2. **P-W2-76-3 (a):** the machine-wide rebuild lock gets a lock-path override, which the test harness sets per run (the root conftest), and `src/gov/rebuild` reads it. The throwaway repositories of about 40 existing suites then never queue behind real rebuilds. W2-76's paths are widened by `tests/conftest.py`. Under ADR-0001, a session that sets the override on purpose is a row for the Wave 3 hardening pass, not a round.
  3. **Run 2 goes after ACT 1** (as W2-64's, DEC-954 Q2 reading): the revision, the override, then the selection's verification on the merged code.
- **Where it goes (DEC-851):** this register; W2-76's ticket (paths); its run-2 brief; RESUME HERE.

| Version | Date | Change |
|---|---|---|
| 0.339 | 2026-10-30 | Delegated (orchestrator, DEC-936 item 2.5): DEC-956 (W2-76: the watchdog case's setup revised by a test designer; a per-run rebuild-lock override set by the test harness; run 2 after ACT 1). Next free id: DEC-957. |
