# PLAN-GROWTH-1: why the plan grew from 89 to 112 tickets, the order to finish, and EXAMIN's readiness

For the owner (asked 2026-10-31). Measured 2026-10-31 at about 13:30 GMT.

## Headline
- **Real growth: 21 tickets, W2-90 to W2-110,** each added by one of your decisions (DEC-957, DEC-959, DEC-966, DEC-969, DEC-971). W2-86 and W2-88 were already rows in the approved WBS (`e814289d`) and were only filed later, so 23 new ticket files in all, and none removed.
- **The 112 also still counts 22 tickets that left the plan:** 19 deferred to Wave 3, W2-78 parked, and W2-79 and W2-80 withdrawn. The live plan is 90 (112 less those 22), W2-00 apart.
- **Where the plan stands:** 33 closed, 5 merged and closing now, 15 in flight and 38 not started.
- **Before EXAMIN's copy can start: 44 tickets** (W2-27 itself not counted). That is about 375 lead-hours at the plan's measured medians.
- **The re-estimate for the copy's start: 2026-11-11 to 2026-11-16, centre 2026-11-13.** The last estimate was 2026-11-12 and the target is 2026-11-18. The cuts in §5 would move it a day or two earlier.

## 1. The tickets added since the plan was approved (DEC-954, `e814289d`, 2026-10-30 18:41)

| Added by | Tickets | What for |
|---|---|---|
| DEC-954 (in the approved plan, filed later) | W2-86, W2-88 | the template embedded as the path map means it; memory for any repository |
| DEC-957 (ACT 1 (a); memory's seven gaps) | W2-90 (closed), W2-91, W2-92, W2-93, W2-94 | the 235 live-wiring tests; full embeddings; graph and code-graph routes; W2-81's hidden half; EXAMIN's question set |
| DEC-959 (ROLES-RESEARCH-1 §5.3; P-W2-H064) | W2-95 to W2-104 (10) | the path-map check; the opaque runner; the merge queue; the spec-writing, benchmarking, release and technical-writing skills; domain skills A and B; the skill harness |
| DEC-966, DEC-967 (P-W2-90-1; speed) | W2-105, W2-106, W2-107 | the template's install block; its hook lines pinned; gitleaks results remembered by content hash |
| DEC-969 (P-W2-54-LOAD-1) | W2-108 | freshness checked once per run |
| DEC-971 (the morning's items 2 and 4) | W2-109, W2-110 | Contract v4.3; a product's CTO-only install rule |

## 2. The WBS and the dependencies of the new tickets
**Every new ticket has its WBS row.** Their dependencies:
- **Correct as filed:** W2-88 (W2-03 closed; W2-52, W2-76, W2-81), W2-91 (W2-86), W2-92 (W2-03 and W2-87, closed), W2-93 (W2-81, W2-84), W2-94 (W2-84), W2-102 (W2-16).
- **No dependencies, rightly:** W2-95 to W2-97, W2-104 to W2-110.

**Gaps to fix (none made; each one ticket-file commit; recommended):**

| # | Gap | The fix |
|---|---|---|
| 1 | W2-90's next round (its 7 named reds, the 14 ids ACT 1 dropped, W1-33 ×4, W1-05 ×2, W2-54's sandboxed case) has no ticket: W2-90 closed | file **W2-90b** (LITE, test designer), depending on W2-105 and W2-106 |
| 2 | W2-98, W2-99, W2-103 "start after W2-11 r1" in their bodies only | add W2-11 as a dependency (round 1) |
| 3 | The six skill tickets (W2-98 to W2-103) must pass their three scenarios before adoption (DEC-959 item 5) | add **W2-104** (the harness) to each |
| 4 | W2-100 and W2-101 "after ACT 2": ACT 2 has no ticket or WBS row | add ACT 2 (the one re-pin, DEC-954 item 6) as a WBS milestone row and name it |
| 5 | W2-27 (EXAMIN's copy) does not list the tickets DEC-959 put "before EXAMIN", nor DEC-966's and DEC-971's template fixes | add W2-61h, W2-86, W2-91 to W2-110 (W2-107 optional) to W2-27 |
| 6 | W2-46 (the exit run) does not list W2-95 to W2-110 | add them |
| 7 | W2-15a and W2-15b have no `wbs_id`, so neither the status block nor the close tool can find them | add their `wbs_id` lines |

## 3. The order: what runs at once, what waits, and how it batches
**What the machine held today:**
- 8 leads at most, 5.1 on average.
- The load stopped launches far more often than memory: 392 load stops against 29 memory stops.
- The 15-minute load averaged 45 against 20 processors. Memory (23 GB) fell as low as 3.6 GB available.
- **So about 6 leads at once** is the realistic capacity, more when leads are between test runs.

**In flight (15 claimed):**
- **Leads running at 13:30:** W2-05, W2-67, W2-95, W2-96, W2-107, W2-108 (6).
- **Queued for the next free slots:** W2-110, W2-105, W2-52, W2-109 (4).
- **Claimed, waiting for a dependency or an answer:** W2-20, W2-56, W2-60a, W2-81, and W2-37 in spare capacity (5).
- **Merged and closing:** W2-16, W2-49, W2-76, W2-84, W2-106 (5 more).

**Ready to start as slots free (no open dependency, no overlap with a running ticket):** W2-86, W2-97, W2-104, W2-11, W2-55 or W2-04 (not both: both hold `src/gov/context/**`), W2-92, and W2-61h and W2-94 (once W2-84's close lands today).

**Waits, and for what:**

| Ticket(s) | Waits for | Why |
|---|---|---|
| W2-60b, W2-82, W2-21 | W2-56 and W2-60a, then W2-20 for W2-21 | the five share `src/gov/launch/launcher.py`: **one chain** |
| W2-13, then W2-32 | W2-108 (`lexical.py`), then W2-13 and W2-92 | retrieval files: **one chain** (W2-32 holds `src/gov/retrieval/**`) |
| W2-04 / W2-55 | each other | both hold `src/gov/context/**` |
| W2-23 | W2-16 (closing), W2-52 | `src/gov/adopt/**` |
| W2-88 | W2-52, W2-76 (closing), W2-81 | its dependencies; then W2-93 waits for W2-81 too |
| W2-83a | W2-52 | the adopt skill's files |
| W2-91 | W2-86 | the path map |
| W2-06 | W2-05 | its dependency |
| W2-33 | W2-11 | the role files |
| W2-98, W2-99, W2-103 | W2-11 r1, W2-104 | after the gap fixes 2 and 3 |
| W2-102 | W2-16 | its dependency |
| W2-100, W2-101 | ACT 2 | DEC-959 item 4 |
| W2-90b | W2-105, W2-106 | gap fix 1 |
| W2-24 (the quality-control repeat, DEC-794), then W2-27 | everything above, K9's criteria, ACT 2 and the three layers | the WBS's Track B |

**How the closes batch** (one scoped run per batch on the merged head, DEC-968):
- **Template and guard:** W2-105, W2-106 (closing), W2-110, W2-90b.
- **Memory:** W2-86, W2-91, W2-92, W2-108, W2-55, W2-04.
- **Then:** W2-13, then W2-32 with W2-61h, W2-93 and W2-94 (the enlarged measure).
- **Roles and launch:** W2-11, W2-33, W2-56, W2-60a, W2-60b, W2-82, W2-21, W2-83a.
- **Speed and checks:** W2-107, W2-95, W2-96, W2-97, W2-104.
- **Skills:** W2-98 to W2-103.

**The two longest chains decide the date:**
- **launch:** W2-56 → W2-60a → W2-60b → W2-82 → W2-21, five tickets, four of them FULL;
- **memory:** W2-108 → W2-13 → W2-15a → W2-32 → the enlarged measure, which must reach 85 %.

## 4. The measured rates
**Closes per day** (when a ticket's status turned closed):

| Day | 10-25 | 10-26 | 10-27 | 10-28 | 10-29 | 10-30 | 10-31 |
|---|---|---|---|---|---|---|---|
| Closes | 0 | 0 | 8 | 0 | 5 | 1 | 10 (5 more closing) |

- **Over the 7 days:** 24 closes, **3.4 a day**.
- **Under the new close rules** (scoped, traced reds, DEC-968): 11 in two days, **5.5 a day**, soon 8 a day with today's five.

**Lead runs:**

| Days | Returns | Lead-hours | Cost (lead sessions, from their own records) | DONE / PACKAGES |
|---|---|---|---|---|
| 10-30 and 10-31 | 33 | 168 (about 84 a day) | $281 (about $140 a day) | 12 DONE (36 %) / 20 PACKAGES (61 %) |

- **Most returns end in PACKAGES,** so a ticket takes about 2 to 3 lead runs on average.
- **The cost figure leaves out** the workers' sessions (the leads launch them separately); no measured total exists for those yet.

## 5. EXAMIN's readiness
**What K9 needs before the copy** (DEC-941, DEC-954 Q1): memory proven at 85 % on the enlarged set; the roles, skills and briefs landed; the proving ground passed (W2-81); W2-88 and W2-16's frozen release; DEC-959's work; ACT 2 and the three layers started (DEC-954's order); W2-24's quality-control repeat (DEC-794).

**How long:**
- **By volume:** 44 tickets at the measured close rate is 8 days at 5.5 a day, or 13 days at 3.4 a day.
- **By the chains:** each of the two chains is about 5 to 6 tickets in series at about a day each (a FULL ticket's median is 13.6 lead-hours plus its close). Then come ACT 2 and the three layers' start (about a day), the domain skills after ACT 2 (1 to 2 days, in parallel), and W2-24's repeat (half a day).
- **So the copy starts 2026-11-11 to 2026-11-16, centre 2026-11-13.** That is a day behind the last estimate (2026-11-12) and still inside the target (2026-11-18).

**What would cut it** (each is your call):
- move W2-100 and W2-101 (domain skills, 700 lines, after ACT 2), W2-99 (benchmarking) and W2-103 (technical writing) to after the copy: about 1.5 days off the end;
- move W2-97 (the merge queue) after the copy; closes work today without it;
- split `launcher.py` by function, so W2-56, W2-60a, W2-60b and W2-82 can run in parallel: up to 2 days off the launch chain.

**What would lengthen it:**
- memory short of 85 % after W2-32: the escalation of DEC-954 Q9e;
- the PACKAGES rate (61 %) and the time to your answers;
- reds the nightly finds in that day's merges;
- W2-81 (FULL, 1,200 lines, in flight) running long, since W2-88 and W2-93 wait for it.
