# W2-193 acceptance tests: gov close's harness in an adopted repository (DAEO-7jln)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines and verify lines, the lead's
interface (the brief of 2026-11-17) and EXAMIN's exa-g6db close (F-028, F-024; `retro-P2-lifecycle.md` §4), never
from the implementation. The base is `2b365738c`.

## How the suite runs

- **Public interfaces only:** `gov close <ticket> --json [--base <rev>]` and `gov checkpoint` through W1-07's
  console-script stand-in (this worktree's `src/` on `PYTHONPATH`), with no model (W2-115's `quiet_env`: the
  embedding endpoint at a dead local address); the close record `docs/close/<ticket>/CL-<ticket>.md`; the ticket's
  status; the files in `.tickets/` (none is opened for a base red, S6); the refusal's envelope and stderr (W2-115's `refusal_text`).
- **Planted projects under pytest's `tmp_path`:** W2-115's `Smart` projects (`close: scoped`, W2-115's tickets and
  suites, its test map and path map), built by `w2_193_support.py` (shared with `tests/acceptance/W2-194/`), with what
  an adopted repository adds:
  - a **legacy suite** `governance/scripts/tests/` and its **kit copy** `governance/framework/kit/governance/scripts/tests/`:
    no `__init__.py`, the same module names (`test_g19_determinism.py`, ...), a `conftest.py` each with
    `build_tree`, and modules that do `from conftest import build_tree`; the ticket's own suite
    (`tests/acceptance/W2-aa/`) has a `conftest.py` of its own without it. The modules import the widget the
    ticket changes, so the scoped selection reaches them by its import rule (the test map's couplings may name only
    targets under `tests/`, its schema);
  - an **absent red**: a test in `tests/acceptance/W2-bb/whole/` whose parameter id is `whole` only when a target of
    the pytest run is its folder or a folder above it (`part` otherwise); run alone by the id the full run gave
    (`...[whole]`), pytest finds nothing (exit 4), with the change and at the base;
  - `close_workers: 2` (the parallel run uses xdist, as EXAMIN's did; a collection error is then a red, not an
    incomplete run).
- **Telling tests:** each planted test appends one JSON line per run (and, where planted so, per import) to a file
  outside the project: the widget's text it saw (`CHANGED` on the change's side), whether it passed, its process id
  and its pytest run's (the xdist controller's from a worker). "Ran in different processes" is read from the run ids.
- One close per case; deterministic, no network, no model. About a minute for this folder under `-n 6`.

## Interface (as used; the lead's naming where the KPI lines leave it open)

- Refusal codes `RED_CAUSED`, `BASELINE_MISSING`. A refused close need not write a record; where one is written, a
  caused red is `caused: true`.
- Record keys: `base` (full commit id), `base_from` (`given` | `green_record` | `ticket`), `base_run`
  (`{ran, commit, passed, failed, errors, skipped, complete}` or null when not run); each `reds` entry
  `{test, failure_type, caused, reason, repair_ticket}`.
- The default base: `--base` given > the newest green record on HEAD's line > the first parent of the ticket's
  oldest own (trailered, non-merge) commit.

Readings this suite takes (named to the lead):

1. A collection error's `reds` entry is found by its module file (`test` is the file, or a node of it); a test's
   entry by its own node id.
2. "The colliding suites ran in different processes" is asserted only for pairs the lead's rule makes collide: a
   folder whose modules import `conftest` by name against every other selected folder with a `conftest.py`, and two
   folders sharing a test module's name. Whether two folders that only both hold a `conftest.py` share a process is
   left open.
3. The base run "collected zero tests": planted as a root `conftest.py` at the base that deselects every collected
   test (`items.clear()`); the ticket's change removes it (a coupling places `conftest.py` on the ticket's suite).
   The refusal names the base by a prefix of 7 digits or more (or its full id).
4. "No base run needed" is `base_run: null` or `base_run.ran: false`.

## KPI map

| KPI | Test | Red on the base |
|---|---|---|
| success-1 (S1: colliding suites each in its own process; no collection error or import collision; every test collected and run) | `test_w2_193_suites.py::test_the_legacy_suite_and_its_kit_copy_run_in_their_own_processes_and_every_test_runs`, `test_w2_193_suites.py::test_each_form_of_collision_alone_runs_its_suites_in_separate_processes` | the selection runs in one pytest process: the modules import the ticket suite's `conftest` (or collide by name), each a collection error with the node id `<file>::<dotted module>`, absent alone, so the close refuses `RED_CAUSED` ("the close did not pass") and no planted test runs |
| success-2 (S2: a collection error re-run as its module file, a test as its own node id; nothing that exists judged absent) | `test_w2_193_alone.py::test_a_collection_error_and_a_nested_test_are_each_re_run_by_an_id_pytest_resolves` | the import-failing module's alone runs use `<file>::<dotted module>` (pytest: "found no collectors", exit 4): absent both ways, the change's: `RED_CAUSED` ("the close did not pass"); the suites also collide (S1) |
| success-3 (S3: no `--base`, no green record: judged at the first parent of the ticket's oldest own commit; `base` and `base_from` recorded; a red red there is not the change's) | `test_w2_193_base.py::test_with_no_green_record_a_red_red_at_the_parent_of_the_oldest_own_commit_is_not_the_change_s`, `test_w2_193_base.py::test_with_no_green_record_a_red_green_at_the_parent_of_the_oldest_own_commit_refuses`, `test_w2_193_base.py::test_the_record_says_where_the_base_came_from` | DEC-1150 (2): with no green record every red is the change's, so the base red refuses `RED_CAUSED` ("the close did not pass") and the caused red never runs off the change ("was not judged against the parent ..., where it passes: []"); the record has no `base_from` ("base_from is None") |
| success-4 (S4: an unjudgeable red judged by the base run; red there a base red, green there the change's; zero collected or incomplete: `BASELINE_MISSING` naming the base and the reds, never `RED_CAUSED`; `base_run` recorded) | `test_w2_193_base_run.py::test_an_absent_red_red_at_the_base_run_is_a_base_red`, `test_w2_193_base_run.py::test_an_absent_red_green_at_the_base_run_is_the_change_s`, `test_w2_193_base_run.py::test_a_base_run_that_collects_nothing_refuses_baseline_missing_never_red_caused`, `test_w2_193_base.py::test_with_no_green_record_a_red_red_at_the_parent_of_the_oldest_own_commit_is_not_the_change_s` | no base run: an absent red is always the change's, so the base red refuses `RED_CAUSED` ("the close did not pass"), the green one never runs at the base ("did not run at the base ...: []"), and the empty base gives `RED_CAUSED`, not `BASELINE_MISSING` ("the refusal does not name BASELINE_MISSING") |
| success-5 (S5: the exa-g6db case closes, exit 0, every base red `caused: false`) | `test_w2_193_examin.py::test_the_exa_g6db_case_closes_with_every_base_red_not_caused` | the colliding suites' collection errors are absent alone and every red is the change's with no green record: `RED_CAUSED` (8 reds), exit 3 ("gov close did not exit 0") |
| success-6 (S6: a base red no `accepted_reds` entry covers opens no repair ticket; the close proceeds, `.tickets/` holds no new file, the record lists each base red with `caused: false`, a reason saying it was red at the base and `repair_ticket: null`; a red the change brings still refuses `RED_CAUSED`) | `test_w2_193_no_repair.py::test_the_exa_g6db_base_reds_open_no_repair_ticket_and_the_record_lists_each`, `test_w2_193_no_repair.py::test_a_base_red_judged_from_either_base_route_opens_no_repair_ticket`, `test_w2_193_no_repair.py::test_a_red_the_change_brings_still_refuses_beside_a_base_red_and_no_ticket_names_the_base_red`, `test_w2_193_base.py::test_with_no_green_record_a_red_red_at_the_parent_of_the_oldest_own_commit_is_not_the_change_s` (rewritten); W2-115's and W2-194's rewritten cases are listed below | today's close opens a repair ticket (a new file in `.tickets/`) for each base red and the record's `repair_ticket` names it (\"the close created files in .tickets/\", \"the base red names a repair ticket\"); the reason does not say it was red at the base. The caused-red case is green by design (a guard: `RED_CAUSED` stays, no repair names either red) |
| success-7 (S7: a FULL ticket with no probe record under `docs/probes/<ticket>/` closes, scoped and batch, with `review` READY and `record` null, no `VERDICT_MALFORMED`; where a review happened a blocking verdict block still refuses `FINDING_BLOCKS`) | `test_w2_193_no_review_gate.py::test_a_full_ticket_with_no_probe_record_closes_with_review_ready_and_no_record`, `test_w2_193_no_review_gate.py::test_a_batch_of_full_tickets_with_no_probe_record_lands_with_review_ready_and_no_record`, `test_w2_193_no_review_gate.py::test_a_verdict_block_that_fails_a_kpi_line_still_refuses_finding_blocks`, `test_w2_193_no_review_gate.py::test_a_batch_whose_full_candidate_has_a_blocking_verdict_block_is_refused_and_nothing_lands` | today's scoped close and batch refuse a FULL ticket with no probe record: `VERDICT_MALFORMED` (\"no probe record under docs/probes/<ticket>/ holds a fenced verdict block\"), the ticket stays open and nothing lands. The two blocking-block cases are green by design (guards: READY stays computed by code); the malformed and not-the-reviewer blocks stay in `tests/acceptance/W2-115/test_w2_115_verdict.py` |
| failure-1 (F1: a red the change brings excused in a new route; the existing close cases changed) | `test_w2_193_guards.py::test_a_red_in_a_colliding_suite_green_at_the_base_refuses`, `test_w2_193_guards.py::test_a_module_that_fails_to_import_only_with_the_change_refuses_with_its_failure_not_absent`, `test_w2_193_base.py::test_with_no_green_record_a_red_green_at_the_parent_of_the_oldest_own_commit_refuses`, `test_w2_193_base_run.py::test_an_absent_red_green_at_the_base_run_is_the_change_s`; the existing close suites (`tests/unit/close`, `tests/acceptance/W2-115/`, W2-66, W2-68, W2-150 and the rest) with W2-115's three cases rewritten for S3 (below) | each refuses `RED_CAUSED` today too, but for the wrong reason: the colliding suite's test never runs (a collection error), so it is not judged at a base where it passes ("... was not judged against the base, where it passes: []"); the module's red is judged `absent` ("the refusal does not name the module's failure"); S3's and S4's caused reds never run off the change |

## Cases of another folder rewritten for S6 (EMERGENCY-2 4.2: no repair ticket for a base red)

Each with a `Rewrite-Reason` line in its docstring: `tests/acceptance/W2-115/test_w2_115_reds.py::test_an_unowned_red_is_named_in_the_record_and_opens_no_repair_ticket` (was `..._and_opened_as_a_repair_ticket_for_the_orchestrator`), the helper `_assert_judged_at_the_ticket_s_parent` and the two S3 cases that use it (also below), `test_w2_193_base.py::test_with_no_green_record_a_red_red_at_the_parent_of_the_oldest_own_commit_is_not_the_change_s` (this folder), and `tests/acceptance/W2-194/test_w2_194_accepted.py::test_an_entry_whose_decision_is_not_accepted_is_named_in_the_record_and_covers_nothing`: each now asserts `repair_ticket: null`, a reason that says it was red at the base and no new file in `.tickets/`, where it asserted a repair ticket. W2-115's README (S5, S11 and the Interface) is updated to match. S7 revises no case: no existing case asserted the missing-review refusal of a FULL ticket through the public interface (W2-115's S11 cases all plant a probe record); the unit cases that do are listed for the engineer in the lead's return.

## Cases of another folder rewritten for S3

S3 supersedes DEC-1150 (2) ("no green base on HEAD's line: every red is the change's"). In
`tests/acceptance/W2-115/test_w2_115_reds.py`, each with `Rewrite-Reason: W2-193 S3 (EMERGENCY-2 6.1, close against
the base by default; supersedes DEC-1150 (2))` in its docstring, and W2-115's README readings 3 and 7 and its S4 and
F1 rows updated:

- `test_with_the_green_base_not_an_ancestor_a_red_the_parent_also_has_is_not_the_change_s` (was
  `..._is_still_the_change_s`): the close passes, `base` the ticket's parent, `base_from: ticket`, the red not caused
  with no repair ticket (S6), run on that parent.
- `test_with_the_green_base_not_an_ancestor_a_red_the_parent_does_not_have_is_the_change_s`: still `RED_CAUSED`, now
  also run on the ticket's parent, where it passes.
- `test_with_no_green_record_a_red_an_untrailered_first_commit_caused_is_judged_at_the_ticket_s_parent` (was
  `..._caused_is_the_change_s`): the untrailered slip is the parent of the oldest own commit and the red is red
  there, so it is not the change's: the close passes and the record lists it as a base red, no repair ticket (S6).

All three are red at `2b365738c` for S3's reason (W2-115's README, S4 row).
