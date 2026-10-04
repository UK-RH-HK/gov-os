# W1-12 acceptance tests — readiness schema and proposal templates

Ticket `DAEO-lc4q` (W1-12), profile STANDARD. Written by the Independent Test Designer (MR-3, DEC-069) before
implementation. 19 tests: 13 read the delivered files only, 6 run the `openspec` binary and are marked `local_only`.

## Run

```
PATH=$HOME/.nvm/versions/node/v22.23.3/bin:$PATH python3 -m pytest tests/acceptance/W1-12 -q -p no:cacheprovider
```

- OpenSpec 1.13.2 runs under Node v22.23.3, which is not on the default PATH (DEC-202). The suite calls the binary
  by that folder itself, so the prefix is a convention here, not a need.
- A `local_only` test is skipped when the binary is not installed. Nothing is installed by a test.
- Each `local_only` test works in a temporary project: `template/openspec/` copied to `<tmp>/project/openspec/`.
  HOME and the XDG folders are in the temporary directory; telemetry and the update check are switched off
  (`OPENSPEC_TELEMETRY=0`, `DO_NOT_TRACK=1`, `OPENSPEC_NO_UPDATE_CHECK=1`). Nothing runs in the repository and no
  connection is opened.
- Every expected row, state and table entry is read from `docs/contract/readiness-dimensions.yaml` when the test
  runs. No copy of it is in this folder.

## What the implementer delivers

| Path | What |
|---|---|
| `template/openspec/schemas/feature-readiness/schema.yaml` | The fork of OpenSpec's `spec-driven` schema, `name: feature-readiness`. Keeps the artifacts `proposal`, `specs`, `design`, `tasks`; adds one artifact with `readiness` in its id. Carries `dimensions`, `cell_states` and `capability_types` (see "Readings"). |
| `template/openspec/schemas/feature-readiness/templates/<file>` | One template per artifact, at the name the artifact's `template` gives. OpenSpec reads templates only from this folder. |
| `template/governance/kernel/templates/openspec/**` | Not read by any test (decision package DP-3). |

## Red reason (observed 2026-10-04, before implementation)

`12 failed, 7 errors`. Every one carries the same line:

```
template/openspec/schemas/feature-readiness/schema.yaml does not exist: W1-12 has not delivered the forked OpenSpec schema
```

The 7 errors are the tests that use the `schema` or `project` fixture; the fixture fails with that reason, and pytest
reports a fixture failure as an error. No test fails on an error of its own.

The suite was also run against a stand-in deliverable in a scratch folder (not committed): 19 passed with the
readiness record as a Markdown table and as YAML, and each of seven planted defects (a changed row name, a bare
`N/A` state, a changed table entry, a dropped row, a defaulted N/A in either record form, the unforked spec template)
turned the tests of its KPI line red.

## KPI lines and their tests

Files: `rows` = `test_w1_12_rows_and_states.py`, `types` = `test_w1_12_capability_types.py`,
`templates` = `test_w1_12_templates.py`.

| KPI line | Tests |
|---|---|
| **S1** The forked OpenSpec schema carries all 26 rows x 5 states exactly as readiness-dimensions.yaml [CAP-30.a] | `rows`: `test_schema_is_where_openspec_looks_for_it`, `test_fork_keeps_the_base_workflow_and_adds_the_readiness_record`, `test_every_row_is_carried_by_its_id_in_order`, `test_the_five_states_are_carried_exactly`, `test_the_only_not_applicable_state_needs_a_reason`, `test_the_readiness_record_template_lists_every_row`, `test_the_readiness_record_template_fills_no_cell` · `templates`: `test_openspec_accepts_the_forked_schema` |
| **S2** Proposal templates pass `openspec validate --strict` on first use | `templates`: `test_every_artifact_has_its_template_in_the_schema_folder`, `test_the_project_resolves_the_schema_and_its_templates`, `test_a_fresh_change_from_the_templates_passes_validate_strict`, `test_validating_everything_in_the_fresh_project_passes` |
| **S3** The schema carries the capability-type table for STANDARD rows; a change to the taxonomy or to readiness-dimensions.yaml is accepted only with a linked CIT-E record [CAP-30.e] | `types`: `test_the_table_has_the_capability_types_of_the_yaml`, `test_each_capability_type_marks_the_rows_of_the_yaml`, `test_the_table_marks_only_rows_the_schema_carries`, `test_the_schema_states_the_governed_change_rule` |
| **F1** A row name or state differs from readiness-dimensions.yaml | `rows`: `test_every_row_name_is_the_name_in_the_yaml`, `test_the_five_states_are_carried_exactly`, `test_every_row_is_carried_by_its_id_in_order` |
| **F2** A template fails validate --strict | `templates`: `test_first_use_of_the_unforked_templates_fails_validate_strict`, `test_a_template_that_breaks_the_delta_format_fails_validate_strict` |

| Covers id | Tests |
|---|---|
| **CAP-30.a** 26-row checklist, five states, silent N/A invalid, no defaulted N/A | 26 rows: `test_every_row_is_carried_by_its_id_in_order`, `test_every_row_name_is_the_name_in_the_yaml`, `test_the_readiness_record_template_lists_every_row` · five states: `test_the_five_states_are_carried_exactly` · silent N/A invalid: `test_the_only_not_applicable_state_needs_a_reason` · no defaulted N/A: `test_the_readiness_record_template_fills_no_cell` |
| **CAP-30.e** Capability taxonomy for STANDARD rows; extended only through a governed change | the four tests of `types`. The second half is only shown, not enforced (DP-5). |

Key edge cases: order of rows and states; a row carried twice; a table entry that names a row the schema does not
carry; `validate --all --strict`, the form CI runs (DEC-087); the readiness record in either form.

## What was looked up

1. **The forked schema as a file.** The installed package ships no `docs/` folder; its built-in schema, its command
   help and its resolver's own description give the format. A schema is a folder `<project>/openspec/schemas/<name>/`
   with `schema.yaml` (`name`, `version`, `description`, `artifacts` with `id`, `generates`, `description`,
   `template`, `instruction`, `requires`, and `apply`) and `templates/`. Resolution order: project, user
   (`XDG_DATA_HOME`), package. `openspec schema fork spec-driven <name>` makes exactly that folder. The name
   `feature-readiness` is ADR-0002's (product layout). `schema.yaml` may hold other top-level keys: OpenSpec ignores
   them and `openspec schema validate` passes (tried). A product uses the schema with
   `openspec new change <name> --schema feature-readiness`, which writes `schema: feature-readiness` into the
   change's `.openspec.yaml`; or by `schema: feature-readiness` in `openspec/config.yaml` (DP-2).
2. **"Exactly as".** Row number, row key, row name and state names, from the YAML at test time.
3. **Templates and first use.** `openspec new change` creates only `.openspec.yaml`; it copies no template. First
   use is therefore: a fresh change, each artifact's resolved template (`openspec templates --json`) copied
   unchanged to its output path (`openspec status --json`), then `openspec validate <change> --strict`. The output
   `specs/**/*.md` becomes `specs/sample-capability/spec.md`. `validate` reads only the delta specs and
   `.openspec.yaml`; the proposal, design, tasks and readiness files are not parsed by it.
   **The stock `spec.md` template fails this** (tried): `ADDED "<!-- requirement name -->" should contain SHALL or
   MUST`, a warning that `--strict` makes a failure. The fork has to change that template. A change with no spec
   file at all also fails ("at least one delta").
4. **The capability-type table** is `capability_types.extra_rows_for_standard` in the readiness YAML (DEC-085: "a
   fixed capability-type table in `readiness-dimensions.yaml`"). No archived source is needed.
5. **The CIT-E rule.** `gov readiness` (W1-13) and `gov check` (W1-26) come later, and the kernel's `checks/` folder
   is outside this ticket's paths. Here the schema can only state the rule; see DP-5.

## Readings (each is a decision package in the test designer's report)

- **DP-1, shape.** The tests find the data by the YAML's own key names, at any depth of any YAML or JSON document in
  the schema's folder outside `templates/`, each held once: `dimensions` (rows with `n`, `key`, `name`),
  `cell_states` (entries with `state`; the N/A entry with `requires: [reason]`), `capability_types` (with `source`,
  `extension`, `extra_rows_for_standard`).
- **DP-4, record form.** The readiness record template may be a Markdown table (a row is a table line with a cell
  that is the row's key or name; its state is the one cell that is a state name) or YAML/JSON, also as frontmatter (a
  row is a mapping that names the row by `n`, `key` or `name` and has `state`).
- **Fresh cells are MISSING.** Derived, not decided: a cell may not be empty, N/A is never defaulted, PRESENT needs
  evidence, PROVISIONAL needs an answer, BLOCKED needs a named dependency.

## Not tested

- `mandatory`, `mandatory_rows`, `profiles`, `rules` and the `satisfies` flags of the YAML: no KPI line names them.
  W1-13 needs them; its test design should say where it reads them.
- The wording of any template and of the artifact instructions.
- That the installed `openspec` is the pinned 1.13.2 (`gov doctor` checks the pin).
- Anything under `template/governance/kernel/templates/openspec/` (DP-3) and `template/openspec/config.yaml` (DP-2).
- That a change to the YAML or the taxonomy carries a linked CIT-E record (DP-5).
