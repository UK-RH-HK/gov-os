# ACT-RERANK-TRIAL-2: the downloads of gte-reranker-modernbert-base and zerank-1-small (DEC-1081 (3))

For the owner's operator, in a plain terminal (downloads are the operator's, P-ACT-SPLIT). Prepared by the CTO,
2026-11-06. **No install and no package:** the trial venv of ACT-RERANK-TRIAL-1 already has what both models need.
Nothing touches the live venv, the pins, the live HF cache (`~/.cache/huggingface`) or the live reranker.

## 1. The two models, confirmed
| | gte-reranker-modernbert-base | zerank-1-small |
|---|---|---|
| repository | `Alibaba-NLP/gte-reranker-modernbert-base` | `zeroentropy/zerank-1-small-reranker` (renamed from `zerank-1-small`; the old name redirects) |
| licence | **Apache-2.0** (card metadata) | **Apache-2.0** (card and `LICENSE` in the repository). Its 4B sibling `zerank-1` is not; it is not used |
| pinned revision | `f7481e6055501a30fb19d090657df9ec1f79ab2c` (2025-07-04) | `a65fd51c450e9b47fdddab98e31166ecad21af8d` (2026-07-24) |
| architecture | ModernBertForSequenceClassification, 149 M; one score per pair; inputs up to 8,192 tokens | Qwen3ForCausalLM, 1.7 B (28 layers, hidden 2,048, 16 heads, 8 KV); up to 32k tokens. The card's "base Qwen3-4B" is a slip on the card: the config is Qwen3-1.7B's shape |
| download (dry run from this machine) | 6 files, **602 MB** (`model.safetensors` 598,436,708 B, F32); the ONNX copies (1.9 GB) left out | 11 files, **3.5 GB** (`model.safetensors` 3,441,185,608 B, bf16); its code file left out (below) |
| input template | a plain cross-encoder pair `(query, passage)`; no instruction or prefix | the query as the **system** message, the passage as the **user** message, through the model's own chat template with the generation prompt (no empty think block); query cut at 2,000 and passage at 10,000 characters |
| the score | the model's one logit (sentence-transformers applies a sigmoid: same order) | the logit of the token `Yes` at the last real position, divided by 5, through a sigmoid |
| what it needs | transformers ≥ 4.48 (the trial venv has 5.18) and sentence-transformers (6.1): **the trial service loads it as it is** | the same libraries: **a trial-only loader** in the trial service's worker (the CTO's tools lane, reviewed; no `src/` change), as ACT-RERANK-TRIAL-1 added the 8-bit switch |

**Why zerank's own code is not used:** the repository's `modeling_zeranker.py` asks for `trust_remote_code=True`,
replaces sentence-transformers' `CrossEncoder.predict` and `.to` for the whole process, and loads the weights by
their hub name, so it would reach the network at run time. It does no subprocess, `eval` or file write. The
trial loader reproduces its template and score in our own code instead. It loads `Qwen3ForCausalLM` from the local
snapshot with `trust_remote_code=False` (the config's `model_type` is `qwen3`, so the library's own class serves it)
and takes the `Yes` logit at each pair's last real position only, so no vocabulary-wide logits are kept. The code
file is not downloaded, so nothing can run it.

**The GPU fit (est.; measured in the window):** gte about 600 MiB of weights in F32, far under the budget. zerank
about 3,280 MiB of weights in bf16, about 340 MiB more than mxbai (2,944), with a smaller MLP (6,144 against 8,960).
So it fits beside the base under the trial's release after each request, as mxbai did. One reranker on the GPU at a
time, as ever.

## 2. The operator's steps (one terminal, about 5 minutes on this line)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
A=governance/project/orchestration/packages/ACT-RERANK-TRIAL-2/act.sh
bash $A check      # every line ok; marks the ACT in progress; records the live HF cache's list and the trial venv's packages
bash $A download   # the two pinned downloads into ~/.cache/gov-os-trial/hf (the trial's own HF_HOME; no token read)
bash $A verify     # every line ok: the two sizes, 6 and 11 files, no .py, no ONNX, the live HF cache and the trial venv unchanged
```
`verify` removes the in-progress mark when every line is ok. On a STOP, run `bash $A undo` and tell the CTO.

## 3. Undo
`bash $A undo` removes the two model folders (and their hub locks) and the mark, nothing else. The mxbai and 4B
downloads stay, as DEC-1079 kept them.

## 4. The rehearsal (DEC-1057)
`.gov-runtime/scratch/orchestrator/drafts/rerank-trial2/rehearse.sh`: `act.sh`'s own steps on stand-in folders (only
the paths substituted), the real trial venv read-only, the downloads as dry runs. **REHEARSAL PASS, 15 of 15**
(2026-11-06, run1):
- `check` passes and marks; run again it stops (an ACT in progress);
- the dry runs list 6 files, 602.1 MB, and 11 files, 3.5 GB, and write no model folder;
- `verify` passes on a stand-in download of the real names and sizes (sparse files) and removes the mark;
- it stops on a planted `modeling_zeranker.py`, and on a short weights file;
- `undo` leaves nothing of either model;
- the real trial cache, the real live HF cache and the real trial venv are unchanged, and no real mark was written.

**Not rehearsed:** the two downloads themselves (4.1 GB).

## 5. After it (the CTO; nothing adopted or installed in the product, DEC-1081 (3))
1. The zerank trial loader in the trial worker, with a test against the published template (a planted tokenizer,
   no GPU), reviewed. The harness keeps one score cache per model, so every replay reuses the scores.
2. **The grid declared and committed before any run:** each model alone; gte for code questions and a Qwen model for
   the rest; cascades; two merged on normalised scores; all on the fixed pipeline after L3, judged by the rule with
   McNemar.
3. **One quiet GPU window** under the safety rules: the 0.6B, the 4B, gte and zerank each score every kept candidate
   list of the 138 once. Then the replays, at no GPU cost.
4. A winner's speed and GPU memory measured in a real window, then to the owner. At the decision point the best
   combination goes onto the fresh 80 once, beside the 0.6B.

**Basis:** question 1 (the reranker chosen from every candidate that fits) and question 4 (the downloads only, no
package, and scores computed once).
