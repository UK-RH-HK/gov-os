# W2-115 — the smart close: evidence and the S9 measurement

Ticket DAEO-emq1 (W2-115), build run 2, engineer. Branch `w2/W2-115`. The scoped close is `gov close` when
`governance/project/close.yaml` holds `close: scoped`; without the file it is the strict close, unchanged.

## S9 — `close_build.py` and this close, side by side on three recorded batches

`close_build.py` could not be run from the engineer's sandbox: it clones into `~/gov-os-runs/W2-00/close/`,
rebuilds stores, runs gitleaks and writes the main repository's records, all outside the sandbox's write paths, and
each recorded run took between 1.3 and 3 hours. So its **recorded** verdicts are used, cited by path.

**The method, exactly (F-7).** "This close's verdict" below is **not** a run of this close (`gov close`) on those
batches: no test was run for this table, and no clone was built. It was **computed from close_build.py's records**:

1. **Run:** nothing of the tests. Only the script below, which reads three files per batch.
2. **Read from the records:** each batch's `run.json` (close_build's own verdict string; its `flaky_candidates`, the
   reds it recorded as green when run alone with the change; its `trace`, per red the number of rounds and how many
   were red alone with the change, `red_with`, and without it, `red_without`) and its `parallel.xml` (the failure
   message of each red, from which this close's reader `gov.close.attribution.failure_type` takes the failure type).
3. **Computed:** each red's alone-runs, rebuilt as lists of outcomes from those counts, are fed into this close's own
   judgement `gov.close.attribution.judge`; the scoped close's rule then gives the verdict (any caused red: REFUSED;
   else CLOSED, every other red named with a repair ticket).
4. **Not compared: the failure types without the change.** close_build records the run without the change by its exit
   code only (`red_without` is a count), so no failure type exists there to compare. The script **assumes** a red
   without the change carries the same type as the run with it; on these records this close's same-type rule (S4)
   is therefore not exercised, only its counts. A batch where the type differs on the two heads would be caused by
   this close and could be unowned by close_build; these records cannot show it.

The script (the whole of it; it was first run from the engineer's sandbox scratch and not committed, so it is given
here to be re-run; `-I` keeps the records' folder out of the import path):

```python
"""S9: close_build.py's recorded verdict beside this close's judgement of the same records (W2-115, F-7).
Run: PYTHONPATH=<worktree>/src python3 -I s9.py <close-build log folder>"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from gov.close.attribution import failure_type, judge

RUNS = [("W2-71-20261030-161658", "clean"), ("W2-107-20261031-184805", "caused red"),
        ("W2-107-20261031-202743", "unowned red")]


def failing(xml: Path) -> dict:
    """{node id: failure type} of every failure or error in a JUnit file, read by this close's reader."""
    out = {}
    for case in ET.parse(xml).getroot().iter("testcase"):
        for bad in list(case.findall("failure")) + list(case.findall("error")):
            path = case.get("classname", "").replace(".", "/") + ".py"
            node = f"{case.get('file') or path}::{case.get('name')}"
            out[node] = failure_type(bad.get("message"), bad.text)
    return out


def verdict(folder: Path) -> tuple[str, str, list]:
    run = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    types = failing(folder / "parallel.xml")
    rows = []
    for test in run.get("flaky_candidates") or []:  # recorded green when run alone with the change
        rows.append((test,) + judge([None], []))
    for test, t in (run.get("trace") or {}).items():
        kind = next((v for k, v in types.items() if k.endswith(test.split("::", 1)[1]) and
                     k.split("::")[0].rsplit("/", 1)[-1] == test.split("::")[0].rsplit("/", 1)[-1]), "unknown")
        n = t["rounds"]
        # close_build records the run without the change by its exit code only: a red there is ASSUMED to carry
        # the same failure type as the run with the change (the types are not compared: they are not recorded)
        with_change = [kind] * t["red_with"] + [None] * (n - t["red_with"])
        without = [kind] * t["red_without"] + [None] * (n - t["red_without"])
        rows.append((test,) + judge(with_change, without))
    caused = any(r[1] for r in rows)
    return run["verdict"], "REFUSED" if caused else "CLOSED", rows


def main(log: str) -> int:
    equal_all = True
    print("| Batch | Kind | close_build.py verdict | This close's verdict | Equal |\n|---|---|---|---|---|")
    for name, kind in RUNS:
        recorded, ours, rows = verdict(Path(log) / name)
        theirs = "REFUSED" if recorded.startswith("REFUSED") else "CLOSED"
        equal_all &= theirs == ours
        print(f"| `{name}` | {kind} | {theirs} | {ours} | {'yes' if theirs == ours else 'NO'} |")
        for test, caused, ftype, reason in rows:
            print(f"<!-- {name}: {test}: caused={caused} type={ftype}: {reason} -->", file=sys.stderr)
    return 0 if equal_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

**Re-run at `ce6a2addf362`** (2026-11-12, fix round 1, eng-5): saved as `s9.py` in the sandbox's TMPDIR and run as
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-115/src python3 s9.py <records folder>`: it printed the table below
unchanged and exited 0 (equal on all three); the per-red lines it printed are the details below.

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
  caused, named in the record with a repair ticket; the W2-50 failure green alone, so CLOSED. Two limits, stated: (1) the
failure types without the change were not compared (method, item 4: close_build does not record them); (2) none of the
fifteen recorded runs had a parallel run with no failure at all, so the clean batch is the one whose only failure was
green alone. The table is this close's judgement applied to close_build's recorded runs, not a run of this close; a
run of `gov close` on these batches was not made (it needs the batches' clones and hours of tests outside the
sandbox).

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

## eng-3 (iteration 3): the last three reds

- **S6, a candidate that cannot be isolated** (`batch._entangled`): two candidates whose commits past the base overlap
  (one built on the other, or both on a common unmerged commit) cannot be isolated, because the build without one
  still holds its work through the other. The batch is refused with `CANDIDATE_NOT_ISOLATED` before anything runs,
  even where the run would be green (fail closed). It names the candidate whose work the other holds. Every refusal
  of the scoped batch (`isolate`, or `run` in a scoped project) also prints `<CODE>: <reason>` on stderr; the strict
  batch prints as before (F4). Unit test: `test_w2_115_batch.py::test_s6_a_candidate_built_on_another_cannot_be_isolated_and_the_code_is_printed`.
- **S4, three rounds for a load-sensitive red** (`attribution.load_sensitive`, `attribute`): a `latency` entry is
  matched in every form the serial phase takes: the file, the node id, a parametrised id, a folder (with or without
  `/`), a leading `./`, a tab before ` #`. The kind is the word after the route whatever follows it (`latency`,
  `latency (x): r`, `Latency`), or the first word where the route is left out. A load-sensitive red runs its 3
  rounds on the head without the change even where a full green nightly of that head would stand for one run
  (rounds on both sides). The planted project's exact cause was not seen (the tests are not read): the close's own
  end-to-end run in a unit test already gave 1 + 3 + 3. Unit tests: `test_w2_115_attribution.py::test_s4_a_latency_entry_is_matched_in_every_form_the_serial_phase_takes`
  (8 forms), `::test_s4_a_load_sensitive_red_runs_its_rounds_without_the_change_even_with_a_nightly`, and
  `test_w2_115_close.py::test_s4_a_latency_entry_red_gets_three_rounds_each_way_in_the_close` (2 forms).
- **S2, a governance file alone** (`select._bookkeeping`): the wider change always holds the green record's own file,
  committed after the head it names. Where a change holds governance files, no code, and only record places that are
  bookkeeping, those records select nothing. Bookkeeping means the ticket's own `.tickets/<id>.md`, its own
  `docs/close/<id>/` and `docs/checkpoints/<id>/`, and the green records the change is counted from. The reading is
  narrow: another ticket's file or record, and any other record place, still selects `record_reading`. Bookkeeping
  alone (no governance file) still selects `record_reading` (records alone), and code beside it is unchanged (own
  suite, `record_reading`, `every_close`). Unit test: `test_w2_115_select.py::test_s2_governance_alone_beside_the_tickets_bookkeeping_selects_nothing`.

## Fix round 1 (eng-5): review round 1's F-1, F-3 and F-7 (PK-3 (a))

- **F-1 (S4, F1): the head a red is judged against.** `select.head_without_change`: the green base the change is
  counted from (`green_base`) when it is an ancestor of `HEAD`, else the first parent of the ticket's oldest own
  commit, else none (DEC-988 item 3, DEC-989). `select.scoped`'s `base` is that head; `gov close` uses it (its
  `--base` still overrides). The selection (suites, options, changed paths) is unchanged. An untrailered commit between
  the green base and the first trailered one is now outside the head without the change, so its red is caused:
  `RED_CAUSED`, no record, no repair ticket. Unit tests: `test_w2_115_select.py::test_f1_*` (3: an ancestor; not an
  ancestor; no green base), `test_w2_115_close.py::test_f1_an_untrailered_slip_after_the_green_base_is_caused_and_never_closes`.
- **F-3 (S6, F3): a culprit's own new test.** `batch.isolate`: a red absent in the build without candidate X is run
  once alone on the base with X alone merged; red there with a real failure type (not a timeout, unknown or absent)
  blames X, and the rest land on the same run; not red there, it stays unexplained and the batch refuses
  `BATCH_UNEXPLAINED` as before. Every confirmation runs before anything lands. Unit tests:
  `test_w2_115_batch.py::test_f3_a_culprits_own_new_red_test_is_blamed_once_confirmed_alone`,
  `test_w2_115_batch.py::test_f3_an_absent_red_not_red_with_its_candidate_alone_refuses_and_nothing_lands`.
- **F-7 (S9):** the method above, stated exactly; the script inline and re-run at `ce6a2addf362`.
