# W2-135 evidence: a line over 4,000 characters in a bundle item is sent as its first 4,000, the item marked cut (DAEO-c4pb; DEC-1086 B, BUNDLE-BUDGET-1 (a))

**The cause.** A chunk is never shorter than one line (`chunking.chunk_text`). The 6,000-token budget governs parent
expansions only (`retrieve()`'s `used + cost <= limit`). So a one-line file goes out whole: a 24,575-character JSON
line was m29's first call, 8,886 tokens. 13 of 688 calls were over the budget, all from one-line items.

**Round 2 (DEC-1086 B, "a guard against one-line files only"; the review's F1 and F2).** Round 1 cut any item over
4,000 characters, so an expanded section of ordinary lines lost its tail, and with it, in the review's probe, the hit
line (F1). Round 2 cuts lines, not items. A narrowed register item also kept its parent's stale `cut` key (F2).

## The change

- **`src/gov/retrieval/retrieve.py`:**
  - the constant `ITEM_CHARS = 4000`;
  - a new function, `capped(body, first)`: the text sent for a span starting at line `first`, and its `cut` key.
    - A line is measured without its newline. A line over 4,000 characters (not bytes) is sent as its first 4,000,
      and keeps its newline (`\n`, `\r\n` or `\r`).
    - Every other line is sent whole, so an item of ordinary lines is never cut, however long it is.
    - Where a line is cut, the key is `cut: {"chars": <the full text's length>, "sent": <the length sent>, "lines":
      [<the cut lines' numbers in the file>]}`. Where none is, there is no key.
    - The lines are the file's, as the item's body is built (`bytes.splitlines`).
  - `retrieve()`'s inner `item()`, where an evidence item's `text` is set, calls `capped`. The pieces of an expanded
    parent go through `item()` too, so only their long lines are cut.
- **`src/gov/decisions/register.py`, `leave_out`'s `narrowed()` (F2):** the parent's `cut` key is never kept. The
  narrowed chunk's text goes through `capped`, so it carries a `cut` key only where its own lines hold a cut line,
  with its own figures.
- **What stays as it was:**
  - `path`, `start_line`, `end_line`, `id`, `chunk_id` and `sha256` stay those of the full span, so a citation still
    names the whole span;
  - an item with no line over 4,000 characters is untouched and has no `cut` key;
  - the budget's `used` is still counted on the full text (from the candidates' and pieces' bodies, before `item()`);
  - the reranker reads `_rerank_text` from the candidates, not the item's text, so its input is unchanged;
  - `pool.without_nested` reads lines only, so which items it leaves out is unchanged.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: each line over 4,000 characters sent as its first 4,000, every other line whole; an item with a cut line carries `cut: {"chars", "sent", "lines"}`; its path, lines, id, chunk_id and sha256 (of the full span) unchanged | `capped()` cuts each long line (measured without its newline, the newline kept) and builds the key; `item()` sets every other key from the full span as before | unit `tests/unit/retrieval/test_w2_135_item_cap.py`: `test_the_planted_files_are_what_the_cases_need`, `test_capped_measures_a_line_without_its_newline_and_keeps_the_newline`, `test_capped_names_every_cut_line_by_its_number_in_the_file`, `test_a_one_line_file_of_24575_characters_is_sent_as_its_first_4000_marked_cut`, `test_a_10631_character_markdown_line_sent_alone_is_cut`, `test_in_the_expanded_section_only_the_long_line_is_cut_its_neighbours_whole`, `test_a_line_of_4001_characters_is_cut_and_keeps_its_newline`, `test_a_cut_item_s_sha256_still_matches_its_cited_lines`; acceptance success-1 (33 passed) |
| S2: an item with no line over 4,000 characters sent as today, with no `cut` key, whatever its length; a narrowed register item carries a `cut` key only if its own lines hold a cut line | `capped()` returns the decoded span unchanged and no key where no line is over the cap; `narrowed()` drops the parent's key and calls `capped()` on its own lines | unit `test_an_expanded_section_of_11000_characters_of_ordinary_lines_is_sent_whole` (its hit word past character 4,000 is sent: F1), `test_a_line_of_exactly_4000_characters_and_its_newline_is_sent_whole`, `test_a_short_item_is_sent_whole_with_no_cut_key`, `test_a_register_item_narrowed_to_ordinary_lines_drops_its_parent_s_cut_key`, `test_a_register_item_narrowed_to_its_long_line_carries_a_cut_of_its_own` (equal to `retrieve`'s item for that chunk sent alone); acceptance success-2 (11 passed) |
| S3: nothing else changes (items, order, batches, expansions and `left_out`, repeats, gaps, continuation, the budget's `used`); the reranker's input unchanged | the change touches only the `text` value and adds `cut`, after every count and choice is made | unit `test_the_bundle_is_the_same_before_and_after_but_for_the_cut_lines_and_key` (twelve calls, field by field against the code before W2-135; the reranker's input recorded on both sides and equal; uncut items equal whole, long sections of ordinary lines among them), `test_the_budget_s_used_is_still_counted_on_the_full_text`, `test_the_continuation_carries_on_the_same_before_and_after` (every page to the end); acceptance success-3 (39 passed) |
| S4: on integrate before re-pin window 4 is built; the window carries it | the CTO's check after the re-pin | not done here |

The planted repository (built in a temporary git repository, secret filter replaced, no vectors, no model, the
reranker a stand-in) holds:

- a one-line JSON file of 24,575 characters (one chunk, its own parent, sent alone);
- a Markdown file with a 10,631-character line among ordinary lines: sent alone when the budget is too small to
  expand, inside its expanded section otherwise (only that line cut, its neighbours whole);
- a Markdown section of 136 ordinary lines (over 11,000 characters), expanded from one of its chunks, its one rare word
  past character 4,000: sent whole, with no `cut` key;
- one-line files with a line of exactly 4,000 and of 4,001 characters (each with its newline), and a short file.

A second planted repository holds a Markdown register (DEC-100 superseded by DEC-101, DEC-101 holding one line of
4,500 characters). Planted parents over both entries carry a cut key, as `retrieve` would send them, and go through
`register.leave_out`.

Accents before the 4,000th character make characters and bytes differ, so the tests show the cut is by characters.

The S3 tests compare against `retrieve.py` as it stood before the change, loaded from git at `e3355def9f99` (blob
`1fb6a75b10b9`). Where the history does not hold that commit, they skip and say so.

**A known row, wider than the ticket's notes say (not this ticket's paths):** `src/gov/retrieval/validate.py` checks
that the item's text is found in the cited span. A cut line keeps its newline, so every item with a cut line followed
by a newline gets `TEXT_NOT_FOUND`, not only one with a cut line in its middle. The sha256 check still holds. No product
code calls `validate` on a real bundle (the ticket's notes). The unit test pins that only that code, and only on a cut
item, is raised.

## Test results (through the heavy slot; HOME a scratch folder with only the user site linked)

- **Unit, the revised file:** `test_w2_135_item_cap.py`: 16 passed.
- **`gov accept W2-135`:** pass, 83/83. success-1 33/33, success-2 11/11, success-3 39/39; 0 unmapped, 0 skipped.
- **`tests/unit/retrieval`, `tests/unit/decisions`, `tests/acceptance/W2-32` and `tests/acceptance/W2-133`**
  (`-m "not local_only" -k "not real and not green_here and not time_limit"`): 794 passed, 18 failed, 3 skipped,
  1 xfailed, 333 deselected (the opt-in lists and the exclusion), in 17 min 0 s.
  - W2-133's 48 acceptance cases and its unit cases pass with the line cut and `narrowed()`'s change (the review's F3
    answered).
  - The 18 failures are all in `test_w2_112_shared_reranker.py`: the launch sandbox refuses the shared reranker's Unix
    socket (`PermissionError: [Errno 1] Operation not permitted`), so the service never listens and each search falls
    back. They are the same 18 as round 1, W2-131 and W2-133. The file never reaches an item's text. The CTO runs them
    outside the sandbox.
  - The three skips: two W2-32 record cases with no baseline measure record under the scratch HOME, and one W2-32
    fusion case whose limit above the cap does not arise.
