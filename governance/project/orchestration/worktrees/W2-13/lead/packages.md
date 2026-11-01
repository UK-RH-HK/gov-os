# W2-13 (DAEO-zqvn) packages, run 1 (draft, lead)

## P-W2-13-3 — the lexical route's interface: the ranking in `hits`, or in a new `ranked` list (KPI dispute between the tests and the build)

1. Context. KPI S1 says "a plain-word question returns hits ranked by BM25 … the exact-match route is kept as a boost". The test designer and the engineer worked in parallel from that line (DEC-963). The designer reads the ranking from `gov.retrieval.lexical.search(...)["hits"]`, W1-17's interface, and named 10 W1-17 cases it would need revising. The engineer kept `hits` exactly as W1-17 holds it (every line that holds the exact string, by path and line), because W1-17 (65 cases) and W2-87's planted authority order (5 cases went red when `hits` were BM25-ordered, then green again) depend on it. It puts the ranking in a new list, `ranked` (exact chunks first, then up to 30 BM25 word chunks), which `fusion.search` fuses.
2. What happened. Lead's `gov accept` on bd329ce3b402: 45 passed, 11 failed. Lead's diagnostic run: S1's 6 failures and S2's `test_the_lexical_route_hands_the_fusion_its_ranking_best_first` all read the ranking from `hits` ("returns no lexical hit", "not ranked above", "fused order is not the lexical route's ranking"). The ranking itself works: the dev queryset's lexical-only hit@5 is 85.0 on `ranked` (44 of 52 hit), against 0.0 on the base.
3. Why it matters. Success 1 and 2 cannot pass until the tests and the code read the same field. CAP-11 (exact strings with file and line) must not be lost.
4. Options.
   - (a) `hits` becomes the ranked route (the exact lines first, then the word hits by BM25). P-W2-13-1 falls away, because retrieve.py's route list reads `hits`. Cost: an engineer batch (about 1 h). A test designer revises W1-17's 10 named cases and W2-87's 5 order cases under this decision, with Rewrite-Reason. canary.py, retrieve_check and gov.decisions.register also read `hits`, so each needs a sweep. Risk: wider; two merged tickets' tests are rewritten.
   - (b) Keep the build: `hits` exact (W1-17, CAP-11), `ranked` the new route list. A test designer rewrites W2-13's 7 cases to read the ranking from `ranked`, a rewrite after implementation with `Rewrite-Reason: P-W2-13-3 (b)`, lowering no expectation. P-W2-13-1 is needed. Cost: one test-design batch (about 45 min) and the one-line change. Risk: low; no merged ticket's tests change.
   - (c) Both: `hits` keeps the exact lines first and then adds the word hits as lines. W1-17's exact-list cases still go red, so this is (a) by another name.
5. Recommendation: (b), confidence medium. Classification: no finding of a probe; a KPI interface dispute, ordinary work, consequence other (nothing fails open; answers stay as good as today until it is settled). P2 (it revises the ticket's own tests after implementation, and with P-W2-13-1 it touches W2-92's file).
6. Blocks: success 1 and 2 of W2-13, so its DONE, its scoped verification and its review (each would be wasted on a head that will change). Waiting costs the ticket's close and memory's chain (DEC-979 item 4); nothing else.

## P-W2-13-1 — `gov retrieve`'s bundle does not fuse the ranked lexical list (retrieve.py, W2-92's route list) (the engineer's, endorsed)

1. Context. `src/gov/retrieval/retrieve.py` line 127 builds the bundle's routes from `answer["hits"]`. That file is outside W2-13's paths, and its route list is held by W2-92, running now.
2. What happened. Under P-W2-13-3 (b), `gov retrieve` keeps fusing only the exact lines, so a plain-word question gets no lexical candidate in the bundle. S2's `test_gov_retrieve_cites_what_the_lexical_route_ranks_for_a_plain_word_question` fails. The memory measure moves only through the bundle (the lead's three-way measure, below).
3. Why it matters. KPI S2 ("the fusion receives a ranked lexical list beside the semantic one") at the bundle level, W2-M292 and W2-M102 at the bundle level, and memory's target (DEC-957).
4. Options. (a) Change line 127 to `routes = {name: answer.get("ranked", answer["hits"]) for name, answer in answers.items()}`, made in W2-92's route-list change, or with W2-13's paths widened by that line once W2-92 merges. Cost: 1 line, then W2-87, W1-21 and RETR-A-04 in the scoped run. (b) Defer to W2-32's tuning: memory's measure stays where it is. (c) Under P-W2-13-3 (a) it is not needed.
5. Recommendation: (a), applied by W2-92's lead in its route list (a cross-stream P2) or by W2-13 after W2-92 merges; confidence medium-high.
6. Blocks: S2's bundle case and the measure's effect. The rest of W2-13 is done.

## P-W2-13-TD-1 — W2-M098 (the designer's): the stopping reason for an id no record has differs by machine

Outside W2-13's reach: `src/gov/closure/**` is not in its paths. A question asked alone, or with only missing ids, is now answered the same on every machine (`UNRESOLVED_IDS`, through the command). The closure's own `FACET_UNAVAILABLE`, when an existing id sits beside a missing one and there is no code tool, is not. Recommendation: the designer's (a) through (c): the row moves to the ticket that owns `src/gov/closure/**`, a residual for the Wave 2 list. P3/P2; confidence medium. Blocks nothing in W2-13.

## P-W2-13-TD-2 — whole tokens against lens G's trigram table (W2-M100 against R8) (the designer's)

Built: whole tokens (no trigram table), recorded in the lexical module's docstring. The case `test_a_word_matches_whole_tokens_only` passes. Recommendation: (a), whole tokens as the row says; the trigram table becomes W2-32's tuning or a Wave 3 row. Confidence medium. Blocks nothing.

## P-W2-13-TD-3 — the paths for success 4 and the traceback (the designer's): settled inside the paths

Both were met in `src/gov/retrieve/command.py` (b555d200b5f6), and their cases pass. What is left is P-W2-13-1. No decision is needed beyond it.
