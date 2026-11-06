# W2-131 acceptance tests: a register chunk in a bundle carries its own entry's id, not DEC-999

Ticket DAEO-r8vq (W2-131), profile STANDARD, a priority fix in re-pin window 4 (DEC-1082 (2); DEC-1073, DEC-424).
Written by the independent test designer (MR-3) from the ticket's KPI lines S1 to S3, before any implementation,
reading only the integrated code (`w2/integrate` `262c488d2baf`, DEC-963). S4 is the CTO's check after the re-pin,
not a test here.

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src TMPDIR=<scratch> \
      python3 -m pytest tests/acceptance/W2-131 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

(`PYTHONUSERBASE` only where pytest is installed in the user's site and `HOME` is emptied.) About 1 s, in process.

- **The planted repository** (`w2_131_support.build`, once per session): a temporary git repository whose path map
  names `docs/DECISION_REGISTER.md`, a register with a preface, DEC-476 (lines 5-7), a section `## Interlude`
  between two entries (no entry's lines, by the store's rule), DEC-999 (13-15) and DEC-1082 (17-49, longer than one
  chunk); a ticket `DAEO-t131` that `depends_on` a failure record `FAIL-131` and a lesson `LES-131` and `constrains`
  DEC-476; plain notes. Each one-word question (`marigold`, `juniper`, `almanac`, `tamarind`, `cardamom`) names one
  span. Its lexical index and record store are built in the temporary folder, with the secret filter replaced
  (as the unit tests do). Never this repository's store.
- **No embedder, reranker or model:** the semantic route is a stand-in with no hit, the file route off, every call
  `reranker=lambda: None`; no question names a symbol and every closure starts from records, so the code index is
  never asked. `GOV_ROLE` and `GOV_TICKET` are cleared, so no role filter of the running session shapes a bundle.
- **The label oracle** (`w2_131_support.label`): S1's rule worked out from the planted register's text alone (an
  entry's lines are its heading to the line before the next heading, without its closing blank lines; a chunk whose
  first line lies in an entry carries that entry's id, any other its `chunk_id`), never from the code under test.
- **"Today's code" for S3** (`w2_131_support.today`): `src/gov/retrieval/retrieve.py` as `w2/integrate`
  `262c488d2baf` held it (blob `62b12493b443`), read from git and loaded as a module of its own beside the running
  tree's. The ticket's only source path is that file, so the two differ by the fix alone; both are asked on the
  same store, in the same process, with the same stand-ins. The comparison takes off the `id` of register items
  only (`w2_131_support.without_register_ids`) and compares the evidence set and order (path, lines, chunk id,
  sha256), then the fields `evidence`, `batches`, `budget`, `gaps`, `continuation`, `expansions`, `repeats`,
  `merge`, `facets`, `stopping_reason`, `rerank`, then the whole bundle.

## KPI lines, tests, and the outcome on `w2/integrate` `262c488d2baf`

Run in the launch sandbox through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not
time_limit"` (it leaves none of these out): **29 tests, 14 failed, 15 passed** (0.46 s). Every red fails on S1's id
or S2's map, none on a premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_131_labels.py::test_s1_a_register_chunk_is_labelled_by_the_entry_that_holds_its_first_line[DEC-476]` | red | "the chunk at lines 5-8, inside DEC-476, is labelled 'DEC-999'" (the query only DEC-476's text answers) |
| S1 | `test_w2_131_labels.py::test_s1_a_register_chunk_is_labelled_by_the_entry_that_holds_its_first_line[DEC-999]` | green (guard) | DEC-999 is the entry that wins today; guards the fix against labelling DEC-999's own chunk otherwise |
| S1 | `test_w2_131_labels.py::test_s1_a_register_chunk_is_labelled_by_the_entry_that_holds_its_first_line[DEC-1082-a-later-chunk-alone]` | red | a later chunk of DEC-1082 (41-49), sent alone (budget 300, no expansion), labelled 'DEC-999' |
| S1 | `test_w2_131_labels.py::test_s1_a_chunk_in_the_preface_or_between_entries_carries_its_chunk_id[the-preface]` | red | the preface chunk (1-4) is labelled 'DEC-999', not its chunk id |
| S1 | `test_w2_131_labels.py::test_s1_a_chunk_in_the_preface_or_between_entries_carries_its_chunk_id[between-entries]` | red | the `## Interlude` chunk (9-12) is labelled 'DEC-999', not its chunk id |
| S1 | `test_w2_131_labels.py::test_s1_a_parent_expansion_carries_the_id_of_its_first_entry` | red | the hit on DEC-1082's last chunk expands to 17-49; "the expansion of DEC-1082 is labelled 'DEC-999'" |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[dec-476-alone]` | red | id 'DEC-999', its own DEC-476; `entry` DEC-476 disagrees with `id` |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[dec-999-alone]` | green (guard) | as the DEC-999 case above |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[the-preface]` | red | id 'DEC-999', its own its chunk id |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[between-entries]` | red | id 'DEC-999', its own its chunk id |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[a-parent-expansion]` | red | id 'DEC-999', its own DEC-1082 |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[a-later-chunk-alone]` | red | id 'DEC-999', its own DEC-1082 |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[a-ticket-dec-424]` | red | DEC-476's chunk, reached by the ticket's closure, labelled 'DEC-999' |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[a-ticket-batched]` | red | the same chunk on a later page (the continuation followed to its end) |
| S1 | `test_w2_131_labels.py::test_s1_every_register_item_s_id_is_its_entry_and_agrees_with_the_entry_key[an-id-at-radius-1]` | red | DEC-476's chunk, by `ids=["DEC-476"]`, labelled 'DEC-999' |
| S2 | `test_w2_131_map.py::test_s2_the_path_to_record_map_holds_no_register_entry_id` | red | `retrieve._graph`'s map holds `docs/DECISION_REGISTER.md -> 'DEC-999'` |
| S2 | `test_w2_131_map.py::test_s2_the_map_keeps_the_record_of_each_record_file` | green (guard) | the ticket's, the failure's and the lesson's files keep their records in the map |
| S2 | `test_w2_131_map.py::test_s2_dec_424_still_lifts_the_failure_and_lesson_records_of_the_ticket_s_closure` | green (guard) | with `ticket=DAEO-t131` every failure and lesson chunk comes before other evidence, and the batched first page is those alone; premise: with DEC-424's types emptied, DEC-476's chunk leads instead |
| S3 | `test_w2_131_unchanged.py::test_s3_premise_todays_module_is_the_code_before_the_fix` | green (premise) | today's module labels DEC-476's chunk DEC-999: the reference is the code before the fix |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[dec-476-alone]` | green (guard) | the running tree is today's code; any change beside register ids fails it |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[dec-999-alone]` | green (guard) | as above |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[the-preface]` | green (guard) | as above |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[between-entries]` | green (guard) | as above |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[a-parent-expansion]` | green (guard) | as above; the expansion and the budget used (691) |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[a-later-chunk-alone]` | green (guard) | as above; budget 300, no expansion |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[a-ticket-dec-424]` | green (guard) | as above; two batches, the closure facet, DEC-424's order |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[a-ticket-batched]` | green (guard) | as above; nine `NOT_GATHERED` gaps and a continuation |
| S3 | `test_w2_131_unchanged.py::test_s3_the_bundle_is_todays_but_for_the_ids_of_register_items[an-id-at-radius-1]` | green (guard) | as above; `DEPTH_LIMIT_REACHED` gaps |
| S3 | `test_w2_131_unchanged.py::test_s3_the_continued_pages_are_todays_but_for_the_ids_of_register_items` | green (guard) | every page of the batched ticket question, the continuation followed to its end |

**A check of the tests themselves** (a scratch run, never committed): the running tree's `retrieve` re-executed
with a two-line sketch of a fix (the map without records that carry a span; a register item labelled by
`entry_of(path, first line)`, else its chunk id) passes all 29. The same with DEC-424's types cut to `failure`
alone fails S3's two ticket cases, its continued pages and S2's DEC-424 guard: S3 sees a change beside the ids.

## Notes and limits

- **N-1. The map is reached by its private name.** S2's map test calls `retrieve._graph(root)[0]`, the map the
  ticket names (`retrieve.py:87` on integrate). A fix that renames `_graph` or changes its first answer fails that
  test with a message saying so; the ticket keeps the change to `item()` and the map, so the name should stay.
- **N-2. S3's reference is pinned.** `TODAY_BLOB` is integrate's `retrieve.py` at `262c488d2baf`. W2-92 and W2-32
  also hold `retrieve.py` in re-pin window 4. If either lands first and changes these planted bundles, S3 goes red
  for a reason that is not this fix; then `TODAY_BLOB` moves to the new integrated blob by a test designer's
  revision (as W2-92's README did under P-6), and what S3 compares is unchanged.
- **N-3. Not tested:** a parent sent in pieces because an earlier call sent one of its children alone (W2-32 S7's
  `left_out`): by S1 each piece is labelled by the entry holding its first line, but building it needs two calls
  whose arguments differ, which a continuation refuses. With today's chunker a parent never holds two entries (its
  sections start at every heading), so "the id of its first entry" and "the entry that holds its first line" agree.
- **N-4. Sub-headings.** The store ends an entry's span at the next heading of any level, so a chunk under a `####`
  heading inside an entry lies "between entries" and carries its chunk id by S1's words. This repository's register
  has no `####` heading today; not tested.

## Files

- `w2_131_support.py`: the planted repository, today's `retrieve` from git, the label oracle, the page walker.
- `conftest.py`: the session's planted repository, today's module, the stand-ins (autouse) and `ask`.
- `test_w2_131_labels.py` (S1), `test_w2_131_map.py` (S2), `test_w2_131_unchanged.py` (S3).
