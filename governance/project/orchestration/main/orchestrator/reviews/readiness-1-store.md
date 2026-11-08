# Readiness review before the fresh 80, aspect 1: the store and its refresh hook (W2-116 pass 1)

- **Reviewer:** one of seven independent, read-only reviewers (DEC-1097 (3); FRESH-80-READINESS §5 item 1), 2026-11-08.
- **Judged by:** JUDGEMENT.md and AUDITOR-common.md (ADR-0001's threat model, the two questions, DEC-1010's blocking rule).
  A finding is **FIX BEFORE THE 80** only if it is in scope, reachable in ordinary work, and fails open or would make
  the fresh-80 verdict wrong. Everything else is a **ROW**.
- **Not opened:** nothing under `~/gov-os-eval/`, no hidden or spent set, no kept outputs. No commit, no rebuild, no
  GPU work, no install. I did not run `gov retrieve`, because it calls the shared reranker on the GPU. I read the
  sources directly instead. Guard refusals: 0.
- **Read:**
  - the code: `src/gov/rebuild/integration.py`; the pin's `retrieve/command.py`, `retrieval/pool.py`,
    `retrieval/measure.py` and `launch/launcher.py`;
  - the hook and the tools: `.git/hooks/reference-transaction`; the tools `store_refresh_daily.sh`,
    `refresh_integration_store.sh`, `rebuild_pinned.sh`, `seed_store.py` (its build path) and `heavy_slot.sh`;
    `merge_queue.py` (`promote`); `drafts/d4b/e0_run.sh`, `e2_run.py` and `w2_137_s5.sh`;
    `drafts/score-once/e4_window.sh`;
  - the records: W2-116's review (`reviews/w2-116.md`, both rounds), PAT-1-RESULT §2 and §5, FRESH-80-1 §2 items 10
    to 19, E3-SA-RESULT (the slip), and W2-88 §7.

## What I checked, and what holds

1. **The pin's code.**
   - The pin `pin-bcea09060ebc`, which `~/.local/bin/gov` points to, holds a `gov` package byte-identical to
     `c00d525f`'s `src/gov` (`diff -rq`: no difference).
   - Its `rebuild/` code is identical to `w2/integrate`'s. Integrate differs from the pin only in `cli/main.py`,
     `launch/` and `retrieval/rerank*.py`, and in `retrieve/` (W2-136, W2-137 and W2-138).
2. **Every update refreshes.**
   - The hook is installed in the shared `.git/hooks` and `core.hooksPath` is not set. It acts only on `committed`
     for `refs/heads/w2/integrate`.
   - Its environment is cleaned (`env -u PYTHONPATH …`, review F5) and its lock is the outer
     `W2-00-store.refresh.lock` with `flock -o` (F6, R2-F2). It runs the pinned `gov rebuild --integration` through
     `heavy_slot.sh`, and its log lines are dated.
   - **The evidence:** since the hook went in (11-07 14:21), `w2/integrate` moved 40 times, and
     `integration-store.log` holds 40 refreshes, one per head (the set of heads is equal to the reflog's).
     Every refresh switched, with no failure, refusal or lock wait.
   - The ready half `-a` is at `e66f2a6965ee`, which is integrate's head, with a clean tree.
3. **The double buffer.**
   - **The order:** the head is read under the lock (F1 fixed). The half being built is never the ready half. The
     link moves only by `os.replace`, and only when `_faults` comes back empty: both stores recreated, lexical
     `fresh`, the semantic facet available, and the half still at its head. A failed build leaves the link where it
     was.
   - **The plain form:** a search through `GOV_STORE` resolves the link once (F2 fixed in the pin).
   - **PAT-1:** 147 searches during a switch had 0 errors and 0 missing facets, and the answers changed from the old
     half to the new half exactly once.
   - **What is left:** only the `--root <link>` form still resolves the link once per facet in the pin (row S3).
4. **A continuation after a switch.**
   - The pin's `pool.reorder` compares a digest of the candidates' chunk ids with the one carried from page 1.
     Another store gives other candidates, and the request is refused with `CONTINUATION_INVALID`.
   - The same candidates give the same order. So a page is never skipped or repeated silently, which matches
     PAT-1 §5.
5. **The backstop.**
   - `store_refresh_daily.sh` has been running since 11-07 15:00 (pid 1668178). It runs with
     `SEED_REBUILD_CMD=rebuild_pinned.sh`, so it builds with the pinned code.
   - Its 18:00 pass on 11-07 ran and logged `fresh at 24e0e8b0f55d`.
6. **A store built by other code than the pin.**
   - `seed.code_fingerprint()` under the pin is `sha256:0d4e8ad06…`.
   - The stores' record in E0's clone and in both halves names exactly that fingerprint.
7. **The fresh 80's isolation (FRESH-80-1 items 12 and 13).**
   - **E0's clone:**
     - It is at `~/gov-os-runs/D4B/w4-e0/repo`, made by `git clone`, so it has no hook: only `.sample` files.
     - It is at `c00d525fd420`, with a clean tree.
     - Its store was written 2026-11-07 15:58:57 by the pinned code.
     - No later script rebuilt it: `w2_137_s5.sh` uses its own clone, and `e4_window.sh`/`e4_prep.sh` check the
       commit and that no rebuild happened since.
   - **The searches:**
     - The measure runs `gov retrieve` with `cwd=<clone>`.
     - `e0_run.sh` unsets `GOV_STORE`.
     - `e2_run.py`'s `search()` removes `GOV_STORE` and runs from the clone. Its readers have no tools.
   - **The sessions:**
     - The CTO's session has no `GOV_STORE`.
     - Ticket leads get none (W2-136's `build_lead_settings`).
     - Only launched workers get it, and the guard refuses them the hidden part (path-map, DEC-873).
   - **What the 80 shares with the integration store:** the embedder and reranker services, and the heavy slots.
     It does not share the store.

## Findings

No finding is FIX BEFORE THE 80. Seven rows.

- **S1: the twice-daily backstop runs only inside the CTO's Claude session.**
  - **The process:** pid 1668177/1668178, a child of the session's `claude` process (pid 1662058).
  - **Not scheduled anywhere else:** neither in `crontab` (which holds only `run_tick.sh`) nor in a systemd timer.
  - **The effect:** when that session ends, the backstop ends with it.
  - **The fix:** the hook stays the main path, but re-arm the backstop each session (as with `sentinel_check.sh`), or
    put it in the crontab.
  - Ordinary work: yes, because CTO sessions end and hand over often.
  - Consequence: other. A missed hook then waits for the next landing; nothing opens and no store is half-built.
  - Touches the 80: no.
  - → ROW.

- **S2: nothing raises an alarm when the refresh stalls or keeps failing.**
  - **The failure modes:**
    - `REBUILD_FAILED` (a failed build, a stale `index.lock`: review F3);
    - a `<link>.lock` held forever, because `fcntl.flock` waits without limit, and so does the hook's outer `flock`;
    - a hung stage.
  - **What happens:** each one leaves the link where it was and writes only to `integration-store.log`.
  - **What nobody watches:** no watcher reads the log or compares the ready half's head with integrate's.
    `sentinel_check.sh`, `interim_watch.sh` and `worktree_states.py` do neither.
  - **Why it matters:** the pin's results carry no store commit (W2-138 brings it at the lift). So the 201-commit
    staleness W2-88 §7 records could recur unseen, with every search answering from an old head.
  - **The fix:** one check, in the sentinel or the dispatcher's tick: `readlink` the link, take that half's
    `HEAD`, and compare it with integrate's head. Behind for more than N minutes means an inbox item.
  - Ordinary work: yes, because it happened before (11-04 to 11-06), and a held lock or a stale `index.lock` needs no
    unusual act.
  - Consequence: other. The store is stale but complete, and it fails closed.
  - Touches the 80: no.
  - → ROW.

- **S3 (carried from W2-116 R2-F1): in the pin, `gov retrieve --root ~/gov-os-worktrees/W2-00-store` still resolves
  the link once per facet.**
  - **The code:** `_store_root` returns a `--root` it was given unchanged.
  - **The effect:** a search that spans a switch can join two complete halves.
  - **Where it is fixed:** on integrate (W2-138's `resolved(root)`), live at the lift's re-pin.
  - **Seen:** PAT-1 saw no mixed answer.
  - Ordinary work: yes, because EMG's common rules use that form.
  - Consequence: other. Both halves are complete; nothing opens.
  - Touches the 80: no, because the 80 searches a plain clone, not the link.
  - → ROW.

- **S4 (carried from W2-116 F7, now heavier): the merge queue's `promote` is still live code.**
  - **What it does:** it rebuilds the standby half with the checkout's own code (`PYTHONPATH=<where>/src`,
    `merge_queue.py:509`), not the pin.
  - **What changed:** since W2-137 and W2-138, integrate's code is not the pin's. After a queue landing, the link
    would first point at a store built by newer code. Then the hook's refresh would find the code different and
    rebuild the other half with the seed refused, from cold.
  - **Dormant today:** the queue last ran on 11-02, and window 4's landings were made by hand.
  - **Feature-gated (DEC-803):** an entry criterion for restarting the queue. Retire `promote`, now that the hook is
    live, or have it build with the pinned `gov`.
  - Ordinary work: no today (the queue is idle); yes once the leads land through it.
  - Consequence: other. A store built by other code for a while, and an unseeded rebuild.
  - Touches the 80: no.
  - → ROW.

- **S5: FRESH-80-1 item 13's hold (no commit on `w2/integrate` during the 80) is kept by hand only.**
  - **Nothing enforces it:** the hook has no hold switch, and `heavy_slot.sh` honours no hold file.
  - **What a commit would do:** any commit during the 80 starts a refresh of about 30 s. It uses the shared embedder
    for the changed chunks and takes a heavy slot beside the measure and the reader's searches.
  - **What it cannot do:** reach E0's clone. That is checked in item 7 above.
  - **The only path to a figure:** batching on the shared embedder could shift a query vector slightly (E0b's padding
    conflicts show that batching moves vectors). E3-SA's slip (two such refreshes during live searches) read the GPU
    flat, and no figure was expected to move.
  - **A ride-along for item 19 (DEC-802):**
    - the fresh-80 runner writes integrate's head at its start and end, and the `integration-store.log` lines inside
      its window, into the result;
    - or a hold file that the hook honours (it skips and logs, and the next landing or the backstop catches up).
  - Ordinary work: yes, because it happened once (E3-SA, 11-07 about 19:30).
  - Consequence: other. At most noise well inside the reader's spread; no wrong store; nothing opens.
  - → ROW.

- **S6: the pinned measure strips `PYTHONPATH` and `GOV_TICKET` from `gov retrieve`'s environment, but not
  `GOV_STORE`.**
  - **The code:** `measure.py:499`, with `_runner` at `cwd=root` and no `--root`. Under W2-116's rule, `GOV_STORE`
    wins over the working folder.
  - **The effect:** a measure run in a session with `GOV_STORE` set would search the integration store, while its
    result names the clone and the clone's commit. The control on the visible 40 (within 2 of 34) need not catch
    that.
  - **Guarded today:**
    - `e0_run.sh` runs `unset GOV_STORE`, and `e2_run.py` strips it;
    - the CTO's and the leads' sessions have no `GOV_STORE`;
    - the guard refuses workers, the only sessions that have it, the hidden part.
  - **A ride-along for item 19:** the fresh-80 runner refuses to start while `GOV_STORE` is set, not only unsets it.
  - **After the lift:** a product row to have the measure pass `--root` or strip `GOV_STORE`.
  - Ordinary work: no, for the 80's judged run, which only the CTO can run, without the variable and through
    `e0_run.sh`'s unset.
  - Consequence: fails open (a wrong store under the right label), if it were hit.
  - → ROW.

- **S7: `e0_run.sh`, reused as it stands (FRESH-80-1 item 11: "the measure as E0 ran it"), rebuilds E0's clone's
  store before measuring.**
  - **The step:** `rebuild_pinned.sh "$C" --seed <the integration store's ready half>`.
  - **The conflict:** item 12 ("the clone and store unchanged") and item 13 ("no store rebuild").
  - **The result would still be a valid `c00d525f` store:** the seed is accepted because the code is the same, and
    the rebuild reconciles the store to the clone's tree.
  - **But not E0's store:** its vectors may differ by padding noise.
  - **A ride-along for item 19:**
    - the fresh-80 runner has no rebuild step;
    - the pre-flight records `store.db`'s sha256 now and checks it, together with
      `.gov-runtime/rebuild/record.json` `written_at` 2026-11-07T15:58:57, before and after the run.
  - Ordinary work: yes, because item 11 points the writer at `e0_run.sh`.
  - Consequence: other. The store would be equivalent rather than identical; the control checks the rest. Nothing
    opens.
  - → ROW.

## For the triage

- None of the seven blocks the 80.
- S5, S6 and S7 cost minutes each. They belong in the build of FRESH-80-1 item 19 (the fresh-80 runner and the
  pre-flight), which is still to be built and reviewed. So they ride along (DEC-802) rather than start a round.
- S2 is the row most worth doing soon after the 80, because a silent stall is the failure memory has already had once.

**Evidence:** no heavy run. My only scratch use was a temporary `git archive` copy of `c00d525f`'s `src/gov` in the
session scratchpad, now removed (the scratchpad: 6.5 MB, 861 inodes, shared with the session).

## Verdict: READY for the 80 (this aspect)

```verdict
{"kpis": [
  {"kpi": "store-refresh-every-update", "verdict": "pass", "findings": [
    {"id": "S1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "double-buffer-no-mixed-halves", "verdict": "pass", "findings": [
    {"id": "S3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
  {"kpi": "continuation-after-switch", "verdict": "pass", "findings": []},
  {"kpi": "failure-modes", "verdict": "pass", "findings": [
    {"id": "S2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "S4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
  {"kpi": "fresh-80-isolation", "verdict": "pass", "findings": [
    {"id": "S5", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
    {"id": "S6", "scope": "in", "ordinary_work": "no", "consequence": "fails open"},
    {"id": "S7", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
