# D-4b memory survey: rerankers that fit, other memory systems, and what each component is for

- **By:** the research role (one session, Claude Opus 5.5), for the Wave 2 CTO, under the brief
  `.gov-runtime/scratch/orchestrator/briefs/D4B-research-memory-survey.md`. Written to disk by the CTO from the
  session's return (the session's Write tool refused report files from a subagent).
- **Date:** 2026-11-05. All web sources were read on 2026-11-05 unless marked "(night one)": those were read by the
  earlier survey on 2026-11-03 and are quoted from its report, not re-read.
- **Method:** read-only. I read the memory record (`docs/research/W2-88-memory-practice.md`), the structural review,
  the misses, the reranker trial, the link census, night one's survey and the retrieval code (`src/gov/retrieval/`,
  `src/gov/store/loader.py`, `governance/project/{retrieval,rebuild}.yaml`, `path-map.yaml`). I read the cached
  reranker snapshots' configuration files and the reranker venv's `sentence-transformers` 6.1 source. I ran one
  tokenizer-only script on the CPU (`HF_HUB_OFFLINE=1`, `CUDA_VISIBLE_DEVICES=-1`, no model weights loaded) to render
  each reranker's input template (section 1.3). No GPU, no install, no download, no `gov retrieve`, nothing under
  `~/gov-os-eval/` or `~/gov-os-runs/`.
- **How each claim is marked:**
  - **[M]** measured by the source, with what it was measured on;
  - **[C]** claimed by the source with no figure, or a vendor's figure nobody else has reproduced;
  - **[E]** my estimate, with how it is reasoned;
  - **[R]** read here, in our code or files.

## 0. The answer in short
1. **The mxbai trial almost certainly saw its template.** Its snapshot carries `chat_template.jinja` and a
   `LogitScore` module ("1" against "0"). `sentence-transformers` 6.1 turns every (query, text) pair into
   `query`/`document` messages and renders them through that template, the same path that gives the 0.6B its
   template. I rendered both templates from the cached snapshots. mxbai's matches the vendor's own `mxbai-rerank`
   library word for word. So a re-run "with its template" would most likely change nothing. The cause of its −31 lies
   elsewhere. One candidate is our design: the authority lift adds 1.0 per tier step to the raw reranker score, a step
   sized for the 0.6B's score scale (section 3.4). **[R]**
2. **The 4B's gain is cheap to test again, at no GPU cost.** Every reranker here scores each pair on its own
   (pointwise), so a score does not depend on the other texts in its request. The trial kept each run's rerank scores.
   So these can be replayed exactly from the kept scores, with no GPU:
   - a cascade, the 0.6B over 40 and then the 4B over the 0.6B's top 8 to 16;
   - the 4B over a shallower fused head;
   - the lift rescaled per model.

   The misses sit at places 6 to 12, so a cascade could keep most of the 4B's +5 at about a third of its cost. **[E]**
3. **Few systems merge four routes and a graph as we do.**
   - The hybrid search engines fuse keyword and vector by RRF or a normalised sum, then rerank a global head of 50 to
     150 with one cross-encoder: Azure AI Search, Elasticsearch, OpenSearch, Vespa, Qdrant and Weaviate.
   - The agent memories use the graph to *expand from seeds* or to *rerank by graph distance*, not as a ranked list
     fused beside the others: Zep, HippoRAG and Continue's code-graph expansion.
   - Code assistants have moved towards agentic search, where the agent issues grep and semantic queries itself:
     Claude Code, Cursor and Sourcegraph.
   - Our closure route enters the RRF as a list in path order (section 3.4). That is an arbitrary rank signal, though
     night one measured it neutral. **[R]**
4. **Rerankers help most on concept and fact questions, and can hurt on code, on large candidate pools and out of
   domain.**
   - The 0.6B is itself measured to *lower* Qwen's code retrieval: MTEB-Code 73.42, against 75.41 for its own first
     stage. The 4B raises it to 81.20. **[M]**
   - Pointwise cross-encoders get worse as more documents are reranked, with "phantom hits". Only the listwise LLM
     rerankers stayed robust. **[M]**
5. **Our post-rerank steps can pre-empt the top 5.**
   - The authority lift is applied again after the rerank.
   - Up to 2 named-record chunks and 2 code chunks are moved ahead.
   - Failure and lesson records are moved ahead.

   Before blaming the reranker for the 10 ranked-low misses, the kept outputs can show in which step each gold piece
   left the top 5. **[R]**

## 1. Rerankers that fit this machine

### 1.1 The budget and how speed is estimated
- **Memory:** the dispatcher's budget is 14,255 MiB and the trial's base about 6,250 MiB (two embedders and the
  desktop). That leaves **about 8,000 MiB** for a reranker's weights *and* its working memory. Measured in the trial
  (D4B-TRIAL-W4), above the base: **[M, on our machine]**

  | Reranker | After load | Peak in the runs | Probe's worst shape |
  |---|---:|---:|---:|
  | 0.6B | +1,405 | +3,597 | – |
  | mxbai-large-v2 | +3,340 | +4,912 | – |
  | 4B in 8-bit | +4,595 | +8,802 (over the budget 10 times) | +4,761 alone; +7,056 at 20 at once |

- **Speed:** the trial gives three anchors. Under load the service is GPU-bound and serial, so the median at N at once
  is about N times the GPU time one search takes (G). **[M, on our machine, 138 questions]**

  | Reranker | Alone | 10 at once | 20 at once | G |
  |---|---:|---:|---:|---:|
  | 0.6B | 1.80 s | 6.6 s | 13.0 s | about 0.65 s |
  | mxbai-large-v2 | 2.09 s | 9.6 s | 17.5 s | about 0.9 s |
  | 4B in 8-bit | 3.89 s | 29.6 s | 54.1 s | about 2.7 s |

  "Alone" fits about 1.80 s + (G − 0.65 s) for all three. The estimates below use **G ≈ 0.3 s + 0.37 s per billion
  parameters** for a bf16 decoder model through `sentence-transformers` (fitted to the 0.6B and mxbai), times about
  1.5 for bitsandbytes 8-bit (fitted to the 4B). An encoder cross-encoder (BERT/ModernBERT) has no chat template to
  render and runs faster per parameter: there I scale from the Ettin blog's RTX 3090 throughput (section 1.2). All
  such figures are **[E], ±50 %**.

### 1.2 The candidates
Scores are nDCG@10 unless marked. "MTEB-R" and "MTEB-Code" are Qwen's reranking evaluation: the top 100 from
Qwen3-Embedding-0.6B reranked. "BEIR/CoIR (Jina)" is the jina-reranker-v3 card's table. "MTEB-eng (HF)" is the Ettin
blog's: MTEB(eng, v2) retrieval, 10 tasks, the top 100 of six first-stage embedders reranked, averaged, inputs capped
at 8,192 tokens.

| Model | Kind | Licence | Params | GPU, bf16 (8-bit / 4-bit) | Published scores (source) | G per search, alone, 10 / 20 at once [E] | Fits? |
|---|---|---|---:|---|---|---|---|
| **Qwen3-Reranker-0.6B (today)** | LLM pointwise (yes/no logit) | Apache-2.0 | 0.6B | measured +1.4 GB load, +3.6 GB peak | MTEB-R 65.80, MTEB-Code 73.42 (embedder alone 75.41) [M, Qwen]; BEIR 56.28, CoIR 65.18 [M, Jina]; MTEB-eng 0.594 [M, HF] | measured: 0.65 s, 1.80 s, 6.6 / 13.0 s | yes |
| **Qwen3-Reranker-4B** | LLM pointwise | Apache-2.0 | 4.0B | bf16 ≈ 8 GB weights: **no**; 8-bit measured +4.6 GB load, +8.8 GB peak; 4-bit ≈ 2.6 GB weights [E] | MTEB-R 69.76, MTEB-Code 81.20 [M, Qwen]; BEIR 61.16, CoIR 73.91 [M, Jina]; MTEB-eng 0.637 [M, HF]; **here 112/138 against 107** [M] | 8-bit measured: 2.7 s, 3.89 s, 29.6 / 54.1 s. FP8 or AWQ kernels est. G 1.6-2.0 s, alone 2.8-3.2 s | only in 8/4-bit; over the budget at peak |
| Qwen3-Reranker-8B | LLM pointwise | Apache-2.0 | 8B | 4-bit ≈ 5 GB weights [E] | MTEB-R 69.02, MTEB-Code 81.22 [M, Qwen] | G ≈ 4-6 s, alone ≈ 5-7 s | no: time; no gain over the 4B |
| **mxbai-rerank-large-v2** | LLM pointwise ("1"/"0" logit) | Apache-2.0 | 1.5B | measured +3.3 GB load, +4.9 GB peak | BEIR 57.49, "Code Search" 32.05 [M, vendor]; BEIR 61.44, CoIR 70.87 [M, Jina]; MTEB-eng 0.612 [M, HF]; **here 76/138** [M] | measured: 0.9 s, 2.09 s, 9.6 / 17.5 s | yes |
| mxbai-rerank-base-v2 | LLM pointwise | Apache-2.0 | 0.5B | ≈ 1.0 GB + work | BEIR 58.40, CoIR 65.71 [M, Jina]; MTEB-eng 0.592 [M, HF] | ≈ 0.5 s, 1.7 s, 5 / 10 s | yes; same family as large-v2 |
| zerank-1-small | LLM pointwise (Qwen3-4B-based) | Apache-2.0 | 1.7B | ≈ 3.4 GB + work | Code 0.730 against embedding baseline 0.678 [vendor M: their sets, top 100 of OpenAI text-embedding-3-small] | ≈ 0.95 s, 2.1 s, 10 / 19 s | yes; vendor figures only |
| zerank-2 | LLM pointwise | Apache-2.0 (card) | 4B | as the Qwen3-4B | Code 0.653 [vendor M]; but MTEB-eng 0.530, below the 0.6B [M, HF] | as the 4B | as the 4B; the figures conflict |
| ctxl-rerank-v2-instruct-multilingual (1B / 2B / 6B) | LLM pointwise, instructable (recency, source) | **CC BY-NC-SA 4.0** | 1-6B | 1B ≈ 2 GB; 2B (3B in safetensors) ≈ 6 GB; NVFP4 variants (vLLM only) | "matches the largest Qwen3-Reranker" on BEIR and MMTEB; wins on recency instructions [C, vendor; no figures in the text] | 1B ≈ 0.7 s, 1.9 s | licence: non-commercial |
| jina-reranker-v3 | **listwise**, up to 64 documents per pass | **CC BY-NC 4.0** | 0.6B | ≈ 1.2 GB + work | BEIR 61.94, CoIR 70.64 [M, Jina] | one pass for 40 texts: ≈ 0.5-0.9 s | licence: non-commercial; remote code |
| jina-reranker-v2-base-multilingual | cross-encoder | CC BY-NC 4.0 | 0.3B | < 1 GB | BEIR 57.06, CoIR 56.14 [M, Jina] | ≈ 0.3 s | licence; weaker |
| bge-reranker-v2-m3 | cross-encoder (XLM-R) | Apache-2.0 | 0.57B | ≈ 1.1 GB | MTEB-R 57.03, MTEB-Code 41.38 [M, Qwen]; CoIR 36.28 [M, Jina] | ≈ 0.4 s | yes; weak on code |
| bge-reranker-v2-gemma | LLM pointwise | Gemma | 2.5B | ≈ 5 GB + work | BEIR 60.71 [M, BAAI card] | ≈ 1.2 s, 2.4 s | tight; licence to check |
| bge-reranker-v2.5-gemma2-lightweight | LLM, layer cut and token compression | Gemma | 9B | 4-bit ≈ 5 GB | BEIR 63.10 at 60 % FLOPs saved [M, BAAI] | ≥ 3 s | no |
| **gte-reranker-modernbert-base** | cross-encoder (ModernBERT) | Apache-2.0 | 149M | < 0.5 GB | BEIR 56.19 or 56.73 (the card gives both), **CoIR 79.99**, LoCo 90.68 [M, Alibaba]; MTEB-eng 0.584 [M, HF] | ≈ 0.15-0.3 s; alone ≈ 1.4 s | yes; tiny; code-strong |
| Ettin-reranker 17M to 1B (May 2026) | cross-encoder (ModernBERT), distilled from mxbai-large-v2 | Apache-2.0 | 17M-1B | ≤ 2 GB | 1B: MTEB-eng 0.611, NanoBEIR 0.724; 400M: 0.609 / 0.719; 150M: 0.599 / 0.709 [M, HF]; no code figures | RTX 3090, 512 tokens: 1B 189 pairs/s, 400M 429, 150M 982 (mxbai-large-v2 69) [M, HF]. Here: 1B ≈ 0.3-0.5 s | yes; but its teacher lost here |
| ms-marco-MiniLM-L6/L12-v2 | cross-encoder | Apache-2.0 | 23-33M | tiny | MTEB-eng 0.508 / 0.507 [M, HF] | ≈ 0.1 s | yes; too weak |
| GTE-ModernColBERT-v1 | late interaction | Apache-2.0 | 149M | tiny; a token-vector index if precomputed | BEIR 54.67; LongEmbed 88.39 [M, LightOn] | ≈ 0.1-0.2 s (no index needed via PyLate `rank.rerank`) | yes; below cross-encoders |
| answerai-colbert-small-v1 / jina-colbert-v2 | late interaction | Apache / CC BY-NC | 33M / 560M | tiny | BEIR 53.79 / (jina) – [M, LightOn's table] | fast | weaker |
| RankZephyr-7B, FIRST, other 7B listwise | LLM listwise | various | 7B | 4-bit ≈ 4.5 GB | DL19 0.742 from BM25 0.506 [M, paper; night one] | windows of 20, stride 10, over 40: 3 passes; alone ≈ 8-15 s | no: time |

**Readings:**
- **The 4B is the only measured gain here**: +5 on the 138, MRR +0.036, the spread narrowed. Every public table agrees
  it is clearly stronger than the 0.6B, most on code (+7.8 MTEB-Code, +8.7 CoIR). **[M]**
- **mxbai-large-v2 is stronger than the 0.6B in every public table**, yet lost 31 here. It was fed correctly (1.3).
  So the cause is either the corpus (governance records full of ids, prefixed with `[path: …]`) or our pipeline after
  the rerank (3.4). **[R]**
- **The small encoders** (gte-reranker-modernbert-base, Ettin 150M to 1B) are fast enough to run 20 at once without
  pain. They lack public figures on prose-plus-id corpora like ours. The Ettins are distilled from the very model that
  lost here, so I would not expect them to beat the 0.6B. gte-modernbert's CoIR 79.99 makes it a possible code-only
  reranker. **[E]**
- **The licences rule out** jina-reranker-v3, jina-reranker-v2 and Contextual AI's v2 (non-commercial), unless the
  owner accepts that.

### 1.3 Input templates, and why the mxbai caution is probably wrong
- **What the code sends:**
  - `retrieve.py` builds each candidate's text as `[path: <path>]\n<chunk body>[:24000]` (`RERANK_CHARS`).
  - `rerank_worker.scores` sends `encoder.predict([(query, text) …])`.
  - `load` builds `CrossEncoder(model, revision=…)`.
  - No template, instruction or prompt is passed. **[R]**
- **What `sentence-transformers` 6.1 does with a pair** (the reranker venv's own source,
  `base/modules/transformer.py` lines 1361-1375 and `base/modality.py` `batch_to_message`):
  - A model whose `sentence_bert_config.json` lists a `message` modality always converts text input to messages. A
    text pair becomes `[{"role": "query", …}, {"role": "document", …}]`.
  - The messages are rendered with the snapshot's `chat_template.jinja`.
  - `LogitScore` reads the last position under left padding, which the module enforces, and scores
    `logit(true) − logit(false)`. **[R]**
- **Both snapshots are built this way** (their files, read here; ST 5.4.0 configs):

  | | Qwen3-Reranker-0.6B and 4B | mxbai-rerank-large-v2 |
  |---|---|---|
  | `sentence_bert_config` | `text-generation`, `message` modality | the same |
  | Score tokens | "yes" (9693) / "no" (2152) | "1" (16) / "0" (15) |
  | Default prompt | `query`: "Given a web search query, retrieve relevant passages that answer the query" | none |

- **Rendered here from the cached snapshots** (tokenizer only, CPU):
  - **0.6B:** `<|im_start|>system\nJudge whether the Document meets the requirements … "yes" or "no".<|im_end|>\n<|im_start|>user\n<Instruct>: Given a web search query, …\n<Query>: Q\n<Document>: [path: a/b.md]\nD<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n`.
    This matches the Qwen card's format. **[M, here]**
  - **mxbai:** `<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\nquery: Q\ndocument: [path: a/b.md]\nD\nYou are a search relevance expert … (0 for not relevant, 1 for relevant).\nRelevance:<|im_end|>\n<|im_start|>assistant\n`.
    This is the vendor library's own prompt: the same prefix, `query: `, `document: `, task prompt and suffix, with
    "1"/"0" scored and left padding (`mxbai_rerank_v2.py`, read on GitHub). The vendor's README shows exactly the
    trial's call: `CrossEncoder("mixedbread-ai/mxbai-rerank-large-v2").predict(pairs)`. **[M, here; R]**
- **Two differences from the vendor library remain:**
  - The library cuts the document to fit 8,192 tokens. Our texts are at most about 6,000 tokens, so this does not bite.
  - The library adds an optional `instruction:` line, which is off by default.

  Neither explains −31. **[R]**
- **What would settle it without a GPU run:** replay mxbai's kept scores (if the trial kept them, as it did for the
  first calls):
  - without the authority lift;
  - without the post-rerank moves;
  - with the lift rescaled to its score spread.

  If mxbai is still far behind, the model is the cause. **[E]**
- **Instructions:** Qwen says that leaving out a task instruction "can lead to a drop … by approximately 1 % to 5 %"
  and recommends task-specific instructions in English. **[C, Qwen card]** Ours is the generic web one. Night one
  measured "a reranker instruction" as a loser, on the older structure (W2-88 §4). A task instruction is a GPU run
  per model (scores change), so it is low on the list.
- **Other templates, for any later trial:**
  - Contextual AI: `Check whether a given document contains information helpful to answer the query.\n<Document> {doc}\n<Query> {query} {instruction} ??`, scored on the logit of token 0.
  - BGE-gemma: `A: {query}` / `B: {passage}` and "Predict whether passage B contains an answer to query A."
  - Encoder cross-encoders: a plain pair, with no template.
  - **The check to make before every trial:** render one pair through the loaded module and compare it with the
    card's format.

### 1.4 What "fits" means once concurrency is counted
- At 20 searches at once, a search waits about 20 × G:

  | Reranker | 20 at once |
  |---|---:|
  | the 0.6B | 13 s (measured) |
  | a 1.5B | ≈ 18 s (measured for mxbai) |
  | the 4B in 8-bit | ≈ 54 s (measured) |
  | the 4B in FP8 or AWQ | ≈ 32-40 s [E] |

- So **the 4B over all 40 does not fit the concurrency limit in any quantisation**. The 4B over the 0.6B's top 12
  costs about 0.3 × 2.7 ≈ 0.8 s of G in 8-bit. Beside the 0.6B's 0.65 s, that gives G ≈ 1.45 s:

  | Cascade, 0.6B over 40 then the 4B over the top 12 | 8-bit [E] |
  |---|---:|
  | alone | ≈ 2.6 s |
  | 10 at once | ≈ 15 s |
  | 20 at once | ≈ 29 s |

- **Memory for the cascade, one request at a time** (both models in one service):
  - the 0.6B's weights, 1.4 GB, and the 4B's in 8-bit, 4.6 GB: 6.0 GB;
  - the larger working memory of the two, not their sum;
  - with the 4B's requests bounded at 8 texts or 12,000 padded characters, about 1.1-1.5 GB [E].

  That is about 7.1-7.5 GB, inside the 8 GB. At today's bound of 16 texts and 24,000 characters the 4B's worst probe
  shape needs about 2.2 GB more, which overruns the budget. **[E]**

## 2. Other memory systems: how they build, recall, fuse and rerank

### 2.1 Code assistants

| System | Build (chunks, indexes, graph) | Recall and fusion | Rerank | Figures, and what they were measured on |
|---|---|---|---|---|
| **Sourcegraph Cody** (blog, 2024-02-15; paper arXiv 2408.05344) | Dropped embeddings (ada-002 and a vector DB) for Sourcegraph's own search engine. Reasons: code sent to a third party, admin complexity, and vector search over 100k+ repositories being heavy | Keyword search with "an adapted BM25 function plus other tuned signals" over the selected repositories (up to 10), plus local IDE snippets; one global ranking across providers; top N by snippet length | The paper: a **pointwise** ranker trained for relevance, kept by a threshold or token budget; retrieval favours recall, ranking precision | No accuracy figures published [C]. Lessons: the online and offline gap is large; labels are scarce and need experts |
| **Cursor** (blog "Improving agent with semantic search", 2025-11-06) | Its own embedding model, **trained on agent traces**: an LLM ranked what would have helped at each step, and the embedder was trained to agree | Semantic search offered *as a tool beside grep*; the agent uses both | none mentioned | Offline, Cursor Context Bench: **+12.5 % answer accuracy on average (6.5-23.5 % by model)** with semantic search against grep alone [M, vendor]. Online A/B: code retention +0.3 % (+2.6 % on 1,000+ file codebases); 2.2 % more dissatisfied follow-ups without it [M, vendor]. "The combination … leads to the best outcomes" |
| **Claude Code** (Boris Cherny, 2025, via secondary write-ups) | **No index**: early versions used RAG with a local vector DB | Agentic search: the model runs grep and glob and reads files, iterating | – | "Agentic search generally works better … by a lot" [C, unpublished]. Reasons given: accuracy, freshness, security, simplicity |
| **GitHub code search** (Blackbird, 2023-02-06) | Rust; an n-gram inverted index ("sparse grams" over trigrams); 45M repositories, 115 TB deduplicated to 28 TB, index 25 TB | Exact, substring and regex; posting lists kept in score order; the top 100 re-sorted by score | – | p99 per shard ≈ 100 ms; ≈ 640 queries/s per 64-core host [M, vendor]. No semantic search |
| **GitHub Copilot embeddings** (2025-09-24) | A new code embedding model: contrastive (InfoNCE), Matryoshka, hard negatives mined with LLMs | Semantic retrieval for chat, agent, edit and ask | none mentioned | **+37.6 % retrieval quality (0.362 → 0.498)** on an unnamed multi-benchmark of four task kinds; 2× throughput; 8× smaller index [M, vendor] |
| **Aider repo map** (docs; `repomap.py` read) | tree-sitter definitions and references; a file graph; **no embeddings** | **Personalised PageRank**: chat files +100/n, mentioned files and identifiers lifted. Edge weight ×10 for a mentioned identifier, ×10 for a long snake/camel identifier, ×0.1 for private or defined in over 5 files, ×50 from a chat file, with √refs. Binary search to fit `--map-tokens` (1k by default; ×8 with no files in chat) | – | none published |
| **Continue** (`core/context/retrieval/retrieval.ts`, read) | LanceDB embeddings (all-MiniLM-L6-v2 locally by default), SQLite full-text, code-graph expansion (VS Code) | FTS for nRetrieve/2, embeddings for nRetrieve, graph expansion of the snippets found; **concatenated and deduplicated by path and lines (no fusion score)** | With a reranker configured, every candidate is scored, those below a threshold dropped and the rest cut to nFinal | none |

### 2.2 RAG frameworks

| Framework | Chunking defaults | Fusion | Rerank |
|---|---|---|---|
| **LlamaIndex** (docs read) | `chunk_size` 1024, `chunk_overlap` 20; smaller for precision, with a higher `similarity_top_k`; hierarchical and auto-merging retrievers (retrieve small, return the parent) | `QueryFusionRetriever`: reciprocal rank, relative score, distribution-based (night one) | Retrieve wide (10+), then `SentenceTransformerRerank`; the docs name **Qwen3-Reranker-0.6B** as the multilingual local choice, and LLM rerankers (`LLMRerank`, `RankGPTRerank`) for the highest quality [C] |
| **LangChain** (not re-read) | `RecursiveCharacterTextSplitter`; `ParentDocumentRetriever` (small chunks searched, parents returned) | `EnsembleRetriever`: weighted RRF; `MultiQueryRetriever` (LLM rephrasings) | `ContextualCompressionRetriever` with a cross-encoder |
| **Haystack** (night one) | – | `DocumentJoiner`: concatenate, merge, RRF, distribution-based | `TransformersSimilarityRanker` / `SentenceTransformersSimilarityRanker` |

All three use the same pattern: **two stages** (hybrid recall, then one cross-encoder over the head), with the small
chunk returned as its parent. That is what we do. None fuses a graph as a ranked route.

### 2.3 Search engines' hybrid search

| Engine | Recall and fusion | Rerank | Figures, and what they were measured on |
|---|---|---|---|
| **Azure AI Search** (blog 2023-09-18, updated 2024-11-22) | BM25 and vector (ada-002) by RRF | **Semantic ranker** (Bing-derived cross-encoder) over the **top 50**, calibrated 0-4 | NDCG@3 on customer sets: keyword 40.6, vector 43.8, hybrid 48.4, **hybrid + ranker 60.1**; BEIR 40.6 / 45.0 / 48.4 / 50.0 [M, vendor]. By query kind (keyword / vector / hybrid / + ranker): **keyword queries 79.2 / 11.7 / 61.0 / 66.9** (keyword search alone is best, and hybrid loses to it); low term overlap 23.0 / 36.1 / 35.9 / 49.1; fact-seeking 37.8 / 49.0 / 49.1 / 63.4. Chunking (Recall@50): 512 tokens 42.4 against 1024 37.5 and 8191 34.9; 25 % overlap 43.9 against none 42.4 [M] |
| **Elasticsearch** (night one; Elastic Rerank blog read) | `rrf` retriever (k 60), `linear` retriever | `text_similarity_reranker`; Elastic Rerank, a 184M DeBERTa-v3 cross-encoder | BEIR, top 100 of BM25 reranked: 0.426 → 0.565 (bge-reranker-v2-gemma 0.568, Cohere v3 0.529); smallest gain Touché 0.35 → 0.36 [M, vendor] |
| **OpenSearch** (night one) | hybrid query, normalisation min-max / L2 / z-score; RRF | rerank processor (cross-encoder) | z-score +2.08 % over min-max on BEIR [M, vendor] |
| **Vespa** (docs read) | first phase on every hit; second phase on the top 100 per node; **global phase on the top 100** overall (`rerank-count`); `reciprocal_rank_fusion` (k 60) and `normalize_linear` in the global phase | cross-encoders as ONNX in the global phase, on a GPU if set | – |
| **Qdrant** (docs read) | `prefetch` and fusion: RRF (**default k 2**, k settable from 1.16, weights from 1.17), DBSF | **multi-stage**: e.g. byte MRL vectors (1000) → full dense (100) → ColBERT multivector (top 10) | Advice: weighted RRF only with an eval set; plain RRF "the safe default" [C] |
| **Weaviate** (docs read) | hybrid with `alpha`; **relativeScoreFusion the default from 1.24** | rerank modules (Cohere, transformers) | about 6 % recall on FiQA for relative score over ranked (night one) [M, vendor] |

**Readings:**
- Every engine reranks **one global head**: 50 at Azure, 100 at Vespa and Elastic, 150 → 20 at Anthropic. Some chain
  **two or three stages** of increasing cost (Qdrant, Vespa). None re-imposes another order on the reranker's output
  except through an explicit, tuned score expression (Vespa's global phase).
- Azure's own figures show **keyword search alone beating hybrid on keyword-like queries** (79.2 against 61.0). This
  is the case for our id questions, and the reason our lexical route gives exact-id chunks first (`lexical.py`'s
  boost). **[M]**

### 2.4 Graph RAG

| System | Build | Recall | Figures, and what they were measured on |
|---|---|---|---|
| **Microsoft GraphRAG** (arXiv 2404.16130) | an LLM extracts entities and relations; Leiden communities; LLM community summaries | global search (map-reduce over summaries) for "global sensemaking"; local search for entities | Better comprehensiveness and diversity than vector RAG on ~1M-token corpora, LLM-judged [C; the abstract gives no figure] |
| **LightRAG** | the GraphRAG-style extraction, without communities | dual-level keywords (low: entities; high: themes) | win rates against naive RAG by an LLM judge (e.g. legal comprehensiveness 83.6 % against 16.4 %, per a secondary summary) [C] |
| **HippoRAG** (arXiv 2405.14831) / **HippoRAG 2** (2502.14802) | OpenIE triples into a graph; v2 adds passage nodes | **Personalised PageRank from the query's entities** | multi-hop QA up to +20 %; as good as iterative IRCoT, 10-30× cheaper [M, paper]; v2: +7 % on associative tasks over a strong embedder, without losing factual QA [M, paper] |
| **Independent comparison** (Han et al., arXiv 2502.11371) | – | – | **Single-hop (NQ, F1): vanilla RAG 64.78 beats every GraphRAG** (community-local 63.01, HippoRAG2 61.03). Multi-hop: GraphRAG ahead (HotpotQA HippoRAG2 63.01 against RAG 60.04). KG-only GraphRAG trails: only 65-66 % of answer entities are in the extracted graphs. Running both and concatenating: +6.4 %. LLM-judge results flip with presentation order [M] |

**Readings:**
- **Graphs pay for multi-hop and relational questions, and cost on single-hop facts when they replace text
  retrieval.** Ours are mostly single-hop questions over stated records.
- **Our graph is stated, not extracted.** The census found 37,815 stated pairs. That is the cheap, exact kind that
  extracted graphs try to approximate (only 65-66 % of answer entities captured).
- **The way others use the graph is to start from seeds** (PPR in HippoRAG, BFS in Zep, the code-graph expansion in
  Continue). That matches our closure and one bounded hop. **[R]**

### 2.5 Long-term agent memory

| System | Build | Recall, fusion and rerank | Figures, and what they were measured on |
|---|---|---|---|
| **MemGPT / Letta** | core memory in context; archival (vector) and recall (history) stores the agent pages itself | the agent's own tool calls | DMR 93.4 % [M, quoted by Zep]. Letta (2025-08-12): an agent with **plain file tools (grep, open)** reached 74.0 % on LoCoMo with gpt-4o-mini, above Mem0's self-reported 68.5 % [M, vendor] |
| **Mem0** (arXiv 2504.19413) | an LLM extracts and consolidates facts (add, update, delete); optional graph (Mem0g) | vector search over the facts; graph lookups | LoCoMo LLM-judge: +26 % relative over OpenAI's memory; graph +2 %; p95 latency −91 % and tokens −90 % against full context [M, vendor; disputed by Zep and Letta] |
| **Zep / Graphiti** (arXiv 2501.13956) | a temporal knowledge graph: episodes, entities and fact edges with **bi-temporal validity**; an LLM marks a contradicted fact's `t_invalid` | **three searches: cosine over facts, names and communities, BM25 (Lucene) and BFS n hops from the hits or from recent episodes; then RRF, MMR, episode-mention frequency, node distance from a centroid, or a cross-encoder (the most accurate and the most costly)** | DMR 94.8 % against MemGPT's 93.4 % (judged a weak benchmark: full context scores 98 %). LongMemEval_s: gpt-4o 60.2 % → **71.2 %**, latency 28.9 s → 2.58 s, context 115k → 1.6k tokens. It *fell* on single-session-assistant questions (94.6 → 80.4) [M, vendor] |
| **A-MEM** (arXiv 2502.12110) | Zettelkasten notes with keywords, tags and context; LLM-made links; "memory evolution" updates old notes | links and embeddings | "superior improvement against SOTA baselines" on six models [C in the abstract] |

**Readings:**
- **Zep is the closest to our design:**
  - keyword, meaning and graph routes;
  - fusion, then an optional cross-encoder;
  - an explicit currency model (an invalidated edge).

  What we lack against it is currency carried *into the ranking*: Zep ranks valid facts and marks invalid ones. The
  W2-92 S9 status marks put currency into the bundle, not the order. **[R]**
- **Letta's file-tool result, Claude Code and Cursor point the same way:** an LLM caller that can run several
  searches recovers much of what a single-shot ranker misses. Our callers are agents. **[C/M, vendor]**

### 2.6 Anthropic's contextual retrieval (a method, not a system)
- **The figures** (1 − recall@20, averaged over codebases, fiction, ArXiv and science papers, Gemini text-004
  embeddings): **[M, vendor]**

  | Method | Failures in the top 20 |
  |---|---:|
  | baseline | 5.7 % |
  | contextual embeddings | 3.7 % |
  | plus contextual BM25 | 2.9 % |
  | **plus a rerank (Cohere) of the top 150 to 20** | **1.9 %** |

- **Our adopted headers** (path and headings in the embedding) are the deterministic, no-LLM part of this. The keyword
  half (C1) tied its control here. **[R]**

## 3. The component question

### 3.1 What each component is for

| Component | What it is for | Where it fails | Evidence |
|---|---|---|---|
| **Keyword (BM25)** | exact terms, ids, rare tokens, code symbols; robust out of domain | paraphrase, vocabulary gap | BEIR: "BM25 is a robust baseline" [M]. Azure: keyword queries 79.2 against vector 11.7; low-overlap queries 23.0 against 36.1 [M] |
| **Meaning (dense)** | paraphrase, concepts, the user's words against the record's | ids, numbers, exact strings; a weak model out of domain | Azure (as left) [M]; Cursor's +12.5 % over grep [M, vendor] |
| **Hybrid fusion** | recall: each route finds what the other misses | a weak route's noise enters; RRF is sensitive to k and depth | Azure hybrid 48.4 against 43.8 and 40.6 [M]; Bruch et al.: convex combination beats RRF with few labels (night one) [M] |
| **Graph** | relations: what governs, what changed, what depends; multi-hop | single-hop facts, if it replaces text; an extracted graph's gaps | Han et al. (2.4) [M]; HippoRAG [M]; Zep [M] |
| **Reranker** | precision at the top: it reads query and text together | see 3.2 | Azure +11.7 NDCG@3 over hybrid [M]; Anthropic −35 % failures [M] |

### 3.2 When a reranker helps and when it hurts
- **It helps:**
  - on concept, fact and low-overlap questions (Azure: +12 to +14 NDCG@3 in every kind but keyword queries);
  - over a recall-oriented first stage, on a modest head (Anthropic 150 → 20; Azure 50). **[M]**
- **It hurts, or helps less, in these cases:**
  - **Large pools.** Pointwise cross-encoders' Recall@10 falls as more documents are reranked. Scaling hurt in 53 %
    (academic) and 44 % (enterprise) of experiments, and the largest depth was best in only 3-15 %. Cross-encoders
    were never worse than the retriever in only 22-23 % of experiments. Examples: a relevant document went from 1st
    to 39th while an irrelevant one rose from 3,337th to 5th. Only a listwise LLM stayed robust (Jacob et al.,
    "Drowning in Documents", arXiv 2411.11767) [M]. **For us:** a weak reranker is the case most exposed to depth.
    Our 40 was adopted only inside v456: it was neutral or negative alone (v3: 34/30 against 36/29).
  - **Code:** the 0.6B reranker lowers Qwen's own MTEB-Code from 75.41 (the embedder alone) to 73.42; the 4B raises
    it to 81.20 [M, Qwen]. bge-reranker-v2-m3 scores CoIR 36.28 against 65-80 for code-trained rerankers [M, Jina].
    **For us:** this agrees with night one's finding that code questions do better with the code route's first two
    put ahead (r01, +3).
  - **Domain shift:** rerankers are trained on web question-answer pairs. Our corpus is records whose relevance often
    lies in an id or a label (`**Under:** DEC-n`). A reranker cannot know that DEC-1066 is "the decision about the
    reader cut". It sees the token. **[E]** Out of domain, BM25 and rerankers are the robust ones (BEIR) [M], but
    individual sets show near-zero gains (Elastic: Touché +0.01) [M].
  - **Long documents and short answers in long chunks:** a pointwise model gives one score for the whole text, so a
    one-line answer inside a 1,000-character chunk about something else is diluted. That is our C2 trait (the answer
    under a quarter of its chunk in 38 of 68 visible pieces). The usual answer is passage-level scoring with the best
    passage's score (MaxP; Dai and Callan 2019, not re-read), or small units searched with the parent returned
    (LlamaIndex auto-merging, LangChain parent-document). **[E/C]**
  - **Currency:** no public reranker knows that a record is superseded or amended. Contextual AI's v2 is the only one
    trained to follow recency instructions, and it is non-commercial [C].

### 3.3 Do others merge all of them as we do?
- **Keyword + meaning, fused, then one rerank:** this is standard (2.2, 2.3). We match it.
- **A graph route fused as a ranked list:** this is rare.
  - Zep runs BFS from the search hits and fuses by RRF or a cross-encoder.
  - HippoRAG ranks by PPR from the query's entities.
  - Continue expands found snippets along the code graph.
  - All three treat the graph as **expansion from seeds** or a **ranking feature** (Zep's node distance), not as an
    independently ordered list.
- **Agentic, multi-query search** is where code assistants have gone (Claude Code, Cursor, Letta's file agent).
  - The caller issues several queries, grep and semantic, and reads.
  - It does not replace a ranker: Cursor found grep plus semantic best. It moves query reformulation and two-part
    questions to the caller.
- **Why not merge everything:** each extra route adds candidates whose rank credit is not comparable. The fused head
  then dilutes, and a weak reranker over a larger pool degrades ("Drowning"). Engines that add stages (Qdrant, Vespa)
  make each later stage costlier and narrower, rather than wider.

### 3.4 Where our integration, chunking, embeddings or pool may be going wrong
Each point names the file and setting, the evidence and whether it is measured here.

1. **Post-rerank steps can pre-empt the reranker's top 5.** **[R]** In `retrieve.py`, after `rerank(...)`, in order:
   - `order.reranked` sorts on `rerank_score + 1.0 × tier steps` (`path-map.yaml` `retrieval_authority.lift.rerank:
     1.0`). With governing +1 and reports −1, the gap between them is 2.0 log-odds.
   - `named_first: 2` moves the named record's 2 best chunks ahead.
   - `code_first: 2` moves the code route's first 2 ahead.
   - DEC-424 moves failure and lesson records ahead.

   A question naming a record and a symbol has 4 of its first 5 places fixed before the reranker's order counts.
   D4B-MISSES says 10 of 19 misses were "ranked below 5" at places 6 to 12, and blames the reranker in 6. Those ranks
   are *final* ranks. **No record says whether the reranker's own order had the gold in its top 5.** The kept outputs
   carry `rerank_score`, `routing` and the tiers, so this is a no-GPU diagnostic.
2. **The authority lift is on the raw score scale of whichever reranker runs.** **[R]**
   - `lift.rerank: 1.0` adds log-odds to Qwen's `yes − no` logit. mxbai's score is `logit("1") − logit("0")`, on
     another scale: the vendor's example spans 0.5 to 12. The 4B's spread is not the 0.6B's either.
   - So the trial compared rerankers under **different effective authority weights**: a confound beside each model's
     quality.
   - Others put fixed boosts on a *normalised* score (Vespa's `normalize_linear`, Azure's calibrated 0-4).
   - Fix: lift on a per-query rank- or z-normalised score. Measurable by replay at no GPU cost.
3. **The closure route enters RRF in path order.** **[R]**
   - `routes[CLOSURE]` is the closure's chunks in `lexical.chunks()` order (path, then line). The hop's chunks are
     appended after.
   - So RRF gives `1/(60+1)` to whichever closure chunk's path sorts first: an arbitrary signal, worth as much as a
     route's first hit.
   - Night one measured the closure off, at weight 0.3 and ranked by vectors: no change on 48 (v03, v04, v06).
     D4B-STRUCTURE G3 found it does not crowd [M, here]. **Low priority**, but a cleaner design is the graph as a
     boost or a seed (3.3).
4. **The two indexes cover different corpora.** **[R]**
   - 50,351 of 69,464 keyword chunks (72 %) are keyword-only: `docs/close/**`, `docs/checkpoints/**`, `docs/probes/**`,
     the orchestration `closes/nightly/sessions/reviews/**`, `tests/**`, `cli/**`, fixtures, and vendored and adapter
     copies (`path-map.yaml`).
   - Most of these are *records of work that restate decisions*. They sit in the default "middle" tier beside tickets,
     except tests and probes ("reports").
   - Crowding ("the same topic restated across files and tiers") is a cause in 4 of the 19 misses (D4B-MISSES) and K5
     in all 7 hidden recall misses (D4B-STRUCTURE R3) [M, here].
   - Others scope the default search: Cody to the selected repositories, Azure by filters. A tier for records of work
     below the middle is a query-time setting.
5. **The reranker reads the path and the chunk only.** **[R]** `text = "[path: …]\n" + body`. Neither the heading path
   (C1's reranker half) nor the record's title, status or changers reach it. The title-and-section variant (fix-d) lost
   here [M, here], so this is not a lever as tried. A *status* line ("superseded in part by DEC-n") for register chunks
   is untried. It would let a reranker that follows instructions (the 4B) prefer current text. Unmeasured; **[E]** low.
6. **Dilution of one-item answers (C2) hits the reranker as well as the embedder.** C2 (answer units beside sections)
   widened the gap here (p2) [M, here]. The others' form is *search small, return the parent*: LlamaIndex auto-merging,
   LangChain `ParentDocumentRetriever`. That is what C2 plus the parent widening does. It may need the units to be the
   *only* thing the reranker scores, with the section returned, rather than units and sections competing in one pool.
   Unmeasured; **[E]**.
7. **The embedder.** **[R/C]**
   - `qwen3-embedding:0.6b` is served by Ollama as GGUF (639 MB, so probably Q8_0 [E]).
   - Qwen3-Embedding pools the last token and expects `<|endoftext|>` appended. Users have reported Qwen3-Embedding
     GGUFs scoring "far worse" when the EOS was not appended (r/LocalLLaMA, July 2025; llama.cpp #14234 said fixed)
     [C, forum]. Whether Ollama's build appends it is **unverified here**.
   - A cheap check (the CTO's, on the owner's service): compare the vectors of `text` and `text<|endoftext|>`. If they
     differ much, the EOS is not appended.
   - The query instruction is the generic web one (`semantic.py` `INSTRUCTION`). A repository instruction lost on
     night one [M, here].
8. **Depth and reranker strength go together.** **[M, here + paper]**
   - The routes are 60 deep and the reranker reads 40. The blind set lost 2 misses below the 40, and 10 at places 6 to
     12.
   - "Drowning" says a weak pointwise reranker gains least, and may lose, as depth grows.
   - So **a deeper pool is not the lever**. A stronger reranker on a *narrower* head is, which is what a cascade gives.
9. **The measure's resolution.** **[E, arithmetic]**
   - 138 questions. One question is 0.7 points on the 138 and 2.5 points on a set of 40. A proportion near 85 % on 40
     questions has a standard error of about 5.6 points.
   - The 4B's +5 on the 138 is not significant on its own. By an exact McNemar test, 5 gains and 0 losses give
     p ≈ 0.06; 7 against 2, p ≈ 0.18.
   - D4B-MISSES' caution 1 (up to 7 of the 19 may be missing label alternatives) is larger than any single lever here.

## 4. Residuals
- I could not read Cursor's chunking, Cody's ranking signals, GitHub Copilot's benchmark names or Contextual AI's
  numeric scores: they are not published in text.
- The mxbai finding rests on the code path and on rendering the template with the tokenizer, not on decoding the
  `input_ids` of a live `predict` call. That check needs the model loaded (on the CPU, about 3 GB of RAM) and is the
  CTO's to run if wanted. *(The CTO's note: done on a stand-in, 2026-11-05: mxbai's own configuration, tokenizer and
  template with tiny random weights; a pair renders through its template, and the instruction survives at every
  length sent, up to about 4,500 tokens.)*
- The Ettin (May 2026) and zerank-2 entries are new since night one. Ettin's MTEB-eng puts zerank-2 below the 0.6B,
  contradicting zerank's own table. Neither is measured on code-plus-prose like ours.
- No public figure exists for any reranker on governance records. Every quality estimate for our sets is reasoned from
  our own trial.

## Sources (all read 2026-11-05 unless marked)
- Qwen3-Reranker-0.6B card (evaluation table, template, instruction note): https://huggingface.co/Qwen/Qwen3-Reranker-0.6B
- jina-reranker-v3 card (BEIR / CoIR table, licence): https://huggingface.co/jinaai/jina-reranker-v3
- Ettin Reranker family (Hugging Face blog, 2026-05-19): https://huggingface.co/blog/ettin-reranker
- Contextual AI Reranker v2 (2025-08-27): https://contextual.ai/blog/rerank-v2 and https://huggingface.co/ContextualAI/ctxl-rerank-v2-instruct-multilingual-2b
- zerank-1-small: https://huggingface.co/zeroentropy/zerank-1-small ; zerank-2: https://huggingface.co/zeroentropy/zerank-2
- gte-reranker-modernbert-base: https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base
- bge-reranker-v2.5-gemma2-lightweight: https://huggingface.co/BAAI/bge-reranker-v2.5-gemma2-lightweight
- GTE-ModernColBERT-v1: https://huggingface.co/lightonai/GTE-ModernColBERT-v1
- mxbai-rerank-large-v2 README (the cached snapshot `ca7e1ee4…`, read locally); the mxbai-rerank v2 library: https://raw.githubusercontent.com/mixedbread-ai/mxbai-rerank/main/mxbai_rerank/mxbai_rerank_v2.py
- Jacob et al., "Drowning in Documents" (arXiv 2411.11767, v2): https://arxiv.org/html/2411.11767v2
- Qwen3-Reranker GGUF and llama.cpp status (secondary): https://huggingface.co/cicaba/Qwen3-Reranker-0.6B-GGUF-llamacpp-fixed ; https://github.com/ggml-org/llama.cpp/pull/14029
- Qwen3-Embedding GGUF EOS reports (forum): https://libreddit.winscloud.net/r/LocalLLaMA/comments/1lt18hg/are_qwen3_embedding_gguf_faulty
- Sourcegraph, "How Cody understands your codebase" (2024-02-15): https://sourcegraph.com/blog/how-cody-understands-your-codebase ; Hartman et al., arXiv 2408.05344: https://ar5iv.labs.arxiv.org/html/2408.05344
- Cursor, "Improving agent with semantic search" (2025-11-06): https://cursor.com/blog/semsearch
- Claude Code and agentic search (secondary): https://smartscope.blog/en/ai-development/practices/rag-debate-agentic-search-code-exploration/
- GitHub, "The technology behind GitHub's new code search" (2023-02-06): https://github.blog/engineering/architecture-optimization/the-technology-behind-githubs-new-code-search/
- GitHub Copilot's new embedding model (2025-09-24): https://github.blog/news-insights/product-news/copilot-new-embedding-model-vs-code/
- Aider repo map: https://aider.chat/docs/repomap.html , https://aider.chat/2023/10/22/repomap.html , source https://raw.githubusercontent.com/Aider-AI/aider/main/aider/repomap.py
- Continue retrieval source: https://github.com/continuedev/continue/blob/b0cdd0ed920bde2d25915dd61920569c03b6dc63/core/context/retrieval/retrieval.ts ; docs https://docs.continue.dev/features/codebase-embeddings
- LlamaIndex basic strategies: https://developers.llamaindex.ai/python/framework/optimizing/basic_strategies/basic_strategies/
- Azure AI Search, hybrid retrieval and ranking: https://techcommunity.microsoft.com/blog/azure-ai-services-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167
- Elastic Rerank: https://www.elastic.co/search-labs/blog/elastic-semantic-reranker-part-2
- Vespa phased ranking: https://docs.vespa.ai/en/phased-ranking.html
- Qdrant hybrid queries: https://qdrant.tech/documentation/concepts/hybrid-queries/
- Weaviate hybrid search: https://docs.weaviate.io/weaviate/search/hybrid
- Microsoft GraphRAG (arXiv 2404.16130): https://arxiv.org/abs/2404.16130
- LightRAG (secondary summary): https://www.emergentmind.com/topics/lightrag-framework
- HippoRAG (arXiv 2405.14831): https://arxiv.org/abs/2405.14831 ; HippoRAG 2 (arXiv 2502.14802): https://arxiv.org/abs/2502.14802
- Han et al., RAG vs GraphRAG (arXiv 2502.11371): https://arxiv.org/html/2502.11371
- Zep (arXiv 2501.13956): https://arxiv.org/html/2501.13956
- Mem0 (arXiv 2504.19413): https://arxiv.org/abs/2504.19413
- Letta, "Benchmarking AI agent memory" (2025-08-12): https://www.letta.com/blog/benchmarking-ai-agent-memory
- A-MEM (arXiv 2502.12110): https://arxiv.org/abs/2502.12110
- Anthropic, contextual retrieval: https://www.anthropic.com/engineering/contextual-retrieval
- BEIR (arXiv 2104.08663): https://arxiv.org/abs/2104.08663
- (night one, read 2026-11-03) Cormack et al. RRF, Bruch et al. fusion functions, the Elastic hybrid blog, OpenSearch z-score, Haystack DocumentJoiner, the LlamaIndex fusion retriever, RankZephyr, ColBERTv2, Jina-ColBERT-v2, CoIR, the Chroma chunking study and HyDE: see `/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/REPORT.md`
- Read here: `src/gov/retrieval/{retrieve,rerank,rerank_worker,fusion,routing,lexical,authority,semantic,chunking}.py`, `governance/project/{retrieval,rebuild,path-map}.yaml`, the reranker venv's `sentence_transformers/base/modules/transformer.py`, `base/modality.py` and `cross_encoder/modules/logit_score.py`, and the cached snapshots' `chat_template.jinja`, `sentence_bert_config.json`, `config_sentence_transformers.json`, `modules.json`, `1_LogitScore/config.json` and `tokenizer_config.json`
