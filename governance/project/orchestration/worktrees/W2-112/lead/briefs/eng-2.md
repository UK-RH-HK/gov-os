The lead: your second batch. Your first brief still holds in full: unsandboxed under the guard, with the tripwire; Policy 2 (c) and (d), so never read `tests/acceptance/W2-112/`; `gov retrieve` with DEC-860 and DEC-859; the read refusals (DEC-849); DEC-732's `PYTHONPATH` rule; the guard's command forms; row W2-L423's rule; the scratch budget; a temporary `HOME` in every test; never the real GPU, Ollama or the real lock files from a test. Refused twice for the same call: stop and say so.

## Decided since your commit

- **DEC-1036 (the CTO, delegated; the ticket's KPI 6 lines follow on `w2/integrate`; until then this text holds):**
  - **T5 (b):** "below its GPU share the service does not start; searches fall back through the slot rule or go unranked, named (no reranker on the CPU anywhere, DEC-1033)." So the service never loads on the CPU, also when there is no GPU or the GPU is hidden. It records its refusal to start, with its reason, in the log under `~/.cache/gov-os/`, and the search's bundle carries the fallback's reason. Remove the CPU path of the service.
  - **T6 (b):** "the service holds one of the two GPU slots (it waits for a slot like any reranker, or fails named), so at most one private reranker beside it, about 10.5 GB with DEC-1032's 2 GB headroom kept; this reverses [the] earlier 'the service takes no slot'." So the service takes one of the same slot locks (`/tmp/gov-os-rerank-gpu-0.lock`, `-1.lock`; `GOV_RERANK_GPU_SLOTS`, `GOV_RERANK_GPU_LOCK_DIR`, `GOV_RERANK_GPU_WAIT_S`) before its free-memory check and before it loads, and holds it for its life. Without a slot within the wait, it ends named and the search falls back (a private worker then also waits for a slot, or goes on unranked). Order the checks so that the cold start's bound still holds for the search that started it. Update the docstrings and the research document (the design section, and the stopgap section: the service now takes a slot).
- **DEC-1034's P3s noted by the CTO:** the cap of 512 texts per request, the 60 s cold start, and the bundle's `rerank {by, device, reason}` stand.
- **DEC-1035:** the sandbox's Unix sockets are W2-127's (later); your fallback for a session that cannot make the socket stands.
- **P-W2-112-UNIT-1 decided (a):** `tests/unit/semantic/test_rerank_process.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py` and `tests/unit/status/test_status.py` join the ticket's paths. **The guard refuses them until the ticket commit lands on `w2/integrate` and the lead merges it: do not touch them in this batch.** A later batch does them.

## What you do in this batch

1. Build T5 (b) and T6 (b), with builder tests in `tests/unit/retrieval/test_w2_112_*.py` (the service takes a slot, waits, and ends named without one; no CPU service, with no GPU, the GPU hidden, or too little free). Run them and `tests/unit/retrieval` to their end. Commit.
2. **The acceptance tests are merged** (`.gov-runtime/scratch/lead/TESTS-READY` exists). After your commit, run them **once**, through `gov accept` only: `TMPDIR=/tmp/gov-os-lead-W2-112 PYTHONPATH=/home/usain/gov-os-worktrees/W2-112/src python3 -m gov.cli.main accept DAEO-clon`. Read only pass or fail per KPI line, the counts, and failure messages, never test source. Note: four cases still encode KPI 6 as it stood before DEC-1036 (the service on the CPU below its share, and its alert). A test designer is revising them now, so expect those to fail. Fix any other failure that is a fault in your code, commit, and run `gov accept` once more at most. A failure you think is a test's fault is returned as a package, never worked around.
3. Return. Leave the research document's "Measured" section to the lead's figures, as before.

Commit with the trailers in the final block: `--trailer "Task: DAEO-clon" --trailer "Role: engineer" --trailer "Implements: DEC-1036,DEC-1033,DEC-1032" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. If the register does not yet hold DEC-1036, use `Implements: DEC-1033,DEC-1032` and say so. Check the hooks folder first.

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Give: the commit hashes (12 digits); the files changed; the lines added and removed in product code; each test run with its counts; `gov accept`'s per-KPI result and counts, each time you ran it; the `gov.__file__` line; the read refusals; your `gov retrieve` use; files written outside the worktree; your scratch figures; packages.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so; no third try.
