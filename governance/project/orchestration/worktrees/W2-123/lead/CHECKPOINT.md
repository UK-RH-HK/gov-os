# W2-123 (DAEO-qzrq) lead checkpoint

## State (2026-11-02, run 2: the bounded retry, DEC-1026)
- Run 1 ended DONE at 9bb92097c811 (verified 17d88232b287); its record is in git history and packages.md.
- Run 2: merged w2/integrate at 94298e0a8 (--no-ff, Task DAEO-qzrq, Role orchestrator; clean). The ticket file now
  holds src/gov/retrieval/semantic.py and the new first success line (bounded retry).
- Lead's interface spec for run 2: briefs/interface-spec-r2.md (R1 what is retried: only a rebuild's chunk batches,
  only on time-out; R2 RETRY_WAITS_S = (10.0, 30.0), TIMEOUT_S unchanged; R3 refresh() gains `retries`, the failure
  reason is fixed, the rebuild's JSON states tries/waits only on failure because command.py is outside the paths).
- Tests worktree /home/usain/gov-os-worktrees/W2-123-tests (branch w2/W2-123-tests at 94298e0a8) added.
- Running in parallel (tripwire-before-7.json taken before both):
  - td-2 (independent-test-designer, sandboxed gov launch, cwd the tests worktree): log/td-2.json, log/td-2.exit
  - eng-4 (engineer, sandboxed gov launch, this worktree): log/eng-4.json, log/eng-4.exit
- Run 1's TESTS-READY renamed TESTS-READY.run1; the run-2 TESTS-READY must say "run 2".

## Done since (10:40 UTC)
- eng-4 returned DONE: 181bb54c0050 (engineer; trailers ok; semantic.py +34 -12, test_w2_123_retry.py unit +152).
- td-2 returned DONE: 0c97cee70eaa (test designer; trailers ok incl. Rewrite-Reason; retry tests 9 cases + README map).
- Red check by lead on base (tests worktree src): 9 failed, reasons as README (log/red-r2/).
- Merged tests at e17efc47ba15; TESTS-READY says run 2. gov accept (lead): 8/8 lines pass, 48 passed, 0 unmapped.
- Tests worktree removed (--force: only td's pytest temp, 13M) and branch deleted.
- Neither worker ran gov retrieve (both briefs said so). Both met the read-only TMPDIR in the sandbox: pytest-of-usain/
  in this worktree grew (engineer's runs).

## Next (now): verification under log/verify-r2/ (rebuild, select_tests, scoped run, serial, gov check, collect-only)

## Verification so far (log/verify-r2/)
- gov.__file__ -> /home/usain/gov-os-worktrees/W2-123/src/gov/__init__.py; select_tests: scoped, core_changed
  [src/gov/retrieval/ollama.py, src/gov/retrieval/semantic.py], unplaced []; collect-only 19266/19268 (2 deselected),
  exit 0; trailer_gate: 19 commits judged, 0 lacking; keyword_warn 0.
- rebuild 1 (10:39-11:12, exit 75): semantic not_recreated with the BARE NO_EMBEDDING after 1896.5 s (three rebuilds
  at once on the shared server): a non-time-out failure, so not retried by design. The failing batch (first missing)
  embedded fine at 11:20 in 2.6 s (probe_batch.log): transient. 2280 chunks missing then. Shared server pid 414672
  never restarted. => PACKAGE: extend the retry to transient non-time-out failures (HTTP 5xx / connection reset)?
- rebuild 2 (incremental) started ~11:21: log/verify-r2/rebuild-2.{log,exit}. Then verify_r2.sh (scoped run once),
  then gov check in heavy_slot.

## Next (as first planned)
1. On td-2's return: tripwire compare, check twelve fields and commit trailers; merge w2/W2-123-tests when eng-4 is
   not running (message file, Task/Role trailers); write TESTS-READY ("run 2").
2. On eng-4's return: tripwire compare, trailers; then (after the merge) a fresh engineer batch (eng-5) runs gov accept
   only, if eng-4 did not.
3. Red check of the new tests at the merge base (scratch clone), the rebuild (rebuild_slot.sh), select_tests, the
   scoped run once (verify_lock.sh), output under log/verify-r2/; gov accept (all lines); collect-only; trailer_gate;
   keyword_warn; remove the tests worktree and branch; gov checkpoint record; return DONE with the head.

## Residual to name in the return
- On success after a retry, the rebuild's JSON shows only "recreated" (command.py outside the paths): tries/waits
  are in semantic.refresh's report then. A one-line follow-up in src/gov/rebuild/command.py if the owner wants it.

## Loop count: kept by lead. Brief gaps / guard refusals (run 2): none yet.
