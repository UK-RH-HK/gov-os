The lead: your third batch. Your first brief still holds in full: unsandboxed under the guard, with the tripwire; Policy 2 (c) and (d), so never read `tests/acceptance/W2-112/`; `gov retrieve` with DEC-860 and DEC-859; the read refusals (DEC-849); DEC-732's `PYTHONPATH` rule; the guard's command forms; row W2-L423's rule; the scratch budget; a temporary `HOME` in every test; never the real GPU, Ollama or the real lock files from a test. Refused twice for the same call: stop and say so.

## 1. A fault: the failing output (the acceptance run, by the lead, on your commit 775c58eda031)

Three cases fail on the code; each is a KPI 7 / DEC-1033 / DEC-1036 rule (no reranker on the CPU anywhere, also when no GPU exists at all):

    FAILED test_w2_112_gpu.py::test_below_its_share_or_without_a_gpu_the_service_does_not_start_and_nothing_loads_on_the_cpu[no-gpu]
    E   AssertionError: search 1 with {'present': False}: a model was loaded on the CPU ([1718293]): no reranker runs on the CPU anywhere (DEC-1036, DEC-1033)
    FAILED test_w2_112_slots.py::test_a_fallback_never_runs_a_reranker_on_the_cpu[no-gpu]
    E   AssertionError: the fallback ran a reranker on the CPU (no-gpu): KPI 7 forbids it
    FAILED test_w2_112_bundle.py::test_below_its_share_the_bundle_never_names_the_cpu_and_gives_its_reason[no-gpu]
    E   AssertionError: the bundle names the CPU below the service's share of the GPU: {'by': 'private', 'device': 'cpu', 'reason': 'the shared reranker did not answer (ConnectionError: the service ended before it listened (the GPU has too little free memory for its share))'}

That is: with no GPU present (CUDA not available; the GPU not hidden by an environment variable), the private fallback worker loads its model on the CPU. It must end named instead (no model line, a reason on standard error), and the search goes on unranked with that reason, unless `GOV_RERANK_ALLOW_CPU=1`. Add a builder test.

Two other cases, the success-2 answer-form cases, fail on a test detail. The moderator decided that your answer object `{"scores": [...], "device": ...}` stays, and the test designer revises those cases. Change nothing for them.

## 2. The research document's "Measured" section (the lead's run on the real GPU, your commit 775c58eda031, 2026-11-02 14:11 UTC)

Write these figures into `docs/research/W2-112-shared-reranker.md`'s "Measured" section, with the method as run. Replace the method that sends `gov retrieve` searches with this one: the shared Ollama servers were never asked. Each measured "search" is a process that reranks one visible question's candidates through `gov.retrieval.rerank.rerank()`. The candidates are the lexical route's first 30 chunks for that question's text, in the form the search gives the reranker (`[path: …]` and the first 500 characters). There are 20 questions, `fixtures/evaluation/memory-retrieval/visible/q01`–`q20`; Q12 has 7 candidates, the rest 30. A sampler read `nvidia-smi` memory.used, the RSS of every reranker process and `free -b` every 0.25 s.
- **Before the run:** the GPU held 3,171 MiB of 16,303 MiB (the embedder, pinned in the shared Ollama server), RAM used 6.32 GiB; no GPU slot held.
- **Cold (1 search; it started the service and loaded the model):** 7.56 s wall; the service answered on `cuda:0`.
- **20 concurrent searches, warm:** all 20 answered by the one service process on `cuda:0`, none fell back; wall p50 2.32 s, p95 3.82 s, max 4.01 s (the whole phase 4.12 s); GPU memory used peak 6,429 MiB (embedder plus the service: the service's one copy about 3.26 GB; 9.9 GB free); the service's RSS 1.68 GiB; one reranker process of this tree.
- **10 concurrent searches, warm:** all 10 answered by the service on `cuda:0`; wall p50 1.09 s, p95 2.13 s; GPU peak 6,428 MiB; the service's RSS 1.69 GiB (peak over cold and warm: 1.79 GiB).
- **Before (a private reranker per search):** one private reranker started directly took 4.18 s to load on `cuda:0`, 0.20 s per question (p50), about 1.7 GiB RSS and about 3.3 GB of GPU memory each (GPU peak 9,694 MiB with the service and one private). With 10 searches at once that was up to 10 such processes; CAPACITY-1 measured 9 at once, 9.4 GiB at peak. Under the emergency interim (DEC-1033) at most two run on the GPU and the others go unranked after 20 s. After: one process, 1.7–1.8 GiB, whatever the number of searches.
- **The same answers:** for each of the 20 questions, the service's scores against one private reranker's on the same device (`cuda:0`): the order identical in 20 of 20, the largest score difference 0.
- **The stop:** the service ended on SIGTERM; the GPU's memory came back to 3,163 MiB (released); no reranker process of this tree left. `gov status`'s reranker part afterwards: 0 fallbacks, 0 service refusals.
- **A note:** on SIGTERM the service left its socket file (it removes it on its idle end). A later search starts a new service over the stale socket.
- **After W2-61h:** the 48 questions, not yet measured.

If you think the stale socket on SIGTERM should be removed (a signal handler, a few lines), do it with a builder test. Otherwise leave the note.

## 3. The three unit-test files (P-W2-112-UNIT-1 (a))

Only if the ticket file in this worktree lists `tests/unit/semantic/test_rerank_process.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py` and `tests/unit/status/test_status.py` in its `allowed_paths` (the lead merges that ticket commit before you start, if it has landed): revise their four out-of-date cases as you proposed (about 15 lines), and run those three files to their end. If the paths are not there, say so and leave them.

## 4. Then

Commit (trailers: `Task: DAEO-clon`, `Role: engineer`, `Implements: DEC-1036,DEC-1033,DEC-1032` if the register holds DEC-1036, else `DEC-1033,DEC-1032`, and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; check the hooks folder first). Run your builder tests and `tests/unit/retrieval` to their end. Then run `gov accept DAEO-clon` once and report its per-line result. The designer's revision of the answer-form cases and a corrected README map are merged (b8802d80), and the ticket commit with the three unit-test paths is merged (6b83a8b4). So every line should now report its own cases, failure-1 to failure-3 included. If a line fails, report it as it stands; do not chase it beyond one fix and one more `gov accept` run.

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Give: the commit hashes (12 digits); the files changed; the product lines added and removed in this batch and in total for the ticket; each test run with its counts; `gov accept`'s per-line result; the `gov.__file__` line; the read refusals; your `gov retrieve` use; files written outside the worktree; your scratch figures.

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
