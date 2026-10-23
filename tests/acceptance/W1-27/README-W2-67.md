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

## Files

- `test_w2_67_copies.py`, `test_w2_67_temp_folders.py`: the new KPI tests (6 + 5 cases).
- `w2_67_tmp_probe.py`: the one case the nested runs start (not collected by a run of `tests`).
- `w2_67_doctor.py`: reading doctor's sections; a small committed project; doctor with this worktree's code.
- Revised in place: `test_w1_27_path_compliance_r2.py` (1 case), `test_w1_27_held_out.py` (2 cases),
  `test_w1_27_adoption.py` (3 cases).
