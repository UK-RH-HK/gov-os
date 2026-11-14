# MEMORY-AUDIT-P1: the standing hidden set, two tickets and the adopt skill's CIT-P, for the owner's decision

> **Decided 2026-11-14 (DEC-1179):** the owner's yes, with O3 (b) ("weekly while a repository is actively worked on, monthly once it is stable, back to weekly at once on a miss, a retrieval change or churn of 10 % or more"). The draft's "DEC-1177" reads DEC-1179 throughout (DEC-1177 went to P-W2-184-1). W2-187 is DAEO-0cd2, W2-188 is DAEO-zlog.

2026-11-14. Drafted by a helper of the CTO (orchestrator DAEO-sdxk). Nothing is filed, recorded or committed. No sets root,
run folder or hidden file was opened.

The decision is numbered DEC-1179 here, provisionally. DEC-1176 is the W2-88b decision: the owner said yes at 00:33, and
it is not yet recorded. The tickets are W2-187 and W2-188, the next free W2 numbers after W2-186. Their tk ids are
assigned at filing; the drafts use DAEO-NEW1 and DAEO-NEW2.

Beside this file:
- `W2-187-ticket.md`: the memaudit ticket.
- `W2-188-ticket.md`: the adopt skill and practice record ticket.
- `W2-188-CIT-P.md`: the skill's CIT-P draft.

The reconciliation it builds on, with file and line for each part, is `../memory-scope-20261113/MEMORY-AUDIT.md`.

---

## 1. Context

**What happened.**
- On 11-13 the owner set the model: each adopted repository's memory is built in its own Wave 0, measured on its own
  hidden questions to at least 95 %, and kept there by weekly maintenance and re-measuring (DEC-1176 (1)).
- DEC-1176 (1) left the "how" open: "until then DEC-1101 (1), DEC-1125 (2), DEC-1098 (1) and the adopt skill's step 6
  stand as written".
- The reconciliation found six gaps, G1 to G6, between the owner's model and what the product does.
- On 11-14 the owner chose (a): "G1 to G6 as you set them out, the standing hidden set judged end to end every week as
  we measured Gov OS, with double search and agents as second rerankers, at 95 %, counts only, with the monthly
  fresh-set check against fitting. File the two tickets and the skill's CIT-P as one P1 package for my decision."

**What the product does today** (W2-170 to W2-173 and W2-88, all closed):
- **Each audit is a fresh 40, used once.** A `USED` marker locks each set (`src/gov/memaudit/declare.py:234-235`,
  `layout.py:77-79`).
- **Old questions come back for retrieval only.** They are re-run in the pool for retrieval figures, never against
  the end-to-end bar (`pool.py:3-7`).
- **The bar is judged at 85 %.** 95 % is printed beside it, not judged (`declare.py:32-33`).
- **There is one state folder per machine,** and it watches Gov OS's retrieval paths only (`schedule.py:18-22, 48-55`).
- **Nothing is scheduled yet.** ACT-MEMORY-AUDIT-CRON-1 is not written.
- **There is no weekly maintenance job.**
- **The adopt skill measures once.** It tells every adopted repository to measure its verdict set once and never run it
  again (`template/governance/kernel/skills/adopt/SKILL.md:58`).

**Why "used once" exists** (the contamination concern):
- Once every fix was judged on all 80, both halves of the first set became tuning sets.
- The hidden half then scored 84.6 % against 67.8 % on a fresh blind set (DEC-1074 (1);
  `docs/research/W2-88-memory-practice.md:186-191`).
- The standing set meets this concern with four walls, all decided: walled measurement, counts only, never choosing a
  fix, and a fresh set checking it each month.

## 2. What: the shape decided, and how it is built

### 2.1 How the standing set is judged: exactly as Gov OS's memory was measured

"Double search, agents as second rerankers" is the fresh 80's judged configuration. FRESH-80-1 §3.1 set it, DEC-1097
(1)(a) chose it, and DEC-1098 (1) accepted it at 78 of 79 right, 0 wrong. `gov.memaudit judge` already runs it, and the
standing set reuses it unchanged:
- **The bundle:** the store at the audit commit, served with the standard: the 0.6B through the one shared reranker,
  the pool on, the 6,000-token bundle widened to sections. Each question's first bundle comes from W2-61's measure,
  `gov.retrieval.measure`.
- **Agents as second rerankers:** the reader (`claude-opus-5-5`, effort high, no tools, the pinned prompt in
  `src/gov/memaudit/prompts.py`) reads the whole ranked bundle and itself decides what answers. That is a second
  ranking after the 0.6B. In E3, the ranked, widened bundle read whole gave 114 of 138 right in one call, against 84
  for the top 5, 89 for the top 10, 101 for the top 20 and 101 for 40 unranked (`packages/LIFT-1/E3-RESULT.md`).
- **Double search:** the reader may search again once with its own words. The A2 cut is judged; the run allows 3 and
  keeps A1 and A3 as data.
  - E2 gave 115 right at one search and 128 at two, of 138.
  - In E3-SA a second search never lost a right answer: 15 and 14 gains, no losses (`E3-SA-RESULT.md`).
- **Grading:** `claude-opus-5-5` grades and `claude-sonnet-5-5` checks agreement. The citation is checked by the
  measure's matcher with source families.
- **The figure:** right end to end at A2 (the answer correct and its citation right), with the nonexistent-id questions
  apart.
- **A name clash to avoid:** "a second reranker" in W2-88 S10 and its failure line means a second reranking model, which
  stays forbidden. The reader is not one, and the tickets say so.

### 2.2 The two tickets (one P1 package; DEC-974)

**W2-187 (DAEO-NEW1): the standing hidden set in `gov.memaudit`.** Class implementation, role engineer, profile FULL.
It covers G1, G2, G3, G5 and G4's code, about 700 lines plus tests.
- **G1, the standing set and its method:**
  - It adds a `standing` mode beside today's fresh mode and shares its judged path.
  - One standing set is live per repository. For Gov OS it is a new 80 (O1); for an adopted repository it is its Wave 0
    verdict set.
  - The set is judged at most once per ISO week (a per-week `USED` instead of a per-set lock), by exactly §2.1's method.
- **G2, counts only and the bar:**
  - No `misses.jsonl` and no auditor. Only counts leave the run folder: right, wrong, not found, the misses by outcome
    and by rank bucket, and the questions dropped by the anchor check.
  - The bar is ceil(0.95 n) right end to end for standing and fresh runs alike: 76 of 80, 76 of 79, 38 of 40.
- **The checks around it:**
  - Staleness is handled by count.
  - At each fresh run the tool compares the standing set with the fresh set (§2.4).
  - The states of the below-95 rule are recorded, with `status --repair` for the release step.
- **G3, state per repository:** the runs folder is keyed by repository. A retrieval change is read from the gov pin,
  the repository's `retrieval.yaml` and its path map. `pool-import` reads that repository's own sets.
- **G5, a weekly `maintain` pass before each standing run:**
  - the integration store at the head, by one refresh through W2-116;
  - the layout current;
  - new `gov links` findings;
  - unindexed paths;
  - the runs' "not found" answers.

  It reports counts and never gates.
- **G4's code:** the cron wrapper takes `--repo`, and A9's ACT package writes the repository's cron line as text.
- **Revised tests:** six acceptance files of W2-170, W2-171 and W2-172 pin the old 85 % bar. The ticket's independent
  test designer revises them, about 16 lines of values (DEC-1156 (7)).
- **Dependencies:** W2-116 (closed) and W2-138 (in progress: each result's store commit).
- **Not a dependency of W2-46 or W2-47** (§5.3).

**W2-188 (DAEO-NEW2): the adopt skill's step 6 and the practice record.** Class spec, role product-spec, profile STANDARD.
It covers G6 and G4's text, about 60 lines.
- **The skill:** A9's step 6 is re-worded. The verdict set is declared and measured once at Wave 0 as the first
  verdict; from then on it is the repository's standing set, judged end to end on the same questions every week (monthly
  once the repository is stable, O3), as Gov OS's memory is judged, at 95 %, behind the walls, counts only. It never
  chooses or judges a fix, and a monthly fresh set checks it for fitting.
- **The cron paragraph:** a new paragraph after A9's steps says the weekly cron line comes in A9's ACT package for the
  repository's operator and is never installed by adoption.
- **The practice record:** three places are re-worded, and a new §9 states the method, the walls, the check against
  fitting and DEC-1179 (4)'s rule word for word.
- **Why it goes by CIT-P:** a kernel skill path, so the CIT-P, one independent review, the owner's approval of the
  bytes, a version bump to 1.1.0, and the `.claude` copy by the copies ACT after W2-187 merges.
- **W2-88a's cases stay unrevised:** the new step keeps "declare", "measure", "the verdict set" and "once", so its
  matcher passes. This was checked on the draft text with `check_steps`, with no problems.
- **One departure from the brief:** G4's cron line in A9's ACT package is code (`src/gov/adopt/memory_sets.py`,
  `walls_act`), which the product-spec role cannot write. That code moves to W2-187 (S11), and W2-188 carries only its
  text.

### 2.3 Around the tickets (the CTO's work, not tickets)

- **ACT-MEMORY-AUDIT-CRON-1** (class (b), crontab), for Gov OS. The CTO builds it after W2-187 merges, and it is
  reviewed, given the owner's yes and applied by the operator before 11-23. It installs one line: Mondays 21:00,
  `memaudit_cron.sh --repo <Gov OS>`. That line runs the maintenance pass, the standing run and, when due, the fresh
  cycle.
- **The standing set's writer brief variant.** The approved writer brief weights fresh questions toward recent change;
  the standing set needs a broad sample of about 80. A variant, hashed, goes to the owner for approval (class O,
  `indep-briefs`; DEC-1101 (2)). Then the independent writer and checker write it, in at most two rounds, before 11-23.
- **Records** (DEC-851):
  - DEC-1179 in the register;
  - "Changed by: DEC-1179" on DEC-1074, 1097, 1098, 1101, 1125, 1126 and 1176;
  - the re-baseline marks of §5.5 on W2-88, W2-170, W2-171 and W2-172;
  - DECIDED-NOT-DONE rows;
  - the WBS and plan rows for W2-187 and W2-188;
  - the next status block naming both tickets with DEC-1179 (DEC-1169 (2)).

### 2.4 The monthly check against fitting (DEC-1179 (3), proposed rule)

At each fresh run, F is the fresh set's right-end-to-end per cent, and S is the mean of the standing set's last four
weekly figures.
- **S − F ≥ 5 points:** the standing set is declared **fitted**. It is retired: no further judged run, and it joins the
  pool as a diagnostic set, counts only. The writer writes its replacement under the approved variant brief. The
  replacement's first run is the new baseline.
- **F − S ≥ 5 points:** the standing set may be stale or harder than the product now is. The checker's staleness pass
  runs on it, counts only. It is not replaced.
- **With fewer than four weekly figures:** `drift: not yet (k of 4)`.
- **The noise, honestly:** on two sets of 80 at about 95 %, the spread of their difference is about 3.4 points. The
  5-point rule (DEC-1074 (4)'s bound) is then about 1.5 spreads, so a false "fitted" comes about once in 14 months. Its
  remedy, one replacement set, costs about $25 to $45. On a fresh 40 instead of 80, 5 points is 2 questions; the rule
  would then need the gap in two months running (O2).

## 3. Why it matters

- **A verdict on the same questions every week shows drift as it happens.** The week a merge, a re-pin or a stale
  store costs memory quality, it shows, measured end to end as agents use memory.
- **It keeps the same conditions as the measurement that accepted Gov OS's memory.** The reader is the same, as are
  the bundle, the second search and the grading (§2.1).
- **The four walls keep the set honest.** It is hidden, counts only, never used for a fix, and checked against a fresh
  set. Without them, re-using one set every week would turn it into a tuning set within weeks, as the first 80 became
  one (DEC-1074 (1)).
- **The skill change carries the practice to every adopted repository** (DEC-1176 (1)), with EXAMIN's copy first.
- **It costs less than today's plan.**
  - **The standing 80:** about $12.6 a week (80 × $0.157, FRESH-80-RESULT) and about 45 minutes of wall-clock.
  - **A monthly fresh 80:** about $45 (MEMORY-AUDIT-1 §7, option (b)).
  - **About $100 a month in all,** against about $125 for a weekly fresh 40 (MEMORY-AUDIT-1 §7).
  - **Once, and at each replacement:** the standing set's writing, about $25 to $45.
  - **The owner's time:** about 5 minutes a week for the digest block.

## 4. Options: the owner chose (a); the open choices only

| # | Choice | Recommended | Other | Cost or effect |
|---|---|---|---|---|
| O1 | Gov OS's standing set | **(a)** a new 80, written and checked under the variant brief, before 11-23 | (b) promote the fresh 80's 79 | (b) is spent: it judged the configuration and its miss was read, so the tool's S1 refuses it. (a) costs about $25 to $45 and one evening |
| O2 | The monthly fresh set's size | **(a) 80**, so the drift check compares sets of the size DEC-1074 (4)'s bound was set for | (b) 40, as DEC-1126 (5) has it | (a) about $45 a month; (b) about $25 a month, but the drift rule then needs two months running |
| O3 | The standing set's cadence | **(b)** DEC-1125 (2)'s computed rule kept: weekly while active (Gov OS now, every repository in its first weeks); monthly once stable; back to weekly at once on a miss, a retrieval change or churn of 10 % or more. W2-172 S5's tested rule reused unchanged | (a) every week, always, the owner's words read literally | (a) changes W2-172 S5's `due` rule and its acceptance file, and costs about $12.6 a week for each quiet repository; the skill text drops one parenthesis |
| O4 | What a memory repair holds for Gov OS (R8) | **(a)** the next release cut and the next re-pin, until a weekly standing run is back at 95 % or the owner accepts a named residual. Adopted repositories pin Gov OS's releases, so a regression would ship to all of them | (b) a P1 only, no hold | (a) is a new hold on releases, not on leads (DEC-1157 removed lead holds). It weighs against DEC-1052's "no new gates", so it is named here |
| O5 | When a thinned standing set is replaced | **(a)** below 70 live questions (anchors dropped by count) | (b) never, until the monthly check | (a) about $25 to $45 per replacement |
| O6 | The weekly slot | **(a)** Mondays 21:00, the standing run (about 45 minutes); on a fresh week the fresh cycle follows at about 21:45 and ends about 01:15, before the 02:00 quiet hours | (b) the fresh cycle first at 20:00 | |
| O7 | Is the first standing pass a Wave 2 exit criterion? | **(a) No.** It is a standing practice from its first run on 11-23 | (b) Yes, W2-46 gains a line | §5.3: (b) moves the close to 11-24 at best, or a week later on a miss |
| O8 | A split of W2-187 if its suite shows it over about 900 lines | **(a)** pre-approved now: S10 and S11 as W2-187b, so the lead does not wait for a P1 (DEC-974) | (b) a P1 if it happens | (a) saves about half a day of waiting if the split is needed |
| O9 | DEC-1101 (1)'s count of agents' "not found" answers from work returns | **(a)** left with the CTO's tool; the maintenance pass counts only the audit runs' own | (b) a product home now | (b) needs a source of agents' returns the product does not have; it would be a third ticket |

## 5. Recommendation (confidence: high on the shape and the rule; medium on the dates)

File W2-187 and W2-188, approve the CIT-P route, record DEC-1179 with items (1) to (8) below, and take O1 to O9 as
recommended.

### 5.1 What an audit below 95 % triggers (DEC-1179 (4)): each rule is a proposal for the owner's yes

- **R1. It is recorded as a miss, with counts only:**
  - right, wrong, not found;
  - the misses by outcome and by rank bucket;
  - the questions dropped;
  - the store commit, the gov pin, and whether retrieval changed since the last pass.

  It is never re-run that week and never re-scored, and no label changes after its figures exist (W2-88 S16 kept).
- **R2. A fault is not a miss.** A run stopped by the fault rule before its reader run started (FRESH-80-1 §3.5) may
  start once more that week. A run whose reader run started stands.
- **R3. A P1 to the repository's owner in the next digest** (for Gov OS, the 09:00 digest). It names the counts by
  class and the week's maintenance counts, and never a question.
- **R4. The maintenance pass runs at once,** in the same cycle. Its findings are fixed by role: a stale store refreshed,
  links fixed by the role responsible.
- **R5. The cadence returns to weekly.** The standing set goes to weekly at once if it was monthly (W2-172 S5). The
  fresh set runs every Monday until a standing run passes again, then every 28 days. Fixes need readable misses, and
  only fresh sets have them.
- **R6. Fixes are chosen only on the tuning set and on the fresh sets' misses** (read by the independent auditor),
  structural only (DEC-1071 (1)), and brought to the repository's owner with the counts. The standing set never
  chooses, adopts, rejects or reverts a fix.
- **R7. The standing set is re-judged at the next scheduled run, not before.** No extra run is made to check a fix:
  that would turn it into a tuning set.
- **R8. Memory repair.** It opens on two consecutive standing misses, or on one miss 5 points or more below the last
  passing figure (4 questions on 80).
  - It goes into that repository's own backlog as a P1 ticket proposal to its owner, naming the counts and the fresh
    sets' classified misses (no ticket without the owner, DEC-974).
  - **For Gov OS:** the P1 holds the next release cut and the next re-pin until a weekly standing run is back at 95 %,
    or until the owner accepts the figure as a named residual with its cause by decision id (O4).
    `gov.memaudit status --repair` exits 1 while a repair is open, and the release step reads it.
  - The store stays in service, and no lead is held.
- **R9. With the check against fitting:**
  - A standing set declared fitted (§2.4) is retired. Its passes since the last monthly check count as no evidence.
    The replacement's first run is the new baseline, and R8's count restarts.
  - A monthly fresh set below 95 % is a miss under R1, R3 and R6. It does not count toward R8, which counts standing
    runs. A fresh miss while the standing set passes is what §2.4's comparison exists to catch.

### 5.2 DEC-1179's items (the draft)

1. **The standing set** (G1), judged by §2.1's method.
2. **The 95 % bar and the walls** (G2): counts only, dropping by count.
3. **The monthly check against fitting** (§2.4).
4. **The rule below 95 %** (§5.1).
5. **State and schedule per repository** (G3, G4): the cadence as O3 decides; ACT-MEMORY-AUDIT-CRON-1 by the CTO; each
   adopted repository's cron line in A9's ACT package.
6. **The weekly maintenance pass** (G5).
7. **The decisions changed (§5.4) and the use-once lines re-baselined** under DEC-105 (§5.5).
8. **The tickets:** W2-187 and W2-188 filed, with the CIT-P route. They are not dependencies of W2-46; both close
   before W2-47's audit starts (§5.3).

### 5.3 How they move Wave 2's close

**The CTO's estimate before this package:** about 11-21, range 11-20 to 11-24.

**The sizes:**
- **W2-187:** about 700 lines plus tests. The reconciliation's 500 to 650 covered G1, G2, G3, G4 and G6; the owner's
  choice adds G5, 150 to 250 more. It is FULL, so test design and build run in parallel, then QA and up to two review
  rounds. Elapsed: about 2 to 3 days, landing about 11-17 (range 11-16 to 11-19).
- **W2-188:** about 60 lines. Its review round, the owner's bytes and the copies ACT take about a day. It lands about
  11-16; its promotion and the `.claude` copy follow W2-187, about 11-18.
- **Around them:** the cron ACT, the variant brief and the standing set's writing, all before 11-23.

**The critical path:**
- The close runs through the EXAMIN chain: W2-27, then W2-28 to W2-30, then W2-46's exit run, then W2-47's audit.
- Neither ticket is a dependency of W2-46 (its 76 dependencies name none of the memaudit tickets), and neither feeds
  the EXAMIN chain.
- W2-27 does not wait for W2-188: an EXAMIN verdict set measured once under today's step 6 becomes its standing set
  later (W2-187 S1 accepts a used Wave 0 verdict set).

**The capacity:**
- At 5 to 7 tickets a day with five leads, the two tickets weigh about three average tickets, about half a day of
  throughput.
- The chain is serial, so at the wave's end two or three leads are free beside it. The two tickets fit there.

**The new estimate:**
- **Under O7 (a), the first standing pass not a close criterion:** about **11-21**, range **11-20 to 11-25**. The upper
  edge moves out by a day for W2-187's second review round, the CIT-P's owner step, and W2-47 auditing two more tickets
  and six changed decisions (one to two hours).
- **Under O7 (b), the first standing pass a close criterion:**
  - with the first run at the scheduled Monday, 11-23 21:00: the close is **11-24** at best;
  - on a miss, R7's next run is 11-30, and the close is about **12-01**;
  - with a hand-run baseline about 11-19 or 11-20: about **11-21** on a pass, about **11-28** on a miss.
  - **The chance of a miss:** FRESH-80-1 forecast about 89 % end to end (80 to 94 %) for a fresh 80, and the actual
    was 98.7 %. A first pass at 95 % on a new 80 is likely but not sure.

**What keeps 11-21:**
1. The owner's yes today, with O1 to O9 as recommended in one line.
2. W2-187's test designer and engineer and W2-188's product-spec launched today, in parallel.
3. W2-138 closed by about 11-16.
4. W2-188's review and the owner's bytes in one sitting, and its copies ACT ridden with the next CLAUDE-COPIES ACT.
5. O7 (a).
6. O8 (a), so a split never waits.

### 5.4 The decisions it changes (old quoted, new proposed)

| Decision | Old (quoted) | New (proposed) |
|---|---|---|
| DEC-1101 (1) | "Each audit: an independent writer writes a fresh set, weighted toward what was added or changed since the last audit plus a sample of older areas, cross-checked in at most two rounds; measured once (retrieval figures, and agents right end to end with search again once) against the bar (85 %, target 95 %); an independent auditor classifies the misses by kind; structural fixes only, brought to the owner and judged on the earlier sets; the spent set joins a growing pool of earlier questions, re-run at every audit as a regression check; the next audit's fresh set is the verdict on the fixes." | "Each repository keeps a standing hidden set of about 80, written once by an independent writer and checker under the rubric and held behind the walls; it is judged end to end on the same questions at every standing run, as Gov OS's memory was measured (the standard's bundle read whole by the reader, search again once, A2), against 95 %; only counts leave its run, and it never chooses or judges a fix. A fresh set, written as before and cross-checked in at most two rounds, is measured once each month against the same bar; an independent auditor classifies its misses by kind; structural fixes only, chosen on the tuning set and the fresh sets' misses, brought to the owner and judged on the earlier sets; the fresh set is also the check against fitting on the standing set; the spent fresh set joins the pool, re-run at every audit as a regression check (DEC-1179)." |
| DEC-1125 (2) | "an independent writer drafts fresh questions, they are measured once, misses are classified, drift is fixed." (and "weekly while development is active, monthly once stable") | "the standing set is judged end to end weekly while development is active and monthly once stable (back to weekly at once on a miss); an independent writer drafts a fresh set every 28 days (weekly while a standing miss stands), measured once, its misses classified, drift fixed; the fresh set checks the standing set for fitting (DEC-1179)." Its "replaces ad-hoc re-measures" stands |
| DEC-1098 (1) | "proven there with its own tuning set and a fresh verdict set, measured once." | "proven there with its own tuning set and a fresh verdict set, declared and measured once at Wave 0 as its first verdict and kept from then on as that repository's standing set (DEC-1179)." |
| DEC-1097 (1)(d), as W2-88 S14 and the audit carry it forward | "the K9 bar: right end to end at least 85 % with wrong claims at most 5 %, target 95 %, hit@5 reported beside it" | Stands as the fresh 80's bar, which DEC-1098 (1) met. Added: "From DEC-1179, every memory verdict (the standing set, each fresh audit, an adopted repository's Wave 0 verdict set) passes at 95 %: at least ceil(0.95 n) right end to end; wrong claims and hit@5 reported beside it." K9 is not re-opened |
| DEC-1074 (1), as the practice reads it (`W2-88-memory-practice.md:190-191`) | "a set used to judge a fix is a tuning set from then on; only a fresh blind set gives a verdict, used once" (DEC-1074 (1) itself: "Only a fresh set gives a verdict.") | "a set used to choose or judge a fix is a tuning set from then on; a verdict comes only from a set nothing was tuned on: a fresh blind set, used once, or the standing set behind its walls, counts only, never used to choose or judge a fix, and checked each month against a fresh set (DEC-1179)." |
| DEC-1126 (5) | "The memory audit (MEMORY-AUDIT-1): Mondays 21:00, 40 questions, the first audit on 11-23: approved." | "The memory audit: Mondays 21:00, the standing set of 80 (its first run on 11-23, the baseline); the fresh set of 80 (O2) every 28 days after the standing run, the first also on 11-23. If the standing set is not ready by 11-23, 11-23 runs the fresh set alone and the standing set starts on 11-30 (DEC-1179)." |
| DEC-1176 (1) | "Until then DEC-1101 (1), DEC-1125 (2), DEC-1098 (1) and the adopt skill's step 6 stand as written." | Spent by DEC-1179 |

### 5.5 The use-once lines of closed tickets, re-baselined under DEC-105 (each costed)

For every line below, **apply now** means re-opening the closed ticket to change its code. It is never recommended,
because W2-187 builds the standing mode beside the fresh mode, and the fresh and Wave 0 runners keep their use-once lock.
**Defer** means leaving the line until Wave 3. Its cost is the same each time: the closed line contradicts DEC-1179, and
W2-47's exit audit finds it, about an hour of re-baselining then, on the close path. **Re-baseline** (recommended) means
the CTO's record edit: the old text is kept as "Re-baselined by DEC-1179 (7)", and the new text goes beside it.

| Line | Old (quoted) | New (re-baseline) | Re-baseline cost |
|---|---|---|---|
| W2-88 S13 | "It is used once, as FRESH-80-1 did. … A USED marker is written before the first search, and the runner refuses to start once it exists." | "It is declared and measured once at Wave 0 as the first verdict, as FRESH-80-1 did … the Wave 0 runner refuses to start once USED exists; from then on the set is the repository's standing set, judged only by `gov.memaudit`'s standing mode, counts only (W2-187)." | Text only; the planted-USED cases stay true |
| W2-88 S14 | "It must be at least 85 % with wrong claims at most 5 %; the target is 95 %. On n judged questions that is at least ceil(0.85 n) right and at most floor(0.05 n) wrong claims." | "It must be at least 95 %: on n judged questions at least ceil(0.95 n) right end to end; wrong claims reported beside it." | Text. W2-88's bar case (`test_w2_88_practice.py::test_s15_guard_the_declared_bar_is_ceil_085_n_right_and_floor_005_n_wrong`) compares against W2-170's helper `V.bar(n)`, so it follows W2-187's revision of `w2_170_world.py` with no edit. Its name still says 085; renaming it is optional, for the test designer |
| W2-88 S16 | "It is never run again, never re-scored to pass … options: structural fixes judged on the tuning set and then a new fresh set used once, or the figure accepted as a named residual" | "It is never re-run by the Wave 0 runner and never re-scored … options: structural fixes judged on the tuning set, then the standing set's next run (counts only) and the next fresh set, or the figure accepted as a named residual." | Text only |
| W2-88 F6 | "A verdict set read by a measured role, measured twice, or used to choose anything" | "A verdict set read by a measured role, measured twice by the Wave 0 runner, judged outside the standing mode (one run a week, counts only), or used to choose or judge anything" | Text only |
| W2-88 S21 | "the tuning and verdict sets join the repository's pool" | "the tuning set joins the repository's pool; the verdict set becomes the standing set and joins the pool when retired" | Text; W2-187 S1 holds the code |
| W2-170 S3 | "the bar scaled to n (at least ceil(0.85 n) right end to end, at most floor(0.05 n) wrong claims; the target ceil(0.95 n)) … The runner refuses to start while `USED` exists, so a set is measured once." | "the bar scaled to n (at least ceil(0.95 n) right end to end; wrong claims reported) … The runner refuses to start while `USED` exists, so a fresh set is measured once; a standing set has one judged run a week (W2-187)." | Two acceptance files revised by W2-187's test designer (3 lines), within W2-187 |
| W2-170 F2 | "A set measured twice, or measured without `DECLARATION.json` and `USED` written first." | "A fresh set measured twice, a standing set judged twice in one week, or either measured without `DECLARATION.json` and `USED` written first." | Text; its cases stay true |
| W2-171 S5 | "A miss is a result: a verdict below either limit stands as recorded, is never run again and never re-scored to pass. The runner writes `runs/<audit>/misses.jsonl` …" | "… stands as recorded, is never run again and never re-scored to pass. For a fresh set the runner writes `runs/<audit>/misses.jsonl` …; a standing set writes no misses file, only counts (W2-187 S4)." | Text; its case stays true |
| W2-171 S3 and W2-172 S7 (the bar's values) | the 85 % bar's numbers in the judge's verdict and the digest's bar line | the 95 % bar's numbers | Four acceptance files revised within W2-187 (about 13 lines) |

## 6. What it blocks, and what waiting costs

- **Nothing on Wave 2's critical path waits for it** under O7 (a).
- **The 11-23 audit waits for it.** A yes after about 11-17 leaves no time to build W2-187, write the standing set and
  apply the cron ACT before 11-23. That audit would then run today's fresh 40 at 85 %, and the standing set would start
  on 11-30 or later.
- **EXAMIN's copy follows today's skill text if W2-188 is late.** It is EXAMIN's first full run of the practice
  (DEC-1099 (2)), so it would measure once and never re-run, and later convert under W2-187 S1. The conversion is
  possible, but the skill would teach the old rule meanwhile.
- **W2-47's exit audit would find the contradiction if the package waits past the close.** DEC-1176 (1) says the
  re-measure is "decided separately", and closed lines would still say "measured once". That is one finding per line
  of §5.5.

---

## The owner's yes line

`yes MEMORY-AUDIT-P1: DEC-1179 (1)-(8) as drafted; file W2-187 and W2-188; W2-188's CIT-P route; O1 (a), O2 (a), O3 (b), O4 (a), O5 (a), O6 (a), O7 (a), O8 (a), O9 (a)`

(Change any O-letter in place. "O3 (a)" means every week, always, and adds W2-172 S5's revision to W2-187.)
