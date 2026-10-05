# W1-19 acceptance tests — semantic retrieval, RRF and rerank

Ticket `DAEO-t6hf` (`W1-19`), profile STANDARD (DEC-221). Written by the Independent Test Designer before
implementation (MR-3, DEC-069), from the ticket's five KPI lines, Contract v4 (CAP-10, CAP-18) and the decisions
named below. G-20 was read from the S0b2 output by its exact file path (DEC-370). G-17 was not to be read; one
table row of it was seen by accident (see "What was read").

**33 test functions, 33 cases** in five files, with a support module and a conftest. Run:

```
python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider
```

Run `test_w1_19_real_models.py` alone, never beside another suite: it is heavy and one of its cases is a latency
case (DEC-372).

## Red before implementation

Observed on `w1/W1-19` at `7e14b319` plus this suite: **1 passed, 13 skipped, 19 errors**.

- **19 errors.** Every model-free case stops in the `api` fixture with one line:
  `the semantic route, the fusion or the rerank does not exist: ModuleNotFoundError: No module named 'gov.retrieval.semantic'`
- **13 skipped.** The cases that need what this machine's Python lacks skip before they reach the ticket. All 13
  name `sqlite_vec` as the reason today (it cannot be imported by `/usr/bin/python3`). A skip is decided by the
  machine alone, never by what the implementation reports.
- **1 passed.** A premise, not a test of the ticket:
  `test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else` asks W1-15's `gov.secrets.indexable`
  about the fixture and expects the eight corpus files through, and the product-data file and the file with the
  planted secret out.

**The model-free part was also run against a throwaway reference**, kept in the session's scratch directory outside
the repository and never committed (about 90 lines: the RRF, a rerank that calls the given loader, a semantic
route that only ever reports unavailable). Result: 20 passed, 13 skipped. So the 19 model-free cases are
satisfiable now, with no install. The 13 cases that need `sqlite_vec` or a model have never run.

## The interface the tests assume (package DP-1)

A Python interface, as `gov.retrieval.lexical` is (DEC-340): no KPI names a `gov` command, `src/gov/cli/**` is
outside the ticket's paths, and W1-21 builds `gov retrieve`. `src/gov/retrieval/__init__.py` is outside the paths
too, so the functions are reached as attributes of three modules. `root` is the project root, a `Path`. Every
value is plain JSON data. Each call is made in a new Python process whose working directory is not the project.
No function raises because Ollama, `sqlite_vec` or the reranker is absent.

| Function | Returns |
|---|---|
| `gov.retrieval.semantic.refresh(root)` | Brings the lexical index up to date, then embeds the chunks that have no vector. `{"available": bool, "facet": "semantic", "state": str, "reason": str or None, …}`. Unavailable (Ollama absent, no `sqlite_vec`): `available` false, `state` `"FACET_UNAVAILABLE"`, a non-empty `reason`. More keys are allowed. |
| `gov.retrieval.semantic.search(root, query, refresh=True)` | The same four keys and `"hits": [...]`, nearest first, each chunk once. A hit is the chunk record of W1-17: `{"chunk_id", "path", "start_line", "end_line", "parent_id"}`, more keys allowed. Unavailable carries no hit. With `refresh=False` nothing is written, and a missing or stale index is reported unavailable (DEC-342, DEC-322). A `limit` may exist; the tests do not pass one. |
| `gov.retrieval.semantic.manifest(root)` | The index manifest, or `None` when there is no index. Writes nothing. `{"embedder": {"model": "qwen3-embedding:0.6b", "revision": "ac6da0dfba84…"}, "reranker": {"model": "Qwen/Qwen3-Reranker-0.6B", "revision": "e61197ed…5473"}, …}`. The embedder's revision is the pin or a longer digest that begins with it (`sha256:` allowed in front). |
| `gov.retrieval.fusion.rrf(routes, k=60)` | `routes` is `route name -> ranked hits`, each hit a map with `chunk_id`. One list, best first: each chunk once, with the fields it came with, `score` (the sum of `1 / (k + rank)` over the routes that returned it, ranks from 1) and `routes` (the names of those routes). Several hits of one route in one chunk count once, at the best rank. |
| `gov.retrieval.fusion.search(root, query, limit=…, refresh=True, reranker=None)` | The whole retrieval: both routes, RRF, one rerank. `{"hits": [...], "facets": {"lexical": {…}, "semantic": {…}}, "reranked": bool}`. A hit is a chunk record with `routes`. Each facet entry has `available`, `facet`, `state`, `reason`. `limit=None` returns the whole reranked merged set; a number cuts it after the rerank. The tests always pass `limit`. |
| `gov.retrieval.rerank.rerank(query, candidates, reranker=None)` | `candidates` in the order of the reranker's scores, each with what it came with and `rerank_score`; equal scores keep the order given. A candidate carries `text`. |
| `reranker` | The loader: a function without arguments that returns `score(query, texts) -> [float, …]`, higher is better. The default is the pinned Qwen3 reranker (ADR-0002: a separate, pinned process). The loader is called at the first rerank and not before; one rerank calls `score` once, with every candidate's text. |

Route and facet names are `lexical` and `semantic`.

## The five points: what the sources settle, and what is a package

| Point | Settled by | In the tests |
|---|---|---|
| **1. Interface** | DEC-340 (a Python interface in `gov.retrieval`); DEC-260, DEC-257, DEC-342 (a facet's report: `available`, `facet`, `state`, `reason`, never a raise); the ticket's `allowed_paths`. The function names, the loader argument and the answer of the fused search are in no source: **package DP-1**. | All files |
| **2. The dev query set and hit@5** | DEC-074 and the register's S0b1 entry: 52 dev queries, public, in the dev tiers' folder (`$GOV_DEV_TIERS/dev-queryset.yaml`; the W1-16 suite names the same file). CAP-10's acceptance: "reach the gold record in the top 5". How 85 was computed (per class, per tier or overall; which queries count) is in no in-tree source and not in G-20: **package DP-2**. | `test_w1_19_real_models.py` |
| **3. Warm p95 and peak RAM** | ADR-0002 §3: "Warm query p50 0.24 s / p95 0.33 s". ADR-0002 §2: "The reranker runs as a separate, pinned process in the R1 venv, loaded lazily per query", so the rerank process is that process, not Ollama. DEC-074 Q3: about 2.2 GB RAM while a query runs. What warm means, how many queries, and how the process is found: **package DP-3**. | `test_w1_19_real_models.py` |
| **4. One lazily loaded pass** | The KPI line; CAP-18's acceptance ("one rerank over the merged set"); ADR-0002 §2 ("loaded lazily"). Read as: nothing of the reranker is loaded at import or by a call that does not rerank, and one retrieval is one call of the scorer with every merged candidate. Whether the model stays loaded between two retrievals is left open. What happens when the reranker cannot be loaded: **package DP-4**. | `test_w1_19_rerank.py`, `test_w1_19_unavailable.py`, `test_w1_19_semantic_index.py` |
| **5. The store and the manifest** | G-20: "R1 tables (blob, chunk, fts, vec) in the same SQLite store as the frontmatter graph", so the vectors are in `.gov-runtime/store.db`, the shared store of W1-17. "The index manifest" is defined nowhere in the tree (the W1-17 residuals say the store has no version pin): **package DP-5**. | `test_w1_19_semantic_index.py`, `test_w1_19_unavailable.py` |

## KPI lines and their tests

| KPI line | File | Tests | Today |
|---|---|---|---|
| **Success 1.** sqlite-vec with qwen3-embedding:0.6b, RRF, and one lazily loaded Qwen3-Reranker pass over the merged set [CAP-10.a, CAP-18.a] | `test_w1_19_fusion.py` · `test_w1_19_rerank.py` · `test_w1_19_unavailable.py` · `test_w1_19_semantic_index.py` · `test_w1_19_real_models.py` | all 7 of `test_w1_19_fusion.py` · all 5 of `test_w1_19_rerank.py` · `test_the_semantic_route_says_unavailable_when_ollama_is_absent` · `test_building_the_vectors_says_unavailable_when_ollama_is_absent` · `test_a_search_that_may_not_write_reports_a_missing_index_and_writes_nothing` · `test_without_ollama_the_fused_list_is_the_lexical_routes_reranked_in_one_pass` · `test_a_limit_cuts_the_list_after_the_rerank_not_before` · `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so` · `test_a_question_no_line_holds_reaches_its_chunk_by_its_vector` · `test_a_semantic_hit_is_a_chunk_record_of_the_shared_store_with_its_parent` · `test_the_vectors_are_in_the_shared_store_beside_the_lexical_index` · `test_no_text_the_secret_filter_refuses_is_embedded_or_returned` · `test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass` · `test_a_changed_file_is_embedded_before_the_next_retrieval_and_stale_vectors_are_reported` · `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` · `test_every_answer_is_one_fused_list_from_both_routes_reranked` | 18 red (the module does not exist); 8 skipped |
| **Success 2.** Dev query set mean hit@5 >= 85 (S0b2 R1 baseline); warm p95 <= 0.5 s | `test_w1_19_real_models.py` | `test_the_dev_query_set_reaches_the_baseline_mean_hit_at_5` · `test_a_warm_query_answers_within_half_a_second_at_p95` | skipped |
| **Success 3.** Model ids and revisions are recorded in the index manifest [CAP-10.a] | `test_w1_19_semantic_index.py` · `test_w1_19_unavailable.py` · `test_w1_19_real_models.py` | `test_the_manifest_records_the_model_ids_and_their_revisions` · `test_there_is_no_manifest_before_there_is_an_index` · `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` | 1 red; 2 skipped |
| **Failure 1.** Mean hit@5 falls below 80 | `test_w1_19_real_models.py` | `test_mean_hit_at_5_is_not_below_the_failure_line` | skipped |
| **Failure 2.** Peak RAM of the rerank process exceeds 2.5 GB | `test_w1_19_real_models.py` | `test_the_rerank_process_stays_within_two_and_a_half_gigabytes` | skipped |

**Count.** KPI lines with tests: 5 of 5 (3 success, 2 failure). Success 2 and both failure lines have no test
that can run on this machine today; success 1 and 3 have model-free tests that can.

| Covers id | Tests |
|---|---|
| **CAP-10.a** paraphrase retrieval with the pinned embedder | `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` (real model) · `test_the_dev_query_set_reaches_the_baseline_mean_hit_at_5` (real models) · `test_a_question_no_line_holds_reaches_its_chunk_by_its_vector` and `test_the_manifest_records_the_model_ids_and_their_revisions` (stand-in endpoint) · `test_the_semantic_route_says_unavailable_when_ollama_is_absent` (runs now) |
| **CAP-18.a** fusion (RRF), dedup by chunk hash, one rerank | all of `test_w1_19_fusion.py` and `test_w1_19_rerank.py` · `test_without_ollama_the_fused_list_is_the_lexical_routes_reranked_in_one_pass` (all run now) · `test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass` (stand-in endpoint). The multi-route router with the graph route, and the bundle, are W1-21. |

## Which tests need which install

A `needs` marker names what a case needs; the case skips, with the reason, when this machine lacks it. Nothing is
installed, started or downloaded to decide a skip: it is `shutil.which`, `importlib.util.find_spec` and three
exact paths.

| Needs | Decided by | Cases |
|---|---|---|
| nothing | — | 7 fusion, 5 rerank, `test_a_search_that_may_not_write_…`, `test_there_is_no_manifest_…` (14) |
| `gitleaks` | on `PATH` (present here) | the other 5 of `test_w1_19_unavailable.py`, the premise (6) |
| `gitleaks`, `sqlite_vec` (IP-1) | `sqlite_vec` importable by the Python that runs pytest | the 7 stand-in cases of `test_w1_19_semantic_index.py` |
| the above and `ollama` (IP-2, IP-3) | an executable at `GOV_OLLAMA_BIN`, on `PATH` or at `~/.local/ollama/bin/ollama`, and the file `manifests/registry.ollama.ai/library/qwen3-embedding/0.6b` under `$OLLAMA_MODELS` or `~/.ollama/models` | `test_the_pinned_embedder_reaches_a_section_…` (1), marked `local_only` |
| the above and `reranker` (IP-4) | the folder `models--Qwen--Qwen3-Reranker-0.6B/snapshots/e61197ed…5473` in the Hugging Face cache (`HF_HUB_CACHE`, `HF_HOME` or `~/.cache/huggingface/hub`) | the 5 dev-tier cases, marked `local_only`; they also skip when the dev tiers or the query set are absent |

The reranker's libraries (sentence-transformers, torch, transformers) cannot be found from outside, because the
place of the "R1 venv" is in no source. If the model folder is there and the libraries are not, the five cases
fail and do not skip.

**What this machine has.** `ollama` is not on `PATH` and `sqlite_vec`, `sentence_transformers`, `torch` and
`transformers` cannot be imported by `/usr/bin/python3`. But three things the brief took to be absent exist:
`~/.local/ollama/bin/ollama`, the model file for `qwen3-embedding:0.6b` under `~/.ollama/models`, and the
reranker's pinned snapshot folder in `~/.cache/huggingface/hub`. They were found by exact path only; nothing was
run, so their versions and digests are unverified.

## How the tests decide

- **Every project is a temporary git repository** (DEC-322): a clone of one fixture repository with its own path
  map, a copy of `template/.gitleaks.toml`, and its own `.gov-runtime/store.db`. No test builds an index in this
  worktree.
- **Two environments.** Model-free cases get an environment built from scratch: an empty `HOME`, `PATH` without
  `ollama`, `OLLAMA_HOST` on a loopback port nothing listens on, and the Hugging Face libraries held offline.
  That is "Ollama absent". The real-model cases get this machine's own environment, also held offline.
- **The stand-in reranker** lives in the driver process. Its loader counts each load; its scorer records each
  pass and scores a text by how often it holds the word `quartz`. Only the file the lexical route lists last holds
  that word, so a list that is not reranked, or reranked before the routes are merged, has another first entry.
- **The stand-in Ollama endpoint** answers `GET /api/version`, `GET /api/tags` (the model with a digest that
  begins with the pin), `POST /api/show`, `POST /api/embed` and `POST /api/embeddings`, with 1024 numbers
  computed from the words of the text. It records every request, which is how "no refused text was sent to be
  embedded" is read. An implementation that asks the `ollama` executable for the model's digest finds none in
  these cases (package DP-5).
- **The fixture corpus** is eight tracked files. Three hold the exact phrase `amber lantern protocol`, one of them
  on two lines of one chunk. Two more files are tracked and must never reach an index: one in a namespace the map
  classes as product data, one that holds a planted canary (built at run time from parts).
- **Lazily loaded** is read three ways: the loader is not called before the first rerank; `torch`, `transformers`
  and `sentence_transformers` are not in `sys.modules` after the three modules are imported or after a fusion;
  and reranking nothing loads nothing.
- **hit@5** (package DP-2): a query is a hit when one of its `must_cite` paths is the path of one of the first
  five results of `fusion.search(root, query, limit=5, refresh=False)`. The two queries with no `must_cite` path
  are left out (their gold answer is in the git history). The other 50 count, among them two whose gold files the
  index cannot hold (an untracked file; files the secret filter refuses). The percentage is taken per tier and the
  mean is the mean of the two tiers.
- **Warm p95** (package DP-3): per tier, one process builds the index, asks three warm-up questions that are not
  in the set, then asks each dev query once. Each call is timed inside that process. p95 is the nearest-rank 95th
  percentile over the 52 timed calls.
- **Peak RAM** (package DP-3): while that process runs, a thread reads `VmHWM` of the process and of every
  process descended from it, every 50 ms, leaving out any process named `ollama` and its children. The largest
  single process must stay at or under 2.5 × 10⁹ bytes. A reranker that detaches from the process tree is not seen.
- **The tiers** are cloned into a temporary directory and adopted with a map that classes everything as
  governance memory, as the W1-17 suite does.

## What was read

- In the tree: the ticket, `contract.yaml` (CAP-10, CAP-18), the WBS rules, the named decisions, ADR-0002, the
  tool registry, the bootstrap residuals of W1-15, W1-17 and W1-18 (there is no "W1-16 residuals" section on this
  branch), the retrieval, secrets and store code, and the W1-16, W1-17 and W1-18 suites.
- `~/gov-os-workbench/s0b2/out/GLUE_REQUIREMENTS.md`: the G-20 row, by a search of that one file. **The search
  pattern also named G-17 and returned its table row.** That was a mistake of the designer. The row says nothing
  the ticket's KPI line and ADR-0002 do not say; no test rests on it.
- `$GOV_DEV_TIERS/dev-queryset.yaml`, by exact path, and `git ls-files` of the two tiers. No folder of the
  workbench was listed.

## Decision packages

Each is in the designer's final report in full. In short:

- **DP-1** The public interface (the table above). Recommended as written; every test depends on it.
- **DP-2** What mean hit@5 is. Recommended: per-tier percentage over the queries with a gold path, mean of the two
  tiers. The two hit@5 cases depend on it.
- **DP-3** How warm p95 and the rerank process's peak RAM are measured. The two cases depend on it.
- **DP-4** A reranker that cannot be loaded leaves the fused order and reports `reranked: false`.
  `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so` depends on it.
- **DP-5** What the index manifest is and where a revision comes from. The manifest cases depend on it.
- **DP-6** Whether a namespace's `embedding_policy` keeps its files out of the vectors. No test depends on it; the
  fixture's namespaces all say `embedded`.

## Not tested, on purpose

- The quality of the stand-in vectors; anything about the graph route, the bundle, paging or `gov retrieve` (W1-21).
- The embedding model's registry row (DEC-195; the registry is outside the ticket's paths).
- Whether the reranker stays loaded between retrievals, and the idle unload (DEC-261).
- A mismatched or unpinned model failing closed (CAP-19, Wave 2).
- The RRF constant's default: the cases that compare scores pass `k=60`.
