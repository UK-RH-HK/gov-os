# Review: emg/query @ 75f18d1118c7 (DEC-1033 query-vector patch)

Method: read `git diff w2/integrate...emg/query`; ran the three named test files (61 passed); probed `query_vector` with stand-in `_ask` answers (no server touched).
ADR-0001 questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"

## Findings

### F1 (low, non-blocking): all-zero question vector is accepted and cached
- Scenario: the query embedder answers `[[...],[0.0, 0.0, ...]]` for the question (finite, one length). `_well_formed` passes; `_device` is cpu/gpu; the zero vector is cached under that device key and served on every later search of that text.
- Ordinary work: no, because a healthy Ollama does not return a zero embedding; only a faulty GPU/runner would.
- Consequence: other (a degenerate vector served permanently; ranking by cosine distance is meaningless for it).
- Scope: in (the patch's "well-formed" check is the new guard). Severity: low.
- Note: bool entries (`True`) are also packed as 1.0 and accepted. Same reasoning.

### F2 (low, non-blocking): a non-object JSON answer from `/api/embed` or `/api/tags` crashes retrieval
- Scenario: the endpoint returns a JSON list. `_embed` does `(_ask(...) or {}).get("embeddings")` and `_revision` does `.get("models")`, giving AttributeError out of `query_vector`. Probed: `CRASH AttributeError 'list' object has no attribute 'get'`.
- Ordinary work: no, because Ollama answers objects there.
- Consequence: other (crash, not a silent open). Scope: out (existing code; the patch hardened only `/api/ps`, with `_device` handling it). Severity: low.

### Checked and found sound
- Facet silently dropped on GPU: `_on_cpu`, `NOT_ON_CPU` and the `CUDA_VISIBLE_DEVICES=-1` hiding are gone. A GPU-computed vector is now used (gpu or partly offloaded). The remaining NOT_LOADED path (model absent or odd sizes in `/api/ps`) is a named reason, not silent, and applies only when the model is not reported loaded.
- Odd `/api/ps` answers (non-dict, non-list models, non-dict entries, bool, float or negative numbers, size 0) return None, so NOT_LOADED. No crash.
- Malformed vectors (NaN, inf, ragged, string or None entries, 1e300 overflow) give MALFORMED with nothing cached. The probe confirmed NaN and 1e300.
- Cache compatibility: the table `device_query_vector` and the key shape are unchanged, and existing entries use device "cpu", so they are still served. Round-3 drop still applies. The lookup tries cpu then gpu, both keyed with the model and revision, so no vector from another model or revision is served.
- Wrong vector from cache: a GPU vector is cached only under "gpu", and a CPU one under "cpu"; the owner accepted GPU drift (DEC-1033). Device is read after the computation, so labelling matches the compute except in a theoretical unload/reload race.
- Query server start: only `CUDA_VISIBLE_DEVICES=-1` was removed; `OLLAMA_HOST` is still set to the query address, and the server is never stopped. A pre-existing CPU-only query server (started by DEC-798) is still labelled "cpu" correctly. No unsafe start behaviour found.

## Verdict

```verdict
{"kpis": [
  {"kpi": "query-vector-any-device", "verdict": "pass", "findings": []},
  {"kpi": "no-wrong-or-lost-vectors", "verdict": "pass", "findings": [
    {"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
    {"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}
  ]}
]}
```
