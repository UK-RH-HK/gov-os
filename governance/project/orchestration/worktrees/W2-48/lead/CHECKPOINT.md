# W2-48 (DAEO-xxgp) lead checkpoint

- Run 1. Base bdb96b77; branch w2/W2-48. Identity checked (orchestrator, DAEO-xxgp).
- Install gate: PASSED — pytest-testmon 2.2.0 + coverage 7.16.2 under ~/.local, installed 2026-10-20 14:17 (registry commit b0756906 on w2/integrate).
- td-1 DONE (session 1f74a191-3b6e-4d69-92fa-20ccec7b4456, sandboxed gov launch, xhigh): commit ceb4ec1d "acceptance tests, red", 46 tests, 12 files; twelve fields present. Tripwire 1: W2-48 head + acceptance W2-48 only (allowed); main tree head moved (orchestrator commits); W2-58 worktree ` M src/gov/guard/reads.py` (not ours).
- Packages from td-1: P-1 module commands `python3 -m gov.testcache run|command|nightly` (rec a); P-2 interpreter plant = venv same version (rec a); P-3 subprocess coverage as mechanism, always-re-run fallback (rec a); P-4 `src/gov/close/command.py` needed for --no-cache and the call (rec widen paths; BLOCKS close-level cases: close 7, leads 3, nightly 2).
- w2/integrate moved to 872874e6 (tool registry, DEC-871, checkpoint): merge it in before verification (DEC-750 form).
- Verified facts (lead's own run): testmon 2.2.0 crashes with -p no:cacheprovider (KeyError 'lf'); all-reused run = "no tests ran" (exit 5); testmon has no working subprocess support (sub_cov_file vestigial); coverage installed a1_coverage.pth (child measures only when COVERAGE_PROCESS_START/CONFIG reaches it, and only when ~/.local site is on its path — tests that build a fresh env/HOME lose it).
- Refusals: 1 write refusal (unresolvable variable in a Bash write target, my scratch test; redone with literal paths). Read refusals: 0.
- Loop count: held by lead.
- Next: CLOSE-RUNNING gate -> red check (W2-48 suite) -> engineer eng-1 (all in-path work; close wiring blocked by P-4) -> verify -> return PACKAGES (P-4).

- Red check DONE 16:06: 46 failed (34 no module gov.testcache, 11 no test_cache in close answer, 1 research record missing) = README reasons. log/red-1.txt
- Merge 9657051f (w2/integrate 872874e6 in, DEC-750 form). W2-53 now closed. integrate head f5738e5a (DAEO-0rfi checkpoint): merge again before verification.
- Containment flagged 8dfd54e9 (owner Role: owner commit, DEC-871) brought in by my merge: not ours.
- Next: eng-1 launched (briefs/eng-1.md, log/eng-1.json, tripwire-before-2.json).

- eng-1 DONE (session 71bddafd-ad32-4511-bab8-f543100b177d, sandboxed, high): commits 1df8233b, 635b690f (trailers ok). 32/46 pass; 12 held by P-4; 1 by P-A (timed figure); 1 P-C test defect (confirmed by lead: planted "ok\nok again" makes the fixture tool exit 1). unit 2387p/1s; W2-01 88p; W2-53 57p; W1-07 223p; W1-32 81p; collection ok. 1680 LOC added. Tripwire 2: W2-48 head only here; other trees changed by their own leads / W2-53 close.
- Merge f233b944 (integrate 0cbe240a), clean.
- Now: rebuild-1 (log/rebuild-1.*), then gov check, W2-48 suite, unit, timed uncached+cached runs (store in .gov-runtime/scratch/lead/testcache-store).

- Verify (lead): rebuild-1 ok 17:21-17:35; gov.__file__ -> worktree src; gov check: core-schema RED (docs/close/DAEO-7rr2/CL-DAEO-7rr2.md type close, from integrate, not ours), YELLOW core-decision-citations, openspec-validate. W2-48 32p/14f (12 P-4, 1 P-A, 1 P-C); unit 2387p 1s; collection 14752/14754 (2 deselected).
- Timed (store GOV_TESTCACHE_HOME in scratch): T0 unit uncached 47s, cached 53s (1152 reused/2388; 10 failures = builder tests nested under GOV_TESTCACHE_HOME, artefact confirmed: plain with var 9 fail, without 21 pass). T1 W1-01..15 running; then T2 W1-16, T3 W1-17..50, T4 W2-*.

- T1 W1-01..15: uncached 1275s (load 29) 5702p 1e 28s; cached 690s (load 16). 97% always_runs (4858 unmeasured process). W1-07 check_declarations: 2 errors through cache (copytree of session live repo, objects vanish; likely detached git gc race), plain passes. lead run discards pytest output (no failure text). T2 W1-16 running.

## END OF RUN 1 — status PACKAGES; head 17ddaf09
- T1 cached: 178 reused of 5731; 5 reds only in the cached half (W1-02 p95 [engineer-deny-outside-the-ticket], W1-05 p95 x3, W1-05 switch-over record). T2 W1-16: uncached 677s (load 42-93; 2f 1e secrets/token cases), cached 582s (0 reds; 15 reused of 167). Totals over 8,286 tests: reuse 1345 (16%), always-run 6912 (83%). W1-17..50 and W2-* not timed (load 40-90 from other sessions; re-measure on the final code).
- 17ddaf09 orchestrator: gov checkpoint record CP-DAEO-xxgp-0003 committed. Collection at head: 14752/14754 tests collected (2 deselected) in 6.77s.
- Packages returned: P-W2-48-4 (widen paths by src/gov/close/command.py; blocks 12 cases), P-W2-48-5 (near-zero saving on this repository as built), P-W2-48-6 (= P-C, declared-command fixture defect), P-1..P-3 confirmations, P-B test_inputs.
- Resume must: read the answers; if P-C, a fresh test designer revises that one case (Rewrite-Reason); a fresh engineer with the failing output only (wiring, cache-only false reds, pytest output for leads, GOV_TESTCACHE_HOME not inherited by tests, research figure); merge integrate; rebuild; full verification + timed pair; FULL review (max).
- Left behind: /tmp/gov-testcache-{05t8_upy,fpsxsi6u,qtd2k3iv,rphh0v_7} (my probes) and .gov-runtime/scratch/lead/testcache-store (27M SQLite) and testcache-probe: rm needed approval. DO NOT copy the stores into the repository.

## RUN 2 (resume after DEC-875, DEC-876)
- Identity ok; head was 17ddaf09, status clean.
- Merge 81f16a0b: w2/integrate (a90b2709; message says 65039414, integrate moved one W2-00 record commit during the merge) into w2/W2-48, DEC-750 form, trailers Task/Role/Implements in message. Brings DEC-874..876, test_inputs (fixtures/**, template/**, schemas/**), command.py in paths.
- td-2 launched (briefs/td-2.md, log/td-2.json, tripwire-before-3.json): P-W2-48-6 revision (Rewrite-Reason DEC-875) + DEC-876 cond. 1 proving cases (own-env child; git version) (Rewrite-Reason DEC-876).
- Plan: red check -> eng-2 (wiring, widenings, cache-only reds, lead-run failure output, GOV_TESTCACHE_HOME not inherited, simplify) -> verify (rebuild, all suites, unit, gov check, collection) -> timed pair (lead measures: uncached --no-cache; fill; engineer resumed plants a typical change uncommitted; cached run; engineer reverts + writes figures, commits) -> FULL review max -> probe record.
- Loop count: held by lead (run 2 iteration 1 starts at eng-2).
