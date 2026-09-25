# Semantic route: decision, pins and procedures (BR-AR-0001)

| Field | Value |
|---|---|
| Class | `ORCHESTRATION_RECORD` (design). The pinned model is **provisional**. This is not the final retrieval model, and it is not a Phase-3 selection. |
| Rule applied | Launcher, "SEMANTIC/VECTOR BOOTSTRAP RULE"; OD-P2-10 §5 ("semantic/vector retrieval on the existing replaceable architecture where available"); BR-HO-0001 §2.2 item 6 |
| Evidence | SO-02, SO-07, SO-08, SO-09, SO-10, SO-11, SO-18, SO-21 (`ARCHITECTURE/spike-outputs/`), with commands and hashes in `AGENT_RUNS/BR-AR-0001.checkpoint.yaml` |

## 1. Decision: no operational semantic route exists, so one provisional model is provisioned

**What exists, measured (SO-02):**

* **The D-0006 replaceable architecture exists and runs.** That is the `gov-capability/1` protocol
  (`capabilities/PROTOCOL.md`, `capabilities/python/govos_capabilities/plugin.py`). Its tree is identical at the bridge
  base `6e7a2a3` and at the frozen product `3c880d8` (tree `bfac2954`).
* **Its only neural embedder is not operational.** `embed_sentence_transformers.py` answers
  `{"ok": false, "error": {"code": "MODEL_UNAVAILABLE", …"No module named 'sentence_transformers'"}}`. It fails
  closed, as designed. No torch, onnxruntime, sentence-transformers, fastembed, tokenizers, model2vec or transformers
  is importable.
* **The hashed-ngram plugin runs, but is not semantic.** Its own docstring says: *"This is NOT a neural embedding
  model. It is a reproducible lexical-semantic approximation"* (`embedder_hashed_ngram.py:1-5`). D-0006 records that no
  paraphrase-capable model ships in the kernel.
* **The product's in-core route is not invocable** without adopting this repository (`ARCHITECTURE.md` §0.2).

**The existing architecture is used as the adapter.** The bridge's embedder **is a `gov-capability/1` `embed`
plugin**. It uses the request/response shape of `plugin.py`, the `model`/`runtime` declarations that `PROTOCOL.md`
requires of embed plugins, and the fail-closed codes of `embed_sentence_transformers.py`. It is an **ADAPT** of that
plugin, with the sentence-transformers backend replaced by ONNX Runtime. The ADAPT is applied to a copy inside the
domain. The bridge invokes it directly as a subprocess. It does not register it with `gov plugins register`, because
that needs an adopted project and Human Decision Gates. On promotion, the same file registers the governed way
(`ARCHITECTURE.md` §9, §10).

## 2. The one provisional model, pinned

| Pin | Value | Evidence |
|---|---|---|
| Model id | `BAAI/bge-small-en-v1.5` | SO-08 (HF API) |
| Revision | `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (repository commit; `lastModified 2024-02-22T03:36:23Z`) | SO-08 |
| Licence | **MIT** (model card `license: mit`; API tag `license:mit`) | SO-08, SO-18 |
| Artefact `onnx/model.onnx` | sha256 `828e1496d7fabb79cfa4dcd84fa38625c0d3d21da474a00f08db0f559940cf35`, 133,093,490 bytes, **published in the pinned revision**, so there is no local conversion step | SO-08, SO-18 |
| `tokenizer.json` | sha256 `d241a60d5e8f04cc1b2b3e9ef7a4921b27bf526d9f6050ab90f9267a1f9e5c66` | SO-18 |
| `config.json` | sha256 `094f8e891b932f2000c92cfc663bac4c62069f5d8af5b5278c4306aef3084750` (BERT; hidden 384; 12 layers; 512 positions; vocabulary 30,522) | SO-08, SO-18 |
| `tokenizer_config.json`, `special_tokens_map.json` | `9261e7d7…2ab3`, `b6d346be…7ee3` | SO-18 |
| `1_Pooling/config.json` | sha256 `d1caf60c96f5fba2157c0c26b76d80818fad6cf0b8eb5e73ec372ff9818eba5c`: `pooling_mode_cls_token: true` | SO-09, SO-18 |
| Dimensions | **384** | SO-09 (`"dim": 384`) |
| Pooling / normalisation | CLS token → L2-normalised | SO-09 |
| Max tokens | 512 (truncation on). A ≤1,200-char chunk fits without truncation | config.json |
| Query mode | the query prefix `Represent this sentence for searching relevant passages: `; passages carry no prefix | model card convention for bge-*-en-v1.5 |
| Runtime / provider | `onnxruntime 1.30.0`, `CPUExecutionProvider`; `tokenizers 0.23.2`; `numpy 2.5.3`; Python 3.12.3 on Linux x86_64 (WSL2, glibc 2.39) | SO-07, SO-18 |
| Session options | `intra_op_num_threads` = any (measured bitwise-identical at 4 and 16); `inter_op_num_threads 1`; `ORT_SEQUENTIAL`; `use_deterministic_compute True` | SO-09 |
| Batching | batch 1. It is fastest (24.9 chunks/s against 15.5 at batch 32), and results are **identical** at any batch composition | SO-10 |
| Stored vector | `float32` little-endian, 1,536 bytes per chunk | — |

**Pin id** (recorded in every build manifest):
`sha256(model_id ‖ revision ‖ sorted artefact sha256s ‖ runtime versions ‖ session options ‖ pooling ‖ query prefix)`.
Changing any of these changes the pin id, which invalidates the whole semantic layer. The index is never
mixed-embedder.

### Why this model: selection without a bake-off

The launcher permits exactly one provisional model and forbids a bake-off. No second model was run or scored. The
choice rests on published facts and on feasibility measured on this one model:

* **Current and small.** It is the smallest English member of the current BGE v1.5 family (BGE-family models are
  permitted, not mandated): 33M parameters, 384-d vectors, which keep brute-force search trivial (about 61 MB for 40k
  chunks).
* **Fit to the chunking.** A 512-token window holds the 1,200-char chunks that `MEMORY_POLICY.chunking.max_chars`
  specifies. The example model in the product's own plugin docstring, `all-MiniLM-L6-v2`, is older (2021) and uses a
  256-token window, which would truncate those chunks. That is a reason from documentation, not a measurement.
* **No derived artefact.** An ONNX file is published inside the pinned revision, so the hash of the file that runs is
  the hash of the file downloaded. No local export or quantisation step can drift.
* **CPU-deterministic, measured.** Three separate runs over the same 3,000 real corpus chunks produced one vector
  digest (`4c138e5a…`): two at 16 threads, one at 4. Batch-1, batch-32 and length-sorted batch-32 over 600 chunks gave
  `max_abs_diff 0.0` (SO-09, SO-10). Incremental builds therefore reproduce full builds bit for bit.
* **Licence.** MIT for the model; MIT for onnxruntime; Apache-2.0 for tokenizers (SO-18).
* **Not chosen, and why, without measurement.** Static embedding models (for example model2vec) are far faster, but
  they are distilled approximations of models like this one, so a provisional model that already meets the cost
  envelope has no need of them. They remain Phase-3 candidates behind the same adapter. GPU inference (an RTX 5070 Ti
  is present) was not used, because GPU kernels do not give the bitwise CPU determinism the rebuild guarantee depends
  on.

**Smoke check, not a benchmark** (SO-09). Three natural-language questions over the 3,000-chunk sample returned
topically correct passages:

* "which rule wins when two path rules match the same file" → `framework/policies/POLICY_PRECEDENCE.yaml` among the
  top 3;
* "how is a checkpoint made mandatory for a worker" → `framework/policies/CHECKPOINT_POLICY.yaml` at ranks 1–2.

This shows that the pipeline works. It says nothing about recall, and recall is Phase 3's to measure.

## 3. What gets embedded, and what that costs

`config/embed-profile.yaml` embeds prose, structured records and code: `md, txt, html, yaml, yml, toml, rs, py, sh`,
and `json` up to 64 KiB. It does **not** embed machine output: `out, log, shimlog, stderr, diff, patch, tsv, jsonl,
summary`, or larger `json`. Those remain fully covered by the exact and lexical routes (`ARCHITECTURE.md` §1.1
`L-MACHINE-OUTPUT`).

| Quantity | Value | Basis |
|---|---|---|
| Embeddable blobs and bytes, union of the three named refs | **3,021 blobs, 40.8 MB** (lexical-only: 2,766 blobs, 36.5 MB) | **SO-21, measured** |
| Chunks to embed | **40,035**, line-aligned, ≤1,200 chars (lexical-only chunks: 38,023) | **SO-21, measured** |
| Throughput | 24.9 chunks/s (1 process × 16 threads, batch 1); 27.7 chunks/s (5 processes × 4 threads) under load 10–14 from other sessions | SO-10, SO-11 |
| **Full semantic build, union of the three named refs** | **≈ 27 min CPU** (40,035 ÷ 24.9/s) | SO-21 × SO-10 |
| Additional named refs | already inside the union figure, because blobs are deduped (one ref alone is about 97% of it) | SO-04 |
| History refs | **not embedded** (`canonical-view.yaml`: `layers: [exact, lexical, records, graph]`) | cost rule |
| Incremental build | only new chunk texts: seconds for an ordinary commit | §5 |
| Query | one embedding (~0.04 s) + brute-force cosine over ≈40k × 384 (milliseconds) | SO-10 |

## 4. Index manifest and schema

**Store table:** `vector(chunk_id TEXT PRIMARY KEY, text_sha256 TEXT, pin_id TEXT, dim INT, vec BLOB)`. Here `vec` is
384 × `float32` LE.

**The manifest's `semantic` block:**

```yaml
semantic:
  adapter: {protocol: gov-capability/1, capability: embed, plugin_path: govbridge/semantic/adapters/onnx_embed.py,
            plugin_blob: <git blob id at the build commit>}
  model: {id: BAAI/bge-small-en-v1.5, revision: 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a,
          artefacts: {onnx/model.onnx: 828e1496…, tokenizer.json: d241a60d…, config.json: 094f8e89…,
                      tokenizer_config.json: 9261e7d7…, special_tokens_map.json: b6d346be…, 1_Pooling/config.json: d1caf60c…}}
  runtime: {onnxruntime: 1.30.0, tokenizers: 0.23.2, numpy: 2.5.3, python: 3.12.3, provider: CPUExecutionProvider,
            session: {inter_op: 1, execution_mode: sequential, deterministic_compute: true}}
  encoding: {pooling: cls, normalize: l2, max_tokens: 512, query_prefix: "Represent this sentence for searching relevant passages: ", dtype: float32le}
  embed_profile_sha256: <sha256 of config/embed-profile.yaml>
  pin_id: <sha256 as defined in section 2>
  vectors: {count: <n>, digest: <sha256 over sorted (chunk_id, sha256(vec))>}
```

## 5. Rebuild, reindex and replacement procedures

1. **Bootstrap** (`bootstrap/bootstrap.sh`, idempotent, and it writes nothing in Git):
   * create `$HOME/.cache/gov-bridge/venv` with `python3 -m venv`;
   * `pip install --require-hashes --no-deps -r config/requirements.lock`. This installs every wheel SO-07 resolved,
     with its sha256, plus pytest;
   * download each artefact in `config/model-pin.yaml` from
     `https://huggingface.co/<model_id>/resolve/<revision>/<path>` into
     `$HOME/.cache/gov-bridge/models/<model>/<revision>/<path>`;
   * **verify each sha256, and on any mismatch stop and download nothing further**;
   * finish by printing a one-line environment identity: python, package versions and the pin id.
2. **Full semantic reindex:** `python -m govbridge index rebuild --layer semantic`. It embeds every eligible chunk
   under the current pin. **Acceptance:** two from-clean rebuilds give an equal `vectors.digest`.
3. **Incremental:** runs as part of `index update`. Only chunks whose `text_sha256` has no vector under the current
   pin id are embedded. All others are reused.
4. **Replacement.** This is the Phase-3 path; the launcher requires that a replacement need no redesign:
   1. add a new `gov-capability/1` embed adapter, or change `config/model-pin.yaml`;
   2. `index rebuild --layer semantic --pin <new>` builds a **parallel** vector set under the new pin id, and the old
      set is untouched;
   3. run the held-out retrieval benchmark (Recall@K, MRR, stale-hit and superseded-hit rates, latency) against
      `MEMORY_POLICY.regression` thresholds (`min_recall_at_k 0.8`, `min_mrr 0.5`, `max_stale_hit_rate 0.0`,
      `max_superseded_hit_rate 0.0`);
   4. switch the active pin in config with a governed commit;
   5. garbage-collect the old pin's vectors.
   
   Nothing outside the semantic layer changes. The authority invariant (`ARCHITECTURE.md` §5.3) does not depend on
   which embedder is active.
5. **Failure semantics** (D-0005 for embed): a missing, mis-pinned or failing embedder is a **typed error**
   (`MODEL_UNAVAILABLE`, `DIMENSION_MISMATCH`, `PIN_MISMATCH`). The build marks the semantic layer `UNAVAILABLE`, and
   packets record that the semantic route did not run. **The hashed-ngram embedder is never substituted.** It is used
   only as a deterministic test double in unit tests. Section A is unaffected (W10).
