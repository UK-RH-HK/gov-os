# W2-87 acceptance tests: retrieval ranks by authority

Ticket DAEO-s9qc (W2-87), profile STANDARD. Written by the independent test designer (MR-3) from the ticket's KPI
lines, DEC-952 item 1, DEC-423, DEC-424, DEC-791 item 1, DEC-860, DEC-866, DEC-694, DEC-951 item 5 and CAP-10,
before the implementation exists.

## How they run (DEC-732)

Every call runs this worktree's own `src/`, set per command:

    PYTHONPATH=/home/usain/gov-os-worktrees/W2-87/src python3 -m pytest tests/acceptance/W2-87 -q -p no:cacheprovider

Each call of `gov.retrieval.retrieve.retrieve` and of `gov retrieve --json` runs in a child process whose
`PYTHONPATH` is this worktree's `src/` (`w2_87_support.SRC`), with an empty `HOME`, a dead embedder endpoint and
offline model hubs. Nothing is built in this worktree and this repository's store is never read: every project is
a temporary git repository built from nothing (`w2_87_support.build_project`), its lexical index and record graph
built by `gov.retrieval.lexical.refresh` and `gov.store.load` (never `gov rebuild`), with no vector, so the
semantic route is unavailable and gives no hit. A reranker is either absent (a loader that returns None) or a stub
passed in (it scores a text by how often it holds `quartz`). No network, no embedder, no real reranker.
`gitleaks` must be on `PATH` (the lexical index's secret filter); without it the suite skips.

The planted corpus is the same in every project; only the path map's `retrieval_authority` block (and, for one
case, the register) differs. The register holds a superseding pair (DEC-102's status line supersedes DEC-101),
then DEC-104 to DEC-106 without the matching text, DEC-106 the last by id. Beside it, all carrying the same text
`vermilion beacon clause`: an ADR (`docs/adr/`), a specification (`docs/spec/`), a capability record
(`records/capabilities/`, governing by its record type only), a note (middle tier), an assessment report
(`docs/assessment/`), a test (`tests/`) and a DEPRECATED decision record (always dropped). Six further reports and
one specification carry `cinder gate tally` for the first-call cut.

## Part 1: the register is its entries (`test_w2_87_register.py`)

| KPI line | Test | Red on today's code because |
|---|---|---|
| Success 4: a chunk of the register is ranked as the entry whose span holds it, never as the register as a whole (DEC-952, DEC-866) | `test_r1_the_closure_route_takes_an_older_entry_by_its_own_id` | `ids=["DEC-104"]` gives an empty bundle: today every register chunk takes the id of the last entry by id (DEC-106), so the closure route takes no register chunk unless DEC-106 is reached. |
| Success 4 and failure 2: a register chunk ranked by another entry's status | `test_r2_a_superseded_last_entry_does_not_drop_the_other_entries` | The register's last entry DEC-203 is SUPERSEDED, so today every register chunk is dropped: `merge.dropped` names `docs/DECISION_REGISTER.md` with DEC-203, and DEC-201 and DEC-202 (ACCEPTED) are missing. |
| Success 4 (what the bundle leaves out is unchanged; W2-55's) and failure 4 | `test_r2_a_superseded_entry_that_is_kept_today_stays_kept` | Green today, a guard: DEC-101 (superseded by DEC-102's edge) is kept today because the last entry is accepted; it must stay kept. |

## Part 2: the authority order (`test_w2_87_authority.py`)

The planted blocks are `w2_87_support.CONFIGS`. `main` is the brief's form: tiers `governing` (decision records
with status ACCEPTED, capability records, `docs/contract/**`, `docs/charter/**`, `docs/spec/**`, `docs/adr/**`),
`middle` (the default) and `reports` (`tests/**`, `docs/assessment/**`, `docs/audit/**`, `docs/probes/**`), with a
lift of 0.004 per step on the fused score and 1.0 per step on the reranker's. `flipped` puts the reports tier first
and the governing tier last; `small` is `main` with a fused lift of 0.00054; `absent` has no block. With the
lexical route alone, the plain fused order is the lexical order (path, then line), each chunk scoring
`1 / (60 + rank)`; the tests check that precondition through `gov.retrieval.lexical.search` and
`gov.retrieval.fusion.rrf` before relying on it.

| KPI line | Test | Red on today's code because |
|---|---|---|
| Success 1 and failure 1: every governing chunk (DEC-102, the ADR, the specification, the capability) ranks above every test and report chunk, with and without the reranker | `test_1_every_governing_chunk_outranks_every_test_and_report[no-reranker, stub-alike, cli]` | Today's order is the plain one: the assessment report (`docs/assessment/`) ranks above the specification (`docs/spec/`) and the capability (`records/capabilities/`), by path. The stub scores every text 0, so the rerank keeps that order; the command, with no reranker in its empty HOME, gives the same. |
| Success 2: the order is applied before the first call's cut | `test_2a_a_governing_chunk_just_past_the_first_call_enters_it` | With `batch_size=2` the first call gathers four of `cinder gate tally`'s seven chunks: six reports, then the specification, by path. Today the specification is the seventh and is left out as `NOT_GATHERED`. |
| Success 2: the lift is bounded and its size is configuration | `test_2b_a_lower_chunk_better_by_more_than_the_lift_keeps_its_place` | With a lift of 0.00054 per step (0.00108 between governing and reports), the specification (1/67) overtakes the reports of plain ranks 3 to 6 (at most 0.00095 better) and not those of ranks 1 and 2 (0.00147 and 0.00120 better): the bundle must be r01, r02, the specification, r03. Today it is r01 to r04, the specification not gathered. |
| Success 2: applied again after the rerank, which does not undo it; the lift there is bounded too | `test_2c_the_rerank_does_not_undo_the_order_and_its_lift_is_bounded` | The stub scores the report 3, the test 1 and the rest 0; with a rerank lift of 1.0 per step the report (3 − 1) stays above the governing chunks (0 + 1) and the test (1 − 1) falls below them. Today the rerank alone orders them: the test is second, above every governing chunk. |
| Success 3 and failure 3: the order is configuration, not code | `test_3a_a_path_map_that_puts_tests_above_decisions_flips_the_order` | The `flipped` block puts tests and reports first; today the block is ignored and DEC-102 and the ADR rank above the report and the test. |
| Success 3: with the block absent the bundle is today's, item for item | `test_3b_without_the_block_the_order_is_the_plain_fused_one` | Green today, a guard: the evidence's chunks are the plain fused order, the dropped ones left out. |
| Success 3 and failure 3: a block that cannot be read or holds an unknown tier refuses with `CONFIG_INVALID`, never read as empty | `test_4_an_unreadable_block_refuses_with_config_invalid[not-a-mapping, unknown-default, unknown-key, status-not-a-word]`, `test_4_the_command_carries_config_invalid_in_its_json_error` | Today the block is not read: each call returns a bundle of 8 items, and `gov retrieve --json` answers `ok: true`, exit code 0. |
| Success 4 and failure 2: a superseded entry never outranks its successor and gets no lift | `test_5_the_superseded_entry_ranks_below_its_successor_and_gets_no_lift[no-reranker, stub-alike]` | DEC-101 (superseded by DEC-102's SUPERSEDES edge; its own status line says ACCEPTED) comes first today, by its line in the register, above DEC-102 and every governing chunk. |
| Success 5 and failure 5: two runs on one store give the same bundle | `test_6a_two_runs_on_one_store_give_one_bundle` | Green today, a guard (the whole bundle compared, with the stub reranker, for a full and a cut call). |
| Success 5 and failure 4: nothing else changes; the block changes the order only | `test_6b_the_block_changes_the_order_only[both phrases]` | Green today, a guard: when everything is gathered, the kept chunks, `merge.dropped` (the DEPRECATED ADR), the not-gathered gaps, the stopping reason and the continuation are the same with and without the block. |

Not in this suite: KPI success 5's other half (the W1-19, W1-21 and W1-42 retrieval suites and the close's
regression, run by the lead) and KPI success 6 with failure 6 (W2-61's measure re-run on the visible half, recorded in
`docs/research/W2-87-memory-measure.md` by the lead). DEC-424's failure and lesson records ahead of the rest are
covered by W1-21's `test_w1_21_failure_memory.py`.

## Expected result on today's code

21 tests: 16 fail for the reasons above, 5 pass (the guards: part 1's nothing-newly-dropped, 3b, 6a and both 6b).
