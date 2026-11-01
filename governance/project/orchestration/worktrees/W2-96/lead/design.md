# W2-96 design note: `gov accept <ticket>`, the opaque acceptance runner (behaviour only)

**What it is.** A read command, `gov accept <ticket> [--timeout <seconds>] [--json] [--root <path>]`. `<ticket>` is
a ticket id (the file `.tickets/<id>.md` under the project root) or that ticket's WBS id (its `wbs_id` field). It
runs the folder named by the ticket's `acceptance_tests.path` with the project's own `src/` first on the
import path, and reports per KPI line of the folder's `README.md` map: pass or fail, with counts. Nothing else.

**1. The README's KPI map (the form designers' READMEs use today, W2-61, W2-69, W2-71, W2-72).**
- *Row form:* a Markdown table whose header row has a column whose title begins with `KPI` (any case) and a
  column whose title begins with `Test` or `File`. Each body row maps the backticked items of its Test/File cell
  to the KPI line(s) named at the start of its KPI cell.
- *Heading form:* a table with a Test/File column and no KPI column, under the nearest heading (any level)
  whose text begins with KPI line names (`### KPI 1: …`, `### K2 — …`, `### Success 3 …`), maps its items to
  those lines. A table under a heading that names no line maps nothing.
- *KPI line names*, at the start of a cell or heading, several joined by `/`, `,`, `;` or `and`, any case:
  `success N`, `S N`/`SN`, `KPI N`, `K N`/`KN` (all three mean success line N) and `failure N`, `F N`/`FN`. They
  are reported only in the normal form `success-N` / `failure-N`, never as the README's text.
- *Items:* each backticked item in the Test/File cell. `name.py` (or a path ending in it) means every test in
  that file; `name.py::test_x` that one test; a bare word means every test whose function name (before any `[`)
  is that word or `test_` plus that word. Anything else in the cell is ignored. Text outside the map is ignored.
- No README, or a README with no map (no row maps a line): refused, `ACCEPT_NO_MAP`. No raw fallback, ever.

**2. The child run, and how its results are read without its text.** pytest runs in a child process
(`python -m pytest <folder>` with the project root as working folder, `PYTHONPATH=<root>/src`, its own
`--basetemp` and a JUnit XML file both inside one private temporary folder outside the repository, the cache
plugin off, no bytecode written, `PYTEST_ADDOPTS` and similar caller settings dropped, stdin closed). Its stdout
and stderr go to the null device, never captured. The JUnit file (xunit1, so each case has its `file`; captured
output not logged into it) is read only for each case's file, function name and outcome: no `failure`,
`error` or `skipped` element's message or text, no `system-out`/`system-err`, is ever read. Each case is then
mapped to the KPI lines whose items match it; a case no item matches is `unmapped`.

**3. Temporary files.** One private temporary folder (under `TMPDIR`), holding the JUnit file and the basetemp,
removed in every path (pass, fail, error, timeout, an exception of the runner's own, Ctrl-C). Nothing written
in the repository: no `.pytest_cache`, no `__pycache__` from the child, no report file.

**4. Outcomes.**
- A case passes when it has no failure or error element; `skipped` is counted apart; an error (setup/teardown)
  or a failure counts as failed.
- A KPI line passes when at least one case maps to it, none failed, and at least one passed. A line with no
  matching case fails (nothing proves it).
- Run errors, reported as `error` for the run with their kind only, and no line reported pass or fail:
  `collection` (pytest exit 2 or 5, or any collection error in the JUnit file), `timeout` (the child passed
  `--timeout`, default 1800 s; its whole process group is killed), `crash` (pytest exit 3 or 4, killed by a
  signal, the JUnit file missing or unreadable, or any unexpected exception in the runner itself). Never a
  message, a traceback or a path inside the folder.

**5. Exit codes.** 0: every mapped line passes. 3 (declared): a mapped line fails. 4 (declared): the run errored.
1: refused (`ACCEPT_NO_MAP`, `ACCEPT_UNKNOWN_TICKET`, `ACCEPT_NO_TESTS` for a ticket with no acceptance path or a
path that is not a folder inside the root); the refusal names only the ticket and the ticket's declared path.
Unmapped cases never change the exit code.

**6. The JSON (`result` of the API-0002 envelope `{ok, command, result, error?, session}`; `ok: true` for pass,
fail and error, `ok: false` only for a refusal).**
```
{"ticket": "DAEO-xxxx", "outcome": "pass" | "fail" | "error", "error_kind": null | "collection" | "timeout" | "crash",
 "lines": [{"kpi": "success-1", "outcome": "pass" | "fail", "passed": 2, "failed": 0, "skipped": 0}, ...],
 "unmapped": {"passed": 1, "failed": 1, "skipped": 0},
 "totals": {"passed": 3, "failed": 1, "skipped": 0}}
```
Lines in order `success-1…`, then `failure-1…`. On `error`, `lines` is `[]` and the counts are 0. Without
`--json` the same `result` is printed as text. No test name, file name, parameter id, message or README text
appears anywhere in the output, the envelope, an error, stderr or a file left behind.
