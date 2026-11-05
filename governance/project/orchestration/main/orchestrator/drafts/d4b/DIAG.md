# The recall diagnosis (DEC-1070 (6)), m6, 2026-11-04 evening

- **Data:** m6's kept ranked outputs (`~/gov-os-eval/runs/m6/run1..3`, identical over the three runs). A depth probe
  ran the product's own route functions at the m6 clone, 1,000 deep, with the live embedder (26 s; GPU +2 MiB). The
  route lists were rebuilt exactly as the product builds them.
- **Scripts:** `diag_recall.py` (stage 1, no GPU), `diag_depth.py` (stage 2), `diag_routes.py` (stage 3). Outputs are
  in `~/gov-os-runs/D4B/diag/`.
- **The hidden half:** ids, ranks and yes/no only. Its kinds are W2-61h's role's
  (`docs/audit/memory-recall-diagnosis-hidden.md`).

## Where each miss is lost (first call)
| Stage | Visible | Hidden |
|---|---|---|
| Never searched: the question names only an id that exists nowhere, so the product stops (UNRESOLVED_IDS, RETR-X-02/DEC-900) | - | h24 (the one `nonexistent-id`) |
| Gold in neither route's top 30, though indexed and embedded | q31 | h05, h11, h16 |
| A sibling of the gold (same parent section) gathered, not widened to the gold lines | q23 | h02 (+ a deep piece) |
| Gold found by one phrasing in the meaning route, dropped when the phrasings were fused and cut to 30 | - | h33 (meaning 24, uncut 32) |
| In the fused list, cut below the first 20 | - | h17 (fused 27), h27 (a sibling at 49, widened only at call 3) |
| In the 20, reranked below 5 | Q14 (19; R11, to be re-worded), Q19 (8) | h07 (9), h26 (8), h32 (9) |

## Generic findings
1. **Coverage is not the cause:** every gold span is in both the keyword and the meaning index.
2. **The closure route does not crowd the 20:**
   - Closure-only chunks in the first call's 20 average 0.2 (visible) and 0.1 (hidden). They appear in 3 visible
     questions and 2 hidden.
   - Among the misses, only Q14 and h07 carry one. None of the cut or absent misses has any.
   - The fused list is 56-57 candidates at the median. It reaches 1,209 when the closure is large (Q06, a hit).
3. **Depth.** The gold's own chunk, at its better route rank:

   | Rank | ≤30 | ≤60 | ≤100 | ≤200 | ≤1000 |
   |---|---|---|---|---|---|
   | Visible (of 68 pieces) | 42 | 45 | 48 | 55 | 67 |
   | Hidden (of 52 pieces) | 39 | 40 | 43 | 47 | 52 |

   The closure and code routes and the widening bring the rest of those in the 20.
4. **The phrasing fusion's cut:** the meaning route, fused over its phrasings and cut to 30, drops a piece one phrasing
   found: 2 visible pieces and 3 hidden. One of them (h33) has no other route.
5. **Code chunking:** q23's gold is a function in a 480-line file whose "parent" is the whole file. Two other fragments
   came back; the answering function ranks keyword 64.
6. **The widening budget:** a first call uses about 5,880 of its 6,000 tokens. It widens a median of 4 chunks; 10
   chunks with a bigger parent stay unwidened.
7. **The nonexistent-id question:**
   - The rubric's R3.5 wants its gold to be the line that settles the absence, with the answer "none".
   - The product, by design, returns no evidence when every named id exists nowhere.
   - So hit@5 cannot score it, whatever retrieval does. This holds for h24 and for the measurement set's one question
     of that category.
   - A scoring decision for the owner.

## Generic levers the diagnosis points to (each to be chosen on the visible half, checked on the hidden half)
- **L1:** the meaning route not cut after fusing the phrasings (or cut at 30 × phrasings).
- **L2:** deeper route lists (60), with more reranked in the first call (40). This costs reranker requests and time
  under the padded bound.
- **L3:** code chunks cut on definitions (M2, built, off).
- **L4:** widening policy: a gathered chunk's section first, within budget.
- **L5:** the vocabulary gap (q31; hidden kinds pending). Candidates: M1 file-level, M4 identifier tokenisation, the
  embedder trial.
- **Not a lever:** the closure (no crowding found).

## The hidden half's kinds (W2-61h's role, `docs/audit/memory-recall-diagnosis-hidden.md`, `efb8acb1`)
- **Over 7 ids** (h02, h05, h11, h16, h17, h27, h33):
  - **crowded topic (K5):** all 7;
  - **answer in a list item, field, table row or single line (K7):** all 7;
  - **diluted chunk (K4):** 6;
  - **vocabulary (K1):** 4;
  - **split section (K2):** 3;
  - **code fragment (K3):** 2; **a hop (K6):** 2; **a two-part question (K8):** 1.
- **The closure:** no closure item in any of their first calls' 20.
- **Plausible levers:**
  - deeper lists: 5;
  - 40 reranked: 4;
  - widening to the section: 3 (2 strong);
  - the meaning route uncut: 2;
  - a file-level index: 2;
  - identifier tokenisation: 1;
  - none: h11 and one piece of h02.
- **Outside the list:**
  - phrasing, splitting multi-part questions and mapping terms: 3;
  - a supersession or citation hop: 2;
  - collapsing duplicate generated copies, or a per-file cap: 2.
- **The visible pair:** q31 is K1 (vocabulary; meaning 36, just past the cut); q23 is K3 + K2 (a code fragment whose
  file's other fragments came back).
