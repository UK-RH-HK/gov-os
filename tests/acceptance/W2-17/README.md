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
| S5 | `test_w2_17_pending.py::test_doctor_reports_a_pending_patch_with_its_fixes_and_the_quiet_point`, `test_w2_17_pending.py::test_doctor_reports_a_release_not_marked_patch_as_bigger_for_the_owner`, `test_w2_17_pending.py::test_doctor_says_up_to_date_for_a_clone_at_the_newest_release`, `test_w2_17_pending.py::test_doctor_with_an_unreadable_source_reports_nothing_pending_and_stays_as_healthy`, `test_w2_17_pending.py::test_doctor_holds_an_update_rolled_back_here`, `test_w2_17_pending.py::test_doctor_with_no_held_release_reports_nothing_pending` | `gov doctor --json`'s report has no `updates` part ("gov doctor's report has no `updates` part"); the other parts are as they were |
| S6 | `test_w2_17_session_start.py::test_session_start_prints_the_pending_line`, `test_w2_17_session_start.py::test_session_start_prints_nothing_when_up_to_date`, `test_w2_17_session_start.py::test_session_start_prints_nothing_when_the_source_cannot_be_read`, `test_w2_17_session_start.py::test_session_start_prints_nothing_while_the_update_is_held_after_a_rollback`, `test_w2_17_session_start.py::test_session_start_prints_nothing_when_gov_is_not_importable`, `test_w2_17_session_start.py::test_orchestrator_session_has_the_line_beside_its_existing_parts`, `test_w2_17_session_start.py::test_the_line_survives_a_long_tk_ready_output` | the hook prints no pending line: for B pending, its additionalContext (or no output at all) lacks `Gov OS update pending: this repository holds 0.9.0, 0.9.1 is the newest (patch): at the next quiet point.`; each "prints nothing" case fails at its control, the same line for its clone with B pending |
| S7 | `test_w2_17_rollback_command.py::test_the_update_records_the_pin_it_found_in_pin_before`, `test_w2_17_rollback_command.py::test_rollback_restores_every_tracked_file_of_release_a`, `test_w2_17_rollback_command.py::test_rollback_is_one_revert_commit_holding_its_record`, `test_w2_17_rollback_command.py::test_rollback_puts_the_pin_back_to_a_and_keeps_b_environment`, `test_w2_17_rollback_command.py::test_rollback_rebuilds_the_store_at_the_rollback_commit`, `test_w2_17_rollback_command.py::test_a_project_with_no_pin_before_the_update_has_none_after`, `test_w2_17_rollback_command.py::test_a_record_without_pin_before_rolls_back_through_the_fallback`, `test_w2_17_rollback_command.py::test_the_fallback_without_a_environment_is_refused_no_previous_pin`, `test_w2_17_rollback_command.py::test_a_later_commit_that_conflicts_is_refused_naming_the_path`, `test_w2_17_rollback_command.py::test_a_version_given_with_rollback_is_refused_usage`, `test_w2_17_rollback_command.py::test_a_project_with_no_update_to_undo_is_refused_no_update`, `test_w2_17_rollback_command.py::test_an_uncommitted_change_is_refused_dirty` | `gov update` has no `--rollback`: argparse exits 2 with no JSON envelope ("the following arguments are required: version", or "unrecognized arguments: --rollback" with a version, or the same from A's pinned gov), so no rollback and no `UPDATE_REFUSED` with reason `usage`, `no_update`, `dirty`, `no_previous_pin` or `rollback_conflict`; the update's record has no `pin_before` |

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

## The fixes S5 to S7 (DEC-1223 (6), RB-6 (a))

Written by the independent test designer from the fix section of `.tickets/DAEO-sdhj.md` ("Fix: pending-update
report and rollback") and `docs/emergency-2/proposals/RELEASE-ON-BEHALF.md` ("Adopted repositories: the quiet point
and the update", "Placement and size"), before any implementation of the fixes. Every case is of the acceptance
kind. Public interfaces only: `gov doctor --json`, the kernel's SessionStart hook of this worktree
(`template/governance/kernel/hooks/sessionstart.py`) run as a program, `gov install`, `gov update B`,
`gov update --rollback [--json]`, `retrieve --json`, `git` and the files of the clone. No module of the update, the
doctor, the install or the release code is imported. The fixtures above are reused unchanged; the new ones are
added to `conftest.py` and `w2_17_support.py`.

**What is planted.**

- **The planted sources** (`planted_sources`, copies of the source): on top of B's record commit, two empty commits
  each with a `Fix:` trailer, one chore with `Class: C` and none, then (but for one copy) a commit adding
  `docs/releases/0.9.1/kind.json`; the tag `v0.9.1` is moved onto the last commit. B's `manifest.json`,
  `manifest.sha256` and `template/` are the same objects at the moved tag (checked when it is built), so B still
  verifies, and `v0.9.0..v0.9.1` holds exactly two `Fix:` commits. Copies: `patch` (kind.json `{"kind": "patch",
  "rules": ...}`, and a decoy tag `v0.9.2` on a later commit with no record, which must never be the newest),
  `no-kind` (no kind.json), `unreadable-kind` (kind.json not JSON), `other-kind` (`{"kind": "minor"}`).
- **The clone names its source through a link**: a copy of the adopted project at A whose `_src_path` is set to a
  symbolic link (committed once); a case changes the source the clone reads by changing what the link names (the
  shared source, a planted source, or a path that does not exist), never the clone. The doctor's reference run is
  the same clone with the link naming the shared, untouched source; each other run differs from it only by the link.
- **Held after a rollback**: `governance/updates/0.9.1.rolled-back.json` committed in the clone. **No held release**:
  the lock made to state `release: null`.
- **The hook's environment**: a fake `tk` first on PATH whose `tk ready` prints nothing (or a line, or 300 lines,
  more than the hook's 10,000-character cap, where the case says); no `GOV_ROLE` but in the orchestrator case; no
  `GOV_TICKET`. "gov not importable" is the hook run without `PYTHONPATH` (the case checks first that gov does not
  import so).
- **The pinned update** (`pinned_updated`): a copy of the adopted project, `gov install 0.9.0` (A's environment
  `<common>/gov/envs/0.9.0`, its link and `pin.json`), then `gov update 0.9.1`. **The rollbacks** each run in a copy:
  of the pinned update, by A's environment's gov, `<common>/gov/envs/0.9.0/bin/gov update --rollback --json`, run
  without `PYTHONPATH` (the main rollback, the fallback, the conflict); of S2's update (no pin before it), and of the
  adopted project, by this worktree's gov (`python -m gov.cli.main`), since those copies hold no A environment (no
  pin before, `no_previous_pin`, `usage`, `no_update`, `dirty`). The fallback's record is planted by amending the
  update commit so its record holds no `pin_before` (still the commit that added the record); `no_previous_pin`
  also removes `<common>/gov/envs/0.9.0`. The conflict is a later commit changing
  `governance/kernel/w2-17/updated.md`, which the update changed. Note: under W2-18's pin dispatch
  (`gov.install.dispatch`), a gov started in a repository with a pin re-runs the pin's gov unless `GOV_PIN=off`;
  so, as the code stands, A's environment's gov started in the clone pinned at B hands the rollback to B's gov. Both
  wheels are built from this worktree's code, so the cases cannot tell which gov ran; they hold under either
  answer to that question (in the designer's return).

**How the fix lines are read.**

- **S5**: `held` and `newest` are the versions (`0.9.0`, `0.9.1`); `fixes` is an integer; the patch step must contain
  `at the next quiet point`, the bigger step `owner decides` and `gov update 0.9.1`, the held step `held: rolled back
  here; waits for a newer release`. Up to date is the clone adopted at B with the shared source: `pending` false,
  the summary holds `up to date (0.9.1)`, and a `reason` (the line's "no verified newer record ... with reason").
  "Healthy and the other parts unchanged" is doctor's exit code, `healthy` and every part's `status` but `updates`,
  equal to the reference run's, in every doctor case but the clone at B (whose source is already untouched).
- **S6**: the line is matched whole, as one line of `additionalContext`, in the line's own form. The orchestrator
  case runs the hook twice in the same clone with `GOV_ROLE=orchestrator` and a `tk ready` line: with no readable
  source (its parts as they are), then with B pending; every part of the first must be in the second, beside the
  line. "Critical, never trimmed by the cap" is the line kept whole beside a `tk ready` output longer than the cap.
- **S7**: "A's tracked state" is `git ls-tree -r` of the commit before the update (paths, modes, blobs), equal to
  HEAD's but for `governance/updates/0.9.1.rolled-back.json`. "One commit" is HEAD's parent being the update commit.
  The record is checked for its keys and for `from`, `to` and `update_commit`; `revert_commit` and `pin` only for
  presence (see the spec note in the designer's return: the record is in the revert commit, so it cannot name
  that commit). The pin is checked by the link's target and `pin.json` (as JSON): equal to the pin before the
  update; because the case runs in a copy of the pinned update, whose recorded link names the origin's A
  environment, the copy's own `<common>/gov/envs/0.9.0` is accepted too. The store is checked by `retrieve --json`'s
  `store.commit` equal to HEAD, through the restored pin's gov (or this worktree's gov where no pin is left). A
  refusal asks for the `--json` envelope's `UPDATE_REFUSED` and `details.reason`, with HEAD, every file outside
  `.git` and `<common>/gov/` unchanged and no revert left in progress. Not covered: a failed `gov rebuild` after the
  rollback (`UPDATE_STORE_FAILED`), which the line names but does not verify; it has no public way to plant.

Run the fixes alone: `TMPDIR=$(mktemp -d) python3 -m pytest tests/acceptance/W2-17/test_w2_17_pending.py
tests/acceptance/W2-17/test_w2_17_session_start.py tests/acceptance/W2-17/test_w2_17_rollback_command.py -n auto
--dist loadfile` (each file's session fixtures built once on its worker; the rollback file builds the update twice).
