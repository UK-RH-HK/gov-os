---
id: DAEO-n0wb
status: in_progress
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
- src/gov/store/loader.py
- tests/unit/store/**
- src/gov/retrieval/graph_route.py
- src/gov/retrieval/code_route.py
- src/gov/retrieval/retrieve.py
- tests/unit/retrieval/test_w2_92*
- docs/research/W2-92-memory-measure.md
- docs/research/W2-92-proto-drift.py
kpis:
  success:
  - 'The record route: an id (DEC-n, CAP-n, a ticket id or W2 id) or a record title found in a plain question becomes a start id, so the record closure joins the fusion at radius 0 or 1, without --ticket or --id; a question naming no record gets today''s bundle, item for item [DEC-957, DEC-954 Q9c, CAP-13, CAP-18]'
  - 'The code route: a symbol name found in a plain question is asked of the code index (definition, callers, callees) with the tool''s own traversal in small, paged answers, and the file spans it returns join the fusion as a route; a question naming no symbol gets today''s bundle [DEC-957, DEC-859, CAP-12, CAP-18]'
  - 'A missing or unreadable code index or record store is named in the bundle''s stopping reasons for that route, never silently ok and never a failure of the whole answer [DEC-957, DEC-860]'
  - 'Nothing else changes: the budget, the batches, the continuation, DEC-424''s records ahead and W2-87''s authority order; two runs on one store give the same bundle [DEC-424, DEC-860]'
  - 'W2-61''s measure is re-run on the visible half, control at the base and the head, both figures together (hit@5 against CAP-10''s floor of 85 and the owner''s target of 95 %, full evidence against 99 %), with the graph and code-graph questions named, in docs/research/W2-92-memory-measure.md [DEC-957, DEC-833]'
  - 'S6 A plain question costs about one second (DEC-1065 (4)): the record route no longer parses every record''s front matter in each process (the titles kept in the store at rebuild, or read only when a question names a record); a cold gov retrieve on this repository''s store answers a plain question within about 1.2 s at the median of ten, measured by the CTO on the shared servers; nothing else in the bundle changes (S4) [DEC-1065]'
  - 'S7 The stated links (DEC-1072 (1), the census''s kinds 1 to 4): at rebuild the store keeps, in a table of its own outside the digest, the links the records state that no edge holds: the front-matter id keys (sources, closes, decisions, decisions_applied, decisions_carried, decisions_recorded, decisions_read, requirements_implemented) as CITES, task as OF_TASK, the register''s **Under:** as UNDER, a supersession naming ids alone as SUPERSEDES and every other supersession or amendment as AMENDS, by the census''s patterns in one function (register_statements) that gov links reads too; on this repository''s register they match the census''s statements one for one; the closure, gov dangling and every reader of edges are unchanged [DEC-1072, DEC-1073]'
  - 'S8 One bounded hop: from what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and SUPERSEDES in (from the changed decision to its changer), at most 12 records, after today''s closure chunks; adopted only under DEC-1071''s rule (all 80 not lower, the halves'' gap not wider) [DEC-1071, DEC-1072]'
  - 'S9 Status in the bundle: every register chunk a bundle carries names its entry''s status word and the entries that change it; a PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED decision is marked not in force, so no agent takes it as a rule [DEC-1073 (2)]'
  - 'S10 The drift count before and after, by the census''s definitions (docs/research/W2-92-proto-drift.py on the rebuilt store): of the decisions current though stated changed, how many a search reaching the decision also reaches a changer of, in docs/research/W2-92-memory-measure.md [DEC-1072 (1)]'
  failure:
  - 'A question that names no record or symbol gets a different bundle than today.'
  - 'A whole-graph query, or one over the tool''s row cap.'
  - 'A missing index reported ok, or failing the whole answer.'
  - 'A figure of the measure reported without the other, or the hidden half read or run.'
  - 'A partial supersession that drops its target from what is current; a register chunk in a bundle without its status.'
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
- DEC-1071
- DEC-1072
- DEC-1073
- DEC-1074
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

**DEC-1065 (4) placed here (CTO, 2026-11-03):** S6 added; `graph_route.start_ids` parses ~840 records' front matter with the pure-Python loader in each process (2.9 s; the C loader 0.34 s); the store drops the title it parses at rebuild (`store/loader.py:281`).

**DEC-1074 (5) placed here (CTO, 2026-11-05):** S7 to S10 and the failure line are LINK-INTEGRITY §6.1's text, as the
owner adopted it (DEC-1074 (7)). The stated links are approved for re-pin window 4 in the normal flow, independent
tests first. The measured reference is the prototype `w2/W2-92-proto` (`e884675b`: g1 in D4B-MORNING-2026-11-05 §1,
67/79 with v456, drift 184 → 0 unjoined); the engineer builds from it, the test designer from these KPIs and never from
the prototype's code. W2-54's `test_an_empty_retrieval_result_gives_one_packet` has its premise rewritten by its test
designer (DEC-1074 (6)), with `Task:` this ticket, since the links now legitimately bring a record into it.
