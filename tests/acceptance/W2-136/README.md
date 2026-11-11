# W2-136 acceptance tests: gov plan, the launch batches, and gov launch's check against them

Ticket DAEO-p3ln (W2-136), profile STANDARD (DEC-1088; `governance/project/orchestration/packages/LIFT-1/DEPENDENCY-MAP-1.md`).
Written by the independent test designer (MR-3) from the ticket's KPI lines S1 to S10, before any implementation,
reading only the integrated code (`w2/integrate` at `24e0e8b0f55d`, with the ticket's claim on top: this branch's
`c10bc7b94953`, DEC-963). S11 (under 5 s on this repository) is the
CTO's measure, not a test here.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-136 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

About 6 s. No model, no network, no GPU. The tests use the tree `PYTHONPATH` names (`gov.__file__`'s `src`).

- **A planted ticket store per case** (`w2_136_support.build`): a temporary git repository with `.tickets/<id>.md`
  files (the front matter real tickets carry, plus W2-128's `reads:`, `needs:`, `waits_on:` and DEC-1088's
  `plan_override:`) and a few tracked files, committed with a fixed date. Never this repository's `.tickets/`.
- **`gov plan` runs as a child process**: `python3 -B -m gov.cli.main plan <args> --root <store>`, from an empty
  working folder, with `PYTHONPATH` the tree's `src` and no `GOV_*` or `GIT_*` variable of the session running the
  tests. One case of S4 runs it in process, to reverse the listing of `.tickets/`.
- **S9's launcher cases** replace `subprocess.Popen`, `HOME` (a CLI file planted there), the temp folder and the
  repository-settings check, as the launcher's own unit tests do (`tests/unit/launch/test_w1_28.py`), and replace the
  plan check with a stub. No session is ever started.
- **The guard's matcher** (S3) is `gov.guard.decide._match_pattern` (decide.py:96-102: `*` within a folder, `**`
  across). S3's premise checks every planted pair against it.

## The interface the tests assume

What the KPI lines leave open is fixed here, so the engineer builds to it (a point the CTO settles otherwise changes
the tests by a designer's revision).

**The command.** `gov plan --open [--json] [--ready <file>] [--root <path>]`, a command module
`src/gov/plan/command.py` (the CLI convention, `src/gov/cli/main.py`). The CLI reserves exits 0, 1 and 2 and prints
a dict result as JSON, so S1's text lines and its "exit 1, a plan with findings" need the module to print its own
output and return its code (`CHILD_EXIT_CODE = True`); the tests read only stdout and the exit code.

**The text.**
- First line: `gov plan: N tickets, B batches, W waits (CODE, CODE, ...)`: N the open and in-progress tickets, B the
  batches, W the wait lines, the parenthesis the codes in the plan.
- Then `batch k: T1, T3, T5` for k = 1..B, the names comma-separated.
- For each wait, one line `T2 waits for T1 (<CODE> <path or id>)` (indent allowed); a ticket waiting for two gives two
  lines. `<CODE>` is `NEEDS_WHAT_WRITES` (then the path needed), `WRITES_OVERLAP`, `DEPENDS_ON` or `WAITS_ON` (then the
  ticket's name).
- Every other code on a line of its own naming the code and the ticket: `READS_WIDE` (with the ticket it would have
  waited for), `NEEDS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT` (with the unknown id), `OVERRIDE` (with the
  decision id), `CYCLE_TIEBREAK`.
- A ticket is named by its id or its WBS id (either); one without a `wbs_id` by its id.

**`--json`.** The shared envelope `{"ok": true, "command": "plan", "result": {...}, "session": ...}` on stdout, the
same exit code. `result["batches"]`: a list, batch 1 first, of lists of ticket names (or of `{"tickets": [...]}`).
`result["waits"]`: a list of `{"ticket", "waits_for", "code", "on"}`. Every other code: a dict anywhere in `result`
with `"code"`, `"ticket"` (the ticket flagged) and the other names among its values. `result["tickets"]` may be N or
the list.

**Exit codes.** 0 a plan; 1 a plan with findings (`NEEDS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT`), the plan
still printed; 2 cannot run: a root with no `.tickets/` folder.

**The order.**
- Unfinished: status `open` or `in_progress`; `closed` is finished, waits on it are met, and it is not planned.
- Each ticket goes in the earliest batch after every ticket it waits for.
- `needs:` absent is undeclared (planned on the ticket's own writes, `NEEDS_UNDECLARED`); `needs: []` is a declared
  none.
- `waits_on:` entries are ticket ids (a YAML comment as the reason); one naming no ticket is `UNKNOWN_WAIT`.
- `plan_override: DEC-<n>`: a scalar on the ticket that waits or overlaps.
- The tie key: `priority` ascending (0 first, tk's highest), then WBS order, then the id; two tickets without a
  `wbs_id` tie on WBS.

**`--ready <file>`.** Writes only that file: comment lines `# batch k` (k = 1..B) each followed by its tickets in the
dispatcher's form, `<W2> <ticket id> <brief>.md <W2>-A5-<run>.json` (`dispatcher.py`: `read_list` skips blank and
`#` lines; `why_not` takes 4 or 5 fields, the fifth `first=<phase>`, and a log matching `LOGNAME`). The run name is
the engineer's. Nothing else is written, with or without `--ready`: not in the store, not in the working folder.

**The launch check.** `src/gov/launch/plan_check.py` exposes `check_lead(root, ticket_id, *, ready=<path>)`; its
answer reads `admitted` (bool), `reason` (str) and `override` (the decision id or None), as keys or attributes. A
refusal's reason names the ticket waited for and, for a `needs:` wait, the path; "not in a batch" names the ticket.
The waits are read from the current tickets at the call, not from the list. `ready` defaults to the dispatcher's
list (`.gov-runtime/scratch/orchestrator/dispatch/ready.txt` of the main worktree), not tested. **The launcher**, for
the role `orchestrator` with a ticket, calls `plan_check.check_lead(root, ticket_id)` at its argument checks (looked
up on the module at the call), refuses with `LAUNCH_REFUSED` carrying the reason and starts nothing; on an override
it writes one stderr line holding `OVERRIDE` and the decision id (the launch log) and starts; a worker launch never
calls it.

## KPI lines, tests, and the outcome on `w2/integrate` `24e0e8b0f55d`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **76 tests, 66 failed, 10 passed**. Every red fails on the missing
command (`invalid choice: 'plan'`), the missing module (`No module named 'gov.launch.plan_check'`) or, for three
launcher cases, `'orchestrator' is not a worker role` (D-1); none on a premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_136_plan_output.py::test_s1_the_text_plan_gives_the_first_line_the_batches_and_the_named_waits` | red | no `gov plan`; asks N 4 (the closed ticket left out), B 2, W 2, the batches, a needs wait naming its path and a depends_on wait naming its ticket |
| S1 | `test_w2_136_plan_output.py::test_s1_json_gives_the_same_plan_in_the_shared_envelope` | red | no `gov plan`; the envelope, the same batches and waits as the text |
| S1 | `test_w2_136_plan_output.py::test_s1_a_plan_with_findings_exits_1_and_still_gives_the_plan[text]` | red | no `gov plan`; a ticket without `needs:` makes exit 1, the plan still printed |
| S1 | `test_w2_136_plan_output.py::test_s1_a_plan_with_findings_exits_1_and_still_gives_the_plan[json]` | red | as above, `--json` |
| S1 | `test_w2_136_plan_output.py::test_s1_no_ticket_store_cannot_run_and_exits_2[text]` | red | no `gov plan`: the premise (a store plans, exit 0) fails, so argparse's own 2 is never taken for gov plan's |
| S1 | `test_w2_136_plan_output.py::test_s1_no_ticket_store_cannot_run_and_exits_2[json]` | red | as above, `--json` |
| S2 | `test_w2_136_order.py::test_s2_needs_on_a_path_an_unfinished_ticket_writes_waits_for_it_naming_the_path` | red | no `gov plan`; needs on a path nobody writes, or only a closed ticket wrote, orders nothing |
| S2 | `test_w2_136_order.py::test_s2_tickets_whose_writes_overlap_run_in_series` | red | no `gov plan`; WRITES_OVERLAP, the higher priority first |
| S2 | `test_w2_136_order.py::test_s2_depends_on_an_unfinished_ticket_waits_and_on_a_closed_one_does_not` | red | no `gov plan`; DEPENDS_ON |
| S2 | `test_w2_136_order.py::test_s2_an_unfinished_waits_on_waits_and_a_closed_one_does_not` | red | no `gov plan`; WAITS_ON |
| S2 | `test_w2_136_order.py::test_s2_waits_compose_into_a_chain_of_batches` | red | no `gov plan`; three batches from a depends_on and a waits_on |
| S2 | `test_w2_136_order.py::test_s2_a_wide_read_orders_nothing_and_warns_naming_the_wait_it_would_cause` | red | no `gov plan`; `reads: src/**` beside a writer: one batch, no wait, READS_WIDE naming both (text and JSON) |
| S2 | `test_w2_136_order.py::test_s2_the_rest_share_one_batch` | red | no `gov plan`; four tickets, waits only on what is closed or unwritten: one batch, W 0, exit 0 |
| S3 | `test_w2_136_overlap.py::test_s3_premise_the_cases_hold_under_the_guard_s_own_matcher` | green (premise) | each overlapping pair has a path `_match_pattern` matches under both; no candidate matches both of an apart pair |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[star-within-a-folder-on-a-tracked-file]` | red | no `gov plan`; `src/p/*.py` and the tracked `src/p/mod.py` |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[double-star-across-folders-on-a-tracked-file]` | red | no `gov plan`; `src/p/**` and the tracked `src/p/deep/x/y.py` |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[double-star-and-star-in-a-folder-not-yet-created]` | red | no `gov plan`; `src/new/**` and `src/new/*.py`, no file there |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[a-folder-and-a-file-not-yet-created]` | red | no `gov plan`; `docs/**` and a file not created |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[the-same-literal-path-not-yet-created]` | red | no `gov plan`; one literal path, not created |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[a-name-prefix-and-a-file-not-yet-created]` | red | no `gov plan`; `tests/unit/launch/test_w2_136*` and a file it names |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[an-inner-double-star-and-a-file-in-folders-not-yet-created]` | red | no `gov plan`; `src/**/test_*.py` and `src/q/r/test_a.py` |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_the_guard_lets_two_writers_both_touch_run_in_series[a-wide-folder-and-a-star-in-a-folder-not-yet-created]` | red | no `gov plan`; `src/**` and `src/r/*.py` |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_no_path_matches_both_share_a_batch[a-star-stays-in-its-folder]` | red | no `gov plan`; `src/p/*.py` and the tracked `src/p/deep/x/y.py` share a batch |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_no_path_matches_both_share_a_batch[two-disjoint-folders]` | red | no `gov plan`; `src/a/**` and `src/b/**` |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_no_path_matches_both_share_a_batch[two-tracked-files-in-one-folder]` | red | no `gov plan`; two tracked files of one folder |
| S3 | `test_w2_136_overlap.py::test_s3_patterns_no_path_matches_both_share_a_batch[two-files-not-yet-created-in-one-folder]` | red | no `gov plan`; two literal files not created |
| S4 | `test_w2_136_determinism.py::test_s4_two_runs_on_the_same_tickets_are_byte_identical[text]` | red | no `gov plan`; nine tickets with every code |
| S4 | `test_w2_136_determinism.py::test_s4_two_runs_on_the_same_tickets_are_byte_identical[json]` | red | as above, `--json` |
| S4 | `test_w2_136_determinism.py::test_s4_the_same_tickets_written_in_shuffled_file_orders_give_byte_identical_output[text]` | red | no `gov plan`; rebuilt at one path in three file orders (and mtime orders), the same commit |
| S4 | `test_w2_136_determinism.py::test_s4_the_same_tickets_written_in_shuffled_file_orders_give_byte_identical_output[json]` | red | as above, `--json` |
| S4 | `test_w2_136_determinism.py::test_s4_a_reversed_listing_of_the_ticket_folder_gives_byte_identical_output[text]` | red | no `gov plan`; in process, `os.listdir` and `os.scandir` of `.tickets` reversed |
| S4 | `test_w2_136_determinism.py::test_s4_a_reversed_listing_of_the_ticket_folder_gives_byte_identical_output[json]` | red | as above, `--json` |
| S4 | `test_w2_136_determinism.py::test_s4_an_overlap_tie_goes_by_priority_first[PLN-d011-PLN-d012]` | red | no `gov plan`; the priority-0 ticket first |
| S4 | `test_w2_136_determinism.py::test_s4_an_overlap_tie_goes_by_priority_first[PLN-d012-PLN-d011]` | red | no `gov plan`; priority first where the WBS and id orders point the other way |
| S4 | `test_w2_136_determinism.py::test_s4_an_overlap_tie_of_equal_priority_goes_by_wbs_order_before_the_id` | red | no `gov plan`; W2-421 (id PLN-d029) before W2-422 (id PLN-d021) |
| S4 | `test_w2_136_determinism.py::test_s4_an_overlap_tie_of_equal_priority_and_no_wbs_id_goes_by_the_id` | red | no `gov plan`; two tickets without `wbs_id`: the lower id first |
| S4 | `test_w2_136_determinism.py::test_s4_a_needs_after_write_cycle_is_broken_by_the_key_and_named_cycle_tiebreak[by-priority]` | red | no `gov plan`; each needs the path the other writes |
| S4 | `test_w2_136_determinism.py::test_s4_a_needs_after_write_cycle_is_broken_by_the_key_and_named_cycle_tiebreak[by-priority-swapped]` | red | as above, the other first |
| S4 | `test_w2_136_determinism.py::test_s4_a_needs_after_write_cycle_is_broken_by_the_key_and_named_cycle_tiebreak[equal-priority-by-wbs-order]` | red | as above, equal priority: the WBS order |
| S5 | `test_w2_136_findings.py::test_s5_a_ticket_without_needs_is_planned_on_its_own_writes_and_flagged_needs_undeclared` | red | no `gov plan`; flagged alone (not `needs: []`), one batch, exit 1 |
| S5 | `test_w2_136_findings.py::test_s5_a_deps_that_disagrees_with_depends_on_is_deps_disagree` | red | no `gov plan`; an agreeing ticket not flagged |
| S5 | `test_w2_136_findings.py::test_s5_a_waits_on_id_that_names_nothing_is_unknown_wait` | red | no `gov plan`; the id named; a closed ticket's id not flagged |
| S5 | `test_w2_136_findings.py::test_s5_a_store_with_none_of_the_findings_names_none[text]` | red | no `gov plan`; exit 0, no finding code |
| S5 | `test_w2_136_findings.py::test_s5_a_store_with_none_of_the_findings_names_none[json]` | red | as above, `--json` |
| S6 | `test_w2_136_override.py::test_s6_an_override_shares_the_batch_and_is_shown_with_its_decision_id[despite-an-overlap]` | red | no `gov plan`; one batch, OVERRIDE with DEC-899 (text and JSON) |
| S6 | `test_w2_136_override.py::test_s6_an_override_shares_the_batch_and_is_shown_with_its_decision_id[despite-a-wait]` | red | as above, over a depends_on |
| S6 | `test_w2_136_override.py::test_s6_without_the_override_the_same_tickets_wait[an-overlap]` | red | no `gov plan`; the same pair without the field: two batches, no OVERRIDE |
| S6 | `test_w2_136_override.py::test_s6_without_the_override_the_same_tickets_wait[a-wait]` | red | as above |
| S7 | `test_w2_136_ready.py::test_s7_premise_the_ready_form_is_the_dispatcher_s` | green (premise) | the dispatcher's `LOGNAME`, `read_list` and the 4-or-5-field rule are what the tests read |
| S7 | `test_w2_136_ready.py::test_s7_the_ready_file_holds_the_plan_s_batches_in_the_dispatcher_s_form` | red | no `gov plan`; the file's `# batch k` groups equal `--json`'s batches, each ticket once, every line in the form |
| S7 | `test_w2_136_ready.py::test_s7_with_ready_the_ready_file_is_the_only_thing_written` | red | no `gov plan`; the store and the working folder hashed unchanged, only the ready file added |
| S7 | `test_w2_136_ready.py::test_s7_without_ready_the_command_writes_nothing[text]` | red | no `gov plan`: a plan must be printed (so argparse's refusal, which writes nothing, cannot pass it), the trees unchanged |
| S7 | `test_w2_136_ready.py::test_s7_without_ready_the_command_writes_nothing[json]` | red | as above, `--json` |
| S8 | `test_w2_136_fresh.py::test_s8_a_ticket_edited_between_runs_changes_the_next_plan_and_back[a-dependency-added]` | red | no `gov plan`; a depends_on added (committed, the mtime kept) adds the wait; reverted, the first plan again |
| S8 | `test_w2_136_fresh.py::test_s8_a_ticket_edited_between_runs_changes_the_next_plan_and_back[the-ticket-waited-for-closed]` | red | no `gov plan`; the ticket waited for closed: it leaves the plan and the wait goes |
| S9 | `test_w2_136_launch_check.py::test_s9_a_lead_not_in_the_approved_batches_is_refused_naming_it` | red | no `plan_check` |
| S9 | `test_w2_136_launch_check.py::test_s9_a_lead_in_a_batch_with_no_waits_is_admitted` | red | no `plan_check` |
| S9 | `test_w2_136_launch_check.py::test_s9_a_wait_unmet_at_launch_time_is_refused_naming_what_it_waits_for[depends_on]` | red | no `plan_check`; names the ticket |
| S9 | `test_w2_136_launch_check.py::test_s9_a_wait_unmet_at_launch_time_is_refused_naming_what_it_waits_for[needs]` | red | no `plan_check`; names the ticket and the path |
| S9 | `test_w2_136_launch_check.py::test_s9_a_wait_unmet_at_launch_time_is_refused_naming_what_it_waits_for[waits_on]` | red | no `plan_check`; names the ticket |
| S9 | `test_w2_136_launch_check.py::test_s9_a_wait_met_at_launch_time_is_admitted[depends_on]` | red | no `plan_check`; the ticket waited for is closed now |
| S9 | `test_w2_136_launch_check.py::test_s9_a_wait_met_at_launch_time_is_admitted[needs]` | red | as above |
| S9 | `test_w2_136_launch_check.py::test_s9_a_wait_met_at_launch_time_is_admitted[waits_on]` | red | as above |
| S9 | `test_w2_136_launch_check.py::test_s9_the_waits_are_read_from_the_current_tickets_not_the_list` | red | no `plan_check`; listed in batch 1, a depends_on added since |
| S9 | `test_w2_136_launch_check.py::test_s9_a_plan_override_admits_the_lead_with_its_decision_id` | red | no `plan_check`; admitted with DEC-899 |
| S9 | `test_w2_136_launch_check.py::test_s9_the_launcher_refuses_a_lead_the_check_refuses_and_starts_no_session` | red | `'orchestrator' is not a worker role`: no lead path, no check call (D-1) |
| S9 | `test_w2_136_launch_check.py::test_s9_the_launcher_starts_a_lead_the_check_admits` | red | as above (D-1) |
| S9 | `test_w2_136_launch_check.py::test_s9_the_launcher_writes_an_override_in_the_launch_log` | red | as above (D-1); then one stderr line with OVERRIDE and DEC-899 |
| S9 | `test_w2_136_launch_check.py::test_s9_guard_a_worker_launch_never_consults_the_plan` | green (guard) | a worker of a ticket in no batch starts as before, the check never called (any session's gate is W2-20's, DEC-1088 (5)(b)) |
| S10 | `test_w2_136_never_a_gate.py::test_s10_premise_the_scan_finds_each_way_of_using_gov_plan` | green (premise) | the scan flags imports, `importlib`, command lists and strings; not a docstring, `gov.planner` or another command |
| S10 | `test_w2_136_never_a_gate.py::test_s10_no_module_of_the_category_imports_or_calls_gov_plan[close]` | green (guard) | `src/gov/close/**` |
| S10 | `test_w2_136_never_a_gate.py::test_s10_no_module_of_the_category_imports_or_calls_gov_plan[landing]` | green (guard) | the merge queue and the dispatcher (`tools/merge_queue.py`, `tools/dispatch/*.py`, `*.sh`) |
| S10 | `test_w2_136_never_a_gate.py::test_s10_no_module_of_the_category_imports_or_calls_gov_plan[claim]` | green (guard) | `src/gov/tasks/claims.py`, `src/gov/check/claims.py` |
| S10 | `test_w2_136_never_a_gate.py::test_s10_no_module_of_the_category_imports_or_calls_gov_plan[readiness]` | green (guard) | `src/gov/readiness/**` |
| S10 | `test_w2_136_never_a_gate.py::test_s10_no_module_of_the_category_imports_or_calls_gov_plan[hooks]` | green (guard) | `src/gov/hooks/**`, the kernel's hooks, `.claude/hooks/` |
| S10 | `test_w2_136_never_a_gate.py::test_s10_no_module_of_gov_outside_plan_and_launch_imports_or_calls_gov_plan` | green (guard) | every module of `src/gov` but `plan/` and `launch/` |

**A check of the tests themselves** (a scratch copy of `src`, never committed): a sketch of `gov plan` (about 200
lines: the guard's matcher on the tracked files, then literal-against-pattern exactly and two wildcards by their
literal prefixes; earliest batches; the tie key; the cycle broken at the lowest key), of `check_lead`, and of the
launcher's lead path passes all 68 cases that do not read the rest of the tree (S10 and S7's premise, green here).
Three mutants of it each fail their own cases: overlap decided on the tracked files only (10 cases: S3's six on
paths not yet created, and S4's four ties, whose paths are not created), ties by id alone (3 S4 cases), the override
ignored (2 S6 cases).

## Discoveries and open points (for the CTO)

- **D-1. The launcher is outside the ticket's paths, and has no lead today.** S9 says the launcher calls the check,
  but `src/gov/launch/launcher.py` is not in `allowed_paths`, and `gov launch` takes only worker roles
  (`WORKER_ROLES`; leads start through the scratch tools' `launch_now.sh` and `launch_when_gate_opens.sh`). The three
  launcher cases need the launcher to take `orchestrator` with a ticket and call the check: add
  `src/gov/launch/launcher.py` to W2-136's paths, or move those cases to W2-20's line (DEC-1088 (5)(b), which lands
  with W2-136). The function cases (ten) need only `plan_check.py`.
- **D-2. The CLI convention.** `src/gov/cli/main.py` reserves 0, 1 and 2 and prints a dict result as JSON, so S1's
  text lines and "1, a plan with findings" need `CHILD_EXIT_CODE` (the command prints its own output).
- **D-3. Warnings and the exit code.** Whether `READS_WIDE`, `CYCLE_TIEBREAK` or `OVERRIDE` alone exit 1 is not
  stated; the cases where they appear accept 0 or 1. Exit 1 is asked only for S5's three findings.
- **D-4. Exit 2's trigger** is not stated; the tests use a root with no `.tickets/`.
- **D-5. Batches in the ready list.** The dispatcher's form has no place for a batch: the tests assume `# batch k`
  comment headers (the dispatcher skips `#` lines, so it reads the list unchanged), and a brief and log named
  `<W2>-A5-<run>`. A ticket with no `wbs_id` cannot be written in the form (its first field is the W2): not tested.
- **D-6. "WBS order"** may mean the natural order of `wbs_id` or the WBS document's order; the tests use ids where both
  agree, and a planted root has no WBS document.
- **D-7. Priority's direction** is assumed: the lower number first (tk's 0 is the highest).
- **D-8. `waits_on:` entries.** W2-128 has not fixed their form ("ids or record paths, each with a one-line reason");
  the tests use plain ticket ids with a YAML comment. Decisions (waiting until ACCEPTED) and record paths are not
  tested.
- **D-9. "Written in the launch log":** there is no launch log file; the tests read the launcher's stderr (`_say`).
- **D-10. "Erring toward overlap" against "the rest share one batch".** The tests ask for one batch only where no path
  can match both and one side is literal, or the literal prefixes part. Two wildcards with nested prefixes and no
  common path (`src/new/*.py` and `src/new/sub/**`) are not asked either way.
- **D-11.** `plan_override`'s decision id is not checked against a register (a planted root has none).
- **D-12.** DEPENDENCY-MAP-1 §3 names `READS_UNDECLARED` and `READS_WHAT_WRITES`; the ticket's lines (DEC-1088 (3))
  replace them with `NEEDS_UNDECLARED` and `NEEDS_WHAT_WRITES`. The tests follow the ticket.
- **D-13.** S8's edits are committed and kept on disk alike, so whether the plan reads the working tree or `HEAD` is
  not decided by the tests.

## Files

- `w2_136_support.py`: the planted store, the runner, the text, JSON and ready-list readers, the tree's state, S10's
  scan.
- `conftest.py`: the `planted` fixture.
- `test_w2_136_plan_output.py` (S1), `test_w2_136_order.py` (S2), `test_w2_136_overlap.py` (S3),
  `test_w2_136_determinism.py` (S4), `test_w2_136_findings.py` (S5), `test_w2_136_override.py` (S6),
  `test_w2_136_ready.py` (S7), `test_w2_136_fresh.py` (S8), `test_w2_136_launch_check.py` (S9),
  `test_w2_136_never_a_gate.py` (S10).
