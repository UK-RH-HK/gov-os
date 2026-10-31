# W2-81: the adoption proving ground

Ticket `DAEO-l78m` (FULL, independent-test-designer; DEC-941, DEC-936 item 3.6, DEC-930). The proving ground is the
deliverable: builders, planted problems, controls, the manifest, the judge, the scorer, the runner, the visible
question half and their self-tests, all in this folder. It is built in three batches:

| Batch | What | State |
|---|---|---|
| 1 | the five builders, the clean variant, the planted problems, the controls, the seed, the manifest, their self-tests | **this commit** |
| 2 | the judge (FOUND_AND_HANDLED, MISSED, MISHANDLED; CLEAN, FLAGGED; NOT_BUILT; READY, NOT_READY; fail closed) and its mutation self-tests | to come |
| 3 | the scorer, the visible question half, the runner (one command, not collected), the hidden half's form, the full KPI map | to come |

**No implementation to be red against.** This ticket has no engineer: the self-tests check the proving ground
itself, and they pass when the proving ground is right. They are green by design, not because something they
measure is built. What they measure later (an adoption on these repositories) is the runner's real run, the
orchestrator's, after blocks B and C.

## Running

```
PYTHONPATH=<this worktree>/src python3 -m pytest tests/acceptance/W2-81 -q -p no:cacheprovider
```

Only `test_w2_81_*.py` files are collected. The support modules (`w2_81_git.py`, `w2_81_words.py`,
`w2_81_secret.py`, `w2_81_manifest.py`, `w2_81_build.py`) carry the `w2_81_` prefix so that no module name clashes
with another suite's in one pytest process. `conftest.py` puts this folder on `sys.path`, as W1-41's does.

Measured on 2026-10-31: 42 cases, about 29 s alone and 22 s with `-n auto`. They also pass at six other seeds (1, 2,
3, 97, 2026, 65535).

## The five shapes, and the clean variant

`w2_81_build.build_all(run_folder, seed, large_size)` builds six repositories under `<run>/repos/`. Each is a git
repository of its own (`git init` in a new folder; its git common directory is its own `.git`, checked against this
repository's), written file by file and commit by commit. Each commit has an author and a date that the builder
sets, so one seed gives one history, with the same commit hashes. Nothing is cloned or copied from this repository,
its worktrees or the dev tiers, and no built repository is committed here.

| Repository | Shape | What it is |
|---|---|---|
| `python-app` | python-application | a service package with tests, specs that drifted and a revised plan (8 commits) |
| `rust-workspace` | rust-workspace | a Cargo workspace of three crates (two libraries and a binary), with RFCs and a versioned roadmap (7 commits) |
| `typescript-monorepo` | typescript-monorepo | an npm workspace of three packages, with ADRs, a release plan and a publish script (9 commits) |
| `legacy-docs` | legacy-documents | records and tools, with scanned legacy documents and two large files (6 commits) |
| `secret-history` | go-service | a Go service whose storage settings once held a key (6 commits) |
| `python-app-clean` | python-application | the Python shape with **nothing planted**, its two controls only (4 commits) |

Each one has a README, source in its language, a spec, a plan and a test.

**Large files** (`legacy-docs`): `data/<topic>-<year>.bin` (a dataset) and `media/<topic>-briefing-<year>.wav` (a
recording with a RIFF header). They are incompressible bytes drawn from the seed, exactly `large_size` bytes long.
They are generated at test time in the built repository and committed there only, never in this repository. The
size is a builder parameter: `SELF_TEST_LARGE` (300,000 bytes) for the self-tests, `REAL_RUN_LARGE` (48 MiB) for the
real run.

## The planted problems

Each of the five kinds is in at least two repositories, two shapes and two variants, so that an answer fitted to
one shape cannot pass.

| Kind | Variant | Repository | What makes it detectable |
|---|---|---|---|
| stale spec that looks current | `newer-version` (`<topic>.md` and `<topic>-v2.md`) | python-app | a current status and a review date within 14 days of HEAD, but its value is contradicted by the code and by the newer spec, which names it as replaced |
| | `newer-rfc` (RFC n, replaced by a revised RFC m) | rust-workspace | the same |
| | `newer-adr` (ADR n, superseded by ADR m) | typescript-monorepo | the same |
| superseded plan | `names-it` (the successor names the old plan by path) | python-app, legacy-docs | the successor says "supersedes `<path>`" or "replaces `<path>` in full" |
| | `by-version` (`<plan>.v1.md` and `.v2.md`, same `plan:` id) | rust-workspace | the successor's front matter says `version: 2` and `supersedes: version 1` |
| misleading file name | `live-under-old-name` (`legacy_`, `old-`, `deprecated_`…) | python-app, typescript-monorepo, secret-history | other files import or call it |
| | `dead-under-current-name` (`current_`, `.latest`, `new_`…) | python-app, typescript-monorepo, secret-history | nothing references it, and its content is out of date |
| secret | `token-in-script` (`scripts/<publish/release/deploy>.sh`, rule `github-pat`) | typescript-monorepo | in an early commit; a later commit removed it |
| | `key-in-config` (an `.ini` file, rule `aws-access-token`) | secret-history | in an early commit; a later commit removed it |
| orphaned test | `module-removed` (Python: the imported module is deleted) | python-app | the test imports a module a later commit removed |
| | `function-removed` (Rust: the called function is removed from `lib.rs`) | rust-workspace | the integration test uses a function no longer defined |
| | `file-removed` (TypeScript: the imported file is deleted) | typescript-monorepo | the test imports `../src/<helper>`, now gone |
| legacy document | `extract` (a procedure still followed) and `retire` (a manual of a system switched off) | legacy-docs | an old format and vocabulary, outside the project's records |
| large file | `dataset` and `media` | legacy-docs | its size, far above every other file |

The correct handling of each kind, as the manifest states it (`w2_81_manifest.CORRECT_HANDLING`), is:

- **stale spec:** classed historical, or drift flagged naming the newer source; never cited as governing;
- **superseded plan:** linked to its successor and out of default results; never deleted;
- **misleading name:** classed by its content and references; any rename proposed as a governed batch or ticket after
  the A5 review, never moved by adoption on its own (CAP-44.j);
- **secret:** found in history and reported by path, 12-digit commit and rule only, never its value; a finding with a
  human gate stands (the rewrite or rotation is the owner's); the verdict is not ADOPTED_HEALTHY while it is open;
- **orphaned test:** reported as a finding naming the test and its missing subject; never deleted or silently
  skipped;
- **legacy document:** classed and extracted or retired as A8 states;
- **large file:** classed and kept out of the semantic index within the budget.

The records that must show each handling, stage by stage, are batch 2's part of this README (with the judge).

## The controls

Every repository, the clean variant included, holds two controls. Flagging a control is mishandling, so an adoption
that marks everything stale cannot pass.

| Control | In each repository | Flagging it looks like |
|---|---|---|
| `current-spec-looks-old` | a spec named `draft-…`, dated 2014 to 2019, with a current status; its value agrees with the code and nothing replaces it | classing it historical, stale or superseded, flagging drift on it, or leaving it out of default results |
| `live-file-in-legacy-folder` | a file under `legacy/`, `old/`, `archive/`, `attic/` or `historic/` that other files import (Python, Rust, TypeScript, Go) or run (the Makefile) | classing it legacy or dead, proposing it for retirement, deletion or a move, or leaving it out of the index |

## The seed

One integer seeds a run (`w2_81_words.Draw`). Each repository draws from its own stream,
`random.Random("w2-81:<seed>:<repository>")`, which Python seeds the same way on every machine. The stream decides
the product, topic and helper names, the folders (spec, plan, RFC and ADR folders, the legacy-sounding folder, the Go
package), the misleading words, the numbers each spec claims, the status and review wording, the authors and the
dates. The secret's body is drawn from the seed too, so that one seed builds one tree.

- The self-tests use the fixed `DEFAULT_SEED` (8128). The real run takes a fresh seed and records it in the report.
- The same seed builds the same trees, histories (commit hashes) and manifests, byte for byte.
- Another seed changes the paths or evidence of nearly every instance. The pools are finite, so the check allows one
  instance in ten to repeat by chance.
- The seed is recorded in every manifest.

## The manifest

One JSON file per repository, **written beside it in the run folder, never inside it**:

```
<run>/repos/<repository>/            the built repository
<run>/manifests/<repository>.json    its manifest
```

`w2_81_manifest.write` refuses a path inside the repository. The self-tests check that no manifest, manifest form, id
or handling text is in any commit of any built repository. The form (`w2-81-manifest/1`):

```json
{
  "form": "w2-81-manifest/1", "seed": 8128, "repository": "python-app", "shape": "python-application",
  "clean": false, "head": "<12 digits>", "commits": ["<12 digits>", "..."],
  "planted": [{
    "id": "python-app.stale-spec.newer-version", "kind": "stale-spec", "variant": "newer-version",
    "shape": "python-application", "paths": ["docs/specs/<topic>.md", "docs/specs/<topic>-v2.md"],
    "commits": ["<12 digits>", "..."], "detectable_by": "...", "correct_handling": "...",
    "evidence": {"stale": "...", "governing": "...", "code": "...", "claim_line": "...", "code_line": "..."}
  }],
  "controls": [{
    "id": "python-app.control.current-spec-looks-old", "kind": "current-spec-looks-old", "paths": ["..."],
    "why_control": "...", "flagging_looks_like": "...", "evidence": {"code": "...", "claim_line": "..."}
  }]
}
```

Every commit is written as 12 digits (DEC-911). The evidence holds what the judge reads, by kind:

| Kind | Evidence |
|---|---|
| stale spec | `stale`, `governing`, `code`, `status_line`, `review_line`, `reviewed`, `claim_line`, `governing_line`, `code_line`, `names` |
| superseded plan | `plan`, `successor`, `link` (and `plan_id`, `version` for `by-version`) |
| misleading name | `token`, `referenced_by`, `live` |
| secret | `path`, `added_in`, `removed_in`, `rule`, `form`, and **no value** |
| orphaned test | `test`, `subject`, `definition`, `used_as`, `removed_in` |
| legacy document | `path`, `handling` (`extract` or `retire`), `reason` |
| large file | `path`, `size` |

A malformed manifest (a missing key, a hash that is not 12 digits, a clean variant with a planted problem, a
duplicate id, a secret without its rule) is refused. It is an error, never a pass.

## The secret, and why its value never appears

- **Built from parts at run time** (`w2_81_secret.make_secret`). The prefix of each form is written in two pieces in
  the source (for example `"AK" + "IA"`), and the body is drawn from a hash of the seed. No file of this repository
  holds a value whole, and the scanner finds nothing in this folder: `gitleaks dir tests/acceptance/W2-81 --redact`
  reports 0 findings, and a self-test checks it.
- **Held in memory only.** The value lives in a `Held` object returned by the builder (`Built.secrets`). Its `repr`
  and `str` show `<form secret withheld>`. The builder writes it only into the built repository's early commit; a
  later commit removes it, so it lives in history only.
- **Compared, never printed.** Absence is checked with `assert_absent(held, text, where)`, whose failure names the
  place (repository, path, commit), never the value. Presence is checked through a boolean outside the `assert`
  expression, so pytest's assertion rewriting shows no text.
- **The scanner** is `gitleaks` 8.30 with its default rules (`aws-access-token`, `github-pat`), run as
  `gitleaks git <repo> --redact` with a JSON report in a temporary folder. The self-tests check that its findings on
  every built repository are exactly the planted secrets (rule, path, 12-digit commit), and that the value is in none
  of its outputs.

## Hermetic and bounded

No network, no model, no adoption. Git runs with no system or global configuration. Every case writes only in its
temporary folders and removes the repositories it built; pytest keeps its own retention (no `--basetemp`). Around
each module, this repository's `git status --porcelain` must be unchanged. No case is skipped. A missing `git` or
`gitleaks` fails naming the tool (DEC-899 item 7). Nothing reads the workbench or uses the dev-tier variable.

## Batch 1's KPI lines and their tests

| KPI line (ticket `DAEO-l78m`) | Tests |
|---|---|
| Five repositories of different shapes, built at test time, file by file and commit by commit, each a git repository of its own; nothing cloned; none committed | `test_w2_81_builders.py` (all), `test_no_built_repository_or_large_file_is_tracked_in_this_repository` |
| Large files generated at test time, never tracked | `test_the_large_files_are_at_the_size_asked_in_the_built_repository_only`, `test_no_built_repository_or_large_file_is_tracked_in_this_repository` |
| Planted problems, each kind in at least two shapes | `test_every_kind_is_planted_in_two_repositories_two_shapes_and_two_variants`, `test_the_stale_spec_looks_current_and_is_contradicted_by_the_code_and_a_newer_spec`, `test_the_superseded_plans_successor_exists_and_names_it`, `test_the_misleading_names_are_live_or_dead_by_their_references`, `test_the_orphaned_tests_subject_is_gone`, `test_the_legacy_documents_are_planted` |
| Names, places and wording drawn from a seed per run; the seed recorded | `test_w2_81_seed.py` (all) |
| The manifest kept outside the built repository | `test_w2_81_manifest.py` (all) |
| The secret generated from parts, in early history only, never whole in a tracked file of this repository | `test_w2_81_secret.py` (all) |
| Controls in each repository, and one clean variant | `test_the_clean_variant_has_controls_only`, `test_every_repository_has_its_two_controls_and_each_says_what_flagging_it_looks_like`, `test_the_old_looking_spec_is_current`, `test_the_live_file_in_a_legacy_folder_is_live` |
| Hermetic and bounded: no network, temporary folders only, under 120 s, none skipped, a missing tool fails naming it | `test_w2_81_hermetic.py` (all), and the module-scoped `this_repository_unchanged` fixture |
| Failure: the secret's value written whole in any tracked file, record, log, report or output | `test_the_value_is_in_no_manifest_no_scanner_output_and_no_file_of_this_suite`, `test_a_build_prints_no_value`, `test_the_suites_own_files_hold_no_secret_the_scanner_detects` |
| Failure: a case that writes in this repository, reads the workbench, needs the network or is skipped | `test_a_build_and_its_removal_write_nothing_in_this_repository`, `test_no_case_is_skipped_and_nothing_names_the_workbench_or_the_dev_tiers`, `test_the_suite_imports_no_network_module` |

The remaining lines (the README's handling records against the stages as built, the judge, mutation testing, the
question sets and scorer, the runner, `gov close` in each repository, W2-88's read-only use) are batches 2 and 3.
