# W1-16 — codebase-memory wrapper: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-lkeb` (W1-16), Contract v4
CAP-12 (covers CAP-12.a, CAP-12.b) and CAP-03 (covers CAP-03.e), DEC-076, DEC-078, DEC-285 to DEC-290, DEC-298,
DEC-299, DEC-322, DEC-324, DEC-325 and DEC-221 (profile FULL). Written before implementation.

The suite has **41 test functions, 124 cases** in four files, a support module, a conftest and the question set
`questions.yaml`. **No W1-15 acceptance test was rewritten**: none asserts the old token rule (see "The W1-15
suite" below).

## Run

```sh
python3 -m pytest tests/acceptance/W1-16 -q -p no:cacheprovider
```

Standard library, `pytest` and PyYAML only. Nothing is installed. No network. About 30 seconds today; about two
and a half minutes once the ticket is built (the tool takes 5 to 6 seconds per indexing run, and one runs at a time).

- **No secret is committed.** Every planted string (canaries in a string, a comment and an identifier, token-shaped
  strings, the seven dev-tier values) and every prefixed identifier is built at run time from parts in
  `w1_16_support.py`. None stands whole in a committed file, this README included.
- **Every index is built in a temporary repository** (DEC-322). No test indexes this repository or writes its
  `.gov-runtime/`; one test asserts that. The dev tiers are only cloned (`git clone --no-hardlinks`) into a temporary
  directory; the clone is adopted, renamed in and indexed, never the tier.
- **The code under test** is the repository's `src/`, put on `PYTHONPATH` of a child process. The child's
  environment is built from scratch: `PATH`, an empty temporary `HOME`, `TMPDIR`, `XDG_RUNTIME_DIR` and
  `CBM_RUNTIME_DIR`. `GOV_ROLE` and `GOV_TICKET` are not passed on. The child's working directory is never the
  repository under test.
- **The sandbox path is short** (`/tmp/w16-…`, removed at teardown). The tool's daemon listens on a unix socket in
  its runtime directory, and a socket path holds at most 108 bytes; a pytest `tmp_path` can exceed that.
- **A test repository** is a git repository in a temporary directory, adopted as a project is: a full path map
  (this repository's own, with one namespace `**` classed as governance memory unless the test says otherwise),
  `template/.gitleaks.toml` copied to its root as `.gitleaks.toml`, and `.gov-runtime/` in its `.gitignore`.

## The public interface the tests assume

A Python interface in the package `gov.codeintel` (`src/gov/codeintel/`), as W1-09's `gov.tasks` is. No KPI names a
command and `src/gov/cli/**` is outside the ticket's paths (package DP-2). Eight functions; each takes the project
root as a `pathlib.Path` and never uses the working directory.

| Function | What the tests hold it to |
|---|---|
| `index(root)` | Builds or refreshes the code index of the repository at `root`, in that repository's home. It reads only the files `gov.secrets.indexable(root, paths)` returns. Calling it again after the repository changed makes the answers follow the change. Its return value is not used. |
| `home(root)` | The directory that is the tool's home for this repository: a path under `<root>/.gov-runtime/`. It is the directory the `codebase-memory-mcp` binary takes as `CBM_CACHE_DIR`; the tests ask the binary's own `list_projects` with it. |
| `projects(root)` | The project names `list_projects` shows in that home: a list of strings. |
| `definitions(root, name)` | Where the symbol `name` is defined. |
| `references(root, name)` | The places that use the symbol `name`; each entry is the enclosing symbol and its file. |
| `callers(root, name)` | The functions that call `name`, best first. |
| `impact(root, name)` | What a change to `name` reaches (its callers and theirs), nearest first. |
| `dead_code(root)` | The functions nothing in the repository refers to. |

- **An answer** of the last five functions is a list of maps. Each entry has `path`, the repository-relative POSIX
  path of the source file in the repository (never a path of a staged copy), and `name`, the bare name of the
  symbol. Other keys are free. An unknown name gives an empty list. The order matters for `callers` and `impact`
  only: the first five entries are scored.
- **A file the filter leaves out is not in the index at all**: nothing defined in it is known, and no answer names
  it.
- **Nothing is written outside `<root>/.gov-runtime/`**: no index file in the repository, in `HOME` (the tool's
  default home `~/.cache/codebase-memory-mcp` included), in `TMPDIR` or in the working directory; `git status` of
  the repository stays clean; the tool's `.codebase-memory/` persistence folder is not written.
- The functions need the `codebase-memory-mcp` and `gitleaks` binaries on `PATH`.

## KPI → tests → red reason today

Red run on `w1/W1-16` at `beb8f9c4` plus this suite: **42 errors, 36 failed, 46 passed**. Without the `local_only`
cases: 1 error, 4 passed.

- The 42 errors come from one fixture, with one reason: **`the codebase-memory wrapper does not exist: there is no
  src/gov/codeintel/__init__.py`**.
- The 36 failures are the token rule as it is today: 26 cases give **`an ordinary identifier … is flagged:
  [('notes/page.md', 'gov-token')]`**, 2 give `ordinary identifiers in code are flagged`, and 8 give **`the file
  with the identifier … is kept from the indexer`**.
- The suite was also run against a throwaway stand-in in a scratch directory outside the repository (a wrapper of
  about 110 lines that copies the files the filter allows into a folder under `.gov-runtime/` and indexes that,
  and a token rule written without look-ahead): **124 passed**. So every test can go green, and none is red from a
  mistake in the test code. The stand-in is not part of the suite and was not committed.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1.** The index lives in a per-repository home under `.gov-runtime/`; `list_projects` in one repository shows only its own project [CAP-12.b] | `test_w1_16_home.py` | `test_the_wrapper_offers_its_public_interface` · `test_the_home_is_under_the_repositorys_gov_runtime` · `test_two_repositories_have_two_homes` · `test_list_projects_in_one_repository_shows_only_its_own_project` · `test_a_repository_answers_only_from_its_own_code` · `test_indexing_again_keeps_one_project` | The wrapper does not exist |
| **Success 2.** A secret-exclusion test proves no planted secret enters the codebase-memory index [CAP-03.e, CAP-12.b] | `test_w1_16_secret_exclusion.py` | `test_the_tool_alone_would_index_a_planted_secret` (premise) · `test_the_filter_drops_exactly_the_planted_files` · `test_no_planted_secret_is_in_any_file_under_gov_runtime` · `test_no_planted_secret_is_left_outside_the_repository` · `test_no_planted_secret_comes_back_from_the_code_graph` · `test_a_file_with_a_secret_is_not_in_the_code_graph` · `test_the_clean_files_are_in_the_code_graph` · `test_the_secrets_indexing_check_of_w1_15_is_green_on_the_index` · `test_a_file_the_path_map_classes_as_product_data_is_not_in_the_code_graph` · `test_a_secret_added_after_the_first_index_leaves_the_graph` · `test_no_dev_canary_reaches_the_code_index[2]` | The wrapper does not exist (the premise passes) |
| **Success 3.** Definitions, references, callers, impact and dead code across Rust, Python and TypeScript on the dev tiers, before and after a rename: callers/impact hit@5 ≥ 60 % [CAP-12.a] | `test_w1_16_code_answers.py` | `test_the_expected_answers_stand_in_the_source_of_the_tier[2]` and `test_the_question_set_covers_the_three_languages` (premises) · `test_callers_and_impact_hit_at_five_is_at_least_sixty_percent[2]` · `test_callers_and_impact_are_answered_in_every_language[4]` · `test_a_renamed_symbol_is_answered_under_its_new_name_only[2]` · `test_definitions_name_every_file_that_defines_the_symbol[4]` · `test_references_name_every_file_with_a_call_site[4]` · `test_dead_code_names_the_unreferenced_functions_and_no_live_one[4]` | The wrapper does not exist (the premises pass) |
| **Success 4.** The token rule flags a prefixed string only when its body holds a digit, or both an upper-case and a lower-case letter; an ordinary identifier is not flagged and its file reaches the index; a token-shaped string is still flagged; the seven dev canaries are still detected; the requirement is in the rule, not in an allowlist (DEC-324, DEC-325) | `test_w1_16_token_rule.py` | `test_the_token_rule_carries_no_allowlist[2]` · `test_the_canary_rule_is_unchanged[2]` · `test_a_token_shaped_string_is_still_flagged[16]` · `test_a_body_with_a_digit_or_with_mixed_case_is_flagged[12]` · `test_a_body_without_a_digit_and_without_mixed_case_is_not_flagged[10]` · `test_no_prefix_and_no_separator_flags_an_ordinary_identifier[16]` · `test_ordinary_identifiers_in_code_are_not_flagged[2]` · `test_the_length_floor_of_sixteen_characters_stays[2]` · `test_every_file_holding_a_dev_canary_is_still_reported[4]` · `test_a_file_whose_only_match_is_an_ordinary_identifier_is_indexable[8]` · `test_a_file_with_a_token_shaped_string_is_not_indexable[4]` · `test_a_file_whose_only_match_is_an_ordinary_identifier_reaches_the_index` · `test_a_file_with_a_token_shaped_string_stays_out_of_the_index` | The rule flags ordinary identifiers (36 cases); the wrapper does not exist (2 cases); 42 cases keep true |
| **Failure 1.** A file whose only match is an ordinary identifier with a token prefix is kept out of an index | `test_w1_16_token_rule.py` | `test_a_file_whose_only_match_is_an_ordinary_identifier_is_indexable[8]` (the filter, with either file) · `test_a_file_whose_only_match_is_an_ordinary_identifier_reaches_the_index` (the code index) | The filter keeps the file out; the wrapper does not exist |
| **Failure 2.** An index file of this repository exists outside `.gov-runtime/` after a run | `test_w1_16_home.py` | `test_no_index_file_exists_outside_gov_runtime_after_a_run` · `test_the_tools_default_home_is_not_used` · `test_this_repository_is_not_indexed_by_the_run` | The wrapper does not exist |
| **Failure 3.** A planted secret is found in the code graph | `test_w1_16_secret_exclusion.py` | `test_no_planted_secret_comes_back_from_the_code_graph` · `test_a_file_with_a_secret_is_not_in_the_code_graph` · `test_no_planted_secret_is_in_any_file_under_gov_runtime` · `test_a_secret_added_after_the_first_index_leaves_the_graph` · `test_no_dev_canary_reaches_the_code_index[2]` | The wrapper does not exist |

**Count.** KPI lines with tests: 7 of 7 (4 success, 3 failure).

| Covers id | Tests |
|---|---|
| **CAP-12.a** definitions, references, callers, impact, dead code across languages | all of `test_w1_16_code_answers.py` |
| **CAP-12.b** per-repository index home; secrets excluded from the code graph | all of `test_w1_16_home.py`; all of `test_w1_16_secret_exclusion.py` |
| **CAP-03.e** secret exclusion holds on every retrieval route, the code route included | all of `test_w1_16_secret_exclusion.py`, with `test_no_dev_canary_reaches_the_code_index[2]` on the tiers as they are; the filter and index cases of `test_w1_16_token_rule.py` |

## The 46 cases that pass before implementation

| Cases | Why they pass today |
|---|---|
| `test_the_expected_answers_stand_in_the_source_of_the_tier[2]` · `test_the_question_set_covers_the_three_languages` | Premises of the question set: they read a clone of the tier and `questions.yaml`, not the wrapper. |
| `test_the_tool_alone_would_index_a_planted_secret` | A premise: the tool, run without the wrapper on the planted folder, stores the planted identifier. So the exclusion tests can only pass through the wrapper. |
| `test_a_token_shaped_string_is_still_flagged[16]` · `test_a_body_with_a_digit_or_with_mixed_case_is_flagged[12]` · `test_the_length_floor_of_sixteen_characters_stays[2]` · `test_every_file_holding_a_dev_canary_is_still_reported[4]` · `test_a_file_with_a_token_shaped_string_is_not_indexable[4]` | Keep true: what the old rule already flags and the repaired rule must still flag. |
| `test_the_canary_rule_is_unchanged[2]` · `test_the_token_rule_carries_no_allowlist[2]` | Keep true: the canary rule is the one W1-15 delivered, and no rule of either file has an allowlist of its own. |

## `local_only` (119 cases)

Deselect with `-m "not local_only"` (5 cases remain: the interface test and the four that read the two gitleaks
files as TOML).

- **Run the `codebase-memory-mcp` binary** (through the wrapper, or directly for the premise and `list_projects`):
  all of `test_w1_16_home.py` but the interface test, all of `test_w1_16_secret_exclusion.py`, the wrapper cases of
  `test_w1_16_code_answers.py`, and the two index cases of `test_w1_16_token_rule.py`. Skipped when the binary is
  not on `PATH`.
- **Run the `gitleaks` binary**, directly or through the filter: the other marked cases of
  `test_w1_16_token_rule.py`. Skipped when the binary is not on `PATH`.
- **Clone a dev tier** (`$GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`; tiers `a-dev` and `b-dev`, by
  exact path): the wrapper cases of `test_w1_16_code_answers.py`, its tier premise,
  `test_no_dev_canary_reaches_the_code_index[2]` and `test_every_file_holding_a_dev_canary_is_still_reported[4]`.
  Skipped when the tier is absent.
- **One indexing job at a time.** The suite is not written for `pytest-xdist`. Each tier is cloned and indexed
  once per session (twice: before and after the rename); the two small repositories of the home file and the
  planted repository are indexed once per file.

## How the tests decide

### The home (success 1, failure 2)

- **Facts about the tool** (version 0.11.0, read from the binary and by running it in a temporary directory):
  its home is the directory in the environment variable `CBM_CACHE_DIR`, default `~/.cache/codebase-memory-mcp`.
  It holds one SQLite file per project, `_config.db` and `logs/`. `list_projects` lists the projects of that home.
  Two homes can be used at the same time. The index stores names, paths, hashes, a full-text index and vectors;
  it does not store string values or comment text, but it does store identifiers.
- **Two repositories, two homes.** `home(root)` is under `<root>/.gov-runtime/` and holds an index file after
  indexing. `projects(root)` has one name. The binary's own `list_projects`, asked with `CBM_CACHE_DIR` set to
  that home, shows the same single project and no project whose root path is the other repository.
- **Isolation by content.** Each repository answers for its own function and gives an empty list for the other's.
- **An index file** is a SQLite file (by its first bytes), a `.db`, `.db-wal` or `.db-shm` file, or a `.db.zst`
  dump. None may exist in the repository outside `.gov-runtime/` and `.git/`, nor in the child's `HOME`, `TMPDIR`,
  runtime directory or working directory. The child's `~/.cache/codebase-memory-mcp` must stay empty, and the
  user's own must not gain, lose or change a file.

### Secret exclusion (success 2, failure 3)

- **Where the secrets stand.** Three source files (Python, TypeScript, Rust) hold a planted string: in a string
  value, in a comment, and as the name of a function. The last is the one the tool alone would store; the premise
  test shows it. Three clean files, one per language, stand next to them.
- **In the index** means in any file under the repository's `.gov-runtime/`: its bytes, and for a SQLite file the
  rows of every table as text. That covers the graph, the full-text index, the per-file surfaces, logs and any
  staged copy of the sources the wrapper keeps there.
- **In the code graph** means in an answer: every kind of question is asked about every name of the planted
  files, and neither the results nor the child's output may hold a planted string.
- **The file is not read.** Names defined only in a planted file have no definition, though their names are not
  secrets: the indexer reads what the filter returns and nothing else. A clean file of a namespace the path map
  classes as product data stays out for the same reason.
- **Not everything is left out.** The clean files are defined and have their callers, in all three languages.
- **Re-indexing.** A clean file is indexed, gains a secret and is indexed again: nothing of it is known afterwards.
- **The backstop.** `gov.secrets.stores_with_secrets(root)` (W1-15) returns nothing for the indexed repository.
- **The tiers as they are.** None of the seven dev canaries stands under `.gov-runtime/` of an indexed tier clone
  or comes back in an answer.

### Code answers (success 3)

- **The question set is the test designer's** (`questions.yaml`; package DP-1). The S0b2 C1 baseline is in the
  workbench; its questions and expected answers are not in this repository, and not in the dev tiers. The public
  dev query set in the tiers' folder has five natural-language `callers-impact` queries whose gold answers are
  mostly documents; the code files it names for code questions are used here and marked with their query ids.
- **Every expected answer was read from the source of the tier**, by a whole-word search, never from the tool. The
  tier premise test checks each one against a fresh clone.
- **13 symbols**, 5 Rust, 5 Python, 3 TypeScript, each asked for callers and for impact: **26 questions**.
- **hit@5**: a question is a hit when one of its expected `(path, name)` answers is among the first five entries.
  The threshold is 60 % of the 26 questions, both tiers together, once before and once after the rename. A second
  test requires at least one hit per language for callers and for impact.
- **A rename** is a function renamed wherever it stands as a whole word in a tracked `.rs`, `.py` or `.ts` file of
  the clone, committed, followed by `index(root)` (package DP-3). Five functions are renamed: one per language in
  `a-dev`, Rust and Python in `b-dev` (its TypeScript has no call site of a function). After the rename every
  question is asked with the new names; the old name has no definition and no caller.
- **Definitions**: every expected defining file is answered (two symbols are defined in Rust and in Python).
- **References**: every file with a call site is answered (CAP-12 acceptance), for one function per language.
- **Dead code**: the listed unreferenced functions are answered, and three functions that non-test code calls are
  not.
- The stand-in scored 26 of 26, before and after. The set uses unique names and direct calls, so 60 % has slack
  on it; a harder set is a choice for the owner (package DP-1).

### The token rule (success 4, failure 1)

- **Flagged** means `gitleaks dir <tree> --config <file>` reports the planted file under a rule whose id begins
  with `gov-token`. The engineer may write the requirement as one rule or as several; only the ids' beginning is
  held.
- **Not flagged** means the scan reports nothing at all for the tree: the ordinary identifier stands in prose or in
  code with nothing else a rule could find.
- **Both files**: every scan case runs with `.gitleaks.toml` and with `template/.gitleaks.toml`.
- **The boundaries**: one digit as the last or the first character of a 16-character body; one upper-case letter
  in a lower-case body, and the other way round; a body of lower-case words, of upper-case words alone, and of
  exactly 16 lower-case letters; 15 against 16 characters; four prefixes times two separators.
- **In the rule, not in an allowlist.** The pre-index filter ignores every allowlist (DEC-298). So the eight filter
  cases, which put either file at the project's root and expect the file with the identifier to be let through,
  pass only when the rule itself no longer matches. One more test holds that no rule has an allowlist of its own.
- **The seven dev canaries**: every file of a tier clone that holds one of the seven values is reported with each
  file. The canary rule's expression and keywords are held equal to what W1-15 delivered.
- **Reaches the index**: functions named like a prefixed token are defined, and have their caller, in the code
  index; a file with a token-shaped string is not there.

## The W1-15 suite

No test of `tests/acceptance/W1-15/` asserts the old token rule, so none was rewritten.

- Its planted token strings (the tier form of the canary, and the second `a-dev` value) hold digits and mixed
  case: they are token-shaped under the repaired rule as well, and the canary rule finds them too.
- No W1-15 test plants an ordinary prefixed identifier and expects a finding.
- The W1-15 suite was run unchanged on this branch (92 passed) and against the stand-in's repaired rule (92
  passed).

## Not tested, on purpose

- The shape of the token rule's expression, and the number of rules it takes.
- A prefixed identifier whose body holds a digit (a version suffix, for example): the decision flags it.
- The canary rule's over-blocking, and near spellings of the canary: residuals of W1-15.
- A command (`gov …`) for the wrapper: no KPI names one.
- How the wrapper gives the tool only the allowed files (a staged copy, an ignore mechanism): the tests see the
  result. A file replaced between the filter's answer and the indexer's read is a W1-15 residual.
- The daemon's lock and socket files and its local UI port (package DP-4): they are not index files.
- Index time, memory and graph size (DEC-078 gives the envelope); other languages than Rust, Python, TypeScript.
- Renaming a file or a folder; partial or stale indexes after a crash; two indexing jobs at once.
- The tool's other queries (snippets, text search, architecture, traces): they are not in the interface.

## Decision packages returned with this suite

- **DP-1** The question set and the measure of hit@5 (designer's set, provisional).
- **DP-2** The wrapper's public interface (a Python interface, eight functions).
- **DP-3** What "a rename" is (a function renamed in the clone).
- **DP-4** The tool's daemon: runtime directory outside `.gov-runtime/` and a local UI port.
