The lead: two KPI decisions after your last commit (the CTO, delegated, recorded as DEC-1036; the ticket's KPI 6 line follows on `w2/integrate` within the hour; until then this text holds). Revise your tests in `/home/usain/gov-os-worktrees/W2-112-tests` under the same rules as before. Your first brief still holds in full: Policy 2 (c) and (d); `gov retrieve` from the W2-00-store only, with P-R1; the read refusals (DEC-849); DEC-732's `PYTHONPATH` rule; the guard's command forms; row W2-L423's rule; the scratch budget; no real model, GPU, Ollama or real lock files. Refused twice for the same call: stop and say so.

## The decisions (DEC-1036, the CTO's words)

- **T5 (b):** "below its GPU share the service does not start; searches fall back through the slot rule or go unranked, named (no reranker on the CPU anywhere, DEC-1033)." Your four T5 cases flip: the service below its share on the CPU, the CPU alert, and the bundle case naming the service on the CPU. Below its share (or with no GPU), no model may load anywhere on the CPU: the service does not start, and each search goes to the slot rule (a private reranker on the GPU if a slot is free and the stand-in GPU has room) or goes on unranked, named with its reason. Whether a "named" alert or log line still records the service's refusal to start is not stated: test that the reason reaches the bundle and the fallback log under `~/.cache/gov-os/`, nothing more specific.
- **T6 (b):** "the service holds one of the two GPU slots (it waits for a slot like any reranker, or fails named), so at most one private reranker beside it, about 10.5 GB with DEC-1032's 2 GB headroom kept." Add a case: with the service up (holding one slot) and the other slot held by your test, a fallback private reranker waits and then goes on unranked; and with both slots held before any service exists, the service cannot start on the GPU, so the search goes on unranked, named. Use the private lock folder (`GOV_RERANK_GPU_LOCK_DIR`) as before.

## Also from the lead's run outside the sandbox

- **DEC-1035:** P-W2-112-T2 is decided (c) now, with (a) as the new ticket W2-127. Your sandboxed-session case stands.
- The lead's red check of your suite against the base, run outside the sandbox, is in progress. If it shows a helper failure, you get the output in a later message. Do not change the socket helpers blindly.

## What you do

- Revise only `tests/acceptance/W2-112/` (README included). Run the suite to its end, never `-x`, and the collection line.
- Commit in one commit, with the trailers in the final block:

      git commit -m "W2-112 (DAEO-clon): tests follow DEC-1036 (no service on the CPU; the service holds a GPU slot)" --trailer "Task: DAEO-clon" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1036,DEC-1033,DEC-1032" --trailer "Rewrite-Reason: DEC-1036 (T5 b: no service on the CPU; T6 b: the service holds one of the two GPU slots)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

  First check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file. If DEC-1036 is not in the register on `w2/integrate` when you commit, the `Implements:` line still names it (the lead checks it before the return).

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Give: the commit hash (12 digits); the tests changed and why; the new count; the red run's counts and reasons; the collection line; the read refusals; your `gov retrieve` use and any P-R1 result served; your scratch figures.

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
