# W1-08 — Record schemas and templates: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-uudf` (W1-08), the Contract v4
items its KPI lines name (CAP-31.a, CAP-53.a, CAP-06.a, CAP-03.a, CAP-03.b, CAP-03.c, CAP-41.a, CAP-50.a, CAP-06.e,
CAP-54.b, CAP-07.b, CAP-41.c, CAP-41.f), ADR-0002 §2, §5 and §6, and DEC-012, DEC-168, DEC-185, DEC-189, DEC-221 and
DEC-224 to DEC-230, DEC-238 and DEC-239. Written before implementation, in two batches: batch 1 left seven decision
packages; batch 2 follows the decisions that settled them. No earlier ticket's test was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-08 -q -p no:cacheprovider
```

Standard library, `pytest` and PyYAML (declared in `pyproject.toml`). No network. Nothing is installed.

- **The validator is `check-jsonschema`** (0.38.2, in the tool registry; the stack's validator, ADR-0002 §2). It
  handles `$ref` across files and every draft 2020-12 keyword, which the small validator of the W1-04 and W1-06
  suites does not. Every case that validates is marked `local_only` (147 of 200 cases) and is skipped when the tool
  is absent. Deselect them with `-m "not local_only"`.
- **The good record is the committed one.** For each record type the good record is the frontmatter of the
  committed template; for the path map it is the committed `governance/project/path-map.yaml`. Each bad record is
  the good one with one change. Every refusal test first checks that the unchanged record is accepted, so a schema
  that refuses everything cannot pass. That check is asked of the validator once per run for each record.
- **Files are found by a word in their name**, not by a full name (reading 1). The shared definitions file is found
  by what it defines (reading 11).

About one minute once the schemas exist.

## KPI → tests → red reason today

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
| **Success 5.** The overlay schema carries the project floor; it identifies each constitutional system; no overlay value goes below the kernel floor **[CAP-06.e, CAP-54.b]** | `test_w1_08_floor.py` | Floor keys: `test_a_path_map_without_the_floor_key_is_refused[3]`. Policies and the kernel floor (CAP-06.e): `test_the_path_map_gives_each_of_the_thirteen_policies_a_strength_at_or_above_the_kernel_minimum` · `test_a_path_map_without_one_of_the_thirteen_policies_is_refused` · `test_every_strength_at_or_above_the_kernel_minimum_is_accepted` · `test_a_strength_below_the_kernel_minimum_is_refused[9]` · `test_a_policy_value_that_is_not_a_strength_is_refused[2]`. Capabilities (CAP-06.e): `test_the_path_map_names_no_capability_outside_the_two` · `test_a_capability_outside_the_two_is_refused`. **The shape of a capability entry: DP-8.** Systems (CAP-54.b): `test_the_path_map_identifies_each_of_the_twenty_two_constitutional_systems` · `test_a_path_map_without_one_of_the_twenty_two_systems_is_refused` · `test_a_system_is_implemented_or_minimal_with_a_where` · `test_an_absent_system_gives_its_reason` · `test_a_system_without_one_of_the_three_statuses_is_refused[2]` | No path map; no path-map schema |
| **Success 6.** The shared frontmatter records `state_class` for every record type **[CAP-07.b]** | `test_w1_08_frontmatter.py` · `test_w1_08_path_map.py` | `test_the_template_records_the_state_class_of_its_record_type[7]` · `test_a_record_without_a_state_class_is_refused[7]` · `test_the_six_state_classes_are_accepted_and_no_other[7]` · `test_the_shared_definitions_file_holds_the_six_state_classes` · `test_the_state_classes_are_written_in_one_schema_file_only` · `test_the_path_map_records_its_state_class` · `test_the_path_map_schema_takes_the_six_state_classes_and_no_other` | No templates; no schemas; no shared definitions file; no path map |
| **Success 7.** Lesson records carry a scope of PROJECT, PRODUCT or FRAMEWORK **[CAP-41.c]** | `test_w1_08_lesson.py` | `test_the_lesson_template_carries_a_scope_and_a_severity_in_lower_case` · `test_each_scope_is_accepted[3]` · `test_a_scope_outside_the_three_is_refused[4]` | No lesson template; no lesson schema |
| **Success 8.** The lesson schema requires both a scope and a severity (low, medium, high, critical), DEC-168 **[CAP-41.f]** | `test_w1_08_lesson.py` | `test_a_lesson_without_the_field_is_refused[2]` · `test_each_severity_is_accepted[4]` · `test_a_severity_outside_the_four_is_refused[4]` | No lesson template; no lesson schema |
| **Failure 1.** A schema accepts a ticket without kpis, role or allowed_paths | `test_w1_08_ticket.py` | `test_a_ticket_without_the_field_is_refused[3]` (left out, and null) · `test_a_ticket_without_kpis_role_and_allowed_paths_is_refused` | No ticket template; no ticket schema |
| **Failure 2.** Two schemas define the same id grammar differently | `test_w1_08_id_grammar.py` | `test_the_five_id_grammars_are_defined_in_one_file_only` · `test_the_shared_definition_is_a_grammar[5]` · `test_no_record_schema_writes_an_id_pattern_of_its_own` · `test_the_id_of_the_record_is_governed_by_the_shared_grammar[7]` | No shared definitions file; no schema |

**Count.** KPI lines with at least one test: 10 of 10 (8 of 8 success, 2 of 2 failure). Covers ids with at least one
test: 13 of 13. Tested in part: CAP-06.e, for the capabilities (the closed list is tested; the shape of an entry
waits for DP-8).

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
    `code_intelligence` and `research_corpus`; a third key is refused. The value of an entry is DP-8.
16. **The committed path map must load in `gov`** (DEC-185, DEC-228): `gov status --json --root <a folder holding
    only that file>` ends with exit code 0 and no `CONFIG_INVALID`. The loader in `src/gov/config/` keeps the
    minimal shape and leaves the new keys alone.
17. **"Committed"** means listed by `git ls-files`.

## Not tested, and why

- **The value of a capability entry** (an `enabled` flag, whether both keys are required, where `languages` is and
  when it is required): DP-8.
- **The id patterns themselves**, beyond the two ids this repository already uses: they are the engineer's (DEC-227).
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

## Open decision package

### DP-8 — What is the value of a capability entry?

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
