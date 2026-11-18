---
id: DAEO-gr7t
status: in_progress
deps: []
links: [DAEO-057v, DAEO-sdhj]
created: 2026-11-18T00:00:00Z
type: task
priority: 1
assignee: orchestrator
external-ref: E2-retire-guard
tags: [retirement, standard, emergency-2]
title: 'The guard and the sandbox retired in the product: no PreToolUse guard shipped or registered, src/gov/guard/ and the launch sandbox deleted, the helpers that stay moved to gov.util, gov.adopt and gov.containment'
class: implementation
state_class: AUTHORITATIVE
role: orchestrator
profile: STANDARD
depends_on: []
allowed_paths:
- src/gov/**
- template/.rulesync/hooks.jsonc
- template/governance/kernel/settings.json
- template/governance/kernel/hooks/**
- .rulesync/hooks.jsonc
- .claude/hooks/**
- tests/unit/**
- tests/optin-lifted*.txt
- governance/project/test-map.yaml
- .tickets/DAEO-gr7t.md
kpis:
  success:
  - 'No PreToolUse guard is shipped or registered [EMERGENCY-2 2.2, 6.1]. Verify: `template/.rulesync/hooks.jsonc` has no `preToolUse` key and no entry running `posttooluse.py`; `template/governance/kernel/settings.json` has no `hooks` key; `.rulesync/hooks.jsonc` and `.claude/settings.json` have no `preToolUse`/`PreToolUse` key; `template/governance/kernel/hooks/` holds no `pretooluse.py` or `posttooluse.py`; `.claude/hooks/` does not exist.'
  - 'The guard and the sandbox code are gone [EMERGENCY-2 6.1]. Verify: `src/gov/guard/` and `src/gov/launch/sandbox.py` do not exist; `grep -rn "gov.guard" src --include=*.py` finds only docstrings that say where a helper came from.'
  - '`gov close` still judges each commit''s paths against its trailers [W1-50, DEC-453]. Verify: `tests/acceptance/W1-50`, `tests/unit/containment` and `tests/unit/close` pass on the branch.'
  - 'Every module that used a guard helper still imports and works [audit 5 finding 2]. Verify: the full suite (`python3 -m pytest tests -n 6`) runs green on the branch but for reds that are red on `w2/integrate` too.'
  failure:
  - 'A test of what stays deleted with the retired ones, or a guard line left in a template the product ships.'
non_goals:
- 'The held-out Read deny rules `gov adapters` writes (permission editing, its own row of EMERGENCY-2 6.1): kept, moved to gov.util.heldout.'
- 'The question writers'' walls (`governance/project/indep-walls/`, shipped in `src/gov/_shipped/`): a separate decision (audit 5, table 2).'
- 'The box (`.gov-runtime/scratch/orchestrator/drafts/session-sandbox/`): scratch, archived by the CTO later.'
sources: [EMERGENCY-2 2.1, EMERGENCY-2 2.2, EMERGENCY-2 6.1, docs/emergency-2/audits/05-repository.md]
acceptance_tests:
  path: tests/acceptance/
  author: none new (a retirement); the independent test designer deletes the acceptance tests whose subject is the guard or the sandbox and repoints the imports of the rest
track: A
---
# E2: the guard and the sandbox retired in the product

EMERGENCY-2 §6.1 rows "The guard (PreToolUse hook, its rules and parser): switched off now; retired" and "The sandbox (SANDBOX-1 in gov launch); the box: switched off now; retired"; §2.1, §2.2. A retirement, not a feature: no new acceptance tests; tests whose subject is the retired guard or sandbox are deleted, tests of what stays are kept green.
