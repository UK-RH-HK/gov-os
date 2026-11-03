# Review: W2-54's six cases revised to DEC-1033 (`emg/w2-54-dec1033` at `31186ebfc2b7`)

Reviewer: a fresh independent auditor (Sonnet), read-only, 2026-11-02 ~19:57. **Copied by the CTO, verbatim in
substance, from the reviewer's return**: the guard refused the reviewer's own write to this folder (DEC-953 item 2: a
reviewer writes only in its record places; the CTO's brief named this scratch path by mistake). The reviewer took the
refusal and did not route round it (DEC-849).

## What was checked
Commit diff, DEC-798/DEC-1033/DEC-1039, `.tickets/DAEO-0rfi.md`, `src/gov/retrieval/semantic.py` and `ollama.py` at
`w2/integrate`. None of the four wrong-answer cases is weakened: a vector from the wrong model (`other-model`,
`nothing` unchanged); a search answered with no vector (unavailable with a reason, nothing cached, no fallback, nothing
to the shared runner); a query embedder stopped by a read (`_never_stopped` unchanged); two embedders started by two
reads (one-serving and nothing-stopped checks kept). Only the DEC-798 rule was removed. Deterministic; stand-ins only
(the file never names 11434 or 11435; `S._dead_port()`).

Run: `tests/acceptance/W2-54/test_w2_54_cpu_embedder.py`, 14 passed in 65.95 s through `heavy_slot.sh`, `-m "not local_only"`.

## Findings
- **F1** (out of scope): the README lists the two `shared_gpu` cases as stale under DEC-1033.
  Ordinary work: no, because only a lead runs them on the real servers and the queue never does.
  Consequence: other.
- **F2** (in scope, minor): `_started_alone_at` checks only the named GPU variables and `gpu_hidden`, so a start told an
  unnamed variable (such as `NVIDIA_VISIBLE_DEVICES`) would pass.
  Ordinary work: no, because the code passes the caller's environment through unchanged; it takes a deliberate code change.
  Consequence: other.

Triage (the CTO as moderator, DEC-1010): F1 and F2 are Wave 3 rows; F1 is also P-W2-54-SHARED-GPU-1 (the refactor).

```verdict
{"kpis": [
 {"kpi": "test_a_question_s_vector_from_the_query_embedder_is_used_whatever_device_it_reports_the_model_on[gpu, partial]", "verdict": "pass", "findings": []},
 {"kpi": "test_an_embedder_at_the_query_address_that_does_not_report_the_model_loaded_gives_no_query_vector[nothing, other-model]", "verdict": "pass", "findings": []},
 {"kpi": "test_a_read_starts_the_query_embedder_at_its_address_and_never_stops_it[GOV_OLLAMA_BIN, PATH, HOME]", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "test_two_reads_at_once_leave_one_query_embedder_serving_and_both_get_their_answer", "verdict": "pass", "findings": [{"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "shared_gpu cases (README note)", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}
]}
```
