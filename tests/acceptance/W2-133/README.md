# W2-133 acceptance tests: a narrowed or gap-starting register item carries its own entry's id

Ticket DAEO-k4wm (W2-133), profile STANDARD, W2-131's follow-up in re-pin window 4 (DEC-1083; DEC-1082 (2),
DEC-1073). Written by the independent test designer (MR-3) from the ticket's KPI lines S1 to S3, before any
implementation, reading only the integrated code (`w2/integrate` `a4e713517cac`, DEC-963). S4 is the CTO's check
after the re-pin, not a test here.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-133 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

(`PYTHONUSERBASE` only where pytest is installed in the user's site and `HOME` is emptied.) Under 1 s, in process.
The tests use the tree `PYTHONPATH` names; without one, the worktree's own `src`.

- **The planted repository** (`w2_133_support.build`, once per session): a temporary git repository whose path map
  names `docs/DECISION_REGISTER.txt`, a register in plain text: a preface (lines 1-4), DEC-100 (5-7, `SUPERSEDED by
  DEC-101`), DEC-101 (9-35), a section `## Interlude` (37-50, in no entry by the store's rule) and DEC-476 (51-77);
  and one note. Its lexical index and record store are built in the temporary folder, the secret filter replaced
  (as the unit tests do). Never this repository's store.
- **Why plain text:** a register that is not Markdown is one parent, the whole file, cut by size alone
  (`chunking.parents`: "anything else: the module"). Its chunks are 1-21, 20-32, 31-52, 49-64, 63-75 and 74-77. So
  a hit expands to a parent (1-77) that spans the superseded DEC-100 and then DEC-101, and `leave_out` narrows it
  back to the hit's chunk (S1); and the chunk 49-64 starts in the gap and runs into DEC-476 (S2). A Markdown
  register is cut at every heading, so neither can happen there with today's chunker (W2-131's README, N-3).
- **One question, one chunk:** `persimmon` (20-32, inside DEC-101), `tamarind` (31-52, from DEC-101 into DEC-476),
  `lanterns` (49-64, from the gap into DEC-476), `cardamom` (74-77, inside DEC-476), `quince` and `almanac`
  (1-21, touching DEC-100); `orchard` is in every chunk and the note. At the default budget (6,000) each hit
  expands to the whole file; at `bundle_budget=300` it is sent alone.
- **No embedder, reranker or model:** the semantic route is a stand-in with no hit, the file route off, every call
  `reranker=lambda: None`; no question names a symbol or a record, so neither the code route nor a closure is
  asked. `GOV_ROLE` and `GOV_TICKET` are cleared.
- **Two pipelines** (`conftest.py`): `ask` is `gov retrieve`'s (`gov.retrieve.command.run`, lines 104-113 on
  integrate: `retrieve`, then `register.leave_out` over the evidence, its record kept as `left_out`); `raw` is
  `retrieve` alone. `command.run` itself is not called, as it gives `retrieve` no stand-in reranker.
- **The oracle** (`w2_133_support.entry_spans`, `holder`, `touched`, `status_of`): an entry's lines (its heading to
  the line before the next heading, without its closing blank lines) and its status word, read from the planted
  text alone, never from the code under test.
- **"Before the fix" for S3** (`w2_133_support.today`): `src/gov/retrieval/retrieve.py` (blob `ecfec265dfaf`) and
  `src/gov/decisions/register.py` (blob `9b61ada364cc`) as `w2/integrate` `a4e713517cac` held them, read from git
  and loaded as modules of their own beside the running tree's. They are the ticket's only source paths, so the
  two differ by the fix alone; both are asked on the same store, in the same process, with the same stand-ins. The
  comparison takes off each register item's `id`, `entry`, `status`, `changed_by`, `in_force`, `not_in_force`
  and `also` (`LABEL_FIELDS`) and nothing else, and compares the evidence set and order (path, lines, chunk id,
  sha256), then `evidence`, `batches`, `budget`, `gaps`, `left_out`, `continuation`, `expansions`, `repeats`,
  `merge`, `facets`, `stopping_reason`, `rerank`, then the whole bundle.

## KPI lines, tests, and the outcome on `w2/integrate` `a4e713517cac`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **48 tests, 12 failed, 36 passed** (0.69 s). Every red fails on the
label S1 or S2 names, none on a premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_133_narrowed.py::test_s1_premise_the_expanded_parent_spans_the_superseded_dec_100_then_dec_101` | green (premise) | `retrieve` sends the parent 1-77, which spans DEC-100 (SUPERSEDED) then DEC-101 |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_carries_its_own_entry_s_id_entry_and_status[persimmon-inside-DEC-101]` | red | narrowed to 20-32, inside DEC-101, it carries id and entry DEC-100, status SUPERSEDED, `in_force` False, `not_in_force` SUPERSEDED |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_carries_its_own_entry_s_id_entry_and_status[tamarind-DEC-101-into-DEC-476]` | red | narrowed to 31-52, from DEC-101: the same DEC-100 marks |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_carries_its_own_entry_s_id_entry_and_status[cardamom-inside-DEC-476]` | red | narrowed to 74-77, inside DEC-476: the same DEC-100 marks |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_s_also_names_the_other_entries_its_own_lines_touch[persimmon-inside-DEC-101]` | red | `also` names DEC-101 and DEC-476 (the parent's); its own lines touch no other entry |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_s_also_names_the_other_entries_its_own_lines_touch[tamarind-DEC-101-into-DEC-476]` | red | `also` names DEC-101 and DEC-476; its own lines touch DEC-476 only beside DEC-101 |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_s_also_names_the_other_entries_its_own_lines_touch[cardamom-inside-DEC-476]` | red | `also` names DEC-101 and DEC-476; its own lines touch none other |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_s_marks_are_those_its_chunk_carries_sent_alone[persimmon-inside-DEC-101]` | red | the narrowed item's seven label fields are DEC-100's; the same chunk sent alone (budget 300) carries DEC-101's |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_s_marks_are_those_its_chunk_carries_sent_alone[tamarind-DEC-101-into-DEC-476]` | red | as above; alone it carries DEC-101's with `also` [DEC-476] |
| S1 | `test_w2_133_narrowed.py::test_s1_the_narrowed_item_s_marks_are_those_its_chunk_carries_sent_alone[cardamom-inside-DEC-476]` | red | as above; alone it carries DEC-476's |
| S1 | `test_w2_133_narrowed.py::test_s1_guard_what_leave_out_leaves_out_and_counts_is_unchanged[a-narrowed-parent]` | green (guard) | no kept register item touches DEC-100; `left_out` is `{count 1, superseded [DEC-100], done []}` |
| S1 | `test_w2_133_narrowed.py::test_s1_guard_what_leave_out_leaves_out_and_counts_is_unchanged[a-hit-on-DEC-100-expanded]` | green (guard) | a hit on 1-21 (touching DEC-100), expanded: left out whole, counted |
| S1 | `test_w2_133_narrowed.py::test_s1_guard_what_leave_out_leaves_out_and_counts_is_unchanged[a-hit-on-DEC-100-alone]` | green (guard) | the same hit sent alone: left out, counted |
| S2 | `test_w2_133_gap.py::test_s2_an_item_starting_in_the_gap_before_dec_476_carries_its_chunk_id` | red | the chunk 49-64, starting in the gap, is labelled DEC-476 (the first entry it touches), not its chunk id |
| S2 | `test_w2_133_gap.py::test_s2_an_item_starting_in_the_gap_names_no_entry_beside_its_chunk_id` | green (guard) | today `entry` and `id` are both DEC-476, so they agree; after the fix a gap item may not keep `entry` DEC-476 beside its chunk id (W2-131 S1's agreement rule) |
| S2 | `test_w2_133_gap.py::test_s2_the_whole_file_parent_starting_in_the_preface_carries_its_chunk_id` | red | `retrieve`'s parent 1-77, starting in the preface, is labelled DEC-100 |
| S2 | `test_w2_133_gap.py::test_s2_a_narrowed_item_starting_in_the_gap_carries_its_chunk_id` | red | narrowed to 49-64 by `leave_out`, it is labelled DEC-100 (the parent's), not its chunk id (S1 and S2 together) |
| S2 | `test_w2_133_gap.py::test_s2_guard_an_item_starting_inside_an_entry_carries_that_entry[inside-DEC-476]` | green (guard) | 74-77, sent alone, carries id and entry DEC-476, no `also` |
| S2 | `test_w2_133_gap.py::test_s2_guard_an_item_starting_inside_an_entry_carries_that_entry[inside-DEC-101-running-into-DEC-476]` | green (guard) | 31-52, sent alone, carries DEC-101 and `also` [DEC-476] |
| S3 | `test_w2_133_unchanged.py::test_s3_premise_today_s_modules_are_the_code_before_the_fix` | green (premise) | today's pipeline keeps DEC-100 on the narrowed `persimmon` item: the reference is the code before the fix |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-inside-DEC-101-gov-retrieve]` | green (guard) | the running tree is today's code; any change beside the label fields fails it |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-inside-DEC-101-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-inside-DEC-101-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-inside-DEC-101-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-from-the-gap-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-from-the-gap-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-from-the-gap-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-from-the-gap-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-into-DEC-476-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-into-DEC-476-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-into-DEC-476-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-into-DEC-476-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-inside-DEC-476-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[narrowed-inside-DEC-476-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-inside-DEC-476-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[alone-inside-DEC-476-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[dec-100-left-out-gov-retrieve]` | green (guard) | as above; `left_out` names DEC-100 |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[dec-100-left-out-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[dec-100-left-out-alone-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[dec-100-left-out-alone-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[the-preface-gov-retrieve]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[the-preface-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[every-chunk-gov-retrieve]` | green (guard) | as above; an expansion and children sent alone beside it |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[every-chunk-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[every-chunk-batched-gov-retrieve]` | green (guard) | as above; batches of one, `NOT_GATHERED` gaps and a continuation |
| S3 | `test_w2_133_unchanged.py::test_s3_the_bundle_is_today_s_but_for_the_register_items_ids_and_status[every-chunk-batched-retrieve-alone]` | green (guard) | as above |
| S3 | `test_w2_133_unchanged.py::test_s3_the_continued_pages_are_today_s_but_for_the_register_items_ids_and_status[gov-retrieve]` | green (guard) | every page of the batched `orchard` question, the continuation followed to its end |
| S3 | `test_w2_133_unchanged.py::test_s3_the_continued_pages_are_today_s_but_for_the_register_items_ids_and_status[retrieve-alone]` | green (guard) | as above, `retrieve` alone |

**A check of the tests themselves** (a scratch copy of `src`, never committed): `item()` labelled by the entry
holding the first line (`entry_of(rel, first)`, else the chunk id and no marks), and `leave_out`'s narrowed item
given the marks `item()` would give the chunk's own lines, passes all 48. The same sketch with the narrowed item
also losing its `batch` fails S3's four narrowed `gov-retrieve` cases: S3 sees a change beside the label fields.

## Notes and limits

- **N-1. A plain-text register.** The cases need a parent that spans two entries and a chunk that starts in a gap
  and reaches an entry; with today's chunker only a register that is not Markdown gives both (its parent is the
  whole file). The path map may name any file; the store reads its entries the same way. With a Markdown register
  the same two faults need a parent over two entries, which today's chunker never makes (W2-131's N-3); a fix
  that labels by the item's own lines covers both.
- **N-2. The gap item's other fields.** S2 says a gap-starting item carries its chunk id. Whether it still names
  the entry it runs into (`also`, or a status) is not stated; these tests ask only that it name no `entry` beside
  its chunk id (W2-131 S1's rule: where an item names its entry, the two agree). A fix that keeps `entry` DEC-476
  on it fails `test_s2_an_item_starting_in_the_gap_names_no_entry_beside_its_chunk_id`.
- **N-3. The preface parent.** W2-131's S1 note says "a parent expansion the id of its first entry"; W2-133 S2 says
  an item whose first line lies in the preface carries its chunk id. For a parent starting in the preface the two
  differ; these tests follow W2-133 S2 (`test_s2_the_whole_file_parent_starting_in_the_preface_carries_its_chunk_id`).
- **N-4. `changed_by` and `not_in_force`.** S1 names `id`, `entry`, `status`, `in_force` and `also`. The marks test
  compares all seven label fields with the chunk's own marks sent alone, so a narrowed item that kept the parent's
  `changed_by` or `not_in_force` fails it too; S3 takes all seven off.
- **N-5. S3's reference is pinned.** `TODAY_BLOBS` are integrate's blobs at `a4e713517cac`. W2-92 and W2-32 also
  hold `retrieve.py` in re-pin window 4. If either lands first and changes these planted bundles, S3 goes red for a
  reason that is not this fix; then `TODAY_BLOBS` move to the new integrated blobs by a test designer's revision,
  and what S3 compares is unchanged.

## Files

- `w2_133_support.py`: the planted repository, today's two modules from git, the oracle, the page walker.
- `conftest.py`: the session's planted repository, today's modules, the stand-ins (autouse), `ask` and `raw`.
- `test_w2_133_narrowed.py` (S1), `test_w2_133_gap.py` (S2), `test_w2_133_unchanged.py` (S3).
