# W1-13 acceptance tests: `gov readiness`

Ticket `DAEO-w616`, profile FULL (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
110 cases in 9 files: 92 written before implementation, 18 added by the second batch (DEC-136, see below).

```
PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH python3 -m pytest tests/acceptance/W1-13 -q -p no:cacheprovider
```

## How the tests run

- Through public interfaces only: the `gov readiness` command line (W1-07's console-script stand-in), its API-0002
  envelope and exit code; and the public functions `gov.readiness.close` (DP-2), `gov.tasks.ready`,
  `gov.tasks.blocked` (W1-09) and `gov.store.load` (W1-10), each called in a new process.
- Every project is a temporary git repository (DEC-322): its own `.tickets/`, its own copy of the vendored ticket
  script, its own `openspec/` (a copy of `template/openspec/`, as an adopted project holds it) and its own store.
  No test creates a ticket, a record or a file in this repository. The code under test is this worktree's `src/`.
- Before a command or a function runs, the project is committed and `gov.store.load` is run, so the checker may read
  the working tree or the record graph (W1-09 residual "stale store").
- Expected rows come from `docs/contract/readiness-dimensions.yaml` at test time. Records start from W1-12's
  `readiness.yaml` template.
- Deterministic, no network. `openspec` itself is never run.

## Red before implementation

Observed 2026-10-05: `3 failed, 89 errors`.

- The 89 errors stop at the `built` fixture: `gov readiness is not built yet: it returns NOT_IMPLEMENTED`.
- The 3 failures, in `test_w1_13_command.py`: `gov readiness --json` returns `NOT_IMPLEMENTED`; `gov readiness
  --help` does not name `--specification`; an unknown option ends with exit code 1 (`NOT_IMPLEMENTED`), not 2.

Checked once against a throwaway stand-in of about 110 lines under `src/gov/readiness/` in a scratch copy (never
committed): 92 passed. The suite can be passed from the ticket's paths alone.

## Second batch (DEC-136, DEC-137): two behaviours found by the independent probe

Written after the 92 cases went green, by a fresh Independent Test Designer, from two behaviours described by the
orchestrator. Both let a specification with a required row open pass the gate (KPI failure 1). No existing case was
changed; `w1_13_support.py` gained helpers only (`frontmatter`, `proposal_text`, `write_change`, `edit_schema`,
`unreadable`).

Observed 2026-10-05, before the fix: `16 failed, 94 passed`. The 16 are the red cases below; the 94 are the 92
earlier cases and the two controls.

### B1: the bare command does not pass over a change it cannot judge

`test_w1_13_unreadable.py`, 8 cases. `gov readiness` with neither selector judges every specification (DEC-351),
and a specification is the frontmatter of the change's `proposal.md` (DEC-350), which nothing writes yet. Expected
for a change folder under `openspec/changes/` (not `archive/`) that cannot be read as a specification record:
`ok: false`, `READINESS_INVALID`, exit code 1, the change's folder name somewhere in `error`, nothing written.
Every such change is written with W1-12's `readiness.yaml`, 26 rows MISSING.

| Case | Red reason |
|---|---|
| `test_a_proposal_with_no_frontmatter_does_not_pass` (the proposal template as written today) | `ok: true`, exit 0, `specifications: []` |
| `test_a_proposal_that_is_not_of_type_specification_does_not_pass` (no `type`, then `type: note`) | the same |
| `test_a_proposal_with_no_id_does_not_pass` (no `id`, then an empty one) | the same |
| `test_a_proposal_whose_frontmatter_is_not_yaml_does_not_pass` | the same |
| `test_a_change_with_a_readiness_record_and_no_proposal_does_not_pass` | the same |
| `test_one_unreadable_change_beside_a_complete_specification_does_not_pass` | `ok: true`, exit 0, only the complete specification reported |
| `test_a_project_with_no_change_passes` | control, green |
| `test_the_archive_folder_is_not_a_change` | control, green |

The two cases with two forms stop at the first form; the second form of each was run once on its own and is red
for the same reason.

### B2: a weakened project schema does not weaken the gate

`test_w1_13_schema.py`, 10 cases: five edits of the project's own `openspec/schemas/feature-readiness/schema.yaml`,
each judged by the command (`test_a_weakened_schema_does_not_let_a_specification_pass`) and by
`gov.readiness.close` (`test_a_weakened_schema_does_not_let_a_specification_be_closed`). What a profile requires is
DEC-085's and the Contract's, not the project's copy. Expected: the command does not pass (`SPEC_NOT_CLOSED` or
`READINESS_INVALID`, not fixed which) and `closed` is not true; `close` refuses, and the status, `.tickets/` and the
rest of the project stay as they were.

| Id | Schema edit | Specification | Red reason |
|---|---|---|---|
| `row-removed-FULL` | row 7 removed from `dimensions` | FULL, row 7 MISSING | exit 0, `closed: true`; `close` closes and creates an audit ticket |
| `row-removed-spine-opened-at-LITE` | the same | spine declared LITE, row 7 MISSING | the same |
| `only-the-mandatory-rows-FULL` | `dimensions` cut to the ten mandatory rows | FULL, the 16 other rows MISSING | the same |
| `type-emptied-STANDARD` | `backend: []` in the capability-type table | STANDARD `backend`, row 13 MISSING | the same |
| `type-added-STANDARD` | `blockchain: []` added to the table | STANDARD `blockchain`, mandatory rows PRESENT | the same (DEC-350: an unknown type does not pass) |

The control (the schema as the template ships it, a complete specification passes) is the existing
`test_w1_13_report.py::test_a_record_with_every_required_row_satisfied_passes` (5 cases).

### Not fixed by the second batch

- Where the checker takes the Contract's rows and taxonomy from in an adopted project (a temporary project holds
  no `docs/contract/`): the tests only require that the project's own schema cannot lower them.
- Whether an edited schema is itself an error, or is ignored: both `SPEC_NOT_CLOSED` and `READINESS_INVALID` are
  accepted in B2.
- A change folder with neither `proposal.md` nor `readiness.yaml`; a readable specification record with no
  `readiness.yaml`; a readable specification record under `archive/`; `--specification` or `--ticket` beside an
  unreadable change.
- Consequence of B1, for the owner of DEC-350's residual: until the proposal template (W1-12) or the planning
  skill (W1-35) writes the frontmatter, the bare command fails with `READINESS_INVALID` in any project that holds
  a change written from today's template.

## Earlier test revised

`tests/acceptance/W1-07/`: `readiness` joins `BUILT_LATER` in `w1_07_support.py`, with a note in
`test_w1_07_registry.py`. The case `test_a_reserved_command_not_yet_built_returns_not_implemented[readiness]` leaves
the list. Reason: "planned: command implemented" (DEC-190), the same change W1-25 made for `checkpoint`. W1-07's
other cases keep `readiness` (envelope, read-only, configuration) and stay green before and after: 226 passed.

## The interface the tests fix

| What | Value | From |
|---|---|---|
| Module | `src/gov/readiness/command.py`, a read command with no `ACT_PATHS` | DEC-317, `gov.cli.main`, CAP-27 |
| Arguments | `--specification <record id>`, `--ticket <ticket id>` (the ticket's `specification` key); neither: every specification | DP-4; DEC-307 |
| Passes | `ok: true`, exit 0, `result` = the report with `closed: true`, `open: []` | DP-4 |
| Required rows open | `ok: false`, `error.code: SPEC_NOT_CLOSED`, exit 3, `error.details` = the report | DP-4; API-0002 code 3 |
| Record invalid | `ok: false`, `error.code: READINESS_INVALID`, exit 1, `error.details.invalid` = `[{n, ...}]` | DP-4 |
| Report keys | `specification`, `profile` (the one applied: `FULL` for a spine), `closed`, `open` | DP-4 |
| Open row keys | `n`, `key`, `state`, `gap_ticket` (the id, or `UNLINKED`); rows in order 1 to 26 | KPI, DEC-089 |
| Plain form | same exit code; the text names each open row's key and its gap ticket or `UNLINKED` | MR-1 |
| Specification record | `openspec/changes/<change>/proposal.md` frontmatter: `id`, `type: specification`, `status`, `profile`, `spine`, `capability_types`; `readiness.yaml` beside it | DP-3 |
| Closing | `gov.readiness.close(root, specification_id)` returns `{..., "audit_ticket": <id or null>}`; raises `GovError` `SPEC_NOT_CLOSED` or `READINESS_INVALID` and writes nothing | DP-2 |
| Audit ticket | made with `gov.tasks.create`; `role: independent-auditor`, `class: audit`, `status: open`, `state_class`, `allowed_paths`, `kpis`; its title names the specification id | DP-2; W1-09, W1-43's ticket, `ticket.schema.json` |

All of it is named once, in the first block of `w1_13_support.py`.

## The four points

1. **"Blocks OpenSpec apply/archive and ticket READY."**
   - Settled: `gov.cli.main` gives a command its own exit codes and API-0002 defines 3 as "verification failed"; the
     consumers are named by other tickets (W1-26 "runs ... readiness", W1-35 "the change skill refuses to archive",
     DEC-087 CI, W1-40 lefthook). So this ticket's part of apply/archive is the exit code: 0 only when no required
     row is open and the record is valid, judged from the rows and never from the status.
   - Settled: the READY rule is W1-09's and reads the record's status (DEC-307). This ticket's part is that a
     specification with a required row open cannot become `CLOSED` through its closing function, and a complete one
     can; tested end to end through `gov.tasks.ready` and `blocked`.
   - Open: who runs the gate before `openspec apply` and `archive`, and a record set to `CLOSED` by hand (DP-1).
2. **"Closing a specification."**
   - Settled: closing is the record's status becoming `CLOSED` (DEC-307). CAP-27's acceptance line names
     `readiness` among the read commands that leave `git status --porcelain` empty, and `main.py` reserves it as a
     read command, so no form of the command line closes. DEC-088 gives the trigger and the LITE exception.
     `gov.tasks.create` is the public way to create a ticket.
   - Open: the surface that closes, and the audit ticket's fields beyond what the schema requires (DP-2).
3. **"The profile."**
   - Settled: what each profile requires, and that a spine is judged at FULL (DEC-085, the readiness YAML). The
     mandatory set is not in W1-12's schema (W1-12 residual); the tests take expected rows from the contract YAML,
     and the implementation holds DEC-085's ten rows itself or ships them under its own path.
   - Open: where a specification declares its profile, that it is a spine, and its capability types (DP-3).
4. **Output and exit codes.**
   - Settled: the output is what the command prints plus its exit code; 0, 1 and 2 are the command line's.
   - Open: the report's place in the envelope, the error codes and the code 3 (DP-4).

## KPI lines and covers ids

| KPI line | Tests | Red reason |
|---|---|---|
| **Success 1** "Reports every row open for the profile (FULL for spines) and rejects N/A_WITH_REASON with an empty reason" [CAP-30.a, CAP-53.a] | `test_w1_13_report.py` (26), `test_w1_13_na.py` (14) | `NOT_IMPLEMENTED` |
| **Success 2** "Blocks OpenSpec apply/archive and ticket READY while required rows are open" | `test_w1_13_gate.py` (12): six on the exit code, two on READY, four read-only | `NOT_IMPLEMENTED` |
| **Success 3** "Output is identical on repeated runs" | `test_w1_13_determinism.py` (9) | `NOT_IMPLEMENTED` |
| **Success 4** "Lists every required open row with its linked gap ticket id, or UNLINKED (DEC-089)" [CAP-30.b] | `test_w1_13_gap_tickets.py` (8) | `NOT_IMPLEMENTED` |
| **Success 5** "Closing a spine, STANDARD or FULL feature specification creates an audit ticket for a fresh Independent Auditor naming the milestone (DEC-088)" [CAP-47.d] | `test_w1_13_close.py`: `test_closing_marks_the_record_closed_and_creates_one_audit_ticket` (3), `test_the_audit_ticket_is_for_an_independent_auditor_and_names_the_milestone` (3), `..._is_an_open_ticket_nobody_holds`, `..._carries_what_the_ticket_schema_requires`, `test_closing_changes_the_record_and_adds_the_ticket_and_nothing_else`, `test_closing_a_lite_feature_specification_creates_no_audit_ticket` | `NOT_IMPLEMENTED` |
| **Failure 1** "A spec with a required MISSING row is reported closed" | second batch: `test_w1_13_unreadable.py` (8), `test_w1_13_schema.py` (10); `test_w1_13_report.py::test_one_required_missing_row_is_enough` (3), `::test_a_record_marked_closed_by_hand_with_a_required_row_missing_is_not_reported_closed`; `test_w1_13_gate.py::test_the_gate_reads_the_rows_and_not_the_status`; `test_w1_13_close.py::test_a_specification_with_a_required_row_open_is_not_closed` (3) | `NOT_IMPLEMENTED` |
| **Failure 2** "A defaulted N/A passes" | `test_w1_13_na.py`: `test_a_silent_na_on_a_required_row_is_rejected` (7), `..._on_a_row_the_profile_does_not_require_is_rejected` (2), `test_a_record_that_defaults_every_optional_row_to_na_does_not_pass`, `test_a_record_that_drops_a_row_does_not_pass`; `test_w1_13_gate.py::test_the_gate_is_shut_on_an_invalid_record`; `test_w1_13_close.py::test_a_specification_with_a_silent_na_is_not_closed` | `NOT_IMPLEMENTED` |
| **Failure 3** "A spine, STANDARD or FULL specification closes without an audit ticket" | `test_w1_13_close.py`: `test_a_specification_is_not_closed_when_its_audit_ticket_cannot_be_created`, `test_closing_twice_creates_one_audit_ticket`, `test_closing_marks_the_record_closed_and_creates_one_audit_ticket` (3), `test_a_spine_complete_only_for_the_profile_that_opened_it_is_not_closed` | `NOT_IMPLEMENTED` |

| Covers id | Tests |
|---|---|
| CAP-30.a (26 rows, five states, silent N/A invalid, no defaulted N/A) | `test_w1_13_report.py`, `test_w1_13_na.py` |
| CAP-30.b (gaps and linked tickets) | `test_w1_13_gap_tickets.py` |
| CAP-53.a (readiness rows per profile) | `test_w1_13_report.py`: the five profile cases, twice; `test_a_spine_is_judged_and_reported_at_full`; `test_a_standard_specification_holds_only_the_rows_of_its_declared_types` |
| CAP-47.d (audit triggers: spine, STANDARD and FULL closure) | `test_w1_13_close.py` |

MR-1's acceptance line ("`gov readiness` names the open cells") is `test_the_open_cells_of_a_tickets_specification_are_named`
and `test_the_plain_form_names_the_open_cells`. CAP-30's ("test data MISSING at FULL keeps its production tickets
out of READY") is `test_a_ticket_stays_out_of_ready_while_its_specification_has_a_required_row_open`.

## Files and the packages they depend on

| File | Cases | Depends on |
|---|---|---|
| `test_w1_13_command.py` | 5 | DP-4 for the two argument names (1 case); DP-3 for the fixture (2 cases) |
| `test_w1_13_report.py` | 26 | DP-3, DP-4 |
| `test_w1_13_na.py` | 14 | DP-3, DP-4 |
| `test_w1_13_gap_tickets.py` | 8 | DP-3, DP-4 |
| `test_w1_13_determinism.py` | 9 | DP-3, DP-4 (arguments only, except the last two cases) |
| `test_w1_13_gate.py` | 12 | DP-1, DP-3, DP-4; the two READY cases and `complete-spine` also DP-2 |
| `test_w1_13_close.py` | 18 | **DP-2**, DP-3 |
| `test_w1_13_unreadable.py` (second batch, B1) | 8 | DEC-350, DEC-351 |
| `test_w1_13_schema.py` (second batch, B2) | 10 | DEC-085, DEC-349, DEC-350 |

Only two cases are free of every package (the command is built; an unknown option is a usage error): every other
case needs a specification to exist, and where a specification declares its profile is DP-3. Another answer to a
package changes the first block of `w1_13_support.py`, and for DP-2 the two methods `Project.close` and
`Project.specification`.

## Decision packages

Each is tested at its recommended option.

### DP-1: who runs the gate before `openspec apply` and `archive`, and a record closed by hand

- **Question.** The KPI says `gov readiness` "blocks OpenSpec apply/archive". OpenSpec is an external tool, and this
  ticket's paths hold no hook, check declaration or skill. What does W1-13 deliver of that sentence, and who wires
  the rest? And the READY rule (`src/gov/tasks/**`, outside the paths) trusts the record's status: a record set to
  `CLOSED` by hand with a row open lets its tickets through.
- **Why now.** The tests have to say what "blocks" means before the engineer starts.
- **Options.**
  - (a) W1-13 delivers the exit code only (0 passes, 3 open rows, 1 invalid record); W1-26 runs it as a check and
    also fails a `CLOSED` record whose rows are open; W1-35's change skill runs it before apply and archive.
  - (b) As (a), and W1-13 also registers a check declaration under `template/governance/kernel/checks/` (a path
    added to the ticket).
  - (c) The READY rule calls the checker itself: a change in `src/gov/tasks/queue.py`, in a W1-09 follow-up.
- **Impact.** (a) leaves the sentence true only once W1-26 and W1-35 are built; until then nothing stops a person
  who runs `openspec archive` directly. (c) closes the hand-edit gap and makes `gov.tasks` depend on
  `gov.readiness`.
- **Reversibility.** High: (b) and (c) can follow (a) without changing a test here.
- **Cost.** (a) none beyond this ticket. (b) one file and one KPI line. (c) a small ticket plus W1-09 test additions.
- **Recommendation.** (a), with the hand-edit case recorded as a residual for W1-26. **Confidence:** medium-high.

### DP-2: what closes a specification, and the audit ticket's fields

- **Question.** Which surface performs the closing (status to `CLOSED`, DEC-307) and creates the audit ticket?
  CAP-27's acceptance line and `main.py` make `gov readiness` a read command that leaves `git status --porcelain`
  empty, and `src/gov/cli/**` is closed to this ticket. And which fields does the audit ticket carry?
- **Why now.** KPI success 5 and failure 3 cannot be tested without a surface to call.
- **Options.**
  - (a) A public function `gov.readiness.close(root, specification_id)`: it refuses with `SPEC_NOT_CLOSED` or
    `READINESS_INVALID` and writes nothing; otherwise it creates the audit ticket through `gov.tasks.create` (not for
    a LITE feature), then sets the status, in the working tree, uncommitted. A later ticket gives it a command or a
    skill step (W1-35 planning).
  - (b) `gov readiness --close <id>`: the read command gains a writing form. It contradicts CAP-27's line as
    written; the class in `main.py` would have to become `act`, or the contradiction be accepted by decision.
  - (c) Closing is not an act: `gov check` or the planning skill sets the status, and W1-13 only reports
    "closable". KPI success 5 then moves to W1-35.
- **Impact.** (a) keeps CAP-27 and the paths, and leaves no command-line way to close until another ticket adds one.
  (b) is the most direct for a skill and needs an owner decision on CAP-27. (c) removes a KPI line from this ticket.
- **Reversibility.** Medium: 18 cases call the function through one helper; (b) changes that helper, not the
  assertions.
- **Cost.** (a) about 40 lines in the ticket. (b) the same plus a decision and a `main.py` change. (c) a KPI move.
- **Recommendation.** (a). **Confidence:** medium.
- **Fields tested under (a).** `role: independent-auditor` and `class: audit` (as W1-43's ticket), `status: open`,
  `state_class`, and `allowed_paths` and `kpis` because `ticket.schema.json` requires them. "Naming the milestone":
  the title holds the specification's id. Not fixed: the wording, the paths, a `milestone` key, dependencies.
  Closing twice creates one ticket. When the ticket cannot be created, the record is not left `CLOSED`.
  "Fresh" and "authored none of the audited files" (MR-4) are properties of the session that takes the ticket and
  are not testable here.

### DP-3: the specification as a record, and where its profile is declared

- **Question.** DEC-307 says a specification is a record with an id and a status, and that W1-12 to W1-14 "make a
  specification a record". W1-12 delivered no such record, and its `readiness.yaml` has no profile, spine or
  capability-type field (W1-12 residual). Which file is the record, and where are those three declared?
- **Why now.** Every behavioural test needs a specification with a profile.
- **Options.**
  - (a) The change's `proposal.md` carries the frontmatter: `id`, `type: specification`, `status`, `state_class`,
    `profile`, `spine` (boolean), `capability_types` (list). The readiness record is the `readiness.yaml` of the
    same folder. The store already loads it (Markdown with `id`, `type`, `status`), and `openspec validate --strict`
    does not parse the proposal.
  - (b) A separate `specification.md` per change with the same keys.
  - (c) The three keys live in `readiness.yaml` (a change to W1-12's template), and the record file holds only id
    and status.
  - (d) The profile is taken from the tickets that name the specification. Not workable: tickets come after closure
    (MR-2).
- **Impact.** (a) and (b) need W1-12's proposal template, or the planning skill, to write the frontmatter; nothing
  does today. Under every option a specification with no profile does not pass, and a capability type outside the
  taxonomy does not pass (both tested).
- **Reversibility.** High for the tests: `Project.specification` and five constants.
- **Cost.** (a) a template follow-up on W1-12's path. (b) one more artefact in the schema. (c) a W1-12 template
  change and its suite.
- **Recommendation.** (a). **Confidence:** medium.
- **Not settled by any option, and not tested:** two records with the same id, a `CLOSED` specification superseded
  by a draft, a record of another type named by a ticket (W1-09 residual "specification gate edges"); STANDARD with
  no capability type declared.

### DP-4: the output form, the arguments and the exit codes

- **Question.** How is a specification named on the command line, where is the report in the envelope when the
  specification does not pass, and which exit codes and error codes does the command use?
- **Why now.** KPI success 3 compares output, and every test reads the report.
- **Options.**
  - (a) `--specification <id>` and `--ticket <id>`. Passing: `ok: true`, exit 0, the report in `result`. Open rows:
    `GovError` `SPEC_NOT_CLOSED` with exit code 3 and the report in `error.details`. Invalid record:
    `READINESS_INVALID`, exit 1, the rows in `error.details.invalid`. This is W1-25's form (`CHECKPOINT_STALE`,
    exit 3) and fits W1-07's envelope check (`ok: true` only with exit 0).
  - (b) The report always in `result` with `ok: true`, and exit code 3 by the `(result, code)` return of
    `gov.cli.main`. The plain form then prints the report as JSON for free; W1-07's envelope helper refuses
    `ok: true` with a non-zero exit code.
  - (c) Always exit 0 with `closed: false`; a gate reads the JSON. Weak for a hook.
- **Impact.** Under (a) the plain form shows only the error message, so the message itself has to name the open
  rows (tested: each open row's key and its gap ticket or `UNLINKED`).
- **Reversibility.** High: `report_of` already reads the report from either place; (b) changes `held` and
  `rejected` only.
- **Cost.** None beyond the ticket.
- **Recommendation.** (a). **Confidence:** medium-high on the exit codes, medium on the names.
- **Not fixed.** The result of the bare command beyond "an envelope, the same on every run, nothing written"; the
  error code for a specification that does not exist; extra keys in the report.

## Not tested

- Whether a `gap_ticket` id names a ticket that exists, and its class: `gov check` fails an unlinked row (W1-26).
- `gov readiness --generate` (Wave 2, CAP-30.c).
- That the store is fresh: the tests load it before every call (W1-09 residual "stale store").
- Whether a PRESENT row with no evidence is "open" or "invalid": the test only requires that it does not pass.
- Running `openspec apply` or `archive` (DP-1).
