# W2-115 — the smart close: evidence and the S9 measurement

Ticket DAEO-emq1 (W2-115), build run 2, engineer. Branch `w2/W2-115`. The scoped close is `gov close` when
`governance/project/close.yaml` holds `close: scoped`; without the file it is the strict close, unchanged.

## S9 — `close_build.py` and this close, side by side on three recorded batches

`close_build.py` could not be run from the engineer's sandbox: it clones into `~/gov-os-runs/W2-00/close/`,
rebuilds stores, runs gitleaks and writes the main repository's records, all outside the sandbox's write paths, and
each recorded run took between 1.3 and 3 hours. So its **recorded** verdicts are used, cited by path, and this close's
side is computed from the same records: each red's runs alone with and without the change (close_build's `trace`,
`flaky_candidates`) go through this close's own judgement (`gov.close.attribution.judge`), the failure type read
from the run's own `parallel.xml` by this close's reader (`gov.close.attribution.failure_type`), and the scoped
close's rule applied (a caused red refuses, every other red closes with a repair ticket).

Records: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-build/<run>/`
(`run.json`, `close.txt`, `parallel.xml`, `unowned.txt`).

| Batch | Kind | close_build.py verdict | This close's verdict | Equal |
|---|---|---|---|---|
| `W2-71-20261030-161658` | clean | CLOSED | CLOSED | yes |
| `W2-107-20261031-184805` | caused red | REFUSED | REFUSED | yes |
| `W2-107-20261031-202743` | unowned red | CLOSED | CLOSED | yes |

Equal on all three. The details, per batch:

- `W2-71-20261030-161658` (clean): `close_build.py` recorded `CLOSED (build-phase close, DEC-953)`. No red alone; the
  parallel run's one failure (`W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here`)
  was green alone, a flaky candidate. This close: not the change's (`green when run alone`), so CLOSED.
- `W2-107-20261031-184805` (caused red): `close_build.py` recorded `REFUSED: 1 test(s) red alone, caused by this
  change`. This close: `W1-27/test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime` red
  alone with AssertionError 3/3 and green without the change 0/3: caused, so REFUSED (`RED_CAUSED`); the other red
  (`W1-28/test_w1_28_fixture_copies.py::test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs`) not caused.
- `W2-107-20261031-202743` (unowned red): `close_build.py` recorded `CLOSED (build-phase close, DEC-953)`, the red
  named in `unowned.txt`. This close: the W1-28 red with AssertionError 3/3 and red without the change 3/3, not
  caused, named in the record with a repair ticket; the W2-50 failure green alone, so CLOSED. Two limits, stated: (1) `close_build.py` records the run without the change by its exit code
only, so a red there is taken to carry the same failure type as the run with the change (this close checks the type
itself; on these records it cannot); (2) none of the fifteen recorded runs had a parallel run with no failure at
all, so the clean batch is the one whose only failure was green alone. The script that computed this close's side
ran from the engineer's sandbox scratch (`s9.py`, 50 lines: it reads the three `run.json` and `parallel.xml` and calls
`attribution.judge`).

## One row per KPI line

| Line | What was built | Unit tests (`tests/unit/close/test_w2_115_*.py`) |
|---|---|---|
| S1 the switch | `command.close_mode`: no file → strict (the strict code path untouched, reached first), `scoped`/`strict`, anything else `CLOSE_MODE_INVALID`; both `close.yaml` files read `close: scoped` | `select.py`: 5 |
| S2 scoped selection | `select.scoped`: the change is every path since the newest green record (the strict close's `select.base`) with the ticket's own commits (eng-2: a record commit without the ticket's trailer, or a path merged since the green base, is the change); own suite, couplings, test files, other tickets' paths, the import graph (and a module named as text); records alone → `record_reading` and nothing else (not even the own suite); `governance/project/` alone → nothing; unmapped → `SELECTION_REFUSED`; never `tests/` whole | `select.py`: 11; `close.py`: 2 |
| S3 `--select` | prints `{"ticket","suites","pytest_options"}` (the options the same on every machine: `--timeout=<per-test limit>` always; without pytest-timeout the run does not complete, fail closed), exit 0; refused: stderr, exit 2; the close record's `selection` is the same object | `select.py`: 2; `close.py`: 1 |
| S4 attribution | `attribution.attribute`/`judge`: every failing test alone; one run each way, 3 for a load-sensitive case: an entry of the serial phase's own list (`tests/acceptance/serial-only.txt`) whose comment's kind is `latency` (eng-2, the lead's answer P-TD-1 (a); no marker); timeout/unknown/absent never match; the nightly read first, standing for the run without the change only when that night ran the full suite on that very commit; no baseline clone | `attribution.py`: 14 |
| S5 unowned red | `tool.open_red_repair`: a repair ticket in `.tickets/`, `assignee: orchestrator`, node id and type in its text, reused while open; no list read or written (`ratchet` and its gate untouched by the scoped close) | `close.py`: 1 (with every `ratchet` reader made to fail) |
| S6 batches | `batch.isolate` (`python3 -m gov.close.batch isolate`): fresh merges without each candidate; culprits back, the rest run green again and landed; `BATCH_UNEXPLAINED`, `CANDIDATE_NOT_ISOLATED`; landing only after every candidate is judged; eng-2 (the lead's answer P1 (a)): `python3 -m gov.close.batch run <ticket> ...` in a scoped project is `batch.run_scoped`: each ticket's `w2/<wbs_id>` branch a candidate (none, or already merged: `CANDIDATE_NOT_ISOLATED`), each ticket's review READY first, `isolate` on `HEAD`, the landed tickets closed with `commit` = the land commit and `culprits` named, the culprits not closed; strict: today's | `batch.py`: 10 |
| S7 close record | front matter keys `close, commit, selection, runs, review, reds, culprits, clone, nightly` (and `base`, `changed`) | `close.py`: 1 |
| S8 nightly | `nightly.rebuild_stores`: `gov rebuild` (its own code, in-process, as the batch's) of the project worktree's stores with `GOV_SECRETS_FULL_SCAN=1` set for the rebuild whatever the caller's (and put back after), before the run (eng-2: the project's stores, not the night's temporary worktree); the record adds `secrets_full_scan` alone (true/false, nothing time-varying; a failed rebuild's error on stderr); the strict batch's night does not rebuild again | `nightly.py`: 4 |
| S9 measured | above | — |
| S10 warm clone | `attribution.prepare`: `.gov-runtime/close/clone/`, fetched, reset, cleaned with `.gov-runtime/` kept; replaced with the reason when it cannot be reset | `attribution.py`: 2; `close.py`: 1 |
| S11 READY computed | `command.review_verdict`: the newest committed probe record's last ```verdict block; writer judged by the commit that last changed the block (`Role: independent-auditor` alone); `VERDICT_MALFORMED` (no block on FULL, not the form, a KPI line S1..Sn/F1..Fn missing, a bad value), `VERDICT_NOT_REVIEWER`, `FINDING_BLOCKS` (a line marked fail, or in/yes/fails open or loses work) | `verdict.py`: 9; `close.py`: 1 |
| S13 `--verify` | `command._verify_command`: `select.json`, `parallel.xml`, `serial.xml`, `summary.txt`, `verify.exit` last; 0/1/2/3; the serial phase is `gov.close.serial.phase` on the entries inside the selection; each run in a heavy-job slot where the machine configures them | `verify.py`: 5 |
| F1 | a caused red refuses (`RED_CAUSED`), an unowned red closes | `close.py`: 2 |
| F2 | the runner's call list holds only the selection; no list read | `close.py`: 2 |
| F3 | a culprit never lands; an unexplained red lands nothing | `batch.py`: 3 |
| F4 | the strict close's suites pass unchanged (W1-30, W2-07, W2-57, W2-66, `tests/unit/close`) | the strict suites |

S12 (the trailers switch) is not built in this run (P4: its CIT-P, review and the owner's approval first).
