# E0B-READINESS: the score-once harness on re-pin window 4's code (E0-DECLARATION §E0b, plan steps 1-3)

By the research agent, 2026-11-07, for the CTO's review. Nothing here was run against a set: no E0b, no GPU job, no
question read. Not committed (the CTO commits after review).

## 1. What changed
The folder's `rx.py` (+201 / -17 lines against its L6 form, 72,704 → 84,079 bytes), plus `seed_scores.py`,
`test_rx_e0b.py`, `smoke_w4.py` and `run_harness_tests.sh` (new), and small edits to `so_measure.sh`, `replay.sh`
and `test_rx_l5.py`.

1. **Searches take window 4's `depth` / `top_k` (fault 1).**
   - `_phrased_rx(search, root, asked, key, cut=None, depth=0)` is window 4's `retrieve._phrased` signature
     (`retrieve.py:238`). It passes `depth` on, so the product gives each search `top_k=depth` (`:243-244`).
   - The harness's searches `_lex` / `_sem(root, query, refresh=True, top_k=None)` honour it. Each phrasing's search
     gets `top_k`, `_sem`'s own phrasing cut uses `top_k or TOP_K`, and the stored answer is keyed by the depth used
     (`top_k or TOP_K`).
   - **The older form still works, and is still needed.** That is no `depth`, searches without `top_k`, as on the g1
     clone (`e884675b465e`). `top_k` is passed only when set. The g1-based tests (`test_rx_combine`, `_l5`, `_l6`,
     `_live`) and any replay of the g1 caches use it. A `depth` given to a `_phrased` that takes none stops the run.
   - Before: window 4's `retrieve` fails at once, `TypeError: _phrased_rx() got an unexpected keyword argument
     'depth'` (`smoke_w4.py` on the pre-change file, rebuilt byte-exact).
2. **Route answers keyed by their store (fault 2).**
   - Every stored route answer (lex, sem, chunks, start ids, closure, code, records, edges, semrank) is keyed by the
     store's resolved root and its fingerprints head (`.gov-runtime/store.db` `fingerprints.head`).
   - **Both:**
     - the cache records the store it was filled for (meta `store`), and a run on another store (a new clone, or the
       same clone rebuilt at another commit) is **refused** at its first route call;
     - an answer stored under another store's key is **never returned**, because its key differs. This holds even
       if the claim is removed.
   - A root with no store file stores nothing. A store with no fingerprints head is refused.
   - Scores stay keyed by (model, question, text). A pointwise cross-encoder's score of a text belongs to no store,
     and that is what lets the kept q06 scores seed E0b.
   - **A cache filled before this change** (route answers, no meta `memo_keys`) is refused. `GOV_RX_LEGACY_STORE=1`
     keys as before, for replaying the grid's and extend window's g1 caches on g1 only. One cache never holds both
     key forms.
3. **Replay mode can score missing texts live (fault 3).**
   - `GOV_RX_LIVE_MISSING=1`, in a replay (`GOV_RX_COMBINE`) only, scores a text that no kept cache holds:
     - on the live service, through the product's own client (`rr.default_reranker`): never a start, never a
       private reranker, never a fallback;
     - only for a rule model that is the live service's model at this gov (`rr.MODEL@rr.REVISION`, today
       `Qwen/Qwen3-Reranker-0.6B@e61197ed…`).
   - Refusals: the flag without a replay; a rule with no live model; a missing text of any other model, named.
   - Each request goes after `_gpu_wait`, and a request the service does not score stops the run with nothing kept.
   - Scores are written to the replay's own `GOV_RX_CACHE`, never to a kept cache (those are opened read-only). A
     later replay reads that own cache after the kept caches.
   - **Counts:** `LIVEMISS<TAB>n<TAB>model<TAB>texts` and `OWNCACHE<TAB>n<TAB>model` per pass in `GOV_RX_LOG`.
     `so_measure.sh`'s summary line now ends `texts scored live (GOV_RX_LIVE_MISSING) N; texts read from the
     replay's own cache M`.
   - **Default unchanged:** a missing text stops the run, in any call.
4. **The product's pool (plan step 2), handled in code; `README.md` says the same.**
   - **Refused:** a variant with keys of its own (CUSTOM, e.g. v456) on a clone whose `retrieval.yaml` has the
     `pool:` on. The two would stack: the product's route depth, rerank of 40, cap and nested drop on top of the
     harness's own.
   - **`GOV_RX_POOL_OFF=1`** gives `retrieve` the pool off in this process. The file is still read and validated,
     the clone and its store stay unchanged, and a `POOL\toff\t<settings>` line is written to `GOV_RX_LOG`.
   - `{}` (the shipped path) keeps the clone's pool. Checked by `smoke_w4.py`: the product's pool reranks 40 once,
     with route depth 60 reaching the real keyword index.
   - **Why a switch, not an edit to the clone:** E0b can then use E0's own clone and store (`w4-e0/repo`,
     `c00d525fd420`). It needs no second clone, no edited tracked file and no rebuild.
5. **`seed_scores.py`** builds a new cache from kept caches' scores only:
   - every source must mark the same model;
   - no route answer is copied;
   - it is marked `memo_keys: store`;
   - a key two sources score differently keeps the first source's value and is counted as a conflict.
6. **`replay.sh`** now removes only the model marks from its copy, not the cache's key form. Its comment says the
   g1 replays need `GOV_RX_LEGACY_STORE=1`. `test_rx_l5.py`'s mirror of that copy is changed the same way, and its
   check 2b lists E0b's 17 replaced lines, each named.

## 2. Tests (CPU, stub scorers only; `bash tools/heavy_slot.sh bash <folder>/run_harness_tests.sh`)
| file | before | after |
|---|---|---|
| test_rx_combine.py | 23/23 | 23/23 |
| test_rx_l5.py | 48/48 | 48/48 (2b and 5 adjusted, see 1.6) |
| test_rx_l6.py | 4/4 | 4/4 |
| test_rx_live.py | 26/26 | 26/26 |
| test_live_tools.py | 18/18 | 18/18 |
| test_live_window.py | 26/26 | 26/26 |
| test_yes_logit.py | not run by system python3 (no torch) | 16/16 (`CUDA_VISIBLE_DEVICES=-1`, the reranker venv's python; file untouched) |
| **test_rx_e0b.py** (new, pytest, run by the pin's python) | — | **12/12** |

`test_rx_e0b.py` covers:
- **1a-1c:** depth passed as `top_k`, honoured and keyed by depth; `retrieve.py:324`'s call end to end; the old form.
- **2a-2c:** keyed by root and head; another store refused, and never reused once the claim is removed; no store or
  no head; the legacy cache and its switch.
- **3a-3d:** strict by default; the flag scores only the missing text, counted, in the own cache; a strict re-run
  reads it from there; refusals; a failing service keeps nothing.
- **4:** pool refused under v456, off with the switch, kept for `{}`, and an invalid file still refused.
- **5:** the seed.

**Smoke** (`smoke_w4.py`): the real window-4 `retrieve` on `w4-e0/repo`, read only, with the meaning route, the
cosine and the scorer stubbed:
- **v456 + `rq` + `lift_norm` + `GOV_RX_POOL_OFF=1`:** 19 items, no pool block, 40 scored per call, the
  continuation 16 items, store key `[w4-e0/repo, c00d525fd420…]`;
- **`{}`:** the product's pool, 40 reranked once, the continuation carried, depth 60 to both searches.

The clone's `src/gov/retrieval` is identical to the pin's (`diff -rq`). It imports on system python3, so_measure.sh's
form.

## 3. How to run E0b (the CTO's runs; one light GPU job, then none)
Preconditions:
- E0 is finished.
- Nothing rebuilds `w4-e0/repo`'s store between the runs. A rebuild changes its head, and the own caches would then
  be refused, loudly.
- This folder is reviewed and pinned (an `E0B-REVIEWED.sha256` over `rx.py`, `so_measure.sh`, `seed_scores.py`).
  The older pins (`REVIEWED`, `EXTEND-`, `LIVE-REVIEWED`) no longer match `rx.py`, as they already did not after L6.

```
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
K=$HOME/gov-os-runs/D4B/score-once/caches; X=$HOME/gov-os-runs/D4B/score-once-extend/caches
E=$HOME/gov-os-runs/D4B/e0b/caches; mkdir -p "$E"
# step 3, the seed: the kept q06 scores, no route answers (prints rows per source, rows written, conflicts)
python3 $S/seed_scores.py "$E/seed" $K/q06 $K/q06f $X/b0 $X/d80 $X/split $X/termmap $X/split-termmap
M=Qwen/Qwen3-Reranker-0.6B@e61197ed45024b0ed8a2d74b80b4d909f1255473
export CLONE=$HOME/gov-os-runs/D4B/w4-e0/repo GOV_RX_POOL_OFF=1
export GOV_RX_COMBINE="{\"models\":{\"q06\":\"$M\"},\"caches\":{\"q06\":\"$E/seed\"},\"rule\":{\"kind\":\"alone\",\"m\":\"q06\"}}"
V='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question"}'
VL3='{"sem_uncut":true,"sem_k":60,"lex_k":60,"depth":40,"perfile":2,"dedup":true,"rq":"question","lift_norm":0.0766}'
# steps 4 + 5a, run A (no lift_norm): the new texts scored on the live 0.6B. The one GPU job: its own process group,
# tools/gpu_backstop.sh armed as e0_run.sh lines 15ff, GOV_RX_GPU_LIMIT_MIB so rx stops rather than waits
GOV_RX_LIVE_MISSING=1 GOV_RX_GPU_LIMIT_MIB=14255 bash $S/so_measure.sh e0b a r80 "$V" "$E/a"
GOV_RX_LIVE_MISSING=1 GOV_RX_GPU_LIMIT_MIB=14255 bash $S/so_measure.sh e0b a r60 "$V" "$E/a"
# step 5b, run B (L3's lift_norm, B0's form for E4's M3 bundles): strict, no GPU; A's route answers and live scores
cp -a "$E/a" "$E/b"
bash $S/so_measure.sh e0b b r80 "$VL3" "$E/b"; bash $S/so_measure.sh e0b b r60 "$VL3" "$E/b"
# figures, and A against E0 question for question (W2-32 S11's "within 2 of the product")
D=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b
P=$HOME/gov-os-runs/D4B/e0b; W=$HOME/gov-os-runs/D4B/w4-e0/out
python3 $D/score138.py e0b-a $P/a/r80/measure.txt $P/a/r60/measure.txt
python3 $D/score138.py e0b-b $P/b/r80/measure.txt $P/b/r60/measure.txt
python3 $D/score138.py --same $W/r80/measure.txt $W/r60/measure.txt $P/a/r80/measure.txt $P/a/r60/measure.txt
```
**What to read in each summary line:**
- **Run A:** `texts scored live N` is the step-4 GPU count; `unscored 0`.
- **Run B:** `texts scored live 0`; `texts read from the replay's own cache` is about A's N, once per pass that
  needs them. Any missing text stops B, by design.
- **An optional control, no GPU:** a third run of A's variant on another copy of `$E/a`, strict. It must equal A in
  hit@5 and first gold rank for every question (R0's form).

`so_measure.sh` keeps every search's ranked output under `~/gov-os-eval/runs/e0b/<name>-<set>/`, as every
score-once run did.

## 4. What the seeding from the kept q06 scores needs
- **The sources:**
  - `score-once/caches/q06` (5,486 scores, the question) and `q06f` (5,486, the last phrasing);
  - `score-once-extend/caches/{b0, d80 (10,806), split, termmap, split-termmap (5,736)}`.
  - All mark `Qwen/Qwen3-Reranker-0.6B@e61197ed…`, equal to the pin's `rr.MODEL@rr.REVISION` (checked).
  - The union is valid because a score's key is (model, query text, text).
  - Texts the window-4 tree changed get new keys, and run A scores them live. Its N is not known before the run. As
    an order of size, E1 scored 5,320 new texts inside a 16-minute window, so even a mostly new 40 per call is a
    short job.
- **Route answers are dropped:** `seed_scores.py` copies none, and rx.py would refuse g1's on this store anyway.
- **Conflicts should be 0.** A non-zero count means two windows scored the same (question, text) differently. The
  first source's score is kept and the count is printed: report it.
- **The kept caches are only read:** `seed_scores.py` and replays open them read-only.

## 5. Remaining risks
1. **Two serving processes for one model.**
   - The kept scores came from the 0.6B's trial copy in the score-once window. The new ones come from the live
     service: the same model and revision, but other batches.
   - bf16 scores move slightly with batch padding (D4B-SCORE-ONCE §5's note for q4b). A question or two may differ
     from an all-live run.
   - Not measured. A check would re-score a sample of kept texts live, and needs a small tool and GPU time; it was
     not built.
2. **Not everything is cached, as in E0:**
   - `code_first`'s cosine (`semantic.distances`) and, if it were on, the file route query the shared embedder live.
     Both are off the cache.
   - The file route is off at the clone (no `file_level_index`).
   - Run B reuses A's route answers, so A and B differ by the lift alone.
3. **Continuations.** The harness reranks the same 40 again in each follow-up call, from its cache with no GPU. The
   product carries its pool order in the token. The orders are equal while the scores are, which the cache ensures.
   Any residue is what the A-against-E0 comparison measures, not a harness fault.
4. **The old scripts.** `replay.sh` and its callers (`run_extend_replays.sh`, `run_l6.sh`) are now refused on the
   kept g1 caches unless `GOV_RX_LEGACY_STORE=1` is exported. They fail loudly, never silently.
5. **Pins.** The three earlier sha256 pins no longer match `rx.py`. E0b needs its own pin after review.
6. **One clone, two experiments.** E0 and E0b share `w4-e0/repo`. E0b only reads it, but the two must not run at once
   (the GPU rules), and nothing may rebuild its store in between.
