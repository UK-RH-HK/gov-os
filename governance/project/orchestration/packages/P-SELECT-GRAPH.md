# P-SELECT-GRAPH: should the scoped selection also use W2-92's code graph? (for D-9; short form)

By the CTO (session 33b3628c), 2026-11-03, at the owner's request. **DECIDED (DEC-1062): (a), the trial in D-9; its result to the owner before anything is built.** Nothing changes
now.

**The question.** Today `select_tests.py` (the product's `gov.close.select.plan`) selects by the test map: a changed
path selects the suites the map ties to it. It misses a regression when a change reaches code that a suite exercises
but the map does not tie to that path; such reds surface only in the full run (the nightly, stopped by DEC-1049). The
owner asks whether the selection should also take the tests of every caller of a changed symbol, from W2-92's code graph
(now in `w2/integrate`: the code route asks the index by symbol name, then for its call edges in pages of 50).

**What the repository shows (2026-11-03):**
- Unit tests import the code: 148 of 203 unit test files import `gov`. A reverse call graph reaches them directly.
- Acceptance tests mostly do not: 37 of 983 acceptance files import `gov`; the rest drive it as a process (the `gov`
  command, `python -m gov.cli.main`). A call graph sees no edge from such a test to the code it exercises. So the graph
  alone would catch unit-level regressions and miss most acceptance-level ones.
- The code index is rebuilt with the store (codeintel; about a minute seeded), so it can be current at a change's head.

**The design that would work:** the union of three, never a replacement:
1. the test map, as today (the floor);
2. **callers:** for each symbol the change defines or edits, its callers by the reverse call graph (radius 1 to 2),
   and the unit tests among them or calling them;
3. **commands:** the same reverse walk stopped at a `gov` subcommand's handler (the CLI's command table names the
   handler of each subcommand), then the acceptance tests that run that subcommand (found once per index build by a
   plain scan of the tests for `gov <subcommand>` or the module form).
A cap protects the run: a change that reaches a hub (a helper every command calls) selects at most a set share of the
suite (e.g. 30 %), then falls back to the test map with a named note. Dynamic dispatch the graph cannot see stays
covered by the test map and the full run.

**Options:**
- **(a) Recommended: a measured trial in D-9, then adopt only if it proves itself** (question 5). A research agent
  replays the merges of the last two weeks whose reds were traced to a change (the nightly and close records), and
  computes for each: the test map's selection, the union's selection, which reds each would have caught, the extra cases
  and their seconds. Adopt if the union catches regressions the map missed at a bounded cost (for example a median of
  at most +30 % scoped cases); its home is a KPI line in the selection's product ticket (named in D-9's list), with the
  CTO's `select_tests.py` using it first (in the tools lane) once it has proven itself in use. About half a day for the
  trial; about a day to build (an engineer and a test designer), if adopted.
- **(b) Build it now, without a trial.** Faster, but against question 5, and the acceptance tests' process boundary
  makes its value uncertain without the command step.
- **(c) Leave the selection as it is.** The full run (now about 1.8 h, DEC-1061) catches what the map misses, but only
  when it runs (the owner's word, D-10, then the nightly).

**Basis:** question 3 (tests run where the risk is: the change and everything it reaches) and question 2 (a regression
the map misses would otherwise reach the integration branch), with question 5 deciding the order (trial before product).
