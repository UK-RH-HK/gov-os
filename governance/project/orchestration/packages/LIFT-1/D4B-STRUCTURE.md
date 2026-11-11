# D4B-STRUCTURE: memory's structural review (DEC-1071 (1))

- **For:** the owner, before any structural fix.
- **By:** the CTO, 2026-11-04 ~22:30.
- **The measured product:** m6's clone (`24f06026`), the store as built, the live 0.6B reranker.
- **Evidence:**
  - the whole index (69,464 keyword chunks; 19,113 embedded, from 1,126 files) and the record graph;
  - the 80 questions' gold, per half, counts only for the hidden half;
  - m6's kept ranked outputs; the route-depth probe; stage A's runs;
  - W2-61h's role's kinds for the hidden half (`docs/audit/memory-recall-diagnosis-hidden.md`).
- **Scripts:** `drafts/d4b/structural.py`, `diag_recall.py`, `diag_depth.py`, `diag_routes.py`. Records are in
  `~/gov-os-runs/D4B/diag/`.
- **No fix here is aimed at a named question.** Each changes how the whole memory is chunked, embedded, ranked or
  linked.

## 1. The finding in one paragraph
The halves differ in what they are made of:
- The hidden half's answers are more often a list item (18 of 38 main answers, against 13 of 40 visible) in a chunk
  that does not carry its section heading (20 of 38, against 13 of 40).
- On all 78 scorable questions, those two traits cost about 16 points of hit@5:
  - an answer chunk without its heading hits 73 % (24 of 33), with it 89 % (40 of 45);
  - a list-item answer hits 71 % (22 of 31), otherwise 89 % (42 of 47).
- So the gap is in large part structural. Memory finds sections well and the items inside them poorly. The questions
  chosen to tune it were richer in sections.

The authority tier does not explain the gap: governing gold hits 14/16 visible and 12/16 hidden; middle-tier gold
22/24 and 16/22. The closure does not crowd the 20.

## 2. The weaknesses, the evidence and the fix for the whole memory

### Chunking
**C1. Chunks are cut by size, not by meaning.**
- Embedded chunks are about 1,000 characters (median 951, 90th percentile 1,181).
- 2,772 of 7,553 sections are split into two or more chunks, and 14,332 of the 19,113 embedded chunks (75 %) are a
  piece of a split section.
- The gold:
  - visible: 58 of 68 pieces lie in a split section, and 21 in a chunk without the section's first line;
  - hidden: 44 of 52 and 25.
- The fix C1 has two parts:
  - **every chunk carries its heading path**, in all three places it is read. Today it is only in the embedding (the
    headers method). The keyword index and the reranker read the bare text.
  - Cheap: no re-chunking, a keyword re-index and no re-embed.

**C2. An answer that is one item is diluted in its chunk.**
- The answer is a list item, table row, field or one or two lines in:
  - 43 of 68 visible pieces (27 list items);
  - 37 of 52 hidden pieces (24 list items).
- The answer is under a quarter of its chunk's lines in 38 of 68 visible pieces and 28 of 52 hidden pieces.
- Kinds: K7 (form) in all 7 hidden recall misses; K4 (diluted) in 6.
- The fix C2 is **answer-unit chunks**:
  - each list item, table row and field block becomes a small chunk of its own, with its heading path;
  - they sit beside today's chunks, so a section question still finds the section;
  - the bundle widens a unit to its section within budget.
- Larger: a re-chunk and a re-embed.

**C3. Code is cut away from its definitions.**
- 2,553 of the 4,389 Python chunks (58 %) start mid-body.
- 432 of 1,812 definitions run past their chunk.
- The gold: 7 of 20 visible code pieces and 6 of 15 hidden ones lie in a chunk that does not start at its definition.
- K3 in 2 hidden misses.
- The fix C3 is **code chunks cut on definitions**: **M2**, built, off, being measured now.

### Embedding
**E1. Duplicated and generated copies.**
- 82 groups of identical chunks across files, 182 chunks in all (1 % of the embedded):
  - the assessment copies of project files;
  - the kernel template against its generated copies;
  - `AGENTS.md` against `CLAUDE.md`.
- Small in the index, but they take several places in a 20 when they match (h33's kind: four copies).
- The fix E1 is **one place per identical text** in the fusion, the copy in the higher authority tier kept. Stage A's
  v6 drops nested repeats within a file; this extends it across files.

**E2. Truncation.** Only 11 embedded chunks exceed the embedder's 10,000 characters. **Not a lever.**

### Ranking
**R1. The routes stop at 30, and the meaning route is cut back to 30 after its phrasings are fused.**
- Gold within the better route's top 30, 60 and 100:
  - visible: 42, 45 and 48 of 68 pieces;
  - hidden: 39, 40 and 43 of 52.
- The phrasing cut drops 2 visible pieces and 3 hidden ones that one phrasing found.
- The fix R1 is the meaning route uncut, and routes 60 deep: **v1 + v2** of stage A.

**R2. The reranker sees only 20, and only the bare text.**
- Gold in the fused list but cut below 20: 12 visible pieces and 5 hidden.
- Pieces in the 20 but ranked below 5: Q14, Q19 and 3 hidden questions.
- The fix R2:
  - **40 reranked** (v3; also faster: 0.34 s against 0.75 s a search, since one pass replaces the pages' passes);
  - the reranker reads each chunk's **record title and section path** beside its text (`decorate`, C1's reranker
    half).

**R3. Crowding by one file.**
- K5 in all 7 hidden recall misses: the same topic restated across tiers and copies.
- The fix R3 is **at most 2 chunks of a file in the first 10** (v5), with **nested repeats dropped** (v6).

**R4. The authority lift.** The gap shows in every tier (section 1). **Not a lever now.**

### The graph
**G1. Supersession and amendment are text, not edges.**
- The register states 103 supersessions or amendments in its entries' text (66 `Amended`/`Supersedes` lines). The
  graph holds **3** `SUPERSEDES` edges and 743 `DEPENDS_ON`.
- The register's 1,065 entries cite other decisions 9,111 times; none of these is an edge.
- K6 (a hop) in 2 hidden misses. 0 visible questions name one record whose answer lies in another register entry.
- The fix G1 has two parts:
  - **the register's own supersession, amendment and citation statements become graph edges** at rebuild;
  - the closure follows `SUPERSEDES` and `AMENDS` one hop from a gathered record (DEC-952's authority order is
    unchanged).
- It also mends what an agent sees as current.

**G2. Dependents beyond one hop.** **M3**, built, off, being measured now.

**G3. The closure.** It does not crowd: closure-only chunks average 0.2 of the 20, and the misses have none.
**Not a lever.**

## 3. The rule (DEC-1071 (2))
- Each fix is judged on **all 80 together**, hit@5 then MRR, with the hidden half in counts.
- **It is adopted only if the 80 do not fall and the gap between the halves does not widen.**
- The h24 kind (`nonexistent-id`) is scored apart (DEC-1071 (5)) from the next measure on. So the 80 are 79 for
  hit@5, plus the nonexistent-id check.
- **The baseline, m6 scored this way:**
  - hit@5 65/79: visible 36/40 (90.0 %), hidden 29/39 (74.4 %), a **gap of 15.6 points**;
  - MRR: visible 0.6907, hidden 0.4966;
  - nonexistent-id 1/1 (h24 stops with `UNRESOLVED_IDS` naming the one id it asks).

## 4. The plan and the order
One GPU job at a time. Each fix is measured alone on the current best, three runs once it is adopted.

| Step | Fix | How | Cost | Owner |
|---|---|---|---|---|
| 0 | M1-M5 alone (running since 21:39) | `measure_m.sh`, one run each | ~75 min left | - |
| 1 | Stage A re-judged: v4 + v5 + v6 (R1, R2's 40, R3) | harness, three runs | ~20 min | the order given |
| 2 | R2's reranker text: `decorate` (title and section), on step 1's best | harness, one run, then three | ~7-20 min | - |
| 3 | M2 (C3) and M3 (G2), if step 0 shows them right, on the best | `measure_m.sh` with the flags | ~20 min each | - |
| 4 | E1, one place per identical text across files | a harness switch (small) | ~7 min | - |
| 5 | C1's keyword half: the heading path into the keyword index | a research prototype in a measure clone, then a product change | half a day | approves the product change (W2-32) |
| 6 | C2, answer-unit chunks | a research prototype (chunker), a re-chunk and re-embed in a measure clone | a day | approves the method before it is built into the product |
| 7 | G1, register statements as edges, and the one-hop supersession closure | a research prototype in a measure clone (rebuild) | a day | approves the graph change |
| 8 | When the halves agree within 3 points: memory-verdict (60) once | `measure.py memory-verdict --part hidden` | ~25 min | told before; if it disagrees, to the owner first |
| 9 | Then the rerankers: 0.6B, mxbai, Qwen3-4B 8-bit, on the three sets | `trial_model.sh` (its wait fixed) | ~2 h | decides |

- **The order:**
  - the cheap query-time levers first (1, 2, 4);
  - then the built index methods (3);
  - then the three structural rebuilds (5, 6, 7), in order of evidence: C1 and C2 together reach the trait behind
    the 16-point split, so 5 and 6 come before 7.
- **Adoption into the product:** what steps 1-4 adopt is built into the product for re-pin window 4. Steps 5-7 are
  prototyped and measured first; each comes to the owner as a product change, with its figures, before it is built.
- **Stopping:** when visible and hidden hit@5 agree within 3 points (1 question in 40), with the 80 not lower than
  m6. If the structural steps are exhausted first, the owner gets the figures and the remaining gap.

## 5. What the owner is asked
1. Whether the order stands.
2. Approval for steps 5-7 as research prototypes in measure clones only: no product change until their figures come
   back.
