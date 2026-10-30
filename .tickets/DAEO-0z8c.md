---
id: DAEO-0z8c
status: in_progress
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:10Z
type: task
priority: 1
assignee: engineer
external-ref: W2-05
tags: [wave-2, implementation, full]
wbs_id: W2-05
title: The git environment of every check, hook and helper; the settings re-sort
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/**/*.py
- src/gov/util/gitenv.py
- lefthook.yml
- template/lefthook.yml
- template/.rulesync/hooks.jsonc
- tests/unit/gitenv/**
- docs/research/AR-2-git-sweep.md
kpis:
  success:
  - Every check, test helper and command that runs git in another folder clears the inherited GIT_* variables. One helper does it, and the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161,
    W2-L160].
  - A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (the DEC-710 case) [AR-2].
  - Lefthook install and uninstall leave .claude/settings.json byte-identical to the committed file, and adapter-portability stays green [AR-2].
  failure:
  - A planted GIT_DIR or GIT_INDEX_FILE in a hook's environment reaches no child git call.
profile: FULL
sources:
- DEC-710
est_loc: 140
acceptance_tests:
  path: tests/acceptance/W2-05/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-2
list_rows:
- W2-L109
- W2-L160
- W2-M012
- W2-M105
- W2-M113
- W2-M161
- W2-M231
- W2-M281
---
# W2-05 The git environment of every check, hook and helper; the settings re-sort

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-05), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:**
  - `src/gov/**/*.py`, limited to calls that start git. The sweep is the ticket's first deliverable and names each file before it is changed.
  - `src/gov/util/gitenv.py` (new), `lefthook.yml`, `template/lefthook.yml`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`.
- **KPIs, success:**
  - Every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables. One helper does it, and the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160].
  - A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (the DEC-710 case) [AR-2].
  - `lefthook install` and `uninstall` leave `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green [AR-2].
- **KPIs, failure:** a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call.
