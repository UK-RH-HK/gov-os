# W2-133 evidence: a narrowed or gap-starting register item carries its own entry's id (DAEO-k4wm; DEC-1083, DEC-1082 (2), DEC-1073)

W2-131's independent review (2026-11-06) found two cases its fix did not reach:

- **`register.leave_out` kept the parent's label.** When an expanded register parent touches a superseded or done
  entry, `leave_out` narrows it to its own chunk. The kept item was `{**item, start_line, end_line, sha256, text}`,
  so the parent's `id`, `entry`, `status`, `in_force` and `also` survived, even where the narrowed chunk holds a
  different entry.
- **`retrieve()`'s label took the first entry touched.** `item()` labelled a register item by the first entry its
  lines touch. An item that starts in the preface or a gap therefore took a later entry's id, where W2-131's S1 says
  its chunk id.

## The change

- **`src/gov/retrieval/retrieve.py`, `item()`'s register label only:**
  - the `id` is the entry holding the item's **first line**, by `entry_of` (`authority.register_entries_of`), with
    that entry's mark (`entry`, `status`, `changed_by`, `in_force`, `not_in_force`);
  - a first line in the preface or a gap keeps the chunk id and carries no mark of its own;
  - every other entry the item's lines touch is named in `also`, as before. For a gap starter, that is every entry it
    touches, so DEC-476's status still travels with an item that holds DEC-476's text.
  - Where the first line lies in an entry, the label is exactly what it was (the first entry touched is the entry
    holding the first line).
- **`src/gov/decisions/register.py`, `leave_out`:** a narrowed item is relabelled from the narrowed chunk's own lines,
  by the same rule, through a new inner `narrowed()`:
  - the parent's `entry`, `status`, `changed_by`, `in_force`, `not_in_force` and `also` are dropped, never kept;
  - `id` is the entry holding the chunk's first line, or the chunk id in the preface or a gap;
  - each entry's mark is taken from the parent's own marks (its own and its `also`), which `retrieve` computed. The
    narrowed chunk lies inside the parent, so every entry it touches is among them; no status is recomputed or
    guessed in `register.py`;
  - an item that carries no marks (as `supplementary`'s items are) gets its `id` only, and no mark is invented.
  - `id` keeps its place in the item; every other key is untouched.

Which items are kept, narrowed or left out, their lines, hashes, texts and order, and the `left_out` record are
unchanged: the change only rewrites the label of an item that is already kept.

**Today's chunker never yields a gap starter that reaches an entry.** It cuts the register at every level 1-3 heading
(`chunking.register_sections`), and an entry starts at its `### DEC-` heading. So no chunk or parent starts in a gap
and runs into an entry, and no parent spans two entries. The fix is defensive for both paths. The unit tests plant
those parents: a stood-in `lexical.parent` on the retrieval side, planted parent items on the `leave_out` side.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: a narrowed register item's `id`, `entry`, `status`, `in_force` and `also` are the narrowed chunk's, from its own lines, never the parent's (a parent over a superseded DEC-100 then DEC-101 narrows to DEC-101's chunk, labelled DEC-101) | `leave_out`'s `narrowed()` drops the parent's label and relabels from the chunk's first line, with marks from the parent's own per-entry marks | unit `tests/unit/decisions/test_w2_133_narrowed_label.py`: `test_a_parent_over_superseded_dec_100_then_dec_101_narrows_to_dec_101_s_own_label`, `test_a_parent_whose_first_entry_is_done_narrows_to_the_next_entry_with_its_changers`, `test_a_narrowed_chunk_in_a_gap_carries_its_chunk_id_and_no_entry`, `test_the_narrowed_label_is_the_label_retrieve_gives_the_same_chunk`, `test_an_item_without_entry_marks_takes_its_chunk_s_id_and_gains_no_mark`, `test_an_item_that_touches_no_left_out_entry_is_kept_as_it_is`; acceptance success-1 (13 passed) |
| S2: an item whose first line lies in the preface or a gap carries its chunk id, not the first entry it touches further down; one whose first line lies inside an entry carries that entry | `item()` labels by `entry_of(rel, first)`; none: the chunk id, the touched entries in `also` | unit `tests/unit/retrieval/test_w2_133_gap_label.py`: `test_the_planted_parents_are_what_the_cases_need`, `test_an_item_starting_in_a_gap_before_dec_476_carries_its_chunk_id`, `test_an_item_starting_inside_dec_476_carries_dec_476`, `test_a_parent_starting_inside_dec_476_over_dec_999_carries_dec_476_and_names_dec_999`, `test_a_preface_item_carries_its_chunk_id_and_no_mark`, `test_every_register_item_s_id_agrees_with_its_entry_key`; acceptance success-2 (6 passed) |
| S3: nothing else in a bundle changes (evidence set, order, batches, budget, gaps, `left_out`, continuation) but for S1's and S2's ids and status fields | the change only rewrites the label keys of items already kept | unit `test_the_bundle_is_the_same_before_and_after_but_for_a_gap_starter_s_label` (ten calls, field by field; an item inside an entry is equal whole), `test_the_continuation_carries_on_the_same_before_and_after`, `test_leave_out_keeps_the_same_items_in_the_same_order_but_for_the_label` (six items, kept, narrowed and left out; `left_out` equal); acceptance success-3 (29 passed) |
| S4: on integrate before re-pin window 4 is built; the window carries it with W2-131 | the CTO's, after the re-pin | not done here |

The S3 tests compare against `retrieve.py` and `register.py` as they stood before the fix, loaded from git at
`c59e6cd84f9b` (this branch's base: integrate with the acceptance cases). Where the history does not hold that commit,
they skip and say so. The before side also shows the cause:

- before, a gap starter is labelled `DEC-476`;
- before, a narrowed parent keeps `DEC-100` or `DEC-102`.

W2-131's own unit tests still pass unchanged, so its S1 to S3 still hold.

## Test results (through the heavy slot; HOME an empty folder with only the user site-packages linked)

- **Unit, the new files:** `test_w2_133_narrowed_label.py` (7) and `test_w2_133_gap_label.py` (8): 15 passed.
  W2-131's `test_w2_131_register_ids.py` (11) and W2-55's `test_register_w2_55.py` (8) in the same run: 34 passed.
- **`gov accept W2-133`:** pass, 48/48. success-1 13/13, success-2 6/6, success-3 29/29; 0 unmapped, 0 skipped.
- **`tests/unit/decisions` and `tests/unit/retrieval`** (`-m "not local_only" -k "not real and not green_here and not
  time_limit"`): 428 passed, 18 failed, 303 deselected (the opt-in lists and the exclusion).
  - The 18 failures are all in `test_w2_112_shared_reranker.py`. Each is the launch sandbox refusing the shared
    reranker's Unix socket (`PermissionError: Operation not permitted`), the same 18 W2-131 recorded. The file never
    reaches the register label or `leave_out`.
  - `test_the_socket_is_the_users_alone` was re-run alone and is red the same way.
  - The CTO's scoped run outside the sandbox settles them.
