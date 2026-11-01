# W2-123 (DAEO-qzrq) lead checkpoint

## Update (2026-11-01 23:45)
- Head 3dabcdaca633: e404e268f3fb (eng-1), 65627b745bf3 (merge of tests b87da348bbb2), 3dabcdaca633 (eng-2: no executable -> W1-18's result without settings; W1-18 unit test green). Tripwire 3 clean.
- Red check done: base 39 failed (reasons as README). On eng-1 code (lead's run, file by file): 38 passed, evidence 1 failed (no file yet). log/red-base, log/acc-eng1.
- gov accept refused ACCEPT_MAP_UNREADABLE (README KPI cells "1." / "Failure:"). TD resume 1: 34717de9e43a (S1-S6, F1). TD found 2 parametrized items "[1,4]" "[healthy,slow]" the matcher cannot read; resume 2 running (log/td-1-resume-2.json, tripwire-before-5.json) to use bare function names.
- measure2 (scratchpad/measure2.sh: 4 cases via the ticket's own ensure_available + check_determinism, separating cpus/nice, then a full-corpus stage at parallel 1 capped) waiting for a heavy slot since 23:25:45.
- Next: merge the TD's README commits (second merge), gov accept is the engineer's (eng-3 runs it), eng-3 writes evidence + final defaults from measure figures; then rebuild + verification.

## State (2026-11-01 23:25)
- Branch w2/W2-123 at e404e268f3fb (engineer batch 1: ollama.py +329/-8, tests/unit/retrieval/test_w2_123_embedding_cap.py 281 lines; trailers Task/Role/Implements DEC-1014, DEC-1017/Co-Authored-By: OK).
- Tests worktree /home/usain/gov-os-worktrees/W2-123-tests (w2/W2-123-tests): td-1 still running (gov launch, sandboxed; log/td-1.json; tripwire-before-1.json).
- Engineer eng-1: session 44fee5dc-a719-482c-a2e2-5486f9c31f07, returned PACKAGES with all twelve fields. Tripwire 2: in W2-123 only its commit + untracked pytest-of-usain/ (sandbox TMPDIR read-only, pytest fell back to cwd). The lead's rm -rf of it needs a permission prompt: name it in the return.
- rebuild-1 was cancelled while waiting for a slot (exit 143, no store). The engineer used W2-00-store for retrieval instead. Rebuild before measurement and verification.
- Sweep (KPI 3) running in heavy slot: scratchpad/sweep.jsonl (my session's scratchpad /tmp/claude-1000/.../scratchpad), server started by hand on 127.0.0.1:11444 with cap in preexec (same as the product), MEASURE_BY_HAND=1.

## Findings
- Ollama 0.35.0 forces runner.parallel=1 (-np 1) for the embedding model whatever OLLAMA_NUM_PARALLEL says (log sched.go:745 runner.parallel=1 with OLLAMA_NUM_PARALLEL:4; scratchpad/np_check.log). => "parallel requests" via Ollama's setting is a no-op for qwen3-embedding.
- The embedder is not bit-reproducible in the rebuild's batched form (97/384 differ on identical repeat at np 1, min cos 0.999427). Single-text, one in flight: exact. n in flight: 0-3/384 differ (min cos 0.9997). measure/det_matrix-2242.jsonl.
- Sweep so far (load 38-48): np1 capped alone 32.0 c/s, three 25.8 total (cores 2.6); uncapped alone 31.3, three 37.4 (cores 4.5). GPU 35-62 %. Capped loses under load via nice 10 (cores used < 8): add cases cpus 12-19 nice 0 to separate.

## Packages to return
- P-W2-123-1 (P1 to owner via CTO): Ollama pins embedding runners at -np 1; the ticket's parallel lever does not exist in Ollama 0.35.0. Options: (a) land the durable cap/config/probe/restart with parallel 1 chosen and the figures; real parallelism as a new ticket (several runner instances behind one address, or llama-server direct with -np, or a newer Ollama); (b) ...
- P-W2-123-2: KPI 2 byte-exact reading vs today's jitter in the rebuild's own batched form; also W2-122 K1 "every vector equal" cannot hold on the real embedder.
- P-1 (engineer): tests/unit/ollama/test_ollama.py:49 exact dict equality vs new `settings` key. Lead's reading pending the TD's tests: (A) path added (P2) or (B) settings omitted when no executable exists.
- Note for W2-20: its held gate.json reader refuses unknown keys; it must accept embedding_servers.

## Next
1. td-1 returns: check twelve fields, tripwire 1 compare, merge w2/W2-123-tests (--no-ff, message file trailers Task/Role orchestrator), write TESTS-READY, red check in W2-123-tests worktree.
2. After the sweep: rebuild this tree (rebuild_slot.sh), confirm one case through the engineer's own ensure_available + check_determinism (measure.py without MEASURE_BY_HAND).
3. eng-2: gov accept, P-1 resolution, measured defaults (probe defaults), evidence file from the figures.
4. Verify: select_tests, scoped parallel + serial, gov check, collect-only, trailer_gate, keyword_warn.

## Loop count: kept by lead.

## Brief gaps (running)
- No gate configuration file on w2/integrate (W2-20 unmerged) though KPIs 4 and 6 name it | the ticket file | ~15 min (est.)
- The KPIs name callables for the dispatcher without names; the lead had to fix an interface spec | this ticket's part | ~20 min (est.)
- Ollama ignores OLLAMA_NUM_PARALLEL for embedding models: the ticket's premise (SIZING-1 option 0) was untested | the ticket file / SIZING-1 | ~15 min (est.)
- Sandbox TMPDIR /tmp/gov-os-lead-W2-123 is read-only inside gov launch: pytest writes pytest-of-usain/ into the worktree | common brief / tool | 5 min (est.)
- A new worktree's rebuild waits for a heavy slot; the rule "rebuild before the first worker" cost the wait; used W2-00-store retrieval instead | common brief | ~15 min (measured wait 22:31-22:50)

## Guard refusals
- 23:22 | rm -rf of the engineer's pytest-of-usain/ in this worktree | permission prompt (not the five-rule hook) | true (DEC-922: no allow rule) | 1 min, named for the orchestrator
- engineer: 2 (verify_lock.sh with output redirected to scratch/eng; rm -rf pytest-of-usain), per its return
