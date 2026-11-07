# E0b harness fix (drafts/score-once, uncommitted): independent review, round 1

Reviewer: a fresh independent-auditor session, read-only, 2026-11-07. Nothing under `~/gov-os-eval` was opened beyond
names. No GPU job, no search of a real store, no use of the shared reranker; `smoke_w4.py` was not run.
Judged by `governance/project/briefs/JUDGEMENT.md` (ADR-0001's threat model, the two questions, DEC-801 to DEC-803 and
DEC-807 to DEC-809, DEC-1010 item 1).

## Verdict
C1 to C6 all pass. There are nine findings and none of them blocks: none is in scope, reachable in ordinary work and
fails open or loses work. **READY.** Six findings are worth folding into the E0b pin before it is taken (F3, F4, F6,
F7, F8 and the readiness wording in F2). They ride along with that pin and need no new round (DEC-802).

## What was read
- `rx.py`, diffed against its pre-change form (`scratchpad/before/rx.py`, 72,704 bytes). The diff matches §1 of
  `E0B-READINESS.md`: the store key (`_store_of`, `_scoped`, `memo_keys`), `_depth`/`_lex_call`/`_sem_call`, the
  `top_k` on `_lex`/`_sem`, the `_phrased_rx(depth)`, the `GOV_RX_LIVE_MISSING` block with `_kept`'s own-cache read and
  `_live_missing`, the semrank key, and `_pool_rx`.
- `so_measure.sh`, `replay.sh`, `seed_scores.py`, `smoke_w4.py` (read only), `test_rx_e0b.py`, `test_rx_l5.py`'s
  2b/`copy_kept` edits, `run_harness_tests.sh`, `README.md` and `E0B-READINESS.md`.
- The pin's `retrieve.py` (`_phrased` :238-248, `retrieve` :294-551), `pool.py`, `fusion.py`, `lexical.search`/`_ranked`,
  `semantic.search`, `rerank.default_reranker`/`_connect`, `measure.py` (a failed retrieval raises a fault, :358, so
  each `sys.exit` in rx stops the run), and `store/loader.py` (the fingerprints `head` is the HEAD of the load).
- `E0-DECLARATION.md` §E0b and `d4b/e0_run.sh`.
- The pin's `gov` package against `~/gov-os-runs/D4B/w4-e0/repo/src/gov`: `diff -rq -x __pycache__` found them
  identical. The clone is at `c00d525fd420` with a clean tree, and its `retrieval.yaml` has the pool on (60/40/2/true/true).
- The seven seed sources' `meta` and score counts, read through read-only connections: each is marked
  `Qwen/Qwen3-Reranker-0.6B@e61197ed…`, and the counts are 5,486 / 5,486 / 5,486 / 10,806 / 5,691 / 5,546 / 5,736.

## C1: window 4's `depth`/`top_k`: pass
- `_phrased_rx(search, root, asked, key, cut=None, depth=0)` has the pin's `_phrased` signature. It passes `depth`
  only when it is non-zero, which matches the product's `more = {"top_k": depth} if depth else {}`. The product's
  `_phrased` then passes `top_k=depth` to each phrasing's search, as `refresh=False, top_k=60`.
- The harness's `_lex`/`_sem` take `top_k` and pass it to `_lex_memo`/`_sem_memo` only when it is set (`_depth`). The
  memo key is `top_k or lexical.TOP_K` (sem: `top_k or semantic.TOP_K` plus `INSTRUCTION`), which is exactly how the
  product resolves the depth (`lexical._ranked`: `top_k = top_k or TOP_K`; `semantic.search`: `top_k or TOP_K`).
  `_sem`'s own phrasing cut is `[:top_k or semantic.TOP_K]`.
- With the pool off, `route_depth` is 0, so no `top_k` is passed. The variant's `sem_k`/`lex_k` set the module
  `TOP_K` to 60, and the key is `(q, 60)`, the same key as with the pool on at `route_depth` 60. Both read the same
  answer.
- The older form still works. No `top_k` is passed and the key is unchanged (in legacy mode `_scoped` is `_key`). A
  `depth` given to a `_phrased` that has no `depth` parameter stops the run (`_PHRASED_DEPTH`, test 1c). The g1-based
  files pass on the g1 clone's src: combine 23/23, l5 48/48, l6 4/4, live 26/26.
- `rt.rrf`, `rt.rerank` and `rt._phrased` are module globals at the pin, read at call time, so the patches reach
  window 4's `retrieve`.

## C2: route answers keyed by their store: pass
- Every route answer is stored under `_key(name, (resolved root, fingerprints head), …)`. This covers `_memo` (lex,
  sem, chunks, start, closure, code, records, edges) and the semrank row. The termmap row was already keyed by root
  and git commit. A different root or head gives a different key, so another store's answer is never read. Test 2a
  checks this, including after the meta claim is removed.
- Meta `store` is claimed on the first call, and a different store is refused with `sys.exit`. `measure` turns that
  into a fault that stops the run. A store with no head, or with more than one row, is refused. A root with no store
  file stores nothing.
- **A legacy or marker-less cache cannot slip through.** A cache with no `memo_keys` marker but with any `memo` row
  (route answers, semrank or termmap) is classed `legacy`, and is refused unless `GOV_RX_LEGACY_STORE=1` is set (test
  2c). A cache with no marker and an empty memo holds nothing that could be returned. A cache marked with one key form
  is refused under the other, in both directions.
- `replay.sh` now keeps `memo_keys`/`store` on its copy, so a copy of a store-keyed cache keeps its claim. Kept
  caches given in `GOV_RX_COMBINE` are opened `mode=ro`, and only their `score` table is read.
- `seed_scores.py` copies only scores, marks `memo_keys: store`, refuses mixed models or an existing destination, and
  counts conflicts (test 5).
- The one opt-out is the `GOV_RX_LEGACY_STORE=1` switch, which does no store check by design (F3).

## C3: `GOV_RX_LIVE_MISSING=1`: pass
- The flag is refused outside a replay, and refused when no rule model is the live model (`rr.MODEL@rr.REVISION`)
  (test 3c).
- It acts only on texts that are still missing after the kept caches and then the replay's own cache have been read,
  and only for the rule model equal to `LIVE_MODEL`. A missing text of another model still stops the run, with a
  message that names it (test 3c, merge of q06 and gte).
- **The client is the product's own `rr.default_reranker()`.** `rr._start` and `rr._started` are patched to refuse.
  `GOV_RX_RERANK_DIR` cannot be combined with a replay, so the socket is the live one. A fault falls back to
  `_started`, which returns no private reranker, so `score()` returns None. `_live_missing` stops when `part is None`,
  `by != "service"` or the lengths differ.
- **Nothing is kept on a fault.** All requests are gathered before any insert (test 3d: 0 rows). Each request
  follows `_gpu_wait`.
- **Writes go only to `_db` (`GOV_RX_CACHE`),** and a replay whose cache resolves to any kept cache is refused
  (rx.py :751).
- **The counts are logged:** `LIVEMISS\tn\tname\ttexts` and `OWNCACHE\tn\tname`. `so_measure.sh` sums column 2 of each.
- **Without the flag, a missing text stops the run** (test 3a). A strict re-run reads the live scores from the own
  cache and makes no client (tests 3a and 3b).

## C4: `GOV_RX_POOL_OFF=1`: pass
- `retrieve` reads `pool.settings` through the module (`retrieve.py:36`, `:294`), and it is the only reader in the pin.
  `_pool_rx` calls the real `settings` first, so an invalid file is still refused (test 4, `'pool': must be a map`).
  Under the switch it returns a dict with every key 0 or False, and logs `POOL\toff\t…` once.
- Nothing writes the clone. The patch is in-process only. rx writes only its cache and log. The product's query-vector
  cache is under `~/.cache/gov-os/vector-cache`, not in the clone.
- A CUSTOM variant (v456) on a clone with the pool on is refused, and the message names the switch (test 4).
  `{}` keeps the pool. A tree before S11 has no `pool` module, so nothing is patched.
- With the pool off, window 4's per-page path is the g1-era structure the harness was built on: `rrf` goes to
  `_fusion`, `rerank` goes to `_rerank`, and `order.fused`/`reranked` are no-ops under CUSTOM.
- Only CUSTOM variants are refused (F1).

## C5: `E0B-READINESS.md`'s commands: pass
- **Run A:** `V` has no `lift_norm`. `GOV_RX_LIVE_MISSING=1` and `GOV_RX_GPU_LIMIT_MIB=14255` are prefix assignments
  on the two `so_measure.sh` calls only, so run B does not inherit them. `GOV_RX_POOL_OFF=1`, `CLONE` (w4-e0) and
  `GOV_RX_COMBINE` (the seed, rule alone q06) are exported. The seed `$E/seed` is a kept cache and A's own cache is
  `$E/a`, so the two are distinct and the guard at :751 would refuse otherwise.
- **Run B:** `VL3` carries `lift_norm` 0.0766. It runs strict, without the flag or the GPU limit, on `cp -a "$E/a"
  "$E/b"`. Route answers, semrank and live scores all come from A's copy under the same store claim, so B makes no
  reranker request. `code_first`'s cosine reads the cached query vector and starts no GPU job.
- **Writes:**
  - outputs go to `~/gov-os-runs/D4B/e0b/{a,b}/{r80,r60}` and `~/gov-os-runs/D4B/e0b/caches/{seed,a,b}` (the folder
    does not exist yet);
  - kept outputs go to `~/gov-os-eval/runs/e0b/{a,b}-{r80,r60}`, the DEC-1069 keep place that E0 also used for
    `runs/w4-e0/`. `so_measure.sh` empties only its own `$KEEP` (`runs/e0b/<name>-<set>`);
  - E0's kept outputs (`runs/w4-e0/`, `~/gov-os-runs/D4B/w4-e0/out`) are only read, by `score138.py --same`, which
    only opens files for reading;
  - the measure re-anchors gold in memory and writes only `--out`. Nothing writes the sets' questions or labels.
- **The one shortfall:** the declared "light GPU job with the backstop" is a comment, not a command, and so is the
  review-pin check (F6).

## C6: tests: pass
- `bash tools/heavy_slot.sh bash drafts/score-once/run_harness_tests.sh` was run with the script's default TMPDIR
  (`/tmp/gov-os-emg-e0b`). Results:

  | file | result |
  |---|---|
  | test_rx_combine.py | 23/23 |
  | test_rx_l5.py | 48/48 |
  | test_rx_l6.py | 4/4 |
  | test_rx_live.py | 26/26 |
  | test_live_tools.py | 18/18 |
  | test_live_window.py | 26/26 |
  | test_rx_e0b.py (pytest) | 12 passed |
  | test_yes_logit.py | `ModuleNotFoundError: torch` (system python3), exit 1 |

  The script's overall exit was 1 because of test_yes_logit.py (F8). The file is untouched (mtime 11-06 11:05).
- `test_rx_e0b.py` with the pin's python (`pin-bcea09060ebc/bin/python3 -B -m pytest -q -p no:cacheprovider`):
  **12 passed.**
- **Write check.** A marker file was touched before the runs. Afterwards, `find -newer` over the repo (minus `.git`),
  `~/gov-os-runs`, `~/gov-os-eval` (names only), `~/.local/share/gov-os` and the top level of `~` and `/tmp` showed:
  - new files only in `/tmp/gov-os-emg-e0b` (the `lt-`/`lv-`/`lw-`/`rx-combine-`/`rxl-` folders, `pytest-of-usain`
    and the `.out` files);
  - in the repo, only the orchestrator's own monitoring files (`orchestrator/dispatch/*`, `log/deadman.log`,
    `log/lead-mem.jsonl`, `log/capacity/*`), which daemons rewrite continuously and the tests do not touch;
  - no new `__pycache__` file in the draft folder or in either clone's src;
  - nothing in `~/gov-os-runs` or `~/gov-os-eval`.

  So the suite writes nothing outside its temp folders.
- A first attempt with TMPDIR set to this session's long scratchpad path failed three files with `OSError: AF_UNIX
  path too long` (F9). It wrote only to that scratchpad.

## Findings
- **F1 (C4, C1):** `_pool_rx` refuses only CUSTOM variants. A variant made only of `sem_k`/`lex_k` (with or without
  `chars`/`sem_uncut`), run on a clone with the pool on and without `GOV_RX_POOL_OFF`, is not refused. The product
  then passes `top_k=route_depth` (60) to each search, which overrides the variant's own `TOP_K`. The run is measured
  at depth 60 under a label that says another depth. E0b's variants are CUSTOM and set the switch, so E0b is not
  affected. A fix: refuse when `route_depth` is set and the variant names `sem_k`/`lex_k` with a different value.
  - Ordinary work: yes, because a depth-only variant on a window-4 clone is a natural next experiment, and the README
    says only "a variant of its own" is refused.
  - Consequence: other. It gives a mislabelled figure. No guard or refusal fails open and no work is lost. Scope: out
    (no E0b command uses such a variant).
- **F2 (C2):** the store key is (root, fingerprints head), and the head is the HEAD commit of the last record load.
  Rebuilding or re-indexing a store at the same commit (for example vectors rebuilt by another gov or embedder pin)
  keeps the key, so a cache filled before the re-index would return stale route answers. Precondition 2 in
  `E0B-READINESS.md` §3 also says "A rebuild changes its head". That holds only for a rebuild at another commit.
  - Ordinary work: no, because the E0b clone is read-only between runs, the preconditions forbid a rebuild, and a
    rebuild at the same commit by the same pinned gov produces the same answers.
  - Consequence: fails open (a stale answer would be returned silently). It is a Wave 3 row with a one-line wording
    fix to precondition 2: "a rebuild at another commit changes its head; do not re-index at all".
- **F3 (C2):** `GOV_RX_LEGACY_STORE=1` does no root or commit check at all. `replay.sh` does not set `CLONE`, and
  `so_measure.sh` reads it from the environment. A g1 replay (`GOV_RX_LEGACY_STORE=1 bash replay.sh …`) run in the
  shell where the E0b block exported `CLONE=…/w4-e0/repo` (and `GOV_RX_POOL_OFF=1`) would therefore replay g1's route
  answers on window 4's clone. In practice it stops: chunk texts are read from w4's files, every changed span misses
  its score, and the strict replay stops. `so_measure.sh` also prints the clone's commit first. Two fixes, either
  sufficient: set `CLONE=$HOME/gov-os-runs/D4B/g1/repo` explicitly in `replay.sh`, or have legacy mode refuse a store
  whose head is not g1's `e884675b465e`.
  - Ordinary work: yes, because the E0b block uses `export CLONE=…` in the operator's shell, and `replay.sh`'s own
    comment tells the operator to export `GOV_RX_LEGACY_STORE=1`.
  - Consequence: other. Over 138 questions × 40 texts at least one changed text is all but certain, so the run stops
    loudly. A silently wrong figure would need every span to be unchanged.
- **F4 (C3):** if `GOV_RX_LIVE_MISSING=1` is used without `GOV_RX_GPU_LIMIT_MIB`, `_gpu_wait` falls back to the old
  window protocol. At or above 15,000 MiB it touches `/tmp/gov-os-research-wait.flag` and waits, with no bound, for a
  watcher to remove the flag. That is the unbounded wait L-0075 warns against. E0b's run A sets the limit. A fix: refuse
  the flag unless `GOV_RX_GPU_LIMIT_MIB` is set.
  - Ordinary work: yes, because a later replay that copies run A's line without the limit is plausible.
  - Consequence: other. The run hangs, and nothing is scored wrongly or lost.
- **F5 (C3):** `_live_missing` accepts any answer with `by == "service"`, whatever its `device`. A live service that
  answered from CPU (fp32) would give scores that differ slightly from the bf16 GPU scores and the kept window scores.
  This is the same kind of drift as residual risk 1 in the readiness record.
  - Ordinary work: no, because the shared reranker service runs on the GPU and a CPU start is not part of today's
    service management.
  - Consequence: other. At most a question or two would move, and the A-against-E0 comparison would show it. Logging
    the device in the `LIVEMISS` line would make it visible.
- **F6 (C5):** E0b's runs are a block to paste, not a script. Three declared safety steps appear only as prose:
  - the backstop and its own process group: E0-DECLARATION plan step 4 says "a light GPU job with the backstop", and
    the block has only the comment "armed as e0_run.sh lines 15ff";
  - the `heavy_slot` gate for the measure (`so_measure.sh` already uses `heavy_slot`, so this one is covered);
  - the `E0B-REVIEWED.sha256` pin check, which every earlier window script ran (`sha256sum --quiet -c`).

  As written, run A runs without the backstop and without the pin check. What remains is rx's pre-request stop at
  14,255 MiB (which also stops when the GPU cannot be read) and `so_measure.sh`'s bounded 600 s wait. A fix: a small
  `e0b_run.sh` in `e0_run.sh`'s form (`setsid gpu_backstop.sh "$G"`, `sha256sum --quiet -c`, then A, the copy, B and
  the figures).
  - Ordinary work: yes, because the operator would paste the block as given.
  - Consequence: other. Each request is still GPU-checked and stopped above 14,255 MiB, so no guard passes something it
    should refuse and no work is lost. The kill-switch layer is missing, not bypassed. In scope; worth taking with the
    pin.
- **F7 (C5):** `cp -a "$E/a" "$E/b"` copies into `$E/b/a/` when `$E/b` already exists, for example when B is re-run
  after a fix. B would then run on the earlier copy. A fix: `[ -e "$E/b" ] && { echo exists; exit 2; }` before the copy.
  - Ordinary work: yes, because re-running B after a stop is plausible.
  - Consequence: other. The earlier copy is still A's clone and store, and any text it lacks stops B (strict).
- **F8 (C6):** `run_harness_tests.sh` runs `test_yes_logit.py` with system python3, which has no torch, so the script
  exits 1 on this machine every time. A real failure in another file gives the same exit, and the readiness table's
  "16/16" for that file is from a different interpreter, which the script does not use. A fix: run that file with the
  reranker venv's python and `CUDA_VISIBLE_DEVICES=-1`, or skip it with a printed reason.
  - Ordinary work: yes, because every run of the script shows it.
  - Consequence: other. The script fails closed, and the per-file lines still show the counts.
- **F9 (C6):** the script honours an inherited `TMPDIR`. A long one, such as a Claude Code scratchpad path, makes
  test_rx_l5, test_rx_live and test_live_tools fail with `AF_UNIX path too long` from their stand-in sockets.
  - Ordinary work: no, because TMPDIR is unset in sessions by default and the script's default is short.
  - Consequence: other. The failure is loud and false, and nothing passes that should fail.

Classification: 9 findings. None blocks: no finding is in scope, reachable in ordinary work and fails open or loses
work. F2 fails open but is not ordinary work. Proposed: F3, F4, F6, F7, F8 and F2's wording ride along into the E0b
pin. F1, F5 and F9 are Wave 3 rows. No new round.

```verdict
{"kpis": [
 {"kpi": "C1", "verdict": "pass", "findings": []},
 {"kpi": "C2", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C3", "verdict": "pass", "findings": [{"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "C4", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C5", "verdict": "pass", "findings": [{"id": "F6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "C6", "verdict": "pass", "findings": [{"id": "F8", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F9", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}
]}
```
