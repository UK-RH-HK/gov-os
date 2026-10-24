task: Make the 11 red acceptance cases of DAEO-c1uz (W2-66) pass: moved files counted at both paths, declared acceptance folders as suites, paths only suiteless tickets hold left unplaced, the live test map's entries, deselected cases named in `left_out`.

status: PACKAGES. All five items are built and committed, and all 177 acceptance cases pass. One W2-54 case fails because this sandbox blocks the Claude API; one package explains it.

work_completed:
- Sandbox check (step 0):
  - (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz` failed (`OSError: [Errno 30] Read-only file system`), as required.
  - (b) `git hash-object -w` worked (gave `1ae28402…`) and `git update-index --refresh` worked (exit 0).
  - `GOV_ROLE`/`GOV_TICKET` are `engineer`/`DAEO-c1uz`; the top level is `/home/usain/gov-os-worktrees/W2-66` on `w2/W2-66`; HEAD was `6d17109b`.
  - `git status` listed only the sandbox's placeholders: character devices 1,3 owned by nobody (`.bashrc`, `.gitconfig`, `.idea`, `docs/source` and the like).
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"` printed `/home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py`.
- **Item 1 (45763156):** `select.changed` now reads the change as `git -c core.quotePath=false diff -z --no-renames --name-only`, the same way `repo._LOG` does. A moved file is in the change at both its paths, even when the repository sets `diff.renames=true`.
- **Items 2 and 3 (16e98848, d3650169):**
  - A ticket's suite now comes from `gates.acceptance_folder` (new `suite_folder` in `select.py`). A ticket has a suite when that folder holds a `test_*.py` (`gates.has_tests`).
  - The overlap rule selects that folder; the closing ticket's own suite is its declared folder (`command.py` now passes `ticket=ticket`, nothing else changed there). OWN is named only when that folder exists.
  - The placed rule ignores the `allowed_paths` of tickets without a suite, so such paths are `UNPLACED` and run the full regression.
  - A declared folder outside `tests/` (or containing `..`) counts as no suite, because `pytest tests` would never reach it. Its ticket's paths therefore widen to the full run.
- **Item 5 (1ad4db0d):** each case left out by `--deselect` gets its own `left_out` entry, `{target: <node id>, why: [{reason: NOT_REACHED}]}`.
- **Item 4 (b3e60cbc):**
  - The shared core gains `tests/conftest.py` and `tests/acceptance/conftest.py`.
  - A new coupling takes `tests/acceptance/W1-07/conftest.py` and `W1-25/conftest.py` to `tests/acceptance/W1-27/test_w2_67_copies.py`. W1-27's own conftest reaches it through its suite folder.
  - The `record_only` note is corrected: W1-42's paths place the two `docs/plan/wave-1-exit/` scripts, and `orchestration/sync_context.py` (held only by W2-00, which has no suite) is unplaced.
  - The schema and the template's copy did not need to change; the live map still validates.

files_changed: src/gov/close/select.py, src/gov/close/command.py (one line), governance/project/test-map.yaml, tests/unit/close/test_select.py

evidence:
- Five commits: 45763156, 16e98848, 1ad4db0d, b3e60cbc, d3650169. Each carries `Task: DAEO-c1uz`, `Role: engineer`, `Implements: DEC-880` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Item 2 and item 3 share commit 16e98848 because they are the same hunks.
- `git diff --stat 6d17109b HEAD`: 4 files changed, 109 insertions(+), 18 deletions(-) (select.py +67/−, test_select.py +45, test-map.yaml +13, command.py ±1).
- `git status` is clean apart from the placeholders.
- Live-map selections, computed in memory with the base and change stubbed, nothing written:
  - `src/gov/status/command.py` → scoped: OWN W2-66/, UNIT, OVERLAP W1-32/, plus every_close and record_reading (215 left out, 185 ignored, 31 deselected).
  - `tests/conftest.py` → full, `SHARED_CORE`; `tests/acceptance/conftest.py` → full, `SHARED_CORE`.
  - `governance/project/orchestration/sync_context.py` → full, `UNPLACED`.
  - `docs/plan/wave-1-exit/apply_adapter_output.py` and `write_permissions_source.py` → scoped, OVERLAP W1-42/.
  - `tests/acceptance/W1-07/conftest.py` and `W1-25/conftest.py` → scoped, TEST_CHANGED on their own suite plus COUPLING `tests/acceptance/W1-27/test_w2_67_copies.py`; `W1-27/conftest.py` → TEST_CHANGED W1-27/.
- Scratch (`TMPDIR` `/tmp/gov-launch-engineer-aj_41mg0/claude-1000`):
  - at the start: 8 inodes, 24K;
  - before the long runs: 16,576 inodes, 200M, then 16 inodes, 56K;
  - at the end: 7,094 inodes, 48M.
  - Nothing of mine is left untracked in the worktree. One scratch script (`live_select.py`) is still in the scratchpad: the call to delete it was not approved, and the folder is removed when the session ends. All well inside my 5 GB / 250,000 share.
- Guard refusals: 2.
  1. A grep whose path list included `tests/acceptance/W1-30/` and `W1-39/` (DEC-820 (c)); I narrowed to `git ls-files` of named conftests.
  2. The Monitor tool ("not known to the guard", DEC-685); I waited with a bounded foreground loop instead.
- `gov retrieve`: not used. The brief named every file to read, and I read those directly.

tests (all with `-o tmp_path_retention_policy=failed`):
- The three acceptance suites (W2-66 + W1-30 regression_scope + W1-39 copy): 177 passed on the final head (11 were failing at the start).
- tests/unit/close: 415 passed.
- tests/acceptance/W2-07: 40 passed. W1-30: 515 passed. W2-01: 88 passed. W2-53: 57 passed. W1-07: 223 passed.
- tests/acceptance/W2-54: 96 passed, 1 failed (`test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written`). Its message: "the launched worker did not run the probe to its end"; the launched session got `API Error: … ERR_PROXY_TUNNEL`, and the sandbox reports api.anthropic.com:443 refused.
- One gap in the ordering: W2-01, W2-53, W1-07 and W2-54 ran before d3650169. Only `tests/unit/close` (415 passed) and the three acceptance suites (177 passed) ran after it.
- The 600 s foreground cap moved one long run to the background. I waited for it and read its result.

discoveries:
- With the declared-folder rule, a ticket can declare a folder outside `tests/`. The scoped run (`pytest tests`) cannot reach such a folder, so I treat it as no suite, which widens to the full run.
- The deselection prefix rule also leaves out `test_reads_too` next to a selected `test_reads`, and that case is now named in `left_out` too.

risks:
- `select.plan` now reads every ticket's acceptance folder (one `rglob` per ticket). That is cheap at today's size (under a second here).
- An own folder that does not exist is no longer named with OWN. The acceptance run itself is W2-07's and is unchanged.

lessons:
- Long suites (W2-54 takes about 12 minutes) go past the 600 s foreground cap. Run them one per call, and expect the Monitor tool to be refused.
- Searches over `tests/acceptance/*` trip DEC-820 (c) because of the held W1-30 and W1-39 files; name folders one at a time.

proposed_decisions:
- Package on the W2-54 sandboxed-worker case:
  - **Question:** can the lead treat this case as an environment failure rather than a regression?
  - **Why now:** it is the only red I saw in the suites that must stay green.
  - **Options:** (a) the lead runs it with network to the Claude API; (b) take it as environmental and record that.
  - **Impact:** none on W2-66's code. The case launches a real worker session, which the sandbox's proxy refuses, and this change does not touch the guard, the sandbox or retrieval.
  - **Reversibility and cost:** fully reversible; (a) costs about 3 minutes.
  - **Recommendation:** (a), as part of the lead's full verification.
  - **Confidence:** high.

unresolved: the W2-54 sandboxed-worker case still needs a run with Claude API access (see the package).

recommended_next_action: The lead runs the full verification, including that W2-54 case where the Claude API is reachable, and then sends the five commits to a fresh FULL review.