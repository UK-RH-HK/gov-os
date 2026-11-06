# W2-135 evidence: a bundle item over 4,000 characters is sent as its first 4,000, marked cut (DAEO-c4pb; DEC-1086 B, BUNDLE-BUDGET-1 (a))

**The cause.** A chunk is never shorter than one line (`chunking.chunk_text`). The 6,000-token budget governs parent
expansions only (`retrieve()`'s `used + cost <= limit`). So a one-line file goes out whole: a 24,575-character JSON
line was m29's first call, 8,886 tokens. 13 of 688 calls were over the budget, all from one-line items.

## The change

- **`src/gov/retrieval/retrieve.py`:**
  - a new constant, `ITEM_CHARS = 4000`;
  - `retrieve()`'s inner `item()`, where an evidence item's `text` is set: text over `ITEM_CHARS` characters is sent
    as its first 4,000 characters (not bytes), with `cut: {"chars": <full length>, "sent": 4000}`. `chars` is the
    length of the text the item carried before: its decoded span, its final newline included.
  - the pieces of an expanded parent go through `item()` too, so they are cut the same way.
- **What stays as it was:**
  - `path`, `start_line`, `end_line`, `id`, `chunk_id` and `sha256` stay those of the full span, so a citation still
    names the whole span, and `validate`'s checks (sha256 of the span; the text found in the span) still hold;
  - text at or under 4,000 characters is untouched and has no `cut` key;
  - the budget's `used` is still counted on the full text (from the candidates' and pieces' bodies, before `item()`);
  - the reranker reads `_rerank_text` from the candidates, not the item's text, so its input is unchanged;
  - `pool.without_nested` reads lines only, so which items it leaves out is unchanged.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: an item over 4,000 characters is sent as its first 4,000 with `cut: {"chars", "sent": 4000}`; its path, lines, id, chunk_id and sha256 (of the full span) unchanged | `item()` cuts the decoded text at 4,000 characters and adds `cut`; every other key is set from the full span as before | unit `tests/unit/retrieval/test_w2_135_item_cap.py`: `test_the_planted_files_are_what_the_cases_need`, `test_a_one_line_file_of_24575_characters_is_sent_as_its_first_4000_marked_cut`, `test_a_10631_character_markdown_line_sent_alone_is_cut`, `test_the_expanded_section_holding_the_long_line_is_cut_as_a_piece`, `test_an_expanded_section_of_short_lines_over_4000_is_cut`, `test_a_cut_item_still_validates_against_its_cited_lines`, `test_an_item_of_4001_characters_is_cut`; acceptance success-1 (21 passed) |
| S2: an item at or under 4,000 characters is sent as today, with no `cut` key | the cut applies only when `len(text) > 4000` | unit `test_an_item_of_exactly_4000_characters_is_sent_whole_with_no_cut_key`, `test_a_short_item_is_sent_whole_with_no_cut_key`; acceptance success-2 (4 passed) |
| S3: nothing else changes (items, order, batches, expansions and `left_out`, repeats, gaps, continuation, the budget's `used`); the reranker's input unchanged | the change touches only the `text` value and adds `cut`, after every count and choice is made | unit `test_the_bundle_is_the_same_before_and_after_but_for_the_cut_text_and_key` (twelve calls, field by field; the reranker's input recorded on both sides and equal; uncut items equal whole), `test_the_budget_s_used_is_still_counted_on_the_full_text`, `test_the_continuation_carries_on_the_same_before_and_after` (every page to the end); acceptance success-3 (23 passed) |
| S4: on integrate before re-pin window 4 is built; the window carries it | the CTO's check after the re-pin | not done here |

The planted repository (built in a temporary git repository, secret filter replaced, no vectors, no model, the
reranker a stand-in) holds:

- a one-line JSON file of 24,575 characters (one chunk, its own parent, sent alone);
- a Markdown file with a 10,631-character line: sent alone when the budget is too small to expand, inside its
  expanded section otherwise;
- a Markdown section of 70 short lines (5,720 characters), expanded from one of its chunks;
- items of exactly 4,000 and 4,001 characters, and a short one.

Accents before the 4,000th character make characters and bytes differ, so the tests show the cut is by characters.

The S3 tests compare against `retrieve.py` as it stood before the change, loaded from git at `e3355def9f99` (blob
`1fb6a75b10b9`, this branch's base). Where the history does not hold that commit, they skip and say so. On the before
side, the cut items' text is the whole span (24,575 characters and so on), which also shows the cause.

## Test results (through the heavy slot; HOME a scratch folder with only the user site-packages linked)

- **Unit, the new file:** `test_w2_135_item_cap.py`: 12 passed.
- **`gov accept W2-135`:** pass, 48/48. success-1 21/21, success-2 4/4, success-3 23/23; 0 unmapped, 0 skipped.
- **`tests/unit/retrieval` and `tests/acceptance/W2-32`** (`-m "not local_only" -k "not real and not green_here and not
  time_limit"`): 705 passed, 18 failed, 3 skipped, 1 xfailed, 322 deselected (the opt-in lists and the exclusion),
  in 18 min 51 s.
  - The 18 failures are all in `test_w2_112_shared_reranker.py`. Each is the launch sandbox refusing the shared
    reranker's Unix socket (`PermissionError: Operation not permitted`), the same 18 that W2-131 and W2-133 recorded.
    The file never reaches an item's text.
  - `test_the_socket_is_the_users_alone` was re-run alone and is red the same way (the socket never created).
  - The CTO's scoped run outside the sandbox settles them.
