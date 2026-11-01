# W2-05 (DAEO-0z8c) lead checkpoint — 2026-11-01 05:25, run 7 (resume under DEC-971, DEC-980)

## State: RETURNED DONE. H (DEC-971 item 3) and P-W2-05-W2-72 (DEC-980 item 2) done; the merge of w2/integrate done and reviewed; the round's two reviews passed; scoped run on the final code done; probe record committed.

- Branch `w2/W2-05`, head `8d2a1f540c95`, tree clean. Tests worktree and branch `w2/W2-05-tests` removed (the branch's config section was not left; `git branch -d` could not lock the shared `.git/config` because a read-only, empty `config.lock` dated 05:17 belongs to another process: not touched).
- Commits of run 7 (first parent, after b28866ba3b22):
  - `d1533bf30a10` lead merge of w2/integrate (f7f4fb5e1c88); conflict in src/gov/check/pathmap.py resolved: W2-95's code + `env=git_env(root, pinned=True)`.
  - `aedc72140fcb` td11 (DEC-971 item 3 cases, 14; W2-72's four cases on allowed routes, Rewrite-Reason DEC-802 (P-B1-2)), merged `4e225e7c63da`.
  - `1d9c0dca01b2` eng8: LIFTED_HOOK_EVENTS in src/gov/adapters/portability.py; tests/unit/gitenv/test_hooks_lifted.py.
  - `110125ddda0b` CP-0035 (rev6 head; rev6 PASS, rows R6-1, R6-2; its draft stays at probes/PR-DAEO-0z8c-dec971.md).
  - `a5b728d2f8a7` eng9: lexical `_git` pinned (R6-2; the planted gov close case was red after the merge, W2-108's freshness calls). tests/unit/gitenv/test_lexical_pinned.py; sweep row 24.
  - `e122beca7ef7` CP-0038 (rev7 head; rev7 PASS, rows R7-1..R7-3).
  - `8d2a1f540c95` probe record docs/probes/DAEO-0z8c/PR-DAEO-0z8c-dec971.md, alone (probed e122beca7ef7, full id).
- trailer_gate: 51 commits, 51 judged, 0 lacking, 0 bad. keyword_warn: 0.

## Verification (final code e122beca7ef7; the probe record is governance)
- Rebuild c ok (04:02); gov.__file__ in this worktree. select_tests: scoped, 73 targets, 81 options, core_changed 16, unplaced none (identical at 110125ddda0b and e122beca7ef7).
- Parallel parts (verify7.sh, runner_env, heavy slot, -o tmp_path_retention_policy=failed, JUnit): unit 3086 passed 1 skipped; W1 9708 passed 1 failed 1 skipped (52:40); W2 2269 passed 6 failed 2 skipped (25:44). Serial: 90 passed (17:12).
- Reds alone (05:05): W1-46 npm-install, W2-59 x4 (W2-90b's), W2-66 DEC-919 (conftest W2-05) red; W2-50 gov-check scale case PASSED alone (red in both full runs, alone at 02:19, and on integration code d88a1fff: flaky candidate under load, for the CTO).
- probe-record suites (W1-26, W1-08 probe) on the committed record: 50 passed.
- gov check (05:04-05:16): GREEN 21 (adapter-portability green), YELLOW core-decision-citations, openspec-validate.

## What a resume must do
- Nothing for H or W2-72. At merge (orchestrator): the nightly folder's pinned runs; sweep row 66 after W2-16's close (DEC-777 item 2).
- Rows for Wave 3 (or ride-along): R6-1, R7-1 (also correct sweep row 24's "such a file stale once"), R7-2 (sweep row 62 lapsed: W2-107 closed), R7-3; earlier R4-2..R5-4, N-1.

## Loop count: round DEC-971/980 converged (review 1 pass; verification red on our own case; one fix batch; review 2 pass).

## Scratch at end: /tmp/gov-os-lead-W2-05 1.4G, 148,688 inodes (removal refused by permission prompt: for the orchestrator); .gov-runtime 463M, 3,879 inodes. No /tmp/gov-launch-* of this ticket left.
