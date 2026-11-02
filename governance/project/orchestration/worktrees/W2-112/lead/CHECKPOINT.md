# Lead checkpoint — DAEO-clon (W2-112), run 1

State (2026-11-02 13:10): base be02bb012537, tree clean at start. Tests worktree /home/usain/gov-os-worktrees/W2-112-tests (branch w2/W2-112-tests) added from HEAD.
- td-1 (independent-test-designer, xhigh, gov launch sandboxed, in the tests worktree): RUNNING. Log log/td-1.json, exit log/td-1.exit. Tripwire tripwire-before-1.json.
- rebuild-1 (rebuild_slot.sh, this worktree): RUNNING. Log log/rebuild-1.log, exit log/rebuild-1.exit.
- eng-1 (engineer, high, gov launch sandboxed, this worktree): brief written briefs/eng-1.md; starts after rebuild-1 ends.
Loop count: held by the lead.

Decided/known:
- Scope gap -> package P-W2-112-SCOPE-1 (P2): the bundle's `rerank: unavailable` / device marking needs src/gov/retrieval/retrieve.py; `gov status` fallback count needs src/gov/status/command.py; neither in allowed_paths. Engineer builds hooks inside paths; designer isolates such tests in their own file.
- Stopgap .pth fires inside the service too (takes a /tmp slot or hides GPU); engineer must decide and state.
- Real-GPU measurement: the lead's own session, after eng-1's commit; then eng-2 batch writes figures into the research doc and runs gov accept.

Next: wait rebuild-1 -> tripwire snapshot 2 -> launch eng-1. When td-1 returns: tripwire compare, check 12 fields, merge w2/W2-112-tests (no worker running here), write TESTS-READY, red check on base.

Brief gaps (running list):
- the tests worktree's own launch form (cd into -tests and its src) not spelled out | this ticket's part | 3 min est.
- where the bundle marking / gov status lines live vs allowed_paths | the ticket file | 10 min est.
