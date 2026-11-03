# EXP-003 pass 1 (W2-15a, DAEO-rd0g): the baseline on this repository, five modes

- **Ticket:** DAEO-rd0g (W2-15a), class research, judged by this record. **Under:** DEC-1055 (D-4b, the memory stage),
  decision 5: this repository's part runs in D-4b; `~/workspace` and EXAMIN's corpora wait for W2-88.
- **Role:** research, in the CTO's session (2026-11-03, 21:20-22:45 UTC). Every heavy run went through
  `heavy_slot.sh`, each one after any running D-4b rebuild had ended. No private embedder or reranker was started:
  before and after, the only servers were the shared Ollama servers (pids 6627 and 7034, with their runners) and the
  shared reranker service (pid 356621).
- **The hidden half** was read only by `measure.py`. This record and its raw files show the hidden half's ids, ranks,
  counts, pass/fail and digests, and nothing else.

## 1. Question

How does W2-61's measure score the m1 baseline in each retrieval mode? What do indexing and incremental updates cost?
Does stacking in batches hold? Which of the 20 misses can W2-32's three bounded gaps reach?

## 2. The metric (fixed before the first run: DEC-954 Q9, DEC-957)

This is W2-61's measure (`src/gov/retrieval/measure.py` at the clone), unchanged, on the 48 questions: 24 visible
(copied from the clone into `~/gov-os-eval`) and 24 hidden (`~/gov-os-eval`, outside every tree, with the gold
re-pinned at the clone's head by D-4b's `measure.sh`).

- **hit@5:** a gold source matched by one of the first five items of the stacked context. The floor is 85 % (CAP-10),
  the owner's target 95 %. Memory counts as proven at 21 of 24 or more on the hidden half.
- **Full evidence:** every gold entry matched somewhere in the stacked context, against the owner's target of 99 %.
- **Budgets:** batch size 10, bundle budget 6,000 tokens, stack budget 24,000 tokens.
- **Labels:** the gold was labelled by the question authors (W2-61, Lens B) before any system answer was seen. No
  label is changed here. Q09 below is reported, not re-labelled.

## 3. Corpus and versions

- **Clone:** `~/gov-os-runs/D4B/m1/repo` at `156a5feb677b` (`156a5feb677ba5087bece72723e749860e1bf3bc`), gov 0.1.0,
  Python 3.12.3, SQLite 3.45.1.
- **Store:** digest `28bdbab1ed30fdfc…`. It is unchanged by this work: the incremental rebuild in §5 gave the same
  digest.
- **Index:** 3,138 files, 66,151 chunks, 63,947 vectors.
- **Embedder:** `qwen3-embedding:0.6b` through Ollama 0.35.0, on both shared servers (11434 builds the index, 11435
  embeds the questions). A chunk is embedded as its first 512 characters (`EMBED_CHARS`).
- **Reranker:** `Qwen/Qwen3-Reranker-0.6B` at `e61197ed45024b0ed8a2d74b80b4d909f1255473`, through the shared service
  on cuda:0. It reads `[path]` plus the chunk's first 500 characters (`RERANK_CHARS`).
- **Chunker:** `gov-chunker/1`: at most 1,200 characters per chunk, 120 characters of overlap.
- **Fusion:** RRF with k = 60 over the lexical, semantic, closure and code routes. Lexical and semantic each return
  up to 30 chunks (`TOP_K`).

## 4. The five modes (W2-L329, DEC-074 Q3)

### 4.1 Method

The harness in `w2-15a/` is 90 lines: `modes.py`, `run_modes.sh` and `table.py`. It leaves `src/` unchanged.

- **`modes.py <mode>`** runs the clone's own `gov.cli.main` with two names in `gov.retrieval.retrieve` replaced:
  - `rrf`, which is given only the routes the mode keeps;
  - `rerank`, which is either the identity, or the shipped rerank with the service start and the private fallback
    disabled. One line is logged per rerank, naming who scored it.
- **Every route is still computed;** the mode only chooses what the fusion sees. Everything after the fusion
  (authority order, paging, the drops, parent expansion) is the shipped code in every mode.
- **`run_modes.sh`** writes one wrapper per mode (`~/gov-os-runs/W2-15a/gov-<mode>`) and runs the measure through
  that wrapper as `--gov`.

| mode | routes fused | rerank |
|---|---|---|
| lexical | lexical (ranked: exact boost, then BM25) | none |
| semantic | semantic | none |
| fused | lexical, semantic, closure, code | none |
| fused+rerank | lexical, semantic, closure, code | the shared service (the shipped path) |
| lighter reranker | not run | **not installed:** the HF cache holds only Qwen3-Reranker-0.6B. A MiniLM ONNX model under `~/ASMO-OS-V1-recovery-2026-09-12/.memory-cache` is an embedder, not a cross-encoder. No install was made, and a private reranker is excluded (D-4b) |

**Commands** (from `docs/research/EXP-003/w2-15a/`):

```
bash run_modes.sh lexical semantic fused rerank
# each mode runs, after `flock /tmp/gov-os-d4b-rebuild.lock true`:
env -u GOV_TICKET GOV_ROLE=orchestrator PYTHONPATH=$CLONE/src bash .../tools/heavy_slot.sh \
  python3 -m gov.retrieval.measure memory-retrieval --root $CLONE --sets-root ~/gov-os-eval --part all \
  --out raw/records-<mode> --gov ~/gov-os-runs/W2-15a/gov-<mode>
python3 table.py lexical=raw/records-lexical/*.json semantic=... fused=... fused+rerank=... > raw/table.md
```

**Raw answers:** the measure's text (`raw/measure-<mode>.txt`) and JSON (`raw/records-<mode>/`), plus the reranker
log (`raw/rerank-rerank.log`).

### 4.2 Results

| mode | hit@5 visible | hit@5 hidden | hit@5 all | full evidence visible | full evidence hidden | full evidence all | time |
|---|---|---|---|---|---|---|---|
| lexical | 12/24 | 13/24 | **25/48 (52.1 %)** | 12/24 | 15/24 | 27/48 (56.2 %) | 650 s |
| semantic | 10/24 | 11/24 | **21/48 (43.8 %)** | 10/24 | 10/24 | 20/48 (41.7 %) | 583 s |
| fused | 13/24 | 12/24 | **25/48 (52.1 %)** | 17/24 | 17/24 | 34/48 (70.8 %) | 1,159 s |
| fused+rerank | 12/24 | 16/24 | **28/48 (58.3 %)** | 17/24 | 17/24 | 34/48 (70.8 %) | 1,171 s |
| union of the four (the best mode per question) | 16/24 | 18/24 | **34/48 (70.8 %)** | | | | |

- **Fused+rerank reproduces m1 exactly.** Every question's ranks, figures, call count (169) and stacked digest equal
  m1's run 1 (`measure-memory-retrieval-all-20261103T204508001842Z.json`), so the wrapper is neutral. The log holds
  168 rerank lines, all scored by `service` (one line fewer than calls, with no effect on any digest).
- **The times include machine load:** W2-32's workers ran pytest beside the measure, and every mode computes every
  route.

**What each stage adds:**

- **Fusion:** +0 on hit@5 over lexical alone (25), but +7 on full evidence (27 to 34).
- **The rerank:** +3 net on hit@5, all on the hidden half. It gains five (Q17, h03, h17, h20, h23) and loses two
  (Q06, Q07, both fused rank 2, reranked to 9 and 7).
- **Losses in the fusion:** single-route top-5 hits are lost in four questions:
  - Q11 (semantic rank 5, fused 10);
  - Q18 (lexical 2, fused 9);
  - h04 (lexical 3 and semantic 1, fused 12);
  - h22 (semantic 1, fused 72).

**Per question:** the full table is `w2-15a/raw/table.md`. The 20 misses of fused+rerank, by first gold rank:

| id | lexical | semantic | fused | fused+rerank |
|---|---|---|---|---|
| Q06 | 29 | - | **2** | 9 |
| Q07 | 27 | **2** | **2** | 7 |
| Q08 | 14 | 8 | 7 | 7 |
| Q09 | - | - | 76 | 65 |
| Q10 | - | - | 6 | 7 |
| Q11 | - | **5** | 10 | 11 |
| Q14 | - | - | 12 | 19 |
| Q16 | - | - | - | - |
| Q18 | **2** | - | 9 | 9 |
| Q19 | - | - | - | - |
| q23 | - | - | - | - |
| q24 | - | 18 | 27 | 21 |
| h02 | - | - | - | - |
| h04 | **3** | **1** | 12 | 13 |
| h07 | 9 | - | 39 | 21 |
| h08 | 10 | - | 9 | 9 |
| h11 | - | - | - | - |
| h16 | - | 8 | 19 | 11 |
| h22 | 29 | **1** | 72 | 59 |
| h24 | - | - | - | - |

## 5. Indexing time, peak RSS and incremental update (W2-L102, W2-L321)

| run | total | semantic | lexical | codeintel | peak RSS | digest |
|---|---|---|---|---|---|---|
| cold, m1 rebuild 1 (CTO, `measure.sh`) | 735.5 s | 702.9 s | 7.4 s | 18.0 s | not measured | `28bdbab1…` |
| no change, m1 rebuild 2 (CTO) | 24.1 s | 0.7 s | 0.4 s | 17.0 s | not measured | `28bdbab1…` |
| no change, this run, on the m1 clone | 25.8 s (26.8 s wall) | 0.8 s | 0.7 s | 17.8 s | **115,412 kB** | `28bdbab1…` (unchanged) |
| one file changed (+1 paragraph), on a copy of the clone | 28.3 s (29.3 s wall) | 1.4 s | 0.8 s | 19.2 s | **113,876 kB** | `4e6089ef…` |

**Commands:**

```
flock /tmp/gov-os-d4b-rebuild.lock env -u GOV_TICKET PYTHONPATH=$CLONE/src /usr/bin/time -v -o raw/rebuild-incremental-time.txt \
  bash .../tools/rebuild_slot.sh $CLONE --seed > raw/rebuild-incremental.out
```

The one-file run used the same command on a copy in `/tmp/gov-os-emg-w215a/inc`, with one paragraph appended to
`docs/research/W2-61-baseline.md` and committed in the copy. The copy was removed afterwards. Its index had 66,152
chunks and 63,948 vectors: the new chunk 152-154 was embedded.

**Reading:**

- **An incremental update is cheap:** about 1.5 s of embedding for one changed file. The floor of every rebuild is
  the codeintel stage (about 18 s), which re-runs whole.
- **The vector cache** (`~/.cache/gov-os/vector-cache`) makes the second and later rebuilds warm.
- **Against DEC-078's envelope** (about 2.2 GB peak at 80k nodes and 270k edges, for codeintel): 115 MB is well
  inside it. But `time -v` reports the largest process the rebuild waited for, and the Ollama server that embeds,
  and any codeintel daemon, are not its children. This is the rebuild's own RSS, not the machine's.
- **The cold rebuild's peak RSS is not measured:** a cold run needs the vector cache bypassed (about 12 min of the
  shared embedder). See §8.

## 6. The stacking test (AR-10), once

**Question:** q14 ("Which tickets depend on W2-03?", `--ticket DAEO-ym8a --radius 1`). It needs nine pieces across
nine tickets, the widest gold in the set.

**Method:** retrieved with a bundle budget of 8,000 and its continuations. The items are stacked whole into batches
of at most 8,000 tokens, up to 24,000. The system was fused+rerank (`gov-rerank`).

**Command:**

```
heavy_slot.sh python3 stack.py ~/gov-os-runs/W2-15a/gov-rerank $CLONE $CLONE/fixtures/.../visible/q14.yaml 8000 24000
```

The output is `raw/stack-q14.json`; `raw/stack-q14-duplicates.txt` comes from `diag/dups.py`.

| check | result |
|---|---|
| calls | 4. Each returned 20 items (7,892, 6,196, 7,925 and 7,465 tokens); every rerank by the service |
| batches | 3: 20 items / 7,892 tokens, 25 / 7,908, 16 / 7,513. Stacked: 61 items, 23,313 of 24,000 tokens |
| assembled complete | **yes:** every item's sha256 equals its span's bytes in the clone, and no item is cut |
| no duplicates by span hash | **fails: 3 duplicate hashes** in the 61 items, and 25 overlapping spans |
| gold held | **1 of 9** |

**Why the duplicates fail:**

1. **The same span is sent again across a continuation.** `docs/changes/W2-49-CIT-P.md` 209-225 comes in call 2 and
   again in call 3. The parent expansion's `expanded` set is local to one call, so a child in a later batch expands to
   a parent already sent. The measure dedups by (path, lines), so the figures are unaffected, but tokens are wasted.
2. **Identical bytes in different close records.** For example, `CL-DAEO-e82f.md` 2824-2838 and `CL-DAEO-zflj.md`
   2823-2837. These are close records, which DEC-1052 keeps out of the embedded set; D-7's scope removes them from
   the semantic route.

The overlaps are children and their parents from different batches. Holding 1 of 9 is Q14's own miss: no route
returns the tickets that depend on a record (see §7).

## 7. The gaps: the 20 misses classified

**Evidence used:**

- the per-mode ranks (§4);
- for the visible half only:
  - each gold span's chunks and the gold's character offset inside them (`raw/goldpos-visible-misses.txt`);
  - whether those chunks are embedded (`raw/embedded-visible-misses.txt`: all are);
  - the shipped system's first 12 items (`raw/topk-visible-misses.txt`).

For the hidden half, only the ranks per mode.

| class | misses | what the evidence shows |
|---|---|---|
| **ranking: lost in the fusion** (a single route has it in the top 5, the fused list does not) | Q11, Q18, h04, h22 (4) | RRF (k = 60) over four routes. The closure route is unranked: every chunk of every reached record. So a chunk in any two routes outscores any one route's first hit (2/(60+r) > 1/61 for r up to about 60). h22: semantic 1, fused 72 |
| **ranking: lost in the rerank** (fused top 5, reranked out) | Q06, Q07 (2) | Q07's gold starts at character 534 of its ticket chunk, past the reranker's 500. Q06's starts at 406-413 |
| **ranking: near** (best rank 6-10 in any mode) | Q08, Q10, h07, h08, h16 (5) | Visible: the top 5 holds decision entries, tests that quote the identifier, and `docs/assessment/2026-10/B-memory-retrieval.md`, the Lens B assessment that quotes the questions (it sits in the top 5 of 7 of the 12 visible misses) |
| **chunking: the gold past the 500/512-character view** in every chunk that holds it | Q10 (909, 638), Q16 (529), q24 (entry 2: 638, 980), and in part Q07 (534), Q11 (559, 800) | The chunks are up to 1,200 characters, but the embedder sees 512 and the reranker 500. Q16's gold line was never retrieved by any mode |
| **ranking: never retrieved, indexed and embedded** | Q19, q23 (2) | q23: `select.py` 1-20 is rank 6, while the gold line 27 is in chunk 14-38, which is not retrieved. Q19: decision entries and orchestration packages on the same words (semantic route) hold the whole top 12, above the charter and the role files |
| **labelling** | Q09 (1) | The Contract's CAP-15 (`CONTRACT_v4.md` 256-273, rank 1, and `CAP-15.md`, rank 3) states the ceiling ("default ~6k tokens"). The gold names only DAEO-u4oz's KPI line. Reported, not re-labelled (the labels stay blind to the answers) |
| **coverage: no route answers** | Q14 (1) | "Which tickets depend on W2-03?" needs the reverse `depends_on` edges. The closure from DAEO-ym8a goes forward |
| **not classifiable from ids** (never retrieved by any mode) | h02, h11, h24 (3) | Coverage, labelling or the 500-character view. h24 ends after 1 call. Telling them apart needs an id-only check of the hidden gold's chunk offsets (§8) |

## 8. The gaps proposed for W2-32 (at most three, from its list S6-S8; the owner chooses)

**Ceiling first:** the union of the four modes is 34/48 (70.8 %). Even a perfect choice among today's modes stays 7
below the floor (41/48). The estimates below are this record's (est.), not measured.

**G1. Chunking: span size, overlap and parent expansion, with a re-embed (S7).**

- **The change:** make the span each route judges the span it returns. Cut spans to about 500 characters, so the
  embedder's 512 and the reranker's 500 see the whole span. Keep overlap. Expand the parent within the bundle budget
  so the context returned is unchanged.
- **Also fixes:** the parent expansion's duplicates across continuations (§6): carry the expanded parents in the
  continuation, or dedup by span hash.
- **Targets:** Q10, Q16, q24 (the gold past the view in every chunk), Q07 and Q11 (in part), and any hidden miss whose
  gold sits past character 500.
- **Could reach:** +2 to +4, to about 30-32/48 (62-67 %).
- **Cost:** about 2.4 times the chunks and vectors (66k to about 150k). That works against D-7's 77 % fewer vectors,
  and a cold re-embed takes about 30 min.
- **A cheaper variant for W2-32 to probe first:** embed and rerank the whole span (raise `EMBED_CHARS` and
  `RERANK_CHARS` to the chunk's 1,200 characters). The vector count stays the same, but a re-embed is still needed.
  It needs the owner's reading of "span size".

**G2. Ranked-lexical tuning: field weights, tokenizer and the exact-identifier boost (S6).**

- **The change:**
  - give a path field or weight that ranks code above tests and assessments for code questions;
  - for a `--id` (caller) question, an exact boost that prefers the call site over a chunk that only mentions the
    identifier;
  - split `test-map.yaml`-like tokens.
- **Targets:** Q10 and Q11 (callers: lexical never finds them; the boosted chunks are tests and the Lens B
  assessment), q23 (the constant's line), h07 and h08 (lexical rank 9-10), and Q18 and h04 (lexical rank 2-3,
  provided G3 keeps them through the fusion).
- **Could reach:** +2 to +3 on its own, to about 30-31/48.

**G3. The hit@5 85 row (W2-M341): the semantic route's hits kept through the fusion and the rerank (S8).**

- **The change:** rank the closure route, or give it a lower RRF weight, instead of fusing an unranked set of every
  reached chunk. Keep each route's first hits in the fused head, for example by guaranteeing each route's rank 1-2 a
  place in the first batch. Let the rerank read the whole span (shared with G1).
- **Targets:** h22 (semantic 1), h04 (semantic 1, lexical 3), Q07 (semantic 2), Q11 (semantic 5), h16 (semantic 8),
  Q18 (lexical 2), Q06 (fused 2, reranked 9).
- **Could reach:** +3 to +5, to about 31-33/48. Its upper bound is the union's 34.
- **Which rows it falls under:** W2-M341 names the semantic route's hit@5. The fusion's weights fall under it only if
  the owner reads the row that way. The fusion itself is no row of S6-S8.

**All three together (est.):** about 33-36/48 (69-75 %), and below 21/24 on the hidden half (16 today, 18 for the
union). **The floor of 85 is not expected after W2-32's rounds**, so S9 (the owner decides) is the likely end.

**What none of the three reaches:**

- Q09 (a label);
- Q14 (a reverse-dependency route);
- Q19 (the register's noise);
- h02, h11 and h24 (unknown);
- the Lens B assessment's place in the top 5. It is not one of the set's parts, and whether it counts as quoting the
  set is W2-61's question.

## 9. Verdict and residuals

**Verdict:**

- The baseline stands at 28/48 hit@5, 34/48 full evidence, with a noise band of 0.
- The rerank adds +3 on hit@5 over the fusion.
- The fusion adds full evidence (+7) but no hit@5 over lexical alone.
- The ceiling of today's modes is 34/48.
- Three gaps are proposed from W2-32's list, with estimates. None reaches 41 alone, nor all three together (est.).

**Residuals:**

- The lighter reranker was not run (not installed).
- The cold rebuild's peak RSS was not measured.
- The hidden misses h02, h11 and h24 are unclassified. An id-only report from the CTO would place them: for each
  hidden miss, "gold chunk exists / embedded / gold offset > 500", as `goldpos.py` gives for the visible half.
- Not done, and outside this brief: the dev tiers, `~/workspace` and EXAMIN (W2-88); decision-level retrieval after
  W2-03; the thin-margin cases and the two dev queries without gold paths (W2-M342, W2-L322, W2-M340).
- The reranker log is one line short of the call count (168 of 169), with no effect on any figure.

## 10. Files

All under `docs/research/EXP-003/w2-15a/`:

- **The harness:** `modes.py`, `run_modes.sh`, `table.py`.
- **Tests and probes:** `stack.py` (the stacking test), `goldpos.py` (the visible gold's offsets in its chunks).
- **Diagnostics:** `diag/topk.py`, `diag/dups.py`, `diag/embedded.py` (visible half only).
- **`raw/`:**
  - each mode's measure text and JSON records;
  - `table.md`;
  - the rerank log;
  - `stack-q14.json` and `stack-q14-duplicates.txt`;
  - the rebuilds' outputs and `time -v` reports;
  - the visible diagnostics.
