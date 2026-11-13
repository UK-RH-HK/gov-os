# SMART-WORK-6 — the GPU as a measured and scheduled resource in the Gov OS (DEC-1030 item 4, DEC-1003)

For the owner. KPI line proposals, as the earlier SMART-WORK packages were: each is applied to its ticket file when
you approve it (DEC-1003; `tools/applied_check.py` then checks it is in place).

## Why
In the night of 2026-11-01/02 the GPU crashed three times (`CUDA error: unknown error` at 23:54, 02:36 and 04:30 in
the shared embedder's log) and the shared embedding model reloaded at 04:34 with 0/29 layers on the GPU, about 30 to
100 times slower, for seven hours; 8 to 10 rerankers were running, and they put their model on the GPU whenever they
find one. Neither the CTO's dispatcher nor the morning package saw it (DEC-1029, DEC-1030). The CTO's tools now watch
it (the dispatcher's GPU pass, under review; `tools/server_log_scan.py` in the morning package). An adopted repository
with a GPU meets the same failure, so the product needs it too.

## W2-20 (`DAEO-r30l`), the machine-wide resource gate: two new lines
1. `'The gate measures the GPU as it measures CPU and memory: its memory used and total, its utilisation, and which processes hold it (an embedder, a reranker, other), read once per check; a machine with no GPU or an unreadable one is named in the answer, never an error [DEC-1030 item 4]'`
2. `'The gate schedules GPU memory: each kind of GPU work has a configured share (default: the embedding model first, then one shared reranker, then the rest), and a job that would push the embedder off the GPU waits (or runs its model on the CPU) instead of starting; the answer states the GPU room it saw [DEC-1030 items 2 and 4]'`

## W2-121 (`DAEO-cb2b`), `gov dispatch`: two new lines
3. `'Each pass reads the GPU state and, for each embedding server, its model''s layers on the GPU (from the server''s own log or API); a crash in a server''s log, or a model loaded with 0 layers on a GPU it is expected to use, writes one inbox item at once and one line for the sentinel, once per incident; the status shows the GPU, its holders and each model''s layers [DEC-1030 items 1 and 4]'`
4. `'The morning report lists every crash or error in the servers'' logs overnight (CUDA errors, runner exits, model loads and their layers, failed and timed-out requests with their counts), beside the nightly''s tests [DEC-1030 item 3]'`

## Recommendation
Approve lines 1 to 4. W2-20 is in progress (its next run starts by merging `w2/integrate`, DEC-1003 practice: the
lines ride that run); W2-121 has not started. Confidence high on the need; the share defaults in line 2 follow the
load-balancing plan's GPU section (coming with it), and can be set there.
