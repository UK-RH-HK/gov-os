# W2-16 acceptance tests: immutable, hash-pinned releases (CAP-43.b lite)

Ticket `DAEO-49o5`, profile FULL. Written by an Independent Test Designer before implementation (MR-3), from the
ticket's KPI lines, Contract v4.2 (CAP-43, CAP-43.a to CAP-43.d, CAP-02, CAP-02.a, CAP-02.c), the list rows
W2-H029, W2-L002, W2-L014, W2-L227, W2-M174, W2-M175 with their origin lines, and DEC-722, DEC-023, DEC-027,
DEC-488, DEC-493, DEC-499, DEC-542, DEC-194, DEC-244, DEC-654, DEC-221, DEC-752, DEC-753. 75 cases in three files;
10 more in a fourth, added after implementation from the first review of W2-16 (DEC-136; see "Cases added after the
first review" below); 29 more in a fifth, the last round ordered by DEC-761 after the second review (see "The last
round" below); 28 more in a sixth, round 3 ordered by DEC-772 item 1 (see "Round 3" below). 142 cases in all.

Run from this worktree:

```
PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-16/src python3 -m pytest tests/acceptance/W2-16 -q -p no:cacheprovider -rs
```

## How the cases run this worktree's code

`REPO_ROOT` is the worktree that holds this folder; `SRC` is its `src/`.

- **`gov release`** runs as `sys.executable -m gov.cli.main release …` with `PYTHONPATH=<SRC>`, in a temporary
  repository (never in this worktree: `run_gov` refuses it).
- **`gov doctor --json`** runs through W1-07's launcher with `PYTHONPATH=<SRC>` (`w1_39_support.doctor`).
- **What a Copier task finds:** first on `PATH`, a `gov` script that puts `<SRC>` first on `sys.path` before it
  imports `gov` (so it is this worktree's code whatever `PYTHONPATH` says); and `PYTHONPATH=<SRC>` for any
  `python3` the task runs (W1-39's arrangement). The W2-M175 case takes `PYTHONPATH` away and puts first on
  `PATH` a `python3` (and `python`) that runs this machine's Python with `-I`, which imports no `gov`.
- `test_every_gov_the_suite_runs_is_this_worktree_s` checks all three: each imports `gov` from `<SRC>`.
- **`GOV_ROLE` is unset** in every `gov` and Copier run of the suite (each environment is built from scratch, so
  the role of the session that runs the tests never reaches them): the caller is the owner in a plain terminal
  (DEC-365, DEC-761). Only the role cases of the last round and round 3's seam cases set it (or `GOV_TICKET`), per
  call. Keep it so; the guard `test_the_suite_runs_gov_and_copier_with_gov_role_unset` holds it.
- **The suite's own releases are built through the seam** (round 3, DEC-772 item 1): `build_release` calls
  `gov.release.command._release_test` in a new process as the owner in person (a planted chain with no Claude Code
  session that reaches process 1, a pseudo-terminal, the shown code typed back, `GOV_ROLE` and `GOV_TICKET`
  absent), because `gov release <version>` refuses from every test run. The driver imports the code with
  `PYTHONPATH=<SRC>`, like every other `gov` the suite runs.

## What the cases use

Public interfaces only: the `gov` command line (`gov release <version>`, `gov doctor --json`), the tool `copier`
(the registered 9.18.2, needed and never skipped, as W1-39 holds it), the files of a created project
(`governance/framework.lock`, `.copier-answers.yml`), the files of a release record, and `git` in temporary
repositories. No module of `src/gov/lock/` or of the release code is imported or named, but one, from round 3: the
seam `gov.release.command._release_test` of DEC-772 item 1, imported only inside the seam driver's own process.

- **A stand-in Gov OS repository, never a copy of this one.** `build_gov_os_repository` builds it in a
  temporary folder from single named files of this worktree, listed by `git ls-files` and limited to
  `.gitignore`, `pyproject.toml`, `copier.yml`, `template/` and `src/gov/` (no bytecode, nothing under
  `governance/project/`), copied one by one as W1-39's `assemble_source` copies the template source. Two
  changes are made there, never here: its `pyproject.toml` declares the CLI version `0.7.3` (so the manifest's
  CLI version can be told from the release version and from this worktree's `0.1.0`), and its template holds
  one more kernel file, `governance/kernel/README.w2-16.md`, which the second release changes. Its branch is
  `w2/integrate`. Releases `1.4.0` and `1.5.0` are built there with `gov release`; the test commits the record
  where the command left it uncommitted, and tags the release commit `v1.4.0` / `v1.5.0`, unsigned, standing
  for the owner. That repository is the template source Copier copies and updates from.
- **W1-39's template source** (`copier.yml` and `template/` alone, tagged `v0.1.0`, no release record) is the
  source of the cases that need no release (W2-M174, W2-L227, W2-M175's first form, W2-H029's first form), so
  they are red today on their own assertion.
- Copier runs as `copier copy --defaults --trust --vcs-ref <tag> <source> <destination>` and
  `copier update --defaults --trust --vcs-ref <tag>`, with an empty temporary `HOME`, no network.
- Releases and projects that no case changes are built once per session; a case that changes one works on a
  copy of the temporary folder. The whole suite takes seconds red; with an implementation it is a few dozen
  Copier runs and a handful of release builds, well inside the 20-minute limit.

## The interface the cases assume, and the source of each point

| Point | Assumed | Source |
|---|---|---|
| Command | `gov release <version>`, with no other argument, builds the release | KPI success 1; DEC-753 (`release` is a new `gov` command) |
| Where it is built | a clean commit that `w2/integrate` contains, in the repository `gov release` runs in | KPI success 1; WAVE_2_WBS §0 rule 2 and the release commits note ("Release commits (W2-16) are on `w2/integrate`") |
| Where the record goes | files under `docs/releases/`; nothing else in the tree changes (ignored build products aside); the command may commit the record itself or leave it for a commit | the ticket's allowed path `docs/releases/**`; KPI success 2 (the owner tags the *release commit*) |
| The manifest | the one record file whose name holds `manifest` that parses (JSON or YAML) as a map naming the version | "Its manifest holds" (KPI success 1); no key name or file format is fixed |
| Version | a value equal to the semantic version (`1.4.0`) | KPI success 1 |
| Commit | a value equal to the full id of the commit the release was built from | KPI success 1; CAP-43's acceptance ("template tag, commit") |
| Shipped files | every file under `template/` at that commit, with the sha256 of its bytes, by path as a project sees it or with `template/` before it; as `<path>: <sha256>` or a map with `path`/`file`/`name` and `sha256` | KPI success 1 ("every shipped file with its sha256"); CAP-43.b; W1-39 (sha256, lower-case hex) |
| Wheel hash | a sha256 under a key that names the wheel (or a `.whl` name); a `.whl` file in the record has that hash | KPI success 1 |
| CLI version | a value equal to the version the release commit's `pyproject.toml` declares | KPI success 1; CAP-43.d ("CLI/runtime versions"), delivered ahead (CAP-43 wave note) |
| Schema versions | a non-empty part under a key that names schemas (not a file path) names every kernel schema (`ticket`, …) | KPI success 1; CAP-43.d; see package P-4 |
| Release notes | a non-empty value under a key that names notes | KPI success 1; CAP-43.d |
| Manifest's own hash | the sha256 of the manifest file's bytes, stated in another file of the record | KPI success 1 ("a reader can recompute it and find it equal"); see package P-2 |
| No tag, no signature | the command adds no tag, makes no signed commit, writes no signature file | KPI success 2; DEC-722 item 2; CAP-02.c (W3) |
| The owner's tag | `v<version>`, lightweight or annotated, unsigned | W1-39's tags (`v0.1.0`, `v0.2.0`); DEC-023 ("tags = releases") |
| Lock | `governance/framework.lock`, a YAML map, its file-hash manifest under `manifest` as W1-39 holds it | W1-39's README |
| Release in the lock | a value equal to the version, and a value equal to the manifest's own hash; no key name fixed | KPI success 4 |
| A refusal by Copier | the run exits non-zero, with no traceback, its output names the file at fault (or `manifest`), and no lock records the refused release | the failure line; CAP-02 ("DRIFT naming the edited file") |
| A refusal by doctor | the `framework_lock` part has status `fail` (not `pass`, not `unmeasured`) and doctor exits non-zero; file faults are DRIFT naming the file | the failure line; W1-39's `assert_drift_naming`; DEC-499 |
| Vendored version | a value equal to `vendored.yaml`'s `version` (`v6.4.2`, or `6.4.2`), in a part of the manifest that names `superpowers` or the three skills | KPI success 5; W2-L014; DEC-246 |
| Vendored licence | the text of `vendor/superpowers/LICENSE` (whitespace collapsed) is in a file of the record or a value of the manifest | KPI success 5; W2-L002; DEC-194, DEC-244 (the copies stay unchanged) |

## The failure line's reading (stated as the lead's, and the designer's)

"Refused by `gov install`, `gov update` and `gov doctor`": there is no `gov install` or `gov update` in this tree;
W2-18 and W2-17 build them on this ticket. The install and update paths that exist are `copier copy` and
`copier update` of the template (its task is this ticket's: `copier.yml` is in its paths), and `gov doctor`. The
refusal is tested through those three. The KPI can be tested without the two commands; W2-17's and W2-18's own
KPIs ("an update to a release that fails hash verification refuses", "a hash-verified release") hold them.

## KPI lines and their cases

Red reasons: **R** = `gov release` does not exist (`gov: error: argument <command>: invalid choice: 'release'`,
exit 2): the session fixture `releases` fails at set-up, and every case that needs a release is an *error at
set-up* with that sentence. Otherwise the reason is the case's own assertion, as written.

### Success 1 [CAP-43.b lite]: `gov release <version>` and its manifest — `test_w2_16_release.py`

| Case | Holds | Red |
|---|---|---|
| `test_a_release_writes_its_record_under_docs_releases_and_changes_nothing_else` (2: each release) | record under `docs/releases/`, nothing else touched | R |
| `test_the_manifest_holds_the_semantic_version` (2) | version | R |
| `test_the_manifest_holds_the_full_commit_the_release_was_built_from` (2) | commit, in full | R |
| `test_the_manifest_lists_every_shipped_file_with_its_sha256` (2) | every shipped file with its sha256 | R |
| `test_the_second_release_lists_the_shipped_file_that_changed_with_its_new_hash` | each release hashes its own commit | R |
| `test_the_manifest_holds_the_wheel_hash` (2) | wheel hash | R |
| `test_the_manifest_holds_the_cli_version` (2) | CLI version | R |
| `test_the_manifest_holds_the_schema_versions` (2) | schema versions | R |
| `test_the_manifest_holds_release_notes` (2) | release notes | R |
| `test_the_manifest_s_own_hash_is_in_the_record_and_a_reader_finds_it_equal` (2) | the manifest's own hash | R |
| `test_no_release_from_a_tree_with_uncommitted_or_untracked_changes` (4: a tracked file changed, a change staged, an untracked file, an untracked file in the template) | refused, nothing written (every file and folder, refs, HEAD, index) | R |
| `test_no_release_from_a_commit_that_is_not_on_w2_integrate` (2: another branch, a detached commit) | refused, nothing written | R |
| `test_no_release_with_a_version_that_is_not_a_semantic_version` (6: `1.4`, `1.4.0.0`, `latest`, `01.4.0`, `1.4.0-`, `1.4.x`) | refused, nothing written | R |
| `test_no_release_without_a_version` | refused, nothing written | R |

The refusal cases take the `releases` fixture on purpose: today any `gov release` call is refused (the command
does not exist), so a refusal alone would test nothing. With the fixture each one shows that the same stand-in,
clean, on `w2/integrate`, with a valid version, does release; the case's own change is what is refused.

### Success 2 (CAP-02.c stays in Wave 3, DEC-722): the owner tags, unsigned — release and install files

| Case | Holds | Red |
|---|---|---|
| `test_building_a_release_creates_no_tag` (2) | agents never tag | R |
| `test_building_a_release_signs_nothing` (2) | no signed commit, no signature file | R |
| `test_a_release_installed_from_an_unsigned_lightweight_tag_is_accepted` | `git tag -v` fails on the tag; the copy installs and its lock records the release | R |
| `test_a_release_installed_from_an_unsigned_annotated_tag_is_accepted` | the same with an annotated unsigned tag | R |

### Success 3 [CAP-43]: a release is immutable

| Case | Holds | Red |
|---|---|---|
| `test_the_same_version_from_another_commit_is_refused_and_its_record_left_as_it_was` (2: each version) | refused; the existing record byte for byte as it was (whole-tree snapshot) | R |
| "changing a file after release is refused": the failure line's cases below | | |

### Success 4: framework.lock records the release; the rows — `test_w2_16_install.py`, `test_w2_16_doctor.py`

| Case | Holds | Red |
|---|---|---|
| `test_a_project_copied_from_a_release_tag_records_the_release_version_in_its_lock` | at copy: version | R |
| `test_a_project_copied_from_a_release_tag_records_the_manifest_hash_in_its_lock` | at copy: manifest hash | R |
| `test_a_project_updated_to_a_later_release_records_that_release_in_its_lock` | at update: the later version and hash, not the first's | R |
| `test_doctor_passes_on_a_project_installed_from_a_release` (2: copied, updated) | an untouched release install is a measured MATCH, doctor exits 0 | R (a guard: what must hold once releases exist) |
| **W2-L227** `test_copying_template_directly_gives_a_lock_or_doctor_names_the_missing_step` | `template/` copied as it is: either the copy holds a lock and doctor's lock part is measured, or the part fails, doctor exits non-zero, and the part names `framework.lock` and `copier` (DEC-654) | own: `{"match": "MISSING", "reason": "no framework.lock", "status": "unmeasured"}` |
| **W2-H029** `test_deleting_both_the_lock_and_the_answers_file_does_not_silence_the_comparison` (2: plain source, release) | an installed kernel with neither file: the part fails, doctor exits non-zero | plain: own (`unmeasured`, exit 0); release: R |
| **W2-H029** `test_editing_the_lock_manifest_together_with_a_kernel_file_does_not_give_a_match` | a kernel file and its hash in the lock's `manifest` edited together: the part fails | R (today: MATCH, exit 0 — seen in the trial below) |
| **W2-M174** `test_a_kernel_file_whose_mode_changed_is_drift_naming_it` (2: `bin/tk` loses its executable bit, `hooks/stop.py` gains one) | file modes | own: `{"match": "MATCH", "status": "pass"}` |
| **W2-M174** `test_an_empty_folder_added_to_the_kernel_is_drift_naming_it` | folders | own: MATCH |
| **W2-M174** `test_a_declared_shipped_path_outside_the_kernel_is_compared` | the lock names at least one shipped path outside `governance/kernel/` (never the overlay, the lock or the answers file), and a one-byte edit there is DRIFT naming it | own: "the lock declares no shipped path outside governance/kernel/" |
| Guard `test_an_overlay_file_the_project_edits_is_still_not_drift` | declared paths never reach the overlay (ADR-0002 §5) | **green today**: a guard that must already hold |
| **W2-M175** `test_the_lock_task_runs_where_python3_does_not_import_gov` (2: plain source, release) | `gov` on `PATH` is this worktree's and runs; `python3` on `PATH` cannot import `gov`; `copier copy` succeeds and writes the lock | plain: own (`python3 -m gov.lock`: `No module named 'gov'`, exit 1); release: R |
| Guard `test_the_gov_os_repository_itself_stays_unmeasured` (2: before any release, holding releases) | the stand-in Gov OS repository (no installed kernel) keeps its lock part `unmeasured`, as this repository and W1-27's cases hold it (Wave 2 exit criterion 3) | first: **green today** (a guard); second: R |
| Guard `test_every_gov_the_suite_runs_is_this_worktree_s` | the suite's three ways to `gov` import this worktree's | **green today**: a guard |

**W2-M174, `__pycache__/`.** The row's title lists `__pycache__` among what the comparison ignores; its "closes
when" names modes, folders and declared non-kernel paths only, and DEC-488 leaves `__pycache__/` out (W1-39's
`test_a_file_in_a_bytecode_folder_inside_the_kernel_is_not_drift` holds it). No case here changes that; see
package P-5. The cases run on W1-39's plain source so they are red on their own assertion; a release install
gets the same comparison.

**W2-M175 within DEC-542.** W1-07 holds `gov lock` as a usage error and `python3 -m gov.lock` as the module
command; DEC-753 excuses only `release` as a new command. The case holds the behaviour the row needs (the task
works where `gov` is an isolated tool and no `python3` imports it) and names no subcommand. See package P-3.

### Success 5 [W2-L002, W2-L014]: the vendored skills' licence and version in the release

| Case | Holds | Red |
|---|---|---|
| `test_the_release_holds_the_vendored_skills_version` (2) | `v6.4.2` beside `superpowers` (or the three skill names) in the manifest | R |
| `test_the_release_holds_the_vendored_skills_upstream_licence` (2) | the upstream licence's text in the record | R |

### The failure line: a release that does not match its hashes is refused

| Case | Holds | Red |
|---|---|---|
| `test_copier_copy_refuses_a_release_that_does_not_match_its_hashes` (5: a shipped file changed, a file added, a shipped file removed, the manifest's own hash wrong, a file hash in the manifest wrong) | the first release's tag moved onto a commit made after it: `copier copy` refuses, names the file (or `manifest`), no lock records the release | R |
| `test_copier_update_refuses_a_release_that_does_not_match_its_hashes` (2: a shipped file changed, the manifest's own hash wrong) | the second release's tag moved: `copier update` from the first refuses; the lock does not record the second | R |
| `test_doctor_refuses_a_lock_whose_manifest_hash_is_wrong` | the lock's recorded manifest hash replaced: the part fails | R |
| `test_doctor_refuses_a_lock_whose_file_hash_is_wrong` | one hash of the lock's manifest wrong: DRIFT naming the file | R (W1-39 holds it for a plain install) |
| `test_doctor_refuses_an_installed_release_file_changed_added_or_removed` (3) | DRIFT naming the file | R (W1-39 holds it for a plain install) |

"The manifest's own hash wrong" replaces the stated hash in the record's other files; "a file hash in the
manifest wrong" changes one file's hash inside the manifest and restates the manifest's own hash to match, so
only the file hash is wrong.

### Cases added after the first review — `test_w2_16_immutability.py`

Written by a fresh Independent Test Designer after the implementation (commit `58869611`), from the KPI lines and
the review's findings passed as described behaviour (DEC-136), without reading the implementation. Each refusal
is the suite's: non-zero exit, no traceback, the whole snapshot (files, refs, HEAD, index) unchanged. The positive
controls are the suite's own: the `releases` fixture shows the same stand-in, without the case's change, releases
the same version. Red as seen on `58869611`'s checkpoint `38c8f1bb`.

| Case | KPI line | Source | Holds | Red (seen) |
|---|---|---|---|---|
| `test_the_same_version_from_an_older_integration_commit_is_refused` (2: HEAD detached at the first release's record commit, or at the commit the first release was built from) | success 3 [CAP-43]; success 1 ("a clean `w2/integrate` commit") | first review of W2-16, finding 1 | `w2/integrate` holds release `1.5.0`'s committed record; HEAD is an older commit it contains, whose tree has no record of `1.5.0`: `gov release 1.5.0` refused, nothing written | own: "`gov release 1.5.0` built a release although w2/integrate holds release 1.5.0's record" (exit 0) |
| `test_the_same_version_after_its_record_was_removed_is_refused` (2: each release) | success 3 [CAP-43] | first review of W2-16, finding 1 | the record removed by `git rm` in a later commit on `w2/integrate`, then a new commit: building that version again refused, nothing written | own: "built a release although release <V>'s record was committed on w2/integrate and removed later" (exit 0) |
| `test_the_same_version_as_an_existing_owner_tag_is_refused` (2: lightweight, annotated) | success 3 [CAP-43]; success 2 (the owner's tag) | first review of W2-16, finding 1 | the pristine stand-in with `v1.4.0` tagged by the case (unsigned, standing for the owner), no record in the tree, a later commit: `gov release 1.4.0` refused, nothing written | own: "built a release although the tag v1.4.0 already exists, on another commit" (exit 0) |
| `test_a_version_differing_only_by_build_metadata_from_a_recorded_one_is_refused` (2: each release) | success 3 [CAP-43] | first review of W2-16, finding 4 | `<V>+build.2` beside a recorded `<V>` (equal precedence in semantic versioning), from a later clean commit: refused, nothing written | own: "`gov release 1.4.0+build.2` built a release although release 1.4.0 exists …" (exit 0) |
| `test_a_release_never_hashes_bytes_the_commit_does_not_hold` (2: `--assume-unchanged`, `--skip-worktree`) | success 1 ("from a clean `w2/integrate` commit"; "every shipped file with its sha256") | first review of W2-16, finding 5 | a tracked template file edited and hidden from `git status`: either refused with nothing written, or the manifest gives that file exactly the sha256 of `git cat-file blob <commit>:template/<path>`, never the edited bytes' | own: exit 0, "the manifest of 1.4.0 gives template/governance/kernel/schemas/ticket.schema.json the hash of bytes the commit … does not hold" |

The earlier case `test_the_same_version_from_another_commit_is_refused_and_its_record_left_as_it_was` is
unchanged; these cases hold the forms it leaves open (the record not in the checked-out tree, a tag, build
metadata). Rebuilding the same version from the same commit stays uncovered, as "Not covered here" says: no case
above builds from the commit an existing release names.

### The last round (DEC-761) — `test_w2_16_last_round.py`

Written by a fresh Independent Test Designer after the second review of W2-16 (R2-F1, R2-F2, R2-F3) and the
owner's DEC-761 (2026-10-17, staged; applied as the brief states it), from the KPI lines and the behaviour passed as
described behaviour (DEC-136, the lead's reading), without reading the implementation. Red as seen on `ee557d02`.
A refusal is the suite's: non-zero exit, no traceback, nothing written (the whole snapshot or, for
`gov release --lock-from`, the project's lock byte for byte). `--lock-from` runs by hand at the project root, as the
template's Copier task runs it (`gov release --lock-from <source>`).

| Case | KPI line | Source | Holds | Red (seen) |
|---|---|---|---|---|
| `test_lock_from_a_source_with_no_release_record_is_refused_where_the_lock_records_a_release` (2: a plain folder of `copier.yml` and `template/`; W1-39's git source tagged `v0.1.0`, no record ever) | success 4; the failure line | second review of W2-16, R2-F1; DEC-761 | a project of release 1.4.0, a kernel file edited (doctor DRIFT first): refused, the lock as it was, doctor still DRIFT naming the file | own: exit 0, `"release": null` — the lock rewritten without a release |
| `test_lock_from_the_installed_release_s_own_source_never_makes_an_edited_kernel_pass` | success 4; the failure line | R2-F1; DEC-761 | the same with the genuine source (`v1.4.0` checked out): refused with the lock as it was, or, if it writes, doctor still DRIFT naming the file (never MATCH) | **green today** (a guard): the command writes (exit 0) and doctor still reports DRIFT naming the file |
| `test_a_source_whose_release_records_were_removed_is_refused` (3: `copier copy`, `copier update` from 1.4.0, `gov release --lock-from` by hand) | success 4; the failure line | R2-F3 (b); DEC-761 | the stand-in's `w2/integrate` holds records in its history; a later commit removes `docs/releases/` and edits a kernel file, tagged `v1.6.0` by the case: copy refused (no lock that passes doctor), update refused (the lock still records 1.4.0), `--lock-from` refused (the lock as it was) | own: copy exit 0 and doctor MATCH; update exit 0; `--lock-from` exit 0, `"release": null` |
| `test_a_lock_whose_release_entries_were_deleted_fails` (2: the release entries alone; with a kernel file and its lock hash edited together) | success 4 ("a project cannot silence the lock comparison"); the failure line | R2-F2 (the first review's F2); DEC-761 | every lock entry whose value is the release version, holds the manifest hash, or is the release manifest (map, text or base64) deleted, found by value, nothing else changed: doctor's lock part fails | own: `{"match": "MATCH", "status": "pass"}`, exit 0 (both) |
| `test_gov_release_refuses_every_role_but_the_orchestrator_and_the_owner` (16: 2 forms × `engineer`, `independent-auditor`, `independent-test-designer`, `product-spec`, `research`, `ticket-lead`, an unknown name, set and empty) | success 2 ("agents never tag") | DEC-761; DEC-365 (the caller is `GOV_ROLE`) | refused, the role named or "only the orchestrator or the owner", nothing written. Build form: a clean stand-in on `w2/integrate`, `gov release 1.4.0`. `--lock-from` form: a project of 1.4.0 in the state a copy is in when its task runs (lock not yet written), the genuine `v1.4.0` source | own: exit 0 (the release built; the lock written) |
| `test_gov_release_runs_for_the_orchestrator_and_the_owner` (4: 2 forms × `orchestrator`, unset) | success 2 | DEC-761; DEC-365 | positive controls: the same calls release (a record under `docs/releases/`; a lock recording 1.4.0 and its manifest hash) | **green today** (positive controls) |
| `test_the_suite_runs_gov_and_copier_with_gov_role_unset` | — | DEC-761 (the lead's note) | guard: no `gov` or Copier environment of the suite carries `GOV_ROLE` | **green today** (a guard) |

The two role cases' build halves were rewritten in round 3 (DEC-772 replaces DEC-761 item 1's line for the build
form): see "Round 3", "The four recorded rewrites". The `--lock-from` halves are as the table states.

**Seen on `ee557d02`:** the whole suite `23 failed, 91 passed` (no skip, no error): the 23 are this file's
refusal cases, each on its own assertion as the table states; the 85 earlier cases pass; 6 of this file pass (the
genuine-source guard, the 4 positive controls, the `GOV_ROLE` guard).

**Readings.** "Refuses once the lock records a release" is read as the lead reads it: `--lock-from` never rewrites
or drops the release the lock records; it writes another release's lock only at an update, where that release
verifies against its hashes. The positive control of the update is the suite's own
(`test_a_project_updated_to_a_later_release_records_that_release_in_its_lock`), unchanged. An entry that "records
the release" is found by value: equal to the version, holding the manifest hash, or the manifest itself; a value
that only contains the version inside longer text (the template tag `v1.4.0`) is not one, and stays. The
`--lock-from` role cases run where `--lock-from` must write when allowed (the state of a copy when its task runs:
every file, the answers file, no lock yet), so the refusal is the role's and nothing else's; that state is what
Copier hands the task, and the unset and orchestrator controls show it writes there today. A command that sets
`GOV_ROLE=orchestrator` itself from a session of another role is a known limit (W2-H058's guard side): no case.

**Not covered, by the brief.** Edits beyond the deletion above, which rewrite every record a project holds
consistently, are the unsigned limit (CAP-02.c, Wave 3): no case.

### Open: a source that never held a record (R2-F3, item C)

DEC-761 says "a version tag from a source with no release records is refused". This round builds the refusal for a
source **whose history holds release records** (the case above). A source that **never** held one (W1-39's
template source, `copier.yml` and `template/` alone, tagged `v0.1.0`) still installs as W1-39 holds it: W1-39's
suite (about 55 cases) and this suite's plain-source cases (W2-M174, W2-L227, W2-H029's and W2-M175's first forms)
install from such a source, and the owner named none of them for a rewrite. No case here refuses a never-recorded
source and none of those cases is changed. This part waits for the owner's answer (the lead's package). Item 3 of
DEC-761 leaves to the owner which commit is tagged (W2-L351, R2-P2): no case depends on it beyond what the suite
already does (the tag is on the commit that holds the record).

### The two recorded rewrites of earlier tickets' cases (DEC-761, DEC-491)

Each is in the designer's commit with its `Rewrite-Reason:` trailer and states the rewrite and its reason in its
docstring. Nothing else in W1-39's or W1-32's folders changes.

- **`tests/acceptance/W1-39/test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured`.**
  It deleted both files from a project made by `copier copy` (an installed kernel) and held "unmeasured, exit 0",
  which W2-H029 (KPI success 4) and `test_deleting_both_the_lock_and_the_answers_file_does_not_silence_the_comparison`
  make a failure (package P-1 below, option (a)). Rewritten to a project never installed from the template (W1-27's
  shape: its overlay alone, no installed kernel, no lock, no answers file); both assertions kept
  (unmeasured and no failure; not a match). Today: it passed after the rewrite (before it, it failed: status `fail`).
- **`tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`.**
  It failed because `gov --help` offers `release`, which the recorded lists do not hold yet (DEC-753: recorded in
  W1-07's list and `RECORDED_GOV_COMMANDS` only after W2-20 closes; those lists are not touched). Rewritten so that
  `release`, and only `release`, is excused while the lists lack it, and so it passes unchanged once they record it;
  any other unrecorded command, a recorded command gone, or the module command offered still fails it. Today: it
  passed after the rewrite (before it: `gov has commands the command list does not record: ['release']`).

## Round 3 (DEC-772 item 1) — `test_w2_16_owner_terminal.py`

Written by a fresh Independent Test Designer for W2-16's round 3, from KPI success 2 ("The owner tags the release
commit (agents never tag)"), DEC-772 item 1 and the lead's specification for this round, passed as described
behaviour (DEC-136), without reading the implementation. Red as seen on `2c8cfc7a` (the code in this tree before the
round).

DEC-772 item 1, word for word: "`gov release` is owner-only, from a plain terminal, like `gov approve` and the
freeze lift: it refuses with a Claude Code process among its ancestors, with `GOV_ROLE` or `GOV_TICKET` set, or
without a terminal, and asks for a typed one-time code. This replaces DEC-761 item 1's line '`gov release` refuses
unless the role is orchestrator, or the owner in a plain terminal'."

**The lead's reading, fixed for this round.** Item 1 governs the build form (`gov release <version>`, and every call
that is not `--lock-from`). `gov release --lock-from` (the template's Copier task) keeps its caller check: a
terminal-and-code check there would refuse every install and update not typed by hand (KPI 4, "at copy as well as at
update"; W1-39's closed suite, DEC-771 item 1). No new case for it: the last round's role cases hold it, unchanged.
The build form refuses before it reads or writes anything (non-zero exit, no traceback, the error code
`RELEASE_REFUSED`, `details["reason"]` one word, the reason said in words): `session` (a Claude Code session among
the ancestors: the freeze lift's chain and signs, DEC-409), `ancestry` (the chain cannot be read whole up to process
1, `init` or `systemd`), `role` (`GOV_ROLE` set, to any value), `ticket` (`GOV_TICKET` set, to any value),
`terminal` (standard input and output not both a terminal), `code` (only after every other check passed: a prompt
holding `RELEASE-` and four digits from the system's random source, one line read; a wrong line, an empty line or the
end of input refuses). Nothing is shown on a call refused earlier. On success the build is what it was: the record
under `docs/releases/<version>/`, no commit, no tag; the result `{"version", "record"}`.

**The seam.** Its name and form are the lead's specification for this round, in the freeze lift's form (W1-50's
`gov.pause.command._lift_test`): `gov.release.command._release_test(root, version, ancestry=None, terminal=None)`.
`ancestry` is a chain in the form `gov.pause.command.read_ancestry()` returns (this process first, the system's
first process last); `terminal` a pair of descriptors, each asked `os.isatty` by the product whatever is passed;
`GOV_ROLE` and `GOV_TICKET` are read from the process environment, never planted. It returns the command's result or
raises `GovError` (`RELEASE_REFUSED`, `details["reason"]`). The command itself always reads `/proc` and uses
`(0, 1)`. The driver (`w2_16_support.drive_release`) is W1-50's, copied into this suite's support (no W1-50 module is
imported): a new process, an environment built from scratch, a pseudo-terminal it reads the code from and types the
reply on; whatever the build prints goes to a log in the sandbox, never into the driver's answer.

| Case | KPI line | Source | Holds | Red (seen on `2c8cfc7a`) |
|---|---|---|---|---|
| `test_the_owner_in_person_builds_the_release` (2: a plain terminal's chain to `init`, an editor terminal's to `systemd`) | success 2 | DEC-772 item 1; the lead's specification, item 2 (success) | the positive control: one code shown and typed back, the result names the version and `docs/releases/1.4.0`, the record written there alone, no commit, no tag, the code not in the result | the seam is missing (`module 'gov.release.command' has no attribute '_release_test'`) |
| `test_a_claude_code_session_among_the_ancestors_refuses_the_build` (5: headless `-p`, the operator console, `gov launch`, the npm shape, the command line alone) | success 2 | DEC-772 item 1; DEC-409's signs (W1-50's chains) | refused, reason `session`, the message says `claude` or `session`, nothing written, no code shown | the seam is missing |
| `test_a_chain_that_does_not_reach_process_1_refuses_the_build` (5: nothing read, stops before process 1, an entry not the parent of the one before, the sandbox's own first process, a shell as first process) | success 2 | DEC-772 item 1 (the lead's item 2, `ancestry`); W1-50's unreadable chains | refused, reason `ancestry`, said in words, nothing written, no code shown | the seam is missing |
| `test_gov_role_set_to_any_value_refuses_the_build` (4: `orchestrator`, `owner`, `engineer`, empty) | success 2 | DEC-772 item 1 | refused, reason `role`, said in words, nothing written, no code shown | the seam is missing |
| `test_gov_ticket_set_to_any_value_refuses_the_build` (2: `DAEO-49o5`, empty) | success 2 | DEC-772 item 1 | refused, reason `ticket`, said in words, nothing written, no code shown | the seam is missing |
| `test_without_a_terminal_on_both_sides_the_build_refuses` (4: piped input, piped output, both pipes, `/dev/null`) | success 2 | DEC-772 item 1 | refused, reason `terminal`, said in words, nothing written, no code shown | the seam is missing |
| `test_anything_but_the_shown_code_refuses_the_build` (3: a wrong code, an empty line, end of input) | success 2 | DEC-772 item 1 (the typed one-time code) | refused, reason `code`, one code shown, none shown again after the reply, nothing written | the seam is missing |
| `test_the_code_comes_from_the_system_s_random_source` | success 2 | the lead's specification, item 2 (`code`); W1-50's form | 12 calls in one process, Python's `random` seeded with 0 before each, a wrong code typed back: all refused for `code`, more than one code seen | the seam is missing |
| `test_the_command_refuses_with_standard_input_from_dev_null` | success 2 | DEC-772 item 1 | the real `gov release 1.4.0` as the suite runs it (`GOV_ROLE`, `GOV_TICKET` absent; input `/dev/null`, output a pipe): non-zero, no traceback, `RELEASE_REFUSED` in its output, no code shown, nothing written; the reason is not asserted | own: exit 0, the record written (`{"version": "1.4.0", "record": ".../docs/releases/1.4.0"}`) |
| `test_the_command_refuses_on_a_terminal_under_this_suite_s_ancestry` | success 2 | DEC-772 item 1 | the real command on a pseudo-terminal, the code typed back if shown: the same refusal, the reason not asserted. Where this suite's own chain holds no Claude Code session and reaches process 1 (a plain terminal, a nightly run) it is **skipped with that reason, never passed**: from there the build is the owner's | own: exit 0, the record written; this suite's own chain read as `ancestry` (inside the launched session's sandbox no Claude process is visible and process 1 is the sandbox's own, as W1-50 saw it) |

Counts as seen on `2c8cfc7a`: this file `28 failed` (26 for the missing seam, 2 on their own assertion: the real
command builds).

### The four recorded rewrites (DEC-491, DEC-866)

Each is in a designer's round-3 commit with its `Rewrite-Reason:` trailer (the first three in the round's first
commit, the fourth in its own, after the lead's answer to P-R3-A) and states the rewrite and its reason in its
docstring or on its line. Each keeps its purpose; no other expectation is lowered.

- **The suite's release builds (`w2_16_support.build_release`; `Rewrite-Reason: DEC-772`).** It ran
  `gov release <version>` as a child process; under DEC-772 that call refuses from every test run, so every case
  that needs a release would fail for a reason not its own. It now builds through the seam as the owner in person
  (`release_as_the_owner`: a planted clean chain, a pseudo-terminal, the code typed back, `GOV_ROLE` and
  `GOV_TICKET` absent). Every assertion it made is kept: a release from a clean `w2/integrate` commit, nothing
  changed outside `docs/releases/`, a record written, the owner's commit and tag. **Today:** every case that needs a
  release fails at the `releases` fixture for the missing seam: 82 errors at set-up and 11 failures (the 8
  `--lock-from` refusal role cases and 3 cases that reach the fixture through a parameter), each with "DEC-772 item 1
  is not built: gov.release.command._release_test(...) is missing". **Trial, outside the tree:** with a scratch
  plugin standing the earlier child-process build in for the seam (the earlier code allows `GOV_ROLE` unset), the
  suite without the new file gave `2 failed, 112 passed`: the 2 are the build-form refusals below, red as they must
  be; every case that needs a release passed as before.
- **The two role cases' build halves (`test_w2_16_last_round.py`; `Rewrite-Reason: DEC-772`).** DEC-772 replaces
  DEC-761 item 1's line for the build form. In
  `test_gov_release_refuses_every_role_but_the_orchestrator_and_the_owner` the build form is now held refused for
  every `GOV_ROLE` value, `orchestrator` included, and with `GOV_ROLE` unset (these runs have no terminal): non-zero,
  no traceback, `RELEASE_REFUSED` in the output, a reason said in words (which reason is not fixed), nothing written.
  Its two earlier positive controls in `test_gov_release_runs_for_the_orchestrator_and_the_owner` (build form,
  `orchestrator` and unset) are refusals there now; the seam's positive control replaces them. The `--lock-from`
  half of both cases is as it was (8 refusals, 2 controls). Ids are kept (`[<form>-<role>]`); the build form has 10
  refusal cases, the controls 2. **Today:** the build form's 8 old refusal roles pass (the earlier code's role check
  refuses them with `RELEASE_REFUSED`, which DEC-772 keeps); `orchestrator` and unset fail on their own assertion
  (exit 0, the release built); the `--lock-from` halves fail or error for the missing seam (they need a release), and
  pass in the trial.
- **R3-F5 (`test_a_source_whose_release_records_were_removed_is_refused[copier copy]`; `Rewrite-Reason: DEC-767`,
  P-R3-2 (a)).** It copied into `tmp_path / "product"`, which the `own_release_project` fixture had already filled,
  so Copier stopped before its task ran and the case failed whatever the code did. The one line now copies into a
  fresh folder, `tmp_path / "copied-from-v1.6.0"`; nothing else changed. **Today:** an error at set-up for the
  missing seam (it needs the releases); **in the trial it passed** (the earlier code refuses the copy there).
- **The build's own refusals (P-R3-A; `Rewrite-Reason: DEC-772`).** The lead's answer to P-R3-A: option (a), in
  this round, before the review (DEC-866 with DEC-772). The two `_assert_refused_and_nothing_written` helpers
  (`test_w2_16_release.py`: an unclean tree (4), not on `w2/integrate` (2), a version that is not semantic (6), no
  version (1), the same version from another commit (2); `test_w2_16_immutability.py`: an older integration commit
  (2), a record removed later (2), an owner's tag (2), build metadata (2)) and the hidden-edit case
  `test_a_release_never_hashes_bytes_the_commit_does_not_hold` (2): 25 cases. They ran `gov release` as a child
  process, the owner's old path of DEC-761's line, which DEC-772 replaced; that call now refuses for its ancestry or
  its missing terminal before it reaches the rule each case names, so they would have passed whatever that rule
  does. Each call now goes through the seam as the owner in person (`w2_16_support.assert_the_build_refuses`: a
  planted clean chain, a pseudo-terminal, the code typed back, `GOV_ROLE` and `GOV_TICKET` absent), and each refusal
  is held to come from the build's own rule: exactly one code shown and typed back right (every caller check passed),
  the code `RELEASE_REFUSED`, a `reason` that is none of `session`, `ancestry`, `role`, `ticket`, `terminal`, `code`
  (or none at all: the lead's specification fixes reasons only for the caller checks). Every assertion kept: refused,
  no traceback (the error, the driver's detail and the build's own output), the whole snapshot unchanged; the
  hidden-edit case's manifest branch is as it was. "No version" is the seam called with `version` None. **Today:**
  all 25 are errors at set-up for the missing seam (each takes the `releases` fixture). **Trials, outside the
  tree,** with a scratch plugin answering the seam's owner calls with the earlier child-process build
  (`gov release [<version>] --json`, its envelope turned into the seam's answer as if the code had been typed back):
  the 25 cases `25 passed` (the 23 refusals each `RELEASE_REFUSED`, no reason; the 2 hidden-edit cases released
  and took the manifest branch); the same refusals altered so they are not the build's own each gave
  `23 failed, 2 passed` (a caller check's reason `terminal`; another code; no code shown; not refused; a file written
  by the refused call), the 2 passing being the hidden-edit cases, which the earlier build releases; every call
  outside the `releases` fixture refused for a caller check gave `25 failed`, and refused by the build's own rule
  with the code accepted `25 passed`. The whole suite without the new file under the plugin: `2 failed, 112 passed`
  (the two build-form refusals above).

**W1-07's list.** The entry for `release` in W1-07's list (and `src/gov/check/commands.py`) is not made in this
round: W2-20's change is not in this tree (DEC-753 items 2 and 3).

### Red today, the whole suite (seen on `2c8cfc7a`)

`41 failed, 19 passed, 82 errors` (142 cases, no skip). The 82 errors and 11 of the failures: the missing seam, at
the `releases` fixture. 28 failures: this round's file (above). 2 failures: the build form's refusals for
`orchestrator` and unset. 19 passed: the 10 cases and guards that need no release (W2-L227, W2-H029 plain, W2-M174
(4), the overlay guard, the stand-in "before any release" guard, W2-M175 plain, the worktree guard), the build form's
8 old refusal roles, and the `GOV_ROLE` guard. After the fourth rewrite the counts are the same: the 25 rewritten
cases were and are errors at set-up for the missing seam.

## Covers and rows

| Id | Cases |
|---|---|
| CAP-43.b (lite), success 2, DEC-772 item 1 | round 3's cases (`gov release <version>` the owner's alone, from a plain terminal, with a typed code) |
| CAP-43.b (lite) | success 1, the failure line |
| CAP-43 | success 3 (with the four immutability cases added after the first review), success 4 (lock records the release; the last round's `--lock-from`, removed-records and release-entry cases), the failure line |
| CAP-43.b (lite), success 2 | the last round's role cases (DEC-761: only the orchestrator or the owner releases) |
| CAP-43.d (ahead of its wave) | CLI version, schema versions, release notes |
| CAP-02.a | the doctor cases of the failure line, W2-M174 |
| CAP-02.c (stays W3, DEC-722) | success 2 |
| W2-H029 (the silencing part) | the two silencing cases |
| W2-L002 | the licence case |
| W2-L014 | the vendored version case |
| W2-L227 | the direct-copy case |
| W2-M174 | the mode, empty-folder and declared-path cases, the overlay guard |
| W2-M175 | the isolated-tool case |

## Red today

`10 failed, 3 passed, 62 errors` (75 cases, no skip). 62 errors at set-up, each R. 10 failed on their own
assertion: W2-L227 (1), W2-H029 plain (1), W2-M174 (4), W2-M175 plain (1), and three that need the release
fixture through a parameter and so fail rather than error (W2-H029 release, W2-M175 release, the stand-in
"holding releases" guard), each with R's sentence. 3 passed: the three guards named above.

**Trials, outside the tree.** Two throwaway stand-ins in the session's scratch folder, loaded by a pytest plugin
for the trial only: a `gov release` (a JSON manifest and a `.sha256` beside it) and a lock task added to the
stand-in's `copier.yml` that verifies the release and appends its version and hash to the lock. With them: every
case of `test_w2_16_release.py` (42) passed (the vendored-version case was too strict at first and was
relaxed), every case of `test_w2_16_install.py` (17) passed except the two W2-M175 cases, which failed as they
must because the trial task still ran `python3`, and every doctor case that needs doctor's change stayed red on
its own assertion with its preconditions met. No trial file is in the tree.

## Earlier cases to revise, and the named reds

- **`tests/acceptance/W1-39/test_w1_39_drift.py::test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured`**
  against KPI success 4 (W2-H029, the silencing part): it deletes both files of a project made by `copier copy`
  and holds "unmeasured", exit 0 — exactly what the KPI says may no longer pass. Package P-1. Rewritten in the last
  round (DEC-761; "The two recorded rewrites" above).
- **DEC-753:** the W1-07 and W1-26 cases that find `release` unrecorded are named reds until the resume round
  records it. Not touched here.

## Packages

- **P-1. W1-39's neither-file case contradicts W2-H029.** *Question:* revise
  `test_a_project_with_neither_lock_nor_answers_file_stays_unmeasured`? *Why now:* the engineer cannot make
  both green. *Options:* (a) revise it to a project with no installed kernel (W1-27's shape), keeping DEC-499's
  "never installed: unmeasured"; (b) keep it and drop the silencing part from this KPI. *Impact:* (a) one W1-39
  case, DEC-499's residual closed; (b) W2-H029 stays open. *Reversible:* yes. *Cost:* one case, in the resume
  round. *Recommendation:* (a). *Confidence:* high.
- **P-2. What "the manifest's own hash" is.** *Question:* the sha256 of the manifest file's bytes stated beside
  it (assumed here), or a hash inside the manifest over a canonical form? *Why now:* a reader must be able to
  recompute it; the second needs the canonical form fixed. *Options:* (a) as assumed; (b) a self-hash with a
  documented canonical form, and a case rewritten to recompute it. *Recommendation:* (a), and the lock records
  that hash. *Confidence:* medium.
- **P-3. W2-M175's "closes when" names a `gov lock` subcommand, which DEC-542 and W1-07 rule out.** The row can
  be met without a new top-level command: the task calls a subcommand of `gov release` (for example
  `gov release lock`) or another existing command. *Recommendation:* read the row as "a `gov` subcommand is used
  by the Copier task"; the case holds that behaviour. *Confidence:* medium.
- **P-4. Schema versions.** No kernel schema carries a version. *Recommendation:* each schema's sha256 (or the
  release version) until schemas carry their own; the case accepts any value per schema. *Confidence:* medium.
- **P-5. A non-bytecode file inside a kernel `__pycache__/`.** It escapes the comparison (DEC-488). No case
  here. *Recommendation:* leave it a residual unless the owner wants it closed with W2-M174. *Confidence:* low.

## Not covered here, and why

- **A project that rewrites the lock's manifest, its recorded release hash and any copy of the release manifest
  together:** without a signature (CAP-02.c, W3) or a read of the release source, nothing inside the project
  tells this apart. The cases hold the forms the origin line names (DEC-499's residuals).
- **`gov install` and `gov update`:** W2-18 and W2-17 (see the reading above).
- **Rebuilding the same version from the same commit:** no source decides between refusal and a no-op. No case.
- **The wheel's bytes:** a wheel build is not byte-reproducible; the case holds the hash's presence and its
  agreement with a wheel the record holds.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `breadth` (`tests/optin-breadth.txt`), run with `--optin=breadth`; the switched-off
features' cases are in `lifted` (`tests/optin-lifted*.txt`, `--optin=lifted`).

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: gov release <version> builds a release from a clean w2/integrate commit [CAP-43.b lite]. Its manifest holds: the semantic version and... | `test_w2_16_release.py::test_a_release_writes_its_record_under_docs_releases_and_changes_nothing_else`, `test_w2_16_release.py::test_the_manifest_holds_the_semantic_version`, `test_w2_16_release.py::test_the_manifest_holds_the_full_commit_the_release_was_built_from` | README |
| S2: The owner tags the release commit (agents never tag); the tag is not signed (CAP-02.c stays in Wave 3, DEC-722). | `test_w2_16_release.py::test_building_a_release_creates_no_tag`, `test_w2_16_release.py::test_building_a_release_signs_nothing`, `test_w2_16_install.py::test_a_release_installed_from_an_unsigned_lightweight_tag_is_accepted` | README |
| S3: A release is immutable: building the same version from another commit, or changing a file after release, is refused [CAP-43]. | `test_w2_16_release.py::test_the_same_version_from_another_commit_is_refused_and_its_record_left_as_it_was` | README |
| S4: Framework.lock records the release version and manifest hash, at copy as well as at update. A missing lock fails, and a project canno... | `test_w2_16_install.py::test_a_project_copied_from_a_release_tag_records_the_release_version_in_its_lock`, `test_w2_16_install.py::test_a_project_copied_from_a_release_tag_records_the_manifest_hash_in_its_lock`, `test_w2_16_install.py::test_a_project_updated_to_a_later_release_records_that_release_in_its_lock` | README |
| S5: The vendored skills carry their licence and version in the release [W2-L002, W2-L014]. | `test_w2_16_release.py::test_the_release_holds_the_vendored_skills_version`, `test_w2_16_release.py::test_the_release_holds_the_vendored_skills_upstream_licence` | README |
| F1: A release whose files or manifest do not match their hashes is refused by gov install, gov update and gov doctor. | `test_w2_16_immutability.py::test_a_release_never_hashes_bytes_the_commit_does_not_hold`, `test_w2_16_last_round.py::test_a_source_whose_release_records_were_removed_is_refused` | designer, by its words |

Tier 2's cap here: 36 functions (6 KPI lines x 6); 26 functions moved to the opt-in suite `breadth` (listed in `tests/optin-breadth.txt`).
