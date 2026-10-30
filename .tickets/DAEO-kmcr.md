---
id: DAEO-kmcr
status: open
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-23
tags: [wave-2, implementation, full]
wbs_id: W2-23
title: Adoption safety on a real repository
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-49o5
allowed_paths:
- src/gov/adopt/**
- src/gov/adapters/**
- template/governance/project/path-map.yaml
- tests/unit/adopt/**
- tests/unit/adapters/**
- fixtures/adopt/**
- CLAUDE.md
- AGENTS.md
- .claude/settings.json
kpis:
  success:
  - Rollback never deletes an untracked file it did not create; it refuses or preserves [W2-H036].
  - Adapter generation merges a programme's own CLAUDE.md, AGENTS.md and .claude/settings.json instead of overwriting them, keeping their order [W2-H050, W2-M232, W2-M312, W2-M229].
  - The A8 dependency proof finds every listed citation form [W2-H035, W2-M225].
  - A failed or interrupted batch leaves a resumable record and no half-staged state [W2-M219, W2-M220, W2-M224].
  - A project without .gitleaks.toml, or with a .gitignore that omits .gov-runtime/, is set up, not refused late [W2-M217, W2-M218, W2-M307].
  - Every command and hook works in a repository whose path contains a space (~/EXAMIN APP).
  - A move to a target that no namespace holds is refused before it runs [W2-M216].
  failure:
  - The fixture's own instruction files and every untracked file survive an adoption and its rollback byte for byte.
profile: FULL
sources:
- DEC-729
- DEC-954
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-23/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- W2-H036
- W2-H035
- W2-H050
list_rows:
- W2-H035
- W2-H036
- W2-H050
- W2-I014
- W2-L181
- W2-L184
- W2-L185
- W2-L186
- W2-L187
- W2-L188
- W2-L189
- W2-L192
- W2-L205
- W2-L264
- W2-L265
- W2-M042
- W2-M214
- W2-M216
- W2-M217
- W2-M218
- W2-M219
- W2-M220
- W2-M221
- W2-M223
- W2-M224
- W2-M225
- W2-M226
- W2-M229
- W2-M232
- W2-M237
- W2-M261
- W2-M277
- W2-M300
- W2-M307
- W2-M311
- W2-M312
- W2-M319
---
# W2-23 Adoption safety on a real repository

**DEC-954:** depends on W2-16 (DAEO-49o5), not W2-18 (Wave 3). It shares src/gov/adopt/ with W2-52 and W2-88, split by file; whichever merges second merges back.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-23), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/adopt/**`, `src/gov/adapters/**`, `template/governance/project/path-map.yaml`, `tests/unit/adopt/**`, `tests/unit/adapters/**`, `fixtures/adopt/**` (new: a repository with its own `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, untracked files, and a path with a space).
- **KPIs, success:**
  - Rollback never deletes an untracked file it did not create; it refuses or preserves [W2-H036].
  - Adapter generation merges a programme's own `CLAUDE.md`, `AGENTS.md` and `.claude/settings.json` instead of overwriting them, keeping their order [W2-H050, W2-M232, W2-M312, W2-M229].
  - The A8 dependency proof finds every listed citation form [W2-H035, W2-M225].
  - A failed or interrupted batch leaves a resumable record and no half-staged state [W2-M219, W2-M220, W2-M224].
  - A project without `.gitleaks.toml`, or with a `.gitignore` that omits `.gov-runtime/`, is set up, not refused late [W2-M217, W2-M218, W2-M307].
  - Every command and hook works in a repository whose path contains a space (`~/EXAMIN APP`).
  - A move to a target that no namespace holds is refused before it runs [W2-M216].
- **KPIs, failure:** the fixture's own instruction files and every untracked file survive an adoption and its rollback byte for byte.
