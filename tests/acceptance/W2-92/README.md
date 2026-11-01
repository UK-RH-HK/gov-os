# W2-92 acceptance tests: the record graph and the code graph as routes of plain-question retrieval

Ticket DAEO-n0wb (W2-92), profile STANDARD (DEC-221). Written by the independent test designer (MR-3) from the
ticket's KPI lines and its sources (DEC-957, DEC-954 Q9c, DEC-859, DEC-860, DEC-424, CAP-12, CAP-13, CAP-18;
MEMORY-SPEC-MAP §A.2 gaps 2 and 3), before the implementation exists and without reading it. Expected answers come
from the KPI lines, the public interfaces as they stand on `w2/integrate`, and the base's own answers through them.

## How they run (DEC-732)

    TMPDIR=/tmp/gov-os-lead-W2-92 PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-92 -q -p no:cacheprovider

- **The code under test is the running tree's `src/`.** `w2_92_support.SRC` is `src/` of the worktree that holds this
  folder (`Path(__file__).parents[2]`). Every call of `gov.retrieval.retrieve.retrieve`, `gov.retrieval.lexical`,
  `gov.store.load` and `gov.codeintel`, and every `gov retrieve --json` (`python -m gov.cli.main`), runs in a child
  process whose `PYTHONPATH` is that `src/` alone. Merged into the ticket's worktree and run from there, the suite
  exercises that worktree's code.
- **Nothing of this repository is read or built.** Every project is a temporary git repository built from nothing
  (`build_project`): a register, six records, a lesson, plain pages and three small Python files. Its lexical index
  (`gov.retrieval.lexical.refresh`), record graph (`gov.store.load`) and code index (`gov.codeintel.index`, the
  real `codebase-memory-mcp`) are built in the temporary folder. No vector is built, so the semantic route is
  unavailable (as today it says: `facets.semantic = {available: false, reason: missing}`). No reranker, an empty
  `HOME`, a dead embedder port, offline model hubs. No network.
- **The code-graph tool is reached through a stand-in on `PATH`** named `codebase-memory-mcp`, written per call into
  the session's temporary folder. The *recording* stand-in passes every start of the binary on to the real tool and
  writes one line per request: a `cli <tool> <json>` call by its arguments, and in the server form (MCP over stdin and
  stdout, the form `gov.codeintel` uses for one session of the tool, DEC-561) each `tools/call` message by its tool
  name and arguments; an answer that is the tool's refusal over its cap is recorded too. The *broken* stand-in
  records that it was started and exits 1 (an index the tool cannot read). A third form leaves the tool off `PATH`.
- **Needs** `gitleaks` and `codebase-memory-mcp` on `PATH`; without either the whole suite skips with that reason (the
  `api` fixture). It cannot run inside a worker's sandbox: the wrapper's daemon folder `/tmp/gov-cbm-<uid>` is
  read-only there (W1-20's note). The daemon folders of the planted roots are removed at the end of the session,
  each only when it holds the tool's own folder of plain files (as W1-20 does).
- About 60 s on this machine.

## "Today's bundle"

Two forms, both valid once the implementation lands:

1. **Pinned** (`test_w2_92_unchanged.py::TODAY`): the bundle the base `7ca16b19df3f` gave for the same planted project
   and the same call, recorded by the test designer through `retrieve(...)` and written into the test as a literal.
   The planted project is fixed (fixed dates and authors), so chunk ids are the same in every build. Compared: the
   evidence item for item (`chunk_id`, `path`, `start_line`, `end_line`, in order), `batches`, `merge`, `expansions`,
   `gaps`, `budget`, `stopping_reason`, today's two facets (`lexical`, `semantic`), whether a continuation is given,
   and the page that continuation gives. **Not compared:** the bytes of the continuation token (its form is the
   implementation's; what it continues to is compared) and facet keys other than today's two (package P-3).
2. **Live** (`test_u2`): the plain question's evidence is the plain fused order of the lexical route, the only route
   of today that answers in these projects (`gov.retrieval.lexical.search` then `gov.retrieval.fusion.rrf`, as W2-87
   does), and the pinned answer is that order.

Facts of the base, observed through the public interface and used by the tests:

- The lexical route matches every word of the question. A question holding an id (`DEC-301`, `CAP-77`, ...) or a word
  no planted record holds gets an **empty bundle** today, so a named record's evidence in the bundle comes from the
  new route. The planted records' texts share no word with the questions that name them.
- A project whose record graph was never loaded refuses every question with `STORE_MISSING` today, including a plain
  one (W2-87's authority order reads the record graph).
- Today's per-route state is `facets.<route> = {"available": bool, "reason": str | null}`; with `--id <symbol>` and no
  answer from the code index it is `facets.closure = {available: false, reason: "the code index did not answer ..."}`
  and the stopping reason `FACET_UNAVAILABLE`.
- `gov.codeintel`'s `callers` asks the tool `query_graph` with `MATCH (n) RETURN ...` and `MATCH (a)-[r]->(b) RETURN
  ...`: the whole graph, in pages of 50,000 rows. The recording stand-in names those whole-graph queries.

## KPI lines, tests and red reasons at the base `7ca16b19df3f`

Red run at the base, outside the sandbox: **30 tests, 17 failed, 13 passed**.

| KPI line | Tests | Red at the base because |
|---|---|---|
| **Success 1.** An id (DEC-n, CAP-n, a ticket id, a W2 id) or a record title in a plain question becomes a start id; the record closure joins at radius 0 or 1, without `--ticket` or `--id` | `test_w2_92_record_route.py`: `test_r1_a_record_named_in_a_plain_question_reaches_the_bundle` (cases: decision id, contract id, ticket id, W2 id, record title) · `test_r2_at_radius_1_the_named_records_near_records_join` · `test_r4_the_command_takes_the_record_route_of_a_plain_question` · `test_w2_92_code_route.py::test_c3_a_question_naming_both_a_record_and_a_symbol_takes_both_routes` (edge: both) | The bundle is empty (`[]`): the lexical route matches no planted line for a question holding an id or a word the record lacks, and no route links the id or title to its record. |
| Success 1, edge: an id in the question and with `--id` | `test_r3_an_id_in_the_question_and_with_id_is_one_start_id` | **Passes at the base** (a guard): `--id` alone already brings the record once; it must stay once. |
| **Success 2.** A symbol name in a plain question is asked of the code index with the tool's own traversal; its file spans join the fusion; for "who calls X" the callers' spans reach the bundle | `test_w2_92_code_route.py`: `test_c1_who_calls_a_symbol_brings_its_callers_spans` · `test_c3_a_question_naming_both_a_record_and_a_symbol_takes_both_routes` · `test_c4_the_command_takes_the_code_route_of_a_plain_question` | The bundle of `who calls w92_leaf` is empty: `w92_mid` and `w92_side` (`app/middle.py` 4–5, 8–9) are missing. |
| **Failure 2.** A whole-graph query, or one over the tool's row cap | `test_c2_the_code_route_asks_the_tools_traversal_never_the_whole_graph_nor_over_the_cap` · the request checks of `test_c3_a_question_naming_both_a_record_and_a_symbol_takes_both_routes` and `test_c4_the_command_takes_the_code_route_of_a_plain_question` · `test_c5_a_question_naming_no_symbol_of_the_index_sends_no_whole_graph_query` (cases: unknown, none) · premise `test_c0_premise_the_stand_in_sees_a_whole_graph_query_when_one_is_sent` | `test_c2`: "the code-graph tool was not asked about w92_leaf by its own traversal; it was sent []" (no request at all today). `test_c5` (both) and `test_c0` **pass at the base**: nothing is sent today; `c0` shows the detector names a query over every edge and one asking `max_rows` over 100,000. |
| **Success 3 and failure 3.** A missing or unreadable code index or record store is named in the bundle for that route, never silently ok, never a failure of the whole answer | `test_w2_92_fail_closed.py`: `test_f1_a_code_index_that_cannot_answer_is_named_and_the_rest_is_returned` (cases: never indexed, tool cannot read it, tool not on PATH) · `test_f2_the_command_answers_ok_when_the_code_index_is_missing` · `test_f3_a_missing_record_store_is_named_and_the_code_routes_evidence_is_returned` · `test_f4_a_question_naming_no_symbol_does_not_report_the_code_route_ok_or_fail` | f1, f2: "the bundle names no state of that route" (only `lexical` and `semantic` are in `facets`). f1's evidence check is today's lexical evidence for `w92_leaf`, the planted files whose text holds the word: `app/leaf.py` and `app/middle.py` (the base answers exactly these; `app/top.py` only calls `w92_mid`; DEC-1006, P-W2-92-2), so at the base f1 fails on its facet check only. f3: the whole answer fails with `STORE_MISSING` ("no record graph in the store ..."). **f4 passes at the base** (a guard). |
| **Success 4 and failure 1.** A question naming no record or symbol gets today's bundle, item for item; budget, batches, continuation, DEC-424's records ahead as today; two runs give one bundle | `test_w2_92_unchanged.py`: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle` (cases: plain, batched, unknown id, unknown symbol, ticket) · `test_u2_todays_bundle_is_the_plain_fused_order_of_todays_routes` · `test_u3_two_runs_on_one_store_give_the_same_bundle` (cases: new routes, plain) · `test_u4_a_batched_answer_with_a_new_route_continues_to_its_end_within_the_budget` | u1, u2, u3 **pass at the base** (guards: they are today's bundle by construction). `ticket` is DEC-424's records ahead (`--ticket DAEO-hb92`: the lesson that constrains it first). u4: "no page holds DEC-301's evidence: []" (batch size 1, budget 400, the continuation followed to its end). |
| **Success 5 and failure 4** (W2-61's measure re-run: both figures together; the hidden half never read or run) | none | The lead's re-measure record in `docs/research/W2-92-memory-measure.md`, not a test of this suite. |

**How the tests read "named for that route".** `support.route_entries` takes every entry of `facets` other than
today's `lexical` and `semantic` (today's form of a route's state), and every entry of any other top-level mapping
or list whose key holds `stopping` or `route` (a per-route stopping-reasons form), whose key or text names the
route: `code` or `symbol` for the code route; `record`, `closure`, `graph` or `store` for the record route. At least
one such entry must say unavailable (`available: false` with a reason, or a reason in words such as missing,
unreadable, unavailable, failed), none may say available or ok, and the bundle's stopping reason may not be
`SATURATED` or `CLOSURE_COMPLETE`. The exact form is package P-2.

**W2-87's authority order** is not repeated here: the planted path map has no `retrieval_authority` block. The lead
re-runs `tests/acceptance/W2-87`, `W1-21`, `W1-19` and `W1-42` for "nothing else changes" (some of their questions
may hold ids or symbol-shaped words; see Risks in the return).

## Packages (the KPI lines were not clear; the tests follow the recommendation)

- **P-1. A missing record store and a question that names no record.** Today such a project refuses every question
  with `STORE_MISSING` (W2-87's order reads the record graph). Success 3 says a missing store never fails the whole
  answer; success 4 says nothing else changes. Tested: a question naming a record *and* a symbol (`test_f3`) must
  answer with the code route's evidence and name the record route unavailable. Not tested: a plain question in such
  a project. Options: (a) any question answers, the record route (and W2-87's order) named unavailable; (b) a
  question naming no record keeps today's `STORE_MISSING`; (c) `test_f3` too keeps `STORE_MISSING` (the KPI line
  then reads "the store" as the code index's alone). Recommendation (a), if the lead accepts W2-87's order falling
  back to no tiers when the graph is missing; otherwise (b). Confidence medium-low.
- **P-2. The form of a route's stopping reason.** Today's form is `facets.<route> = {available, reason}` with the
  bundle's one `stopping_reason`. The tests accept that form (recommended: `facets.code`, and `facets.closure` or
  `facets.records`, with `stopping_reason` `FACET_UNAVAILABLE`) or a per-route list or mapping of stopping reasons.
  Confidence medium.
- **P-3. New facet keys in today's bundle.** Whether a question that names no record or symbol may gain a facet
  (`facets.code = {available: true}` or "not asked") without counting as "a different bundle". The tests compare
  today's two facets only and ignore added keys; they also fail if a project with no code index reports the code
  route ok (`test_f4`). Recommendation: allowed, and best left out. Confidence medium.
- **P-4. Radius.** The tests need the named record at the default radius 0, and its near records with `radius=1`
  given. Confidence medium-high.
- **P-5. A ticket id in a plain question and DEC-424.** Whether a ticket named in the question brings its failure
  and lesson records ahead, as `--ticket` does. Not tested; recommendation: no (an id found is an `--id`, not a
  `--ticket`). Confidence low-medium.
- **P-6. The pinned answers.** A later ticket that changes today's bundle for these planted questions (W2-13 holds
  the fusion, W2-55 what is left out) changes `TODAY` by a test designer's revision under that ticket's decision.

## Files

- `w2_92_support.py`: the planted project, the stand-ins, the child-process driver, and the bundle readers.
- `conftest.py`: the session fixtures (`api`, `planted(kind)` for `full`, `nocode`, `nostore`, and `asked`, which
  asks a question once per session).
- `test_w2_92_record_route.py`, `test_w2_92_code_route.py`, `test_w2_92_fail_closed.py`, `test_w2_92_unchanged.py`.
