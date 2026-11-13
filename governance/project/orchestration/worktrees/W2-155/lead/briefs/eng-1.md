# Engineer brief: W2-155 (DAEO-ar89), run 2, eng-1

You are the engineer for ticket DAEO-ar89 (W2-155), profile LITE, class C1. Your tree: /home/usain/gov-os-worktrees/W2-155, branch w2/W2-155 (HEAD 25fc5f5c8). Write only inside the allowed paths: src/gov/retrieve/**, src/gov/retrieval/**, tests/unit/retrieve/**, tests/unit/retrieval/**. Search with the Read and Grep tools (no gov retrieve, no gov context in the sandbox); search again once in different words if the first search does not answer.

## Why (the owner's decision)
The warm real-model query p95 (W1-19, W2-13) is 0.54-0.59 s against a 0.5 s budget. The lead's profile: 95 % of the time is the shared reranker's round trips, and 46 of 52 queries send TWO requests because the client's padded request bound `MAX_REQUEST_CHARS` (24,000 = count x longest pair) splits a search's ~30 whole-chunk candidates (~1,300 characters each, 39,000 padded) in two; each request costs a fixed 60-85 ms per model forward. The owner decided (DEC-1159 (2), 2026-11-13; it changes DEC-1067 (f)): raise `MAX_REQUEST_CHARS` from 24,000 to 48,000 so a search's candidates go in one request. The lead read the GPU peak for the worst request at 48,000 (2 pairs of 24,000): +1,384 MiB, within the card's budget.

## The change (nothing else)
1. `src/gov/retrieval/rerank.py`: `MAX_REQUEST_CHARS = 48_000` (comment: DEC-1159 (2), W2-155; the lead's GPU reading: the worst request at the bound, 2 pairs of 24,000, peaked +1,384 MiB, within the card's budget of total less 2,048 MiB).
2. **What each text is read up to must NOT change** (the Interface: `gov retrieve`'s results for the same store and query unchanged: same items, same order, same fields, same scores). Today two things read up to `MAX_REQUEST_CHARS` and would silently grow to 48,000 with it:
   - `fusion.RERANK_LIMIT_CHARS = MAX_REQUEST_CHARS` (src/gov/retrieval/fusion.py:25; `RERANK_CHARS` and retrieve.py:306-307 use it): the chunk is read up to 24,000 characters;
   - `rerank.requests`: `room = max(0, MAX_REQUEST_CHARS - len(query))` cuts each text so its pair is at most the bound.
   Add one constant in rerank.py, `MAX_PAIR_CHARS = 24_000` (the most characters one pair, question and text, is read to: the former bound, so the read is unchanged), use it for `room` in `requests`, and set `fusion.RERANK_LIMIT_CHARS = MAX_PAIR_CHARS` (import it). Keep `requests`' grouping rule as it is (longest first, `fits = max(1, min(MAX_REQUEST_TEXTS, MAX_REQUEST_CHARS // longest))`). Update the comments and docstrings that state 24,000 as the request bound (rerank.py, fusion.py, chunking.py:28, rerank_service.py's docstring) to say: pair read 24,000, request bound 48,000. No signature, output or exit code changes.
3. The unit case, new file `tests/unit/retrieval/test_w2_155_one_request.py`:
   - a planted 52-query-like set: 30 candidates shaped as fusion makes them (`"[path: docs/part-<i>.md]\n" + text`), lengths deterministic between ~300 and ~1,550 characters, padded size (30 x longest pair) above 24,000 and at most 48,000; `rerank.requests` gives ONE request holding all 30;
   - with a deterministic fake reranker (a `reranker=` loader returning a `score(query, texts)` that scores from each text's content, e.g. a hash or length-based float, never from its position in the batch), `rerank.rerank` gives the same items, same order, same `rerank_score` values as the two-batch path (the same call with `monkeypatch.setattr(rerank, "MAX_REQUEST_CHARS", 24_000)`, which must give 2 requests: assert that too, counting the fake's calls);
   - the read is unchanged: a text longer than 24,000 characters is still sent cut to `24_000 - len(query)` characters (assert on what the fake received), and `fusion.RERANK_LIMIT_CHARS == fusion.RERANK_CHARS == rerank.MAX_PAIR_CHARS == 24_000`, `rerank.MAX_REQUEST_CHARS == 48_000`;
   - no request is above 48,000 padded characters or 64 texts for a pool of long chunks (e.g. 40 texts of 20,000 characters: every request at most 2 texts).
4. Existing unit cases in your paths that pin the old value (they assert a behaviour the owner has since decided): change only the pinned figure, with a comment line `# Rewrite-Reason: DEC-1159 (2) (MAX_REQUEST_CHARS 24,000 -> 48,000; the pair read stays 24,000)`:
   - tests/unit/retrieval/test_w2_137_request_cap.py:59 (and any case there whose arithmetic assumes the pair read equals the request bound: e.g. line 89, `len(QUERY) + len(texts[0]) == rerank.MAX_REQUEST_CHARS`, becomes `rerank.MAX_PAIR_CHARS`);
   - tests/unit/retrieval/test_w2_32_whole_chunk.py:40, 438, 474 (same pattern);
   - tests/unit/retrieval/test_w2_112_shared_reranker.py:572.
   Grep tests/unit/retrieval/ for `MAX_REQUEST_CHARS`, `24_000`, `RERANK_LIMIT_CHARS`, `RERANK_CHARS` and check each; change a case only where it pins the old bound or equates the read with the request bound. Do NOT touch anything under tests/acceptance/ or tests/unit/semantic/ (outside your paths; the lead reports such cases).

## Running tests (every pytest, no exceptions)
Through the heavy slot, TMPDIR outside the repository and outside ~/gov-os-runs:
```
mkdir -p /tmp/w2-155-eng && env TMPDIR=/tmp/w2-155-eng PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-155/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/retrieval -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Put any multi-line command in a script under /home/usain/gov-os-worktrees/W2-155/.gov-runtime/scratch/ and run it with bash. Also run tests/unit/semantic/test_fusion.py the same way and report its result (do not edit it). Never send requests to the live shared reranker (DEC-1159 (3)); every case uses a fake reranker. A resource gate's refusal is a wait: retry when it opens.

## Commit (your paths only)
```
git commit -m "W2-155 (DAEO-ar89): <subject>" --trailer "Task: DAEO-ar89" --trailer "Role: engineer" --trailer "Implements: DEC-1125, DEC-1123, DEC-105, DAEO-t6hf" -- <paths>
```
`Implements:` only those four ids; name DEC-1159 and DEC-1067 in the subject or body text, never in `Implements:`. Never `Role: owner` or `Decided-by:`. One or two commits.

## Done when
The change above is committed, tests/unit/retrieval has no red that is not red on 25fc5f5c8 too (check a red there by `git stash`-free means: `git worktree add /tmp/w2-155-eng/base 25fc5f5c8` and run the case there, then remove that worktree), the new file passes, and `git diff --name-only 25fc5f5c8..HEAD` lists only allowed paths.

Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing):
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` the pass/fail counts of tests/unit/retrieval and of tests/unit/semantic/test_fusion.py, and any red with file:line and whether it is red on 25fc5f5c8 too. In `evidence:` the commit hash(es) and the diff stat.
