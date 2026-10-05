# W1-33 acceptance tests: Wave 1 role definitions

Ticket `DAEO-xog0` (`W1-33`), profile STANDARD. Written by the Independent Test Designer before implementation
(MR-3, DEC-069). Covers ids: `CAP-22.a`, `CAP-58.b`.

Run: `python3 -m pytest tests/acceptance/W1-33 -q -p no:cacheprovider`

The ticket delivers no code. The tests read committed files (the kernel role files, the roster, the definitions
under `.claude/agents/`) and ask the guard and the launcher, in a temporary copy of the project, for the decisions
the definitions describe. No session is started, no network is used, nothing is installed.

## Files

| File | Tests | Reads |
|---|---|---|
| `test_w1_33_kernel_role_files.py` | 52 | `template/governance/kernel/roles/<role>.md` |
| `test_w1_33_roster.py` | 13 | `governance/project/roster.yaml`, the `role:` of every ticket |
| `test_w1_33_guard_and_launcher.py` | 17 | the guard's decisions and the launcher's built settings (W1-46's support code) |
| `test_w1_33_agent_definitions.py` | 33 | `.claude/agents/<role>.md`, and each one's kernel role file |
| `w1_33_support.py`, `conftest.py` | | the field reader, the checks, the fixtures |

`test_w1_33_agent_definitions.py` holds every test that reads `.claude/agents/`. A headless session may be refused a
write there (DEC-312, DEC-315), so the definitions may be placed later than the role files and the roster. Report
this file's result apart from the other three.

## KPI lines and their tests

| KPI line | Tests |
|---|---|
| **Success 1** [CAP-22.a]: five roles, each with the six fields | `kernel_role_files`: `test_the_role_has_a_kernel_role_file_with_the_six_fields[role]`, `test_the_research_role_file_is_read_in_this_form` · `roster`: `test_the_roster_holds_the_five_roles_and_research_and_no_other`, `test_the_entry_names_the_role_s_kernel_role_file_and_its_definition[role]`, `test_every_ticket_s_role_is_in_the_roster` (MR-5) · `agent_definitions`: `test_the_definition_has_the_six_fields[role]` |
| **Success 2**: only the test designer pattern includes `tests/acceptance/**`; the auditor is read-only; only the orchestrator may install, after owner approval (DEC-083), except research (DEC-163) | `kernel_role_files`: `test_the_test_designer_pattern_includes_the_acceptance_tests`, `test_no_other_pattern_includes_the_acceptance_tests[role]`, `test_the_auditor_is_read_only_except_its_ticket_s_report_path`, `test_the_orchestrator_may_install_only_after_owner_approval`, `test_no_other_role_may_install[class-role]`, `test_the_research_exception_is_stated_by_the_research_role_file_alone` · `guard_and_launcher`: `test_only_the_test_designer_may_write_the_acceptance_tests[role]`, `test_the_auditor_writes_only_the_report_path_of_its_own_ticket`, `test_an_install_asks_for_the_orchestrator_and_is_denied_to_every_other_role[role]` · `agent_definitions`: `test_the_definition_states_what_the_kpis_require_of_the_role[role]` |
| **Success 3** [CAP-58.b]: the permission classes; the launcher's network profile, named by the definition | `kernel_role_files`: `test_the_role_maps_every_permission_class[role]`, `test_the_role_maps_the_classes_as_the_contract_says[role]`, `test_a_launched_worker_names_the_launcher_s_empty_network_profile[role]`, `test_the_research_role_file_names_the_research_allowlist` · `roster`: `test_a_launched_worker_s_entry_names_its_session_and_the_empty_profile[role]`, `test_a_role_the_launcher_does_not_start_has_no_launched_session[role]` · `guard_and_launcher`: `test_the_launcher_gives_the_role_an_empty_network_profile[role]`, `test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker[role]` · `agent_definitions`: `test_the_definition_states_what_the_kpis_require_of_the_role[role]` |
| **Success 4** [CAP-22.a]: the generated definitions replace the minimal ones; the orchestrator definition states its write scope (DEC-156) | `agent_definitions`: `test_the_definition_is_no_longer_the_minimal_one[role]`, `test_the_definition_keeps_the_subagent_type_name_of_the_role[role]`, `test_the_definition_agrees_with_its_kernel_role_file[role]`, `test_the_orchestrator_definition_states_its_write_scope`, `test_there_is_one_definition_per_role_and_the_research_one` · `kernel_role_files`: `test_the_orchestrator_role_file_states_its_write_scope` · `guard_and_launcher`: `test_the_orchestrator_may_write_anywhere_else_in_the_repository` |
| **Success 5**: the research role of W1-46 is left in place (DEC-163) | `kernel_role_files`: `test_the_research_role_file_is_unchanged` · `roster`: `test_the_research_entry_is_unchanged` · `agent_definitions`: `test_the_research_definition_is_unchanged` |
| **Failure 1**: a role lacks any required field | `kernel_role_files`: `test_a_role_file_without_one_required_field_is_found[role]`, `test_a_required_field_with_no_text_is_found[role]` · `agent_definitions`: `test_a_definition_without_one_required_field_is_found[role]` |
| **Failure 2**: an implementer role pattern covers `tests/acceptance/**` | `kernel_role_files`: `test_an_implementer_pattern_that_covers_the_acceptance_tests_is_found[pattern-role]`, and `test_no_other_pattern_includes_the_acceptance_tests[engineer]`, `[product-spec]` · `guard_and_launcher`: `test_only_the_test_designer_may_write_the_acceptance_tests[engineer]`, `[product-spec]` |

The two failure lines describe a faulty file. Their tests take the role's own delivered file, make the fault in a
copy held in memory (one field taken out, or the pattern replaced by one that covers the acceptance tests) and
assert that the check names the fault. They are red until the file exists and is complete.

## The expected red reason

Run before implementation: **86 failed, 29 passed**.

| File | Failed | Passed | Red reason |
|---|---|---|---|
| `test_w1_33_kernel_role_files.py` | 48 | 4 | `template/governance/kernel/roles/<role>.md does not exist`, for each of the five roles |
| `test_w1_33_roster.py` | 12 | 1 | `governance/project/roster.yaml has no entry for <role> (it holds ['research'])`; the tickets' roles are not in the roster |
| `test_w1_33_agent_definitions.py` | 26 | 7 | the definition is still W1-05's minimal one: it has none of the six fields; its role file does not exist |
| `test_w1_33_guard_and_launcher.py` | 0 | 17 | none: green already (see below) |

Green before implementation, and they must stay green:

- the 17 tests of `test_w1_33_guard_and_launcher.py`: W1-02, W1-04, W1-45 and W1-46 built these decisions. A
  definition grants nothing by itself, so the suite checks the statement and the decision it describes together;
- the three "unchanged" tests of KPI success 5, and the three tests that read the research role file in the form
  these tests use;
- `test_the_definition_keeps_the_subagent_type_name_of_the_role[role]` (5) and
  `test_there_is_one_definition_per_role_and_the_research_one`: W1-05's definitions already have the right names.

## The form the tests read

**A kernel role file** is `template/governance/kernel/roles/<role>.md`, where `<role>` is the name the guard
knows: `orchestrator`, `product-spec`, `independent-test-designer`, `engineer`, `independent-auditor`. Its form is
the one `research.md` already has (W1-46): a Markdown list whose items start with a bold label.

```markdown
- **Purpose:** ...
- **Allowed paths:** ...
- **Tools:** ...
- **Network:** ...
- **Model tier:** ...
- **Authority level:** ...
- **Handoff format:** ...
- **Permission classes:**
  - `WRITE_REPO_SCOPED`: ...
```

- A field is one labelled item: its text runs to the next labelled item, a heading, or a blank line followed by
  text that is not indented. Indented sub-items belong to the field.
- Labels are matched without regard to case. The six required labels use the patterns of W1-46's tests: Purpose;
  Allowed paths (or "Allowed-path pattern"); Tools; Model tier; Authority level; Handoff format.
- **Network** is required for engineer, independent-test-designer and independent-auditor: it says the grant comes
  from the launcher's profile and that the profile is empty (DEC-158).
- **Permission classes** is required for all five. Each class name of CAP-58.b appears in it, followed by its
  disposition: the first of the words `denied` (or `deny`), `allowed` (or `granted`), `ask` after the name. Names
  written together (`` `PACKAGE_INSTALL` / `SYSTEM_INSTALL`: denied ``) share the text after the last of them. A
  family (`NETWORK_*`, `DB_*`, `CLOUD_*`, `DEPLOY_*`) is the starred name or any name with that prefix.

| Class | What the tests require |
|---|---|
| `WRITE_REPO_SCOPED` | its text names `allowed_paths` |
| `PACKAGE_INSTALL` | orchestrator: `ask`, naming the owner and DEC-083; every other role: `denied` |
| `SYSTEM_INSTALL` | orchestrator: its text names DEC-083 (no disposition is pinned: `sudo` stays with the owner); every other role: `denied` |
| `SECRET_READ` | `denied` |
| `READ_REPO`, `RUN_TESTS` | `allowed` (or `granted`) |
| `NETWORK_*`, `DB_*`, `CLOUD_*`, `CI_TRIGGER`, `DEPLOY_*` | engineer, test designer, auditor: `denied`; orchestrator, product-spec: any stated disposition (package DP-3) |

**The allowed-path pattern.**

- independent-test-designer: the field contains `tests/acceptance/**`.
- Every other role: each sentence of the field that names `tests/acceptance` excludes it (except, excluding, never,
  not, no, outside, denied, refused, without). A sentence ends at `.` or `;`.
- orchestrator: the field says the scope is anywhere in the repository (anywhere, whole, entire, any path, every
  path) and excepts `tests/acceptance/**` (DEC-156).
- independent-auditor: the field says read-only, and names the exception, the report path its own ticket allows
  (DEC-112).

**The roster** keeps the form of the research entry: `roles.<role>` with `role_file` and `agent`. The three
launched workers also have `session: gov launch <role> <ticket>` and a `network_profile` whose value contains
`empty`. The orchestrator and product-spec name no `gov launch` session. The roster holds six entries: the five
and research.

**A definition** is `.claude/agents/<role>.md`: frontmatter with `name: <role>` and a `description`, then the
fields. "Generated" is checked as agreement with the kernel role file: the same labelled fields, each with the same
text once whitespace is collapsed. Text outside the labelled items (a title, an introduction) is free. The words
"minimal definition" are gone.

## How the open points were settled

1. **Generated definitions.** DEC-066: roles are "generated by rulesync from kernel role files plus a project
   roster". MR-5 names W1-33 and W1-38 as providers, and W1-38 ("rulesync adapters and .claude ownership") depends
   on W1-33. W1-33's `allowed_paths` hold no code. So for W1-33 the kernel role file is the source, the definition
   is derived from it, and the test shows agreement field by field. No test asks for a generator. See DP-1.
2. **The six fields** and their labels: those of `research.md` and of `ROLE_FILE_PARTS` in
   `tests/acceptance/W1-46/test_w1_46_research_role.py`.
3. **Installs and the read-only auditor.** DEC-083: install commands are "an `ask` permission for the orchestrator
   role only and are denied for every other role". DEC-112: the auditor is "read-only everywhere except the report
   path its own ticket allows". Each is a statement in the role file, and a decision of the guard asked through the
   committed PreToolUse commands.
4. **The roster.** The five are checked as entries of `governance/project/roster.yaml`, which holds six: the five
   and research (DEC-163). Every ticket's `role` is one of the six (MR-5).
5. **Permission classes.** The names are those CAP-58.b gives. It gives four families only by prefix; the tests
   accept the starred name or any member. See DP-2.
6. **Earlier tests.** None is revised. `tests/acceptance/W1-05/test_w1_05_role_subagents.py` reads only `name` and
   `description`; `tests/acceptance/W1-46/test_w1_46_research_role.py` reads only the research files. Neither pins
   the wording of the minimal definitions.

## Decision packages

**DP-1. What "generated" means before the rulesync adapters exist.**
- Question: is a definition that agrees field by field with its kernel role file, placed by hand, a "generated
  definition" for W1-33?
- Why now: KPI success 4 and 5 say "generated"; the generator is W1-38's.
- Options: (a) yes; W1-38 later produces the same files from the same sources, and this suite's agreement test
  keeps holding. (b) no; W1-33 waits for W1-38, or gains code paths. (c) the definition only points to its role
  file, as `.claude/agents/research.md` does, and carries no fields.
- Impact: (a) none, the tests assume it. (b) a ticket change and a dependency cycle (W1-38 depends on W1-33).
  (c) contradicts MR-5 ("a generated subagent definition with purpose, allowed-path pattern, ...");
  `test_the_definition_has_the_six_fields` and the agreement test would be rewritten.
- Reversibility: high; one test. Cost: none for (a).
- Recommendation: (a). Confidence: medium-high.

**DP-2. The member names of the `NETWORK_*`, `DB_*`, `CLOUD_*` and `DEPLOY_*` families.**
- Question: must a role file list each member class of Framework §32, or may it map the family as CAP-58.b writes
  it?
- Why now: KPI success 3 says "maps the Framework §32 permission classes"; the Contract and the register give no
  member names.
- Options: (a) the family as written in CAP-58.b is enough (the tests). (b) every member is listed; the names come
  from Framework v4.1.2 §32 "Tool permissions" in the archived sources, which the test designer does not read.
- Impact: (b) adds one list of names to `w1_33_support.py` and lines to each role file.
- Reversibility: high. Cost: small.
- Recommendation: (a) for Wave 1. Confidence: medium.

**DP-3. The network, database, cloud, CI-trigger and deploy classes for the orchestrator and product-spec.**
- Question: which of these does each of the two definitions grant?
- Why now: KPI success 3 says "denied unless granted". DEC-158 says the orchestrator "is unrestricted, being
  unsandboxed", and names product-spec only "when it runs experiments". No source says whether the orchestrator's
  definition grants a `NETWORK_*` class, or `CI_TRIGGER` and `DEPLOY_*` for pushes and CI.
- Options: (a) the tests pin nothing: each class has a stated disposition (the tests). (b) the orchestrator grants
  `NETWORK_*` and the rest are denied to both. (c) all denied to both.
- Impact: (b) or (c) adds one line per class to `class_faults`.
- Reversibility: high. Cost: small.
- Recommendation: (a) now; the implementer writes what DEC-158 supports and the audit reviews it.
  Confidence: medium.
