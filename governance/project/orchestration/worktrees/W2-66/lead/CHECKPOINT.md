# W2-66 (DAEO-c1uz) lead checkpoint

## State
- Run 1. Started 2026-10-23 10:35. Base head c2d539c6 on w2/W2-66.
- Head now 967f6205 (td-1's six commits: 14cd488a, 32cd885f [W1-30, Rewrite-Reason], 4c22e4aa, 6c45acd6, c05a31a5, 967f6205; all trailers checked: Task, Role: independent-test-designer, Implements: DEC-880, Co-Authored-By).
- pytest-timeout: absent at 10:35; present at ~11:35 (2.4.0 in ~/.local/lib/python3.12/site-packages; not in the tool registry yet; the orchestrator's install). So KPI 8 is built in this run.

## Decided (by the brief / register)
- W2-07 merges first; this ticket returns DONE unmerged; run 2 merges w2/integrate back, re-verifies, fresh FULL probe.
- Never write governance/project/path-map.yaml; test_inputs moves into the test map; its removal from the path map is the orchestrator's edit (name in return).
- Interface: td-1's INTERFACE payload (in log/td-1.json result) is passed verbatim to the engineer.

## Done
1. td-1 (sandboxed, gov launch, xhigh): DONE, 12 fields OK. session cd7a3fdc-fc87-4c79-8b41-b9ff19d5006f, 33 min. 139 cases (W2-66 134 + W1-30 5).
   - tripwire 1: worktree changes only tests/acceptance/W2-66, W1-30 and an empty harness folder tests/acceptance/.claude/.cc-writes (also in W2-58; invisible to git). Other trees: main tree head c2d539c6->c9a08678 (orchestrator's DEC-899/900 commits, W1-42 folder), W2-00-record head, W2-07 its own designer, W2-69 sandbox placeholder dotfiles (its lead's worker). None from td-1.
   - did NOT use gov retrieve (says so). Guard read refusals: 0. Other refusals: a cd&&pytest compound needing approval; rm -rf of its smoke temp refused.
2. Red check (lead): 133 failed, 6 passed, 136 s; every red for a README reason (64 no test map, 44 no evidence block, 4 no schema, 7 unknown --full/--check-result/nightly, 3 no report, 3 limit, 2 serial not scoped...). log/red.out, log/red.xml.

## Discoveries for the return
- KPI's src/gov/errors.py does not exist: it is src/gov/cli/errors.py (record correction for orchestrator).
- DEC-891 places hold code (orchestration/sync_context.py, docs/plan/tools/validate_s1.py, docs/plan/wave-1-exit/apply_adapter_output.py): record_only = DEC-891 minus those.
- Ticket names designer file test_w1_30_regression*, test lived in test_w1_30_close.py; revised in place (one function) + new test_w1_30_regression_scope.py.
- W1-30's original function would not turn red (no test map -> full) — revised to state its precondition and to require the refusal to name the failing test.
- --check-result + GOV_CLOSE_CHECK_RESULT: the close supplies the gate's result; W2-54's green-here cases still run gov check until a test designer revises them to read it (residual: outside this ticket's named files).
- TIMEOUT_PLUGIN_ABSENT: every close refuses where the runs' interpreter lacks pytest-timeout -> the re-pin's venv must hold pytest-timeout (risk for the return).

3. Lead checkpoint commit 1475b46c (CP-DAEO-c1uz-0002).
4. eng-1 (engineer, high, sandboxed, gov launch): DONE, 12 fields OK, session bfb46feb-c499-4428-944c-28170c2b03f8, 33 min.
   Commits 388d5892, 117b6e64, 528013b3, a8bf29f8, a384480a (trailers OK). +1417/-15 (est 400).
   Its runs: acceptance 136 pass / 3 fail (research report, deferred); tests/unit/close 398; W1-30+W2-01+W2-53 661.
   Tripwire 2: in W2-66 only the head; no acceptance folder change. Others: W2-07, W2-69 own work.
   No gov retrieve. Read refusals 3 (DEC-820 (c), its own over-wide ls/grep/scan of tests/acceptance).
   Packages it raised: failure text --tb=line (recommend defer W2-68); W2-54 green-here reading GOV_CLOSE_CHECK_RESULT (test revision, outside paths).
   Notes: JUnit under .gov-runtime/close/<ticket>/<stamp>/; nightly worktree in mkdtemp (not .gov-runtime), records/xml under .gov-runtime/nightly; nightly does `git worktree prune`; nightly does no rebuild (reviewer to judge).

## Next
- Verify (in progress): rebuild-1 (log/rebuild-1.*), import check, collect-only, parallel run, serial run, gov check.
- Then: eng-2 for docs/research/W2-66-scoped-close.md (KPI 11; measurement env TBD), review (A3, max), fixture trial, return.

## Loop count
- 1 (eng-1)

## Guard read refusals counted
- lead: 0; td-1: 0
