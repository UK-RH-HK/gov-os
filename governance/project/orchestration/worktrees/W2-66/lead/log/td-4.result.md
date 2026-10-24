task: Write acceptance cases for W2-66's two new KPI lines from DEC-912 item 3 (P1: a selected test-map target that cannot be resolved widens the run; P2: W1-28's held-out copy check is coupled to every file its scan reads), and revise the README's Interface and KPI map to match.
status: DONE — both items are written and committed; the new cases are red for the stated reasons and every earlier case of the suite stays green.
work_completed: Step 0 sandbox check passed: (a) the write failed with `OSError: [Errno 30] Read-only file system`, and (b) `git hash-object -w` and `git update-index --refresh` both worked (exit 0). `GOV_ROLE`=`independent-test-designer` and `GOV_TICKET`=`DAEO-c1uz`; the top level was `/home/usain/gov-os-worktrees/W2-66`, the branch `w2/W2-66` and the head `02b62e03`. `git status` showed only placeholder devices (char 1,3, owned by nobody), and `docs/source` was one of them. Item 1 is a new file, `test_w2_66_unresolved_targets.py`, with 8 cases, plus `UNRESOLVED_TARGET`/`FILE_GONE`/`CASE_GONE` in the support module. Item 2 adds 8 cases to `test_w2_66_live_test_map.py`. In the README I revised Interface items 1, 3 and 6, added a "Part 5" KPI-map section with red reasons (n) and (o), updated Part 2's case count, and recorded the scan's file list under Discoveries.
files_changed: tests/acceptance/W2-66/test_w2_66_unresolved_targets.py (new); tests/acceptance/W2-66/w2_66_support.py; tests/acceptance/W2-66/test_w2_66_live_test_map.py; tests/acceptance/W2-66/README.md
evidence: Commit `e9c639f19bd4` (item 1: the new test file, the support constants, README items 3 and 6 and the S14 row). Commit `952193aecd00` (item 2: the live-map cases, README item 1, the S15 row and Discoveries). Both carry `Task: DAEO-c1uz`, `Role: independent-test-designer`, `Implements: DEC-912` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. After each commit `git status --short` was clean apart from the placeholders. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py`. Scratch in `TMPDIR`: 9 inodes / 28K at the start, 13,136 / 160M before the red run, 39,203 / 477M at the end (pytest's three base folders plus the kept temp folders of the 13 failing cases). Nothing untracked in the worktree except the ignored `__pycache__`. All of this is well inside my share of 4 GB and 200,000.
tests: The specified red run of `tests/acceptance/W2-66` (-n auto, `-o tmp_path_retention_policy=failed`, not stopped early): **13 failed, 157 passed, 0 skipped** in 110 s. Failing cases, grouped by red reason:
  - **(n), "the run is not stated full: scope 'scoped'"** (4): `test_a_renamed_record_reading_case_widens_the_run_to_the_full_regression[renamed]` and `[renamed-longer]`, `test_a_renamed_every_close_file_widens_the_run_to_the_full_regression`, `test_a_renamed_coupling_target_widens_the_run_to_the_full_regression`.
  - **(n), "the renamed … did not run: the close passed a red it would catch (scope 'scoped')"** (2): `test_a_red_the_renamed_record_reading_case_catches_refuses_the_close`, `test_a_red_the_renamed_coupled_file_catches_refuses_the_close`.
  - **(o), "a change to … does not select … scanning cases"** (7): `test_a_change_to_each_kind_of_file_w1_28_s_scan_reads_selects_its_check` `[conftest]`, `[test-file]`, `[other-module]`, `[new-suite-folder]`, `[new-suite-folder-conftest]`, `[below-a-suite-folder]`, and `test_every_python_source_w1_28_s_scan_reads_selects_its_check` (643 of 732 sources miss it; 642 of 731 on `02b62e033a10`, the extra file being my own new test file).
  - **Green on the built head by design** (3): `test_a_gone_coupling_target_the_change_does_not_reach_widens_nothing`, `test_selected_targets_that_resolve_change_nothing`, `[support-module]`.
  - Test count per item: item 1 has 8 cases, item 2 has 8 cases.
discoveries: The built head already resolves node-id targets for a class's method, a single parameter set, a parametrised function named by its beginning, and a class (the "resolves" case is green). W1-28's scan reads every `*.py` under `tests/acceptance/` and also imports each copier's module with its suite folder on `sys.path`. Eleven tracked helper modules are none of conftest, test file or `*_support.py`, so a support-only pattern misses them (listed below). `gov retrieve`'s semantic route tried to reach ollama.com and the sandbox denied it (2 violations); the call still returned results.
risks: (1) The README treats a parameter set `[…]` as its function, so a renamed parameter id (`f::test_x[a]` becoming `[b]`) still counts as resolved and runs nothing. That is outside the KPI line ("file or test function renamed or gone"), but it is a narrow fail-open. If the owner wants it closed, resolution would have to come from pytest's collection. (2) The live-map case checks resolution by reading the source for `def`/`class` names, so a W1-28 target naming a dynamically generated case would be judged unresolved. (3) If W1-28's scan changes, the P2 cases fail with "the fixture is wrong" until they are revised.
lessons: In live-map cases, assign the result to a boolean before asserting: pytest's assertion rewriting prints the arguments of a call inside the assert, which here came from the live map (my first draft printed `_runs_w1_28_s_check([...])`). The guard refuses any Bash command containing backticks (DEC-409), so search through the Grep tool. Guard refusals counted: 1 (a Bash `grep` whose pattern held backticks, refused "the command cannot be read", DEC-409; not retried, done with the Grep tool instead). DEC-849 read refusals: 0. One call I did not retry: a combined `rm -f` of my own red-run log in `TMPDIR` plus the scratch measure was not granted permission. The 2 KB log stays in `TMPDIR`, which is removed when the session ends. I used `gov retrieve` once, to confirm what W1-28's scan reads; it returned lens I1's report (`docs/assessment/2026-10/I1-guard-launcher-sandbox.md`:916-918, "reads every file under `tests/acceptance/`"). No rewrites: no existing case contradicted the new behaviours.
proposed_decisions: none (risk 1 is for the lead to judge: I recommend leaving it as written, since the KPI line names files and functions; confidence medium).
unresolved: none
recommended_next_action: Pass the INTERFACE text below to the engineer for P1 (resolve each selected target; widen with `UNRESOLVED_TARGET`) and P2 (couple `tests/acceptance/**.py` to W1-28's check).

INTERFACE:

Item 1, `couplings`: this text was appended after "…reaches it through its suite folder (item 3) or a coupling.":
```
**A file scan is such a coupling too** (DEC-912 item 3, P2): W1-28's
held-out copy check (`tests/acceptance/W1-28/test_w1_28_fixture_copies.py`, DEC-385) reads every Python
source under `tests/acceptance/` (`w1_28_copy_check.functions`: `rglob("*.py")`, `__pycache__` aside: each
suite's `conftest.py`, its `test_*.py` files, its support modules and its other helper modules, in any suite
folder, a new one included, at any depth) and runs the copying fixtures it finds. The live map couples every
such file (for example the pattern `tests/acceptance/**.py`), not only the support modules, to the check's
cases that scan the tree: the whole file, or each of `test_the_check_finds_the_copying_fixtures_of_the_earlier_suites`,
`test_a_fixture_that_copies_from_the_repository_leaves_the_held_out_file_out`,
`test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs` and
`test_the_reading_route_does_not_flag_this_suite_or_a_named_folder`, by targets that resolve (item 3).
`tests/acceptance/conftest.py` reaches it as shared core; W1-28's own files also through their suite folder.
```

Item 3: this text replaces "Every target `selected` names exists in the tree closed.":
```
**A selected test-map target that does not
resolve at the head widens the run** (DEC-912 item 3): the targets of `record_reading` and `every_close` are
selected on every close, a coupling's `suites` when one of its `paths` matches a changed path. A target
**resolves** when the tree closed holds it: a folder or a file, that path; a node id (or its beginning), its
file, holding the case the id names or begins: the function or class named after the file, the method named
after a class, a parameter set (`[…]`) read as its function (`f::test_x[p]`, `f::test_x`, `f::TestC`,
`f::TestC::test_m` each resolve when `f` defines what they name). A selected target that does not resolve (its
file or test function renamed or gone) runs the full regression, `UNRESOLVED_TARGET` naming it (item 6):
`FILE_GONE` when its file (or folder) is not in the tree closed, `CASE_GONE` when its file is there and holds
no case its node id names. A coupling whose `paths` match no changed path is not selected: its targets,
resolved or not, widen nothing. So every target a scoped run's `selected` names exists in the tree closed.
```

Item 6, `why_full`: the reason list gains `UNRESOLVED_TARGET`, and this text is added after "…empty or absent for a scoped run.":
```
`UNRESOLVED_TARGET`'s entry is `{reason: UNRESOLVED_TARGET, target, detail}`, one for each selected target
that does not resolve (item 3): `target` the target as the test map names it, character for character;
`detail` `FILE_GONE` (its file or folder is not in the tree closed) or `CASE_GONE` (its file is there and holds
no case its node id names). Beside other reasons, if any.
```

W1-28's scan, as established from `tests/acceptance/W1-28/w1_28_copy_check.py` (`functions`: `Path(tests_root).rglob("*.py")` with `tests_root=tests/acceptance`, skipping `__pycache__`; `copiers` and `whole_tree_copiers` both use it, and `load` imports each copier's module with its suite folder on `sys.path`). It reads every `*.py` under `tests/acceptance/` at any depth: 731 tracked files on `02b62e033a10`.
- `tests/acceptance/conftest.py`
- 58 suite `conftest.py` files
- 584 `test_*.py` files
- 77 `*_support.py` files
- 11 other helper modules:
  - `W1-04/w1_04_schema.py`
  - `W1-06/w1_06_schema.py`
  - `W1-27/w2_67_basetemp_probe.py`
  - `W1-27/w2_67_doctor.py`
  - `W1-27/w2_67_ns_launch.py`
  - `W1-27/w2_67_ns_probe.py`
  - `W1-27/w2_67_tmp_probe.py`
  - `W1-28/w1_28_copy_check.py`
  - `W1-47/w1_47_hook_time_limit.py`
  - `W1-50/w1_50_freeze_lift.py`
  - `W2-69/w2_69_stdlib_secrets_first.py`

None of these is below a suite folder today, and any new file in any suite folder would be read too.