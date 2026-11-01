# W2-123 packages (draft, the lead)

## P-W2-123-1 — Ollama runs this embedding model one request at a time whatever it is told (P1: the plan's sizing option; a follow-up ticket is the owner's, DEC-974)
1. Context: DEC-1014 item 4 (SIZING-1 option 0) filed W2-123 to let the shared embedding server serve several requests
   at once (`OLLAMA_NUM_PARALLEL` / `-np`), so rebuilds stop queuing behind it.
2. What happened: Ollama 0.35.0 (the installed binary) reads `OLLAMA_NUM_PARALLEL` (its "server config" log line shows
   `OLLAMA_NUM_PARALLEL:4`) but loads the qwen3-embedding runner with `runner.parallel=1` and `-np 1` (sched.go:745;
   `measure/np_check-2314.log`). In all 8 sweep cases (parallel 1, 2, 4, 8, capped and not) the runner read `-np 1`
   (`measure/sweep-1.jsonl`). Throughput did not rise with the setting.
3. Why it matters: the ticket's lever does not exist with this Ollama and this model. The durable cap, the
   configuration, the probe, the safe restart and the determinism check are built and pass; the speed-up is not.
4. Options:
   (a) Land W2-123 as built, with parallel 1 chosen and the figures; real parallel embedding becomes a new ticket the
       owner may file (DEC-974): N runner instances (N `ollama serve` on N ports, the semantic stage spreading its
       batches) or `llama-server` started directly with `-np N`, each judged by the same determinism check. Cost: one
       new ticket (est. 150 lines), more GPU memory per instance (2.2 GiB each, measured). Risk: low.
   (b) Widen W2-123 now to several instances: a scope change (semantic.py outside its paths), a new round.
   (c) Ask the owner for a newer Ollama (an install, P1) and re-measure: no evidence a newer one lifts the pin.
5. Recommendation: (a), confidence high. Findings classification: none is a fail-open or loses work.
6. Blocks: nothing of W2-123's landing. Waiting costs nothing; the slot waits stay as they are until a follow-up.

## P-W2-123-2 — The embedder is not bit-for-bit reproducible even today (P1 for the owner: memory's acceptance, W2-15b's determinism line and W2-122's K1)
1. Context: KPI 2 asks that parallel requests give the same vector as one at a time, "to the stored precision"
   (float32, byte for byte, as the lead's interface S5 fixed).
2. What happened (`measure/det_matrix-2242.jsonl`, 384 chunks, a private server under the cap):
   - single-text requests, one in flight: exact on repeat, and exact at -np 1, 2, 4, 8;
   - the rebuild's own request form (32 texts per request), repeated at -np 1: 97 of 384 vectors differ
     (min cosine 0.999427, largest element difference 0.0077); the stored vectors differ from fresh ones in ~41 %;
   - single-text requests with n in flight: 0 to 4 of 256 differ (min cosine 0.9997), case by case at random.
   So today's cold rebuilds already give different vectors run to run, and two rebuilds sharing the server perturb
   each other's vectors.
3. Why it matters: a byte-exact determinism standard (W2-15b's embedder line, W2-122's K1 "every chunk's vector
   equal" against a cold rebuild) cannot hold on the real embedder; stand-in endpoints in tests hide it.
4. Options: (a) keep W2-123's check byte-exact (as built) as the gate for choosing a setting, and record the jitter
   as a fact for W2-122 and W2-15b; (b) define "the same vector" with a tolerance (cosine at least the measured floor
   of today's own repeat, 0.9994) in W2-15b/W2-122 by owner decision; (c) make the semantic stage reproducible at its
   source (one text per request, one in flight per server), a follow-up ticket, at a measured cost to be stated.
5. Recommendation: (a) now, and (b) or (c) decided with W2-122's landing; confidence medium.
6. Blocks: nothing of W2-123. It bears on W2-122's K1 claim on the real embedder.

## Lead's readings (P3, logged for the CTO)
- The interface S1-S6 (`briefs/interface-spec.md`): W2-20's `~/.gov-os/machine/gate.json`, section `embedding_servers`.
- P-1 (engineer): when no executable is found, the result is W1-18's exactly (no `settings`); otherwise S2.
- P-W2-123-TD-1 (a): the README's parametrized map items by their function names.

## For W2-20 (DAEO-r30l), a cross-stream note (P2)
- W2-20's held `gate.json` reader refuses any key outside its four (`set(given) - set(DEFAULTS)`): it must accept
  `embedding_servers` (W2-123's section) when it lands, or the gate shuts on the first configured cap.
