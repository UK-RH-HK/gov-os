# W1-08 — Record schemas and templates: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-uudf` (W1-08), the Contract v4
items its KPI lines name (CAP-31.a, CAP-53.a, CAP-06.a, CAP-03.a, CAP-03.b, CAP-03.c, CAP-41.a, CAP-50.a, CAP-06.e,
CAP-54.b, CAP-07.b, CAP-41.c, CAP-41.f), ADR-0002 §2, §5 and §6, and DEC-012, DEC-168, DEC-185, DEC-189, DEC-221 and
DEC-224 to DEC-230, DEC-238 and DEC-239. Written before implementation, in two batches: batch 1 left seven decision
packages; batch 2 follows the decisions that settled them. Batch 3 was written after implementation, for DEC-251
and DEC-252 (reason: delegated decision); see "Batch 3" below. No earlier ticket's test was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-08 -q -p no:cacheprovider
```

Standard library, `pytest` and PyYAML (declared in `pyproject.toml`). No network. Nothing is installed.

- **The validator is `check-jsonschema`** (0.38.2, in the tool registry; the stack's validator, ADR-0002 §2). It
  handles `$ref` across files and every draft 2020-12 keyword, which the small validator of the W1-04 and W1-06
  suites does not. Every case that validates is marked `local_only` (155 of 209 cases) and is skipped when the tool
  is absent. Deselect them with `-m "not local_only"`.
- **The good record is the committed one.** For each record type the good record is the frontmatter of the
  committed template; for the path map it is the committed `governance/project/path-map.yaml`. Each bad record is
  the good one with one change. Every refusal test first checks that the unchanged record is accepted, so a schema
  that refuses everything cannot pass. That check is asked of the validator once per run for each record.
- **Files are found by a word in their name**, not by a full name (reading 1). The shared definitions file is found
  by what it defines (reading 11).

About one minute once the schemas exist.

## Batch 3: DEC-251 and DEC-252 (after implementation, reason "delegated decision")

Run on `w1/W1-08` at `4b209505`, the implemented ticket: **9 failed, 200 passed** (209 cases, 71 test functions;
batch 2 had 200 cases in 64 functions). Nine cases are new and one existing case is strengthened. No case was
removed and no assertion of an earlier case was contradicted by the two decisions. The new tests were also run
against a throwaway reference repair outside the tracked tree (all green), and with a defect seeded into one late
system's `where` rule (caught only by the new `where` test).

| KPI line | Decision | Test (cases) | Kind | Result today, and why |
|---|---|---|---|---|
| Success 5 **[CAP-06.e]** | DEC-251 | `test_w1_08_floor.py::test_a_path_map_without_one_of_the_two_capabilities_is_refused[2]` | new | Red: `path-map.schema.json accepts a path map without the capability <name>`; `capabilities` has no `required` |
| Success 5 **[CAP-06.e]** | DEC-251 | `test_w1_08_floor.py::test_a_capability_is_a_closed_map_with_a_boolean_enabled[2]` (accepts `enabled` true and false; refuses no `enabled`, a string, `1`, null, an unknown key, a boolean in place of the map) | new | Red: the schema accepts every bad entry of `research_corpus` (its value is `{}`, anything) and five of six of `code_intelligence` (only "not a map" is refused today) |
| Success 5 **[CAP-06.e]** | DEC-251 | `test_w1_08_floor.py::test_enabled_code_intelligence_lists_its_languages` (accepts two languages; refuses none, an empty list, one string, a number in the list, null) | new | Red: the schema requires the key `languages` and gives it no shape, so four of the five bad values are accepted |
| Success 5 **[CAP-54.b]** | DEC-230 | `test_w1_08_floor.py::test_the_where_rule_holds_for_every_system` (one case, all twenty-two systems: `minimal` with no `where`, and with an empty one, each in one system only) | new, strengthens `test_a_system_is_implemented_or_minimal_with_a_where` | **Green**: every system refers to the one `system` definition, so the rule already holds for all |
| Failure 2 | DEC-252 | `test_w1_08_id_grammar.py::test_the_shared_definition_is_a_grammar[lesson_id]` (now also accepts `L-0074`) | strengthened | Red: `'L-0074' does not match '^LES-[0-9]{3,}$'` |
| Failure 2 | DEC-252 | `test_w1_08_id_grammar.py::test_a_lesson_id_is_the_letter_l_and_four_or_more_digits` (accepts `L-0074`, `L-0000`, `L-12345`; refuses `L-074`, `LES-0074`, `l-0074`, `L0074`, `L-0074a`, `X-L-0074`, `L-00x4`) | new | Red: the shared `lesson_id` is `^LES-[0-9]{3,}$` |
| Success 2a **[CAP-06.a]**, lesson lines 3c, 7, 8 | DEC-252 | `test_w1_08_lesson.py::test_the_lesson_template_carries_an_id_of_the_lesson_form` | new | Red: `lesson.md: id is 'LES-0000', not of the form L-0074` |
| Lesson lines 3c, 7, 8 **[CAP-41.a, CAP-41.c, CAP-41.f]** | DEC-252 | `test_w1_08_lesson.py::test_the_lesson_schema_accepts_the_carried_lesson_id` (accepts `L-0074`, refuses `L-074`) | new | Red: `lesson.schema.json refuses a lesson with id L-0074` |

Once the template's id is `L-0000`, the existing lesson cases (which start from the template) and the three
template cases of success 2a test the new form with no change.

**Helper added.** `Checker.refuses_each` in `w1_08_support.py`: several bad documents in one call of the validator
(`-o json`), each of which must be refused for itself. It keeps the forty-four bad path maps of the `where` test
to one call.

**Readings of batch 3.**

18. **Capabilities** (DEC-251). The good entry is the one of the committed path map. `enabled` must be a JSON
    boolean: a string, `1` and null are refused. An unknown key inside an entry is refused, for both capabilities.
    For enabled code intelligence, `languages` is a list of one or more strings; whether an empty string is a
    language name is not tested. Disabled code intelligence is tested only with a non-empty `languages` (accepted);
    without `languages`, or with an empty list, it is DP-10.
19. **`lesson_id`** (DEC-252) is tested as the pattern the decision gives. A string with a line break is already
    refused by the batch-2 case. That the lesson record's `id` uses `lesson_id` and not another of the five
    grammars is tested only so far as: `L-0074` is accepted and `L-074` is refused.
20. **The `where` rule for every system.** "Identified system" is read as each of the twenty-two: the bad entry is
    `status: minimal` with no `where` (or an empty one), also for a system the committed path map marks absent.

## KPI → tests → red reason before implementation (batch 2)

Red run on `w1/W1-08` at `5203ab3c`: **125 failed, 75 errors, 0 passed** (200 cases, 64 test functions). The errors
are the same assertions, raised in a fixture. Batch 1 had 264 cases in 48 functions: 64 cases fewer, 16 functions
more. The tests fail because nothing is implemented; the suite was run green against a throwaway reference
implementation outside the repository, and red again with defects seeded into it.

| KPI line | Test file | Test functions (cases) | Red reason today |
|---|---|---|---|
| **Success 1.** JSON Schemas exist for MADR decision, ticket (nine fields), lesson, failure, research record, gate/decision package, checkpoint, path map **[CAP-31.a, CAP-53.a]** | `test_w1_08_schemas_exist.py` · `test_w1_08_ticket.py` | `test_a_committed_schema_file_exists_for_the_record_type[8]` · `test_the_schema_is_a_valid_json_schema[8]` · `test_each_record_type_has_its_own_schema_file` · `test_a_committed_shared_definitions_file_exists` · `test_the_shared_definitions_file_is_a_valid_json_schema` · `test_the_ticket_template_carries_the_nine_fields` · `test_the_ticket_schema_defines_the_field[9]` · `test_the_committed_tickets_validate_against_the_ticket_schema` (CAP-31.a) · `test_the_three_profiles_are_accepted_and_no_other` (CAP-53.a) | `no JSON Schema for the <type> record: no file named *.schema.json under template/governance/kernel/schemas/ has one of [...] in its name`; `no shared definitions file: no JSON file under … defines ticket_id, wbs_id, decision_id, lesson_id, record_id`; for the template case, `no record template exists: there is no template/governance/kernel/templates/` |
| **Success 2a.** Every record type has a template that validates against its schema **[CAP-06.a]** | `test_w1_08_templates.py` | `test_a_committed_template_exists_for_the_record_type[7]` · `test_the_template_validates_against_its_schema[7]` · `test_the_template_validates_as_it_is_written[7]` · `test_the_schema_refuses_a_record_that_is_not_a_map[7]` | No templates folder; no schema |
| **Success 2b.** This repository's path map classifies every tracked path **[CAP-06.a]** | `test_w1_08_path_map.py` | `test_this_repository_has_a_committed_path_map_with_namespaces` · `test_the_path_map_validates_against_the_path_map_schema` · `test_the_path_map_validates_as_it_is_written` · `test_every_namespace_lists_its_paths` · `test_every_tracked_path_matches_exactly_one_namespace` · `test_a_namespace_whose_paths_are_not_a_list_of_patterns_is_refused[3]` · `test_the_gov_cli_loads_the_committed_path_map` | `this repository has no path map: governance/project/path-map.yaml does not exist`; no path-map schema |
| **Success 3a.** Each namespace has a sensitivity class, permitted roles, retention, export policy, embedding policy, provenance and deletion/rebuild behaviour **[CAP-03.a, CAP-03.c]** | `test_w1_08_path_map.py` | `test_every_namespace_of_the_path_map_declares_the_field[7]` · `test_a_namespace_without_the_field_is_refused[7]` · `test_a_namespace_that_declares_nothing_is_refused[2]` · `test_a_path_map_that_is_not_a_map_is_refused` | No path map; no path-map schema |
| **Success 3b.** The artefact identity fields of Contract v3 W1 are in the shared frontmatter or derived by gov **[CAP-50.a]** | `test_w1_08_frontmatter.py` | `test_a_record_without_id_type_or_status_is_refused[7]` · `test_the_optional_identity_fields_are_defined_and_optional[7]` · `test_no_template_stores_what_gov_derives[7]` | No templates; no schemas |
| **Success 3c.** Lesson records carry a lifecycle state (candidate → … → approved) **[CAP-41.a]** | `test_w1_08_lesson.py` | `test_the_lesson_template_carries_a_lifecycle_state` · `test_the_six_lifecycle_states_are_accepted_and_no_other` | No lesson template; no lesson schema |
| **Success 4.** Every namespace is governance/development memory or customer/runtime product data, never both **[CAP-03.b]** | `test_w1_08_path_map.py` | `test_every_namespace_is_governance_memory_or_product_data` · `test_each_memory_class_is_accepted` · `test_a_namespace_cannot_be_both_or_neither[4]` | No path map; no path-map schema |
| **Success 5.** The overlay schema carries the project floor; it identifies each constitutional system; no overlay value goes below the kernel floor **[CAP-06.e, CAP-54.b]** | `test_w1_08_floor.py` | Floor keys: `test_a_path_map_without_the_floor_key_is_refused[3]`. Policies and the kernel floor (CAP-06.e): `test_the_path_map_gives_each_of_the_thirteen_policies_a_strength_at_or_above_the_kernel_minimum` · `test_a_path_map_without_one_of_the_thirteen_policies_is_refused` · `test_every_strength_at_or_above_the_kernel_minimum_is_accepted` · `test_a_strength_below_the_kernel_minimum_is_refused[9]` · `test_a_policy_value_that_is_not_a_strength_is_refused[2]`. Capabilities (CAP-06.e): `test_the_path_map_names_no_capability_outside_the_two` · `test_a_capability_outside_the_two_is_refused`. **The shape of a capability entry: batch 3 (DEC-251).** Systems (CAP-54.b): `test_the_path_map_identifies_each_of_the_twenty_two_constitutional_systems` · `test_a_path_map_without_one_of_the_twenty_two_systems_is_refused` · `test_a_system_is_implemented_or_minimal_with_a_where` · `test_an_absent_system_gives_its_reason` · `test_a_system_without_one_of_the_three_statuses_is_refused[2]` | No path map; no path-map schema |
| **Success 6.** The shared frontmatter records `state_class` for every record type **[CAP-07.b]** | `test_w1_08_frontmatter.py` · `test_w1_08_path_map.py` | `test_the_template_records_the_state_class_of_its_record_type[7]` · `test_a_record_without_a_state_class_is_refused[7]` · `test_the_six_state_classes_are_accepted_and_no_other[7]` · `test_the_shared_definitions_file_holds_the_six_state_classes` · `test_the_state_classes_are_written_in_one_schema_file_only` · `test_the_path_map_records_its_state_class` · `test_the_path_map_schema_takes_the_six_state_classes_and_no_other` | No templates; no schemas; no shared definitions file; no path map |
| **Success 7.** Lesson records carry a scope of PROJECT, PRODUCT or FRAMEWORK **[CAP-41.c]** | `test_w1_08_lesson.py` | `test_the_lesson_template_carries_a_scope_and_a_severity_in_lower_case` · `test_each_scope_is_accepted[3]` · `test_a_scope_outside_the_three_is_refused[4]` | No lesson template; no lesson schema |
| **Success 8.** The lesson schema requires both a scope and a severity (low, medium, high, critical), DEC-168 **[CAP-41.f]** | `test_w1_08_lesson.py` | `test_a_lesson_without_the_field_is_refused[2]` · `test_each_severity_is_accepted[4]` · `test_a_severity_outside_the_four_is_refused[4]` | No lesson template; no lesson schema |
| **Failure 1.** A schema accepts a ticket without kpis, role or allowed_paths | `test_w1_08_ticket.py` | `test_a_ticket_without_the_field_is_refused[3]` (left out, and null) · `test_a_ticket_without_kpis_role_and_allowed_paths_is_refused` | No ticket template; no ticket schema |
| **Failure 2.** Two schemas define the same id grammar differently | `test_w1_08_id_grammar.py` | `test_the_five_id_grammars_are_defined_in_one_file_only` · `test_the_shared_definition_is_a_grammar[5]` · `test_no_record_schema_writes_an_id_pattern_of_its_own` · `test_the_id_of_the_record_is_governed_by_the_shared_grammar[7]` | No shared definitions file; no schema |

**Count.** KPI lines with at least one test: 10 of 10 (8 of 8 success, 2 of 2 failure). Covers ids with at least one
test: 13 of 13. CAP-06.e was tested in part until batch 3 (the shape of a capability entry waited for DP-8, now
DEC-251); what is left open is DP-10.

**What batch 2 changed.** Added: the floor (success 5), the memory class and "every tracked path" (success 4, 2b),
the six `state_class` values and the per-type defaults, the path map's `state_class`, the optional identity fields,
the shared definitions file and the id grammar tests that follow DEC-227, the upper-case scope and severity refusals,
and the 48 committed tickets against the ticket schema. Trimmed: cases that repeated one assertion per value or per
field where the KPI asks it once (existence, JSON and git as three cases per schema; three wrong `state_class` values
and four wrong ids per record type; one case per identity field per record type; null as its own case per ticket
field). Removed: the two "same definition name" id tests of batch 1, which DEC-227 replaces. Corrected: the `gov`
launcher of `test_the_gov_cli_loads_the_committed_path_map` was written as `gov.py`, which hides the `gov` package
from the interpreter; it is `run_gov.py` now. That was an error in the batch-1 test, found before implementation.

## Readings the sources do not spell out

1. **File names.** No source names a schema or template file. A schema is a file `*.schema.json` directly under
   `template/governance/kernel/schemas/` (the form of the one existing schema, `tool-registry.schema.json`) whose
   name holds the record type's word: `decision`, `madr` or `adr` (and neither `package` nor `gate`) · `ticket` ·
   `lesson` · `failure` · `research` · `gate` or `package` · `checkpoint` · `path-map`, `path_map` or `pathmap`.
   Exactly one file per type. A template is any file under `template/governance/kernel/templates/` with the same
   word in its name; at least one per type, every one must validate, and the first in name order is the good record.
2. **Format.** A schema is JSON and passes `check-jsonschema --check-metaschema`. The dialect is not asserted. A
   template is a file that opens with YAML frontmatter between two `---` lines (DEC-012; the form of the committed
   tickets and ADRs), or a `.yaml`, `.yml` or `.json` file taken whole. The frontmatter is what validates; the body
   is not checked. A template with Jinja syntax in its frontmatter would fail these tests. A reference from one
   schema to another must resolve from the files alone, with no network (a relative file reference does).
3. **"Every record type has a template"** is read as the seven frontmatter record types. A template for the path
   map is not required: the committed `governance/project/path-map.yaml` is its instance and must validate.
4. **Ticket fields.** "The schema has the field" is tested by behaviour: with the field set to a value of no
   plausible kind (`42` for `class`, `role`, `depends_on`, `allowed_paths`, `kpis`, `sources`, `acceptance_tests`;
   `"many"` for `est_loc`; `"HUGE"` for `profile`) the ticket is refused. Only `kpis`, `role` and `allowed_paths`
   are tested as required (failure 1). A null in their place is refused too. The values of `class` and `role`, the
   inner shape of `kpis` and of `acceptance_tests`, and whether the other six fields are required, are not tested.
5. **The committed tickets are valid tickets.** DEC-229 took option (a) of batch 1's DP-4: tickets carry
   `state_class`, the 48 committed ones were edited (commit `c7aba533`), and `type` stays `tk`'s own field. So the
   ticket schema must accept every committed ticket as it is, with `tk`'s fields (`deps`, `links`, `created`,
   `priority`, `assignee`, `external-ref`, `tags`, `type: task`) and this repository's ids.
6. **CAP-53.a** on this ticket is the `profile` field: `LITE`, `STANDARD` and `FULL` are accepted; another word,
   and the lower-case `standard`, are refused. Readiness rows per profile belong to W1-13.
7. **Scope and severity** are fields named `scope` and `severity`, stored in lower case; the upper-case forms are
   refused (DEC-226).
8. **The lifecycle field** of a lesson. DEC-239 names an optional shared key `lifecycle`, and no source says
   whether the lesson's six-state field is that key or `status`. It is found in the lesson template as the field
   (other than `scope` and `severity`) whose value is one of the six states. That field must take each of the six,
   refuse another word, and be required. States beyond the six (CAP-41.a also has "report" and "versioned") are
   allowed.
9. **Shared frontmatter** is tested by behaviour on each of the seven record types (DEC-239). `id`, `type` and
   `status` are in the template and the schema refuses the record without each. The six optional keys are known
   to the schema (a boolean in their place is refused: no reading makes any of them a boolean) and none is required
   (the template without them is accepted; the lesson keeps its lifecycle field). Their value shapes are not
   tested. No template stores `content_hash`, `canonical_path` or `path` at the top level; whether a schema refuses
   a record that stores them is not tested. How the schemas share the frontmatter is free.
10. **`state_class`** (DEC-229). Every record schema requires it, accepts each of the six values and refuses another
    word, the lower-case form and null. Each template carries its type's default. The shared definitions file
    defines the values under the name `state_class`, and no schema of a record type writes two or more of the six
    values again (one value, as a `default`, is not a list). The path map carries `state_class: AUTHORITATIVE` at
    its top level and its schema requires the key. Whether the path map also carries `id`, `type` and `status` is
    not tested.
11. **The shared definitions file** (DEC-227) is the one `*.json` file directly under the kernel schemas folder
    whose `$defs` (or `definitions`) holds all five names `ticket_id`, `wbs_id`, `decision_id`, `lesson_id`,
    `record_id`. Its file name is free. No other file of that folder defines one of the five names.
12. **Id grammar, the part tested.** The patterns are the engineer's (batch 1's DP-6, option (a)). Each of the five
    definitions refuses the empty string, a string with a line break, a number and `w1-08 probe: not an id!`;
    `ticket_id` accepts `DAEO-uudf` and `wbs_id` accepts `W1-08`. In the eight schemas, no property or definition
    that holds an id (`id`, a name ending in `_id` or `_ids`, `supersedes`, `superseded_by`, `depends_on`, `deps`)
    has a `pattern` below it. Every record schema refuses `w1-08 probe: not an id!` as an `id`, and accepts it in a
    copy of the schemas folder whose five shared grammars are loosened to "any string": that is what "the record
    schemas refer to it" means in behaviour. Which of the five a record type's `id` uses is free.
13. **Path map: namespaces.** `namespaces` maps a name to a map (DEC-189). `paths` is a non-empty list of patterns:
    `**` crosses folders, `*` stays inside one folder, every other character stands for itself (the language of
    ticket `allowed_paths`, DEC-225). Every name of `git ls-files` matches a pattern of exactly one namespace; no
    tracked file is opened. `memory_class` is the string `governance` or `product`; a list of both, another word
    and a missing key are refused. Each of the seven fields of Framework §16 is found by the KPI's word in a key
    name, at any depth inside the namespace: `sensitiv` · `role` · `retention` or `retain` · `export` · `embed` ·
    `provenance` · `delet` or `rebuild`. Removing a field from the first namespace (in name order) must make the
    path map invalid.
14. **Path map: the floor** (DEC-224, DEC-230, DEC-238). `capabilities`, `policies` and `systems` are required
    top-level keys. `policies` maps each of the thirteen keys to one strength, a string; every strength at or above
    the key's kernel minimum is accepted, every strength below it and `off` are refused, and each key is required.
    `systems` maps each of the twenty-two names to a map; each name is required. `where` is tested with the value
    the committed path map gives it: a system that is `implemented` or `minimal` is refused without `where` and with
    an empty one; an `absent` system is accepted with a `reason` and refused without. Whether an extra policy or
    system key is refused, and whether an absent system may carry `where`, are not tested.
15. **Capabilities.** `capabilities` is a map (batch 1's DP-1 option (a), which DEC-224 took) whose keys are among
    `code_intelligence` and `research_corpus`; a third key is refused. The value of an entry was DP-8, settled by
    DEC-251: reading 18.
16. **The committed path map must load in `gov`** (DEC-185, DEC-228): `gov status --json --root <a folder holding
    only that file>` ends with exit code 0 and no `CONFIG_INVALID`. The loader in `src/gov/config/` keeps the
    minimal shape and leaves the new keys alone.
17. **"Committed"** means listed by `git ls-files`.

## Not tested, and why

- **Disabled code intelligence without `languages`, or with an empty list**: DP-10.
- **The id patterns themselves**, beyond `lesson_id` (DEC-252) and the two other ids this repository already uses:
  they are the engineer's (DEC-227).
- **The value shapes of the six optional identity fields**: DEC-239 names the keys only.
- **That `gov` derives the canonical path and `content_hash`**: W1-08 changes no code; W1-10 builds the store.
- **That `gov` refuses a path map the real schema refuses**: W1-27 (DEC-228).
- **The fields of the decision, failure, research, gate and checkpoint records** beyond the shared frontmatter: the
  KPIs name none. DEC-012 lists the decision record's keys (`depends_on`, `implements`, `constrains`) with status
  PROPOSED and no KPI repeats them; W1-11 and W1-34 use them.

## W1-07 revisions (DEC-189, DEC-228)

**None made, and none needed.** W1-08 does not change `src/gov/config/` (DEC-228). The one key the minimal loader
checks, `namespaces` (required, a name mapped to a map), keeps its name and its shape under DEC-225 and DEC-230; the
loader leaves the new top-level keys alone. Every case of `tests/acceptance/W1-07/test_w1_07_config_details.py`
stays valid as written (the W1-07 suite passes on this branch: 228 cases). W1-27 (`DAEO-xw3k`) replaces the minimal
schema, and its test design revises the cases that use `namespaces: {core: {}}`.

## The decisions that settled batch 1's packages

| Package | Question | Decision | What the tests now assert |
|---|---|---|---|
| DP-1 | What is the overlay schema; the floor, the systems, the kernel floor? | **DEC-224** (owner): the floor lives in `path-map.yaml`, under top-level keys of the path-map schema. **DEC-230**: `capabilities`, `policies`, `systems`; strengths `informational` < `warning` < `hard-block`; thirteen required policy keys, each given only the strengths at or above its kernel minimum; twenty-two required systems with `status`, `where`, `reason`. **DEC-238** (owner): the kernel minimum per policy; `capabilities` closed to `code_intelligence` (with `languages`) and `research_corpus`. | `test_w1_08_floor.py`, readings 14 and 15 |
| DP-2 | How does a namespace name its paths, and its memory class? | **DEC-225** (owner): `paths`, patterns in the language of ticket `allowed_paths`; every tracked path matches exactly one namespace; `memory_class` is `governance` or `product`. | Success 2b and success 4, reading 13 |
| DP-3 | The key names of the identity fields | **DEC-239** (owner): `id`, `type`, `status` required; `lifecycle`, `version`, `provenance`, `supersedes`, `superseded_by`, `consumers` optional; canonical path and `content_hash` derived by `gov`. The KPI line was reworded (`ac7f4958`). | Success 3b, reading 9 |
| DP-4 | The values of `state_class`, and the 48 tickets | **DEC-229**: six values, held once in the shared definitions file; every record schema accepts all six; per-type defaults in the templates; the tickets carry it (`c7aba533`). | Success 6, readings 5 and 10 |
| DP-5 | Letter case of scope and severity | **DEC-226**: lower case; the upper-case forms are refused. | Success 7 and 8, reading 7 |
| DP-6 | Which id grammars do two schemas share? | **DEC-227**: one shared definitions file holds the five grammars under fixed names; no other schema writes an id `pattern`; the record schemas refer to it. | Failure 2, readings 11 and 12 |
| DP-7 | Who replaces the minimal path-map schema? | **DEC-228**: W1-27. W1-08 does not change `src/gov/config/`, and its path map must still load there. | Reading 16; no W1-07 revision |

| DP-8 | The value of a capability entry | **DEC-251**: both keys required; each a closed map with a required boolean `enabled`; `code_intelligence` also has `languages`, a non-empty list of strings when it is enabled. | Batch 3, reading 18 |
| DP-9 | The form of a lesson id | **DEC-252**: `lesson_id` is `^L-[0-9]{4,}$`, the form of the carried lesson `L-0074`, in the shared definitions file and in the lesson template. | Batch 3, reading 19 |

DEC-251 and DEC-252 are recorded on another branch and were given to batch 3 in its brief; they are not yet in
this branch's `docs/DECISION_REGISTER.md`.

## Open decision package

### DP-10 — Disabled code intelligence: is `languages` required, and may it be empty?

- **Question.** DEC-251: "`code_intelligence` also has `languages`, a non-empty list of strings when it is
  enabled." When `enabled` is false, must the key `languages` still be there, and may it be an empty list?
- **Why now.** The repair writes the schema's condition one way or the other. Two engineers can read the sentence
  as "required only when enabled" or as "always there, non-empty only when enabled".
- **Options.**
  - (a) `languages` is required only when `enabled` is true. When disabled it may be left out; when present it is
    a list of strings and may be empty. (DP-8 option (a) as it was written.)
  - (b) `languages` is always required; it may be empty only when disabled.
  - (c) Leave it free: the schema may do either, and no test fixes it.
- **Impact.** (a) or (b): one more case (two documents). (c): none; the tests of batch 3 pass under both.
- **Reversibility.** Easy: this repository's path map has code intelligence enabled, so neither choice changes it.
  An adopted repository with the capability disabled would need a one-line edit after a change.
- **Cost.** One line from the orchestrator (it qualifies for DEC-220), then one test case.
- **Recommendation.** (a): a project that does not use code intelligence writes `enabled: false` and nothing else.
- **Confidence.** Medium-high.

## Settled package, kept for the record

### DP-8 — What is the value of a capability entry? (settled by DEC-251)

- **Question.** DEC-238 makes `capabilities` "a closed list of two: `code_intelligence` (with `languages`) and
  `research_corpus`". What does each key map to? Is "enabled" a boolean under the key, or is a capability enabled
  by being listed? Are both keys required? Is `languages` a list of language names, and is it required whenever
  `code_intelligence` is enabled?
- **Why now.** The KPI says the floor carries the *enabled* capabilities. The tests can assert only that the list
  is closed. A schema that accepts `code_intelligence: 42`, or `code_intelligence` with no `languages`, passes
  today. W1-16 (the code intelligence wrapper) and W1-27 (`gov doctor`) are the likely first readers.
- **Options.**
  - (a) Both keys are required. Each maps to a map with a required boolean `enabled` and no unknown key.
    `code_intelligence` also has `languages`, a list of non-empty strings, required and non-empty when `enabled` is
    true.
  - (b) A capability is enabled by being present and disabled by being left out. `research_corpus` maps to an
    empty map; `code_intelligence` maps to a map with a required, non-empty `languages` list.
  - (c) Leave the entry's value free at W1-08 and let the ticket that first reads it fix the shape.
- **Impact.** (a) about 5 more cases (each key required; `enabled` not a boolean refused; enabled code intelligence
  without `languages` refused; disabled without `languages` accepted; this repository's value checked). (b) about 3
  cases, and "disabled" is not visible in the file. (c) none; CAP-06.e stays tested in part, and the first reader
  decides alone.
- **Reversibility.** Easy until W1-16 or W1-27 reads the key; a path-map migration in every adopted repository
  after.
- **Cost.** One line from the owner or the orchestrator (it qualifies for DEC-220), then a short test-design round.
- **Recommendation.** (a): an explicit `enabled` matches the KPI's word and batch 1's DP-1 option (a) ("a map of
  name to `enabled`"), and a disabled capability stays visible.
- **Confidence.** Medium-high for the shape; medium for "both keys required".

## The follow-up after W1-41 on W1-30's ticket (DEC-569): two pieces on the kernel's schemas

Written by a test designer on ticket `DAEO-2lwj` (W1-30, reopened), before the schemas are changed. No earlier
case of this suite is changed. The cases need `check-jsonschema`, as the suite's others do.

### The probe record's schema (DEC-565; `test_w1_08_probe.py`, 7 cases)

DEC-565: "the probe type is added to the kernel's record schema". A probe record is the file `gov close` reads
for a FULL-profile ticket (DEC-137, DEC-487, DEC-490). The schema is found by the word `probe` in a file name
under the kernel's schemas folder (reading 1); the full name is the engineer's.

**Proposed: the fields and their shapes.** The worked example is the form of this repository's four probe
records (three tickets' folders), which state the nine required fields and nothing else.

| Field | Shape | Required |
|---|---|---|
| `type` | `probe` | yes |
| `task` | a ticket id (the shared `ticket_id` grammar) | yes |
| `reviewer_session` | text, not empty | yes |
| `implementer_session` | text, not empty | yes |
| `reviewer_wrote_nothing` | a truth value | yes |
| `commissioned_by` | text, not empty | yes |
| `judged_by` | text, not empty | yes |
| `judgement` | `pass`, `passed`, `fail` or `failed` (the four words DEC-490 names) | yes |
| `probed_commit` | forty lower-case hexadecimal characters: a full commit id, no abbreviation, no name that moves | yes |
| `id`, `status`, `state_class` | as in the shared frontmatter where stated | no |

What the schema does not ask, because the probe gate does: that the reviewer is not the implementer, that
`commissioned_by` and `judged_by` are `orchestrator`, that `reviewer_wrote_nothing` is true and that the
judgement passed. A record of a failed probe is a well-formed record; the gate refuses the close for it.
The schema is the one record schema that does not require the shared frontmatter's `id`, `status` and
`state_class`: the records `gov close` accepts today do not state them, and DEC-565 orders that those records
stop being findings, not that they be rewritten.

| Case | Holds | Red reason |
|---|---|---|
| `test_the_kernel_has_one_schema_for_the_probe_record` | one schema file with `probe` in its name, a JSON object | "no JSON Schema for the probe record" |
| `test_the_probe_schema_names_no_path_of_a_project` | the file names no `docs/` and no `.tickets` path | the same |
| `test_the_probe_schema_is_a_valid_json_schema` | the validator's metaschema check | the same |
| `test_the_probe_schema_accepts_a_well_formed_record` | the nine fields; with the three shared fields added; each of the other three judgement words | the same |
| `test_the_probe_schema_accepts_this_repository_s_probe_records` | the frontmatter of every file under `docs/probes/*/` here | the same |
| `test_the_probe_schema_refuses_a_record_without_a_required_field` | each of the nine fields left out, each for itself | the same |
| `test_the_probe_schema_refuses_a_field_of_a_wrong_type_or_value` | fifteen single changes (a judgement outside the words, in upper case, a truth value; a commit id abbreviated, a moving name, upper case, too long, a number; and one wrong shape of each other field) | the same |

7 red. What the schema check (`core-schema`) reports for a probe record is held in W1-26's suite
(`test_w1_26_probe_records.py`).

Not held: a commit id of forty digits and no letter, which YAML reads as a number unless it is quoted.

### The path-map schema names the optional keys the tools read (DEC-554, point 6; `test_w1_08_path_map_tool_keys.py`, 19 cases)

DEC-554, point 6: "The kernel's path-map schema names neither key, nor DEC-479's two: it goes to the follow-up
after W1-41 with DEC-521's items". The fifth key is the trailers base of DEC-482.

No name is proposed here: each key is read by a tool today under the name below, and each shape is the one
that tool accepts.

| Key | Read by | Valid | Refused (each held) |
|---|---|---|---|
| `close_timeout` | `gov close` (DEC-554; W1-30's round 12, settlement 21) | a positive number of seconds: `7200`, `90.5` | `0`, `-5`, a word, a number in quotes, a truth value, a list, no value |
| `close_workers` | `gov close` (DEC-549, DEC-554 point 5) | a positive whole number (`4`, `1`), or `auto` | `0`, `-2`, `1.5`, a word, a number in quotes, `AUTO`, a truth value, an empty text, no value |
| `decision_register` | the citations check, the store, `gov close` (DEC-479) | a path as text, not empty | an empty text, a list, a number, a truth value, no value |
| `decision_citations_base` | the citations check (DEC-479) | a commit id as text, full (40) or abbreviated (8) | an empty text, a number, `main`, a list, a truth value, no value |
| `trailers_base` | the trailers check (DEC-482; named by W1-30's round 13, settlement 31, and read under that name today) | as the citations base | as the citations base |

A commit id is hexadecimal characters; the cases hold a full id, one of eight characters, and that a name
with other characters is refused. They do not fix the shortest abbreviation (the two checks take four
characters or more today).

The path map of the cases is a fixture (the required systems are read from the schema); this repository's own
path map is held by the suite's earlier cases, unchanged, and must stay valid with the keys it has.

| Case | Holds | Today |
|---|---|---|
| `test_the_path_map_schema_names_the_optional_key` (5) | the key is a top-level property of the schema, with a description | red, all five: "does not name the key" |
| `test_an_optional_key_in_a_wrong_shape_is_refused` (5) | each wrong shape of the table is refused, each for itself, after the valid shape was accepted | red, all five: every wrong shape is accepted |
| `test_an_optional_key_in_a_valid_shape_validates` (5) | each valid shape of the table | green; holds that naming the key refuses nothing a tool accepts |
| `test_a_path_map_with_all_five_keys_validates` | the five together | green |
| `test_a_path_map_without_the_optional_keys_validates_as_before` | none of the five | green; holds what stays |
| `test_no_optional_key_is_required` | none of the five is among the schema's required keys | green; holds what stays |
| `test_a_top_level_key_the_schema_does_not_know_is_no_finding_as_before` | an unknown top-level key validates | green: **today an unknown top-level key is no finding**, and this piece does not change that |

10 red, 9 green.

Not held: what `gov` itself answers for a path map with one of the keys in a wrong shape when it loads the
project's configuration (`CONFIG_INVALID`). That validation is written by hand outside the kernel's schema
file and does not read it; each tool refuses its own key today (`INVALID_TIMEOUT`, `INVALID_WORKERS`,
`CITATIONS_CONFIG_INVALID`, `TRAILERS_BASE_UNKNOWN`). The decision orders the schema, and the cases hold the
schema.
