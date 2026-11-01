You are the ticket lead for ticket `DAEO-57hm` (`W2-95`, core-pathmap checks what it says), profile STANDARD, priority 0 (the owner, DEC-959 item 9: a check that checks nothing is fixed in Wave 2). You work only in the worktree `/home/usain/gov-os-worktrees/W2-95` on branch `w2/W2-95`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `7dda3297a761`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:** the ticket file (`.tickets/DAEO-57hm.md`); `governance/project/orchestration/packages/P-W2-H064.md` (the fault: `src/gov/check/pathmap.py:40-49` returns no finding when `namespaces` is a mapping, which this repository's path map is, or when the path map cannot be parsed); DEC-959 item 9, DEC-954, DEC-694, DEC-381; the path map's schema (`src/gov/config/path_map_schema.py`, `path-map.schema.json`) and loader (`src/gov/config/loader.py`), for the mapping form; how `gov check` runs a core check (`src/gov/check/`).

## The decisions for this run
- **The work order in parallel (DEC-959 item 7, DEC-963, the common brief's loop):** the independent test designer in the tests worktree (`/home/usain/gov-os-worktrees/W2-95-tests`, retrieving only from the integration branch's store) and the engineer in this worktree start at the same time, both from the KPIs. Tests in `tests/acceptance/W2-95/`, planted path maps in temporary repositories (the mapping form and the list form; a path in none, a path in two, an unreadable path map), never this repository's own path map. The engineer changes `src/gov/check/pathmap.py` and adds `tests/unit/check/test_w2_95*` only; when TESTS-READY appears, it merges the tests branch and runs the acceptance tests once.
- **This repository's own result:** after the fix, run `gov check`'s core-pathmap on this worktree and report what it finds (paths in no namespace, paths in two). Do not change the path map: it is shared, and W2-87 holds a block of it. The findings go in your return as a list for the orchestrator (a follow-up, not a round).
- **Fail closed:** a path map that cannot be read or parsed is a finding, never green; a form the schema does not state is a finding.
- **Running beside you:** W2-64 holds `src/gov/check/schema.py` (not yours); W2-16, W2-20 and W2-37 hold `src/gov/check/commands.py` (not yours). Touch only `pathmap.py` and your unit tests.
- **Verification (DEC-959 item 1):** your acceptance suite and unit tests, plus `select_tests.py` once before returning; `src/gov/check` is likely core, so a full run through `verify_lock.sh` if it says so.
- **Budget:** about 4 to 6 hours. Scratch: 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-95`.

Return DONE (commits, suites, this repository's core-pathmap findings) or PACKAGES.


**DEC-968 (owner, 2026-10-31), overriding anything above about a full run:** never run the full suite, whatever your change, core included: the nightly runs it once a day. Your verification is the scoped set `select_tests.py` gives (always `scoped` now; for a core change it names `core_changed` and selects every suite the change can reach), run once before you return, in the close's form. A case that fails there and that your change did not cause (it fails on `w2/integrate` too) is named in your return for the CTO to deal with at once; one your change caused is yours to fix. Exit 2 from the selection (scope `refused`): return PACKAGES with its reasons.
