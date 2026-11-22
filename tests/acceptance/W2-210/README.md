# W2-210 acceptance tests: the lite adoption verdict stage (`gov adopt --lite --stage VERDICT`, CAP-44.h)

Ticket `DAEO-d3d4` (`.tickets/DAEO-d3d4.md`), profile STANDARD, class implementation. Written by the independent test
designer (MR-3) from the ticket's five success lines (V1 to V5) and two failure lines (F1, F2) and CAP-44.h, before any
implementation, on the base `6becd5748`. Sources read: the ticket, `docs/contract/capabilities/CAP-44.h.md`, the stages
as they stand on `w2/integrate` (`gov.adopt.command`, `stages`, `lite_gates`, `project`), W2-02's
`adoption-verdict.schema.json`, the precedents `tests/acceptance/W2-52/`, `W1-41/`, `W2-81/` (public behaviour and
support only), and the W2-81 analysis (rows R7, VERDICT, A5, D1). No implementation was read (none exists).

Every case is of the acceptance kind, through a public interface: the `gov` command line, a file, an exit code, or the
two functions the ticket names (`gov.adopt.verdict.compute`, `check_record`). Two limits are declared: the cases that
run the real command line take seconds (the live `gov doctor` and `gov check` are real child processes) and the first
case of a run builds the adopted project (about a minute; see "The project"), so the folder is **not** within the
5-second-per-case default of the acceptance kind; it is meant to run in parallel (`-n auto`) through the heavy slot.

## Run

```
T=$(mktemp -d); TMPDIR=$T PYTHONPATH=/home/usain/gov-os-worktrees/E2-d1-verdict/src \
  bash <heavy_slot.sh> python3 -m pytest tests/acceptance/W2-210 -q -p no:cacheprovider -n auto; chmod -R u+w $T; rm -rf $T
```

or `gov accept W2-210`. `src/` of this worktree is first on `sys.path` in `conftest.py` and on every child's
`PYTHONPATH` (`test_the_cases_run_this_worktrees_gov` holds it). No network, no model: the semantic index of the build
goes through W2-52's loopback stand-in endpoint; `sqlite_vec` must be installed (a missing one skips the cases, with the
reason: the lite A10 gate's canary cannot hit without it).

## The project every case copies

W1-41's "harbour" (`build_project`), adopted by W2-52's support through A0, A1, A2, AS, A3, A4, A5, A6, A7 (gate), A8 and
A10 (gate). A3's proposal is W2-52's plus a fourth batch that moves `src/app/core.py` out of the native package layout
**with both grounds** (`justification.materially_better`, `.migration_risk`). The A5, A7 and A10 records are the
Independent Auditor's (committed with `Role: independent-auditor` alone, sessions `auditor-001`, `auditor-007`,
`auditor-010`; the stages ran as `adopter-001`). After A10 one commit adds a closed ticket `HARB-d1aa` and its close
record `docs/close/HARB-d1aa/CL-HARB-d1aa.md` (type `close`, `tests_run: {passed: 3, failed: 0, errors: 0, skipped: 0}`).
It is built **once per pytest run** (a lock file shares it between the xdist workers) and each case copies it (without
`.gov-runtime/`) into its own folder. A second build holds the same adoption whose A3 record's entry for the native file
lost its `justification` before A4 stood on it (the one planted failure a repository cannot get honestly: A3 refuses to
write it); it serves the native-layout case only.

**The live tools on the harbour.** `gov doctor` exits 3 there (`path_compliance` and `framework_lock` fail: the
adoption's records name the moved paths, and the repository has no `framework.lock`) and `gov check` has RED families
(no tool registry, no scan configuration). Making them green on a synthetic repository is not cheap, so:

- the cases that need the tools green call `gov.adopt.verdict.compute(root, session, tools=...)` with stand-ins
  (`w2_210_support.healthy_tools`, `doctor`, `check`); the command line never takes a stand-in
  (`test_the_command_line_takes_no_stand_in_for_a_tool`);
- the cases that run the real command line (`test_w2_210_command.py`, `test_w2_210_owner.py`, some in
  `test_w2_210_record.py` and `test_w2_210_check_record.py`) get the live tools' answer, which on the harbour leaves the
  release, `gov doctor` and (as far as `gov check` goes) `gov check` conditions `not met` and every condition read from
  records and git `met`. **An ADOPTED_HEALTHY verdict with exit 0 through the real command line is therefore not
  testable here** (see "How the lines are read"); ADOPTED_WITH_ACCEPTED_EXCEPTIONS with exit 0 is (the owner's file
  names what the live tools left not met), and ADOPTED_HEALTHY is held through `compute`.

## Interface (fixed here; the engineer follows it)

The ticket fixes: `gov.adopt.verdict` with `compute(root, session, tools=None)`, `stage(run)`, `check_record(root)`;
`VERDICT` in `gov.adopt.command.STAGES` after `A10`; the record `governance/adoption/VERDICT-lite.md`; the owner's file
`governance/project/adoption-exceptions.yaml` (a list of `{condition, decision}`); the refusal codes
`ADOPT_EXCEPTIONS_NOT_OWNERS` and `ADOPT_NOT_ADOPTED`; the record's fields `lite`, `adopted_healthy_conditions`,
`conditions_not_checked`, `auditors`, `produced_by`, `supersedes`, `conditions[].evidence`. What it leaves open is fixed
here, once.

### The command line

`gov adopt --lite --stage VERDICT --json --session <id>`: no other argument; no flag takes a tool's stand-in.

1. **Order.** The stage reads the owner's exceptions file first (before the clean-tree check and before anything is
   computed): a file that is not the owner's is `ADOPT_EXCEPTIONS_NOT_OWNERS`, whatever else is wrong (F2 lists "the
   file modified and not committed", which is also a dirty tree). Then the clean tree, then (when a record is there)
   `check_record` of the record it would replace, then `compute`, then the commit.
2. **Exit and envelope.** ADOPTED_HEALTHY and ADOPTED_WITH_ACCEPTED_EXCEPTIONS: `ok: true`, exit 0, `result = {stage:
   "VERDICT", record: "governance/adoption/VERDICT-lite.md", verdict, conditions}`. NOT_ADOPTED_HEALTHY: the record is
   committed first, then `ADOPT_NOT_ADOPTED` (exit 1, as `GATE_NOT_PASSED`), its message and details naming each
   condition not met by name. Every refusal (`ADOPT_EXCEPTIONS_NOT_OWNERS`, and a `check_record` refusal at a re-run)
   writes nothing: HEAD, the refs, the tree and the working tree as before.
3. **The commit.** One commit, its subject `gov adopt --lite VERDICT: lite adoption verdict` (the cases test the prefix
   `gov adopt --lite VERDICT:`), touching `governance/adoption/VERDICT-lite.md` alone, no `Role` trailer needed. The
   stage run again replaces the record: `supersedes` = a list holding the sha256 of the record it replaces, `[<sha256>]` (`common.schema.json` types it as an array of strings); git keeps the old one.

### `gov.adopt.verdict`

- `compute(root, session, tools=None) -> dict`: `root` a `pathlib.Path`; reads only (no write, no commit, HEAD and the
  tree unchanged); returns the record's frontmatter as the stage would commit it, **without** `produced_by`. A failure of
  a condition is a `not met` state, never an exception; an exceptions file that is not the owner's raises
  `GovError("ADOPT_EXCEPTIONS_NOT_OWNERS")`.
- `tools` (the seam): `None` runs the live tools as child `gov` processes; otherwise a `dict` whose keys `"doctor"` and
  `"check"` each map to a callable `tool(root: pathlib.Path) -> tuple[int, str]`: the exit code and the standard output
  of `gov <tool> --json` run at the repository root. A key absent runs that tool live. The envelopes the stand-ins give
  are the real ones' (`w2_210_support.doctor`, `check`): `gov doctor` at exit 0: `result` holds the parts
  (`result.framework_lock.match`), at exit 3 the parts are in `error.details`; `gov check`: `families` (a mapping
  family -> `{status: GREEN | YELLOW | RED}`) in `result` at exit 0, in `error.details` at exit 3.
- `check_record(root) -> dict | raises`: the committed record's frontmatter when it is a verdict the stage produced; else
  `gov.cli.errors.GovError` with the code below and a message naming the cause.
- `stage(run)`: the stage (sent to as the lite gates are, with no chain).
- `CONDITIONS`: the names below, in this order.

### The condition names (`verdict.CONDITIONS`, and `conditions[].name`)

`A0`, `A1`, `A2`, `A3`, `A4`, `A5`, `A6`, `A8`, `A5 review holds`, `native layout kept`, `lite A7 gate`, `lite A10 gate`,
`release pinned and hash-verified`, `gov doctor green`, `gov check no RED family`, `one ticket closed` (16; the
owner's file names a condition by exactly this text). Each condition has `name`, `source` (a text naming CAP-44, here
`CAP-44.h`), `state` (`met` / `not met` / `accepted`, with `owner_entry` only where accepted) and `evidence`, a mapping
with the three keys `command`, `exit`, `path` (a key that does not apply is null; at least `command` or `path` is a
text; a `command` has an integer `exit`). What each says:

| Condition | `met` when | evidence |
|---|---|---|
| `A0`, `A1`, `A2`, `A3`, `A4`, `A5`, `A6`, `A8` | the stage's record is committed, readable, names its stage, and its `stands_on` is the sha256 of the record before it **as that record now is** (A0: none; A8 stands on A6, A5 on A4). A record before it that is not committed is not compared: it is named once, at its own condition | `path` = the stage's record (`governance/adoption/A<n>-<title>.md`) |
| `A5 review holds` | the auditor's record A5 accepted is still the committed one (its sha256 = the record's `verdict_sha256`), reads `verdict: pass`, and passes the auditor re-read (V4) | `path` = the auditor's record (or A5's) |
| `native layout kept` | no A6 move leaves a native package layout (CAP-44.j) without both grounds (the A3 entry's `justification`) | `path` = A3's or A6's record |
| `lite A7 gate`, `lite A10 gate` | the gate's record is committed, readable, `result: pass`, its `stands_on` is the sha256 of the A6 (A10: A8) record as it now is, and the auditor it names passes the re-read (V4) | `path` = the gate's record (`A7-independent-migration-verification.md`, `A10-independent-memory-verification.md`) |
| `release pinned and hash-verified` | `gov doctor`'s `framework_lock.match` is `MATCH` | `command` `gov doctor ...`, `exit` |
| `gov doctor green` | `gov doctor` exits 0 | `command`, `exit` |
| `gov check no RED family` | `gov check` reports no family with status `RED` (a check that gives no readable families is `not met`) | `command` `gov check ...`, `exit` |
| `one ticket closed` | a ticket in `.tickets/` with `status: closed` whose `docs/close/<ticket>/CL-<ticket>.md` is of `type: close` with `tests_run.failed == 0`, `tests_run.errors == 0`, `tests_run.passed >= 1` | `path` = that close record |

Where the ticket's V1 says "(a missing or unreadable record is `not met` and named, never skipped)": a missing record's
condition stays in the record, `not met`, its `evidence.path` the missing path.

### The record's other fields

`id` (a record id), `type: adoption-verdict`, `status`, `state_class`; `verdict`; `conditions`; `lite: true`;
`adopted_healthy_conditions`: ten mappings `{number: 1..10, name: <text>, wave: "W2" | "W3", lite_part: [<condition
names>]}` (only (3) is `W2`; `lite_part` is `[]` for (2), (7), (8) and (10); it names `release pinned and hash-verified`
for (1), `A3` / `A5 review holds` / `native layout kept` for (3), `lite A7 gate` for (4), `A8` for (5), `lite A10 gate`
for (6) and (9)); `conditions_not_checked`: a list of texts naming `(2)`, `(7)`, `(8)`, `(10)`, `A9`, `A11`, the
certification by `qualification` and a separate `verifier` role; `stands_on`: the sha256 of the A10 record as it now is;
`commit`: the 40-hex commit `compute` ran at (HEAD before the stage's own commit); `auditors`: three mappings `{path,
sha256, commit, session, role}` for the A5, A7 and A10 auditor records (`path` as the stage records them,
`sha256` of the file as it stands, `commit` the commit that last touched it, `session` its `auditor_session`, `role` =
`independent-auditor`); `unused_exceptions`: a list of `{condition, decision}` for each entry of the owner's file that
named a condition that is `met` or does not exist (empty or absent when none); `supersedes`: a list holding the sha256 of
the record it replaces, `[<sha256>]` (an array of strings under `common.schema.json`; absent at a first run); `produced_by`.

### `produced_by` (F1)

The sha256 (lower-case hex) of the record's whole text (frontmatter and body, UTF-8) **with the one line that starts
with `produced_by:` removed** (the line and its newline). The stage writes the field as one frontmatter line
`produced_by: <64 hex>`.

### The owner's exceptions file (V2, F2)

`governance/project/adoption-exceptions.yaml`: a YAML list of `{condition: <a name above>, decision: DEC-n}`. It is read
only when `git log -1 --format=%(trailers:key=Role,valueonly) -- <file>` gives exactly one Role, `owner`, **and** the
working-tree file is the committed one (tracked, unmodified). Otherwise `ADOPT_EXCEPTIONS_NOT_OWNERS` (a file that
does not exist is not an exceptions file: nothing is read, nothing is refused), with the file path and the commit
(at least its first 7 hex digits, where a commit touched it) in the error's message or details. An accepted
condition is `accepted` with `owner_entry` = the entry's `decision`; an entry for a `met` condition or for a name
that is no condition changes nothing and is listed in `unused_exceptions`.

### `check_record(root)` refusals (F1, F2): the codes

| Code | The cause |
|---|---|
| `ADOPT_VERDICT_NOT_PRODUCED` | no `produced_by`, or it is not the digest of the record's text |
| `ADOPT_VERDICT_STALE` | the record's `stands_on` is not the sha256 of the A10 record now committed |
| `ADOPT_VERDICT_NOT_THE_STAGES` | the commit that last touched the record has no subject starting `gov adopt --lite VERDICT:`, or touches more than that record |
| `ADOPT_VERDICT_DISAGREES` | the verdict is not the one its conditions give: ADOPTED_HEALTHY only over conditions all `met`; ADOPTED_WITH_ACCEPTED_EXCEPTIONS only over conditions all `met` or `accepted`, one `accepted` (V2) |

A record whose digest is wrong and whose commit is ordinary is refused with one of them (the cases plant one cause at
a time: the stage's subject for the digest cases, a recomputed digest for the disagreement cases). A missing or
unreadable record is refused as well (any `ADOPT_*` code; no case holds which).

### The judge (V5)

`tests/acceptance/W2-81/w2_81_judge.py` is test code and is changed in this ticket's commit: `built_today()` counts
`VERDICT` when `gov.adopt.command.STAGES` lists it; `read_record(..., "VERDICT")` gives PRESENT only for a well-formed
record (the shape V5 states; the verdict the one `derived_verdict(states)` gives, which is V2's rule); the capability
table and the W2-81 README's `VERDICT` row say built; `w2_81_standin.verdict_conditions` gives the stand-in a
well-formed record; the W2-81 self-tests that asserted VERDICT NOT_BUILT now assert it follows `command.STAGES`.

## The map

The KPI lines are the ticket's: success-1 is V1, ..., success-5 is V5; failure-1 is F1, failure-2 is F2. Counts are
cases; a parametrized case is named by its function (every parameter is a case of that line).

| KPI | Tests | Expected red reason |
|---|---|---|
| success-1 | `test_w2_210_conditions.py::test_the_stage_is_in_the_commands_stage_list_after_a10_and_before_ma`, `test_w2_210_conditions.py::test_the_cases_run_this_worktrees_gov`, `test_w2_210_conditions.py::test_every_condition_is_met_on_the_adopted_project_with_the_tools_stood_in`, `test_w2_210_conditions.py::test_each_condition_gives_its_evidence_the_command_and_exit_or_the_record_and_path`, `test_w2_210_conditions.py::test_one_planted_failure_makes_exactly_its_condition_not_met_and_leaves_the_others` (16), `test_w2_210_conditions.py::test_a_move_out_of_a_native_layout_without_both_grounds_makes_exactly_that_condition_not_met`, `test_w2_210_conditions.py::test_a_missing_record_is_named_never_skipped`, `test_w2_210_conditions.py::test_an_unreadable_record_is_not_met_and_named`, `test_w2_210_conditions.py::test_two_planted_failures_make_exactly_their_two_conditions_not_met`, `test_w2_210_conditions.py::test_compute_reads_only_and_gives_the_same_answer_twice`, `test_w2_210_command.py::test_the_command_line_takes_no_stand_in_for_a_tool`, `test_w2_210_command.py::test_every_condition_a_record_gives_is_met_but_the_live_tools_ones_on_the_harbour`, `test_w2_210_command.py::test_the_live_tools_conditions_name_the_commands_run_and_their_exit_codes`, `test_w2_210_command.py::test_the_same_conditions_come_from_the_stood_in_tools_and_from_the_live_ones`, `test_w2_210_command.py::test_a_planted_a7_failure_through_the_command_line_makes_that_condition_not_met_beside_the_tools_ones`, `test_w2_210_command.py::test_a_planted_removed_stage_record_through_the_command_line_is_named` | `gov.adopt.verdict` does not exist (the helper reports "does not exist"; the code guard `test_the_cases_run_this_worktrees_gov` passes on the base); `gov.adopt.command.STAGES` lacks `VERDICT`, so `gov adopt --lite --stage VERDICT` is argparse's usage error (exit 2, "invalid choice") and `assert_taken` says so |
| success-2 | `test_w2_210_verdict.py::test_a7_not_met_and_no_exceptions_file_gives_not_adopted_healthy`, `test_w2_210_verdict.py::test_the_owners_file_naming_that_condition_gives_adopted_with_accepted_exceptions`, `test_w2_210_verdict.py::test_each_entry_names_its_own_decision`, `test_w2_210_verdict.py::test_with_two_conditions_not_met_and_the_file_naming_one_the_verdict_is_not_adopted_healthy`, `test_w2_210_verdict.py::test_with_two_conditions_not_met_and_the_file_naming_both_the_verdict_has_accepted_exceptions`, `test_w2_210_verdict.py::test_with_every_condition_met_and_an_exceptions_file_the_verdict_is_adopted_healthy`, `test_w2_210_verdict.py::test_an_entry_for_a_met_condition_beside_a_used_one_is_recorded_as_unused`, `test_w2_210_verdict.py::test_no_exceptions_file_leaves_no_unused_entry`, `test_w2_210_verdict.py::test_the_verdict_agrees_with_the_conditions_it_records_for_every_case_above`, `test_w2_210_command.py::test_a_verdict_that_is_not_adopted_healthy_is_committed_and_the_command_exits_non_zero`, `test_w2_210_command.py::test_an_owner_exceptions_file_gives_adopted_with_accepted_exceptions_and_the_command_exits_0`, `test_w2_210_command.py::test_the_stage_run_again_after_the_owners_commit_replaces_the_earlier_record`, `test_w2_210_command.py::test_an_exceptions_file_committed_by_the_owner_for_a_condition_that_is_met_changes_nothing` | as success-1 |
| success-3 | `test_w2_210_record.py::test_the_record_is_of_type_adoption_verdict_and_valid_under_the_schema`, `test_w2_210_record.py::test_gov_rebuild_lists_the_record_among_none_invalid`, `test_w2_210_record.py::test_the_record_names_itself_lite`, `test_w2_210_record.py::test_the_record_gives_the_ten_adopted_healthy_conditions_with_their_markings`, `test_w2_210_record.py::test_the_command_lines_record_gives_the_same_ten`, `test_w2_210_record.py::test_conditions_not_checked_names_what_the_verdict_does_not_check`, `test_w2_210_record.py::test_the_record_stands_on_the_a10_record_and_names_the_commit_it_was_computed_at`, `test_w2_210_record.py::test_the_committed_record_stands_on_a10_and_the_commit_before_its_own`, `test_w2_210_record.py::test_the_committed_record_carries_produced_by_the_digest_of_its_body`, `test_w2_210_record.py::test_the_conditions_say_where_they_come_from` | as success-1 |
| success-4 | `test_w2_210_auditors.py::test_the_record_lists_the_three_auditors`, `test_w2_210_auditors.py::test_the_committed_record_lists_the_three_auditors`, `test_w2_210_auditors.py::test_an_auditor_record_brought_by_a_commit_with_another_role_makes_its_stage_not_met` (12), `test_w2_210_auditors.py::test_an_auditor_commit_that_also_wrote_the_adoptions_folder_makes_its_stage_not_met` (3), `test_w2_210_auditors.py::test_an_auditor_whose_session_is_this_stages_session_makes_its_stage_not_met` (3), `test_w2_210_auditors.py::test_an_auditor_session_that_equals_a_stages_or_is_not_named_makes_its_stage_not_met` (4), `test_w2_210_auditors.py::test_an_a7_auditor_record_by_another_role_gives_not_adopted_through_the_command_line` | as success-1 |
| success-5 | `test_w2_210_judge.py::test_built_today_counts_verdict_built_exactly_when_the_command_lists_it`, `test_w2_210_judge.py::test_built_today_counts_the_verdict_stage_the_command_offers`, `test_w2_210_judge.py::test_the_capability_table_and_the_readme_no_longer_say_the_verdict_is_not_built`, `test_w2_210_judge.py::test_a_well_formed_record_is_present` (5), `test_w2_210_judge.py::test_a_missing_record_is_absent`, `test_w2_210_judge.py::test_a_record_not_well_formed_is_malformed` (16), `test_w2_210_judge.py::test_a_stand_in_adoption_with_a_well_formed_verdict_record_has_no_verdict_reason`, `test_w2_210_judge.py::test_a_stand_in_adoption_without_the_record_has_one_verdict_reason`, `test_w2_210_judge.py::test_a_stand_in_adoption_with_a_malformed_verdict_record_has_one_malformed_reason` (3), `test_w2_210_judge.py::test_a_malformed_record_is_never_read_as_the_verdict_for_the_secret`, `test_w2_210_judge.py::test_the_judge_without_a_built_set_follows_the_command_stage_list` | before the judge change (judge group, measured with `w2_81_judge.py` and the W2-81 README at their base): `built_today()` never counts VERDICT, `read_record` gives PRESENT to a record with `lite: false`, no `conditions_not_checked` or a verdict over conditions that do not give it, and the README row says "no"; after it these pass with no implementation; the two cases that read the real stage list (`test_built_today_counts_the_verdict_stage_the_command_offers`, `test_the_judge_without_a_built_set_follows_the_command_stage_list`) stay red until `VERDICT` is in `command.STAGES` |
| failure-1 | `test_w2_210_check_record.py::test_the_record_the_stage_produced_is_accepted`, `test_w2_210_check_record.py::test_a_copy_with_the_verdict_changed_is_refused_as_not_produced`, `test_w2_210_check_record.py::test_a_copy_with_a_conditions_state_changed_is_refused_as_not_produced`, `test_w2_210_check_record.py::test_a_copy_with_the_digest_removed_is_refused_as_not_produced`, `test_w2_210_check_record.py::test_a_hand_written_record_is_refused_as_not_produced`, `test_w2_210_check_record.py::test_a_record_committed_by_an_ordinary_commit_is_refused_as_not_the_stages`, `test_w2_210_check_record.py::test_a_record_committed_with_other_files_is_refused_as_not_the_stages`, `test_w2_210_check_record.py::test_a_record_written_before_an_a10_record_that_has_since_changed_is_refused_as_stale`, `test_w2_210_check_record.py::test_a_verdict_that_does_not_agree_with_its_conditions_is_refused` (2), `test_w2_210_check_record.py::test_the_stage_replacing_a_record_it_did_not_produce_refuses_and_writes_nothing` | as success-1 |
| failure-2 | `test_w2_210_owner.py::test_an_exceptions_file_not_committed_by_the_owner_alone_is_refused_and_nothing_is_written` (7), `test_w2_210_owner.py::test_a_file_the_owner_committed_and_another_role_changed_since_is_refused`, `test_w2_210_owner.py::test_a_file_the_owner_committed_and_that_is_modified_and_not_committed_is_refused`, `test_w2_210_owner.py::test_a_file_never_committed_is_refused`, `test_w2_210_owner.py::test_an_exceptions_file_committed_by_the_owner_alone_is_read`, `test_w2_210_owner.py::test_an_impossible_record_is_refused_by_check_record_and_malformed_to_the_judge` (2), `test_w2_210_owner.py::test_the_stage_commits_no_impossible_record` | as success-1 |

## Red run (before implementation)

Measured on `6becd5748` with this suite and the judge change (below) on top, using the run line above: **136 cases in 8
files** (conditions 25, command 10, record 10, auditors 25, verdict 9, check_record 11, owner 14, judge 32), **105
failed, 31 passed in 104 s** (xdist, six workers; the two adopted projects are built once each, about 50 s apiece). No
case is red for a reason other than these:

- **42 cases fail with "gov adopt --lite does not take --stage VERDICT"** (`assert_taken`): `gov.adopt.command.STAGES`
  does not list `VERDICT`, so argparse answers `invalid choice: 'VERDICT'` (exit 2, no envelope). These are every case
  that runs the command line (all of `test_w2_210_command.py`; the `cli_plain` and `cli_owner` cases of
  `test_w2_210_record.py`, `test_w2_210_auditors.py`, `test_w2_210_check_record.py` and `test_w2_210_owner.py`, and every
  exceptions-file case of F2). No case can be met by a refusal of an unknown stage:
  `assert_taken` fails on the usage error and on a "not built" answer.
- **59 cases fail with "gov.adopt.verdict does not exist"**: the cases that call `compute` (the conditions, the
  planted failures, the auditors, V2's verdicts, the ten conditions).
- **1 case fails on `STAGES` itself** (`test_the_stage_is_in_the_commands_stage_list_after_a10_and_before_ma`) and **1**
  on the `--tools` argument (`test_the_command_line_takes_no_stand_in_for_a_tool`: argparse stops at the unknown
  stage first).
- **2 cases (V5) fail until `VERDICT` is in `command.STAGES`**, whatever the judge says
  (`test_built_today_counts_the_verdict_stage_the_command_offers`,
  `test_the_judge_without_a_built_set_follows_the_command_stage_list`).
- **31 cases are green and stay green**: `test_the_cases_run_this_worktrees_gov` (the code check) and 30 of the 32
  judge cases, which stand on the judge alone. They are red-first against the judge at its base: with
  `w2_81_judge.py` and the W2-81 README as they were, **23 of the 32 fail and 9 pass** (the 9: the well-formed
  records, the absent record, and the records that were MALFORMED before: a verdict outside the three). The judge
  change is part of this commit (it is test code); W2-81's 377 cases are green with it
  (`python3 -m pytest tests/acceptance/W2-81`, 35 s).

**The cases can be met together.** The planted failures, the restoring commits, the exceptions file's commits, the
records written by hand and the schema check were exercised in the cases' own copies without the stage (every plant
commits cleanly and leaves a clean tree; `restore_by` gives back the original bytes with the last commit's roles as
planted; `gov rebuild` lists no invalid record with the ticket and the close record in the tree; the schema check
accepts a well-formed condition and refuses an `accepted` one without its `owner_entry`). No stand-in of the stage was
written or run.


## Mutation check: how each planted failure is caught

`test_one_planted_failure_makes_exactly_its_condition_not_met_and_leaves_the_others` plants one failure per case in a
copy that is otherwise all `met`, computes with the tools stood in, and asserts the set of `not met` conditions is
exactly the planted one, every other condition keeps its baseline state, the evidence names it, and the verdict is
NOT_ADOPTED_HEALTHY. A mutant of the implementation that skips a condition, merges two, or lets one failure spill into
another is killed by the case for that failure:

| Planted failure | Exactly this condition `not met` | Mutants it kills |
|---|---|---|
| A2's record removed (git rm) | `A2` | a missing record skipped or counted met; a cascade into `A3` |
| A1's record changed (A2 no longer stands on it) | `A2` | `stands_on` not compared; compared against the wrong record |
| the A5 auditor's record changed after A5 | `A5 review holds` | the A5 sha256 not re-read |
| A7 (A10) record `result: fail` | `lite A7 gate` (`lite A10 gate`) | the gate's `result` not read; one gate's check read for both |
| A7 record removed | `lite A7 gate` | a missing gate record skipped |
| A7 (A10) record standing on another A6 (A8) record | `lite A7 gate` (`lite A10 gate`) | the gate's `stands_on` not compared |
| the A3 record's native move without grounds (second build) | `native layout kept` | the native check not made, or only half (one ground) |
| `gov doctor` says DRIFT | `release pinned and hash-verified` | the `framework_lock` part not read apart from the exit code |
| `gov doctor` exits 3 (lock MATCH) | `gov doctor green` | the exit code not read apart from the part |
| a RED family | `gov check no RED family` | RED not read from the families |
| ticket reopened / no ticket / close record with a failed test, a test in error, no test passed | `one ticket closed` | each of the close record's three counts, and the ticket's status |
| auditor record brought by an engineer / orchestrator / no-role / auditor-and-engineer commit (content restored) | the stage's own: `A5 review holds`, `lite A7 gate`, `lite A10 gate` | the Role re-read (each of the three, each role form) |
| auditor commit that also wrote `governance/adoption/` | the stage's own | the "wrote nothing of the adoption's folder" half of the re-read |
| `auditor_session` = this stage's session, = a stage's, or absent | the stage's own | the session re-read, each of its three comparisons |

## How the lines are read, and what could not be tested as worded

- **V1's Verify, "every condition `met`" on a synthetic repository, cannot hold with the live tools**: `gov doctor`
  and `gov check` are not green on a harbour-like repository (above), and no case may make them so cheaply. It holds
  through `compute(..., tools=...)` (the ticket's own seam), and through the real command line for the conditions the
  tools do not decide. **ADOPTED_HEALTHY with exit 0 through the real command line is untested** for the same reason.
  A real green `gov doctor` and `gov check` need a kernel-installed repository with a `framework.lock`; if the CTO wants
  that case, it is a dev-tier case on a real adopted project, not this folder's.
- **A "removed" or "changed" stage record and its successor.** Every record is stood on by the next, so the plants
  that change a record would, under a reading in which "stands on the record before it as that record now is" fails
  when that record is missing, spill into the successor. The README's rule (Interface) fixes: a record before it that is
  not committed is named once, at its own condition; a record that is changed (committed, other bytes) does break the
  successor's `stands_on`. The case plants "removed" on A2 and "does not stand" through A1 changed. **The ticket says
  "exactly that condition"; this reading is the one under which the line is testable. Proposed to the CTO, low risk.**
- **A5.** The ticket lists "the A5 review still holds" and "A5" among the conditions: they are two (`A5`, the stage's
  record standing on A4's; `A5 review holds`, the auditor's record and the A5 sha256). The A5 verdict "changed" plant
  and the A5 auditor's Role and session plants name the second.
- **"`gov doctor` DRIFT" and "`gov doctor` exit 3"** are two conditions in V1 (`release pinned...`, `gov doctor green`).
  On a real doctor a lock DRIFT also exits 3; the stand-ins give each alone (DRIFT at exit 0, exit 3 with MATCH) so the
  conditions are told apart; the engineer reads the part and the exit code independently.
- **F2 and the clean tree.** F2 names a modified, uncommitted exceptions file as refused with
  `ADOPT_EXCEPTIONS_NOT_OWNERS`; every stage's own clean-tree check would say `ADOPT_TREE_NOT_CLEAN` first. The cases hold
  the ticket's code, so the stage reads the file before the tree check (Interface, "Order").
- **`NOT_ADOPTED_HEALTHY` over conditions all `met`** is read as inconsistent by the judge cases (V5: "the verdict agrees
  with the conditions as V2 states": a verdict is the one its conditions give). `check_record`'s F1 cases hold only the
  two inconsistencies F2 names (healthy over a condition not met or accepted; accepted-exceptions over one not
  accepted).
- **`produced_by`** is "a sha256 over the record's body as the stage wrote it (without that field)": fixed above as the
  sha256 of the whole text without the one `produced_by:` line, so that a case can recompute a right digest for the
  disagreement cases and a wrong one for the others. A digest that is not a MAC proves "the stage's bytes", and the
  commit's subject proves "the stage's commit": the two checks are separate cases.
- **Not held** (ambiguous or outside the lines): the exit codes' exact number beyond "a refusal (1, 3 or 4)"; the
  `id` of the record beyond the record-id grammar; what `compute` does with a malformed exceptions file; whether
  `NOT_ADOPTED_HEALTHY` also lists the accepted conditions.
