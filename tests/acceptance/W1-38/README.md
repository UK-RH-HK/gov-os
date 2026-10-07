# W1-38 Acceptance Tests — rulesync adapters and .claude ownership

Ticket: `DAEO-3ef2` · Profile: STANDARD · Covers: CAP-52.a, CAP-52.b, CAP-38.b

## KPI → Test mapping

### Success 1 — rulesync 24.0.0 generates CLAUDE.md, AGENTS.md (<= 1.5k tokens) and .claude/ with hooks, deny rules, roles and skills; OpenSpec commands and vendored skills are registered sources [CAP-52.a, CAP-52.b]

| Test | Covers | Red reason |
|---|---|---|
| `test_role_fields_match_kernel[<role>]` × 6 | CAP-52.b, DEC-352 P-2 | generated agent definition lacks labelled fields from kernel role file |
| `test_skill_body_matches_source[<skill>]` × 8 | CAP-52.a | skill not generated or body differs from kernel source |
| `test_vendored_skills_present` | CAP-52.a, DEC-244 | vendored skill not found under `.claude/skills/` |
| `test_both_files_exist` | CAP-52.a | CLAUDE.md or AGENTS.md not generated |
| `test_agents_md_token_limit` | CAP-52.a | AGENTS.md exceeds 1500 tokens |

### Success 2 — Hook-script stubs referenced by generated settings exist; rulesync generate --check is clean in CI

| Test | Covers | Red reason |
|---|---|---|
| `test_hook_stubs_exist` | CAP-52.a | hook script path in settings does not resolve to a file |
| `test_check_clean_after_generate` | CAP-52.a | `--check` fails after a fresh generation |

### Success 3 — Registers the adapter/model-portability family check: generated adapters match their source for Claude Code and AGENTS.md [CAP-38.b]

| Test | Covers | Red reason |
|---|---|---|
| `test_declaration_file_exists` | CAP-38.b, DEC-438 | `adapter-portability.yaml` not found under `kernel/checks/` |
| `test_declaration_has_required_fields` | CAP-38.b | declaration missing a required field (id/family/tier/severity/command) |
| `test_declaration_family_is_correct` | CAP-38.b | family does not normalise to `adapter-model-portability` |
| `test_declaration_command_is_correct` | CAP-38.b | command is not `python3 -m gov.adapters.portability` |
| `test_portability_module_exists` | CAP-38.b | `src/gov/adapters/portability` module does not exist |

### Failure 1 — generate --delete removes OpenSpec or vendored skills

| Test | Covers | Red reason |
|---|---|---|
| `test_delete_preserves_openspec_commands` | CAP-52.a | OpenSpec commands in `.claude/commands/opsx/` removed by `--delete` |
| `test_delete_preserves_vendored_skills` | CAP-52.a | vendored skills removed by `--delete` |

### Failure 2 — A generated file is hand-edited

| Test | Covers | Red reason |
|---|---|---|
| `test_hand_edit_claude_md` | CAP-52.a | `--check` does not detect hand-edited CLAUDE.md |
| `test_hand_edit_agents_md` | CAP-52.a | `--check` does not detect hand-edited AGENTS.md |
| `test_hand_edit_role_file` | CAP-52.b | `--check` does not detect hand-edited role definition |
| `test_hand_edit_skill_file` | CAP-52.a | `--check` does not detect hand-edited skill |

### Edge cases — missing files and source changes

| Test | Covers | Red reason |
|---|---|---|
| `test_missing_agents_md_fails_check` | CAP-38.b | `--check` silently passes when AGENTS.md is deleted |
| `test_portability_check_fails_on_missing_agents_md` | CAP-38.b | portability check passes despite missing AGENTS.md |
| `test_source_change_fails_check` | CAP-52.a | `--check` does not detect source change without regeneration |

### Edge cases — portability check

| Test | Covers | Red reason |
|---|---|---|
| `test_rulesync_absent_not_green` | CAP-38.b, DEC-425 | portability check is GREEN with absent rulesync |
| `test_rulesync_bin_missing_file` | CAP-38.b | `RULESYNC_BIN` missing not reported as "not found" |
| `test_version_from_project_pin_not_env` | CAP-38.b | version check skipped when `RULESYNC_EXPECTED_VERSION` unset; expected version must come from project's registered pin |
| `test_timeout_handling` | CAP-38.b | unhandled exception when rulesync hangs |
| `test_agents_md_always_checked` | CAP-38.b | portability check skips agentsmd target when file missing; targets must come from project config |
| `test_no_invented_findings` | CAP-38.b | check invents file names not in rulesync output |

## Covers mapping

| Covers ID | Tests |
|---|---|
| CAP-52.a | `test_skill_body_matches_source` × 8, `test_vendored_skills_present`, `test_both_files_exist`, `test_agents_md_token_limit`, `test_hook_stubs_exist`, `test_check_clean_after_generate`, `test_delete_preserves_openspec_commands`, `test_delete_preserves_vendored_skills`, `test_hand_edit_claude_md`, `test_hand_edit_agents_md`, `test_hand_edit_skill_file`, `test_source_change_fails_check` |
| CAP-52.b | `test_role_fields_match_kernel` × 6, `test_hand_edit_role_file` |
| CAP-38.b | `test_declaration_file_exists`, `test_declaration_has_required_fields`, `test_declaration_family_is_correct`, `test_declaration_command_is_correct`, `test_portability_module_exists`, `test_missing_agents_md_fails_check`, `test_portability_check_fails_on_missing_agents_md`, `test_rulesync_absent_not_green`, `test_rulesync_bin_missing_file`, `test_version_from_project_pin_not_env`, `test_timeout_handling`, `test_agents_md_always_checked`, `test_no_invented_findings` |

## `needs_rulesync` tests

Tests marked `@pytest.mark.needs_rulesync` require the rulesync binary at
`/home/usain/.local/bin/rulesync` (override with `RULESYNC_BIN`). They are
skipped automatically when rulesync is not installed. The lead runs those with
`pytest -m needs_rulesync`.

Tests that only inspect repository files (e.g. `TestCheckDeclaration`) run
without rulesync.

## Test design

- **39 test cases** across 11 test classes.
- Every generation runs in a temporary directory created by pytest's `tmp_path`.
- Projects are built by copying the template's `.rulesync/` sources file by file
  and placing kernel hook scripts at the adoption path.
- Token counting: `math.ceil(len(text) / 4)`.
- Field comparison uses W1-33's whitespace-collapsed labelled-field parser.
- Portability check edge cases use mock rulesync scripts to test behaviour when
  the binary is absent, hanging, or reporting a wrong version.
- OpenSpec commands are placed in `.claude/commands/opsx/` (the output, not the
  sources), simulating `openspec init` (DEC-074 Q7).

## Packages

- **W1-40 (CI workflow)**: The CI workflow must include a step that runs
  `rulesync generate --check --targets claudecode,agentsmd --features
  rules,hooks,permissions,subagents,commands,skills` and fails the pipeline
  when exit code is non-zero. This verifies KPI success 2.
- **W1-42 (runtime loading)**: Whether Claude Code loads the generated roles,
  hooks and skills at runtime is a session-level integration; file-level tests
  cover as much as they can.
