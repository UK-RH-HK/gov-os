---
id: DAEO-gr7t
status: closed
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
  path: tests/acceptance/E2-retire-guard/
  author: none new (a retirement); the independent test designer deletes the acceptance tests whose subject is the guard or the sandbox and repoints the imports of the rest
track: A
---
# E2: the guard and the sandbox retired in the product

EMERGENCY-2 §6.1 rows "The guard (PreToolUse hook, its rules and parser): switched off now; retired" and "The sandbox (SANDBOX-1 in gov launch); the box: switched off now; retired"; §2.1, §2.2. A retirement, not a feature: no new acceptance tests; tests whose subject is the retired guard or sandbox are deleted, tests of what stays are kept green.

**Closed at the land 2026-11-18 by the CTO (EMERGENCY-2 4.3 step 5):** merged into w2/integrate with gov accept green on the merged tree; no review (3.6).

## Fix: the ticket names no whole tree as its acceptance folder (L2-4, DEC-1217 (1))
- **The bug (found by the L2-4 lead's proving landing, 2026-11-20):** this ticket declared `acceptance_tests.path:
  tests/acceptance/` (a retirement writes no acceptance test of its own) and holds `src/gov/**` and `tests/unit/**` in
  its `allowed_paths`. The selection reads a path a ticket with a suite holds as selecting that suite, so every change
  under `src/gov/**` or `tests/unit/**` selected the whole `tests/acceptance/` and `gov queue` refused it,
  `SELECTION_REFUSED: the selection would run the whole of tests/acceptance/`. It has refused every such landing since
  this ticket closed (2026-11-18), behind the unplaced-path refusal of W2-115b's fix. No other ticket has this shape.
- **The fix:** `acceptance_tests.path` is `tests/acceptance/E2-retire-guard/`, the folder the ticket's own id would
  have (it holds no test, so the ticket holds no suite and its paths place nothing). The test is written first, red on
  the base, by the independent test designer: `tests/unit/close/test_live_tickets_name_no_whole_suite.py` (no ticket
  of the live tree names a whole tree as its suite). Commits carry `Task: DAEO-gr7t` and a `Fix:` trailer. The ticket
  stays closed.
