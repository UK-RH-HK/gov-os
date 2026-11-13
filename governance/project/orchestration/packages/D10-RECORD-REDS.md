# D10-RECORD-REDS — D-10's two record reds and W1-01's merges: options for the owner (2026-11-10, CTO 8ddb8b14)

`gov check` must be green or ruled on before the re-pin (owner, 11-10). Both reds were noted at D-10's go (row 110).
Evidence: run 1 (`log/nightly/20261110-1810/serial.txt`, W2-54's `green_here`), `python3 -m gov.close.traceability`
at `c9742b089` (37 s), the ticket files' status lines. Costs are list-price estimates (E) under usage (A).

## 1. `context-reproducibility` (hard-block; W2-54's `green_here` and `time_limit` cases)
**What is red, corrected:** not the tickets over the 6,000-token ceiling. A refusal over the ceiling that reproduces
counts as green (`context_check.py`: "N refused over the ceiling twice alike"); run 1 had 30 such refusals (16 closed
tickets, 14 open or in progress; 6,328 to 23,150 tokens, DAEO-03dg 16,469). The check's verdict was **"0 ticket(s)
failed, 34 error(s)"**: tickets whose mandatory inputs the store cannot find. All 19 tickets named in the visible part
of the message are open (10) or in progress (9). The ids are of two kinds: backlog rows (`W2-H021`, `W2-H015`,
`W2-H018`, `W2-H034`, `W2-H035`, `W2-M176`, `W2-M188`, `W2-M284`, `W2-L233`, `W2-L256`) and WBS ids (`W2-11b`,
`W2-15b`, `W2-24`, `W2-26`, `W2-61h`, `W2-106`, `W2-112`, `W2-129`); one cites `DEC-798` in a state the store refuses.
A live ticket with such an input cannot have its context built (`gov context` errors), so this affects real work.

| option | what | cost | result |
|---|---|---|---|
| **(a) apply now: fix the records** (recommended) | a product-spec worker (C1, Sonnet high) re-points each mandatory input to a record the store holds (the backlog file's row, the ticket file, the live decision) or moves it to optional inputs; the full list of 34 from a store rebuilt at head | ~45 min, ~$5-10 | green in run 2; the 30 refusals stay (allowed) |
| (b) re-baseline the product: the store resolves backlog-row and WBS ids as records | a ticket (engineer Opus high + test designer), CIT-E | 2-4 h, ~$30-60 | green and no recurrence; better after the lift, as the follow-up to (a) |
| (c) defer: rule the red accepted for the re-pin | a DEC naming the 34 errors; fix after the lift | 0 | `gov check` stays red on one family, ruled; those tickets' contexts still fail |

## 2. `product-traceability-trailers` (hard-block; lifted, so it shows only in the lifted step)
**What is red:** 424 findings, every one an October commit (10-01 to 10-30), 66 tickets: 354 commits without an
`Implements:` trailer, 66 whose `Implements:` id resolves to no record, 4 closed tickets with no `Task:` commit. The
check judges the whole history because `trailers_base` (DEC-482: the base `429815b5`) and `accepted_history` were
deleted by D-4 (`c5e9d9625`, row Q-8: "trailers not refusals; the family a warning (after T-3); `traceability.py` an
on-demand report; `accepted_history` and `trailers_base` deleted here"). Q-8's product half, the family becoming a
warning, is in W2-115 (P1-9), after the resume; until then the family is still a hard-block.

| option | what | cost | result |
|---|---|---|---|
| **(c) rule now, as Q-8 already decided** (recommended) | a DEC: the family's red is accepted for the re-pin, being the state Q-8 decided to make a warning; W2-115's switch after the resume | 0 | ruled; no work on the critical path |
| (a) apply now: bring Q-8's switch forward | the family's severity to warning (check declaration and its tests), engineer (Opus high) + test designer (Sonnet high) | 1 round, 1-2 h, ~$15-30 | green (a warning) before the re-pin |
| (b) re-baseline: restore a trailers base | the owner's commit (O) of `trailers_base` at the first commit after 10-30 in `path-map.yaml` | 5 min, 0 | green; reverses part of an approved row (Q-8), so a change to it |

## 3. W1-01's merge rule (DEC-253), 2 cases, a record of the same kind
Three merges settle a README conflict inside `tests/acceptance/` without `Role: independent-test-designer`:
`cade65dfe` (W1-32's README), `04460404e` (W1-19's), `8c512d7e7` (W2-32's, 11-04), each "as the designer settled it".
The fix is the owner's commit (O) adding the three full ids to `path-map.yaml`'s `acceptance_exemptions` (as for the
11-02 decision on `0568d91baf56`), or a ruling. Recommended: the owner's commit (5 min); the CTO prepares the lines.

## What the CTO does on each answer
1(a): one product-spec worker after the lifted step, merged before run 2. 2(c) and 3: the DEC recorded; 3's lines
prepared for the owner's commit. Any (a)/(b) choice is briefed the same day under RUBRIC-2.
