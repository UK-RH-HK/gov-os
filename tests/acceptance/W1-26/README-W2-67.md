# W1-26 under W2-67 (DAEO-9nys), round 1, batch 2: the planted-defect cases and their base

Ticket `DAEO-9nys` (W2-67), KPI 5 in round 1's scope (DEC-904 item 5): W1-26's planted-defect cases, their fixture
shown green before any defect (P-IS-7 (a); I2 F3, F7 and §2.7; I-SYNTHESIS §5.2's W1-26 row). Written by a fresh
independent test designer (MR-3). Each revised case keeps its name, lowers no expectation, asserts the named check's
or family's own status and finding, was shown red against a planted fault and green on the head, and is committed
with a `Rewrite-Reason:` trailer (DEC-491).

## The base, green before any defect

**Before.** `support.Project` holds every kernel declaration. Six of their checks need what a temporary project does
not hold, so the base was red under `gov check` before any defect (I2 R1; seen again on 2026-10-23: exit 3,
`CHECK_FAILED`, six hard-block checks RED):

| Check left out | Why it is red in a temporary project |
|---|---|
| `adapter-portability` | no `governance/project/tool-registry.yaml`, no rulesync source |
| `context-reproducibility` | no store |
| `index-freshness` | no lexical index |
| `recovery-rebuild` | no store (unmeasured) |
| `retrieval-regression` | `GOV_DEV_TIERS` is not configured: the environment |
| `secrets-indexing` | no `.gitleaks.toml` |

**Now.** `support.green_base(project, dimensions=False)` removes those six declarations (`NOT_MEASURABLE_HERE`) and
folds the result into the project's first commit; with `dimensions=True` that commit also holds
`docs/contract/readiness-dimensions.yaml`, so that only a later change of it is a change (adding the file in a
later commit is itself reported by the taxonomy check). The conftest fixtures `green_project` and
`green_project_with_dimensions` give the two. None of the cases below names one of the six checks or its family;
their families are then YELLOW ("no registered check"), never GREEN (DEC-425).

`test_w1_26_green_base.py` (new, 3 cases) holds it:

- `test_the_base_project_is_green_before_any_defect[green_project, green_project_with_dimensions]`: `ok` and exit 0,
  no check RED, each judged check (`JUDGED_CHECKS`: `core-schema`, `core-graph`, `core-authority`, `core-mutation`,
  `core-claims`, `skill-version`, `readiness`) GREEN with no finding, the six not run and their families not GREEN.
  Green on the head; red under PF21 (`g0-PF21.xml`: "the base project is not green before any defect").
- `test_the_checks_left_out_of_the_base_are_the_only_red_checks_of_the_full_base`: on the base as built, every RED
  check is one of the six, and every judged check is GREEN with no finding: the six are not the checks under test.

## Planting a fault

`src/` is never written and the tree is never copied. A throwaway pytest plugin, `w2_67c_plant` (`-p w2_67c_plant`,
its folder on `PYTHONPATH`), wraps `w1_07_support.write_launcher` in the test process: each launcher a case writes
first imports `w2_67c_child` and applies the faults named in `W2_67_PLANT`, in that `gov` process only. A fault of
a declared check's text (PF7, PF8, PF17, PF24, P67C-1, P67C-3, P67C-4) replaces that check's command, in that run,
by `python3 w2_67c_run_patched.py <fault>`, which runs the check's module as `python3 -m` would with one exact text
change made in memory, as I2 made its PF-n in a clone. The plant modules, their record (`PLANTS.md`) and every
run's JUnit XML are in `.gov-runtime/scratch/td-2/plant/` (written in the session scratch folder and copied there as
single named files). A command, for one fault:

    W2_67_PLANT=PF7 PYTHONPATH=<worktree>/src:<worktree>/.gov-runtime/scratch/td-2/plant \
      python3 -m pytest -p no:cacheprovider -p w2_67c_plant -q -n 4 --junitxml=<plant>/g1-planted-defects-PF7.xml <node ids>

| Fault | In words | How |
|---|---|---|
| PF20 (I2) | every check reports GREEN with no finding | the runner's declared, OpenSpec, skill, readiness and policy results made GREEN, no finding |
| PF21 (I2) | `gov check` fails whatever its checks say | `gov.check.command.run`: `if has_hard_block_red:` → `if True:` |
| PF22 (I2) | the readiness check ignores `check_all`'s answer | `_check_readiness`: the `closed` test → `if False:` |
| PF23 (I2) | the readiness check swallows an error of `check_all` | `_check_readiness`: the `except` branch appends nothing |
| PF7 (I2) | the schema check no longer reads ticket files | `RECORD_PATHS = ("docs",)` in the check's process |
| PF17 (I2) | the schema check reads no record | `RECORD_PATHS = ()` |
| PF8 (I2) | the graph check reads no record | `RECORD_PATHS = ()` |
| PF24 (I2) | the commands check measures nothing | `check` returns `[]` first |
| MUTE-authority, -mutation, -claims | the check's command measures nothing (PF3's form) | its command runs as `true` |
| MUTE-skill-version, -policy, -readiness, -openspec | the built-in check measures nothing | its result made GREEN with no finding |
| P67C-2 | an "unmeasured" answer counts as GREEN (DEC-425) | a declared check whose every finding says unmeasured made GREEN |
| P67C-3 | the schema check reads a hand-kept list of folders (DEC-436, F-2) | `RECORD_PATHS = (".tickets", "docs/adr")` |
| P67C-4 | the schema check skips an unknown type silently (DEC-436) | the `SCHEMA_UNKNOWN_TYPE` finding is not appended |

## The revised cases

All 42 green on the head: the touched files whole (and W1-28's copy check and W2-02's file), 112 passed in 40 s
(`final-head-w1-26.xml`; `test_exit_0_when_all_checks_green` deselected, see "Cases left"). Each plant failed
exactly the cases named after the behaviour it breaks and no other case of the run (the XML of each run is
`g<group>-<set>-<fault>.xml`). "Red" quotes the failure.

### The overall-red class, 24 cases (commit `c0297fc3`)

`Rewrite-Reason: the fixture was red before the defect, so the case could not fail (I2 R1, F3)`. Each plants its
defect on the green base and calls `support.assert_check_red_naming(run, interface, <check>, <values>)`: the named
check's own entry RED, a finding of it that names the defect (the planted record's path or id and the field,
target, pattern, gap ticket or key), and `gov check` failed with exit 3.

| Case | Check, and what its finding names | Red under (seen) |
|---|---|---|
| `test_w1_26_planted_defects.py::test_planted_schema_defect_ticket_missing_kpis` | `core-schema`: `.tickets/BAD-aaaa.md`, `kpis` | PF7, PF17, PF20: "core-schema is 'GREEN' on the planted defect, expected RED" |
| `…::test_planted_schema_defect_decision_missing_status` | `core-schema`: `docs/adr/BAD-0001.md`, `status` | PF17, PF20 (PF7 green: a decision is not a ticket) |
| `…::test_planted_graph_defect_dangling_depends_on` | `core-graph`: `DEC-001`, `NONEXISTENT-999` | PF8, PF20 |
| `…::test_planted_graph_defect_duplicate_id` | `core-graph`: `DEC-001` and both files | PF8, PF20 (the authority mute: green) |
| `…::test_planted_graph_defect_id_outside_grammar` | `core-graph`: `docs/adr/bad.md`, `!!!INVALID!!!` | PF8, PF20 |
| `…::test_planted_authority_defect_active_while_superseded` | `core-authority`: `ADR-0001` and its file | MUTE-authority, PF20 |
| `…::test_planted_mutation_defect_implementer_covers_acceptance` | `core-mutation`: `.tickets/IMPL-aaaa.md`, `tests/acceptance/**` | MUTE-mutation, PF20 |
| `…::test_planted_mutation_defect_implementer_covers_acceptance_subpath` | `core-mutation`: `.tickets/IMPL-bbbb.md`, `tests/acceptance/W1-99/**` | MUTE-mutation, PF20 |
| `…::test_planted_claims_defect_ticket_dag_cycle` | `core-claims`: a ticket of the cycle; and no such finding once the cycle is broken | MUTE-claims, PF20 |
| `…::test_planted_claims_defect_ticket_missing_required_field` | `core-claims`: `.tickets/BAD-cccc.md`, `role` | MUTE-claims, PF20 |
| `test_w1_26_authority.py::test_research_cited_as_decision_is_red` | `core-authority`: `RES-001`, `DEC-AUTH-001` | MUTE-authority, PF20 |
| `…::test_research_cited_as_policy_is_red` | `core-authority`: `RES-002`, `POL-aaaa` | MUTE-authority, PF20 |
| `…::test_lesson_cited_as_policy_is_red` | `core-authority`: `LES-001`, `DEC-AUTH-002` | MUTE-authority, PF20 |
| `…::test_superseded_record_satisfying_current_requirement_is_red` | `core-authority`: `DEC-OLD-001`, `REQ-aaaa` | MUTE-authority, PF20 |
| `test_w1_26_decisions.py::test_supersession_cycle_flagged` | `core-authority`: `DEC-CYC-001`, `DEC-CYC-002` | MUTE-authority, PF20 |
| `test_w1_26_gap_tickets.py::test_required_missing_row_no_gap_ticket_is_red` | `core-claims`: the specification's `readiness.yaml` | MUTE-claims, PF20 |
| `…::test_required_missing_row_with_unlinked_gap_ticket_is_red` | `core-claims`: `readiness.yaml`, `UNLINKED` | MUTE-claims, PF20 |
| `…::test_gap_ticket_naming_closed_ticket_is_red` | `core-claims`: `readiness.yaml`, `CLOSED-aaaa` | MUTE-claims, PF20 |
| `…::test_gap_ticket_naming_nonexistent_ticket_is_red` | `core-claims`: `readiness.yaml`, `NOPE-zzzz` | MUTE-claims, PF20 |
| `test_w1_26_policy.py::test_a_new_policy_key_with_no_check_and_not_informational_is_red` | a check RED whose finding names `brand_new_policy`, the only key reported | MUTE-policy, PF20: "the policy keys reported are not exactly the new one: []" |
| `test_w1_26_skill.py::test_skill_content_changed_version_unchanged_is_red` | `skill-version`: the skill file | MUTE-skill-version, PF20 |
| `…::test_skill_content_changed_version_unchanged_no_decision_is_red` | `skill-version`: the skill file | MUTE-skill-version, PF20 |
| `test_w1_26_taxonomy.py::test_dimensions_changed_without_cite_is_red` | `core-claims`: `docs/contract/readiness-dimensions.yaml` | MUTE-claims, PF20 |
| `…::test_taxonomy_field_changed_without_cite_is_red` | `core-claims`: the same file | MUTE-claims, PF20 |

Notes. The gap and taxonomy cases use `green_project_with_dimensions` (the gap cases' own `add_readiness_dimensions`
then writes the same bytes, so the taxonomy check has nothing to report). The policy case also needed a valid path
map: its fallback wrote `namespaces: []`, which `gov check` refused (`CONFIG_INVALID`, exit 1) before any check ran;
its base path map now holds the keys a declared check of the project states and the informational ones (with the six
left out, `security` and `tool` are stated by none), so `brand_new_policy` is the only key reported.

### The derived-scope class, 7 cases (commit `eeb36c7d`)

`Rewrite-Reason: the outputs always differ (they carry the commit id), and an envelope or a red base proved nothing
(I2 F3)`. Each plants a record the named check must read and asserts that check's own entry (GREEN with no finding
before, RED with a finding that names the new record after). Where the original record was well-formed, it now
carries one defect so that the check's reading of it shows (a missing `kpis`, a `depends_on` no record has).

| Case | Red under (seen) |
|---|---|
| `test_w1_26_derived.py::test_adding_a_ticket_is_picked_up_by_schema_check` | PF7, PF17, PF20 |
| `…::test_adding_a_decision_is_picked_up_by_graph_check` | PF8, PF20 |
| `…::test_schema_check_discovers_all_ticket_files` (a finding on each of three) | PF7, PF17, PF20 |
| `…::test_graph_check_discovers_all_decision_files` (a finding on each of three) | PF8, PF20 |
| `…::test_removing_a_defective_record_clears_the_finding` (RED naming it, then GREEN and `gov check` passes) | PF7, PF17, PF20 |
| `test_w1_26_dec436.py::test_record_in_new_directory_discovered_by_schema_check` | P67C-3 (folders kept by hand), PF17, PF20 |
| `…::test_record_with_unknown_type_not_silently_skipped` | P67C-4 (unknown type skipped), PF17, PF20 |

### The always-true assertions, 5 cases, and the duplicate pair (commit `6a44dcd6`)

`Rewrite-Reason: each word asserted is in every output (check ids, family names), or the loop matched no family
(I2 §2.7)`; for the pair, `Rewrite-Reason: test_duplicate_id_flagged duplicated the graph check's case and judged
only gov check's failure on a red base (I2 §2.5, §2.7)`.

| Case | Now asserts | Red under (seen) |
|---|---|---|
| `test_w1_26_decisions.py::test_gov_check_runs_decision_checker` | each finding `gov.decisions.checker.check(root)` gives (called in a new process, this worktree's code) is a finding of `core-authority`, by code and message | MUTE-authority, PF20 |
| `test_w1_26_readiness.py::test_readiness_invalid_is_a_finding` | `readiness` RED with a finding that names `SPEC-bad1` | MUTE-readiness, PF23, PF20 |
| `test_w1_26_openspec.py::test_openspec_absent_reported_by_name` | a finding of `openspec-validate` names openspec (PATH without one) | MUTE-openspec, PF20 |
| `…::test_openspec_absent_never_green` | `openspec-validate` RED or YELLOW, and its family not GREEN | MUTE-openspec, PF20 |
| `…::test_openspec_present_and_failing_is_red` | the fake `openspec` is now on the PATH `gov check` runs with; `openspec-validate` RED, exit 3 | MUTE-openspec, PF20 |
| `test_w1_26_decisions.py::test_duplicate_id_flagged` | `core-authority` (the decision checker, called as-is) RED with a finding that names the id and both files; the family RED | MUTE-authority, PF20; **green under PF8**, while the graph check's case fails under PF8 and is green under MUTE-authority: the pair holds two behaviours |

The decision-checker case commits its decisions with the owner's `Role: owner` trailer. Without it the checker
also reports `ACTIVE_UNAPPROVED` for both decisions, which `core-authority` does not carry: a gap DEC-627 already put
on the Wave 2 list (not a new finding).

### `test_w1_26_command.py::test_warning_yellow_does_not_change_exit_code` (commit `e294a521`)

`Rewrite-Reason: the fixture was red, so the case asserted nothing (I2 F7, P-I2-6)`. Rewritten as P-I2-6 (a) says:
every kernel declaration removed, one passing hard-block check and one failing warning; the warning YELLOW with a
finding, the hard-block check GREEN, no check RED, and `ok` with exit 0, unconditionally. Red under PF21 ("only a
warning failed but gov check did not answer ok with exit 0") and PF20.

### DEC-436's unmeasured family and W2-L379's three (commit `0532c84d`)

- `test_w1_26_dec436.py::test_family_only_unmeasured_check_not_green`. `Rewrite-Reason: the declaration was invalid
  YAML, so its check never ran (I2 F3, sample row 9)`. The declaration is now written with `yaml.safe_dump` on the
  green base (whose retrieval-regression declaration is left out, so this check is the family's only one); its own
  entry must be in the result and RED or YELLOW, and the family too. Red under P67C-2 ("the unmeasured check is
  'GREEN'") and PF20.
- W2-L379 (DEC-877 item 5), `Rewrite-Reason: W2-L379: the planted readiness module was never imported, no family's
  name holds readiness, and the commands condition was always true`:
  - `…::test_readiness_check_all_return_value_not_ignored` and `…::test_readiness_check_all_exception_caught` now run
    `gov check` with the project's own code (`run_gov_with_code(project.root, …)`): the copy of this worktree's
    `src/` the project was built with, plus the planted `gov/readiness/checker.py`, which the readiness check imports
    in the `gov` process. The case first asserts the project's `src/gov/check/runner.py` and `command.py` are this
    worktree's, byte for byte. Each asserts the `readiness` check's own entry RED with a finding that names
    `SPEC-test` (the return value) or carries the raised message (the exception), and its family RED. Red under PF22
    (the first only), PF23 (the second only), MUTE-readiness and PF20.
  - `…::test_new_command_module_discovered_by_commands_check`: the reserved commands are the Contract's (the case's
    own note); what the check derives from the repository is which of their modules exist. The project starts with
    no module file for `adopt` (the declared check's finding names it), then the module is planted at
    `src/gov/adopt/command.py` and the check's entry is GREEN with no finding. Red under PF24 and PF20.

## Cases left, and why

- `test_w1_26_planted_defects.py::test_planted_pathmap_defect_file_matches_no_namespace`,
  `…::test_planted_pathmap_defect_file_matches_two_namespaces` and `test_w1_26_dec436.py::test_new_pathmap_namespace_picked_up`:
  they ride with the path-map check's fix, whose carrier is still open (P-I2-4, P-IS-9). Unchanged; they still take
  the `project` fixture.
- `test_w1_26_command.py::test_exit_0_when_all_checks_green`: a retirement (P-I2-6), not this batch's.
- Weak cases of these files that I2 does not name (for example `test_required_missing_row_with_valid_gap_ticket_passes`,
  `test_openspec_present_and_passing`) are not in this batch and are unchanged.
