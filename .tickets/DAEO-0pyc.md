---
id: DAEO-0pyc
status: open
deps: [DAEO-g0ip, DAEO-rd0g]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-32
tags: [wave-2, implementation, standard]
wbs_id: W2-32
title: 'Retrieval components and bounded improvements: model pin, swap by configuration, learning loop; ranked-lexical tuning, chunking, the hit@5 85 row'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-rd0g
allowed_paths:
- src/gov/retrieval/**
- src/gov/config/models*
- tests/unit/retrieval/**
- tests/unit/semantic/**
kpis:
  success:
  - Changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression passes [CAP-10.b].
  - An unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065].
  - A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c].
  - A reranker that dies after loading is reported, not raised [W2-M104].
  - The fusion limit is honoured [W2-M103].
  - 'At most the three gaps that W2-15a named, from these: ranked-lexical tuning: field weights, tokenizer, and the exact-identifier boost'
  - 'At most the three gaps that W2-15a named, from these: chunking: span size, overlap and parent expansion, with a re-embed'
  - 'At most the three gaps that W2-15a named, from these: the hit@5 85 row on the dev queryset [W2-M341]: Each gets one round plus its probe; its effect is measured by W2-15b. What remains is a named residual.'
  - 'If memory is below 85 % after two improvement rounds, the orchestrator escalates to the owner with the reasons; at the third the owner decides: a discovery and research ticket benchmarking market tools in a separate worktree, accepting the level reached, or another course. At 85 % or above but under the owner''s target of 95 %, with room for improvement found, memory is not closed: an escalation to the owner [DEC-954 Q9e, DEC-957]'
  failure:
  - An improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.
profile: STANDARD
sources:
- CAP-10.b
- CAP-19.a
- CAP-19.c
- DEC-725
- DEC-954
- DEC-957
est_loc: 320
acceptance_tests:
  path: tests/acceptance/W2-32/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-10.b
- CAP-19.a
- CAP-19.c
- DEC-725
list_rows:
- W2-L029
- W2-L065
- W2-L066
- W2-L068
- W2-L239
- W2-M001
- W2-M073
- W2-M103
- W2-M104
- W2-M191
- W2-M341
---
# W2-32 Retrieval components and bounded improvements: model pin, swap by configuration, learning loop; ranked-lexical tuning, chunking, the hit@5 85 row

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-32), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/retrieval/**`, `src/gov/config/models*`, `tests/unit/retrieval/**`, `tests/unit/semantic/**`.
- **KPIs, components:**
  - Changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression passes [CAP-10.b].
  - An unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065].
  - A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c].
  - A reranker that dies after loading is reported, not raised [W2-M104].
  - The fusion limit is honoured [W2-M103].
- **KPIs, bounded improvements (DEC-725):** at most the three gaps that W2-15a named, from these:
  - ranked-lexical tuning: field weights, tokenizer, and the exact-identifier boost;
  - chunking: span size, overlap and parent expansion, with a re-embed;
  - the hit@5 85 row on the dev queryset [W2-M341].
  Each gets one round plus its probe; its effect is measured by W2-15b. What remains is a named residual.
- **Failure:** an improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.
