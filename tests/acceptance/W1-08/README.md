# W1-08 — Record schemas and templates: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-uudf` (W1-08), the Contract v4
items its KPI lines name (CAP-31.a, CAP-53.a, CAP-06.a, CAP-03.a, CAP-03.b, CAP-03.c, CAP-41.a, CAP-50.a, CAP-06.e,
CAP-54.b, CAP-07.b, CAP-41.c, CAP-41.f), ADR-0002 §2, §5 and §6, and DEC-012, DEC-168, DEC-185 and DEC-189. Written
before implementation. No earlier ticket's test was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-08 -q -p no:cacheprovider
```

Standard library, `pytest` and PyYAML (declared in `pyproject.toml`). No network. Nothing is installed.

- **The validator is `check-jsonschema`** (0.38.2, in the tool registry; the stack's validator, ADR-0002 §2). It
  handles `$ref` across files and every draft 2020-12 keyword, which the small validator of the W1-04 and W1-06
  suites does not. Every case that validates is marked `local_only` (165 of 264 cases) and is skipped when the tool
  is absent. Deselect them with `-m "not local_only"`.
- **The good record is the committed one.** For each record type the good record is the frontmatter of the
  committed template; for the path map it is the committed `governance/project/path-map.yaml`. Each bad record is
  the good one with one change. Every refusal test first checks that the unchanged record is accepted, so a schema
  that refuses everything cannot pass.
- **Files are found by a word in their name**, not by a full name (reading 1).

About 25 seconds once the schemas exist.

## KPI → tests → red reason today

Red run on `w1/integrate` at `ea79747d`: **205 failed, 59 errors, 0 passed** (264 cases, 48 test functions). The
errors are the same assertions, raised in a fixture.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1.** JSON Schemas exist for MADR decision, ticket (nine fields), lesson, failure, research record, gate/decision package, checkpoint, path map **[CAP-31.a, CAP-53.a]** | `test_w1_08_schemas_exist.py` · `test_w1_08_ticket.py` | `test_a_schema_file_exists_for_the_record_type[8]` · `test_the_schema_file_is_a_json_object[8]` · `test_the_schema_file_is_tracked_by_git[8]` · `test_the_schema_is_a_valid_json_schema[8]` · `test_each_record_type_has_its_own_schema_file` · `test_the_ticket_template_carries_the_field[9]` · `test_the_ticket_schema_defines_the_field[9]` (CAP-31.a) · `test_each_profile_is_accepted[3]` · `test_a_profile_outside_the_three_is_refused[3]` · `test_the_ticket_template_declares_one_of_the_three_profiles` (CAP-53.a) | `no JSON Schema for the <type> record: no file named *.schema.json under template/governance/kernel/schemas/ has one of [...] in its name`; for the template cases, `no record template exists: there is no template/governance/kernel/templates/` |
| **Success 2a.** Every record type has a template that validates against its schema **[CAP-06.a]** | `test_w1_08_templates.py` | `test_a_template_exists_for_the_record_type[7]` · `test_the_template_is_tracked_by_git[7]` · `test_the_template_carries_frontmatter_that_is_a_map[7]` · `test_the_template_validates_against_its_schema[7]` · `test_the_template_validates_as_it_is_written[7]` · `test_the_schema_refuses_a_record_that_is_not_a_map[7]` | No templates folder; no schema |
| **Success 2b.** This repository's path map classifies every tracked path **[CAP-06.a]** | `test_w1_08_path_map.py` | `test_this_repository_has_a_committed_path_map` · `test_the_path_map_has_namespaces` · `test_the_path_map_validates_against_the_path_map_schema` · `test_the_path_map_validates_as_it_is_written` · `test_the_gov_cli_loads_the_committed_path_map`. **"Every tracked path" itself is not tested: DP-2.** | `this repository has no path map: governance/project/path-map.yaml does not exist`; no path-map schema |
| **Success 3a.** Each namespace has a sensitivity class, permitted roles, retention, export policy, embedding policy, provenance and deletion/rebuild behaviour **[CAP-03.a, CAP-03.c]** | `test_w1_08_path_map.py` | `test_every_namespace_of_the_path_map_declares_the_field[7]` · `test_a_namespace_without_the_field_is_refused[7]` · `test_an_empty_namespace_is_refused` · `test_a_namespace_that_is_not_a_map_is_refused[4]` · `test_a_path_map_that_is_not_a_map_is_refused[3]` | No path map; no path-map schema |
| **Success 3b.** The artefact identity fields of Contract v3 W1 are in the shared frontmatter **[CAP-50.a]** | `test_w1_08_frontmatter.py` | `test_the_template_carries_the_identity_field[21]` · `test_a_record_without_the_identity_field_is_refused[21]` — `id`, `type`, `status` only. **The other six fields: DP-3.** | No templates; no schemas |
| **Success 3c.** Lesson records carry a lifecycle state (candidate → … → approved) **[CAP-41.a]** | `test_w1_08_lesson.py` | `test_the_lesson_template_carries_a_lifecycle_state` · `test_the_six_lifecycle_states_are_accepted_and_no_other` | No lesson template; no lesson schema |
| **Success 4.** Every namespace is governance/development memory or customer/runtime product data, never both **[CAP-03.b]** | — | **No test: DP-2.** | — |
| **Success 5.** The overlay schema carries the project floor; it identifies each constitutional system; no overlay value goes below the kernel floor **[CAP-06.e, CAP-54.b]** | — | **No test: DP-1.** | — |
| **Success 6.** The shared frontmatter records `state_class` for every record type **[CAP-07.b]** | `test_w1_08_frontmatter.py` | `test_the_template_records_a_state_class[7]` · `test_a_record_without_a_state_class_is_refused[7]` · `test_a_state_class_that_is_not_a_word_is_refused[21]`. **Its values, and the 48 committed tickets: DP-4.** | No templates; no schemas |
| **Success 7.** Lesson records carry a scope of PROJECT, PRODUCT or FRAMEWORK **[CAP-41.c]** | `test_w1_08_lesson.py` | `test_the_lesson_template_carries_a_scope` · `test_each_scope_is_accepted[3]` · `test_a_scope_outside_the_three_is_refused[5]` | No lesson template; no lesson schema |
| **Success 8.** The lesson schema requires both a scope and a severity (low, medium, high, critical), DEC-168 **[CAP-41.f]** | `test_w1_08_lesson.py` | `test_a_lesson_without_a_scope_is_refused` · `test_the_lesson_template_carries_a_severity` · `test_each_severity_is_accepted[4]` · `test_a_severity_outside_the_four_is_refused[4]` · `test_a_lesson_without_a_severity_is_refused` · `test_a_lesson_with_a_scope_and_no_severity_or_a_severity_and_no_scope_is_refused` | No lesson template; no lesson schema |
| **Failure 1.** A schema accepts a ticket without kpis, role or allowed_paths | `test_w1_08_ticket.py` | `test_a_ticket_without_the_field_is_refused[3]` · `test_a_ticket_without_kpis_role_and_allowed_paths_is_refused` · `test_a_ticket_whose_field_is_null_is_refused[3]` | No ticket template; no ticket schema |
| **Failure 2.** Two schemas define the same id grammar differently | `test_w1_08_id_grammar.py` | `test_a_definition_shared_by_name_is_the_same_in_every_schema` · `test_no_schema_gives_one_property_two_grammars` · `test_the_id_of_every_record_type_follows_a_grammar[28]`. **Grammars shared by meaning: DP-6.** | No schema for the first record type asked for (checkpoint) |

**Count.** KPI lines with at least one test: 8 of 10 (6 of 8 success, 2 of 2 failure). Success 4 and success 5 have
none, by decision package. Covers ids with at least one test: 10 of 13. Without a test: **CAP-03.b** (DP-2),
**CAP-06.e** and **CAP-54.b** (DP-1). Tested in part: CAP-06.a (the tracked-path half waits for DP-2), CAP-50.a
(three of nine fields, DP-3), CAP-07.b (presence, not the values, DP-4).

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
   is not checked. A template with Jinja syntax in its frontmatter would fail these tests.
3. **"Every record type has a template"** is read as the seven frontmatter record types. A template for the path
   map is not required: the committed `governance/project/path-map.yaml` is its instance and must validate.
4. **Ticket fields.** "The schema has the field" is tested by behaviour: with the field set to a value of no
   plausible kind (`42` for `class`, `role`, `depends_on`, `allowed_paths`, `kpis`, `sources`, `acceptance_tests`;
   `"many"` for `est_loc`; `"HUGE"` for `profile`) the ticket is refused. Only `kpis`, `role` and `allowed_paths`
   are tested as required (failure 1). A null in their place is refused too. The values of `class` and `role`, the
   inner shape of `kpis` and of `acceptance_tests`, and whether the other six fields are required, are not tested.
5. **CAP-53.a** on this ticket is the `profile` field: `LITE`, `STANDARD` and `FULL` are accepted, another word is
   refused. Readiness rows per profile belong to W1-13.
6. **Scope and severity** are fields named `scope` and `severity`. CAP-41.c writes the scope in upper case, CAP-41.f
   in lower case; the tests take the letter case the template uses, for both fields (DP-5 asks which one).
7. **The lifecycle field** has no name in any source. It is found in the lesson template as the field (other than
   `scope` and `severity`) whose value is one of the six states. That field must take each of the six, refuse
   another word, and be required. States beyond the six (CAP-41.a also has "report" and "versioned") are allowed.
8. **Shared frontmatter** is tested by behaviour on each of the seven record types: the template has the field and
   the schema refuses the record without it. How the schemas share it (one file with `$ref`, or a copy) is free.
   `state_class` must be a non-empty string; null, a number and the empty string are refused.
9. **Path map.** The top level is DEC-189's: `namespaces` maps a name to a map. Each of the seven namespace fields
   is found by the KPI's word in a key name, at any depth inside the namespace: `sensitiv` · `role` · `retention` or
   `retain` · `export` · `embed` · `provenance` · `delet` or `rebuild`. One key may serve one field only if removing
   it is refused. Removing the key from any one namespace must make the path map invalid.
10. **The committed path map must load in `gov`** (DEC-185): `gov status --json --root <a folder holding only that
    file>` ends with exit code 0 and no `CONFIG_INVALID`. Today that means it must fit the minimal shape in
    `src/gov/config/`; see the note under "W1-07 revisions".
11. **Id grammar, the part tested.** A `$defs` or `definitions` entry with the same name in two schema files is the
    same definition (annotations aside); inside one schema file a property name does not carry two different
    `pattern` values; and every record schema refuses an `id` that is empty, holds a line break, or is not a string.
12. **"Committed"** means listed by `git ls-files`.

## Not tested, and why

- **Success 5 as a whole** (overlay schema, project floor, constitutional systems, kernel floor): DP-1.
- **Success 4** (memory class of a namespace) and **"classifies every tracked path"**: DP-2.
- **Identity fields other than `id`, `type`, `status`**: DP-3.
- **The values of `state_class`**, and **whether the committed tickets validate against the ticket schema**: DP-4.
- **Grammars shared by meaning between schemas**: DP-6.
- **The fields of the decision, failure, research, gate and checkpoint records** beyond the shared frontmatter: the
  KPIs name none. DEC-012 lists the decision record's keys (`supersedes`, `superseded_by`, `depends_on`,
  `implements`, `constrains`, `content_hash`) with status PROPOSED and no KPI repeats them; W1-11 and W1-34 use them.

## W1-07 revisions (DEC-189)

**None made.** W1-08's `allowed_paths` do not include `src/gov/config/`, so the loader keeps the minimal shape and
the cases of `tests/acceptance/W1-07/test_w1_07_config_details.py` stay valid as written. They will need the planned
revision ("owner decision, DEC-189") when a ticket makes `gov` validate against the real path-map schema: then
`namespaces: {core: {}}` (`test_a_valid_path_map_loads`, `test_a_valid_path_map_is_not_reported_as_invalid_by_any_command`,
`test_repairing_the_key_clears_the_error`) stops being valid. No ticket is named for that replacement: see DP-7.

## Decision packages, in order of how much they block

### DP-1 — What is "the overlay schema", and what are the project floor, the constitutional systems and the kernel floor?

- **Question.** Success 5 says the overlay schema carries the project floor (enabled capabilities and policy
  strengths), identifies each constitutional system at least minimally, and lets no overlay value go below the
  kernel floor. Which file is the overlay schema, which file does it validate, what are the keys, what is the list
  of constitutional systems, and where is the kernel floor written down?
- **Why now.** No readable source answers any of the five. DEC-185 says there is no `overlay.yaml` and that the
  overlay is the set of `governance/project/` files. W1-08 may write only `path-map.yaml` there. The sources of
  CAP-06.e and CAP-54.b (OWNER-DECISION-P2-0008 §2, Framework §7) are under `docs/source/`, which no session reads.
  "Below the floor" needs an order of policy strengths and a floor to compare with; a JSON Schema alone cannot
  compare two files. Two KPI covers (CAP-06.e, CAP-54.b) have no test until this is answered.
- **Options.**
  - (a) The floor lives in `path-map.yaml`, under new top-level keys, for example `capabilities` (a map of name to
    `enabled`), `policies` (a map of name to a strength from a fixed ordered list) and `systems` (a list with `id`
    and `paths`), all in the path-map schema. The kernel floor is the schema's own minimum: the schema refuses a
    strength below it. The owner names the strengths, the minimum, and the systems.
  - (b) A separate schema, `overlay.schema.json` or `floor.schema.json`, for a file `governance/project/floor.yaml`
    that a later ticket creates (W1-08 writes only the schema and a template). The kernel floor is a file in the
    kernel template; "not below" is checked by `gov doctor` (W1-27), not by the schema.
  - (c) Move success 5 to the ticket that builds the check (W1-27 or W1-39), and leave W1-08 with the eight schemas.
- **Impact.** (a) one file, testable now with the validator alone, about 12 tests; the path-map schema grows.
  (b) a new file outside W1-08's `allowed_paths` (a ticket edit), and the floor comparison has no test at W1-08.
  (c) a CIT-P plan change: two covers items change provider, and `validate_s1.py` must still pass.
- **Reversibility.** (a) and (b) are schema keys: easy to change before W1-27 reads them, a migration after. (c) is
  a plan change, easy to reverse.
- **Cost.** (a) one owner answer with three short lists, then a short test-design round. (b) the same plus a ticket
  edit. (c) a plan change.
- **Recommendation.** (a), with the owner giving the list of policy strengths in order, the minimum, and the list of
  constitutional systems (or the rule "a system is an id plus at least one path").
- **Confidence.** Medium. The structure is sound; the three lists can only come from the owner or the unreadable
  sources.

### DP-2 — How does a namespace name its paths, and how is its memory class written?

- **Question.** (1) Which key of a namespace lists its paths, in which pattern language, and may a tracked path
  fall in two namespaces? (2) Which key says "governance/development memory" or "customer/runtime product data",
  with which values?
- **Why now.** "This repository path map classifies every tracked path" needs a matching rule to be tested, and
  "one namespace cannot be both" needs the key and its values. Neither is in a readable source. CAP-06.a also asks
  for class, authority and intended target per artefact, with no key named. CAP-03.b has no test until answered.
- **Options.**
  - (a) `paths`: a list of patterns in the language of the tickets' `allowed_paths` (`**` crosses folders, `*` stays
    inside one). Every `git ls-files` path matches exactly one namespace. `memory_class`: one string, either
    `governance` or `product`; a single enumerated string cannot be both.
  - (b) As (a), but a path may match several namespaces and the first in file order wins.
  - (c) The namespace name is the path prefix (no `paths` key); `memory_class` as in (a).
- **Impact.** (a) about 8 tests: every tracked path matches, a path added outside the map is named, the two values
  are accepted, a list of both and another word are refused, a missing key is refused. (b) adds an ordering rule
  every reader of the map must implement. (c) is the smallest file, but cannot express a namespace of scattered
  files.
- **Reversibility.** Easy until W1-15, W1-17 and W1-27 read the map; a migration of every adopted repository after.
- **Cost.** One owner answer; a short test-design round; the path map of this repository must then list all 408
  tracked paths' patterns.
- **Recommendation.** (a).
- **Confidence.** Medium-high.

### DP-3 — What are the key names of the artefact identity fields?

- **Question.** CAP-50.a lists nine: id, type, canonical path, status, lifecycle, version/hash, provenance, lineage,
  expected consumers. Under which keys do the last six (plus `lifecycle`) appear in the shared frontmatter, and
  which are required?
- **Why now.** Only `id`, `type` and `status` are named as keys anywhere readable, so only those three are tested.
  DEC-012 has `content_hash` (computed), `supersedes` and `superseded_by`; API-0002 has `version` and `consumers`.
  A record's canonical path is where the file is, and a hash of a file cannot be stored inside it without a rule.
- **Options.**
  - (a) Required: `id`, `type`, `status`, `state_class`. Optional but defined: `version`, `provenance`,
    `supersedes`, `superseded_by` (lineage), `consumers`. Derived by `gov` into the store and not written in the
    file: canonical path, `content_hash`. `lifecycle` is the same field as `status`.
  - (b) All nine are required keys of every record (`path`, `lifecycle`, `content_hash`, `provenance`, `lineage`,
    `consumers`, …).
  - (c) As (a), with `provenance` required too.
- **Impact.** (a) about 10 more tests; committed records need only `state_class` added. (b) every committed ticket
  and ADR needs six new keys, and a stored hash that changes on every edit. (c) one more required key.
- **Reversibility.** Making an optional key required later is a migration; the reverse is free. (a) is the safe side.
- **Cost.** One owner answer; a short test-design round.
- **Recommendation.** (a).
- **Confidence.** Medium.

### DP-4 — `state_class`: its values, and the 48 committed tickets

- **Question.** (1) What are the allowed values of `state_class`? (2) The KPI says every record type, the ticket
  included. No committed ticket has `state_class`, and `tk` writes `type: task`. Must the committed tickets, and
  tickets `tk` creates later, validate against the ticket schema?
- **Why now.** The only value in a readable file is `AUTHORITATIVE` (`docs/interfaces/API-0002.yaml`); the list is
  in Framework §3. The tests follow the KPI: a ticket without `state_class` is refused. If the owner wants the
  committed tickets to validate (W1-09 vendors `tk` and checks READY), then either the tickets change or the KPI
  does, and three tests change with it.
- **Options.**
  - (a) Values `AUTHORITATIVE`, `DERIVED`, `EVIDENCE`, or the owner's list. Tickets carry `state_class` too: the 48
    are edited once by the orchestrator, and W1-09 adds the key when it creates a ticket. `type` stays `tk`'s own
    field for a ticket.
  - (b) The same values; the ticket schema is exempt from `state_class` (a ticket is always authoritative), and the
    KPI line is reworded.
  - (c) Leave the values open (any non-empty string) at W1-08.
- **Impact.** (a) one commit touching 48 tickets, plus 4 tests (each value accepted, another refused, every
  committed ticket validates). (b) a KPI edit and three test cases removed. (c) nothing now; CAP-07.b is weaker.
- **Reversibility.** Easy in all three.
- **Cost.** One owner answer; a short round.
- **Recommendation.** (a).
- **Confidence.** Medium: the list of values is a guess until the owner confirms it.

### DP-5 — Letter case of the lesson's scope and severity

- **Question.** CAP-41.c and success 7 write `PROJECT/PRODUCT/FRAMEWORK`; CAP-41.f, success 8 and DEC-168's
  wording write `project, product or framework` and `low, medium, high or critical`. Which is the stored form?
- **Why now.** The tests accept either, taking the case of the template, so this blocks nothing. A schema that
  accepts both forms would also pass, and W1-21's scope match would then need to fold case.
- **Options.** (a) lower case for both fields. (b) upper case for both. (c) both forms accepted.
- **Impact.** (a) or (b): two more tests (the other case is refused). (c): none, and every reader folds case.
- **Reversibility.** Easy before W1-44 writes the first lesson records; a small migration after.
- **Cost.** One line from the owner.
- **Recommendation.** (a): it is the form of the later decision (DEC-168) and of the lifecycle states.
- **Confidence.** High.

### DP-6 — Which id grammars do two schemas share?

- **Question.** Failure 2 forbids two schemas from defining the same id grammar differently. Which grammars are
  shared, and what are they? For example: the ticket id (`DAEO-uudf`, and the WBS id `W1-08` in `depends_on`), the
  decision id (`ADR-0002`, `DEC-012`), the lesson id (`L-0074`), the capability id (`CAP-41.f`).
- **Why now.** Without the list, a test can only compare definitions that carry the same name (reading 11). Two
  schemas that each write their own pattern for a ticket id under different names would pass.
- **Options.**
  - (a) One shared definitions file (or one `$defs` block that the others `$ref`) holds every id grammar under a
    fixed name (`ticket_id`, `wbs_id`, `decision_id`, `lesson_id`, `record_id`), and no other schema file writes a
    `pattern` for an id. The owner confirms the names; the patterns are the engineer's.
  - (b) The owner fixes each grammar as a regular expression, and the tests assert sample ids against each schema.
  - (c) Keep the same-name rule only.
- **Impact.** (a) 2 tests (no id `pattern` outside the shared file; every `id` property refers to it). (b) about 15
  tests and five owner-approved expressions. (c) none; the failure KPI stays weakly tested.
- **Reversibility.** Easy.
- **Cost.** (a) one line. (b) a longer answer.
- **Recommendation.** (a).
- **Confidence.** Medium-high.

### DP-7 — Who replaces the minimal path-map schema in `src/gov/config/`?

- **Question.** DEC-185 says the minimal schema lives under `src/gov/config/` "until W1-08 supplies the real one and
  replaces it". W1-08's `allowed_paths` are the kernel schemas, the kernel templates and `path-map.yaml`; its role
  is product-spec. Which ticket makes `gov` validate against the real schema?
- **Why now.** It does not block W1-08's tests. It decides when the W1-07 cases listed above are revised, and until
  then `gov` accepts a path map the real schema refuses.
- **Options.** (a) W1-10 or W1-27 (engineer tickets that depend on W1-08) replaces it, and that ticket's test design
  revises the W1-07 cases. (b) `src/gov/config/**` is added to W1-08's `allowed_paths` and an engineer does that part.
  (c) Leave the minimal loader for Wave 1 and let `gov doctor` (W1-27) run the full schema.
- **Impact.** (a) one KPI line on the chosen ticket. (b) W1-08 becomes a two-role ticket. (c) two validators of one
  file with different answers.
- **Reversibility.** Easy.
- **Cost.** One line in a ticket.
- **Recommendation.** (a), on W1-27, which already reads the path map for `gov doctor`.
- **Confidence.** Medium.
