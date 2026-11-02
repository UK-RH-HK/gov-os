# Review: emg-rerank-slot (DEC-1033 interim reranker GPU-slot patch, uncommitted)

Reviewer: fresh read-only session. Subject: `governance/project/orchestration/tools/gov_reranker_gpu_slot.py` (rewritten) and `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`.

## Evidence
- `python3 -m pytest -q -p no:cacheprovider tests/unit/orchestration/test_gov_reranker_gpu_slot.py tests/unit/semantic/test_rerank_process.py`: 17 passed.
- Probed in a scratch venv (`--without-pip`, scratchpad, own lock dir; the installed venv and /tmp locks untouched), `python -I rerank_worker.py`:
  - non-worker `python -I -c`: untouched. A free slot: worker runs, slot recorded, CUDA_VISIBLE_DEVICES unset.
  - No slot within wait: named line, exit 75, nothing on stdout. GPU hidden (`-1`): named, exit 76. Bad GOV_RERANK_GPU_SLOTS, missing lock dir: named, exit 70, no traceback. SIGINT during the wait: named, exit 70.
  - GOV_RERANK_ALLOW_CPU=1 with no slot: CUDA_VISIBLE_DEVICES=-1, worker runs (explicit opt-out only).
  - Any other script named `rerank_worker.py` is treated as the worker (harmless; acts only on that name).
- The search side: `rerank._started` reads an empty first line, waits, returns None; `rerank` returns candidates as given; `retrieve` sets `reranked` false. A worker ended by this module is handled like the existing "no model" path. Not broken by the patch.

## Findings

### F1 (low): a forked child of the worker keeps the slot lock after the worker ends
Scenario: the worker forks (probe: `os.fork()` in the worker, child sleeps 6 s); the worker exits; a second worker with GOV_RERANK_GPU_SLOTS=1 got exit 75 while the child lived. `set_inheritable(False)` guards only exec, not fork.
Ordinary work: no, because the real worker (CrossEncoder load and predict) forks nothing; a child outliving the worker needs a torch/tokenizers multiprocessing fork.
Consequence: other
Scope: in. Bounded by the child's life; the effect is a slot unavailable (later searches go unranked), not a crowded GPU.

### F2 (low): GOV_RERANK_GPU_WAIT_S=nan (or inf) makes the wait unbounded
Scenario: env set to `nan`; with no free slot the loop never ends (probe killed by timeout 10). Hangs the search's `readline`.
Ordinary work: no, because only a hand-typed bad value does it; the default is 20.
Consequence: other (a hang)
Scope: in. Fix: reject non-finite or negative values and use the default, or end 70.

### F3 (low): one NO_SLOT makes the whole long-lived process unranked for its life
Scenario: `_started` is `lru_cache`d; a long-lived caller (the query server) that met busy slots once caches None and never reranks again, until restarted. Not new (a missing model did the same), but the 20 s wait now makes a transient busy state permanent.
Ordinary work: yes, because the slots are shared by concurrent searches.
Consequence: other (quality degraded, named once on stderr; no failure, no lost work)
Scope: out (rerank.py, not this patch). Advisory.

### F4 (advisory): the module cannot see a GPU that is not there
Scenario: a host with no CUDA device, or the WSL driver dropped, and CUDA_VISIBLE_DEVICES unset: the worker takes a slot, the library chooses the CPU, and it grinds. The module checks the variable, not CUDA availability.
Ordinary work: no on the owner's GPU host; yes on a GPU-less host.
Consequence: fails open (CPU grind)
Scope: out of what the interim patch can check without importing torch; a worker-side `cuda.is_available()` check would close it. Not blocking for the interim.

### Cost noted, not a defect
A search waits up to 20 s (default) at start-up when both slots are busy, then goes on unranked. Bounded; matches the owner's "waits for one".

## Verdict
```verdict
{"kpis": [
 {"kpi": "no-cpu-grind-no-gpu-crowding", "verdict": "pass",
  "findings": [
   {"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "F4", "scope": "out", "ordinary_work": "no on the GPU host", "consequence": "fails open"}]},
 {"kpi": "search-goes-on-unranked-never-fails", "verdict": "pass",
  "findings": [
   {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"},
   {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}
]}
```
No blocking findings.
