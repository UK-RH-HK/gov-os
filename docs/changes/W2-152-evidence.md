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
| S5 | `UNTIL_CLOSED <ticket>` for a line of T-0, of the role's own whole template (every role; W2-153 sends it whole as the system prompt) or of `--part` holding "until <ticket>" whose status is `closed` | success-5 6/6; unit `test_refusals_name_each_finding`, `test_until_in_the_whole_role_template_is_checked` |
| S6 | `--run <kind>` appends T-7's "## Your run:" heading with `{RUN_KIND}` filled and that kind's block (to the next `**<kind>**:` line or the first `{STEP:}` line) after the T-0 body | success-6 6/6; unit `test_lead_carries_only_its_run_block` |
| S7 | A line holding a `{STEP:name}` switched off is dropped whole; an on step is its filled `line` | success-7 2/2; unit `test_step_switch_changes_only_its_line` |
| S8 | Refused: `ALLOWED_PATHS_EMPTY`, `KPI_NO_VERIFY`, `DEPENDS_NOT_CLOSED <id>`; `KPI_NO_VERIFY kpis` when `kpis` is missing, not a mapping or has no success line; an unclosed or non-mapping front-matter block, or a ticket that is not UTF-8, is `TICKET_UNREADABLE` alone; warned only: `NON_GOALS_MISSING`, `EST_LOC_OVER <n>` (> 400) | success-8 15/15; unit `test_refusals_name_each_finding`, `test_advisory_items_only_warn`, `test_no_readable_kpi_lines_is_refused`, `test_unreadable_front_matter_is_ticket_unreadable` |
| S9 | Created on or after `ready.new_since`: `READS_MISSING`, `NEEDS_MISSING`, `WAITS_ON_MISSING` (an empty list declares none); every `waits_on` ref must be a ticket or an existing path (`WAITS_ON_UNKNOWN <ref>`); no `ready.new_since` is `READY_NEW_SINCE_MISSING ready.new_since`, one that is not a date `READY_NEW_SINCE_NOT_DATE ready.new_since` | success-9 12/12; unit `test_dependency_fields_from_the_date_on`, `test_no_readable_new_since_is_refused` |
| S10 | `ready: {new_since: "2026-11-10"}` in facts.yaml; the schema requires `ready` and declares `ready.new_since` (string, `format: date` and a date pattern) | success-10 3/3; `gov accept W2-128` 92/92; `python3 -m gov.check.schema` ok (974 records); unit `test_facts_schema_requires_a_date` |
| F1 | Same inputs, same bytes | failure-1 2/2 |
| F2 | Advisory items never refuse; a missing required field always does | failure-2 2/2 |
| F3 | No write; reads only the ticket files, facts.yaml, the kernel templates and the flag files (and the CLI's configuration) | failure-3 3/3; unit `test_command_output_and_refusal` (no file's mtime changes) |

Choices where the ticket leaves a point open (the simplest reading): `{ROLE}` is the role template's front-matter
`role` (a lead's is `orchestrator`, the guard's role for a lead); `{BRANCH}` is `w2/<W2>` (`w2/<W2>-tests` for a test
designer); `{COMMANDS_TABLE}` lists the commands the role's template names; `{DOD_REFS}` is the ticket's `done_when`,
else every facts `dod` id; `{IMPL}` is the ticket's `sources`; a ticket without `created` is not held to the dependency
fields; a `waits_on` string's ref is its first word (`DAEO-x — why`); a ref with no `/` must be a ticket here.

**Fix round (review round 1, `governance/project/orchestration/reviews/w2-152-r1.md`):** F1, F3, F4 and F6 as above;
F5 (DEC-802): a ticket that is not UTF-8 is `TICKET_UNREADABLE` (another such ticket no longer breaks a W2-id lookup),
a `--part`/`--repair` file or template that is not UTF-8 is `GovError("BRIEF_FILE_UNREADABLE")`, and facts.yaml that
is not UTF-8 or not YAML is `GovError("BRIEF_FACTS_UNREADABLE")` (unit `test_unreadable_files_are_named_refusals`).
`gov accept W2-152` 67/67, `gov accept W2-128` 92/92, unit 25/25.
