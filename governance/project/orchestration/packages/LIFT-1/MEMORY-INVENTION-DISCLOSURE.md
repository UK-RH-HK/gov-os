# Invention disclosure: drift-aware memory for governed multi-agent software work

- **For:** the owner (DEC-1077 (e)), for your own prior-art searches. Plain words; every claim of novelty below is
  the CTO's belief from what it knows, not the result of a search.
- **By:** the CTO (session `812bc5ce`), 2026-11-05, on `w2/integrate` at `8a395630` (with W2-92's stated links merged,
  `3679ca0b`; W2-32's candidate pool on its branch, `1aeae788`).
- **Not a legal document.** It describes what is built and measured, so that a search can be run against it.
- **Sources in the repository:** `src/gov/retrieval/`, `src/gov/store/loader.py`, `governance/project/path-map.yaml`,
  `docs/research/W2-88-memory-practice.md`, `docs/research/D4B-link-census.md`,
  `docs/research/memory-measure-audit/RUBRIC.md`, the D-4b packages in `governance/project/orchestration/packages/LIFT-1/`,
  and the decision register (DEC-1055 to DEC-1077).

## 1. Technical field
Information retrieval for software-engineering agents: building and searching a memory of one software repository, its
code and its governance records (decisions, tickets, specifications, plans, lessons), so that many AI agents working in
parallel under role rules find the rule that is in force, the code it governs and the records that changed it. Also: a
method to measure such a memory honestly while it is being tuned.

## 2. The problem
1. **Drift.** In a repository governed by recorded decisions, decisions are amended or replaced often, usually in part
   ("item 3 of DEC-x is replaced by DEC-y"). The changed decision's own text rarely says so. An agent that searches and
   finds the old decision takes it as the rule. In this repository a census found 215 decisions current although the
   register says they changed, 87 of them with no hint in their own entry, and 536 text chunks of them with no hint.
   The search graph held 3 of the 395 stated supersession and amendment links, and none of the 1,378 links from tickets
   to the decisions they cite.
2. **Memory for agents, not people.** Agents ask in their own words, about code, decisions, tickets and plans at once,
   need the whole answer within a token budget, and run 10 to 20 searches at once on one machine with one GPU.
3. **Role separation.** The builder must never read its own acceptance tests; the test designer must never read the
   builder's new code. A search that hands a builder its own tests breaks that rule silently.
4. **Honest measurement.** A memory tuned on a question set fits that set. Here the visible half rose from 12 to 21 of 24
   while the hidden half stayed at 16 to 17; later, two tuned halves agreed within 0.4 points while a fresh blind set
   scored 17 points lower.
5. **The machine.** Per-session rerankers on one GPU crashed it; a request bounded by its text count, not its size,
   pushed the GPU past its limit twice.

## 3. Prior art known to the CTO (not a search)
- **Keyword search:** BM25 (Robertson and others), SQLite FTS5 with porter stemming; field weighting (BM25F).
- **Meaning search:** dense embeddings and vector indexes (sqlite-vec, FAISS); instruction-prefixed embedders
  (Qwen3-Embedding, E5, BGE).
- **Hybrid search:** reciprocal rank fusion, RRF (Cormack, Clarke and Büttcher, 2009), used by Elasticsearch, OpenSearch,
  Weaviate, Qdrant, Azure AI Search, Vespa.
- **Rerankers:** cross-encoders (monoBERT, monoT5; the bge, mxbai and Qwen3 rerankers), late interaction (ColBERT), LLM
  rerankers (RankGPT, listwise and pointwise).
- **Chunking and context:** parent-document retrieval (LangChain), chunk headers and contextual retrieval (Anthropic,
  2024), sentence-window retrieval (LlamaIndex), late chunking.
- **Query rewriting:** multi-query and RAG-Fusion, HyDE, query expansion.
- **Diversity:** maximal marginal relevance; per-document caps in search results.
- **Graphs:** knowledge-graph RAG (Microsoft GraphRAG, LightRAG, HippoRAG), Zep/Graphiti's temporal graphs (facts with
  validity intervals), code graphs (Sourcegraph's code intelligence, Aider's repository map, tree-sitter indexes).
- **Agent memory:** MemGPT/Letta, Mem0, A-MEM.
- **Records:** architecture decision records (ADRs, Nygard 2011), requirements traceability matrices, commit trailers.
- **Measurement:** held-out test sets, benchmark contamination studies, blind annotation with adjudication.

The research session started on 2026-11-05 (DEC-1077 (d)) adds a sourced survey (`docs/research/D4B-memory-survey/`).

## 4. Summary
A repository's memory is built as **four stores from one rebuild**: a keyword index, a meaning index, a record graph
with **stated links**, and a code graph, each chunk carrying its heading path. A question is answered by **several
routes at once** (keywords and meaning over three deterministic phrasings, the records the question names and their
closure, the symbols it names, and a **bounded hop over the stated links**), fused by rank with an authority lift, a
**deep candidate pool reranked once** by a **shared GPU reranker service** with size-bounded requests, re-ordered by
**question type** and **crowding limits**, and returned as a **token-budgeted bundle** whose continuation carries the
reranked order. **Every register chunk in a bundle carries its decision's status and the decisions that changed it**, and
a **changed decision brings its changer** into the bundle, so an agent never takes an amended or replaced rule as current
without seeing what changed it. **Search results are filtered by the caller's role**. The memory is **measured by a
discipline** built for an agent system tuning itself: a rubric, three question sets with three jobs, writers outside the
system, a hidden half kept outside every working tree, counts-only reporting with a leak check, and **consistency across
sets** as the proof of the structure.

## 5. Detailed description

### 5.1 Overview
```
                     BUILDING (one rebuild, from the committed tree)
  records, code, docs ──► path map ──► chunker (sections, ~1,200 chars, heading paths)
                                         │
       ┌──────────────────┬──────────────┼───────────────────┬────────────────────┐
       ▼                  ▼              ▼                   ▼                    ▼
  keyword index      meaning index   record graph        stated links         code graph
  (FTS5, BM25,       (GPU embedder,  (front-matter       (register statements, (definitions,
   text/id/title)     heading path)   edges)              front-matter ids)     callers, callees)

                     RECALL (one question)
  question ─► start ids (ids, titles, symbols named) ─► three phrasings
     │
     ├─► keyword route (60) ─┐
     ├─► meaning route (60) ─┤
     ├─► record route + closure ─┤──► rank fusion (RRF k 60) + authority lift
     ├─► code route ─────────┤
     └─► stated-links hop ───┘
                                  ▼
               the pool: first 40 reranked once (shared GPU service)
                                  ▼
          routing by question type ─► crowding limits ─► status marks
                                  ▼
          bundle: 6,000 tokens, batches of 10, widened to sections, no span twice
                                  ▼
          continuation token (carries the reranked order) ─► next call
```

### 5.2 Building the memory
1. **What is indexed, and how, is configuration** (`governance/project/path-map.yaml`). Each tracked path belongs to one
   namespace. A namespace is **embedded** (meaning and keyword search: tickets, code, the register, the Contract, plans,
   research, governance texts), **keyword-only** (tests, close and checkpoint records, reviews, agent settings), or **in
   neither index** (the evaluation's own documents and fixtures, so the measure cannot find itself). The hidden
   evaluation sets are not in the tree at all.
2. **Chunking** (`chunking.py`). Text is cut inside parent sections (Markdown headings; Python definitions optionally),
   at most 1,200 characters a chunk with 120 of overlap; the parent section is kept so a chunk can be widened to it.
   The register is kept one entry per span. A chunk records its path, lines and parent.
3. **Heading paths.** Each chunk is embedded with a header: its file path and the headings above it. (Measured: +1 on
   the old 48 questions; it also moved the halves' structure.)
4. **Embedding** (`semantic.py`). One embedder, Qwen3-Embedding-0.6B, served on the GPU by a shared server, up to
   10,000 characters a chunk. **No CPU fallback anywhere:** a vector computed on the CPU is refused, never cached or
   stored; when the GPU server cannot be reached, search reports its meaning part unavailable and answers by keywords.
   A machine-wide vector cache is keyed by model, revision and text hash, so rebuilds re-embed only what changed.
5. **Keyword index** (`lexical.py`). SQLite FTS5 with porter stemming and `_` kept inside words; three columns weighted
   1 (text), 10 (identifiers) and 4 (title); an exact-id boost; 32 terms at most a question.
6. **Record graph** (`store/loader.py`). Every record (decision, ticket, capability, plan, lesson, checkpoint, close
   record) with its front matter; edges from front-matter keys named after edge types (`depends_on`, `constrains`, …).
7. **Stated links** (W2-92, merged into integrate). At rebuild, one function, `register_statements`, reads the links the
   records state but no edge holds, by the census's patterns, into a table of its own outside the store's digest:
   - **CITES**: a record's id keys in its front matter (`sources`, `closes`, `decisions`, `decisions_applied`, …);
   - **OF_TASK**: a checkpoint's or close record's `task`;
   - **UNDER**: a decision's `**Under:**` line (the decisions it rests on);
   - **SUPERSEDES**: a supersession that names whole decisions by id alone;
   - **AMENDS**: every other supersession or amendment, labelled (`Changes:`, `Changed by:`, `Amends:`, `Replaces:`,
     `Lifted by:`, …) or in free text.

   Kept apart on purpose: a partial supersession is an AMENDS, so it never drops its target from what is current (42
   of the 43 supersessions here are partial). On this register: CITES 1,679; OF_TASK 381; UNDER 2,481; AMENDS 388;
   SUPERSEDES 7 (3,171 statements, equal one for one to the census).
8. **Code graph.** A code-intelligence index (definitions, callers, callees), asked in small pages.
9. **One rebuild, fingerprinted.** The stores are rebuilt together from a commit; the store records that commit and a
   recipe digest; a stale store is named stale. The shared integration store is double-buffered (two halves, a link
   flipped after a full check).

### 5.3 Recall
1. **Start ids.** Ids and record titles named in the question become start ids for the record route; symbols named
   become questions for the code route. An id that exists nowhere stops the search with `UNRESOLVED_IDS` naming it,
   rather than answering with something else.
2. **Three deterministic phrasings, no model:** the question itself; its content words without stopwords; the question
   with the record ids the record route resolved appended. The keyword and meaning routes search each, and each route
   fuses its phrasings.
3. **The routes:**
   - keyword route: BM25 ranks;
   - meaning route: cosine to the question's vector (the query side through a separate GPU server, so questions never
     wait behind a rebuild);
   - record route and closure: the named records and their graph neighbours at radius 0 or 1;
   - code route: definitions, callers and callees of named symbols;
   - **the stated-links hop:** from what the record route or the closure reached, follow CITES, UNDER and OF_TASK
     outward, and AMENDS and SUPERSEDES **inward, from the changed decision to its changer**; at most 12 records, 2
     chunks each, placed after the closure's chunks.
4. **Fusion.** Reciprocal rank fusion (k 60) across routes, with an **authority lift** by tier (the Charter and the
   Contract, decisions and architecture records, the kernel's roles and skills, plans and tickets, reports, tests), so a
   governing source outranks a report that quotes it.
5. **The pool (v456; W2-32 S11, on its branch):** routes 60 deep instead of 30; the meaning route's phrasings fused
   without cutting back; the first 40 fused candidates reranked **once**, and every page of the answer cut from that one
   order. Each setting is off by default and switched on by configuration.
6. **The reranker** (W2-112): one shared service on the GPU for every agent on the machine, Qwen3-Reranker-0.6B today,
   reached over a local socket; **no private reranker beside it** (a slot guard holds the other GPU slot). Requests are
   **bounded by size as padded on the GPU**: at most 16 texts, and texts × the longest at most 24,000 characters (a count
   bound alone let a request exceed GPU memory). The service releases its cache after each request (window 4). A failed
   rerank is reported and the order falls back.
7. **Routing by question type:** a question naming a symbol puts the code route's first 2 hits ahead after the rerank; a
   question naming a record puts that record's 2 best chunks ahead.
8. **Crowding limits:** at most 2 chunks of one file in the first 10; an item whose lines lie inside an earlier item of
   the same file is dropped.
9. **Status in the bundle** (W2-92 S9): every register evidence item carries its entry's status word, the entries that
   change it, and whether it is in force; a PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED decision is marked not in force.
10. **The bundle:** at most 6,000 tokens, gathered in batches of 10; a gathered chunk is widened to its parent section
    within the budget; no span is sent twice across calls; what could not be gathered is listed with its reason.
11. **Continuations:** the next call resumes from a token; with the pool on, **the token carries the pool's reranked
    order** (a digest of the candidates and their positions, about 120 characters), so later calls send no rerank
    request and write no file; a token that does not match the question's candidates is refused.
12. **Role separation:** results are filtered by the caller's role paths, as the guard filters reads: an engineer never
    gets its own ticket's acceptance tests through a search; a test designer never gets the ticket's new code.

### 5.4 The machine's safety around memory (supporting, not memory itself)
- One GPU job at a time for measures and experiments; a **GPU backstop** pauses only the named process groups of a job
  when memory passes 15.5 GiB, an embedder loses layers or memory spills (never processes matched by name).
- Heavy test runs through machine-wide slots confined to their CPUs.

## 6. The measurement method
1. **The measure** (`gov.retrieval.measure`): each question's answer gathered by the real command; **hit@5** (a gold
   source among the first 5 stacked items), **full evidence** (every gold piece in the stack), and the **mean reciprocal
   rank** of the first gold source, from kept ranked outputs (every search's output is kept, so an approved label change
   is re-scored without running again).
2. **The rubric** (R1 to R11): correct today from the governing source, never a superseded decision; findable by
   meaning or marked keyword; unambiguous; the kind of question an agent really asks, never phrased from the answer;
   spread across code, decisions, tickets, the plan and the Contract; every source holds its answer; well formed; never
   from the evaluation's own documents; distinct; recorded; stable under ordinary work.
3. **Three sets, three jobs:** a **tuning set** (methods are tried on it); a **hidden check** (reported in counts only,
   never chooses); a **verdict set**, written blind, measured once at a decision point. **A set used to judge a fix is a
   tuning set from then on**; only a fresh set gives a verdict.
4. **Independent writers outside the agent system:** the hidden and verdict sets are written and cross-checked in
   sessions the owner opens, outside the tuning agent's system, which never sees a question, answer or source: ids and
   counts only. A writer never finds gold with the product's own search. An overlap check keeps a new set off the
   earlier sets' gold sources; an anchor check and a quota check run before the set is used.
5. **The hidden-half rule:** the hidden sets live outside every working tree, store and commit; reports about them are
   run through a **leak check** (no six-word run of a question or answer, no gold path or heading) before the tuning
   agent reads them.
6. **Structural fixes only:** no fix aimed at a named miss; each fix judged on all used sets together (hit@5, then
   MRR), adopted only if the total does not fall and the gap between the sets does not widen.
7. **Consistency is the proof:** the same structure must score within 5 points on different sets of about 80.
8. **The miss diagnosis by stage:** never retrieved; cut from the pool; a sibling of its section only; reranked below
   5; and by cause (vocabulary, crowding, the answer's form, a two-part question, a hop needed).
9. **The drift count:** of the decisions current though stated changed, how many a search reaching the decision also
   reaches a changer of.

## 7. Results so far (hit@5; counts only for the hidden sets)
| Point | What | Result |
|---|---|---|
| m1 | the baseline (48 questions) | 28/48 |
| m2g1 | the models read the whole chunk | 35/48 |
| m5 | + routing, phrasings, heading paths (the product) | 38/48 |
| m6 | the same on 80 questions | 65/79: visible 90.0 %, hidden 74.4 %, gap 15.6 |
| v456 | the deep pool and crowding limits | 67/79: 85.0 % and 84.6 %, gap 0.4 |
| + the stated links | the graph's links and hop | 67/79, gap 0.4; drift 184 → 0 unjoined |
| the blind verdict set (60), once | v456 + the links | 40/59 (67.8 %): disagrees with the halves |
| reranker trial (138 = 79 + 59) | 0.6B / mxbai-rerank-large-v2 / Qwen3-Reranker-4B 8-bit | 107 / 76 / 112; 1.8 / 2.1 / 3.9 s a search alone |
| W2-92 built (the links), against the control | the product's code | 67/79 = 67/79, MRR 0.6306 against 0.6242; 106/138 against 105; drift 0 → 190 of 190 |
| W2-32 built (the pool), pool on / off | the product's code | 107 / 108 of 138; the halves' gap 2.9 / 13.1; 1.20 / 1.48 s a call |

The 19 misses of the blind set: 10 reached the reranked pool but were ranked 6 to 12, 3 had only a neighbouring chunk,
2 were cut below the pool, 4 were never in a route's top 60; by cause: the reranker 6, vocabulary 4, crowding 4, the
answer's form 3, two-part questions 2. In 7 of the 19 an unlabelled chunk in the first five already answered.

## 8. What the CTO believes is new, and why (to be checked by your searches)
1. **Drift-aware retrieval over governance records.** Stated links built at rebuild from the records' own statements
   (labels and free text), with supersession and amendment kept apart so a partial supersession never hides its target;
   a hop that runs **inward from a changed decision to its changer**, bounded; and **status and changers marked on every
   register chunk** a bundle carries. Known temporal graphs (Zep/Graphiti) give facts validity intervals from
   conversation; known ADR practice marks status by hand; the CTO knows of no retrieval system that derives
   amendment links from a decision register's text and brings the changer into the answer for agents.
2. **A measurement discipline for a memory tuned by the agent system itself:** three sets with three jobs; "a used set
   becomes a tuning set"; writers and checkers outside the agent's system; the hidden sets outside every tree with a
   leak check on every report; consistency across sets as the acceptance proof; structural fixes only. Each piece has
   precedents (held-out sets, blind annotation); their combination as the operating rule of a self-tuning agent memory
   is believed new.
3. **Role-separated retrieval:** search results filtered by the caller's role paths, so a builder agent cannot find its
   own acceptance tests and a test designer cannot find the builder's new code, keeping role separation in a
   multi-agent software process.
4. **One shared GPU reranker for many agents with padded-size request bounds** (count × longest), memory released after
   each request, no private reranker, no CPU fallback, and a backstop that pauses by process group.
5. **A continuation that carries the reranked pool's order** in its token (a digest plus positions), so later pages of
   an answer need no rerank and no cache write.
6. **The combination:** hybrid keyword and meaning search, a record graph, a code graph and stated links, fused, reranked
   once from a deep pool, routed by question type and limited for crowding, in one token-budgeted bundle for agents,
   built from one fingerprinted rebuild of a governed repository.

## 9. Variations
- Other embedders and rerankers (larger, quantised, late-interaction, LLM listwise); the pool's depths (24 to 60).
- Answer-unit chunks (each list item, row or field its own chunk beside its section): measured, not kept yet.
- Free citations between decisions as links (4,987 pairs here), not built: they would crowd the closure.
- Links from contract capabilities to their provider tickets and decisions.
- Commit trailers (`Task:`, `Implements:`) as links from tickets to decisions.
- A link-integrity check that reports unmarked changes and unlinked ids as notices (`gov links`, W2-129, adopted).
- The same practice applied to any adopted repository at its Wave 0 (W2-88).

## 10. Open questions
1. **The vocabulary gap:** the blind set, phrased as agents ask, scores about 17 points below the tuned sets; is a
   stronger embedder, query rewriting, or term mapping the lever?
2. **The reranker:** the 4B gains +5 on 138 at twice the time; is a cheaper variant (24 candidates) as good; what does
   the reranker add at all against the fused order alone (DEC-1077 (c), being measured)?
3. **Labels:** in 7 of the 19 blind misses an unlabelled chunk already answered; how many misses are missing
   alternatives in the labels (a rubric item is coming, DEC-1076 (5))?
4. **Speed:** the deep pool costs a first call more; how far can the continuation and the service bring it down?
5. **Scale:** the figures are on one repository (19,113 embedded chunks); how do they hold on an adopted repository of
   ten times the size?
