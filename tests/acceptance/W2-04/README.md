# W2-04 acceptance tests (DAEO-u4oz): `gov context` bounded and reproducible

A fresh independent test designer (MR-3) wrote these tests before the implementation, in the tests worktree, from the ticket's seven success KPI lines and its failure line, CAP-15 and CAP-15.a to CAP-15.g, DEC-860, W2-03's register entries, and the list rows W2-H034, W2-L088, W2-L180, W2-L183, W2-L219, W2-M126, W2-M134, W2-M215, W2-M228, W2-M239, W2-M294 and W2-M330 (with their source lines in `governance/project/bootstrap.md`). They follow the specification of run 1 (S1 to S10), the text the engineer has. The profile is FULL: each KPI line's success and failure, and the edge cases the rows name.

**56 cases in 10 files** in run 1. At the base (`847616af`, this tree's `src/` equal to `w2/integrate`): **35 failed, 19 passed, 2 skipped**, about 30 s.

**Round 2 (DEC-1005; "Round 2", at the end): 61 cases in 10 files.** Four cases were revised and five added. At the base (`d2ff95b2`): **40 failed, 19 passed, 2 skipped** (the same 19 pass, and every added case is red).

## How the suite runs, and the code it runs (DEC-732)

From the root of the tree that holds the suite:

    PYTHONPATH=<that tree>/src python3 -m pytest tests/acceptance/W2-04 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

- **The tree's own code.** Every process a case starts gets `Api.env()` from `w2_04_support.py`. Its `PYTHONPATH` ends with `SRC`, the `src/` beside the support file's own `tests/` folder. Merged into the ticket's worktree, the same files exercise that worktree's code. `test_w2_04_code_under_test.py` checks it (with and without the stand-ins in front).
- **Public interfaces only.** No case reads `src/`.
  - `gov context <ticket> --json [--budget N] [--brief] [--dry-run]`, as `python3 -m gov.cli.main context … --json --root <project>`, run from a folder outside the project. The cases read its envelope and its exit code.
  - `gov.context.context(root, ticket, …)`, called in a child process through a small driver. The driver also calls `gov.store.load`, `gov.records.records` (an entry's `span` and `content_hash`), `gov.retrieval.lexical.refresh` and `gov.retrieval.synthesis.validate_notes`.
  - The context-reproducibility check: `python3 -m gov.context.context_check`, run in the project root.
  - Round 2: `gov retrieve <query> --json --root <project>` (`Api.retrieve`), the read that reaches the semantic route.
- **Nothing is written in this tree.** Every project is a temporary git repository built from nothing under pytest's `tmp_path`. Two of this tree's files are read, each a single named file: the path map, which is rewritten with one namespace and no authority block, and `template/.gitleaks.toml`. Two cases `git clone` a temporary project, never this repository.
- **Deterministic, no network.** Fixed authors and dates. `HOME` is empty, so no reranker and no embedder venv. The embedder's address is a dead local port. No vector is built. `HF_HUB_OFFLINE` is set. Every child process has a time limit (300 s).
- **gitleaks.** The cases that build a lexical index skip without `gitleaks` on PATH, because its secret filter is needed (DEC-287). This machine has it.

## The planted projects

| Project | Where | What it holds |
|---|---|---|
| plain | `test_w2_04_ceiling.py` | No index. A charter and a capability file. `TK-W204-PLAIN` cites both. `TK-W204-LARGE` has a body of about 4,000 tokens. |
| over | `test_w2_04_refusal.py` | No index. A charter of about 35,000 tokens (`TK-W204-BIG`), and a small ticket. |
| audit | `test_w2_04_refusal.py` | DAEO-03pw's shape: the sources DEC-070, DEC-088, DEC-092, DEC-096, MR-4, CAP-47 and CAP-59, the dependency DAEO-gjjf, and a register at least as large as this repository's (1.57 MB). Its four cited entries are short and stand among fillers. Indexed. |
| harbour | `test_w2_04_decision_hash.py` | A register of about 300,000 characters. `TK-W204-DEC` cites one short entry (DEC-102) and a capability file. |
| ledger | `conftest.py` (`ledger`) | 48 pages. Each holds the ticket's title (`Beacon ledger`) and its KPI line, each on a line of its own. Every fourth page is large (about 260 tokens), the rest small (about 25). Room for all of them at the default ceiling. Indexed. |
| ties | `test_w2_04_reproducible.py` | Four files with identical text in `docs/ties/`, six matching notes whose paths sort before them, one note no query matches (`docs/semantic/gulls.md`). Indexed. |
| quay | `test_w2_04_query.py` | Title `Harbour lamps, north quay`. KPI line `The tide gauge records the vermilion datum at dawn.` `docs/notes/datum.md` holds the KPI line and no word of the title. Indexed. |

The lexical route matches a line's exact text. So in the ledger, every page holds the title and the KPI line verbatim, and any query built from the title, the KPI lines or their words finds every page. The lexical route ranks its hits by path, so the ledger's pages are ranked by path.

## The stand-ins (`_HOOK` in `w2_04_support.py`)

A `sitecustomize.py` sits in a temporary folder that is put first on `PYTHONPATH`, only for the processes of the cases that ask for it. Each stand-in is on only where its variable is set.

- **`watch`** (`W204_WATCH`): an audit hook (`sys.addaudithook`) counts two things in the `gov context` process: every `open` of the ticket file, and every child process whose arguments name it. At exit it prints `W204-READS [...]` on stderr. This is S9, observed from outside the code. In a project without a lexical index, nothing but the context reads the ticket file (the retrieval reads only the files of its evidence).
- **`semantic-live`** (`W204_MODE=semantic-live`): the semantic route's search, `gov.retrieval.semantic.search`, answers. It says it is available and returns hits for the chunks of `W204_SEMANTIC_PATH`, a note no lexical query finds. This is a live semantic index, deterministic and without a network. Each question it is asked is logged (`semantic.jsonl`), so a case sees whether a process asked the semantic route anything.
- **Removed in round 2:** `log` and `ties-reversed`, which wrapped the retrieval's public entry. Under P-W2-04-2 (A) the context no longer reaches that entry. One batch is one of the context's own lookups, shown in the packet's `supplementary_batches`.

## Orders produced from outside (round 2)

The tie case no longer reorders anything inside a process. It builds the orders the project, the store and the process could give:

- **The project's files** are written in another order into another project. The same files, the same fixed dates and identity, and so the same commit.
- **The store's rows** come in another order (`Api.build_in_order`). The named files are set aside outside the project and the lexical index is refreshed. Then each file is put back in the given order, with a refresh after it, so its chunks get later rowids. The tree and the commit end as the project's own, and the index is fresh.
- **The process:** other hash seeds (`PYTHONHASHSEED` 0, 1, 4099), each computation in a process of its own.

The fixture holds its premise. `row_order` reads the temporary store's `lexical_chunk` rowids (the order a reader that names no order gets) and shows the same rows in another order. The tied rows come in two other orders: reversed, and in the order the files were written (tie-d, tie-b, tie-a, tie-c).

## KPI lines and rows → tests, and why each is red today

### KPI 1 (S1; CAP-15, CAP-15.d): the ceiling, and the ticket's own text: `test_w2_04_ceiling.py`

| Test | Holds | Today |
|---|---|---|
| `test_the_packet_carries_the_tickets_own_text_whole_and_verbatim` | `ticket_text` is the ticket file's text, front matter and body. | red: no `ticket_text` |
| `test_tokens_count_the_tickets_text_and_every_mandatory_input` | With nothing supplementary, `tokens` is the ticket's text plus its two mandatory files. Either rounding is taken. `budget == {limit: 6000, used: tokens}`. | red: `tokens` 90, expected 172 to 173 (the ticket's 83 left out) |
| `test_a_large_ticket_whose_total_fits_is_served_whole` | A ticket of about 4,000 tokens is served whole under the default ceiling. | red: no `ticket_text` |
| `test_under_pressure_supplementary_goes_first_and_the_ticket_text_stays_whole` (3: default ceiling, `--budget` with room for half the supplementary items, `--budget` with room for none) | Each packet holds its ceiling. The mandatory input and the whole ticket text stay. Only the supplementary block shrinks. With no room, `tokens` is the mandatory size exactly. | red: no `ticket_text` |
| `test_the_function_holds_the_ceiling_as_the_command_does` | `gov.context.context` gives the command's packet and hash. | red: no `ticket_text` |
| `test_a_dependency_ticket_is_counted_by_its_front_matter_so_a_large_body_still_fits` (round 2, the addendum's S1) | The dependency `TK-W204-DEP` has a body of about 38,000 tokens. The ticket that names it in `deps` is `ok: true`, holds the default ceiling, and its text is whole. The dependency keeps its file's sha256. A change to the dependency's body alone (commit, reload) leaves `tokens` unchanged and moves its sha256 to the new file's. A change that lengthens its KPI line by about 200 tokens raises `tokens`, so the KPI lines are counted. | red: no `ticket_text` (the base is `ok: true` with the dependency counted whole, over the ceiling) |

`assert_holds_its_ceiling` (support) is applied to every `ok: true` packet in the suite. It checks `ticket_text` whole, `tokens == budget.used`, `tokens <= budget.limit`, and `tokens` ≥ the ticket's text + the supplementary items.

### KPI 2 and the failure line, first half (S2; AR-1, F-M5): `test_w2_04_refusal.py`

| Test | Holds | Today |
|---|---|---|
| `test_mandatory_inputs_over_the_default_ceiling_refuse_by_name` | `ok: false`, `CONTEXT_OVER_CEILING`, non-zero exit. The message names the ticket, `6000` and the mandatory size. `details` holds `ticket`, `limit` and `mandatory_tokens` (> 6000). | red: `ok: true` with tokens 35,758 |
| `test_mandatory_inputs_over_a_given_budget_refuse_by_name` | The same under `--budget 40`. | red: `ok: true` with tokens 50 |
| `test_the_function_refuses_with_the_named_error` | `gov.context.context` raises `CONTEXT_OVER_CEILING`. | red: a packet of 35,758 tokens |
| `test_at_the_line_it_fits_and_one_token_over_it_refuses` | The line is the packet's own count of the ticket and its mandatory input. `--budget line+1` and `--budget line` fit, at exactly `line` tokens. `--budget line-1` refuses. | red: no `ticket_text`. The base never refuses. |
| `test_brief_over_the_ceiling_refuses_and_writes_no_packet_file` (2: `--brief`, `--brief --dry-run`) | It refuses, and no file is written under `.gov-runtime/scratch/` or named after the ticket. | red: `ok: true` (a brief file is written) |
| `test_daeo_03pw_shape_fits_or_refuses` | The failure KPI. Either `CONTEXT_OVER_CEILING`, or `ok: true` under the ceiling with all seven sources mandatory and the ticket text whole. | red: `ok: true` with tokens 1,631,999 (each decision counted as the whole register) |
| `test_this_repositorys_daeo_03pw_fits_or_refuses` (`local_only`) | The same on this tree's own DAEO-03pw and this tree's own store, read and never rebuilt. | skipped: the tests worktree has no store (see "local_only") |

### KPI 3 (S3; W2-03, AR-1): each decision by its own hash: `test_w2_04_decision_hash.py`

| Test | Holds | Today |
|---|---|---|
| `test_a_decision_is_named_by_its_entrys_own_hash_not_the_registers` | DEC-102's `sha256` and `constraint` are its entry's `content_hash` (from `gov.records.records`), not the register file's sha256. | red: the register's hash |
| `test_a_decisions_token_cost_is_its_span_so_one_short_decision_of_a_large_register_fits` | One short entry of a 75,000-token register fits. `tokens` is the ticket, the span and the capability file. | red: no `ticket_text` (the packet is `ok: true` at about 75,000 tokens) |
| `test_editing_another_entry_leaves_the_decisions_hash_unchanged` | Edit DEC-104, commit, reload: DEC-102's `sha256` stays, and it equals its `content_hash`. | red: it changes with the register file |
| `test_editing_the_decisions_own_text_changes_its_hash_to_its_new_entry_hash` | Edit DEC-102, commit, reload: its `sha256` changes to its new `content_hash`. | red: it changes to the register's new hash |
| `test_a_mandatory_input_that_is_a_file_of_its_own_keeps_its_files_sha256` | A capability file keeps its file's sha256. | **green**: holds what stays |

### KPI 4 (S4; AR-9, W2-M239, W2-M294, W2-M330): reproducible: `test_w2_04_reproducible.py`

| Test | Holds | Today |
|---|---|---|
| `test_two_builds_in_one_process_give_one_hash` | Two calls in one process give one packet. | **green** (lexical route only) |
| `test_two_builds_in_two_processes_give_one_hash` | Two commands give one packet (W2-M330: across processes, with an index). | **green** |
| `test_two_stores_rebuilt_from_one_commit_give_one_hash` | Two clones, each indexed and loaded, give the first project's hash. | **green** |
| `test_tied_items_are_ordered_by_path_then_id` | The four tied items are in `(path, id)` order. | **green**: the lexical route ranks by path |
| `test_tied_items_keep_one_order_whatever_order_the_retrieval_gives_them` (round 2) | Orders from outside ("Orders produced from outside"): (a) the same files written in reverse into another project at the same commit, its rows inserted in reverse path order; (b) a clone whose tied rows come last in the order the files were written. Each runs under three hash seeds. Every packet is the first one, hash included. The tied items stand in `(path, id)` order in the stack and in the batches' rank order. The first packet holds its ceiling. | red: no `ticket_text` and no `supplementary_batches`. A throwaway probe outside the tree ran the fixture on the base: the same commit, the rows in other orders, and the base's packet the same under each (its lexical route sorts by path) |
| `test_the_packet_is_the_same_whether_or_not_the_semantic_route_answers` (round 2) | The premise is seen through `gov retrieve`: with `semantic-live` it finds the gulls note, without it not. `gov context` with the stand-in live gives the packet and hash it gives with the route unavailable. The note stands nowhere in the packet, and the context asked the semantic route nothing. The packet holds its ceiling. | red: no `ticket_text`; behind it, the gulls note enters the supplementary block and the context asks the semantic route |
| `test_with_a_live_local_embedder_the_packet_is_the_same` (`local_only`) | Vectors are built with a live local embedder. The packet with the embedder answering equals the packet with it unreachable. | skipped: `W204_LIVE_HOME` is not set |
| `test_the_check_is_never_green_on_a_stale_store_and_red_on_a_fresh_one` | The store is built, then the next commit retires the ticket's source. On the stale store the check exits non-zero and names the stale store (`stale`, `unmeasured`) or the ticket. After the reload it is red. | red: `context-reproducibility: green` on the stale store, exit 1 after the reload |

### KPI 5 and the failure line, second half (S5; W2-H034, W2-L088, W2-M215): `test_w2_04_unreadable.py`

| Test | Holds | Today |
|---|---|---|
| `test_a_mandatory_file_that_cannot_be_read_blocks_or_is_marked_not_read` (2: deleted, no permission) | `BLOCKED` naming the id and the file, or `"read": false`. Never shown as read. | **green** (W1-24's follow-up, DEC-552) |
| `test_a_register_entry_whose_span_cannot_be_read_blocks_or_is_marked_not_read` (3: deleted, emptied, no permission) | The store holds the entry and the working tree's register is gone, empty or unreadable. The context blocks naming DEC-102 and the register, or marks it not read, or shows it read with its own `content_hash` (span read from the store). Never the empty hash, never 0 tokens. | red for **emptied**: shown read with the hash of empty content. Deleted and no permission are **green** (BLOCKED, naming the file). |
| `test_a_source_that_no_longer_stands_blocks_naming_its_status` (6: SUPERSEDED, RETIRED, REJECTED × register entry, decision file) | `BLOCKED`, naming the id and its status. | **green**, each (DEC-552, DEC-568). Held now that decisions are read as entries. |

### KPI 6 (S6; W2-M126): the supplementary query: `test_w2_04_query.py`

| Test | Holds | Today |
|---|---|---|
| `test_the_packet_carries_the_query_built_from_the_kpi_lines_and_the_title` | `supplementary_query` (a string, or a list of strings) holds a word of the KPI lines that the title lacks, and is not the title's first long word alone. | red: no `supplementary_query` |
| `test_a_document_matching_only_the_kpi_lines_reaches_the_supplementary_block` | `docs/notes/datum.md` is supplementary. | red: the query is `Harbour`, and only the ticket and `lamps.md` are found |

### KPI 7 (S7; DEC-860, W2-L180): batches, ranked and stacked: `test_w2_04_batches.py`

| Test | Holds | Today |
|---|---|---|
| `test_with_room_for_all_every_matching_item_is_stacked_in_rank_order` | All 48 pages are stacked, in rank order (path), and `further_batch == []`. | red: no `ticket_text`. 18 pages: one call gives at most 20 items. |
| `test_when_room_is_left_after_one_batch_the_next_batch_is_taken` (round 2) | Read through `supplementary_batches`, with room for every page. Every batch but the last read its `limit` (one that read fewer ended the evidence, so nothing was left to take). The last read fewer than its limit, or none. The stack is every item the batches read, in their order. When the evidence passes the first batch's limit, there are at least two batches and more stacked than the largest limit. No limit exceeds the room's tokens (each item costs at least one). | red: no `supplementary_batches` |
| `test_with_less_room_the_stack_stops_at_the_first_item_that_does_not_fit` | From the full stack, it takes the first item k that has a smaller item ranked below it. The budget holds the items above k and is one token short of k. The stack is exactly the items above k: nothing ranked below k. | red: an item ranked below k is stacked (greedy fill) |
| `test_further_batch_begins_with_the_first_item_that_did_not_fit_in_rank_order` | `further_batch` is a list of `{id, path}`. It begins with item k, is the ranked items from k on, and holds no stacked item. | red: no `further_batch` |
| `test_further_batch_is_at_most_one_batch_long` (round 2) | Under the tight budget, read through `supplementary_batches`. The stack is the first items the batches read. `0 < len(further_batch) <=` the largest `limit`. It begins with the first ranked item not stacked, continues in the batches' order, and holds no stacked item. | red: no `supplementary_batches` |
| `test_a_lookup_failure_is_named_in_dropped_by_its_kind` | A damaged index (its chunk table dropped) is named in `dropped` as `index unavailable`, and nothing is stacked. | **green** (W2-L180, fixed in W1-24's follow-up) |
| `test_supplementary_batches_is_present_and_of_its_form` (round 2; 4: room for all, a tight budget, no index, a damaged index) | The addendum's S7a and "The packet's keys". The packet's keys are the eight it carried before and exactly the four added. `supplementary_batches` is a list of `{items: [{id, path}], limit}` with `len(items) <= limit` and `limit >= 1`. `supplementary` is the first items of the batches' items. With no index or a damaged one, nothing is stacked or left. With a damaged one, `dropped` names the failure. Two builds give the same batches and hash. | red: the four keys are absent |

### Rows W2-M228 and W2-L219 (S8): the check's shapes: `test_w2_04_context_check.py`

| Test | Holds | Today |
|---|---|---|
| `test_an_unheld_file_alone_is_named_and_the_message_is_accurate` | A ticket folder holding only `README.md`: red, the file named, and never "every ticket's context computation failed". | red: that message |
| `test_an_unheld_file_beside_a_ticket_keeps_the_check_red` | A README beside a ticket keeps the check red and is named. | **green** (DEC-628) |
| `test_a_ticket_file_with_another_ending_is_named_never_unseen` (2: `.MD`, `.markdown`) | The output names the file or its id. | red: green, and it is never named |
| `test_two_ticket_files_with_one_id_are_named_as_a_duplicate_and_not_green` | Exit non-zero, and a line naming the id says "duplicate". | red: green |

### Rows W2-L183 and W2-M134 (S9, S10): `test_w2_04_one_read_and_notes.py`

| Test | Holds | Today |
|---|---|---|
| `test_a_context_reads_the_ticket_file_once` | With `watch`: at most one read of the ticket file (opens and child processes naming it), and `ticket_text` is the file's text. | red: 3 opens (its ids, its sources, its title) |
| `test_notes_that_fail_their_validator_are_reported_as_failing_never_as_valid` | The notes cite the charter with a wrong span hash (`validate_notes` gives `HASH_MISMATCH`, checked first). The packet names `HASH_MISMATCH` and holds no `"valid": true` anywhere. | red: the packet says nothing of the notes |
| `test_a_project_with_no_notes_is_unchanged` | No `NOTES_NOT_FOUND` in the packet. | **green** |

The specification does not name the packet key for the notes' result. The case reads the whole packet: the failure code is named somewhere, and nothing says `"valid": true`.

### DEC-732

`test_w2_04_code_under_test.py::test_the_processes_the_suite_starts_run_this_trees_code`: **green**.

## The cases that pass at the base (19), and why

- Rows fixed earlier, held now that decisions are read as entries:
  - SUPERSEDED, RETIRED and REJECTED block, as register entries and as decision files (6). DEC-552 and DEC-568, in W1-24's follow-up.
  - A missing or unreadable mandatory file blocks and names it (2).
  - A register deleted or unreadable blocks and names it (2).
  - A lookup failure is named by its kind (1). W2-L180.
- With the lexical route alone, the packet is already the same:
  - in one process, in two processes, and on two stores rebuilt from one commit (3);
  - with ties in path order (1).
  W2-M330 asked for these cases with an index. They hold what the change must keep.
- Kept as they are: a file of its own keeps its file's sha256 (1); a README beside a ticket keeps the check red (1); no notes, no change (1); the code under test (1).

## `local_only` (2 cases)

Deselect with `-m "not local_only"`.

- `test_this_repositorys_daeo_03pw_fits_or_refuses` needs **this tree's own store** (`.gov-runtime/store.db`, the one the lead's rebuild makes before verification). It reads that store and never rebuilds it. It skips where there is none: the tests worktree has none.
- `test_with_a_live_local_embedder_the_packet_is_the_same` needs two things: `W204_LIVE_HOME`, naming a HOME that holds the pinned CPU embedder; and Ollama with the pinned model answering at `OLLAMA_HOST` (default `127.0.0.1:11434`). It builds vectors in a clone of the ties project with `gov.retrieval.semantic.refresh`. It skips where `W204_LIVE_HOME` is unset, or where no vectors were built.

## Readings taken (each is the specification's word, applied)

- **R1. "Ties"** are items with identical text at different paths, as the brief says. The stand-in reverses only the order within a group of tied items, which stand together in the rank. A change that keeps the retrieval's rank and orders each tied run by `(path, id)` meets the case. So does one that sorts by its own relevance, then `(path, id)`.
- **R2. "Rank order"** is the order of the full stack at the default ceiling, where everything fits. The tight-budget cases take that order as the rank and compare `(id, path)`.
- **R3. "Marked not read"** is any map in the packet with that `id` and `"read": false`. An entry shown as read with its own `content_hash` (its span read from the store) is not an unread record. The working tree's register being gone does not make the store's span unreadable.
- **R4. The mandatory size** in the refusal's message is `details.mandatory_tokens`, printed as a number. The cases require it to be more than the ceiling only where the mandatory inputs alone are. Whether it includes the ticket's text is not fixed.

## Packages (run 1; each decided, "Round 2")

**Decided:**

- **P-1:** (A) of P-W2-04-2, DEC-1005. One batch is one of the context's own lookups, shown under `supplementary_batches`; not a call of the retrieval's entry.
- **P-2:** (b), by the lead. A reproduced `CONTEXT_OVER_CEILING` is named on a `REFUSED:` line; any other difference or error stays red.
- **P-3:** (a), by the lead. Items left for lack of room are in `dropped` ("budget exceeded") and in `further_batch`.
- **P-4:** a split outside this ticket; no case.

**P-1. What one batch is.** "The stack holds more than one batch" and "further_batch is at most one batch long" (S7) need a batch size, and the specification leaves the size to the implementation.
- *Why now:* two cases (`…the_next_batch_is_taken`, `…at_most_one_batch_long`) read one call of the retrieval's public entry as one batch.
- *Options:*
  - (a) One call of `gov.retrieval.retrieve.retrieve`, whatever its `batch_size`. This is the reading taken; W2-54's suite already requires that the context reach that entry.
  - (b) One entry of the bundle's `batches` list.
  - (c) A batch size the packet states under a key of its own.
- *Impact:* under (a), an implementation that asks for all evidence in one call of `batch_size=1000` fails `…the_next_batch_is_taken`. That is DEC-860's "never one giant query".
- *Reversibility:* high (two cases). *Cost:* small.
- *Recommendation:* (a). *Confidence:* medium.

**P-2. A refusal over the ceiling in the context-reproducibility check.** Today any exception counts as an error, and the check goes red.
- *Why now:* after W2-04, the same `CONTEXT_OVER_CEILING` twice could be either an error or a measured, reproducible result. If any ticket of this repository has mandatory inputs over 6,000 tokens, `gov check`'s context-reproducibility on this repository turns red (W2-54's `test_gov_check_gives_context_reproducibility_green_here`).
- *Options:*
  - (a) A refusal is an error: red, and named.
  - (b) The same named refusal twice is measured as reproducible and named in the output. A refusal that differs between the two computations is red.
  - (c) The engineer chooses.
- *Impact:* (a) can turn this repository's check red on a legitimate refusal. (b) keeps the check about reproducibility.
- *Reversibility:* high. *Cost:* small.
- *Recommendation:* (b). *Confidence:* medium. No case here holds either option.

**P-3. Items left for lack of room: `dropped` as well as `further_batch`?** The specification keeps `dropped` in W2-54's form for lookup failures and names what was left under `further_batch`. It does not say whether an item that did not fit is still listed in `dropped`.
- *Why now:* earlier cases assume it is.
  - W1-24's `test_w1_24_supplementary.py::test_supplementary_is_dropped_before_mandatory_and_the_drop_is_named` expects a non-empty `dropped` under `--budget 200`.
  - W2-54's `test_w2_54_dropped_order.py::test_nothing_is_dropped_or_added_every_item_stays_in_the_packet_once` expects each returned item once in `dropped`.
- *Options:*
  - (a) Keep listing them in `dropped` (reason "budget exceeded"), and name the next batch in `further_batch`.
  - (b) `further_batch` only, and revise those cases.
- *Recommendation:* (a). *Confidence:* medium. No case here holds either option.

**P-4. W2-M133 (provenance `inputs_hash`).**
- *Question:* the row is in the ticket's `list_rows`, but the specification of run 1 gives it no behaviour. Is it in W2-04?
- *Why now:* no case covers it.
- *Options:*
  - (a) Out of W2-04: the row is about a check's provenance, not the packet.
  - (b) Give a specification line, and the test designer adds a case.
- *Recommendation:* (a), or (b) with one line. *Confidence:* low.

## Earlier tests this specification affects (run 1: named, not revised; round 2 revised them, "Round 2")

W1-24's cases are **not revised**: none is contradicted. Under the new count, the tightest one, `test_w1_24_pressure.py::test_supplementary_is_dropped_before_mandatory_inputs` (`TK-W24-PRESS` at `--budget 200`), is the ticket's 66 tokens plus its mandatory 126, which makes 192 and still fits.

Contradicted (they turn red once W2-04 is built):

- `tests/acceptance/W1-41/test_w1_41_external_references.py::test_an_external_reference_adds_nothing_to_the_packets_tokens`. `TK-H9-EXT` and `TK-H9-REC` must count the same `tokens` and have the same `budget`. Under S1, `tokens` counts each ticket's own text, and `TK-H9-EXT`'s file is longer by its external source's line.
- `tests/acceptance/W2-54/test_w2_54_dropped_order.py`: `TK-W254-BIG`'s mandatory input (about 25,000 tokens) is past the default ceiling. Under S2 its context refuses with `CONTEXT_OVER_CEILING`, and `S.packet()` asserts exit 0. The cases:
  - `test_the_stand_in_reaches_the_retrieval_s_public_entry_with_tied_and_same_id_items`;
  - `test_two_computations_with_the_retrieval_s_own_order_give_one_packet`;
  - `test_every_order_of_the_retrieval_s_items_gives_the_same_packet_and_hash` (3);
  - `test_nothing_is_dropped_or_added_every_item_stays_in_the_packet_once` (2);
  - `test_an_empty_retrieval_result_gives_one_packet`;
  - `test_a_store_whose_index_is_missing_gives_one_packet_under_any_order[TK-W254-BIG]`;
  - `test_a_budget_below_the_mandatory_inputs_gives_the_same_packet_under_any_order`: a `--budget` below the mandatory inputs now refuses;
  - `test_the_check_is_green_when_two_computations_see_two_orders`: its computations refuse, which is red unless P-2 (b).

At risk, depending on the implementation:

- `tests/acceptance/W2-54/test_w2_54_dropped_order.py::test_a_ticket_whose_items_fit_keeps_every_item_and_drops_nothing` compares the supplementary block with the last retrieval call's items. With batches (S7), the stack holds the items of several calls.
- `tests/acceptance/W2-55/test_w2_55_left_out.py`, the `gov context` cases. Its tickets have no KPI lines, and their title begins with the word the old lookup asked for (`vermilion`). Under S6 the query is built from the title (and the KPI lines). A query that is the whole title as one phrase finds none of the register's entries, because the lexical route matches a line's exact text.
- `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here`: see P-2.

## Round 2 (DEC-1005, 2026-11-01): the revision batch

A fresh independent test designer revised the suite from the specification and its addendum (DEC-1005, delegated by the CTO, deciding P-W2-04-2 (A) and P-W2-04-3 (b)). Every commit carries `Rewrite-Reason: W2-04's KPIs 2 and 4 (CAP-15.d, DEC-860), DEC-1005`. No expectation is lowered: each revised case asserts at least what it did, observed where the addendum puts it.

### What changed in this folder

| case | why | what it guards now |
|---|---|---|
| `test_w2_04_batches.py::test_when_room_is_left_after_one_batch_the_next_batch_is_taken` | P-1 decided as (A): the context no longer reaches the retrieval's entry, so `log` saw nothing | the batches' own rules, through `supplementary_batches` (KPI 7 table) |
| `test_w2_04_batches.py::test_further_batch_is_at_most_one_batch_long` | the same | `further_batch` against the batches' items and their largest `limit` |
| `test_w2_04_reproducible.py::test_tied_items_keep_one_order_whatever_order_the_retrieval_gives_them` | the same: `ties-reversed` saw nothing | ties in `(path, id)` order and one packet, whatever order the files, the store and the process give |
| `test_w2_04_reproducible.py::test_the_packet_is_the_same_whether_or_not_the_semantic_route_answers` | the semantic-free block (P-W2-04-2 (A)) | the premise through `gov retrieve`; one packet; the note never in it; no semantic question from `gov context` |
| **added** `test_w2_04_ceiling.py::test_a_dependency_ticket_is_counted_by_its_front_matter_so_a_large_body_still_fits` | the addendum's S1 (P-W2-04-3 (b)) | a dependency counted by its front matter (KPI 1 table) |
| **added** `test_w2_04_batches.py::test_supplementary_batches_is_present_and_of_its_form` (4) | the addendum's S7a and "The packet's keys" | the key's presence and form, and the packet's key set |
| `test_w2_04_code_under_test.py` | `log` is gone | the same check, with `semantic-live` in front |

**S1 as amended, read against the rest of the suite.** Only the audit shape plants a dependency (DAEO-gjjf). Its case asserts "fits or refuses" and no count, so no case was counted whole. `assert_holds_its_ceiling` counts the ticket's own text and the supplementary items, never a dependency.

### Readings taken in round 2

- **R5. "Every batch but the last read its limit."** A batch that read fewer items than its limit ended the evidence, so no further batch had anything to take. With room for everything the last batch reads fewer than its limit, or none.
- **R6. "The stack holds more than one batch"** is required when the matching evidence passes the first batch's limit. A limit at or above the evidence (48 pages and more) gives one batch, and the case then holds only the rules. A limit is bounded only by the room's tokens: each item costs at least one, so no batch reads more items than the room has tokens.
- **R7. `further_batch` is among the items the batches read.** Naming what is next means reading it, and a read is a batch the context took (S7a: "one entry per batch the context took").
- **R8. "The context asked the semantic route nothing."** The real semantic search embeds its question, so a context that calls it sends an embedder text. The stand-in's log stands in for the embedder's.

### Earlier suites revised in round 2

- **W2-54:** `tests/acceptance/W2-54/README.md`, "W2-04 (DEC-1005)". `test_w2_54_dropped_order.py` (14 cases) and the three embedder cases changed.
- **W1-41:** `tests/acceptance/W1-41/README.md`, "Rewrite (W2-04, DEC-1005)". Two cases changed.
