# D-4b research and discovery: rerankers that fit, other memory systems, and what each component is for (owner, 2026-11-05)

You are a research and discovery session for the CTO of the Gov OS repository (`/home/usain/Dynamic-Agentic-Engineering-OS`,
branch `w2/integrate`). **Read-only, no installs, no model downloads, no GPU, no `gov retrieve` runs.** Web research
(WebSearch, WebFetch) is allowed. Your writes: only the folder `docs/research/D4B-memory-survey/` in the main tree
(create it). Read `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` for the common rules. Do not commit; the
CTO commits.

## Why this matters (the owner's words, in short)
D-4b, memory, is the core of the Gov OS. The owner wants as much evidence as can be had before deciding the next
levers. Nothing is adopted before the owner decides. Be thorough, cite every source, and say what each figure was
measured on; separate what is measured from what is claimed.

## What our memory is today (read these first; they are the facts to compare against)
- `docs/research/W2-88-memory-practice.md` (how the store is built, measured and tuned; every method tried with figures)
- `governance/project/orchestration/packages/LIFT-1/D4B-STRUCTURE.md` (the structural review)
- `governance/project/orchestration/packages/LIFT-1/D4B-MISSES.md` (the 19 misses by kind)
- `governance/project/orchestration/packages/LIFT-1/D4B-TRIAL-W4.md` (the reranker trial: 0.6B 107/138, mxbai 76, Qwen3-4B 8-bit 112)
- `docs/research/D4B-link-census.md` (the stated links)
- the code: `src/gov/retrieval/` (`retrieve.py`, `routing.py`, `lexical.py`, `semantic.py`, `rerank.py`, `graph_route.py`,
  `code_route.py`, `chunking.py`), `src/gov/store/loader.py`
- the earlier survey (night one): `/home/usain/gov-os-worktrees/research-retrieval/docs/research/EXP-003/retrieval-survey/REPORT.md`
- **Never read:** the hidden questions or the measurement sets (`~/gov-os-eval/`), any run output (`~/gov-os-runs/`),
  the visible questions' files are allowed only for their form, never to tune.

**In short:** four stores (a record graph with stated links, an FTS5 BM25 keyword index, a sqlite-vec meaning index
with Qwen3-Embedding-0.6B on the GPU, a code graph); chunks about 1,000 characters inside parent sections, embedded
with their heading path; recall by three deterministic phrasings, keyword and meaning routes (60 deep under v456), the
record route and its closure, the code route, the stated-links hop; RRF (k 60) with an authority lift; the first 40
fused reranked once by Qwen3-Reranker-0.6B (a shared GPU service, requests bounded at 16 texts and 24,000 padded
characters); routing by question type; at most 2 chunks of a file in the first 10; a 6,000-token bundle widened to
parent sections; continuations.

**The machine:** one RTX 5070 Ti, 16,303 MiB, shared by two embedding servers (about 2.3 GB each) and the desktop (about
1.2 GB); the dispatcher's GPU budget is 14,255 MiB, the backstop 15,872 MiB; so a reranker has about 8 GB at most, less
its working memory. Searches may come 10 to 20 at once from parallel agents. Linux under WSL2, CUDA 13, torch 2.14,
transformers 5.18, sentence-transformers 6.1.

## The three questions
1. **Rerankers that fit this machine.** Every open model that fits the budget beside the two embedders: cross-encoders
   of every size, quantised and smaller variants, late-interaction models (ColBERT-style), LLM rerankers (listwise,
   pointwise). For each: licence; parameters and GPU memory (and in 8-bit or 4-bit where that is offered); its input
   template (how query and document must be given, which matters: our mxbai run was probably fed without its template);
   published retrieval scores (BEIR, MTEB-R, CoIR, MTEB-Code, others) with the source; expected speed alone and with
   10 to 20 searches at once on a card like ours (reason from parameters and published throughput where no figure
   exists, and mark it estimated).
2. **Other memory systems.** How established retrieval and agent-memory systems build memory (chunking, embedding,
   indexes, graphs), recall, fuse and combine routes, whether and how they rerank (two or three stages), and the hit
   rates they report, with what each figure was measured on. At least: code assistants' code search (e.g. Sourcegraph
   Cody, Continue, Cursor, GitHub's code search, Aider's repository map), RAG frameworks (LlamaIndex, LangChain,
   Haystack), search engines' hybrid search (Elasticsearch/OpenSearch, Vespa, Weaviate, Qdrant, Azure AI Search), graph
   RAG (Microsoft GraphRAG, LightRAG, HippoRAG), long-term agent memories (MemGPT/Letta, Mem0, Zep/Graphiti, A-MEM), and
   anything else that is well evidenced.
3. **The component question.** What each component is usually for (keyword search, meaning search, graphs, rerankers);
   when a reranker helps and when it hurts (domain shift, code, long documents, short answers in long chunks); whether
   others merge all of them as we do, and why or why not; and where our integration, chunking, embeddings or pool may be
   going wrong compared with them. Be concrete about our design, with the files and settings.

## What you deliver
1. `docs/research/D4B-memory-survey/REPORT.md`: the three questions answered, every claim with its source (URL and
   date read) and whether it is measured or claimed, tables where they help; plain words.
2. `docs/research/D4B-memory-survey/PACKAGE-DRAFT.md`: a draft for the owner, for the CTO to review: what we should
   adopt, what not, why, and the expected rise in hit@5 of each (on our sets of 138; give a range and say how it is
   reasoned), in the order you would try them, each with its cost (GPU, time, install, code) and how it would be
   measured under our rules (structural fixes only; judged on all used sets together; a fresh set for the verdict).
3. Your return: the twelve labelled fields (EMG-common.md), then the package draft's list of recommendations in short.

Est.: 3 to 4 hours. Work in the order 1, 3, 2 if time is short, but cover all three.
