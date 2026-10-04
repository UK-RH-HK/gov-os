# W1-15 — Secret rules and pre-index filter: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-7nne` (W1-15), Contract v4
CAP-03 (covers CAP-03.a, CAP-03.b, CAP-03.e) and CAP-38 (CAP-38.b), DEC-074 Q8 and Q9, DEC-076, DEC-186, DEC-187,
DEC-225 and DEC-221 (profile FULL). Written before implementation. No earlier ticket's test was rewritten.

The suite has **53 test functions, 92 cases**: 36 functions and 59 cases written before implementation, 14
functions and 21 cases of the second batch (below), written after green from behaviours a review described
(DEC-136), and 3 functions and 12 cases of the third batch (below), written after implementation from a probe
finding (DEC-298).

## Run

```sh
python3 -m pytest tests/acceptance/W1-15 -q -p no:cacheprovider
```

Standard library, `pytest` and PyYAML only. Nothing is installed. No network. About 20 seconds once the ticket is
built.

- **No secret is committed.** Every planted string (the canary of the first KPI line, the seven dev-tier values, a
  private key block, an access token) is built at run time from parts in `w1_15_support.py`. None stands whole in a
  committed file, this README included, so the suite cannot trip the rules it tests.
- **Everything planted lives in a temporary directory.** No test writes into the repository. The dev tiers are only
  cloned (`git clone --no-hardlinks`) into a temporary directory.
- **The code under test** is the repository's `src/`, put on `PYTHONPATH` of a child process. The child's
  environment is built from scratch (`PATH`, an empty temporary `HOME`, `TMPDIR`, locale); `GOV_ROLE` and
  `GOV_TICKET` are not passed on. The child's working directory is never the project.
- **A test project** is a temporary directory with a full path map (this repository's own, with the tests'
  namespaces in place of its namespaces) and `template/.gitleaks.toml` copied to its root as `.gitleaks.toml`, as
  an adopting project would have it.

## The public interface the tests assume

The engineer of W1-15, and the tickets that build indexers (W1-16, W1-17, W1-19), can rely on this.

1. **`gov.secrets.indexable(root, paths)`** (package `src/gov/secrets/`).
   - `root`: the project root (a `pathlib.Path`). The working directory is not used.
   - `paths`: a list of project-relative POSIX paths (strings) an indexer wants to read.
   - Returns the paths an indexer may read: a sub-list of `paths`, in the order asked, no path twice, no path that
     was not asked.
   - A path is left out when its file holds a secret (by content, whole file), or when the project's
     `governance/project/path-map.yaml` does not class its namespace as `memory_class: governance`, or when it is
     not a readable file. A link is judged by what it points to.
   - Default deny: when the filter cannot decide (no scanner, a map it cannot read) it raises, or leaves the path
     out. It never lets the path through. The tests accept either.
   - It writes nothing into the project outside `.gov-runtime/`, leaves no copy of a secret in the project, `HOME`
     or `TMPDIR`, and does not print a secret.
   - **For an indexer ticket:** "calls the content filter before chunking" means the indexer reads and chunks only
     what this function returned. This ticket cannot assert that of an indexer that does not exist; the suites of
     W1-16, W1-17 and W1-19 plant a secret and a product-data file and assert both are absent from their store.
2. **The two gitleaks files.** `.gitleaks.toml` (this repository) and `template/.gitleaks.toml` (shipped to an
   adopting project) both have `[extend] useDefault = true` and at least one `[[rules]]` entry of their own. The
   template file allowlists no path.
3. **The family check.** One declaration file matching `template/governance/kernel/checks/secrets-indexing*.yaml`
   (DEC-186), listed by `gov check --list --json` with a `family` that reads "secrets indexing" (case and
   punctuation are ignored). Its `command` is run by `sh -c` **in the project's root**, with the `gov` package
   importable. Exit code 0: no secret in a derived store. Any other code: a secret was found. The derived stores are
   every file under `.gov-runtime/`, text or SQLite. Source files are not its subject. Its output names the file and
   never repeats the secret.

## KPI → tests → red reason today

Red run on `w1/W1-15` at `092cd013` plus this suite: **45 errors, 7 failed, 7 passed**.

- The 45 errors come from three fixtures, each with one reason: **`the secret filter does not exist: there is no
  src/gov/secrets/__init__.py`** (27 cases), **`the secrets-indexing check is not registered: nothing matches
  template/governance/kernel/checks/secrets-indexing*.yaml`** (12 cases) and **`template/.gitleaks.toml does not
  exist`** (6 cases).
- The 7 failures: 3 give `template/.gitleaks.toml does not exist`; 1 gives `.gitleaks.toml adds no [[rules]] to the
  defaults`; 2 give `gitleaks with .gitleaks.toml does not detect the canary` (one per form); 1 gives `gitleaks
  with .gitleaks.toml does not report` the dev tier's token file.
- Without the `local_only` cases: 37 errors, 4 failed, 1 passed.
- The suite was also run against a throwaway stand-in in a scratch directory outside the repository (about 70
  lines: the filter, the check, two rules): 59 passed. So every test can go green, and none is red from a mistake
  in the test code.

| KPI line | Test file | Test functions | Red reason today |
|---|---|---|---|
| **Success 1.** `.gitleaks.toml` extends the defaults with token and canary rules; the canary is detected | `test_w1_15_gitleaks_rules.py` | `test_the_configuration_extends_the_gitleaks_defaults[2]` · `test_the_configuration_adds_rules_of_its_own[2]` · `test_the_template_configuration_allowlists_no_path` · `test_the_canary_is_detected[4]` · `test_the_gitleaks_defaults_alone_miss_the_canary[2]` · `test_a_secret_the_defaults_find_is_still_detected[4]` · `test_text_about_canaries_and_tokens_is_not_a_finding[2]` · `test_the_token_canary_file_of_the_dev_tier_is_reported[2]` | No template file; the repository file has no rules and misses the canary |
| **Success 2.** Every indexer calls the content filter before chunking; 0 of 7 dev canaries reach any store [CAP-03.a, CAP-03.e] | `test_w1_15_filter.py` | `test_a_file_without_a_secret_is_indexable` · `test_a_file_with_the_canary_is_not_indexable[2]` · `test_a_file_with_a_secret_the_defaults_find_is_not_indexable[2]` · `test_the_secret_is_found_by_content_whatever_the_file_is[5]` · `test_a_secret_far_into_a_long_file_is_found` · `test_only_the_files_with_a_secret_are_dropped_and_the_order_is_kept` · `test_a_link_to_a_file_with_a_secret_is_not_indexable` · `test_a_path_that_is_no_file_is_not_indexable` · `test_without_a_scanner_nothing_with_a_secret_is_let_through` · `test_the_filter_leaves_no_copy_of_a_secret_behind` · `test_the_dev_tiers_hold_the_seven_canaries` · `test_no_dev_canary_is_in_a_file_an_indexer_may_read[2]` | The filter does not exist |
| **Success 3.** Indexers skip every namespace the path map classes as product data [CAP-03.b] | `test_w1_15_product_data.py` | `test_a_file_in_a_product_namespace_is_not_indexable` · `test_the_same_file_is_indexable_once_the_map_classes_its_namespace_as_governance` · `test_a_namespace_the_map_turns_into_product_data_is_skipped` · `test_the_product_folder_of_this_repository_has_no_special_place` · `test_every_product_namespace_and_every_pattern_of_it_is_skipped` · `test_the_patterns_are_read_as_the_path_map_writes_them` · `test_a_namespace_the_map_does_not_class_as_governance_is_not_let_through[2]` · `test_a_secret_in_a_governance_file_is_dropped_whatever_the_map_says` | The filter does not exist |
| **Success 4.** Registers the secrets-indexing family check: no planted secret or canary in any derived store [CAP-38.b] | `test_w1_15_family_check.py` | `test_the_check_is_registered_in_the_kernel_template` · `test_the_check_passes_when_there_is_no_derived_store` · `test_the_check_passes_on_stores_without_a_secret` · `test_the_check_fails_on_a_canary_in_a_store_packet_or_bundle[3]` · `test_the_check_fails_on_a_planted_secret_in_a_database_store[3]` · `test_one_bad_store_among_clean_ones_fails_the_check` · `test_a_failing_check_names_the_store_and_does_not_repeat_the_secret` · `test_a_secret_in_a_source_file_is_not_a_store_finding` | The check is not registered |
| **Failure 1.** Any planted secret appears in a derived store, packet or bundle | `test_w1_15_family_check.py` · `test_w1_15_filter.py` | the six `test_the_check_fails_on_…` cases · `test_one_bad_store_among_clean_ones_fails_the_check` · every "is not indexable" test of the filter · `test_the_filter_leaves_no_copy_of_a_secret_behind` · `test_no_dev_canary_is_in_a_file_an_indexer_may_read[2]` | As above |
| **Failure 2.** The filter relies on a hard-coded path list | `test_w1_15_product_data.py` | the three tests that change the map and see the filter follow (`…once_the_map_classes_its_namespace_as_governance`, `…the_map_turns_into_product_data…`, `…has_no_special_place`) · `…every_pattern_of_it_is_skipped` · `…read_as_the_path_map_writes_them` | The filter does not exist |

**Count.** KPI lines with tests: 6 of 6 (4 success, 2 failure).

| Covers id | Tests |
|---|---|
| **CAP-03.a** default-deny content filter; class per namespace before index | all of `test_w1_15_filter.py`; the default-deny cases `test_without_a_scanner_…`, `test_a_path_that_is_no_file_…`, `test_a_namespace_the_map_does_not_class_as_governance_…[2]`; `test_w1_15_gitleaks_rules.py` |
| **CAP-03.b** governance memory separated from product data | all of `test_w1_15_product_data.py` |
| **CAP-03.e** exclusion holds on every route, the code route included | `test_the_secret_is_found_by_content_whatever_the_file_is[5]` (code files go through the same filter) · `test_the_check_fails_on_a_canary_in_a_store_packet_or_bundle[code-index]` · `test_no_dev_canary_is_in_a_file_an_indexer_may_read[b-dev]` (the canary stands in a TypeScript file) |
| **CAP-38.b** governance test family "secrets indexing" | all of `test_w1_15_family_check.py` |

## The 7 cases that pass before implementation

| Case | Why it passes today |
|---|---|
| `test_the_configuration_extends_the_gitleaks_defaults[repository]` | The existing `.gitleaks.toml` already extends the defaults; the test keeps that true. |
| `test_the_gitleaks_defaults_alone_miss_the_canary[2]` | A baseline, not a test of the ticket: it shows the planted strings really are ones the defaults miss (CAP-03 acceptance), so `test_the_canary_is_detected` can only pass through a rule the ticket adds. |
| `test_a_secret_the_defaults_find_is_still_detected[2 × repository]` | The existing file has the defaults on; the test guards against the new rules switching them off. |
| `test_text_about_canaries_and_tokens_is_not_a_finding[repository]` | The existing file has no rule that could match prose; the test guards the new rules against matching the words "canary" and "token". |
| `test_the_dev_tiers_hold_the_seven_canaries` | The premise of the dev-tier test: it reads the tiers, not the ticket's code. |

## Second batch: behaviours a review after green described (DEC-136)

File `test_w1_15_review_batch.py`: **14 test functions, 21 cases**. The review passed described behaviours, never
code; the tests were written from them and from DEC-285, DEC-290 and the KPIs. No earlier test was changed or
rewritten. The support module gained `Project.write_bytes`, `utf16` and `RULELESS_CONFIGS`.

Red run on `w1/W1-15` at `2936beee` plus this batch: **17 failed, 63 passed** (the 59 cases of the first batch and
the 4 "keep true" cases of this one). Without the `local_only` cases: 17 failed, 46 passed. Each failure is the
test's own assertion, with the reason below; none is a premise or a set-up failure.

| Behaviour | Test functions | Red reason today |
|---|---|---|
| **B1.** A link is judged by what it points to, for its namespace too (KPI success 3, CAP-03.b) | `test_a_governance_link_to_a_product_file_is_not_indexable[2]` (a relative and an absolute link) · `test_a_file_reached_through_a_governance_link_to_the_product_folder_is_not_indexable` · `test_a_governance_link_to_a_file_outside_the_project_is_not_indexable` · keep true: `test_a_governance_link_to_clean_governance_content_is_indexable[2]` (a file link and a folder link) | 4 red: the link, the path through the linked folder and the link out of the root are let through. The 2 keep-true cases pass. |
| **B2.** A scanner configuration without rules is "cannot decide" (DEC-285, CAP-03.a) | `test_the_filter_lets_no_canary_through_when_the_configuration_has_no_rules[2]` · `test_the_check_is_not_green_when_the_configuration_has_no_rules[2]` (an empty file; the defaults switched off and no rule) | 4 red: the canary is let through, and the check is green with the canary in a store. |
| **B3.** The check is not green on a store it cannot read (KPI success 4, CAP-38.b) | `test_the_check_is_not_green_on_a_store_it_cannot_enter[2]` (a folder under `.gov-runtime/`; `.gov-runtime/` itself) · keep true, first batch: `test_the_check_passes_when_there_is_no_derived_store` | 2 red: the check exits 0. |
| **B4.** The check follows a linked store folder (KPI success 4) | `test_the_check_fails_on_a_canary_in_a_linked_store_folder` | 1 red: the check exits 0. |
| **B5.** A secret in UTF-16 text is found (KPI failure 1, CAP-03.a) | `test_a_utf16_file_with_the_canary_is_not_indexable[2]` · `test_the_check_fails_on_a_canary_in_a_utf16_store[2]` (with and without a byte-order mark) · keep true: `test_the_check_passes_on_a_utf16_store_without_a_secret` | 4 red: the UTF-16 file is let through, and the check exits 0. The keep-true case passes. |
| **B6.** The check sees the whole content of a SQLite store (DEC-290, KPI success 4) | `test_the_check_fails_on_a_canary_left_in_the_bytes_of_a_deleted_row` · `test_the_check_fails_on_a_canary_in_the_text_of_a_view` · keep true: `test_the_check_passes_on_a_database_with_a_deleted_row_and_a_view_and_no_secret` (and, first batch, `test_the_check_passes_on_stores_without_a_secret`) | 2 red: the check exits 0. The keep-true case passes. |

How these tests decide:

- **B1.** The linked files hold no secret, so only the namespace of what the link points to can keep them out. A
  clean neighbour must stay, and the call must succeed: the filter can decide these.
- **B2.** The test project's `.gitleaks.toml` is replaced by one of two files that are valid TOML and hold no rule.
  The filter may raise instead of leaving the path out (DEC-285); no clean neighbour is required to stay.
- **B3.** The folder's mode is set to 0 and given back at teardown. Skipped when running as root, or when the file
  system still lets the folder be listed.
- **B4.** The linked folder stands outside the project, in the temporary directory.
- **B5.** UTF-16 is little-endian, with and without a byte-order mark. The filter test asserts first that the
  canary does not stand in the project as UTF-8 bytes, and that a UTF-16 neighbour without a secret stays.
- **B6.** The store is built with `PRAGMA secure_delete = OFF` and no vacuum. Each test asserts its premise before
  running the check: no row of the table holds the canary, and the bytes of the SQLite file do.

Not tested in this batch, on purpose: big-endian UTF-16 and other encodings; a store file (not folder) that cannot
be read; a link to a single store file; a SQLite store in WAL mode, with its side files.

## Third batch: a secret the project's `.gitleaks.toml` shelters (probe finding, DEC-298)

File `test_w1_15_shelter_batch.py`: **3 test functions, 12 cases**, added after implementation; reason: probe
finding (DEC-136). The probe passed a described behaviour, never code. No earlier test was changed or rewritten.
The support module gained `SHELTERS` and `shelter_config`.

DEC-290 made the pre-index filter ignore path allowlists. DEC-298 extends it to the other ways a project's
`.gitleaks.toml` can shelter a secret. The four shelters, each applied to the template's file at the test project's
root:

| Shelter | Change to the project's file | Planted secret |
|---|---|---|
| `global-regexes` | a `[[allowlists]]` entry whose `regexes` matches the secret | the canary (tier form) |
| `global-stopwords` | a `[[allowlists]]` entry whose `stopwords` holds a part of the secret | the canary (tier form) |
| `rule-allowlist` | a `[[rules.allowlists]]` entry on every rule the file itself holds (both find the canary) | the canary (tier form) |
| `disabled-rule` | `disabledRules` under `[extend]`, naming the default rule that finds the secret | the access token (a default rule finds it) |

Red run on `w1/W1-15` at `dfe244f0` plus this batch: **8 failed, 84 passed** (the 80 earlier cases and the 4
"keep true" cases of this one). Without the `local_only` cases: 4 failed, 67 passed. Each failure is the test's own
last assertion; every premise holds.

| Behaviour | Test functions | Red reason today |
|---|---|---|
| **C1.** The filter lets no secret through that the project's file shelters (DEC-298, CAP-03.a) | `test_a_file_with_a_secret_the_configuration_shelters_is_not_indexable[4]` · keep true: `test_a_file_without_a_secret_is_indexable_under_a_sheltering_configuration[4]` | 4 red: the planted file is let through to the indexer. The 4 keep-true cases pass. |
| **C2.** The check is not green on a store holding a secret the project's file shelters (KPI success 4, failure 1, CAP-38.b) | `test_the_check_is_not_green_on_a_store_with_a_secret_the_configuration_shelters[4]` | 4 red: the check exits 0. |

How these tests decide:

- **C1.** Before the filter is asked, the test runs the `gitleaks` binary by hand over the planted folder, twice:
  with the template's rules it reports the planted file and only it; with the shelter it reports nothing. So the
  shelter is one the scanner honours. Then the planted file must be absent from what the filter returns and the
  clean neighbour present. The call must succeed: the rules are there, so the filter can decide, and the keep-true
  cases require it to let files without a secret through under each of the four configurations.
- **C2.** **The check reads the project's `.gitleaks.toml`.** Its public behaviour shows it: with the same store
  the check fails under the template's file (the premise each case asserts) and is green once the file shelters the
  secret; and it is not green when the file holds no rules (B2). So each case plants the secret in a packet under
  `.gov-runtime/`, sees the check fail, applies the shelter, and expects the check still not to be green. DEC-298
  names the filter; for the check the expectation comes from KPI success 4 and failure 1 (no planted secret in a
  derived store).
- **Disabled rules.** `gitleaks` 8.30.1 disables only rules of the configuration a file extends
  (`[extend] disabledRules`); it has no switch for a rule the file itself holds, and naming such a rule there
  changes nothing. So the disabled case plants a secret a default rule finds.

Not tested in this batch, on purpose: a project that deletes or rewrites one of the template's own rules (package
DP-7); the older `[allowlist]` and `[rules.allowlist]` spellings of the same shelters; allowlist `commits`, and
`targetRules`, `condition` and `regexTarget`; inline `gitleaks:allow` comments and a `.gitleaksignore` file; that the
check stays green on clean stores under a sheltering file.

## `local_only` (21 cases)

Deselect with `-m "not local_only"` (71 cases remain).

- **Run the `gitleaks` binary directly** (18 cases): `test_the_canary_is_detected[4]`,
  `test_the_gitleaks_defaults_alone_miss_the_canary[2]`, `test_a_secret_the_defaults_find_is_still_detected[4]`,
  `test_text_about_canaries_and_tokens_is_not_a_finding[2]`,
  `test_the_token_canary_file_of_the_dev_tier_is_reported[2]`,
  `test_a_file_with_a_secret_the_configuration_shelters_is_not_indexable[4]`. Skipped when `gitleaks` is not on
  `PATH`.
- **Clone a dev tier** (`$GOV_DEV_TIERS`, default `~/gov-os-workbench/synthetic`; tiers `a-dev` and `b-dev`, by
  exact path): `test_the_dev_tiers_hold_the_seven_canaries`, `test_no_dev_canary_is_in_a_file_an_indexer_may_read[2]`
  and the two `…dev_tier_is_reported` cases above. Skipped when the tier is absent.
- The other filter and check tests are not marked. They pass `PATH` on to the child, so a filter that runs the
  `gitleaks` binary finds it; on a machine without the binary they depend on package DP-3.

## How the tests decide

- **Detected** means `gitleaks dir <tree> --config <file>` reports the planted file. The canary is planted in
  ordinary prose, with no key name beside it, in two forms: as the KPI writes it and as the b-dev tier holds it.
- **Not indexable** means the path is absent from what `gov.secrets.indexable` returns. A neighbour without a
  secret must stay, so "return nothing" does not pass.
- **The map decides** (failure 2). The product namespace of the test project is `tenant-exports/**`; no namespace
  or path of the test project is classed as product by this repository's own map. Three tests rewrite the map
  between two calls and expect the result to follow, and one classes `fixtures/**` as governance and expects its
  file to be let through.
- **The seven dev canaries** are the seven planted secret values of the two public dev tiers: three values with the
  canary word and an example cloud key pair in `a-dev`, the token canary and the key-file canary in `b-dev`
  (package DP-2). The dev-tier test adopts a clone with a one-namespace governance map, asks the filter about every
  tracked file, and expects no file holding one of the values to be let through, `README.md` to be let through,
  and more than half of the files to remain.
- **The check** is run by the tests, not by `gov check` (running checks is W1-26, DEC-186). A SQLite store with the
  secret in a row must fail the check: the Wave 1 stores are SQLite (DEC-074 R1). Note for the engineer:
  `gitleaks dir` skips a file it recognises as binary, a SQLite file included, so a plain scan of `.gov-runtime/`
  does not pass these three cases.

## Not tested, on purpose

- That an indexer calls the filter (no indexer exists; see the interface above).
- A path that matches no namespace, and a project with no path map at all: the sources do not say. The tests give
  every path a namespace.
- The namespace fields `sensitivity`, `export_policy`, `embedding_policy`, `retention` and `permitted_roles`: no
  KPI of this ticket reads them (package DP-5). Only `paths` and `memory_class` are read.
- The check's `tier` and `severity` values, beyond being valid.
- `.gov-runtime/scratch/`: whether it counts as a derived store.
- That this repository's own tree stays clean under the new rules (package DP-6).
