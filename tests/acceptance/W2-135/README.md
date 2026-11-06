# W2-135 acceptance tests: a bundle item over 4,000 characters is sent as its first 4,000, marked cut

Ticket DAEO-c4pb (W2-135), profile STANDARD, BUNDLE-BUDGET-1 option (a) (DEC-1086 B; DEC-1087 (1)). Written by the
independent test designer (MR-3) from the ticket's KPI lines S1 to S3, before any implementation, reading only the
integrated code (`w2/integrate` `fc61f303d467`, DEC-963). S4 is the CTO's check after the re-pin, not a test here.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-135 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

(`PYTHONUSERBASE` only where pytest is installed in the user's site and `HOME` is emptied.) About 1 s, in process.
The tests use the tree `PYTHONPATH` names; without one, the worktree's own `src`.

- **The planted repository** (`w2_135_support.build`, once per session): a temporary git repository with
  `data/ledger.json`, one line of 24,575 characters and no newline at its end (valid JSON); `docs/survey.md`, a
  section of ordinary lines holding one line of 10,631 characters (line 9), then a section `## Almanac` of 44
  ordinary lines; `notes/lantern.txt` (exactly 4,000 characters) and `notes/beacon.txt` (4,001), one line each, no
  newline at the end; `notes/brioche.txt` (4,500 accented characters, about 6,900 bytes) and `notes/meringue.txt`
  (3,000 accented characters, over 4,000 bytes); and an ordinary note. Its lexical index and record store are built
  in the temporary folder, the secret filter replaced (as the unit tests do). Never this repository's store.
- **One question, one span:** `zephyrine` reaches the JSON file alone; `quillwort` the long line alone, which at the
  default budget is expanded to its section (lines 1-14, 11,220 characters) and at `bundle_budget=1` is sent alone
  (line 9, 10,632 characters with its newline); `beacon`, `brioche`, `lantern`, `meringue` and `kestrel` their own
  files; `harbour` every file; `tide almanac` the almanac section.
- **No embedder, reranker or model:** the semantic route is a stand-in with no hit, the file route off; every call
  is given a stand-in reranker (`w2_135_support.Scorer`) that keeps each text it is sent (the reranker's input) and
  scores it by a hash of the text. No question names a symbol or a record, so neither the code route nor a closure
  is asked. `GOV_ROLE` and `GOV_TICKET` are cleared.
- **The oracle** (`w2_135_support.span_text`, `span_bytes`): an item's full text and bytes read from the planted
  files alone, never from the code under test.
- **"Today" for S1's guard, S2 and S3** (`w2_135_support.today`): `src/gov/retrieval/retrieve.py` (blob
  `7444017b123c`) as `w2/integrate` `fc61f303d467` held it, read from git and loaded as a module of its own beside the
  running tree's. It is the ticket's only source path, so the two differ by the fix alone; both are asked on the same
  store, in the same process, with the same stand-ins.
- **S3's comparison** sets apart each item's `text` and `cut` only, and holds even those: an item with a `cut` key
  is today's text's first 4,000 characters; one without is today's text, unchanged. Every other item field, the
  items' order and cited lines (path, lines, chunk id, sha256), and every other bundle key (`budget` with its `used`,
  `batches`, `expansions` with `left_out`, `repeats`, `gaps`, `continuation`, `merge`, `facets`, `stopping_reason`,
  `rerank`) must equal today's, on every page of each batched question followed through its continuations. The
  reranker's input is the list of texts the stand-in reranker is sent, over all pages, compared with today's.
- **S3's premise** (`test_s3_premise_the_scenarios_hold_what_s3_names`) shows on today's code that the eleven
  scenarios hold an expansion with a left-out span, repeats of both kinds, not-gathered gaps, continuations, a second
  batch, items over the cap both alone and as an expansion, and one call (`zephyrine quillwort`) where today's
  `used` (8,802, on the full text) is over the 6,000 limit, so the survey's section is not expanded, while a `used`
  counted on the cut text would let it expand: a fix that counts the cut text fails S3 there.

## KPI lines, tests, and the outcome on `w2/integrate` `fc61f303d467`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **48 tests, 11 failed, 37 passed** (1.00 s). Every red fails because the
item is sent whole or carries no `cut` key, none on a premise. `gov accept W2-135` reads this map: S1 10 passed and
11 failed, S2 4 passed, S3 23 passed, none unmapped (outcome `fail`, exit 3).

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[json-one-line-24575]` | green (premise) | the span holds 24,575 characters and today's item is it whole, no `cut` |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[markdown-long-line-alone]` | green (premise) | line 9 alone, 10,632 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[markdown-section-expanded]` | green (premise) | the expanded section 1-14, 11,220 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[one-over-the-cap-4001]` | green (premise) | 4,001 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[accented-4500-characters]` | green (premise) | 4,500 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_the_item_s_text_is_its_first_4000_characters[json-one-line-24575]` | red | the JSON file's item is sent as 24,575 characters |
| S1 | `test_w2_135_cut.py::test_s1_the_item_s_text_is_its_first_4000_characters[markdown-long-line-alone]` | red | sent as 10,632 characters |
| S1 | `test_w2_135_cut.py::test_s1_the_item_s_text_is_its_first_4000_characters[markdown-section-expanded]` | red | the expansion is sent as 11,220 characters |
| S1 | `test_w2_135_cut.py::test_s1_the_item_s_text_is_its_first_4000_characters[one-over-the-cap-4001]` | red | sent as 4,001 characters |
| S1 | `test_w2_135_cut.py::test_s1_the_item_s_text_is_its_first_4000_characters[accented-4500-characters]` | red | sent as 4,500 characters (a cut by bytes would also fail it: 4,000 bytes are fewer characters) |
| S1 | `test_w2_135_cut.py::test_s1_the_cut_item_carries_its_cut_key[json-one-line-24575]` | red | no `cut` key; expected `{"chars": 24575, "sent": 4000}` |
| S1 | `test_w2_135_cut.py::test_s1_the_cut_item_carries_its_cut_key[markdown-long-line-alone]` | red | no `cut` key; expected `{"chars": 10632, "sent": 4000}` |
| S1 | `test_w2_135_cut.py::test_s1_the_cut_item_carries_its_cut_key[markdown-section-expanded]` | red | no `cut` key; expected `{"chars": 11220, "sent": 4000}` |
| S1 | `test_w2_135_cut.py::test_s1_the_cut_item_carries_its_cut_key[one-over-the-cap-4001]` | red | no `cut` key; expected `{"chars": 4001, "sent": 4000}` |
| S1 | `test_w2_135_cut.py::test_s1_the_cut_item_carries_its_cut_key[accented-4500-characters]` | red | no `cut` key; expected `{"chars": 4500, "sent": 4000}` |
| S1 | `test_w2_135_cut.py::test_s1_the_one_line_json_file_s_cut_names_24575_characters` | red | the ticket's number, written out: no `cut` key today |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[json-one-line-24575]` | green (guard) | path, start_line, end_line, id, chunk_id and sha256 are today's; the sha256 is of the full span's bytes |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[markdown-long-line-alone]` | green (guard) | as above |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[markdown-section-expanded]` | green (guard) | as above, for an expansion |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[one-over-the-cap-4001]` | green (guard) | as above |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[accented-4500-characters]` | green (guard) | as above |
| S2 | `test_w2_135_under.py::test_s2_an_item_at_or_under_4000_characters_is_sent_as_today_with_no_cut_key[exactly-the-cap-4000]` | green (guard) | exactly 4,000 characters: whole, no `cut`, every field today's |
| S2 | `test_w2_135_under.py::test_s2_an_item_at_or_under_4000_characters_is_sent_as_today_with_no_cut_key[accented-3000-characters-over-4000-bytes]` | green (guard) | 3,000 characters but over 4,000 bytes: whole (the cap counts characters) |
| S2 | `test_w2_135_under.py::test_s2_an_item_at_or_under_4000_characters_is_sent_as_today_with_no_cut_key[ordinary-note]` | green (guard) | two ordinary items: as today |
| S2 | `test_w2_135_under.py::test_s2_every_item_at_or_under_the_cap_in_every_scenario_is_today_s` | green (guard) | every item at or under 4,000 characters on every page of S3's eleven scenarios equals today's, field by field |
| S3 | `test_w2_135_unchanged.py::test_s3_premise_the_scenarios_hold_what_s3_names` | green (premise) | the scenarios hold what S3 names (see above), on today's code |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[json-alone]` | green (guard) | the running tree is today's code; any change beside the cut text and the cut key fails it |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[long-line-alone]` | green (guard) | as above; `used` 2,658 over a limit of 1 |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[long-line-section-expanded]` | green (guard) | as above; an expansion over the cap |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[json-beside-the-long-line]` | green (guard) | as above; `used` 8,802 over 6,000, no expansion (a count on the cut text would expand) |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[edges]` | green (guard) | as above; the four files at the cap's edge |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[every-file]` | green (guard) | as above; 15 items in two batches |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[every-file-budget-12000]` | green (guard) | as above; `used` 13,879 over 12,000 (on the cut text it would be under) |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[every-file-expanded]` | green (guard) | as above; two expansions, one over the cap |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[almanac-batched]` | green (guard) | as above; a continuation, gaps, repeats `SENT_IN_AN_EARLIER_PARENT` |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[every-file-batched]` | green (guard) | as above; eight pages, gaps, repeats, the cut-size items on their own pages |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_text_and_cut_key[almanac-batched-budget-1000]` | green (guard) | as above; an expansion with `left_out` [[30, 57]] and repeats `SENT_EARLIER_AS_A_CHILD` |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[json-alone]` | green (guard) | the texts the reranker is sent equal today's |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[long-line-alone]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[long-line-section-expanded]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[json-beside-the-long-line]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[edges]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[every-file]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[every-file-budget-12000]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[every-file-expanded]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[almanac-batched]` | green (guard) | as above, over every page |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[every-file-batched]` | green (guard) | as above, over every page |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[almanac-batched-budget-1000]` | green (guard) | as above, over every page |

**A check of the tests themselves** (scratch copies of `src`, never committed): `item()` setting
`cut = {"chars": len(text), "sent": 4000}` and `text = text[:4000]` when the text is over 4,000 characters passes all
48. The same sketch with the budget's `used` counted on the first 4,000 characters fails 10: nine of S3's bundle
cases (`budget` changed; at `bundle_budget=12000` a parent then expands that today's does not) and S2's sweep (an
item's lines changed by that expansion).

## Notes and limits

- **N-1. `chars` is the item's full text length, newline included.** The ticket's Markdown line is 10,631
  characters; the item that holds it alone is that line with its newline, 10,632 characters, so its `cut` is
  `{"chars": 10632, "sent": 4000}`. The JSON file has no newline at its end, so its item is exactly 24,575 characters
  and its `cut` names 24,575 (`test_s1_the_one_line_json_file_s_cut_names_24575_characters`). These tests read
  "its full length" as the length of the text today's item carries.
- **N-2. Characters, not bytes.** S1 and S2 say characters; the accented files hold a 4,500-character line (cut at
  4,000 characters, not 4,000 bytes) and a 3,000-character line of over 4,000 bytes (sent whole).
- **N-3. Expansions are cut too.** The ticket puts the cut in `item()`, which builds both an item sent alone and each
  piece of an expanded parent; S1 says "an evidence item". So an expanded parent over 4,000 characters (the survey's
  section, 11,220) is cut and carries `cut`.
- **N-4. The reranker's input** is read as the texts the reranker is sent (`candidate["text"]`, already cut at
  `RERANK_CHARS` with its `[path: …]` line, today). The stand-in reranker sees every request, over every page.
- **N-5. S3's reference is pinned.** `TODAY_BLOB` is integrate's `retrieve.py` at `fc61f303d467`. W2-116, W2-129 or
  W2-32 may also change `retrieve.py` in re-pin window 4. If one lands first and changes these planted bundles, S3
  goes red for a reason that is not this fix; then `TODAY_BLOB` moves to the new integrated blob by a test
  designer's revision, and what S3 compares is unchanged.

## Files

- `w2_135_support.py`: the planted repository, today's `retrieve.py` from git, the stand-in reranker, the oracle,
  S3's scenarios and the page walker.
- `conftest.py`: the session's planted repository, today's module, the stand-ins (autouse), `ask`.
- `test_w2_135_cut.py` (S1), `test_w2_135_under.py` (S2), `test_w2_135_unchanged.py` (S3).
