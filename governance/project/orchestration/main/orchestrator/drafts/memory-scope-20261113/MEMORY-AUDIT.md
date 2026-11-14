# Memory kept at 95 % per adopted repository: what the product does today and what is missing

2026-11-13, a helper of the CTO (DAEO-sdxk). This is for the owner's question: "each adopted repository's memory
re-measured weekly on the same hidden questions, with the maintenance tooling keeping it from drifting." It is read only:
no tracked file was changed, and no sets root or run folder was opened. The line numbers are at integrate `1fd0066e1`.

## 1. What the adopt skill says today: the verdict set is measured once
- The adopt skill, step 6 (`template/governance/kernel/skills/adopt/SKILL.md:58`; the same in `.rulesync/skills/adopt/SKILL.md:58`): "Declare and measure the verdict set once. A miss stands as it is: the set is never run again. [DEC-1071 (1)-(3), DEC-1098 (1)]"
- The practice record:
  - `docs/research/W2-88-memory-practice.md:221`: "6. Declare and measure the verdict set once."
  - `:91-92`: "Then the measurement set is measured once, as the confirmation."
  - `:190-191`: "a set used to judge a fix is a tuning set from then on; only a fresh blind set gives a verdict, used once"
- W2-88 (closed), in `.tickets/DAEO-2bdu.md`:
  - S13 (`:57`): "The fresh verdict set, used once … A USED marker is written before the first search, and the runner refuses to start once it exists."
  - S16 (`:60`): "It is never run again, never re-scored to pass".
  - F6 (`:73`): "A verdict set … measured twice" is a failure.
- The decisions behind it:
  - DEC-1098 (1): "proven there with its own tuning set and a fresh verdict set, measured once".
  - DEC-1101 (1): "an independent writer writes a fresh set … measured once".
  - DEC-1125 (2): "an independent writer drafts fresh questions, they are measured once".
- **Why the rule exists (the contamination concern):** `W2-88-memory-practice.md:186-188` records the owner's reading under DEC-1074 (1). Once every fix was judged on all 80 questions, both halves had become tuning sets: the hidden half scored 84.6 % against 67.8 % on a fresh blind set, at the same distance from their answers. A set whose results are seen and acted on stops measuring the product and starts measuring how well it was fitted to that set.

## 2. What the product does today for memory over time
**The weekly audit (`src/gov/memaudit/`; W2-170 to W2-173, all closed):**
- **The CLI:** `python3 -m gov.memaudit preflight|void|declare|measure|judge|classes|pool|pool-import|run|due|baseline|status|figures` (`__main__.py:1-2, 38-131`).
- **One cycle,** `run`, in a fixed order (`driver.py:27`, W2-172 S1, `.tickets/DAEO-p8tv.md:30`): writer 1, pre-flight, checker 1, (writer 2, checker 2), void, measure, judge, auditor, classes, pool, figures. Each audit writes a **fresh 40-question set**, named `memory-audit-<date>` (`driver.py:236`; DEC-1126 (5): "Mondays 21:00, 40 questions, the first audit on 11-23").
- **The use-once marker:**
  - `declare` writes `DECLARATION.json`, then `USED` (`O_CREAT|O_EXCL`), before any search, and refuses with exit 3 once `USED` exists (`declare.py:1-5, 234-235`; `layout.py:77-79` "a set is measured once"; W2-170 S3 and F2, `DAEO-61vm.md:27, 33`).
  - `measure`, `judge` and `pool` all refuse a used set (`judge.py:179-187`, `pool.py:113`).
  - W2-171 S5 (`DAEO-k1e2.md:30`): "A miss is a result … never run again and never re-scored to pass."
- **The bar:** `declare.bar(n)` = at least ceil(0.85 n) right and at most floor(0.05 n) wrong, with the target ceil(0.95 n) printed beside it (`declare.py:26, 32-33`). 95 % is reported, not judged.
- **The same questions again, retrieval only (the regression pool):**
  - After each audit the pool is re-run through the retrieval measure only (hit@5 and full evidence, no model tokens): the whole pool up to 400 questions, else a seeded draw of 400. A fall of 3 points is a "regression". Then the audit's questions join the pool (`pool.py:3-7, 30`; W2-171 S7, `DAEO-k1e2.md:32`).
  - So hidden questions are already re-run weekly, but only for retrieval figures and never against the 95 % end-to-end bar.
  - `pool-import` loads Gov OS's own 79 + 138 questions, once (`pool.py:29-32, 98-100`).
- **The active and stable rule** (`schedule.py:174-205`, W2-172 S5, `DAEO-p8tv.md:34`):
  - weekly for the first 3 measured audits;
  - then monthly once the last 3 had churn under 5 %, no retrieval change in 28 days, a pass and no pool regression;
  - back to weekly at 10 % churn, a retrieval change, a miss or a pool regression (`:26-27, 180-194`).
  - The retrieval paths it watches are Gov OS's own (`src/gov/retrieval/**`, … `schedule.py:18-22`).
- **The digest block:** 12 lines, counts and ids only: the audit, the mode, the verdict, HIT5, the misses by class, the pool, the retrieval change (`digest.py:56-104`; W2-172 S7). `status --since` says whether a retrieval change has been audited yet (W2-172 S8).
- **Where it runs:** one folder per machine, `~/gov-os-runs/indep/memaudit/` (`schedule.py:48-55`; `GOV_INDEP_RUNS_DIR` overrides it), with one `AUDITS.log`, `HISTORY.jsonl` and `STARTS.log`. The main line is `w2/integrate`, else `main` (`:62-67`). The store is `integration_store` from `rebuild.yaml` (`:70-82`).
- **Scheduled?** Not yet, even for Gov OS. The cron is a later ACT (ACT-MEMORY-AUDIT-CRON-1, class (b), `ACT-MEMORY-AUDIT-INSTALL-1.md:72, 183`; the wrapper `memaudit_cron.sh` is W2-172 S9). No crontab line names it, and no `~/gov-os-runs/indep/memaudit/` exists on this machine today.
- **Not built:** DEC-1101 (1)'s weekly count of agents' "not found" and "may be incomplete" answers. The phrase appears only in the reader prompt (`prompts.py`).

**For an adopted repository (W2-88, closed):**
- A9 writes `memory-audit/AUDIT-RECORD.json`, the three brief variants and an `ACT-WALLS/` package (S18, S19, S22, `DAEO-2bdu.md:61-62, 65`; interface `:266-272`).
- It starts no audit, writes no cron line and applies no ACT (`fabric.py:7`).
- The first scheduled audit waits for the verdict set's `USED` (S21, `:64`). The tuning and verdict sets then join that repository's pool.
- So the same tool is meant to run there, on DEC-1125 (2)'s cadence (weekly while active, monthly once stable). It runs only after the repository owner's operator applies the walls and cron ACT. Nothing has run in an adopted repository yet (EXAMIN's copy at W2-27 is the first).

**Maintenance against drift:**
- **The store current after every merge:** `gov rebuild --integration <branch>` (W2-116, `DAEO-f58b`, **in progress**) keeps a double-buffered store; a failed build keeps the last good one (`src/gov/rebuild/integration.py:1-25`). For an adopted repository it is installed through A9's ACT package, never by the tool (`memory_sets.py:37`; `fabric.py:732`; W2-88 S11).
- **A stale layout:** `STORE_LAYOUT_STALE`, and `gov rebuild` rebuilds the store (W2-88 S4 and the layout line; `src/gov/store/layout.py`).
- **Each search result's store commit, and the worker's line-hash check:** W2-138, **in progress**.
- The glossary refreshed with the store (DEC-1096) is built only if its retest helps (DEC-1097 (6)).
- There is no single weekly maintenance job. Refresh, layout, link census and unindexed-path notices are separate tools or not yet built.

## 3. What is missing for the owner's model
**G1. A standing hidden set, re-measured weekly (the core change).**
- **Exists:** a fresh set each audit, used once; the pool re-runs old questions for retrieval only.
- **Would change:**
  - a per-repository **standing verdict set** (about 80, written once at Wave 0 by the independent writer and checker), judged end to end every week on the same questions;
  - `USED` becomes a per-run marker (one judged run per audit commit) instead of a per-set lock.
- **How the owner's model meets the contamination concern:**
  - (i) **walled measurement only:** the set and its run folder stay hidden from every measured role, as today (ACT-GUARD-SETS-1);
  - (ii) **counts only, ever:** no miss is seen by id, not even by the auditor (today `misses.jsonl` goes to the auditor, `driver.py:192`). For the standing set, only the class counts and rank buckets leave;
  - (iii) **it never chooses a fix:** fixes are chosen on the tuning set and on the fresh audits' misses only;
  - (iv) **a fresh set keeps checking the standing one:** the weekly fresh 40 (or a monthly one) stays, and if the standing set's score drifts more than 5 points above the fresh sets' over 4 weeks, the standing set is declared fitted and replaced (DEC-1074 (4)'s 5-point rule);
  - (v) **staleness:** the checker's staleness pass plus the pre-flight's anchor check at each audit commit; a question whose gold moved is dropped (counts only), not re-labelled.
- **Size:** medium. About 300-450 LOC in `gov.memaudit` (a `standing` mode in declare, measure, judge and driver; counts-only misses) plus tests, and a brief and walls change by ACT.

**G2. The bar at 95 %.**
- **Exists:** judged at 85 % with wrong claims at most 5 %; 95 % is a printed target (`declare.py:32-33`).
- **Would change:** pass at ceil(0.95 n). On 40 questions that is 38 (one miss is 2.5 points), so the standing set should be 80 (76 of 80).
- **Size:** small in code (one function, the digest line, tests), but a decision change.

**G3. Per-repository scoping of the audit's state.**
- **Exists:** one runs folder and one set of logs per machine (`schedule.py:48-55`). The retrieval globs are Gov OS's (`:18-22`). `pool-import` is fixed to Gov OS's sets (`pool.py:29-32`).
- **Would change:** the runs folder keyed by repository; the retrieval trigger read from the adopted repository's path map and `retrieval.yaml` plus the gov pin; the pool seeded from that repository's own tuning and verdict sets.
- **Size:** small to medium, about 100-150 LOC. `GOV_INDEP_RUNS_DIR` already allows a per-repository wrapper.

**G4. The schedule installed and running.**
- **Exists:** no cron for Gov OS yet (ACT-MEMORY-AUDIT-CRON-1 not written); for an adopted repository only an ACT package, applied by its operator.
- **Would change:** the cron ACT for Gov OS before 11-23; a per-repository cron line in A9's ACT package.
- **Size:** small. ACT text and a wrapper argument, no product logic.

**G5. Maintenance as one weekly job.**
- **Exists:** W2-116 and W2-138 are in progress; the refresh is per merge; the layout check is on open.
- **Would change:** a weekly maintenance pass before the re-measure: the store at the main line's head, layout current, link census drift count (DEC-1072 (1)), unindexed paths (DEC-1101 (1)'s notice) and the "not found" counts. It reports in the digest block.
- **Size:** medium. About 150-250 LOC, mostly calling existing checks, after W2-116 and W2-138 land.

**G6. The skill and practice text.**
- **Would change:** the adopt skill's step 6 and the practice record §5 and §6 say "measured once" (`SKILL.md:58`, `W2-88-memory-practice.md:191, 221`). They become: the verdict set declared and measured at Wave 0, then re-measured weekly as the standing set under G1's walls.
- **Size:** small. A kernel skill change under CAP-33 (CIT-P, review, the owner's bytes).

## 4. Recommendation (the smallest change set)
- **What to build:** G1, G2 and G6 together are the owner's model; G3 and G4 make it run per repository; G5 can follow.
- **The smallest set:** a `standing` mode in `gov.memaudit`, with these parts:
  - one standing set of 80 per repository;
  - a per-run marker;
  - counts-only misses and no auditor reading of its misses;
  - a 95 % pass line;
  - the fresh 40 kept monthly as the drift check on the standing set.
- **Around it:** the runs folder keyed by repository; the adopt skill's step 6 re-worded; the cron ACT for Gov OS and the per-repository cron line in A9's ACT package.
- **How to file it:** one P1 package (DEC-974: it is new work, no ticket without the owner's decision), about 500-650 LOC across two tickets (memaudit, adopt skill and record). The skill change goes by CIT-P.
- **Decisions it would change:**
  - DEC-1101 (1) and DEC-1125 (2) ("fresh set … measured once" becomes "a standing set re-measured weekly, with a fresh set as its drift check");
  - DEC-1098 (1) ("a fresh verdict set, measured once");
  - DEC-1097 (1)(d) and W2-88 S14 (the bar of 85 % becomes 95 %);
  - DEC-1074 (1) as the practice reads it ("only a fresh blind set gives a verdict, used once");
  - DEC-1126 (5) (40 questions a week);
  - W2-88's S13, S16 and F6 and W2-170 and W2-171's use-once lines, re-baselined under DEC-105 (apply now, defer or re-baseline, each costed in the package).
