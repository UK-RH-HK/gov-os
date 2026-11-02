The lead: decisions on your packages, and a correction of KPI 7 made after your commit. Revise your tests in `/home/usain/gov-os-worktrees/W2-112-tests` accordingly, under the same rules as before (your brief still holds in full: Policy 2 (c) and (d), `gov retrieve` from the W2-00-store only with P-R1, the read refusals (DEC-849), DEC-732's `PYTHONPATH` rule, the guard's command forms, row W2-L423's rule, the scratch budget, no real model, GPU, Ollama or real lock files; refused twice for the same call, stop and say so).

## What changed (all on `w2/integrate`; read them with `git show w2/integrate:<path>`)

1. **KPI 7 corrected** (`.tickets/DAEO-clon.md` on `w2/integrate`, commit 9124fc25aa2a, DEC-1033): "When it lands, the stopgap that caps private rerankers on the GPU (...) is retired by an owner ACT the lead prepares, and when the service is down the search falls back to a private reranker through the GPU slot rule (it waits for one of the slots, else the search goes on unranked, named: `merge.reranked` false with its reason); it never runs a reranker on the CPU (DEC-1033: on the CPU a query takes over 100 s)". Your case expecting the fallback private reranker on the CPU now contradicts it. The GPU slot rule is described in `governance/project/orchestration/packages/ACT-RERANK-WAIT-1.md` and the module `governance/project/orchestration/tools/gov_reranker_gpu_slot.py` (both on `w2/integrate`; `GOV_RERANK_GPU_SLOTS`, `GOV_RERANK_GPU_LOCK_DIR`, `GOV_RERANK_GPU_WAIT_S`, `GOV_RERANK_ALLOW_CPU=1` for tests only). The KPI requires the rule to hold also after the owner removes that module from the environment (so your stand-in environment, which has no such module, must still see it obeyed): with a private lock folder (`GOV_RERANK_GPU_LOCK_DIR` in your temporary area, never `/tmp` itself) and both slots held by your test, a fallback search must wait (a short `GOV_RERANK_GPU_WAIT_S`) and then go on unranked, named with its reason, with no model loaded on the CPU; with a slot free, the private reranker loads on the GPU device of your stand-in.
2. **DEC-1034** (on `w2/integrate`, commits 1224cf1d and 2458fedd; read the register entry): (a) **T1 adopted:** `GOV_RERANK_IDLE_S` and `GOV_RERANK_TIMEOUT_S`, as your tests use them; the cap is well below 20,000. (b) **T3 (a):** "about 2 s" is the connection; the answer is bounded by the request's time limit. (c) **T4 (a):** the fallback log and the CPU alert go to a file under `~/.cache/gov-os/`, which `gov status` reads; the bundle names the device. (d) **The scope package granted:** `src/gov/retrieval/retrieve.py` and `src/gov/status/command.py` are now in the ticket's paths; the bundle carries a `rerank` entry (`unavailable` with its reason when unranked; otherwise which reranker answered and its device). Your surfaces tests are now ordinary KPI tests: update the README (no longer "depends on a package"). (e) **T2 goes to the owner as a P1; the ticket builds for (c):** a session that cannot create or reach the Unix socket (the launch sandbox) falls back exactly as for a service that is down, quickly and without an error. If you can express that as a test without a real sandbox (for example a session where creating a Unix socket fails), add one; otherwise say so.
3. **Your helpers that could not run in your sandbox** (the broken-service fakes, the raw socket client, the listening-socket check): the lead will run your suite outside the sandbox at the red check and will report any helper failure to you as its output; do not change them blindly now.
4. **W1-19's real-model case you named** stays untouched in this ticket (DEC-1033 item 3: revised afterwards by a test designer); keep it named in your return.

## What you do

- Revise only `tests/acceptance/W2-112/` (README included). Run the suite again to its end, never `-x` (inside your sandbox the socket cases fail as before; say which fail for that reason only), and the collection line.
- Commit in one commit, with the trailers in the final block, including the rewrite reason:

      git commit -m "W2-112 (DAEO-clon): tests follow corrected KPI 7 and DEC-1034" --trailer "Task: DAEO-clon" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1033,DEC-1034,DEC-1032" --trailer "Rewrite-Reason: KPI 7 corrected under DEC-1033 (no CPU reranker; the GPU slot rule); DEC-1034 items 2 and 3" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file.

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Give the commit hash (12 digits), the tests changed and why, the new test count, the red run's counts and reasons, the collection line, the read refusals, your `gov retrieve` use and any P-R1 result served, your scratch figures.

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
