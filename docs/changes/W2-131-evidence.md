# W2-131 evidence: a register chunk carries its own entry's id (DAEO-r8vq; DEC-1082 (2), DEC-1073, DEC-424)

The CTO's health check (2026-11-06) found register chunks of DEC-476, DEC-496, DEC-672, DEC-455 and DEC-487 each
labelled `"id": "DEC-999"`. The cause was in `retrieve.py`. `_graph()` built `record_of` as `{path: id}` over every
record, so the register's entries, which share one path, left one id: the last by `records.records()`'s text order
(DEC-999). `item()` then labelled every register item `record_of.get(rel, chunk_id)`.

## The change (`src/gov/retrieval/retrieve.py`, three places)

- **`_graph()`:** `record_of` leaves out records that carry a span (the register's entries), as
  `supplementary.py:78` does. No one entry stands for the register's path. `not_current` and `record_types` still
  hold every record.
- **`item()`:** a register item with entries takes its first entry as its `id`, the same entry its `entry` key
  (W2-92 S9) names, so the two always agree. A register item with no entry (the preface, a section between entries)
  keeps its chunk id, as `supplementary.py:95` does (`entry['id'] if entry else chunk_id`). Under the register's
  chunking (Markdown sections cut at headings; M5's entry chunks), a chunk or parent never starts outside an entry
  and runs into one. So "the entry that holds its first line" (a chunk) and "its first entry" (a parent expansion)
  are the same entry as `entry`.
- **The DEC-423 front-matter check:** it now skips the register (`record_id is None and not in_register`). Before,
  the register's path mapped to DEC-999, so the check never ran on it. Without that skip, the new map would have read
  the register's front matter for every register chunk. The skip keeps the drops exactly as they were (S3).

Nothing else changes. Which evidence is gathered, its order, the batches, the budget, the gaps and the continuation
all come from the routes, the fusion and the ranking. The map only fed them for the register's path through DEC-424's
ahead paths. There it could only lift the whole register if the last entry by id were a failure or lesson. It is now
never lifted by one entry's type, which is S2's intent. `measure.py` scores by path and line span, so no recorded
figure changes.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: every register item carries the entry holding its first line (DEC-476's chunk is DEC-476); a preface or between-entries chunk its chunk id; a parent expansion its first entry's id; `id` and `entry` agree | `item()` sets `id` to the first entry of the item's lines (`entries_in`), the same entry as the `entry` key; none: the chunk id | unit `test_w2_131_register_ids.py`: `test_the_planted_store_holds_three_entries_and_dec_999_sorts_last`, `test_a_chunk_inside_dec_476_is_labelled_dec_476`, `test_a_chunk_in_the_preface_carries_its_chunk_id`, `test_a_chunk_between_entries_carries_its_chunk_id`, `test_a_parent_expansion_carries_its_first_entry_s_id`, `test_every_register_item_s_id_agrees_with_its_entry_key`, `test_a_record_file_keeps_its_own_id`; acceptance success-1 (15 passed) |
| S2: the path-to-record map holds no register entry for the register's path; DEC-424's move still lifts a failure or lesson record | `_graph()` leaves out records with a span | unit `test_the_path_map_holds_no_register_entry`, `test_dec_424_still_lifts_a_lesson_in_the_ticket_s_closure` (a lesson reached only by the ticket's closure is first with the move, not first without it); acceptance success-2 (3 passed) |
| S3: nothing else in a bundle changes; only register items' ids | the change touches only the map and the label | unit `test_the_bundle_is_the_same_before_and_after_but_for_register_ids` (nine calls, field by field), `test_the_continuation_carries_on_the_same_before_and_after`; acceptance success-3 (11 passed) |
| S4: on integrate before re-pin window 4; a live search after it labels each register chunk by its own entry | the CTO's, after the re-pin | not done here |

The S3 tests compare against `retrieve.py` as it stood before the fix, loaded from git at `72cf8df13a04` (this
branch's base). The comparison covers nine calls: single queries, a ticket closure with DEC-424's move, an id closure,
`batch_size=1` with paging, and a 200-token budget. Every key but `evidence` is equal; every evidence item is equal
but for `id`. A non-register item keeps its id. Every register item was `DEC-999` before and is its own entry (or
chunk id) after. Where the history does not hold that commit, the two tests skip and say so.

## Test results (through the heavy slot; HOME an empty folder with only the user site-packages linked)

- **Unit:** `tests/unit/retrieval/test_w2_131_register_ids.py`, 11 passed.
- **`gov accept W2-131`:** pass, 29/29. success-1 15/15, success-2 3/3, success-3 11/11; 0 unmapped, 0 skipped.
- **`tests/unit/retrieval`** (`-m "not local_only" -k "not real and not green_here and not time_limit"`): 383 passed,
  18 failed, 292 deselected (the opt-in lists and the exclusion).
  - The 18 failures are all in `test_w2_112_shared_reranker.py`. Each one is `PermissionError: Operation not
    permitted` on the shared reranker's Unix socket: the launch sandbox refuses it. The file never calls
    `retrieve()`'s register path. `test_the_socket_is_the_users_alone` was re-run alone, and is red the same way.
  - These were not caused by this change. The CTO's scoped run outside the sandbox settles them.
