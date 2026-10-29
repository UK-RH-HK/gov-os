# W2-68 acceptance tests — batched closes, reuse on the same code, and two fingerprints

Ticket `DAEO-2gc7` (W2-68), profile FULL. Written by the independent test designer (MR-3) before the
implementation, from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md` §2, W2-68), DEC-883 items 1 to 4
(as DEC-889 changed them), DEC-884 item 4, DEC-889 items 2 and 4, DEC-890, DEC-880, DEC-899, DEC-906, DEC-919,
DEC-905, DEC-530 and DEC-487, and lens I's area 2 report (`docs/assessment/2026-10/I2-close-checks-ratchet.md`
§2.6). No implementation was read. The existing code was read as it stands on the base for its public interfaces
only (the close's envelope, evidence block and record; the store check; the lexical freshness check; `gov
rebuild`; the nightly record).

**The design note `docs/research/W2-68-batched-close.md` was not read:** the guard refused the read (DEC-820 (c):
it is in the ticket's diff). The interfaces below are the ones the lead's brief names from it; every other detail
is tested by behaviour, not by a name (see "Interface").

## How the suite runs

- **The code under test is this worktree's `src/`** (DEC-732). Run the suite with
  `PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-68 -p no:cacheprovider
  -o tmp_path_retention_policy=failed -n auto`. The check: `PYTHONPATH=<worktree>/src python3 -c "import gov;
  print(gov.__file__)"` prints `<worktree>/src/gov/__init__.py`. Every `gov` the suite starts goes through W1-07's
  console-script stand-in with `PYTHONPATH=<worktree>/src` (`w1_30_support.run_gov`, `sandbox_env`); the batch
  command and the lexical check are started as `python3 -m gov.close.batch …` and `python3 -m
  gov.retrieval.lexical` in the same environment. Nothing uses an installed `gov`.
- **Fixture repositories.** Every project is a temporary git repository built from scratch: W2-66's fixture project
  (`w2_66_support.Fixture`, imported from W2-66's folder, never copied), whose `src/gov/__init__.py` is a stand-in
  that appends this worktree's `gov` folder to the package's path. `w2_68_support.Project` adds, in one commit that
  a green nightly record names (the base, so none of it is in a close's change): ticket C (`PROJ-cccc`,
  `src/gov/gadget/**`) in progress beside ticket A (`PROJ-aaaa`, `src/gov/widget/**`); W1-07's minimal
  `.gitleaks.toml` (the rebuild's secret filter needs rules); a path map with W2-66's settings and one governance
  namespace holding every path (`**`, `embedding_policy: not embedded`), so the lexical index holds chunks (an index
  without any is "empty", which the freshness check never calls fresh); one declared check of the project's own
  (`template/governance/kernel/checks/w2-68-told.yaml`) whose command adds a line to a file outside the project at
  each `gov check`; and, where a case asks, a planted skip (W2-zz) or the red batch's two planted tests.
- **What ran is told by the tests themselves** (W1-30's telling tests): each run of a fixture test adds a line to a
  file of its own outside the project, with its xdist worker and the time. The red batch's two planted tests also
  tell the commit their file stood in (`git rev-parse HEAD` of their folder), so a run at another commit than the
  batch's head (a bisect) is seen.
- **The embedding endpoint is down** in every command: a dead local address in `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST`, and a stand-in for its program (`GOV_OLLAMA_BIN`) that only records a start (as W1-30's
  rebuild case). The suite's own rebuilds are `gov rebuild --no-embeddings` in its temporary projects.
- **Deterministic, no network, no live case.** No case needs a real model, so none is marked `local_only`. The
  semantic chunks' refresh with a real model is not tested here (see "Not tested here").
- **No `conftest.py`** (DEC-919): the fixtures are module-scoped fixtures of the test modules and the support
  module. Three modules share one scenario among their cases (`test_w2_68_batch.py`, `test_w2_68_reuse.py`'s
  same-code cases, `test_w2_68_red_batch.py`); under xdist each worker that takes one of a module's cases builds it
  once. Every case can run in the parallel phase; none needs `serial-only.txt`.
- Cost: a fixture close takes about 6 s; a scenario about 30–60 s. The suite's 22 cases run in a few minutes under
  `-n auto`.

## Interface

What the brief names from the design note, used as named:

1. **The batch:** `python3 -m gov.close.batch run <ticket> [<ticket> ...] --root <project> --json`, an API-0002
   envelope: `ok: true` and exit 0 when the batch's run is green; `ok: false` and a non-zero exit when it is red.
   The exact red exit code is not asserted (open in the brief).
2. **The incremental record load:** `python3 -m gov.close.batch refresh --root <project> --json`: `ok: true`, exit
   0 after a record-only commit; refused with `error.code` `STORE_CODE_CHANGED` (non-zero exit) after a code commit.
3. **The batch's run record** under `docs/close/nightly/`, with `kind: batch` (JSON or YAML). Read by behaviour:
   it names the batch's head (the full id or its first 12 digits), the code fingerprint the closes cite (the
   value, wherever it stands), and at least one JUnit XML file that exists (any string ending `.xml`, relative to
   the project or absolute).
4. **A close's evidence block** (W2-66's, in the close record's frontmatter and under `result.evidence`):
   `scope: reused`; the `reused` block citing the reused run; `code_fingerprint` and `records_fingerprint` (non-empty
   strings); `governance_checks_reused` (in the evidence or at the record's top level; truthy) for a close of a
   batch. The `reused` block's inner fields are not named by the tests: it must contain the close's own
   `code_fingerprint` value, the run's commit, JUnit XML files that exist, the reused run's skip count under a key
   holding both `skip` and `count`, and each skip's test name and reason.
5. **What a reused close runs:** its own acceptance suite and the record-reading set, nothing else. The fixture's
   test map has no `every_close` target, so whether an every-close target also runs on a reused close is not
   decided here (the sources name the record-reading set only).
6. **The store check:** `gov close` refuses `STORE_STALE` (exit code 1) on a store built on another code
   fingerprint, as today (DEC-487).
7. **The lexical freshness check:** `python3 -m gov.retrieval.lexical` in the project root, exit 0 only on a fresh
   index; it prints each stale path.
8. **A red batch:** what it says (its envelope and its run records, read as one text) names the red test, its
   failure text, and its cause: the commit that caused it (`git bisect` over the batch's merges; full id or its
   first 12 digits) or the failing test's own ticket (`PROJ-dddd`). A red that passes alone is named with the words
   "flaky candidate" (any of `flaky_candidate`, `flaky-candidate`, `flaky candidate`).

## KPI map

Expected red reason on the base, for every case: **(a)** `gov.close.batch` does not exist: `python3 -m
gov.close.batch` prints `No module named gov.close.batch` and no envelope ("… gave no API-0002 envelope"). Each
case's first assertion is on the batch's or the refresh's answer, so no case is red for another reason first.

| KPI line | Tests | Red on the base |
|---|---|---|
| S1 a batch: one rebuild, one `gov check`, one full regression on the head; then each ticket's own checks; each close record cites the batch's run (fingerprint, commit, JUnit XML) and its scope [DEC-883 item 1, DEC-890] | `test_w2_68_batch.py`: `::test_the_batch_closes_both_tickets`, `::test_one_gov_check_for_the_whole_batch`, `::test_one_full_regression_on_the_head_then_each_ticket_s_own_checks`, `::test_each_close_record_cites_the_batch_s_run_and_states_its_scope`, `::test_the_batch_s_closes_reuse_its_governance_checks`, `::test_the_batch_s_run_record_states_its_head_its_fingerprint_and_its_junit_xml`, `::test_a_ticket_of_the_batch_whose_own_check_fails_does_not_close_and_the_other_does` | (a) |
| S2 a red batch: re-run alone first; a red that passes alone is a flaky candidate, not bisected; a red that fails alone is attributed with the evidence; nothing closes on a red run [DEC-883 item 2, DEC-889 item 2 b] | `test_w2_68_red_batch.py`: `::test_nothing_closes_on_a_red_batch`, `::test_failing_tests_re_run_alone_first_at_the_batch_s_head`, `::test_a_red_that_passes_alone_is_a_flaky_candidate_and_is_not_bisected`, `::test_a_red_that_fails_alone_is_attributed_with_the_evidence`, `::test_a_close_after_a_red_batch_does_not_cite_its_run` | (a) |
| S3 same code: a close whose code fingerprint (record-only paths left out, the test map's `record_only` read) equals the last fully passing run's reuses it and runs its own checks and the record-reading set; a failing run is never reused; the reused evidence states the skip count [DEC-883 item 3, DEC-889 item 2, I4 F2] | `test_w2_68_reuse.py`: `::test_a_close_on_the_same_code_after_a_record_only_commit_reuses_the_passing_run`, `::test_a_reused_close_runs_its_own_suite_and_the_record_reading_set_and_nothing_else`, `::test_reused_evidence_states_the_reused_run_s_skip_count_and_its_skip`; never reused: `::test_a_close_that_cannot_reuse_the_run_runs_fresh_and_does_not_cite_it[code-commit]`, `[junit-xml-gone]` (a run that lacks its JUnit XML; W2-66's reading: a run cut at its time limit writes none), `[no-record-only-list]` (no test map: the record-only list cannot be read, so the fingerprint cannot leave the checkpoint out and the close runs fresh); a failing run: `test_w2_68_red_batch.py::test_a_close_after_a_red_batch_does_not_cite_its_run` | (a) |
| S4 two fingerprints: the code fingerprint governs the code index; changed record files refresh their chunks incrementally; a lexical index whose record files differ is never fresh [DEC-889 items 2 and 4] | `test_w2_68_fingerprints.py`: `::test_a_record_only_commit_is_loaded_incrementally_and_the_store_and_the_lexical_index_are_fresh`, `::test_after_a_code_commit_the_store_is_stale_and_the_incremental_load_refuses[code-commit]`, `[path-map-change]` | (a), at the refresh; the stale-index and `STORE_STALE` assertions hold on the base (guards) |
| S5 the path map counts as code [DEC-880, DEC-899] | `test_w2_68_reuse.py::test_a_close_that_cannot_reuse_the_run_runs_fresh_and_does_not_cite_it[path-map-change]`; `test_w2_68_fingerprints.py::test_after_a_code_commit_the_store_is_stale_and_the_incremental_load_refuses[path-map-change]` (in both, the test map lists the path map as record-only, and a comment line is the only change) | (a) |
| S6 W1-30's `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` re-read [DEC-889, I2 §2.6, DEC-906] | not changed: see "W1-30's case re-read" | — |
| S7 the trial (DEC-884 item 4) | not this suite's: the trial is the lead's measured run on a fixture or dev tier. Its four observables are each a case here: reuse correct (S3), a planted code change forcing a fresh run (`[code-commit]`), a planted record-only commit running the set and nothing else (`::test_a_reused_close_runs_its_own_suite_and_the_record_reading_set_and_nothing_else`), a red batch attributed with nothing closing (S2) | — |
| F a close that cites a red run or another fingerprint's run | `test_w2_68_red_batch.py::test_a_close_after_a_red_batch_does_not_cite_its_run`; the fingerprint asserted equal in `::test_each_close_record_cites_…` and `::test_a_close_on_the_same_code_…`; `[code-commit]`, `[path-map-change]` | (a) |
| F a reused run on different code | `test_w2_68_reuse.py::…[code-commit]`, `[path-map-change]` | (a) |
| F a store accepted on another code fingerprint | `test_w2_68_fingerprints.py::test_after_a_code_commit_…[code-commit]`, `[path-map-change]` | (a) |
| F a lexical index fresh with changed records | `test_w2_68_fingerprints.py::test_a_record_only_commit_…` (stale before the load, named), `::test_after_a_code_commit_…` | (a) |
| F a code merge during a batch | as the brief reads it: a close after a code commit does not reuse the batch's run, `test_w2_68_reuse.py::…[code-commit]` | (a) |
| F a red that passes alone being bisected | `test_w2_68_red_batch.py::test_a_red_that_passes_alone_is_a_flaky_candidate_and_is_not_bisected` (it never runs at another commit than the batch's head, and runs exactly twice) | (a) |
| F reused evidence that hides a skip | `test_w2_68_reuse.py::test_reused_evidence_states_the_reused_run_s_skip_count_and_its_skip` | (a) |

## What each scenario does

- **The batch** (`test_w2_68_batch.py`): A's and C's work and checkpoints committed; no store yet; one `batch run
  PROJ-aaaa PROJ-cccc`. One full regression: every case outside A's and C's suites ran exactly once (the serial-only
  cases and `tests/unit` included); after the last of those runs, A's and C's suites each ran again and the
  record-reading case ran exactly twice (once per ticket). One `gov check`: the declared check told one run. Each
  close record: `scope: reused`, a `reused` block holding the close's `code_fingerprint`, the batch's head and JUnit
  XML that exists and holds the full regression's cases; `records_fingerprint`; `governance_checks_reused`. The
  last case: C has no checkpoint, so its own checks refuse it (`CHECKPOINT_MISSING` in what the batch says) and A
  still closes on the batch's run.
- **Reuse** (`test_w2_68_reuse.py`): C's work, then A's, A's checkpoint, `batch run PROJ-aaaa` (head H), what the
  batch left committed by the orchestrator, then C's checkpoint (record-only) and `gov close PROJ-cccc`. On the same
  code it reuses H's run and runs exactly C's suite once and the record-reading case once. Between the batch and
  C's checkpoint the parametrised case plants: C's second code commit; a comment line in the path map (listed
  record-only in that test map); the batch's JUnit XML files deleted (and the deletion committed where they were
  tracked); or nothing, in a project without a test map. Each runs fresh (`tests/unit` runs) and does not cite
  H's run (no `scope: reused`, and no `reused` block naming H).
- **The red batch** (`test_w2_68_red_batch.py`): C's work writes `BROKEN` into the gadget, which W1-dd's planted
  test reads (a red that fails alone; C's commit is the first bad one between the base and H; the test's own ticket
  is `PROJ-dddd`); W1-cp's planted test fails on its first run only. One `batch run PROJ-aaaa PROJ-cccc`: refused;
  neither ticket closed and no close record; each red ran twice at H first (the regression, then alone); the flaky
  one ran exactly twice, never at another commit, and is named a flaky candidate; the real red is named with its
  failure text and attributed to C's commit or to `PROJ-dddd`. Then `gov close PROJ-aaaa` neither reuses nor cites
  the red run (it may pass on a fresh run or be refused; either way it cites nothing of H).
- **The fingerprints** (`test_w2_68_fingerprints.py`): A's work, `gov rebuild --no-embeddings` (the lexical index
  fresh), A's checkpoint (record-only): the lexical check is not fresh and names the checkpoint file; `refresh`
  passes; the lexical check is fresh; `gov close` on that store (no load first) accepts it and closes A. After a
  code commit (`notes/later.txt`, as W1-30's case) or a path-map comment: `refresh` refuses `STORE_CODE_CHANGED`,
  `gov close` refuses `STORE_STALE` with exit code 1, the lexical index is not fresh.

## Not tested here

- **"One rebuild" is not counted.** No public interface tells how many rebuilds ran. The one observable would be
  the code-index tool's starts (`codebase-memory-mcp` on `PATH`), but in a launched session its daemon folder
  (`/tmp/gov-cbm-<uid>`) is read-only, so the count would differ between a session and the close. The batch case
  holds what the rebuild is for: no store before the batch, and both closes pass their store check inside it.
- **The code index itself** ("the code fingerprint governs the code index") is observed through the store check and
  the refresh's refusal, not through the code-index tool, for the same reason.
- **The semantic chunks' refresh with a real model**: the endpoint is down in every case; a case needing a model
  would be `local_only`, and none is written.
- **A run cut short** is tested as a run that lacks its JUnit XML (`[junit-xml-gone]`), not by planting a run cut
  at a time limit (the batch's run limit is not named by the brief).
- **Whether the store check accepts a code-fresh store after a record-only commit before any refresh** (DEC-883
  item 4 says it accepts a store "built on the same code fingerprint"; its note says the record-only commit's
  records must be loaded): not decided by the sources the brief gives, so not asserted (see the return's package).
- **"No code merges while a batch runs"** as a lock: tested only as the brief reads it (a close after a code commit
  does not reuse the batch's run); a merge refused while a batch runs needs the integration branch's lock, which no
  named interface exposes.

## W1-30's case re-read (S6, I2 §2.6, DEC-906)

`tests/acceptance/W1-30/test_w1_30_r11_rebuild_mode.py::test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later`
**needs no change**. Its project has no test map (`settings=None`: no path map, so no test map either), so no
record-only list can leave any path out of the code fingerprint; its later commit is a file under `notes/`, which
no record-only pattern holds in any map (I2 §2.6: "a file under `notes/`, which a code fingerprint keeps"). The
commit changes code under two fingerprints as under one, and the case still requires `STORE_STALE` with exit code 1,
the ticket not closed and nothing counted. No expectation changes; no Rewrite-Reason commit was made. Its pair under
two fingerprints (a record-only commit refreshed and accepted; a code commit and a path-map change refused) is
`test_w2_68_fingerprints.py`.
