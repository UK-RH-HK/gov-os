# W1-19 acceptance tests — semantic retrieval, RRF and rerank

Ticket `DAEO-t6hf` (`W1-19`), profile STANDARD (DEC-221). Written by the Independent Test Designer before
implementation (MR-3, DEC-069), from the ticket's five KPI lines, Contract v4 (CAP-10, CAP-18) and the decisions
named below. Two batches: the first returned seven decision packages; the second, after they were decided
(DEC-373, DEC-374, DEC-379 to DEC-384), revised the suite to the answers.

**39 test functions, 39 cases** in six files, with a support module and a conftest (33 after the first batch). Run:

```
python3 -m pytest tests/acceptance/W1-19 -q -p no:cacheprovider
```

Run `test_w1_19_real_models.py` alone, never beside another suite: it is heavy and one of its cases is a latency
case (DEC-372).

## Red before implementation

Observed on `w1/W1-19` at `1a6f9a45` plus this suite: **1 passed, 16 skipped, 22 errors**.

- **22 errors.** Every model-free case stops in the `api` fixture with one line:
  `the semantic route, the fusion or the rerank does not exist: ModuleNotFoundError: No module named 'gov.retrieval.semantic'`
- **16 skipped.** The cases that need what this machine's Python lacks skip before they reach the ticket. All 16
  name `sqlite_vec` as the reason today (it cannot be imported by `/usr/bin/python3`). A skip is decided by the
  machine alone, never by what the implementation reports.
- **1 passed.** A premise, not a test of the ticket:
  `test_the_secret_filter_lets_the_fixture_corpus_through_and_nothing_else` asks W1-15's `gov.secrets.indexable`
  about the fixture and expects the eight corpus files through, and the product-data file and the file with the
  planted secret out.

In the first batch the 19 model-free cases of that time were run against a throwaway reference outside the
repository (20 passed, 13 skipped). The second batch built no reference and no stand-in of the ticket's modules: its
three new model-free cases and the one it tightened were reasoned from the decisions, and have never run green. The
16 cases that need `sqlite_vec` or a model have never run at all. No model was loaded and Ollama was not started in
either batch (DEC-384).

## The interface (DEC-379)

A Python interface, as `gov.retrieval.lexical` is (DEC-340): no KPI names a `gov` command, `src/gov/cli/**` is
outside the ticket's paths, and W1-21 builds `gov retrieve`. The functions are reached as attributes of three
modules. `root` is the project root, a `Path`. Every value is plain JSON data. Each call is made in a new Python
process whose working directory is not the project. **No function raises because Ollama, `sqlite_vec` or the
reranker is absent.**

| Function | Returns |
|---|---|
| `gov.retrieval.semantic.refresh(root)` | Brings the lexical index up to date, then embeds the chunks that have no vector. `{"available": bool, "facet": "semantic", "state": str, "reason": str or None, …}`. Unavailable (Ollama absent, no `sqlite_vec`): `available` false, `state` `"FACET_UNAVAILABLE"`, a non-empty `reason`. More keys are allowed. |
| `gov.retrieval.semantic.search(root, query, refresh=True)` | The same four keys and `"hits": [...]`, nearest first, each chunk once. A hit is the chunk record of W1-17: `{"chunk_id", "path", "start_line", "end_line", "parent_id"}`, more keys allowed. Unavailable carries no hit. With `refresh=False` nothing is written, and a missing or stale index is reported unavailable (DEC-342, DEC-322). |
| `gov.retrieval.semantic.manifest(root)` | `None` when there is no index; else `{"embedder": {"model", "revision"}, "reranker": {"model", "revision"}}`. Writes nothing and asks Ollama nothing: the manifest is held in the shared store (DEC-374). The embedder's revision is the digest the endpoint's model list reported when the vectors were built, not a constant (DEC-374); the tests accept the digest or its first twelve or more characters, with `sha256:` allowed in front. |
| `gov.retrieval.fusion.rrf(routes, k=60)` | `routes` is `route name -> ranked hits`, each hit a map with `chunk_id`. One list, best first: each chunk once, with the fields it came with, `score` (the sum of `1 / (k + rank)` over the routes that returned it, ranks from 1) and `routes` (the names of those routes). Several hits of one route in one chunk count once, at the best rank. |
| `gov.retrieval.fusion.search(root, query, limit, refresh=True, reranker=None)` | The whole retrieval: both routes, RRF, one rerank. `{"hits": [...], "facets": {"lexical": {…}, "semantic": {…}}, "reranked": bool}`. A hit is a chunk record with `routes`. Each facet entry has `available`, `facet`, `state`, `reason`. A limit cuts after the rerank; `limit=None` returns the whole reranked merged set. The tests always pass `limit` by name. |
| `gov.retrieval.rerank.rerank(query, candidates, reranker=None)` | `candidates` in the order of the reranker's scores, each with what it came with and `rerank_score`; equal scores keep the order given. A candidate carries `text`. |
| `reranker` | The loader: a function without arguments that returns `score(query, texts) -> [float, …]`, higher is better. It is called at the first rerank and not before, and one rerank calls `score` once with every candidate's text. The default is the pinned Qwen3 reranker (ADR-0002 §2: a separate, pinned process). |

Route and facet names are `lexical` and `semantic`.

**Not fixed by any test: how the default reranker's process is started** (which interpreter, which command). It is
not decided; the engineer keeps it behind the loader. The tests only use the default where it is absent.

## The seven packages of the first batch, and what settled each

| Package | Settled by | What the answer changed in the suite |
|---|---|---|
| **DP-1** the public interface | **DEC-379** (owner): as proposed, name by name | Nothing in the cases. One case added for the last line of the decision: `test_without_sqlite_vec_the_semantic_facet_is_unavailable_and_nothing_raises`. |
| **DP-2** what mean hit@5 is | **DEC-380** (owner): S0b2's own method where it is stated | S0b2 states it (below). The two hit@5 cases were revised: per class and the mean of the ten classes, not per tier; the first five distinct paths, not the first five chunks; every query counts. |
| **DP-3** warm p95 and peak RAM | **DEC-373** (delegated): option (a) for both | Nothing: the two cases measure as the decision states it. |
| **DP-4** a reranker that cannot be loaded | **DEC-374** (delegated): the fused order is kept, the answer says nothing was reranked, nothing raises | The existing case now also holds the order to the fused order, and no longer skips by what the test interpreter can import. One case added for `rerank.rerank`. |
| **DP-5** the manifest | **DEC-374** (delegated): held in the shared store, read through the semantic module; the embedder's revision is the one observed from Ollama's model list | The manifest case now holds the revision to the digest the stand-in's model list reports. Two cases added: another digest in the model list, and a clone given only the store's files. The stand-in's `/api/show` no longer carries a digest. |
| **DP-6** `embedding_policy` | **DEC-381** (owner): a namespace that is `not embedded` never reaches the vectors | Two cases added, in `test_w1_19_embedding_policy.py`. |
| **DP-7** the read of G-17's row | **DEC-382** (owner): accepted; DEC-370 extends to G-17 | Nothing. |

Also read: DEC-383 (the four S0b2 files a worker may read by exact path) and DEC-384 (nothing is installed in
this round).

## hit@5: S0b2 states its method, and the cases follow it (DEC-380)

`~/gov-os-workbench/s0b2/out/RESULTS.md`, read by exact path (DEC-383), states the method in three places:

> **Corpus:** clones of `synthetic/a-dev` and `b-dev`, queries from `synthetic/dev-queryset.yaml` (52 queries, ten classes).

> Scoring: each candidate's top-5 distinct paths per query against `must_cite` / `must_not_cite` in
> `dev-queryset.yaml`. The same matcher is applied to both: the agent's `eval_r*.py` path matcher, not
> `synthetic/scoring/score.py`, so the absolute numbers are not directly comparable with a scorer run

and the table of §1, whose rows are the ten classes with their sizes (`decisions (6)` … `why (5)`, `history (6)`),
and whose last row is

> | **Mean of ten classes** | **85.0** | **76.0** | **0.711** | **0.584** |

So the 85 of the KPI line is the mean of ten per-class percentages. It is not a mean of two tiers.

**The rule in the tests.**

1. Stated by S0b2: the **first five distinct paths** of a query's results are scored (the cases ask for the whole
   reranked list and take the first five distinct paths in rank order).
2. Stated by S0b2: a **percentage per class**, both tiers together, over every query of the class. The sizes in
   S0b2's table add up to 52, so **all 52 queries count**.
3. Stated by S0b2: the **mean of the ten classes' percentages**, against 85 (success 2) and 80 (failure 1).
4. Not stated by S0b2, so DEC-380's option (a): a query is a **hit when one of its `must_cite` paths** is among
   those five paths, by equal path. The matcher itself (`eval_r*.py`) is not one of the four files a worker may
   read. `must_not_cite` does not enter hit@5: S0b2 reports it apart ("Forbidden citations (top-5)").

**One point where the two halves of DEC-380 meet.** Two queries (`DQ-A-21`, class why; `DQ-A-24`, class history)
name no `must_cite` path. Option (a) would leave them out; S0b2's class sizes (`why (5)`, `history (6)`) include
them. The cases follow what S0b2 states: they count in their classes, and with no path to reach they are misses.
This is the stricter reading (it can only lower the mean: at most 96.3 instead of 100). How S0b2 scored those two
is not stated; its figures for the two classes (80.0 and 83.3) are what one miss in each gives.

The code-intelligence report (`~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`) was searched for the scoring
words only; it scores the code classes of the same set by "in top 5" and adds nothing to the method.

## `embedding_policy`: the closed reading (DEC-381)

The schema of W1-08 (`template/governance/kernel/schemas/path-map.schema.json`) requires the field on every
namespace and allows any non-empty text; the loader in `src/gov/config/` checks neither. DEC-289 moved the closed
list to the first ticket that reads the field, which is this one. The cases read it closed:

| The namespace's `embedding_policy` | Read as | In the policy fixture |
|---|---|---|
| `embedded` | embedded | `open/**` |
| `not embedded` | not embedded | `closed/**`, the root files, `governance/**` |
| any other value | not embedded (fail closed) | `odd/**`: `embedded on request`, which a reading by prefix or by substring would take for `embedded` |
| no field | not embedded (fail closed) | `bare/**` |

"Never reaches the vectors" is observed through the interface of DEC-379 and the stand-in endpoint, with no new
public function: no word of such a file is in any request to be embedded, and the file is not a hit of the semantic
route, alone or in the fused list. The lexical index is W1-17's and is not changed: the cases require that the same
files are still found by the lexical route.

- `test_no_text_of_a_namespace_that_is_not_embedded_is_sent_to_be_embedded_or_returned` needs no `sqlite_vec`. It
  runs today. **What it can show today is limited:** without `sqlite_vec` nothing can be embedded, so it holds for
  an implementation that sends nothing at all. It catches an implementation that sends text to the endpoint before
  it knows it can store a vector, and one that drops the files from the lexical route.
- `test_only_the_namespace_that_says_embedded_reaches_the_vectors` needs `sqlite_vec` and skips today. It is the
  whole rule, with its premise (the `embedded` namespace's text is sent and its file is a semantic hit) and one edge:
  files without a vector do not make the index stale.

The sources give no model-free way to see the positive half through the interface of DEC-379: without
`sqlite_vec` the facet is unavailable and the manifest is `None`.

**Not tested: the third value in use.** This repository's own map gives `template/**` the value
`embedded, except vendored code`. No source says which paths are vendored code. Under the closed reading it is an
unknown value, so not embedded. No case uses that value: decision package DP-8 in the designer's report.

## KPI lines and their tests

| KPI line | File | Tests | Today |
|---|---|---|---|
| **Success 1.** sqlite-vec with qwen3-embedding:0.6b, RRF, and one lazily loaded Qwen3-Reranker pass over the merged set [CAP-10.a, CAP-18.a] | `test_w1_19_fusion.py` · `test_w1_19_rerank.py` · `test_w1_19_unavailable.py` · `test_w1_19_embedding_policy.py` · `test_w1_19_semantic_index.py` · `test_w1_19_real_models.py` | all 7 of `test_w1_19_fusion.py` · all 6 of `test_w1_19_rerank.py` · 7 of `test_w1_19_unavailable.py` (all but `test_there_is_no_manifest_before_there_is_an_index`) · both of `test_w1_19_embedding_policy.py` · `test_a_question_no_line_holds_reaches_its_chunk_by_its_vector` · `test_a_semantic_hit_is_a_chunk_record_of_the_shared_store_with_its_parent` · `test_the_vectors_are_in_the_shared_store_beside_the_lexical_index` · `test_no_text_the_secret_filter_refuses_is_embedded_or_returned` · `test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass` · `test_a_changed_file_is_embedded_before_the_next_retrieval_and_stale_vectors_are_reported` · `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` · `test_every_answer_is_one_fused_list_from_both_routes_reranked` | 21 red (the module does not exist); 9 skipped |
| **Success 2.** Dev query set mean hit@5 >= 85 (S0b2 R1 baseline); warm p95 <= 0.5 s | `test_w1_19_real_models.py` | `test_the_dev_query_set_reaches_the_baseline_mean_hit_at_5` · `test_a_warm_query_answers_within_half_a_second_at_p95` | skipped |
| **Success 3.** Model ids and revisions are recorded in the index manifest [CAP-10.a] | `test_w1_19_semantic_index.py` · `test_w1_19_unavailable.py` · `test_w1_19_real_models.py` | `test_the_manifest_records_the_model_ids_and_their_revisions` · `test_the_embedders_revision_is_the_one_the_model_list_reports_not_a_constant` · `test_the_manifest_is_held_in_the_shared_store_and_read_without_ollama` · `test_there_is_no_manifest_before_there_is_an_index` · `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` | 1 red; 4 skipped |
| **Failure 1.** Mean hit@5 falls below 80 | `test_w1_19_real_models.py` | `test_mean_hit_at_5_is_not_below_the_failure_line` | skipped |
| **Failure 2.** Peak RAM of the rerank process exceeds 2.5 GB | `test_w1_19_real_models.py` | `test_the_rerank_process_stays_within_two_and_a_half_gigabytes` | skipped |

**Count.** KPI lines with tests: 5 of 5 (3 success, 2 failure). Success 2 and both failure lines have no test
that can run on this machine today; success 1 and 3 have model-free tests that can. Of success 3, the only
model-free case is "no manifest before there is an index": that a revision is recorded has never been observed.

| Covers id | Tests |
|---|---|
| **CAP-10.a** paraphrase retrieval with the pinned embedder | `test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it` (real model) · `test_the_dev_query_set_reaches_the_baseline_mean_hit_at_5` (real models) · `test_a_question_no_line_holds_reaches_its_chunk_by_its_vector`, the three manifest cases and `test_only_the_namespace_that_says_embedded_reaches_the_vectors` (stand-in endpoint) · `test_the_semantic_route_says_unavailable_when_ollama_is_absent`, `test_without_sqlite_vec_the_semantic_facet_is_unavailable_and_nothing_raises` and `test_no_text_of_a_namespace_that_is_not_embedded_is_sent_to_be_embedded_or_returned` (run now) |
| **CAP-18.a** fusion (RRF), dedup by chunk hash, one rerank | all of `test_w1_19_fusion.py` and `test_w1_19_rerank.py` · `test_without_ollama_the_fused_list_is_the_lexical_routes_reranked_in_one_pass` · `test_a_limit_cuts_the_list_after_the_rerank_not_before` · `test_a_reranker_that_cannot_be_loaded_leaves_the_fused_list_and_says_so` (all run now) · `test_both_routes_are_fused_into_one_list_and_reranked_in_one_pass` (stand-in endpoint). The multi-route router with the graph route, and the bundle, are W1-21. |

## Which tests wait for which install

A `needs` marker names what a case needs; the case skips, with the reason, when this machine lacks it. Nothing is
installed, started or downloaded to decide a skip: it is `shutil.which`, `importlib.util.find_spec` and three
exact paths. Nothing is installed in this round (DEC-384).

| Needs | Decided by | Cases | Today |
|---|---|---|---|
| nothing | — | 7 fusion, 6 rerank, `test_a_search_that_may_not_write_…`, `test_there_is_no_manifest_…` (15) | red |
| `gitleaks` | on `PATH` (present here) | the other 6 of `test_w1_19_unavailable.py`, `test_no_text_of_a_namespace_that_is_not_embedded_…`, the premise (8) | 7 red, the premise passes |
| `gitleaks`, `sqlite_vec` (IP-1) | `sqlite_vec` importable by the Python that runs pytest | the 9 stand-in cases of `test_w1_19_semantic_index.py`, `test_only_the_namespace_that_says_embedded_…` (10) | skipped |
| the above and `ollama` (IP-2, IP-3) | an executable at `GOV_OLLAMA_BIN`, on `PATH` or at `~/.local/ollama/bin/ollama`, and the file `manifests/registry.ollama.ai/library/qwen3-embedding/0.6b` under `$OLLAMA_MODELS` or `~/.ollama/models` | `test_the_pinned_embedder_reaches_a_section_…` (1), marked `local_only` | skipped |
| the above and `reranker` (IP-4) | the folder `models--Qwen--Qwen3-Reranker-0.6B/snapshots/e61197ed…5473` in the Hugging Face cache (`HF_HUB_CACHE`, `HF_HOME` or `~/.cache/huggingface/hub`) | the 5 dev-tier cases, marked `local_only`; they also skip when the dev tiers or the query set are absent | skipped |

So **22 cases need no install** (15 + 7), and **16 wait**: 10 for `sqlite_vec` alone, 1 more for Ollama with the
embedding model, 5 more for the reranker as well.

The `needs` marker sees the reranker's snapshot folder and not its process: where the pinned process and its
libraries live is not decided. If the folder is there and the process cannot be started, the five cases fail and
do not skip.

**Three cases use an absent thing on purpose, and are built to stay valid after the installs:**

- `test_without_sqlite_vec_…` puts a module named `sqlite_vec` that raises `ImportError` first on `PYTHONPATH`, so
  the import fails whatever the machine has.
- `test_a_reranker_that_cannot_be_loaded_…` and `test_reranking_with_no_reranker_that_can_be_loaded_…` pass no
  `reranker` and run in the scratch environment: an empty `HOME`, no Hugging Face cache, the libraries held
  offline. Today the default reranker is absent on this machine in any environment. **After IP-4 their premise must
  be checked again:** if the decided way to start the reranker's process finds it without `HOME` and without the
  Hugging Face cache, the default is no longer absent there and the two cases need another way to make it so. That
  belongs to the open decision on how the process is started.

**What this machine has.** `ollama` is not on `PATH` and `sqlite_vec`, `sentence_transformers`, `torch` and
`transformers` cannot be imported by `/usr/bin/python3`. The first batch found, by exact path only,
`~/.local/ollama/bin/ollama`, the model file for `qwen3-embedding:0.6b` under `~/.ollama/models`, and the
reranker's pinned snapshot folder in `~/.cache/huggingface/hub`. Nothing was run, so their versions and digests are
unverified (DEC-384 has the orchestrator verify them against the recorded hashes).

## How the tests decide

- **Every project is a temporary git repository** (DEC-322): a clone of a fixture repository with its own path
  map, a copy of `template/.gitleaks.toml`, and its own `.gov-runtime/store.db`. No test builds an index in this
  worktree, and no test copies this repository or a folder of it.
- **Two environments.** Model-free cases get an environment built from scratch: an empty `HOME`, `PATH` without
  `ollama`, `OLLAMA_HOST` on a loopback port nothing listens on, and the Hugging Face libraries held offline.
  That is "Ollama absent". The real-model cases get this machine's own environment, also held offline.
- **The stand-in reranker** lives in the driver process. Its loader counts each load; its scorer records each
  pass and scores a text by how often it holds the word `quartz`. Only the file the lexical route lists last holds
  that word, so a list that is not reranked, or reranked before the routes are merged, has another first entry.
- **The stand-in Ollama endpoint** answers `GET /api/version`, `GET /api/tags` (the model list: the model with
  its digest), `POST /api/show` (no digest, as with the daemon), `POST /api/embed` and `POST /api/embeddings`,
  with 1024 numbers computed from the words of the text. It records every request, which is how "no refused text
  was sent to be embedded" is read. Its digest begins with the pin unless a case gives it another. The scratch
  environment has no `ollama` executable, so the model list of the endpoint is the only place a revision can be
  observed (DEC-374).
- **The fixture corpus** is eight tracked files. Three hold the exact phrase `amber lantern protocol`, one of them
  on two lines of one chunk. Two more files are tracked and must never reach an index: one in a namespace the map
  classes as product data, one that holds a planted canary (built at run time from parts). All its namespaces say
  `embedded`.
- **The policy fixture** (DEC-381) is a second repository: four governance namespaces that differ only in
  `embedding_policy`, one file in each. Each file holds one word no other file and no question holds, and all four
  hold the phrase `pewter whistle signal`.
- **Lazily loaded** is read three ways: the loader is not called before the first rerank; `torch`, `transformers`
  and `sentence_transformers` are not in `sys.modules` after the three modules are imported or after a fusion;
  and reranking nothing loads nothing.
- **The fused order** (DEC-374) is what `fusion.rrf` returns for the lexical route's own hits; the case compares
  the chunk ids of `fusion.search` with it, one after the other.
- **hit@5**: the section above.
- **Warm p95** (DEC-373): per tier, one process builds the index, asks three warm-up questions that are not
  in the set, then asks each dev query once. Each call is timed inside that process. p95 is the nearest-rank 95th
  percentile over the 52 timed calls, against 0.5 s.
- **Peak RAM** (DEC-373): while that process runs, a thread reads `VmHWM` of the process and of every
  process descended from it, every 50 ms, leaving out any process named `ollama` and its children. The largest
  single process must stay at or under 2.5 × 10⁹ bytes. A reranker that detaches from the process tree is not
  seen: a residual the decision records.
- **The tiers** are cloned into a temporary directory and adopted with a map that classes everything as
  governance memory and as `embedded`, as the W1-17 suite does.

## Readings the designer made, where a decision leaves room

Each is the stricter or the plainer reading; none is a new public name.

- **`rerank.rerank` with no reranker** returns the candidates it was given, in the order given, each with what it
  came with (DEC-379: it returns the candidates and does not raise; DEC-374: nothing is reranked and the order is
  kept). No candidate may carry a number as `rerank_score`, because nothing was scored. Whether the key is left
  out or is `None` is open, and the case accepts both.
- **`semantic.manifest` without `sqlite_vec`** on a project that has never had vectors is `None` (DEC-379:
  `None` without an index).
- **A file of a namespace that is not embedded is still a lexical hit**, in `lexical.search` and in the fused list.
- **Another digest in the model list is recorded, not refused.** A mismatched model failing closed is CAP-19
  (Wave 2).
- **The reranker's revision** in the manifest is the pin of ADR-0002: DEC-374 names only the embedder's as
  observed.

## What was read

- In the tree, first batch: the ticket, `contract.yaml` (CAP-10, CAP-18), the WBS rules, the decisions of that
  time, ADR-0002, the tool registry, the bootstrap residuals of W1-15, W1-17 and W1-18, the retrieval, secrets and
  store code, and the W1-16, W1-17 and W1-18 suites.
- In the tree, second batch: the ticket, CAP-10 and CAP-18, the WBS rules, the decisions named in this file (each
  in full), the lexical index, the Ollama lifecycle module, the secret filter's namespace code, the config loader,
  the path-map schema of W1-08 and this repository's path map (its namespaces). ADR-0002 and the tool registry were
  not read again; the chunking and store-loader code was not read in this batch.
- `~/gov-os-workbench/s0b2/out/RESULTS.md`, by exact path (DEC-380, DEC-383): the head and §1 in full, and the
  lines of the rest that a search of that one file for the scoring words returned.
- `~/gov-os-workbench/s0b2/sandbox/_reports/codeintel.md`, by exact path (DEC-383): only the lines a search of
  that one file for the scoring words returned.
- `~/gov-os-workbench/s0b2/out/GLUE_REQUIREMENTS.md` (first batch): the G-20 row, and by a mistake of the
  designer the G-17 row; DEC-382 accepts that read.
- `$GOV_DEV_TIERS/dev-queryset.yaml`, by exact path: the classes, their sizes per tier, and the two queries
  without a `must_cite` path. No folder of the workbench was listed.

## Open after the second batch

- **DP-8** (new, in the designer's report in full): how `embedded, except vendored code` is read. No case depends
  on it and it does not affect the model-free build.
- **How the default reranker's process is started**: not decided, fixed by no test (see above).

## Not tested, on purpose

- The quality of the stand-in vectors; anything about the graph route, the bundle, paging or `gov retrieve` (W1-21).
- The embedding model's registry row (DEC-195; the registry is outside the ticket's paths).
- Whether the reranker stays loaded between retrievals, and the idle unload (DEC-261).
- A mismatched or unpinned model failing closed (CAP-19, Wave 2).
- The RRF constant's default: the cases that compare scores pass `k=60`.
- Spellings of `embedding_policy` that differ from the two known values only by case or spacing, and a path that
  matches two namespaces with different policies.
