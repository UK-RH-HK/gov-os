# CAPACITY-1: how to use the machine to finish the Gov OS (P1, the owner's assessment of 2026-10-31)

For the owner, before deciding anything more on capacity. Asked 2026-10-31 14:25 (five parts), with the bigger-machine part added at about 15:00 and DEC-975 (W2-107 first; size a bigger machine only on figures taken after W2-107) at about 17:00. Nothing on capacity was changed while it was measured. The first form went to the owner in the chat at about 20:10; this file is the full record of it.

## Headline

- **The machine is bound by its processor, and overload finishes no more work.** The same fixed test run takes 63 to 106 s at a load of 17 to 32 and 211 to 282 s at a load of 57 to 76, about 3.5 times as long. Running more at once only stretches each job, and the stretch turns time-limited tests red, loses runs at the two-hour limit and makes leads wait.
- **Gitleaks was the hidden big user**, inside rebuilds and test runs. **W2-107 (merged 2026-10-31 18:47, `73736f4b`) cuts a rebuild's secrets stage from 548 to 696 s to 12 s (5 s on an unchanged tree), and a whole rebuild from 735 s to 133 s (36 s unchanged).**
- **One recommendation:** a machine-wide limit on heavy jobs (test runs and rebuilds take a slot; the rest runs freely), replacing the leads' load wait. About a day sooner for Wave 2 (range half a day to a day and a half).
- **Memory:** today's peak fits (18.7 of 24 GiB). The three layers do not, unless the rerankers are shared: about 31 to 37 GiB as things are, about 21 GiB with one shared reranker.
- **A bigger machine:** on today's figures, 4 times the capacity closes Wave 2 about a day sooner and more than 4 times gains nothing. Under DEC-975 it is sized again on figures taken after W2-107; expected to weaken the case.

## 1. What uses the machine, by kind

**Method.** `tools/kind_sampler.py` sampled every 60 s from 14:17 to 20:04 (290 samples; raw `log/capacity/kinds.jsonl`). Each process is put in a kind by its own command (embedding, reranker, gitleaks, code graph, Claude session) or else by its nearest ancestor (a test run, a rebuild, git, other). A process's CPU is its own time plus its reaped children's, so short-lived work counts under the kind that started it. The kinds are scaled to the machine's busy total from `/proc/stat`. All of it is before W2-107 was merged anywhere but its own worktree.

**The machine.** An Intel i7-12700F (20 threads), 31.8 GB of RAM (WSL is given 24 GB and 8 GB of swap, `memory=24GB` in `.wslconfig`), an NVIDIA RTX 5070 Ti with 16 GB (about 3.4 GB in use). Over the day: 16.2 of 20 threads busy on average, 1.9 idle, 0.04 waiting on disk; the load averaged 44 and peaked at 89; memory used averaged 11.4 GiB and peaked at 18.7 GiB.

| Kind | CPU, threads (average) | Share | Memory, GiB (average / peak) | Processes (average / peak) |
|---|---|---|---|---|
| Test runs (leads' and closes') | 8.2 | 51 % | 2.5 / 6.5 | 34 / 123 |
| Rebuilds | 2.5 | 16 % | 0.1 / 0.2 | 5 / 14 |
| Embedding (index on the GPU; queries on the CPU, port 11435, DEC-798) | 2.3 | 14 % | 1.2 / 3.1 | 3 / 6 |
| Other (sandboxes, shells, helpers) | 2.0 | 12 % | 2.5 / 4.2 | 142 / 172 |
| Claude sessions (0.24 GiB each) | 0.7 | 4.5 % | 1.1 / 2.3 | 5 / 9 |
| Rerankers (1.2 GiB each, up to 2.0) | 0.2 | 1 % | 3.5 / **9.4** | 3 / 9 |
| Gitleaks, seen as its own process | 0.1 | 1 % | 0.9 / 3.0 | 24 / 74 |

**The caveat that matters.** Gitleaks runs once per file and rule set, and each run lasts under a second, so a minute's sample rarely catches it and its time is reaped into its parent: most of "rebuilds" is gitleaks (W2-76 measured the secrets stage at 548 to 696 s of a 735 s rebuild), and so is part of "test runs" (the fixtures' own rebuilds). The operator's snapshot of about 8 of 20 threads in 54 gitleaks processes agrees. From 19:00, with fewer leads and W2-107's close using the cache, the rebuild kind fell to 0.7 threads.

## 2. What overload costs

**The same work at different loads** (`tools/bench_loop.sh`: `tests/unit` with 4 workers, 2,976 tests, on a frozen clone at `5036f64a8077`, every 30 minutes; raw `log/capacity/bench.jsonl`):

| Load at start | Time |
|---|---|
| 17 to 32 | 63 to 106 s |
| 48 to 58 | 177 to 219 s |
| 57 to 76 | 211 to 282 s |

Other measures agree: W2-108's context check took 300 s at load 10, 406 s at 20, 940 s at 36 and 1,063 s at 48 (before W2-108's fix up to 2,414 s at 63); the nightly took 5,623 s alone and 14,838 s sharing the machine.

**Does more at once finish more? No.** The processor is near full, so more jobs only stretch each one. The stretch costs, on 2026-10-31 alone:
- **Waiting:** the leads' load wait (both loads at or above 20) held W2-108 90 minutes, W2-96 125, W2-95 75, W2-67 62 and W2-107 52: about 6.7 lead-hours.
- **Lost runs:** runs past the two-hour limit of a background command: W2-107 about 60 minutes, W2-67 about 55, W2-95 its rebuild's exit record.
- **False reds:** the 11 hook-latency cases (W1-02, W1-05, W2-57, p95 under 100 ms) fail under load and pass when quiet; they refused the batch of four at 15:19 (a 3.5-hour batch run redone). `gov check`'s families pass their 600 s limit under load and must be re-run alone.

## 3. What memory adds once it is live

- **Today:** a peak of 18.7 of 24 GiB, with up to 9 reranker processes at 1.2 to 2.0 GiB each.
- **With the three layers** (the CTO, about 4 senior engineers, about 8 leads, about 2 workers each: about 29 sessions):

| Part | As today | With one shared reranker |
|---|---|---|
| Sessions (0.24 GiB each) | 7 | 7 |
| Rerankers (one per searching process, about 10 at once) | 12 to 18 | about 2 |
| Embedders | 3 | 3 |
| Test runs | 6.5 | 6.5 |
| Other | 2.5 | 2.5 |
| **Total, GiB** | **31 to 37 (does not fit 24)** | **about 21 (fits, narrowly)** |

So a shared reranker is a precondition of the three layers, not an option. Under DEC-974 it comes to the owner as a P1 ticket proposal before it is filed.

## 4. The options

| Option | What it changes | Gain | Cost and risk |
|---|---|---|---|
| **W2-107, the gitleaks cache (merged)** | A rebuild's secrets stage 548-696 s to 12 s (5 s unchanged); a rebuild 735 s to 133 s (36 s unchanged). The nightly still scans in full (`GOV_SECRETS_FULL_SCAN=1`, `2e2e6c8a`) | about 40 to 60 machine-minutes per ticket | none found; review round 3 passed |
| **A heavy-job limit (recommended)** | Test runs and rebuilds take one of a few machine-wide slots and wait for one; it replaces the leads' load wait | jobs at 2 to 3 times their overloaded speed; most of the waits, lost runs and false reds go | a queue to manage; the slot count from the re-measure (likely 3 or 4) |
| **Single-process runs exempt from the load wait** (W2-96's option (b)) | one `gov accept` or one red check never waits | 1 to 2 lead-hours a day | a little more load; covered by the heavy-job limit |
| **Lower review effort** (max to high) | reviews are Claude sessions: 0.7 threads in all | little on the machine; some API time and cost | weaker reviews; not recommended |
| **Heavy work at night** | closes and full runs 20:00 to 04:00 | uses quiet hours | delays a close by up to a day; 04:00 to 08:00 is the nightly's |
| **More WSL memory** | 24 GB to 27 GB | 3 GiB | leaves Windows about 5 GB; small |
| **A shared reranker** (needed before the three layers) | one reranker for every session, perhaps on the GPU (about 13 GB free) | 7 to 16 GiB | a ticket; on the GPU, a determinism test like W2-15b's new embedder KPI (DEC-975) |

## 5. The recommendation, with the time it saves

**A machine-wide heavy-job limit, replacing the leads' load wait.** Test runs and rebuilds take a slot; sessions, reviews and single-process runs run freely. The slot count is set from the re-measure after W2-107 (likely 3 or 4). It is the CTO's tool (in the lighter lane, if P-TOOLS-LANE-1 is approved).
- Scoped runs from 46 to 80 minutes at loads of 50 to 75 to about 25 to 35 minutes at about 20.
- About 6 lead-hours a day of waiting gone, and most of the lost runs and false-red re-runs.
- **Toward Wave 2: about a day sooner (range half a day to a day and a half),** with W2-107's rebuild gain perhaps another half day.

## 6. A bigger machine (on figures from before W2-107; sized again after it, DEC-975)

A model of the WBS (dependencies, the measured lead and close times, the ordering rules; `log/capacity/sim.py`, `bigger-machine.md`) on today's figures:

| Machine | Leads at once | EXAMIN's copy starts | Wave 2 closes |
|---|---|---|---|
| This one | 6 | 11-05 | 11-06 |
| 4 times | up to 24 (peak 20 used) | 11-04 | 11-05 |
| 6 times | 36 | 11-04 | 11-05 |
| 10 times | 60 | 11-04 | 11-05 |

- **Where the gain stops:** at most about 20 tickets are ever ready at once; the series chain W2-108, W2-13, W2-15a, W2-32, ACT 2 (the owner's), the three layers, then W2-27 to W2-47 takes about 3 days on any machine.
- **Cost:** a 4-times dedicated server about EUR 199 a month plus EUR 79 setup; cloud about USD 720 to 750 a week at 4 times, USD 1,500 to 1,600 at 6 to 10 times; 64 GB more for this PC about USD 880 to 1,150. Setup 1 to 2 days (the repository, the secrets, the network, the pinned gov), which is about the whole gain.
- **The model is optimistic:** it closes tickets faster than the measured 8 a day, with no refused batches (today had three). The one figure for EXAMIN's copy stays PLAN-GROWTH-1's: **13 November (range 11 to 16).**
- **Free gain whatever the machine:** keep the critical chain's files clear of other work (about 17 hours in the model).
- **Next:** re-sized on tomorrow's working-day figures, with W2-107 merged into every worktree.

## 7. Ready now, and what holds the rest

At 15:20, of 61 tickets not closed: **13 ready** (W2-04, W2-11, W2-37, W2-56, W2-81, W2-86, W2-92, W2-94, W2-97, W2-104, W2-61h, and W2-105 and W2-52 queued); held by open dependencies 27, by ordering rules 7 (the launcher chain, the retrieval chain, the adopt files), by another ticket's files 3; the rest running, closing or at the owner's decisions. Since then W2-95, W2-67 and W2-107 merged, W2-86 was claimed, and W2-108 went back for a test fix (DEC-977).

## 8. Memory's state (DEC-974 item 1)

- **Measured** (visible half, 20 questions): after W2-87, hit@5 11 of 20 (55 %), full evidence 11 of 20 (55 %), in the bundle 15 of 20; W2-61's baseline 8, 12 and 14. Target 95 % (floor 85 %), full evidence 99 %.
- **Closed:** W2-61 (the measure), W2-87 (authority order, the register fix), W2-54 (the context check).
- **Merged, not closed:** W2-108 (back for its test's DEC-385 form, DEC-977).
- **Queued:** W2-86 (claimed; it re-measures in its own run). W2-81 was claimed long ago and never run; recommended next (W2-88 and W2-93 wait for it).
- **Not started:** W2-61h, W2-91, W2-92, W2-13, W2-93, W2-94, W2-88, W2-04, W2-55, W2-14, W2-15a, W2-15b, W2-32.
- **The next measure:** in W2-86's run, about 5 to 6 hours after it starts; the 48-question measure after W2-61h, which follows W2-84's close.

## 9. Tickets added since the plan's approval (DEC-954): 24

| Decision | Decided by | Tickets |
|---|---|---|
| DEC-954 | the owner | W2-86, W2-88 |
| DEC-957 | the owner | W2-90, W2-91, W2-92, W2-93, W2-94 |
| DEC-959 | the owner | W2-95 to W2-104 (10) |
| DEC-966 (W2-107's start DEC-967) | the owner | W2-105, W2-106, W2-107 |
| DEC-969 | the owner | W2-108 |
| DEC-971 | the owner | W2-109, W2-110 |
| DEC-965, DEC-970 | **the CTO, under delegation** (2026-10-31 13:15) | **W2-90b**, W2-90's next round |

From DEC-974, every new ticket comes to the owner as a P1 before it is filed.

## 10. P-TOOLS-LANE-1: a lighter lane for the CTO's own tools (DEC-974 item 3)

- **Scope:** the scratch tools (the close tool, the selection, the gate, the watchers, the samplers, the brief builders) and the nightly folder.
- **Today:** a nightly change needs an independent review and `test_nightly.sh`; the scratch tools have no tests and no review, their changes noted only in the CTO's checkpoint; none is a WBS ticket.
- **Proposed:** (1) each tool has its own test file, run before the tool is used; (2) an independent review only when a change could fail open (let a red or a refusal through, widen a gate) or lose work (kill, delete, lock, overwrite); (3) a "Tools changed" section in the daily document (tool, change, test, reviewed or why not); (4) never a WBS ticket.
- **What it changes:** fewer reviews of nightly changes of a time or a message; more tests on the scratch tools (stricter); the WBS count shows the product only.
- **Today's example:** the close tool's attribution change could fail open; it had two reviews and 11 tests (`tools/test_close_build.py`), and the second review's fix made the tests run the tool's own code.

## The owner's decisions

Each in the six parts (DEC-818), briefly.

### D1. The heavy-job limit
1. **Context:** the leads' load wait holds whole leads while the machine is busy, and the jobs already running stretch.
2. **What happened:** about 6.7 lead-hours waited, three runs lost, a batch refused on load-sensitive cases (sections 2 and 4).
3. **Why it matters:** about a day on Wave 2.
4. **Options:** (a) a heavy-job limit replacing the load wait, sized from the re-measure; (b) keep the load wait.
5. **Recommendation:** (a), medium-high confidence.
6. **Blocks:** nothing; waiting keeps today's losses.

### D2. P-LATENCY-1: the 11 hook-latency cases
1. **Context:** W1-02's, W1-05's and W2-57's p95-under-100-ms cases; no ticket owns them (not W2-90b).
2. **What happened:** traced 3 rounds with and without W2-106: red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30; they pass alone.
3. **Why it matters:** they redden closes and the nightly whatever the change; DEC-968 allows no accepted reds.
4. **Options:** (a) a fresh test designer revises them to time the hook's own work (its CPU time, or against a quiet reference beside each run), at the same 100 ms, lowering nothing (DEC-906: under the owner's named decision); (b) run them only in the nightly.
5. **Recommendation:** (a), filed after W2-90b (W1-05's file shared). Under DEC-974 the ticket is itself a P1: this decision is that P1.
6. **Blocks:** nothing directly; each close names them meanwhile.

### D3. P-TOOLS-LANE-1
As section 10. **Recommendation:** (a) as proposed. **Blocks:** nothing.

### D4. P-W2-108-BATCH: the query-embedding batching
1. **Context:** DEC-969 asked for the batching as W2-108's next step if the context check stayed slow at load.
2. **What happened:** after W2-108 the check takes 300 to 406 s at loads of 10 to 20; the remaining 550 to 600 s at load is not the embedding.
3. **Why it matters:** batching would change the query path without the measured cause.
4. **Options:** (a) no batching; profile the remaining time first; (b) batch now.
5. **Recommendation:** (a), high confidence.
6. **Blocks:** nothing.

### D5. W2-90b, filed by the CTO under delegation
1. **Context:** W2-90's next round (its 7 named reds, the 14 ids ACT 1 dropped, W1-33's four, W1-05's two, W2-54's sandboxed case), filed 13:15 under DEC-965 and DEC-970, before DEC-974.
2. **What happened:** it is in the WBS, after W2-105 and W2-106; today's runs add W2-59's four hook-line cases to its cause (the planted projects lack the hook file, like W1-33's).
3. **Why it matters:** under DEC-974 a new ticket is the owner's.
4. **Options:** (a) approve it as filed; (b) withdraw it, and the reds go to another ticket.
5. **Recommendation:** (a).
6. **Blocks:** the 13 named reds stay red until it runs.

### D6. W2-96's gate option
1. **Context:** W2-96's P2 P-W2-96-GATE; the CTO took (a) (resume when the queue allows, DEC-976) and left (b) to the owner.
2. **Options:** (a) exempt single-process runs (one `gov accept`, one red check) from the load wait; (b) keep them waiting.
3. **Recommendation:** decided by D1 if D1 is (a); otherwise (a).
4. **Blocks:** W2-96's resume waits meanwhile.

## Sources

`.gov-runtime/scratch/orchestrator/log/capacity/` (kinds.jsonl, bench.jsonl, latency-trace.txt, bigger-machine.md, sim.py, ready_now.json), `drafts/CAPACITY-1-notes.md`; the close logs under `log/close-build/`; DEC-966 to DEC-978 in the register.
