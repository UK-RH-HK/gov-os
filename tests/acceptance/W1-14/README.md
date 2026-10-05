# W1-14: acceptance tests of the proposal-to-ticket bridge

Ticket `DAEO-w9l3`, profile STANDARD (DEC-221). Written before implementation by the Independent Test Designer
(MR-3). 63 tests in five files.

Run: `python3 -m pytest tests/acceptance/W1-14 -q -p no:cacheprovider`

## Expected red

Before implementation every test fails at setup, in the `built` fixture, with:

`the bridge is not built yet: no module gov.tasks.bridge (gov.tasks.bridge.derive)`

Observed: `63 errors`. Once the module exists, each test fails or passes on its own behaviour.

## KPI lines and their tests

| KPI line | Tests |
|---|---|
| Success 1: tickets derived from a change's `tasks.md` carry kpis, role, allowed_paths, profile and a back-reference to the change **[CAP-31.a]** | `test_w1_14_derive.py` (7). The covers item is `test_a_derived_ticket_carries_the_task_contract_of_its_task`, with `..._names_the_specification_of_its_change` and `..._gives_a_ticket_with_those_inputs` |
| Success 2: derived tickets pass the ticket schema and the DAG is acyclic | `test_w1_14_schema_and_dag.py` (13): schema, `deps`, cycles, dangling edges, the READY rule. `test_w1_14_rerun.py` (3): one ticket per task on a second run |
| Failure 1: a derived ticket lacks KPIs or allowed_paths | `test_w1_14_refusals.py` (23): 11 lacking tasks, whole-derivation refusal, the template as delivered, profile and class, the unclosed specification (MR-2), unreadable changes |
| Failure 2: an implementer ticket's allowed_paths covers `tests/acceptance/**` | `test_w1_14_acceptance_paths.py` (17): 11 spellings, three other roles, the test designer's own task, look-alike paths |

## The interface the tests assume

```
gov.tasks.bridge.derive(root: Path, change: str) -> dict
```

- `change` is the folder name under `openspec/changes/`.
- Returns `{"change": <folder name>, "specification": <record id>, "tickets": [{"task": "1.1", "ticket": "<id>"}, ...]}`,
  one entry per task of `tasks.md`, in file order, tickets that already existed included.
- Refuses with `gov.cli.errors.GovError`, never a raw exception, and then writes nothing at all:
  - `SPEC_NOT_CLOSED`: the specification's status is not `CLOSED`, or it is `CLOSED` with a required row open;
  - `TASKS_INVALID`: a task cannot become a ticket. `details["invalid"]` is a non-empty list of maps, each with
    `"task": "<number>"` (other keys, such as a reason, are free). It names every faulty task and no sound one;
  - any `GovError` code: no such change, no `tasks.md`, no specification record in `proposal.md`.
- Writes only under `.tickets/`, through the project's vendored ticket script, and commits nothing.

Sources: the module name from the ticket's `allowed_paths` (`src/gov/tasks/bridge*`; `gov/tasks/__init__.py` and
`gov/cli/**` are outside them); `GovError` and "refuses and writes nothing" from `gov.readiness.close` (DEC-349);
`SPEC_NOT_CLOSED` from `gov.readiness` and the READY rule. The function name, the argument, the returned keys and
`TASKS_INVALID` are **package DP-1**.

## The task format the tests assume

`tasks.md` keeps W1-12's template: `## <n>. <group>` headings and checkbox lines. A task is:

````
- [ ] 1.2 Implement the export function and verify the export test passes
  ```yaml
  role: engineer
  class: implementation
  profile: STANDARD
  allowed_paths:
  - src/export/**
  kpis:
    success:
    - The export of the sample data equals the expected file
    failure:
    - The export loses a row
  depends_on:
  - '1.1'
  ```
````

- The task is the checkbox line `- [ ] <number> <description>`; `<number>` is `<group>.<n>`.
- Its fields are the one map in the fenced `yaml` block indented two spaces under that line, before the next
  checkbox line or heading. OpenSpec tracks only checkbox lines, so the block does not disturb `openspec apply`.
- `role`, `allowed_paths` (a non-empty list of non-empty strings) and `kpis` (`success`: at least one non-empty
  line; `failure`: a list) are required: a task without one is refused (KPI failure 1; `role` under MR-2 and the
  ticket schema).
- `class` and `profile`: every derived ticket has both (MR-2). The tests accept a refusal or a stated default
  for a task without one (DP-2).
- `depends_on` (optional): strings, each a task number of the same file or the id of a ticket that already exists.
  A YAML number (`- 1.10` unquoted) is refused. `inputs` (optional) is copied to the ticket.
- The derived ticket carries `kpis`, `role`, `allowed_paths`, `profile`, `class` as the task wrote them,
  `specification: <record id>` (DEC-307, DEC-350), `status: open`, `deps: [<ticket ids>]` (the key the READY rule
  reads, W1-09), the task's description in its text, and passes `ticket.schema.json`.

What W1-12's template gives is the number and the description only. The block and its keys are **package DP-2**;
`depends_on` is **package DP-4**. The whole format is written by one function, `w1_14_support.tasks_md`.

## Settled from the sources

- **Back-reference**: the ticket key `specification` holds the record id of the change's `proposal.md` frontmatter
  (DEC-307, DEC-350).
- **Schema**: `template/governance/kernel/schemas/ticket.schema.json` with `common.schema.json` (W1-08), read at
  test time; applied in full when `jsonschema` can be imported, and by hand for the required keys always.
- **DAG**: the `deps` key of every ticket, ticket ids (W1-09 residual: "only `deps` is read").
- **Not closed**: a status other than `CLOSED` gives no tickets, whatever the rows say (MR-2, DEC-307, DEC-349).
- **Who may hold `tests/acceptance/**`**: only `independent-test-designer` (Contract v4, MR-3: "every role but
  the Independent Test Designer", DEC-156). Patterns are read as `gov.guard.decide` reads them.
- **Fixtures** write the specification frontmatter themselves (DEC-350) and never touch this repository (DEC-322).

## Decision packages, and the tests that rest on them

Each was written on its recommended option. The names live in the first block of `w1_14_support.py`.

| Package | Question | Tests that rest on it |
|---|---|---|
| DP-1 | Name, argument, return and error codes of the function | all (through `support`), and `test_derivation_writes_tickets_and_nothing_else_and_commits_nothing` |
| DP-2 | How a task carries its fields; refuse the whole derivation or only the task | all fixtures (`tasks_md`); `test_one_lacking_task_refuses_the_whole_derivation`, `test_one_covering_engineer_task_refuses_the_whole_derivation`, and the "nothing written" half of every refusal test |
| DP-3 | Is a hand-set `CLOSED` trusted | `test_a_specification_closed_by_hand_with_a_required_row_open_gives_no_ticket` |
| DP-4 | How dependencies are written; cycles through existing tickets; dangling edges | `test_a_task_may_depend_on_a_ticket_that_already_exists`, `test_a_cycle_through_tickets_that_already_exist_is_refused`, `test_a_dependency_that_names_nothing_is_refused`, `test_a_task_number_written_as_a_yaml_number_is_refused` |
| DP-5 | What a second run does | `test_w1_14_rerun.py` |

The full packages are in the test designer's return for this ticket.

## Not tested, on purpose

- G-05 (the ticket's source in the archived sources) was not read. No KPI line needed it.
- A task whose box is checked (`- [x]`), a task edited after its ticket was derived, and a task removed from
  `tasks.md`: DP-5 leaves them open.
- A pattern such as `**/*.py`, which matches files under `tests/acceptance/` without naming the folder.
- Whether `role` is checked against a roster, and whether the ticket also records its task number or its change
  folder: the bridge's own business.
- A `gov` command: none is in the ticket's paths or KPIs.
