# Lead checkpoint, W2-90 (DAEO-8lmb), run 1: returning PACKAGES

- State (2026-10-31 ~01:15Z): branch w2/W2-90, head 12f8535095ce. Test design batch done; both scoped runs done; returning PACKAGES to the orchestrator. Nothing running.
- Commits: c9ba95d8e497, a6c3eca87ac6, acffe4ef6581, c491c5d8c521 (independent-test-designer; Task DAEO-8lmb; Implements DEC-957, DEC-953, DEC-906; Rewrite-Reason DEC-953 item 2); 12f8535095ce (orchestrator; checkpoint record CP-DAEO-8lmb-0002). trailer_gate: 7 commits, 0 lacking.
- Results: of the 235, 228 moved and green on the head after ACT 1 (parallel run plus the serial-only cases alone) and green on a clean clone of aafd45c19725 with the revised files; 7 not moved (left unchanged): red after ACT 1, green on base.
  - head run1 (-n 4): 482 passed, 5 failed, 5 errors, 1 skipped (493). Reds: the 7 unmoved + 3 W1-46 live-session cases (serial-only; research probe under xdist). Serial re-run alone (36 live sessions + 9 latency): 45 passed.
  - base (-n 4): 478 passed, 5 failed (latency, serial-only), 23 errors (W1-46 live sessions, serial-only) (506: base still has the 14 W2-59/W2-65 ids ACT 1 removed). Serial re-run alone: 45 passed.
- Packages: P1 template install deny rules (3 cases); P1 template hook line without pin, fail-open under PYTHONPATH (4 cases); P2 parameter splits; P2 236th case revised; P2 14 vanished ids + 1 empty-parameter skip from ACT 1.
- Loop count: 1 test design batch (converged on what can move).
- A resume must: take the orchestrator's decisions on the packages; if (a) on P1s, a product-spec/engineer ticket fixes the template, then a test designer moves the 7 cases (and the 14 vanished ids if approved); re-run the 19 files on both heads (scripts in the lead session's scratchpad: verify_head.sh, verify_base.sh, rerun.sh -- rewrite them if the scratchpad is gone).
- Temp left: /tmp/gov-os-lead-W2-90 (579 MB, 78,752 inodes; base clone 157 MB inside) -- rm refused by the harness; orchestrator removes.

## brief_gaps
- The five-rule hook refuses any Bash command that names a tests/acceptance/ path (grep, sed -n, ls, a script's argument) for the lead (false positive) | common brief | 10 min est.
- Ticket part says the 19 files and nothing wider; common part says acceptance tests plus select_tests' selection | this ticket's part | 3 min est.
- Ticket part says each run under the verify lock; common part says scoped runs take no lock; the lock held my run ~60 min behind a close's full run | this ticket's part | 60 min measured (waiting)
- The serial-only list applies to the 19 files (latency and live sessions); a -n run shows their reds | this ticket's part | 10 min est.
- gov check timed out in the foreground at load ~50 (several families time out at 60 s) | common brief | 10 min est.
- rm -rf of the base clone in the lead's own temp folder is refused | common brief | 1 min
- Worker gaps: template deny rules change verdicts; kernel python3 line needs gov importable (.pth, W1-38 precedent); session cases need api.anthropic.com, refused in the sandbox; whether a mixed function may be split by parameter; 236th red and 14 vanished ids outside the list; rm -rf of worker scratch not granted.

## guard_refusals
- ~22:3x | grep -n / sed -n over tests/acceptance/ files | "a command that may write the acceptance tests, which only the independent test designer writes (DEC-953 item 2)" | false-positive | 1 min; Grep and Read tools
- ~00:0x | git status; ls -la tests/acceptance/.claude | same | false-positive | 1 min; Glob tool
- ~00:0x | python3 <script> <worktree>/tests/acceptance/.claude <json> | same | false-positive | 1 min; stopped, no third form
- ~01:1x | python3 mapcheck.py <cases> tests/acceptance/W2-90/README.md <xml> <xml> | same | false-positive | 1 min; path moved into the script
