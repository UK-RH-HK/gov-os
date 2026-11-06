# Building memory for a repository: the practice learned in D-4b (DEC-1072 (2))

- **Status:** a living record, kept up to date as D-4b goes. It becomes a kernel skill after the refactoring.
- **Owner ticket:** W2-88 (`DAEO-2bdu`), memory for any repository at adoption.
- **Who uses it:** whoever builds memory in an adopted repository's Wave 0: the W2-88 engineer, the adopting team,
  and later the kernel skill.
- **Sources:** DEC-1009, DEC-1060, DEC-1066 to DEC-1072; the rubric (`docs/research/memory-measure-audit/RUBRIC.md`);
  the structural review (`governance/project/orchestration/packages/LIFT-1/D4B-STRUCTURE.md`); the measures' records
  under `~/gov-os-runs/D4B/` (figures only are quoted here).

## 1. How the store is built
- **Four stores:**
  - the record graph (records, edges);
  - the keyword index (SQLite FTS5, BM25, `porter unicode61`);
  - the vectors (an embedder on the GPU, sqlite-vec);
  - the code graph.
- **The path map decides which namespaces are embedded.** Everything else is keyword-only. In this repository, 19,113
  of 69,464 chunks are embedded, from 1,126 files. The evaluation set's own documents are indexed nowhere (G4).
- **Chunking:**
  - Chunks are sized at about 1,000 characters, inside parent sections.
  - Python chunks may be cut on definitions (M2's `chunk_code_by_definition`). The register may be cut one entry per
    span (M5).
  - **The lesson:** size-based chunks split 75 % of embedded chunks off their section, and bury one-item answers.
    Plan chunking by meaning from the start: answer units (list items, rows, fields) with their heading path, beside
    section chunks. This is being prototyped as D4B-STRUCTURE C2.
- **Embedding:**
  - Each chunk is embedded with a header: its path and the headings above it (`embed_headers`, adopted).
  - Up to 10,000 characters per chunk; the embedder cuts silently above its 4,096-token context.
  - The reranker reads up to 24,000 characters with the path.
  - **The lesson:** give the heading path to every reader of a chunk (the keyword index and the reranker too), not
    only the embedder (C1).
- **Links:**
  - The record graph holds the edges the records state in their own fields: 743 `DEPENDS_ON`, 9 `CONSTRAINS`,
    3 `SUPERSEDES` and 2 `IMPLEMENTS` here.
  - **The census** (`docs/research/D4B-link-census.md`) counted every link the repository states:
    - 37,815 distinct pairs across 65 kinds, of which the graph held 895 (2.4 %);
    - of about 9,000 pairs that involve a decision, 6 were edges;
    - no ticket reached the decisions it cites;
    - commit trailers were neither indexed nor edges.
  - **The drift:** 215 decisions read as current although the register or the archive says they were changed. 87 of
    them carry no hint in their own entry.
  - **The lesson:** census the stated links first. Build each kind as typed edges (ticket → decision; supersedes and
    amends kept apart, so a partial supersession never hides its target; `Under:`). Measure drift as well as hit@5.
- **Retrieval:**
  - three phrasings (no model);
  - keyword and meaning routes, 30 each;
  - the record route and the closure;
  - the code route;
  - RRF (k = 60) with an authority lift;
  - 20 chunks reranked per call (Qwen3-Reranker-0.6B);
  - routing by question type;
  - a 6,000-token bundle.

## 2. How it is measured
- **The measure:** W2-61's `gov.retrieval.measure`. It reports hit@5 (a gold source in the first 5 stacked items) and
  full evidence (every gold piece in the stack). Each search's ranked output is kept, so a label change is re-scored
  without running again.
- **The rubric (R1-R11),** applied to every question:
  - correct today, from the governing source;
  - searchable by meaning, or marked as a keyword question;
  - unambiguous;
  - the kind agents ask;
  - spread across code, decisions, tickets, the plan and the Contract (R5: each domain at least 10 %, no subsystem
    over 25 %);
  - every source holds its answer;
  - well formed;
  - never from the evaluation's own documents;
  - distinct;
  - recorded;
  - stable under ordinary work (R11).
- **Three sets, three jobs (DEC-1070):**
  - **The tuning set** (visible, 40): methods are tried on it.
  - **The hidden check** (40): reported in counts only, kept outside every tree and read only by the measure.
  - **The measurement set** (`memory-verdict`, 60):
    - written fresh and blind by a writer outside the CTO's system, cross-checked by a second fresh session;
    - never used to choose;
    - measured only at decision points;
    - its figure is the verdict.
- **The writers are independent of the retrieval work.** A writer never reads search results, the other sets, or the
  research that names misses. It never finds gold with the product's own search: a set built with the product favours
  what the product finds.
- **The hidden-half rule:** no hidden question, answer, path, heading or line reaches the tuning session. Ids, counts,
  ranks and kinds only. A label is corrected only by an independent checker (the owner's operator).
- **Scoring:** hit@5, then the MRR of the first gold source (DEC-1070 (9)). A question about an id that exists nowhere
  is scored apart: it passes when the product stops with `UNRESOLVED_IDS` naming that id (DEC-1071 (5)).

## 3. How it is tuned (DEC-1071)
- **Structural fixes only:** chunking, embedding, ranking, the graph. Never a fix aimed at a named question.
- **Judged on all sets together** (hit@5, then MRR). A fix is adopted if the total does not fall and the gap between
  the halves does not widen.
- **Consistency is the proof:** the same product must score within 3 points on different sets. Then the measurement
  set is measured once, as the confirmation.
- **Diagnose before fixing:** classify every miss by where it is lost. The stages: never searched, in no route's top
  30, a sibling only, a phrasing cut, cut from the reranked pool, reranked low. Then turn the kinds into structural
  weaknesses measured across the whole index.
- **Models last:** a reranker or embedder trial comes after the structure is sound, on all three sets, with speed and
  GPU figures beside quality.

## 4. Every method tried, with its figures
The figures are hit@5. The 48-question set ran from m1 to m5 (24 visible + 24 hidden); the 80-question set from m6 on.

| Method | Measure | Visible | Hidden | Adopted | Why |
|---|---|---|---|---|---|
| Baseline (pin) | m1 | 12/24 | 16/24 | - | - |
| G4: the evaluation documents out of the index; re-labels | m2 | 13/24 | 16/24 | yes | an honest measure (effect 0) |
| G1: the models read the whole chunk | m2g1 | 18/24 | 17/24 | yes | DEC-1066 (chosen with all 48 in view) |
| x5: routing by question type + three phrasings | measure 3 | 20/24 | 17/24 | yes | the visible rule (tie, fewer methods) |
| x7: x5 + the reranker shown title and section + expansion | measure 3 | 20/24 | 17/24 | no | tie; more methods |
| Contextual headers in the embedding | measure 4 | 21/24 | 17/24 | yes | the visible rule |
| The product with all the above | m5 | 21/24 | 17/24 | - | - |
| The same, on the 80 questions | m6 | 36/40 | 29/40 | - | the baseline |
| The meaning route uncut after phrasings | stage A v1 | 35/40 | 30/40 | no (visible rule) | to re-judge on all 80 |
| Routes 60 deep | v2 | 34/40 | 30/40 | no (visible rule) | to re-judge |
| 40 reranked | v3 | 34/40 | 30/40 | no (visible rule) | to re-judge |
| v1 + v2 + v3 | v4 | 33/40 | 33/40 | no (visible rule) | re-judged with v5 + v6 (DEC-1071 (2)) |
| At most 2 chunks of a file in the first 10 | v5 | 36/40 | 29/40 | yes (MRR) | small |
| Nested repeats dropped | v6 | 36/40 | 29/40 | yes (MRR) | small |
| v5 + v6, three runs | v56 | 36/40 | 29/40 | yes | MRR 0.6925 visible, 0.4912 hidden |
| M1, a file-level index | m6-M1 | 36/40 | 30/40 | to judge on all 80 | MRR 0.7015 visible, 0.4835 hidden |
| M2, code chunks cut on definitions | m6-M2 | 36/40 | 29/40 | to judge | no change (embedded code changed by 50 chunks) |
| M3, dependents beyond one hop | m6-M3 | 37/40 | 29/40 | no (DEC-1071) | the 80 rise, the gap widens (92.5 against 74.4) |
| M4, identifier tokenisation | m6-M4 | 36/40 | 29/40 | no | MRR lower |
| M5, one span per register entry | m6-M5 | 34/40 | 30/40 | no (retest with the links) | the 79 fall by 1 (gap 8.1) |
| **v456 = v4 + v5 + v6** (judged on the 79, DEC-1071) | fix-b | 34/40 | 33/39 | **yes** | the 79 at 67 (from 65); **gap 15.6 → 0.4**; 0.34 s |
| M1 + v456 | fix-c | 34/40 | 33/39 | no | a tie; MRR over the 79 lower (0.6300 against 0.6313); 1.0 s |
| v456 + the reranker shown title and section | fix-d | 32/40 | 34/39 | no | the 79 fall, the gap widens |
| v456 + one place per identical text | fix-d | 34/40 | 33/39 | no | no effect |
| C1, the heading path in the keyword index | p1 | 33/40 | 34/39 | no | a tie with its control (p0: 33/34, gap 4.7); MRR lower |
| C2, answer-unit chunks (26.8k more) | p2 | 35/40 | 32/39 | no | the gap widens (5.4) |
| C1 + C2 | p3 | 35/40 | 31/39 | no | the 79 fall |
| **The stated links** (ticket → decision, amends/supersedes, `Under:`, front-matter ids) + a bounded hop | g1 | 34/40 | 33/39 | **yes** | nothing falls; **drift 184 → 0 unjoined** |
| The stated links + M5 | g2 | 33/40 | 34/39 | no | the gap widens |
| **The measurement set, its single use, on v456 + the links** | verdict | — | — | — | **40/59 (67.8 %)** against 85.0 / 84.6: disagrees |
| The 19 misses of the spent 60, by kind (an independent auditor, counts only) | D4B-MISSES | — | — | — | ranked below 5: 10, vocabulary 4, never retrieved 3, other 2 |
| Reranker: Qwen3-Reranker-4B 8-bit, 40 reranked (the 138 = the 79 + the spent 59) | trial | 35/40 | 34/39 | no | 112/138 against 107; 11 gains, 6 losses, McNemar p 0.33; 3.89 s alone; over the GPU budget |
| Reranker: mxbai-rerank-large-v2 (its own template, checked on a stand-in) | trial | 27/40 | 23/39 | no | 76/138 |
| Reranker: the 4B at 24 reranked | trial | 36/40 | 32/39 | not yet (DEC-1079) | 112/138; 9 gains, 4 losses, p 0.27; 2.84 s alone, 33 s at 20 at once |
| No reranker (the fused order alone) | trial | 35/40 | 28/39 | — | 95/138: the reranker is +12 net (21 lifted, 9 pushed out, p 0.04); without it the sets' spread is 33.3 against 17.2 |
| **W2-92 built: the stated links in the product** | w4-92 | 33/40 | 34/39 | **yes**, merged | the 79 67 = the control 67, MRR 0.6306 against 0.6242; drift 0 → 190 of 190 |
| W2-32 built: v456 as five pool settings, pool on / off | w4-32b / c | 34/40 / 36/40 | 32/39 / 30/39 | pending (wording) | 107 / 108 of 138; the halves' gap 2.9 / 13.1; 1.20 / 1.48 s a call |

Night one's survey (63 variants on all 48) and night two's (32 on the visible half) also found:
- **Losers:** pool quotas, a global pool, an embedder instruction, a reranker instruction, authority ×2.
- **Neutral:** route agreement, a blend.
- **Speed:** every method within 0.08 s.

**From m6-M1 on, the figures are judged on the 79** (h24, the nonexistent-id question, scored apart): adopted when
the 79 do not fall and the halves' gap does not widen, then by MRR over the 79.

## 5. The lessons
1. **Overfitting to the tuning set.**
   - The visible half rose from 12 to 21 of 24 while the hidden half stayed at 16 to 17. Every method was chosen by
     looking at the visible half's misses, two of them with all 48 in view.
   - When recall was widened, the visible half fell and the hidden half rose: its hits depended on the exact pool
     it was tuned on.
   - **The practice:** three sets with three jobs, structural fixes only, consistency as the proof.
2. **Labels checked because questions missed.**
   - Missed questions were the ones whose labels got checked, on both halves, so the labels were not audited evenly.
   - **The practice:** labels are audited on a schedule, all questions at once, never because one missed
     (DEC-1070 (14)).
3. **The halves were not alike.**
   - The hidden half held more one-item answers in chunks without their heading. That is a structural trait, which
     cost about 16 points of hit@5 across all 80.
   - **The practice:** measure the gold's structure (form, dilution, heading) per set, and fix the structure.
4. **The GPU trips** (twice, the night of DEC-1067).
   - The reranker's requests were bounded by text count only, then by summed characters; padding to the longest text
     exceeded memory.
   - **The practice:**
     - bound each request by count × longest text (24,000 characters, 16 texts);
     - a GPU backstop at 15.5 GB;
     - one GPU job at a time;
     - the reranker's memory released after each request (window 4).
5. **Process hazards seen on the way.**
   - `git bisect` from a linked worktree re-initialised the repository (`core.bare`). Bisect only in a throwaway clone.
   - Stopping processes by a text match killed another agent's work. Stop only by named pids.
   - A measure script on a clone with an uncommitted setting was refused by the re-pin's clean-tree check. Commit the
     setting in the throwaway clone.
6. **Agreement between two tuned halves is not the verdict.**
   - The halves came within 0.4 points; the blind measurement set scored 17 points lower.
   - Its questions share the fewest words with their answers (median 0.41, against 0.50 tuning and 0.43 hidden), which
     is a vocabulary gap that structure does not close.
   - Content change alone moved the halves by one question each way, so a 3-point bound on 40 questions is within
     noise.
   - **The practice:** keep the blind set for the verdict, profile the sets' phrasing, and treat vocabulary (the
     embedder, the query) as its own lever.
   - **The owner's reading (DEC-1074 (1)):** the gap is mainly that both halves had become tuning sets once every fix
     was judged on all 80, with vocabulary a smaller part. The hidden half and the blind set are about equally far
     from their answers (0.43 against 0.41), yet score 84.6 % against 67.8 %.
   - **The practice:**
     - a set used to judge a fix is a tuning set from then on;
     - only a fresh blind set gives a verdict, used once;
     - consistency is judged within 5 points, on sets of about 80;
     - the next lever is chosen from the misses' kinds (never retrieved against ranked low).
7. **A question about something that does not exist** cannot be scored by hit@5 when the product rightly returns
   nothing. Score it apart.

8. **Say whether a gain is more than chance.** On 138 questions one question is 0.7 points; the 4B's +5 came from 11
   gains against 6 losses (exact McNemar p 0.33). **The practice:** every comparison reports its gains, its losses and
   an exact McNemar test (DEC-1079).
9. **Measure what each component adds.** The reranker against the fused order alone: +12 net (p 0.04), and it is what
   makes the sets agree (spread 17.2 against 33.3). **The practice:** an ablation of each component before choosing its
   model.
10. **Check a model's input before judging it.** Render one pair through the loaded module (or a stand-in with the
    model's own configuration and tiny weights) and compare it with the model card.
11. **Labels must not chase copies.** A gold source and its generated twins (the Contract's Markdown and YAML, the
    capability pages) are one source family, counted by the measure's code (DEC-1078 (4)); the cross-check lists every
    other place that states an answer (DEC-1076 (5)).
12. **Keep each measure's inputs fixed.** A script that copied a branch's re-labelled question into the shared sets
    root broke the next runs; a measure checks the sets root against the integrated labels before it starts.

## 6. For an adopted repository's Wave 0 (the practice in order)
1. Assess the repository, and plan its refactoring for full indexing (W2-88's KPIs).
2. Census its stated links (records, front matter, trailers, text). Build the graph from them.
3. Chunk by meaning (sections, answer units, code by definition), and give every reader the heading path.
4. Write the three sets by independent writers under the rubric. Keep the hidden check and the measurement set outside
   every tree.
5. Measure. Diagnose by stage and by structure. Fix the structure on all sets until they agree within 5 points on sets of about 80 (DEC-1074 (4)).
   Confirm on the measurement set once.
6. Then choose the models (reranker, embedder) on all three sets, with speed and GPU figures.
7. Record every method and figure here, or in the repository's copy of this record.
