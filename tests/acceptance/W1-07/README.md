# W1-07 — gov CLI skeleton: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-drvn` (W1-07), its "Owner
answers at test design" paragraph (DEC-185, DEC-186, DEC-187), CAP-27 / CAP-27.a and CAP-28 / CAP-28.b of Contract v4,
`docs/interfaces/API-0002.yaml` and DEC-046. Written before implementation. No earlier ticket's test was rewritten.

## Run

```sh
python3 -m pytest tests/acceptance/W1-07 -q -p no:cacheprovider
```

Standard library and `pytest` only. No network. Nothing is installed.

- **How the CLI is run.** An install would create a `gov` console script from `[project.scripts] gov =
  "<module>:<function>"` in `pyproject.toml`. The tests read that line, write the same launcher into a temporary
  directory, and run it with `python3` and `src/` on `PYTHONPATH`, as `.claude/settings.json` does for the hooks.
- **The repository is never the project.** The working tree (tracked files and untracked, unignored ones) is copied to
  a temporary directory and committed. Each test gets its own copy, which is both the project and the code under test.
  Bytecode goes to a temporary `PYTHONPYCACHEPREFIX`.
- **Environment, built from scratch:** `PATH`, an empty temporary `HOME`, `TMPDIR`, locale, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX`. The session's `GOV_ROLE` and `GOV_TICKET` are not passed on.
- **Dev tier.** Eight cases are marked `local_only`. They clone `$GOV_DEV_TIERS/a-dev` (default
  `~/gov-os-workbench/synthetic/a-dev`) into a temporary directory and are skipped when the tier is absent.
  Deselect them with `-m "not local_only"`.

The whole directory takes about 45 seconds once the CLI exists.

## KPI → tests → red reason today

Red run on `w1/integrate` at `110bd452`: **196 errors, 0 passed, 0 failed** (196 cases, 37 test functions). Every case
errors in the `cli` fixture with the same reason: **`the gov command does not exist: there is no pyproject.toml`**.
The column below gives what each group will fail on first once `pyproject.toml` declares the command.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1.** Every command returns the API-0002 JSON envelope with exit codes 0-4 | `test_w1_07_envelope.py` | `test_every_command_returns_the_envelope[13]` · `test_status_succeeds_with_exit_code_0` · `test_a_governance_error_has_exit_code_1_and_its_code_in_the_json` · `test_an_unknown_command_is_a_usage_error` · `test_an_unknown_option_is_a_usage_error` · `test_the_exit_code_is_the_same_without_json[3]` · `test_the_envelope_carries_the_session_given` · `test_an_error_envelope_carries_the_session_given` · `test_root_names_the_project_from_another_directory` | No `gov` command (`pyproject.toml` missing); then no `gov.cli` code to print an envelope |
| **Success 2.** Commands are classed read or act; read commands leave `git status --porcelain` empty **[CAP-27.a]** | `test_w1_07_read_act.py` | `test_a_read_command_leaves_git_status_empty[16]` · `test_a_read_command_changes_no_file_and_no_ref[8]` · `test_a_read_command_leaves_uncommitted_work_as_it_was[8]` · `test_a_read_command_with_root_writes_neither_in_the_project_nor_where_it_runs` · `test_a_read_command_leaves_a_dev_tier_clone_clean[8]` (`local_only`) | No `gov` command; the read commands cannot be run |
| **Success 3a.** Overlay and path-map config load with schema validation (DEC-185) | `test_w1_07_config.py` | `test_a_missing_path_map_is_not_an_error[13]` · `test_status_succeeds_without_a_path_map` · `test_status_succeeds_without_a_governance_project_folder` · `test_an_invalid_path_map_gives_config_invalid_on_every_command[39]` · `test_an_invalid_path_map_gives_exit_code_1_without_json` · `test_root_decides_which_path_map_is_loaded` · `test_repairing_the_path_map_clears_the_error` | No `gov` command; no loader, so no `CONFIG_INVALID` |
| **Success 3b.** `gov --help` < 300 ms | `test_w1_07_help.py` | `test_help_prints_usage_and_ends_with_exit_code_0` · `test_help_answers_in_under_300_ms` | No `gov` command |
| **Success 4.** The check-declaration format (family, tier, hard-block or warning, command) is defined and loaded by the CLI, so any ticket can register a check (DEC-186) | `test_w1_07_check_declarations.py` | `test_check_list_succeeds` · `test_a_declared_check_is_listed_with_its_five_fields[2]` · `test_the_list_follows_the_declaration_files` · `test_every_declaration_in_the_kernel_template_is_listed` · `test_listing_does_not_run_a_check` · `test_running_checks_stays_not_implemented_with_declarations_present` · `test_an_uncommitted_declaration_is_listed_and_left_alone` | No `gov` command; no `check --list` |
| **Success 5.** The registry reserves each Wave 1 operation as a `gov` command; a reserved command not yet built returns a `NOT_IMPLEMENTED` envelope **[CAP-28.b]** | `test_w1_07_registry.py` | `test_help_names_every_reserved_command` · `test_each_wave_1_operation_is_a_gov_command[12]` · `test_a_reserved_command_not_yet_built_returns_not_implemented[11]` · `test_a_name_outside_the_registry_is_not_answered_as_not_implemented` | No `gov` command; no registry |
| **Failure 1.** A command writes outside its declared act paths | `test_w1_07_read_act.py` | `test_no_command_writes_outside_its_act_paths[14]` · `test_a_command_refused_for_invalid_configuration_writes_nothing[13]` · the read-command tests above · `test_listing_does_not_run_a_check` | No `gov` command |
| **Failure 2.** Envelope fields drift from `docs/interfaces/API-0002.yaml` | `test_w1_07_envelope.py` | `test_the_envelope_has_no_field_outside_the_interface[13]` · every test that calls `assert_envelope` (all files) | No `gov` command |

**Count.** KPI lines with tests: 7 of 7 (5 success, 2 failure). Covers ids with tests: 2 of 2 (CAP-27.a, CAP-28.b).
Owner answers: DEC-185, DEC-186 and DEC-187 are tested as the ticket states them, except the one point in the
decision package below.

## How the tests decide

- **The envelope** is read from `docs/interfaces/API-0002.yaml` in the copy (`json_envelope` and `exit_codes`), not
  typed into the tests, so the interface file is the measure. A test passes when standard output is one JSON object
  that has `ok` (boolean), `command` (string), `result` (object) and `session` (string), no field the interface does
  not define, and, when `ok` is false, an `error` object with exactly `code`, `message` and `details`.
- **Exit code and envelope agree:** `ok: true` with 0; `ok: false` with 1-4. Codes 3 and 4 need verification and
  pause, which later tickets build, so no W1-07 test produces them.
- **Read/act by behaviour (DEC-187).** Before and after a command the tests compare `git status --porcelain`, HEAD
  and every ref, a content hash of every file in the project, and the contents of `HOME` and of an unrelated
  directory.
- **Check declarations.** A test registers a check as a ticket would: it adds a YAML file to
  `template/governance/kernel/checks/` of its project copy. It then looks, anywhere inside `result` of
  `gov check --list --json`, for an object whose `id` is the declared one.

## Readings the sources do not spell out

1. **The command line without an install.** `pyproject.toml` declares `[project.scripts] gov = "<module>:<function>"`,
   and the function returns the exit code or calls `sys.exit` (what a console script does). ADR-0002 says `gov` is an
   installed user tool; no source names the entry point.
2. **Flag position.** Global flags are given after the command (`gov status --json --root <p> --session <id>`), the
   form DEC-186 and CAP-28 use for `--json`. No test puts a global flag before the command.
3. **`--root`** names the project; without it the project is the working directory (every test runs in the project's
   root). **`--session <id>`** becomes the envelope's `session`. Without `--session`, `session` is only required to
   be a string. `--role` is not tested.
4. **`command`** in the envelope names the command: the command's name is one of its space-separated words
   (`"status"` and `"gov status"` both pass).
5. **`error` on success** is absent or `null`. **`result` on failure** is still an object (the interface marks only
   `error` optional). `details` must be present; its type is not checked.
6. **`NOT_IMPLEMENTED` and `CONFIG_INVALID` end with exit code 1** ("governance error (GovError code in JSON)").
   `error.code` is an upper-case code.
7. **What W1-07 builds:** `status` (succeeds, exit 0, any `result` object) and `check --list`. The ten other reserved
   commands, and `check` without `--list`, return `NOT_IMPLEMENTED` when called with `--json` and no other argument.
   The ticket that builds a command revises that command's case in `test_w1_07_registry.py`.
8. **Usage errors** (unknown command, unknown option) end with exit code 2. If anything is printed on standard
   output under `--json`, it must be a valid envelope with `ok: false`; an empty standard output passes.
9. **Without `--json`** the exit code is the same; the human output is not checked (except that an invalid
   path-map's message names the file).
10. **Derived state.** The project ignores `.gov-runtime/` (the repository's own `.gitignore`), and the file
    snapshot leaves out `.git/` and `.gov-runtime/`. A read command may therefore write under `.gov-runtime/`, and
    nowhere else. CAP-27's measure, `git status --porcelain`, is applied as written.
11. **A command not yet built writes nothing**, whatever class it will have; so do `--help` and a command refused
    with `CONFIG_INVALID`. This is how failure 1 is tested while no act path is declared in public.
12. **`context --dry-run`**, **`closure`** and **`retrieve`** are run with no further argument. For the read tests
    only the exit code range (0-4) and the unchanged project are asserted, so a usage error would pass there.
13. **Configuration precedence.** "Every `gov` command loads" is taken literally: with an invalid `path-map.yaml`,
    a command not yet built answers `CONFIG_INVALID`, not `NOT_IMPLEMENTED`.
14. **Invalid under any schema:** a `path-map.yaml` that is not YAML, and one whose top level is a list or a scalar.
    "Naming the file": the string `path-map.yaml` appears in the `error` object (message or details).
15. **Check declarations:** one declaration per file, as a top-level map with string values; the directory is
    `template/governance/kernel/checks/` under the project root; `severity` is `hard-block` or `warning` (the KPI's
    words); `tier` values are `G1`, `G2` (CAP-39's tier names); `family` values are family names of CAP-38.b
    (`mutation scope`, `command-contract consistency`). The listed record repeats the five fields under the same
    names with the same values. Listing reads the working tree, committed or not, and starts no declared command.
16. **`gov --help` < 300 ms** is the median wall time of nine runs after one warm-up run, measured around the whole
    `python3` process.

## Not tested, and why

- **`CONFIG_INVALID` naming the key, and a valid `path-map.yaml` loading** — decision package DP-1 below.
- **An invalid check declaration** (a missing field, a severity outside the two words, two files with one `id`). No
  source says what `gov check --list` does with it. W1-26, which runs the checks, is the natural place; raise it
  there or answer it with DP-1.
- **The other overlay files** (roster, profiles, tool registry): DEC-185 leaves them to the tickets that add them.

## Decision package

### DP-1 — What does a minimal valid `path-map.yaml` look like, so that "naming the key" can be tested?

- **Question.** DEC-185 says an invalid `governance/project/path-map.yaml` gives `CONFIG_INVALID`, "naming the file
  and the key", against "a minimal path-map schema" under `src/gov/config/`. No source states one key of that
  schema. Which top-level key (name and type) does the minimal schema fix, and where in the `error` object is the
  key named?
- **Why now.** A test of "naming the key" must write a file with one known-invalid key, and a test of "a valid file
  loads" must write a valid one. Without the shape, either test would be the designer's guess at the engineer's
  schema, or would have to read `src/gov/config/` (an internal). The file-level cases (not YAML, not a map, missing)
  are tested.
- **Options.**
  - (a) The owner fixes one line of shape for the minimal schema, for example: the top level is a map; `namespaces`
    is required and is a map from a namespace name to a map; `error.details` has `file` and `key`. The designer adds
    three tests: a valid file loads, `namespaces: 42` names `namespaces`, a missing `namespaces` names it.
  - (b) The schema file gets a fixed public name and format (for example `src/gov/config/path-map.schema.json`), and
    the tests derive a valid and an invalid document from it.
  - (c) Key naming is left to the engineer's unit tests at W1-07 and gets its acceptance tests at W1-08, with the
    real schema.
- **Impact.** (a) three tests, about 30 lines, and one line in the ticket; the engineer's schema must match it.
  (b) a schema-walking generator in the tests, about 100 lines, and the tests then follow whatever the schema says.
  (c) nothing now; "naming … the key" of DEC-185 has no independent test until W1-08, and that ticket's test design
  must pick it up.
- **Reversibility.** All three are easy to reverse: W1-08 replaces the minimal schema anyway, and its test design
  revises these cases.
- **Cost.** (a) one owner sentence and a short test-design round. (b) a longer round, and a weaker test. (c) none
  now, and a gap recorded for W1-08.
- **Recommendation.** (a).
- **Confidence.** Medium-high. The only risk is that the one-line shape differs from what W1-08 will define, and
  DEC-185 already expects W1-08 to replace it.
