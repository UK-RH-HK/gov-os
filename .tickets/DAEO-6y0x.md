---
id: DAEO-6y0x
status: open
deps: [DAEO-l78m, DAEO-m1u3]
links: []
created: 2026-10-30T22:14:08Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-93
tags: [wave-2, audit, evaluation, held-out, standard, proving-ground]
wbs_id: W2-93
title: 'W2-81''s held-out half: hidden questions and planted-problem variants per synthetic repository, by an independent session'
class: audit
state_class: AUTHORITATIVE
role: independent-auditor
depends_on: [DAEO-l78m, DAEO-m1u3]
allowed_paths:
- fixtures/evaluation/adoption-proving-ground/hidden/**
kpis:
  success:
  - 'At least 10 hidden questions per synthetic repository, each with its gold answer, gold sources and forbidden citations, in the form W2-81''s README states [DEC-957, DEC-941, DEC-828]'
  - 'At least one hidden planted-problem variant per kind that the visible builders do not produce, so an adoption tuned to the visible generator is caught [DEC-941]'
  - 'Written by a session independent of the sessions it measures; nothing hidden written outside the hidden folder; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d), DEC-845, DEC-873]'
  - 'Every gold answer is held by the repository the builder builds, checked on a built copy [DEC-828]'
  failure:
  - 'A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work.'
  - 'A question whose gold answer the built repository does not hold.'
profile: STANDARD
sources:
- DEC-957
- DEC-941
- DEC-828
- DEC-820
- DEC-845
- DEC-873
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-93/
  author: independent-test-designer (MR-3); form only (counts, fields, sources exist), never printing a question or an answer
track: B
list_rows: []
---
# W2-93 W2-81's held-out half

Card: the WBS's proposed companion "W2-81's held-out half" (§2), filed as MEMORY-SPEC-MAP gap 6, resolved by the owner in DEC-957. Without it W2-81's and W2-88's question figures stand on the visible half only.

- **Starts** once W2-81's README states the hidden half's form and its builders exist. The auditor reads the builders and the README, never edits them.
- **Before it starts, the orchestrator adds an `evaluation_sets` entry** to the path map: `adoption-proving-ground`, `visible: tests/acceptance/W2-81/questions/**`, `hidden: fixtures/evaluation/adoption-proving-ground/hidden/**`; `measures` by tickets (adoption and retrieval builders, the sessions running the adoption under test, and W2-81); the writer's own ticket is not measured. W2-84's refusal then covers it from every worktree.
- **Started by the orchestrator,** never by an adoption or retrieval ticket's lead.
