# W2-178 acceptance tests: the auditor's copy of a set leaves out its dropped questions

Ticket DAEO-7oxm (W2-178), profile FULL, class C2 (DEC-1101 (2), DEC-820 (b), (d), DEC-1052, DEC-1120). Written by the
independent test designer (MR-3) from the ticket's KPI lines S1 and F1-F3 and the lead's brief (td-1), before the
engineer's code, reading only the base `03393ee51` (the ticket's claim commit, also the merge-base with `w2/integrate`;
the script at W2-173's merge). Never read: the branch `w2/W2-178`, its unit tests or its evidence.

## How they run

    env HOME=<an empty scratch folder> PYTHONUSERBASE=$HOME_REAL/.local TMPDIR=<a folder outside the repository> \
      PYTHONPATH=<worktree>/src bash <heavy_slot.sh> python3 -m pytest tests/acceptance/W2-178 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
    python3 -m gov.cli.main accept W2-178 --root <worktree>

About 26 s, serial, no model, network or GPU. No test name carries `real`, `green_here` or `time_limit`, so the
exclusion leaves nothing of this folder out.

- **W2-149's planted world, imported, never copied** (`conftest.py`): W2-149's planted repository once per session and,
  per case, its `World` (planted HOME, sets root, runs and trees folders under pytest's `tmp_path`; `World.check_planted`
  fails every launch on a real location) with the stub `claude`. `w2_178_support.py` adds the planted `dropped/` files,
  the base script and the wall snapshots; W2-173's `auditor_out()` is the one helper taken from its folder.
- **The planted set** is W2-149's `memory-verdict-3` (`hidden/q01.yaml`, `hidden/q02.yaml`, `hidden/sub/q03.yaml`) with
  `hidden/dropped/q07.yaml`, `hidden/dropped/x/q08.yaml` and `hidden/dropped/x/y/q11.yaml` added; look-alikes
  (`hidden/dropped.yaml`, `hidden/dropped-items/q10.yaml`, `hidden/droppedq/q13.yaml`), a folder named `dropped` one level
  down (`hidden/sub/dropped/q09.yaml`) and a non-text file (`hidden/sub/raw.bin`) for the cases that need them.
- **The base script** is taken out of git at `03393ee51` (with its `indep-schemas` folder) into a temporary folder and run
  the way W2-149's world runs the head's, in the same planted world, so two builds differ only in the script. The
  builds are `--dry` with a fixed `--seed`; each wall is read right after its build and removed with its tree (a later
  wall's settings deny any earlier wall of the kind still there, which would differ for that alone).
- **What differs between two builds of one script with one seed:** only the run id, which sits in the wall's and tree's
  paths that the settings, `CLAUDE.md` and `WALL.json` name; and `WALL.json`'s `settings_sha256`, the hash of a settings
  file that names the run id (checked against the wall's own settings file, then replaced by the hash of the settings with
  the id replaced). Every file's mode is compared as well. The sanity cases run the base script twice, for the writer's
  round 2, the checker and the auditor, and show those are the only two.

## The interface held (the lead's brief; readings marked)

- **S1 / F1, new.** For `--kind auditor`, `input/set/` holds every file of the set except those under `hidden/dropped/`
  (the whole subtree, to any depth); no path, file or folder, exists under `input/set/dropped`; every other file is there
  at its relative path, byte for byte. Also through a delivered (stubbed) run: the packed wall's tar holds none.
- **S1 / F1, unchanged.** The writer's (round 2) and the checker's walls from the same set, `dropped/` included, equal
  the base script's walls entry for entry, byte for byte, and still carry `input/set/dropped/...`. The auditor's wall of a
  set with no `dropped/` folder equals the base's too.
- **Readings (named in `unresolved`).** `hidden/dropped/` is the folder directly under `hidden/`; a file `dropped.yaml`, a
  folder `dropped-items/` or `droppedq/`, and `hidden/sub/dropped/` are not under it and stay. A set whose every file is
  under `dropped/` and set-up A's overlap auditor are not tested. F3's allowed paths also take the ticket's own process
  records (W1-01's reading, as in W2-173's F4 case): `.tickets/DAEO-7oxm.md`, `docs/checkpoints/DAEO-7oxm/**`,
  `docs/probes/DAEO-7oxm/**`.

## The map

| KPI id | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_wall_holds_nothing_under_dropped` | the wall's `input/set/` carries `dropped/q07.yaml`, `dropped/x/q08.yaml`, `dropped/x/y/q11.yaml` |
| S1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_set_is_exactly_the_files_outside_dropped` | the three dropped files are extra in `input/set/` |
| S1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_wall_differs_from_the_base_build_only_by_the_dropped_subtree` | the head's wall still holds the dropped subtree the base's did |
| S1 | `test_w2_178_auditor.py::test_s1_a_delivered_auditor_run_packs_a_wall_without_the_dropped_files` | the packed wall's tar holds `input/set/dropped/...` |
| S1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_wall_holds_every_other_file_byte_identical` | green today (holds already) |
| S1 | `test_w2_178_auditor.py::test_s1_names_that_only_look_like_dropped_stay_in_the_auditor_s_wall` | green today (holds already) |
| S1 | `test_w2_178_auditor.py::test_s1_a_folder_named_dropped_below_another_folder_stays` | green today (holds already) |
| S1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_other_inputs_are_still_staged` | green today (holds already) |
| S1 | `test_w2_178_auditor.py::test_s1_a_set_with_no_dropped_folder_builds_the_same_auditor_wall_as_before` | green today (holds already) |
| S1 | `test_w2_178_auditor.py::test_s1_building_the_auditor_s_wall_leaves_the_set_on_disk_as_it_was` | green today (holds already) |
| S1 | `test_w2_178_unchanged.py::test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it[writer-round-2]` | green today (holds already) |
| S1 | `test_w2_178_unchanged.py::test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it[checker]` | green today (holds already) |
| S1 | `test_w2_178_unchanged.py::test_s1_the_wall_of_a_set_without_a_dropped_folder_equals_the_base_build[writer-round-2]` | green today (holds already) |
| S1 | `test_w2_178_unchanged.py::test_s1_the_wall_of_a_set_without_a_dropped_folder_equals_the_base_build[checker]` | green today (holds already) |
| S1 | `test_w2_178_unchanged.py::test_s1_sanity_the_base_script_twice_gives_equal_walls_but_for_the_run_id[writer-round-2]` | green (the base against itself) |
| S1 | `test_w2_178_unchanged.py::test_s1_sanity_the_base_script_twice_gives_equal_walls_but_for_the_run_id[checker]` | green (the base against itself) |
| S1 | `test_w2_178_unchanged.py::test_s1_sanity_the_base_script_twice_gives_equal_walls_but_for_the_run_id[auditor]` | green (the base against itself) |
| F1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_wall_holds_nothing_under_dropped` | the wall's `input/set/` carries the dropped files |
| F1 | `test_w2_178_auditor.py::test_s1_the_auditor_s_wall_differs_from_the_base_build_only_by_the_dropped_subtree` | the head's wall still holds the dropped subtree |
| F1 | `test_w2_178_unchanged.py::test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it[writer-round-2]` | green today (holds already) |
| F1 | `test_w2_178_unchanged.py::test_s1_the_wall_equals_the_base_build_byte_for_byte_with_the_dropped_files_in_it[checker]` | green today (holds already) |
| F1 | `test_w2_178_unchanged.py::test_f1_the_dropped_files_stay_in_the_source_set_after_the_build[writer-round-2]` | green today (holds already) |
| F1 | `test_w2_178_unchanged.py::test_f1_the_dropped_files_stay_in_the_source_set_after_the_build[checker]` | green today (holds already) |
| F2 | `test_w2_178_unchanged.py::test_f2_no_line_of_this_folder_names_the_owner_s_sets_root` | green today (holds already) |
| F3 | `test_w2_178_unchanged.py::test_f3_the_branch_changes_only_the_ticket_s_paths` | green on this branch (it changes only `tests/acceptance/W2-178/`); judged on the engineer's branch |

At `03393ee51`: 4 red, 17 green (21 cases). With a throw-away copy of the script that leaves `hidden/dropped/` out of the
auditor's set only (kept outside the repository): 21 green; with a prefix match (`startswith("dropped")`) the look-alike
case goes red; with any folder named `dropped` the nested case goes red.
