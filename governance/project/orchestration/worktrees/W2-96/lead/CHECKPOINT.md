# W2-96 (DAEO-ouet) lead checkpoint — run 2 (resume under DEC-968/DEC-970)

## Run 4 of the lead (the brief's "run 3"), under DEC-987 = P-W2-96-R4 (a)
- 04:20Z resumed at 943543cea0e8 (clean; merge of w2/integrate: DEC-983–987). Identity ok. /tmp/gov-os-lead-W2-96 had been removed (recreated empty). Disk gate open.
- Order (DEC-987): td-6 (2 W1 cases, harness form, red on head; + one bare rmdir of tests/acceptance/.claude/.cc-writes and parent) → merge -F → red check myself → eng-7 (subreaper + reap before clean-up; one gov accept, 108 cases) → rev-5 (A3 + JUDGEMENT, max, change alone; owner's exception to DEC-916) → rebuild, select_tests, scoped run via verify_lock.sh (nightly holds slots from 04:00, DEC-984; >90 min held → PACKAGES) → probe record (reviews 3, 4, 5) → DONE. rev-5 FAIL → PACKAGES, no 4th review.
- 04:22Z tests worktree W2-96-tests added (branch w2/W2-96-tests at 943543cea0e8). Tripwire snapshot 17. td-6 launched (high, sandboxed; briefs/td-6.md; log/td-6.json). eng-7 brief written (briefs/eng-7.md; HEAD_AFTER_MERGE placeholder to fill).
- 04:32Z td-6 (session 02d3df7b-85f7-42f9-a934-46d8f46914a8) DONE: 4b9353954f88 (test_w2_96_at_review_4.py: 2 cases + 1 premise; support, README), red 4/4; twelve fields ok. rmdir of W2-96/tests/acceptance/.claude/.cc-writes refused: "Read-only file system" (sandbox of the tests worktree cannot write W2-96). Tripwire 17: only W2-96-tests head + its W2-96 folder.
- 04:33Z merged 9d2d27e2b5bd (-F merge-r4.txt). TESTS-READY written. Red check (red_r5.sh, log/red-r5.*): 2 failed (both R16: processes alive at gov end; 6 entries later, marker) / 107 passed (162 s). gov.__file__ = W2-96/src. No orphans after.
- 04:37Z tripwire snapshot 18; eng-7 launched (engineer, high, sandboxed; log/eng-7.json).
- 04:49Z eng-7 (session aaade71a-d60f-45cd-9aea-6b49f21ab6b2) DONE: 44dbc90ee340 (runner.py +62/−4: subreaper, SIGKILL + waitpid by pid every 2 ms, bound 5 s, restore setting; test_w2_96_review4.py 14 cases; unit 95 pass). gov accept DAEO-ouet 109/109 exit 0 (106 + 2 cases + 1 premise; brief's 108 was my miscount). Twelve fields ok. Tripwire 18: only W2-96 head.
- Tests worktree removed, branch w2/W2-96-tests deleted. CP-DAEO-ouet-0024 committed c9daee7c9ce8 = the head review 5 probes.
- ~04:52Z rev-5 launched (independent-auditor, max; briefs/rev-5.md; log/rev-5.json; tripwire snapshot 19). verify5_chain.sh launched beside it (rebuild-5, check5, select5, keyword5, scratch5-before, then verify5.py via verify_lock.sh → parallel5/serial5). Held >90 min by the slots → checkpoint + PACKAGES.
- Next after rev-5: pass → docs/probes/DAEO-ouet/PR-DAEO-ouet.md (reviews 3, 4, 5; probed_commit = full id of c9daee7c9ce8), commit; collect-only; trailer_gate; cleanup; DONE. Fail → draft under probes/, PACKAGES.
- 05:15Z rebuild-5 ok (lock wait ~23 min). gov.__file__ W2-96/src. check5: RED secrets-indexing ("secret found in derived store"), YELLOW core-decision-citations (195), openspec-validate (absent). select5: scoped, core_changed [src/gov/check/commands.py], unplaced [], per_test_timeout 900. keyword_warn 0. Scratch before: /tmp 6.3M/1,633; .gov-runtime 500M/3,399.
- leak_scan.py (gitleaks dir --redact over the 116 files changed since rebuild-4): 1 hit, generic-api-key, tests/acceptance/W2-96/w2_96_support.py line 875 = `R16_TOKEN_KEY = "<env var name>"` (false positive, td-6's). Probe gate (close/command.py ~767) refuses any ticket commit on own paths after probed_commit → a rename after rev-5 = stale probe = 4th review (owner). Lead P3: stop rev-5 (~35 min in, no output) and the scoped run (3 min in, parallel only) at ~05:28Z; rename by fresh td-7; re-checkpoint; relaunch the third review on the new head; rebuild + scoped run again. Logs kept as rev-5-stopped.*, parallel5-stopped.out. Tripwire 19: nothing in W2-96 trees.
- ~05:31Z tests worktree re-added (w2/W2-96-tests at c9daee7c9ce8); tripwire snapshot 20; td-7 launched (high; briefs/td-7.md; rename + gitleaks + folder run).
- td-7 (session 70b5ad2a-b6da-4fcb-a6ab-9d60b793e910) DONE: d19019ca483e (R16_TOKEN_KEY → R16_RUN_VAR, 4 lines; RR trailer; gitleaks "no leaks found"; folder 109/109). Tripwire 20: only W2-96-tests head + folder. Merged d86588d5 (-F merge-r5.txt); tests worktree + branch removed. CP-DAEO-ouet-0025 committed 90122df096e7 = the head review 5 probes.
- ~05:45Z rev-5 relaunched (log/rev-5.json; tripwire snapshot 21); verify5_chain.sh relaunched (first chain's logs kept as log/a-*).
- 05:30Z rebuild-5 (2nd) ok 31 s; check5: ok, 23 checks, only YELLOW core-decision-citations (195) + openspec-validate (absent): secrets-indexing GREEN. select5 scoped, core_changed [src/gov/check/commands.py], unplaced [], 64 targets.
- 06:2xZ rev-5 (session cef1ac98-daa4-4f57-b407-8be31bccb127) PASS on 90122df096e7: W1 not reproduced (33 stops during nested pytest; positive control 3/3); X1 yes/other (held zombies → pid-probe tests fail closed; optional PKG-R5-X1, reviewer recommends (b) defer); X2 Wave 3 row. Tripwire 21: nothing changed anywhere. Result: log/rev-5-result.md.
- Scoped run (05:37–06:32Z, verify_lock heavy slot): parallel5 9 failed / 9472 passed / 4 skipped / 2 errors (W1-05 install ×2 err, W1-33 ×4, W1-46 ×1, W2-59 ×4: W2-90b's hook switch-over, as run 3); serial5 1 failed / 65 passed (W2-54 sandboxed_worker, as run 3). No W2-96/accept red.
- 06:3xZ probe record committed 220e2923 (docs/probes/DAEO-ouet/PR-DAEO-ouet.md; probed_commit full id of 90122df096e7). select6 identical to select5. collect-only "18747/18749 tests collected (2 deselected)". trailer_gate 37/37, 0 lacking. keyword_warn 0. Scratch end: /tmp/gov-os-lead-W2-96 301M / 37,843 (rm refused: permission prompt); .gov-runtime 515M / 3,445.
- END: return DONE. Branch head 220e2923 (clean). Left: /tmp/gov-os-lead-W2-96; tests/acceptance/.claude/.cc-writes (+ parent), empty, untracked (td-6's rmdir: read-only file system from the tests worktree's sandbox).
- (old) Next: merge (-F) → gov checkpoint commit → rev-5 relaunch (brief rev-5.md with new head/merge) → verify5_chain.sh again (rebuild-5b) → probe record → DONE.
- (old) Next: eng-7 returns → trailers/tripwire → checkpoint commit (gov checkpoint) → rev-5 (A3, max; briefs/rev-5.md; diff 9d2d27e2b5bd..eng commit + the 2 cases) → on pass: rebuild, select_tests, scoped run (verify_lock), probe record docs/probes/DAEO-ouet/ → DONE. FAIL → PACKAGES.

## Run 3 (resume under DEC-976; DEC-979: load wait unchanged until the heavy-job limit runs)
- 21:5xZ resumed at 064c69f8b785 (clean; merge of w2/integrate: W2-107, DEC-974–979). Load 7/11/13 on 20; disk gate open.
- 21:55Z tests worktree re-added detached at c348af6bc9ae (run-2 code 382e6d8f + review 3's cases); no branch. red_r4.sh started (whole folder, then review_3 file alone).
- 22:0xZ red check (log/red-r4.out, red-r4-file.out): whole folder 4 failed / 102 passed; review_3 file alone 4 failed / 2 premises passed; reasons as README (R14 races: crash/exit 4 + leftovers; R15: clean-up 6.8–7.1 s > 3 s). gov.__file__ = W2-96-tests/src (run-2 code). Tests worktree removed (detached, no branch).
- 22:1xZ eng-6b (resume of 7db40b77-6636-42a9-a111-3ffe1a6fb25f) DONE: gov accept DAEO-ouet 106/106, exit 0, first run; no commit. Twelve fields ok. Tripwire 14: nothing in W2-96 (only W2-86-tests, its own lead).
- 22:00Z checkpoint CP-DAEO-ouet-0019 committed 0e0883b80397 (the head review 4 probes). select4.json: scoped, core_changed [src/gov/check/commands.py], unplaced [], 64 targets, per_test_timeout 900 (added to verify4.py as the close does: --timeout=900 --timeout_method=signal).
- 22:01Z launched rev-4 (independent-auditor, max; briefs/rev-4.md; log/rev-4.json; tripwire snapshot 15) and rebuild4.sh (log/rebuild-4.*); after_rebuild4.sh chains gov check (log/check4.*) then run_verify4.sh (log/parallel4.*, serial4.*).
- Next: rev-4 result → pass: probe record docs/probes/DAEO-ouet/PR-DAEO-ouet.md (full probed_commit), commit; fail: draft under probes/, residual/package (last review of the round). Then collect-only, trailer_gate, td for rmdir .cc-writes (once), cleanup, return.
- 22:11Z rebuild-4 ok (116.4 s; lock wait ~8 min). gov.__file__ in W2-96/src. 22:18Z gov check: ok, 23 checks, YELLOW core-decision-citations (DECISION_UNRECORDED 195), openspec-validate (absent); all else green.
- 22:49Z rev-4 (session 6051140e-4d52-4a9e-9697-9c3eadf24f57) FAIL on W1 (yes / fails open per reviewer): stop of gov alone while a nested own-session pytest lives → 2.4–3.4 s after gov ends, 6 empty folders (outer test's name) recreated in caller TMPDIR by the nested pytest's report writer; not new with this head (exists at 382e6d8f). V1 fixed (76/76 stopped nested runs ok), `..` check closes a real escape, R15 linear. Rows W2 (silent give-up), W3 (link replacing private folder). Draft: probes/PR-DAEO-ouet-review-4-DRAFT-fail.md. Package PKG-R4: (a) apply (third review = owner's exception), (b) defer + brief line (stop by process tree), (c) re-baseline. Lead: W1 leaks names only (Policy 2 (c) lets the engineer see names; failure KPI 1 not met) → recommend (b), medium; (a) if owner holds the fails-open reading and grants a third review.
- Tripwire 15: nothing in W2-96 trees (others: their own leads, main tree).
- Scoped run (verify4) running since 22:18. Then: collect-only, td-5 (rmdir .cc-writes, briefs/td-5.md, once), cleanup, return PACKAGES.
- 23:30Z parallel4: 15 failed, 9451 passed, 4 skipped, 4 errors (1:09:29). Not this ticket's: W1-05 x2 (errors), W1-46 x1, W1-33 x4, W2-59 x4 (W2-90b's, DEC-977 item 4); W1-28 x1, W1-50 x4 (W2-108's copy, DEC-977 item 1); W2-54 green_here x2 errors (900 s per-test limit under load ~90).
- 00:03Z serial4 (13 entries): 12 failed, 54 passed (32:21). W1-05 hook p95 x9, W2-57 p95 x1 (P-LATENCY-1, DEC-979 D2); W2-54 sandboxed_worker, W2-54 time_limit (630 s under load). verify_lock.sh was rewritten mid-run at 23:50 (DEC-979 D1: heavy_slot.sh) → bash "unexpected EOF" at the end; exit 1 = pytest's.
- 00:04Z rerun4.sh: the W2-54 four and the 10 latency cases alone, through the heavy slot (log/rerun4.*).
- 00:24Z rerun4 alone (load ~31): 5 passed (W2-54 green_here x2, time_limit; W1-05 Edit-engineer, Glob-no-role), 9 failed: W1-05 p95 x7 + W2-57 p95 (113–226 ms; P-LATENCY-1), W2-54 sandboxed_worker (launched worker: ".claude/hooks/pretooluse.py" missing → hook switch-over not done; not this ticket's).
- 00:3xZ collect-only: "18734/18736 tests collected (2 deselected) in 21.43s", no error. trailer_gate: 27/27, 0 lacking. keyword_warn 0.
- 00:4xZ td-5 (session 6674c9a0-1567-4f9b-ac90-0344a2108cf4): rmdir of tests/acceptance/.claude/.cc-writes refused by permission prompt (one try); folder stays (empty, untracked). Tripwire 16: nothing in W2-96.
- Scratch at end: /tmp/gov-os-lead-W2-96 388 MB / 56,875 inodes (pytest-of-usain 328 MB: retained failing tests' folders; run 1's auditor folder 60 MB); .gov-runtime 499 MB / 3,336. Not removable (permission prompt).
- No commit after the probed head 0e0883b80397 (so a decision (b) can commit the probe record on it). Return PACKAGES: PKG-R4 (W1).
- RESUME: on PKG-R4 (a) [owner grants a third review]: td batch (W1 cases in harness form) in a tests worktree → merge (-F) → engineer (reap own-session descendants before clean-up) → gov accept once → review 5 (that change alone) → rebuild, select_tests, scoped run → probe record. On (b)/(c) or W1 judged "other": commit the probe record from probes/PR-DAEO-ouet-review-4-DRAFT-fail.md with judgement pass and the decision cited, on 0e0883b80397 (docs/probes/DAEO-ouet/), select_tests again, return DONE.
- Next (done above for eng-6): eng-6 resume (briefs/eng-6-resume.md, one gov accept on 106 cases) → rev-4 (A3, max; V1 + R14/R15 + `..` escape + processes outside the child's process group) → rebuild, gov check, collect-only, select_tests, scoped run, probe record → P3 rmdir .cc-writes (td) → cleanup → return.

## Run 2 END (returned PACKAGES 2026-10-31T17:30Z: load gate held 90 min)
- Branch head 162f8f4e (CP-DAEO-ouet-0016). Code head b3dd46f82321; tests merged a1d14a3f (106 cases). Tests worktree and branch removed.
- Done: R8–R13 (41b9fddd, 917aba42), review 3 (FAIL V1) → R14/R15 (b3dd46f8) + cases 588e43ae, c348af6b. gov accept 100/100 on b3dd46f8 before review 3's cases merged.
- Resume must: (1) red check of review 3's cases on run-2 code (scratch: tests at c348af6b over 382e6d8f — recreate a tests worktree from 382e6d8f + merge c348af6b, or accept td-4's two red runs); (2) resume engineer session 7db40b77-6636-42a9-a111-3ffe1a6fb25f with briefs/eng-6-resume.md (one gov accept run on 106 cases); (3) review 4 = second and last of run 2's round (DEC-916), on what changed since 382e6d8f (R14/R15, cases); (4) rebuild (store at 382e6d8f code; rebuild again before verification), select_tests (rerun), scoped run via run_verify3.sh (regenerate select3.json first); (5) probe record docs/probes/DAEO-ouet/ if review 4 passes; (6) remove tests/acceptance/.claude/.cc-writes (P3, needs a session allowed to rmdir).
- All of these wait on the load gate only.

## Run 2 state (2026-10-31)
- 12:00Z resumed at 549dd29b1c6f (clean). DEC-970: CMDLIST (a), PKG-1 (a), PKG-2 (c) + N2/N5/N7/N8. Addendum: design-r2.md (R8–R13 + README map forms for KPI 6).
- 12:03Z tests worktree /home/usain/gov-os-worktrees/W2-96-tests (branch w2/W2-96-tests from 549dd29b). Tripwire snapshot 9 (both workers).
- Launching td-3 (tests worktree, xhigh) and eng-5 (this worktree, high) in parallel. Next: merge w2/W2-96-tests (-F message file) when td-3 returns and eng-5 is not running; write TESTS-READY; resume eng-5 for one acceptance run; review 3 (effort max); rebuild, gov check, collect-only, select_tests, scoped run, W1-07/W1-32 command cases; probe record; checkpoint; cleanup (worktree, branch).
- 12:28Z eng-5 DONE (session 4e893242-3ac1-4506-94d6-3e8991f51230): 41b9fdddf109 (R8–R13, 59 unit pass; run-1 suite 72/7, the 7 R8 by design).
- 12:32Z td-3 DONE (session 7a404285-ffa8-46d8-9c09-779b6c8e7f9e): 1bf0c1d2e18f (W1-07/W1-32 lists, RR DEC-959 item 6), a5ad2254e97b (21 new + 7 revised, RR DEC-970). Package P-W2-96-R11-GROUP (keep the process-group variant) — lead decides P3 (a) keep. rmdir of .cc-writes refused (permission prompt). W1-26's recorded-commands gains [accept] variants (green once commands.py has accept).
- Tripwire 9: only W2-96 (head) and W2-96-tests (W1-07, W1-32, W2-96) — allowed. Other trees: their own leads.
- 12:37Z merged tests: 7bc8a030 (-F merge-r2.txt). TESTS-READY written. Tripwire snapshot 10 taken.
- 12:43Z load gate shut (load 82/72/55 on 20). Waiting before red check (tests worktree) and eng-5 resume (briefs/eng-5-resume.md).
- 13:20Z gate open. Red check (tests worktree, run-1 code): 23 failed / 77 passed, reasons as README (log/red-r2.out).
- 13:34Z eng-5 resumed (eng-5b): gov accept 1st exit 3 (R9 cases: signal after handlers restored killed gov) → fix 917aba42cd9c → 2nd exit 0, 100/100; unit 62; W1-07/W1-32/W1-26 recorded-command files 21 passed. Tripwire 10: only W2-96 head.
- 13:35Z checkpoint CP-DAEO-ouet-0013 committed 382e6d8fba8c (the head review 3 probes).
- select3.json: scoped, core_changed [src/gov/check/commands.py], unplaced [], 64 targets (W2-96, unit, W1-07/26/30/32, W2-16 …). keyword_warn 0.
- 13:36–13:54Z rebuild-3 ok (1117 s). gov.__file__ in W2-96/src.
- 13:57Z launched rev-3 (independent-auditor, max; log/rev-3.json) and run_verify3.sh (scoped run, gated; log/parallel3.*, serial3.*). Tripwire snapshot 11.
- Next: gov check (after rebuild), collect-only; on rev-3 pass → probe record docs/probes/DAEO-ouet/PR-DAEO-ouet-run-2.md, commit; cleanup worktree+branch; return.
- Slip: ran run-1 fill_rev2.py by mistake (rev-2.md rewritten, identical content).
- 14:30Z gov check (check3): RED context-reproducibility, product-traceability-trailers (time limits under load ~60), YELLOW core-decision-citations (time limit), openspec-validate (absent). collect-only 18548/18550, no error.
- 14:39Z rev-3 (session 2ddd0f47-0cc9-4858-a7bd-17c976e23674) FAIL: V1 yes/fails open (R10's removal stops at first error; own-session nested processes → crash + test-named leftovers on a stopped run); V2 row (quadratic removal; rides along), V3 row. Draft probes/PR-DAEO-ouet-review-3-DRAFT-fail.md. Tripwire 11: nothing in this ticket's trees.
- Stopped run_verify3.sh (never passed the gate). Tests worktree recreated from 382e6d8fba8c (branch deleted after merge, re-added).
- Fix batch (review 1 of 2 this round used): design-r3.md (R14 tolerant removal, R15 linear). briefs td-4.md, eng-6.md. Next: launch both; merge tests; resume eng-6; review 4 (the second and last of this round, DEC-916) on the final head; then rebuild? (only if needed: store unaffected by code? — rebuild again before verification on final head), select_tests, scoped run, probe record.
- 15:02Z eng-6 (session 7db40b77-6636-42a9-a111-3ffe1a6fb25f) DONE: b3dd46f82321 (R14/R15; unit 81; gov accept 100/100 exit 0). Its rm of own pytest temp refused (permission).
- 15:44Z td-4 (session 8d459332-fa40-4a9d-b500-4d668ab14513) PACKAGES: 588e43ae11ff (4 cases + 2 premises, red on run-2 code). P-W2-96-R9-PREMISE → lead P3 decision (a): resumed td-4 (td-4b) to tie run 2's R9 two-press case to the clean-up. Tripwire 12 ok; snapshot 13 taken.
- 15:52Z td-4b DONE: c348af6bc9ae (R9 two-press tied to clean-up; RR P-W2-96-R9-PREMISE (a)). Whole folder on run-2 code: 102/4 (review 3's four only). Tripwire 13 ok.
- 15:5xZ merged tests as a1d14a3f (-F merge-r3.txt); TESTS-READY updated; briefs/eng-6-resume.md written (resume session 7db40b77-6636-42a9-a111-3ffe1a6fb25f).
- 15:53Z red_r3.sh (gated) started; gate shut since (load 37–74 on 20). Held 90 min at ~17:23 → PACKAGES per DEC-943 if still shut.
- (old) Next: td-4b returns → red check on tests worktree (run-2 code) → merge (-F) → TESTS-READY → resume eng-6 for one acceptance run → rev-4 (last of round) → rebuild → scoped run → probe → return.
- Loop count run 2: 1 (eng-5b fix within the acceptance run), converged; review-3 fix round = iteration 2.
- tests/acceptance/.claude/.cc-writes/ still present at start; td-3 asked to rmdir once.

# Run 1 (end state, returned PACKAGES 2026-10-31T08:25Z)

## State
- Branch w2/W2-96, head e1c581ec09aa (final checkpoint CP-DAEO-ouet-0009; last probed head ea5728df2d9a). Base ab1ea26c5585. Tests worktree W2-96-tests and branch w2/W2-96-tests removed.
- Verification: rebuild-2 OK (06:06–06:30); gov check: RED context-reproducibility and retrieval-regression, YELLOW core-decision-citations (all time limits under load ~100), YELLOW openspec-validate (not on PATH); collect-only 17428/17430, no error; select_tests scoped, core_changed [], unplaced []; **scoped run NOT run**: held by verify_lock/gate_check 06:51–08:22 (load 23–158 on 20 CPUs, memory below need, 7 leads), stopped at 90 min (DEC-943).
- Commits (ticket): 73e50896445c (td, 54 cases) · 9859695c8fcc (eng, runner) · 986fa7cf4b1e (lead merge) · 6ec6cbd6e158 (lead checkpoint CP-0003) · d8ac34ff71de (eng, review 1 fixes R1–R7) · 3955f72177b6 (td, review 1 cases, Rewrite-Reason) · 382ef3b6c3d7 (lead merge) · 720a26fd4d7d (eng, counts of tests run only) · ea5728df2d9a (lead checkpoint CP-0007).
- Acceptance tests/acceptance/W2-96: 79 passed (eng-4 run 2); unit tests/unit/accept: 41 passed; `gov accept DAEO-ouet --json`: pass, 9 lines, exit 0 (eng-4 and rev-2).
- Review 1: FAIL (F2, F3, F6 yes/fails open; F1 yes/other) → fixed in d8ac34ff71de/720a26fd4d7d; rev-2 confirms F1, F2, F6 closed.
- Review 2 (second and last, DEC-413): FAIL on N1 (a table under a KPI heading whose header the reader does not take is dropped silently; W1-30's form). Drafts: probes/PR-DAEO-ouet-review-{1,2}-DRAFT-fail.md. No probe record committed.

## Packages (returned)
- P-W2-96-CMDLIST (P2): record `accept` in RECORDED_GOV_COMMANDS (src/gov/check/commands.py into allowed_paths) + test-designer revision of W1-07/W1-32 pinned lists (DEC-747). Red caused: W1-32 test_the_command_set_is_the_twelve_and_the_three_recorded_ones (not in the scoped selection).
- PKG-1 (P2, KPI 5): any failed/errored case, mapped or not, fails the run (exit 3). Reviewers 1 and 2 recommend; lead recommends (a), medium-high.
- PKG-2 (N1): (a) refuse such tables; (b) read them; (c) = PKG-1 (a). Lead: (c) with PKG-1, else (a).
- P-W2-96-TRIPWIRE4: empty tests/acceptance/.claude/.cc-writes/ left by review 1's sandbox (cd into tests/acceptance); remove before close.

## Resume (run 2) must
1. Get the decisions (CMDLIST, PKG-1, PKG-2). 2. Test design batch (tests worktree): N1 form(s) + ride-alongs N2 (hold SIGINT during clean-up), N5 (non-recursive unlock), N7 (keep inherited SIG_IGN for SIGHUP), N8 (exit 128+N after a held-back signal), PKG-1 per decision, W1-07/W1-32 revisions per CMDLIST. 3. Engineer: same + commands.py line. 4. Engineer runs acceptance once. 5. Review (new run's round). 6. Rebuild, scoped run, probe record, return.

## Loop count
1 fix round (review 1). Second review was the last of this run.

## Brief gaps (running list)
- command-list record outside allowed_paths (DEC-747) | ticket file | ~10 min
- rebuild lock queue 30+ min; store-less worktree; engineers retrieve from W2-00-store | common brief | ~45 min waiting (est.)
- gov retrieve hangs in sandboxed workers (embedder → ollama.com denied) | tool | ~3 min per worker
- engineer sandbox makes tests/acceptance read-only → engineer cannot merge the tests branch | common brief (TESTS-READY step) | ~15 min (extra engineer launch)
- .gov-runtime/scratch/<worker>/ refused to workers by permission settings | common brief | ~3 min per worker
- rm in own temp/scratch needs a permission prompt (non-interactive) | common brief | ~5 min
- guard false positives on printf > scratch file naming tests/acceptance and on pytest | sed | tool | ~5 min
- load gate shut for hours (load 40–75 on 20 CPUs) | machine | rebuild/scoped run waits
- the README map forms are stated nowhere for designers (KPI 6's brief change must include them) | skill test-design / brief template | review rounds
- reviewers' cd into repo subfolders leaves .claude/.cc-writes/ | common brief | ~5 min
