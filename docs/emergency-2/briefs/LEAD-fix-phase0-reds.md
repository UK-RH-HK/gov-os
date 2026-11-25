# Lead brief: the 0.1.6 release suite's Phase 0 reds (three; fixes under W2-116 and W2-208)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-25. **Read `docs/emergency-2/briefs/LEAD-COMMON.md` first: every rule there applies** (never cut a `gov retrieve` result, list your retrieves, one trailer paragraph with no blank line before `Co-Authored-By`). Decide, never ask (I-10). Use `systematic-debugging`. **This blocks the 0.1.6 patch release: work fast and small.**

## The reds
The release full suite on `7b5650f44` (record `docs/close/nightly/NR-20261125T003933Z-7b5650f44543.json`; junit under `.gov-runtime/nightly/20261125T003933Z-7b5650f44543/`; it runs with `GOV_TESTS_OPTIN=weekly` and `PYTHONPATH=<tree>/src:<tree>/src/gov/close/pytest_plugin`) failed three cases after Phase 0 landed (`83bc050aa`, record `.gov-runtime/scratch/orchestrator/log/landings/phase0-memory-20261124.md`):
- `tests/acceptance/W2-116/test_w2_116_s2_when_due.py::test_s2_success_second_is_due_once_after_its_time_and_brings_the_store_to_the_branch_head`: "noon, after a merge, between the two times: expected not_due, got ... status switched". Phase 0's P0-1 deliberately made a store behind its branch head due (the owner's G-1, DEC-1241: the refresh retried, the store current). If S2 states the old rule, the test designer brings it to P0-1 (a store behind the head is due at any time) and keeps what S2 still rightly asserts (no refresh when the store is at the head). If instead the code is wrong, the engineer fixes it. Decide from DEC-1241 G-1, P0-1's K-line in `.tickets/DAEO-f58b.md` and W2-116's S2 line.
- `tests/acceptance/W2-208/test_w2_208_p0_3_kit_hook.py::test_p0_3_only_the_state_committed_refreshes[trunk]` and `[main]`: "the state `committed` on '<branch>' refreshed nothing" (log: `refresh-hook: try 1 of 3: gov rebuild --integration <branch> --when-due` then a JSON answer). Phase 0's lead had them green; the W2-207 lead found them red on a clean `w2/integrate` too (each took about 9 minutes). Find why outside the lead's run: which `gov` the hook runs in the rig (the pinned 0.1.5 at `~/.local/bin/gov` lacks P0-1's due rule), `PYTHONPATH` (Phase 0's lead kept it for the rig's shim), the store's state, the 9 minutes. Fix the cause (code or the rig, by the role that owns it).

## Where
Worktree `/home/usain/gov-os-worktrees/E2-fix-phase0-reds`, branch `e2/fix-phase0-reds` from `w2/integrate`. Code area: `src/gov/rebuild*`, the kit's `githooks/reference-transaction`, `src/gov/update/` (hook install only). Another lead (fix-walls) works in the memaudit walls.

## Green
The three cases green when run as the release suite runs them (`GOV_TESTS_OPTIN=weekly`, the PYTHONPATH above, node on PATH); W2-116, W2-208 folders green; then exactly the impact-selected suites (`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-f58b=e2/fix-phase0-reds --onto w2/integrate --select`), through the heavy slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; each red's cause in two lines and its fix; the cases before and after; the selected suites' summary; your retrieves.
