---
task: DAEO-kmcr
decisions_applied: [DEC-954, DEC-1052, DEC-1112]
---
# W2-23 run 4 (resume -> build -> review round 2 on S3): round 2 NOT READY on S3 (R2-1); for the owner (DEC-1010)

Head w2/W2-23 3e7194a45a58, verified: `gov accept W2-23` 29 passed, 0 failed (S3 9 = 2 old + 7 new from td-4b);
W1-41 3 passed; rebuild ok; lead_verify 4024 tests, 7 red: the same 6 W2-96 signal cases in tests/unit/accept as run 3
(environment-dependent, outside this delta) and `tests/unit/retrieval/test_w2_112_shared_reranker.py::test_the_running_service_writes_one_memory_line_per_request`
(timing; 1 passed alone, `log/w2-112-alone.txt`; this ticket touches no src/gov/retrieval).
Review round 2 (rev-2b, Opus high, session 7cd1f104, 1.12 USD; record `log/rev-2b.result.md`): R1 and R2 fixed through
the A8 call path, no other form of Interface item 6 worse, the change only adds matches. **S3 fails on R2-1.** The lead
reproduced it at the head (`r2.py`):
`citations('Did you search legacy/memory?', ['legacy/memory/index.md','legacy/memory/decisions/leg-001.md'], [])` -> `[]`;
`'Is it still in legacy/memory/?'` -> `[]`; `'Should we keep notes/memory?'` (nested store) -> `[]`; with `!` or `.` found.
Cause: `?` is in the folder form's blocking set as a glob character (`_NOT_MORE_PATH_DIR`, safety.py:281), and the glob
reading of `legacy/memory?` matches no store file. Not a regression (the previous head behaves the same). eng-4 named
`legacy/memory?` as a discovery; the lead did not act on it before the review (lesson).

This was the last review round under DEC-1010, so the lead returns it to the owner once and does not open a third round.

## P-W2-23-8: R2-1, a folder citation ending a question
- (a) Fix without a further review round: td adds one S3 case (a folder citation, flat and nested, ending in `?`); eng
  treats a `?` that ends a folder citation (followed by whitespace, closing punctuation or end of text) as a stop, like
  the full stop, in `_NOT_MORE_PATH_DIR` and the glob token handling (about 3 lines). The lead's verification (`gov accept`,
  lead_verify) stands in place of review; the probe record names round 2's verdict and the fix's verification. Cost
  about 1 USD and 45 min. Needs the owner to accept verification in place of review for this one change.
  **Recommended.**
- (b) The same fix with a third review round limited to R2-1 (Opus, about 2 USD). Cost about 3 USD and 1.5 h. Needs
  the owner to allow a third round, which DEC-1010 bars.
- (c) Land as is, R2-1 a Wave 3 row. Decides a FAIL away, which only the owner may do. Cost: A8 can retire a store a
  rule or record still cites by its folder at the end of a question (recoverable from the archive ref).
Recommendation: (a). Confidence: high on the fix (the reviewer gave the same fix, 3 lines plus 1 test), medium on the
process (the owner's call under DEC-1010). Blocks: the probe record and the landing.

## Triage of every round-2 finding
| id | KPI | where | scope / ordinary / consequence | triage |
|---|---|---|---|---|
| R2-1 | S3 | safety.py:281 (with :240, :324-333) | in / yes / fails open | P-W2-23-8 (reproduced) |
| R2-2 | S3 | safety.py:284-301, legacy.py:222-225 | in / yes / other (fails closed, refusal names `docs/`) | row: one A8 run's memory-store entries are one store, so two stores under one broad parent are held back by a bare mention of the parent; the CTO's reading taken literally. The owner may retire the stores in separate runs or reword the rule. |

## Other
- rev-2 (first launch, session 60f93227) ended on `API Error: Can't reach the API server (EAI_AGAIN)` after 13 turns
  with no verdict (0.61 USD); rev-2b was a fresh relaunch at 02:13, not a further round.
- td-4 was refused at the resource gate (memory, DEC-1088 (5)) before any session; td-4b relaunched once the gate opened.
- rev-2b reported one guard refusal: a Write of a probe script into its `TMPDIR`, refused under the quiet-hours rule
  (DEC-991) and queued; it then ran its probes as inline `python3 -c` (no file written). Named for the CTO to judge
  against "never work around a refusal".
