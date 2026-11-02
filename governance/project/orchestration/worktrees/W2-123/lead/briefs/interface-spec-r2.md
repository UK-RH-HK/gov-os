## The outside of W2-123 run 2 (the lead's interface spec: the same text in both workers' briefs)

The ticket's new KPI line (now the **first** success line of `.tickets/DAEO-qzrq.md`, DEC-1026) says what must be
true; it does not say what the result names or how a test can shorten the waits. So that the test designer and the
engineer, working in parallel and never reading each other's work, meet on the same behaviour, the lead fixes these
public forms (a P3 reading of the lead, inside the ticket's paths, reversible; logged for the CTO). Everything not
fixed here is the implementer's choice, and the tests do not depend on it. Every name below is in the module
`gov.retrieval.semantic`, which today holds `TIMEOUT_S` (120.0, the per-request timeout), `BATCH`, `MODEL`,
`NO_EMBEDDING`, `refresh(root)` and `search(root, query, refresh=True)` (read it on `w2/integrate`).

### R1. What is retried

- Only the **chunk embedding of a rebuild**: each batch request (`/api/embed` with up to `BATCH` chunk texts) that the
  semantic stage sends to the shared runner at `OLLAMA_HOST` while it brings the vectors up to date (`refresh(root)`,
  which `gov rebuild`'s semantic stage calls, and `search(..., refresh=True)`, which runs the same build).
- A try is retried only when it **timed out**: the endpoint accepted the request but gave no complete answer within
  `TIMEOUT_S` seconds. Every other failure (nothing listening, an HTTP error, an answer that is not JSON or lacks a
  vector for each text) ends the stage at once, with no retry and the reason `NO_EMBEDDING` exactly as today.
- The question's embedding (`query_vector`, the CPU-only query server) and the model-list and process-list requests
  (`/api/tags`, `/api/ps`) are not retried: unchanged.

### R2. How many tries and how long

- `RETRY_WAITS_S`: a new module attribute, a tuple of the waits in seconds before the 2nd, 3rd, … try of one request,
  each larger than the one before. Default `(10.0, 30.0)`, so **at most three tries** per request, with a growing
  wait. The number of tries is `len(RETRY_WAITS_S) + 1`.
- Each try uses the existing per-request timeout `TIMEOUT_S` (unchanged at 120.0); no try waits longer for its answer.
- Both attributes are read at the time of each request, so a test may set `gov.retrieval.semantic.TIMEOUT_S` and
  `gov.retrieval.semantic.RETRY_WAITS_S` (for example to `0.5` and `(0.05, 0.1)`) in the process that runs the
  rebuild: in-process with `monkeypatch.setattr`, or in a child process through a small launcher script that sets
  them and then calls `gov.cli.main.main([...])`.
- A request that answers on a later try is used as if it had answered first: the rebuild goes on with the next batch.

### R3. What the result states

- `refresh(root)`'s report keeps its keys (`available`, `facet`, `state`, `reason`) and gains **`retries`**: a list,
  in the order of the requests, with one object for each batch request that timed out at least once:
  `{"tries": <int, the tries made for that request>, "waits_s": [<float, each wait taken before its 2nd, 3rd … try>],
  "embedded": <bool, whether its last try returned the vectors>}`. An empty list when no request timed out (also
  when nothing was sent to be embedded).
- **After the last failed try** the stage stops (no later batch is sent), `refresh` reports `available: False`,
  `state: "FACET_UNAVAILABLE"`, and its `reason` is exactly
  `f"{NO_EMBEDDING}: the request timed out at all {tries} tries (each under {TIMEOUT_S:g} s; waits {', '.join(f'{w:g} s' for w in RETRY_WAITS_S)})"`,
  e.g. `Ollama did not embed with qwen3-embedding:0.6b: the request timed out at all 3 tries (each under 120 s; waits
  10 s, 30 s)`. `gov rebuild --json` then shows the semantic stage `"status": "not_recreated"` with that `reason`
  (the rebuild command passes `refresh`'s reason through unchanged; its own code is outside this ticket's paths), so
  **the tries and waits are stated in the rebuild's result** when the stage fails.
- When a retried request finally answers, the stage ends `recreated` as today; the tries and waits are stated in
  `refresh`'s report (`retries`), not in the rebuild's JSON, whose semantic entry the rebuild command writes as
  `{"status": "recreated"}` (outside this ticket's paths).
- **Never a partial store reported as built:** after the last failed try, the vectors embedded by earlier batches may
  stay in the store (the next rebuild embeds only what is missing), but the store is not reported as built: the
  rebuild's semantic stage is `not_recreated`, and a search without refresh (`search(root, q, refresh=False)`) reports
  `FACET_UNAVAILABLE` with the reason `stale` and no hit.
