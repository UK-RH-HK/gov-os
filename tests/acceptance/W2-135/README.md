# W2-135 acceptance tests: a line over 4,000 characters in a bundle item is sent as its first 4,000, the item marked cut

Ticket DAEO-c4pb (W2-135), profile STANDARD, BUNDLE-BUDGET-1 option (a) (DEC-1086 B, "a guard against one-line files
only"; DEC-1087 (1)). Written by the independent test designer (MR-3) from the ticket's KPI lines S1 to S3, before
any implementation, reading only the integrated code. **Round 2** (the CTO, 2026-11-06; the review's F1 and F2): S1
and S2 were re-worded to cut lines, not items, and `register.py` joined the ticket's paths; these tests were revised
to the new wording on `w2/integrate` `33a8b77db663`. S4 is the CTO's check after the re-pin, not a test here.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-135 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

(`PYTHONUSERBASE`, or a `HOME` whose `.local/lib` links to the user's site, only where pytest is installed there.)
About 1.3 s, in process. The tests use the tree `PYTHONPATH` names; without one, the worktree's own `src`.

- **The planted repository** (`w2_135_support.build`, once per session): a temporary git repository with
  `data/ledger.json`, one line of 24,575 characters and no newline at its end (valid JSON); `docs/survey.md`, a
  section of ordinary lines holding one line of 10,631 characters (line 9), then a section `## Almanac` of 44
  ordinary lines; `docs/logbook.md`, one section of 131 ordinary lines (10,991 characters), the word `gannet` on line
  90, past character 4,000; `notes/candle.txt`, a first line of exactly 4,000 characters and its newline, then a short
  line; `notes/lantern.txt` (exactly 4,000 characters) and `notes/beacon.txt` (4,001), one line each, no newline at
  the end; `notes/brioche.txt` (4,500 accented characters, about 6,900 bytes) and `notes/meringue.txt` (3,000
  accented characters, over 4,000 bytes); and an ordinary note.
- **The register's repository** (`w2_135_support.build_register`, the review's F2): a path map naming
  `docs/DECISION_REGISTER.txt`, a plain-text register of 41 lines: a preface, DEC-100 (SUPERSEDED by DEC-101) and
  DEC-101, whose clause 6 (line 17) is one line of 5,200 characters and whose clause 24 (line 35) holds `marjoram`.
  A register that is not Markdown is one parent, the whole file, so the parent expanded around a hit spans DEC-100,
  and `gov retrieve`'s `leave_out` narrows it to the hit's own chunk (W2-133's mechanism): `samphire` narrows to line
  17 alone, `marjoram` to lines 29-41, clear of line 17.
- Each repository's lexical index and record store are built in the temporary folder, the secret filter replaced
  (as the unit tests do). Never this repository's store.
- **One question, one span:** `zephyrine` reaches the JSON file alone; `quillwort` the long line alone, which at the
  default budget is expanded to its section (lines 1-14, 11,220 characters) and at `bundle_budget=1` is sent alone
  (line 9, 10,632 characters with its newline); `gannet` the logbook's section, expanded; `candlewick` the candle's
  first line, expanded to both lines at the default budget and alone at `bundle_budget=1`; `beacon`, `brioche`,
  `lantern`, `meringue` and `kestrel` their own files; `harbour` every file of the first repository but the logbook
  and the candle; `tide almanac` the almanac section; on the register's repository `samphire`, `marjoram`, `wicker`
  (DEC-100, left out whole) and `quay` (every chunk).
- **Two pipelines:** `ask(..., repo="register", pipeline=True)` is `gov retrieve`'s (`retrieve`, then the register's
  `leave_out`, its record kept as `left_out`, as `gov.retrieve.command.run` does); every other call is `retrieve`
  alone.
- **No embedder, reranker or model:** the semantic route is a stand-in with no hit, the file route off; every call
  is given a stand-in reranker (`w2_135_support.Scorer`) that keeps each text it is sent (the reranker's input) and
  scores it by a hash of the text. No question names a symbol or a record, so neither the code route nor a closure
  is asked. `GOV_ROLE` and `GOV_TICKET` are cleared.
- **The oracle** (`w2_135_support.span_text`, `span_bytes`, `cut`, `sent_text`, `cut_key`): an item's full text, its
  bytes, the text S1 says is sent and the `cut` key it says the item carries, all read from the planted files alone,
  never from the code under test.
- **"Today" for the guards, S2 and S3** (`w2_135_support.today`, `today_register`): `src/gov/retrieval/retrieve.py`
  (blob `1fb6a75b10b9`) and `src/gov/decisions/register.py` (blob `491959f05271`) as `w2/integrate` `e3355def9f99`
  held them; integrate's head `33a8b77db663` holds the same two blobs. Each is read from git and loaded as a module of
  its own beside the running tree's. They are the ticket's only source paths, so the two differ by the fix alone;
  both are asked on the same stores, in the same process, with the same stand-ins.
- **S3's comparison** takes off only the cut lines' text and the cut key: an item's text must be today's line for
  line, each line either today's whole or, where today's line is over 4,000 characters, its first 4,000 and its
  newline. Every other item field, the items' order and cited lines (path, lines, chunk id, sha256), and every other
  bundle key (`budget` with its `used`, `batches`, `expansions` with `left_out`, `repeats`, `gaps`, `continuation`,
  `merge`, `facets`, `stopping_reason`, `rerank`, and the register's `left_out`) must equal today's, on every page
  of each batched question followed through its continuations, through both pipelines. The reranker's input is the
  list of texts the stand-in reranker is sent, over all pages, compared with today's.
- **S3's premise** (`test_s3_premise_the_scenarios_hold_what_s3_names`) shows on today's code that the nineteen
  scenarios hold an expansion with a left-out span, repeats of both kinds, not-gathered gaps, continuations, a second
  batch, a register entry left out, items with a line over the cap both alone and inside an expansion, an expansion
  of ordinary lines over 10,000 characters, and one call (`zephyrine quillwort`) where today's `used` (8,802, on the
  full text) is over the 6,000 limit, so the survey's section is not expanded, while a `used` counted on the cut
  text would let it expand: a fix that counts the cut text fails S3 there.

## KPI lines, tests, and the outcome on `w2/integrate` `33a8b77db663`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **83 tests, 16 failed, 67 passed** (1.26 s). Every red is an S1 case and
fails because the item is sent whole or carries no `cut` key, none on a premise. Every green is a premise or a guard:
it holds today and fails a fix that cuts more than S1 says, or changes anything else. `gov accept W2-135` reads this
map: S1 17 passed and 16 failed, S2 11 passed, S3 39 passed, none unmapped (outcome `fail`, exit 3).

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[json-one-line-24575]` | green (premise) | the span holds a line over 4,000; today's item is it whole, no `cut` |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[markdown-long-line-alone]` | green (premise) | line 9 alone, 10,632 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[markdown-section-expanded]` | green (premise) | the expanded section 1-14, 11,220 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[one-over-the-cap-4001]` | green (premise) | 4,001 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[accented-4500-characters]` | green (premise) | 4,500 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[register-parent-retrieve-alone]` | green (premise) | the register's parent, lines 1-41, 7,995 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_premise_today_sends_the_item_whole[register-narrowed-to-the-long-clause]` | green (premise) | the item narrowed to line 17, 5,201 characters, sent whole today |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[json-one-line-24575]` | red | sent as 24,575 characters; S1 sends 4,000 |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[markdown-long-line-alone]` | red | sent as 10,632; S1 sends the line's first 4,000 and its newline, 4,001 |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[markdown-section-expanded]` | red | sent as 11,220; S1 sends 4,589 (line 9 cut, lines 1-8 and 10-14 whole) |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[one-over-the-cap-4001]` | red | sent as 4,001; S1 sends 4,000 |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[accented-4500-characters]` | red | sent as 4,500 characters; S1 sends 4,000 (a cut by bytes would also fail it) |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[register-parent-retrieve-alone]` | red | sent as 7,995; S1 sends 6,795 (line 17 cut, the other 40 lines whole) |
| S1 | `test_w2_135_cut.py::test_s1_each_line_over_4000_is_its_first_4000_and_every_other_line_whole[register-narrowed-to-the-long-clause]` | red | through `gov retrieve`, the narrowed item is sent as 5,201; S1 sends 4,001 |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[json-one-line-24575]` | red | no `cut` key; expected `{"chars": 24575, "sent": 4000, "lines": [1]}` |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[markdown-long-line-alone]` | red | no `cut` key; expected `{"chars": 10632, "sent": 4001, "lines": [9]}` |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[markdown-section-expanded]` | red | no `cut` key; expected `{"chars": 11220, "sent": 4589, "lines": [9]}` |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[one-over-the-cap-4001]` | red | no `cut` key; expected `{"chars": 4001, "sent": 4000, "lines": [1]}` |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[accented-4500-characters]` | red | no `cut` key; expected `{"chars": 4500, "sent": 4000, "lines": [1]}` |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[register-parent-retrieve-alone]` | red | no `cut` key; expected `{"chars": 7995, "sent": 6795, "lines": [17]}` |
| S1 | `test_w2_135_cut.py::test_s1_the_item_with_a_cut_line_carries_its_cut_key[register-narrowed-to-the-long-clause]` | red | no `cut` key; expected the narrowed item's own `{"chars": 5201, "sent": 4001, "lines": [17]}`, never its parent's |
| S1 | `test_w2_135_cut.py::test_s1_the_one_line_json_file_s_cut_names_24575_characters` | red | the ticket's number, written out: no `cut` key today |
| S1 | `test_w2_135_cut.py::test_s1_the_long_markdown_line_alone_keeps_its_newline` | red | line 9 alone is sent whole today; S1 sends its first 4,000 characters and its newline |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_long_line_s_neighbours_are_sent_whole_in_their_own_lines[markdown-section-expanded]` | green (guard) | lines 1-8 and 10-14 are sent whole, each a line of its own; a cut of the item at a character count fails it |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_long_line_s_neighbours_are_sent_whole_in_their_own_lines[register-parent-retrieve-alone]` | green (guard) | as above, the register's 40 other lines |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[json-one-line-24575]` | green (guard) | path, start_line, end_line, id, chunk_id and sha256 are today's; the sha256 is of the full span's bytes |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[markdown-long-line-alone]` | green (guard) | as above |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[markdown-section-expanded]` | green (guard) | as above, for an expansion |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[one-over-the-cap-4001]` | green (guard) | as above |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[accented-4500-characters]` | green (guard) | as above |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[register-parent-retrieve-alone]` | green (guard) | as above, for the register's parent |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_cited_fields_are_today_s_and_the_sha256_is_of_the_full_span[register-narrowed-to-the-long-clause]` | green (guard) | as above, for a narrowed item |
| S1 | `test_w2_135_cut.py::test_s1_guard_the_word_asked_for_past_character_4000_of_an_ordinary_section_is_sent` | green (guard) | the review's F1 probe: `gannet`, past character 4,000 of the logbook's expanded section, is in the text sent |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[exactly-the-cap-4000]` | green (guard) | exactly 4,000 characters: whole, no `cut`, every field today's |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[accented-3000-characters-over-4000-bytes]` | green (guard) | 3,000 characters but over 4,000 bytes: whole (the cap counts characters) |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[ordinary-note]` | green (guard) | two ordinary items: as today |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[ordinary-section-expanded-about-11000]` | green (guard) | the logbook's section, 10,991 characters of ordinary lines: whole, no `cut` (whatever its total length) |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[line-of-4000-and-its-newline-expanded]` | green (guard) | the candle's two lines (4,044 characters), its first line exactly 4,000 and its newline: whole, no `cut` |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[line-of-4000-and-its-newline-alone]` | green (guard) | the candle's first line alone, 4,001 characters with its newline: whole, no `cut` (N-1) |
| S2 | `test_w2_135_under.py::test_s2_an_item_with_no_line_over_4000_is_sent_as_today_with_no_cut_key[register-narrowed-without-the-long-clause]` | green (guard) | through `gov retrieve`, the item narrowed to lines 29-41: as today, no `cut` |
| S2 | `test_w2_135_under.py::test_s2_premise_the_long_cases_are_long` | green (premise) | today the logbook's section is one item over 10,500 characters, the candle's two lines one item over 4,001 |
| S2 | `test_w2_135_under.py::test_s2_premise_the_narrowed_item_s_parent_holds_the_long_clause` | green (premise) | today `marjoram`'s parent is lines 1-41 (holding line 17), narrowed by `leave_out` to lines 29-41 |
| S2 | `test_w2_135_under.py::test_s2_a_narrowed_register_item_carries_no_cut_key_unless_its_own_lines_hold_a_cut_line` | green (guard) | the review's F2: the narrowed item carries no `cut` key, whatever its parent's, and its own lines whole |
| S2 | `test_w2_135_under.py::test_s2_every_item_with_no_line_over_the_cap_in_every_scenario_is_today_s` | green (guard) | every item with no line over 4,000 on every page of S3's nineteen scenarios equals today's, field by field |
| S3 | `test_w2_135_unchanged.py::test_s3_premise_the_scenarios_hold_what_s3_names` | green (premise) | the scenarios hold what S3 names (see above), on today's code |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[json-alone]` | green (guard) | the running tree is today's code; any change beside the cut lines and the cut key fails it |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[long-line-alone]` | green (guard) | as above; `used` over a limit of 1 |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[long-line-section-expanded]` | green (guard) | as above; an expansion holding a line over the cap |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[json-beside-the-long-line]` | green (guard) | as above; `used` 8,802 over 6,000, no expansion (a count on the cut text would expand) |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[edges]` | green (guard) | as above; the four files at the cap's edge |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[every-file]` | green (guard) | as above; two batches |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[every-file-budget-12000]` | green (guard) | as above; `used` over 12,000 (on the cut text it would be under) |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[every-file-expanded]` | green (guard) | as above; two expansions, one holding a line over the cap |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[almanac-batched]` | green (guard) | as above; a continuation, gaps, repeats `SENT_IN_AN_EARLIER_PARENT` |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[every-file-batched]` | green (guard) | as above; many pages, gaps, repeats |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[almanac-batched-budget-1000]` | green (guard) | as above; an expansion with `left_out` and repeats `SENT_EARLIER_AS_A_CHILD` |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[logbook-section-expanded]` | green (guard) | as above; an expansion of 10,991 characters of ordinary lines |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[candle-expanded]` | green (guard) | as above; a line of exactly 4,000 and its newline, expanded |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[candle-alone]` | green (guard) | as above, alone |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[register-long-clause-retrieve-alone]` | green (guard) | as above; the register's parent through `retrieve` alone |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[register-long-clause-gov-retrieve]` | green (guard) | as above, through `gov retrieve`: narrowed to line 17, `left_out` DEC-100 |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[register-marjoram-gov-retrieve]` | green (guard) | as above; narrowed to lines 29-41 |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[register-dec-100-gov-retrieve]` | green (guard) | as above; the item touching DEC-100 left out whole |
| S3 | `test_w2_135_unchanged.py::test_s3_the_bundles_are_today_s_but_for_the_cut_lines_and_cut_key[register-every-chunk-batched-gov-retrieve]` | green (guard) | as above; every chunk, batched, through its continuations |
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
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[logbook-section-expanded]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[candle-expanded]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[candle-alone]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[register-long-clause-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[register-long-clause-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[register-marjoram-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[register-dec-100-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_135_unchanged.py::test_s3_the_reranker_s_input_is_today_s[register-every-chunk-batched-gov-retrieve]` | green (guard) | as above, over every page |

**A check of the tests themselves** (scratch copies of `src` in the sandbox's TMPDIR, never committed):

- **A, S1 and S2 as worded:** `item()` and `register.leave_out`'s `narrowed()` each send every line over 4,000
  characters (newline not counted) as its first 4,000 and its newline, and set `cut: {"chars", "sent", "lines"}`
  only when a line was cut; `narrowed()` drops the parent's `cut` before it. **83 passed.**
- **B, round 1 (the whole item cut at 4,000 characters, `{"chars", "sent": 4000}`, `register.py` unchanged): 33
  failed** (the line tests, the cut keys, the neighbours, `gannet`, the logbook's section, both candle cases, the
  narrowed item's stale key, S2's sweep, and S3 on 11 scenarios).
- **C, A with the budget's `used` counted on the cut text: 15 failed** (S3 on 14 scenarios, `budget` changed, and
  S2's sweep).
- **D, A in `retrieve.py` only, `register.py` unchanged (F2 left as it was): 5 failed** (the narrowed item on line
  17 not cut and carrying its parent's key; the narrowed item on lines 29-41 carrying its parent's key, three ways).

## Notes and limits

- **N-1. A line's length is counted without its newline, and a cut line keeps its newline.** S1 says "each line over
  4,000 characters is sent as its first 4,000 characters" and "every other line of the item is sent whole"; these
  tests read a line as its characters before the line break, the way an editor counts it, and keep the break, so
  the line after a cut line is still a line of its own. So the survey's line 9 (10,631 characters) is sent as its
  first 4,000 and its newline: alone, 4,001 characters (`cut: {"chars": 10632, "sent": 4001, "lines": [9]}`). The
  candle's first line, exactly 4,000 characters and its newline, is not over the cap and is sent whole. `chars` is
  the item's full text length (newline included), `sent` the length of the text sent, `lines` the file's line
  numbers of the cut lines, in order. The JSON file has no newline at its end, so its item is 24,575 characters and
  is sent as 4,000 (`test_s1_the_one_line_json_file_s_cut_names_24575_characters`).
- **N-2. Characters, not bytes.** The accented files hold a 4,500-character line (cut at 4,000 characters, not 4,000
  bytes) and a 3,000-character line of over 4,000 bytes (sent whole).
- **N-3. Expanded items are cut by line too.** `item()` builds both an item sent alone and each piece of an expanded
  parent, and S1 says "an evidence item", so the survey's expanded section is sent with line 9 cut and its other 13
  lines whole; the logbook's section, about 11,000 characters of ordinary lines, is sent whole with no `cut` key.
- **N-4. The reranker's input** is read as the texts the reranker is sent (`candidate["text"]`, already cut at
  `RERANK_CHARS` with its `[path: …]` line, today). The stand-in reranker sees every request, over every page.
- **N-5. S3's reference is pinned.** `TODAY_BLOBS` are integrate's `retrieve.py` (`1fb6a75b10b9`) and `register.py`
  (`491959f05271`) at `e3355def9f99`, the merge of W2-32 S11; integrate's head at round 2, `33a8b77db663`, holds the
  same two. S11's five `pool:` settings are absent in the planted repositories (no `retrieval.yaml`), so each is 0
  and the path is the earlier one. W2-116 or W2-129 may still change `retrieve.py` in re-pin window 4; if one lands
  first and changes these planted bundles, `TODAY_BLOBS` moves again the same way, and what S3 compares is unchanged.
- **N-6. A narrowed item exists only through `gov retrieve`, and only with a register that is not Markdown.** A
  Markdown register is cut at every heading, so no parent spans two entries (the review's F2); the planted `.txt`
  register reaches it, as W2-133's tests do.

## Files

- `w2_135_support.py`: the two planted repositories, today's `retrieve.py` and `register.py` from git, the stand-in
  reranker, the oracle, S3's scenarios and the page walker.
- `conftest.py`: the session's planted repositories, today's modules, the stand-ins (autouse), `ask`.
- `test_w2_135_cut.py` (S1), `test_w2_135_under.py` (S2), `test_w2_135_unchanged.py` (S3).

- **D-10 run 2 (W2-138 `dcda27011`, DEC-1090 (3); DEC-1122 (3)):** `test_w2_135_unchanged.py` compares the continuation token decoded without its `s` key (the store's commit); the running tree's token must name a full commit, the same on every page, today's none, and every other key is still compared.
