# Review: dispatcher v4.6 (DEC-1032/1033), uncommitted over v4.5

Reviewer: fresh, read-only. Tests: `tests/unit/orchestration/test_dispatcher.py`, 157 passed in 112.76 s. The dispatcher was never run for real. One scenario was reproduced by importing the module in isolation, with `inbox_item`, `log` and `now` replaced and a log file in the scratchpad.

ADR-0001 questions applied to each finding: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"

## Findings

### F1 (medium, in scope): a request caught in flight after an idle spell is flagged HUNG at once

- Scenario: an embedder is idle for at least `embed_stall_s` (180 s), because the query server gets about 2 tasks a minute and the shared one is quiet at night. A first request arrives. At the pass the request is in flight: `ss` shows one waiting socket (oldest 0.4 s), and the log has no completed task yet.
- Cause: `judge_progress` measures `quiet` from `last_progress_at`, which moves only on a task or a request. It does not move while the server is idle. The branch `elif conn["waiting"]: state = "HUNG" if quiet >= stall` then fires on the first waiting request. `oldest_wait_s` is never consulted.
- Reproduced: shared server idle 600 s, then one waiting socket with `oldest_s` 0.4 gives `HUNG`, and one `server-hung` inbox item is written.
- Effect: the false HUNG writes an inbox item and an inbox-stale line. For the shared server it also holds starts for the next pass. It clears on the next BUSY or IDLE pass, but the item is already written. This is the "busy embedder flagged hung (holding starts falsely)" case.
- Likelihood: roughly (request duration / pass interval) per query on a quiet server. That is rare per query but certain over days, and the query server is the likeliest.
- Fix: measure the stall from the later of the last progress and the moment a wait began, or require `oldest_wait_s >= embed_stall_s` or two consecutive waiting passes.
- Ordinary work: yes, because an ordinary first query after an idle spell triggers it.
- Consequence: other (a false hold and a false alert; no work lost).

### F2 (medium, in scope): failed requests count as progress, so a failing embedder is BUSY and a HUNG incident clears

- Scenario: the runner crashes or returns 500 on `POST /api/embed`, for example "model runner has unexpectedly stopped" in a restart loop. Ollama still writes `[GIN] ... | 500 | ... | POST "/api/embed"`.
- Cause: `REQ_DONE` matches any status. The regex `^\[GIN\] .*\|\s*POST\s+"/api/embed"` returns True for a 500 line (checked). Any such line sets `reqs > 0`, so the state is BUSY and `last_progress_at` is reset.
- Effect: a crash-looping or erroring embedder shows BUSY. A standing HUNG clears ("BUSY again"). v4.5's test request would have counted these as failures. This is a missed alert for a real fault.
- Fix: count only 2xx, or count 5xx separately as an error rate that is not progress.
- Ordinary work: yes, because runner errors happen in ordinary use.
- Consequence: other (a missed alert; nothing is lost directly, but starts and rebuilds run against a failing server).

### F3 (low, in scope): `ss` counts a connection that has sent nothing and received nothing as a waiting request

- Cause: `-i` always prints `lastsnd`, so `sent` is always true. `bytes_received == 0` then makes any ESTAB connection with no data count as waiting.
- Effect: an idle pooled connection that has never carried a request, together with 180 s of quiet, would read as HUNG. This is not seen live. It is the same false-hold class as F1.
- Fix: require `bytes_sent > 0` for `sent`.
- Ordinary work: yes (rare).
- Consequence: other.

### F4 (low, in scope): the memory reservation for the rerankers is conservative and slow to relax

- Context: the 9.4 GiB comes from `kinds.reranker.rss_kb_p95` (9,884,288 kB, a 7-day window) via the v4.5 `outside_reranker_possible` branch. It applies only while a land or close run, or an outside reranker, exists. It is not new in this diff.
- New in this diff: `lead_cap` and `_admission_rules` now report it as "lead cap N". The cap is never stricter than the existing `need` check, because `need` uses `max(p95, own)` for every lead. So the cap adds no new refusals. Today it shows cap 1 with 3 leads running, so the refusal there is by CPU.
- Why the figure is stale: live rerankers hold about 2.2 GB each (3 rerankers, 6.6 GB). With at most 2 on the GPU and the rest ending, the true peak is far below 9.4 GiB. The p95 was set by the earlier CPU-reranker era and stays in the 7-day window for days.
- Scenario: a close or land run is active and `available - floor - slots (3 × 1.8 GB) - 9.4 GiB` is below one lead's p95. Admission refuses with cap 0 even when zero leads are running. It recovers when the run ends, because `outside_reranker_possible` becomes false, or when the old samples age out. It does not refuse forever, but it can idle the machine for the length of the land or close run.
- Not sound as a long-term figure: it should be recomputed from the post-DEC-1033 era only, or capped at `rerank_gpu_slots × per-process RSS`.
- Ordinary work: yes (land and close runs are routine).
- Consequence: other (lost throughput, transient).

### F5 (low, in scope): the GPU check is "not judged" when the read is missing, with no alert for that

- Scenario: nvidia-smi is unreadable or older than 300 s. `gpu_room` returns True ("not judged"), so admission lets work in while a GPU need exists.
- Effect: the status line shows it, but `gpu_stale_line` raises no item for an unreadable nvidia-smi. A multi-hour outage is silent apart from the status text.
- Exposure is bounded because the reranker GPU slots (2) and the rule that the rest end cap the real GPU use.
- Related: several starts in one pass each see the same `free_mib`. Pending launches are not subtracted, but the 2-slot limit bounds the damage.
- Ordinary work: yes (a driver or WSL hiccup).
- Consequence: fails open (for the machine), bounded.

### F6 (low, out of scope): heavy-slot reservation versus actual slots

- `slots_by_device` gives 2 when the shared embedder is on the CPU or partial. `heavy_slots.conf` is untouched, so 3 slots can still run.
- Memory for a third run is reserved only once it is held (`max(target, held)`). A slot that starts after an admission is under-reserved by about 1.9 GB.
- Ordinary work: no, because the 0-layer or partial state already raises an alert.
- Consequence: other.

### F7 (low, out of scope): partial-load alerts cover only the embedders

- Only the embedders' logs (`gpu_logs`) are read for "offloaded x/y layers". A reranker that loads partly on the GPU is not alerted.
- The reranker is covered instead by the GPU-memory check, the slot lock and the DEC-1033 patches.
- Ordinary work: no, because the emergency patch handles it.
- Consequence: other.

## Checked and sound

- Partial and zero loads: `watch_gpu` alerts once per incident (`zero_since`), covers the first read and a later reload, and ends the incident on a full load. The query server is exempt through `gpu_expected`. The incident also shows in `gpu_stale_line`.
- The first log read starts at the end of the log (baseline 0), so a restart does not give a false HUNG.
- Probe fallback when the shared log is unreadable; per-server exceptions are caught.
- NOT RUNNING needs 3 passes of "not listening". A shared server that is down in the test is held.
- Dispatcher duties: every new step is wrapped. `truth()` has try/except around the rerankers, `gpu_last` and `slots_by_device` (admission then fails closed, naming the cause). `lead_cap`, `balance` and `ss` failures never stop a pass. `status.json` is rewritten later with the balance. `ss` has a 10 s limit.
- `rerankers()` counts via `/proc/locks` and gives None when the table is unreadable, which is priced as "a slot free" (conservative).

## Verdict

```verdict
{"kpis": [
 {"kpi": "health-by-progress", "verdict": "fail", "findings": [
  {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
  {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
  {"id": "F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "admission-on-every-resource", "verdict": "pass", "findings": [
  {"id": "F4", "scope": "in", "ordinary_work": "yes", "consequence": "other"},
  {"id": "F5", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"},
  {"id": "F6", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "gpu-alerts", "verdict": "pass", "findings": [
  {"id": "F7", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "dispatcher-duties-unharmed", "verdict": "pass", "findings": []}
]}
```
