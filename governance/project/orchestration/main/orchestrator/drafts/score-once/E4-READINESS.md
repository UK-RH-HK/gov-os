# E4-READINESS: E4's scoring window and its runs (E3-E5-DESIGN §1, E0B-RESULT "Next")

By the research agent, 2026-11-07, for the CTO's review. Not committed. **Nothing here stopped, started or touched the
live reranker service, a trial service or the GPU.** Done so far: the seeds, the window caches and the count (step 1,
no GPU, no reranker; a strict replay of E0b's run B), and the DRY=1 runs. Counts only.

## 0. What E4 needs, and the shape of the work
E4 compares **today's bundle built by M3** (zerank-1-small, yes-logit, + gte, merged) and **by M1** (the 0.6B + gte,
merged) against E3's "today's bundle". D4B-SCORE-ONCE's rules (grid.txt `g-M3`, `g-M1`): `merge`, min-max over the 40,
w = 0.5. Variant: E0b B's (v456 + `"rq":"question"` + L3's `lift_norm` 0.0766), `GOV_RX_POOL_OFF=1`, on E0's clone
`~/gov-os-runs/D4B/w4-e0/repo` at `c00d525fd420`.

**The texts a replay asks do not depend on the scorer.** The depth rerank's 40 come from the fusion (route answers,
cached), and the lift and merge only reorder them. So every model needs the same texts, the ones E0b's runs asked. The
0.6B already holds all of them; gte and zerank need only the texts their kept scores lack.

| step | what | GPU | script |
|---|---|---|---|
| 1 | seeds, window caches, count | none | `e4_prep.sh` (**done**) |
| 2 | gte, then zerank, score the texts they lack, one trial service at a time, the live service stopped | **one window** | `e4_window.sh` |
| 3 | M3 and M1: strict replays, kept outputs, figures | none | `e4_replays.sh` |

## 1. Step 1, done: the seeds, the window caches and the counts
`bash e4_prep.sh` ran 2026-11-07 21:44:55 to 21:49:29 (log `~/gov-os-runs/D4B/e4/prep.log`).

- **The seeds** (`seed_scores.py`):
  - `e4/caches/gte-seed`: 5,486 rows from `score-once/caches/gte`, 0 conflicts;
  - `e4/caches/zer-seed`: 5,486 from `score-once/caches/zer`, 0 conflicts.
  - Each comes from one source. The live window's two-model caches (gte as `rerank_model2`) were left out, since
    seed_scores.py refuses a second model mark. They hold the first calls of the first 20 visible questions on g1,
    which are in the grid's cache already.
- **The window caches** (`e4_prepare.py routes`):
  - `e4/caches/gte` and `e4/caches/zer`: 5,486 scores each, plus E0b run A's 875 route answers;
  - store `["…/w4-e0/repo", "c00d525fd4200303f4ad0fcc7e013d49e60dc2a6"]`, checked against the clone's store now.
- **The count:** a strict replay of E0b's run B with `e4_count.py` as its gov.
  - r80: 159 s, 397 combined passes, 1,154 own-cache reads. r60: 114 s, 293 passes, 407 reads.
  - unscored 0. These are run B's own figures.
- **The count replay equals E0b's run B:** 0 of 138 differ in hit@5 or first gold rank. The 138's hit@5 is 106, MRR
  0.5602, 123 in the bundle.

| model | distinct texts asked on window 4 | held by | **lacking** |
|---|---|---|---|
| q06 (the 0.6B, M1) | 5,488 | E0b's seed (16,025) + run A's own cache (314) | **0** |
| gte (M1, M3) | 5,488 | its seed (5,486) | **360** |
| zer (M3) | 5,488 | its seed (5,486) | **360** |

The window scores **720 texts in all** (360 per model): about 7 % of what the 11-06 window scored (5,486 per model).

**The 0.6B for M1 is scored before the window, from E0b's own caches, not in the trial frame.** E0b's seed plus run A's
own cache (its 314 live scores) already hold every 0.6B text. M1's replay reads the seed as its kept cache, and run A's
scores from its own cache (a fresh copy of E0b's run-B cache, which holds them). Nothing of the 0.6B is scored in the
window. The frame could not score it there anyway: the live service is stopped for the window, and a third trial
service is not in the plan.

**The new files** (in this folder):
- `e4_prepare.py`: `routes` makes a window cache, that is the seed copied whole plus E0b run A's 875 route answers and
  their `store`. It refuses a seed that is not seed_scores.py's form, a routes cache keyed otherwise or for another
  store (the clone rebuilt), and an existing folder. `check` checks a cache's model, key form, store and routes, and
  optionally that it equals its seed. `store` prints the clone's store key.
- `e4_count.py`: the count. It is a measure's gov that imports rx.py unchanged (GOV_RX_NO_MAIN=1) and wraps
  `rx.scores`. Each pass's texts are keyed per counted model (`rx._key("rr", model, query, text)`) and looked up in that
  model's caches, read-only. Digests only. It refuses anything but a strict replay. `--summary` and `--check` modes.
- `e4_prep.sh`, `e4_window.sh`, `e4_replays.sh`, `test_e4.py`. `run_harness_tests.sh` now runs `test_e4.py` too.
- **rx.py, so_measure.sh and seed_scores.py are unchanged.** `E0B-REVIEWED.sha256` still matches them.

## 2. The exact commands (the CTO's, after the review)
```
S=/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/score-once
# 0. the review pin (after the review, in $S): all nine files, relative names, as E0B-REVIEWED.sha256
( cd $S && sha256sum rx.py so_measure.sh seed_scores.py rerank_worker.py e4_prep.sh e4_prepare.py e4_count.py \
    e4_window.sh e4_replays.sh > E4-REVIEWED.sha256 )
# 1. done (bash $S/e4_prep.sh); it refuses to run again over its count
# 2. the window: the conditions and the plan, then the window itself in the BACKGROUND, its own session and group,
#    its output to a file (never a foreground tool call: the window outlives the 10-minute call limit; review F1/F4)
DRY=1 bash $S/e4_window.sh
setsid bash $S/e4_window.sh > ~/gov-os-runs/D4B/e4/window-run.out 2>&1 < /dev/null &   # gte then zer ("… zer" resumes)
echo $! > ~/gov-os-runs/D4B/e4/window.pid
#    to stop it early: TERM to the script's pid only, with a grace longer than its cleanup (never by its group, and
#    never with the default 30 s grace, which can SIGKILL the cleanup mid-restore):
#    bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh stop --grace 300 $(cat ~/gov-os-runs/D4B/e4/window.pid)
#    its full log: ~/gov-os-runs/D4B/e4/window/<stamp>/window.log
# 3. no GPU: M3 and M1
DRY=1 bash $S/e4_replays.sh
bash $S/e4_replays.sh                # m3 then m1
```
**What to read:**
- **The window, per model:**
  - `load: … READY … cuda`;
  - `GPU peak during its runs` and `samples at or above 14255: 0`;
  - `GPU after the stop` within the base + 300;
  - `texts newly scored N`, which should equal the count's lacking figure in §1;
  - `route answers 875 -> 875`;
  - `e4_count.py --check: … 0 lacking`;
  - the model-alone figures on window 4, a by-product;
  - then `restore: … rerank.by = service`.
- **The replays, per cell:** `unscored 0; … texts scored live (GOV_RX_LIVE_MISSING) 0`, the figures, and the count of
  questions differing from E0b B.
- **The bundles for E4's reader run:** `~/gov-os-eval/runs/e4/m3-r80/`, `m3-r60/`, `m1-r80/`, `m1-r60/`. A question's
  first call is found by `e3_run.py`'s `first_calls()` on `~/gov-os-runs/D4B/e4/<cell>/<set>/measure.txt`, as E3 did
  with E0's outputs.

## 3. The GPU budget plan (budget 14,255 MiB; card 16,303 MiB)
The figures come from the 11-06 score-once window (`~/gov-os-runs/D4B/score-once/window.log`), which loaded the same
two models from the same snapshots with the same trial service. The base then was 6,096 MiB (live service stopped,
both embedders warm).

| order | load | after load (11-06) | peak in its runs (11-06) | rise over base | free memory its start needs | headroom check in `e4_window.sh` |
|---|---|---|---|---|---|---|
| 1 | gte (cross-encoder, 16 texts / 24,000 chars) | 6,957 (+861), load 5 s | 7,659 | **1,563** | 5,632 MiB (rerank_service `gpu_short`) | base + 1,563 + 300 < 14,255, so a base up to 12,391 |
| 2 | zerank (yes-logit, 16 / 24,000, model cut 10,000) | 9,652 (+3,556), load 7 s | 12,316 | **6,220** | 5,632 MiB | base + 6,220 + 300 < 14,255, so a base up to 7,734 |

- **One service at a time.** gte is stopped by group, and the GPU is back to the base + 300 before zerank loads.
- **The 0.6B is never loaded:** the live service is stopped, and M1's 0.6B scores are already held.
- **Today's reading:** 7,461 MiB with the live service up (2026-11-07 21:39). On 11-06 the live service's stop took
  8,831 down to 6,096. If today's base lands near 6,100, zerank's expected peak is about 12,300, with about 1,900 MiB of
  margin.
- **The headroom is checked on the GPU read just before each load** (review F2), not on the window's first base. An
  empty or non-numeric reading, at the base or before a load, stops the window: it is never taken as 0. A free
  reranker slot is checked again before each load.
- **If the GPU reads above 7,734 before zerank's load**, the window stops before the load and restores the live
  service. gte's scores stay. Free the GPU, then run `setsid bash e4_window.sh zer` (in the background, as §2).
- **Guards:**
  - `GOV_RX_GPU_LIMIT_MIB=14255`: rx stops before a request at the budget;
  - `tools/gpu_backstop.sh` on the script's group, the service's and each measure's, armed from the load;
  - so_measure.sh's own wait at 15,000 (600 s at most).

## 4. Expected durations
- **gte:** load 5 s; r80 plus r60 about 4-6 min; back to the base, seconds.
  - Basis: E0b B took 164 + 116 s with everything cached, and 11-06's gte took 227 + 143 s scoring all 5,486.
  - Here the routes are cached and only the lacking texts are scored.
- **zerank:** load 7 s; r80 plus r60 about 5-7 min (11-06: 250 + 177 s for all 5,486).
- **The window, with conditions, the live stop, two returns to the base and the restore:** about 15-20 min. The live
  service is down for all of it.
- **The replays:** M3 and M1, about 5 min each (E0b B's form), so about 10-12 min with the figures. No GPU.

## 5. The restore path
- **One trap (`cleanup`) on EXIT, with INT and TERM turned into exits.** It runs once on every path the script
  survives to run it: a stop, a failure, a TERM or INT to its pid or to its whole group, its output closing, a normal
  end. In order:
  1. **first, `trap '' INT TERM PIPE`** (review F1), so a second signal or a dead output cannot cut the restore short;
  2. the sampler;
  3. the measure's group (`proc.sh stop --grace 10 -<pgid>`);
  4. the trial service's group (`--grace 30`);
  5. the backstop;
  6. if the live service was stopped, **class 3's start line** (`gov retrieve` in `W2-00-store` with
     `GOV_RERANK_IDLE_S=43200`, then the check `rerank.by`, and a line in `log/restarts.jsonl`). Each `gov retrieve`
     now runs as `setsid -w env --default-signal=INT,TERM,PIPE …`: in its own session, so a further group signal cannot
     reach it, and with those signals back to their defaults, so the live service it starts does not inherit the
     cleanup's ignores (it stays stoppable by TERM);
  7. the hold (`log/act-in-progress.txt` moved to `.ended-HHMM-e4-window.txt`).
- **The output frame (review F1):** `exec > >(trap '' INT TERM; exec tee -p -a "$OUT/window.log") 2>&1`. A signal to
  the whole group no longer kills the `tee`, and `-p` keeps it writing the log when the caller's output closes, so the
  script's writes never kill it. Tested: G1 (TERM to the group), G2 (INT), G3 (output closed), G3b (both). In each,
  the log shows the restore, and no stand-in trial service or measure is left.
- **A trial service that survives SIGKILL (review F3):** the window stops, does **not** restore (the live service
  would fight it for the GPU), prints `NOT RESTORED: …` and leaves the hold, rewritten to say so. Free the GPU, then
  class 3's start line by hand.
- **`LIVE_STOPPED=1` is set before the stop is tried,** so a failed stop still restores.
- **The one path that does not restore by design: the backstop's pause.** A backstop trip sends SIGSTOP to the
  script's own group (`$MG`), the service's and the measure's. A stopped script runs no trap, so the live service stays
  down. The CTO then acts on the inbox item: stop the groups by pid, and restore by hand with class 3's start line
  (`cd /home/usain/gov-os-worktrees/W2-00-store && GOV_RERANK_IDLE_S=43200 ~/.local/bin/gov retrieve "what decides a
  close" --json`, then check `rerank.by`).
- **Not covered:** SIGKILL to the script (no trap can run), or `proc.sh stop` with a grace shorter than the cleanup.
  Hence §2's form.
- **If the restore's check is not `service`:** the owner's class 3 path as in every window (the live service is
  started by the product's own client on the next search).
- **live_window.sh and score_once_window.sh** share the old frame and its defect. They are not changed here: they are
  done, and their fix (this frame and this cleanup line) is for when either is next used.

## 6. Risks
1. **Two serving processes for one model.** The kept gte and zerank scores came from 11-06's trial service, and the
   new ones from the same trial service code and snapshots, in other batches. bf16 scores move slightly with batch
   padding (E0b's 246 seed conflicts for the 0.6B). gte's and zerank's seeds come from one source each: 0 conflicts.
   A question or two of M3 and M1 may differ from an all-at-once scoring. Not measured.
2. **The candidate lists must stay E0b's.** The window caches carry E0b's 875 route answers, and the window stops if
   its runs add any (`route answers 875 -> N`). The count replay reproduced E0b B (§1). The window refuses a rebuilt
   store (the `store` check), and so do the replays (rx.py's own store key).
3. **The base may be higher than on 11-06.** The headroom check, on the GPU read just before each load, stops before
   zerank's load (§3). The cost is a second, shorter window for zerank alone.
4. **The heavy gate inside the window has no bound (review F4).** so_measure.sh runs each measure through
   `heavy_slot.sh`. It waits, without limit, for a free slot, and it also yields to any landing or close that is
   waiting (`heavy_slot: a landing or close waits first`). For that whole wait the live service is down and a trial
   service is loaded. The `quiet` condition and the hold make this unlikely. The operator watches the log for
   `heavy_slot: all 3 slots taken` or `a landing or close waits first`, and if it lasts, stops the window by its pid
   (§2), which restores.
5. **The GPU slots.** One trial service at the default 2 slots, as the score-once and extend windows ran. A private
   reranker that took the freed slot first would leave none. A free slot is checked after the live stop and again
   before each load; with none, the window stops and restores.
5b. **The backstop's pause (review F4).** A backstop trip SIGSTOPs the script's own group along with the service and
   the measure. No trap runs, and the live service stays down until the CTO restores it by hand (§5). This is the
   owner's design, and it is the one designed path that leaves the live service down.
5c. **A stop by group, a default grace, or a foreground run.** All three are now survived (§5, tests G1-G3b), but the
   form in §2 is still the one to use: background, output to a file, TERM to the pid with `--grace 300`.
6. **e4_prep.sh is in the pin, but it has already run.** If the review changes it, or `e4_prepare.py` or
   `e4_count.py`, the seeds, caches and count must be made again. Moving `~/gov-os-runs/D4B/e4/` aside is the CTO's
   act: this agent removes nothing outside its TMPDIR.
7. **Nothing may rebuild `w4-e0/repo`'s store** between E0b, the prep, the window and the replays. A rebuild changes
   its head, and every cache is then refused, loudly.
8. **The live service is down for 15-20 min.** Agents' searches in that time get the product's fallback. The hold and
   the quiet condition are the usual mitigation.
9. **Not cached:** `code_first`'s cosine queries the shared embedder live in every run, as in E0 and E0b.
10. **The model-alone figures on window 4** (the window's runs) are by-products. They are not E4's conditions.

## 7. Tests (CPU, stand-ins only)
`bash .gov-runtime/scratch/orchestrator/tools/heavy_slot.sh bash <folder>/run_harness_tests.sh` runs them, or
`test_e4.py` alone with python3.
- **`test_e4.py`: 61 of 61** (after review round 1; 52 before). Every temporary folder sits under one root, removed
  when every case passes, and no byte code is written (review F6).
  - **E0-E7, the window**, on a copy with one stubs line, checked byte-identical less that line:
    - the order and one service at a time;
    - a failed measure; texts still lacking; no return to the base; route answers added; a TERM to the script's pid;
    - **review F2:** E5 (headroom on the GPU read just before zerank's load, not the first base), E5b (an empty base
      reading), E5c (an empty reading before the load), E5d (the slot taken before the load);
    - **review F3:** E5e (a trial service that survives SIGKILL: no restore, a loud line, the hold rewritten), and E5f
      (the restore's gov calls in their own session with default signals);
    - DRY changes nothing;
    - the real `arm` with a backstop that dies, and with one that stays up (5 backstops, each up before the old one
      stops).
  - **G1-G3b, review F1:** the copy runs in its own session, with real stand-in processes (`setsid sleep`) for the
    trial service and the measure. It is then given TERM to its whole group (G1, exit 143), INT to its whole group (G2,
    exit 130), its output closed (G3: it runs on to its end, exit 0), and both (G3b). Each log shows the restore and
    the hold released, and no stand-in process is left.
  - **R0-R5, the replays:** the order; not strict (unscored or scored live); a failing replay; DRY.
  - **PIN1-4, both scripts:** all nine files pinned; one left out; one changed; none.
  - **P1-P9, `e4_prepare.py`.**
  - **C1-C5b, `e4_count.py`.** C5 uses the real rx.py on window 4's gov: the search's own lookup goes through the
    wrapper, and `GOV_RX_LIVE_MISSING` is refused.
- **The folder's other tests, unchanged:**
  - test_rx_combine 23/23, test_rx_l5 48/48, test_rx_l6 4/4, test_rx_live 26/26, test_live_tools 18/18,
    test_live_window 26/26, test_rx_e0b 12/12 (pytest);
  - test_yes_logit 16/16 with the trial venv's python and `CUDA_VISIBLE_DEVICES=-1`. Under system python3 it fails
    on `No module named 'torch'`, as before, so run_harness_tests.sh exits 1 for that file only.

## 8. The DRY=1 runs (2026-11-07 22:07, after review round 1)
- **`e4_window.sh`: 1 condition not met; nothing stopped or started.**
  - `E4-REVIEWED.sha256`: no pin before the review.
  - Met (each cache line now printed once, review F7):
    - quiet;
    - the worker is the reviewed copy;
    - the trial service, its venv and both snapshots;
    - both window caches (5,486 scores, 875 route answers, the clone's store);
    - both counted (`360 lacking` each);
    - the clone at `c00d525fd420`, no ACT, the trial lock free, the tools.
  - Slots now 0 of 2 free (the live service and the watcher). GPU 7,431 of 16,303 MiB with the live service up.
- **`e4_replays.sh`: 3 conditions not met.**
  - The pin.
  - zer and gte still lack 360 each: the window has not run.
  - The 0.6B: 5,488 held by E0b's seed + **run B's cache** (what M1's replay reads, review F5), 0 lacking.

## 9. Review round 1 (`reviews/e4-window.md`), each finding's fix
- **F1 (blocking):** the output frame is `exec > >(trap '' INT TERM; exec tee -p -a LOG) 2>&1`, and the cleanup's first
  line is `trap '' INT TERM PIPE`. The restore's gov calls run under `setsid -w env --default-signal=INT,TERM,PIPE`.
  Tests G1, G2, G3 and G3b.
- **F2:** headroom is checked on `$(gpu)` read just before each load. An empty or non-numeric reading stops the window,
  and the slot is checked again before each load. Tests E5-E5d.
- **F3:** a trial service that survives SIGKILL means no restore, a `NOT RESTORED` line and the hold rewritten. Test E5e.
- **F4:** §2 (background, output to a file, `proc.sh stop --grace 300 <pid>`), §5 (the pause, and the paths not
  covered), §6 risks 4, 5b and 5c.
- **F5:** M1's condition reads `$E/seed` + `$E/b`.
- **F6:** a single temporary root, removed on a pass; `PYTHONDONTWRITEBYTECODE`.
- **F7:** `quietly` wraps the conditions whose own line the `need` line shows.
- **Not changed:** live_window.sh and score_once_window.sh (§5's last point).
