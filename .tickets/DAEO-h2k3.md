---
id: DAEO-h2k3
status: open
deps: []
links: []
created: 2026-10-29T15:55:50Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-61h
tags: [wave-2, audit, evaluation, held-out, standard, keystone-4]
wbs_id: W2-61h
title: 'W2-61''s held-out half: 20 hidden memory questions with their gold sources, by an independent session'
class: audit
state_class: AUTHORITATIVE
role: independent-auditor
depends_on: [DAEO-m1u3]
allowed_paths:
- fixtures/evaluation/memory-retrieval/hidden/**
kpis:
  success:
  - 'Twenty hidden questions about this repository''s governance and code, each with its gold answer and the governing source or sources an answer must cite (file and section), in the form W2-61''s visible half takes (lens B''s 20 questions, docs/assessment/2026-10/B-memory-retrieval.md section 2) [DEC-828 items 3 and 4, DEC-820 (d)]'
  - 'Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61''s engineer, W2-64, W2-04, W2-05, W2-06, W2-13, W2-15a) writes or reads them [DEC-828 item 3, DEC-845 item 2]'
  - 'The same spread as the visible half: decisions, superseded decisions, the plan, the path map, code facts and cross-file questions, at least three questions whose answer needs evidence from two or more files, and at least two whose naive answer is a superseded decision [DEC-833, DEC-866]'
  - 'Every gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4]'
  - 'Nothing written outside fixtures/evaluation/memory-retrieval/hidden/; no question or answer quoted in a commit message, a return, a log or a ticket note [DEC-820 (d)]'
  failure:
  - A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work.
  - A question copied from or paraphrasing lens B's visible 20.
  - A gold source that does not hold its answer.
profile: STANDARD
sources:
- DEC-828
- DEC-820
- DEC-845
- DEC-833
- DEC-873
- DEC-941
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-61h/
  author: independent-test-designer (MR-3); form only (count, fields, sources exist), never printing a question or an answer
track: A
list_rows: []
---
# W2-61h W2-61's held-out half: 20 hidden memory questions with their gold sources

Companion to W2-61 (DEC-941). W2-61's engineer writes the measure and runs the visible half's baseline. The engineer is a measured role (`measures: roles: [engineer, research]` in the path map's `evaluation_sets.memory-retrieval`), so the hidden half is written here, by an independent auditor whose role is not measured, in a session the orchestrator starts, never a retrieval ticket's lead.

- **Why:** a measure tuned on its own questions overstates itself. The hidden half keeps W2-61's figures honest across the memory chain (DEC-828 item 3, DEC-820 (d)).
- **Form:** the auditor reads W2-61's script's input form once it is merged (`src/gov/retrieval/measure.py` and its README or docstring) and writes in that form. Before then, one YAML file per question with `question`, `gold_answer` and `sources` (path plus heading or line).
- **After it:** the orchestrator, which no set measures, runs W2-61's script on the hidden half and records the scores only (never the questions or answers) beside the visible baseline in `docs/research/W2-61-baseline.md`.
- **No path map change:** the hidden folder and its refusal are already in the path map (`evaluation_sets.memory-retrieval`, W2-58).
