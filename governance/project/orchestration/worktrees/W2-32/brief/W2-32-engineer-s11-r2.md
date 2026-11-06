# W2-32's engineer, round 2: S11 brought to the harness's v456 and to the pin's speed (DEC-1074 (5))

You are W2-32's engineer (`DAEO-0pyc`), launched by `gov launch` under that ticket's id. The same rules as your round
1 (`/home/usain/gov-os-worktrees/W2-32/.gov-runtime/scratch/brief/W2-32-engineer-s11.md`, with `EMG-d4b-launched.md`
and `EMG-common.md` beside it): read them first. Your branch `w2/W2-32` now holds the designer's tests (`a4c5e9c4`);
never read `tests/acceptance/W2-32/`. `gov accept W2-32` gave 257 passed, 0 failed, 2 skipped, and the review is READY.

## What the CTO's measure found (counts only)
The product with the pool on (60, 40, 2 and both true), through its own `gov`, on the 80 and the spent 60, against the
research harness's v456 on integrate's head (the same content but your own new files):
- **Not the harness, question for question:** 15 of 138 questions differ in hit@5 (the product gains 9, loses 6), and
  47 more differ only in the first gold source's rank. In total the product scores 108 of 138, the harness 105.
- **Slower:** a call's median is 1.75 s with the pool on, against about 0.75 s for today's product (m6), so S11's
  "a plain search's median stays at or under the pin's" is not met.

## What to change (three things, each named in the review or the measure)
1. **The per-file cap after S8's routing (the review's F2).** The harness applies `perfile` after `front` and `pin`;
   your build applies `per_file_first10` before S8's routing, so with routing on, a routed hit can leave more than n
   chunks of one file in the first 10. Place it where the harness does.
2. **No rerank request on a continuation.** The harness reranks a question's 40 once and cuts every page from that
   order; your build reranks the pool again in every call (each continuation is a new process), which is most of the
   extra time. Make a continuation reuse the first call's pool order **without writing any new file**: a read command
   may write only the query-vector cache (DEC-782). The continuation token is the place: carry the pool's order (its
   chunk ids, or what you need to rebuild it exactly) in it, bounded in size, and refuse a token that does not match
   the question. If you find no way within DEC-782, stop and return PACKAGES with the options.
3. **A failed pool rerank (the review's F1):** fall back to today's per-page path for that call, so a failure costs
   ranking only once, never the whole question.

## Verify
- Your unit tests (stand-ins) for each change, with the earlier 39 still passing; the padded bound on every request.
- On stand-ins, the number of reranker requests a question with three continuations sends: one pass (at most three
  requests under the bound), not one per call.
- Then stop and return. The CTO merges nothing new from the designer; it re-runs `gov accept W2-32` and its measure.

**Commits:** `Task: DAEO-0pyc`, `Implements: DEC-1071, DEC-1074`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5
<noreply@anthropic.com>`. **Return:** the sandbox and `ps` checks first, then the twelve labelled fields. Est.: 2 hours.
