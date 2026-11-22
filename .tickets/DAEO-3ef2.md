---
id: DAEO-3ef2
status: closed
deps: [DAEO-78bn, DAEO-zsvl, DAEO-xog0, DAEO-0i6h, DAEO-skiy, DAEO-yvzh]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-38
tags: [wave-1, config, standard]
wbs_id: W1-38
title: rulesync adapters and .claude ownership
class: config
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-78bn
- DAEO-zsvl
- DAEO-xog0
- DAEO-0i6h
- DAEO-skiy
- DAEO-yvzh
allowed_paths:
- template/.rulesync/**
- .rulesync/**
- src/gov/adapters/**
- tests/unit/adapters/**
- template/governance/kernel/checks/adapter-portability*
kpis:
  success:
  - rulesync 24.0.0 generates CLAUDE.md, AGENTS.md (<= 1.5k tokens) and .claude/ with hooks, deny rules, roles and skills; OpenSpec commands and vendored skills are registered sources [CAP-52.a, CAP-52.b]
  - Hook-script stubs referenced by generated settings exist; rulesync generate --check is clean in CI
  - 'Registers the adapter/model-portability family check: generated adapters match their source for Claude Code and AGENTS.md [CAP-38.b]'
  failure:
  - generate --delete removes OpenSpec or vendored skills
  - A generated file is hand-edited
profile: STANDARD
sources:
- G-11
- G-15
- DEC-022
- DEC-074
- CAP-52
- CAP-38
- MR-5
est_loc: 50
acceptance_tests:
  path: tests/acceptance/W1-38/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-38 rulesync adapters and .claude ownership

One adapter source for Claude Code and AGENTS.md.

## Fix: no unfilled slot in a generated agent file (F11, fixes-015a)

Found 2026-11-22: the generated `.claude/agents/*.md`, the `.rulesync/subagents/*.md` sources and the kit's `template/.rulesync/subagents/*.md` held `{CMD:...}` and `{ID}`-style slots that only the brief builder fills from a ticket; a role file is written for no ticket. No test caught it, and the portability check reported only `GENERATED_DIFFERS`. Required: composition fills or drops every slot; the check refuses a generated agent file holding one and names it; the checked-in generated files hold none. Kind: a fix, no new ticket; the ticket stays closed. Failing tests first: `tests/acceptance/W1-38/test_w1_38_fix_slots.py` (3 cases); code `src/gov/adapters/portability.py` (`SLOT`, `fill_slots`, used by `compose`; finding `GENERATED_SLOT` in the generated comparison); the six role sources with a template, their kit copies and `.claude/agents/*.md` regenerated; unit `tests/unit/adapters/test_w2_153_compose.py`. `{CMD:name}` reads "the `name` command of your brief", a key a known wording or `<key>`. Result: the 3 cases green; `tests/unit/adapters` and `tests/unit/hooks` green (381 passed with the fix files). Two things are for the test designer: `tests/acceptance/W2-153/test_w2_153_sources.py::test_s3_each_role_source_is_...` (12 cases) compares a source with the template's raw body, slots included, so it contradicts this fix; and `gov accept W1-38` refuses with ACCEPT_MAP_UNREADABLE (the README's `fix-F11` rows).
