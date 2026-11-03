# W2-97 acceptance tests: the local merge queue

Ticket `DAEO-wq2b` (W2-97), profile STANDARD. Written by the independent test designer (MR-3, DEC-963) from the
ticket's KPI lines and the lead's specification (the tool's public interface), with DEC-959 item 1, DEC-968,
DEC-979 item 3, DEC-962, DEC-848, DEC-953 item 4 and ROLES-RESEARCH-1 §4 (c) and §5.3 item 5. The implementation was
not read. Proportion (DEC-951 item 5, STANDARD): every KPI line's success and failure, and the key edge cases the
specification names (a flaky red that passes alone, a red that is not the batch's, a fail-closed batch). 18 test
functions, 19 cases, a few seconds each.

**Run 2 (DEC-985, DEC-983; a fresh test designer, after the implementation began, DEC-491):** the enqueue helper
passes `--repo` (P-W2-97-ENQ-1 (b), `Rewrite-Reason: P-W2-97-ENQ-1`); the KPI lines below take DEC-983's wording
(DEC-866) and one case is added for KPI 3's new text, `test_a_full_selection_is_never_run`
(`Rewrite-Reason: DEC-983`). No case asserted the old rules (a shared test lock, or the full suite on a change to the
core): the lock case is the queue's own one-writer lock, which stays, so no assertion was revised for them.

## How the suite runs the tool (DEC-732)

- The tool under test is `governance/project/orchestration/tools/merge_queue.py` **of the repository the tests sit
  in** (`w2_97_support.TOOL`, found from this folder, never a hard-coded worktree), run as a subprocess with
  `sys.executable`. From the ticket's worktree, that worktree's copy is what runs.
- Run it with a **writable** `TMPDIR` (where `TMPDIR` cannot be written, pytest falls back to the current folder
  and leaves `pytest-of-<user>/` in the worktree):

      PYTHONPATH=<worktree>/src TMPDIR=<a writable folder> python3 -m pytest tests/acceptance/W2-97 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

- The queue and its stubs get a clean environment: `PYTEST_ADDOPTS`, `PYTEST_PLUGINS`, `PYTEST_CURRENT_TEST`,
  `PYTEST_XDIST_*`, `PYTHONPATH` and every `GIT_*` variable are taken out; `HOME` and `TMPDIR` are folders of the
  test's `tmp_path` (so no global git identity and nothing of `~/gov-os-runs/`); `PYTHONUSERBASE` keeps pytest
  importable from the user site.

## What each test builds (stand-ins only)

- **A planted repository** under `tmp_path/repo`, built from scratch: `pytest.ini`, `app/a.txt`, `app/b.txt`,
  `app/notes.txt`, `tests/test_a.py` and `tests/test_b.py` (green while their `app/*.txt` holds `ok`), plus a case's
  own files. One base commit H0 on `main` and `w2/integrate`; **`w2/integrate` is checked out in the planted
  repository's worktree** (as in production), and every test checks that `main` never moves. The planted repository
  has its own git identity.
- **H1:** in most cases a code commit (`app/notes.txt`) lands on `w2/integrate` after the tickets are cut, so no
  merged result equals a lead's tested tree and the run is not skipped (rule 2). The skip case uses a governance
  commit instead.
- **Ticket branches** `w2/W2-9xx`, cut from H0 without a checkout, each commit carrying `Task: DAEO-t9xx` (one also
  carries another ticket's commit, `Task: DAEO-other`).
- **Stubs** in `tmp_path/stubs`, each with a JSON file beside it:
  - the **test command** (`--test-cmd "<python> stub_test.py"`) logs every call (its arguments, its targets, its
    folder, the commit and tree checked out there, whether it is a single case "alone"), then runs
    `python3 -m pytest -q -p no:cacheprovider` with the queue's arguments. Options: `incomplete` (exit 2, no JUnit
    file), `block` (waits for a release file: the lock case), `move` (on its first batch run, commits onto
    `w2/integrate` in the planted repository: the head moves under test);
  - the **selection** (`--select-cmd "<python> stub_select.py"`) prints `select_tests.py`'s JSON object, with
    targets per ticket (default `tests`), `core_changed` and `unplaced`; `full` answers scope `full` (with its
    targets, exit 0: the answer a selection gives for the full suite); `refuse` makes it exit 2 with scope
    `refused`;
  - the **prepare command** is `true`, or `false` for the case where it fails.
- `--work` and `--queue` are always under `tmp_path`. No test touches this repository's branches, its stores,
  `~/gov-os-runs/` or the network.

## What the tests observe (public interface only)

The exit code; `w2/integrate`'s head and its parents (a merge commit whose parents are the old head and the approved
commit); the merge commit's subject and trailers; the checked-out worktree after a fast-forward; the files in
`requested/`, `approved/`, `ejected/`, `landed/` and `records/` and their stated fields; the stubs' call logs (how
many batch runs, on which commit, on which targets; whether a case was re-run without the batch). **"The commit
tested is the commit landed"** is checked directly: the stub logs the commit checked out when it ran, and it must be
the new head.

## KPI lines and their tests

| KPI line | Tests |
|---|---|
| S1. Entry only with approval; `--no-ff` merge onto the current head in a clean clone; the scoped set run once on that merged result in a heavy-job slot (DEC-979), or freely until the slots run (DEC-962, DEC-983, DEC-982); on green, `--ff-only` to that same merge commit (the commit tested is the commit landed). **The heavy-job slot has no acceptance case** (see "Gaps") | `test_w2_97_entry.py`: `test_only_an_approved_ticket_enters`, `test_green_advances_to_the_very_merge_commit_tested`, `test_a_second_run_while_one_holds_the_lock_exits_4` (one writer) |
| S2. On red the branch does not move; ejected with the failing tests' names and the log path; a red that passes alone is a flaky candidate, named, deciding nothing | `test_w2_97_red.py`: `test_red_ejects_the_ticket_and_the_head_stays`, `test_a_red_that_passes_alone_is_a_flaky_candidate`, `test_a_red_not_the_batch_s_does_not_stop_the_advance` (DEC-968), `test_a_failing_test_the_ticket_added_is_the_ticket_s` |
| S3. The scoped set once per batch on the merged result; skipped when the merged code is the lead's (governance left out), with the reason recorded; the full suite never runs here, only in the nightly (DEC-968, DEC-983, DEC-982) | `test_w2_97_once.py`: `test_code_identical_to_the_lead_s_is_skipped_with_its_reason`, `test_a_step_that_cannot_be_done_moves_nothing_and_ejects_nothing[selection-refused, run-did-not-complete, prepare-failed]`; the full suite never: `test_a_full_selection_is_never_run` (a selection answering scope `full` is not run: exit 4, no test call, nothing moved, ejected or landed, the entry kept); one run on a code difference: `test_green_advances_to_the_very_merge_commit_tested`; the run is the selection's union and no more: `test_a_batch_gives_one_merged_result_and_one_run_on_the_union` |
| S4. One head, one merged result, one run; a red batch searched by ticket, the good ones advance, the culprit ejected | `test_w2_97_batch.py`: `test_a_batch_gives_one_merged_result_and_one_run_on_the_union`, `test_a_red_batch_ejects_only_its_culprit_and_lands_the_rest_tested`, `test_a_red_no_single_ticket_explains_ejects_the_whole_batch`, `test_a_ticket_bringing_another_ticket_s_commits_fails_the_batch_closed`, `test_a_conflicting_ticket_is_ejected_and_the_rest_go_on` |
| S5. Each advance writes the record the close cites (head, tickets, selection, counts, time) | `test_w2_97_record.py`: `test_each_advance_writes_the_record_the_close_cites`; the record's `flaky`, `unowned`, `ejected` and `skipped` fields in the red, once and batch cases |
| S6. A head that moves under test: re-merged and re-tested, never advanced onto a head it was not tested on | `test_w2_97_moved.py`: `test_a_head_moved_under_test_is_re_merged_and_re_tested` |
| F1. Advanced to a commit not the one tested, or after a red | `test_green_advances_to_the_very_merge_commit_tested`, `test_a_head_moved_under_test_is_re_merged_and_re_tested` (the logged tested commit is the head); `test_red_ejects_the_ticket_and_the_head_stays`, `test_a_failing_test_the_ticket_added_is_the_ticket_s`, the two fail-closed batch cases (the head unmoved after a red); `test_a_red_batch_ejects_only_its_culprit_and_lands_the_rest_tested` and `test_a_conflicting_ticket_is_ejected_and_the_rest_go_on` (the rest land only on a run of their own) |
| F2. A second run on code identical to the lead's, or a skip without its recorded reason | `test_code_identical_to_the_lead_s_is_skipped_with_its_reason` (no test call; `skipped` names the lead's commit and the governance paths); `test_green_advances_to_the_very_merge_commit_tested` and `test_a_batch_gives_one_merged_result_and_one_run_on_the_union` (exactly one batch run on one merged result) |
| F3. A red batch that advances its causing ticket | `test_a_red_batch_ejects_only_its_culprit_and_lands_the_rest_tested` (the culprit's commit is not in the new head), `test_a_red_no_single_ticket_explains_ejects_the_whole_batch`, `test_a_ticket_bringing_another_ticket_s_commits_fails_the_batch_closed` |
| F4. A close that re-runs tests the queue already ran on the same code | **Not testable here** (see "Gaps"): what the queue gives a close is checked: `test_each_advance_writes_the_record_the_close_cites` (a record keyed by the new head, with its counts, that every landed file points at) |

## The red reason of each test, today

On the ticket's base the tool does not exist, so **every one of the 18 cases fails with the same reason**, at its
first call of the tool (after its planted repository is built):

    AssertionError: the merge queue does not exist on this tree: <worktree>/governance/project/orchestration/tools/merge_queue.py (W2-97 not built)

Seen on 2026-10-31 in the tests worktree: `18 failed in 1.15s`, all 18 with that line.

**Run 2 (2026-11-01, on the engineer's implementation):** `test_a_full_selection_is_never_run` is red (the tool as
it stands runs a `full` selection); the other 18 cases are green.

## Gaps and points the specification leaves open (tested only as far as it fixes them)

- **KPI 1's heavy-job slot (DEC-983, DEC-979 D1): no acceptance case covers it.** Only the production default run
  goes through the slots (`verify_lock.sh`); a `--test-cmd` stand-in replaces the whole run command, slot included,
  and is run as given, so through the stand-ins the slot is not observable, and a default run would reach this
  machine's own slots and suites. What remains of the old rule is tested: there is no shared test lock, and the
  queue's own one-writer lock (`test_a_second_run_while_one_holds_the_lock_exits_4`) stays.
- **F4 (a close that re-runs the queue's tests):** the close (`close_build.py`) is the CTO's untracked tool and not
  in this ticket's `allowed_paths`; nothing in the queue's interface can show whether a close cites the record. The
  suite tests what a close needs to cite: the record keyed by the new head, its counts, and the landed files that
  point at it. Whether `close_build.py` reads it belongs to the CTO's tool lane (DEC-979 D3).
- **Approval order with equal `approved_at`:** the batch is merged "in the order approved"; two approvals in the same
  second have no stated tie-break. The batch case approves W2-901 before W2-902, so approval order and name order
  agree.
- **The record's inner shapes:** `tickets` is read as a list or a map of rows; `skipped` and `selection` are checked
  by what they name (the lead's commit and `governance/`; the targets, `core_changed`, `unplaced`), not by their keys;
  a landed file's `record` is accepted as absolute or relative to the queue folder.
- **Where the queue's lock lives:** not fixed. The lock case runs both runs with the same `--repo`, `--queue` and
  `--work`. A lock held machine-wide (one fixed path under `/tmp`) would make cases running side by side (for example
  under `-n auto`) refuse each other with exit 4; a lock kept with the queue folder or the repository does not.
- **Failing test ids:** their format is not fixed; a failing id must contain the test function's name.
- **The trace without the batch:** whether the queue checks out the old head or reverts the merges is open; the
  suite checks that a case was run on a tree equal to the old head's.
- **Not tested (the specification names them; left out in proportion):** a head that keeps moving on every attempt
  (bounded attempts, then exit 4: the bound is not fixed); a ticket whose test the ticket edited (DEC-979's weak
  proof, `close_build.py`'s "absent" path); the test map's `record_only` places in the skip rule (the planted
  repository has no test map); the ref move when the branch is not checked out; the default (production) commands.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `lifted` (`tests/optin-lifted*.txt`), run report-only with `--optin=lifted`.

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: A ticket enters the queue only with its Senior Engineer's approval (until the three layers start, the CTO's); the queue makes the --n... | `test_w2_97_entry.py::test_only_an_approved_ticket_enters`, `test_w2_97_entry.py::test_green_advances_to_the_very_merge_commit_tested`, `test_w2_97_entry.py::test_a_second_run_while_one_holds_the_lock_exits_4` | README |
| S2: On red, w2/integrate does not move: the ticket is ejected back to its Senior Engineer (or the CTO) with the failing tests' names and ... | `test_w2_97_red.py::test_red_ejects_the_ticket_and_the_head_stays`, `test_w2_97_red.py::test_a_red_that_passes_alone_is_a_flaky_candidate`, `test_w2_97_red.py::test_a_red_not_the_batch_s_does_not_stop_the_advance` | README |
| S3: Tests run no more than this: the queue runs the scoped set once per batch on the merged result, and skips the run when the merged cod... | `test_w2_97_once.py::test_code_identical_to_the_lead_s_is_skipped_with_its_reason`, `test_w2_97_once.py::test_a_step_that_cannot_be_done_moves_nothing_and_ejects_nothing`, `test_w2_97_once.py::test_a_full_selection_is_never_run` | README |
| S4: A batch of queued tickets on one head gives one merged result and one run; a red batch is bisected by ticket, the good ones advance a... | `test_w2_97_batch.py::test_a_batch_gives_one_merged_result_and_one_run_on_the_union`, `test_w2_97_batch.py::test_a_red_batch_ejects_only_its_culprit_and_lands_the_rest_tested`, `test_w2_97_batch.py::test_a_red_no_single_ticket_explains_ejects_the_whole_batch` | README |
| S5: Each advance writes the record the close cites (the head, the tickets, the selection, the counts, the time); close_build cites it ins... | `test_w2_97_record.py::test_each_advance_writes_the_record_the_close_cites`, `test_w2_97_record.py::test_each_advance_writes_the_record_the_close_cites` | README |
| S6: When the head moves while a candidate is under test, the candidate is re-merged and re-tested, never advanced onto a head it was not ... | `test_w2_97_moved.py::test_a_head_moved_under_test_is_re_merged_and_re_tested`, `test_w2_97_moved.py::test_a_head_moved_under_test_is_re_merged_and_re_tested` | README |
| F1: w2/integrate advanced to a commit that was not the one tested, or after a red. | `test_w2_97_entry.py::test_green_advances_to_the_very_merge_commit_tested`, `test_w2_97_moved.py::test_a_head_moved_under_test_is_re_merged_and_re_tested`, `test_w2_97_red.py::test_red_ejects_the_ticket_and_the_head_stays` | README |
| F2: A second run on code identical to the lead's tested code, or a skip without its recorded reason. | `test_w2_97_once.py::test_code_identical_to_the_lead_s_is_skipped_with_its_reason`, `test_w2_97_entry.py::test_green_advances_to_the_very_merge_commit_tested`, `test_w2_97_batch.py::test_a_batch_gives_one_merged_result_and_one_run_on_the_union` | README |
| F3: A red batch that advances its causing ticket. | `test_w2_97_batch.py::test_a_red_batch_ejects_only_its_culprit_and_lands_the_rest_tested`, `test_w2_97_batch.py::test_a_red_no_single_ticket_explains_ejects_the_whole_batch`, `test_w2_97_batch.py::test_a_ticket_bringing_another_ticket_s_commits_fails_the_batch_closed` | README |
| F4: A close that re-runs tests the queue already ran on the same code. | `test_w2_97_record.py::test_each_advance_writes_the_record_the_close_cites` | README |
