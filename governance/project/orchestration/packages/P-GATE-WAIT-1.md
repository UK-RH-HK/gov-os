# P-GATE-WAIT-1: the batch of ten is starved by the gate; cap a run's wait for room (P1, a change to DEC-961)

For the owner. It changes your standing rule DEC-961 item 1 ("a full run checks the gate before it starts and waits until there is room"), so it is a P1.

## 1. Context
- Since DEC-961, every test run of a close, the nightly or a lead's large run asks the gate for room for its measured peak (`gate_check.py --full-run`): the load (1-minute and 15-minute both under 20 processors) and the memory. Then it waits, with no limit.
- Leads start only when the same gate is open. Once eight are running, their own suites keep the load above 20 for hours.

## 2. What happened (2026-10-31 04:00)
- **The batch of ten** (W2-57, W2-77, W2-03, W2-26, W2-61, W2-85, W2-51, W2-87, W2-64, W2-90) started at 01:58. Its copy was rebuilt by 02:38 and its scoped set selected: 80 targets, with 9 core files and 11 unplaced files named.
- **Since 02:38 it has waited for the gate,** for 82 minutes so far:
  - the load is 35 to 61, from 8 leads plus the nightly;
  - the memory is 19.5 of 21.4 GB needed.
- **It will start only when enough leads end.** That may take hours.
- **Leads face the same.** The common brief's wait before each suite batch (both loads under 20) holds their scoped runs in the same conditions.

## 3. Why it matters
- **Closes:** your aim is that no ticket waits for something it didn't cause. Here ten merged tickets wait for leads that started after them.
- **The machine is not idle,** so nothing is lost in throughput. But finishing comes last, against DEC-946's "finish before you start".

## 4. Options
- **(a) Recommended: a run waits at most 15 minutes for the gate's room, then starts.** The memory floor (3 GiB) and the out-of-memory trip-wire stay as they are, so the machine is still protected; the run may run slower under load.
  - It is one change in `gate_check.py --full-run`: it remembers when each waiting caller first asked, and opens for it after 15 minutes, saying so.
  - It reaches the batch already waiting at the next minute, and also the nightly, which already starts by its latest start.
- **(b) The same cap for closes only;** leads' large runs still wait without limit. This keeps more room for closes, but a lead's verification can stall the same way.
- **(c) No new lead starts while a close is waiting.** This brings back the CLOSE-PENDING hold you ended in DEC-961 item 2.
- **(d) Keep waiting:** the batch starts when enough of the eight leads end, probably mid-morning.

## 5. Recommendation
**(a), confidence medium-high.** The floor and the trip-wire, not the wait, are what protect the machine from running out of memory. A 15-minute cap gives room a chance without starving anything. Classification: ordinary work yes; consequence: other (stalls; nothing fails open).

## 6. What it blocks, and what waiting costs
- **Blocks:** the close of ten merged tickets.
- **With (a):** the batch starts within a minute of the change and should end in about 2 to 3 hours, slower under load.
- **With (d):** it ends hours later. Leads' scoped runs stall the same way.
