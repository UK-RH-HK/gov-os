The load rose after your last turn, and the lead ran a fourth pair, both runs at a load of 40 or more. Add it to §4 "Measure" of `docs/research/W2-108-freshness-once.md`, correct every sentence there that says no run reached a load of 40, and review the record's verdict on the query-embedding batching against all eight runs. Write it in your own words, and claim nothing the figures do not show. Change no other file. Commit the record alone, with the same trailers as before, `-- docs/research/W2-108-freshness-once.md`. Then run the acceptance tests once more, reading results only, as before. All the rules of your brief still hold (hooks check before the commit, `git log --oneline -2` and `git status --short` after it, never read `tests/acceptance/W2-108/`, a commit hash only from `git rev-parse --short=12`, refused twice: stop and say so).

**Pair 4 (2026-10-31 12:41 to 13:39 GMT), measured exactly as pairs 1 to 3: the same store and clone, a cold query-vector cache, cProfile, the load sampled every 15 s; before first, then after.**

| pair | run | code | wall s | 1-min load mean (min–max) | samples at load ≥ 40 | 5-min load mean | freshness and status s | query embedding s |
|---|---|---|---|---|---|---|---|---|
| 4 | before-4 | base `f6af39c1665b` | 2,414 | 63.4 (18.6–106.0) | 133 of 145 | 64.6 | 611.4 | 894.4 |
| 4 | after-4 | W2-108 `ee5056be590a` | 1,063 | 48.0 (18.2–77.7) | 38 of 64 | 48.4 | 18.2 | 451.4 |

- Both verdicts: `context-reproducibility: green`, exit 0; 336 retrieval calls and 97 embedder calls each.
- The load fell during pair 4 (the 1-minute load went from 82 at 12:40 to about 30 at 13:21), so the "after" run had the lighter load (48 against 63): part of pair 4's wall-time saving is the load, not the change. The freshness and status times compare cleanly (611.4 s against 18.2 s); the rest does not.
- For the verdict: after-4's wall time less all of its query embedding is 1,063 − 451 = 612 s, still over W2-54's 600 s.
