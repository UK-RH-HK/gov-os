# W2-153 evidence: the role template delivered at launch (W2-128 TPL-4)

Ticket `DAEO-8s85`, engineer, branch `w2/W2-153` (from integrate with the designer's cases, TESTS-READY
`0c73fd5a2cbe`). Unit tests: `tests/unit/launch/test_w2_153_template.py` (26) and
`tests/unit/adapters/test_w2_153_portability.py` (22), all passing (48, with the opt-in rows).

| KPI line | what was built | how it is verified |
|---|---|---|
| S1 | `launcher.ROLE_TEMPLATES` (the role -> template map) and `template_args`: every worker and lead launch gets `--append-system-prompt-file <root>/.claude/templates/<stem>.md` (absolute, real root) after the caller's arguments; a missing file (or a folder in its place) raises `GovError LAUNCH_NO_TEMPLATE` naming the path, before the CLI, the gate or the temp folder | `test_the_flag_comes_after_the_callers_arguments_by_absolute_path[*]` (7 roles), `test_a_missing_template_refuses_naming_the_path_and_starts_nothing[*]`, `test_a_template_that_is_a_folder_refuses` |
| S2 | `launch_now.sh`: the absolute `claude` call kept (D-4); `TEMPLATE=/home/usain/gov-os-worktrees/$W2/.claude/templates/role-lead.md`; a missing file prints `LAUNCH_NO_TEMPLATE: ... <path>` and exits 2 before `exec`; the flag is one added line after `--settings` | `test_the_dispatchers_lead_form_passes_the_lead_template` and `..._refuses_without_the_template` (the script run on a copy whose absolute paths point into tmp_path, with a stub `claude`) |
| S3 | The six `.rulesync/subagents/<role>.md` and `template/.rulesync/subagents/<role>.md`: their rulesync front matter as on integrate, plus `skills:` (the ticket's lists, D-1), then the body of the kernel role template (D-2). `portability._kernel_findings` compares a role that has a template with that composition (body of the template, the `skills:` list) in place of the role file's text; the role file's Tools field is still compared with `claudecode.tools`. The test designer's list is `[test-design]`: W2-128's round 2a reconciled that skill with DEC-963, so the "until W2-128" exception and its comments are gone (switch-over round) | `test_w2_153_portability.py` S3 cases; `test_this_repositorys_sources_are_the_composition`; the existing `test_portability.py` unchanged and green |
| S4 | `portability._template_findings`: `TEMPLATE_COPY_MISSING` / `TEMPLATE_COPY_DIFFERS` for each of the eight copies whose kernel template exists; `python3 -m gov.adapters.portability --write-templates <dir>` writes exactly the eight copies into `<dir>`, **the copies' folder itself** (D-3: the ACT runs it with `.claude/templates`), and writes nothing if a kernel template is missing | `test_one_changed_and_one_missing_copy_are_two_findings`, `test_the_writer_writes_exactly_the_eight_copies` (subprocess, temporary folder), `test_the_written_copies_pass_the_check` |
| S5 | Not this branch: the ACT (ACT-CLAUDE-COPIES, rebuilt on integrate after merge) installs the copies with S4's writer and regenerates `.claude/agents/` with rulesync, in the same ACT that makes S1 and S2 live. No `.claude/` file is committed here (DEC-315) | the ACT's record |
| F1 | No session starts without its template | S1's and S2's refusal cases |
| F2 | The argv is otherwise unchanged: the CLI, `--settings <json>`, the caller's arguments, then the one flag; the dispatcher's exec lines are integrate's with one line added | `test_the_launch_is_otherwise_what_it_was[*]`, `test_the_dispatchers_lead_form_is_otherwise_the_same_command` |

**Portability on this branch** (`python3 -m gov.adapters.portability`, rulesync 24.0.0): no finding on any
`.rulesync/subagents/` source. Expected until the ACT: 8 `TEMPLATE_COPY_MISSING`, 6 `GENERATED_DIFFERS`
(`.claude/agents/*.md`), and the 2 `SOURCE_DIFFERS` of the discovery and retrieval skills that integrate already has.

**rulesync and `skills:`:** rulesync 24.0.0 drops a top-level `skills:` from the generated `.claude/agents/<role>.md`;
it passes `skills` through when the key sits under `claudecode:` (tried on a temporary copy). As built, the sources
follow S3's text (a top-level list), so the generated agents carry no `skills:` after the ACT.

**Fix round (DAEO-8s85, the CTO's decision after the build, DEC-1112 (3)):** the 12 sources hold the list under
`claudecode: skills:`; portability reads it there and reports a top-level `skills:` as `SOURCE_DIFFERS` (unit cases
`test_a_top_level_skills_list_is_a_finding[*]`). `rulesync generate --targets claudecode --features subagents` from a
temporary copy of `.rulesync/` into an empty folder writes 6 agents, each with its `skills:` (engineer
`test-driven-development`, auditor `audit`, product-spec `change`, research `discovery`, orchestrator `orchestration`;
the test designer `[]` until W2-128). The launcher's existing unit tests (`test_runs.py`, `test_w1_28.py`,
`test_w1_32.py`, `test_w2_136_plan_check.py`) write the role's template copy in their fixtures; W2-136's argv-end case
allows the one appended flag. Acceptance 51/51; W2-128 92/92.

**Switch-over round (2026-11-10):** W2-128's round 2a is merged, so the test designer's sources and
`portability.ROLE_SKILLS` list `test-design`; the exception and its comments are dropped.

**S3 amended (2026-11-10, the CTO, DEC-1112 (3)):** the composed agents lacked the role file's labelled fields.
- `portability.compose(root, role) -> str` is the expected source's full text: the source's own rulesync front matter
  as written (with `claudecode.skills`), a blank line, the role template's body, one blank line, and the kernel role
  file's body (its front matter, if any, stripped by `_split`). A role without a template: the role file's body alone.
  It raises `FileNotFoundError` without a kernel, role file or source.
- `_kernel_findings` compares each role source's body with `compose()`'s (the blank lines after the front matter stay
  the one tolerated difference). A `SOURCE_DIFFERS` names both origins: "differs from its composition of
  `<template>` and `<role file>`". The skills, tools and `TEMPLATE_COPY_*` checks are unchanged.
- The twelve sources were written from `compose()` by a one-off scratch script: each only gained the role file's body.
- Verified: `tests/unit/adapters/test_w2_153_compose.py` (15) and `test_w2_153_portability.py` (18), 33 passed;
  `tests/unit/adapters` and `tests/unit/launch` 314 passed (126 left out by the repository's opt-in lists, none by
  the real-model exclusion); acceptance `tests/acceptance/W2-153` 66 passed; portability with rulesync 24.0.0: only
  the six `GENERATED_DIFFERS` for `.claude/agents/*.md`, which ACT-CLAUDE-COPIES-3 regenerates; W1-33 21 failed,
  90 passed, 1 skipped, all 21 in `test_w1_33_agent_definitions.py`, which reads `.claude/agents/` (red until the ACT).
- `rulesync generate --targets claudecode --features subagents` from a temporary copy into an empty folder writes the
  six agents; the engineer's carries `skills: [test-driven-development]` and the labels Purpose, Allowed paths, Tools,
  Network, Model tier, Authority level, Handoff format and Permission classes.
