---
id: DAEO-kia7
status: open
deps: [DAEO-g0ip, DAEO-0z8c]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-06
tags: [wave-2, implementation, full]
wbs_id: W2-06
title: Fast pre-commit tier and commit-time re-index
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-0z8c
allowed_paths:
- src/gov/ci/**
- src/gov/rebuild/**
- src/gov/retrieval/index*
- template/governance/kernel/checks/index-freshness.yaml
- template/governance/kernel/checks/recovery-rebuild.yaml
- template/governance/kernel/checks/secrets-indexing.yaml
- lefthook.yml
- template/lefthook.yml
- tests/unit/ci/**
- tests/unit/rebuild/**
kpis:
  success:
  - After any commit, the lexical (ranked and exact) and semantic indexes match the committed tree without a rebuild by hand, and index-freshness is green [CAP-17.b, W2-H041, W2-M011, W2-M293].
  - A merge commit triggers the same re-index (post-merge) [W2-M295].
  - The pre-commit tier holds only fast checks and finishes in under 60 s on this repository. Index-freshness and recovery-rebuild run at pre-push (G3) or in CI [W2-H039, W2-H040, W2-M210, W2-M282].
  - The staged-secrets scan reads only the staged files [W2-M243, W2-M143].
  - A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719].
  failure:
  - A re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088].
profile: FULL
sources:
- DEC-719
- CAP-17.b
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-06/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-2 (DEC-719)
- CAP-17.b
list_rows:
- W2-H039
- W2-H040
- W2-H041
- W2-L056
- W2-L103
- W2-L330
- W2-M011
- W2-M040
- W2-M045
- W2-M070
- W2-M088
- W2-M099
- W2-M125
- W2-M143
- W2-M210
- W2-M243
- W2-M282
- W2-M293
- W2-M295
---
# W2-06 Fast pre-commit tier and commit-time re-index

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-06), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/ci/**`, `src/gov/rebuild/**`, `src/gov/retrieval/index*`, `template/governance/kernel/checks/index-freshness.yaml`, `template/governance/kernel/checks/recovery-rebuild.yaml`, `template/governance/kernel/checks/secrets-indexing.yaml`, `lefthook.yml`, `template/lefthook.yml`, `tests/unit/ci/**`, `tests/unit/rebuild/**`.
- **KPIs, success:**
  - After any commit, the lexical (ranked and exact) and semantic indexes match the committed tree without a rebuild by hand, and index-freshness is green [CAP-17.b, W2-H041, W2-M011, W2-M293].
  - A merge commit triggers the same re-index (`post-merge`) [W2-M295].
  - The pre-commit tier holds only fast checks and finishes in under 60 s on this repository. Index-freshness and recovery-rebuild run at pre-push (G3) or in CI [W2-H039, W2-H040, W2-M210, W2-M282].
  - The staged-secrets scan reads only the staged files [W2-M243, W2-M143].
  - A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719].
- **KPIs, failure:** a re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088].
