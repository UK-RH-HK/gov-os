# Lead checkpoint — DAEO-clon (W2-112), run 1

State (2026-11-02 ~14:00). Branch w2/W2-112 head 566c68f0 (my merge of w2/integrate, Task DAEO-clon, Role orchestrator, Implements DEC-1033,DEC-1032). Base be02bb012537.
Tests worktree /home/usain/gov-os-worktrees/W2-112-tests (w2/W2-112-tests): td-1 commit b64cd652537c (37 tests, red 33/4 in sandbox; trailers OK; tripwire OK for our trees).

Running:
- td-2 (designer resume, session d071bd6e, sandboxed, xhigh): rewrite for corrected KPI 7 + DEC-1034. Log log/td-2.json, exit log/td-2.exit, tripwire-before-2.json.
- rebuild-2 (incremental after merge): log/rebuild-2.log, exit log/rebuild-2.exit.
Next: after rebuild-2 -> tripwire snapshot 3 -> eng-1 in OLD launch form, unsandboxed (DEC-1034 item 1). When td-2 returns: tripwire compare, 12 fields, check trailers incl. Rewrite-Reason. When eng-1 returns: merge w2/W2-112-tests here, TESTS-READY, red check (scratch clone at merge base + tests), then eng batch 2 (gov accept + the measured figures in the research doc). Real-GPU measure is mine (lead session), <=20 concurrent searches, never touch 11434/11435, stop the service, confirm GPU memory released.

Decisions received (CTO, by SendMessage):
- DEC-1033: merge w2/integrate (done); interim slot rule (rerank_worker.py only; ALLOW_CPU for tests).
- CTO correction + ticket fix 9124fc25: fallback never on CPU; through the GPU slot rule; else unranked, named.
- DEC-1034: (1) engineer unsandboxed, old form + tripwire; (2) retrieve.py and status/command.py added to allowed_paths (2458fedd); (3) T1 GOV_RERANK_IDLE_S / GOV_RERANK_TIMEOUT_S; T3 (a) 2 s = connection; T4 (a) log under ~/.cache/gov-os/; (4) P-W2-112-T2 (sandbox refuses AF_UNIX) to the owner as P1; build for (c) fallback.
- Lead's reading given to the engineer: the slot rule moves into rerank_worker.py (so the ACT removing the .pth changes no behaviour).

Known for return:
- W1-19 test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment will need revision (DEC-1033 item 3), named by the designer.
- Designer's untracked scratch in its sandbox TMPDIR under /tmp/gov-os-lead-W2-112/gov-launch-independent-test-designer-*: retr1.json, retr1.err, torchinductor_usain (removal refused twice).
- tripwire-1 showed other sessions' changes in the main tree, EMG-query, W2-00-record, W2-122, W2-123-tests (not ours).
- rebuild-1: 2091 s (semantic 2030 s, cold, load ~30), "slow": true.
Loop count: held by the lead.

Brief gaps (running list):
- the tests worktree's own launch form (cd into -tests and its src) not spelled out | this ticket's part | 3 min est.
- where the bundle marking / gov status lines live vs allowed_paths | the ticket file | 10 min est.
- the launch sandbox refuses AF_UNIX: a Unix-socket ticket cannot be built or tested sandboxed | common brief / tool | 30 min est.
- the sandboxed designer's briefed TMPDIR is read-only inside the sandbox | common brief | 5 min est. (designer's)
- KPI 7 internally inconsistent after the correction (retire the slot module vs keep its rule) | the ticket file | 10 min est.
- cold rebuild 35 min under load before the first worker | tool | 35 min measured.
