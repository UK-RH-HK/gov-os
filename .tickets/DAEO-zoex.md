---
id: DAEO-zoex
status: in_progress
deps: []
links: [DAEO-0rfi]
created: 2026-10-31T02:37:52Z
type: task
priority: 1
assignee: engineer
external-ref: W2-108
tags: [wave-2, implementation, memory, standard, follow-up]
wbs_id: W2-108
title: 'Retrieval checks the stores'' freshness once per run, not on every call: the context check''s 328 calls stop repeating it (a follow-up of W2-54)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/semantic.py
- src/gov/retrieval/lexical.py
- tests/unit/retrieval/test_w2_108*
- docs/research/W2-108-freshness-once.md
kpis:
  success:
  - 'Within one process, the semantic store''s status (which files should be embedded and whether the store holds them) and the lexical index''s freshness are worked out once per store and tree, keyed by the store''s fingerprint and the tree''s head, and reused by every later retrieval call in that process [DEC-969, DEC-966 item 4]'
  - 'Every answer is unchanged: for the same store and tree, each retrieval call returns the same bundle, facets and stopping reason as before, item for item, on a planted repository and on this repository''s store [DEC-969, DEC-860]'
  - 'A change is still seen: a store rebuilt, a file changed or a head moved between two calls is seen as such (a new key, a fresh check); a process that cannot read the fingerprint or the head checks every time, never reuses an old answer [DEC-969]'
  - 'Measured: `python3 -m gov.context.context_check` on one store, before and after, at the same measured load (two loads, one of them 40 or more), with the time spent in the freshness checks and in query embedding, in docs/research/W2-108-freshness-once.md; the target is under W2-54''s 600 s limit at ordinary load, and the record says whether the embedding batching is still needed [DEC-969, DEC-968 item 3]'
  failure:
  - 'A freshness or status check repeated on every call within one process.'
  - 'Any bundle, facet or stopping reason different from before for the same store and tree.'
  - 'A stale answer reused after the store, a file or the head changed.'
  - 'W2-54''s time limits raised, or its tests changed.'
profile: STANDARD
sources:
- DEC-969
- DEC-968
- DEC-966
- DEC-860
- DEC-424
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-108/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7, DEC-963); planted repositories and stores in a temporary folder
track: B
list_rows: []
---
# W2-108 Retrieval checks freshness once per run

A follow-up of W2-54 (`DAEO-0rfi`, closed; it stays closed): the owner's P-W2-54-LOAD-1 (a), DEC-969. Memory stream, after the tickets already queued.

- **Why:** W2-54's two cases time the context-reproducibility check (600 and 630 s) and fail under load. A cProfile on 2026-10-31 (load 40 to 70) measured 1,252 s for its 328 retrieval calls. About 460 s of that is freshness checks repeated on every call: `semantic._status` 315 s (inside it `_wanted`, 17 million calls to `embedded()`, 228 s), and `lexical.freshness` 148 s (the tracked files listed on each of 656 calls). Query embedding takes 375 s, and the searches the rest. Neither freshness answer can change within one run.
- **The fix:** remember both answers for the life of the process, keyed so that any change is seen.
- **Next step, only if the measure says so:** batch the check's query embeddings (96 calls). The owner decides it from this ticket's record (DEC-969).
- **Not done:** W2-54's time limits are not raised and its tests are not changed.
- **Overlaps (split by function):** W2-13 (`fusion*`, `lexical*`) and W2-32 (`src/gov/retrieval/**`) are open and not running. This ticket changes only the freshness and status functions of `semantic.py` and `lexical.py`. Whichever merges second merges back.
