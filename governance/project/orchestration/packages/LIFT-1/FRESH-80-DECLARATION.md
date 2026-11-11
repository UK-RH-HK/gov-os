# The fresh 80, declared before any search (FRESH-80-1 §3.4; DEC-1097 (1))

Declared by the CTO (session `ad44f5fe`), 2026-11-08, after the pre-flight (every check as expected) and before any search of the 80; the scripts pinned `FRESH80-REVIEWED.sha256` = `d621d58bc697…`. **Committed before any search of the 80**, after the pre-flight;
the blanks (four underscores) are filled from the pre-flight's output. Counts only: no question, label or answer of the 80 is
named here.

## 1. The set
- **The set:** `memory-verdict-2`, part hidden, 80 questions (DEC-1078), in the sets root (`~/gov-os-eval`).
- **ACT-GUARD-SETS-1 applied** (DEC-1097 (2)) at commit `15952bbfa` (the owner's operator, 2026-11-08); the guard check 453 run, 0 failed, PASS (live hook
  `bd545af83198`); the live worktrees merged: none live (no worker or lead running; a reused worktree merges integrate
  before its next launch). The tools refuse to write anything unless the main tree's `sets_root_hidden` block (with the run folder's and
  the 80's globs) and the live hook's sets-root rule are in place (checked by content).
- **Its digest** (`LC_ALL=C sha256sum *.yaml | sha256sum` in its folder, `preflight.py` item 1): `c4668b57b32f4ce8c8a46d073b5cee35faf5dc17942a14d4a5347da783ccc60c`. It is
  recomputed by `run_measure.sh` before USED and before each attempt, by the reader at its start, and by the figures,
  against this line and the pre-flight's. The checker's
  digest after its staleness pass matches: yes. Files changed since DEC-1078's close: 0 (the checker's re-labelled
  count: 0: unchanged 80, changed 0, ambiguous 0; the writer's step skipped).
- **Anchors at the measured commit** (item 2, the measure's own loader): found once 179; found more than once 0;
  missing and re-anchored by commit 0; missing with lines unchecked 0; unresolved 0 (of 179 source alternatives). Any source not found
  once was fixed by the writer and checker before this record, or stays as the measure scores it (not found), named:
  none.
- **The nonexistent-id question** (item 6): 1 by category; it names no token the product reads as an id
  (`lexical.ids_in`), so the product's check cannot run; the owner's checker searched the tree at `c00d525f` for the
  whole token: nowhere. **Kept apart, not dropped** (`--item6-outside-nowhere`, reviewed READY); DEC-1071 (5)'s
  `UNRESOLVED_IDS` stop is **not applicable** to it (the product cannot stop on a token it does not read as an id), so
  it is reported apart on the reader's answer alone, outside the bar. If no, it is dropped from every figure and the drop reported (decided in FRESH-80-1 item 6): the declared
  drop, not a stop.
- **The families line** (item 5): `families: contract (4 members), kernel (3 members), agents (2 members)`: as required.
- **The clone** (item 12): clean yes; HEAD `c00d525fd420` yes; the pool's lines as window 4 yes; gov at
  `pin-bcea09060ebc` yes; store sha256 `60ea492753004905…` (recorded again before and after the run).

## 2. The judged condition (one only; DEC-1097 (1)(a))
- **Retrieval:** window 4's pin `pin-bcea09060ebc` (`~/.local/bin/gov`), the pool on, on E0's clone
  `~/gov-os-runs/D4B/w4-e0/repo` at `c00d525fd4200303f4ad0fcc7e013d49e60dc2a6`, its store as written by E0
  (2026-11-07 15:58; not rebuilt); the live shared servers (the two embedders, the 0.6B reranker service).
- **The measure:** `python -m gov.retrieval.measure memory-verdict-2 --part hidden` by the pin's python, default
  budgets (batch 10, bundle 6,000 tokens, stack 24,000), `GOV_ROLE=orchestrator`, `GOV_STORE` and `GOV_TICKET` unset,
  every call kept (`GOV_KEEP`), by `drafts/fresh80/run_measure.sh` (pinned: `FRESH80-REVIEWED.sha256`).
- **The bundle:** today's bundle, the first call's, as the measure kept it.
- **The reader:** `claude-opus-5-5`, effort high, no tools, no transcript; E2's instruction (with "may be
  incomplete"), schema and prompt form, read byte for byte from `drafts/d4b/e2_run.py` (sha256
  `f0099fd67ef0cb6d9f6f296a86dc4893a1fe15f3110e30074397d7cbcab9d60a`); search again in its own words, later searches
  live with the pinned gov on the same clone; at most three attempts; **A2 is the A3 run cut at two**, computed as in
  E2 (a request for one more search at the cut counts as not found).
- **The labelling rubric:** `docs/research/memory-measure-audit/RUBRIC.md` version 2 (`cc9c94d42a54`; the 80's writer's).
- **Grading:** `claude-opus-5-5`'s grade counts; `claude-sonnet-5-5`'s agreement reported; E2's grader instruction. A
  grade that never comes fails closed (a wrong claim) and is counted. No re-grading after the run.
- **The citation:** the measure's matcher (`_match`), source families on; right end to end = the answer graded
  correct and a cited range matching a gold source.
- **Script:** `drafts/fresh80/fresh80_reader.py` (projection 15 USD, brake 30).

## 3. The denominator and the bar (DEC-1097 (1)(d); FRESH-80-1 §4.3)
- **The denominator:** 79 (the 80 less the nonexistent-id question, reported apart). A question with no row (a brake
  stop) counts as not right; no question leaves the denominator once figures exist.
- **The bar (K9), on the observed figure:** right end to end at A2 **at least 85 %** (at least **68 of 79**; 67 is
  84.8 % and misses) **and** wrong claims **at most 5 %** (at most **3 of 79**; 4 is 5.1 % and misses). **Target 95 %**
  (at least 76 of 79).
- **Beside it, never in it:** the 95 % interval (the exact Clopper-Pearson interval named, Wilson's beside it; the exact Clopper-Pearson interval, or Wilson's as in
  FRESH-80-1 §4.3's example; both are printed); hit@5 (and hit@10, hit@20, MRR, in the bundle, full evidence); "answer
  correct, citation aside"; the stricter of the two grades; grader agreement; A1 and A3; the nonexistent-id question
  (right or not, and whether the product stopped with `UNRESOLVED_IDS` naming its id, DEC-1071 (5)); the failed later
  searches (item 17); the citations outside every received item (item 18).
- **Figures:** `drafts/fresh80/fresh80_figures.py`. The verdict line is computed from the judged condition only.

## 4. Data conditions: data only, not judged (DEC-1097 (1)(c))
Each runs after the judged run and after the hold ends, has its own projection and a brake at twice it, and is
reported in a separate table headed "data only, not judged". No figure here chooses anything (§3.4 item 4).
| condition | what | projection | brake |
|---|---|---|---|
| retrieval figures | from the measure itself | 0 | |
| A1, A3 | from the judged run | 0 | |
| e3: top 5, 10, 20, 40 unranked | one reader call each on the 80's first calls | 36 | 72 |
| e3sa: top 20, 40 unranked with search again | up to three attempts, later searches live | 19 | 38 |
| e5: 12,000 tokens, page 40 | a second live retrieval of the 80, one reader call | 17 | 34 |
| e4: M3 (zerank + gte), M1 (the 0.6B + gte) | the 80's candidates through the harness, a scoring window (`f80_e4_window.sh`, e4_window.sh's F1 restore fix kept), replays, one reader call each | 22 | 44 |
| e2g: the prototype glossary consulted | E2's condition, the glossary at each search again | 14 | 28 |

**The e2g figure on the 80 cannot decide GLOSSARY-1 (DEC-1097 (6)), nor M3's or M1's figure M3's adoption (DEC-1097 (5)): a later adoption chosen on the 80 would have no fresh set to confirm it.**

## 5. The fault rule (FRESH-80-1 §3.5, as written)
- **Before the first search** (the pre-flight, a load fault, the control outside 34 ± 2 on the visible 40): the set
  is unused; fix, then run.
- **During the measure** (a non-zero exit, an output not whole, the backstop tripping, the machine stopping, **or a
  retrieval answered otherwise than declared: a search whose bundle was not reranked by the shared service (`rerank.by`
  other than `service`), a route (lexical or semantic) missing or unavailable, or the pool's rerank fallen back**): the
  run stops; its partial outputs are kept and reported, never as the verdict; **one restart from the start follows**,
  same commit, store and command, into a new kept folder (`attempt-2`), **whatever the partial figures show**; the
  restart's figures count; a second fault stops everything and goes to the owner.
  - Before the restart: the live reranker answers READY from the pin, a probe search is answered by the shared
    service with every route, and the control passes again. If not, nothing is spent and the restart does not run
    into the same outage: to the owner, and the one restart is taken when the servers are back.
  - A store whose sha256 changed during an attempt stops everything (a restart could not run on the same store).
- **During the reader run:** it resumes (only questions with no row run); a reader or grader call that returned
  nothing is run once more; a later search that fails, or is answered otherwise than declared (as above), is a failed
  search, counted and named (item 17); the brake stops new questions, and the owner decides.
- **After the run:** no re-run. Re-scoring the kept outputs (`--kept`, no new search) only to correct a named fault in
  the scoring; both figures shown; the owner decides.
- **One shot:** `runs/fresh-80/USED` is written before the first search; run_measure.sh refuses to start once it
  exists (except the one `--restart`).

## 6. The hold (FRESH-80-1 item 13)
From the control to the end of the judged reader run: no commit on `w2/integrate`, no store rebuild, no GPU window
(`log/act-in-progress.txt` holds the line `FRESH-80 HOLD`, written by `drafts/fresh80/hold.sh begin` only when no
other mark stands, and ended by `hold.sh end` only when it is that hold); W2-139 and W2-140 held. integrate's head and the
integration store log's new lines are recorded over the run window.

**Basis:** question 1 (memory judged by what agents answer, on a set used once, by a condition chosen beforehand).
