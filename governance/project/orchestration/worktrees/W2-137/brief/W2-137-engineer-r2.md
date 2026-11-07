Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-137/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-137 — the engineer's second pass (DAEO-5emz)

Your first pass is built (`dba3fa54`; `gov accept W2-137` 37/37). Read the ticket's "Built" section. One unit test still
pins the cap at 16 and is now in your paths (D-1):
`tests/unit/retrieval/test_w2_32_routing.py::test_routing_on_keeps_one_rerank_of_the_merged_set_in_full_requests_of_16`
(and its sibling `test_phrasings_on_rerank_the_merged_pool_once_within_the_bounds`, which checks `n <= 16`). Change only
their cap expectations to the cap in force (read `MAX_REQUEST_TEXTS`, not a new literal), each change commented
`DEC-1090 (2)`, keeping what they protect.

Your worktree `/home/usain/gov-os-worktrees/W2-137`, branch `w2/W2-137` (integrate merged). Run
`tests/unit/retrieval/test_w2_32_routing.py tests/unit/retrieval/test_w2_137_request_cap.py` through the heavy slot,
then `gov accept W2-137` again. The rules of your first brief (`W2-137-engineer.md`) hold. Commit with
`--trailer "Task: DAEO-5emz" --trailer "Implements: DEC-1090" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
Return the twelve fields, short.
