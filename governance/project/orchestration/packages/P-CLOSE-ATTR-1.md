# P-CLOSE-ATTR-1: a close refuses only on a red its change caused (P1, a change to your close rule)

For the owner. It changes a standing rule of yours (DEC-953 §0: "A red that fails alone refuses the close"), so it is a P1 by DEC-957's rubric.

## 1. Context
- A build-phase close (`tools/close_build.py`) runs the ticket's selection on the merged commit, re-runs every failing case alone, and refuses on any case that still fails.
- A close run in full (core changes, every batch) therefore runs the whole suite. It refuses on any red anywhere, including reds that the change did not cause and that would fail without it.

## 2. What happened
- **The batch of five** (W2-57, W2-77, W2-03, W2-26, W2-61) ran in full on the head pinned before ACT 1 (`aafd45c1`). It started at 22:45 with its clone and rebuild, which took 2,057 s. The parallel run took 6,015 s: 17,091 tests, 4 failures, 3 errors. The serial-only cases (104) all passed.
- **Re-run alone,** the reds are:
  - **W1-08:** a close record in no path-map namespace;
  - **W2-66:** two ACT patch files missing from the test map's record-only list;
  - **W2-61:** its question q07 quotes a WBS row that DEC-954's edits changed;
  - **W2-54's time-limit and green-here cases,** load failures that W2-85 routes to the nightly on the current head.
- **None of these is caused by the five tickets' code.** The first three came from my record commits. I have fixed two of them (`730636ba`), and a test designer is fixing q07. The W2-54 ones are load.
- **The batch will be refused anyway** (it is finishing its alone re-runs, about 02:15). The current head also carries W2-90's 7 named reds (P-W2-90-1), which fail alone until W2-105, W2-106 and W2-90's next round land. So under today's rule no full close can pass on the current head before then, and 10 merged tickets wait: W2-57, W2-77, W2-03, W2-26, W2-61, W2-85, W2-51, W2-87, W2-64 and W2-90.

## 3. Why it matters
- **Closes stall on reds that have nothing to do with the change.** Every full close pays a 2- to 3-hour run, only to be refused for an unrelated red.
- **The fix keeps the purpose of the rule:** a change that breaks a test is still refused.

## 4. Options
- **(a) Trace each red to the change (recommended).**
  - Each case that fails alone is run again alone on a second clone of the same head with the batch's merges reverted (`git revert -m 1`, newest first) and its store rebuilt.
  - **Red there too:** not this change's. It is named in the close record under "red without the change too", and added to the nightly's watch.
  - **Green there:** the change caused it, and the close is refused, as today.
  - **Fails closed:** if a merge cannot be reverted cleanly, the red cannot be traced and the close is refused.
  - **Cost:** one more clone and rebuild per close that has reds, about 35 minutes today, about 5 after W2-107. A tool change of about 40 lines in `close_build.py`, tested with `--dry` on the current batch before use.
- **(b) Keep the rule, and close after the known reds are fixed:** W2-105, W2-106 and W2-90's next round, then one batch of all ten. This is about 10 to 16 hours, and any new unrelated red restarts the wait.
- **(c) A list of known reds that closes skip.** This is quicker than (a), but it is a ratchet list (lifted by DEC-953) and it never shows whether a listed red is still unrelated.

## 5. Recommendation
**(a), confidence medium-high.** Classification: ordinary work yes (every full close); consequence: other (stalls; nothing fails open, since a caused red still refuses, and an untraceable red refuses).

## 6. What it blocks, and when the batch can finish
- **Blocks:** the close of all ten merged tickets.
- **With (a):** I remove `CLOSE-HEAD` and run one batch of all ten on the current head. That means a clone and rebuild (about 35 minutes), the full run (about 100 to 120 minutes at load 40), and the alone re-runs with their tracing (about 45 minutes). Started about 02:30, it should end about **06:00 to 06:30**. The nightly runs beside it from 02:00 and shares the machine, so it may be later.
- **With (b):** later today, after W2-105, W2-106 and W2-90's next round.
