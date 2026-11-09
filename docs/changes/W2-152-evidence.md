# W2-152 evidence: `gov brief` and the ready check (DAEO-o5x1)

Built by a launched engineer session on `w2/W2-152` (base `61231e618`, the designer's cases merged at `a176f5060`,
TESTS-READY `b08ede6890c6`). Code: `src/gov/brief/__init__.py`, `build.py`, `command.py`; facts: `ready.new_since`;
schema: `ready` declared. The acceptance cases were run only through `gov accept W2-152` (DEC-820 (c)).

| KPI | How it is met | Evidence |
|---|---|---|
| S1 | `gov brief <role> <ticket>` prints T-0's body (front matter left out) filled from the ticket, facts.yaml and the kernel templates with `keys.yaml`; no clock, no randomness, sorted reads | `gov accept W2-152` success-1 8/8; unit `test_fills_the_brief_deterministically` |
| S2 | `GovError("BRIEF_NOT_READY")`, `details.findings` each `{code, detail}`: `PLACEHOLDER_LEFT <key>` (a key not in keys.yaml, or a `CMD:`/`STEP:` name not in facts.yaml), `KPI_NO_VERIFY <S|F><n>` | success-2 5/5; unit `test_refusals_name_each_finding` |
| S3 | Warnings and `SIZE <n> of <budget>` (R3 §C's prose measure against `budgets.brief`) on stderr as `gov brief: <CODE> <detail>`; a warning never refuses | success-3 3/3; unit `test_advisory_items_only_warn`, `test_command_output_and_refusal` |
| S4 | `--part` fills `{LEAD_NOTE}`, `--repair` fills `{REPAIR}`, `none` when absent; the role template is read only for its `{CMD:}` names (the commands table) and, for a lead, the one run block | success-4 3/3; unit `test_part_and_repair_fill_their_keys`, `test_lead_carries_only_its_run_block` |
| S5 | `UNTIL_CLOSED <ticket>` for a T-0 line, the lead's run block or a `--part` line holding "until <ticket>" whose status is `closed` | success-5 3/3; unit `test_refusals_name_each_finding` |
| S6 | `--run <kind>` appends T-7's "## Your run:" heading with `{RUN_KIND}` filled and that kind's block (to the next `**<kind>**:` line or the first `{STEP:}` line) after the T-0 body | success-6 6/6; unit `test_lead_carries_only_its_run_block` |
| S7 | A line holding a `{STEP:name}` switched off is dropped whole; an on step is its filled `line` | success-7 2/2; unit `test_step_switch_changes_only_its_line` |
| S8 | Refused: `ALLOWED_PATHS_EMPTY`, `KPI_NO_VERIFY`, `DEPENDS_NOT_CLOSED <id>`; warned only: `NON_GOALS_MISSING`, `EST_LOC_OVER <n>` (> 400) | success-8 10/10; unit `test_refusals_name_each_finding`, `test_advisory_items_only_warn` |
| S9 | Created on or after `ready.new_since`: `READS_MISSING`, `NEEDS_MISSING`, `WAITS_ON_MISSING` (an empty list declares none); every `waits_on` ref must be a ticket or an existing path (`WAITS_ON_UNKNOWN <ref>`) | success-9 9/9; unit `test_dependency_fields_from_the_date_on` |
| S10 | `ready: {new_since: "2026-11-10"}` in facts.yaml; the schema declares `ready.new_since` (string, `format: date` and a date pattern) | success-10 3/3; `gov accept W2-128` 92/92; `python3 -m gov.check.schema` ok (974 records); unit `test_facts_schema_requires_a_date` |
| F1 | Same inputs, same bytes | failure-1 2/2 |
| F2 | Advisory items never refuse; a missing required field always does | failure-2 2/2 |
| F3 | No write; reads only the ticket files, facts.yaml, the kernel templates and the flag files (and the CLI's configuration) | failure-3 3/3; unit `test_command_output_and_refusal` (no file's mtime changes) |

Choices where the ticket leaves a point open (the simplest reading): `{ROLE}` is the role template's front-matter
`role` (a lead's is `orchestrator`, the guard's role for a lead); `{BRANCH}` is `w2/<W2>` (`w2/<W2>-tests` for a test
designer); `{COMMANDS_TABLE}` lists the commands the role's template names; `{DOD_REFS}` is the ticket's `done_when`,
else every facts `dod` id; `{IMPL}` is the ticket's `sources`; a ticket without `created` is not held to the dependency
fields; a `waits_on` string's ref is its first word (`DAEO-x — why`); a ref with no `/` must be a ticket here.
