# W2-18 acceptance tests: the pinned install (DAEO-057v)

Ticket `DAEO-057v` (W2-18), profile STANDARD, Emergency 2. Written by the independent test designer before the
implementation (MR-3), from the ticket's six KPI lines (5 success, 1 failure), CAP-43, and the lead's interface for
`gov install`, the pin dispatch, doctor's section `install` and the kernel hook lines. 28 cases in four files. Every
case is of the kind *acceptance*.

Run from this worktree (the case count and pass/fail per KPI line, through the opaque runner):

```
PYTHONPATH=$PWD/src python3 -m gov.cli.main accept W2-18 --root $PWD
```

or directly, at most six workers, each run with its own `TMPDIR`:

```
TMPDIR=$(mktemp -d) python3 -m pytest tests/acceptance/W2-18 -q -p no:cacheprovider -n 6
```

## What the cases build, and how they run gov

Everything is in temporary folders. Nothing reads or runs the live pins under `~/.local`: each command gets a fake
`HOME`, `PATH=/usr/bin:/bin` (plus a folder of the case's own, where it needs one), the real user base in
`PYTHONUSERBASE` (so the system and user packages gov needs stay importable), and no `PYTHONPATH` or `GOV_*` unless
the case sets them.

- **The source.** W2-16's stand-in Gov OS repository (`w2_16_support.build_gov_os_repository`: this worktree's
  `pyproject.toml`, `copier.yml`, `template/` and `src/gov/`, copied file by file). Two releases are built there
  through W2-16's owner seam (`build_release`): **A = 0.9.0** and **B = 0.9.1**. Before each, `pyproject.toml`'s
  version is set to the release version and committed, so a release's CLI version equals its version. The owner's
  tags are `v0.9.0` and `v0.9.1`. Each release's wheel is built again by the support code, the way `gov release`
  builds it (`pyproject.toml` and `src/` at the manifest's commit, setuptools, `SOURCE_DATE_EPOCH` the commit's time).
  The fixture checks that this wheel's name and sha256 equal the manifest's, so the build is reproducible on this
  machine.
- **The adopted product.** `copier copy --vcs-ref v0.9.0 --trust` of the stand-in, committed. Its lock names
  release A and its `.copier-answers.yml` names the stand-in in `_src_path`. A case that changes a product works on its
  own copy, made before any pin is put in it.
- **A pin made by hand** (`plant_pin`), as the interface states it: `<common>/gov/envs/<v>/`
  (`python -m venv --system-site-packages`), the release's wheel installed with `pip install --no-deps --no-index`,
  `bin/gov` a link to the environment's `gov`, and `pin.json` with every key the interface names. The doctor, hook and
  side-by-side cases use pins made this way, so they are measured even if `gov install` is wrong. The editable pin
  installs, with `pip install -e --no-deps --no-build-isolation`, release A's `gov` package in a flat layout: `gov/`
  beside a `pyproject.toml`, with no `src/`.
- **`gov install`** runs as `python3 -m gov.cli.main install …` with `PYTHONPATH=<this worktree>/src`, in the
  product's folder. Where a pin already exists, the dispatch hands the call to the pinned gov, which is this
  worktree's code too (the stand-in's `src/gov`).
- **Doctor** runs as `<common>/gov/bin/gov doctor --json` (the pin's doctor). For the source-tree cases it runs as
  `python3 -m gov.cli.main doctor --json` with `PYTHONPATH=<a source tree>/src` and `GOV_PIN=off`. With no pin, it
  runs with this worktree's code. Only the section `install` is read.
- **Hook lines** are read from `template/.rulesync/hooks.jsonc` of this worktree. Each `command` runs with `bash -c`
  in the tree, with `CLAUDE_PROJECT_DIR=<tree>` and the event's JSON payload on stdin. Each payload is a call the hook
  itself has no reason to refuse: a Bash `ls`, and a SubagentStop return with all twelve fields. The hook files run
  are the product's `governance/kernel/hooks/`, which come from release A, that is from this worktree's template.

## How the interface is read where it leaves a choice

- **"A's version" (S1, S5).** A release's CLI version is set equal to its release version, so either reading gives
  the same string. `gov --version` must print it as a word of its own.
- **Editable versus source tree (S2).** An editable install of a `src/` layout is both `editable` and `source_tree`
  by the interface's words. The ticket wants the editable case to name `editable`, so the editable pin here is a flat
  layout (no `src/`), and only `editable` applies to it.
- **The lock case (S2).** The pin of release B is in a product whose lock names release A. The doctor is B's, run
  from the pin, so neither `session` nor `source_tree` applies.
- **"Each kernel hook command line" (S4)** is read literally: every command line of `hooks.jsonc`. That includes the
  context watch and SubagentStop lines, whose hook files import no gov today. Each must exit 0 and print exactly one
  non-empty line on stderr. That line begins `gov hook: no gov` and names a place it looked (`bin/gov` or `PATH`).
  `GOV_TICKET` and `GOV_ROLE=engineer` are set, as in a session. The `python3` on `PATH` runs this machine's Python
  isolated (`-I`), so it imports no gov.
- **"Left as it was" (S1).** Every entry under `<common>/gov/` is compared by type, link target, sha256 and mode.
  With no pin before, the folder must still be absent after.
- **"Neither repository's files change" (S5).** The files outside `.git`, `HEAD` and `git status` of both repositories
  are the same before and after the `gov --version` runs. The pin's own folder is not compared: running a pinned gov
  may write bytecode in its environment.

## KPI lines and their tests

| KPI line | tests | expected red reason on the base |
|---|---|---|
| S1: gov install installs the release's wheel into the repository's own environment, hash-verified, never editable; a wheel that does not hash to the manifest is refused and the pin folder kept | `test_w2_18_install.py::test_install_exits_zero_and_pin_json_names_the_release_and_its_verified_wheel`, `test_w2_18_install.py::test_the_pinned_gov_prints_the_release_s_cli_version`, `test_w2_18_install.py::test_the_pinned_gov_lies_in_the_environment_s_own_site_packages_never_editable`, `test_w2_18_install.py::test_a_wheel_given_by_wheel_that_does_not_hash_to_the_manifest_is_refused_and_nothing_is_written`, `test_w2_18_install.py::test_a_release_whose_wheel_built_from_its_commit_does_not_hash_to_the_manifest_is_refused_and_the_pin_kept` | no command install: gov exits 2, invalid choice; the first three fail on install's exit code, the two refusals on the missing hashes in the message |
| S2: doctor's install section fails for an editable pin, a pin that differs from the lock, and a gov from a source tree; passes for a matching pin run from the pin; unmeasured with no pin | `test_w2_18_doctor.py::test_doctor_fails_install_with_case_editable_when_the_pinned_gov_is_an_editable_install`, `test_w2_18_doctor.py::test_doctor_fails_install_with_case_lock_when_the_pin_differs_from_framework_lock`, `test_w2_18_doctor.py::test_doctor_fails_install_with_case_source_tree_when_its_gov_resolves_to_a_source_tree`, `test_w2_18_doctor.py::test_doctor_passes_install_when_run_from_a_pin_that_matches_framework_lock`, `test_w2_18_doctor.py::test_doctor_reports_install_unmeasured_naming_gov_install_without_a_pin` | doctor's report has no section install; the passing case fails earlier, on the missing command install |
| S3: the PreCompact and Stop hook lines write the checkpoint record with the pinned gov, never the product's own package, from the main tree and a linked worktree | `test_w2_18_hooks.py::test_checkpoint_hooks_write_the_record_with_the_pinned_gov_never_the_product_s_package` | PreCompact: the hook puts the product's src first and imports its gov (the marker is written); Stop: plain python3 imports no gov, no record is written |
| S4: with no gov anywhere, each hook line exits 0 and prints one line on stderr naming the missing gov | `test_w2_18_hooks.py::test_each_hook_line_without_any_gov_exits_zero_saying_so_in_one_line` | the three guard lines exit 2 and the context watch line exits 1 (they block); the plain python3 lines exit 0 and print nothing |
| S5: the same gov run from two repositories pinned to A and B prints A's version in one and B's in the other; GOV_PIN off runs its own; no file changes | `test_w2_18_side_by_side.py::test_the_same_gov_runs_each_repository_s_pinned_release` | no pin dispatch: gov prints this worktree's version (0.1.2) in both repositories |
| F1: a session that imports a source tree's gov is refused by doctor, case source_tree naming the imported path, never passing | `test_w2_18_doctor.py::test_a_session_importing_a_source_tree_s_gov_is_refused_by_doctor_naming_the_path` | doctor's report has no section install, and doctor exits 0 |

Parametrised cases: the S3 test runs four times (main tree or linked worktree, PreCompact or Stop). The S4 test runs
once per command line of `hooks.jsonc` (eight today; a line the implementation adds is included). The S5 test runs
four times (the console script or `python -m gov.cli.main`, from the top or from a subfolder). The F1 test runs twice
(this worktree's `src`, or the stand-in's `src`).

## Cost

The releases (two seam builds, two wheel builds), the adopted product, the `gov install 0.9.0` product and the two
pins made by hand are built once per session (once per worker under xdist). On the base, a serial run takes about
a minute and `-n 6` about a minute and a half. An implementation adds a few wheel builds and environments, still a
few minutes, well inside `gov accept`'s 1800 s.
