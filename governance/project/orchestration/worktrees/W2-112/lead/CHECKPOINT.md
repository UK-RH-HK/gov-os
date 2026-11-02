# Lead checkpoint — DAEO-clon (W2-112), run 1

State (2026-11-02 ~14:00). Branch w2/W2-112 head 566c68f0 (my merge of w2/integrate, Task DAEO-clon, Role orchestrator, Implements DEC-1033,DEC-1032). Base be02bb012537.
Tests worktree /home/usain/gov-os-worktrees/W2-112-tests (w2/W2-112-tests): td-1 commit b64cd652537c (37 tests, red 33/4 in sandbox; trailers OK; tripwire OK for our trees).

UPDATE ~15:20: eng-2 done 775c58eda031 (Implements DEC-1033,DEC-1032; DEC-1036 not yet in register). td-3 faa66e1a9d98 merged here acf04cbf. Red check 2 (clone): 41 failed / 10 passed, as stated. Lead's acceptance run on acf04cbf: 46 passed / 5 failed: 3 no-gpu cases = code fault (private worker loads on CPU when no GPU) -> engineer; 2 success-2 cases = answer form dispute -> CTO moderator decided (a): designer accepts {"scores":[...]} (DEC-1036). README map: bare test_x[param] items fail lines silently -> designer fixes; W2-96 runner row to Wave 3 parking. td-4 RUNNING (resume d071bd6e, log td-4.json, tripwire-before-5.json). Real-GPU measure DONE on 775c58eda031 (record /tmp/gov-os-lead-W2-112/measure/record-1.json; analysis in log via analyze.py): GPU 3171->6429 MiB peak (service ~3.26 GB) under 20 concurrent; with one private 9694; service RSS 1.68-1.79 GiB; cold 7.6 s; warm20 p50 2.32 p95 3.82; warm10 p50 1.09 p95 2.13; same answers 20/20 order identical, max diff 0; private load 4.18 s, 0.20 s/question; stop: SIGTERM, GPU back to 3163, socket file left (removed only on idle end); status fallbacks 0, refusals 0. Waiting: the ticket commit (DEC-1036 KPI 6 + three unit test paths) on w2/integrate.
Next: td-4 -> merge tests; eng-3 (no-gpu fix + Measured section; unit tests if integrate merged); verification; reviewer.

UPDATE ~14:45: eng-1 done: d26e5a2cd3bd (engineer, trailers OK; 21 builder tests; +358/-33 product). Tests merged here effd94b957c3 (td-2 a26963a87707). TESTS-READY written. Red check on base+tests in clone /tmp/gov-os-lead-W2-112/red (rm refused by permission prompt; 8363 inodes, 200M, orchestrator to remove): 36 failed, 9 passed, reasons as README (the 4 socket fakes pass outside the sandbox). DEC-1035 (T2 (c), W2-127), DEC-1036 (T5 b no CPU service; T6 b service holds a slot), P-W2-112-UNIT-1 (a): three unit test files join paths after the ticket commit lands on integrate (CTO tells me; then merge w2/integrate; then eng batch does them). Running now: eng-2 (resume 693e64e4, old form, log eng-2.json) and td-3 (resume d071bd6e, sandboxed, log td-3.json); tripwire-before-4.json. Measure scripts in .gov-runtime/scratch/lead/measure/ (prep_candidates.py done -> /tmp/gov-os-lead-W2-112/measure/candidates.json; driver.py, measure.py, analyze.py: rerank() direct, no Ollama).
Next: td-3 -> merge tests again; CTO's word -> merge integrate; eng-3: unit tests + gov accept + Measured figures; my measure after eng-2's final code; then verification (rebuild, select_tests, verify_lock), reviewer.

Running (older):
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
