# W2-02 acceptance tests (DAEO-zflj): record types, core-schema green here, unmeasured types, the `wbs_id` grammar

Written by a fresh independent test designer (MR-3, DEC-136) before the implementation, from the ticket's KPI lines and sources: DEC-441, DEC-446, DEC-447, CAP-44.h, DEC-722, DEC-730, DEC-624, DEC-626, DEC-714, DEC-718, DEC-274, DEC-466, DEC-448. Profile STANDARD (DEC-221): each KPI line's success and failure, and the key edge cases.

## How the suite runs, and the code it runs (DEC-732)

From this worktree's root:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-02/src python3 -m pytest tests/acceptance/W2-02 -q -p no:cacheprovider -rs

- **This worktree's code.** `PYTHONPATH` in the command makes the suite import this worktree's `gov`. Every process a case starts gets the environment of `w2_02_support.env`. That environment sets `PYTHONPATH` to this worktree's `src/`, found from the support file's own place (`SRC`), so the subprocess imports the same `gov`. `test_w2_02_code_under_test.py` checks this: `gov.__file__` in a started process lies under `SRC`.
- **Public interfaces only.**
  - core-schema runs as `gov check` runs it: the command named in `template/governance/kernel/checks/core-schema.yaml` (`python3 -m gov.check.schema`), by `sh -c`, in a project's root. A case reads its output (a JSON list of findings, each with `code` and `path`) and its exit code.
  - The kernel schema folder `template/governance/kernel/schemas/` is read as files.
  - One module fixture runs a real `gov close` through the console entry (`gov.cli.main:main`) to get the close record as this worktree's `gov close` writes it.
  - No case reads `src/`.
- **Nothing is written in this worktree.**
  - Each project is a temporary git repository built from scratch under pytest's `tmp_path`.
  - The kernel's schema files are copied into it one named file at a time. The close fixture also copies the kernel's `tk` (one file) and the W1-43 case copies that report (one file).
  - The cases of KPI line 2 run core-schema in this worktree's root and only read.
- **Deterministic, no network.** 3 to 13 s in all; the real close takes most of it.

## KPI lines → tests, and why each is red today

Red reasons below are what this suite printed at the commit that added it.

### Success 1: the kernel schemas define the four types [AR-1, AR-3, W2-M316, W2-M317, AR-9]

A defined type is one core-schema measures: a well-formed record of it passes, and a record missing what the type requires is refused.

| Test (`test_w2_02_record_types.py`) | Holds | Today |
|---|---|---|
| `test_an_audit_report_in_dec_441_form_passes_core_schema` | A report with `milestone`, `commit`, `pack_sha256` and its `item`/`class`/`evidence` table, at `docs/audit/wave-9/…`, with no `type` key (DEC-441's form has none): no finding, exit 0 | red: `SCHEMA_INVALID_TYPE` ('type' field is missing) |
| `test_one_kernel_schema_states_the_three_verdicts_of_cap_44_h` | Exactly one kernel schema file has a property whose values are exactly `ADOPTED_HEALTHY`, `ADOPTED_WITH_ACCEPTED_EXCEPTIONS` and `NOT_ADOPTED_HEALTHY`, and it states a constant `type` | red: 0 such files |
| `test_each_of_the_three_verdicts_is_a_well_formed_verdict` (3) | A record of that type with each verdict: no finding names the verdict field, and no `SCHEMA_UNKNOWN_TYPE` | red: 0 such files |
| `test_a_verdict_record_without_one_of_the_three_verdicts_is_refused` (4: `ADOPTED`, `pass`, lower case, missing) | A finding on the file names the verdict field; exit ≠ 0 | red: 0 such files |
| `test_one_kernel_schema_is_a_decision_entry_with_id_status_owner_date_and_its_own_span` | Exactly one kernel schema file requires `id`, `status`, `owner`, `date` and a span field (a required field whose name holds `span`), states its type, and gives `id` a grammar that takes `DEC-730` and refuses any text | red: 0 such files |
| `test_the_kernel_has_one_schema_of_the_close_type` | One kernel schema file whose `type` is the constant `close` | red: 0 |
| `test_the_close_record_gov_close_writes_passes_core_schema` | The record a real `gov close` wrote (`docs/close/PROJ-aaaa/CL-PROJ-aaaa.md`), unchanged, in a project with the kernel's schemas: no finding, exit 0 | red: `SCHEMA_UNKNOWN_TYPE` (unknown record type 'close') |
| `test_a_close_record_that_names_no_ticket_is_refused` | The same record without `task`: a finding names `task`; exit ≠ 0 | red: the one finding is `SCHEMA_UNKNOWN_TYPE`, which names no field |

Readings taken:

- **The audit report is found where audit reports lie.** It has no `type` key, and W1-43's report has none either. The cases put it under `docs/audit/<milestone>/`. That is where the repository keeps reports, and where the audit-reproducibility check reads every file with frontmatter as a report (DEC-626).
- **The verdict field and the verdict type are found by content.** The field is the property whose values are exactly the three CAP-44.h verdicts. The type is that schema's constant `type`. The implementer names both.
- **The decision entry's fields are the KPI's words:** `id`, `status`, `owner`, `date`, and a field whose name holds `span`.
- **The close record is the one this worktree's `gov close` writes,** run for real. Its frontmatter at this commit: `id`, `type: close`, `status: ACTIVE`, `state_class: AUTHORITATIVE`, `task`, `created`, `outputs`, `packet_hash`, `inputs`, `requirements_implemented`, `decisions_applied`, `tests_produced`, `tests_run`, `test_runs`, `deviations`, `skill_versions`, `commits`, `governance_share`.
  - No field the close type needs waits for W2-01.
  - `task` is the field the refusal case removes. It names the ticket closed, and W1-30's suite finds a close record by `type: close` and `task`.

### Success 2: core-schema reads the W1-43 report and the exit report as valid, and is green here [F-M13, W2-M301, W2-M309, W2-M310, W2-L243]

| Test (`test_w2_02_green_here.py`) | Holds | Today |
|---|---|---|
| `test_core_schema_reads_the_w1_43_exit_audit_report_as_valid_here` | No finding names `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` in this worktree | red: `SCHEMA_INVALID_TYPE` |
| `test_core_schema_reads_the_w1_43_report_as_valid_in_a_project_of_its_own` | The same file, copied by name to its path in a temporary project: no finding, exit 0 | red: `SCHEMA_INVALID_TYPE` |
| `test_core_schema_reads_the_wave_1_exit_report_as_valid_here` | No finding names `docs/plan/wave-1-exit/EXIT-REPORT.md` | green ("still": it has no frontmatter) |
| `test_the_a5_adoption_verdict_still_validates_here` | W2-M317: no finding names `docs/adoption/adoption-path-map-verdict.md` (type `research`, moved unchanged by DEC-626) | green ("still") |
| `test_core_schema_is_green_on_this_repository` | In this worktree's root: `[]` and exit 0 | red: exit 1, one finding (the W1-43 report) |

The W1-43 report is read as it was committed. It lies outside the ticket's paths.

### Success 3: a type with no schema file is reported unmeasured, not green [W2-M260, W2-L177]

A finding "says unmeasured" when its code or message holds `unmeasured` or `not measured`. Case, `_` and `-` don't count. The finding names the type in `type` or in its message. "Not green" means exit ≠ 0.

| Test (`test_w2_02_unmeasured.py`) | Holds | Today |
|---|---|---|
| `test_a_type_whose_schema_file_is_absent_is_reported_unmeasured_and_not_green[research]` | All kernel schema files except `research.schema.json`, plus one well-formed research record: a finding says research is unmeasured; exit ≠ 0 | red: no finding, exit 0 |
| `…[close]` | The same, leaving out the kernel's close schema, with a close record | red: no kernel schema of type close |
| `test_a_project_with_no_schema_file_at_all_is_not_green` | No schema file at all, plus one research record: a finding says unmeasured; exit ≠ 0 | red: no finding, exit 0 |
| `test_a_type_whose_schema_file_is_present_is_not_reported_unmeasured` | The converse: every schema file and a well-formed research record give no such finding, exit 0 | green; guards against over-reporting |

### Success 4: the `wbs_id` grammar [DEC-730]

The pattern is read from `common.schema.json` `$defs.wbs_id` and applied as a regular expression, as W1-08's and W1-30's suites do. Core-schema does not read a ticket's `wbs_id` today (measured: `W2-15ab` in a ticket gives no finding), so the grammar is tested where its one definition lies.

| Test (`test_w2_02_wbs_grammar.py`) | Holds | Today |
|---|---|---|
| `test_the_wbs_id_grammar_accepts_one_lower_case_letter_suffix` (3: `W2-15a`, `W2-15b`, `W10-123z`) | Accepted | red: `^W[0-9]+-[0-9]{2,}$` refuses each |
| `test_the_wbs_id_grammar_still_refuses_every_other_form` (8: `W2-15ab`, `W2-15A`, `W2-1`, `W2-1a`, `W2-15-a`, `w2-15a`, `W2-15a␠`, `W2-`) | Refused | green ("still") |
| `test_the_ticket_schema_takes_its_wbs_id_grammar_from_the_one_definition` | `ticket.schema.json` refers to the common definition, and no other file in the kernel schema folder or `schemas/` writes a `wbs` pattern of its own | green ("still"); the widening goes in the one place |

`W2-15` (no suffix) is held in neither direction: see package P-1.

### Failure: an audit report missing its milestone or pack hash is invalid [W2-M138]; a record with an unknown type is still `SCHEMA_INVALID_TYPE`

| Test (`test_w2_02_failure.py`) | Holds | Today |
|---|---|---|
| `test_an_audit_report_missing_a_field_of_dec_441_is_refused_on_that_field` (3: `milestone`, `commit`, `pack_sha256`) | A finding on the report names the missing field (in `field` or in its message); exit ≠ 0 | red: the one finding is `SCHEMA_INVALID_TYPE`, which names no such field |
| `test_an_audit_report_missing_both_milestone_and_pack_hash_names_both` | Both are named | red, as above |
| `test_a_record_with_an_unknown_type_is_still_refused` | `type: frobnicate`: a finding on the file with code `SCHEMA_UNKNOWN_TYPE` or `SCHEMA_INVALID_TYPE` (P-4), never "unmeasured"; exit ≠ 0 | green ("still") |
| `test_a_record_whose_type_is_missing_or_no_text_is_still_schema_invalid_type` (2: missing, a list) | A record outside the audit folder: `SCHEMA_INVALID_TYPE` on the file | green ("still"); the audit form's lack of `type` opens no way round it elsewhere |

Notes on these cases:

- A missing field is asked to be named, not just to give some finding. Today the report already gives a finding (`SCHEMA_INVALID_TYPE`), so "some finding" would pass for the wrong reason.
- DEC-441's third field, `commit`, is held the same way. It is part of the form that line 1 asks for.
- The other half of W2-M138 is left to the audit-report validator, not to core-schema: whether the milestone matches the plan and the hash matches the pack.

### DEC-732

`test_w2_02_code_under_test.py::test_the_processes_the_suite_starts_run_this_worktrees_code`: green.

**Totals at the commit that added the suite:** 42 cases. 26 fail, each for the reason given above. 16 pass, each a "still" case, a guard, or the DEC-732 case.

## Packages (proposed decisions; no case holds what they leave open)

**P-1: is `W2-15` (two digits, no suffix) accepted?**
- Question: KPI line 4 lists `W2-15` among the forms "still" refused.
- Why now: the engineer widens the grammar in this ticket.
- Facts that point the other way:
  - DEC-730's own grammar, `^W[0-9]+-[0-9]{2,}[a-z]?$`, accepts it, and DEC-730 calls the change a widening.
  - Every Wave 2 ticket here carries `wbs_id: W2-NN`, this one included.
  - Today's grammar accepts it, so it cannot be "still" refused.
  - `tests/acceptance/W1-08/test_w1_08_id_grammar.py` holds `W1-08` as a real `wbs_id`.
- Options:
  - (a) `W2-15` stays accepted, and the KPI line's list is read as `W2-15ab`, `W2-15A`, `W2-1`. A test of acceptance is added later by the test designer.
  - (b) It is refused, as written. Every ticket's `wbs_id` becomes invalid, and W1-08's acceptance test must be revised.
- Impact: (b) breaks every ticket and the planning tools' ids.
- Reversibility: both are easy to reverse in the schema.
- Cost: (a) one KPI wording fix; (b) renumbering the waves.
- **Recommendation: (a). Confidence: high.**

**P-2: what "the conditions behind them, in the lite form Contract v4.2 states" are.**
- Question: Contract v4.2 is W2-49's, which is still open. This worktree's contract has CAP-44.h in its Wave 3 form: "with the ten ADOPTED_HEALTHY conditions" (Adoption Protocol v3.0 §20). DEC-722 brings in CAP-44.h lite with the A7 and A10 gates. No lite list of conditions exists yet.
- Why now: the verdict type is defined in this ticket.
- Options:
  - (a) W2-02 defines the type with the three verdicts and a conditions field in a form of its own choosing. A test of the conditions is added once W2-49 states them.
  - (b) W2-02 waits for W2-49.
  - (c) The ten conditions of the protocol are taken now.
- Impact: (a) may need a schema change after W2-49; (b) delays Track A's critical path; (c) may contradict the lite form.
- Reversibility: (a) and (c) are reversible as schema changes.
- Cost: low for (a); days for (b).
- **Recommendation: (a). Confidence: medium.**
- The tests hold only the three verdicts, not the conditions. A well-formed verdict record is checked only on its verdict field, never "no finding at all".

**P-3: how a decision entry reaches core-schema.**
- Question: a register entry is a `### DEC-nnn` heading, not a file with frontmatter. W2-03 makes each entry a record of the store. The ticket allows only "the type map" in `src/gov/check/schema.py`.
- Why now: line 1's "a defined type is one the check measures" can't be tested end to end for this type without knowing its record form.
- Options:
  - (a) W2-02 gives the schema only, which the structural case holds. The "measured" side is W2-03's acceptance: the store's record for each entry validates against this schema.
  - (b) core-schema reads the register itself, which goes beyond the type map.
  - (c) Decision entries are also written as files.
- Impact: (b) widens W2-02's paths; (c) duplicates the register.
- Cost: none for (a).
- **Recommendation: (a), with the field names as the KPI words them (`owner`, `date`, and a field holding `span`). Confidence: medium.**

**P-4: which code "a record with an unknown type is still `SCHEMA_INVALID_TYPE`" holds.**
- Today: unknown type → `SCHEMA_UNKNOWN_TYPE`; missing or non-text `type` → `SCHEMA_INVALID_TYPE`.
- Options:
  - (a) "Still" means unchanged: both codes stay as they are, and no earlier test changes.
  - (b) An unknown type becomes `SCHEMA_INVALID_TYPE`. Two earlier acceptance tests must be revised by a test designer:
    - `tests/acceptance/W1-30/test_w1_30_r15_record_types.py::test_a_type_nobody_knows_is_still_an_unknown_type`, which asserts `[(SCHEMA_UNKNOWN_TYPE, type)]`;
    - `tests/acceptance/W1-26/test_w1_26_probe_records.py::test_a_record_of_an_unknown_type_is_still_a_finding`, which asserts `SCHEMA_UNKNOWN_TYPE` in the codes.
- Impact: (b) changes a public finding code.
- Reversibility: easy.
- Cost: (b) two test revisions.
- **Recommendation: (a). Confidence: high.**
- The case here accepts either code and holds "refused, never unmeasured, not green".

## Risks

- **Earlier suites that run core-schema in a project with no schema files.** Once unmeasured types are reported, a case in another suite that expects such a project to be silent may turn red. The suites seen here (W1-26, W1-30 round 15) copy the kernel's schemas into their projects.
- **The close fixture depends on `gov close` succeeding** in a minimal project. W2-01 is changing the close path. If a later close refuses this project, the three close cases fail with the close's own output in the message. That is a fixture failure, not a schema one.
