# P-FRESH-80-1: a fresh 80 for every memory measure: the amendments, the cost per measure, the first fresh 80 (2026-11-16)

For the owner's decision of 2026-11-16 ~16:5x (recorded by another fork as DEC-120x): "every measure uses a fresh set
of 80 questions, 40 visible and 40 hidden, written by the walled writer for that measure, with the same mix of kinds,
areas and difficulty each time; no set is reused … The measure runs straight after the set is written, on the same
frozen state: no merge, commit or memory rebuild between writing and measuring [(a pinned snapshot of the commit and
its store meets this, so other work need not stop)]. This amends DEC-1179's standing set; bring the amendments and the
cost per measure." And the owner's correction: "My 95 % bar is the end-to-end judged figure, by the configuration DEC-1097 and
DEC-1098 accepted: the reader reads the whole ranked bundle as a second reranker, may search once more in its own
words, Opus grades and Sonnet checks agreement, and both the answer and its citation must be right. W2-15a's hit@5 is a
component figure, not that bar. So every fresh 80 is measured end to end by that configuration, and reports hit@5,
hit@10, hit@20 and the stacked share per mode beside it as diagnostics. W2-15a's first fresh 80 is measured both ways."
Read-only work: nothing committed, no hidden half, held-out material or secret read.

## 1. What already exists, and what it means for the rule
- **The walled writer** is `governance/project/orchestration/tools/indep_launch.py` (W2-149, ACT-INDEP-WALLS-1) with the
  owner-approved brief `governance/project/indep-briefs/memory-audit/writer.md` (sha256 `bc089423…`), checked by
  `…/checker.md` (`cea517b8…`). One writer run writes **40** questions about Gov OS at a pinned commit into
  `<sets root>/fixtures/evaluation/<set>/hidden/`, refusing a set that already exists (`indep_launch.py:1883-1884`), so "no
  set is reused" is already how it delivers. Its quotas are fixed (`writer.md:65-69`): decision 6, contract 4, plan 4,
  ticket 4, exact-string 4, callers 4, code-paraphrase 3, kernel-template 3, multi-file 3, failure-memory 3, history 1,
  nonexistent-id 1; the five areas at least 4 each, no subsystem over 10 (`writer.md:89-93`). **Kinds and areas are
  therefore the same every time; difficulty is not fixed** (only "at most 6 keyword", "at least 2 supersession").
- **The writer's output form is the measure's form** (id, question, gold_answer, sources with path, heading, lines and
  alternatives, commit: `writer.md:149-170` against `src/gov/retrieval/measure.py:249-265`), so a fresh set is measured
  by W2-15a's measure in its four modes unchanged; the measure takes `n` from the set (no 39/40 assumption in code).
- **The judged configuration is in the pinned product:** `gov.memaudit judge` (`src/gov/memaudit/judge.py`, W2-171; the
  fresh 80's `fresh80_reader.py` generalised): the reader (Opus) answers from the whole ranked bundle, searches again
  once through `--gov` or settles; the grader (Opus) judges, a Sonnet grade is kept beside it; the citation is checked by
  the measure's matcher; $0.157 a question; its model calls are `claude -p --safe-mode --tools ""
  --no-session-persistence` (no tools, no session: walled by construction). It runs on an audit's layout
  (`memory-audit-<8 digits>`: writer, `preflight`, checker, `void`, `measure`, `judge`), so each half is one audit.
- **The frozen state** has a precedent: JOB-20261116-02's script (`drafts/w2-15a-close/walled_hidden_counts.sh`) cloned
  the repository at the commit and built that clone's own store (seeded; about one minute), so nothing live stopped.
- **The guard already walls every fresh set's hidden half:** `governance/project/path-map.yaml:639` lists
  `fixtures/evaluation/*/hidden/**` under `sets_root_hidden`. A new set needs only its `evaluation_sets` entry in the
  sets root's path map (the measure refuses an undeclared set, `measure.py:478`), which `gov.memaudit declare` writes itself.
- **The weekly audit is not live yet:** no `gov.memaudit` cron line is installed (crontab), so changing it now costs no
  migration.

## 2. The amendments (old where it stands, new beside it)
| # | Where | Today | Amended |
|---|---|---|---|
| A1 | DEC-1179 (1), `docs/DECISION_REGISTER.md:15129` | "each repository keeps a standing hidden set of about 80, written once … judged end to end on the same questions at every standing run" | "every memory measure, scheduled or at a decision point, uses a fresh 80 (40 visible, 40 hidden) written by the walled writer for that measure at a pinned snapshot of the commit and its store, measured straight after on the same snapshot; no set is reused; **the bar is the end-to-end judged figure at 95 %, by DEC-1097/DEC-1098's configuration (the reader with the whole ranked bundle as a second reranker, one more search in its own words, Opus grading, Sonnet agreement, answer and citation both right); hit@5, hit@10, hit@20 and the stacked share per mode are diagnostics beside it**; the visible half is released for diagnosis after its measures, the hidden half stays sealed" |
| A2 | DEC-1179 (2) | "a stale question is dropped by count" | dropped: a fresh set cannot go stale between writing and measuring; the bar (95 %), the walls and counts-only stay |
| A3 | DEC-1179 (3), `:15131` | the monthly fresh set as the check against fitting; a fitted standing set retired | retired: nothing is reused, so nothing can be fitted |
| A4 | DEC-1179 (4) R1-R9 | "the standing set re-judged at the next scheduled run only"; R9 the check against fitting | "the next scheduled fresh measure"; R9 retired; R1-R8 stand |
| A5 | DEC-1179 (5) | the standing run weekly/monthly (O3 (b)) | the same cadence for the fresh measure (weekly while active, monthly once stable, back to weekly on a miss, a retrieval change or 10 % churn) |
| A6 | DEC-1179 (6), `:15134`; DEC-1178 (1); DEC-1180 (2) | the maintenance pass hands the walled writer the gold questions whose cited lines changed | that item retired (no re-anchoring of an old set); the pass's other counts stay |
| A7 | DEC-1179 options O1, O2, O5, `:15137` | O1 a new standing 80 before 11-23; O2 a monthly fresh 80; O5 a thinned set replaced below 70 | O1 is the first fresh 80, today (JOB-20261116-15); O2 every measure 80; O5 retired |
| A8 | DEC-1186 (4) (G2's re-anchoring route: W2-94's code plus a walls-only ACT) | re-anchor stale gold | kept only for reading an old record; no measure re-anchors (the owner's earlier "if stale gold explains most, re-anchor" is replaced by the fresh 80) |
| A9 | W2-187 (DAEO-0cd2, closed): `gov.memaudit standing declare/run/live` (S1, S2), the drift check, the maintenance pass's stale list, the cron wrapper | one standing set judged weekly | **reopened under this decision** (the owner's line names "W2-187's weekly audit": that is the owner's word, no new ticket): the weekly run becomes the fresh cycle (`gov.memaudit run`, today writer → preflight → checker → void → measure → judge → auditor) for **two** 40-question halves per measure, at a snapshot clone and store it builds itself (today the driver measures the store link, `driver.py:179-188`); `standing` refuses with a code naming the decision; the drift check retired; acceptance revised by a test designer (DEC-1179 O8's split pre-approval covers a W2-187b if it runs over about 900 lines). About 1.5 to 2 days |
| A10 | W2-188 (DAEO-zlog, closed): the adopt skill's step 6 (`template/governance/kernel/skills/adopt/SKILL.md:58,61`, and its `.claude` copy), the practice record `docs/research/W2-88-memory-practice.md:92,191,221,282-291` (§9 "The standing set") | "from then on it is the repository's standing set: judged end to end every week on the same questions … each month a fresh set checks it for fitting" | **reopened under this decision**: step 6 "declare and measure the verdict as a fresh 80 at Wave 0; every later measure writes a fresh 80 at a pinned snapshot and measures it at once; no set is reused"; §9 renamed "Every measure a fresh 80"; a kernel change: CIT-P with review, your yes on the bytes, the `.claude` copy by a copies ACT. About half a day to a day |
| A11 | W2-15b (DAEO-swdu, open), `.tickets/DAEO-swdu.md:28` | "The same metric, corpora and modes as W2-15a … each figure beside its baseline" | "the end-to-end judged figure on a fresh 80 written for that measure (no set reused) against 95 %, by DEC-1097/DEC-1098's configuration; beside it, as diagnostics, W2-15a's metric and modes (hit@5, hit@10, hit@20, the stacked share per mode); each beside the first fresh 80's (JOB-20261116-15) as the baseline, W2-15a's figures shown as history"; the hit@5-against-95 line ("hit@5 is judged against the owner's target of 95 %") re-worded: hit@5 is a diagnostic against CAP-10's floor of 85, the 95 % bar is the judged figure. The CTO edits the open ticket (your line names it) |
| A12 | EXAMIN's Wave 0 measure, the approved brief 2ec48c78 step 5 (`packages/EXAMIN-CTO-wave0-brief.approved-2ec48c78.md:54`) | "a fresh question set written after the memory build by a walled writer; the measure: hit@5 95 % or better on the hidden half" | "a fresh 80 (40 visible, 40 hidden) written by the walled writer at a pinned snapshot after the memory build and measured at once on it: the end-to-end judged figure 95 % or better (DEC-1097/DEC-1098's configuration), hit@5, hit@10, hit@20 and the stacked share beside it as diagnostics; every later measure the same, no set reused": to the EXAMIN CTO by a REPLIES section; a brief amendment needs your yes on its new sha |
| A13 | The writer brief's difficulty (`writer.md:89-93`) | "at most 6 keyword", "at least 2 supersession" | **option (a), recommended:** exact counts, "exactly 6 keyword, exactly 2 supersession", so difficulty is fixed by structure as kinds and areas are; a new brief version, your yes on its sha (the brief is hashed); **(b)** leave the brief, record the difficulty proxy each time (the job prints it) and compare; (c) a difficulty label per question (the checker grades it): more cost, a new rubric item |
| A14 | The two halves | one writer run is 40 | **(a), recommended:** two writer runs per measure (v and h), the same brief and quotas, at the same commit, both sealed while measured, the visible one released after; **(b)** a new 80-question brief that splits itself (a new rubric version, your yes) |
| A16 | DEC-1179 (2)'s verdict wording; DEC-1097 (1)(d) as carried by W2-88 S14 | "every memory verdict passes at 95 % (at least ceil(0.95 n) right end to end …)" | unchanged in substance; one line added: "the verdict of a fresh 80 is per half and for the 80 together: the hidden half's figure is the verdict; the visible half's is reported beside it and its misses are read" (**for your decision:** the verdict on the hidden 40 alone, recommended, or on all 80) |
| A17 | W2-187's driver (`src/gov/memaudit/driver.py:179-205`) and `measure`'s control | one audit of 40 per run, measured at the store link; the control is the fixed visible 40 | the driver runs two audits per measure (v, h) on a snapshot clone and store it builds; the control stays a fixed retriever check (it is not a figure and not reused as a measure set); part of A9's reopening |
| A15 | W2-81 (the proving ground, in flight) | each build writes its question sets from its seed; the read step measures after the adopters changed the repositories | **for your decision:** recommended outside the rule (a judge of adoption on synthetic repositories with generator-built gold, not a memory measure of a live repository); if inside, the read step needs a writer after adoption |

## 3. The cost per measure (E: MEMORY-AUDIT-1 §7's estimates; M: measured)
| Step | $ | Wall-clock |
|---|---|---|
| The snapshot: a clone and its seeded store (M: JOB-02, about 1 minute) | 0 | 1 to 5 min |
| Writer round 1, two halves (E: $3.5, 40 min each) | 7 | 80 min (halves one after the other) |
| Checker round 1, two halves (E: $7, 40 min each) | 14 | 80 min |
| Round 2 when the notes ask (E: $3 + $7, 65 min per half) | 0 to 20 | 0 to 130 min |
| The retrieval measure, four modes, both halves (M: JOB-02, 962 to 1,312 s per mode on 39) | 0 (no model tokens) | about 160 min of GPU; 40 min in the standard mode alone |
| The audit steps per half: `preflight`, `void`, `measure` (the declaration, the control, the counting attempt; M: about 10 min of GPU per 40, MEMORY-AUDIT-1 §7) | 0 | about 20 min |
| **The judged end-to-end run, both halves: THE figure** (M: FRESH-80, $0.157 a question; about 5 to 10 min per 40 with four workers) | 12.6 | about 10 to 20 min |
| Optional: the auditor's miss classes (E: $3 a half) | 6 | about 30 min |
| **One measure** | **about $34 to $54 (the judged run included); $40 to $60 with the classes** | **about 5.5 to 8 h with the four-mode diagnostics; about 3.5 to 5 h with the standard mode only** |

- **A year, per repository, under O3 (b):** weekly while active about $1,800 to $2,800 (52 measures); monthly once stable
  about $400 to $650. DEC-1179's standing plan cost about $1,200 a year ($12.6 a week plus a $45 fresh 80 a month).
- **The owner's minutes:** none per measure (the operator runs it on your "run JOB-<id>"; later the cron line).
- **Recommendation:** the judged end-to-end run in every measure (it is the bar); the four-mode diagnostics only at
  decision points (W2-15b, a release, a miss), the standard mode's hit@5, hit@10, hit@20 and stacked share otherwise:
  about $35 to $55 and 3.5 to 5 h a week.

## 4. The first fresh 80 (JOB-20261116-15)
Drafted beside this page (`JOB-20261116-15.md`, `fresh80.sh`, `fresh_counts.py`, `rehearsal.log`):
snapshot at w2/integrate's head and its own store; per half an audit of the pinned product: the walled writer and
checker through `indep_launch.py` with the approved memory-audit briefs, `preflight`, `void`, `measure` and **`judge`,
the end-to-end judged figure against 95 % (THE figure)**; then the four modes on both halves as diagnostics; counts
only (each half's mix, per mode hit@5, hit@10, hit@20, the stacked share, missed ids, misses by kind and area, the
halves' overlap as a count); the visible half released to `~/gov-os-runs/W2-00/fresh80-<TAG>/visible/`. About 5.5 to
8 hours; about $34 to $54. **Not queued.** Before the CTO queues it:
- fill `<C>` and `<TAG>` and the three sha prefixes; it uses the writer brief as approved today (A13 (b)), so the first
  set's difficulty is recorded, not fixed;
- each half runs as a `memory-audit-<YYMMDD>01/02` audit, so `preflight` and `void` run and a rejected question is set
  aside before the measure; the job needs the claude CLI logged in where the operator runs it (the judge's and the
  launch script's model calls), the pinned product at `~/.local/bin/gov`, and the two briefs on the walls' approved
  list (the launch script refuses otherwise);
- risk: the two halves draw from the same changed and sample lists with different seeds, so they can share governing
  paths; the job counts the overlap (5b); a nonzero count is reported, not a stop.

## 5. What needs the owner
- `P-FRESH-80-1 (a)`: A1 to A12, A16 (the hidden half's figure is the verdict) and A17 as written, A13 (a) (exact keyword and supersession counts, a new writer brief version
  for your yes on its sha), A14 (a) (two 40-question writer runs per measure), A15 W2-81 outside the rule; W2-187 and
  W2-188 reopened under your line (no new ticket); then `run JOB-20261116-15` once the CTO names it.
- or `(a) with A13 (b)` (no brief change now), or `(b)` (a new 80-question brief, A14 (b)).
- the EXAMIN brief amendment's yes on its new sha, when the CTO brings it.
