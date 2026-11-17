# W2-17 acceptance tests: `gov update`

Written by the independent test designer (MR-3) from the ticket's six KPI lines (`.tickets/DAEO-sdhj.md`, profile
FULL) and the interface the ticket lead fixed for `gov install` and `gov update` (base commit 72cfbbcfb), before any
implementation. Every case is of the acceptance kind. Public interfaces only: the `gov` command line (`gov update <B>
[--check] [--source] [--wheel] --json` and its text form, `gov adapters generate`, the pinned gov's `--version`,
`doctor --json` and `retrieve --json`), `copier`, `git`, and the files of the project: its tree,
`governance/framework.lock`, `.copier-answers.yml`, `governance/updates/<B>.json`,
`governance/updates/<B>/release/<path>` and `<common>/gov/`. No module of the update, the install or the release code
is imported by a test.

## The fixtures

- **The source** (`w2_17_support.build_source`): W2-16's stand-in Gov OS repository (single named files of this
  worktree: `template/`, `src/gov/`, `pyproject.toml`, `copier.yml`), built through W2-16's release seam as the owner
  in person. Release A = 0.9.0 (`pyproject.toml` 0.9.0), tagged `v0.9.0` on its record commit. Release B = 0.9.1
  (`pyproject.toml` 0.9.1), tagged `v0.9.1`, whose template, against A's:
  - updates `governance/kernel/w2-17/updated.md`, adds `.../added.md`, removes `.../removed.md`;
  - changes the overlay file `governance/project/path-map.yaml` (a comment line);
  - changes the skill `.rulesync/skills/audit/SKILL.md` (a marker line);
  - changes line 12 of `.../merged.md` (the project changes line 2: a clean merge) and line 3 of `.../conflict.md`
    (the project changes line 3 too: a conflict);
  - leaves `.../kept.md` (the project changes it) and `.../unchanged.md` alone.
- **The adopted project**: `copier copy --vcs-ref v0.9.0 --trust` (its Copier task writes the lock naming A),
  `gov adapters generate` (rulesync), then the project's own changes (`kept.md`, `merged.md`, `conflict.md`, a line
  in `governance/project/test-map.yaml`, its own file `openspec/specs/w2-17-own.md`), all committed.
- **Shared outcomes**: the dry run (`--check --json`, then the text form) and the update (`--json`) each run once
  per session in their own copy of the adopted project; the cases that only read an outcome share them. The rollback
  and every refusal run in their own copy.
- **Environment**: a fake `HOME` per run, `PYTHONUSERBASE` the real user base, `GOV_REBUILD_LOCK` a file of the run's
  own sandbox, copier, rulesync and node found on `PATH` (or under `~/.local/bin` and `~/.nvm`). The fixture path map
  has no embedded namespace, so the store refresh calls no embedder. `gov` is this worktree's (`python -m
  gov.cli.main`, `PYTHONPATH` its `src/`); the pinned gov runs without `PYTHONPATH`.
- A fixture that cannot be built fails its cases with "W2-17 fixture could not be built (not the feature under
  test)", never as the feature's failure.

Run: `TMPDIR=$(mktemp -d) python3 -m pytest tests/acceptance/W2-17 -n 2` (one session builds the source, the
adoptions, the dry run and the update: a few minutes), or `gov accept W2-17`.

## The map

| KPI line | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_17_check.py::test_check_reports_versions_checks_and_the_whole_plan`, `test_w2_17_check.py::test_check_text_form_prints_the_same_plan`, `test_w2_17_check.py::test_check_changes_nothing` | `gov update` does not exist: exit 2, "invalid choice: 'update'", no JSON report |
| S2 | `test_w2_17_update.py::test_update_gives_every_unchanged_shipped_file_release_b_bytes`, `test_w2_17_update.py::test_update_keeps_the_projects_change_and_every_overlay_file`, `test_w2_17_update.py::test_update_writes_answers_and_lock_and_doctor_drifts_only_on_kept_files`, `test_w2_17_update.py::test_update_installs_the_pinned_gov_of_release_b`, `test_w2_17_update.py::test_update_regenerates_the_skill_release_b_changed`, `test_w2_17_update.py::test_update_refreshes_the_memory_store_at_the_update_commit`, `test_w2_17_update.py::test_update_is_one_commit_holding_its_record` | `gov update` does not exist: exit 2, "invalid choice: 'update'" |
| S3 | `test_w2_17_local_changes.py::test_a_clean_three_way_merge_holds_both_changes`, `test_w2_17_local_changes.py::test_a_conflicting_change_keeps_the_projects_file_and_writes_release_b_copy_aside`, `test_w2_17_local_changes.py::test_no_file_the_update_wrote_holds_a_conflict_marker` | `gov update` does not exist: exit 2, "invalid choice: 'update'" |
| S4 | `test_w2_17_rollback.py::test_failed_adapter_generation_rolls_back_to_the_recorded_point` | `gov update` does not exist: exit 2 with no JSON envelope, so no `UPDATE_FAILED` naming the step and `rolled_back` |
| F1 | `test_w2_17_hash_refusals.py::test_a_release_failing_hash_verification_is_refused_and_nothing_changes` | `gov update` does not exist: exit 2 with no JSON envelope, so no `UPDATE_REFUSED` with reason `manifest`, `files` or `wheel` (six cases: three mismatches, each with and without `--check`) |
| F2 | `test_w2_17_project_refusals.py::test_an_uncommitted_change_is_refused_naming_its_path`, `test_w2_17_project_refusals.py::test_a_project_without_a_lock_is_refused_naming_the_lock`, `test_w2_17_project_refusals.py::test_a_lock_stating_release_null_is_refused_naming_the_lock`, `test_w2_17_project_refusals.py::test_a_project_already_at_b_is_refused_saying_so` | `gov update` does not exist: exit 2 with no JSON envelope, so no `UPDATE_REFUSED` with reason `dirty`, `not_adopted` or `same` |

A refusal case is red on the base because it asks for the feature's own refusal (the `--json` envelope's
`UPDATE_REFUSED` and its `details.reason`), not merely a non-zero exit: argparse's exit 2 for an unknown command
is not the refusal the line asks for.

## How the lines are read

- **S1**: the plan's outcomes are checked in the `--json` report (`files.updated`, `added`, `removed`, `merged`,
  `kept`, `conflicts`, `overlay`), each W2-17 path under its outcome and no other; the text form must print A, B,
  "passed", B's manifest sha256 and every planned path. "Byte-identical" is every file and folder outside `.git`
  (bytes and mode) and HEAD as before; "no pin" is `<common>/gov/` absent.
- **S2**: "release B's bytes" is checked for every file under `template/` at `v0.9.1` that is not a `.jinja` file,
  not under `governance/project/` and not one the project changed. The doctor's drift is allowed on the files the
  update reports kept, merged or conflicts (the interface's step 4: a merged file holds the project's lines too, so
  it cannot match B's hash). The store refresh is checked by the report (`store: refreshed`) and by the pinned gov's
  `retrieve --json`, whose `store.commit` must be the update commit.
- **S3**: shares the S2 update (the clean merge and the conflict are planted in the same project).
- **S4**: the failing step is adapter generation (a `rulesync` first on `PATH` that exits 1); an ignored file
  planted before (`.gov-runtime/`) must survive; the pin before is none.
- **F1**: the manifest and the file mismatches are planted in copies of the source whose tag `v0.9.1` is moved onto
  a tampering commit, passed by `--source`; the wheel mismatch is a `--wheel` file with the manifest's wheel name and
  other bytes.
- **F2**: an uncommitted change is a changed tracked file and, as a second case, a new untracked file.
