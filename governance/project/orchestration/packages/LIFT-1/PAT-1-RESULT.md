# PAT-1: the parallel-agents and memory test after re-pin window 4 (DEC-1087 (10), DEC-1089 (1))

For the owner, before E0. Run 2026-11-07 14:45 to 15:05 by the CTO (session `ad44f5fe`) on `pin-bcea09060ebc`, with the pool switched on at `c00d525f`. The raw outputs and scripts are in `~/gov-os-runs/PAT-1/`, and the agents' findings are in `pat/A-findings.md` and `pat/B-findings.md`.

## 1. Verdict
- **Working:** the store refreshes itself after every landing. A search during the refresh never failed, never lost a facet and never got a mixed answer. Page 2 after a switch fails closed. Memory is released after every request.
- **Four gaps, none of them a failure:**
  - G1, concurrency is slow;
  - G2, results carry no commit;
  - G3, overlapping slices remain;
  - G4, a worker that is behind gets line numbers that don't match its own tree.

## 2. The store and the hook (START-NEXT-SESSION §4 step 3)
- **The pool commit `c00d525f`, 14:46:** the hook built store half -a in 30 s and switched the link. No hand run was needed.
- **The record commit `84c4f92d`, 14:59:28:** the hook built half -b from 14:59:25 and switched by about 15:00:00. Agent A saw the new head within 76 s of the commit.
- **A search through the store:** both facets, `rerank.by` service on cuda:0, and register items carry their own ids (no DEC-999), their status and "changed by".

## 3. Speed: the pin against the candidate (DEC-1086 A)
10 plain questions, 3 timed passes each, interleaved with the order rotated, after one warm pass. Each search ran alone.

| | median | p95 | max | errors | answers with overlapping items | overlapping items per answer |
|---|---|---|---|---|---|---|
| old pin `8284fb40` | 1.44 s | 6.90 s | 7.31 s | 0 | 30 of 30 | 4.5 |
| new pin, pool off | 1.45 s | 6.90 s | 7.22 s | 0 | 30 of 30 | 4.5 |
| **new pin, pool on** | **1.68 s** | 7.46 s | 7.58 s | 0 | **15 of 30** | **1.0** |

- **The new pin's own cost:** none (1.45 s against 1.44 s).
- **The pool's cost:** +0.23 s at the median (+16 %).
- **The p95:** one question ("how does gov launch set GOV_STORE for a worker") takes about 7 s in every configuration. It is not the pool's doing.

## 4. 10 and 20 searches at once: W2-112's live measure (its review F1)
Method: W2-112's own. Its 20 visible questions (q01-q20), started together against the warm service, 3 rounds each. `nvidia-smi` was sampled every 0.25 s and the reranker log was read alongside.

| | p50 | p95 | max | errors / fallbacks / refusals |
|---|---|---|---|---|
| W2-112's baseline (30 candidates, before the 16-text cap) | 2.32 s | 3.82 s | 4.01 s | 0 |
| old pin, 20 at once | 10.24 s | 10.26 s | 10.26 s | 0 / 0 / 0 |
| new pin, pool off, 20 at once | 10.25 s | 10.27 s | 10.27 s | 0 / 0 / 0 |
| **new pin, pool on, 20 at once (3 rounds)** | **13.4-13.9 s** | 13.4-14.2 s | 13.4-14.2 s | 0 / 0 / 0 |
| new pin, pool on, 10 at once (3 rounds) | 6.6-6.8 s | 8.8-8.9 s | 8.8-8.9 s | 0 / 0 / 0 |

- **G1, why:**
  - The service answers one request at a time, first come, first served, with no batching (`rerank_service.py`).
  - Each request carries at most 16 texts (`MAX_REQUEST_TEXTS`, DEC-1067 (f), added after W2-112's baseline as a memory bound).
  - The pool reranks 40 candidates, which takes 3 requests (63 log lines for 20 searches; the old pin's 30 candidates took 2, 41 lines).
  - About 0.2 s per request gives about 13 s for 60 requests. All 20 searches finish together because their requests interleave.
- **G1 is older than window 4.** The old pin is already at 10.2 s; the pool adds about 31 %.
- **What it means:** the three layers expect about 10 searching at once (W2-112's ticket), and that now takes 6.7 s at the median and 8.9 s at the worst. Nothing failed and nothing timed out.
- **Memory (the release):**
  - after every request the log reads 1,168 MiB allocated and 1,192 MiB reserved, flat across all 401 requests of the bursts;
  - `nvidia-smi` rises by up to 1.95 GB during a burst (the CUDA context and the request's working memory, which the logged figure leaves out) and returns to the base level (7,466 to 7,483 MiB) after every round;
  - the peak was 9,427 MiB, under the 14,255 MiB budget. The GPU backstop never tripped.
- **Options for G1, nothing done yet:**
  - (a) the service batches the requests it has queued;
  - (b) raise the 16-text cap, now that memory is released after each request (the reason for the cap);
  - (c) a second service process, within the GPU budget.

  Each would be a new ticket (W2-112 is merged and closes at the lift, DEC-1088 (6)), tests first. My recommendation is (b), measured first, then (a).

## 5. Search during a refresh, and the continuation (W2-116's R2-F1 and R2-F3)
- **The probe:** a search every 1.5 s for 4 minutes, alternating the two forms a worker uses (`--root <link>`, and `GOV_STORE=<link>` from inside a worktree with no store). A record commit landed during it.
  - 147 searches: 0 errors, 0 fallbacks, 0 with a facet missing.
  - The answers changed from the old half to the new half **exactly once**, in both forms: 92 old, then 55 new, with no flip-back.
  - One search spanned the switch and answered from one half. No answer had the new record through only one facet, so R2-F1 (the link resolved once per facet) never showed.
- **R2-F3, page 2 after a switch:** it is **refused**, with `CONTINUATION_INVALID` ("the continuation's candidate pool is not this question's: the store or the pool settings changed since the earlier call"). It never pages the other half silently. The worker asks page 1 again. Agent B saw the same.
  - The refusal does not name the store the token came from (B's note).

## 6. Two agents in two worktrees (the test itself)
Two research agents worked at the same time, each in its own worktree, both searching the one shared store. They answered three questions with line citations from their own trees, then edited and committed in their own trees.
- **PAT-a** started at integrate's head (`c00d525f`).
- **PAT-b** sat 4 commits behind (`bcea0906`).

The record commit landed while both were working.
- **Both worked:** searches, reads and their own commits (`7fa459e9` on `test/pat-a`, `c43b4c98` on `test/pat-b`). `rerank.by` was service with both facets on every search.
- **G2, no commit in the results.** Neither agent could tell from a result which commit the store held (no commit, build time or half field). They found it from the content (whether DEC-1089 was there) or with `readlink` and `git rev-parse` on the link.
- **G4, line numbers mislead.** This applies to **both** agents: A was "at head" when it started, but integrate moved under it.
  - The store's `DECISION_REGISTER.md:13703-13752` (DEC-1089) is the version table in their trees.
  - `START-NEXT-SESSION.md:88-133` in B's tree is a different section (§4 "Live and running now").
  - `K7-W2-REMAINDER.md` and `retrieval.yaml:7-14` do not exist in B's tree.
  - Files the commit did not touch matched exactly.
  - Before the refresh, B's search for the K7 and usage decision found only older ping rules. Nothing hinted that a newer decision existed.
- **A check that works today (found by A):** each evidence item's `sha256` is the hash of exactly those lines. Hashing your own lines settles "same or not". Nothing tells a worker to do it.
- **Also seen:**
  - a third facet, `closure`, appears when a question names a record id;
  - `W2-32-evidence.md:34` still says the pool is "not switched on", which ranked in a bundle as a stale line;
  - the register's version table is folded into the last decision's chunk.

## 7. Overlapping slices (DEC-1089 (1))
- **Partly fixed.** With the pool on, answers with overlapping items fell from 30 of 30 to 15 of 30, and from 4.5 overlapping items per answer to 1.0.
- **On the case you named** ("what decides whether a closed ticket may be edited"):
  - the whole-entry chunk of DEC-1088, which contained the others, is dropped;
  - three slices of DEC-1088 remain (positions 1, 3 and 12). They are adjacent pieces sharing one boundary line, not copies.
- **What remains (G3):** `drop_nested` removes only items wholly inside an earlier one. Slices that merely overlap stay: DEC-1087 three or four times, and DEC-1037 twice, in the agents' searches.
- **Options:**
  - (a) merge the overlapping slices of one record into one item;
  - (b) cap the slices per record in the top 10, as `per_file_first10` does per file;
  - (c) leave it, since they carry different lines.

  Any change goes through the 138 first, since it moves hit@5.

## 8. The link graph and dependency gating in use
- **The link graph:** W2-92's stated links are live. Register items carry `status`, `in_force` and `changed_by` (seen in every register hit), and a question naming an id adds the `closure` facet (one bounded hop). `gov links` runs in the structural pass after every record commit.
- **Dependency gating:** today it is the tickets' `depends_on` plus the READY rule (the dispatcher's `ready.txt`, `tools/verdict.py`). No lead runs during the emergency, so it was not exercised live.
  - `gov plan` (W2-136) is to be built beside the experiments and live at the lift's re-pin, with W2-20's launch gate (DEC-1088).

## 9. Proposed (for the owner; nothing changed yet)
1. **G2 + G4:** every `gov retrieve` result carries the store's commit and half. The worker brief (EMG-common, and the templates) adds one line: check an evidence item's `sha256` against your own lines before relying on it, and when your branch is behind, read the store's file at its commit (`git show <commit>:<path>`). This would be a new ticket, tests first, on `src/gov/retrieve/`, plus a brief line now.
2. **G1:** a new ticket, tests first: option (b), the cap raised and measured on the 138 and the 20-at-once burst, then (a) batching if still needed. It lands at the lift's re-pin.
3. **G3:** decided after E0, with the 138's figures for options (a) and (b).
4. **Neither blocks E0.** E0 runs the 138 one at a time (G1 doesn't touch it), and G2 to G4 affect agents, not the measure.

**Spend (DEC-1089 (3)):** agent A 114,556 tokens; agent B 86,307 tokens; the K7 research agent 136,162 tokens. The scripted searches used no model. Cost: no measured per-run price (subscription).

**Basis:** question 1 (agents get the current store and can tell when their tree differs) and question 2 (no silent wrong page; search times known before the three layers).
