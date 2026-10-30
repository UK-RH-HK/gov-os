# MEMORY-SPEC-MAP: the memory spec mapped to the tickets (DEC-954 Q9d), and the enlarged measure (Q9a)

From the W2 orchestrator's helper, 2026-10-30, for the owner. Draft. Read-only sources:
- the code at `w2/integrate` `29389754`;
- `.tickets/`;
- the WBS (revision 4) and PLAN-W2-DEC953;
- `docs/research/W2-61-baseline.md`, `docs/research/EXP-003/examin/README.md`;
- the Contract (CAP-08 to CAP-20, CAP-44);
- `governance/project/path-map.yaml`.

The hidden half was not read.

**The answer in one screen:**
- **Covered by tickets:**
  - semantic search: W2-86, W2-87, W2-32;
  - ranked lexical search: W2-13, W2-32;
  - freshness of the index: W2-06, W2-76;
  - the record graph's correctness: W2-03, W2-55, W2-87;
  - the measure: W2-61, W2-61h, W2-84, W2-15a/b;
  - the tools that build memory in an adopted repository: W2-88, new (Q9f).
- **Seven parts have no ticket, or only half of one.** Each is listed in §A.2 with why it is missing:
  1. full embeddings of this repository beyond `template/`;
  2. a graph route in plain-question retrieval;
  3. a code-graph route in plain-question retrieval;
  4. the store structure stated as a whole;
  5. an indexed vector store for very large repositories;
  6. W2-81's hidden question half;
  7. EXAMIN's question set.
- **A consequence for Q9c:** memory is judged through `gov retrieve`. A plain question today uses only the lexical and semantic routes. So the knowledge graph and the code graph earn no credit in the combined measure until gaps 2 and 3 are closed. Gap 3 is the code-graph route.

---

## A. The memory spec, part by part

States, as of 2026-10-30:
- **built:** in `w2/integrate`, from Wave 1 or merged;
- **open:** a ticket filed, not started;
- **running:** a lead is on it;
- **held:** built on its branch, not merged;
- **draft:** a ticket draft not yet filed.

### A.1 The map

| # | Part of the spec | What exists today (where) | Tickets that build or prove it, with state | Covered? |
|---|---|---|---|---|
| 1 | **Semantic search** (CAP-10, CAP-18, CAP-19) | `src/gov/retrieval/semantic.py` (W1-19): a vector per chunk of the lexical index, from Ollama's `qwen3-embedding:0.6b`. Questions are embedded on the CPU (DEC-798). The vectors are compared with sqlite-vec's cosine. RRF fusion with the lexical route and one rerank (`fusion.py`, `rerank.py`, `retrieve.py`) | W2-86 (draft): `template/` embedded. W2-87 (running, `DAEO-s9qc`): authority order. W2-32 (open): model pin and swap (CAP-10.b, CAP-19.a), chunking, the 85 row. W2-15a and W2-15b (open): the modes measured, the lighter-reranker spike included | **Yes** |
| 2 | **Lexical search** (CAP-11, CAP-18) | `src/gov/retrieval/lexical.py` (W1-17): an FTS5 table over line-aligned chunks. Exact strings and identifiers. Incremental by blob hash. **No ranking**: today it is an exact-match route | W2-13 (open, FULL): ranked BM25 with field weights, the exact route kept as a boost; it holds `src/gov/retrieval/lexical*` and `fusion*`. W2-32: tuning | **Yes**, the ranking is open |
| 3 | **Full indexing of this repository** (CAP-17, CAP-20) | Lexical: every tracked file (`git ls-files`) through the secrets filter, no include list. The code graph: built by `gov rebuild`. Rebuild time on a clone: 7 min 13 s to 44 min 54 s (W2-61 §2) | W2-06 (open): commit-time re-index (CAP-17.b), after W2-05 (held). W2-76 (running): rebuild timings and one rebuild at a time. W2-88 (draft): "every tracked file indexed or named with its reason", a coverage record that also runs here | **Yes** for the index. **Partly** for proof: nothing today reports which files were not indexed, and why. W2-88 adds that |
| 4 | **Full embeddings of this repository** (CAP-10.a, DEC-388, DEC-694) | Embedded: `.tickets/**`, `docs/**`, `src/**`, `tests/**`. **Not embedded:** `template/**` (W2-86 fixes it); root files (`CLAUDE.md`, `README.md`, `AGENTS.md`, …); `governance/**` (the overlay: prompts, briefs, packages, this plan, checkpoints, session summaries); `.github/**`; `cli/**` and `schemas/**` (carried code); `.claude/**` and `.rulesync/**` (generated copies); `fixtures/**` | W2-86 (draft): `template/` only | **No** beyond `template/`. See gap 1 |
| 5 | **The knowledge graph** (the record graph; CAP-08, CAP-09, CAP-13) | `src/gov/store/loader.py`: `.gov-runtime/store.db`, built from git `HEAD` alone. It holds the records with an `id` in their front matter, the eight typed edges, each register entry as its own record with its own hash (W2-03), and commits with their `Task:` and `Implements:` trailers. `gov closure` walks it (`src/gov/closure/`) | W2-03 (merged, closing): decisions as records. W2-87: a register chunk ranked as its own entry, not as the newest decision's. W2-55 (open): tags, and superseded and done entries left out, with the count. W2-04 (open): the packet names each decision by its hash. W2-64 (running): the record validator. W2-37 (held): `gov impact` over both graphs | **Partly.** The graph is built and corrected. In `gov retrieve` it is a route **only when the question names a ticket or ids** (`--ticket`, `--id`; `retrieve.py:125-133`). See gap 2 |
| 6 | **The code graph** (CAP-12) | `src/gov/codeintel/` wraps `codebase-memory-mcp` 0.11.0 (W1-16). It is built by `gov rebuild` into `.gov-runtime/codeintel/`. It answers definitions, references, callers, callees, impact and dead code. It is used by `gov closure` (a named symbol's callers and callees), by adoption's A4 (importers) and by `gov impact` (W2-37, DEC-859's paged queries) | W2-56 (running, claimed): the graph's folder inside the sandbox. W2-37 (held). W2-15b (open): the scale probe, graph cache included. W2-88: the graph built in adopted repositories of other languages (W2-81's Rust and TypeScript shapes) | **Partly.** It is built and usable by name. It is **not a route of plain-question retrieval**. See gap 3 |
| 7 | **The SQLite structure** | One `.gov-runtime/store.db` holds: the record graph's tables and `register_entries`; the lexical tables (`lexical_file` and the FTS5 chunks); the semantic tables (`semantic_vector`, `semantic_manifest`). Beside it: `.gov-runtime/query-vector-cache.db` (DEC-782) and the code graph's own databases under `.gov-runtime/codeintel/home/`. The rebuild's digest covers **the record graph only** (`loader.py:305`, as W2-86's draft notes). W2-61 saw the same digest after two rebuilds, while `store.db`'s bytes differed (W2-61 §2) | W2-03 (`register_entries`); W2-13 (the BM25 table); W2-06 (re-index); W2-76 (rebuild lock and timings); W2-32 (re-embed on a pin change); W2-88 (draft): a stated, versioned layout and a digest per store | **Partly.** Each ticket changes its own tables. Only W2-88's draft states the layout as a whole. See gap 4 |
| 8 | **The vector store structure** | float32 BLOBs in a plain table, compared one by one (a brute-force scan) with `vec_distance_cosine`. There is no `vec0` virtual table and no approximate index, by design: the store stays readable without the extension (`semantic.py` docstring). The manifest names the embedder and the reranker with their revisions | W2-15b (open): the scale probe measures the brute-force scan against DEC-078's envelope (W2-M351). W2-32: chunking and re-embed. W2-88 (draft): the query time measured on each proof repository, and a proposal if it is over budget | **Partly.** It is measured. Building an indexed store has no ticket. See gap 5 |
| 9 | **The tools that build indexes and embeddings in an adopted repository** (CAP-44, CAP-20) | `gov rebuild` builds every store where a path map and `.gitleaks.toml` exist. **On an unadopted clone it builds nothing and reports `"ok": true`** (W2-26's finding 2). Adoption (A0–A6, A8; W1-39, W1-41): A3 refuses a namespace with a bad embedding policy, and A4 indexes the code graph for importers. **There is no knowledge-fabric stage:** CAP-44.f's A9 ("new knowledge fabric") is Wave 3 in the Contract. Nothing assesses a large repository, and nothing plans what full indexing needs | **W2-88 (draft, new, Q9f).** Also W2-52 (held): lite A7 and A10 records (A10 is the independent memory verification); W2-23 (open): adoption safety; W2-81 (claimed): the synthetic repositories, their question sets and the judge; W2-27: the live trial on EXAMIN's copy | **Only by W2-88**, which is new. Before it, **no** |
| 10 | **The measure** (EXP-003, DEC-833, DEC-860) | `src/gov/retrieval/measure.py` (W2-61, merged `758cd53f`): both figures together, stacked in batches. The visible half is lens B's 20 questions. The baseline is 8 of 20 hit@5 (40 %), 12 of 20 full evidence (60 %), 14 of 20 in the bundle | W2-61 (merged, close due). W2-61h (open): the hidden half, re-scoped to the enlarged set (part B). W2-84 (built, serial phase left): the hidden half refused from every tree, with ACT 1's hook (Q9b). W2-15a and W2-15b: EXP-003's passes. W2-81: a question set per synthetic repository, with a visible half | **Yes** for this repository. **No** for two sets. See gaps 6 and 7 |
| 11 | *(Delivery: the context packet, CAP-15; batches, CAP-16)* | `gov context` (W1-24) and `gov retrieve`'s batches and continuation (W1-21) | W2-04 (open): bounded and reproducible. W2-54 (closed): the dropped list | **Yes** |

### A.2 The parts with no ticket, and why each is missing

1. **Full embeddings beyond `template/`.**
   - **Not embedded today:**
     - the root files;
     - the governance overlay (`governance/**`: prompts, briefs, packages, the plan, the orchestration record's searchable part, checkpoints);
     - `schemas/**` and `.github/**`.
   - **Why missing:** each was set "not embedded" by an earlier path-map decision. The overlay is DEC-856's governance memory, marked `sensitivity: restricted` and `export_policy: denied`, with DEC-887's record split. The carried code was set at Wave 1. W2-86 was scoped only to the kernel template's fault that lens B found (F6). No one has asked again since "full embeddings" became the owner's target.
   - **What stays out by necessity:**
     - `fixtures/**`, which holds the hidden half: an embedded hidden half would leak through `gov retrieve`;
     - `.claude/**` and `.rulesync/**`, generated copies that would double every kernel skill;
     - `cli/**`, the old carried code, which would compete with `src/`.
   - **Proposal:** a path-map line like W2-86's: embed the root files, `governance/**` (the overlay's own namespaces) and `schemas/**`. Est. 2 h, plus a rebuild and the measure. One check first: whether "restricted" sensitivity is read by the indexer or only by export. A W2-86b, or W2-86 widened before it is filed. **It needs the owner's word**, because the overlay is restricted.
2. **The knowledge graph as a route of plain-question retrieval.**
   - **Today:** `gov retrieve` adds the closure route only for the start ids it is given. A plain-language question is not linked to the records it names. For example, "what replaced DEC-723's listing refusal?" reaches the register only through words.
   - **Why missing:** Wave 1 built the graph for `gov context` and `gov closure`, which start from a ticket. DEC-791's tags (W2-55) leave records out of results but add no route. No ticket covers it.
   - **Proposal:** a small ticket. It links ids and record titles found in the question (exact id match, then a lexical lookup of titles) to start ids, so that the closure route joins the fusion at radius 0 or 1. It can only be judged with the enlarged measure's graph questions (part B).
3. **The code graph as a route of plain-question retrieval.**
   - **Today:** callers and definitions come only from `gov closure` or `gov impact` given a symbol's name. A "who calls X" question is answered by lexical and semantic text alone. In the baseline, Q10's first caller was at rank 25, outside the bundle, and lens B found none.
   - **Why missing:** W1-16 built the graph as a tool for `closure` and `impact`, and CAP-18's acceptance names a "graph route" that Wave 1 read as the record closure. No ticket covers it.
   - **Proposal:** fold it into gap 2's ticket. A symbol name in the question is asked of the code index (callers, callees, definition), and its file spans join the fusion as a route.
   - **Without gaps 2 and 3,** the "knowledge and code graph" of Q9c is built but earns nothing in the combined measure.
4. **The store structure stated as a whole.**
   - **Today:** each ticket adds its own tables. There is no layout version, no rule for what happens when the layout changes, and no digest that covers the lexical and vector stores. So "the right structure in SQLite and the vector store" (Q9c) has no definition to judge against.
   - **Why missing:** Wave 1 grew the store table by table under separate tickets (W1-10, W1-17, W1-19). CAP-20's digest was specified over records.
   - **Proposal:** W2-88's draft takes the minimum: a stated, versioned layout in `src/gov/store/layout.py`, a store of another version rebuilt and never read, and a digest per store in the rebuild's record. A wider structure review has no ticket and is not proposed for Wave 2. Examples: one database or several, the FTS5 tokenizer, the chunk table's keys.
5. **An indexed vector store for very large repositories.**
   - **Today:** the scan is brute force. That is fine at this repository's size (2,521 tracked files). It is unmeasured at "however large".
   - **Measured nearest:** `~/workspace` has 77,346 code-graph nodes and 270,647 edges, at 2.2 GB peak RSS (DEC-078). The ARGUS stress tier has 57,777 chunks (DEC-071).
   - **Why missing:** DEC-379 and DEC-381 chose a plain table so that the store opens without the extension. Scale was left to EXP-003's probe (W2-15b).
   - **Proposal:** W2-15b and W2-88 measure the query time on the largest proof repositories. If it is over the retrieve budget, W2-88 returns a CIT-P (`vec0`, or an approximate index) as a package. No ticket builds it before the measure says so.
6. **W2-81's hidden question half.**
   - **Today:** the WBS card "W2-81's held-out half (proposed companion; … id the orchestrator's)" was never filed.
   - **Why missing:** the card waited for W2-81's README to state the half's form, and W2-81 is claimed with no commits.
   - **Proposal:** file it when W2-81's builders and README exist. Without it, W2-81's question figures are on its visible half only, and so are W2-88's.
7. **EXAMIN's question set.**
   - **Today:** W2-61's KPI 6 says "the same split for EXAMIN's set, written by a session independent of the adopting team before W2-27". No such set exists: `fixtures/evaluation/` holds `memory-retrieval` only.
   - **Why missing:** W2-61 delivered the tool and the visible half. The EXAMIN set needs an independent session with a ticket of its own, which was never filed.
   - **Proposal:** a small independent-auditor ticket, about 10 to 20 questions with a visible and a hidden half. It is written from a clone of the owner's copy before W2-27. W2-61 should not close while this KPI is open unless its close record names the KPI as moved to that ticket.

**Also noted, not a gap of the spec:**
- The `evaluation_sets.memory-retrieval.measures` block in the path map lists roles (`engineer`, `research`).
- W2-61's own text says it narrows this to tickets.
- When the set is enlarged, the measured tickets must include W2-86, W2-87, W2-88, W2-13, W2-55, W2-04 and W2-32. That is a path-map edit by the CTO.

---

## B. Q9a: the enlarged question set

### B.1 The proposal

- **Size: 48 questions, 24 visible and 24 hidden.** That is about double today's 20, under the owner's ceiling of 50.
- **The visible half (24):** lens B's 20, unchanged, plus 4 new.
- **The hidden half (24):** all new.
- **The 28 new questions are written by one unmeasured independent auditor.** That is W2-61h, re-scoped from "20 hidden" to "28 new". The CTO starts it, never a retrieval lead, as W2-61h was set up. The auditor writes all 28 first. Then a recorded, seeded draw, stratified by category, sends 4 to the visible half and 24 to the hidden half, so the hidden half is not hand-picked. The 4 visible ones are drawn one each from the categories lens B's 20 lack: exact string, history, failure memory and multi-file.
- **Its spread covers the combined memory spec (Q9c).** The 28 new questions:

| Category (the spec part it tests) | New questions |
|---|---|
| Decision and supersession, at least 2 whose naive answer is superseded (the knowledge graph; W2-55, W2-87) | 5 |
| Exact string, identifier or error message, answered with file and line (lexical; CAP-11; W2-13) | 4 |
| Callers, callees, definitions (the code graph; CAP-12; gap 3) | 4 |
| Code facts by paraphrase (semantic; CAP-10) | 3 |
| Kernel template: role files, skills, hooks (W2-86) | 3 |
| Multi-file, stacked across batches (at least 3 needing 2 or more files; CAP-16, DEC-860) | 3 |
| History: which commit, ticket or decision changed a file (CAP-13) | 2 |
| Failure memory: a failed approach before a retry (CAP-14) | 2 |
| Plan, ticket or path-map fact (records) | 1 |
| An id that exists nowhere: the stated gap (DEC-900) | 1 |
| **Total** | **28** |

- **Precision:** at p = 0.85, a 95 % interval:
  - ±15.6 points on 20 questions;
  - ±14.3 on 24;
  - ±10.1 on 48.
  - One question is 5 points of 20, and 4.2 of 24.
  - CAP-10's floor of 85 means at least 17 of 20, or 21 of 24.
- **Which figure counts (recommendation, confidence medium-high):**
  - K9's "memory proven" is judged on the **hidden half**: at least 21 of 24 hit@5, with full evidence against 99 %.
  - The visible half and the 48 together are reported beside it.
  - The reason: the visible half is the one the improvement tickets are tuned against. W2-86 and W2-87 already target its Q17 to Q20.
  - Alternative: judge on all 48 (at least 41 of 48).
- **The hidden half's protection (Q9b):** it is used only after ACT 1's hook (rule 2) and W2-84 refuse it from every worktree and run clone. The orchestrator runs it and records scores only.

### B.2 The time cost

**Run time, measured.** The source is W2-61's three runs of the 20 visible questions on one clone, by the pinned gov, with the default budgets (`docs/research/W2-61-baseline.md` §3, start and end in UTC). The loads differed: the 1-minute load was 10 to 53 at the rebuilds' starts.

| Run | Wall time | Per question |
|---|---|---|
| 1 | 18 min 31 s | 55.6 s |
| 2 (the repeat) | 28 min 13 s | 84.7 s |
| 3 (after a rebuild) | 11 min 18 s | 33.9 s |
| **Median** | | **55.6 s** (mean 58.1 s) |

**Projected for 48** (34 s to 85 s a question, median 56 s; estimates from the measured rate):

| Use | Today (20 visible) | Enlarged |
|---|---|---|
| One re-measure of the visible half (each memory ticket; W2-86 and W2-87 run it twice, control and head) | 18.5 min (11–28) | 24 questions: **22 min** (14–34); twice: 44 min (27–68) |
| The hidden half, once (the orchestrator) | — (not written) | **22 min** (14–34) |
| Both halves, once | — | **45 min** (27–68) |
| W2-61's full protocol (run, repeat, rebuild, run again), both halves | — | **2.2 h** (1.4–3.4 h) + one rebuild (7–45 min, W2-61 §2) |

- **Writing cost (estimate, unmeasured).**
  - The plan's W2-61h estimate is S 9.2 h for 20 questions, a profile median: no hidden-writing session has run yet, and lens B's writing time is not recorded.
  - For 28 that is **est. 12–14 lead-hours**, one auditor session or two. Each gold source is checked at the commit read.
- **The added cost per memory ticket** is about 4 minutes per visible run (24 against 20 questions). The hidden half adds 22 minutes, run by the orchestrator only at the memory milestones: W2-15a, after each W2-32 round, W2-15b, and before K9.

### B.3 Who writes what

| Half | Writer | Ticket |
|---|---|---|
| Visible: lens B's 20 | lens B (already written) | W2-61 (merged) |
| Visible: 4 new | the unmeasured independent auditor, drawn from its 28 | W2-61h (re-scoped) |
| Hidden: 24 new | the same unmeasured independent auditor, never a retrieval lead | W2-61h (re-scoped) |
| W2-81's synthetic repositories: visible | W2-81's independent test designer | W2-81 |
| W2-81's synthetic repositories: hidden | an independent auditor | W2-81's companion (not filed, gap 6) |
| EXAMIN's set, both halves | an independent auditor, independent of the adopting team | not filed (gap 7) |
| W2-88's two real GitHub repositories: visible only, 10 each | W2-88's independent test designer | W2-88 |

**Open for the owner:**
- (a) the size (48, or 50 as 25 and 25);
- (b) which figure counts for K9 (the hidden half, recommended, or all 48);
- (c) gap 1's path-map line (the overlay is restricted);
- (d) one small ticket for gaps 2 and 3 (the graph and code-graph routes in plain-question retrieval);
- (e) filing gaps 6 and 7.
