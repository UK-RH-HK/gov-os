# W2-60a (DAEO-cv58) lead checkpoint, run 4 (resume, build) — LAUNCH_BLOCKED, 2026-11-13 ~01:15
task: DAEO-cv58
decisions_applied: DEC-826, DEC-1052, DEC-313 (the launcher's main-checkout check, working as built)

STATE: merge of w2/integrate IN PROGRESS in the tree (uncommitted, MERGE_HEAD 84cc42343ffb); launcher.py + 3 unit files resolved by engineer b11 (not yet git-added); 4 acceptance files still conflicted; no worker can launch | HEAD: 7ff4b82c9b3e | NEXT: once the main checkout's .claude/settings.local.json carries no permissions.additionalDirectories (CTO/owner, package P-1): LAUNCH_TICKET=DAEO-cv58 bash <tools>/launch_worker.sh --class C3 --model claude-opus-5-5 independent-test-designer high .gov-runtime/scratch/lead/briefs/b12-test-designer-merge.md | WAITING ON: package P-1 (launch refused), P-2 (S12 interface)
Workers: b11-engineer-merge (session 469c7ca8-4478-4fe8-bc76-125ee95598e8, exit 0, done) · b12 test designer: launch refused by the launcher's dry run (DEC-313) · Rounds: review rounds spent (DEC-1010); narrow check (DEC-1154) still to run · Paths: briefs/b11-*, b12-*; log/b11-engineer-merge.*; backup of the resolved files in merge-r4/

## Decisions taken (lead)
- launcher.py: `git checkout --theirs` (integrate's) so the engineer could be launched; b11 re-applied W2-60a's side onto it.
- Appended prompt: one --append-system-prompt-file <TMPDIR>/role-<role>.md = role file bytes + one blank line + .claude/templates/<stem>.md bytes, last after the caller's args; record gains template {path, sha256}. Lead launches: integrate's line unchanged.

## Then (after P-1)
1. b12: TD resolves tests/acceptance/W2-50/w2_50_support.py, W2-58/{README.md,test_w2_58_launched_sessions.py,w2_58_support.py}; plants templates + open gate in tests/acceptance/W2-60a fixtures.
2. lead: git add the 8 files; git commit (merge) with trailers.
3. S12 pair (after P-2 answers the interface); gov accept; rebuild; lead_verify; narrow check of W2-60a's own diff since e1a3e2214266; probe record (rename old to -round-3.md).

## Evidence so far
- tests/unit/launch W2-60a files (test_role, test_launch_record, test_runs, test_w1_28, test_w1_32): 95 passed, 11 deselected (lead, 01:06).
- b11: tests/unit/launch 280 passed, 16 failed (all other tickets' fixtures with no role file: test_w2_136_plan_check.py:239 x3, test_w2_153_template.py:109 x5, :118 x5, test_w2_56.py:369 [0],[3], :413).
