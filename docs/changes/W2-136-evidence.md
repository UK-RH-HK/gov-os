# W2-136 evidence: `gov plan`, the dependency map and the launch batches, and `gov launch`'s check against them (DAEO-p3ln; DEC-1088, DEPENDENCY-MAP-1)

**What it is.** A new read-only command, `gov plan`, derives from each open ticket's writes (`allowed_paths`), `needs:`,
`waits_on:` and `depends_on` which tickets must wait for which, and proposes launch batches. `reads:` orders nothing
(DEC-1088 (3), §5 (b)). The orchestrator approves the batches into the ready list (DEC-1007 (2)). `gov launch` refuses a
lead outside the approved batches or with an unmet wait (DEC-1088 (5)(a)).

## The change

- **`src/gov/plan/`** (new; `gov plan` is found through `src/gov/plan/command.py`, so `gov.cli.main` is unchanged):
  - `tickets.py`: every `.tickets/*.md`, read fresh on every call; the fields above, plus `deps`, status, priority, WBS
    id and `plan_override: <DEC-id>`. A `waits_on` entry is read for its id: `"DAEO-x — the reason"`, `"DEC-12: why"`,
    `{id: ..., reason: ...}` or `{DAEO-x: the reason}`.
  - `overlap.py`: two patterns overlap when some path matches both, read as the guard reads them
    (`gov.guard.decide._match_pattern`: `*` inside a folder, `**` across). A literal path against a pattern is the
    guard's matcher called on it; two patterns are compared pattern to pattern (a search over pairs of positions in the
    guard's own reading of each), which decides the paths not yet created as well as the tracked ones. It errs toward
    overlap: a literal path is also read as the folder of that name. A tracked file that matches both names the
    overlap.
  - `derive.py`: the waits (`DEPENDS_ON`, `WAITS_ON`, `NEEDS_WHAT_WRITES`, `WRITES_OVERLAP`), the warning
    (`READS_WIDE`), the findings (`NEEDS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT`) and `OVERRIDE`. The order is a
    topological order by the fixed key (priority, then WBS order with numbers compared as numbers, then id); a cycle is
    broken at its first ticket by the key and named `CYCLE_TIEBREAK`; overlapping writers go in that order; each ticket's
    batch is one after its latest predecessor. A wait on something outside the plan that is not met (a decision not
    ACCEPTED in `docs/DECISION_REGISTER.md`, an unfinished ticket not planned) holds the ticket out of every batch,
    with every ticket that waits for it.
  - `render.py`: the text lines, the `--json` result, the `--ready` list (`# batch k`, then
    `<W2> <id> <W2>-A5-run1.md <W2>-A5-run1.json`), written whole through a temporary file beside it.
  - `command.py`: `gov plan [--open | --tickets <id> ...] [--json] [--ready <file>]`; `--open` is the default. It prints
    the plan itself and ends with its own code (`CHILD_EXIT_CODE`): 0 a plan, 1 a plan with findings, 2 cannot run (no
    store, a ticket that cannot be read, an unknown `--tickets` id, a `--ready` file that cannot be written), with the
    shared envelope under `--json` (`PLAN_CANNOT_RUN` as the error code).
- **`src/gov/launch/plan_check.py`** (new): `check_lead(root, ticket_id, *, ready=None)` returns `admitted`, `reason`
  and `override` (fields, a mapping or a triple). `ready` is the file, its text, its lines or its ids; `None` reads
  `$GOV_PLAN_READY` (relative to the project) or else `governance/project/orchestration/ready.txt`. The waits are the
  plan's own (`hard_waits`) on the current tickets: `depends_on` on an unfinished ticket, `waits_on` not closed or not
  ACCEPTED or naming nothing, a needed path an unfinished ticket writes. A missing ready list refuses. An override
  admits, with its reason naming what it set aside.
- **`src/gov/launch/launcher.py`** (the designer's D-1): at the argument checks, a lead is checked once. A lead is a
  launch as `orchestrator` (or `lead`, W2-121's name), or a call from a session whose `GOV_ROLE` is `orchestrator`
  with a `GOV_TICKET` (its own ticket is checked). A refusal is `LAUNCH_REFUSED` naming what the ticket waits for, before
  any folder or session; an override is written to the launch's stderr as `gov launch: OVERRIDE <DEC-id>: <reason>`.
  `check_lead` is a module-level function in the launcher that calls `plan_check.check_lead` when called.

## The KPI lines and how each is met

| KPI | How it is met | Unit tests (`tests/unit/plan/`, `tests/unit/launch/test_w2_136_plan_check.py`) | `gov accept` |
|---|---|---|---|
| S1: the lines, `--json`, exit 0/1/2 | `render.lines`, `command.run` | `test_the_first_line_the_batches_and_the_waits`, `test_only_open_and_in_progress_tickets_are_planned`, `test_json_gives_the_same_plan_in_the_shared_envelope`, `test_no_ticket_store_cannot_run`, `test_a_ticket_that_cannot_be_read_stops_the_plan`, `test_tickets_names_the_planned_tickets_and_an_unknown_one_cannot_run` | 6/6 |
| S2: `NEEDS_WHAT_WRITES` naming the path, `WRITES_OVERLAP`, `DEPENDS_ON`, `WAITS_ON`, `READS_WIDE` orders nothing, the rest in one batch | `derive.hard_waits`, `_reads_wide`, `make_plan` | `test_a_needed_path_an_unfinished_ticket_writes_...`, `test_a_needed_path_a_closed_ticket_wrote_orders_nothing`, `test_depends_on_and_an_unfinished_waits_on_make_it_wait`, `test_reads_orders_nothing_and_warns_...`, `test_a_waits_on_decision_not_accepted_holds_...`, `test_a_waits_on_record_path_that_exists_is_met` | 7/7 |
| S3: the guard's matcher, tracked files and pattern to pattern, toward overlap | `overlap.patterns_overlap`, `Tracked.witness` | `test_w2_136_overlap.py`: 15 pattern pairs both ways; the guard's matcher called for a literal; 120 random patterns: every pair the guard's matcher shows a common path for is an overlap; the witness; plus `test_writes_that_overlap_run_in_series` (5 rows) | 13/13 |
| S4: byte-identical in any file order; ties and cycles by priority, WBS order, id; `CYCLE_TIEBREAK` | `derive.key`, `_order` | `test_the_same_tickets_give_the_same_bytes_in_any_file_order`, `test_ties_go_by_priority_then_wbs_order_then_id`, `test_a_needs_after_write_cycle_is_broken_by_the_key_and_named` | 13/13 |
| S5: `NEEDS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT` | `derive._findings` | `test_no_needs_is_planned_on_its_writes_and_flagged`, `test_deps_that_disagree_...`, `test_a_waits_on_that_names_nothing_...`, `test_a_waits_on_entry_is_read_for_its_id` (6 rows) | 5/5 |
| S6: `plan_override` shares a batch despite an overlap or a wait, shown as `OVERRIDE <DEC-id>` | `make_plan`'s overrides | `test_an_override_shares_a_batch_despite_an_overlap_and_a_wait` | 4/4 |
| S7: `--ready` writes the list and nothing else; without it nothing is written | `render.write_ready` only under `--ready` | `test_without_ready_nothing_is_written` (tree hashed), `test_ready_writes_the_batches_in_the_dispatchers_form_and_nothing_else` | 5/5 |
| S8: recomputed from the current tickets every run | `tickets.load` on every call; no file kept | `test_a_ticket_changed_between_two_runs_changes_the_plan` | 2/2 |
| S9: `gov launch` refuses a lead not in the batches or with an unmet wait, naming it, starting nothing; an override admits and is logged | `plan_check.check_lead`; the launcher's one call (`_admit_lead`), for the launched role only; an admitted lead starts with `build_lead_settings` (second pass, below) | 34 cases: not in a batch, a wait met, `depends_on`/`needs`/`waits_on`/unknown unmet, the current tickets, an override, no ready list, the launcher's refusal (both lead forms), an admitted lead's start and env (both forms), an override's start and log line, a refused lead starts nothing, a lead's guard-removing arguments and an unwired guard refused, a stand-in verdict, a worker launch from the CTO's or a lead's session never checked | 14/14 |
| S10: no close, landing, claim, readiness or hook module imports `gov plan` | only `gov.launch.plan_check` imports it; the launcher reaches it only through that module | `test_no_module_but_launchs_check_imports_the_plan`, `test_the_launcher_reaches_the_plan_only_through_its_check` | 7/7 |
| S11: under 5 s on this repository (the CTO's) | the CTO's measure, 2026-11-07, `gov plan --open` from the main tree (integrate `26328bc1`) with this branch's code, five runs | 77 open tickets, 17 batches; runs 0.81 / 0.85 / 0.78 / 0.78 / 0.84 s, **median 0.81 s**: pass (exit 1: older tickets are NEEDS_UNDECLARED until W2-128) | pass |

## Second pass (DAEO-p3ln, the CTO's settlement under DEC-1088 (5)(a))

- **A lead admitted by the check is started.** `gov launch orchestrator|lead <ticket>`: the plan's check, then the CLI
  arguments check and the repository settings check (the guard wired: a lead has no sandbox, so the guard is its only
  fence), then the session, with `{"env": {"GOV_ROLE": "orchestrator", "GOV_TICKET": <ticket>}}` and no sandbox block,
  as the dispatcher starts a lead. No ticket status check (the plan's check already found the ticket), no own folder
  (DEC-743 7), no temp folder. The lead's settings come from a separate `build_lead_settings`: `build_settings` always
  yields the strict sandbox block and deny rules that `sandbox_faults` checks, and a lead branch in it would loosen that
  shape. The session running and signal code moved unchanged into `_run`, shared; a worker launch is as before.
- **The caller's environment is no longer read.** The clause that checked the calling session's own `GOV_TICKET` when
  its `GOV_ROLE` was `orchestrator` is removed: only the launched `role` and `ticket_id` decide; a worker launch never
  consults the plan (the CTO's session `DAEO-sdxk` launching any worker included).
- **Results:** unit (`tests/unit/launch` and `tests/unit/plan/test_w2_136_*.py`, the heavy slot, `-m "not local_only"
  -k "not real and not green_here and not time_limit"`, HOME an empty folder): 154 passed, run without `GOV_ROLE` and
  `GOV_TICKET` and again with `GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk`; the exclusion selected none of them, the 86
  deselected are the project's opt-in lists (`tests/conftest.py`). **`gov accept W2-136`: pass, 76/76 (success-9 14/14),
  both without and with the CTO's env.**

## First pass test results (through the heavy slot; HOME a scratch folder whose `.local` links to the user site)

- **Unit:** `tests/unit/plan tests/unit/launch/test_w2_136_plan_check.py`: 80 passed.
- **`gov accept W2-136`:** fail, 74/76. success-1 6, success-2 7, success-3 13, success-4 13, success-5 5, success-6 4,
  success-7 5, success-8 2, **success-9 12 passed, 2 failed**, success-10 7; 0 unmapped, 0 skipped. The engineer does
  not see which two S9 cases fail (DEC-957). The likeliest reason, from S9's words "a plan_override ... lets it
  start": the cases expect an admitted lead to start a session through `gov launch`. The launcher has no lead start
  (it starts worker roles only; `gov launch lead <ticket>` is W2-121's line), and this ticket's path holds the one
  call at the argument checks only. A second possible reason: where the launcher finds the approved ready list is not
  stated by the KPI line (here `$GOV_PLAN_READY`, else `governance/project/orchestration/ready.txt`).
- **Regression:** `tests/unit/launch` with `--optin lifted,breadth` (every row), `-m "not local_only" -k "not real and
  not green_here and not time_limit"`: 177 passed (the exclusion deselected none; without `--optin` the project's
  opt-in lists keep 91 of the 177). `tests/unit/cli` the same way: 14 passed. `tests/acceptance/W2-20` is not on this
  branch (W2-20 is built and held on `w2/W2-20`), so it was not run.
- **On this repository** (`gov plan --open`): 76 tickets, 17 batches, exit 1: every ticket filed before W2-128's line
  is `NEEDS_UNDECLARED`, and DAEO-ongl is `DEPS_DISAGREE` (`deps [DAEO-5ce2]`, `depends_on []`).
