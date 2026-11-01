# SMART-WORK-2 — today's practices from the CTO's tools mapped into the product's tickets (DEC-1003)

**For the owner: KPI change proposals** (each a P2 within the approved spec unless marked; your yes applies them).
Today's practices in the CTO's tools: the merge queue's four speed-ups (DEC-1001 (a) to (d)), merge and close in one
step (DEC-989), the attribution baseline (DEC-988, DEC-989). Already mapped earlier today: the approvals discipline and
the quiet-hours hook (W2-11 round 2, W2-33, W2-113; DEC-994); the dead-man's switch as a product feature (Wave 3
parking, DEC-994: a row to file with this package).

| # | Practice (CTO's tool) | The product today | Ticket | Change |
|---|---|---|---|---|
| a | A record-only head move re-runs only the record-reading tests (`merge_queue.py`) | No | W2-117 (the queue in the product), W2-115 (the selection) | new line; amend S2 |
| b | Warm clones between runs (`merge_queue.py`; to `close_build.py`) | No: every run clones fresh | W2-117, W2-115 | new line each |
| c | The baseline's verdict read from the nightly's own results; same failure, both at the baseline and on the head without the batch; an unknown failure never matches | No: W2-115 S4 traces "with and without the change" (undoing merges, which DEC-988 forbids); S6 takes merges out | W2-115 | replace S4 and S6 (with DEC-1002 item 2) |
| d | Rebuilds share the heavy-job slots; each tree its own rebuild lock (no machine-wide one) | **The opposite:** `src/gov/rebuild/watch.py` (W2-76, closed) defaults to one machine-wide lock | W2-20 (the resource gate; its S7 already names rebuilds in the slots) | amend S7; add `src/gov/rebuild/watch.py` to its paths |
| e | Merge and close are one step: a green queue run lands and closes, with the close record (`land.py`) | Partly: W2-117 S2 has the queue's record cited by the close | W2-117 | amend S2 |

## The KPI lines

**W2-117 (`DAEO-zkr9`, FULL, after EXAMIN's copy)**
- new: `'When the integration branch moved during a run only by record or governance files (the record places and the governance overlay), the queue merges onto the new head and re-runs only the record-reading suites (named in the test map), then advances; any other file in the move re-runs the whole selection; a record-reading set that cannot be read re-runs the whole selection [DEC-1001 (a), DEC-1003]'`
- new: `'The queue keeps its work clones between runs (reset to the head, untracked files removed, the stores kept, so a rebuild is incremental); a clone that cannot be reset is replaced by a fresh one; measured: the rebuild''s seconds per run, warm against fresh [DEC-1001 (b), DEC-1003]'`
- amend S2 to: `'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run; no ticket sits merged but not closed [DEC-989, DEC-959 item 1, DEC-1003]'`

**W2-115 (`DAEO-emq1`, FULL)**
- amend S2: after "records and governance files ... select nothing by themselves" add `"; a change to records alone selects the record-reading suites (named in the test map) and nothing else [DEC-1001 (a)]"`
- replace S4: `'Every failing test is run again alone; a red alone is judged against a known baseline (the last nightly with a verdict until a green one exists, then the last green one), never against code made by undoing merges: it is not the change''s only if the baseline had it red with the same failure (read from the nightly''s recorded results where they hold it, else traced there) and the head without the batch has it red the same way; an unknown failure (a timeout, no record) never matches; otherwise it is the change''s [DEC-988, DEC-989, DEC-1001 (c), DEC-1003]'`
- replace S6 (with DEC-1002 item 2): `'A batch''s culprit is found before anything lands, by building the merged result without each candidate (never by taking merged code out); only the culprits go back and the rest land on the same run; a red no single candidate explains, or a candidate that cannot be isolated, refuses the batch [DEC-979 item 3, DEC-988, DEC-1002]'`
- new: `'The close''s clean clone is a warm one kept between closes (reset, stores kept), replaced by a fresh one when it cannot be reset [DEC-1001 (b)]'`

**W2-20 (`DAEO-r30l`, STANDARD, in progress)**
- amend S7: add `"; a rebuild excludes only another rebuild of the same tree (each tree its own lock), never every rebuild on the machine; the rebuild's peak memory is measured with the re-measure (S9) and counted by the gate like a test run''s [DEC-1001 (d), DEC-1003]"`
- paths: add `src/gov/rebuild/watch.py` (the default lock moves from one machine-wide path to one per tree) and `tests/unit/rebuild/test_w2_20*`. W2-76 is closed; this is the product half of DEC-1001 (d). Changing the behaviour of a closed ticket's code: **a P1 under DEC-105 if you read it as re-baselining W2-76; I read it as W2-20 taking a decided change (DEC-1001), so P2.**

**Wave 3 parking** (DEC-994 item 3): `W3-P16 The dead-man's switch as a product feature: a sentinel session that pushes when the orchestrator's session has stalled (this repository's ACT-SENTINEL-1 as the model); the push channel is the host's, not cron's`.

## Recommendation
Apply all, confidence medium-high; W2-20's change now (it is in progress), W2-115's before it starts, W2-117's with it
after EXAMIN's copy.
