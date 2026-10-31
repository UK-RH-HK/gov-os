# P-W2-54-LOAD-1: W2-54's load failures: the context check repeats its freshness checks 328 times (P1, the fix)

For the owner (DEC-968 item 3: a failure the change did not cause is investigated at once; bring the fix or a P1).

## 1. Context
- W2-54's two cases time `gov`'s context-reproducibility check: the time-limit case (630 s) and the green-here cases (600 s).
- They fail under load and pass at low load (W2-57's close at load 4; the nightly before DEC-961). W2-85 routed them to the nightly (DEC-951 item 3). But since DEC-961 the nightly runs beside leads and closes, so they will meet load there too.

## 2. What happened (measured 2026-10-31 02:00 to 02:21, a cProfile of `python3 -m gov.context.context_check` on the designers' store, load 40 to 70 falling to 8)
- **The run:** 1,252 s wall (1,178 s profiled), verdict green: the check is correct but slow. It makes 328 retrieval calls (3.5 s each).
- **Where the time goes:**
  - **Freshness checks repeated on every call: about 460 s.**
    - The semantic store's status (`semantic._status`) takes 315 s over 328 calls. Inside it, `_wanted` works out which files should be embedded by calling `embedded()` about 17 million times (228 s).
    - The lexical index's freshness (`lexical.freshness`, 656 calls) lists the tracked files each time: 148 s.

    Neither result can change within one run.
  - **Query embedding: 375 s.** There are 96 calls to the embedder (848 HTTP requests), 3.9 s each under load. The rest are answered by the query-vector cache.
  - **The searches and the rest:** about 340 s.
- **Why load decides the outcome:** at low load the same work fits under 600 s; at load 40 to 70 it takes twice that.

## 3. Why it matters
- The check runs in every `gov check` and in W2-54's cases. Under load it will go red in closes that select W2-54, and in the nightly now that the nightly shares the machine.
- The cause is repeated work, not the limit. Raising the limit would hide the cost; it would not fix it.

## 4. Options
- **(a) Recommended: compute freshness once per process.** Remember the semantic store's status and the lexical index's freshness for the life of one process, keyed by the store's fingerprint and the tree's head, so a run of 328 queries checks them once. A new ticket, W2-108, STANDARD:
  - **paths:** `src/gov/retrieval/semantic.py` and `src/gov/retrieval/lexical.py` (no running ticket holds them; W2-13 and W2-32, both open, are split by function), plus unit tests;
  - **KPIs:** an unchanged answer for every call; a store that changes between two processes is still seen as changed; the check's time measured before and after at the same load;
  - **expected:** about 460 s less per run, roughly 1,250 s down to about 750 s at load 40 to 70, and well under 600 s at ordinary load;
  - **cost:** about 4 to 6 hours.
- **(b) (a), plus embedding the check's queries in one batch** (96 calls down to a few). This saves up to about 350 s more under load, but it touches the embedder's client. It is better as a second step after (a)'s measure.
- **(c) Scale the time limit by the measured load.** This keeps W2-54 green without fixing the cost. Not recommended: it hides a real slowdown that the owner's speed priority targets.

None of these lowers W2-54's expectations or changes its tests.

## 5. Recommendation
**(a) now, then (b) if (a)'s measure is still over 600 s at load 40.** Confidence high. Classification: ordinary work, yes (every `gov check` and context packet); consequence: other (slow, and red under load; nothing fails open).

## 6. What it blocks, and what waiting costs
- **Blocks:** nothing now. Under DEC-968 a close is not refused by these failures, since they are not its change's.
- **Waiting costs:** W2-54's cases stay red under load, in the nightly too, each one investigated again. Every `gov check` and context packet pays about 460 s of repeated work.
