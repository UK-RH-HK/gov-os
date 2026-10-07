# W1-39 acceptance tests: the Copier kernel template and the lock

Ticket `DAEO-5ylr`, profile STANDARD. Written by the Independent Test Designer before implementation (MR-3).
48 cases in five files.

Run, without `PYTHONPATH`:

```
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-39 -q -p no:cacheprovider -rs
```

## What the cases use

Three public interfaces and nothing else: the tool `copier` (the version the tool registry records, 9.18.2), the
command `gov doctor --json`, and the files of a created project. No module of `src/gov/lock/` is imported or
named.

- **Copier is never given this repository.** A git repository given to Copier as its source is cloned whole.
  `assemble_source` builds the template source in a temporary folder from the single file `copier.yml` and the
  files under `template/` alone (a listing limited to those two paths, copied file by file), and makes that
  folder a git repository of its own with a commit and the tag `v0.1.0`. A second release (`v0.2.0`) is a second
  commit and tag in that temporary repository. No tag is made in this repository. Nothing under
  `governance/project/` is copied; one named file there is read, `tool-registry.yaml`, for Copier's version.
- **Copier is run as `copier copy --defaults --trust --vcs-ref <tag> <source> <destination>`** and
  `copier update --defaults --trust --vcs-ref <tag>` (with `--answers-file` when `copier.yml` sets
  `_answers_file`). So: every question has a default, and the tasks `copier.yml` declares may run.
- **What a Copier task finds:** `gov` on `PATH` (this worktree's command line), the `gov` package importable by
  `python3`, an empty temporary `HOME`, no network.
- **Copier is needed and never skipped.** Where it is absent or another version than the registered one, every
  case that needs it fails with that sentence. Nothing is installed (DEC-083).

## The interface the cases assume of the lock, and the source of each point

| Point | Assumed | Source |
|---|---|---|
| Place in a project | `governance/framework.lock` | ADR-0002 §5 (product layout); the allowed path `template/governance/framework.lock*` |
| Form | one YAML map | `gov doctor` reads it so today (W1-27) |
| Manifest | under the key `manifest`: a non-empty map of path to hash | CAP-02.a "file-hash manifest"; the first key `gov doctor` reads (W1-27) |
| Manifest paths | relative to the project root, POSIX | `gov doctor` resolves them so (W1-27) |
| Hash | sha256 of the file's bytes, lower-case hex | `gov doctor` computes that (W1-27) |
| What is listed | every file under `governance/kernel/`; no overlay file; not the lock, not the answers file | ADR-0002 §5 (kernel is Copier-owned, `governance/project/` is the overlay); CAP-02 (installed kernel) |
| Tag and commit | the lock's text holds the release tag and the full commit id; **no key name is fixed** | KPI failure 2; CAP-43's acceptance (tag, commit and manifest) |
| Answers reference | the lock's text holds the answers file's path | DEC-023; ADR-0002 L7 |
| Answers file | `_answers_file` of `copier.yml`, else `.copier-answers.yml` | Copier; DEC-023 |
| Doctor's report | the section `framework_lock`; the words MATCH and DRIFT; the drifted file's path in the section; exit 0 or not | W1-27 as built; CAP-02's acceptance |

## KPI lines and their cases

### Success 1 [CAP-44.a]: copy creates governance/, the overlay, .rulesync/, hooks and the lock with a manifest; doctor passes

`test_w1_39_copy.py`

| Case | Clause |
|---|---|
| `test_copy_installs_the_kernel_exactly_as_the_template_holds_it` | creates `governance/` (the kernel, both directions) |
| `test_copy_installs_the_hooks_and_keeps_them_executable` | hooks |
| `test_copy_installs_the_rulesync_sources` | `.rulesync/` |
| `test_copy_creates_the_overlay` | the overlay exists after copy. **Red until package P-2** |
| `test_copy_into_a_folder_that_has_an_overlay_file_keeps_it` (2) | the overlay is under `_skip_if_exists` at install |
| `test_copy_writes_the_answers_file_that_names_the_release` | the answers file (DEC-023) |
| `test_copy_writes_the_lock_where_the_product_layout_places_it` | `framework.lock` |
| `test_the_manifest_lists_every_installed_kernel_file_with_its_sha256` | file-hash manifest |
| `test_every_manifest_entry_is_a_file_of_the_project_with_that_sha256` | file-hash manifest, no entry without a file |
| `test_the_manifest_leaves_out_the_overlay_and_the_lock_itself` | how a project's file is told from a kernel file |
| `test_doctor_passes_on_a_freshly_created_project` | doctor passes; the lock part is a measured MATCH. **Red until P-1** |
| `test_doctor_reads_the_lock_and_leaves_it_as_it_was` | doctor only reads |

**Parts of `gov doctor` on a freshly created project.** With an empty `HOME` and a project that has only the
kernel, doctor reports: tools *unmeasured* (the project has no tool registry), hooks *unmeasured* (no
`lefthook.yml`: W1-40), path map *unmeasured* (no path map), index freshness and canaries *unmeasured* (no
index), isolation *unmeasured* (no `.gov-runtime/`), the held-out file *reported missing*, path compliance
*pass*, adoption level MINIMAL (CAP-54). The Claude Code part looks at the machine's own CLI (the real home's
`~/.local/bin/claude`), whatever `HOME` says: it is the one part of this case that depends on the machine. The
case asserts that no part fails and that the lock part is measured; it does not assert that the unmeasured
parts are measured. Their measurement in an installed project belongs to W1-40 (hooks), W1-41 (registry, path
map) and the exit run.

### Success 2 [CAP-02.a]: one edited kernel file is DRIFT naming it; the update procedure is documented

`test_w1_39_drift.py`, and one case of `test_w1_39_update.py`

| Case | Clause |
|---|---|
| `test_a_one_byte_edit_of_a_kernel_file_is_drift_naming_it` (2) | the line itself. **Red until P-1** |
| `test_drift_names_the_edited_file_and_no_other` | naming it. **P-1** |
| `test_the_edit_taken_back_is_a_match_again` | the verdict follows the bytes. **P-1** |
| `test_a_listed_file_that_is_missing_is_reported_by_name` | measured or refused. **P-1** |
| `test_a_listed_file_that_cannot_be_read_is_reported_by_name` | measured or refused. **P-1** |
| `test_a_kernel_file_the_manifest_does_not_list_is_drift_naming_it` | measured or refused. **P-1** (new behaviour) |
| `test_a_kernel_file_struck_from_the_manifest_is_drift_naming_it` | measured or refused. **P-1** (new behaviour) |
| `test_a_file_the_project_adds_outside_the_kernel_is_not_drift` (3) | a project's file is not drift. **P-1** |
| `test_a_missing_lock_is_not_a_match` | measured or refused |
| `test_a_lock_without_manifest_entries_is_not_a_match` (2) | measured or refused. **P-1** (new behaviour) |
| `test_a_lock_that_is_not_readable_as_a_map_is_not_a_match` | measured or refused. **P-1** |
| `test_the_update_procedure_is_documented_in_one_place` | the procedure is documented (see P-3) |

What the report must say for a kernel file the manifest does not list was settled from the sources: CAP-43's
acceptance has doctor fail when the manifest disagrees with the installed kernel, and ADR-0002 §5 makes
`governance/kernel/` Copier-owned, so a file there that no release shipped is DRIFT naming it. A file anywhere
else is the project's and is not drift.

### Success 3 [CAP-43.a]: separate trees here; a product holds only the installed kernel and its overlay

`test_w1_39_layout.py`

| Case | Clause |
|---|---|
| `test_this_repository_is_a_copier_template_whose_subdirectory_is_the_kernel_template_tree` | `copier.yml` with `_subdirectory: template`; the seven trees exist apart from it |
| `test_the_template_tree_holds_nothing_but_what_a_product_receives` | no CLI, test, fixture or document tree under `template/` |
| `test_a_created_project_holds_none_of_the_gov_os_repositorys_own_trees` | a product holds only … |
| `test_a_created_project_holds_only_the_product_layout` | every top-level entry is ADR-0002 §5's |
| `test_governance_of_a_created_project_is_the_kernel_the_overlay_and_the_lock` | kernel, overlay, lock, nothing else |

This repository is not adopted yet (W1-41): "a product repository" is shown on a created project in a
temporary folder.

### Failure 1: an overlay file is overwritten by copier update

`test_w1_39_update.py`

| Case | Clause |
|---|---|
| `test_update_keeps_an_overlay_file_the_project_wrote` (2) | the project's file, the release ships one at that path |
| `test_update_keeps_an_overlay_file_the_template_shipped_and_the_project_edited` (2) | shipped by both releases, edited by the project: no merge, no reject file |
| `test_update_leaves_every_file_the_project_added_as_it_was` | tickets, decisions, code, an overlay file |
| `test_update_brings_the_kernel_of_the_second_release` | the update is a real one: the kernel changes |
| `test_after_an_update_the_lock_names_the_second_release_and_its_files` | the lock follows the update |
| `test_after_an_update_doctor_reports_a_match` | **Red until P-1** |

The overlay is `governance/project/`, at any depth (ADR-0002 §5; DEC-023). Two cases put a file of the
template's own at an overlay path in the *temporary* template source, to stand for a release that ships one.

### Failure 2: framework.lock lacks the template tag or commit

`test_w1_39_lock_identity.py`

| Case | Clause |
|---|---|
| `test_the_lock_names_the_template_tag` | the tag |
| `test_the_lock_names_the_template_commit` | the commit, in full |
| `test_the_lock_of_an_untagged_template_commit_still_names_the_commit` | a commit without a tag of its own |
| `test_the_lock_refers_to_the_answers_file` | DEC-023: answers reference plus manifest |
| `test_doctor_fails_when_the_locks_tag_or_commit_disagrees_with_the_install` (2) | CAP-43's acceptance. **Red until P-1** |

## Red today, and why

All 48 are red before implementation: 45 at set-up and 2 layout cases with "no copier.yml yet: this repository
is not a Copier template", and the documentation case with "no file of the ticket's paths exists yet".

The behaviour assertions were told apart from that reason by a trial that is not in the tree: a throwaway
`copier.yml`, answers template and lock-writing task were put into the **temporary** template source only.
With the lock at `governance/framework.lock`, 26 cases passed and 22 failed, each on its own assertion: 16
because doctor reads `framework.lock` at the project root and so reports the lock as missing; 2 for the tag and
commit comparison doctor does not make; `test_copy_creates_the_overlay`; and the three cases that read this
repository's own `copier.yml` and documents. With the lock at the root instead (where doctor reads today), the
five cases of new doctor behaviour stayed red on their own assertion (a kernel file not in the manifest, a
struck entry, an empty manifest, no manifest, a changed tag or commit were all reported MATCH), and the two
layout cases went red on the lock's place.

## Cases that stay red until a package is decided

- **P-1 (doctor reads the lock the sources call for).** `src/gov/doctor/` is outside this ticket's paths. 18
  cases: every case marked P-1 above.
- **P-2 (what the overlay holds at install).** `test_copy_creates_the_overlay`.

## Not covered here, and why

- **Generation of `.claude/`, `CLAUDE.md` and `AGENTS.md`** in a created project (DEC-468, DEC-469, DEC-471):
  whether `copier copy` runs rulesync or leaves it as a documented step is undecided (package P-4). The layout
  cases admit both.
- **The declared checks' `template/…` paths** and **the ignore rule for `.gov-runtime/`** (residuals of
  `governance/project/bootstrap.md`): neither can be settled within this ticket's paths. No case.
- **The `.rulesync/` overlay part** (ADR-0002 §5: "kernel part + overlay part"): no source in the tree says
  which paths of `.rulesync/` are the project's. No case.
- **G-14 and S0a-G-15:** their text is not in the readable tree. No case is derived from them.
- **`lefthook.yml` and the CI workflow** (ADR-0002 §5's template list): W1-40.
- **Signed tags** (`git tag -v`): CAP-02.c, Wave 3.
