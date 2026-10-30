---
id: DAEO-n0wb
status: open
deps: [DAEO-s9qc, DAEO-ym8a]
links: []
created: 2026-10-30T22:14:08Z
type: task
priority: 1
assignee: engineer
external-ref: W2-92
tags: [wave-2, implementation, memory, standard, keystone-4]
wbs_id: W2-92
title: 'The knowledge graph and the code graph as routes of plain-question retrieval: ids, record titles and symbol names in a question join the fusion'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-s9qc, DAEO-ym8a]
allowed_paths:
- src/gov/retrieval/graph_route.py
- src/gov/retrieval/code_route.py
- src/gov/retrieval/retrieve.py
- tests/unit/retrieval/test_w2_92*
- docs/research/W2-92-memory-measure.md
kpis:
  success:
  - 'The record route: an id (DEC-n, CAP-n, a ticket id or W2 id) or a record title found in a plain question becomes a start id, so the record closure joins the fusion at radius 0 or 1, without --ticket or --id; a question naming no record gets today''s bundle, item for item [DEC-957, DEC-954 Q9c, CAP-13, CAP-18]'
  - 'The code route: a symbol name found in a plain question is asked of the code index (definition, callers, callees) with the tool''s own traversal in small, paged answers, and the file spans it returns join the fusion as a route; a question naming no symbol gets today''s bundle [DEC-957, DEC-859, CAP-12, CAP-18]'
  - 'A missing or unreadable code index or record store is named in the bundle''s stopping reasons for that route, never silently ok and never a failure of the whole answer [DEC-957, DEC-860]'
  - 'Nothing else changes: the budget, the batches, the continuation, DEC-424''s records ahead and W2-87''s authority order; two runs on one store give the same bundle [DEC-424, DEC-860]'
  - 'W2-61''s measure is re-run on the visible half, control at the base and the head, both figures together (hit@5 against CAP-10''s floor of 85 and the owner''s target of 95 %, full evidence against 99 %), with the graph and code-graph questions named, in docs/research/W2-92-memory-measure.md [DEC-957, DEC-833]'
  failure:
  - 'A question that names no record or symbol gets a different bundle than today.'
  - 'A whole-graph query, or one over the tool''s row cap.'
  - 'A missing index reported ok, or failing the whole answer.'
  - 'A figure of the measure reported without the other, or the hidden half read or run.'
profile: STANDARD
sources:
- DEC-957
- DEC-954
- DEC-859
- DEC-860
- DEC-424
- DEC-833
- CAP-12
- CAP-13
- CAP-18
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-92/
  author: independent-test-designer (MR-3); written before implementation; a planted repository with a register, records and code, its store and a stand-in code index built in a temporary folder; never this repository's store
track: B
list_rows: []
---
# W2-92 The knowledge graph and the code graph as routes of plain-question retrieval

Card: MEMORY-SPEC-MAP gaps 2 and 3, resolved by the owner in DEC-957 ("a ticket for the knowledge-graph and code-graph routes in ordinary questions"); without them the graphs are built but earn nothing in the combined measure (Q9c).

- **Today:** `gov retrieve` adds the closure route only for start ids given with `--ticket` or `--id` (`retrieve.py`); callers and definitions come only from `gov closure` or `gov impact` given a symbol. In W2-61's baseline, Q10's first caller was at rank 25.
- **What changes:** two new route modules, and `retrieve.py`'s route list (one call each). The ranking (W2-87) and what is left out (W2-55) are not touched.
- **Order and overlaps:** after W2-87 (`DAEO-s9qc`, running), which holds `retrieve.py`; W2-13 holds `fusion*` and `lexical*`: read only; W2-32 holds `src/gov/retrieval/**` broadly (open): this ticket takes its two new files and `retrieve.py`'s route list only, and W2-32 merges back after it.
- **Judged with** W2-61h's enlarged set (graph and code-graph categories), once it is in.
