
## W1-30 follow-up: the parallel test runs of `gov close`, the serial-only list, the rebuild without embeddings (DEC-527 to DEC-532, DEC-549, DEC-554, DEC-555; 2026-10-09)

Merged from `w1/W1-30` at `c52de7c2` (probed at that commit; 355 cases in the suite). Built: `gov close`
runs the ticket's acceptance tests and the regression tests with the installed runner's parallel option, and
the cases that `tests/acceptance/serial-only.txt` names (53 entries here) alone afterwards, each once; the
plugin that keeps them out is `src/gov/close/pytest_plugin/gov_close_serial_only.py`; the close record and
the result state each run under `test_runs`; `close_workers` (default `auto`) and `close_timeout` are
optional top-level keys of `governance/project/path-map.yaml`, refused with `INVALID_WORKERS` or
`INVALID_TIMEOUT` when of a wrong shape; `gov rebuild --no-embeddings`. Test-side repairs, each with
"defect found by the parallel trial": two W1-50 files that set their own import path, the pause's unit case,
W1-27's own wait for its commands (180 s), W1-30's temporary projects with two workers. This repository's
path map now says `close_timeout: 7200`.

As measured by the lead (two whole regressions in the close form, other leads' suites running beside them):
the ticket's own run 142 to 152 s, everything else in parallel 793 to 1038 s, the declared cases alone 1341
to 1968 s. A close of this repository: about 16 to 20 minutes for the parallel part and 28 to 33 for the
serial part, against 80 to 110 minutes before.

From the probe (session `2e97ad0c-eee6-4500-baae-303e79f117f7`; record in `docs/probes/DAEO-2lwj/`).
**To be built in the follow-up after W1-41 (DEC-555), test designer first:**

- **Fails open, deliberate or unusual shape:** a run of the declared cases that ends with exit code 0 and no
  result (a case that ends its own process with 0) is accepted; the parallel run's passes cover it. Until
  the follow-up, the orchestrator reads each close's `test_runs`.
- **Closes by the caller's input, deliberate:** a file in the project named like the close's plugin (under
  `src/` or at the root) replaces it, so a ticket's own commit can keep a failing case out of every run.
- Parallel workers outlive a run cut at the time limit: they finish their cases during the serial run and
  after the close has returned, and can still write into the project. The close is refused either way.
- A list entry that names an existing file with no case in it refuses nothing (only a file or function that
  does not exist does), against DEC-549's fourth point.
- A byte in the list that is not UTF-8 ends the close in a traceback (fails closed).

**Residuals, not planned:**

- Counts that do not match what ran for entries outside the documented forms: a parent folder as an entry
  counts cases twice in `tests_run`; a trailing slash, `//` or `..` in an entry runs its cases twice.
- `test_runs` says `parallel` with `workers: auto` for a run in which the runner started no worker (a
  machine that sets the runner's own worker-count variable to 0); the record states `auto`, not the number.
- `close_workers` has no upper bound; YAML's own readings (`010` as 8, `1:30` as 90) are accepted; a time
  limit of about 9.2e9 seconds or more ends in a traceback.
- A list path that is a folder declares nothing; a byte-order mark drops the first entry silently (its cases
  then run in parallel).
- An unusable parallel plugin (autoload switched off by the caller, `-p no:xdist` in the project, a project
  folder named like it) is a finding counted against the ticket, not "could not measure".
- Without the parallel plugin the close runs serially with a note and no finding.
- The rebuild mode does not remove vectors an earlier full rebuild left in the store (the semantic status
  reports them stale once an embedded file changed); a full rebuild runs before W1-42's retrieval
  measurements (DEC-530).
- A close started inside a parallel worker passes the runner's worker variable on to its own runs.
- W1-36's helper takes any `PYTHONPATH` that contains the `src` path as a substring for the path itself.
- W1-27's `run_python_snippet` and one literal 30 s wait in its recovery cases keep the old bound.
- W1-07's 30 s wait for a read command was passed once under ten workers (`gov status --json`); re-run
  alone and named until a designer lengthens it in the follow-up after W1-41 (DEC-554).
- The kernel's path-map schema names neither new key (DEC-554, the same follow-up).
- One failure of the unit case `test_options_of_the_callers_environment_do_not_reach_the_run[--collect-only]`
  in run F1 is unexplained; it did not recur in ten unit runs.
- A path map in a small project brings the lexical index into its `gov rebuild`.
- Not probed: another version of the parallel plugin, a very large worker count, a close inside a parallel
  worker.
- **Latency under load (DEC-372):** W1-05's switch-over case failed once in the serial part at a load of 17
  (its child run's W1-02 p95) and passed alone.
- **KPI disputes:** none. **Acceptance tests rewritten after implementation began:** five support or fixture
  commits, each "defect found by the parallel trial"; no assertion changed. Added: rounds 11 and 12.
