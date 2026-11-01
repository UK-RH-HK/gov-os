You are the ticket lead for ticket `DAEO-zqvn` (`W2-13`, "RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5)"). It is profile FULL, on memory's critical chain (DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-13` on branch `w2/W2-13`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-725, DEC-900); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-13/`) are set; dependencies closed: W2-01 (`DAEO-g0ip`) and W2-03 (`DAEO-ym8a`). Its rows (W2-L233, W2-M071, W2-M072, W2-M098, W2-M100, W2-M102, W2-M292, W2-M296) are re-checked against the code as you take them in (DEC-718).

**Read first:**
- the ticket file (`.tickets/DAEO-zqvn.md`), its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-13") and its rows in `docs/plan/WAVE_2_TRIAGE.md`;
- DEC-725, DEC-900 (RETR-X-02: the stated gap is the accepted outcome; W1-42's case is retired, so your acceptance tests hold the requirement), AR-9; DEC-957 (memory's target 95 %, floor 85 %), DEC-860 (batched, ranked, stacked);
- `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/rebuild/lexical*` and the secrets filter on the lexical index (W2-107's content-hash cache sits in front of it: keep it);
- W2-61's measure and W2-86's record (`docs/research/W2-86-memory-measure.md`, once on `w2/integrate`): ranking is the remaining cause of the misses.

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer, sandboxed, **effort xhigh** (DEC-839's measured trial for a FULL ticket's designer; record its time and cost in your return), in `/home/usain/gov-os-worktrees/W2-13-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-13/` (FULL: thorough; planted stores in temporary folders; the planted secrets canary never indexed in the FTS5 table; RETR-A-04's bundle unchanged; an id that exists nowhere stops with a named reason and no unrelated items; "unavailable" never raises). In parallel, a fresh engineer (sandboxed, effort high) builds the FTS5 route with BM25 field weights (id, title, body), the exact-match route kept as a boost, and the fusion's ranked lexical list; it runs the acceptance tests once merged (`gov accept` once on `w2/integrate`), reading results only.
- **Scope, by file:** `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/rebuild/lexical*`, and tests under `tests/unit/retrieve/**` and `tests/unit/retrieval/**` **except** `test_w2_92*` (W2-92's, running now) and `test_w2_86*` (W2-86's): never write those. W2-92 holds `graph_route.py`, `code_route.py` and `retrieve.py`'s route list: read only. W2-55 (merged, closing) shares `src/gov/retrieve/**`: merge `w2/integrate` first if your base predates its close. If your change needs another ticket's file, return PACKAGES.
- **The dev queryset's lexical-only hit@5** goes in your evidence (KPI 2), and W2-61's visible-half measure is repeated on base and head as W2-86 ran it (two clones under `/home/usain/gov-os-runs/W2-13/`, rebuilt under the rebuild lock, `--part visible` only, never hidden), both figures together, in your return.
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh` (a heavy-job slot). Never the full suite.
- **FULL:** after green, a fresh reviewer (A3 plus `JUDGEMENT.md`, independent-auditor, effort max), read-only, on the final head; a passing probe record committed under `docs/probes/DAEO-zqvn/`; at most two reviews in this declared round (DEC-916).
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head your reviewer probed; the CTO lands it through the merge queue, which merges and closes it in one step.

## This run's order
1. Test designer and engineer in parallel; merge the tests branch; red check at `@@HEAD@@` yourself.
2. The engineer's route; one acceptance run. 3. The re-measure. 4. Verify (scoped). 5. Review; probe record. 6. Return DONE or PACKAGES.

**Estimate:** about 300 lines of code and 300 of tests; about 9 hours (tests and code 4 h, review 1 h, rebuilds and measures 2.5 h, scoped run 1 h). Scratch budget (DEC-898): 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-13`.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
