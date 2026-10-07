# W1-38 Acceptance Tests — rulesync adapters and .claude ownership

Ticket: `DAEO-3ef2` · Profile: STANDARD · Covers: CAP-52.a, CAP-52.b, CAP-38.b

## KPI → Test mapping

### Success 1 — rulesync 24.0.0 generates CLAUDE.md, AGENTS.md (<= 1.5k tokens) and .claude/ with hooks, deny rules, roles and skills; OpenSpec commands and vendored skills are registered sources [CAP-52.a, CAP-52.b]

| Test | Covers | Red reason |
|---|---|---|
| `test_generate_produces_claude_md` | CAP-52.a | *(behavioral, passes)* |
| `test_generate_produces_agents_md_within_token_limit` | CAP-52.a | *(behavioral, passes)* |
| `test_generate_produces_settings_with_hooks` | CAP-52.a | *(behavioral, passes)* |
| `test_generate_produces_settings_with_deny_rules` | CAP-52.a | *(behavioral, passes)* |
| `test_generate_produces_role_agents` | CAP-52.a, CAP-52.b | *(behavioral, passes)* |
| `test_generate_produces_skills` | CAP-52.a | *(behavioral, passes)* |
| `test_openspec_commands_are_registered` | CAP-52.a | *(behavioral, passes)* |
| `test_vendored_skills_are_registered` | CAP-52.a | *(behavioral, passes)* |
| `test_template_rulesync_dir_exists` | CAP-52.a | `template/.rulesync/` does not exist |
| `test_project_rulesync_dir_exists` | CAP-52.a | `.rulesync/` does not exist |
| `test_template_rulesync_has_hooks` | CAP-52.a | `template/.rulesync/hooks.jsonc` does not exist |
| `test_template_rulesync_has_permissions` | CAP-52.a | `template/.rulesync/permissions.jsonc` does not exist |
| `test_template_rulesync_has_rules` | CAP-52.a | `template/.rulesync/rules/` does not exist |
| `test_template_rulesync_has_subagents` | CAP-52.a, CAP-52.b | `template/.rulesync/subagents/` does not exist |
| `test_template_rulesync_has_skills` | CAP-52.a | `template/.rulesync/skills/` does not exist |

### Success 2 — Hook-script stubs referenced by generated settings exist; rulesync generate --check is clean in CI

| Test | Covers | Red reason |
|---|---|---|
| `test_hook_script_stubs_exist` | CAP-52.a | *(behavioral, passes)* |
| `test_generate_check_is_clean` | CAP-52.a | *(behavioral, passes)* |
| `test_generate_check_fails_when_stale` | CAP-52.a | *(behavioral, passes)* |
| `test_template_rulesync_has_hooks` | CAP-52.a | `template/.rulesync/hooks.jsonc` does not exist |

### Success 3 — Registers the adapter/model-portability family check: generated adapters match their source for Claude Code and AGENTS.md [CAP-38.b]

| Test | Covers | Red reason |
|---|---|---|
| `test_check_declaration_exists` | CAP-38.b | no `adapter-portability*.yaml` under checks/ |
| `test_check_declaration_fields` | CAP-38.b | no adapter-portability check declaration |
| `test_check_command_module_exists` | CAP-38.b | `src/gov/adapters/` does not exist |
| `test_portability_check_green_when_matching` | CAP-38.b | portability module does not exist |
| `test_portability_check_fails_when_file_hand_edited` | CAP-38.b | portability module does not exist |
| `test_portability_check_fails_when_file_missing` | CAP-38.b | portability module does not exist |
| `test_portability_check_unmeasured_when_rulesync_absent` | CAP-38.b | portability module does not exist |
| `test_portability_check_fails_when_rulesync_wrong_version` | CAP-38.b | portability module does not exist |
| `test_portability_check_fails_when_source_empty` | CAP-38.b | portability module does not exist |

### Failure 1 — generate --delete removes OpenSpec or vendored skills

| Test | Covers | Red reason |
|---|---|---|
| `test_delete_preserves_openspec_commands` | CAP-52.a | *(behavioral, passes)* |
| `test_delete_preserves_vendored_skills` | CAP-52.a | *(behavioral, passes)* |
| `test_template_rulesync_has_commands` | CAP-52.a | `template/.rulesync/commands/` does not exist |

### Failure 2 — A generated file is hand-edited

| Test | Covers | Red reason |
|---|---|---|
| `test_agents_md_hand_edited_is_detected` | CAP-38.b | portability module does not exist |
| `test_settings_hand_edited_is_detected` | CAP-38.b | portability module does not exist |
| `test_generate_check_fails_when_stale` | CAP-52.a | *(behavioral, passes)* |

## Covers mapping

| Covers ID | Failing tests |
|---|---|
| CAP-52.a | `test_template_rulesync_dir_exists`, `test_project_rulesync_dir_exists`, `test_template_rulesync_has_hooks`, `test_template_rulesync_has_permissions`, `test_template_rulesync_has_rules`, `test_template_rulesync_has_skills`, `test_template_rulesync_has_commands` |
| CAP-52.b | `test_template_rulesync_has_subagents` |
| CAP-38.b | `test_check_declaration_exists`, `test_check_declaration_fields`, `test_check_command_module_exists`, `test_portability_check_green_when_matching`, `test_portability_check_fails_when_file_hand_edited`, `test_portability_check_fails_when_file_missing`, `test_portability_check_unmeasured_when_rulesync_absent`, `test_portability_check_fails_when_rulesync_wrong_version`, `test_portability_check_fails_when_source_empty`, `test_agents_md_hand_edited_is_detected`, `test_settings_hand_edited_is_detected` |

## Test design

Tests are split into two categories:

1. **Behavioral tests** (13 passing): build a temporary project under `tmp_path`, populate a valid `.rulesync/` source tree, run `rulesync generate`, and assert the output. These verify that rulesync can produce the expected artifacts. They pass because rulesync 24.0.0 is installed and works correctly with valid source trees.

2. **Implementation tests** (19 failing): verify that the engineer has created the required source tree (`template/.rulesync/`, `.rulesync/`), the portability check module (`src/gov/adapters/portability`), and the check declaration (`template/governance/kernel/checks/adapter-portability*.yaml`). These fail because the implementation does not exist yet.

## Packages

- **W1-42**: whether Claude Code loads the generated roles, hooks and skills at runtime — the file-level tests cover as much as they can; runtime loading is a session-level integration that W1-42's exit run tests.
