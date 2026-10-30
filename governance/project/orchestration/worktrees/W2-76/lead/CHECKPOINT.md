# W2-76 lead checkpoint (DAEO-tgk2), end of run 1: PACKAGES

## State (20:30, 2026-10-30)
- Branch w2/W2-76, head 744522864d75. Nothing running. Return: PACKAGES (P-W2-76-1, P-W2-76-3); P-W2-76-2 settled.
- Commits: 320775831c50 (independent-test-designer), 2f6c3fda7827 and 59b48d2ebbec (engineer), 744522864d75 (lead
  checkpoint record docs/checkpoints/DAEO-tgk2/CP-DAEO-tgk2-0003.md). All carry Task DAEO-tgk2, Role, Implements
  DEC-939, Co-Authored-By. trailer gate: 6 commits, 6 judged, 0 lacking, 0 bad Implements.
- Loop count: implementation iteration 1 (code unchanged since).

## Packages
- P-W2-76-1: `tests/acceptance/W2-76/test_w2_76_watchdog.py::test_a_slow_rebuild_records_what_it_waits_on_and_goes_on`
  asserts lexical_s >= 8 on the second rebuild of a tree the first rebuild indexed; the lexical index is incremental by
  blob, so that stage judges nothing; the planted filter shows in secrets_s/codeintel_s (10.5 s). Recommend: a fresh
  test designer revises the setup only (slowed rebuild first on its tree), Rewrite-Reason; no expectation lowered.
- P-W2-76-3: once pinned, every temp-repo rebuild in the existing suites takes /tmp/gov-os-rebuild.lock and waits
  behind real rebuilds of other sessions; full run: 10 failures + 2 errors, all "did not end within 180 s", each
  printing "waiting for the rebuild lock ... held by pid 1713011 (flock /tmp/gov-os-rebuild.lock python3 -m
  gov.cli.main rebuild --json)"; serial phase: two W2-69 rebuild cases the same. Alone: fail while a real rebuild
  holds the lock, pass once it is free. Blocks DONE. Options: (a) a lock-path override set by the test harness
  (root conftest or the close plugin) + reader in src/gov/rebuild; (b) the lock opt-in by a committed
  governance/project/rebuild.yaml; (c) each affected suite's fixture writes rebuild.yaml with its own lock (test
  designers of W1-07, W1-27, W1-41, W2-69, adopt...). Lead's recommendation: (a).

## Verification done (run 1)
- r0 rebuild (base code, wrapper): exit 0, 3007 s incl. ~30 min lock wait. v1 rebuild (new code, `flock
  /tmp/gov-os-rebuild.lock timeout 3600`): exit 0, 307 s, held_by_caller true, wait 0.0, all stores recreated,
  secrets_s 274.8 of codeintel_s 287.1, slow false, faults [].
- W2-76 + tests/unit/rebuild unsandboxed: 46 passed, 1 failed (P-W2-76-1).
- gov check: exit 3; secrets indexing RED (truncated traceback; `python3 -m gov.secrets` alone exit 0); product
  traceability YELLOW (openspec absent; core-decision-citations: DEC-942 unrecorded). Others GREEN.
- scoped_plan: full (UNPLACED governance files changed by the orchestrator since base 94e7115cd59a).
- Full parallel: 10 failed, 16541 passed, 31 skipped, 2 errors in 4082 s (P-W2-76-3 + W2-66 DEC-919 known red).
- Full serial: STOPPED at 19:49 after 36 of ~63 cases (held the verify lock while its rebuild cases queued on the
  machine lock; W2-87's full run waited): 5 F W1-02 p95 latency, 2 F W2-69 rebuild (lock wait).
- Alone: see log/alone.out.
- collect-only: `16786/16788 tests collected (2 deselected) in 23.49s`. keyword_warn: 0 files.

## What a resume must do
- Nothing until the orchestrator decides P-W2-76-1 and P-W2-76-3. Then: test designer revision (P-1), the fix for
  P-3 by its decided owner, the engineer if code changes, then the full verification in the close's form.

## Left over
- /tmp/gov-os-W2-76-held.lock, /dev/shm/gov-os-W2-76-held.lock (empty; the guard refused the lead's rm).
- /tmp/gov-os-lead-W2-76: 12,892 inodes, 112M (the lead's temp; cannot be removed by the lead, DEC-922).
- .gov-runtime: 2,794 inodes, 411M.

## Brief gaps
- the launcher's sandbox lives in src/gov/launch/launcher.py (no sandbox.py) | this ticket's part | 2 min est.
- existing suites' temp-repo rebuilds take the machine lock once it is the rebuild's own (became P-W2-76-3) | this ticket's part | ~4 h measured (full run + alone runs)
- the lexical index is incremental by blob (became P-W2-76-1) | this ticket's part (test designer's facts) | one run
- removing the lead's own probe files in /tmp and /dev/shm is refused by the guard | common brief | 2 min est.
- scoped_plan full because of orchestrator record files changed since the last green base | common brief | 5 min est.
- PATH holds Windows folders with spaces: unquoted PATH= in an env command fails (exit 127) | common brief | 2 min measured
- tracebacks of acceptance runs show test source: an engineer should read only E lines | common brief | -
- gov check truncates a failing check's stderr, so the secrets RED's cause is not visible | a tool | 10 min est.
