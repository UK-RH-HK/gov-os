# W2-138 evidence: the store's commit in every search result, and the worker's line-hash check (DAEO-rmhj; DEC-1090 (3), PAT-1 G2 and G4)

**The cause.** In PAT-1, two agents in two worktrees could not tell from a search result which commit the shared store
held (G2), and both were misled by the store's line numbers once integrate moved past their trees (G4). Each item's
`sha256` already settles "same or not"; nothing told a worker to use it. W2-116's R2-F1 rides along: with `--root
<link>`, each facet followed the link on its own (only `GOV_STORE` was resolved once).

## The change

- **`src/gov/retrieval/retrieve.py`:**
  - `resolved(root)`: the folder `root` names, its links followed once (`os.path.realpath`); as given where it leads
    to no folder. `retrieve()` calls it first, so every facet of a direct call reads one folder too.
  - `store_of(root)`: `{"commit": <the fingerprints row's head>, "root": <the folder>}`. The commit is the one the
    store was built at (`loader.fingerprints`), never the folder's HEAD now. A store built before W2-68 (no row), a
    folder with no store, or a store that cannot be read gives `commit: null`; the search then answers as today.
  - The continuation token carries `s`, the store's commit. `_decode_continuation(..., commit=)` refuses
    `CONTINUATION_INVALID`:
    - a token with no `s`: "the continuation was made before W2-138 and names no store commit: ask the first page
      again", `details.store_commit`;
    - a token whose `s` is not the store's commit now: "made on the store at commit <12 digits>, and the store is now
      at commit <12 digits>", `details = {"token_commit", "store_commit"}` in full;
    - a token that decodes to something other than an object (it used to raise `AttributeError`).
  - `retrieve(..., store=None)`: the command passes the `store_of` it read, so the result and the token name one
    reading.
- **`src/gov/retrieve/command.py`:** `_store_root` resolves a `--root` given and a call's `root` once, as `GOV_STORE`
  already was (`session_root`). Every result carries `store` first: the bundle and the stated gap (`UNRESOLVED_IDS`).
- **`src/gov/cli/main.py`** (DEC-1090, the designer's point (1)): the text form of `gov retrieve` prints
  `store: <commit, 12 digits> (<folder>)` before the JSON (`unknown` where the store names no commit).
- **`template/governance/kernel/skills/retrieval/SKILL.md`**, step 5: one line: compare each item's sha256 with the
  same lines in your own tree; if they differ, read `git show <commit>:<path>`; never cite the store's line numbers as
  your tree's. The generated `.claude` copy follows at the lift's re-pin ACT.
- **What stays as it was:**
  - each item's `sha256` is computed as before, from the bytes of its lines in the store's folder
    (`bytes.splitlines(keepends=True)`, both ends inclusive; a cut item on its full lines). The lexical index reads
    the working tree (DEC-344) and answers `stale` (no evidence) when a file there differs from what it indexed, so
    whenever a search hands out evidence, those lines are the lines at the store's commit;
  - `store` is added by the command, not by `retrieve()`: a direct call's bundle keeps today's keys, so the other
    tickets' "bundle unchanged" guards see only the token's new key (see the regression run);
  - `src/gov/retrieval/validate.py` is not changed: nothing in S1-S5 needs it.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: `--json` carries `result.store = {"commit", "root"}`; the text form's first line `store: <12 digits> (<folder>)` | `store_of` reads the fingerprint's head; the command puts it first in every result; `main._emit` prints the line | unit `tests/unit/retrieval/test_w2_138_store.py`: `test_s1_the_json_result_names_the_commit_the_store_was_built_at_and_its_folder` (the folder's HEAD moved by an empty commit after the build: the build's commit is named), `test_s1_the_text_form_opens_with_the_store_line`, `test_s1_the_session_variable_form_names_the_store_too`, `test_s1_the_stated_gap_names_the_store`, `test_s1_a_folder_with_no_store_names_no_commit`; acceptance success-1 6/6, failure-1 2/2 |
| S2: one folder for every facet of one search, even when the link is switched during it | `resolved()` in `_store_root` (`--root`, a call's `root`) and at `retrieve()`'s start; `GOV_STORE` as before | unit `test_s2_every_facet_reads_the_folder_resolved_at_the_start_across_a_switch[--root, GOV_STORE, direct]` (the lexical route's stand-in switches the link before the meaning route reads); acceptance success-2 2/2, failure-2 1/1 |
| S3: `CONTINUATION_INVALID` names the token's commit and the store's commit now | `s` in the token; `_same_store` in `_decode_continuation` | unit `test_s3_a_token_carries_its_store_commit_and_pages_on_the_same_store`, `test_s3_a_token_replayed_on_another_store_names_both_commits`, `test_s3_the_command_refuses_it_through_the_envelope`, `test_s3_a_token_made_before_w2_138_is_refused_as_such`, `test_s3_a_token_that_is_no_object_is_refused[2 rows]`; acceptance success-3 3/3 |
| S4: each item's sha256 is the sha256 of exactly its lines at `result.store.commit` | unchanged hashing over the store folder's lines, which the index holds at that commit (above) | unit `test_s4_every_item_s_sha256_is_its_lines_at_the_named_commit` (`git show <commit>:<path>`, a CRLF file and a file with no final newline among the items); acceptance success-4 2/2, failure-3 1/1 |
| S5: the retrieval skill's step 5 gains the line; the skills check | the line added under step 5 | `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/retrieval ...` (the `skill-regression-b1` check): no findings; acceptance success-5 5/5 |

The planted stores (temporary git repositories; secret filter replaced, no vectors, no model, the reranker a stand-in)
hold the same four Markdown files, built at two commits, and a link to the first.

## Test results (through the heavy slot; HOME a scratch folder with only the user site linked)

- **Unit:** `test_w2_138_store.py`: 15 passed (12 in a plain run, the 3 further parametrised rows by node id: the
  opt-in list keeps one row of each in a plain run).
- **`gov accept W2-138`:** pass, 18/18. success-1 6, success-2 2, success-3 3, success-4 2, success-5 5, failure-1 2,
  failure-2 1, failure-3 1; 0 unmapped, 0 skipped.
- **Regression** (`tests/unit/retrieval tests/unit/retrieve tests/acceptance/W2-116 tests/acceptance/W2-32
  tests/acceptance/W2-133`, `-m "not local_only" -k "not real and not green_here and not time_limit"`): 801 passed,
  29 failed, 3 skipped, 1 xfailed, 328 deselected (the opt-in lists and the exclusion), in 27 min 0 s.
  - 19 in `test_w2_112_shared_reranker.py`: the launch sandbox refuses the shared reranker's Unix socket
    (`PermissionError: [Errno 1] Operation not permitted`), as in W2-131, W2-133 and W2-135's runs. Not this change.
  - 10 "the same as before" guards, each failing on `continuation` alone (every field compared before it is equal):
    `test_w2_131_register_ids.py` (2), `test_w2_133_gap_label.py` (2), `test_w2_135_item_cap.py` (2) and
    `tests/acceptance/W2-133/test_w2_133_unchanged.py` (the two `every-chunk-batched` rows and the two continued-pages
    rows). Each compares today's token with the one `retrieve.py` made before its own ticket, which has no `s`. S3
    requires the token to carry the store's commit, so these guards change with it: the fix is in those tests (compare
    the decoded tokens without `s`), outside this ticket's paths. The unpaged cases of the same files pass, as `store`
    is added by the command and not by `retrieve()`.
  - W2-116's and W2-32's acceptance folders: no failure.
- **Skills check:** `skill-regression-b1`: `{"findings": []}`.
