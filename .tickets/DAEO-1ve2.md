---
id: DAEO-1ve2
status: open
deps: [DAEO-drvn]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: engineer
external-ref: W1-18
tags: [wave-1, implementation, standard]
wbs_id: W1-18
title: Ollama on-demand lifecycle and fallback
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-07
allowed_paths:
- src/gov/retrieval/ollama*
- tests/unit/ollama/**
kpis:
  success:
  - gov starts ollama serve on demand and relies on the 5-min idle unload; no always-on unit
  - When Ollama is unavailable retrieval degrades to FTS-only with a warning and the facet state recorded
  failure:
  - A query hangs > 30 s waiting for Ollama
  - Semantic results are silently omitted without a warning
profile: STANDARD
sources:
- G-22
- DEC-074 Q4
est_loc: 40
acceptance_tests:
  path: tests/acceptance/W1-18/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-18 Ollama on-demand lifecycle and fallback

On-demand start and stop of the stack only daemon, with lexical fallback.
