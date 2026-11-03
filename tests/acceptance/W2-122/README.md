# W2-122 acceptance tests: seeded rebuilds (DAEO-blwa, STANDARD)

Written by the independent test designer (MR-3) from the ticket's KPI lines (`.tickets/DAEO-blwa.md`), DEC-1014
items 4 and 6, DEC-1015 item 4, and the lead's fixed interface (below), before and apart from the implementation.
Sources read: the ticket, the decision register (DEC-1014, DEC-1015, DEC-1011, DEC-1001, DEC-982, DEC-996, DEC-719,
DEC-530, DEC-374, DEC-694, DEC-966, DEC-963), `gov rebuild` as it stands on `w2/integrate` (its arguments, its
`--json` answer and its stores), and the earlier suites that rebuild planted repositories against a stand-in
endpoint (W2-76, W2-108, W1-27, W1-19), whose ways these tests reuse.

## How the tests choose the code under test (DEC-732)

**The code under test is whatever `gov` the pytest process imports.** Every rebuild is started as
`sys.executable -m gov.cli.main rebuild --json ...`, and its `PYTHONPATH` is the pytest process's own (else the folder
of the `gov` it imports). Nothing of this worktree is written into a child's path. Merged into the ticket's worktree
and run there with that worktree's `PYTHONPATH`, the tests exercise the ticket's code. Run them as:

    PYTHONPATH=<worktree>/src TMPDIR=<budget folder> python3 -m pytest tests/acceptance/W2-122 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

## The interface (the lead's reading, the same for the engineer)

- `gov rebuild --seed <folder>`: `<folder>` is the root of a warm base tree (it holds the base's `.gov-runtime/`); a
  link is followed. `gov rebuild --seed` with no folder reads `integration_store` (an absolute path) from
  `governance/project/rebuild.yaml`.
- The `--json` result of a rebuild given `--seed` holds `seed`: `status` (`seeded`, `refused` or `none`), `base` (the
  base read, or none) and `reason` (why, where it is not `seeded`).
- Every full rebuild writes `.gov-runtime/rebuild/stores.json`: at least `code`, `embedder` (`model`, `revision`, as
  the semantic stage records them) and `schema`.

**DEC-1027 C (owner, 2026-11-02):** the ticket's former KPI 5 (a rebuild whose semantic store was asked for and not
recreated fails, named) moved to W2-124 (`DAEO-mb2t`); its four cases (`test_w2_122_semantic_required.py`) are
retired from this suite. The ticket's other lines keep their numbers (K1 to K4, F1): K5 was the last success line.

## How the tests run

- Every project is a temporary git repository built from scratch under pytest's `tmp_path`: a path map (the
  template's, plus an embedded `docs/**` namespace), the template's gitleaks rules, a `rebuild.yaml` whose `lock` is
  a temporary path (no case takes the machine's rebuild lock), and four notes, each with a word of its own.
- **The base** is that repository at commit 1, rebuilt cold. **The tree** is a clone of it at commit 2: one note kept
  twice (`kept.md`, `kept-too.md`), one changed (`changed.md`), one removed (`removed.md`), one added (`added.md`).
- **The stand-in endpoint** speaks Ollama's HTTP interface on a loopback port that the case starts and stops. It
  reports `qwen3-embedding:0.6b` with a digest that begins with the pin (or with another revision), gives vectors
  made of the words of each text (and a salt per endpoint, so two embedders give other vectors), and records every
  text it is asked to embed. The shared embedding server is never asked.
- **Entry for entry** means: the result's `digest`; the stores' outcomes (`stores`, not `seed`); and every
  `lexical_*` and `semantic_*` table of `.gov-runtime/store.db`, row for row (a blob compared by its sha256, so every
  chunk's vector is compared; an `INTEGER PRIMARY KEY` row number is left out, as no entry of the store). The cold
  reference is the same tree with its `.gov-runtime/` removed and rebuilt without `--seed`. A cold rebuild against a
  cold rebuild of the same tree was checked equal under this comparison before the tests were written.
- **Re-embedded or not** is seen at the endpoint: a seeded rebuild must send no text holding a kept note's word.
- The environment of every child is built from scratch: an empty `HOME`; the real `gitleaks` linked first on
  `PATH`; no code-graph tool on `PATH` (as in W2-76: the code index reports itself not recreated and no daemon
  starts); `GOV_OLLAMA_BIN` naming no program; `GOV_SECRETS_CACHE` empty. Cases skip where `gitleaks`, `git` or
  `sqlite_vec` is missing.

## KPI lines and their tests

| KPI line | Tests |
|---|---|
| K1: `--seed <folder>` copies the base's stores, rebuilds incrementally (only changed files re-embedded), the same store entry for entry as a cold rebuild | `test_w2_122_seeded_equals_cold.py`: `test_a_seeded_rebuild_is_the_cold_rebuild_entry_for_entry`, `test_the_seed_names_the_base_it_read`, `test_a_seeded_rebuild_embeds_only_the_files_whose_content_changed`, `test_a_file_removed_since_the_base_leaves_no_entry_in_the_seeded_store`, `test_a_link_to_the_base_is_followed`, `test_seeding_leaves_the_base_unchanged` |
| K1, K2, K4: the answer (`seed`) and the base's record (`stores.json`), the lead's interface these three lines read | `test_w2_122_answer_and_record.py`: `test_a_full_rebuild_writes_the_record_of_its_stores`, `test_the_same_code_and_embedder_write_the_same_record_in_two_trees`, `test_a_seeded_answer_has_its_form`, `test_without_seed_a_rebuild_does_not_seed` |
| K2: a base whose code fingerprint, embedder model or schema differs is refused, named, and the rebuild runs cold (never two embedders mixed) | `test_w2_122_fail_closed.py`: `test_a_base_whose_record_differs_is_refused_named_and_the_rebuild_runs_cold` (four cases: code, schema, embedder-model, embedder-revision), `test_a_base_with_no_record_is_refused_and_the_rebuild_runs_cold`, `test_a_base_whose_record_cannot_be_read_is_refused_and_the_rebuild_runs_cold`, `test_a_base_built_by_another_embedder_revision_is_refused_and_never_mixed` |
| K3: measured on this repository, in `docs/changes/W2-122-evidence.md` | `test_w2_122_evidence.py::test_the_evidence_file_names_the_measurement` (the file exists and names the semantic stage's seconds and the embedding requests, seeded against cold, alone and with two others; no test runs the measurement) |
| K4: the warm base is the project's configured integration store; none configured rebuilds cold, named; nothing of this repository in the code | `test_w2_122_configured_base.py`: `test_seed_without_a_folder_reads_the_configured_base`, `test_a_project_with_no_configured_base_rebuilds_cold_named` (a base planted at ~/gov-os-worktrees/W2-00-store under the rebuild's HOME is not read), `test_a_configured_path_that_holds_no_base_rebuilds_cold_named`, `test_a_configured_base_that_does_not_match_is_refused_and_the_rebuild_runs_cold` |
| F1 (the ticket's first failure line): a seeded store that differs from a cold rebuild's; a seed from another embedder or schema used | Every K1 equality: `test_a_seeded_rebuild_is_the_cold_rebuild_entry_for_entry`, `test_a_link_to_the_base_is_followed`, `test_seed_without_a_folder_reads_the_configured_base`; every K2 case (refused, run cold, equal to cold): `test_a_base_whose_record_differs_is_refused_named_and_the_rebuild_runs_cold`, `test_a_base_with_no_record_is_refused_and_the_rebuild_runs_cold`, `test_a_base_whose_record_cannot_be_read_is_refused_and_the_rebuild_runs_cold`, `test_a_base_built_by_another_embedder_revision_is_refused_and_never_mixed` (the other embedder's vectors differ, so a mixed store fails the equality) |

## Expected red reasons (on the base code, `w2/integrate` at the designer's branch point)

| Test(s) | Red reason |
|---|---|
| Every K1 case, `test_a_seeded_answer_has_its_form`, the K4 cases with `--seed` | `gov rebuild` takes no `--seed`: a usage error, exit 2 ("unrecognized arguments: --seed") |
| `test_a_full_rebuild_writes_the_record_of_its_stores`, `test_the_same_code_and_embedder_write_the_same_record_in_two_trees`, every K2 case, `test_a_configured_base_that_does_not_match_...` | No `.gov-runtime/rebuild/stores.json` is written ("the full rebuild wrote no record"); the other-revision K2 case fails on `--seed` (usage error) |
| `test_the_evidence_file_names_the_measurement` | No `docs/changes/W2-122-evidence.md` |
| `test_without_seed_a_rebuild_does_not_seed` | Green: today's behaviour, held |

## Not tested here, and why

- **The code-graph store under a seed.** The code-graph tool is kept off `PATH` (as in W2-76: no daemon, no shared
  `/tmp` folder), so the code index is `not_recreated` in the seeded and the cold rebuild alike and only that outcome
  is compared. Its copy is the engineer's to show in the evidence.
- **The secrets record's entries.** W2-107's cache is machine-wide (`GOV_SECRETS_CACHE`, else one file under the
  home), not under a base's `.gov-runtime/`, so what "copied from the base" means for it is not observable from a
  base folder. Returned to the lead as a package; no case guesses it.
- **A rebuild whose semantic store was not recreated** (the former KPI 5): moved to W2-124 (DEC-1027 C); its
  tests are W2-124's.
