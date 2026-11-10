# D-10 run 1 triage (session 8ddb8b14, 2026-11-10 ~19:20 UTC)

## Run 1 figures
- 16 workers (nproc 20), head afad23270a30, 18:10:09 -> 19:12:42 UTC. Nightly wall 3,749 s (62.5 min; nightly's own 3,420 s:
  setup 41, parallel 1,082 (pytest 991), serial 1,349 (pytest 1,220)).
- Swap: 4.2 GB in use before the run, peak 4.1 GB during, 2.4 GB after (the run added none); swap I/O in 40 of 114
  30 s samples, peak 3,264 KB/s, mean ~45 KB/s; min free+cache 9,268 MB. Memory never tight.
- Lifted step: ran nothing (exit 5, 1 s). d10_run.sh passed optin-lifted-guard.txt's two `rep:` lines to pytest as a
  path. Fixed: prefix stripped + tools/d10_lifted_only.py (keeps only lifted cases: 8,604, cf. D10-RUNTIME 8,596,
  ~1,370 s); LIFTED_ONLY=1 runs that step alone. Old script: tools/d10_run.sh.pre-lifted-fix.
- Red 168 (parallel 118 F + 44 E, serial 6). The nightly re-ran each alone: all 168 red alone too.

## Groups (168)
| grp | cases | where | cause | fix, role |
| A | 103 | W2-145 (55), W2-112 (46), W2-32 s4 (2) | test helper short_base() refuses /tmp itself (len(parts)<3); with TMPDIR unset no folder qualifies. Passes only where TMPDIR is a subfolder (Claude sessions) | harness: TMPDIR=/tmp/gov-d10 in d10_run.sh (no code); test fix by test designer (DEC-866) |
| B | 18 | W2-50 (17), W1-28 (1, to confirm) | gov launch LAUNCH_NO_TEMPLATE: fixtures plant worktrees without .claude/templates/role-<role>.md (templates 1.0.x) | fixtures by test designer; templates unchanged |
| C | 20 | W1-41 (16), W2-69 (3, serial), W1-06 (1) | tests/conftest.py hides codebase-memory-mcp from PATH except _CBM_SUITES {W1-16, W1-20} | add the suites to _CBM_SUITES (test designer; check class first) |
| D | 5 | tests/unit/orchestration/test_cto_safety_nets.py | reads the LIVE log/cto-standby.txt (stale, 412a4e37's 15:49 note) and appends to the live deadman.log | stale file retired 19:18; isolate the test (--standby/--log to tmp) |
| E | 6 | W2-131 (2), W2-135 (4) | bundle 'continuation' token differs from the recorded one | engineer: find the change since capture |
| F | 5 | W2-96 (3), W2-56 (2) | SIGHUP cases: pass in a plain shell (checked ~19:19); the detached launch's signal state | launch run 2 from a plain shell; no code |
| G | 8 | W2-54 (2), W1-01 (2), W2-61/61h (4) | records: context-reproducibility red #1 (DAEO-03dg 16,469 tokens > 6,000; DAEO-057v missing input); W1-01 DEC-253: merges cade65dfe, 04460404e, 8c512d7e7 settle tests/acceptance READMEs (acceptance_exemptions, path-map = control path, ACT); W2-61 gold q22/q23 drift + Table 2 lacks Q07/Q14 | records; red #2 (product-traceability) is lifted: shows only in the lifted step |
| H | 2 | W2-04 (damaged index not named by kind), W1-21 (batches differ) | product/test | engineer |
| I | 1 | W2-13 warm p95 0.577 s > 0.5 s (serial; alone too) | real-model latency | look at the embedder at the time |

## Incidents this session
- 18:55 outside-slot: run 1's own serial pytest (slots lifted on purpose). Closed.
- 19:17 sentinel-silent: my re-run of test_cto_safety_nets wrote a fixture line into the live deadman.log. Recovered 19:19.
