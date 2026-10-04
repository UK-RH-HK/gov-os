# W1-09 — Ticket vendoring, claims and READY rule: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-topz` (W1-09), the Contract v4
items its KPI lines name (CAP-23.a, CAP-31.c, CAP-31.d, CAP-34.e, with the acceptance lines of CAP-23, CAP-31 and
CAP-34), ADR-0002 §3 and §5, the "Rules for every ticket" of the Wave 1 plan, and DEC-069, DEC-074, DEC-116, DEC-133,
DEC-135, DEC-136, DEC-221, DEC-229 and DEC-274 to DEC-278. Written before implementation. Profile FULL. No earlier
ticket's test was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-09 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed. No dev-tier test: no KPI line needs one.

- **Every call runs in a new Python process**, through a small driver written to a temporary directory, with this
  worktree's `src/` on `PYTHONPATH`. A claim is therefore always read by another process than the one that made it.
- **Nothing is written in this worktree.** Every project is a temporary git repository with its own `.tickets/`,
  `.tickets/.claims/` and `tests/acceptance/<id>/` folders.
- **Environment, built from scratch:** a `PATH` without any folder that holds a `tk`, an empty temporary `HOME`,
  `TMPDIR`, locale, `PYTHONPATH`, `PYTHONPYCACHEPREFIX`. The session's `GOV_ROLE` and `GOV_TICKET` are not passed on.
- **The temporary project** holds the vendored script at `governance/kernel/bin/tk`, where an adopted project has it
  (ADR-0002 §5), once `template/governance/kernel/bin/tk` exists. Its tickets are written as this repository's are:
  tk's fields, then the task contract, `deps` in tk ids and `depends_on` in WBS ids, both naming the same tickets.
- **Before the ready queue is read**, the project is committed and `gov.store.load` is run, so the rule may read
  records from the working tree or from the record graph. Claims are never committed.

About 20 seconds when green; the race test takes about 6 of them.

## The public interface

No `gov` command belongs to this ticket. `src/gov/cli/**` is outside its `allowed_paths`, and the registry of W1-07
reserves no claim or ready command (`gov claim` is Wave 3, CAP-23.b). So no `NOT_IMPLEMENTED` case of
`tests/acceptance/W1-07/test_w1_07_registry.py` changes. The tests call one package (package DP-1). The engineer builds
to exactly this:

**`gov.tasks`** (`src/gov/tasks/`)

| Function | Returns |
|---|---|
| `claim(root, ticket, holder)` | Creates the lock `<root>/.tickets/.claims/<ticket>` exclusively (O_EXCL) and writes the holder into it. Returns `{"ticket": <id>, "holder": <holder>}`. |
| `release(root, ticket, holder)` | Removes the lock when `holder` is its holder. Returns `{"ticket": <id>, "holder": <holder>}`. |
| `holder(root, ticket)` | The holder of the ticket's claim, a string, or `None` when nobody holds it. |
| `ready(root)` | A list of ticket ids: the tickets that are READY. |
| `blocked(root)` | A map `ticket id -> list of reason codes`, one entry per ticket that is not closed and not READY, with every reason that holds it. |
| `create(root, title)` | Runs `tk create <title>` of the project's vendored script and adds `state_class: AUTHORITATIVE` to the new ticket's frontmatter. Returns the new ticket's id. |

`root` is a `pathlib.Path`; `ticket`, `holder` and `title` are strings. Every return value is plain JSON data. The
tests sort every list, so order is not part of the interface.

**Errors** are `gov.cli.errors.GovError`, with `details` a map:

| Code | Raised by | When | `details` |
|---|---|---|---|
| `CLAIM_HELD` | `claim` | the lock file already exists | `ticket`, `holder` (the current holder, also named in the message) |
| `CLAIM_NOT_HELD` | `release` | nobody holds the ticket, or another holder does | `ticket`, `holder` (the current holder or `None`) |
| `TICKET_NOT_FOUND` | `claim` | `<root>/.tickets/<ticket>.md` is no ticket, or the id contains a path separator | `ticket` |
| `TICKET_CLOSED` | `claim` | the ticket's `status` is `closed` | `ticket` |

**Reason codes** of `blocked`:

| Code | The ticket is held because |
|---|---|
| `DEPENDENCY_OPEN` | a ticket it depends on (`deps`) is not `closed` |
| `CLAIMED` | its lock file exists, or its `status` is `in_progress` (DEC-116) |
| `NO_ACCEPTANCE_TESTS` | its acceptance tests folder is not a directory: `acceptance_tests.path` of the ticket, or `tests/acceptance/<wbs_id>/`, or `tests/acceptance/<ticket id>/` when it has neither |
| `SPEC_NOT_CLOSED` | it names a `specification` whose record is absent or has a `status` other than `CLOSED` |
| `INPUT_ABSENT` | an id in its `inputs` is the id of no record |
| `INPUT_SUPERSEDED` | a SUPERSEDES edge of the record graph points at an id in its `inputs` |
| `DECISION_OPEN` | a record of type `decision-package` with status `PROPOSED` names it in `constrains` |

A ticket is READY when it is `open` and none of these holds. A closed ticket is in neither answer.

**One point the race test fixes for the engineer.** A process that loses the race must still name the holder, so it
cannot report what it reads between the winner's exclusive creation and the winner's write. A first reference did
exactly that and failed the test. A lock file that stays empty (a session that died while claiming) is still a held
claim; the test of that case does not ask for a holder.

## KPI → tests → red reason today

Red run on `w1/W1-09` at `ee7f0ffb`: **62 errors, 0 passed, 0 failed** (62 cases, 59 test functions). 57 cases error
in the `api` fixture with **`the task interface does not exist: ModuleNotFoundError: No module named 'gov.tasks'`**.
The 5 cases of `test_w1_09_vendoring.py` error in the `vendored` fixture with **`the vendored ticket script does not
exist: template/governance/kernel/bin/tk`**. The last column gives what each group fails on once both exist.

| KPI line | Test file | Test functions | Red reason after the interface exists |
|---|---|---|---|
| **Success 1.** tk v0.3.2 is vendored with sha256 408f2c11... verified by gov doctor | `test_w1_09_vendoring.py` | `test_the_ticket_script_is_vendored_into_the_kernel_template` · `test_the_vendored_script_has_the_pinned_sha256` · `test_the_vendored_script_matches_the_tool_registry` · `test_the_vendored_script_is_executable` · `test_the_vendored_script_works_without_the_installed_one` | No file, or another digest |
| **Success 2.** A second claim on a held ticket fails with the holder named (O_EXCL lock in .tickets/.claims/) **[CAP-23.a]** | `test_w1_09_claims.py` | `test_a_claim_on_a_free_ticket_names_the_ticket_and_its_holder` · `test_a_claim_is_a_lock_file_in_the_claims_folder` · `test_the_holder_of_a_ticket_is_reported` · `test_a_second_claim_on_a_held_ticket_fails_with_the_holder_named` · `test_a_failed_claim_leaves_the_first_claim_as_it_was` · `test_claims_on_different_tickets_do_not_collide` · `test_one_holder_may_hold_several_tickets` · `test_a_lock_file_that_exists_is_a_held_claim_whatever_it_holds` · `test_a_released_ticket_can_be_claimed_again` · `test_a_release_by_another_than_the_holder_fails_and_the_claim_stays` · `test_a_release_of_a_ticket_nobody_holds_fails` · `test_a_claim_on_a_ticket_that_does_not_exist_fails_and_leaves_no_lock` · `test_a_ticket_id_with_a_path_separator_is_no_ticket[4]` · `test_a_closed_ticket_cannot_be_claimed` | No claim, no collision error |
| **Success 3.** The ready queue excludes tickets that are claimed, whose acceptance tests directory is missing, or whose specification is not closed **[CAP-31.c]** | `test_w1_09_ready.py` | By dependency: `test_tickets_with_nothing_in_their_way_are_all_ready` · `test_a_ticket_is_not_ready_before_its_dependencies_are_closed` · `test_closing_a_dependency_makes_the_next_ticket_ready` · `test_a_ticket_with_one_of_two_dependencies_open_is_not_ready` · `test_a_closed_ticket_is_neither_ready_nor_blocked`. Claimed: `test_a_claimed_ticket_is_not_in_the_ready_queue` · `test_a_ticket_in_progress_is_not_in_the_ready_queue` · `test_a_ticket_whose_dependency_is_only_claimed_is_not_ready`. Specification: `test_a_ticket_whose_specification_is_closed_is_ready` · `test_a_ticket_whose_specification_is_not_closed_is_not_ready` · `test_the_ticket_becomes_ready_when_its_specification_closes` · `test_a_specification_that_is_no_record_is_not_closed`. The queue: `test_every_reason_that_holds_a_ticket_is_reported` · `test_every_open_ticket_is_either_ready_or_blocked` · `test_reading_the_queue_changes_nothing_in_the_project`. Acceptance tests folder: see failure 2 | No queue |
| **Success 4.** A ticket whose mandatory input is absent or superseded is not READY **[CAP-31.d]** | `test_w1_09_inputs.py` | `test_a_ticket_whose_mandatory_inputs_are_all_present_is_ready` · `test_a_ticket_whose_mandatory_input_is_absent_is_not_ready` · `test_one_absent_input_among_several_is_enough` · `test_the_ticket_becomes_ready_when_the_absent_input_arrives` · `test_a_ticket_whose_mandatory_input_is_superseded_is_not_ready` · `test_an_input_that_names_its_own_successor_is_superseded` · `test_the_successor_of_a_superseded_input_is_a_good_input` · `test_a_ticket_becomes_not_ready_when_its_input_is_superseded_later` · `test_a_bad_input_holds_only_the_ticket_that_names_it` | Inputs not read |
| **Success 5.** A ticket waiting on an open decision package is blocked, and tickets that do not depend on it stay READY **[CAP-34.e]** | `test_w1_09_decisions.py` | `test_a_ticket_waiting_on_an_open_decision_package_is_blocked` · `test_tickets_that_do_not_depend_on_the_package_stay_ready` · `test_the_ticket_is_ready_again_when_the_package_is_answered` · `test_a_ticket_waiting_on_two_packages_is_blocked_while_one_is_open` · `test_a_ticket_that_depends_on_the_blocked_ticket_waits_for_it_as_for_any_dependency` · `test_an_open_package_that_names_no_ticket_of_the_project_blocks_nothing` · `test_a_record_of_another_type_that_constrains_a_ticket_does_not_block_it` | Packages not read |
| **Failure 1.** Two agents hold the same claim | `test_w1_09_claims.py` | `test_claims_raced_from_separate_processes_give_exactly_one_holder` (8 processes, 4 rounds) · `test_a_second_claim_on_a_held_ticket_fails_with_the_holder_named` · `test_a_failed_claim_leaves_the_first_claim_as_it_was` · `test_a_lock_file_that_exists_is_a_held_claim_whatever_it_holds` · `test_a_release_by_another_than_the_holder_fails_and_the_claim_stays` | No claim |
| **Failure 2.** A ticket without tests/acceptance/<id>/ appears as READY | `test_w1_09_ready.py` | `test_a_ticket_without_its_acceptance_tests_folder_is_not_ready` · `test_the_ticket_becomes_ready_when_its_acceptance_tests_folder_exists` · `test_the_acceptance_tests_of_another_ticket_do_not_count` · `test_a_file_in_place_of_the_acceptance_tests_folder_does_not_count` · `test_the_folder_is_the_one_the_ticket_names` · `test_a_ticket_that_names_no_folder_needs_the_folder_of_its_own_id`; also the last assertion of `test_a_created_ticket_is_the_ticket_the_script_writes` | No queue |
| DEC-229, no KPI line (package DP-7) | `test_w1_09_create.py` | `test_a_created_ticket_carries_state_class` · `test_a_created_ticket_is_the_ticket_the_script_writes` | No `create` |

Covers ids: CAP-23.a (`test_w1_09_claims.py`), CAP-31.c (the dependency tests and the three exclusions of
`test_w1_09_ready.py`), CAP-31.d (`test_w1_09_inputs.py`), CAP-34.e (`test_w1_09_decisions.py`).

**Checked that the suite can go green and catches the failure lines.** The tests were run against a throwaway
reference outside the tracked tree, with a copy of the installed script as the vendored one: 62 passed. With a claim
that checks for the lock and then creates it without O_EXCL, the race test failed. With the acceptance tests folder
ignored, 9 cases failed (the six of failure 2 among them). With an open package blocking every ticket, 3 cases of
`test_w1_09_decisions.py` failed. The reference is not in the repository.

## Described behaviours from review (DEC-136)

| Behaviour | Outcome |
|---|---|
| Two claims on one ticket raced from two separate processes: exactly one holds it, the other fails with the holder named | A test: `test_claims_raced_from_separate_processes_give_exactly_one_holder`. It is failure line 1. |
| A claim on a closed ticket | A test on the recommended option of DP-2: `test_a_closed_ticket_cannot_be_claimed`. **Specification gap:** no source says what a claim on a closed ticket does. |
| A claims folder (`.tickets/.claims`) that is a symbolic link | No test. **Specification gap** (package DP-9): no source says whether claims may live outside the worktree, and a shared claims folder may be what parallel worktrees need. Under DEC-135 it is a residual, not a guard finding: exclusive creation cannot overwrite a file. |
| A ticket id that contains a path separator | A test: `test_a_ticket_id_with_a_path_separator_is_no_ticket[4]`. The ticket id grammar of W1-08 (`common.schema.json`) has no separator, so such an id names no ticket; the test also checks that nothing is written. |

## Readings

1. **The ready queue is by dependency** (CAP-31.c, CAP-31's acceptance line): a ticket is not READY before every
   ticket in its `deps` is `closed`. The fixtures give `deps` (tk ids) and `depends_on` (WBS ids) the same meaning,
   so the tests hold whichever of the two the rule reads (W1-10 residual on WBS ids).
2. **A claim lasts until it is released.** Every call is its own process, so every second claim in the suite is
   against a holder whose process has ended. Nothing expires.
3. **`blocked` gives every reason**, and the tests compare the whole list in the single-cause cases.
4. **Reading the queue writes nothing** in the project outside `.gov-runtime/`.
5. **A ticket created by `tk create`** has none of the task contract's fields. The rule must still read it; it is not
   READY, having no acceptance tests folder.

Not tested: a second claim by the same holder; an empty holder; tk's partial ticket ids in `claim`; an empty
acceptance tests folder; a `deps` entry that names no ticket; whether `claim` also sets `status: in_progress`; whether
a released ticket returns to the queue (it depends on the previous point); a specification or package status other
than those named; `ready` before any `gov.store.load`; a ticket file changed and not committed.

## Decision packages

Each package's affected tests are written on its recommended option. Every other test holds under any option.

### DP-1 — The public interface

- **Question.** Is the Python interface above the one the engineer builds, with no `gov` command in this ticket?
- **Why now.** The tests need an entry point; `src/gov/cli/**` is outside the ticket's paths, and no reserved command
  is a claim or a ready queue.
- **Options.** (a) The six functions of `gov.tasks`; `gov status` (W1-32), `gov check` (W1-26), `gov readiness`
  (W1-13) and the hooks (W1-29) call them. (b) Add `src/gov/cli/**` to the ticket and new commands `gov claim` and
  `gov ready`.
- **Impact.** (b) brings `gov claim` forward from Wave 3 (CAP-23.b, DEC-235) and changes the twelve-command registry
  of CAP-28.b and its W1-07 tests.
- **Reversibility.** High for (a): a command can wrap the functions later. **Cost.** (a) none beyond the ticket.
- **Recommendation.** (a). **Confidence:** high.
- **Tests that depend on it:** all but `test_w1_09_vendoring.py`.

### DP-2 — The claim convention

- **Question.** What is the lock file's name and content, who is the holder, how is a claim released, what happens
  to a claim whose session died, may a closed ticket be claimed, and is `status: in_progress` a claim?
- **Why now.** The KPI fixes only "O_EXCL lock in .tickets/.claims/" and "the holder named". DEC-116 says "claimed
  means `status: in_progress`" for the guard, and DEC-133 has the orchestrator claim with `tk start`.
- **What the sources settle.** The folder; exclusive creation; a collision error that names the holder; the held
  ticket is absent from the ready queue (CAP-23); `gov claim` and the claims role are Wave 3.
- **Options.**
  - (a) The lock is `.tickets/.claims/<ticket id>`, a text file that names the holder. The holder is a string the
    caller gives (by convention `<role>:<session>`); `gov.tasks` does not work it out. `release(root, ticket,
    holder)` removes the lock for its holder only. Nothing expires: a dead session's claim is released by whoever
    names its recorded holder, which in Wave 1 is the main orchestrator (DEC-236). A closed ticket cannot be claimed.
    The ready queue treats a lock file and `status: in_progress` alike as claimed.
  - (b) As (a), but the holder is taken from `GOV_ROLE` and a session id in the environment.
  - (c) As (a), with a time limit after which a claim may be taken over.
  - (d) Only the lock file is a claim; an `in_progress` ticket without a lock stays in the queue, as `tk ready`
    lists it today.
- **Impact.** (b) needs a session id no source defines yet. (c) adds a clock to a lock and a way for two agents to
  hold one ticket, which is failure line 1. (d) puts the six tickets now in progress in this repository into the
  ready queue, because they were claimed with `tk start` and have no lock.
- **Reversibility.** High for the name and the holder; medium once other tickets (W1-28, W1-29) read the lock.
- **Cost.** (a) is the smallest.
- **Recommendation.** (a). **Confidence:** medium-high; medium for the closed ticket and for `in_progress`.
- **Left open inside it:** whether `claim` also sets `status: in_progress` (so that the guard's reading under DEC-116
  and the lock agree) and `release` sets it back; a second claim by the same holder; an empty holder.
- **Tests that depend on it:** `test_a_claim_is_a_lock_file_in_the_claims_folder` (the name),
  `test_a_lock_file_that_exists_is_a_held_claim_whatever_it_holds` (the name), the three release tests,
  `test_a_closed_ticket_cannot_be_claimed`, `test_a_ticket_in_progress_is_not_in_the_ready_queue`,
  `test_a_ticket_whose_dependency_is_only_claimed_is_not_ready`, and the `in_progress` ticket of
  `test_every_open_ticket_is_either_ready_or_blocked`.

### DP-3 — The acceptance tests folder

- **Question.** Which folder must exist, and for which tickets?
- **Why now.** The plan's rule and ADR-0002 say `tests/acceptance/<ticket-id>/`; the KPI says `<id>`; every suite in
  this repository is named by its WBS id; all 50 tickets carry `acceptance_tests.path: tests/acceptance/<WBS id>/`.
  The plan's rule and DEC-069 say "an implementation ticket"; the KPI lines say "tickets".
- **Options.**
  - (a) The folder is the ticket's `acceptance_tests.path` when it has one, else `tests/acceptance/<wbs_id>/`, else
    `tests/acceptance/<ticket id>/`. It must be a directory. The rule holds for every ticket, whatever its class.
  - (b) Always `tests/acceptance/<ticket id>/` with the tk id.
  - (c) As (a), but only for tickets of class `implementation`.
- **Impact.** (b) makes none of this repository's tickets READY. (c) follows the plan's wording, and lets a gap
  ticket of class discovery or test-design (DEC-089) be READY without tests; under (a) such a ticket needs a folder,
  or the planning skill must give it one.
- **Reversibility.** High. **Cost.** Equal.
- **Recommendation.** (a) for the folder, confidence high. For the classes, (a) follows the KPI as written, with
  confidence medium: the question of gap tickets goes to W1-14 and W1-35, which create them.
- **Left open inside it:** an empty folder; DEC-133 claims a ticket before its tests exist, so the claimed ticket is
  out of the queue for two reasons until the tests are written.
- **Tests that depend on it:** `test_the_folder_is_the_one_the_ticket_names`,
  `test_a_ticket_that_names_no_folder_needs_the_folder_of_its_own_id`. No test uses a ticket of another class.

### DP-4 — Where a ticket's specification status is read from

- **Question.** How does the READY rule know that a ticket's specification is not closed?
- **Why now.** KPI success 3. A specification is closed when its readiness contract has every required cell filled
  (Charter MR-1). The readiness schema is W1-12 and `gov readiness` is W1-13, and both come after this ticket; W1-13's
  KPI "blocks … ticket READY while required rows are open" builds on this ticket. No ticket field names a
  specification; W1-14 will give derived tickets "a back-reference to the change".
- **Options.**
  - (a) A ticket names its specification in the frontmatter key `specification`, a record id. The rule reads that
    record's `status` from the record graph: `CLOSED` is closed, anything else or no such record is not. A ticket
    without the key is not held by this input. W1-13 later decides what sets the status.
  - (b) The rule calls a readiness function that W1-13 supplies; until then this input is never true, and the KPI's
    third clause is tested in W1-13.
  - (c) A ticket key `specification_closed: true|false`, written by whoever closes the specification.
  - (d) As (a), and a ticket without a `specification` is never READY.
- **Impact.** (a) needs W1-12 or W1-13 to make a specification a record with a `status` (an OpenSpec change has no
  frontmatter today) and W1-14 to write the key. (b) leaves a KPI clause of this ticket untested here. (c) puts a
  derived fact in the ticket. (d) empties this repository's ready queue: none of the 50 tickets names a specification.
- **Reversibility.** Medium: W1-13 and W1-14 build on the key's name and on the status value.
- **Cost.** (a) a few lines; W1-12 to W1-14 carry the rest.
- **Recommendation.** (a). **Confidence:** medium-low. The key's name and the value `CLOSED` are mine, not a source's.
- **Tests that depend on it:** the four specification tests of `test_w1_09_ready.py`.

### DP-5 — Which ticket field names the mandatory inputs

- **Question.** Where are a ticket's mandatory inputs, and when is one absent or superseded?
- **Why now.** KPI success 4 [CAP-31.d]. CAP-31.a lists "inputs" in the task contract, but the ticket schema and
  template of W1-08 have no such key. `sources` holds ids such as `G-03` and `MR-2` that are no records.
- **Options.**
  - (a) A frontmatter key `inputs`, a list of record ids. Absent: no record of the graph has the id. Superseded: a
    SUPERSEDES edge points at it (DEC-277), whichever side names the link. A ticket without the key has no mandatory
    input.
  - (b) `sources` is the list.
  - (c) `inputs` as a list of maps `{id, version, hash, reason}`, as CAP-15.b asks of the context packet.
- **Impact.** (a) needs `inputs` added to the ticket schema and template (W1-08's files, outside this ticket's
  paths; the schema accepts unknown keys today). Under (b) nearly every ticket of this repository has an absent
  input, since decisions are not records yet (DEC-274). (c) is W1-24's and can extend (a) later.
- **Reversibility.** High. **Cost.** (a) the smallest.
- **Recommendation.** (a). **Confidence:** medium.
- **Tests that depend on it:** all nine of `test_w1_09_inputs.py`.

### DP-6 — Where an open decision package is recorded, and how a ticket waits on it

- **Question.** Before W1-34 and W1-11, what is an open decision package, and what ties a ticket to it?
- **Why now.** KPI success 5 [CAP-34.e]. W1-08 delivered a `decision-package` schema and template (type
  `decision-package`, status `PROPOSED`, no link to a ticket). Packages of this build live in lead summaries and the
  register, not in records.
- **Options.**
  - (a) The package record names the tickets that wait on it in `constrains`, which is already a CONSTRAINS edge of
    the graph (DEC-277). It is open while its status is `PROPOSED`.
  - (b) The ticket names the packages in a new key such as `waits_on`.
  - (c) A new key `blocks` on the package; the store does not carry it, so the rule reads the package files itself.
- **Impact.** (a) needs no ticket edit (leads may not edit `.tickets/`, DEC-236) and no store change. (b) needs a
  ticket edit for every package and its answer. Under each option W1-34 must keep the key and the status value, and
  W1-11 decides what a declined or stale package does (CAP-34.d).
- **Reversibility.** Medium once W1-34's template and skills write the key.
- **Cost.** (a) the smallest.
- **Recommendation.** (a). **Confidence:** medium-low. No source names the key or the status of an answered package;
  the tests use `ACCEPTED` for answered.
- **Tests that depend on it:** all seven of `test_w1_09_decisions.py`.

### DP-7 — DEC-229's duty has no KPI line

- **Question.** DEC-229 says "W1-09 adds the key when a ticket is created". Is `create(root, title)` the way, and
  where does it find the script?
- **Why now.** The vendored script must keep its sha256, so `tk create` itself cannot write `state_class`. No KPI
  line carries the duty.
- **Options.** (a) `gov.tasks.create` runs `<root>/governance/kernel/bin/tk create` and adds the key. (b) Leave it to
  W1-14, whose derived tickets must pass the ticket schema anyway. (c) A wrapper script beside the vendored one.
- **Impact.** Under (a), in this repository the script is at `template/governance/kernel/bin/tk`, not at
  `governance/kernel/bin/tk`, until the kernel is installed here; which of the two `create` uses here is open.
- **Reversibility.** High. **Cost.** About ten lines.
- **Recommendation.** (a), and a KPI line for it on this ticket. **Confidence:** medium.
- **Tests that depend on it:** both of `test_w1_09_create.py`.

### DP-8 — "Verified by gov doctor"

- **Question.** What does this ticket show of "verified by gov doctor"?
- **What the sources settle.** `gov doctor` is W1-27 and is reserved today; W1-27 does not depend on W1-09 and its
  KPI lines name "pinned vs found tool versions", not the vendored copy.
- **Options.** (a) This ticket's tests check the vendored file against the pin (the full digest of ADR-0002 §3 and
  the tool registry's `ticket` entry); the doctor check goes to W1-27's test design as a described behaviour: a
  vendored script with another digest makes doctor fail. (b) This ticket also delivers a function doctor calls.
- **Recommendation.** (a). **Confidence:** medium-high.
- **Tests that depend on it:** none; under (b) tests would be added.

### DP-9 — A claims folder that is a link, and claims across worktrees

- **Question.** Under DEC-235 each ticket has its own worktree, so each has its own `.tickets/.claims/`. Is a claim
  meant to be seen by other worktrees, and may `.tickets/.claims` be a link to a shared folder? Is the folder ignored
  by git?
- **Options.** (a) Wave 1: claims are made only in the main tree by the main orchestrator (DEC-236); the folder is
  not tracked; a linked folder is neither refused nor supported; recorded as a residual. (b) Refuse a claims folder
  that is a link. (c) A shared claims folder for all worktrees.
- **Recommendation.** (a). **Confidence:** medium. Returned as a question; no test depends on it.
