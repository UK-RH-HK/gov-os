# The fresh 80's result: K9's memory bar PASSES (declared in FRESH-80-DECLARATION.md, `16d3d61b`; DEC-1097 (1))

Run on 2026-11-08 by the CTO (session `ad44f5fe`), on the owner's go after the push of `895169fb` and `6eb31751`.
Counts only: no question, label or answer of the 80 is named here. The 80 are now spent (USED written 19:05).

## The verdict (the judged condition only)
**Right end to end: 78 of 79 (98.7 %); wrong claims: 0 of 79 (0.0 %).** The bar (at least 68 right, at most 3 wrong
claims) is **met**; the 95 % target (at least 76) is **reached**. The exact 95 % interval is 93.1 to 100.0 % (Wilson's
93.2 to 99.8 %).
- **Judged:** window 4's pin `pin-bcea09060ebc`, the pool on, today's 6,000-token bundle, search again once (A2), at
  `c00d525f` on E0's clone, E2's reader (`claude-opus-5-5`, effort high, no tools) and graders (opus counts, sonnet
  agrees), the measure's matcher with source families.

## Beside the verdict (data, not judged)
| figure | the fresh 80 (of 79) | expected (FRESH-80-1 §1.4) | the 138 |
|---|---|---|---|
| right end to end, search again once (A2) | **78 (98.7 %)** | about 89 % (80 to 94) | 128 (92.8 %) |
| one search (A1) | 72 (91.1 %) | about 76 % | 115 (83.3 %) |
| up to three searches (A3) | 79 | | 128 |
| hit@5 | 67 (84.8 %) | about 68 % | 106 (76.8 %) |
| hit@10, hit@20, MRR | 70, 74, 0.629 | | 118, 124, 0.567 |
| gold in the first bundle; full evidence | 74; 73 | about 85 % | 123; 116 |
| answer correct, citation aside (A2) | 78 | | 135 |
| the stricter of the two grades (A2) | 77 right, 1 wrong claim (still passes) | | |
| grader agreement | 78 of 80; no grade missing | | 138 of 140 |
- **A1 against A2:** 6 gains, 0 losses, exact McNemar p 0.031: search again once helps on a fresh set too.
- **The one question not right at A2** was "not found", not a wrong answer.
- **hit@5 at 84.8 %** sits just under the old hit@5 bar of 85 % (DEC-1083 (2)), which DEC-1097 (1)(d) replaced.
- **The nonexistent-id question,** apart: the reader was right. DEC-1071 (5)'s `UNRESOLVED_IDS` stop is **not
  applicable**: the product does not read this id form as an id (declared before the run; the figures tool prints
  "no" for that line, a product limit, not a failed stop; code review row D1).
- **Integrity:** 0 failed later searches; 0 citations outside the items the reader received; 0 reader errors; 0 calls
  run once more; the set's digest the same as at the pre-flight; integrate unchanged (`895169fb`) and no store refresh
  over the run; every one of the measure's 407 searches answered by the shared reranker.

## Data only, not judged (FRESH-80-1 §3.4: no figure here chooses anything)
| condition | right (of 79) | wrong claims | against the judged run |
|---|---|---|---|
| top 5, one call (e3) | 56 | 5 | 16 fewer than A1 (p < 0.0001) |
| top 10, one call (e3) | 63 | 1 | 9 fewer than A1 (p 0.004) |
| top 20, one call (e3) | 70 | 0 | 2 fewer than A1 (p 0.5) |
| 40 unranked, one call (e3) | 68 | 1 | 4 fewer than A1 (p 0.13) |
| top 20, search again (e3sa) | A1 69, A2 76, A3 79 | A2 0 | 2 fewer than A2 (p 0.5) |
| 40 unranked, search again (e3sa) | A1 69, A2 75, A3 78 | A2 1 | 3 fewer than A2 (p 0.25) |
| 12,000-token bundle, page 40, one call (e5) | 72 | 0 | equal to A1 (0 and 0) |
| M3 (zerank + gte), one call (e4) | 72 | 0 | equal to A1 (0 and 0) |
| M1 (the 0.6B + gte), one call (e4) | 72 | 0 | equal to A1 (0 and 0) |
| the prototype glossary consulted, search again (e2g) | A1 72, A2 77, A3 77 | A2 0 | 1 fewer than A2 (p 1.0) |
- **On a set used to choose nothing, the 138's findings hold:** the ranked, expanded bundle with search again once is
  best; fewer items answer worse and less carefully (5 wrong claims at the top 5); a doubled bundle and both
  two-model rerankers add nothing end to end (72 each, as today's one call); the glossary as prototyped is one behind.
- **None of these decides anything** (DEC-1097 (5), (6)): M3 stays out; the glossary's redesign is retested on the 138.

## How the run went
- **18:54, the first start:** stopped before any search; the shared reranker had exited after 15 idle minutes and the
  runner checks READY before its own probe (code review row N3, now seen). Not an attempt; the 80 untouched.
- **18:55, the relaunch:** the visible-40 control hit@5 34 (E0's 34); USED at 19:05; the measure one whole attempt, no
  fault (80 question lines, 407 searches, median call 1.3 s, 0 unresolved anchors).
- **19:32, the judged reader run:** 80 rows in 8.2 minutes, $12.46 (projection $15, brake $30).
- **19:40 to 21:46, the data conditions:** in a chain, each dry first. Two stops before any work, both the scripts'
  own guards: E5's live script refused to start outside its own process group (re-run under `setsid -w`); the E4 window
  read the dispatcher's status 5 s after E4's prep had finished its last slot job (re-run after `quiet_wait.sh`). The
  E4 window stopped the live service and restored it by its trap (21:25, `rerank.by` = service, from the pin).

## Cost
| part | cost | projection |
|---|---|---|
| the judged reader run | $12.46 | $15 |
| e3, e3sa, e2g, e5, e4 | $35.25, $15.68, $7.00, $16.99, $21.67 | $36, $19, $14, $17, $22 |
| **all** | **$109.05** | $123 |
The measure, the control, E5's live retrieval and the E4 window used no model tokens.

## What follows (DEC-1097)
- K9's memory line (its home under W2-32 S9) is met; K9's other lines stand (D9-FATES §3).
- After the 80: W2-139 and W2-140 (held until now); Q07 and Q14 re-worded before any re-measure of the 138; the
  rubric's version 3; the glossary's redesign, declared, then retested on the 138; the P2 items (ADR-0002, P-SELECT-GRAPH,
  the 150-id sitting).
- A product row: the product does not read the nonexistent-id form as an id, so DEC-1071 (5)'s stop cannot fire for
  it (lexical `ids_in`); found at the pre-flight.

**Basis:** question 1 (memory judged by what agents answer, on a set used once, the configuration chosen beforehand).
