---
id: DAEO-zqvn
status: in_progress
deps: [DAEO-g0ip, DAEO-ym8a]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-13
tags: [wave-2, implementation, full]
wbs_id: W2-13
title: RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ym8a
allowed_paths:
- src/gov/retrieval/supplementary.py
- src/gov/guard/role_paths.py
- tests/unit/guard/test_role_paths*
- src/gov/retrieve/**
- src/gov/retrieval/lexical*
- src/gov/retrieval/fusion*
- src/gov/rebuild/lexical*
- src/gov/retrieval/retrieve.py
- tests/unit/retrieve/**
- tests/unit/retrieval/**
kpis:
  success:
  - 'The ranked lexical route. The lexical index is an SQLite FTS5 table over the same parents and spans as today, built by gov rebuild (and, after W2-06, by the commit-time re-index). A plain-word question
    returns hits ranked by BM25, with field weights for id, title and body. An exact identifier still ranks first: the exact-match route is kept as a boost, not replaced [DEC-725, W2-M102, W2-L233, W2-M292,
    W2-M072, W2-M100].'
  - The fusion receives a ranked lexical list beside the semantic one, so that lexical, semantic and the reranker each contribute. The dev queryset's lexical-only hit@5 is recorded in the ticket's evidence
    [DEC-725].
  - Lexical search returns "unavailable" instead of raising [W2-M071]. Retrieval latency stays within the retrieve budget on the dev tiers.
  - 'A question about an id that exists nowhere stops with a named reason and no unrelated items: the stated gap, as the owner ruled for RETR-X-02 (DEC-900, AR-9), and as W1-21 asserts; W1-42''s RETR-X-02 case is retired, so this ticket''s own acceptance tests hold the requirement [AR-9, W2-M296, DEC-900].'
  - 'S5 Search respects role separation (DEC-1065 (2)): gov retrieve''s results (every route) and gov context''s supplementary block are filtered by the caller''s role_paths (GOV_ROLE or --role, and GOV_TICKET; the same path checks as the guard''s, from one product module): an engineer never receives its own ticket''s acceptance tests, a test designer never the ticket''s new code; what is filtered is named in the bundle (how many, by which rule), never dropped silently; no role_paths section means no filter [DEC-1065, DEC-1056, DEC-1063]'
  failure:
  - RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason).
  - 'The secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed.'
profile: FULL
sources:
- DEC-725
- DEC-900
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-13/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-9 (RETR-X-02)
- DEC-725
list_rows:
- W2-L233
- W2-M071
- W2-M072
- W2-M098
- W2-M100
- W2-M102
- W2-M292
- W2-M296
---
# W2-13 RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-13), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **The owner's ruling on RETR-X-02 (Q-1) is made (DEC-900, 2026-10-23):** the accepted outcome is the stated gap.
- **Allowed paths:** `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `src/gov/retrieval/fusion*`, `src/gov/rebuild/lexical*`, `tests/unit/retrieve/**`, `tests/unit/retrieval/**`.
- **KPIs, success:**
  - **The ranked lexical route.** The lexical index is an SQLite FTS5 table over the same parents and spans as today, built by `gov rebuild` (and, after W2-06, by the commit-time re-index). A plain-word question returns hits ranked by BM25, with field weights for id, title and body. An exact identifier still ranks first: the exact-match route is kept as a boost, not replaced [DEC-725, W2-M102, W2-L233, W2-M292, W2-M072, W2-M100].
  - The fusion receives a ranked lexical list beside the semantic one, so that lexical, semantic and the reranker each contribute. The dev queryset's lexical-only hit@5 is recorded in the ticket's evidence [DEC-725].
  - Lexical search returns "unavailable" instead of raising [W2-M071]. Retrieval latency stays within the retrieve budget on the dev tiers.
  - A question about an id that exists nowhere stops with a named reason and no unrelated items: the stated gap, as the owner ruled for RETR-X-02 (DEC-900, AR-9), and as W1-21 asserts; W1-42's RETR-X-02 case is retired, so this ticket's own acceptance tests hold the requirement [AR-9, W2-M296, DEC-900].
- **KPIs, failure:**
  - RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason).
  - The secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed.

**Delegated (CTO, 2026-11-03, P2 under DEC-957; DEC-1057 R-8: a line here, not a register entry):** `src/gov/retrieval/retrieve.py` added to the allowed paths, so that S2's fusion takes the ranked lexical list W2-92's merged `retrieve()` now carries (one line, `answer.get("ranked", answer["hits"])`); D-4b (DEC-1055) finishes W2-13 on top of W2-92.

**Delegated (CTO, 2026-11-03, P2; DEC-1057 R-8):** P-W2-13-R3 (a): the bundle budget bounds parent expansion only, as W1-21's approved spec DEC-419 DP-3 says (a cut of the gathered children was tried and reverted, `ea486253`/`80cdd7ff`); whether the budget should bound the whole bundle (DEC-860) is W2-32's S5, with its own tests. The 13 cases of W2-92, W2-87, W1-21 and W1-19 that W2-13's S2 and DP-3 changed were re-pinned by a test designer (`d71df8f8`). Merged as built in D-4b (`8550788b`).

**DEC-1065 (2) placed here (CTO, 2026-11-03):** S5 added (W2-13 owns `gov retrieve`); the filter at `retrieve.py`'s chunk list, the matcher in a product module the hook can later reuse.

**P-W2-13-TD-5 (a) (CTO, 2026-11-03, P2):** the supplementary block is built in `src/gov/retrieval/supplementary.py` (not `src/gov/context/`): that file replaces the wrong path in S5's allowed paths.
