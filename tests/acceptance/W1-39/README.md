# W1-39 acceptance tests: the Copier kernel template and the lock

Ticket `DAEO-5ylr`, profile STANDARD. Written by the Independent Test Designer before implementation (MR-3),
and brought to DEC-488 and DEC-493 before any implementer commit: 61 cases. Three cases were added after
implementation began (no existing case rewritten): 64 cases in five files.

Run, without `PYTHONPATH`:

```
env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-39 -q -p no:cacheprovider -rs
```

## What the cases use

Three public interfaces and nothing else: the tool `copier` (the version the tool registry records, 9.18.2), the
command `gov doctor --json`, and the files of a created project (with `git` in that project for the ignore
rules). No module of `src/gov/lock/` is imported or named.

- **Copier is never given this repository.** A git repository given to Copier as its source is cloned whole.
  `assemble_source` builds the template source in a temporary folder from the single file `copier.yml` and the
  files under `template/` alone (a listing limited to those two paths, copied file by file), and makes that
  folder a git repository of its own with a commit and the tag `v0.1.0`. A second release (`v0.2.0`) is a second
  commit and tag in that temporary repository. No tag is made in this repository. Nothing under
  `governance/project/` is copied; one named file there is read, `tool-registry.yaml`, for Copier's version.
- **Copier is run as `copier copy --defaults --trust --vcs-ref <tag> <source> <destination>`** and
  `copier update --defaults --trust --vcs-ref <tag>`. So: every question has a default, the tasks `copier.yml`
  declares may run, and Copier finds its standard answers file by itself.
- **What a Copier task finds:** `gov` on `PATH` (this worktree's command line), the `gov` package importable by
  `python3`, an empty temporary `HOME`, no network. One case runs the copy on a `PATH` where `rulesync`, `node`,
  `nodejs`, `npx` and `npm` are not found: every folder of `PATH` that holds one of them is replaced by a
  temporary folder of links to its other entries, so `git`, `python3` and the shell stay.
- **What Copier prints** is read from both of its streams, without its own account of its work: the lines
  `create  <path>` (one per file) and `> Running task ...` (which repeats the task's command) are left out, so a
  path or a command does not count as a message.
- **Copier is needed and never skipped.** Where it is absent or another version than the registered one, every
  case that needs it fails with that sentence. Nothing is installed (DEC-083).

## The interface the cases assume, and the source of each point

| Point | Assumed | Source |
|---|---|---|
| Lock: place in a project | `governance/framework.lock` | ADR-0002 §5 (product layout); the allowed path `template/governance/framework.lock*` |
| Lock: form | one YAML map, after a comment header | `gov doctor` reads it so today (W1-27); DEC-488 (header) |
| Lock: comment header | the leading lines that begin with `#`; they state the update procedure | DEC-488 |
| Manifest | under the key `manifest`: a non-empty map of path to hash | CAP-02.a "file-hash manifest"; the first key `gov doctor` reads (W1-27) |
| Manifest paths | relative to the project root, POSIX | `gov doctor` resolves them so (W1-27) |
| Hash | sha256 of the file's bytes, lower-case hex | `gov doctor` computes that (W1-27) |
| What is listed | every file under `governance/kernel/` outside a `__pycache__/` folder; no overlay file; not the lock, not the answers file | ADR-0002 §5 (kernel is Copier-owned, `governance/project/` is the overlay); CAP-02; DEC-488 |
| Tag and commit | the lock's text holds the release tag and the full commit id; **no key name is fixed** | KPI failure 2; CAP-43's acceptance |
| Answers reference | the lock, outside its comment header, holds the answers file's path | DEC-023; ADR-0002 L7 |
| Answers file | `.copier-answers.yml` at the project root | DEC-023; DEC-493 |
| Path map | `governance/project/path-map.yaml`, the only file the copy creates under `governance/project/` | DEC-493; where `gov` reads a project's path map (`src/gov/config/`, DEC-185) |
| "Minimal and valid" | doctor loads it, and its path-map part reports `status: pass` with `unclassified_count: 0` on the created project, committed | `gov doctor` as built (W1-27): with a path map present the part is measured, and it passes only when every tracked path matches a pattern; KPI success 1 (doctor passes) |
| Adoption level | `MINIMAL` on a freshly created project | CAP-54's acceptance; the section `adoption_level` of `gov doctor` (W1-27) |
| The procedure's words | `copier update`, `.copier-answers.yml`, `gov doctor`, `rulesync` (line breaks and `#` inside a phrase are passed over) | DEC-488; DEC-023 (never edit the answers file); CAP-02 |
| Where the procedure is | what `copier copy` prints, what `copier update` prints, the lock's comment header: each states all four | DEC-488 ("the template's messages after copy and after update, and a comment header of the generated lock") |
| What the copy does not write | `.claude/`, `CLAUDE.md`, `AGENTS.md` | DEC-488; ADR-0002 §5 (generated by rulesync) |
| Ignore file | by behaviour: `git check-ignore` and `git status` in the created project, for files under `.gov-runtime/` and under a `__pycache__/` at any depth; the file's text is not read | DEC-493 |
| Doctor's report | the section `framework_lock`; the words MATCH and DRIFT; the drifted file's path in the section; exit 0 or not | W1-27 as built; CAP-02's acceptance; DEC-488, DEC-493 |

## KPI lines and their cases

### Success 1 [CAP-44.a]: copy creates governance/, the overlay, .rulesync/, hooks and the lock with a manifest; doctor passes

`test_w1_39_copy.py` (19 cases)

| Case | Clause |
|---|---|
| `test_copy_installs_the_kernel_exactly_as_the_template_holds_it` | creates `governance/` (the kernel, both directions) |
| `test_copy_installs_the_hooks_and_keeps_them_executable` | hooks |
| `test_copy_installs_the_rulesync_sources` | `.rulesync/` |
| `test_copy_creates_the_overlay` | the overlay is the path map and nothing else (DEC-493) |
| `test_the_path_map_of_a_fresh_project_is_one_doctors_path_map_part_accepts` | minimal and valid: measured, zero unclassified paths (DEC-493) |
| `test_a_freshly_created_project_is_at_the_minimal_adoption_level` | CAP-54: kernel only, the minimal level |
| `test_copy_into_a_folder_that_has_an_overlay_file_keeps_it` | the overlay is under `_skip_if_exists` at install |
| `test_copy_into_a_folder_that_has_a_path_map_keeps_it` | the same for the one overlay file the template ships |
| `test_copy_writes_the_answers_file_that_names_the_release` | `.copier-answers.yml` (DEC-023, DEC-493) |
| `test_copy_writes_nothing_that_rulesync_generates` | the copy does not run the adapter generation (DEC-488) |
| `test_copy_succeeds_where_rulesync_and_node_are_absent` | an install does not fail without rulesync or Node (DEC-488) |
| `test_a_created_project_ignores_the_runtime_folder_and_bytecode_folders` | the ignore file, by behaviour (DEC-493) |
| `test_the_ignore_file_hides_no_installed_kernel_file` | the shipped ignore rules hide no kernel file |
| `test_copy_writes_the_lock_where_the_product_layout_places_it` | `framework.lock` |
| `test_the_manifest_lists_every_installed_kernel_file_with_its_sha256` | file-hash manifest |
| `test_every_manifest_entry_is_a_file_of_the_project_with_that_sha256` | file-hash manifest, no entry without a file |
| `test_the_manifest_leaves_out_the_overlay_and_the_lock_itself` | how a project's file is told from a kernel file |
| `test_doctor_passes_on_a_freshly_created_project` | doctor passes; the lock part is a measured MATCH |
| `test_doctor_reads_the_lock_and_leaves_it_as_it_was` | doctor only reads |

**Parts of `gov doctor` on a freshly created project.** With an empty `HOME` and a project that holds the
kernel, its path map and nothing else, doctor reports: the lock part *pass*, MATCH (measured); the path map
*pass*, zero unclassified paths (measured: the created project's tracked paths are everything the copy wrote);
path compliance *pass*; adoption level MINIMAL (CAP-54); tools *unmeasured* (the project has no tool registry:
the copy ships only the path map in the overlay); hooks *unmeasured* (no `lefthook.yml`: W1-40); index
freshness and canaries *unmeasured* (no index); isolation *unmeasured* (no `.gov-runtime/`); the held-out file
*reported missing*. The Claude Code part looks at the machine's own CLI (the real home's
`~/.local/bin/claude`), whatever `HOME` says: it is the one part of this case that depends on the machine. The
cases assert that no part fails, that the lock part and the path-map part are measured and pass, and the
level; they do not assert that the unmeasured parts are measured. Their measurement in an installed project
belongs to W1-40 (hooks), W1-41 (registry) and the exit run.

### Success 2 [CAP-02.a]: one edited kernel file is DRIFT naming it; the update procedure is documented

`test_w1_39_drift.py` (20 cases), and four cases of `test_w1_39_update.py`

| Case | Clause |
|---|---|
| `test_a_one_byte_edit_of_a_kernel_file_is_drift_naming_it` (2) | the line itself |
| `test_drift_names_the_edited_file_and_no_other` | naming it |
| `test_the_edit_taken_back_is_a_match_again` | the verdict follows the bytes |
| `test_a_listed_file_that_is_missing_is_reported_by_name` | measured or refused |
| `test_a_listed_file_that_cannot_be_read_is_reported_by_name` | measured or refused |
| `test_a_kernel_file_the_manifest_does_not_list_is_drift_naming_it` | DEC-488: unlisted is drift, named |
| `test_a_kernel_file_hidden_from_git_by_an_ignore_rule_is_still_drift_naming_it` | DEC-488: git-ignored files are not left out |
| `test_a_file_in_a_bytecode_folder_inside_the_kernel_is_not_drift` | DEC-488: only `__pycache__/` folders are left out |
| `test_a_kernel_folder_that_cannot_be_listed_is_not_passed_over` (2) | measured or refused: a kernel folder without permissions, or enter-only, is said (folder or reason), the lock part fails, no traceback |
| `test_a_project_without_any_installed_kernel_file_is_not_a_match` | measured or refused: no kernel file, a manifest of one file outside the kernel with its true hash, is not a match |
| `test_a_kernel_file_struck_from_the_manifest_is_drift_naming_it` | DEC-488: unlisted is drift, from the lock's side |
| `test_a_file_the_project_adds_outside_the_kernel_is_not_drift` (3) | a project's file is not drift |
| `test_a_missing_lock_is_not_a_match` | measured or refused (not a match; no more is asserted) |
| `test_a_lock_without_manifest_entries_is_not_a_match` (2) | DEC-488: an absent or empty manifest is not a match |
| `test_a_lock_that_is_not_readable_as_a_map_is_not_a_match` | measured or refused |
| `test_copier_prints_the_update_procedure_after_a_copy` | the procedure, in the template's message after copy (DEC-488) |
| `test_copier_prints_the_update_procedure_after_an_update` | the procedure, in the template's message after update (DEC-488) |
| `test_the_generated_lock_states_the_update_procedure_in_its_comment_header` | the procedure, in the lock's header (DEC-488) |
| `test_the_lock_keeps_its_comment_header_after_an_update` | the header survives the lock being written again |

The procedure cases read what Copier prints and what the generated lock of a created project holds, never a
file of this repository. The adapter generation step is held by the word `rulesync` (the tool, and the folder
`.rulesync/` the step generates from): no source fixes the command a project runs for it.

### Success 3 [CAP-43.a]: separate trees here; a product holds only the installed kernel and its overlay

`test_w1_39_layout.py` (5 cases)

| Case | Clause |
|---|---|
| `test_this_repository_is_a_copier_template_whose_subdirectory_is_the_kernel_template_tree` | `copier.yml` with `_subdirectory: template`; the seven trees exist apart from it |
| `test_the_template_tree_holds_nothing_but_what_a_product_receives` | no CLI, test, fixture or document tree under `template/`, and nothing rulesync generates |
| `test_a_created_project_holds_none_of_the_gov_os_repositorys_own_trees` | a product holds only … |
| `test_a_created_project_holds_only_the_product_layout` | every top-level entry is ADR-0002 §5's without what rulesync generates, or `.copier-answers.yml` |
| `test_governance_of_a_created_project_is_the_kernel_the_overlay_and_the_lock` | kernel, overlay, lock, all three, nothing else |

This repository is not adopted yet (W1-41): "a product repository" is shown on a created project in a
temporary folder.

### Failure 1: an overlay file is overwritten by copier update

`test_w1_39_update.py` (14 cases with the four above)

| Case | Clause |
|---|---|
| `test_update_keeps_an_overlay_file_the_project_wrote` (2) | the project's file, the release ships one at that path |
| `test_update_keeps_an_overlay_file_the_template_shipped_and_the_project_edited` (2) | shipped by both releases, edited by the project: no merge, no reject file |
| `test_update_keeps_the_path_map_when_the_release_ships_a_different_one` (2) | DEC-493: the path map, edited by the project or as the copy created it, against a release that ships another |
| `test_update_leaves_every_file_the_project_added_as_it_was` | tickets, decisions, code, an overlay file |
| `test_update_brings_the_kernel_of_the_second_release` | the update is a real one: the kernel changes |
| `test_after_an_update_the_lock_names_the_second_release_and_its_files` | the lock follows the update |
| `test_after_an_update_doctor_reports_a_match` | the procedure's check, after an update |

The overlay is `governance/project/`, at any depth (ADR-0002 §5; DEC-023). The path-map cases start from the
path map the real template ships; the project's edit is that text with a comment line at its end, and the
later release's is that text with a comment line at its head, so both stay path maps whatever the shipped one
holds. Four other cases put a file of the template's own at another overlay path in the *temporary* template
source, to stand for a release that ships one.

### Failure 2: framework.lock lacks the template tag or commit

`test_w1_39_lock_identity.py` (6 cases)

| Case | Clause |
|---|---|
| `test_the_lock_names_the_template_tag` | the tag |
| `test_the_lock_names_the_template_commit` | the commit, in full |
| `test_the_lock_of_an_untagged_template_commit_still_names_the_commit` | a commit without a tag of its own |
| `test_the_lock_refers_to_the_answers_file` | DEC-023: answers reference plus manifest |
| `test_doctor_fails_when_the_locks_tag_or_commit_disagrees_with_the_install` (2) | CAP-43's acceptance; DEC-488 (compared with the answers file) |

## Red today, and why

All 61 are red before implementation: 59 at set-up and 2 layout cases, each with "no copier.yml yet: this
repository is not a Copier template".

The behaviour assertions were told apart from that reason by trials that are not in the tree: a throwaway
`copier.yml`, answers template, path map, ignore file and lock-writing task were put into the **temporary**
template source only.

- **A template that follows the decisions, its lock at `governance/framework.lock`:** 39 passed, 22 failed.
  18 fail because `gov doctor` as built reads `framework.lock` at the project root and so reports the lock as
  missing; 2 for the tag and commit comparison; 2 read this repository's own `copier.yml`.
- **The same template, its lock at the project root (where doctor reads today):** 50 passed, 11 failed, each on
  its own assertion: the 7 cases of doctor behaviour that DEC-488 asks for and that is not built (a kernel file
  not in the manifest, the same hidden by an ignore rule, a struck entry, an empty manifest, no manifest, a
  changed tag, a changed commit: all reported MATCH), 2 layout cases on the lock's place, 2 on this
  repository's `copier.yml`.
- **A template that ignores the decisions** (a path map that classifies the kernel only and names a system, a
  second overlay file, no ignore file, no messages, no lock header, the overlay not spared, a task that calls
  `node` and one that writes `CLAUDE.md`): every case changed or added for DEC-488 and DEC-493 went red on its
  own assertion, save the bytecode-folder case, which only a comparison that reports unlisted files can turn
  red.

## Added after implementation began

Three cases of `test_w1_39_drift.py` (DEC-488: never a match without having hashed), red on their own
assertion against the implementation as it stood when they were written; the other 61 were green:

- `test_a_kernel_folder_that_cannot_be_listed_is_not_passed_over` (2: no permissions at all; enter-only without
  list): doctor answered `{"match": "MATCH", "status": "pass"}`, exit 0. The case needs a user whom permissions
  bind: where the folder can still be listed it fails with that sentence, it never skips. It restores the
  folder's permissions before it ends.
- `test_a_project_without_any_installed_kernel_file_is_not_a_match`: doctor answered MATCH, exit 0. The case
  holds "not a match, not passed"; whether the part fails or is reported unmeasured is not asserted.

## The decisions the cases follow

The packages of the first run are decided; no case waits on one.

- **DEC-488.** The comparison of a project with its lock never answers match without having hashed; an absent
  or empty manifest is not a match; a kernel file the manifest does not list is drift, named, git-ignored or
  not; only `__pycache__/` folders are left out; the lock's tag and commit are compared with the answers file.
  The update procedure is in the template's messages after copy and after update and in a comment header of
  the generated lock. `copier copy` does not run the adapter generation, and does not fail where rulesync or
  Node is absent.
- **DEC-493.** `gov doctor` reports that comparison's answer (its call site is within this ticket's paths).
  The copy creates `governance/project/` with a minimal path map that an update never overwrites. The answers
  file is Copier's standard `.copier-answers.yml`. A created project has an ignore file for `.gov-runtime/`
  and `__pycache__/`.

## Not covered here, and why

- **Whether doctor must fail on a missing lock once an answers file exists.** Not decided by a source. The
  case holds "not a match" and nothing more.
- **The command of the adapter generation step.** DEC-488 has the procedure name the step; no source fixes
  its command. The cases hold the word `rulesync`. Running the step in a created project is W1-41's.
- **Whether the shipped path map is valid against the kernel's `path-map.schema.json`** (which requires all
  five top-level keys): the cases hold what `gov doctor` reports, and doctor's loader as built also accepts a
  path map of namespaces alone.
- **The declared checks' `template/…` paths** (a residual of `governance/project/bootstrap.md`): not within
  this ticket's paths. No case.
- **The `.rulesync/` overlay part** (ADR-0002 §5: "kernel part + overlay part"): no source in the tree says
  which paths of `.rulesync/` are the project's. No case.
- **G-14 and S0a-G-15:** their text is not in the readable tree. No case is derived from them.
- **`lefthook.yml` and the CI workflow** (ADR-0002 §5's template list): W1-40.
- **Signed tags** (`git tag -v`): CAP-02.c, Wave 3.
