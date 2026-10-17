# W2-16 acceptance tests: immutable, hash-pinned releases (CAP-43.b lite)

Ticket `DAEO-49o5`, profile FULL. Written by an Independent Test Designer before implementation (MR-3), from the
ticket's KPI lines, Contract v4.2 (CAP-43, CAP-43.a to CAP-43.d, CAP-02, CAP-02.a, CAP-02.c), the list rows
W2-H029, W2-L002, W2-L014, W2-L227, W2-M174, W2-M175 with their origin lines, and DEC-722, DEC-023, DEC-027,
DEC-488, DEC-493, DEC-499, DEC-542, DEC-194, DEC-244, DEC-654, DEC-221, DEC-752, DEC-753. 75 cases in three files.

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

## What the cases use

Public interfaces only: the `gov` command line (`gov release <version>`, `gov doctor --json`), the tool `copier`
(the registered 9.18.2, needed and never skipped, as W1-39 holds it), the files of a created project
(`governance/framework.lock`, `.copier-answers.yml`), the files of a release record, and `git` in temporary
repositories. No module of `src/gov/lock/` or of the release code is imported or named.

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

## Covers and rows

| Id | Cases |
|---|---|
| CAP-43.b (lite) | success 1, the failure line |
| CAP-43 | success 3, success 4 (lock records the release), the failure line |
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
  and holds "unmeasured", exit 0 — exactly what the KPI says may no longer pass. Package P-1. Not edited.
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
