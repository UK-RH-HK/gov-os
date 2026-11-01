You are the ticket lead for ticket `@@ID@@` (`W2-04`, "gov context bounded and reproducible"). It is profile FULL, on memory's critical chain (W2-15a waits for it, DEC-979 item 4), and you work only in the worktree `/home/usain/gov-os-worktrees/W2-04` on branch `w2/W2-04`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (CAP-15.d, DEC-860, and the rows the ticket takes in); allowed paths, KPIs, profile and the acceptance path (`tests/acceptance/W2-04/`) are set; it has no open dependency. W2-55 (`DAEO-arrl`, merged; its close runs today) changed `src/gov/context/**` before you: read its merged code on `w2/integrate`, do not undo it.

**Read first:** the ticket file and its card in `docs/plan/WAVE_2_WBS.md`; the rows it takes in (`docs/plan/WAVE_2_LIST.md`: W2-H034, W2-L088, W2-L180, W2-L183, W2-L219, W2-M126, W2-M133, W2-M134, W2-M215, W2-M228, W2-M239, W2-M294, W2-M330); `src/gov/context/**` as it stands; W2-03's per-decision hash; DEC-860 (retrieval in batches, ranked and stacked; never one giant query or context).

## The decisions for this run
- **The work order (DEC-957, DEC-959 item 7, DEC-963):** a fresh independent test designer (sandboxed, effort xhigh as a measured trial for a FULL ticket, DEC-839) in `/home/usain/gov-os-worktrees/W2-04-tests`, retrieving only from the integration branch's store, writes `tests/acceptance/W2-04/` from the spec and KPIs (planted repositories and stores built in temporary folders). In parallel a fresh engineer (sandboxed, effort high) builds to the spec, never to the tests; it runs the acceptance tests once merged, through `gov accept @@ID@@`, results only.
- **Scope, by file:** `src/gov/context/**`, `src/gov/retrieval/supplementary*`, builder tests under `tests/unit/context/**`. **W2-13 (running) holds `src/gov/retrieval/lexical*`, `fusion*`, `src/gov/retrieve/**` and `tests/unit/retrieval/**`; W2-92 (running) holds `src/gov/retrieval/graph_route.py`, `code_route.py` and the route list in `retrieve.py`:** read only. If your change needs one of their files, return PACKAGES.
- **Fail closed:** the packet over its ceiling refuses with a named error and a non-zero exit, never `ok: true`; an unreadable mandatory record blocks or is marked not read, never shown read with an empty hash; ties ordered deterministically.
- **Review (FULL):** after green, a fresh independent-auditor (read-only, effort max) on the final head, with `JUDGEMENT.md`; commit only a passing probe record; up to two reviews in this declared round (DEC-916).
- **Verification (DEC-968, DEC-983):** the scoped set from `select_tests.py`, once, in the close's form, through `verify_lock.sh`. Never the full suite.
- **One role (DEC-995):** a part needing another role's writes is a split named in your return. A measurement of your own change is your evidence at `docs/changes/W2-04-evidence.md` (DEC-996 (A)) if you need one; it is outside your paths today, so name it in your return rather than write it. **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head you verified.

**Estimate:** about 220 lines of code and 250 of tests; about 7 hours with the review. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-04`.

---
