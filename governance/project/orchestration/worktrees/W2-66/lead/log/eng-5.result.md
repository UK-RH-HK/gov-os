task: DAEO-c1uz (W2-66) round 3: P1, a selected test-map target the head does not hold widens the close to the full regression (`UNRESOLVED_TARGET`); P2, the live map couples every Python file under `tests/acceptance/` to W1-28's held-out copy check (DEC-912 item 3).
status: DONE — both items are built and committed, and every acceptance case passes (193/193); every suite they could break stays green.
work_completed: Step 0 sandbox check passed. (a) The write outside the worktree failed with `OSError: [Errno 30] Read-only file system`. (b) `git hash-object -w` and `git update-index --refresh` both worked (exit 0). The environment matched: `engineer`, `DAEO-c1uz`, the W2-66 worktree on `w2/W2-66`, HEAD `952193ae`. `git status` listed only the sandbox's placeholders (`.bashrc`, `.gitconfig`, `.idea`, `docs/source` and others), all character devices 1,3 owned by nobody. **P1:** `select.unresolved(root, targets)` checks each target against HEAD as committed. It lists files with `git ls-tree -r -z --name-only HEAD` and reads a node id's file with `git show HEAD:./<file>`, parsed with `ast`. A folder or file resolves if HEAD holds it. A node id (or its beginning) resolves if its file defines what it names: a top-level function or class, a method inside a class, or a name bound by assignment or import. A trailing `[…]` counts as its function. A missing file or folder gives `FILE_GONE`. A file that is there but holds no such case, or does not parse, gives `CASE_GONE`. `plan()` checks the record-reading and every-close targets on every close, and a coupling's targets only when one of its `paths` matches a changed path. It adds one `{reason: UNRESOLVED_TARGET, target, detail}` per failure to `why_full`, beside any other reasons, and the run goes full. A coupling no changed path reaches widens nothing. `evidence.py` needed no change. **P2:** in the live map, W1-28's coupling changed from `tests/acceptance/**_support.py → tests/acceptance/W1-28/` to `tests/acceptance/**.py → tests/acceptance/W1-28/test_w1_28_fixture_copies.py` (the whole file; it resolves). The template map and the schema needed no change, and the live map still passes the schema.
files_changed: src/gov/close/select.py; governance/project/test-map.yaml; tests/unit/close/test_select.py
evidence: Commit `73a402771ec2` (P1) and commit `0f0f6cb2acd5` (P2), each with trailers `Task: DAEO-c1uz`, `Role: engineer`, `Implements: DEC-912`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. `git diff --stat 952193ae HEAD`: 3 files changed, 95 insertions(+), 4 deletions(-) (select.py +60/−1, test-map.yaml +3/−3, test_select.py +32). `gov.__file__` = `/home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py`. `git status` shows no tracked changes. Live-map selections, computed in memory with `changed`/`base` stubbed and nothing written:
  - `src/gov/status/command.py`: scoped, empty `why_full`, W1-28 not selected, 16 of 59 acceptance suites reached.
  - `tests/acceptance/W1-05/conftest.py`, `tests/acceptance/W1-05/test_w1_05_live_hooks.py` and `tests/acceptance/W2-01/test_w2_01_close.py`: scoped, each selects `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`, 17 of 59 suites.
  - `tests/acceptance/W1-47/w1_47_hook_time_limit.py`: scoped, selects it, 20 of 59 suites.
  - So a typical acceptance-test change gains one file (W1-28's copy-check file, about 6 cases) and one suite; it is not widened to the whole W1-28 folder.
  - All 59 live-map targets resolve at HEAD (`unresolved(...) == []`).
  - Scratch: `TMPDIR` measured 17 inodes and 60K at the start and at the end (pytest keeps only failed tests' folders). Nothing I wrote is left untracked in the worktree.
tests: P1 cases (`test_w2_66_unresolved_targets.py`): 8 passed (all red before). P2 cases (`test_w2_66_live_test_map.py`): 81 passed. Each command below ran with `PYTHONPATH=…/W2-66/src` and `-o tmp_path_retention_policy=failed`, and all were green:

| Suite | Result |
|---|---|
| The ticket's set: W2-66 + W1-30 regression_scope + W1-39 copy | 193 passed (13 failed before) |
| tests/unit/close | 417 passed |
| tests/acceptance/W2-07 | 40 passed |
| tests/acceptance/W1-30 | 515 passed |
| tests/acceptance/W1-28 | 151 passed |
| tests/acceptance/W1-07 | 223 passed |
| tests/acceptance/W1-39 | 71 passed |
| tests/acceptance/W2-01 | 88 passed |
| tests/acceptance/W2-53 | 57 passed |

discoveries: No acceptance suite other than W1-39 (and the counterpart's W2-66 and W1-30 files, which I did not search) names the test map; I searched the other suite folders by name. The template map has no W1-28 coupling, so it needed no change.
risks: 
  - A node id whose case comes from a base class, or is defined inside an `if`/`try` block at module level, gets `CASE_GONE` and widens the run. That is the safe side, and no live-map target is like that today.
  - The new coupling makes every acceptance-test change also run W1-28's copy-check file. This costs a little time but no scope.
  - The W2-07 + W1-30 command passed the 600 s tool limit and the harness moved it to the background. I waited for it in the foreground (`until grep` loop) and read its result (40 and 515 passed) before going on.
lessons: Running W1-30's whole suite with `-n auto` takes about 11 min. Run it alone, under one 600 s command or less, or wait on it in the foreground. The guard refuses a `grep -r` over `tests/acceptance` even when it excludes the counterpart's files; grepping a list of named folders works.
proposed_decisions: none
unresolved: none
recommended_next_action: The lead runs the full verification on `0f0f6cb2acd5`, then the FULL review of P1 and P2.

Refusals, counted:
- **1 guard read refusal:** `grep -rl --exclude-dir=W2-66 … tests/acceptance` (DEC-820 (c)). I did not retry it in another form; I searched named folders instead.
- **1 call refused twice** (AR-6, not retried a third time): a combined command (scratch measure, `rm` of my scratch script, `git status`, and `git log` with a `%(trailers…)` format) failed with "Quoted text in this command can't be checked". I split it into simpler commands without the format.
- **1 permission refusal:** the `rm` of my scratchpad script `live_select.py` was not approved, so that one small file stays in the session's scratchpad, which is removed when the session ends (DEC-386).

`gov retrieve`: not used. The brief named the exact files to read, and the questions were narrow code reads of `select.py` and the test map.