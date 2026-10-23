# W2-67 (DAEO-9nys): test hygiene, round 1, test design batch 1

Independent test designer (MR-3), 2026-10-23. Sources: the ticket file's KPI lines; the card (`docs/plan/WAVE_2_WBS.md`
§2, W2-67); DEC-889 item 7, DEC-892 item 1, DEC-898, DEC-899, DEC-904 (item 5: round 1 only); DEC-456, DEC-448,
DEC-385, DEC-491, DEC-866; lens I (`I-SYNTHESIS.md` §4, §5.2, P-IS-7; `I4-records-plan-rest.md` §2.1, §2.2, §2.4,
F1, F5; `I3-retrieval-context-resume.md` F9).

Every run here uses this worktree's code (DEC-732): `PYTHONPATH=<worktree>/src` per command; the doctor revisions
run `gov` with `support.REPO_ROOT` as the code root or with the suite's copy of this worktree.

## KPI lines and their tests

| KPI line (round 1) | Tests | On the head |
|---|---|---|
| 1. Every per-test copy commits with `gc.auto=0` or copies the working files without `.git`; a planted 7,000-object tree runs every copying case green in parallel (I3 F9, I4 F5, I4 §2.1) | `test_w2_67_copies.py`: `test_w1_07_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc`, `test_w1_25_…`, `test_w1_27_…`; `test_a_per_test_copy_from_the_working_files_carries_no_copied_git_while_gc_runs[W1-26-FullProject, W1-26-Project-copy_tree, W1-27-copy_working_tree-per-test]` | 3 red, 3 green (guards) |
| 1. W1-27's old-path case gets a project of its own (I4 §2.1) | `test_w1_27_path_compliance_r2.py::test_old_path_inside_its_new_path_is_not_stale` (revised) | green |
| 4. pytest's own retention of three base folders; no per-run `--basetemp`; a full run leaves at most three base folders behind (DEC-898) | `test_w2_67_temp_folders.py`: `test_the_pytest_configuration_passes_no_basetemp_and_keeps_three_base_folders`, `test_no_source_of_round_1_passes_a_per_run_basetemp_or_changes_the_retention`, `test_a_run_after_older_runs_leaves_at_most_three_base_folders`, `test_a_run_after_killed_runs_leaves_at_most_three_base_folders`, `test_a_base_folder_of_a_run_still_going_is_kept` | 1 red, 4 green (guards) |
| 5. Each weak case revised: red against a planted fault, then green on the head, with a `Rewrite-Reason` (P-IS-7 (a); I4 F1) | the revised W1-27 cases below | green; red under their plants |

KPIs 2 (the unit close nested runs) and 3 (W2-50's limits, the guard unit test's `/tmp`) and the other weak-case
groups of KPI 5 (W1-26, W1-30, W2-02, T-A3) are not in this batch (DEC-904 item 5; the brief of batch 1).

## KPI 1: the copies (`test_w2_67_copies.py`)

**The planted tree.** A git repository of 7,200 untracked, unignored working files (7,200 blobs) built in the case's
temporary folder; `copy_working_tree` lists untracked files, so nothing is committed there. `git gc --auto` estimates
the loose objects from `.git/objects/17` alone; 64 of the planted blobs are chosen to land there (above
`ceil(6700 / 256) = 27`), so the copy's commit passes git's default threshold on every run, not only when the hash
spread allows it (at 7,000 objects the mean is 27.3 per folder: about one run in two).

**Pointing the copiers at it.** Each suite's own copying code runs unchanged: the conftest's fixture bodies (`live`,
`project`, W1-25's `_copy`) are called as functions (`__wrapped__`), and `copy_working_tree`'s default root is set to
the planted tree for the case (`monkeypatch` on `__defaults__`). Finding: **no copier of W1-25, W1-26 or W1-27, and
none of the conftest fixtures, takes a root parameter**; only `w1_07_support.copy_working_tree` does, and every other
copier calls it with its default (the repository). W1-28's check (`w1_28_copy_check.copiers`) finds that one copier
alone in the four suites. The cases reach the others through the default, which a fix may keep or replace.

**The judgement (the KPI's either/or).** Two per-test copies are made at once from the session copy (two workers, the
brief's bound). A case is red when a copy raised, when a copy's objects are not all there (`git fsck
--connectivity-only`), or when an automatic gc started in the session copy (its `gc.pid`, `gc.log` or a pack,
watched for 5 s) **and** a per-test copy carries the session copy's `.git` (a marker file left in it) or raised. A copy
that takes the working files without `.git` passes whatever the session copy's gc does; a session copy that commits
with `gc.auto=0` shows no pack.

**Why no nested run of the suites' copying cases.** The race needs a session copy past about 6,700 objects. A nested
run of the real cases on such a tree would make whole-tree copies of this repository plus 7,000 planted objects per
case (the inode explosions of 2026-10-22 and 2026-10-23 this ticket removes), and would show the race only by chance.
The cases above run each suite's copying code itself, in parallel, on the planted tree; the gc is observed directly,
so the result does not depend on timing. Each case removes its trees before it ends (about 50,000 files at peak).

| Case | Red reason on the head (seen 2026-10-23) |
|---|---|
| `test_w1_07_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc` | an automatic gc in the session copy (1 pack) and both per-test copies raised `shutil.Error: … session/w1-07-live/repo/.git/objects/08 … No such file or directory`: the race itself |
| `test_w1_25_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc` | the same, `…/w1-25-live/repo/.git/objects/1c` (the `_copy` behind `raw_project` and `project`; `built` and `test_w1_25_live_session.py` copy the same `live` the same way) |
| `test_w1_27_per_test_copies_of_a_7000_object_tree_do_not_race_gits_gc` | the same, `…/w1-27-live/repo/.git/objects/24` |
| `test_a_per_test_copy_from_the_working_files_carries_no_copied_git_while_gc_runs[…]` (3) | green on the head: a guard. W1-26's `FullProject` and `Project(copy_tree=True)`, and the W1-27 cases that call `copy_working_tree` themselves (adoption, held-out until this batch), take the working files, never a `.git`; their own commit starts gc in the copy, which nothing copies afterwards |

Shown green with the copies committing under `gc.auto=0` (a throwaway pytest plugin, `w2_67_fixed_copier`, wrapping
`w1_07_support.git` in the test process only): the three chain cases, 3 passed in 32.6 s (JUnit XML
`.gov-runtime/scratch/td-1/plant/kpi1-chains-with-gc-auto-0.xml`).

## KPI 4: temp folders (`test_w2_67_temp_folders.py`)

Two static guards (no run) and three nested runs. A nested run is bounded: one worker (`-p no:xdist`), one tiny case
(`w2_67_tmp_probe.py`, not collected by a run of `tests`), the repository's configuration (`--rootdir` the repository,
so a root `tests/conftest.py` is loaded once it exists), a `TMPDIR` of the case's own, and no `--basetemp`.

| Case | On the head |
|---|---|
| `test_the_pytest_configuration_passes_no_basetemp_and_keeps_three_base_folders` | green: a guard (no `addopts` with `--basetemp`; `tmp_path_retention_count` absent or 3; DEC-904 item 1's `tmp_path_retention_policy=failed` trial is allowed) |
| `test_no_source_of_round_1_passes_a_per_run_basetemp_or_changes_the_retention` | green: a guard (no argument list with `--basetemp`, no assignment of a base folder or of the retention count, in `tests/conftest.py` and round 1's folders) |
| `test_a_run_after_older_runs_leaves_at_most_three_base_folders` | green: a guard (five finished runs' folders; pytest's own retention leaves `pytest-3`, `-4`, `-5`) |
| `test_a_run_after_killed_runs_leaves_at_most_three_base_folders` | **red**: `6 base folders left behind, more than 3 (DEC-898): ['pytest-0', …, 'pytest-5']`. Each older folder holds the `.lock` a killed run leaves, naming a pid no process holds; pytest keeps any folder whose lock is younger than three days, whatever the retention count. This is how `/tmp/pytest-of-usain` came to 61 run folders (the card) |
| `test_a_base_folder_of_a_run_still_going_is_kept` | green: a guard. A folder whose `.lock` names a running process is another run's and must stay: a clean-up that removed it would break a concurrent session |

What a run given a per-run `--basetemp` must do is not tested: the KPI states only that nothing passes one. That
question is returned as a package (the designer's return, P-W2-67-TD1-A).

## KPI 5: the revised W1-27 cases (`gov doctor` first)

**Planting a fault.** `src/` is never written and the tree is never copied. A throwaway pytest plugin
(`w2_67_plant`, loaded with `-p w2_67_plant` from the designer's session scratch folder) wraps
`w1_07_support.write_launcher` in the test process: each launcher a case writes in its sandbox first imports
`w2_67_child_plants` and replaces one function of `gov.doctor.command` in that `gov` process only, by the fault
named in `W2_67_PLANT`. The JUnit XML of each run is under `.gov-runtime/scratch/td-1/plant/`. (The plant modules
stayed in the session scratch folder: the Write tool refused `.gov-runtime/scratch/td-1/plant/`; the faults are
described here instead.)

| Fault | In words | How |
|---|---|---|
| P27-1 (I4) | a moved-path reference never reported (CAP-06.d) | `_check_path_compliance`'s result with `moved_references = []`, status pass |
| P27-2 (I4) | the held-out file reported missing when present, and the reverse (DEC-223) | `_check_held_out`'s `missing` inverted |
| P27-3 (I4) | `ADOPTED_HEALTHY` for every project (CAP-54.a) | `_check_adoption_level`'s level set to `ADOPTED_HEALTHY` |
| P27-4 (I4) | never an unclassified path (CAP-06.d) | `_check_path_map`'s result with no unclassified path, status pass |
| P456-3 | DEC-456 point 3 dropped: an old path inside its own new path is reported | `_has_standalone_old_path` returns `old_path in content` |

| Case | Weak because (I4 §2.1, §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_w1_27_path_compliance_r2.py::test_old_path_inside_its_new_path_is_not_stale` | copies the whole tree, and doctor greps every tracked file: its result depended on every file's text (red on 2026-10-21 when a lead log named its fixture) | P456-3: `doctor reports subpath_target.py as a moved-path reference although it appears only as part of its own new path …`; P27-1: `the control's standalone reference to control_target.py in notes.md is not reported` | green, 0.85 s (9 to 14 s before) | the result depends on every tracked file's text |
| `test_w1_27_held_out.py::test_missing_held_out_yaml_is_reported` | asserted `held` anywhere; the key `held_out` is always printed | P27-2: `doctor does not report the missing held-out.yaml` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_held_out.py::test_present_held_out_yaml_is_not_reported` | read only `result`, `{}` whenever doctor is unhealthy | P27-2: `doctor reports held-out.yaml as missing when it is present` | green | the case read only `result`, empty whenever doctor is unhealthy |
| `test_w1_27_adoption.py::test_doctor_report_mentions_adoption_level` | asserted `adopt` or `level` anywhere; the key `adoption_level` is always printed | P27-3: `ADOPTED_HEALTHY although ['canaries', 'framework_lock', 'index_freshness', 'isolation'] are unmeasured (DEC-425)` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_adoption.py::test_minimal_kernel_passes_at_minimal_level` | asserted `minimal`, `kernel` or `level` in `result`; `level` is a key of every adoption section | P27-3: `minimal kernel project does not report the minimal adoption level` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_adoption.py::test_completed_stages_raise_adoption_level` | failed only without any of five words, and `healthy` is always a key | P27-3: `the completed stages do not raise the adoption level: before ADOPTED_HEALTHY, after ADOPTED_HEALTHY` | green | the assertion matches a key name that doctor always emits |

Each revised case keeps its name and its rule, reads the section it claims (`w2_67_doctor.section`: `result` when
doctor is healthy, `error.details` when it exits 3 with `DOCTOR_UNHEALTHY`), keeps the API-0002 envelope check, and
lowers no expectation. The old-path case gained a control (a standalone reference to another moved file, which must
be reported), so a doctor that reports nothing cannot pass it. The held-out and old-path cases run on small
committed projects of their own (`w2_67_doctor.small_project`) with this worktree's code, not on a copy of the
whole tree.

The adoption cases read the level's value: a defined level (`MINIMAL` < `INTERMEDIATE` < `ADOPTED_HEALTHY`), never
`ADOPTED_HEALTHY` while another section is unmeasured (DEC-425); the lowest level for the minimal kernel project; and
a higher level with this repository's path map than with the stages taken out (a minimal path map) on the same
project, as I4 proposed ("compare the levels before and after the stages").

**Not revised in this batch** (the remaining 34 of the 40, and the duplicate): `test_w1_27_doctor.py` ×8;
`doctor_r5`'s stale-path case; `doctor_r7`'s home-tool sha256 case; drift ×6; `isolation_r2`; path compliance ×3;
path compliance r2 ×3 (the old-path case aside); rebuild ×5; rebuild r2, r3, r4, r8; recovery check r2 ×3;
`test_rebuild_does_not_silently_drop_lexical_tables`. Time ran out; see the designer's return for the order.

## KPI 5, batch 1b: the rest of W1-27's weak cases

Independent test designer (MR-3), batch 1b, 2026-10-23. The same rule as batch 1: each case reads the value of the
key it claims, wherever doctor or rebuild put it, is shown red under a planted fault of the behaviour it claims and
green on the head, keeps its name, and lowers no expectation.

**Planting a fault (batch 1b).** The same method as batch 1, with its own modules, kept with the evidence in
`.gov-runtime/scratch/td-1b/plant/` (written in the session scratch folder and copied there as single named files):
`w2_67b_plant.py`, a pytest plugin (`-p w2_67b_plant`, the folder on `PYTHONPATH`), wraps
`w1_07_support.write_launcher` in the test process; each launcher a case writes first imports `w2_67b_child.py`
from that folder and applies the faults named in `W2_67_PLANT` (comma-separated) in that `gov` process only.
`src/` is never written and the tree is never copied. Each run's JUnit XML is in the same folder (`g<group>-<fault>.xml`,
`g<group>-head.xml`). A command, for one fault:

    W2_67_PLANT=P27-1 PYTHONPATH=<worktree>/src:<worktree>/.gov-runtime/scratch/td-1b/plant \
      python3 -m pytest -p no:cacheprovider -p no:xdist -p w2_67b_plant -q --junitxml=<plant>/g1-P27-1.xml <node ids>

`w2_67b_support.py` holds this batch's helpers: a file written and committed in a small project, a moved path git
records, and `path_compliance.moved_references` read through `w2_67_doctor.section`.

### Group 1: path compliance (`test_w1_27_path_compliance.py` ×3, `test_w1_27_path_compliance_r2.py` ×3)

| Fault | In words | How (in `w2_67b_child.py`) |
|---|---|---|
| P27-1 (I4) | a moved-path reference never reported (CAP-06.d) | `_check_path_compliance`'s result with `moved_references = []`, status pass |
| P27-4 (I4) | never an unclassified path (CAP-06.d) | `_check_path_map`'s result with no unclassified path, count 0, status pass |
| P67B-1 | the path matcher matches no pattern: every tracked path unclassified (CAP-06.a) | `_match_pattern` returns false |
| P67B-2 | `src/gov/cli/` left out of the stale-path check as if it were the old `cli/` tree (DEC-456 point 2) | `_excluded_from_stale_check` true also under `src/gov/cli/` |
| P67B-3 | every document under `docs/` left out, not `docs/SOURCES.md` alone (DEC-456 point 1) | `_excluded_from_stale_check` true also under `docs/` |
| P67B-4 | DEC-456 point 3 too broad: a file that names the new path is never reported | `_has_standalone_old_path` returns false |
| P67B-5 | an unrelated section fails, so doctor is unhealthy whatever path_map says | `_check_tools`'s status `fail` (combined with P27-4) |

| Case | Weak because (I4 §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_w1_27_path_compliance.py::test_full_coverage_is_healthy` | read only top-level values of `result` (empty when doctor is unhealthy); the count is nested | P67B-1: `doctor reports unclassified paths on a project whose path map covers every tracked path (**): {'status': 'fail', 'unclassified_count': 5, …}` | green | the case reads result, which is empty when doctor is unhealthy |
| `test_w1_27_path_compliance.py::test_unclassified_path_is_reported` | `ok` false on every machine for the tools section alone; `path` is a key name | P27-4: `doctor is ok despite unclassified paths`; P27-4 + P67B-5 (doctor unhealthy for tools): `doctor does not name docs/outside.md … as unclassified: {'status': 'pass', 'unclassified_count': 0, 'unclassified': []}`; P67B-5 alone: green | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_path_compliance.py::test_moved_path_reference_is_reported` | no file named the old path; `moved` is the key `moved_references` | P27-1: `doctor does not report docs/notes.md's reference to the moved path src/gov/doctor/old_module.py` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_path_compliance_r2.py::test_stale_path_in_live_document_not_sources_is_reported` | `moved` always there | P27-1 and P67B-3: `doctor does not report a reference to a moved path in a live document` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_path_compliance_r2.py::test_stale_path_in_src_gov_cli_is_reported` | the same always-true alternative | P27-1 and P67B-2: `doctor does not report a reference to a moved path in src/gov/cli/` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_path_compliance_r2.py::test_old_path_standalone_is_stale_when_new_path_elsewhere` | the same always-true alternative | P27-1 and P67B-4: `doctor does not report the standalone old path as stale` | green | the assertion matches a key name that doctor always emits |

Head: the six, 6 passed in 6.7 s (`g1-head.xml`). Each runs on a small committed project of its own with this
worktree's code (`w2_67_doctor.small_project`, `w2_67_doctor.doctor`), not on a copy of the whole tree, and reads
`path_map` or the named entry of `path_compliance.moved_references` (old path, the file that names it, and for the
moved-path case the new path). The two DEC-456 counter-cases keep the excluded place beside the live one in the same
project (`docs/SOURCES.md`, the old `cli/` tree), so the exclusion and the report are seen together. The
unclassified case gained a covered control path (`src/covered.py`), which must not be reported.

### Group 2: doctor's sections (`test_w1_27_doctor.py` ×8, `doctor_r5` ×1, `isolation_r2` ×1)

| Fault | In words | How (in `w2_67b_child.py`) |
|---|---|---|
| P27-11 (I4) | a tool doctor cannot find reported with its pinned version only (nothing says why) | not-ok entries of `_check_tools` keep only `name`, `pinned_version`, `ok` |
| P67B-6 | the found version is the pin: doctor reads the registry, not the tool | every entry's `found_version` set to its `pinned_version` |
| P67B-7 | framework.lock always MATCH | `_check_framework_lock` returns `{"status": "pass", "match": "MATCH"}` |
| P67B-8 | hooks always wired | `_check_hooks` returns pass, `config_present` and `binary_installed` true |
| P67B-9 | the index always fresh | `_check_index_freshness` returns pass, `fresh`, no stale file |
| P67B-10 | every canary passes, measured or not | every index `passed`, `AVAILABLE`, no miss; status pass |
| P67B-11 | the lexical canary never passes | `lexical.passed` false, a planted miss |
| P27-9 (I4) | isolation reported whatever the runtime folder's parent (DEC-425) | a measured result (with `git_root`) set to isolated, pass |
| P67B-12 | the constant stub the round-2 case names | `_check_isolation` returns `{"status": "pass", "isolated": True}` |
| P27-1, P27-4 | as in group 1 | as in group 1 |

| Case | Weak because (I4 §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_doctor_real_registry_every_entry_reported` | its "not ok with a reason" half was met by `pinned_version`, which every entry carries | P27-11: `entry 'pytest-xdist' is not ok but says nothing about why (…): {'name': 'pytest-xdist', 'pinned_version': '3.8.0', 'ok': False}` | green, 6.9 s (whole-tree copy, real home: machine-dependent, as before) | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_tool_versions` | `tool` anywhere; no version read | P67B-6: `the tool at another version is not reported as pinned 1.0.0, found 9.9.9: {… 'found_version': '1.0.0' …}` | green | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_hooks` | `hook` anywhere | P67B-8: `doctor reports hooks wired on a project with no lefthook.yml: {'status': 'pass', 'config_present': True, …}` | green | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_path_map_coverage` | `path` anywhere | P27-4: `doctor does not count docs/guide.md as unclassified under a path map of src/**: {'status': 'pass', 'unclassified_count': 0, 'unclassified': []}` | green | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_index_freshness` | `index` or `fresh` anywhere | P67B-9: `doctor reports a fresh index before any index was built: {'status': 'pass', 'index_status': 'fresh', 'stale': []}` | green | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_canaries` | `canar` anywhere | P67B-10: `the lexical canary does not miss on a project with no index: {'status': 'pass', …}`; P67B-11: `the lexical canary does not pass once the rebuilt index holds its queries ['juniper lantern protocol sentinel']` | green | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_framework_lock` | `framework` or `lock` anywhere; MATCH or DRIFT never read | P67B-7: `a project with no framework.lock is not unmeasured (DEC-425): {'status': 'pass', 'match': 'MATCH'}` | green | the assertion matches a key name that doctor always emits |
| `test_doctor_report_mentions_isolation` | `isolat` anywhere | P67B-12: `isolation is reported with no .gov-runtime to measure (DEC-425): {'status': 'pass', 'isolated': True}`; P27-9: green (the round-2 case holds that rule) | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_doctor_r5.py::test_stale_path_in_live_document_is_reported` | the same always-true alternative | P27-1: `doctor does not report a reference to a moved path inside a live document` | green | the assertion matches a key name that doctor always emits |
| `test_w1_27_isolation_r2.py::test_doctor_isolation_is_measured_not_constant` | rejected one exact stub only; the copy had no `.gov-runtime` | P27-9: `a .gov-runtime whose parent (…/outer/inner) is not the git root (…/outer) is not reported as not isolated`; P67B-12: `the isolation check is a constant stub` | green | the assertion matches a key name that doctor always emits |

Head: the nine small-project cases, 9 passed in 19.8 s (`g2-head.xml`). Each reads its section's typed fields on
small committed projects of its own, one input that makes the section measure and, where it can pass, one it
must not pass: two fake tools (pinned 2.0.0 found 2.0.0; pinned 1.0.0 found 9.9.9); no `lefthook.yml` and one;
`**` and `src/**`; no index, a rebuild, a change after it (the changed file stale, the other not); the lexical
canary's own missed queries, read from doctor's report, written into a document and rebuilt; no `framework.lock`
(unmeasured) and an installed project (`.copier-answers.yml`) without its lock (fail); no `.gov-runtime`
(unmeasured), the project's own (isolated, its git root named), and one in a subfolder (not isolated).
`framework_lock`'s MATCH and DRIFT need an installed kernel and its lock (no `gov` command writes one); W1-39's
lock cases hold them, so this case holds the two verdicts reachable without an install.

### Group 3: Claude Code drift (`test_w1_27_drift.py` ×6)

Where doctor reads its input, seen on the head with a probe (one doctor run per placement): the CLI is the
`claude` on the PATH doctor is given (a fake at `HOME/.local/bin/claude` is not read; this machine's real CLI,
2.1.292, is read instead); the extension is read under `HOME/.vscode-server/extensions` or `HOME/.vscode/extensions`
(the sandbox's home). Each case now puts the fake CLI first on that PATH (`monkeypatch` of the test process's
`PATH`, which the launcher's environment copies) and the fake extension under `HOME/.vscode-server/extensions`.

| Fault | In words | How (in `w2_67b_child.py`: `_check_claude_code`'s issues of one rule removed; drift and status follow the rest) |
|---|---|---|
| P27-6 (I4) | no drift for a CLI newer than the registry (DEC-210) | `CLI … newer than registry …` |
| P67B-13 | the CLI and the extension differing not reported (DEC-210) | `… differs from extension …` |
| P67B-14 | the extension's bundled binary hash at the recorded version not compared (DEC-214) | `extension binary sha256 mismatch …` |
| P67B-15 | the CLI below the minimum not a failure (DEC-210) | `CLI version … below minimum …` |
| P67B-16 | the extension below the minimum not a failure (DEC-210) | `extension version … below minimum …` |
| P67B-17 | the CLI at the recorded version with another hash not a failure (DEC-214) | `… has sha256 mismatch` |

| Case | Weak because (I4 §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_cli_newer_than_registry_is_drift` | the fake CLI was off doctor's PATH; `drift` always a key | P27-6: `doctor does not report drift for CLI newer than registry: {'status': 'pass', 'drift': False, 'cli_version': '2.1.300', …}` | green | the fake CLI is never read |
| `test_cli_and_extension_different_versions_is_drift` | the fake extension was not under the home doctor reads | P67B-13: `doctor does not report drift for CLI/extension version mismatch: {'status': 'pass', …}` | green | the planted input is not where doctor reads it |
| `test_extension_bundled_binary_different_sha256_is_drift` | the same two reasons | P67B-14: `doctor does not report drift for extension binary sha256 mismatch: {'status': 'pass', …}` | green | the planted input is not where doctor reads it |
| `test_cli_below_minimum_is_failure` | the fake never read; green on the real CLI's drift | P67B-15: `doctor raises no failure naming the CLI's 2.1.280: {'status': 'pass', …}`; P27-6: green (no longer rests on that drift) | green | the fake CLI is never read |
| `test_extension_below_minimum_is_failure` | the extension never read | P67B-16: `doctor raises no failure naming the extension's 2.1.280: {'status': 'drift', …}`; P27-6: green | green | the fake extension is never read |
| `test_cli_at_recorded_version_different_sha256_is_failure` | the real CLI (2.1.292) is not at the recorded version, so the rule never ran | P67B-17: `the CLI at its recorded version with another sha256 raises no failure (or only drift): {'status': 'pass', …}`; P27-6: green | green | the fake CLI is never read |

Head: 6 passed in 3.2 s (`g3-head.xml`), on small committed projects of their own. Each case first asserts that
doctor read the fakes (`cli_version`, `extension_version`, the hashes), then the issue its rule raises, with its
type (`drift` or `failure`), the section's status and, for the failures, `ok` not true. The CLI/extension case
records the extension's version and binary, so the difference is the only rule that applies.

### Group 4: rebuild (`test_w1_27_rebuild.py` ×5, `rebuild_r2` ×1, `rebuild_r3` ×1) and group 5 (`rebuild_r2`'s duplicate)

| Fault | In words | How (in `w2_67b_child.py`: `gov.rebuild.command.run` wrapped) |
|---|---|---|
| P27-7 (I4) | a reversed digest (CAP-20.a) | the result's `digest` reversed |
| P67B-18 | rebuild writes outside `.gov-runtime` | a file written at the project's root after the rebuild |
| P67B-20 | rebuild fails | `run` raises |
| P67B-21 | rebuild reports stores it never builds | `run` returns a result naming the lexical store recreated, and builds nothing |
| P67B-22 | rebuild needs the state an earlier run left (not in git) | `run` raises when no `.gov-runtime/store.db` exists |
| P67B-23 | rebuild needs a tool other than git and gitleaks | `run` raises when `codebase-memory-mcp` is not on PATH |
| P67B-24 | a store not rebuilt reported recreated | every `not_recreated` store set to `recreated`, its reason removed |
| P67B-25 | a constant reason for every store not rebuilt | each `not_recreated` reason set to `requires ollama and qwen3-embedding model` |
| P67B-26 | rebuild keeps every lexical row an earlier store held | the rows of `lexical_file` read before the rebuild are inserted again after it |

| Case | Weak because (I4 §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_rebuild_is_an_act_command` | accepted any envelope, REBUILD_FAILED included; the write scope never checked | P67B-18: `rebuild changed the project outside .gov-runtime: created: rebuild-wrote-here.txt`; P67B-20: `standard output is not one JSON document` (exit 1) | green | the assertion does not read what the case's name claims |
| `test_rebuild_recreates_derived_stores` | checked that `.gov-runtime` exists only | P67B-21: `rebuild did not recreate the store` | green, 5.9 s | the assertion does not read what the case's name claims |
| `test_fresh_clone_doctor_rebuild` | made no clone; doctor's verdict not read | P67B-21: `doctor does not report the clone's index fresh after the rebuild: {'status': 'unmeasured', 'index_status': 'missing', …}` | green | the assertion does not read what the case's name claims |
| `test_rebuild_needs_only_git` | the folder it deleted never existed; every tool of the machine on PATH | P67B-22 and P67B-23: the rebuild fails (`standard output is not one JSON document`, exit 1) | green, 6.0 s | the assertion does not read what the case's name claims |
| `test_rebuild_digest_matches_store_loader` | the envelope's session is a string, so the digests were never compared | P27-7: `rebuild digest 0cb7fa07… does not match store digest 98c0fbec…` | green | the assertion does not read what the case's name claims |
| `test_w1_27_rebuild_r2.py::test_rebuild_result_names_unreconstructed_stores` | `stores.semantic` always present | P67B-24: `the semantic index was not recreated but rebuild does not name it not_recreated with a reason` | green | the assertion does not read what the case's name claims |
| `test_w1_27_rebuild_r3.py::test_rebuild_result_names_derived_stores_with_measured_status` | computed its facts and never asserted them | P67B-25: `store semantic is not recreated with a constant or missing reason: {… 'reason': 'requires ollama and qwen3-embedding model' …}`; P67B-24: green (every store then recreated, which the case allows) | green | the assertion does not read what the case's name claims |
| `test_w1_27_rebuild_r2.py::test_rebuild_does_not_silently_drop_lexical_tables` (group 5, the duplicate) | the same table-presence check as `test_rebuild_recreates_lexical_index`; the planted row's fate never read | P67B-26: `the row planted for test.py, which git does not hold, survives the rebuild: lexical_file holds ['.gitleaks.toml', 'governance/project/path-map.yaml', 'test.py']` | green | the assertion does not read what the case's name claims |

Head: the eight, 7 passed and `test_rebuild_needs_only_git` red at first (`g4-head.xml`): with git alone on PATH,
`REBUILD_FAILED … rebuild failed on the lexical index: [Errno 2] No such file or directory: 'gitleaks'`. The
lexical index's owner runs the secrets filter on every file and fails closed without it (DEC-440), so the case
holds a PATH of git and gitleaks alone (green, `g4-head-needs-only-git.xml`), and whether "needs only git" admits
the secrets filter's tool is returned as a package (the designer's return). Every case runs on W1-27's tiny rebuild
project built for this worktree's code (`w2_67b_support.rebuild_project`, `rebuild`), except r3's, which keeps the
suite's fixtures. The clone case clones the tiny committed project it built, never this repository.

**The recovery check (`test_w1_27_recovery_check_r2.py` ×3).** The declared command
(`python3 -m gov.rebuild.check`) runs through `sh -c`, not a launcher, so the plugin also wraps `subprocess.run` in
the test process for that one command: its `PYTHONPATH` starts with `.gov-runtime/scratch/td-1b/plant/site/`, whose
`sitecustomize.py` applies the same faults in the check's process.

| Fault | In words | How |
|---|---|---|
| P67B-27 | the check fails open: it exits 0 whatever it found (CAP-38.b) | `sys.exit` exits 0 |
| P67B-28 | the check always finds a mismatch | `gov.store.digest` returns a new value each call |
| P67B-29 | the check exits non-zero without saying unmeasured (DEC-425) | `print`'s `unmeasured` becomes `store.db missing` |

| Case | Weak because (I4 §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_recovery_rebuild_command_not_unconditionally_exit_zero` | read the declaration's text, which never holds `exit(0)` | P67B-27: `the check command exits 0 on a tampered store as on a clean one, making it a fail-open`; P67B-28: `the check is not green on a clean store` | green | the assertion does not read what the case's name claims |
| `test_recovery_rebuild_command_exits_nonzero_on_tampered_store` | a crash also exits non-zero; no clean store held green | P67B-27: `the recovery-rebuild check exits 0 on a tampered store`; P67B-28: `the check is not green on the clean store (the control)` | green | the assertion does not read what the case's name claims |
| `test_recovery_rebuild_check_reports_unmeasured_when_no_store` | `unmeasured` never asserted; a non-zero exit of any cause passed | P67B-29: `the check does not report unmeasured when there is no store (DEC-425) … stderr: store.db missing` | green | the assertion does not read what the case's name claims |

Head: 3 passed in 4.0 s (`g4-head-recovery.xml`), on the tiny rebuild project with this worktree's code and its
check declaration. The tampered case names the mismatch (`mismatch` in the check's report, no traceback) and holds
the clean store green first.

**`rebuild_r8`'s write-scope case.** P67B-31 (in `w2_67b_child.py`): rebuild writes `$HOME/.gov-planted` after it
runs.

| Case | Weak because (I4 §2.2) | Plant: red (seen) | Head | Rewrite-Reason |
|---|---|---|---|---|
| `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_writes_only_under_gov_runtime` | snapshotted `sandbox.elsewhere`, which nothing uses, not the home | P67B-31: `the mode wrote in the home it was given: created: .gov-planted`; P67B-18: `the mode wrote outside .gov-runtime/` | green, 1.9 s | the assertion does not read what the case's name claims |

The code index's daemon folder (`/tmp/gov-cbm-<uid>`, I4's second place) is not snapshotted: in this session's
sandbox it is read-only (`[Errno 30] Read-only file system: '/tmp/gov-cbm-1000/…'`, the code index's reason on
every rebuild here), so what the mode writes there could not be seen; it is left open in the designer's return.

## Files

- `test_w2_67_copies.py`, `test_w2_67_temp_folders.py`: the new KPI tests (6 + 5 cases).
- `w2_67_tmp_probe.py`: the one case the nested runs start (not collected by a run of `tests`).
- `w2_67_doctor.py`: reading doctor's sections; a small committed project; doctor with this worktree's code.
- Revised in place: `test_w1_27_path_compliance_r2.py` (1 case), `test_w1_27_held_out.py` (2 cases),
  `test_w1_27_adoption.py` (3 cases).
