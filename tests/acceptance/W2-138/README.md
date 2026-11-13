# W2-138 acceptance tests: the store's commit in every search result, and the line-hash check

Ticket DAEO-rmhj (W2-138), profile STANDARD (DEC-1090 (3), PAT-1 G2 and G4). Written by the independent test
designer (MR-3) from the ticket's KPI lines S1 to S5 and its three failure lines, before any implementation,
reading only the integrated code (`w2/integrate` at `f50fb0025`, DEC-963): `gov.retrieve.command` (`_store_root`,
`GOV_STORE`), `gov.launch.store.session_root`, `gov.retrieval.retrieve` (the item, its sha256, the continuation),
`gov.cli.main` (the envelope, the text form), `gov.store.loader.fingerprints` and `gov.rebuild.integration`.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-138 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

Under 1 s, in process. The tests use the tree `PYTHONPATH` names; without one, the worktree's own `src`.
`gov accept W2-138 --root <worktree>` reads the map below: 8 lines (S1-S5, F1-F3), 18 tests, none unmapped. Its
child drops every `PYTHON*` variable, `PYTHONUSERBASE` too, so where pytest lives in the user site and `HOME` is
emptied, that `HOME` needs a `.local` link to the user site (nothing else) for the child to import pytest.

- **The planted stores** (`w2_138_support.make_stores`, once per session): one git repository with two commits
  and two store folders as the integration store keeps its halves (W2-116): detached worktrees, `store-a` at C1 and
  `store-b` at C2, each with its lexical index and record store built in place (`lexical.refresh`, `store.load`),
  the secret filter replaced (as the unit tests do). The path map is `namespaces: {}` plus the register's key
  (the command line loads the configuration first, DEC-185). C1 holds a register (`DEC-101`, *juniper*), a long
  Markdown note (`alpha.md`, *quillwort* in its last chunk: expanded to its parent at the default budget, sent alone
  at 200), a CRLF note (*bergamot*), a note with no final newline (*marjoram*), a note with one line over 4,000
  characters (*saffron*: W2-135's `cut`) and a short note (*fennel*); *lantern* is in all of them. C2 puts two
  lines before everything in `alpha.md`, adds a line to `gamma.md` and adds `delta.md`.
- **The commit "the store was built at"** is the commit its record store's load ran at (the fingerprints row's
  `head`, W2-68), which is the folder's HEAD when built. One S1 case moves the folder's HEAD by an empty commit
  after the build, with no rebuild: the result still names the commit the store was built at.
- **The link:** a symbolic link under the case's `tmp_path`, switched as `gov rebuild --integration` switches it
  (a new link renamed over the old).
- **The command line in process:** `gov.cli.main.main([...])`, stdout captured, so the stand-ins hold for it
  too. `--json` reads the envelope's `result` and `error`; the text form is the same call without `--json`.
- **No embedder, reranker or model:** the semantic route is a stand-in with no hit, the file route off, the
  reranker the identity (`retrieve.rerank`, `retrieve.last_outcome`), no question names a symbol. `GOV_ROLE`,
  `GOV_TICKET` and `GOV_STORE` are cleared and each case runs in an empty folder.

## The S2 seam

`gov.retrieval.lexical.search` is wrapped (monkeypatch): the first time it returns, the link is switched from
`store-a` to `store-b`. The folder each store read is given is recorded as it stands at the call
(`os.path.realpath` of its root argument): `lexical.search`, the semantic stand-in, `lexical.chunks`,
`lexical.parent`, `records.records` and `records.edges`. All must be `store-a`, and every item's lines and sha256
must be `store-a`'s at C1. On integrate, through `--root <link>`, the semantic facet and the chunks read
`store-b` after the switch; through `GOV_STORE` the link is already followed once (`session_root`).

## The byte rule (S4)

An item's lines are read from git, never from the code under test: `git cat-file blob <commit>:<path>` (no
filter, no decoding). A line is its bytes up to and including its LF, so a CRLF line keeps both bytes; the file's
last line is taken as it is, with no newline added where the file has none; lines are numbered from 1, and
`start_line` and `end_line` are both inclusive. The expected sha256 is the hex sha256 of lines `start_line` to
`end_line` joined as they are. An item whose text is cut (W2-135) is hashed on its full lines. This agrees with
today's item (`bytes.splitlines(keepends=True)` over the folder's file) for every planted file; it differs only
for a lone CR, which no planted file holds.

## KPI lines, tests, and the outcome on `w2/integrate`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and
not time_limit"` (it leaves none of these out), on `f50fb0025`: **18 tests, 13 failed, 5 passed** (0.7 s). Every
red fails on its own line's behaviour, none on a planted premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_138_store.py::test_s1_the_json_result_names_the_store_s_full_commit_and_folder` | red | the result has no `store` key |
| S1 | `test_w2_138_store.py::test_s1_the_text_form_s_first_line_is_store_commit_12_digits_and_folder` | red | the text form's first line is `{` (the result as JSON) |
| S1 | `test_w2_138_store.py::test_s1_through_a_link_given_as_root_the_root_is_the_half_it_points_to` | red | no `store` key (and `--root <link>` is kept as the link today) |
| S1 | `test_w2_138_store.py::test_s1_through_gov_store_with_no_root_the_root_is_the_half_the_link_points_to` | red | no `store` key |
| S1 | `test_w2_138_store.py::test_s1_the_commit_is_the_one_the_store_was_built_at_not_a_later_head_of_its_folder` | red | no `store` key |
| S1 | `test_w2_138_store.py::test_s1_a_stated_gap_result_names_the_store_too` | red | the `UNRESOLVED_IDS` bundle has no `store` key |
| S2 | `test_w2_138_one_folder.py::test_s2_one_search_reads_one_folder_when_the_link_is_switched_between_the_facets[root-link]` | red | through `--root <link>`, `semantic.search` and `lexical.chunks` read `store-b` after the switch |
| S2 | `test_w2_138_one_folder.py::test_s2_one_search_reads_one_folder_when_the_link_is_switched_between_the_facets[gov-store-link]` | green (guard) | `GOV_STORE`'s link is followed once today (`session_root`); it must stay so |
| S3 | `test_w2_138_continuation.py::test_s3_a_token_made_on_one_store_and_replayed_on_another_is_refused_naming_both_commits[two-folders]` | red | the token from `store-a` is accepted on `store-b` (`ok`, a page) |
| S3 | `test_w2_138_continuation.py::test_s3_a_token_made_on_one_store_and_replayed_on_another_is_refused_naming_both_commits[one-link-switched]` | red | as above, through one link switched between the two calls |
| S3 | `test_w2_138_continuation.py::test_s3_guard_a_token_replayed_on_the_store_it_was_made_on_carries_on` | green (guard) | the token replayed on its own store is accepted; it must stay so |
| S4 | `test_w2_138_line_hash.py::test_s4_every_item_s_sha256_is_the_hash_of_its_own_lines_at_result_store_commit` | red | no `result.store.commit` to read the lines at (S1's field); the hashes themselves hold |
| S4 | `test_w2_138_line_hash.py::test_s4_guard_every_item_s_sha256_is_the_hash_of_its_own_lines_at_the_commit_the_store_was_built_at` | green (guard) | every item's sha256 is its own lines' at C1 / C2 today, CRLF, no final newline, a cut line and an expanded parent included |
| S5 | `test_w2_138_skill.py::test_s5_step_5_tells_the_worker_to_compare_each_item_s_sha256_with_its_own_tree` | red | step 5 says nothing of the worker's own tree |
| S5 | `test_w2_138_skill.py::test_s5_step_5_names_result_store_commit_and_git_show_of_the_store_s_text` | red | step 5 names neither `result.store.commit` nor `git show <commit>:<path>` |
| S5 | `test_w2_138_skill.py::test_s5_step_5_says_never_cite_the_store_s_line_numbers_as_your_tree_s` | red | step 5 says nothing of line numbers |
| S5 | `test_w2_138_skill.py::test_s5_guard_step_5_keeps_its_checks_of_the_bundle` | green (guard) | step 5 keeps the stopping reason, `id`, `sha256` and superseded checks |
| S5 | `test_w2_138_skill.py::test_s5_guard_the_skills_check_finds_nothing_in_the_retrieval_skill` | green (guard) | `gov.check.skill_validator` finds nothing in the file (frontmatter, token limits, commands) |
| F1 | `test_w2_138_store.py::test_s1_the_json_result_names_the_store_s_full_commit_and_folder` | red | as in S1 |
| F1 | `test_w2_138_store.py::test_s1_a_stated_gap_result_names_the_store_too` | red | as in S1 |
| F2 | `test_w2_138_one_folder.py::test_s2_one_search_reads_one_folder_when_the_link_is_switched_between_the_facets[root-link]` | red | as in S2 |
| F3 | `test_w2_138_line_hash.py::test_s4_every_item_s_sha256_is_the_hash_of_its_own_lines_at_result_store_commit` | red | as in S4 |

**A check of the tests themselves** (a scratch copy of `src`, never committed): about 25 lines in `command.run`
(the root resolved with `os.path.realpath` once, the commit read from the store's fingerprints row, `store` put
on both bundles, the text line printed when `--json` is not given) and in `retrieve` (the token carrying the
store's commit as one more key, a mismatch refused `CONTINUATION_INVALID` naming both) passes all 15 code cases;
the 3 S5 text cases stay red as the sketch leaves the skill alone. Step 5 with the KPI's own sentence added
passes all five S5 checks (checked on the text, outside the tests).

## Notes and limits

- **N-1. The text form.** `gov.cli.main._emit` prints the result as JSON when `--json` is not given, and
  `src/gov/cli/main.py` is not in the ticket's `allowed_paths`. The cases ask only for the first line of stdout;
  the command may print it itself before the result.
- **N-2. "Built at".** The cases read it as the store's fingerprints `head` (the commit `store.load` ran at); a
  result that names the folder's HEAD instead fails only
  `test_s1_the_commit_is_the_one_the_store_was_built_at_not_a_later_head_of_its_folder`.
- **N-3. Naming both commits (S3).** Each commit is accepted by its full id or its first 12 hex digits, in the
  refusal's `message` or `details`. A token made before this change (with no commit in it) is not planted: what
  it should get is not stated.
- **N-4. S4's red is S1's.** The hash holds today; the case goes red only because `result.store.commit` is absent.
  The guard reads the lines at the commit the test knows the store was built at.
- **N-5. S5's skills check** is `gov.check.skill_validator.validate_file` on the template's file. The generated
  `.claude` copy follows at the lift's re-pin ACT and is not read here.

## Files

- `w2_138_support.py`: the planted repository and its two store folders, the link, the command line in process,
  the S4 oracle.
- `conftest.py`: the session's stores and the stand-ins (autouse).
- `test_w2_138_store.py` (S1, F1), `test_w2_138_one_folder.py` (S2, F2), `test_w2_138_continuation.py` (S3),
  `test_w2_138_line_hash.py` (S4, F3), `test_w2_138_skill.py` (S5).
