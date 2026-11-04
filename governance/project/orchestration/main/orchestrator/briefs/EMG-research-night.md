# The research agent, the night of 2026-11-04: step 3 of DEC-1067 (the CTO)

Read the register's `### DEC-1067` (grep) first: it is the owner's order for tonight and it changes your rules.

**What changed since your survey:** W2-32's G1 is merged into `w2/integrate` (the embedder reads up to 10,000 characters
of each chunk, the reranker up to 32,768, requests capped at 16 texts, no span sent twice), and D-7's path map (tests,
records and the evaluation set's own documents out of the vectors; lens B's report, W2-15a's raw output and the
evaluation fixtures out of both indexes). The CTO rebuilt a clone at the merged head with a full re-embed: **the fixed
stores**, at `/home/usain/gov-os-runs/D4B/g1/repo` (commit `296a4639`, w2/integrate with W2-32 G1, D-7, W2-13, and tonight's re-labels of visible Q03, Q16, Q19 and re-anchors of q10, q12). Use that clone for every run; never rebuild it yourself.

**Your rules tonight (DEC-1067 (b), standing):**
- **The visible half only.** Every run is `--part visible`. You never run `--part all` or `--part hidden`, and you never
  read a hidden record. The hidden half is read only by the CTO's measures, and **never chooses**: a method is a winner
  only if it wins on the visible half alone.
- Each method on its own, against the fixed stores' own baseline (re-run the shipped path on the clone first: it is the
  new base; check your harness still reproduces the product at no-op, digests equal).
- hit@5 and full evidence on the 24 visible questions, and **the speed per search** (median over the run) for every
  variant.
- **GPU safety (as last night):** only today's models, nothing new loaded, no install; `nvidia-smi` before each batch;
  smaller batches near the limit (never more than 16 texts per reranker request: the product's cap); wait at or above
  15.5 GB (15,872 MiB) or on any sign of a spill, and log every wait in `raw/gpu-waits.txt`. The CTO's backstop pauses
  your processes past 15,872 MiB, at the card's total, or if an embedder loses layers: if your run stops making
  progress, that is why; restart or kill nothing; wait for the CTO.
- One run at a time, through `heavy_slot.sh`. No measure and no rebuild of the CTO's runs beside yours (the CTO keeps to
  that).

**The methods to test, each on its own (DEC-1067 order (3)):**
1. G3's routing by question type (your r01 and s01 halves, separately).
2. Each route's top hits guaranteed a place in the reranker's pool.
3. The reranker shown each chunk's path, title and section as well as its text.
4. Repository-specific instructions for the embedder (query side only: no re-embed) and the reranker (the Qwen3 models
   take an instruction).
5. Questions expanded with the record ids and symbols the knowledge graph and the code graph find.
6. Several phrasings of a question searched and fused (phrasings made deterministically from the question: no model
   call beyond today's; state how).
7. Route agreement and authority combined with the reranker's score.
8. Any other method you find, query-time, no install.

Also list the **index-time** methods worth trying (chunks carrying their file and section headings when embedded;
file-level and chunk-level indexes together; others), with your expected effect: the CTO groups them into the next
rebuild for measure 4.

**Return:** a table (method, visible hit@5, visible full evidence, speed, gained and lost visible ids), the winners on
the visible half alone, and your best combination's visible figure, for the CTO's measure 3. Commit to
`w2/research-retrieval` under `docs/research/EXP-003/retrieval-survey/night/` (`raw/` stays on the branch, DEC-1067
(b)). Your return is the report: write it as text (your file write of a report was refused last time), the CTO files it.
Never read secrets, held-out material or the hidden half.
