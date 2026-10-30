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
