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
   **Revised under DEC-1055 (D-4b), P-6:** W2-112 (the shared reranker, merged into `w2/integrate` in D-1) added
   one field to every bundle, `rerank` (`{by, device, reason}`: who scored, or why no one did). "Today" is now the
   integrated code: the pinned bundles are `w2/integrate` `23625eb2aebe`'s (the code W2-92 merged at `ebba014a`),
   recorded by the test designer through the same call. Every field but `rerank` is there exactly as at the base;
   `rerank` is pinned as that code gives it with no reranker (`by: unavailable`, reason `the reranker given could
   not be loaded`, or `nothing to rerank` for an empty bundle). So `rerank` is part of the baseline, not a W2-92
   change, and any other added or changed field, order or content still fails `test_u1`.
   **Revised under DEC-1055 (D-4b) for W2-13's S2** (the fusion receives the lexical route's ranked list, BM25):
   the pins are W2-13's head `d6cba69e`, recorded by the test designer through the same call. The plain question
   (and "unknown id", whose id is in no planted line and names no record, so it adds nothing) gives the six pages
   that hold the phrase, then the three chunks BM25 finds for its words (`README.md`, the register's head, the
   lantern note); the batched pages and their continuation follow that order; the ticket's lesson and ticket chunks
   come in BM25 order, the lesson still first (DEC-424). Every other field is as before, and any other change
   still fails `test_u1`.
2. **Live** (`test_u2`): the plain question's evidence is the plain fused order of the lexical route, the only route
   of today that answers in these projects (`gov.retrieval.lexical.search` then `gov.retrieval.fusion.rrf`, as W2-87
   does), and the pinned answer is that order. Since W2-13's S2 the route's list for the fusion is its `ranked`
   list (else its `hits`), as `retrieve` takes it (`Api.plain_order`). `test_f4` holds the no-code-index answer to
   the same order (before: its length, the six pages).
3. **The budget** (`test_u4`, revised under DEC-1055 for the CTO's decision P-W2-13-R3 (a)): DEC-419 DP-3, W1-21's
   approved spec, has the bundle budget bound parent expansion only, never dropping a child hit. Each page carries
   the budget asked for, and a page that names an expansion is within it; a page whose gathered chunks alone pass
   the budget (W2-13's longer lexical list does, at 400) is not cut and expands nothing. Before, each page's whole
   bundle had to be within 400. Whether the budget should bound the whole bundle is W2-32's S5, with its own tests.

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
| **Success 4 and failure 1.** A question naming no record or symbol gets today's bundle, item for item; budget, batches, continuation, DEC-424's records ahead as today; two runs give one bundle | `test_w2_92_unchanged.py`: `test_u1_a_question_naming_no_record_or_symbol_gets_todays_bundle` (cases: plain, batched, unknown id, unknown symbol, ticket) · `test_u2_todays_bundle_is_the_plain_fused_order_of_todays_routes` · `test_u3_two_runs_on_one_store_give_the_same_bundle` (cases: new routes, plain) · `test_u4_a_batched_answer_with_a_new_route_continues_to_its_end_within_the_budget` | u1, u2, u3 **pass at the base** (guards: they are today's bundle by construction; since the D-4b revision u1 is pinned to `w2/integrate` `23625eb2aebe`, where it passes, W2-112's `rerank` included). `ticket` is DEC-424's records ahead (`--ticket DAEO-hb92`: the lesson that constrains it first). u4: "no page holds DEC-301's evidence: []" (batch size 1, budget 400, the continuation followed to its end). |
| **Success 5 and failure 4** (W2-61's measure re-run: both figures together; the hidden half never read or run) | none | The lead's re-measure record in `docs/research/W2-92-memory-measure.md`, not a test of this suite. |

## KPI line S6 (DEC-1065 (4)), tests and red reasons on the integrated code `eb28c40866af`

Added under DEC-1065 by the test designer (D-4b round, `DAEO-n0wb`), from the KPI line alone and the integrated
code's public interfaces. The time figure (a cold `gov retrieve` on this repository's store within about 1.2 s at
the median of ten) is the CTO's measure on the shared servers, not a test. The tests check the cause and the
guard: in a planted project with many records (`MASS` = 240 besides the harbour's; no code index, the code-graph
tool off `PATH`), one `retrieve` in a new process counts the planted records' files it opens (an audit hook on
`open`) and the front matters it parses (the YAML module's load functions wrapped), both switched on around the one
call only. `test_s6c` compares this worktree's bundles with the integrated code's (`BASE`, its `src/` taken by
`git archive` into the session's folder), item for item, with `support.projection`. Runs inside a worker's sandbox
(no code index is built). About 60 s.

Red run on `w2/integrate` `eb28c40866af`, in the sandbox: **15 tests, 3 failed, 12 passed** (about 35 s). A check
of the tests themselves: with the integrated record route changed to read no file (titles of records outside the
register then empty), `test_s6a` passes (nothing else in `retrieve` opens the many records) and `test_s6c` fails on
its two title cases (it sees the change).

| KPI line | Tests | Red on the integrated code because |
|---|---|---|
| **Success 6.** A plain question costs about one second: the record route no longer parses every record's front matter in each process (the titles kept in the store at rebuild) | `test_w2_92_speed.py::test_s6a_a_plain_question_does_not_read_every_records_front_matter` (cases: plain, unknown id) · `test_w2_92_speed.py::test_s6a_premise_the_counter_sees_a_record_read` · `test_w2_92_speed.py::test_s6b_a_title_is_the_one_the_store_was_built_with` · `test_w2_92_speed.py::test_s6b_after_a_rebuild_the_new_title_is_the_stores` | `test_s6a` (both cases): "one plain question opened 240 of the 240 planted records' files (at most 12 allowed)": `graph_route.start_ids` reads every record's title from its file and parses its front matter in each process. `test_s6b_a_title_is_the_one_the_store_was_built_with`: the bundle is empty (`[]`): the title is read from the working tree's file, which the edit after the load changed, not from the store (the store holds titles of register entries only). Its premises hold there: after the edit the lexical index is refreshed and fresh, and the lexical route alone finds nothing for the old title, so only the record route can bring the record (revised under the CTO's decision P2, DEC-342: before, the edit left the index stale, and a stale index cites nothing whatever the title's source). Checked in a scratch copy, never committed: the integrated record route made to read titles as committed (`git show HEAD:<path>`) passes both `s6b` cases. **The premise and `test_s6b_after_a_rebuild_the_new_title_is_the_stores` pass** (guards: the counter counts one open and one parse for one record read; a committed title change and a rebuild move the title). |
| **Success 6 with success 4.** Nothing else in the bundle changes; S1's record route answers as before | `test_w2_92_speed.py::test_s6c_the_record_route_answers_as_the_integrated_code_does` (cases: plain, unknown id, decision id, contract id at radius 1, ticket id, W2 id, record title, a many-records title, ticket, batched) | **Passes on the integrated code** (a guard, by construction): any change to an item, its order, or a field outside the evidence fails it. |

- **S6-P1. Where the titles come from.** The KPI line allows "the titles kept in the store at rebuild, or read only
  when a question names a record"; the CTO's brief for this round says the titles come from the store after a
  rebuild. `test_s6b_a_title_is_the_one_the_store_was_built_with` follows the brief: a title edited in the working
  tree after the load is not read. A reading that opens a named record's file when a question names it by title
  fails that one test. Confidence medium.
- **S6-P2. A W2 id in the question.** The integrated code reads every ticket's front matter (by pattern, not YAML)
  to resolve a W2 id, since a ticket's W2 id is not in the store. That question names a record, so S6 (a plain
  question) does not bound it; not tested.
- **S6-P3. The pinned base.** `BASE` is the integrated code at this round. A later ticket that changes these
  bundles (as P-6) moves `BASE` by a test designer's revision under that ticket's decision.

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

## KPI lines S7 to S10 (DEC-1074 (5), LINK-INTEGRITY §6.1), tests and red reasons on the integrated code `8c28aa70fb3f`

Added under DEC-1074 (5) by the test designer (re-pin window 4, `DAEO-n0wb`), from the KPI lines, the failure line
"a partial supersession that drops its target from what is current; a register chunk in a bundle without its
status", the census's forms and patterns (`docs/research/D4B-link-census.md` §0–2, §4 and its script's patterns)
and LINK-INTEGRITY §2.2, never from the prototype. "Today" is `w2/integrate` `8c28aa70fb3f`, the tree merged into
this branch at `436a7520` (`support.LINKS_BASE`, its `src/` taken by `git archive` into the session's folder).

- **The marina** (`support.links_corpus`): a project of its own, so the harbour's pinned bundles do not move. Its
  register states `**Under:**`, `**Changes:**`, `**Changed by:**`, `**Amends:**`, `**Supersedes:**` naming a part,
  `**Supersedes:**` naming ids alone on a later line (no edge today), `**Supersedes:**` ids alone on the status line
  (today's edge), `**Replaces:**`, `**Changed by:** superseded by` and a free-text "superseded by"; one entry each
  PROPOSED, REJECTED, WITHDRAWN and SUPERSEDED; DEC-432, four chunks long, changed twice. Its tickets state
  `sources:` and `closes:` (DAEO-lk03 cites twenty decisions), DAEO-lk02 `depends_on` DAEO-lk01, a checkpoint
  `task:`, a close record `task:`, `decisions_applied:` and `requirements_implemented:`, a spec `decisions:`, a
  change record `decisions_carried:`, `decisions_recorded:` and `decisions_read:`. Every record's text uses words no
  other record and no question holds. The expected links are `support.STATED` (the census's direction: the changer
  to the changed decision).
- **Built twice** in the session's folder, the same commit: by this worktree's code (`marina`) and by the integrated
  code (`marina_at_base`); lexical index and record store; no vector, no code index, the code-graph tool off `PATH`,
  no reranker, an empty `HOME`. Never this repository's store. Runs inside a worker's sandbox; about 12 s.
- **The questions are titles alone.** The record route reaches the record by its title; no id is in the question,
  so the lexical route's id boost (W2-13) brings no chunk that names the record's id. Each S8 case first checks that
  today's bundle holds the named record and not the hop's record.

Red run on `8c28aa70fb3f` (this branch's `src/`, identical to it), in the sandbox through the heavy slot, with the
exclusions of `EMG-d4b-launched.md` (they leave none of these out): **71 tests, 51 failed, 20 passed** (about 11 s).
Every red fails on its KPI's own assertion, none on a premise. The 20 that pass are guards, named below. A check of
the readers themselves (in a scratch run, not committed): a register chunk with fields (`status`, `in_force`,
`changed_by`), with an entry keyed by its id outside the evidence, or with a header line in its text, gives no S9
fault; a row `("CITES", "DAEO-lk01", "DEC-411", ...)` reads as CITES and not the other way round.

| KPI line | Tests | Red on the integrated code because |
|---|---|---|
| **S7.** The stated links kept at rebuild, in a table of their own outside the digest: the front-matter id keys as CITES, `task` as OF_TASK, `**Under:**` as UNDER, a supersession naming ids alone as SUPERSEDES, every other supersession or amendment as AMENDS, by the census's patterns in one function (`register_statements`); the closure, `gov dangling` and every reader of edges unchanged | `test_w2_92_stated_links.py::test_s7_each_stated_link_is_kept_as_its_type_in_a_table_of_its_own` (cases: each of the 21 forms of `support.STATED` but the twenty sources) · `test_w2_92_stated_links.py::test_s7_a_tickets_twenty_sources_are_each_kept` · `test_w2_92_stated_links.py::test_s7_the_census_patterns_are_one_function_register_statements` · guards: `test_w2_92_stated_links.py::test_s7_a_supersession_of_ids_alone_on_the_status_line_stays_todays_edge` · `test_w2_92_stated_links.py::test_s7_the_store_digest_is_unchanged` · `test_w2_92_stated_links.py::test_s7_every_reader_of_the_graph_answers_as_today` (cases: edges, gov dangling, records) · `test_w2_92_stated_links.py::test_s7_the_closure_is_unchanged` (cases: five start sets at depth 1 and 3) | Each form: "the store has no table the integrated code's store lacks: the stated links are kept nowhere". The twenty sources: none kept as CITES. `register_statements`: "defined 0 times in src/gov". **The guards pass** (by construction): today's edge DEC-445 → DEC-446, the digest, `edges`, `gov dangling`, `records` and the closure equal the integrated code's on the same commit. |
| S7, "on this repository's register they match the census's statements one for one" | none: the CTO's measured check on this repository's store, **verified by the evidence file** (`docs/changes/W2-92-evidence.md`) | n/a |
| **S8** and the failure line's first half. From what the record route or the closure reached, one hop: CITES, UNDER and OF_TASK out, AMENDS and SUPERSEDES in, at most 12 records, after today's closure chunks; a question that reaches no record gets today's bundle; a partial supersession never drops its target from what is current | `test_w2_92_hop.py::test_s8_a_reached_record_brings_its_stated_links_in_one_hop` (cases: a ticket's sources, a ticket's closes, a checkpoint's task, a close record's three keys, a spec's decisions, a change record's three keys, a decision's Under, a changer stated on the changer, a changer stated on the changed entry, Amends, a partial supersession by Supersedes naming a part, one in free text, a whole supersession by Replaces, by Supersedes on a later line, by Changed by superseded by, from a record the closure reached) · `test_w2_92_hop.py::test_s8_a_partial_supersession_never_drops_its_target` (cases: Supersedes naming a part, free text) · `test_w2_92_hop.py::test_s8_one_hop_brings_at_most_twelve_records` · `test_w2_92_hop.py::test_s8_the_hop_comes_after_todays_closure_chunks` · guards: `test_w2_92_hop.py::test_s8_the_hop_follows_each_link_its_one_way_once` (cases: CITES not in, AMENDS not out, UNDER not in, OF_TASK not in, one hop not two) · `test_w2_92_hop.py::test_s8_a_question_reaching_no_record_gets_todays_bundle` (cases: plain, unknown id, batched) | The hop's record is not in the bundle: e.g. "a ticket's sources: the bundle for 'Quayside winch overhaul' (reaching DAEO-lk01) does not bring ['DEC-411'] in one hop" (today's bundle holds the ticket and DAEO-lk02, by depends_on). The partial supersessions: the target stays (its text in the bundle, not dropped, not marked) but "its changer DEC-436 is not brought". At most 12: "brings none of DAEO-lk03's twenty sources". After the closure: "the hop brought nothing". **The guards pass** (by construction). |
| S8, "adopted only under DEC-1071's rule (all 80 not lower, the halves' gap not wider)" | none: the CTO's measure, **verified by the evidence file** | n/a |
| **S9** and the failure line's second half. Every register chunk a bundle carries names its entry's status word and the entries that change it; a PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED decision is marked not in force | `test_w2_92_status.py::test_s9_every_register_chunk_names_its_status_and_its_changers` (cases: a long entry changed twice, every chunk; the same, its chunks alone (no parent); PROPOSED; REJECTED; WITHDRAWN; SUPERSEDED; in force though superseded in part; guards: in force though superseded in part, in free text; in force, changed by nothing) | DEC-432: "its chunk at lines 65-78 does not name its status ACCEPTED", the same for its other later chunks, and every chunk "does not name the entries that change it: ['DEC-431', ...]" (DEC-431's `**Changes:**` stands in DEC-431's entry only). Each status not in force: "DEC-451's chunk ... is PROPOSED and not marked not in force". DEC-437: "does not name the entries that change it: ['DEC-436']". **The two guards pass**: DEC-438's own text names its changer and its status; DEC-455 is in force and changed by nothing. |
| **S10.** The drift count before and after, by the census's definitions, in `docs/research/W2-92-memory-measure.md` | `test_w2_92_drift.py::test_s10_the_measure_record_holds_the_drift_count_before_and_after` (the record holds the section; the counts themselves are the CTO's measure, **verified by the evidence file**) | "W2-92-memory-measure.md has no section whose heading names drift". |

**How the S9 tests read "names" and "marked not in force".** What an agent is told about a register chunk
(`support.what_the_item_says`) is its text, every field of its evidence item beyond its place (`path`, the lines,
`id`, `chunk_id`, `sha256`, `routes`, `batch`), and any entry outside the evidence that names the chunk or its entry
(a mapping keyed by either, or a listed entry holding either). "Names its status" is the status word in capitals
anywhere in that; "names a changer" its id. "Marked not in force" is a field `not_in_force: true` or `in_force:
false` (`_`, `-` or a space between the words), else the words "not in force"; an entry in force must not be so
marked. The planted texts hold none of these words.

- **S7-P1. The table's form.** The KPI names neither the table nor its columns. The tests take any table the
  integrated store lacks, and read a row as a link when one cell is the type (any case) and it holds the source and,
  after it, the target, as `edges` orders them. A table that stores the target before the source fails. Confidence
  medium-high.
- **S7-P2. Direction.** AMENDS and SUPERSEDES run from the changer to the changed decision (S8's "in (from the
  changed decision to its changer)", the census's `source`, and the loader's SUPERSEDES edge), whichever entry states
  the link (`**Changes:**` on the changer, `**Changed by:**` on the changed). Confidence high.
- **S7-P3. Whole or part.** By the census's `alone` rule: `**Supersedes:** DEC-437 (2)` names a part (AMENDS);
  `**Replaces:** DEC-442`, `**Supersedes:** DEC-444` and `**Changed by:** superseded by DEC-455` name ids alone
  (SUPERSEDES); free text is never whole in the census (AMENDS). A `**Supersedes:**` of ids alone on the status line
  stays today's edge; whether the table holds it too is not tested, only that it is never AMENDS. Confidence
  medium-high.
- **S7-P4. `register_statements`.** Tested only as exactly one definition of that name in `src/gov`; its signature
  is the implementation's (W2-129 reads it). Confidence medium.
- **S8-P1. The hop's directions.** The guards hold the KPI's words strictly: a cited decision does not bring the
  ticket that cites it, a changer does not bring the decision it changes, a governing decision does not bring the
  decisions under it, a task does not bring its checkpoint, and the hop is one step. Confidence medium-high.
- **S8-P2. "After today's closure chunks."** Read as the evidence order: every chunk of a record today's closure
  reaches comes before every chunk the hop brings (no reranker). Confidence medium.
- **S8-P3. Whole supersessions.** The tests do not say whether a decision superseded whole by a stated link (not an
  edge) becomes not current; only that its changer is brought, and (S9) that a SUPERSEDED status word is marked.
  Confidence medium.
- **S9-P1. The form of the mark.** A per-item field is recommended: a new top-level key of every bundle would change
  `test_w2_92_unchanged.py`'s pinned bundles (`test_u1`, `test_u3`), which include register chunks. Confidence medium.

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
- `test_w2_92_speed.py`: S6 (DEC-1065 (4)), its many-records project, its counting child process and its fixtures.
- `w2_92_support.py`'s S7–S10 part and `conftest.py`'s `marina*` fixtures: the marina, built by this worktree's code
  and by the integrated code; the store's tables read with sqlite; the readers of register chunks.
- `test_w2_92_stated_links.py` (S7), `test_w2_92_hop.py` (S8), `test_w2_92_status.py` (S9), `test_w2_92_drift.py`
  (S10).
