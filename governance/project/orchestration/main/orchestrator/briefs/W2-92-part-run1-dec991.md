You are the ticket lead for ticket `@@ID@@` (`W2-92`, "The knowledge graph and the code graph as routes of plain-question retrieval: ids, record titles and symbol names in a question join the fusion"). It is profile STANDARD, on memory's critical chain (DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-92` on branch `w2/W2-92`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-957, DEC-954, DEC-859, DEC-860, DEC-424, DEC-833, CAP-12, CAP-13, CAP-18); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-92/`) are set; dependencies closed: W2-87 (`DAEO-s9qc`) and W2-03 (`DAEO-ym8a`).

**Read first:**
- the ticket file (`.tickets/@@ID@@.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-92");
- `governance/project/orchestration/packages/MEMORY-SPEC-MAP.md`, gaps 2 and 3 (the reason for this ticket);
- DEC-957 (memory's target 95 %, floor 85 %), DEC-859 and DEC-860 (the code graph's own traversal, small paged answers; never one giant query or context), DEC-424 (records ahead), DEC-833 (both figures together);
- `src/gov/retrieval/retrieve.py` (the route list; the closure route today only with `--ticket` or `--id`), and how `gov closure` and `gov impact` reach the record store and the code index;
- W2-61's measure (`src/gov/retrieval/measure.py`, on `w2/integrate`) and its §8 in `docs/research/W2-61-baseline.md`; W2-86's record `docs/research/W2-86-memory-measure.md` once it is on `w2/integrate` (the latest figures: hit@5 11/20, full evidence 11/20, bundle 15/20; Q10's first caller at rank 25 in the baseline).

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort high) in `/home/usain/gov-os-worktrees/W2-92-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-92/` from the spec and KPIs: a planted repository with a register, records and code, its store and a stand-in code index built in a temporary folder, never this repository's store. In parallel, a fresh engineer (sandboxed, effort high) builds the two route modules and `retrieve.py`'s route list to the spec and KPIs, never to the tests; it runs the acceptance tests once they are merged (`gov accept` once it is on `w2/integrate`), reading results only.
- **Scope, by file:** the two new modules `src/gov/retrieval/graph_route.py` and `code_route.py`, and in `retrieve.py` only the route list (one call each). The ranking (W2-87's authority order) and what is left out (W2-55) are not touched. Builder tests only as new `tests/unit/retrieval/test_w2_92*` files.
- **Running beside you:** W2-13 (FULL, starting now) holds `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/retrieve/**` and the rest of `tests/unit/retrieval/**`: read only; it is told the same of your files. W2-32 (later) merges back after you. W2-05 (merged) holds `src/gov/**/*.py` broadly for its git-environment sweep only; it runs no lead. If your change needs another ticket's file, return PACKAGES.
- **Fail closed:** a question that names no record or symbol gets today's bundle item for item; a missing or unreadable code index or record store is a named stopping reason for that route, never "ok" and never a failure of the whole answer; no whole-graph query, none over the tool's row cap.
- **The re-measure, in your own session (W2-61's §8, as W2-86 ran it):** two clones by exact path under `/home/usain/gov-os-runs/W2-92/` (`base` at `@@HEAD@@`, `head` at your final commit) plus `measure` at `w2/integrate`'s head; each store rebuilt under `flock /tmp/gov-os-rebuild.lock` with this ticket's code for `head` (the change is code, so the code under test builds and answers); the visible half only (`--part visible`), never `--part hidden`; `head` with `--compare` on `base`. A fresh engineer batch writes `docs/research/W2-92-memory-measure.md` in W2-61's form: both figures together (hit@5 against 85 and the owner's 95 %, full evidence against 99 %), the in-the-bundle count, per question, the graph and code-graph questions named, beside W2-86's and W2-61's figures.
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh` (a heavy-job slot). Never the full suite.
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified; the CTO lands it through the merge queue, which merges and closes it in one step.
- **No review (STANDARD).**

## This run's order
1. Test designer and engineer in parallel; merge the tests branch; check red at `@@HEAD@@` yourself (a scratch clone).
2. The engineer's routes; one acceptance run.
3. The re-measure and its record.
4. Verify (scoped). 5. Return DONE or PACKAGES.

**Estimate:** about 200 lines of code and 150 of tests; about 6 hours (tests and code 2.5 h, two rebuilds with embeddings and two measures 2 h, the scoped run about an hour). Scratch budget (DEC-898): 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-92`.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
