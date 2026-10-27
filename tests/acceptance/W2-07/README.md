# W2-07 acceptance tests: `gov close` by ticket class; the gates before any test

Ticket `DAEO-r9ss` (W2-07, STANDARD). Written by the independent test designer (MR-3) before the implementation,
from the ticket's KPI lines, its card (`docs/plan/WAVE_2_WBS.md` §2, W2-07), lens I's P-IS-4 and I2 F9/F13, and
DEC-868, DEC-892, DEC-896, DEC-898, DEC-899 and DEC-790. No implementation was read.

**Round 2 (DEC-923 item 2, DEC-924).** A fresh independent test designer revised `test_w2_07_decision_records.py`
(and added W1-01's `acceptance_exemptions` list to the support's path-map writer) to KPI 3 as amended, the round-2
KPI and failure lines 3 and 4, from the ticket file, the card's "Round 2 (owner, DEC-923)" note, DEC-923, DEC-924,
DEC-896 item 1, DEC-891, DEC-906 and DEC-734, the trailer gate's public reading of `accepted_history`
(`src/gov/close/history.py` on `w2/integrate`) and W1-01's reading of `acceptance_exemptions`
(`tests/acceptance/W1-01/w1_01_support.py`). Each change is carried by a commit with `Rewrite-Reason: DEC-923`; no
expectation was lowered. Round 2's own map is the section "Round 2: what the work-without-a-task gate measures".

## How the tests run

- **Through public interfaces only:** `gov close <ticket> --json` (the API-0002 envelope, exit codes, findings),
  `gov check --json`, `gov readiness --ticket`, `python3 -m gov.check.audit_validator`, the project's path map,
  ticket files, records, the decision register and commit trailers.
- **The code under test is this worktree's `src/` (DEC-732).** The support module reuses W2-53's support, which
  reuses W2-01's and W1-30's. W1-30's sandbox gives every process it starts (`gov close`, `gov check`, the audit
  validator) `PYTHONPATH=<this worktree>/src`, derived from the support file's own location, and `w2_07_support`
  asserts the four supports agree on that `src/`. Run the suite from this worktree:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 -q -p no:cacheprovider -rs`.
- **Every project is a temporary git repository built from scratch** (W2-01's `Project`): single named files only
  (the ticket tool, the trailers check's declaration, the feature-readiness schema where a case needs it), never a
  folder of this repository. Deterministic, no network.
- **"No test ran" is seen from outside.** Each gate case's project holds two *telling* tests (W1-30's
  `telling_test`): the ticket's acceptance test `test_w207_acceptance_mark` and a regression test
  `tests/unit/test_w207_regression_mark.py`. Each writes a file into a folder outside the project whenever it runs.
  A gate that refuses before any test leaves the folder empty.
- **"No attempt spent"** is the ticket's iteration count (`.gov-runtime/iterations/<ticket>.json`, W1-30's reader)
  still 0, and no escalation file written.
- **The suite's path map sets low disk floors** (assumption A2), so no case depends on how full this machine's
  disk is. Two workers per parallel run (DEC-549), as W1-30's projects.

## KPI and row map

| KPI line / row | Tests (file :: function) | Red today because |
|---|---|---|
| S1 judged by class [W2-H045]: research | `test_w2_07_by_class.py::test_a_research_ticket_closes_on_its_evidence_record` | refused `NO_ACCEPTANCE_TESTS` |
| S1: audit | `...::test_an_audit_ticket_is_judged_on_its_report_and_the_audit_validator[report-passes-the-validator]` | refused `NO_ACCEPTANCE_TESTS` |
| S1: integration, coordination | `...::test_an_integration_or_coordination_ticket_closes_on_its_named_evidence_files[integration, coordination]` | refused `NO_ACCEPTANCE_TESTS` |
| S1: specification (closed readiness and tests) | `...::test_a_specification_ticket_is_judged_on_its_readiness_record_and_its_tests[readiness-closed]` | **green already** (it has tests; the readiness check is new) |
| S1: specification, readiness open | `...[a-required-row-open]` | closes: today's close does not read the readiness record |
| S1: implementation on its acceptance tests | `...::test_an_implementation_ticket_naming_evidence_but_without_acceptance_tests_is_refused`; W1-30's revised `test_w1_30_no_acceptance_tests.py` | **green already** (the guard against "any evidence closes"); W1-30's revision is red (below) |
| F1 research without evidence record | `...::test_a_research_ticket_without_its_evidence_record_is_refused` | refused, but for `NO_ACCEPTANCE_TESTS`; the refusal does not name the evidence record |
| F1 audit report fails the validator | `...[report-fails-the-validator]` | refused for `NO_ACCEPTANCE_TESTS`, not the validator's finding |
| S1 integration missing a named file | `...::test_an_integration_or_coordination_ticket_missing_a_named_evidence_file_is_refused[...]` | refused, not naming the missing file |
| S2 test-revision on declared `acceptance_tests.path` [DEC-892, DEC-896 item 3] | `test_w2_07_test_revision.py::test_a_test_revision_ticket_closes_on_the_tests_its_ticket_file_names`, `...whose_named_tests_fail_is_refused_on_its_acceptance_run` | refused `NO_ACCEPTANCE_TESTS`; no `acceptance` run of the declared folder |
| S3 decision record under an ACCEPTED decision is measured [DEC-896 item 1] (round 1) | `test_w2_07_decision_records.py::test_a_decision_record_of_governance_records_under_an_accepted_decision_counts_as_measured` | refused `WORK_WITHOUT_TASK` (round 1; built, green). Round 2's rows are in the section below |
| F3 decision record outside an ACCEPTED decision (round 1) | `...::test_a_decision_record_naming_a_decision_that_is_not_accepted_counts_as_unmeasured`, `...naming_no_decision...`, `...that_also_changes_any_other_path...` (round 1's `...code_tests_or_the_kernel...`) | **green already** (today every such commit is unmeasured); they hold the rule's limits. Round 2 widened them (below) |
| S4 commit gates first: trailers | `test_w2_07_commit_gates.py::test_a_commit_without_its_trailers_stops_the_close_before_any_test` | both telling tests ran (finding gathered after the runs, counted) |
| S4: work without a task | `...::test_work_without_a_task_stops_the_close_before_any_test` | tests ran |
| S4: accepted history | `...::test_a_refused_accepted_history_entry_stops_the_close_before_any_test` | tests ran |
| S4: the probe gate, stale probe [W2-M403] | `...::test_a_stale_probe_is_named_before_any_test_runs` | tests ran |
| S4: the ratchet's reading of both lists [I4 F14] | `...::test_a_ratchet_entry_the_ratchet_would_not_count_stops_the_close_before_any_test[accepted_reds, load_sensitive]` | tests ran |
| S5 pre-close gate: collection in one process | `test_w2_07_pre_close_gate.py::test_a_collection_error_in_any_suite_refuses_before_any_test[regression, acceptance]` | tests ran, counted; the refusal does not say "collect" |
| S5: `gov check` | `...::test_a_red_gov_check_refuses_before_any_test` | closes: today's close runs the checks only when governance files changed (DEC-480) |
| S5: fresh checkpoint | `...::test_a_stale_checkpoint_refuses_before_any_test` | tests ran (`CHECKPOINT_STALE` gathered after them, counted) |
| S6 disk floor [DEC-898, DEC-899 item 5] | `...::test_a_disk_below_a_floor_refuses_before_the_regression_naming_the_reading[space, inodes]` | closes: no disk reading |
| S7 probe named-finding acceptance [W2-M371, DEC-790] | `test_w2_07_probe_findings.py::test_a_failed_probe_whose_every_finding_an_accepted_owner_decision_names_lets_the_ticket_close`, `...::test_a_finding_the_decision_does_not_name_still_refuses`, `...::test_a_decision_that_is_not_accepted_does_not_accept_the_findings` | refused `PROBE_INVALID` (judgement `fail`); the refusal does not name `F2`; the third is **green already** |
| S8 complete, tracked repair ticket [F-m8, W2-L209, W2-L236, AR-9] | `test_w2_07_repair_and_escalation.py::test_a_refused_close_writes_a_complete_schema_valid_repair_ticket`, `...::test_the_repair_ticket_stays_tracked_and_blocks_no_later_close` | no `role`, `allowed_paths`, `kpis`; the file is untracked |
| S9 governance share [W2-M166, W2-M286] | `test_w2_07_share.py::test_a_close_by_class_carries_the_measured_governance_share` | the research ticket cannot close (`NO_ACCEPTANCE_TESTS`) |
| S10 adoption-gap refusals not counted [W2-H038, W2-M249] | `...::test_adoption_gap_refusals_do_not_count_toward_escalation` | the trailer refusal is counted (count 1 after the first) |
| S10 repeated refusal reuses its repair ticket [W2-M252] | `...::test_a_repeated_identical_refusal_reuses_its_repair_ticket` | a second repair ticket is opened |
| S11 interrupted close [W2-M158] | `...::test_an_interrupted_close_leaves_nothing_that_blocks_the_next_close` | `TREE_NOT_COMMITTED`: the killed close's record and checkpoint block the next close |
| S12 the named revisions | `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` (3 functions, 6 cases), `test_w1_30_close.py::test_collection_error_refuses_close` | see "Revisions of W1-30" |
| W2-M263 (DEC-738 item 4) | covered by the commit gates' trailer case and W1-30's existing trailers-base cases; RED stays when nothing comes after the base (DEC-479), and how the close reports it is today's `TRAILER_MISSING` "not measured" | (no new behaviour asserted: the sources fix no new form) |
| W2-L107 (repair ticket carries class and context hash) | W1-30's `test_w1_30_disposition.py` (existing); this suite's complete-ticket case | already held by W1-30 |
| W2-L108 (fields through the ticket tool) | the complete-ticket case holds the outcome (schema-valid); how the file is written is not a public interface | not separately testable from outside |
| W2-L165 (repair-ticket cut, `findings_cut`, narrow catch) | W1-30's `test_w1_30_r13_long_findings.py` (existing) | builder rows (the triage: "its builder takes it") |
| W2-L210 (close record per close, escalation folder, Implements ids) | the interrupted-close case holds "one close record"; the rest are builder rows | builder |
| W2-M149 (a check-runner error counted, with a repair ticket) | builder row; the pre-close gate's red-check case covers the runner's red | builder |
| W2-M157 (installed kernel skills listed) | W1-30's `test_w1_30_r13_installed_skills.py` (existing, green) | already fixed at the base |
| W2-L123, W2-L124, W2-L196, W2-L197, W2-L208, W2-M178, W2-M248, W2-M348, W2-M349 (telemetry counting details) | the share case holds that a measured share reaches the record; the counting rules are the engineer's unit tests (`tests/unit/telemetry/**`) | builder rows ("fits W2-07's paths; its builder takes it", the triage) |
| W2-M276 (`checker.close` writes an audit ticket citing DEC-088, MR-4) | builder row in `gov readiness`'s close, outside `gov close`'s KPI lines | builder |
| W2-M354 (repair ticket in a-dev incomplete) | the complete-ticket case (the same defect at its source) | — |

Round 1's count: expected **green already** (8 of the suite's 40 cases; the other 32 were red): the specification ticket with a closed record (its acceptance tests already ran),
the implementation-with-evidence guard, the five decision-record limit cases, and the not-accepted probe decision.
They hold limits of the new rules; none shows a row already fixed except that today every task-less commit is
unmeasured (DEC-490) and a failed probe always refuses.

## Interface assumptions (the specification these tests assume)

- **A1. Evidence of a class ticket.** A ticket names the evidence its class is judged on in its `acceptance_tests`
  mapping, under `evidence`: a list of repository-relative paths (beside the `judged_by` text real tickets
  already carry). Research: each named path is a committed record with `type: research`. Audit: each named path is
  a report the audit validator passes (`python3 -m gov.check.audit_validator <path>` exits 0). Integration and
  coordination: each named file exists and is committed. A missing or failing piece refuses the close and names the
  path (or, for an audit report, the validator's finding). The tests also commit the evidence with the ticket's own
  commits inside its allowed paths, so a close that finds it through those commits reads the same files.
- **A1b. Specification.** A specification ticket names its specification in `specification:` (DEC-307); its
  readiness record is closed when `gov readiness --ticket <id>` passes; the close runs its acceptance tests too, and
  an open record refuses, naming the readiness record (or `SPEC_NOT_CLOSED`).
- **A1c. Test revision.** A ticket's acceptance run is the folder its file declares in `acceptance_tests.path`;
  the answer states that run as `run: acceptance` in `test_runs`, and a failing test there refuses (exit 3).
- **A2. Disk floors.** Two top-level keys of the path map, as `close_timeout` and `close_workers` are (DEC-549):
  `close_free_gib_floor` (default 100) and `close_free_inodes_floor` (default 10,000,000). The reading is of the
  file system that holds the project (free space and free inodes as an unprivileged process sees them). Below
  either floor the close refuses before its regression; the refusal says "free" and names the disk or space (or
  "inode"), and spends no attempt.
- **A3. Probe findings.** A probe record lists its findings in its frontmatter under `findings`: a list of finding
  ids.
- **A4. The accepting decision.** An entry of the register the path map names (`decision_register`, DEC-479), with
  the status `ACCEPTED (owner, …)` and brought in by a `Role: owner` commit, whose text names the probe record (its
  id and path), its probed commit (full id) and every finding id with its list row. A finding not so named refuses,
  and the refusal names it. A close that passes names the decision (in its result or close record).
- **A5. A decision-record commit "names" a decision** in its message: its subject and/or an `Implements:` trailer
  (the tests use both). The governance records are, as amended by DEC-923 item 2, DEC-891's records (`.tickets/**`,
  `docs/checkpoints/**`, `docs/close/**`, `docs/probes/**`, the register the path map names, `docs/plan/**`,
  `governance/project/orchestration/**`) beside the prompts (`governance/project/prompts/**`), the briefs
  (`governance/project/briefs/**`) and the path map. Round 1 read DEC-896 item 1's narrower list (without DEC-891's
  first four folders).
- **A6. Gate refusals.** A commit-gate or pre-close-gate refusal is a refusal (`ok: false`, non-zero exit) that
  names its cause: the gate's existing code where one exists (`TRAILER_MISSING`, `WORK_WITHOUT_TASK`,
  `ACCEPTED_HISTORY_REFUSED`, `PROBE_INVALID`, `ACCEPTED_RED_REFUSED`, `LOAD_SENSITIVE_REFUSED`,
  `CHECKPOINT_STALE`), the word "collect" and the broken file for a collection error, the check's id for a red
  check. No test runs and the iteration count is not raised. The tests assert no exit code beyond "not 0" and
  nothing about a repair ticket for such a refusal (see the packages).
- **A7. Repair ticket.** A refused close's repair ticket is in `.tickets/`, valid against
  `ticket.schema.json` (with `role`, `allowed_paths`, `kpis`), known to git after the refusal, and blocks no later
  close of the ticket. A second refusal with the same findings reuses it and names it.
- **A8. Interruption.** A close killed (SIGKILL) inside the ticket tool's `close` leaves nothing that makes the next
  close refuse (in particular no `TREE_NOT_COMMITTED` for its own records); the next close leaves one close record.

## Round 2: what the work-without-a-task gate measures (DEC-923 item 2)

All in `test_w2_07_decision_records.py`, each through `gov close --json` in a temporary project. "Red today" is
against this worktree's code at `b6bc7773` (round 1, built): each red is refused `WORK_WITHOUT_TASK`, naming the
record or listed commit (checked on the run of 2026-10-27).

| KPI line | Case (function `[ids]`) | Red today because |
|---|---|---|
| S3 (amended): measured under a delegated decision | `test_a_decision_record_of_governance_records_under_an_accepted_decision_counts_as_measured[delegated-decision]` | refused `WORK_WITHOUT_TASK`: the judge counts only an ACCEPTED owner decision |
| S3: measured under the owner's decision, no owner trailer | `...[owner-decision]` (round 1's case, revised) | **green already** |
| S3: measured under a decision later superseded | `test_a_decision_record_under_a_decision_later_superseded_or_changed_counts_as_measured[superseded]` | refused `WORK_WITHOUT_TASK`: a superseded decision is not counted |
| S3: measured under a decision later changed (`· **Changed by:**`) | `...[changed]` | **green already** (kept: it holds the line against a judge that would read any later note as undone) |
| S3: `.tickets/`, the closing ticket's own file | `test_a_decision_record_that_changes_the_closing_tickets_own_file_counts_as_measured` | refused `WORK_WITHOUT_TASK`, naming `.tickets/PROJ-dcrd.md` |
| S3: DEC-891's other record folders | `test_a_decision_record_that_also_changes_another_governance_record_counts_as_measured[checkpoints, close, probes]` | refused `WORK_WITHOUT_TASK`: those folders are not records to the judge |
| S3: the records round 1 already counted | `...[orchestration, prompts, briefs, plan]` | **green already** |
| Round-2 KPI: on `accepted_history`, code or tests | `test_a_commit_an_owner_committed_list_names_under_its_accepted_owner_decision_counts_as_measured[accepted_history-code, accepted_history-tests, accepted_history-abbreviated-id-code, accepted_history-abbreviated-id-tests]` | refused `WORK_WITHOUT_TASK` (the trailer gate accepts the entry: its answer lists it in `accepted_history`) |
| Round-2 KPI: on `acceptance_exemptions`, code or tests | `...[acceptance_exemptions-code, acceptance_exemptions-tests]` | refused `WORK_WITHOUT_TASK`: the judge does not read the list |
| F3: a decision never ACCEPTED | `test_a_decision_record_naming_a_decision_that_is_not_accepted_counts_as_unmeasured[proposed, rejected, superseded-never-accepted]`; `test_a_decision_record_naming_no_decision_counts_as_unmeasured` | **green already** (they hold the limit) |
| F3, F4: any other path (code, tests, kernel, `docs/assessment/`), with or without `Role: owner`, no list | `test_a_decision_record_that_also_changes_any_other_path_counts_as_unmeasured[code, tests, kernel, assessment × orchestrator, owner]` | **green already** (they hold the limit) |
| Round-2 KPI, F4: the lists' own limits | `test_a_list_entry_outside_the_lists_reading_measures_nothing[accepted_history-delegated, accepted_history-proposed, acceptance_exemptions-delegated, acceptance_exemptions-proposed, acceptance_exemptions-abbreviated-id]` | **green already** (they hold the limit) |

Count: 35 cases in the file, 12 red and 23 green against today's code. Round 2 is done when all 35 pass.

### Revisions of round 1's cases (`Rewrite-Reason: DEC-923`)

- **The measured case** (`...under_an_accepted_decision_counts_as_measured`). Before: the owner's commit with
  `Role: owner`, under an `ACCEPTED (owner, …)` decision. After: the orchestrator's commit with
  `Role: orchestrator` (as this repository records the owner's decisions, DEC-861), and the case asserts that no
  `Role: owner` trailer is there, so the trailer cannot measure it (DEC-923 item 2). A delegated-decision id is
  added. Expectation unchanged: it closes.
- **The not-accepted case.** Before: `PROPOSED`. After: `PROPOSED`, `REJECTED` and a decision superseded without
  ever being ACCEPTED (`SUPERSEDED by DEC-599 (…; it was PROPOSED)`), each on a `Role: owner` commit. Expectation
  unchanged: refused `WORK_WITHOUT_TASK`, naming the commit.
- **The no-decision case.** Unchanged (`Role: owner`, refused).
- **The code, tests, kernel case.** Renamed `...that_also_changes_any_other_path_counts_as_unmeasured`. Before:
  code, tests, kernel, `Role: owner`. After: code, tests, kernel and `docs/assessment/` (611955fa's shape), each with
  `Role: orchestrator` and with `Role: owner` and no list naming it (failure line 4). Expectation unchanged: refused
  `WORK_WITHOUT_TASK`, naming the commit.

### Readings chosen (round 2)

- **A9. The register's status forms of "an ACCEPTED decision".** These are copied from the register, not invented:
  `ACCEPTED (owner, …)`, DEC-903's `ACCEPTED (delegated, orchestrator, …)`, DEC-876's
  `SUPERSEDED by DEC-n (<date>; it was ACCEPTED, owner, …)`, and an `ACCEPTED (owner, …)` line with
  `· **Changed by:** DEC-n: …` after its basis. Never ACCEPTED: `PROPOSED`, DEC-021's `REJECTED (for authority)`,
  and `SUPERSEDED by DEC-n (…; it was PROPOSED)`. The later-superseded and later-changed cases make the record while
  the decision is ACCEPTED, then restate its status in a later record of the register alone. The judge may read
  the register at the commit or at `HEAD`, and both readings give the same answer in every case (not pinned).
- **A10. The lists' readings.** `accepted_history` is read as the trailer gate reads it (DEC-734;
  `src/gov/close/history.py` on `w2/integrate`): the commit by a full or an abbreviated id, and the decision an entry
  of the register with a status line `ACCEPTED (owner…`, not superseded or revoked, whose text names the commit
  (eight or more of its digits). `acceptance_exemptions` is read as W1-01 reads it (`w1_01_support.acceptance_exemptions`):
  the commit by its whole id only, and the decision a `DEC-<n>`. DEC-923 item 2 adds "under its ACCEPTED owner
  decision", so a delegated or a proposed decision on either list measures nothing. The entries are the owner's own
  `Role: owner` commits (`Task: setup`) outside the ticket's paths. The listed commit is the owner's
  `Task: decision-record`, `Implements: DEC-n`, `Role: owner` commit (c9a08678's shape, with `Implements:` so that
  the trailer gate has nothing to say about it). It changes the ticket's code or its tests (`tests/unit/w207/`, in
  the fixture ticket's allowed paths).
- **A11. Gate order for a refused `accepted_history` entry.** The trailer gate refuses an `accepted_history` entry
  outside DEC-734's form on its own (`ACCEPTED_HISTORY_REFUSED`), and the rule fixes no order between that gate and
  the work-without-a-task gate. So those two limit cases accept either code, provided the refusal names the commit.
  The `acceptance_exemptions` limits must be `WORK_WITHOUT_TASK` itself, because no other gate reads that list.

### Readings left open (not pinned; any of them is a package if it matters)

- **O1.** Whether an `acceptance_exemptions` entry's decision must also name the commit in its text, as DEC-734
  requires for `accepted_history`. W1-01 does not read the register. The fixtures name it, so either reading passes.
- **O2.** A commit that names two decisions, one ACCEPTED and one never ACCEPTED: is "names an ACCEPTED decision"
  enough, or must every decision it names be one? 611955fa names two decisions that are both ACCEPTED. Not tested.
- **O3.** Whether a listed commit must be a decision-record commit (`Task: decision-record`). The rule says "a
  commit that the lists name", so a listed commit with no `Task:` at all would also be measured, but the trailer
  gate refuses that commit without `accepted_history`. Not tested.
- **O4.** An `accepted_history` entry under an owner decision that was ACCEPTED and later superseded. The trailer
  gate refuses it (DEC-734's reading: not undone), while the record rule counts such a decision. DEC-923 says the
  lists are read as the trailer gate reads them, so a test would follow the trailer gate. That is not stated
  outright, so it is not tested.

## Revisions of W1-30 (the ticket's named batch; `Rewrite-Reason:` in the commit)

- `test_w1_30_no_acceptance_tests.py` (3 functions × 2 forms): the fixture ticket declares
  `acceptance_tests.path: tests/acceptance/W1-noat-declared/`, which is absent or holds a README only, while
  `tests/acceptance/W1-noat/` holds a passing test it does not declare. Expectations unchanged (refused naming the
  acceptance tests, counted once, a dependent repair ticket). Red today: the close reads the WBS folder and closes.
  Reason: DEC-892 item 1.
- `test_w1_30_close.py::test_collection_error_refuses_close`: the broken regression file is the owner's (outside
  the ticket's work), the acceptance test is a telling test, and the case adds: the refusal names the collection
  error, no test ran, the count is 0. Red today: the refusal is `CHECK_FAILED` without the word "collect" (and the
  tests ran, counted). Reason: DEC-868 item 3.

## Not tested, and why

- Classes the KPIs do not name (`config`, `skill`, `schema`, `template`, `documentation`, `ops`,
  `role-definition`): no test (a package in the return).
- A name clash between two suites that shows only when they are collected in one process: DEC-868 (a) says "in one
  process, as the close runs them", which leaves open whether a clash between the acceptance and regression runs
  (two processes today) must refuse. Not asserted.
- The default floors (100 GiB, 10,000,000 inodes) against the real disk: that depends on the machine.
