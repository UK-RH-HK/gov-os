# P-LB-PRODUCT-1 — The Gov Load Balancer in the Gov OS: KPI lines in W2-121 and W2-20, no new ticket (DEC-1039 (1b), DEC-1003)

Written 2026-11-02 21:05 by the CTO (session debdb3f7).

1. **Context.** DEC-1039 (1b): the Gov Load Balancer, in the CTO's tools first, then a proposal for the Gov OS: its own
   ticket, or KPI lines in W2-20 (the machine-wide resource gate, `DAEO-r30l`) and W2-121 (`gov dispatch`, one pass a
   minute keeps the machine full). DEC-974: a new ticket is a P1; KPI lines change a ticket's scope (the owner's here).
2. **What happened.** Built in the dispatcher (`emg/lb`, two review rounds, READY, merged `758bc89f`, live 20:56):
   phases and their measured peaks (p95 over 72 h, today's floors), a forecast before admission naming the binding
   resource, pairing GPU-heavy with CPU-heavy work, the GPU rule each pass (dedicated memory at most total minus
   headroom; no spill into shared memory, read from the Windows counter; one `gpu-alert` per incident),
   machine-derived limits, the standing targets T1-T5 with incidents after 15 minutes. First live pass 20:57: it
   priced 2 reranker slots, read 660 MiB shared (no spill), and refused new starts on CPU (15.7 busy of a band of 18).
3. **Why it matters.** EXAMIN and every adopted repository will run many agents on one machine; last night's CUDA
   crashes and today's overload are what the product must prevent on its own.
4. **Options.** (a) KPI lines, no new ticket: W2-121 gains four lines (phases and measured peaks; the forecast before
   every start naming the binding resource; pairing; the GPU rule and its alert, tested); W2-20 gains two (limits
   derived from the detected machine by ratios, an explicit setting winning; the standing targets and their
   incidents). Cost: W2-121 grows by about a third; nothing new to schedule. (b) A new ticket W2-128 "the load
   balancer", after W2-121. Cost: one more ticket and its dependencies; clearer scope. (c) Keep it in the CTO's tools
   until after EXAMIN's copy. Cost: EXAMIN runs without it.
5. **Recommendation: (a)**, confidence medium-high: W2-121 is already the product's dispatcher and W2-20 its gate; the
   lines are written from the reviewed tool, so the test designer has a working reference behaviour.
6. **What it blocks.** Nothing now (the tool is live here). Waiting leaves W2-121's and W2-20's KPIs short of what
   runs in this repository.
