## What you read

- The ticket file `.tickets/DAEO-qzrq.md` as the merge leaves it (read-only): success-7 now says the query server
  starts "with the GPU visible (DEC-1033, replacing DEC-798)"; success-8 says `ensure_query_available` starts the
  query server without hiding the GPU (no `CUDA_VISIBLE_DEVICES=-1`).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-1033 (it replaces DEC-798's CPU-only query embedder), DEC-1032,
  DEC-1014, DEC-1017, DEC-866.
- The two sides of the conflict: `git diff 6ed6a5ae^1 6ed6a5ae -- src/gov/retrieval/ollama.py` (the emergency patch:
  `NO_GPU` removed, `ensure_query_available` no longer adds it, docstrings say the GPU is left visible) and this
  branch's `ollama.py` (`git show HEAD:src/gov/retrieval/ollama.py`: run 1's capped start, which adds `NO_GPU` for
  the query server in its own start path, about line 207, and in `ensure_query_available`).
- The unit tests that read the query server's environment: `tests/unit/retrieval/test_w2_123_embedding_cap.py` (run 1's,
  yours to update), `tests/unit/retrieval/test_emg_query_device.py` and `tests/unit/retrieval/test_semantic_cpu_embedder.py`
  (the patch's; not in your paths: read only, they must pass).

## What to resolve

- **Keep both:** run 1's capped start exactly as it is for both servers (the configured or default CPU list, niceness
  and `OLLAMA_NUM_PARALLEL`, applied in the started process and inherited by its children; an unreadable value
  refuses the start; the `settings` in the result; the probe and the safe restart), **and** the patch's rule: the
  query server is started with the GPU left visible. No `CUDA_VISIBLE_DEVICES=-1` is added anywhere by the code (not
  in `ensure_query_available`, not in run 1's start path, not in a safe restart), and the caller's own environment
  reaches the daemon as it is. `NO_GPU` goes, as the patch removed it, unless something still needs the name (say so).
- Docstrings and comments follow the patch's wording (the query embedder, DEC-1033), with run 1's cap described.
- No other behaviour changes. `semantic.py` merged cleanly: do not edit it.
- **The cap on an automatic start (the CTO asks):** confirm, by a unit test of your own with a planted executable,
  that when the code itself starts the query server (`ensure_query_available` with nothing listening), the started
  process runs with the configured (or default) CPU list and niceness, the same as the shared server; say so in your
  return with the test's name.

## What you write

- Only `src/gov/retrieval/ollama.py` (the resolution) and `tests/unit/retrieval/test_w2_123*` (update run 1's unit
  tests that expected the hidden GPU; add the automatic-start cap test). Nothing else. If anything else needs a
  change, return a package naming it.
- Proportion (DEC-135). Say how many lines the resolution changed against `HEAD`.
- Check that no conflict marker is left anywhere: `git diff --check` and `grep -n "^<<<<<<<\|^>>>>>>>" src/gov/retrieval/ollama.py`.
- Run, to their end, never with `-x`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-123/src TMPDIR=/tmp/gov-os-lead-W2-123 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/verify_lock.sh python3 -m pytest tests/unit/ollama tests/unit/retrieval tests/unit/semantic -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (if `/tmp/gov-os-lead-W2-123` is read-only in your sandbox, use the sandbox's own `TMPDIR` and say so).

## Stage, do not commit

1. `git add src/gov/retrieval/ollama.py` and your unit test files. **Do not run `git commit` or `git merge`:** the lead
   commits the merge. Then `git status --short` and quote it (the merge's other files appear staged; that is the
   lead's merge).
2. Do not run the acceptance tests in this batch: the lead runs `gov accept` after the merge is committed and the
   designer's revised tests are merged.
