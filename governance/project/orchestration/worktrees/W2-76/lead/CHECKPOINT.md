# W2-76 lead checkpoint (DAEO-tgk2), run 1

- Update (16:10): v1 rebuild done (exit 0, 307 s, held_by_caller true, wait 0.0, all stores recreated, secrets_s
  274.8 of codeintel_s 287.1). keyword_warn 0. gov check: exit 3, secrets indexing RED (truncated traceback; the
  secrets module alone exits 0), product traceability YELLOW (openspec absent; DEC-942 unrecorded citations).
  collect-only: `16786/16788 tests collected (2 deselected) in 23.49s`, no error. trailer gate: `DAEO-tgk2: 5 commits,
  5 judged, 0 lacking, 0 Implements item(s) not a decision or Contract id that resolves`. Full parallel phase started
  15:57:47 (`full.sh parallel`; first try failed at once on an unquoted PATH, fixed). Next: serial phase, gov check
  again, return PACKAGES.
- State (15:30): engineer eng-1 returned PACKAGES (session 938fc738), twelve fields present. Verification rebuild v1
  (new code, under `flock /tmp/gov-os-rebuild.lock timeout 3600`) running in the background: logs
  `log/rebuild-v1.{json,err,summary,exit}`. Next: gov check, keyword_warn, W1-27 code-index cases outside the
  sandbox, then the full run in the close's form (scope full), then return PACKAGES (P-W2-76-1).
- Branch head: 59b48d2ebbec. Commits: 320775831c50 (test designer), 2f6c3fda7827 and 59b48d2ebbec (engineer), each
  with Task DAEO-tgk2, Role, Implements DEC-939, Co-Authored-By.
- P-W2-76-1 (package, lead-verified): `test_w2_76_watchdog.py::test_a_slow_rebuild_records_what_it_waits_on_and_goes_on`
  runs an unslowed rebuild first and then the slowed one on the same tree; the lexical index is incremental by blob,
  so the second rebuild's lexical stage judges nothing and the planted filter shows in codeintel_s/secrets_s, not
  lexical_s. Recommendation (a): a fresh test designer revises the setup (slowed rebuild first on its tree, or the
  baseline on its own tree), Rewrite-Reason, no expectation lowered. Code unchanged.
- P-W2-76-2 (engineer's scratch, 443,071 files in its sandbox temp): settled by the launcher, which removed
  `/tmp/gov-launch-engineer-rz1m24k5` when the session ended (checked 15:15).
- Lead runs: red (14:20) 21 failed / 1 passed; green1 (15:20, unsandboxed) W2-76 + tests/unit/rebuild: 46 passed,
  1 failed (P-W2-76-1 only).
- scoped_plan.py: scope full (UNPLACED: LEAD-w2-common.md, nightly.sh, push_emergency.sh, test_nightly.sh,
  w2-orchestrator.md; none changed by this ticket), base 94e7115cd59a, pytest_options
  `--ignore=/home/usain/gov-os-worktrees/W2-76/tests/acceptance/W2-76`, per_test_timeout 900.
- Loop count: implementation iteration 1 done.
- Workers:
  - td-1 (independent-test-designer, sandboxed, session de62ac96): DONE. Tripwire: W2-76 head + tests/acceptance/W2-76
    only; other trees changed by others (W2-64 head and dotfiles; W2-78 dotfiles gone). gov retrieve: told; used once.
    Refusals: 0 guard; 1 permission prompt (rm -rf of its probe folder).
  - eng-1 (engineer, sandboxed, session 938fc738): PACKAGES. Tripwire: W2-76 head only (and the sandbox's dotfile
    placeholders while it ran, gone after); main tree head moved, W2-64 head moved (others). gov retrieve: told; NOT
    used. Refusals: 2 (Monitor tool, DEC-685; rm -rf of its pytest folders). DEC-820 (c) slip reported by itself: a
    few traceback lines of test_w2_76_watchdog.py seen in pytest output.
  - Lines: about 470 product lines (command.py +87 -53, watch.py +384) and 124 builder-test lines, against 80.
- Left over: empty probe files `/tmp/gov-os-W2-76-held.lock`, `/dev/shm/gov-os-W2-76-held.lock` (guard refused rm).
- Brief gaps so far:
  - the launcher's sandbox lives in `src/gov/launch/launcher.py` (no `sandbox.py`) | this ticket's part | 2 min est.
  - existing suites' temp-repo rebuilds take the machine's real lock once pinned | this ticket's part | 10 min est.
  - removing the lead's own probe lock files in /tmp and /dev/shm is refused by the guard | common brief | 2 min est.
  - the lexical index is incremental by blob, so a second rebuild of a tree judges no file there | test designer brief (this ticket's part) | one package, a run
  - scoped_plan says full because of orchestrator record files changed since the last green base | common brief | 5 min est.
  - the engineer brief should say: read only `E ` lines of acceptance output (tracebacks show test source) | common brief | -
