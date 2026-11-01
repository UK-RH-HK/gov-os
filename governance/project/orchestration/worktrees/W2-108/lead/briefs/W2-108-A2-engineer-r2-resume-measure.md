The lead's measure for KPI 4 is in. Fill in the "Measure" section of `docs/research/W2-108-freshness-once.md` with it, and write the record's verdict on whether the query-embedding batching (the package's option (b), 96 embedder calls) is still needed, from these figures. Write it in your own words, and claim nothing the figures do not show. Change no other file. Then commit the record alone, with the same trailers as before (`Task: DAEO-zoex`, `Role: engineer`, `Implements: DEC-969`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`), `-- docs/research/W2-108-freshness-once.md`. Then run the acceptance tests once more, reading results only (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-108/src python3 -m pytest tests/acceptance/W2-108 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`). All the rules of your brief still hold: the hooks check before the commit, `git log --oneline -2` and `git status --short` after it, never read `tests/acceptance/W2-108/`, refused twice: stop and say so.

**How it was measured (by the lead, outside the sandbox, 2026-10-31 10:04 to 12:01 GMT):**
- One store: a scratch clone of this branch at the ticket's base `f6af39c1665b` under `/tmp/gov-os-lead-W2-108/measure`, fully rebuilt once (`gov rebuild --json`, exit 0, under the machine-wide rebuild lock). The store was the same for every run; only the code under test changed: "before" is the base's `src/` (`f6af39c1665b`), "after" is this branch's `src/` at `ee5056be590a`.
- Each run: `python3 -m cProfile -o <file> -m gov.context.context_check` in the clone's root, with `PYTHONPATH` set to the code under test. The query-vector cache (`.gov-runtime/query-vector-cache.db`) was deleted before every run, so each run embeds the same questions cold (97 embedder calls each). The 1-minute load was sampled every 15 s during each run. The runs went in three back-to-back pairs (before then after, after then before, before then after), so each pair saw about the same load.
- "Freshness and status" is cProfile's cumulative time in `semantic._status` plus `lexical.freshness` when not called from `_status`. "Query embedding" is the cumulative time in `semantic.query_vector`. The wall time includes cProfile's own overhead.
- The machine has 20 processors. The load is not controlled: it is what the other sessions on the machine made.

**The figures (every run's verdict: `context-reproducibility: green`, exit 0; 336 retrieval calls each):**

| pair | run | code | wall s | 1-min load mean (min–max) | samples at load ≥ 40 | freshness and status s | query embedding s |
|---|---|---|---|---|---|---|---|
| 1 | before-1 | base | 1,141 | 34.0 (16.1–45.8) | 19 of 69 | 360.0 | 259.3 |
| 1 | after-1 | W2-108 | 940 | 36.2 (17.0–46.8) | 23 of 57 | 17.0 | 372.9 |
| 2 | after-2 | W2-108 | 406 | 19.6 (12.5–26.5) | 0 of 25 | 10.9 | 33.7 |
| 2 | before-2 | base | 876 | 22.6 (9.8–40.3) | 2 of 53 | 291.6 | 161.0 |
| 3 | before-3 | base | 625 | 12.6 (0.1–38.7) | 0 of 38 | 230.6 | 67.5 |
| 3 | after-3 | W2-108 | 300 | 10.1 (8.0–20.3) | 0 of 19 | 8.7 | 6.9 |

**Call counts from the profiles:**
- Before, each run: `lexical._tracked` was called 672 times, `semantic._wanted` 336 times and `semantic.embedded` 17,615,472 times.
- After, each run: `lexical._tracked` once, `semantic._wanted` once, `semantic.embedded` 52,427 times, `lexical._checked` 672 times (10.4 to 16.3 s in all, mostly the stat sweep `_stamps`).

**What the lead notes for you to weigh (the verdict is yours):**
- No run's mean load reached 40. The machine's load fell during the measure: pair 1 ran with a mean of 34 to 36 (peaks 46 to 47, about a third of its samples at 40 or more); a waiter for a load of 40 or more held from 11:00 to 11:46 and the load fell to 0.2 instead. Say so plainly in the record: KPI 4 asks for one load of 40 or more, and this measure's highest is the mean 36.2 (peaks 46.8). The original profile (the package, 1,252 s at load 40 to 70) is a different measure on a different store; keep it apart from these figures.
- W2-54's limit is 600 s (its tests time the check at 600 and 630 s).
