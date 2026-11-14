# FAIL: data, scenario 2 (An import that lets bad rows through), run 6, skill 1.0.1, run_at 2026-11-14T03:19:28+00:00

## The session's reply

~~~~
**task:** Nightly import of partner shipment records into `shipments`, replacing the first draft that loads whatever parses.

**status:** Blocked. No files were written. Writing `tests/test_shipment_import.py` was refused (permission not granted), and so were running the tests and `gov retrieve`. I didn't retry them.

**work_completed:**
- Loaded the data skill and checked the inputs it says to read first. The folder holds only the skill itself: no ticket file, no `shipments` schema, no migrations, no sample, and nothing that shows what reads or writes the table.
- Wrote down the rules for each field (below).
- Drafted the unit tests in full (the content of the refused write): 9 rule tests, 11 import tests and 1 migration test, on a synthetic fixture with no real data.
- Designed the load (below). None of it was implemented or run.

**files_changed:** None.

**evidence:** None. Nothing ran, so there are no counts.

**tests:** Drafted but never run, so there is no result, not even the failing run that should come before the code is written.

**discoveries:** The data-quality rules, applied to every row before anything is loaded. A row that breaks a rule goes to a rejects table with its line number, its raw text and the reason. Nothing is dropped or fixed silently.

| Field | Rule | Rejection reason |
|---|---|---|
| `shipment_id` | Present and not blank once spaces are trimmed | `shipment_id_missing` (this is the 2 %) |
| `shipment_id` | Appears once in the file. Every copy of a repeat is rejected, because we can't tell which copy is right | `shipment_id_duplicate_in_file` |
| `shipment_id` | Not already in `shipments`. Such a row is rejected, and the existing row is never overwritten | `shipment_id_already_loaded` |
| `weight_kg` | Present, a finite number (`nan`, `inf` and `1,5` are refused), and ≥ 0 | `weight_kg_missing` / `weight_kg_not_number` / `weight_kg_negative` |
| File | The required columns are there. If not, the whole file fails | Exception; nothing is loaded |

Small reversible choices I made myself: reject every copy of a duplicate, allow a weight of 0, and send rows already in the table to the rejects table instead of updating them.

Planned design:
- **Migration 0001 (reversible, adds only).** It creates two new tables:
  - `shipment_import_runs`: run id, source name, a unique file hash, and the counts read, loaded and rejected.
  - `shipment_import_rejects`: run id, line number, `shipment_id`, reason, raw row as JSON.

  The "down" step drops only those two tables. Both steps are safe to run twice, and `shipments` itself is not altered.
- **The load.** Each file loads in one transaction, so a failure leaves nothing behind and a rerun starts clean. The same file a second time, even renamed, is a no-op because of the hash. Each run records that rows read = rows loaded + rows rejected.

**risks:**
- None of this exists yet.
- The real `shipments` columns are unknown, so I only covered `shipment_id` and `weight_kg`.
- Whether `shipments.shipment_id` has a unique constraint is unknown. I didn't propose adding one, because existing duplicates could make it fail and it would need its own step-by-step change.
- `gov accept` was not run.

**lessons:** Get write and run permission confirmed before starting a data ticket in this workspace.

**proposed_decisions:** These need your answer (P2, since they affect what lands in the table):
1. A partner resends a shipment with corrected values. Reject it (my default), or update the row and keep a copy of the old values?
2. Is a weight of 0 valid? Is there an upper limit?
3. Should the identical copies of a duplicate (same id, same values) load once, or are all copies rejected?

**unresolved:**
- The ticket's KPIs and allowed paths
- The real schema, and which other jobs read `shipments`
- The project's migration tool and its database (I would have tested on SQLite as a stand-in)

**recommended_next_action:** Grant write and run permission in this folder, and point me at the real schema and the ticket's paths. I'll then write the tests and see them fail, implement the migration and importer, run the migration forward and back on a fixture with counts, run the test suite and the pre-commit checklist, and then run `gov accept`.
~~~~

## The judge's reply

~~~~
The reply meets two of the three parts of the pass line but not the third.

1. **The three rules: met.** The table states all three. The key must be present and not blank (`shipment_id_missing`). The key must be unique in the file and not already loaded (`shipment_id_duplicate_in_file` / `shipment_id_already_loaded`). The weight must be in range: present, finite and ≥ 0 (`weight_kg_missing` / `weight_kg_not_number` / `weight_kg_negative`).
2. **Rejected rows kept with a reason: met.** Rows that break a rule go to a `shipment_import_rejects` table with the run id, line number, `shipment_id`, reason and raw row as JSON. The reply says nothing is dropped silently. This is only a design and wasn't built, but the pass line asks only that the reply keep them somewhere, and it does.
3. **A named test with a bad row: not met.** The reply only counts the tests ("9 rule tests, 11 import tests and 1 migration test") and gives the file path `tests/test_shipment_import.py`. It names no test and shows no bad-row input for any rule. The examples `nan`, `inf` and `1,5` appear under the rule descriptions, not as tests. The full test content is said to be in the write that was refused, so it isn't in the reply.

VERDICT: FAIL
~~~~
