# HOLDS-REVIEW-1: every rule still in force that holds a lead, a close or a test run beyond the gate's capacity check

For the owner's review (DEC-961 item 4), 2026-10-30 23:55 GMT. "The gate" is `tools/gate_check.py` after DEC-961: load (the 1-minute and 15-minute loads both under the processor count) and memory (the floor, each running lead at what it uses, the newcomer). A full run asks the gate for room for its own peak before it starts.

## A. Holds that make work wait while the machine has room

| # | Rule | What it holds | Where it came from | Where it is enforced | Note |
|---|---|---|---|---|---|
| 1 | One full run at a time: closes' and leads' full runs share one lock | a full run waits while another runs, even with room for both | DEC-905, DEC-906 item 3, DEC-954; kept by DEC-953 §5 practice 2 ("one run at a time under one lock") | `tools/verify_lock.sh`, `tools/close_build.py` | The nightly no longer takes it (DEC-961). It was a guard against memory and load collisions, which the gate now checks itself. Candidate to end. |
| 2 | Closes take the lock ahead of leads' full runs | a lead's full run waits while any close wants the lock | DEC-954 | `verify_lock.sh` (the wants-lock flag) | Only matters while rule 1 stands. |
| 3 | One store rebuild at a time on the machine | a rebuild waits for any other rebuild (they take 5 to 40 minutes) | DEC-939 item 2 "until W2-76 lands"; **listed as ended by DEC-953** (LIFTED §C) but still applied | the common lead brief, `close_build.py`, the nightly, my tools | W2-76 is building it into the product as a machine-wide lock. Contention for the code-graph daemon and gitleaks was a measured failure cause. Decide: keep until W2-76 measures it, or end now. |
| 4 | No two tickets in flight with overlapping paths (unless split by file) | a ready ticket waits for a running one that edits the same files | DEC-786, DEC-847, DEC-942 | by hand at claim | W2-20 and W2-37 wait behind W2-16 (`src/gov/check/commands.py`). Prevents merge conflicts. |
| 5 | Launches staggered by 2 minutes, and the chain waits up to 10 minutes for the new lead to be counted | the next launch | DEC-946 item 8 | `tools/lead_chain2.sh` | It lets the gate see the new lead's memory before the next start. |
| 6 | One writing worker per worktree | a ticket's second writing worker | the prompt §3 and §4 | the briefs | Prevents two sessions editing one tree. |
| 7 | Dependencies closed, Definition of Ready checked by hand at claim | a ticket whose dependencies are open | DEC-944 item 2, DEC-786 (stacking) | by hand (`dor_hand.py`) | |
| 8 | "Nothing else starts": only EXAMIN's minimum, in the standing priority order | tickets outside the minimum | DEC-946 items 1 to 6, DEC-954's order | by hand | |
| 9 | Sequencing decisions | W2-100 and W2-101 after ACT 2 (DEC-959 item 4); W2-98, W2-99, W2-103 after W2-11 r1; W2-102 after W2-16; EXAMIN's copy at K9 (DEC-954 Q1); W2-78 parked (DEC-954 Q5) | the decisions named | ticket files, by hand | |
| 10 | Closes test on the head before ACT 1 until W2-90 lands (`CLOSE-HEAD`) | the closes of W2-85 and W2-51, whose merges are after that head | DEC-955, DEC-957 | `close_build.py` | Ends when W2-90 merges. |
| 11 | A loop that does not converge in three iterations goes to the owner | a ticket's fourth iteration | DEC-096 | the lead | Not capacity; listed for completeness. |
| 12 | A FULL ticket's independent review before its merge, at most two per round | the merge | DEC-137, DEC-413, DEC-916 | the lead | Not capacity. DEC-959 moves it to the QA engineer per stream, in batches. |

## B. Floors and budgets the owner kept (capacity-like, outside the gate's line)

| # | Rule | Where it came from | Note |
|---|---|---|---|
| 13 | The disk floor: 100 GiB and 10,000,000 inodes free, or no launch, run or close | DEC-898, DEC-899 item 5; kept by DEC-953 practice 8 | `disk_gate.sh`; today 876 GiB free. |
| 14 | Scratch budgets per session (30 GB and 2 million files for an auditor, trial or research session; 20 GB and 1 million for a lead with its workers); passing one stops the heavy work | DEC-898 | |
| 15 | The memory floor (3 GiB) and the trip-wire (6.4 GiB after an out-of-memory kill or under 2 GiB free) | DEC-947 item 5; kept by DEC-961 | `oom_watch.sh` |
| 16 | The pace of the owner's usage allowance | DEC-847 | |
| 17 | No long foreground work in the CTO's session from 07:15 to 07:35 | DEC-951 B | My session only. |

## C. Found while sweeping: rules DEC-953 had lifted that the tools still enforced (my slips)

- **The memory arithmetic as a gate** (LIFTED §D: "Until whole") was still enforced by `gate_check.py`. That included the reserved verification peak that DEC-960 corrected and DEC-961 removes. DEC-961 now keeps the floor, the trip-wire and the working size per lead by the owner's word.
- **The CLOSE-PENDING hold and the 00:30 to 05:30 window** (LIFTED §C) were still in `lead_chain.sh` and `lead_chain2.sh`; removed now.
- **The 01:00 cut-off, the close's quiet window and "no suites during the nightly"** (LIFTED §C) were still in the common lead brief; removed now.
- **The interim rebuild lock** (LIFTED §C) is still applied everywhere: rule 3 above, for your decision.
- **The nightly's booking inside its window by its estimate** (LIFTED §C) is still in `nightly.sh`. It holds only the nightly itself. It stays until you decide, since the nightly folder changes only by a reviewed commit.

## Recommendation

- **End rule 1 now** (and rule 2 with it). The gate now gives each full run room for its own peak, so the lock only serialises runs the machine could hold together.
- **Keep rule 3 until W2-76's lock is measured**, then decide from its figures.
- **Keep rules 4 to 17.** They prevent conflicts or protect the disk and memory, not capacity.
